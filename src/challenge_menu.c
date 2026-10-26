// Platinum Imperium: the challenge menu, shown before a new game starts and on the settings PC.
// Crystal Imperium's challenge menu (from Pokemon Heart & Soul) with the two tabs this game has:
// FEATURES and DIFFICULTY.
#include "global.h"
#include "bg.h"
#include "event_data.h"
#include "gpu_regs.h"
#include "international_string_util.h"
#include "list_menu.h"
#include "main.h"
#include "malloc.h"
#include "menu.h"
#include "menu_helpers.h"
#include "new_game.h"
#include "palette.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "window.h"
#include "constants/rgb.h"
#include "constants/songs.h"
#include "overworld.h"
#include "script.h"
#include "challenge_menu.h"

enum {
    TAB_FEATURES,
    TAB_DIFFICULTY,
    TAB_COUNT,
};

enum {
    ITEM_FEATURES_EASY_CATCH,
    ITEM_FEATURES_WILD_VARIETY,
    ITEM_FEATURES_AUTO_RUN,
    ITEM_FEATURES_NEXT,
    ITEM_FEATURES_COUNT,
};

enum {
    ITEM_DIFFICULTY_PRESET,
    ITEM_DIFFICULTY_MIN_GRINDING,
    ITEM_DIFFICULTY_LEVEL_CAP,
    ITEM_DIFFICULTY_EXP_MULTIPLIER,
    ITEM_DIFFICULTY_SAVE,
    ITEM_DIFFICULTY_COUNT,
};

#define MAX_ITEMS_PER_TAB 8
#define ITEMS_VISIBLE 5
#define Y_DIFF 16

struct ChallengeMenuItem
{
    const u8 *name;
    const u8 *const *descriptions;
    u8 numChoices;
    const u8 *const *choiceNames;
};

struct ChallengeMenuState
{
    u8 currentTab;
    u8 listTaskId;
    u8 arrowTaskId;
    u16 scrollOffset[TAB_COUNT];
    u16 selectedRow[TAB_COUNT];
    u8 selections[TAB_COUNT * MAX_ITEMS_PER_TAB];
};

static EWRAM_DATA struct ChallengeMenuState *sMenu = NULL;
static EWRAM_DATA bool8 sIsInitialSetup = FALSE;
// Set when the menu shown before a new game was confirmed: NewGameInitData keeps its choices
static EWRAM_DATA bool8 sNewGameSettingsChosen = FALSE;

// =============================================================================
// Window / BG templates
// =============================================================================

enum {
    WIN_TOPBAR,
    WIN_OPTIONS,
    WIN_DESCRIPTION,
    WIN_CONFIRM_MSG,
};

static const struct WindowTemplate sWinTemplates[] = {
    [WIN_TOPBAR] = {
        .bg = 1,
        .tilemapLeft = 0,
        .tilemapTop = 0,
        .width = 30,
        .height = 2,
        .paletteNum = 1,
        .baseBlock = 2,
    },
    [WIN_OPTIONS] = {
        .bg = 0,
        .tilemapLeft = 2,
        .tilemapTop = 3,
        .width = 26,
        .height = 10,
        .paletteNum = 1,
        .baseBlock = 62,
    },
    [WIN_DESCRIPTION] = {
        .bg = 1,
        .tilemapLeft = 2,
        .tilemapTop = 15,
        .width = 26,
        .height = 4,
        .paletteNum = 1,
        .baseBlock = 500,
    },
    [WIN_CONFIRM_MSG] = {
        .bg = 1,
        .tilemapLeft = 2,
        .tilemapTop = 15,
        .width = 20,
        .height = 4,
        .paletteNum = 1,
        .baseBlock = 604,
    },
    DUMMY_WIN_TEMPLATE,
};

static const struct BgTemplate sBgTemplates[] = {
    {
        .bg = 0,
        .charBaseIndex = 1,
        .mapBaseIndex = 30,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 1,
        .baseTile = 0,
    },
    {
        .bg = 1,
        .charBaseIndex = 1,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0,
    },
};

static const u16 sBgPal[] = {RGB(14, 20, 24)};
static const u16 sTextPal[] = INCBIN_U16("graphics/interface/option_menu_text_custom.gbapal");

// Frame tile IDs — loaded from window frame tileset at base 0x1A2
#define TILE_TOP_CORNER_L 0x1A2
#define TILE_TOP_EDGE     0x1A3
#define TILE_TOP_CORNER_R 0x1A4
#define TILE_LEFT_EDGE    0x1A5
#define TILE_RIGHT_EDGE   0x1A7
#define TILE_BOT_CORNER_L 0x1A8
#define TILE_BOT_EDGE     0x1A9
#define TILE_BOT_CORNER_R 0x1AA

