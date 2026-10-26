// Crystal Imperium: Training Kit key item (Emerald Imperium-style instant nature/ability changes,
// and Imperium's Stat Editor for IVs and EVs). The script side is data/scripts/training_kit.inc;
// these specials read the party slot chosen with ChoosePartyMon from VAR_0x8004.
#include "global.h"
#include "battle_main.h"
#include "event_data.h"
#include "international_string_util.h"
#include "main.h"
#include "menu.h"
#include "party_menu.h"
#include "pokemon.h"
#include "script.h"
#include "sound.h"
#include "string_util.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "window.h"
#include "constants/abilities.h"
#include "constants/moves.h"
#include "constants/songs.h"

static struct Pokemon *GetChosenMon(void)
{
    return &gPlayerParty[gSpecialVar_0x8004];
}

// VAR_0x8005 = nature to set. Buffers the nickname in STR_VAR_1 and the nature in STR_VAR_2.
void TrainingKit_SetNature(void)
{
    struct Pokemon *mon = GetChosenMon();
    u32 nature = gSpecialVar_0x8005;

    if (nature >= NUM_NATURES)
        return;
    SetMonData(mon, MON_DATA_HIDDEN_NATURE, &nature);
    CalculateMonStats(mon);
    GetMonNickname(mon, gStringVar1);
    StringCopy(gStringVar2, gNaturesInfo[nature].name);
}

// Moves to the species' next distinct ability (slot 1 -> 2 -> Hidden -> 1).
// VAR_RESULT = FALSE if the species has only one ability. Buffers the nickname in STR_VAR_1
// and the new ability in STR_VAR_2.
void TrainingKit_CycleAbility(void)
{
    struct Pokemon *mon = GetChosenMon();
    u16 species = GetMonData(mon, MON_DATA_SPECIES);
    u32 current = GetMonData(mon, MON_DATA_ABILITY_NUM);
    enum Ability currentAbility = GetMonAbility(mon);

    GetMonNickname(mon, gStringVar1);
    gSpecialVar_Result = FALSE;
    for (u32 step = 1; step < NUM_ABILITY_SLOTS; step++)
    {
        u32 next = (current + step) % NUM_ABILITY_SLOTS;
        enum Ability ability = GetAbilityBySpecies(species, next);
        if (ability != ABILITY_NONE && ability != currentAbility && GetSpeciesAbility(species, next) != ABILITY_NONE)
        {
            SetMonData(mon, MON_DATA_ABILITY_NUM, &next);
            StringCopy(gStringVar2, gAbilitiesInfo[ability].name);
            gSpecialVar_Result = TRUE;
            return;
        }
    }
    StringCopy(gStringVar2, gAbilitiesInfo[currentAbility].name);
}

// The stat editor: a window over the field with the chosen Pokemon's IVs, EVs and stats. The
// d-pad picks an IV or an EV and A changes it: UP/DOWN by one (going round), LEFT/RIGHT by ten,
// A keeps the new value and B puts the old one back. START sets every IV to 31; B leaves. EVs
// stay within 252 a stat and 510 in all. With Minimal Grinding on, every Pokemon battles at 31
// IVs and 0 EVs, so, as in Imperium, the EVs are locked and the IVs only set Hidden Power's type.

enum
{
    STAT_EDITOR_IV,
    STAT_EDITOR_EV,
};

#define STAT_EDITOR_WIDTH 28
#define STAT_EDITOR_HEIGHT 18 // nine rows: names and columns, six stats, Hidden Power, help
#define STAT_EDITOR_IV_RIGHT 104
#define STAT_EDITOR_EV_RIGHT 148
#define STAT_EDITOR_STAT_RIGHT 200

#define tRow       data[0]
#define tColumn    data[1]
#define tEditing   data[2]
#define tOldValue  data[3]
#define tWindowId  data[4]

// The rows in the summary screen's order
static const u8 sStatEditorStats[NUM_STATS] = {STAT_HP, STAT_ATK, STAT_DEF, STAT_SPATK, STAT_SPDEF, STAT_SPEED};

static const u8 *const sStatEditorStatNames[NUM_STATS] =
{
    [STAT_HP]    = COMPOUND_STRING("HP"),
    [STAT_ATK]   = COMPOUND_STRING("ATTACK"),
    [STAT_DEF]   = COMPOUND_STRING("DEFENSE"),
    [STAT_SPEED] = COMPOUND_STRING("SPEED"),
    [STAT_SPATK] = COMPOUND_STRING("SP. ATK"),
    [STAT_SPDEF] = COMPOUND_STRING("SP. DEF"),
};

