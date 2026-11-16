// Crystal Imperium: the L menu's BOSSES list (DECISIONS.md D34's L menu). Three pages, JOHTO, KANTO
// and TO RED, list every Gym Leader, both POKéMON LEAGUES, the 25 visiting challengers of the side
// battles (D41) and RED in play order, each Gym followed by the visitor who battles after it. A row
// shows a tick once beaten (a "!" while a visitor's reward waits), the name and the place; the next
// boss on the way to Red is red, a visitor whose battle isn't open yet gray. The info window under the
// list says what the selected row is, what opens it and how it stands. The rows are generated into
// src/data/boss_tracker.h by tools/crystal_imperium/boss_tracker.py, the visitors' from
// side_battles.py's table, so a visitor who moves or opens at another point moves here too.
//
// Everything reads flags the game already keeps (no save data): a Gym's badge, a League's champion
// flag, FLAG_DEFEATED_RED, and a visitor's trainer flags and reward flag, tested as its script tests
// them (data/scripts/side_battles.inc). The screen opens from the L menu like the DexNav (a fade, then
// CB2_ReturnToFieldWithOpenLMenu back to the menu) and looks like Heart & Soul's challenge menu: a top
// bar, a framed list, its own window frame and colours. Its state is allocated on opening and freed on
// leaving, behind one pointer.
#include "global.h"
#include "bg.h"
#include "boss_tracker.h"
#include "event_data.h"
#include "gpu_regs.h"
#include "list_menu.h"
#include "main.h"
#include "malloc.h"
#include "menu.h"
#include "overworld.h"
#include "palette.h"
#include "region_map.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"
#include "caps.h"
#include "constants/opponents.h"
#include "constants/rgb.h"
#include "constants/songs.h"

#include "data/boss_tracker.h"

STATIC_ASSERT(BOSS_TRACKER_ROW_COUNT < BOSS_TRACKER_NO_NEXT, BossTrackerTooManyRows);

// ---------------------------------------------------------------------------------------------------
// The rows' state

u32 BossTracker_GetRowCount(void)
{
    return BOSS_TRACKER_ROW_COUNT;
}

const struct BossTrackerRow *BossTracker_GetRow(u32 row)
{
    return &sBossTrackerRows[row];
}

u32 BossTracker_GetPageStart(u32 page)
{
    return sBossTrackerPageStart[page];
}

u32 BossTracker_GetPage(u32 row)
{
    u32 page;

    for (page = 0; page < BOSS_TRACKER_PAGE_COUNT - 1; page++)
    {
        if (row < sBossTrackerPageStart[page + 1])
            break;
    }
    return page;
}

u32 BossTracker_GetPlaceX(void)
{
    return BOSS_TRACKER_PLACE_X;
}

// The Gyms, the Leagues and RED are on the way to Red; the visitors are optional
bool32 BossTracker_IsRequired(u32 row)
{
    return sBossTrackerRows[row].kind != BOSS_KIND_VISITOR;
}

// A visitor is beaten as its script sees it: its reward flag (the reward given), else any of its
// trainer flags (goto_if_defeated), whatever its gate says now
bool32 BossTracker_IsBeaten(u32 row)
{
    const struct BossTrackerRow *r = &sBossTrackerRows[row];
    u32 i;

    if (FlagGet(r->flag))
        return TRUE;
    if (r->kind != BOSS_KIND_VISITOR)
        return FALSE;
    for (i = 0; i < ARRAY_COUNT(r->trainers) && r->trainers[i] != TRAINER_NONE; i++)
    {
        if (FlagGet(TRAINER_FLAGS_START + r->trainers[i]))
            return TRUE;
    }
    return FALSE;
}

// A visitor's gate, tested as its script tests it: as many badges of either region (GetBadgeCount),
// or its flag. The others have none here.
bool32 BossTracker_IsGateOpen(u32 row)
{
    const struct BossTrackerRow *r = &sBossTrackerRows[row];

    if (r->kind != BOSS_KIND_VISITOR)
        return TRUE;
    if (r->gateKind == BOSS_GATE_BADGES)
        return GetBadgeCount() >= r->gate;
    return FlagGet(r->gate);
}

