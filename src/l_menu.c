// Crystal Imperium: the L menu, after Emerald Imperium's L button menu (DECISIONS.md D34). In the
// field, L opens a quick menu with the tools that otherwise live in the bag: the PokeVial, a PC,
// the DexNav, the time of day, the Training Kit (STATS: IVs and EVs, nature, ability), and on/off
// switches for the Infinite Repel, the follower Pokemon and Auto Run, green when on. The clock
// and the time of day show at the top right. The tools need their key items, which every save has
// (new games get them at the start, older saves when they are loaded).
#include "global.h"
#include "l_menu.h"
#include "battle_pike.h"
#include "battle_pyramid.h"
#include "bug_contest.h"
#include "clock.h"
#include "dexnav.h"
#include "event_data.h"
#include "event_object_lock.h"
#include "event_object_movement.h"
#include "event_scripts.h"
#include "field_player_avatar.h"
#include "field_screen_effect.h"
#include "field_specials.h"
#include "field_weather.h"
#include "international_string_util.h"
#include "item.h"
#include "item_use.h"
#include "link.h"
#include "main.h"
#include "map_name_popup.h"
#include "menu.h"
#include "overworld.h"
#include "palette.h"
#include "rtc.h"
#include "safari_zone.h"
#include "script.h"
#include "sound.h"
#include "start_menu.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "wild_encounter.h"
#include "window.h"
#include "constants/items.h"
#include "constants/songs.h"

enum
{
    L_MENU_POKEVIAL,
    L_MENU_PC,
    L_MENU_DEXNAV,
    L_MENU_TIME,
    L_MENU_STATS,
    L_MENU_REPEL,
    L_MENU_FOLLOWER,
    L_MENU_AUTO_RUN,
    L_MENU_COUNT,
};

// Windows on BG0, in tiles. The menu sits on the left like Imperium's, the clock at the top
// right, and the time of day choice next to the menu's TIME row. Their tiles stay below the
// field's yes/no and message boxes (0x125 on).
#define L_MENU_LEFT       1
#define L_MENU_TOP        1
#define L_MENU_WIDTH      11
#define CLOCK_WIDTH       7
#define CLOCK_LEFT        (DISPLAY_TILE_WIDTH - 1 - CLOCK_WIDTH)
#define TIME_MENU_LEFT    (L_MENU_LEFT + L_MENU_WIDTH + 2)
#define TIME_MENU_WIDTH   7
#define L_MENU_BASE_BLOCK    0x8
#define CLOCK_BASE_BLOCK     (L_MENU_BASE_BLOCK + L_MENU_WIDTH * L_MENU_COUNT * 2)
#define TIME_MENU_BASE_BLOCK (CLOCK_BASE_BLOCK + CLOCK_WIDTH * 4)

EWRAM_DATA static u8 sLMenuCursorPos = 0;
EWRAM_DATA static u8 sNumLMenuActions = 0;
EWRAM_DATA static u8 sLMenuActions[L_MENU_COUNT] = {0};
EWRAM_DATA static u8 sLMenuWindowId = 0;
EWRAM_DATA static u8 sLMenuClockWindowId = 0;
EWRAM_DATA static u8 sLMenuTimeWindowId = 0;
EWRAM_DATA static s8 sLMenuClockMinute = 0;
EWRAM_DATA static bool8 sLMenuFollowerChanged = FALSE;
EWRAM_DATA static u8 sLMenuDexNavChain = 0;

static void Task_LMenuOpened(u8 taskId);
static void Task_LMenu(u8 taskId);
static void Task_LMenuTime(u8 taskId);
static void Task_LMenuChangeTime(u8 taskId);
static void Task_WaitFadeInLMenu(u8 taskId);
static void FieldCB_ReturnAfterTimeChange(void);

static const u8 sText_PokeVial[] = _("POKéVIAL");
static const u8 sText_PC[] = _("PC");
static const u8 sText_Time[] = _("TIME");
static const u8 sText_Stats[] = _("STATS");
static const u8 sText_Repel[] = _("REPEL");
static const u8 sText_Follower[] = _("FOLLOWER");
static const u8 sText_AutoRun[] = _("AUTO RUN");
static const u8 sText_On[] = _("ON");
static const u8 sText_Off[] = _("OFF");
static const u8 sText_AM[] = _("AM");
static const u8 sText_PM[] = _("PM");

