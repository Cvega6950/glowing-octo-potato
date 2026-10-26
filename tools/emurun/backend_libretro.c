// emurun backend: a libretro GBA core loaded at run time, named by the EMURUN_CORE environment
// variable. Used with VBA-M's libretro core (vbam_libretro.so), the emulator Delta's GBA core is
// built on, so the play tests can run on both mGBA and VBA-M.
#include "backend.h"
#include "libretro.h"
#include <dlfcn.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define WIDTH 240
#define HEIGHT 160
#define MAX_DESCRIPTORS 32

static void *sCore;
static unsigned long sFrames;
static const char *sSavePath;
static unsigned sKeys;
static uint32_t sVideo[WIDTH * HEIGHT];
static enum retro_pixel_format sPixelFormat = RETRO_PIXEL_FORMAT_0RGB1555;
static struct retro_memory_descriptor sDescriptors[MAX_DESCRIPTORS];
static unsigned sNumDescriptors;
static void *sRom;

static void (*pInit)(void);
static void (*pDeinit)(void);
static void (*pSetEnvironment)(retro_environment_t);
static void (*pSetVideoRefresh)(retro_video_refresh_t);
static void (*pSetAudioSample)(retro_audio_sample_t);
static void (*pSetAudioSampleBatch)(retro_audio_sample_batch_t);
static void (*pSetInputPoll)(retro_input_poll_t);
static void (*pSetInputState)(retro_input_state_t);
static bool (*pLoadGame)(const struct retro_game_info *);
static void (*pUnloadGame)(void);
static void (*pRun)(void);
static void (*pReset)(void);
static void *(*pGetMemoryData)(unsigned);
static size_t (*pGetMemorySize)(unsigned);
static size_t (*pSerializeSize)(void);
static bool (*pSerialize)(void *, size_t);
static bool (*pUnserialize)(const void *, size_t);

static void QuietLog(enum retro_log_level level, const char *fmt, ...)
{
    (void)level; (void)fmt;
}

static bool Environment(unsigned cmd, void *data)
{
    switch (cmd)
    {
    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
        sPixelFormat = *(const enum retro_pixel_format *)data;
        return sPixelFormat == RETRO_PIXEL_FORMAT_XRGB8888 || sPixelFormat == RETRO_PIXEL_FORMAT_RGB565;
    case RETRO_ENVIRONMENT_GET_LOG_INTERFACE:
        ((struct retro_log_callback *)data)->log = QuietLog;
        return true;
    case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
    case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:
        *(const char **)data = ".";
        return true;
    case RETRO_ENVIRONMENT_SET_MEMORY_MAPS:
    {
        const struct retro_memory_map *map = data;
        sNumDescriptors = map->num_descriptors < MAX_DESCRIPTORS ? map->num_descriptors : MAX_DESCRIPTORS;
        memcpy(sDescriptors, map->descriptors, sNumDescriptors * sizeof(*sDescriptors));
        return true;
    }
    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        *(bool *)data = false;
        return true;
    case RETRO_ENVIRONMENT_GET_CAN_DUPE:
        *(bool *)data = true;
        return true;
    default:
        return false; // core options keep their defaults
    }
}

static void VideoRefresh(const void *data, unsigned width, unsigned height, size_t pitch)
{
    if (!data)
        return;
    for (unsigned y = 0; y < height && y < HEIGHT; y++)
    {
        for (unsigned x = 0; x < width && x < WIDTH; x++)
        {
            unsigned r, g, b;
            if (sPixelFormat == RETRO_PIXEL_FORMAT_XRGB8888)
            {
                uint32_t c = ((const uint32_t *)((const uint8_t *)data + y * pitch))[x];
                r = (c >> 16) & 0xFF, g = (c >> 8) & 0xFF, b = c & 0xFF;
            }
            else
            {
                uint16_t c = ((const uint16_t *)((const uint8_t *)data + y * pitch))[x];
                r = ((c >> 11) & 0x1F) << 3, g = ((c >> 5) & 0x3F) << 2, b = (c & 0x1F) << 3;
            }
            sVideo[y * WIDTH + x] = r | (g << 8) | (b << 16);
        }
    }
}

