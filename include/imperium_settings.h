#ifndef POKEPLATINUM_IMPERIUM_SETTINGS_H
#define POKEPLATINUM_IMPERIUM_SETTINGS_H

#include "constants/imperium.h"

#include "savedata.h"
#include "vars_flags.h"

// Platinum Imperium settings registry (stage 2, frozen API; see docs/platinum_imperium/API.md).
//
// Every setting lives in a renamed var or flag, so reading one costs a few loads and changing one
// never changes the save layout. Battle code has no SaveData: it must read the BATTLE_STATUS_*
// bits and the level cap that Imperium_FieldBattleStatusBits / LevelCap_Get put into the
// FieldBattleDTO, never these functions.

// VarsFlags variants, for code that already holds a VarsFlags*.
int Imperium_VarsFlags_GetDifficulty(VarsFlags *varsFlags);
int Imperium_VarsFlags_GetLevelCapMode(VarsFlags *varsFlags);
BOOL Imperium_VarsFlags_IsMinimalGrinding(VarsFlags *varsFlags);
BOOL Imperium_VarsFlags_CheckSetting(VarsFlags *varsFlags, u16 flagID);
void Imperium_VarsFlags_SetSetting(VarsFlags *varsFlags, u16 flagID, BOOL on);

// IMPERIUM_DIFFICULTY_NORMAL / _EASY / _HARD. Out-of-range values read as NORMAL.
int Imperium_GetDifficulty(SaveData *saveData);
void Imperium_SetDifficulty(SaveData *saveData, int difficulty);

// IMPERIUM_LEVEL_CAP_NORMAL / _HARD / _OFF. Out-of-range values read as NORMAL.
int Imperium_GetLevelCapMode(SaveData *saveData);
void Imperium_SetLevelCapMode(SaveData *saveData, int mode);

BOOL Imperium_IsMinimalGrinding(SaveData *saveData);
void Imperium_SetMinimalGrinding(SaveData *saveData, BOOL on);
BOOL Imperium_AreFastBattlesOn(SaveData *saveData);
void Imperium_SetFastBattles(SaveData *saveData, BOOL on);
BOOL Imperium_IsFastIntroOn(SaveData *saveData);
void Imperium_SetFastIntro(SaveData *saveData, BOOL on);
BOOL Imperium_IsExpShareAllOn(SaveData *saveData);
void Imperium_SetExpShareAll(SaveData *saveData, BOOL on);
BOOL Imperium_IsExpBoostOn(SaveData *saveData);
void Imperium_SetExpBoost(SaveData *saveData, BOOL on);
BOOL Imperium_AreTMsReusable(SaveData *saveData);
void Imperium_SetReusableTMs(SaveData *saveData, BOOL on);
BOOL Imperium_IsInfiniteRepelOn(SaveData *saveData);
void Imperium_SetInfiniteRepel(SaveData *saveData, BOOL on);
BOOL Imperium_IsSleepClauseOn(SaveData *saveData);
void Imperium_SetSleepClause(SaveData *saveData, BOOL on);
BOOL Imperium_IsEasyCatchOn(SaveData *saveData);
void Imperium_SetEasyCatch(SaveData *saveData, BOOL on);

u16 Imperium_GetCarePackagesGiven(SaveData *saveData);
void Imperium_SetCarePackagesGiven(SaveData *saveData, u16 count);

// IMPERIUM_SETTINGS_VERSION once InitNewGame has run; 0 for a save that predates the hack.
u16 Imperium_GetSettingsVersion(SaveData *saveData);
BOOL Imperium_AreSettingsInitialized(SaveData *saveData);

// The BATTLE_STATUS_* bits (8 and up) for the current settings. The caller decides whether the
// battle may receive them (never link, Frontier or Wi-Fi battles).
u32 Imperium_FieldBattleStatusBits(SaveData *saveData);

// Level caps. LevelCap_Get reads the badge count, the cap mode and the game-completed flag.
u8 LevelCap_Get(SaveData *saveData);
u8 LevelCap_ForBadges(int badges, int mode, BOOL champion);

#endif // POKEPLATINUM_IMPERIUM_SETTINGS_H