static const u8 *const sLMenuTexts[L_MENU_COUNT] =
{
    [L_MENU_POKEVIAL] = sText_PokeVial,
    [L_MENU_PC]       = sText_PC,
    [L_MENU_DEXNAV]   = gText_MenuDexNav,
    [L_MENU_TIME]     = sText_Time,
    [L_MENU_STATS]    = sText_Stats,
    [L_MENU_REPEL]    = sText_Repel,
    [L_MENU_FOLLOWER] = sText_Follower,
    [L_MENU_AUTO_RUN] = sText_AutoRun,
};

static const u8 *const sTimeOfDayNames[TIMES_OF_DAY_COUNT] =
{
    [TIME_MORNING] = COMPOUND_STRING("MORNING"),
    [TIME_DAY]     = COMPOUND_STRING("DAY"),
    [TIME_EVENING] = COMPOUND_STRING("EVENING"),
    [TIME_NIGHT]   = COMPOUND_STRING("NIGHT"),
};

// The clock time (minutes after midnight) each TIME choice moves to, where that time of day
// shows best: UpdateTimeOfDay blends each one in from the one before (night into morning until
// the middle of the morning, day into evening over the evening's hour, evening into night over
// the night's first hour)
static const u16 sTimeOfDayClock[TIMES_OF_DAY_COUNT] =
{
    [TIME_MORNING] = (MORNING_HOUR_BEGIN + (MORNING_HOUR_END - MORNING_HOUR_BEGIN) / 2) * MINUTES_PER_HOUR,
    [TIME_DAY]     = 12 * MINUTES_PER_HOUR,
    [TIME_EVENING] = EVENING_HOUR_BEGIN * MINUTES_PER_HOUR + MINUTES_PER_HOUR / 2,
    [TIME_NIGHT]   = (NIGHT_HOUR_BEGIN + 1) * MINUTES_PER_HOUR,
};

static u8 AddLMenuWindow(u8 left, u8 top, u8 width, u8 height, u16 baseBlock)
{
    struct WindowTemplate template = CreateWindowTemplate(0, left, top, width, height, 15, baseBlock);
    return AddWindow(&template);
}

static const u8 sTextColor_Normal[] = {TEXT_COLOR_WHITE, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY};
static const u8 sTextColor_On[] = {TEXT_COLOR_WHITE, TEXT_COLOR_GREEN, TEXT_COLOR_LIGHT_GREEN};

// Wherever the start menu is limited to a few entries (link rooms, the Safari Zone, the Bug
// Catching Contest, the Battle Pike and Pyramid), the L menu stays closed. With the L=A button
// mode, L is the A button.
static bool32 CanOpenLMenu(void)
{
    if (gSaveBlock2Ptr->optionsButtonMode == OPTIONS_BUTTON_MODE_L_EQUALS_A
     || !FlagGet(FLAG_SYS_POKEMON_GET))
        return FALSE;
    return !(IsOverworldLinkActive()
          || InUnionRoom()
          || GetSafariZoneFlag()
          || GetBugContestFlag()
          || InBattlePike()
          || CurrentBattlePyramidLocation() != PYRAMID_LOCATION_NONE
          || InMultiPartnerRoom());
}

static void BuildLMenuActions(void)
{
    sNumLMenuActions = 0;
    if (CheckBagHasItem(ITEM_POKE_VIAL, 1))
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_POKEVIAL);
    if (CheckBagHasItem(ITEM_POKEMON_BOX_LINK, 1))
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_PC);
    if (DN_FLAG_DEXNAV_GET != 0 && FlagGet(DN_FLAG_DEXNAV_GET))
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_DEXNAV);
    AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_TIME);
    if (CheckBagHasItem(ITEM_TRAINING_KIT, 1))
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_STATS);
    if (CheckBagHasItem(ITEM_INFINITE_REPEL, 1))
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_REPEL);
    if (OW_FOLLOWERS_ENABLED)
        AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_FOLLOWER);
    AppendToList(sLMenuActions, &sNumLMenuActions, L_MENU_AUTO_RUN);
    if (sLMenuCursorPos >= sNumLMenuActions)
        sLMenuCursorPos = 0;
}

// TRUE/FALSE for the switches, -1 for the other entries
static s32 GetLMenuSwitchState(u32 action)
{
    switch (action)
    {
    case L_MENU_REPEL:
        return FlagGet(FLAG_INFINITE_REPEL_ON);
    case L_MENU_FOLLOWER:
        return gSaveBlock3Ptr->challengeSettings.followerEnable == 0; // 0 = a Pokemon follows
    case L_MENU_AUTO_RUN:
        return gSaveBlock3Ptr->challengeSettings.autoRun == 0; // 0 = running without B
    default:
        return -1;
    }
}

