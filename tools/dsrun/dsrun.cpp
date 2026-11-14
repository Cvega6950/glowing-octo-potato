// dsrun: a headless Nintendo DS runner for play tests, built on the melonDS core that Delta uses
// (rileytestut/melonDS at a53f9ba, melonDS 0.9.5 with Delta's patches), set up the way Delta's
// MelonDSEmulatorBridge.mm sets it up: DS mode, interpreter (no JIT), threaded software renderer,
// direct boot, FreeBIOS and generated firmware unless all three BIOS files are given, firmware
// user "Delta" born 7 October, raw in-game saves.
//
// Differences from Delta, all outside the emulated machine: no audio output (the SPU's output is
// drained and dropped), and the real-time clock reads a fake clock that starts at a chosen time
// and advances with emulated frames, so that tests are deterministic.
//
// C API (see dsrun.py):
//   dsrun_open(rom, save_or_null, bios_dir_or_null, start_epoch) -> 0 on success
//   dsrun_set_keys(pressed_mask), dsrun_touch(x, y), dsrun_release()
//   dsrun_run(frames), dsrun_frame_count()
//   dsrun_main_ram() -> 4 MB of main RAM (0x02000000)
//   dsrun_read8/16/32(addr), dsrun_write8/16/32(addr, value): ARM9 bus access
//   dsrun_screenshot(path) -> PNG of both screens (256x384)
//   dsrun_save_size(), dsrun_save_data(), dsrun_write_save(path)

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <png.h>

#include "NDS.h"
#include "GPU.h"
#include "SPU.h"
#include "Platform.h"

namespace
{
std::string g_biosDir;
bool g_externalBios = false;
std::vector<u8> g_save;
bool g_saveDirty = false;
u64 g_frames = 0;
time_t g_startEpoch = 0;
std::vector<u8> g_rom;

bool FileExistsPlain(const std::string& p)
{
    FILE* f = fopen(p.c_str(), "rb");
    if (!f) return false;
    fclose(f);
    return true;
}

bool ReadFile(const char* path, std::vector<u8>& out)
{
    FILE* f = fopen(path, "rb");
    if (!f) return false;
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    out.resize(len > 0 ? len : 0);
    size_t got = len > 0 ? fread(out.data(), 1, len, f) : 0;
    fclose(f);
    return (long)got == len;
}
}

// The emulated real-time clock: start_epoch plus the emulated time (59.8261 frames a second).
// melonDS's RTC calls time(NULL) and localtime_r(); with -Bsymbolic this definition is the one
// the core uses. Run with TZ=UTC for a fixed local time.
extern "C" time_t time(time_t* t)
{
    time_t now = g_startEpoch + (time_t)((double)g_frames / 59.8261);
    if (t) *t = now;
    return now;
}