// The first row on the way to Red not beaten yet, in page order
u32 BossTracker_GetNextRow(void)
{
    u32 row;

    for (row = 0; row < BOSS_TRACKER_ROW_COUNT; row++)
    {
        if (BossTracker_IsRequired(row) && !BossTracker_IsBeaten(row))
            return row;
    }
    return BOSS_TRACKER_NO_NEXT;
}

enum BossTrackerState BossTracker_GetState(u32 row, u32 nextRow)
{
    if (BossTracker_IsRequired(row))
    {
        if (BossTracker_IsBeaten(row))
            return BOSS_STATE_BEATEN;
        return row == nextRow ? BOSS_STATE_NEXT : BOSS_STATE_NOT_YET;
    }
    if (FlagGet(sBossTrackerRows[row].flag))
        return BOSS_STATE_BEATEN;
    if (BossTracker_IsBeaten(row))
        return BOSS_STATE_REWARD;
    return BossTracker_IsGateOpen(row) ? BOSS_STATE_OPEN : BOSS_STATE_LOCKED;
}

u32 BossTracker_CountBeaten(u32 page)
{
    u32 row, count = 0;

    for (row = sBossTrackerPageStart[page]; row < sBossTrackerPageStart[page + 1]; row++)
        count += BossTracker_IsBeaten(row);
    return count;
}

static const u8 sText_Beaten[] = _("BEATEN");
static const u8 sText_BeatenRewardReceived[] = _("BEATEN - REWARD RECEIVED");
static const u8 sText_RewardHer[] = _("BEATEN - REWARD WAITING: TALK TO HER");
static const u8 sText_RewardHim[] = _("BEATEN - REWARD WAITING: TALK TO HIM");
static const u8 sText_OpenHer[] = _("OPEN - TALK TO HER FOR A BATTLE");
static const u8 sText_OpenHim[] = _("OPEN - TALK TO HIM FOR A BATTLE");
static const u8 sText_Locked[] = _("NOT OPEN YET");
static const u8 sText_Next[] = _("NEXT ON THE WAY TO RED");
static const u8 sText_NotYet[] = _("NOT BEATEN YET");

// The info window's second line
const u8 *BossTracker_GetStateText(u32 row, enum BossTrackerState state)
{
    bool32 female = sBossTrackerRows[row].female;

    switch (state)
    {
    case BOSS_STATE_NEXT:
        return sText_Next;
    case BOSS_STATE_BEATEN:
        return BossTracker_IsRequired(row) ? sText_Beaten : sText_BeatenRewardReceived;
    case BOSS_STATE_REWARD:
        return female ? sText_RewardHer : sText_RewardHim;
    case BOSS_STATE_OPEN:
        return female ? sText_OpenHer : sText_OpenHim;
    case BOSS_STATE_LOCKED:
        return sText_Locked;
    case BOSS_STATE_NOT_YET:
    default:
        return sText_NotYet;
    }
}

static const u8 *const sPageNames[BOSS_TRACKER_PAGE_COUNT] =
{
    [BOSS_TRACKER_JOHTO]  = COMPOUND_STRING("JOHTO"),
    [BOSS_TRACKER_KANTO]  = COMPOUND_STRING("KANTO"),
    [BOSS_TRACKER_TO_RED] = COMPOUND_STRING("TO RED"),
};

// The top bar's texts: in the middle (side 0) the page's name and how many of its rows are beaten,
// on the left (side -1) the page L goes to, on the right (side 1) the one R goes to; none at the ends
void BossTracker_BufferTopBarText(u8 *dest, u32 page, s32 side)
{
    *dest = EOS;
    if (side == 0)
    {
        dest = StringCopy(dest, sPageNames[page]);
        *dest++ = CHAR_SPACE;
        *dest++ = CHAR_SPACE;
        dest = ConvertIntToDecimalStringN(dest, BossTracker_CountBeaten(page), STR_CONV_MODE_LEFT_ALIGN, 2);
        *dest++ = CHAR_SLASH;
        dest = ConvertIntToDecimalStringN(dest, sBossTrackerPageStart[page + 1] - sBossTrackerPageStart[page],
                                          STR_CONV_MODE_LEFT_ALIGN, 2);
        StringCopy(dest, COMPOUND_STRING(" BEATEN"));
    }
    else if (side < 0 && page > 0)
    {
        dest = StringCopy(dest, COMPOUND_STRING("{L_BUTTON}"));
        StringCopy(dest, sPageNames[page - 1]);
    }
    else if (side > 0 && page < BOSS_TRACKER_PAGE_COUNT - 1)
    {
        dest = StringCopy(dest, sPageNames[page + 1]);
        StringCopy(dest, COMPOUND_STRING("{R_BUTTON}"));
    }
}