static void PrintLMenuAction(u32 index)
{
    u32 action = sLMenuActions[index];
    u32 y = index * 16 + 1;
    s32 state = GetLMenuSwitchState(action);
    const u8 *color = (state == TRUE) ? sTextColor_On : sTextColor_Normal;

    FillWindowPixelRect(sLMenuWindowId, PIXEL_FILL(1), 8, y, L_MENU_WIDTH * 8 - 8, 16);
    AddTextPrinterParameterized3(sLMenuWindowId, FONT_NORMAL, 8, y, color, TEXT_SKIP_DRAW, sLMenuTexts[action]);
    if (state != -1)
    {
        const u8 *onOff = state ? sText_On : sText_Off;
        AddTextPrinterParameterized3(sLMenuWindowId, FONT_NORMAL,
                                     GetStringRightAlignXOffset(FONT_NORMAL, onOff, L_MENU_WIDTH * 8 - 2), y,
                                     color, TEXT_SKIP_DRAW, onOff);
    }
}

// The clock like the start menu's ("8:23 AM"), and the time of day under it
static void PrintLMenuClock(void)
{
    u8 *ptr;
    u32 hours;

    RtcCalcLocalTime();
    sLMenuClockMinute = gLocalTime.minutes;
    hours = gLocalTime.hours % 12;
    if (hours == 0)
        hours = 12;
    FillWindowPixelBuffer(sLMenuClockWindowId, PIXEL_FILL(1));
    ptr = ConvertIntToDecimalStringN(gStringVar4, hours, STR_CONV_MODE_LEFT_ALIGN, 2);
    *ptr++ = CHAR_COLON;
    ptr = ConvertIntToDecimalStringN(ptr, gLocalTime.minutes, STR_CONV_MODE_LEADING_ZEROS, 2);
    *ptr++ = CHAR_SPACE;
    StringCopy(ptr, gLocalTime.hours < 12 ? sText_AM : sText_PM);
    AddTextPrinterParameterized(sLMenuClockWindowId, FONT_NORMAL, gStringVar4, 0, 1, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(sLMenuClockWindowId, FONT_NORMAL, sTimeOfDayNames[GetTimeOfDay()], 0, 17, TEXT_SKIP_DRAW, NULL);
    CopyWindowToVram(sLMenuClockWindowId, COPYWIN_GFX);
}

#define tTimeOfDay  data[0]
#define tClockTimer data[1]

// The cartridge clock is read once a second (with interrupts off while it is read)
static void UpdateLMenuClock(u8 taskId)
{
    if (++gTasks[taskId].tClockTimer < 60)
        return;
    gTasks[taskId].tClockTimer = 0;
    RtcCalcLocalTime();
    if (gLocalTime.minutes != sLMenuClockMinute)
        PrintLMenuClock();
}

static void DrawLMenu(void)
{
    u32 i;

    BuildLMenuActions();
    LoadMessageBoxAndBorderGfx();
    sLMenuWindowId = AddLMenuWindow(L_MENU_LEFT, L_MENU_TOP, L_MENU_WIDTH, sNumLMenuActions * 2, L_MENU_BASE_BLOCK);
    DrawStdWindowFrame(sLMenuWindowId, FALSE);
    for (i = 0; i < sNumLMenuActions; i++)
        PrintLMenuAction(i);
    sLMenuCursorPos = InitMenuNormal(sLMenuWindowId, FONT_NORMAL, 0, 1, 16, sNumLMenuActions, sLMenuCursorPos);
    CopyWindowToVram(sLMenuWindowId, COPYWIN_FULL);

    sLMenuClockWindowId = AddLMenuWindow(CLOCK_LEFT, L_MENU_TOP, CLOCK_WIDTH, 4, CLOCK_BASE_BLOCK);
    DrawStdWindowFrame(sLMenuClockWindowId, FALSE);
    PrintLMenuClock();
    CopyWindowToVram(sLMenuClockWindowId, COPYWIN_FULL);
    sLMenuFollowerChanged = FALSE;
}

static void RemoveLMenuWindows(void)
{
    ClearStdWindowAndFrameToTransparent(sLMenuClockWindowId, FALSE);
    RemoveWindow(sLMenuClockWindowId);
    ClearStdWindowAndFrameToTransparent(sLMenuWindowId, TRUE);
    RemoveWindow(sLMenuWindowId);
}

// Back to the field (an action's script may follow)
static void CloseLMenu(void)
{
    RemoveLMenuWindows();
    if (sLMenuFollowerChanged)
        UpdateFollowingPokemon();
    ResumeMtSilverBlizzardAfterMenu();
    ScriptUnfreezeObjectEvents();
    UnlockPlayerFieldControls();
}

bool32 TryShowLMenu(void)
{
    if (!CanOpenLMenu())
        return FALSE;

    PlaySE(SE_WIN_OPEN);
    HideMapNamePopUpWindow();
    FreezeObjectEvents();
    PlayerFreeze();
    StopPlayerAvatar();
    // Also ends a DexNav search, keeping the chain (Imperium: L cancels a search)
    LockPlayerFieldControls();
    DrawLMenu();
    CreateTask(Task_LMenuOpened, 80);
    return TRUE;
}

// The L press that opened the menu must not close it
static void Task_LMenuOpened(u8 taskId)
{
    gTasks[taskId].func = Task_LMenu;
}

static void OpenTimeMenu(void)
{
    u32 i;
    u32 top = L_MENU_TOP + sLMenuCursorPos * 2;

    if (top + TIMES_OF_DAY_COUNT * 2 > DISPLAY_TILE_HEIGHT - 1)
        top = DISPLAY_TILE_HEIGHT - 1 - TIMES_OF_DAY_COUNT * 2;
    sLMenuTimeWindowId = AddLMenuWindow(TIME_MENU_LEFT, top, TIME_MENU_WIDTH, TIMES_OF_DAY_COUNT * 2, TIME_MENU_BASE_BLOCK);
    DrawStdWindowFrame(sLMenuTimeWindowId, FALSE);
    for (i = 0; i < TIMES_OF_DAY_COUNT; i++)
        AddTextPrinterParameterized(sLMenuTimeWindowId, FONT_NORMAL, sTimeOfDayNames[i], 8, i * 16 + 1, TEXT_SKIP_DRAW, NULL);
    InitMenuNormal(sLMenuTimeWindowId, FONT_NORMAL, 0, 1, 16, TIMES_OF_DAY_COUNT, GetTimeOfDay());
    CopyWindowToVram(sLMenuTimeWindowId, COPYWIN_FULL);
}

static void CloseTimeMenu(void)
{
    ClearStdWindowAndFrameToTransparent(sLMenuTimeWindowId, TRUE);
    RemoveWindow(sLMenuTimeWindowId);
}

static void DoLMenuAction(u8 taskId)
{
    u32 action = sLMenuActions[sLMenuCursorPos];

    switch (action)
    {
    case L_MENU_POKEVIAL:
        CloseLMenu();
        HealPartyWithPokeVial();
        PlaySE(SE_USE_ITEM);
        ScriptContext_SetupScript(LMenu_EventScript_PokeVial);
        DestroyTask(taskId);
        break;
    case L_MENU_PC:
        // The whole PC, like a Pokemon Center's (Imperium 1.3), without the PC on the map to light up
        PlaySE(SE_SELECT);
        CloseLMenu();
        ScriptContext_SetupScript(EventScript_FakePC);
        DestroyTask(taskId);
        break;
    case L_MENU_DEXNAV:
        PlaySE(SE_SELECT);
        if (MapHasNoEncounterData())
        {
            CloseLMenu();
            ScriptContext_SetupScript(LMenu_EventScript_NoDexNav);
            DestroyTask(taskId);
        }
        else
        {
            // B in the DexNav comes back to this menu
            FadeScreen(FADE_TO_BLACK, 0);
            gTasks[taskId].func = Task_OpenDexNavFromLMenu;
        }
        break;
    case L_MENU_TIME:
        PlaySE(SE_SELECT);
        OpenTimeMenu();
        gTasks[taskId].func = Task_LMenuTime;
        break;
    case L_MENU_STATS:
        PlaySE(SE_SELECT);
        CloseLMenu();
        ScriptContext_SetupScript(EventScript_TrainingKit);
        DestroyTask(taskId);
        break;
    case L_MENU_REPEL:
        FlagToggle(FLAG_INFINITE_REPEL_ON);
        PlaySE(FlagGet(FLAG_INFINITE_REPEL_ON) ? SE_REPEL : SE_PC_OFF);
        PrintLMenuAction(sLMenuCursorPos);
        CopyWindowToVram(sLMenuWindowId, COPYWIN_GFX);
        break;
    case L_MENU_FOLLOWER:
        gSaveBlock3Ptr->challengeSettings.followerEnable ^= 1;
        sLMenuFollowerChanged = !sLMenuFollowerChanged;
        PlaySE(SE_SELECT);
        PrintLMenuAction(sLMenuCursorPos);
        CopyWindowToVram(sLMenuWindowId, COPYWIN_GFX);
        break;
    case L_MENU_AUTO_RUN:
        gSaveBlock3Ptr->challengeSettings.autoRun ^= 1;
        PlaySE(SE_SELECT);
        PrintLMenuAction(sLMenuCursorPos);
        CopyWindowToVram(sLMenuWindowId, COPYWIN_GFX);
        break;
    }
}

static void Task_LMenu(u8 taskId)
{
    if (JOY_NEW(DPAD_UP))
    {
        PlaySECursorMove(SE_SELECT);
        sLMenuCursorPos = Menu_MoveCursor(-1);
    }
    else if (JOY_NEW(DPAD_DOWN))
    {
        PlaySECursorMove(SE_SELECT);
        sLMenuCursorPos = Menu_MoveCursor(1);
    }
    else if (JOY_NEW(A_BUTTON))
    {
        DoLMenuAction(taskId);
        return;
    }
    else if (JOY_NEW(B_BUTTON | L_BUTTON))
    {
        PlaySE(SE_SELECT);
        CloseLMenu();
        DestroyTask(taskId);
        return;
    }
    UpdateLMenuClock(taskId);
}

// The time of day to move the clock to. Choosing the current one changes nothing.
static void Task_LMenuTime(u8 taskId)
{
    s8 input = Menu_ProcessInput();

    if (input == MENU_NOTHING_CHOSEN)
    {
        UpdateLMenuClock(taskId);
        return;
    }
    CloseTimeMenu();
    if (input == MENU_B_PRESSED || input == GetTimeOfDay())
    {
        if (input == MENU_B_PRESSED)
            PlaySE(SE_SELECT);
        InitMenuNormal(sLMenuWindowId, FONT_NORMAL, 0, 1, 16, sNumLMenuActions, sLMenuCursorPos);
        gTasks[taskId].func = Task_LMenu;
        return;
    }
    gTasks[taskId].tTimeOfDay = input;
    RemoveLMenuWindows();
    FadeScreen(FADE_TO_BLACK, 0);
    gTasks[taskId].func = Task_LMenuChangeTime;
}

// Moves the clock forward (never back, so berry trees and daily events only see time pass) to
// the time of day's clock time: today if it is still ahead, otherwise tomorrow
static void ForwardClockTo(u32 clock)
{
    s32 days;

    RtcCalcLocalTime();
    days = gLocalTime.days;
    if (gLocalTime.hours * MINUTES_PER_HOUR + gLocalTime.minutes >= clock)
        days++;
    RtcCalcLocalTimeOffset(days, clock / MINUTES_PER_HOUR, clock % MINUTES_PER_HOUR, 0);
    // Also sets the flags that show the Pokemon seen by day or by night, before the reload
    // spawns them
    UpdateTimeOfDay();
    FormChangeTimeUpdate();
}

// Reloads the map where the player stands, so its lighting, the Pokemon seen by day or by night
// and the time-based events all follow the new time
static void Task_LMenuChangeTime(u8 taskId)
{
    if (gPaletteFade.active)
        return;

    ForwardClockTo(sTimeOfDayClock[gTasks[taskId].tTimeOfDay]);
    sLMenuDexNavChain = gSaveBlock3Ptr->dexNavChain;
    StoreInitialPlayerAvatarState();
    gFieldCallback = FieldCB_ReturnAfterTimeChange;
    SetMainCallback2(CB2_LoadMap);
    DestroyTask(taskId);
}

#undef tTimeOfDay
#undef tClockTimer

static void FieldCB_ReturnAfterTimeChange(void)
{
    // The map is the same one: keep the DexNav chain that loading it reset
    gSaveBlock3Ptr->dexNavChain = sLMenuDexNavChain;
    FieldCB_DefaultWarpExit();
}

// The DexNav returns here (B, CB2_ReturnToFieldWithOpenLMenu), like the start menu's DexNav
// returns to the start menu
bool8 FieldCB_ReturnToFieldOpenLMenu(void)
{
    FreezeObjectEvents();
    LockPlayerFieldControls();
    DrawLMenu();
    FadeInFromBlack();
    CreateTask(Task_WaitFadeInLMenu, 80);
    return TRUE;
}

static void Task_WaitFadeInLMenu(u8 taskId)
{
    if (IsWeatherNotFadingIn())
        gTasks[taskId].func = Task_LMenu;
}