namespace Platform
{
void Init(int, char**) {}
void DeInit() {}
void StopEmu() {}
int InstanceID() { return 0; }
std::string InstanceFileSuffix() { return ""; }

int GetConfigInt(ConfigEntry entry)
{
    switch (entry)
    {
    case Firm_Language: return 1; // English, Delta's default
    case Firm_BirthdayMonth: return 10;
    case Firm_BirthdayDay: return 7;
    case Firm_Color: return 0;
    case AudioBitrate: return 0;
    case DLDI_ImageSize: return 0;
    case DSiSD_ImageSize: return 0;
    default: return 0;
    }
}

bool GetConfigBool(ConfigEntry entry)
{
    switch (entry)
    {
    case ExternalBIOSEnable: return g_externalBios;
    case Firm_OverrideSettings: return false;
    default: return false;
    }
}

std::string GetConfigString(ConfigEntry entry)
{
    switch (entry)
    {
    case BIOS9Path: return g_biosDir + "/bios9.bin";
    case BIOS7Path: return g_biosDir + "/bios7.bin";
    case FirmwarePath: return g_biosDir + "/firmware.bin";
    case Firm_Username: return "Delta";
    default: return "";
    }
}

bool GetConfigArray(ConfigEntry, void*) { return false; }

FILE* OpenFile(std::string path, std::string mode, bool mustexist)
{
    if (mustexist && !FileExistsPlain(path)) return nullptr;
    return fopen(path.c_str(), mode.c_str());
}
FILE* OpenLocalFile(std::string path, std::string mode) { return OpenFile(path, mode, mode[0] != 'w'); }
FILE* OpenDataFile(std::string path) { return OpenFile(path, "rb", true); }

struct Thread { std::thread t; };
Thread* Thread_Create(std::function<void()> func) { Thread* th = new Thread; th->t = std::thread(func); return th; }
void Thread_Free(Thread* th) { if (th->t.joinable()) th->t.detach(); delete th; }
void Thread_Wait(Thread* th) { if (th->t.joinable()) th->t.join(); }

struct Semaphore { std::mutex m; std::condition_variable cv; int count = 0; };
Semaphore* Semaphore_Create() { return new Semaphore; }
void Semaphore_Free(Semaphore* s) { delete s; }
void Semaphore_Reset(Semaphore* s) { std::lock_guard<std::mutex> l(s->m); s->count = 0; }
void Semaphore_Wait(Semaphore* s) { std::unique_lock<std::mutex> l(s->m); s->cv.wait(l, [s] { return s->count > 0; }); s->count--; }
void Semaphore_Post(Semaphore* s, int count) { { std::lock_guard<std::mutex> l(s->m); s->count += count; } s->cv.notify_all(); }

struct Mutex { std::mutex m; };
Mutex* Mutex_Create() { return new Mutex; }
void Mutex_Free(Mutex* m) { delete m; }
void Mutex_Lock(Mutex* m) { m->m.lock(); }
void Mutex_Unlock(Mutex* m) { m->m.unlock(); }
bool Mutex_TryLock(Mutex* m) { return m->m.try_lock(); }

void Sleep(u64 usecs) { std::this_thread::sleep_for(std::chrono::microseconds(usecs)); }

void WriteNDSSave(const u8* savedata, u32 savelen, u32, u32)
{
    g_save.assign(savedata, savedata + savelen);
    g_saveDirty = true;
}
void WriteGBASave(const u8*, u32, u32, u32) {}

bool MP_Init() { return false; }
void MP_DeInit() {}
void MP_Begin() {}
void MP_End() {}
int MP_SendPacket(u8*, int, u64) { return 0; }
int MP_RecvPacket(u8*, u64*) { return 0; }
int MP_SendCmd(u8*, int, u64) { return 0; }
int MP_SendReply(u8*, int, u64, u16) { return 0; }
int MP_SendAck(u8*, int, u64) { return 0; }
int MP_RecvHostPacket(u8*, u64*) { return 0; }
u16 MP_RecvReplies(u8*, u64, u16) { return 0; }

bool LAN_Init() { return false; }
void LAN_DeInit() {}
int LAN_SendPacket(u8*, int) { return 0; }
int LAN_RecvPacket(u8*) { return 0; }

void Camera_Start(int) {}
void Camera_Stop(int) {}
void Camera_CaptureFrame(int, u32*, int, int, bool) {}

void Mic_Prepare() {}
}

namespace NDS
{
u8 ARM9Read8(u32 addr);
u16 ARM9Read16(u32 addr);
u32 ARM9Read32(u32 addr);
void ARM9Write8(u32 addr, u8 val);
void ARM9Write16(u32 addr, u16 val);
void ARM9Write32(u32 addr, u32 val);
}