// ---------------------------------------------------------------------------------------------------
// The screen

// Rows shown at once
#define LIST_ROWS 6
#define ROW_HEIGHT 16

enum
{
    WIN_TOPBAR,
    WIN_LIST,
    WIN_INFO,
};

// The window frame's tiles (the player's frame type), after the windows'
#define FRAME_TILE 0x200

// The top bar's texts (FONT_SMALL), 2 pixels down in its 16
#define TOPBAR_Y 2

#define TAG_SCROLL_ARROW 0x2B10
// The scroll arrows' centres on the screen: the list's window starts at (8, 24)
#define ARROW_X        (8 + BOSS_TRACKER_WINDOW_WIDTH - 12)
#define ARROW_TOP_Y    (24 + ROW_HEIGHT / 2)
#define ARROW_BOTTOM_Y (24 + LIST_ROWS * ROW_HEIGHT - ROW_HEIGHT / 2)

struct BossTrackerScreen
{
    u8 page;
    u8 nextRow;     // BOSS_TRACKER_NO_NEXT once Red is beaten
    u8 cursorRow;   // the selected row
    u8 listTaskId;
    u8 arrowTaskId;
    u16 scrollOffset[BOSS_TRACKER_PAGE_COUNT];
    u16 selectedRow[BOSS_TRACKER_PAGE_COUNT];
    struct ListMenuItem items[BOSS_TRACKER_MAX_PAGE_ROWS];
};

EWRAM_DATA static struct BossTrackerScreen *sBossTracker = NULL;

static void CB2_InitBossTracker(void);
static void Task_BossTrackerFadeIn(u8 taskId);
static void Task_BossTrackerInput(u8 taskId);
static void Task_BossTrackerFadeOut(u8 taskId);