#define TEXT_COLOR_OPTIONS_WHITE              1
#define TEXT_COLOR_OPTIONS_GRAY_FG            2
#define TEXT_COLOR_OPTIONS_GRAY_SHADOW        3
#define TEXT_COLOR_OPTIONS_GRAY_LIGHT_FG      4
#define TEXT_COLOR_OPTIONS_ORANGE_FG          5
#define TEXT_COLOR_OPTIONS_ORANGE_SHADOW      6
#define TEXT_COLOR_OPTIONS_RED_FG             7
#define TEXT_COLOR_OPTIONS_RED_SHADOW         8
#define TEXT_COLOR_OPTIONS_GREEN_FG           9
#define TEXT_COLOR_OPTIONS_GREEN_SHADOW      10
#define TEXT_COLOR_OPTIONS_GREEN_DARK_FG     11
#define TEXT_COLOR_OPTIONS_GREEN_DARK_SHADOW 12
#define TEXT_COLOR_OPTIONS_RED_DARK_FG       13
#define TEXT_COLOR_OPTIONS_RED_DARK_SHADOW   14

// =============================================================================
// Strings and tab tables
// =============================================================================

static const u8 *const sChoices_OffOn[] = {
    COMPOUND_STRING("OFF"),
    COMPOUND_STRING("ON"),
};

static const u8 sText_TopBar_Left[]   = _("{L_BUTTON}PREVIOUS");
static const u8 sText_TopBar_Right[]  = _("{R_BUTTON}NEXT");
static const u8 sText_TopBar_Save[]   = _("{R_BUTTON}SAVE");
static const u8 sText_TopBar_Cancel[] = _("{B_BUTTON}CANCEL");
static const u8 sText_ConfirmSave[] = COMPOUND_STRING("Confirm your choices?");

static const u8 *const sDesc_EasyCatch[] = {
    COMPOUND_STRING("Catch rates work as usual."),
    COMPOUND_STRING("Every POKé BALL catches the wild\n{PKMN} on the first throw."),
};

static const u8 *const sChoices_WildVariety[] = {
    COMPOUND_STRING("OFF"),
    COMPOUND_STRING("15%"),
    COMPOUND_STRING("30%"),
    COMPOUND_STRING("60%"),
};
static const u8 *const sDesc_WildVariety[] = {
    COMPOUND_STRING("Only the usual {PKMN} of each area."),
    COMPOUND_STRING("15% of wild {PKMN} can be any {PKMN}\nof Gen 1-9, at the area's level."),
    COMPOUND_STRING("30% of wild {PKMN} can be any {PKMN}\nof Gen 1-9, at the area's level."),
    COMPOUND_STRING("60% of wild {PKMN} can be any {PKMN}\nof Gen 1-9, at the area's level."),
};
// The menu lists OFF / 15% / 30% / 60%; the save stores 30% as 0 (see src/wild_variety.c)
static const u8 sWildVarietyFromMenu[] = { 2, 3, 0, 1 };
static const u8 sWildVarietyToMenu[] = { 2, 3, 0, 1 };

static const u8 *const sDesc_AutoRun[] = {
    COMPOUND_STRING("Hold B to run."),
    COMPOUND_STRING("Run without holding B. Hold B\nto walk. Also in the L menu."),
};

static const u8 *const sDesc_FeaturesNext[] = {
    COMPOUND_STRING("Continue to the difficulty options."),
};

static const struct ChallengeMenuItem sTabItems_Features[] = {
    [ITEM_FEATURES_EASY_CATCH] = {
        .name         = COMPOUND_STRING("EASY CATCH"),
        .descriptions = sDesc_EasyCatch,
        .numChoices   = 2,
        .choiceNames  = sChoices_OffOn,
    },
    [ITEM_FEATURES_WILD_VARIETY] = {
        .name         = COMPOUND_STRING("WILD VARIETY"),
        .descriptions = sDesc_WildVariety,
        .numChoices   = 4,
        .choiceNames  = sChoices_WildVariety,
    },
    [ITEM_FEATURES_AUTO_RUN] = {
        .name         = COMPOUND_STRING("AUTO RUN"),
        .descriptions = sDesc_AutoRun,
        .numChoices   = 2,
        .choiceNames  = sChoices_OffOn,
    },
    [ITEM_FEATURES_NEXT] = {
        .name         = COMPOUND_STRING("NEXT"),
        .descriptions = sDesc_FeaturesNext,
        .numChoices   = 0,
        .choiceNames  = NULL,
    },
};

static const u8 *const sChoices_DifficultyPreset[] = {
    COMPOUND_STRING("EASY"),
    COMPOUND_STRING("NORMAL"),
    COMPOUND_STRING("HARD"),
};
static const u8 *const sDesc_DifficultyPreset[] = {
    COMPOUND_STRING("-10% levels (not bosses), trainers\ncan't use items."),
    COMPOUND_STRING("Platinum Imperium as designed:\ncompetitive teams at fair levels."),
    COMPOUND_STRING("+10% levels (not bosses), HARD caps,\nSET style, no Bag in trainer battles."),
};
// The menu lists EASY / NORMAL / HARD; the save stores NORMAL as 0
static const u8 sDifficultyPresetFromMenu[] = { CHALLENGE_DIFFICULTY_EASY, CHALLENGE_DIFFICULTY_NORMAL, CHALLENGE_DIFFICULTY_HARD };
static const u8 sDifficultyPresetToMenu[] = { [CHALLENGE_DIFFICULTY_NORMAL] = 1, [CHALLENGE_DIFFICULTY_EASY] = 0, [CHALLENGE_DIFFICULTY_HARD] = 2 };