static void AudioSample(int16_t left, int16_t right) { (void)left; (void)right; }
static size_t AudioSampleBatch(const int16_t *data, size_t frames) { (void)data; return frames; }
static void InputPoll(void) {}

static int16_t InputState(unsigned port, unsigned device, unsigned index, unsigned id)
{
    // emurun key bits: A, B, SELECT, START, RIGHT, LEFT, UP, DOWN, R, L
    static const unsigned ids[] = {
        RETRO_DEVICE_ID_JOYPAD_A, RETRO_DEVICE_ID_JOYPAD_B, RETRO_DEVICE_ID_JOYPAD_SELECT,
        RETRO_DEVICE_ID_JOYPAD_START, RETRO_DEVICE_ID_JOYPAD_RIGHT, RETRO_DEVICE_ID_JOYPAD_LEFT,
        RETRO_DEVICE_ID_JOYPAD_UP, RETRO_DEVICE_ID_JOYPAD_DOWN, RETRO_DEVICE_ID_JOYPAD_R,
        RETRO_DEVICE_ID_JOYPAD_L,
    };
    (void)index;
    if (port != 0 || device != RETRO_DEVICE_JOYPAD)
        return 0;
    for (unsigned i = 0; i < sizeof(ids) / sizeof(ids[0]); i++)
    {
        if (ids[i] == id)
            return (sKeys >> i) & 1;
    }
    return 0;
}

#define LOAD(sym, name) do { *(void **)&sym = dlsym(sCore, name); if (!sym) { fprintf(stderr, "core lacks %s\n", name); return -1; } } while (0)

int Backend_Init(const char *rom, const char *save)
{
    const char *corePath = getenv("EMURUN_CORE");
    struct retro_game_info game = {0};
    FILE *f;
    long size;

    if (!corePath)
    {
        fprintf(stderr, "set EMURUN_CORE to a libretro GBA core (e.g. vbam_libretro.so)\n");
        return -1;
    }
    sCore = dlopen(corePath, RTLD_NOW | RTLD_LOCAL);
    if (!sCore)
    {
        fprintf(stderr, "could not load core %s: %s\n", corePath, dlerror());
        return -1;
    }
    LOAD(pInit, "retro_init");
    LOAD(pDeinit, "retro_deinit");
    LOAD(pSetEnvironment, "retro_set_environment");
    LOAD(pSetVideoRefresh, "retro_set_video_refresh");
    LOAD(pSetAudioSample, "retro_set_audio_sample");
    LOAD(pSetAudioSampleBatch, "retro_set_audio_sample_batch");
    LOAD(pSetInputPoll, "retro_set_input_poll");
    LOAD(pSetInputState, "retro_set_input_state");
    LOAD(pLoadGame, "retro_load_game");
    LOAD(pUnloadGame, "retro_unload_game");
    LOAD(pRun, "retro_run");
    LOAD(pReset, "retro_reset");
    LOAD(pGetMemoryData, "retro_get_memory_data");
    LOAD(pGetMemorySize, "retro_get_memory_size");
    LOAD(pSerializeSize, "retro_serialize_size");
    LOAD(pSerialize, "retro_serialize");
    LOAD(pUnserialize, "retro_unserialize");

    pSetEnvironment(Environment);
    pInit();
    pSetVideoRefresh(VideoRefresh);
    pSetAudioSample(AudioSample);
    pSetAudioSampleBatch(AudioSampleBatch);
    pSetInputPoll(InputPoll);
    pSetInputState(InputState);

    f = fopen(rom, "rb");
    if (!f)
    {
        fprintf(stderr, "could not load ROM %s\n", rom);
        return -1;
    }
    fseek(f, 0, SEEK_END);
    size = ftell(f);
    fseek(f, 0, SEEK_SET);
    sRom = malloc(size);
    if (fread(sRom, 1, size, f) != (size_t)size)
    {
        fclose(f);
        return -1;
    }
    fclose(f);
    game.path = rom;
    game.data = sRom;
    game.size = size;
    if (!pLoadGame(&game))
    {
        fprintf(stderr, "core could not load %s\n", rom);
        return -1;
    }

    // Cartridge save: read into the core's save memory now, written back at exit
    sSavePath = save;
    if (save && (f = fopen(save, "rb")))
    {
        size_t len = pGetMemorySize(RETRO_MEMORY_SAVE_RAM);
        void *mem = pGetMemoryData(RETRO_MEMORY_SAVE_RAM);
        if (mem && len && fread(mem, 1, len, f) == 0)
            fprintf(stderr, "note: save %s is empty\n", save);
        fclose(f);
    }
    return 0;
}