static const struct BgTemplate sBgTemplates[] =
{
    {
        .bg = 0,
        .charBaseIndex = 1,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
};

// The top bar, then the list and the info window inside one frame (FRAME_TILE)
static const struct WindowTemplate sWindowTemplates[] =
{
    [WIN_TOPBAR] =
    {
        .bg = 0,
        .tilemapLeft = 0,
        .tilemapTop = 0,
        .width = 30,
        .height = 2,
        .paletteNum = 1,
        .baseBlock = 1,
    },
    [WIN_LIST] =
    {
        .bg = 0,
        .tilemapLeft = 1,
        .tilemapTop = 3,
        .width = BOSS_TRACKER_WINDOW_WIDTH / 8,
        .height = LIST_ROWS * ROW_HEIGHT / 8,
        .paletteNum = 1,
        .baseBlock = 1 + 30 * 2,
    },
    [WIN_INFO] =
    {
        .bg = 0,
        .tilemapLeft = 1,
        .tilemapTop = 3 + LIST_ROWS * ROW_HEIGHT / 8,
        .width = BOSS_TRACKER_WINDOW_WIDTH / 8,
        .height = 4,
        .paletteNum = 1,
        .baseBlock = 1 + 30 * 2 + (BOSS_TRACKER_WINDOW_WIDTH / 8) * (LIST_ROWS * ROW_HEIGHT / 8),
    },
    DUMMY_WIN_TEMPLATE,
};

STATIC_ASSERT(1 + 30 * 2 + (BOSS_TRACKER_WINDOW_WIDTH / 8) * (LIST_ROWS * ROW_HEIGHT / 8 + 4) <= FRAME_TILE, BossTrackerWindowTiles);
STATIC_ASSERT(3 + LIST_ROWS * ROW_HEIGHT / 8 + 4 == DISPLAY_TILE_HEIGHT - 1, BossTrackerFitsTheScreen);

// The challenge menu's background and text colours: 1 white, 2 dark gray, 3 light gray, 4 gray,
// 5/6 orange, 7/8 red, 11/12 green, 15 the top bar's blue
static const u16 sBgColor[] = {RGB(14, 20, 24)};
static const u16 sTextPal[] = INCBIN_U16("graphics/interface/option_menu_text_custom.gbapal");

#define COLOR_WHITE      1
#define COLOR_DARK_GRAY  2
#define COLOR_LIGHT_GRAY 3
#define COLOR_GRAY       4
#define COLOR_TOPBAR     15

static const u8 sColor_TopBar[] = {COLOR_TOPBAR, COLOR_WHITE, COLOR_DARK_GRAY};
static const u8 sColor_Normal[] = {COLOR_WHITE, COLOR_DARK_GRAY, COLOR_LIGHT_GRAY};
static const u8 sColor_Red[]    = {COLOR_WHITE, 8, 7};
static const u8 sColor_Gray[]   = {COLOR_WHITE, COLOR_GRAY, COLOR_LIGHT_GRAY};
static const u8 sColor_Orange[] = {COLOR_WHITE, 6, 5};
static const u8 sColor_Green[]  = {COLOR_WHITE, 12, 11};

// A row's name and place, by state
static const u8 *const sRowColors[BOSS_STATE_COUNT] =
{
    [BOSS_STATE_NOT_YET] = sColor_Normal,
    [BOSS_STATE_NEXT]    = sColor_Red,
    [BOSS_STATE_BEATEN]  = sColor_Normal,
    [BOSS_STATE_REWARD]  = sColor_Normal,
    [BOSS_STATE_OPEN]    = sColor_Normal,
    [BOSS_STATE_LOCKED]  = sColor_Gray,
};

// The info window's state line, by state
static const u8 *const sStateColors[BOSS_STATE_COUNT] =
{
    [BOSS_STATE_NOT_YET] = sColor_Normal,
    [BOSS_STATE_NEXT]    = sColor_Red,
    [BOSS_STATE_BEATEN]  = sColor_Normal,
    [BOSS_STATE_REWARD]  = sColor_Orange,
    [BOSS_STATE_OPEN]    = sColor_Green,
    [BOSS_STATE_LOCKED]  = sColor_Gray,
};

// 8x8 marks in the text colours (0 is left as it is): a tick for a beaten row, a "!" for a waiting
// reward. Two pixels a byte, the left one in the low nibble.
#define MARK_ROW(a, b, c, d, e, f, g, h) ((b) << 4 | (a)), ((d) << 4 | (c)), ((f) << 4 | (e)), ((h) << 4 | (g))
static const u8 sMark_Tick[] =
{
    MARK_ROW( 0,  0,  0,  0,  0,  0,  0,  0),
    MARK_ROW( 0,  0,  0,  0,  0,  0, 12,  0),
    MARK_ROW( 0,  0,  0,  0,  0, 12, 12, 11),
    MARK_ROW(12,  0,  0,  0, 12, 12, 11,  0),
    MARK_ROW(12, 12,  0, 12, 12, 11,  0,  0),
    MARK_ROW( 0, 12, 12, 12, 11,  0,  0,  0),
    MARK_ROW( 0,  0, 12, 11,  0,  0,  0,  0),
    MARK_ROW( 0,  0,  0,  0,  0,  0,  0,  0),
};
static const u8 sMark_Reward[] =
{
    MARK_ROW( 0,  0,  0,  6,  6,  0,  0,  0),
    MARK_ROW( 0,  0,  0,  6,  6,  5,  0,  0),
    MARK_ROW( 0,  0,  0,  6,  6,  5,  0,  0),
    MARK_ROW( 0,  0,  0,  6,  6,  5,  0,  0),
    MARK_ROW( 0,  0,  0,  0,  5,  5,  0,  0),
    MARK_ROW( 0,  0,  0,  6,  6,  0,  0,  0),
    MARK_ROW( 0,  0,  0,  6,  6,  5,  0,  0),
    MARK_ROW( 0,  0,  0,  0,  5,  5,  0,  0),
};
#undef MARK_ROW

static u32 GetPageRowCount(u32 page)
{
    return sBossTrackerPageStart[page + 1] - sBossTrackerPageStart[page];
}

static void PrintRow(u8 windowId, u32 row, u8 y)
{
    enum BossTrackerState state = BossTracker_GetState(row, sBossTracker->nextRow);
    const u8 *color = sRowColors[state];

    if (state == BOSS_STATE_BEATEN)
        BlitBitmapRectToWindow(windowId, sMark_Tick, 0, 0, 8, 8, BOSS_TRACKER_MARK_X, y + 3, 8, 8);
    else if (state == BOSS_STATE_REWARD)
        BlitBitmapRectToWindow(windowId, sMark_Reward, 0, 0, 8, 8, BOSS_TRACKER_MARK_X, y + 3, 8, 8);
    AddTextPrinterParameterized4(windowId, FONT_NORMAL, BOSS_TRACKER_NAME_X, y, 0, 0, color, TEXT_SKIP_DRAW,
                                 sBossTrackerRows[row].name);
    GetMapName(gStringVar1, sBossTrackerRows[row].mapsec, 0);
    AddTextPrinterParameterized4(windowId, FONT_NORMAL, BOSS_TRACKER_PLACE_X, y, 0, 0, color, TEXT_SKIP_DRAW,
                                 gStringVar1);
}

// The list's itemPrintFunc: the whole row (the items' names are empty)
static void ListPrintRow(u8 windowId, u32 itemId, u8 y)
{
    PrintRow(windowId, itemId, y);
}

static void PrintInfo(u32 row)
{
    enum BossTrackerState state = BossTracker_GetState(row, sBossTracker->nextRow);

    FillWindowPixelBuffer(WIN_INFO, PIXEL_FILL(COLOR_WHITE));
    // A line between the list and the info
    FillWindowPixelRect(WIN_INFO, PIXEL_FILL(COLOR_LIGHT_GRAY), 0, 0, BOSS_TRACKER_WINDOW_WIDTH, 1);
    AddTextPrinterParameterized4(WIN_INFO, FONT_NORMAL, BOSS_TRACKER_INFO_X, 2, 0, 0, sColor_Normal, TEXT_SKIP_DRAW,
                                 sBossTrackerRows[row].info);
    AddTextPrinterParameterized4(WIN_INFO, FONT_NORMAL, BOSS_TRACKER_INFO_X, 16, 0, 0, sStateColors[state],
                                 TEXT_SKIP_DRAW, BossTracker_GetStateText(row, state));
    CopyWindowToVram(WIN_INFO, COPYWIN_GFX);
}

// The list's moveCursorFunc
static void ListMoveCursor(s32 itemIndex, bool8 onInit, struct ListMenu *list)
{
    if (!onInit)
        PlaySE(SE_SELECT);
    sBossTracker->scrollOffset[sBossTracker->page] = list->scrollOffset;
    sBossTracker->selectedRow[sBossTracker->page] = list->selectedRow;
    sBossTracker->cursorRow = itemIndex;
    PrintInfo(itemIndex);
}

// The page's name and how many on it are beaten in the middle, the pages L and R go to at the sides
static void PrintTopBar(void)
{
    u32 page = sBossTracker->page;

    FillWindowPixelBuffer(WIN_TOPBAR, PIXEL_FILL(COLOR_TOPBAR));
    BossTracker_BufferTopBarText(gStringVar4, page, 0);
    AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, (DISPLAY_WIDTH - GetStringWidth(FONT_SMALL, gStringVar4, 0)) / 2,
                                 TOPBAR_Y, sColor_TopBar, TEXT_SKIP_DRAW, gStringVar4);
    BossTracker_BufferTopBarText(gStringVar4, page, -1);
    AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, BOSS_TRACKER_TOPBAR_MARGIN, TOPBAR_Y, sColor_TopBar, TEXT_SKIP_DRAW,
                                 gStringVar4);
    BossTracker_BufferTopBarText(gStringVar4, page, 1);
    AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL,
                                 DISPLAY_WIDTH - BOSS_TRACKER_TOPBAR_MARGIN - GetStringWidth(FONT_SMALL, gStringVar4, 0), TOPBAR_Y,
                                 sColor_TopBar, TEXT_SKIP_DRAW, gStringVar4);
    CopyWindowToVram(WIN_TOPBAR, COPYWIN_GFX);
}