extern "C" {

int dsrun_open(const char* romPath, const char* savePath, const char* biosDir, long long startEpoch)
{
    g_startEpoch = (time_t)startEpoch;
    g_frames = 0;
    g_biosDir = biosDir ? biosDir : "";
    g_externalBios = biosDir && FileExistsPlain(g_biosDir + "/bios7.bin") && FileExistsPlain(g_biosDir + "/bios9.bin")
                     && FileExistsPlain(g_biosDir + "/firmware.bin");

    if (!ReadFile(romPath, g_rom)) return 1;

    GPU::InitRenderer(0);
    NDS::SetConsoleType(0);
    if (!NDS::Init()) return 2;
    GPU::RenderSettings settings;
    settings.Soft_Threaded = true;
    settings.GL_ScaleFactor = 1;
    settings.GL_BetterPolygons = false;
    GPU::SetRenderSettings(0, settings);
    NDS::Reset();

    std::vector<u8> save;
    if (savePath && savePath[0] && ReadFile(savePath, save) && !save.empty())
    {
        g_save = save;
        if (!NDS::LoadCart(g_rom.data(), (u32)g_rom.size(), save.data(), (u32)save.size())) return 3;
    }
    else
    {
        if (!NDS::LoadCart(g_rom.data(), (u32)g_rom.size(), nullptr, 0)) return 3;
    }
    const char* slash = strrchr(romPath, '/');
    NDS::SetupDirectBoot(slash ? slash + 1 : romPath);
    NDS::Start();
    return 0;
}

// pressed: bit 0 A, 1 B, 2 SELECT, 3 START, 4 RIGHT, 5 LEFT, 6 UP, 7 DOWN, 8 R, 9 L, 10 X, 11 Y
void dsrun_set_keys(unsigned pressed) { NDS::SetKeyMask((~pressed) & 0xFFF); }
void dsrun_touch(int x, int y) { NDS::TouchScreen((u16)x, (u16)y); }
void dsrun_release() { NDS::ReleaseScreen(); }

void dsrun_run(int frames)
{
    static s16 audio[8192];
    for (int i = 0; i < frames; i++)
    {
        NDS::RunFrame();
        g_frames++;
        int avail = SPU::GetOutputSize();
        while (avail > 0)
        {
            int n = avail > 4096 ? 4096 : avail;
            SPU::ReadOutput(audio, n);
            avail -= n;
        }
    }
}

unsigned long long dsrun_frame_count() { return g_frames; }
unsigned char* dsrun_main_ram() { return NDS::MainRAM; }
unsigned dsrun_read8(unsigned a) { return NDS::ARM9Read8(a); }
unsigned dsrun_read16(unsigned a) { return NDS::ARM9Read16(a); }
unsigned dsrun_read32(unsigned a) { return NDS::ARM9Read32(a); }
void dsrun_write8(unsigned a, unsigned v) { NDS::ARM9Write8(a, (u8)v); }
void dsrun_write16(unsigned a, unsigned v) { NDS::ARM9Write16(a, (u16)v); }
void dsrun_write32(unsigned a, unsigned v) { NDS::ARM9Write32(a, v); }

// Both screens as 8-bit RGB (256x384, top screen first). The software renderer's last step
// (GPU2D_Soft.cpp, "convert to 32-bit BGRA") leaves 0xAARRGGBB in each pixel.
void dsrun_framebuffer_rgb(unsigned char* out)
{
    for (int s = 0; s < 2; s++)
    {
        const u32* src = GPU::Framebuffer[GPU::FrontBuffer][s];
        for (int i = 0; i < 256 * 192; i++)
        {
            u32 c = src ? src[i] : 0;
            unsigned char* p = out + (s * 256 * 192 + i) * 3;
            p[0] = (c >> 16) & 0xFF;
            p[1] = (c >> 8) & 0xFF;
            p[2] = c & 0xFF;
        }
    }
}

int dsrun_screenshot(const char* path)
{
    std::vector<unsigned char> rgb(256 * 384 * 3);
    dsrun_framebuffer_rgb(rgb.data());
    FILE* f = fopen(path, "wb");
    if (!f) return 1;
    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, nullptr, nullptr, nullptr);
    png_infop info = png_create_info_struct(png);
    if (setjmp(png_jmpbuf(png))) { png_destroy_write_struct(&png, &info); fclose(f); return 2; }
    png_init_io(png, f);
    png_set_IHDR(png, info, 256, 384, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT,
                 PNG_FILTER_TYPE_DEFAULT);
    png_write_info(png, info);
    for (int y = 0; y < 384; y++) png_write_row(png, rgb.data() + y * 256 * 3);
    png_write_end(png, nullptr);
    png_destroy_write_struct(&png, &info);
    fclose(f);
    return 0;
}

unsigned dsrun_save_size() { return (unsigned)g_save.size(); }
const unsigned char* dsrun_save_data() { return g_save.data(); }
int dsrun_save_dirty() { return g_saveDirty ? 1 : 0; }

int dsrun_write_save(const char* path)
{
    FILE* f = fopen(path, "wb");
    if (!f) return 1;
    fwrite(g_save.data(), 1, g_save.size(), f);
    fclose(f);
    g_saveDirty = false;
    return 0;
}

int dsrun_external_bios() { return g_externalBios ? 1 : 0; }

}