static const u8 *const sDesc_MinGrinding[] = {
    COMPOUND_STRING("IVs and EVs work as usual for all\n{PKMN}."),
    COMPOUND_STRING("All {PKMN} battle as if they had\nperfect IVs and zero EVs. No grind!"),
};

static const u8 *const sChoices_LevelCap[] = {
    COMPOUND_STRING("OFF"),
    COMPOUND_STRING("NORMAL"),
    COMPOUND_STRING("HARD"),
};
static const u8 *const sDesc_LevelCap[] = {
    COMPOUND_STRING("No level cap. Overleveling possible.\nBosses use the NORMAL caps."),
    COMPOUND_STRING("Max level 15, 24, 33, 42, 50, 58, 66,\n75, 85. Bosses are at the cap."),
    COMPOUND_STRING("Max level 12, 21, 30, 39, 47, 55, 63,\n72, 85. Bosses are at the cap."),
};

static const u8 *const sChoices_ExpMult[] = {
    COMPOUND_STRING("x1.0"),
    COMPOUND_STRING("x1.5"),
    COMPOUND_STRING("x2.0"),
    COMPOUND_STRING("x0.0"),
};
static const u8 *const sDesc_ExpMult[] = {
    COMPOUND_STRING("{PKMN} gain normal EXP. Points."),
    COMPOUND_STRING("{PKMN} gain 50 percent more EXP.\nPoints!"),
    COMPOUND_STRING("{PKMN} gain double EXP. Points!"),
    COMPOUND_STRING("{PKMN} gain ZERO EXP. Points!!!"),
};

static const u8 *const sDesc_SaveExit[] = { COMPOUND_STRING("Save choices and continue...") };

static const struct ChallengeMenuItem sTabItems_Difficulty[] = {
    [ITEM_DIFFICULTY_PRESET] = {
        .name         = COMPOUND_STRING("DIFFICULTY"),
        .descriptions = sDesc_DifficultyPreset,
        .numChoices   = 3,
        .choiceNames  = sChoices_DifficultyPreset,
    },
    [ITEM_DIFFICULTY_MIN_GRINDING] = {
        .name         = COMPOUND_STRING("MIN. GRINDING"),
        .descriptions = sDesc_MinGrinding,
        .numChoices   = 2,
        .choiceNames  = sChoices_OffOn,
    },
    [ITEM_DIFFICULTY_LEVEL_CAP] = {
        .name         = COMPOUND_STRING("LEVEL CAP"),
        .descriptions = sDesc_LevelCap,
        .numChoices   = 3,
        .choiceNames  = sChoices_LevelCap,
    },
    [ITEM_DIFFICULTY_EXP_MULTIPLIER] = {
        .name         = COMPOUND_STRING("EXP. MULTIPLIER"),
        .descriptions = sDesc_ExpMult,
        .numChoices   = 4,
        .choiceNames  = sChoices_ExpMult,
    },
    [ITEM_DIFFICULTY_SAVE] = {
        .name         = COMPOUND_STRING("SAVE"),
        .descriptions = sDesc_SaveExit,
        .numChoices   = 0,
        .choiceNames  = NULL,
    },
};

struct TabDef
{
    const u8 *tabName;
    const struct ChallengeMenuItem *items;
    u8 count;
};

static const struct TabDef sTabs[TAB_COUNT] = {
    [TAB_FEATURES]   = { COMPOUND_STRING("FEATURES"),   sTabItems_Features,   ITEM_FEATURES_COUNT },
    [TAB_DIFFICULTY] = { COMPOUND_STRING("DIFFICULTY"), sTabItems_Difficulty, ITEM_DIFFICULTY_COUNT },
};

// =============================================================================
// Forward declarations
// =============================================================================

static void MainCB2(void);
static void VBlankCB(void);
static void Task_FadeIn(u8 taskId);
static void Task_ProcessInput(u8 taskId);
static void Task_Save(u8 taskId);
static void Task_ConfirmSaveYes(u8 taskId);
static void Task_ConfirmSaveNo(u8 taskId);
static void Task_FadeOut(u8 taskId);
static void InitListMenu(void);
static void DestroyCurrentListMenu(void);
static void DrawTopBar(void);
static void DrawDescription(void);
static void DrawBgFrames(void);
static void DrawConfirmWindowFrame(void);
static void ChallengeMenu_MoveCursorFunc(s32 itemIndex, bool8 onInit, struct ListMenu *list);
static void ChallengeMenu_ItemPrintFunc(u8 windowId, u32 itemId, u8 y);

static EWRAM_DATA struct ListMenuItem sListItems[MAX_ITEMS_PER_TAB] = {0};

// =============================================================================
// Helpers
// =============================================================================

static u8 *GetSelectionPtr(u8 tab, u8 itemIndex)
{
    return &sMenu->selections[tab * MAX_ITEMS_PER_TAB + itemIndex];
}