static void DrawFrame(void)
{
    u32 bottom = DISPLAY_TILE_HEIGHT - 1, right = DISPLAY_TILE_WIDTH - 1;

    FillBgTilemapBufferRect(0, FRAME_TILE + 0, 0, 2, 1, 1, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 1, 1, 2, right - 1, 1, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 2, right, 2, 1, 1, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 3, 0, 3, 1, bottom - 3, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 5, right, 3, 1, bottom - 3, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 6, 0, bottom, 1, 1, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 7, 1, bottom, right - 1, 1, 7);
    FillBgTilemapBufferRect(0, FRAME_TILE + 8, right, bottom, 1, 1, 7);
}

static void CreatePageList(void)
{
    struct ListMenuTemplate template;
    u32 page = sBossTracker->page, start = sBossTrackerPageStart[page], count = GetPageRowCount(page), i;

    for (i = 0; i < count; i++)
    {
        sBossTracker->items[i].name = gText_EmptyString2;
        sBossTracker->items[i].id = start + i;
    }
    memset(&template, 0, sizeof(template));
    template.items = sBossTracker->items;
    template.moveCursorFunc = ListMoveCursor;
    template.itemPrintFunc = ListPrintRow;
    template.totalItems = count;
    template.maxShowed = LIST_ROWS;
    template.windowId = WIN_LIST;
    template.item_X = BOSS_TRACKER_NAME_X;
    template.cursor_X = 0;
    template.upText_Y = 1;
    template.cursorPal = COLOR_DARK_GRAY;
    template.fillValue = COLOR_WHITE;
    template.cursorShadowPal = COLOR_LIGHT_GRAY;
    template.scrollMultiple = LIST_NO_MULTIPLE_SCROLL;
    template.fontId = FONT_NORMAL;
    template.cursorKind = CURSOR_BLACK_ARROW;
    sBossTracker->listTaskId = ListMenuInit(&template, sBossTracker->scrollOffset[page], sBossTracker->selectedRow[page]);
    // The scroll arrows at the right of the list's first and last rows, clear of the names and places
    if (count > LIST_ROWS)
        sBossTracker->arrowTaskId = AddScrollIndicatorArrowPairParameterized(SCROLL_ARROW_UP, ARROW_X, ARROW_TOP_Y,
                                                                             ARROW_BOTTOM_Y, count - LIST_ROWS,
                                                                             TAG_SCROLL_ARROW, TAG_SCROLL_ARROW,
                                                                             &sBossTracker->scrollOffset[page]);
    else
        sBossTracker->arrowTaskId = TASK_NONE;
}

