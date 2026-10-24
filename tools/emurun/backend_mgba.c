// emurun backend: libmgba
#include "backend.h"
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba/gba/core.h>
#include <mgba-util/vfs.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>

static struct mCore *core;
static color_t *videoBuffer;
static unsigned width, height;

static void QuietLog(struct mLogger *logger, int category, enum mLogLevel level, const char *format, va_list args)
{
    (void)logger; (void)category; (void)level; (void)format; (void)args;
}
static struct mLogger sLogger = { .log = QuietLog };

int Backend_Init(const char *rom, const char *save)
{
    mLogSetDefaultLogger(&sLogger);
    core = mCoreFind(rom);
    if (!core || !core->init(core))
    {
        fprintf(stderr, "could not create core for %s\n", rom);
        return -1;
    }
    mCoreInitConfig(core, NULL);
    core->desiredVideoDimensions(core, &width, &height);
    videoBuffer = calloc(width * height, BYTES_PER_PIXEL);
    core->setVideoBuffer(core, videoBuffer, width);
    if (!mCoreLoadFile(core, rom))
    {
        fprintf(stderr, "could not load ROM %s\n", rom);
        return -1;
    }
    if (save)
    {
        struct VFile *vf = VFileOpen(save, O_CREAT | O_RDWR);
        if (!vf || !core->loadSave(core, vf))
        {
            fprintf(stderr, "could not attach save %s\n", save);
            return -1;
        }
    }
    core->reset(core);
    return 0;
}

void Backend_Deinit(void)
{
    core->deinit(core);
}

void Backend_RunFrame(unsigned keys)
{
    core->setKeys(core, keys);
    core->runFrame(core);
}

uint32_t Backend_Read(int size, uint32_t addr)
{
    switch (size)
    {
    case 8: return core->busRead8(core, addr);
    case 16: return core->busRead16(core, addr);
    default: return core->busRead32(core, addr);
    }
}

void Backend_Write(int size, uint32_t addr, uint32_t value)
{
    if (size == 8)
        core->busWrite8(core, addr, value);
    else if (size == 16)
        core->busWrite16(core, addr, value);
    else
        core->busWrite32(core, addr, value);
}

const uint32_t *Backend_Video(unsigned *w, unsigned *h)
{
    *w = width;
    *h = height;
    return (const uint32_t *)videoBuffer;
}

void Backend_Reset(void)
{
    core->reset(core);
}

static int State(const char *path, int saving)
{
    struct VFile *vf = VFileOpen(path, saving ? O_CREAT | O_TRUNC | O_RDWR : O_RDONLY);
    int ok = vf && (saving ? mCoreSaveStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC)
                           : mCoreLoadStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC));
    if (vf)
        vf->close(vf);
    return ok;
}

int Backend_SaveState(const char *path) { return State(path, 1); }
int Backend_LoadState(const char *path) { return State(path, 0); }
const char *Backend_Name(void) { return "mGBA"; }