static const u8 sText_StatEditorIV[] = _("IV");
static const u8 sText_StatEditorEV[] = _("EV");
static const u8 sText_StatEditorStat[] = _("STAT");
static const u8 sText_StatEditorHiddenPower[] = _("HIDDEN POWER: ");
static const u8 sText_StatEditorEvTotal[] = _("EVs {STR_VAR_1}/{STR_VAR_2}");
static const u8 sText_StatEditorMinimalGrinding[] = _("MINIMAL GRINDING");
static const u8 sText_StatEditorHelp[] = _("{A_BUTTON}CHANGE {B_BUTTON}DONE {START_BUTTON}ALL IVs 31");
static const u8 sText_StatEditorEditHelp[] = _("{DPAD_UPDOWN}1 {DPAD_LEFTRIGHT}10 {A_BUTTON}OK {B_BUTTON}UNDO");

static const u8 sStatEditorColor_Normal[] = {TEXT_COLOR_WHITE, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY};
// Gray (the message box palette's color 14) for EVs that Minimal Grinding ignores
static const u8 sStatEditorColor_Locked[] = {TEXT_COLOR_WHITE, 14, TEXT_COLOR_LIGHT_GRAY};
static const u8 sStatEditorColor_Raised[] = {TEXT_COLOR_WHITE, TEXT_COLOR_RED, TEXT_COLOR_LIGHT_RED};
static const u8 sStatEditorColor_Lowered[] = {TEXT_COLOR_WHITE, TEXT_COLOR_BLUE, TEXT_COLOR_LIGHT_BLUE};

// A hyper-trained stat battles at 31 whatever its IV
static u32 StatEditor_GetIV(struct Pokemon *mon, u32 stat)
{
    if (GetMonData(mon, MON_DATA_HYPER_TRAINED_HP + stat))
        return MAX_PER_STAT_IVS;
    return GetMonData(mon, MON_DATA_HP_IV + stat);
}

static u32 StatEditor_GetEVTotal(struct Pokemon *mon)
{
    u32 i, total = 0;

    for (i = 0; i < NUM_STATS; i++)
        total += GetMonData(mon, MON_DATA_HP_EV + i);
    return total;
}

static u32 StatEditor_GetValue(struct Pokemon *mon, u32 stat, u32 column)
{
    if (column == STAT_EDITOR_IV)
        return StatEditor_GetIV(mon, stat);
    return GetMonData(mon, MON_DATA_HP_EV + stat);
}

static u32 StatEditor_GetMax(struct Pokemon *mon, u32 stat, u32 column)
{
    u32 others;

    if (column == STAT_EDITOR_IV)
        return MAX_PER_STAT_IVS;
    others = StatEditor_GetEVTotal(mon) - GetMonData(mon, MON_DATA_HP_EV + stat);
    if (others >= MAX_TOTAL_EVS)
        return 0;
    return min(MAX_PER_STAT_EVS, MAX_TOTAL_EVS - others);
}

static void StatEditor_SetValue(struct Pokemon *mon, u32 stat, u32 column, u32 value)
{
    if (column == STAT_EDITOR_IV)
    {
        bool32 notTrained = FALSE;
        SetMonData(mon, MON_DATA_HP_IV + stat, &value);
        // The IV set here is the one that counts
        SetMonData(mon, MON_DATA_HYPER_TRAINED_HP + stat, &notTrained);
    }
    else
    {
        SetMonData(mon, MON_DATA_HP_EV + stat, &value);
    }
    CalculateMonStats(mon);
}

static void StatEditor_PrintRightAligned(u32 windowId, const u8 *str, u32 right, u32 y, const u8 *color)
{
    AddTextPrinterParameterized3(windowId, FONT_NORMAL, GetStringRightAlignXOffset(FONT_NORMAL, str, right), y, color, TEXT_SKIP_DRAW, str);
}

