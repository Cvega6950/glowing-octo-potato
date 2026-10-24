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
//   (peek/expect ADDR may be *PTR+OFF: the pointer stored at PTR plus OFF, e.g. *{gSaveBlock1Ptr}+4)
//   savestate/loadstate FILE   write or restore a full emulator state
//   poke8/poke16/poke32 ADDR VALUE   write memory
//   reset                  soft reset the core
//   autobattle MOVES MAXFRAMES key=ADDR...   play the current battle to the end (see AutoBattle)
//   menuselect CURSOR LIST COUNT TARGET   with a list menu open whose u8 cursor, u8 action list and
//                          u8 length live at those addresses, move to the entry equal to TARGET and press A
//   walkto SB1PTR X Y [yx]  step (holding the d-pad 8 frames per tile) until the player's map position,
//                          read from *SB1PTR (gSaveBlock1Ptr->pos, offset 4 after HnS's saveVersion),
//                          is (X,Y); x first unless "yx". With "soft" as 5th argument, not reaching
//                          the target (e.g. a wild battle started) is not a failure
//   expectflag SB1PTR FLAGSOFF FLAG WANT [LABEL]   check event flag FLAG (0/1) in (*SB1PTR)->flags
//   seek8/seek16 ADDR TARGET KEYUP KEYDOWN   tap KEYUP while the value at ADDR is below TARGET and
//                          KEYDOWN while above, until it equals TARGET (at most 32 taps)
//   tally NAME ADDR VALUE  count runs of NAME, and how many had the 8-bit value at ADDR == VALUE
//   expecttally NAME MIN MAX   fail unless the matching count of NAME is within [MIN, MAX]
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

#define MAX_TALLIES 16
static struct { char name[64]; int hits, runs; } sTallies[MAX_TALLIES];

static int *TallySlot(const char *name, int create, int **runs)
{
    for (int i = 0; i < MAX_TALLIES; i++)
    {
        if (sTallies[i].name[0] == 0 && create)
            snprintf(sTallies[i].name, sizeof(sTallies[i].name), "%s", name);
        if (!strcmp(sTallies[i].name, name))
        {
            *runs = &sTallies[i].runs;
            return &sTallies[i].hits;
        }
    }
    return NULL;
}

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

// An address is a number, or *PTR+OFF: the 32-bit pointer stored at PTR, plus OFF
static uint32_t ParseAddr(const char *text)
{
    char *end;
    if (text[0] != '*')
        return strtoul(text, NULL, 0);
    uint32_t addr = Peek(32, strtoul(text + 1, &end, 0));
    if (*end == '+')
        addr += strtoul(end + 1, NULL, 0);
    return addr;
}

// Battle autopilot. Reads the game's battle state each frame and answers whatever input it is
// waiting for, so play tests don't depend on RNG or text timing.
//   MOVES: one entry per party slot, the move slot (0-3) that Pokemon uses, e.g. "2,3,1".
//          Append 'm' (e.g. "2m") to press the gimmick trigger (Mega Evolution) first.
//   key=ADDR pairs (emu.py fills these from the ELF): main outcome ctrl act mov actcur movcur
//          partyidx party count pmenu pmenucb2 battlecb2 mons (gBattleMons, for the turn log)
// Forced switches send out the first party Pokemon that still has HP and is not already active.
struct AutoSyms
{
    uint32_t main, outcome, ctrl, act, mov, actcur, movcur, partyidx, party, count, pmenu, pmenucb2, battlecb2, mons;
};

static void Tap(unsigned keys)
{
    RunFrames(keys, 4);
    RunFrames(0, 8);
}

static int PartyHp(const struct AutoSyms *sy, int slot)
{
    return Peek(16, sy->party + slot * 100 + 86);
}

