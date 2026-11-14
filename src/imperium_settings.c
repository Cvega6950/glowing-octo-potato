#include "imperium_settings.h"

#include <nitro.h>

#include "constants/battle.h"
#include "constants/imperium.h"
#include "constants/savedata/vars_flags.h"

#include "save_player.h"
#include "savedata.h"
#include "system_flags.h"
#include "trainer_info.h"
#include "vars_flags.h"

#define NUM_CAP_BADGE_STEPS 9

static const u8 sLevelCapsNormal[NUM_CAP_BADGE_STEPS] = { 15, 24, 33, 42, 50, 58, 66, 75, 85 };
static const u8 sLevelCapsHard[NUM_CAP_BADGE_STEPS] = { 12, 21, 30, 39, 47, 55, 63, 72, 85 };

static u16 GetVar(VarsFlags *varsFlags, u16 varID)
{
    return *VarsFlags_GetVarAddress(varsFlags, varID);
}

static void SetVar(VarsFlags *varsFlags, u16 varID, u16 value)
{
    *VarsFlags_GetVarAddress(varsFlags, varID) = value;
}

static BOOL CheckSaveFlag(SaveData *saveData, u16 flagID)
{
    return VarsFlags_CheckFlag(SaveData_GetVarsFlags(saveData), flagID);
}

static void SetSaveFlag(SaveData *saveData, u16 flagID, BOOL on)
{
    Imperium_VarsFlags_SetSetting(SaveData_GetVarsFlags(saveData), flagID, on);
}

int Imperium_VarsFlags_GetDifficulty(VarsFlags *varsFlags)
{
    u16 difficulty = GetVar(varsFlags, VAR_IMPERIUM_DIFFICULTY);

    if (difficulty >= IMPERIUM_DIFFICULTY_COUNT) {
        return IMPERIUM_DIFFICULTY_NORMAL;
    }

    return difficulty;
}

int Imperium_VarsFlags_GetLevelCapMode(VarsFlags *varsFlags)
{
    u16 mode = GetVar(varsFlags, VAR_IMPERIUM_LEVEL_CAP_MODE);

    if (mode >= IMPERIUM_LEVEL_CAP_COUNT) {
        return IMPERIUM_LEVEL_CAP_NORMAL;
    }

    return mode;
}

BOOL Imperium_VarsFlags_IsMinimalGrinding(VarsFlags *varsFlags)
{
    return VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_MINIMAL_GRINDING);
}

BOOL Imperium_VarsFlags_CheckSetting(VarsFlags *varsFlags, u16 flagID)
{
    return VarsFlags_CheckFlag(varsFlags, flagID);
}

void Imperium_VarsFlags_SetSetting(VarsFlags *varsFlags, u16 flagID, BOOL on)
{
    if (on) {
        VarsFlags_SetFlag(varsFlags, flagID);
    } else {
        VarsFlags_ClearFlag(varsFlags, flagID);
    }
}

int Imperium_GetDifficulty(SaveData *saveData)
{
    return Imperium_VarsFlags_GetDifficulty(SaveData_GetVarsFlags(saveData));
}

void Imperium_SetDifficulty(SaveData *saveData, int difficulty)
{
    GF_ASSERT(difficulty >= 0 && difficulty < IMPERIUM_DIFFICULTY_COUNT);
    SetVar(SaveData_GetVarsFlags(saveData), VAR_IMPERIUM_DIFFICULTY, difficulty);
}

int Imperium_GetLevelCapMode(SaveData *saveData)
{
    return Imperium_VarsFlags_GetLevelCapMode(SaveData_GetVarsFlags(saveData));
}

void Imperium_SetLevelCapMode(SaveData *saveData, int mode)
{
    GF_ASSERT(mode >= 0 && mode < IMPERIUM_LEVEL_CAP_COUNT);
    SetVar(SaveData_GetVarsFlags(saveData), VAR_IMPERIUM_LEVEL_CAP_MODE, mode);
}

BOOL Imperium_IsMinimalGrinding(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_MINIMAL_GRINDING);
}

void Imperium_SetMinimalGrinding(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_MINIMAL_GRINDING, on);
}

BOOL Imperium_AreFastBattlesOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_FAST_BATTLES);
}

void Imperium_SetFastBattles(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_FAST_BATTLES, on);
}

BOOL Imperium_IsFastIntroOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_FAST_INTRO);
}