static void DestroyPageList(void)
{
    DestroyListMenuTask(sBossTracker->listTaskId, &sBossTracker->scrollOffset[sBossTracker->page],
                        &sBossTracker->selectedRow[sBossTracker->page]);
    if (sBossTracker->arrowTaskId != TASK_NONE)
    {
        RemoveScrollIndicatorArrowPair(sBossTracker->arrowTaskId);
        sBossTracker->arrowTaskId = TASK_NONE;
    }
}

// The list of a page opens with the given row on the screen, as near its middle as it can be
static void PlaceCursor(u32 page, u32 index)
{
    u32 count = GetPageRowCount(page), shown = min(count, LIST_ROWS), scroll = 0;

    if (index > (shown - 1) / 2)
        scroll = index - (shown - 1) / 2;
    if (scroll > count - shown)
        scroll = count - shown;
    sBossTracker->scrollOffset[page] = scroll;
    sBossTracker->selectedRow[page] = index - scroll;
}

// The screen opens on the next boss, or on RED once he is beaten too. Each page keeps its place
// while the screen is open.
static void PlaceCursors(void)
{
    u32 row = sBossTracker->nextRow, page;

    if (row == BOSS_TRACKER_NO_NEXT)
        row = BOSS_TRACKER_ROW_COUNT - 1;
    for (page = 0; page < BOSS_TRACKER_PAGE_COUNT; page++)
        PlaceCursor(page, 0);
    sBossTracker->page = BossTracker_GetPage(row);
    PlaceCursor(sBossTracker->page, row - sBossTrackerPageStart[sBossTracker->page]);
}