static void AutoBattle(const char *movesArg, unsigned long maxFrames, const struct AutoSyms *sy)
{
    int moves[6] = {0}, mega[6] = {0};
    const char *p = movesArg;
    for (int i = 0; i < 6 && *p; i++)
    {
        moves[i] = *p - '0';
        p++;
        if (*p == 'm')
        {
            mega[i] = 1;
            p++;
        }
        if (*p == ',')
            p++;
    }

    unsigned long start = frameCount, idle = 0;
    int turns = 0, switches = 0, megaPressed = 0, shownMoves = 0;
    uint32_t outcome = 0;
    while (frameCount - start < maxFrames)
    {
        outcome = Peek(8, sy->outcome);
        uint32_t cb2 = Peek(32, sy->main + 4) & ~1u;   // gMain.callback2
        uint32_t ctrl = Peek(32, sy->ctrl) & ~1u;           // gBattlerControllerFuncs[0]
        if (outcome != 0 && cb2 != sy->battlecb2)
            break;
        if (cb2 == sy->pmenucb2)
        {
            // Skip the active battler: it may still have HP after a voluntary switch (U-turn, Teleport)
            int target = -1, count = Peek(8, sy->count), active = Peek(8, sy->partyidx);
            for (int i = 0; i < count && i < 6; i++)
            {
                if (PartyHp(sy, i) > 0 && i != active)
                {
                    target = i;
                    break;
                }
            }
            int slot = (int8_t)Peek(8, sy->pmenu + 9);
            if (target < 0 || slot == target)
            {
                Tap(1u << 0); // A: choose the Pokemon
                RunFrames(0, 30);
                Tap(1u << 0); // A: SEND OUT
                RunFrames(0, 60);
                switches++;
                printf("[frame %lu] autobattle: switch to party slot %d\n", frameCount, target);
            }
            else
            {
                Tap(slot < target ? 1u << 7 : 1u << 6); // DOWN / UP
            }
            idle = 0;
        }
        else if (ctrl == sy->act)
        {
            if (Peek(8, sy->actcur) != 0)
                Tap(1u << 6 | 1u << 5); // UP+LEFT: back to BATTLE
            else
                Tap(1u << 0);
            idle = 0;
        }
        else if (ctrl == sy->mov)
        {
            int slot = Peek(8, sy->partyidx);
            int want = moves[slot < 6 ? slot : 0], cur = Peek(8, sy->movcur);
            if (cur != want)
            {
                if ((cur ^ want) & 1)
                    Tap((want & 1) ? 1u << 4 : 1u << 5); // RIGHT / LEFT
                else
                    Tap((want & 2) ? 1u << 7 : 1u << 6); // DOWN / UP
            }
            else
            {
                if (mega[slot] && !(megaPressed & (1 << slot)))
                {
                    Tap(1u << 8); // R: gimmick trigger
                    megaPressed |= 1 << slot;
                }
                // BattlePokemon is 0x88 bytes: species +0, moves +12, hp +42, level +44, maxHP +46
                if (!(shownMoves & (1 << slot)))
                {
                    shownMoves |= 1 << slot;
                    printf("[frame %lu] autobattle: party slot %d species %u knows move %u / move %u / move %u / move %u\n",
                           frameCount, slot, Peek(16, sy->mons), Peek(16, sy->mons + 12), Peek(16, sy->mons + 14),
                           Peek(16, sy->mons + 16), Peek(16, sy->mons + 18));
                }
                printf("[frame %lu] autobattle: turn %d: player species %u %u/%u uses move %u (slot %d)%s vs opponent species %u %u/%u\n",
                       frameCount, turns + 1, Peek(16, sy->mons), Peek(16, sy->mons + 42), Peek(16, sy->mons + 46),
                       Peek(16, sy->mons + 12 + 2 * want), want,
                       mega[slot] && (megaPressed & (1 << slot)) ? " (mega)" : "",
                       Peek(16, sy->mons + 0x88), Peek(16, sy->mons + 0x88 + 42), Peek(16, sy->mons + 0x88 + 46));
                Tap(1u << 0);
                turns++;
            }
            idle = 0;
        }
        else
        {
            RunFrames(0, 1);
            // Some messages wait for a button; nudge them along
            if (++idle % 60 == 0)
                Tap(1u << 0);
        }
    }
    // Let the post-battle text and fade finish
    for (int i = 0; i < 40 && (Peek(32, sy->main + 4) & ~1u) == sy->battlecb2; i++)
        Tap(1u << 0);
    printf("[frame %lu] autobattle: outcome=%u (1=won 2=lost) turns=%d forced_switches=%d party_hp=",
           frameCount, outcome, turns, switches);
    for (int i = 0; i < (int)Peek(8, sy->count) && i < 6; i++)
        printf("%s%d", i ? "/" : "", PartyHp(sy, i));
    printf("\n");
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
            uint32_t addr = ParseAddr(a1);
            printf("[frame %lu] %s @0x%08X = 0x%X (%u)\n", frameCount, n > 2 ? a2 : "peek", addr, Peek(size, addr), Peek(size, addr));
        }
        else if (!strncmp(cmd, "expectne", 8) || (!strncmp(cmd, "expect", 6) && cmd[6] >= '0' && cmd[6] <= '9'))
        {
            int negate = !strncmp(cmd, "expectne", 8);
            int size = atoi(cmd + (negate ? 8 : 6));
            uint32_t addr = ParseAddr(a1), want = strtoul(a2, NULL, 0), got = Peek(size, addr);
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
        else if (!strcmp(cmd, "autobattle"))
        {
            struct AutoSyms sy = {0};
            char *rest = line;
            for (int skip = 0; skip < 3 && rest; skip++)
            {
                rest = strpbrk(rest, " \t");
                if (rest)
                    rest += strspn(rest, " \t");
            }
            for (char *tok = rest ? strtok(rest, " \t\n") : NULL; tok; tok = strtok(NULL, " \t\n"))
            {
                char *eq = strchr(tok, '=');
                if (!eq)
                    continue;
                *eq = 0;
                uint32_t v = strtoul(eq + 1, NULL, 0) & ~1u;
                if (!strcmp(tok, "main")) sy.main = v;
                else if (!strcmp(tok, "outcome")) sy.outcome = v;
                else if (!strcmp(tok, "ctrl")) sy.ctrl = v;
                else if (!strcmp(tok, "act")) sy.act = v;
                else if (!strcmp(tok, "mov")) sy.mov = v;
                else if (!strcmp(tok, "actcur")) sy.actcur = v;
                else if (!strcmp(tok, "movcur")) sy.movcur = v;
                else if (!strcmp(tok, "partyidx")) sy.partyidx = v;
                else if (!strcmp(tok, "party")) sy.party = v;
                else if (!strcmp(tok, "count")) sy.count = v;
                else if (!strcmp(tok, "mons")) sy.mons = v;
                else if (!strcmp(tok, "pmenu")) sy.pmenu = v;
                else if (!strcmp(tok, "pmenucb2")) sy.pmenucb2 = v;
                else if (!strcmp(tok, "battlecb2")) sy.battlecb2 = v;
            }
            AutoBattle(a1, strtoul(a2, NULL, 0), &sy);
        }
        else if (!strcmp(cmd, "menuselect"))
        {
            uint32_t cursorAddr = strtoul(a1, NULL, 0), listAddr = strtoul(a2, NULL, 0), countAddr = strtoul(a3, NULL, 0);
            char a4[64] = {0};
            sscanf(line, "%*s %*s %*s %*s %63s", a4);
            uint32_t target = strtoul(a4, NULL, 0);
            int found = 0;
            for (int tries = 0; tries < 24 && !found; tries++)
            {
                int count = Peek(8, countAddr), cursor = Peek(8, cursorAddr);
                if (cursor < count && Peek(8, listAddr + cursor) == target)
                {
                    Tap(1u << 0);
                    found = 1;
                }
                else
                {
                    Tap(1u << 7); // DOWN
                }
            }
            if (!found)
            {
                printf("[frame %lu] FAIL menuselect: entry %u not in menu\n", frameCount, target);
                failures++;
            }
        }
        else if (!strcmp(cmd, "walkto"))
        {
            uint32_t sb1 = Peek(32, strtoul(a1, NULL, 0));
            int tx = atoi(a2), ty = atoi(a3), yFirst = 0, soft = 0;
            char a4[16] = {0}, a5[16] = {0};
            sscanf(line, "%*s %*s %*s %*s %15s %15s", a4, a5);
            yFirst = !strcmp(a4, "yx");
            soft = !strcmp(a5, "soft");
            int stuck = 0, steps = 0;
            while (steps < 400 && stuck < 6)
            {
                int x = (int16_t)Peek(16, sb1 + 4), y = (int16_t)Peek(16, sb1 + 6);
                if (x == tx && y == ty)
                    break;
                unsigned key;
                int moveX = x != tx && (!yFirst || y == ty);
                if (moveX)
                    key = x < tx ? 1u << 4 : 1u << 5;
                else
                    key = y < ty ? 1u << 7 : 1u << 6;
                RunFrames(key, 8);
                RunFrames(0, 2);
                int nx = (int16_t)Peek(16, sb1 + 4), ny = (int16_t)Peek(16, sb1 + 6);
                stuck = (nx == x && ny == y) ? stuck + 1 : 0;
                steps++;
            }
            RunFrames(0, 16);
            int x = (int16_t)Peek(16, sb1 + 4), y = (int16_t)Peek(16, sb1 + 6);
            printf("[frame %lu] walkto (%d,%d): at (%d,%d)%s\n", frameCount, tx, ty, x, y, (x == tx && y == ty) ? "" : " BLOCKED");
            if ((x != tx || y != ty) && !soft)
                failures++;
        }
        else if (!strcmp(cmd, "expectflag"))
        {
            char a4[64] = {0}, a5[128] = {0};
            sscanf(line, "%*s %*s %*s %*s %63s %127s", a4, a5);
            uint32_t sb1 = Peek(32, strtoul(a1, NULL, 0)), flag = strtoul(a3, NULL, 0);
            uint32_t addr = sb1 + strtoul(a2, NULL, 0) + flag / 8;
            int got = (Peek(8, addr) >> (flag % 8)) & 1, want = atoi(a4);
            printf("[frame %lu] %s %s: flag %u = %d (want %d)\n", frameCount, got == want ? "PASS" : "FAIL",
                   a5[0] ? a5 : "expectflag", flag, got, want);
            if (got != want)
                failures++;
        }
        else if (!strncmp(cmd, "seek", 4))
        {
            char a4[64] = {0};
            sscanf(line, "%*s %*s %*s %*s %63s", a4);
            int size = atoi(cmd + 4);
            uint32_t addr = strtoul(a1, NULL, 0), target = strtoul(a2, NULL, 0);
            unsigned up = ParseKeys(a3), down = ParseKeys(a4);
            int taps = 0;
            for (uint32_t v = Peek(size, addr); v != target && taps < 32; v = Peek(size, addr), taps++)
            {
                Tap(v < target ? up : down);
                RunFrames(0, 8);
            }
            if (Peek(size, addr) != target)
            {
                printf("[frame %lu] FAIL seek: @0x%08X stuck at %u (want %u)\n", frameCount, addr, Peek(size, addr), target);
                failures++;
            }
        }
        else if (!strcmp(cmd, "tally"))
        {
            int *runs, *hits = TallySlot(a1, 1, &runs);
            int hit = Peek(8, strtoul(a2, NULL, 0)) == strtoul(a3, NULL, 0);
            if (hits)
            {
                *hits += hit;
                (*runs)++;
                printf("[frame %lu] tally %s: run %d %s (%d/%d)\n", frameCount, a1, *runs, hit ? "hit" : "miss", *hits, *runs);
            }
        }
        else if (!strcmp(cmd, "expecttally"))
        {
            int *runs, *hits = TallySlot(a1, 0, &runs);
            int lo = atoi(a2), hi = atoi(a3), got = hits ? *hits : 0;
            int ok = hits && got >= lo && got <= hi;
            printf("[frame %lu] %s tally %s: %d/%d (want %d..%d)\n", frameCount, ok ? "PASS" : "FAIL", a1, got, hits ? *runs : 0, lo, hi);
            if (!ok)
                failures++;
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