void Imperium_SetFastIntro(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_FAST_INTRO, on);
}

BOOL Imperium_IsExpShareAllOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_EXP_SHARE_ALL);
}

void Imperium_SetExpShareAll(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_EXP_SHARE_ALL, on);
}

BOOL Imperium_IsExpBoostOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_EXP_BOOST);
}

void Imperium_SetExpBoost(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_EXP_BOOST, on);
}

BOOL Imperium_AreTMsReusable(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_REUSABLE_TMS);
}

void Imperium_SetReusableTMs(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_REUSABLE_TMS, on);
}

BOOL Imperium_IsInfiniteRepelOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_INFINITE_REPEL);
}

void Imperium_SetInfiniteRepel(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_INFINITE_REPEL, on);
}

BOOL Imperium_IsSleepClauseOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_SLEEP_CLAUSE);
}

void Imperium_SetSleepClause(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_SLEEP_CLAUSE, on);
}

BOOL Imperium_IsEasyCatchOn(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_EASY_CATCH);
}

void Imperium_SetEasyCatch(SaveData *saveData, BOOL on)
{
    SetSaveFlag(saveData, FLAG_IMPERIUM_EASY_CATCH, on);
}

u16 Imperium_GetCarePackagesGiven(SaveData *saveData)
{
    return GetVar(SaveData_GetVarsFlags(saveData), VAR_IMPERIUM_CARE_PACKAGES);
}

void Imperium_SetCarePackagesGiven(SaveData *saveData, u16 count)
{
    SetVar(SaveData_GetVarsFlags(saveData), VAR_IMPERIUM_CARE_PACKAGES, count);
}

u16 Imperium_GetSettingsVersion(SaveData *saveData)
{
    return GetVar(SaveData_GetVarsFlags(saveData), VAR_IMPERIUM_SETTINGS_VERSION);
}

BOOL Imperium_AreSettingsInitialized(SaveData *saveData)
{
    return CheckSaveFlag(saveData, FLAG_IMPERIUM_SETTINGS_INITIALIZED);
}

u32 Imperium_FieldBattleStatusBits(SaveData *saveData)
{
    VarsFlags *varsFlags = SaveData_GetVarsFlags(saveData);
    u32 bits = 0;

    switch (Imperium_VarsFlags_GetDifficulty(varsFlags)) {
    case IMPERIUM_DIFFICULTY_EASY:
        bits |= BATTLE_STATUS_EASY;
        break;
    case IMPERIUM_DIFFICULTY_HARD:
        bits |= BATTLE_STATUS_HARD;
        break;
    default:
        break;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_FAST_BATTLES)) {
        bits |= BATTLE_STATUS_FAST_BATTLE;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_FAST_INTRO)) {
        bits |= BATTLE_STATUS_FAST_INTRO;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_SLEEP_CLAUSE)) {
        bits |= BATTLE_STATUS_SLEEP_CLAUSE;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_EXP_SHARE_ALL)) {
        bits |= BATTLE_STATUS_EXP_SHARE_ALL;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_MINIMAL_GRINDING)) {
        bits |= BATTLE_STATUS_MINIMAL_GRINDING;
    }

    if (VarsFlags_CheckFlag(varsFlags, FLAG_IMPERIUM_EXP_BOOST)) {
        bits |= BATTLE_STATUS_EXP_BOOST;
    }

    return bits;
}

u8 LevelCap_ForBadges(int badges, int mode, BOOL champion)
{
    if (mode == IMPERIUM_LEVEL_CAP_OFF || champion) {
        return IMPERIUM_LEVEL_CAP_NONE;
    }

    if (badges < 0) {
        badges = 0;
    } else if (badges >= NUM_CAP_BADGE_STEPS) {
        badges = NUM_CAP_BADGE_STEPS - 1;
    }

    if (mode == IMPERIUM_LEVEL_CAP_HARD) {
        return sLevelCapsHard[badges];
    }

    return sLevelCapsNormal[badges];
}

u8 LevelCap_Get(SaveData *saveData)
{
    VarsFlags *varsFlags = SaveData_GetVarsFlags(saveData);
    int badges = TrainerInfo_BadgeCount(SaveData_GetTrainerInfo(saveData));

    return LevelCap_ForBadges(badges, Imperium_VarsFlags_GetLevelCapMode(varsFlags), SystemFlag_CheckGameCompleted(varsFlags));
}
