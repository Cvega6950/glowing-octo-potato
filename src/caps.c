#include "global.h"
#include "battle.h"
#include "event_data.h"
#include "caps.h"
#include "pokemon.h"

static u8 GetCurrentBadgeCount(void)
{
    u16 i;
    u8 badgeCount = 0;
    for (i = FLAG_BADGE01_GET; i < FLAG_BADGE01_GET + NUM_BADGES; i++)
    {
        if (FlagGet(i))
            badgeCount++;
    }
    return badgeCount;
}

// Crystal Imperium: specialvar VAR_RESULT, GetBadgeCount (the Goldenrod Dept. Store 5F TM shop).
// Gyms 5-7 can be taken in any order, so FLAG_BADGE06_GET alone doesn't mean six badges.
u16 GetBadgeCount(void)
{
    return GetCurrentBadgeCount();
}

static const u8 sLevelCapTable_Normal[] =
{
    [0] = 11,  // no badges
    [1] = 16,  // badge 1
    [2] = 21,  // badge 2
    [3] = 25,  // badge 3
    [4] = 31,  // badge 4
    [5] = 36,  // badge 5
    [6] = 38,  // badge 6
    [7] = 45,  // badge 7
    [8] = 56,  // badge 8
};

static const u8 sLevelCapTable_Hard[] =
{
    [0] = 8,
    [1] = 15,
    [2] = 20,
    [3] = 23,
    [4] = 29,
    [5] = 33,
    [6] = 37,
    [7] = 42,
    [8] = 54,
};

// Post-league caps, matching HnS: beating the Johto Elite Four raises the cap to
// 70 for the Kanto half, and only beating the Kanto league removes it entirely.
#define KANTO_MAX_LEVEL 70

// Crystal Imperium: the stage of the game the level caps go by: the badge count (0-8), then the
// Johto League won and the Kanto League won (include/caps.h)
u32 GetLevelCapStage(void)
{
    u8 badgeCount = GetCurrentBadgeCount();

#if IS_HNS
    if (FlagGet(FLAG_IS_KANTO_CHAMPION))
        return LEVEL_CAP_STAGE_KANTO_CHAMPION;
    if (FlagGet(FLAG_IS_CHAMPION))
        return LEVEL_CAP_STAGE_JOHTO_CHAMPION;
#else
    if (FlagGet(FLAG_IS_CHAMPION))
        return LEVEL_CAP_STAGE_KANTO_CHAMPION;
#endif
    return badgeCount > 8 ? 8 : badgeCount;
}

// The level cap at a stage with the player's level cap setting: the HARD table when it is HARD,
// the NORMAL table otherwise (also when the cap is off, so bosses keep their levels then)
u32 GetLevelCapAtStage(u32 stage)
{
    if (stage >= LEVEL_CAP_STAGE_KANTO_CHAMPION)
        return MAX_LEVEL;
    if (stage == LEVEL_CAP_STAGE_JOHTO_CHAMPION)
        return KANTO_MAX_LEVEL;
    if (gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap == 2)
        return sLevelCapTable_Hard[stage];
    return sLevelCapTable_Normal[stage];
}

// The level of every Pokemon of a boss (DECISIONS.md D21): the level cap at the boss's stage (the
// earliest point its battle can happen) or at the player's, whichever comes later. In play that
// is the player's own level cap, HARD caps included.
u32 GetBossLevel(u32 bossStage)
{
    u32 stage = GetLevelCapStage();

    return GetLevelCapAtStage(stage > bossStage ? stage : bossStage);
}

// Crystal Imperium: with a level cap on, no Pokemon the player meets or is given is above it
// (DECISIONS.md D28; DexNav's level bonuses had turned up a level-12 Turtwig at cap 8)
u32 GetLevelWithinCap(u32 level)
{
    u32 cap = GetCurrentLevelCap();

    return level > cap ? cap : level;
}

