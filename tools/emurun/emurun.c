// emurun: headless mGBA driver for Crystal Imperium automated play tests.
//
// Usage: emurun <rom.gba> <script.txt> [save.sav]
//
// Script commands (one per line, '#' starts a comment):
//   wait N                 run N frames with no input
//   press KEY[+KEY] [N]    hold keys for N frames (default 6), then release 6 frames
//   hold KEY[+KEY] N       hold keys for N frames, no release
//   mash KEY N             press KEY every 12 frames for N frames
//   shot FILE.png          write the current frame as PNG
//   peek8/peek16/peek32 ADDR [LABEL]   print memory value
//   expect8/expect16/expect32 ADDR VALUE [LABEL]   fail (exit 2) if mismatch
//   expectne8/expectne16/expectne32 ADDR VALUE [LABEL]   fail (exit 2) if equal
//   savestate/loadstate FILE   write or restore a full emulator state
//   poke8/poke16/poke32 ADDR VALUE   write memory
//   reset                  soft reset the core
// KEY: A B SELECT START RIGHT LEFT UP DOWN R L
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/serialize.h>
#include <mgba/gba/core.h>
#include <mgba-util/vfs.h>
#include <png.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

static struct mCore *core;
static color_t *videoBuffer;
static unsigned width, height;
static unsigned long frameCount;
static int failures;

static void QuietLog(struct mLogger *logger, int category, enum mLogLevel level, const char *format, va_list args)
{
    (void)logger; (void)category; (void)level; (void)format; (void)args;
}
static struct mLogger sLogger = { .log = QuietLog };