static u8 GetCurrentTabItemCount(void)
{
    return sTabs[sMenu->currentTab].count;
}

static const struct ChallengeMenuItem *GetCurrentTabItems(void)
{
    return sTabs[sMenu->currentTab].items;
}

// Later in the game, DIFFICULTY and LEVEL CAP can only be made easier
static bool8 IsOneWayDown(u8 tab, u8 itemIndex)
{
    if (sIsInitialSetup)
        return FALSE;
    return tab == TAB_DIFFICULTY && itemIndex == ITEM_DIFFICULTY_LEVEL_CAP;
}

static void MainCB2(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    UpdatePaletteFade();
}

static void VBlankCB(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

// =============================================================================
// Drawing
// =============================================================================

static void HighlightRow(void)
{
    u16 scrollOffset, selectedRow;
    ListMenuGetScrollAndRow(sMenu->listTaskId, &scrollOffset, &selectedRow);
    SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(Y_DIFF, 224));
    SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(selectedRow * Y_DIFF + 24, selectedRow * Y_DIFF + 40));
}

static void DrawRightSideChoiceText(const u8 *text, int x, int y, bool8 chosen)
{
    u8 color[3];
    color[0] = TEXT_COLOR_TRANSPARENT;
    color[1] = chosen ? TEXT_COLOR_OPTIONS_RED_FG : TEXT_COLOR_OPTIONS_GRAY_FG;
    color[2] = chosen ? TEXT_COLOR_OPTIONS_RED_SHADOW : TEXT_COLOR_OPTIONS_GRAY_SHADOW;
    AddTextPrinterParameterized4(WIN_OPTIONS, FONT_NORMAL, x, y, 0, 0, color, TEXT_SKIP_DRAW, text);
}

static int GetMiddleX(const u8 *txt1, const u8 *txt2, const u8 *txt3)
{
    int widthLeft = GetStringWidth(FONT_NORMAL, txt1, 0);
    int widthMid = GetStringWidth(FONT_NORMAL, txt2, 0);
    int widthRight = GetStringWidth(FONT_NORMAL, txt3, 0);
    widthMid -= (198 - 104);
    return (widthLeft - widthMid - widthRight) / 2 + 104;
}

static void DrawChoices_Two(const u8 *const *strings, int selection, int y)
{
    DrawRightSideChoiceText(strings[0], 104, y + 1, selection == 0);
    DrawRightSideChoiceText(strings[1], GetStringRightAlignXOffset(FONT_NORMAL, strings[1], 198), y + 1, selection == 1);
}

static void DrawChoices_Three(const u8 *const *strings, int selection, int y)
{
    int xMid = GetMiddleX(strings[0], strings[1], strings[2]);
    DrawRightSideChoiceText(strings[0], 104, y + 1, selection == 0);
    DrawRightSideChoiceText(strings[1], xMid, y + 1, selection == 1);
    DrawRightSideChoiceText(strings[2], GetStringRightAlignXOffset(FONT_NORMAL, strings[2], 198), y + 1, selection == 2);
}

static void DrawChoices_Four(const u8 *const *strings, int selection, int y)
{
    static const u8 orders[][3] = { {0, 1, 2}, {0, 1, 2}, {1, 2, 3}, {1, 2, 3} };
    const u8 *order = orders[selection];
    int xMid = GetMiddleX(strings[order[0]], strings[order[1]], strings[order[2]]);
    DrawRightSideChoiceText(strings[order[0]], 104, y + 1, selection == order[0]);
    DrawRightSideChoiceText(strings[order[1]], xMid, y + 1, selection == order[1]);
    DrawRightSideChoiceText(strings[order[2]], GetStringRightAlignXOffset(FONT_NORMAL, strings[order[2]], 198), y + 1, selection == order[2]);
}

static void ChallengeMenu_MoveCursorFunc(s32 itemIndex, bool8 onInit, struct ListMenu *list)
{
    if (!onInit)
        PlaySE(SE_SELECT);

    ListMenuGetScrollAndRow(sMenu->listTaskId, &sMenu->scrollOffset[sMenu->currentTab], &sMenu->selectedRow[sMenu->currentTab]);
    HighlightRow();
    DrawDescription();
}

static void ChallengeMenu_ItemPrintFunc(u8 windowId, u32 itemId, u8 y)
{
    const struct ChallengeMenuItem *items = GetCurrentTabItems();
    u8 sel;

    if (itemId >= GetCurrentTabItemCount())
        return;
    if (items[itemId].numChoices == 0 || items[itemId].choiceNames == NULL)
        return;

    sel = *GetSelectionPtr(sMenu->currentTab, itemId);
    if (sel >= items[itemId].numChoices)
        sel = 0;

    switch (items[itemId].numChoices)
    {
    case 2:
        DrawChoices_Two(items[itemId].choiceNames, sel, y);
        break;
    case 3:
        DrawChoices_Three(items[itemId].choiceNames, sel, y);
        break;
    case 4:
        DrawChoices_Four(items[itemId].choiceNames, sel, y);
        break;
    }
}