static void StatEditor_Draw(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    struct Pokemon *mon = GetChosenMon();
    u32 windowId = task->tWindowId;
    bool32 minimalGrinding = IsMinimalGrindingMode();
    const struct NatureInfo *nature = &gNaturesInfo[GetMonData(mon, MON_DATA_HIDDEN_NATURE)];
    u32 i, y, fontId;
    u8 *ptr;

    FillWindowPixelBuffer(windowId, PIXEL_FILL(1));

    // Nickname and the columns
    GetMonNickname(mon, gStringVar1);
    fontId = GetStringWidth(FONT_NORMAL, gStringVar1, 0) > STAT_EDITOR_IV_RIGHT - 28 ? FONT_NARROW : FONT_NORMAL;
    AddTextPrinterParameterized3(windowId, fontId, 8, 1, sStatEditorColor_Normal, TEXT_SKIP_DRAW, gStringVar1);
    StatEditor_PrintRightAligned(windowId, sText_StatEditorIV, STAT_EDITOR_IV_RIGHT, 1, sStatEditorColor_Normal);
    StatEditor_PrintRightAligned(windowId, sText_StatEditorEV, STAT_EDITOR_EV_RIGHT, 1, sStatEditorColor_Normal);
    StatEditor_PrintRightAligned(windowId, sText_StatEditorStat, STAT_EDITOR_STAT_RIGHT, 1, sStatEditorColor_Normal);

    for (i = 0; i < NUM_STATS; i++)
    {
        u32 stat = sStatEditorStats[i];
        const u8 *nameColor = sStatEditorColor_Normal;
        const u8 *ivColor = sStatEditorColor_Normal;
        const u8 *evColor = minimalGrinding ? sStatEditorColor_Locked : sStatEditorColor_Normal;

        y = (i + 1) * 16 + 1;
        if (nature->statUp != nature->statDown && stat == nature->statUp)
            nameColor = sStatEditorColor_Raised;
        else if (nature->statUp != nature->statDown && stat == nature->statDown)
            nameColor = sStatEditorColor_Lowered;
        if (task->tEditing && task->tRow == i)
        {
            if (task->tColumn == STAT_EDITOR_IV)
                ivColor = sStatEditorColor_Raised;
            else
                evColor = sStatEditorColor_Raised;
        }

        AddTextPrinterParameterized3(windowId, FONT_NORMAL, 8, y, nameColor, TEXT_SKIP_DRAW, sStatEditorStatNames[stat]);
        ConvertIntToDecimalStringN(gStringVar1, StatEditor_GetIV(mon, stat), STR_CONV_MODE_LEFT_ALIGN, 2);
        StatEditor_PrintRightAligned(windowId, gStringVar1, STAT_EDITOR_IV_RIGHT, y, ivColor);
        ConvertIntToDecimalStringN(gStringVar1, GetMonData(mon, MON_DATA_HP_EV + stat), STR_CONV_MODE_LEFT_ALIGN, 3);
        StatEditor_PrintRightAligned(windowId, gStringVar1, STAT_EDITOR_EV_RIGHT, y, evColor);
        ConvertIntToDecimalStringN(gStringVar1, GetMonData(mon, MON_DATA_MAX_HP + stat), STR_CONV_MODE_LEFT_ALIGN, 3);
        StatEditor_PrintRightAligned(windowId, gStringVar1, STAT_EDITOR_STAT_RIGHT, y, sStatEditorColor_Normal);
    }

    // The cursor, left of the chosen IV or EV
    AddTextPrinterParameterized3(windowId, FONT_NORMAL,
                                 (task->tColumn == STAT_EDITOR_IV ? STAT_EDITOR_IV_RIGHT - 12 : STAT_EDITOR_EV_RIGHT - 18) - 8,
                                 (task->tRow + 1) * 16 + 1, sStatEditorColor_Normal, TEXT_SKIP_DRAW, gText_SelectorArrow3);

    // Hidden Power's type (from the IVs), and the EVs used or Minimal Grinding
    y = (NUM_STATS + 1) * 16 + 1;
    ptr = StringCopy(gStringVar4, sText_StatEditorHiddenPower);
    StringCopy(ptr, gTypesInfo[CheckDynamicMoveType(mon, MOVE_HIDDEN_POWER, 0, MON_OUTSIDE_BATTLE)].name);
    AddTextPrinterParameterized3(windowId, FONT_NORMAL, 8, y, sStatEditorColor_Normal, TEXT_SKIP_DRAW, gStringVar4);
    if (minimalGrinding)
    {
        StatEditor_PrintRightAligned(windowId, sText_StatEditorMinimalGrinding, STAT_EDITOR_WIDTH * 8 - 4, y, sStatEditorColor_Raised);
    }
    else
    {
        ConvertIntToDecimalStringN(gStringVar1, StatEditor_GetEVTotal(mon), STR_CONV_MODE_LEFT_ALIGN, 3);
        ConvertIntToDecimalStringN(gStringVar2, MAX_TOTAL_EVS, STR_CONV_MODE_LEFT_ALIGN, 3);
        StringExpandPlaceholders(gStringVar4, sText_StatEditorEvTotal);
        StatEditor_PrintRightAligned(windowId, gStringVar4, STAT_EDITOR_WIDTH * 8 - 4, y, sStatEditorColor_Normal);
    }

    y += 16;
    AddTextPrinterParameterized3(windowId, FONT_NORMAL, 8, y, sStatEditorColor_Normal, TEXT_SKIP_DRAW,
                                 task->tEditing ? sText_StatEditorEditHelp : sText_StatEditorHelp);
    CopyWindowToVram(windowId, COPYWIN_GFX);
}