static unsigned ParseKeys(const char *s)
{
    static const char *names[] = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" };
    unsigned keys = 0;
    char buf[128];
    strncpy(buf, s, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    for (char *tok = strtok(buf, "+"); tok; tok = strtok(NULL, "+"))
    {
        int found = 0;
        for (unsigned i = 0; i < sizeof(names) / sizeof(names[0]); i++)
        {
            if (!strcasecmp(tok, names[i]))
            {
                keys |= 1u << i;
                found = 1;
            }
        }
        if (!found)
            fprintf(stderr, "unknown key '%s'\n", tok);
    }
    return keys;
}

static void RunFrames(unsigned keys, unsigned n)
{
    core->setKeys(core, keys);
    for (unsigned i = 0; i < n; i++)
    {
        core->runFrame(core);
        frameCount++;
    }
}

static int WritePng(const char *path)
{
    FILE *f = fopen(path, "wb");
    if (!f)
        return -1;
    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    png_infop info = png_create_info_struct(png);
    png_init_io(png, f);
    png_set_IHDR(png, info, width, height, 8, PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
                 PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
    png_write_info(png, info);
    unsigned char *row = malloc(width * 3);
    for (unsigned y = 0; y < height; y++)
    {
        for (unsigned x = 0; x < width; x++)
        {
            uint32_t c = videoBuffer[y * width + x];
            row[x * 3 + 0] = c & 0xFF;
            row[x * 3 + 1] = (c >> 8) & 0xFF;
            row[x * 3 + 2] = (c >> 16) & 0xFF;
        }
        png_write_row(png, row);
    }
    png_write_end(png, NULL);
    png_destroy_write_struct(&png, &info);
    free(row);
    fclose(f);
    return 0;
}

static uint32_t Peek(int size, uint32_t addr)
{
    switch (size)
    {
    case 8: return core->busRead8(core, addr);
    case 16: return core->busRead16(core, addr);
    default: return core->busRead32(core, addr);
    }
}

int main(int argc, char **argv)
{
    if (argc < 3)
    {
        fprintf(stderr, "usage: %s rom.gba script.txt [save.sav]\n", argv[0]);
        return 1;
    }
    mLogSetDefaultLogger(&sLogger);
    core = mCoreFind(argv[1]);
    if (!core || !core->init(core))
    {
        fprintf(stderr, "could not create core for %s\n", argv[1]);
        return 1;
    }
    mCoreInitConfig(core, NULL);
    core->desiredVideoDimensions(core, &width, &height);
    videoBuffer = calloc(width * height, BYTES_PER_PIXEL);
    core->setVideoBuffer(core, videoBuffer, width);
    if (!mCoreLoadFile(core, argv[1]))
    {
        fprintf(stderr, "could not load ROM %s\n", argv[1]);
        return 1;
    }
    if (argc > 3)
    {
        struct VFile *vf = VFileOpen(argv[3], O_CREAT | O_RDWR);
        if (!vf || !core->loadSave(core, vf))
        {
            fprintf(stderr, "could not attach save %s\n", argv[3]);
            return 1;
        }
    }
    core->reset(core);

    FILE *script = fopen(argv[2], "r");
    if (!script)
    {
        fprintf(stderr, "could not open script %s\n", argv[2]);
        return 1;
    }
    char line[512];
    int lineNo = 0;
    while (fgets(line, sizeof(line), script))
    {
        lineNo++;
        char *hash = strchr(line, '#');
        if (hash)
            *hash = 0;
        char cmd[32] = {0}, a1[256] = {0}, a2[256] = {0}, a3[256] = {0};
        int n = sscanf(line, "%31s %255s %255s %255s", cmd, a1, a2, a3);
        if (n <= 0)
            continue;
        if (!strcmp(cmd, "wait"))
            RunFrames(0, strtoul(a1, NULL, 0));
        else if (!strcmp(cmd, "press"))
        {
            RunFrames(ParseKeys(a1), n > 2 ? strtoul(a2, NULL, 0) : 6);
            RunFrames(0, 6);
        }
        else if (!strcmp(cmd, "hold"))
            RunFrames(ParseKeys(a1), strtoul(a2, NULL, 0));
        else if (!strcmp(cmd, "mash"))
        {
            unsigned total = strtoul(a2, NULL, 0), keys = ParseKeys(a1);
            for (unsigned i = 0; i < total; i += 12)
            {
                RunFrames(keys, 6);
                RunFrames(0, 6);
            }
        }
        else if (!strcmp(cmd, "shot"))
        {
            if (WritePng(a1))
                fprintf(stderr, "line %d: could not write %s\n", lineNo, a1);
            else
                printf("[frame %lu] shot %s\n", frameCount, a1);
        }
        else if (!strncmp(cmd, "peek", 4))
        {
            int size = atoi(cmd + 4);
            uint32_t addr = strtoul(a1, NULL, 0);
            printf("[frame %lu] %s @0x%08X = 0x%X (%u)\n", frameCount, n > 2 ? a2 : "peek", addr, Peek(size, addr), Peek(size, addr));
        }
        else if (!strncmp(cmd, "expect", 6))
        {
            int negate = !strncmp(cmd, "expectne", 8);
            int size = atoi(cmd + (negate ? 8 : 6));
            uint32_t addr = strtoul(a1, NULL, 0), want = strtoul(a2, NULL, 0), got = Peek(size, addr);
            int ok = negate ? got != want : got == want;
            printf("[frame %lu] %s %s: @0x%08X = 0x%X (%s 0x%X)\n", frameCount, ok ? "PASS" : "FAIL",
                   n > 3 ? a3 : "expect", addr, got, negate ? "must not be" : "want", want);
            if (!ok)
                failures++;
        }
        else if (!strcmp(cmd, "savestate") || !strcmp(cmd, "loadstate"))
        {
            int saving = cmd[0] == 's';
            struct VFile *vf = VFileOpen(a1, saving ? O_CREAT | O_TRUNC | O_RDWR : O_RDONLY);
            int ok = vf && (saving ? mCoreSaveStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC)
                                   : mCoreLoadStateNamed(core, vf, SAVESTATE_SAVEDATA | SAVESTATE_RTC));
            if (vf)
                vf->close(vf);
            printf("[frame %lu] %s %s %s\n", frameCount, cmd, a1, ok ? "ok" : "FAILED");
            if (!ok)
                failures++;
        }
        else if (!strncmp(cmd, "poke", 4))
        {
            int size = atoi(cmd + 4);
            uint32_t addr = strtoul(a1, NULL, 0), value = strtoul(a2, NULL, 0);
            if (size == 8)
                core->busWrite8(core, addr, value);
            else if (size == 16)
                core->busWrite16(core, addr, value);
            else
                core->busWrite32(core, addr, value);
        }
        else if (!strcmp(cmd, "reset"))
            core->reset(core);
        else
            fprintf(stderr, "line %d: unknown command '%s'\n", lineNo, cmd);
    }
    fclose(script);
    printf("done: %lu frames, %d failures\n", frameCount, failures);
    core->deinit(core);
    return failures ? 2 : 0;
}