static void InitListMenu(void)
{
    struct ListMenuTemplate template;
    const struct ChallengeMenuItem *items = GetCurrentTabItems();
    u8 count = GetCurrentTabItemCount();
    u8 i;

    for (i = 0; i < count; i++)
    {
        sListItems[i].name = items[i].name;
        sListItems[i].id = i;
    }

    memset(&template, 0, sizeof(template));
    template.items = sListItems;
    template.moveCursorFunc = ChallengeMenu_MoveCursorFunc;
    template.itemPrintFunc = ChallengeMenu_ItemPrintFunc;
    template.totalItems = count;
    template.maxShowed = (count < ITEMS_VISIBLE) ? count : ITEMS_VISIBLE;
    template.windowId = WIN_OPTIONS;
    template.header_X = 0;
    template.item_X = 8;
    template.cursor_X = 0;
    template.upText_Y = 1;
    template.cursorPal = TEXT_COLOR_OPTIONS_ORANGE_FG;
    template.fillValue = 1;
    template.cursorShadowPal = TEXT_COLOR_OPTIONS_ORANGE_SHADOW;
    template.lettersSpacing = 0;
    template.itemVerticalPadding = 0;
    template.scrollMultiple = LIST_NO_MULTIPLE_SCROLL;
    template.fontId = FONT_NORMAL;
    template.cursorKind = CURSOR_INVISIBLE;

    sMenu->listTaskId = ListMenuInit(&template,
        sMenu->scrollOffset[sMenu->currentTab],
        sMenu->selectedRow[sMenu->currentTab]);

    HighlightRow();

    if (count > ITEMS_VISIBLE)
    {
        sMenu->arrowTaskId = AddScrollIndicatorArrowPairParameterized(
            SCROLL_ARROW_UP, 240 / 2, 20, 110,
            count - ITEMS_VISIBLE,
            110, 110,
            &sMenu->scrollOffset[sMenu->currentTab]);
    }
    else
    {
        sMenu->arrowTaskId = TASK_NONE;
    }
}

static void DestroyCurrentListMenu(void)
{
    DestroyListMenuTask(sMenu->listTaskId,
        &sMenu->scrollOffset[sMenu->currentTab],
        &sMenu->selectedRow[sMenu->currentTab]);

    if (sMenu->arrowTaskId != TASK_NONE)
    {
        RemoveScrollIndicatorArrowPair(sMenu->arrowTaskId);
        sMenu->arrowTaskId = TASK_NONE;
    }
}

static void DrawTopBar(void)
{
    const u8 color[3] = { TEXT_DYNAMIC_COLOR_6, TEXT_COLOR_OPTIONS_WHITE, TEXT_COLOR_OPTIONS_GRAY_FG };
    const u8 *tabName = sTabs[sMenu->currentTab].tabName;
    int width = GetStringWidth(FONT_SMALL, tabName, 0) / 2;
    int right = 240 - GetStringWidth(FONT_SMALL, sText_TopBar_Right, 0) - 5;

    FillWindowPixelBuffer(WIN_TOPBAR, PIXEL_FILL(15));

    AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, 120 - width, 1, color, 0, tabName);

    if (sMenu->currentTab > 0)
        AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, 5, 1, color, 0, sText_TopBar_Left);
    if (sMenu->currentTab < TAB_COUNT - 1)
        AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, right, 1, color, 0, sText_TopBar_Right);
    else
        AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, right, 1, color, 0, sText_TopBar_Save);
    if (!sIsInitialSetup)
    {
        int cancelX = (120 + width + right) / 2 - GetStringWidth(FONT_SMALL, sText_TopBar_Cancel, 0) / 2;
        AddTextPrinterParameterized3(WIN_TOPBAR, FONT_SMALL, cancelX, 1, color, 0, sText_TopBar_Cancel);
    }

    PutWindowTilemap(WIN_TOPBAR);
    CopyWindowToVram(WIN_TOPBAR, COPYWIN_FULL);
}

static void DrawDescription(void)
{
    const u8 color[3] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_OPTIONS_GRAY_FG, TEXT_COLOR_OPTIONS_GRAY_SHADOW };
    const struct ChallengeMenuItem *items = GetCurrentTabItems();
    u16 scrollOffset, selectedRow;
    u8 itemIndex;

    ListMenuGetScrollAndRow(sMenu->listTaskId, &scrollOffset, &selectedRow);
    itemIndex = scrollOffset + selectedRow;

    FillWindowPixelBuffer(WIN_DESCRIPTION, PIXEL_FILL(1));
    if (itemIndex < GetCurrentTabItemCount() && items[itemIndex].descriptions != NULL)
    {
        u8 sel = *GetSelectionPtr(sMenu->currentTab, itemIndex);
        if (sel >= items[itemIndex].numChoices)
            sel = 0;
        AddTextPrinterParameterized4(WIN_DESCRIPTION, FONT_NORMAL, 8, 1, 0, 0, color, TEXT_SKIP_DRAW, items[itemIndex].descriptions[sel]);
    }
    CopyWindowToVram(WIN_DESCRIPTION, COPYWIN_FULL);
}