static void Task_StatEditor(u8 taskId)
{
    struct Task *task = &gTasks[taskId];
    struct Pokemon *mon = GetChosenMon();
    u32 stat = sStatEditorStats[task->tRow];

    if (task->tEditing)
    {
        s32 value = StatEditor_GetValue(mon, stat, task->tColumn);
        s32 limit = StatEditor_GetMax(mon, stat, task->tColumn);
        s32 newValue = value;

        if (JOY_NEW(A_BUTTON))
        {
            PlaySE(SE_SELECT);
            task->tEditing = FALSE;
        }
        else if (JOY_NEW(B_BUTTON))
        {
            PlaySE(SE_SELECT);
            StatEditor_SetValue(mon, stat, task->tColumn, task->tOldValue);
            task->tEditing = FALSE;
        }
        else if (JOY_REPEAT(DPAD_UP))
        {
            newValue = (value >= limit) ? 0 : value + 1;
        }
        else if (JOY_REPEAT(DPAD_DOWN))
        {
            newValue = (value <= 0) ? limit : value - 1;
        }
        else if (JOY_REPEAT(DPAD_RIGHT))
        {
            newValue = value + 10;
        }
        else if (JOY_REPEAT(DPAD_LEFT))
        {
            newValue = max(value - 10, 0);
        }
        else
        {
            return;
        }

        if (newValue > limit)
            newValue = limit;
        if (newValue != value)
        {
            PlaySE(SE_SELECT);
            StatEditor_SetValue(mon, stat, task->tColumn, newValue);
        }
        StatEditor_Draw(taskId);
        return;
    }

    if (JOY_REPEAT(DPAD_UP))
    {
        PlaySE(SE_SELECT);
        task->tRow = (task->tRow == 0) ? NUM_STATS - 1 : task->tRow - 1;
    }
    else if (JOY_REPEAT(DPAD_DOWN))
    {
        PlaySE(SE_SELECT);
        task->tRow = (task->tRow == NUM_STATS - 1) ? 0 : task->tRow + 1;
    }
    else if (JOY_NEW(DPAD_LEFT | DPAD_RIGHT))
    {
        if (IsMinimalGrindingMode())
            return;
        PlaySE(SE_SELECT);
        task->tColumn ^= 1;
    }
    else if (JOY_NEW(A_BUTTON))
    {
        PlaySE(SE_SELECT);
        task->tEditing = TRUE;
        task->tOldValue = StatEditor_GetValue(mon, stat, task->tColumn);
    }
    else if (JOY_NEW(START_BUTTON))
    {
        u32 i;
        PlaySE(SE_SUCCESS);
        for (i = 0; i < NUM_STATS; i++)
            StatEditor_SetValue(mon, i, STAT_EDITOR_IV, MAX_PER_STAT_IVS);
    }
    else if (JOY_NEW(B_BUTTON))
    {
        PlaySE(SE_SELECT);
        ClearStdWindowAndFrameToTransparent(task->tWindowId, TRUE);
        RemoveWindow(task->tWindowId);
        DestroyTask(taskId);
        ScriptContext_Enable();
        return;
    }
    else
    {
        return;
    }
    StatEditor_Draw(taskId);
}

// For the party slot in VAR_0x8004; the script waits (waitstate) until B closes it
void OpenStatEditor(void)
{
    u8 taskId = CreateTask(Task_StatEditor, 80);
    struct Task *task = &gTasks[taskId];
    struct WindowTemplate template;

    task->tRow = 0;
    task->tColumn = STAT_EDITOR_IV;
    task->tEditing = FALSE;
    LoadMessageBoxAndBorderGfx();
    template = CreateWindowTemplate(0, 1, 1, STAT_EDITOR_WIDTH, STAT_EDITOR_HEIGHT, 15, 0x8);
    task->tWindowId = AddWindow(&template);
    DrawStdWindowFrame(task->tWindowId, FALSE);
    StatEditor_Draw(taskId);
    CopyWindowToVram(task->tWindowId, COPYWIN_FULL);
}

#undef tRow
#undef tColumn
#undef tEditing
#undef tOldValue
#undef tWindowId
