// Crystal Imperium: the PC's RAISE TO LV. CAP (DECISIONS.md D63). Emerald Imperium sets the Pokemon in the party
// and the PC to the level cap; here the PC's own menu does it, so it can be used from any PC, the L menu or the
// Pokemon Box Link. Every Pokemon in the party and the boxes is raised to the level, its experience set to that
// level's least, unless it is an Egg, has a PC marking (the player's way to keep one as it is), is already at or
// above the level (nothing is ever lowered) or, in a Nuzlocke, has fainted. Nothing evolves and no move is learned,
// as in Emerald Imperium: one Rare Candy evolves a Pokemon at the cap, and the relearner teaches what it skipped.
#include "global.h"
#include "caps.h"
#include "event_data.h"
#include "nuzlocke.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "raise_to_cap.h"
#include "constants/flags.h"

// The level: the level cap; with LEVEL CAP OFF, the cap NORMAL has at the player's progress (the level every
// trainer battles at, D56) rather than 100
u32 GetRaiseToCapLevel(void)
{
    if (gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap != 0)
        return GetCurrentLevelCap();
    return GetLevelCapAtStage(GetLevelCapStage());
}

// Not while FLAG_LIMIT_TO_50 holds every Pokemon at Lv. 50 (the Trainer Hill; the Battle Pike and Pyramid): stats
// are then worked out at Lv. 50, a boxed Pokemon's HP too, so one that fainted can read as alive
bool32 CanUseRaiseToCap(void)
{
    return !FlagGet(FLAG_LIMIT_TO_50);
}

static bool32 IsNuzlockeOn(void)
{
    return IsNuzlockeActive() || IsNuzlockeEasyActive();
}

static u32 GetExpForLevel(u32 species, u32 level)
{
    return gExperienceTables[gSpeciesInfo[species].growthRate][level];
}

// A boxed Pokemon's HP is its max HP less the HP it had lost: only one that lost some can have fainted
static bool32 IsBoxMonFainted(struct BoxPokemon *boxMon)
{
    struct Pokemon mon;

    if (GetBoxMonData(boxMon, MON_DATA_HP_LOST) == 0)
        return FALSE;
    BoxMonToMon(boxMon, &mon);
    return GetMonData(&mon, MON_DATA_HP) == 0;
}

// Any Pokemon, an Egg or Bad Egg (MON_DATA_IS_EGG; MON_DATA_SPECIES is SPECIES_EGG only for a Bad Egg) and a
// marked one aside
static bool32 IsRaisable(struct BoxPokemon *boxMon)
{
    return GetBoxMonData(boxMon, MON_DATA_SANITY_HAS_SPECIES)
        && !GetBoxMonData(boxMon, MON_DATA_IS_EGG)
        && GetBoxMonData(boxMon, MON_DATA_MARKINGS) == 0;
}

// The level its experience gives, not the stored one, which FLAG_LIMIT_TO_50 sets to 50: nothing is ever lowered
bool32 CanRaisePartyMonToLevel(struct Pokemon *mon, u32 level)
{
    if (!IsRaisable(&mon->box) || GetLevelFromMonExp(mon) >= level)
        return FALSE;
    return !(IsNuzlockeOn() && GetMonData(mon, MON_DATA_HP) == 0);
}

bool32 CanRaiseBoxMonToLevel(struct BoxPokemon *boxMon, u32 level)
{
    if (!IsRaisable(boxMon) || GetLevelFromBoxMonExp(boxMon) >= level)
        return FALSE;
    return !(IsNuzlockeOn() && IsBoxMonFainted(boxMon));
}

// HP goes up by the max HP gained, so a full Pokemon stays full; a fainted one stays fainted (CalculateMonStats)
void RaisePartyMonToLevel(struct Pokemon *mon, u32 level)
{
    u32 exp = GetExpForLevel(GetMonData(mon, MON_DATA_SPECIES), level);

    SetMonData(mon, MON_DATA_EXP, &exp);
    CalculateMonStats(mon);
}

// A boxed Pokemon keeps no level or stats, only its experience and the HP it lost: a Pokemon that lost none
// only needs its experience. One that lost some is raised as a party Pokemon would be, so that the HP it
// lost stays what it was (and a fainted one stays fainted)
void RaiseBoxMonToLevel(struct BoxPokemon *boxMon, u32 level)
{
    if (GetBoxMonData(boxMon, MON_DATA_HP_LOST) == 0)
    {
        u32 exp = GetExpForLevel(GetBoxMonData(boxMon, MON_DATA_SPECIES), level);

        SetBoxMonData(boxMon, MON_DATA_EXP, &exp);
    }
    else
    {
        struct Pokemon mon;

        BoxMonToMon(boxMon, &mon);
        RaisePartyMonToLevel(&mon, level);
        *boxMon = mon.box;
    }
}

u32 CountMonsToRaise(u32 level)
{
    u32 count = 0, boxId, i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (CanRaisePartyMonToLevel(&gPlayerParty[i], level))
            count++;
    }
    for (boxId = 0; boxId < TOTAL_BOXES_COUNT; boxId++)
    {
        for (i = 0; i < IN_BOX_COUNT; i++)
        {
            if (CanRaiseBoxMonToLevel(GetBoxedMonPtr(boxId, i), level))
                count++;
        }
    }
    return count;
}

u32 RaisePartyToLevel(u32 level)
{
    u32 count = 0, i;

    for (i = 0; i < PARTY_SIZE; i++)
    {
        if (CanRaisePartyMonToLevel(&gPlayerParty[i], level))
        {
            RaisePartyMonToLevel(&gPlayerParty[i], level);
            count++;
        }
    }
    return count;
}

u32 RaiseBoxToLevel(u32 boxId, u32 level)
{
    u32 count = 0, i;

    for (i = 0; i < IN_BOX_COUNT; i++)
    {
        struct BoxPokemon *boxMon = GetBoxedMonPtr(boxId, i);

        if (CanRaiseBoxMonToLevel(boxMon, level))
        {
            RaiseBoxMonToLevel(boxMon, level);
            count++;
        }
    }
    return count;
}