static void DrawBgFrames(void)
{
    // Outer frame — top edge at row 2, shared side edges rows 3-18
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_L,  1,  2,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_EDGE,      2,  2, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_R, 28,  2,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_LEFT_EDGE,     1,  3,  1, 16,  7);
    FillBgTilemapBufferRect(1, TILE_RIGHT_EDGE,   28,  3,  1, 16,  7);

    // Horizontal divider between options and description
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_L,  1, 13,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_EDGE,      2, 13, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_R, 28, 13,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_L,  1, 14,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_EDGE,      2, 14, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_R, 28, 14,  1,  1,  7);

    // Bottom edge at row 19
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_L,  1, 19,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_EDGE,      2, 19, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_R, 28, 19,  1,  1,  7);

    CopyBgTilemapBufferToVram(1);
}

static void DrawConfirmWindowFrame(void)
{
    // Options box
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_L,  1,  2,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_EDGE,      2,  2, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_R, 28,  2,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_LEFT_EDGE,     1,  3,  1, 10,  7);
    FillBgTilemapBufferRect(1, TILE_RIGHT_EDGE,   28,  3,  1, 10,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_L,  1, 13,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_EDGE,      2, 13, 26,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_R, 28, 13,  1,  1,  7);

    // Confirm message box border (cols 1-22, leaves cols 23-28 for yes/no border)
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_L,  1, 14,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_EDGE,      2, 14, 21,  1,  7);
    FillBgTilemapBufferRect(1, TILE_TOP_CORNER_R, 22, 14,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_LEFT_EDGE,     1, 15,  1,  4,  7);
    FillBgTilemapBufferRect(1, TILE_RIGHT_EDGE,   22, 15,  1,  4,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_L,  1, 19,  1,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_EDGE,      2, 19, 21,  1,  7);
    FillBgTilemapBufferRect(1, TILE_BOT_CORNER_R, 22, 19,  1,  1,  7);

    CopyBgTilemapBufferToVram(1);
}

// =============================================================================
// Input
// =============================================================================

static void SwitchTab(u8 taskId, s8 direction)
{
    s8 newTab = sMenu->currentTab + direction;

    if (newTab < 0 || newTab > TAB_COUNT)
        return;
    if (newTab == TAB_COUNT)
    {
        JumpListMenuToBottom(sMenu->listTaskId);
        gTasks[taskId].func = Task_Save;
        return;
    }

    DestroyCurrentListMenu();
    FillWindowPixelBuffer(WIN_OPTIONS, PIXEL_FILL(1));
    sMenu->currentTab = newTab;
    InitListMenu();
    DrawTopBar();
    DrawDescription();
    CopyWindowToVram(WIN_OPTIONS, COPYWIN_GFX);
    PlaySE(SE_SELECT);
}

static void ProcessLeftRight(void)
{
    const struct ChallengeMenuItem *items = GetCurrentTabItems();
    u16 scrollOffset, selectedRow;
    u8 itemIndex, prev, *sel;

    ListMenuGetScrollAndRow(sMenu->listTaskId, &scrollOffset, &selectedRow);
    itemIndex = scrollOffset + selectedRow;
    if (itemIndex >= GetCurrentTabItemCount() || items[itemIndex].numChoices == 0)
        return;

    sel = GetSelectionPtr(sMenu->currentTab, itemIndex);
    prev = *sel;

    if (JOY_NEW(DPAD_RIGHT))
        *sel = (*sel < items[itemIndex].numChoices - 1) ? *sel + 1 : 0;
    else if (JOY_NEW(DPAD_LEFT))
        *sel = (*sel > 0) ? *sel - 1 : items[itemIndex].numChoices - 1;

    // LEVEL CAP: OFF < NORMAL < HARD, so "down" (easier) is a lower value
    if (*sel != prev && IsOneWayDown(sMenu->currentTab, itemIndex) && *sel > prev)
    {
        *sel = prev;
        PlaySE(SE_FAILURE);
        return;
    }

    if (*sel != prev)
    {
        // HARD difficulty also selects the HARD level caps
        if (sMenu->currentTab == TAB_DIFFICULTY && itemIndex == ITEM_DIFFICULTY_PRESET && *sel == 2
         && (sIsInitialSetup || *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP) == 2))
            *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP) = 2;

        // Minimal Grinding ON: pair it with level caps and faster EXP
        if (sMenu->currentTab == TAB_DIFFICULTY && itemIndex == ITEM_DIFFICULTY_MIN_GRINDING && *sel == 1)
        {
            if (*GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP) == 0 && sIsInitialSetup)
                *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP) = 1;
            if (*GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_EXP_MULTIPLIER) == OPTIONS_EXP_MULTIPLIER_1X)
                *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_EXP_MULTIPLIER) = OPTIONS_EXP_MULTIPLIER_1_5X;
        }

        PlaySE(SE_SELECT);
        RedrawListMenu(sMenu->listTaskId);
        HighlightRow();
        CopyWindowToVram(WIN_OPTIONS, COPYWIN_GFX);
        DrawDescription();
    }
}