void Backend_Deinit(void)
{
    FILE *f;
    if (sSavePath && (f = fopen(sSavePath, "wb")))
    {
        size_t len = pGetMemorySize(RETRO_MEMORY_SAVE_RAM);
        void *mem = pGetMemoryData(RETRO_MEMORY_SAVE_RAM);
        if (mem && len)
            fwrite(mem, 1, len, f);
        fclose(f);
    }
    pUnloadGame();
    pDeinit();
    dlclose(sCore);
    free(sRom);
}

void Backend_RunFrame(unsigned keys)
{
    sKeys = keys;
    pRun();
    sFrames++;
}

// VBA-M's cartridge clock reads time(). The executable exports this definition (see the
// Makefile), so the core's calls resolve to it: EMURUN_EPOCH plus the emulated time.
time_t time(time_t *t)
{
    time_t now = EMURUN_EPOCH + sFrames / 60;
    if (t)
        *t = now;
    return now;
}

static uint8_t *Locate(uint32_t addr, int size)
{
    for (unsigned i = 0; i < sNumDescriptors; i++)
    {
        const struct retro_memory_descriptor *d = &sDescriptors[i];
        if (d->ptr && addr >= d->start && addr + size / 8 <= d->start + d->len)
            return (uint8_t *)d->ptr + d->offset + (addr - d->start);
    }
    return NULL;
}

uint32_t Backend_Read(int size, uint32_t addr)
{
    uint8_t *p = Locate(addr, size);
    if (!p)
        return 0;
    switch (size)
    {
    case 8: return p[0];
    case 16: return p[0] | (p[1] << 8);
    default: return p[0] | (p[1] << 8) | (p[2] << 16) | ((uint32_t)p[3] << 24);
    }
}

void Backend_Write(int size, uint32_t addr, uint32_t value)
{
    uint8_t *p = Locate(addr, size);
    if (!p)
        return;
    for (int i = 0; i < size / 8; i++)
        p[i] = value >> (8 * i);
}

const uint32_t *Backend_Video(unsigned *width, unsigned *height)
{
    *width = WIDTH;
    *height = HEIGHT;
    return sVideo;
}

void Backend_Reset(void)
{
    pReset();
}

int Backend_SaveState(const char *path)
{
    size_t size = pSerializeSize();
    void *buf = malloc(size);
    FILE *f;
    int ok = buf && pSerialize(buf, size) && (f = fopen(path, "wb"))
          && fwrite(buf, 1, size, f) == size && fclose(f) == 0;
    free(buf);
    return ok;
}

int Backend_LoadState(const char *path)
{
    size_t size = pSerializeSize();
    void *buf = malloc(size);
    FILE *f = fopen(path, "rb");
    int ok = buf && f && fread(buf, 1, size, f) == size && pUnserialize(buf, size);
    if (f)
        fclose(f);
    free(buf);
    return ok;
}

const char *Backend_Name(void)
{
    return "libretro";
}