u32 GetCurrentLevelCap(void)
{
    static const u32 sLevelCapFlagMap[][2] =
    {
        {FLAG_BADGE01_GET, 15},
        {FLAG_BADGE02_GET, 19},
        {FLAG_BADGE03_GET, 24},
        {FLAG_BADGE04_GET, 29},
        {FLAG_BADGE05_GET, 31},
        {FLAG_BADGE06_GET, 33},
        {FLAG_BADGE07_GET, 42},
        {FLAG_BADGE08_GET, 46},
        {FLAG_IS_CHAMPION, 58},
    };

    u8 challengeLevelCap = gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap;

    if (challengeLevelCap != 0)
    {
        u8 badgeCount = GetCurrentBadgeCount();
        if (badgeCount > 8)
            badgeCount = 8;

#if IS_HNS
        if (FlagGet(FLAG_IS_KANTO_CHAMPION))
            return MAX_LEVEL;

        if (FlagGet(FLAG_IS_CHAMPION))
            return KANTO_MAX_LEVEL;
#else
        if (FlagGet(FLAG_IS_CHAMPION))
            return MAX_LEVEL;
#endif

        if (challengeLevelCap == 1)
            return sLevelCapTable_Normal[badgeCount];
        else
            return sLevelCapTable_Hard[badgeCount];
    }

    u32 i;

    if (B_LEVEL_CAP_TYPE == LEVEL_CAP_FLAG_LIST)
    {
        for (i = 0; i < ARRAY_COUNT(sLevelCapFlagMap); i++)
        {
            if (!FlagGet(sLevelCapFlagMap[i][0]))
                return sLevelCapFlagMap[i][1];
        }
    }
    else if (B_LEVEL_CAP_TYPE == LEVEL_CAP_VARIABLE)
    {
        return VarGet(B_LEVEL_CAP_VARIABLE);
    }

    return MAX_LEVEL;
}

u32 GetSoftLevelCapExpValue(u32 level, u32 expValue)
{
    static const u32 sExpScalingDown[5] = { 4, 8, 16, 32, 64 };
    static const u32 sExpScalingUp[5]   = { 16, 8, 4, 2, 1 };

    u32 levelDifference;
    u32 currentLevelCap = GetCurrentLevelCap();

    if (B_EXP_CAP_TYPE == EXP_CAP_NONE)
        return expValue;

    if (level < currentLevelCap)
    {
        if (B_LEVEL_CAP_EXP_UP)
        {
            levelDifference = currentLevelCap - level;
            if (levelDifference > ARRAY_COUNT(sExpScalingUp) - 1)
                return expValue + (expValue / sExpScalingUp[ARRAY_COUNT(sExpScalingUp) - 1]);
            else
                return expValue + (expValue / sExpScalingUp[levelDifference]);
        }
        else
        {
            return expValue;
        }
    }
    else if (B_EXP_CAP_TYPE == EXP_CAP_HARD)
    {
        return 0;
    }
    else if (B_EXP_CAP_TYPE == EXP_CAP_SOFT)
    {
        levelDifference = level - currentLevelCap;
        if (levelDifference > ARRAY_COUNT(sExpScalingDown) - 1)
            return expValue / sExpScalingDown[ARRAY_COUNT(sExpScalingDown) - 1];
        else
            return expValue / sExpScalingDown[levelDifference];
    }
    else
    {
       return expValue;
    }
}

u32 GetCurrentEVCap(void)
{
    static const u16 sEvCapFlagMap[][2] = {
        // Define EV caps for each milestone
        {FLAG_BADGE01_GET, MAX_TOTAL_EVS *  1 / 17},
        {FLAG_BADGE02_GET, MAX_TOTAL_EVS *  3 / 17},
        {FLAG_BADGE03_GET, MAX_TOTAL_EVS *  5 / 17},
        {FLAG_BADGE04_GET, MAX_TOTAL_EVS *  7 / 17},
        {FLAG_BADGE05_GET, MAX_TOTAL_EVS *  9 / 17},
        {FLAG_BADGE06_GET, MAX_TOTAL_EVS * 11 / 17},
        {FLAG_BADGE07_GET, MAX_TOTAL_EVS * 13 / 17},
        {FLAG_BADGE08_GET, MAX_TOTAL_EVS * 15 / 17},
        {FLAG_IS_CHAMPION, MAX_TOTAL_EVS},
    };

    if (B_EV_CAP_TYPE == EV_CAP_FLAG_LIST)
    {
        for (u32 evCap = 0; evCap < ARRAY_COUNT(sEvCapFlagMap); evCap++)
        {
            if (!FlagGet(sEvCapFlagMap[evCap][0]))
                return sEvCapFlagMap[evCap][1];
        }
    }
    else if (B_EV_CAP_TYPE == EV_CAP_VARIABLE)
    {
        return VarGet(B_EV_CAP_VARIABLE);
    }
    else if (B_EV_CAP_TYPE == EV_CAP_NO_GAIN)
    {
        return 0;
    }

    return MAX_TOTAL_EVS;
}