static void Task_FadeIn(u8 taskId)
{
    if (!gPaletteFade.active)
        gTasks[taskId].func = Task_ProcessInput;
}

static void Task_ProcessInput(u8 taskId)
{
    const struct ChallengeMenuItem *items;
    s32 input;

    if (JOY_NEW(DPAD_LEFT | DPAD_RIGHT))
    {
        ProcessLeftRight();
        return;
    }
    if (JOY_NEW(L_BUTTON))
    {
        SwitchTab(taskId, -1);
        return;
    }
    if (JOY_NEW(R_BUTTON))
    {
        SwitchTab(taskId, +1);
        return;
    }

    input = ListMenu_ProcessInput(sMenu->listTaskId);
    if (input == LIST_NOTHING_CHOSEN)
        return;

    if (input == LIST_CANCEL)
    {
        if (!sIsInitialSetup)
        {
            BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
            gTasks[taskId].func = Task_FadeOut;
        }
        return;
    }

    if (sMenu->currentTab == TAB_DIFFICULTY && (u32)input == ITEM_DIFFICULTY_SAVE)
    {
        gTasks[taskId].func = Task_Save;
        return;
    }

    items = GetCurrentTabItems();
    if ((u32)input < GetCurrentTabItemCount() && items[input].numChoices == 0 && sMenu->currentTab < TAB_COUNT - 1)
        SwitchTab(taskId, +1);
}

static const struct WindowTemplate sConfirmSaveYesNoTemplate =
{
    .bg          = 1,
    .tilemapLeft = 24,
    .tilemapTop  = 15,
    .width       = 4,
    .height      = 4,
    .paletteNum  = 1,
    .baseBlock   = 688,
};

static const struct YesNoFuncTable sConfirmSaveYesNoFuncs =
{
    Task_ConfirmSaveYes,
    Task_ConfirmSaveNo,
};

static void Task_Save(u8 taskId)
{
    u8 color_gray[3] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_OPTIONS_GRAY_FG, TEXT_COLOR_OPTIONS_GRAY_SHADOW };

    FillWindowPixelBuffer(WIN_DESCRIPTION, PIXEL_FILL(1));
    CopyWindowToVram(WIN_DESCRIPTION, COPYWIN_GFX);

    FillWindowPixelBuffer(WIN_CONFIRM_MSG, PIXEL_FILL(1));
    AddTextPrinterParameterized4(WIN_CONFIRM_MSG, FONT_NORMAL, 8, 1, 0, 0, color_gray, TEXT_SKIP_DRAW, sText_ConfirmSave);
    PutWindowTilemap(WIN_CONFIRM_MSG);
    CopyWindowToVram(WIN_CONFIRM_MSG, COPYWIN_GFX);

    // Yes/no draws its own border at cols 23-28 and flushes the tilemap
    CreateYesNoMenuWithCallbacks(taskId, &sConfirmSaveYesNoTemplate, 1, 0, 0, 0x1A2, 7, &sConfirmSaveYesNoFuncs);
    DrawConfirmWindowFrame();
}

static void Task_ConfirmSaveYes(u8 taskId)
{
    struct ChallengeSettings *cs = &gSaveBlock3Ptr->challengeSettings;

    cs->tx_Features_EasyCatchOff      = !*GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_EASY_CATCH);
    cs->tx_Features_WildVariety       = sWildVarietyFromMenu[*GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_WILD_VARIETY)];
    cs->autoRun                       = *GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_AUTO_RUN);
    cs->tx_Difficulty_Preset          = sDifficultyPresetFromMenu[*GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_PRESET)];
    cs->tx_Difficulty_MinimalGrinding = *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_MIN_GRINDING);
    cs->tx_Challenges_LevelCap        = *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP);
    cs->tx_Challenges_ExpMultiplier   = *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_EXP_MULTIPLIER);
    if (sIsInitialSetup)
        sNewGameSettingsChosen = TRUE;

    BeginNormalPaletteFade(PALETTES_ALL, 0, 0, 16, RGB_BLACK);
    gTasks[taskId].func = Task_FadeOut;
}

static void Task_ConfirmSaveNo(u8 taskId)
{
    PutWindowTilemap(WIN_DESCRIPTION);
    DrawDescription();
    DrawBgFrames();
    gTasks[taskId].func = Task_ProcessInput;
}

static void Task_FadeOut(u8 taskId)
{
    if (!gPaletteFade.active)
    {
        DestroyCurrentListMenu();
        DestroyTask(taskId);
        FreeAllWindowBuffers();
        FREE_AND_SET_NULL(sMenu);
        SetMainCallback2(gMain.savedCallback);
    }
}

// =============================================================================
// Init
// =============================================================================