static void SwitchPage(s32 delta)
{
    s32 page = sBossTracker->page + delta;

    if (page < 0 || page >= BOSS_TRACKER_PAGE_COUNT)
        return;
    PlaySE(SE_SELECT);
    DestroyPageList();
    sBossTracker->page = page;
    CreatePageList();
    PrintTopBar();
}

static void VBlankCB_BossTracker(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

// Windows are copied to VRAM as they are drawn (CopyWindowToVram), nothing is scheduled: after the
// last frame frees them there is nothing left to copy
static void CB2_BossTracker(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void CB2_InitBossTracker(void)
{
    switch (gMain.state)
    {
    case 0:
    default:
        SetVBlankCallback(NULL);
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, OAM, OAM_SIZE);
        DmaClear16(3, PLTT, PLTT_SIZE);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sBgTemplates, ARRAY_COUNT(sBgTemplates));
        ResetBgPositions();
        InitWindows(sWindowTemplates);
        DeactivateAllTextPrinters();
        SetGpuReg(REG_OFFSET_BLDCNT, 0);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
        ShowBg(0);
        gMain.state = 1;
        break;
    case 1:
        ResetPaletteFade();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        FreeAllSpritePalettes();
        gMain.state++;
        break;
    case 2:
        LoadBgTiles(0, GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->tiles, 0x120, FRAME_TILE);
        LoadPalette(sBgColor, BG_PLTT_ID(0), sizeof(sBgColor));
        LoadPalette(sTextPal, BG_PLTT_ID(1), sizeof(sTextPal));
        LoadPalette(GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->pal, BG_PLTT_ID(7), PLTT_SIZE_4BPP);
        gMain.state++;
        break;
    case 3:
        sBossTracker->nextRow = BossTracker_GetNextRow();
        sBossTracker->arrowTaskId = TASK_NONE;
        PlaceCursors();
        DrawFrame();
        PutWindowTilemap(WIN_TOPBAR);
        PutWindowTilemap(WIN_INFO);
        PrintTopBar();
        CreatePageList();
        CopyBgTilemapBufferToVram(0);
        gMain.state++;
        break;
    case 4:
        CreateTask(Task_BossTrackerFadeIn, 0);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetVBlankCallback(VBlankCB_BossTracker);
        SetMainCallback2(CB2_BossTracker);
        break;
    }
}

static void Task_BossTrackerFadeIn(u8 taskId)
{
    if (!gPaletteFade.active)
        gTasks[taskId].func = Task_BossTrackerInput;
}

// L/R (or LEFT/RIGHT) change the page, UP/DOWN move in the list, B goes back to the L menu
static void Task_BossTrackerInput(u8 taskId)
{
    if (JOY_NEW(L_BUTTON | DPAD_LEFT))
    {
        SwitchPage(-1);
        return;
    }
    if (JOY_NEW(R_BUTTON | DPAD_RIGHT))
    {
        SwitchPage(1);
        return;
    }
    if (ListMenu_ProcessInput(sBossTracker->listTaskId) == LIST_CANCEL)
    {
        PlaySE(SE_SELECT);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
        gTasks[taskId].func = Task_BossTrackerFadeOut;
    }
}

static void Task_BossTrackerFadeOut(u8 taskId)
{
    if (gPaletteFade.active)
        return;
    DestroyPageList();
    FreeAllWindowBuffers();
    FREE_AND_SET_NULL(sBossTracker);
    SetMainCallback2(CB2_ReturnToFieldWithOpenLMenu);
    DestroyTask(taskId);
}

// The L menu's BOSSES, after its fade to black (as Task_OpenDexNavFromLMenu): B comes back to the menu
void Task_OpenBossTrackerFromLMenu(u8 taskId)
{
    if (gPaletteFade.active)
        return;
    CleanupOverworldWindowsAndTilemaps();
    sBossTracker = AllocZeroed(sizeof(*sBossTracker));
    if (sBossTracker == NULL)
        SetMainCallback2(CB2_ReturnToFieldWithOpenLMenu);
    else
        SetMainCallback2(CB2_InitBossTracker);
    DestroyTask(taskId);
}