void CB2_InitChallengeMenu(void)
{
    switch (gMain.state)
    {
    default:
    case 0:
        SetVBlankCallback(NULL);
        gMain.state++;
        break;
    case 1:
        DmaClearLarge16(3, (void *)VRAM, VRAM_SIZE, 0x1000);
        DmaClear32(3, OAM, OAM_SIZE);
        DmaClear16(3, PLTT, PLTT_SIZE);
        SetGpuReg(REG_OFFSET_DISPCNT, 0);
        ResetBgsAndClearDma3BusyFlags(0);
        InitBgsFromTemplates(0, sBgTemplates, ARRAY_COUNT(sBgTemplates));
        ResetBgPositions();
        InitWindows(sWinTemplates);
        DeactivateAllTextPrinters();
        SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(16, 224));
        SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(24, 104));
        SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_BG0 | WININ_WIN1_BG0 | WININ_WIN0_OBJ);
        SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG0 | WINOUT_WIN01_BG1 | WINOUT_WIN01_OBJ | WINOUT_WIN01_CLR);
        SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_EFFECT_DARKEN | BLDCNT_TGT1_BG0);
        SetGpuReg(REG_OFFSET_BLDALPHA, 0);
        SetGpuReg(REG_OFFSET_BLDY, 4);
        SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_WIN0_ON | DISPCNT_WIN1_ON | DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);
        ShowBg(0);
        ShowBg(1);
        gMain.state++;
        break;
    case 2:
        ResetPaletteFade();
        ScanlineEffect_Stop();
        ResetTasks();
        ResetSpriteData();
        gMain.state++;
        break;
    case 3:
        LoadBgTiles(1, GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->tiles, 0x120, 0x1A2);
        gMain.state++;
        break;
    case 4:
        LoadPalette(sBgPal, 0, sizeof(sBgPal));
        LoadPalette(GetWindowFrameTilesPal(gSaveBlock2Ptr->optionsWindowFrameType)->pal, 0x70, 0x20);
        gMain.state++;
        break;
    case 5:
        LoadPalette(sTextPal, 16, sizeof(sTextPal));
        gMain.state++;
        break;
    case 6:
    {
        struct ChallengeSettings defaults;
        const struct ChallengeSettings *cs = &gSaveBlock3Ptr->challengeSettings;

        sMenu = AllocZeroed(sizeof(struct ChallengeMenuState));
        sMenu->currentTab = TAB_FEATURES;
        sMenu->arrowTaskId = TASK_NONE;
        // Before a new game, the save block isn't the new game's yet: start from the defaults
        if (sIsInitialSetup)
        {
            SetDefaultChallengeSettings(&defaults);
            cs = &defaults;
        }

        *GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_EASY_CATCH)       = !cs->tx_Features_EasyCatchOff;
        *GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_WILD_VARIETY)     = sWildVarietyToMenu[cs->tx_Features_WildVariety];
        *GetSelectionPtr(TAB_FEATURES, ITEM_FEATURES_AUTO_RUN)         = cs->autoRun;
        *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_PRESET)         = sDifficultyPresetToMenu[cs->tx_Difficulty_Preset];
        *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_MIN_GRINDING)   = cs->tx_Difficulty_MinimalGrinding;
        *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_LEVEL_CAP)      = cs->tx_Challenges_LevelCap;
        *GetSelectionPtr(TAB_DIFFICULTY, ITEM_DIFFICULTY_EXP_MULTIPLIER) = cs->tx_Challenges_ExpMultiplier;
        gMain.state++;
        break;
    }
    case 7:
        PutWindowTilemap(WIN_TOPBAR);
        PutWindowTilemap(WIN_OPTIONS);
        PutWindowTilemap(WIN_DESCRIPTION);
        DrawTopBar();
        DrawBgFrames();
        InitListMenu();
        DrawDescription();
        CopyWindowToVram(WIN_TOPBAR, COPYWIN_FULL);
        CopyWindowToVram(WIN_OPTIONS, COPYWIN_FULL);
        CopyWindowToVram(WIN_DESCRIPTION, COPYWIN_FULL);
        gMain.state++;
        break;
    case 8:
        CreateTask(Task_FadeIn, 0);
        BeginNormalPaletteFade(PALETTES_ALL, 0, 16, 0, RGB_BLACK);
        SetVBlankCallback(VBlankCB);
        SetMainCallback2(MainCB2);
        break;
    }
}

// =============================================================================
// Entry points
// =============================================================================

// Before a new game: the menu can't be cancelled, and NewGameInitData keeps what it chose
void ChallengeMenu_OpenForNewGame(MainCallback returnCallback)
{
    sIsInitialSetup = TRUE;
    sNewGameSettingsChosen = FALSE;
    gMain.savedCallback = returnCallback;
    gMain.state = 0;
    SetMainCallback2(CB2_InitChallengeMenu);
}

bool32 ChallengeMenu_WereNewGameSettingsChosen(void)
{
    bool32 chosen = sNewGameSettingsChosen;

    sNewGameSettingsChosen = FALSE;
    sIsInitialSetup = FALSE;
    return chosen;
}

// callnative Script_OpenChallengeMenu (the settings PC)
void Script_OpenChallengeMenu(struct ScriptContext *ctx)
{
    sIsInitialSetup = FALSE;
    ScriptContext_Stop();
    gMain.savedCallback = CB2_ReturnToFieldContinueScriptPlayMapMusic;
    SetMainCallback2(CB2_InitChallengeMenu);
}
