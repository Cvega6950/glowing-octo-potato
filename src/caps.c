#include "global.h"
#include "battle.h"
#include "event_data.h"
#include "caps.h"
#include "pokemon.h"

static u8 GetCurrentBadgeCount(void)
{
    u32 badgeCount = 0, flag;

    for (flag = FLAG_BADGE01_GET; flag < FLAG_BADGE01_GET + NUM_BADGES; flag++)
    {
        if (FlagGet(flag))
            badgeCount++;
    }
    return badgeCount;
}

// specialvar VAR_RESULT, GetBadgeCount
u16 GetBadgeCount(void)
{
    return GetCurrentBadgeCount();
}

// Platinum Imperium: Emerald Imperium-style caps (Crystal Imperium's), up to 85 for the Elite Four.
// HARD caps are a few levels lower until the Elite Four.
static const u8 sLevelCapTable_Normal[] =
{
    [0] = 15,  // no badges
    [1] = 24,  // badge 1 (Roark)
    [2] = 33,  // badge 2 (Gardenia)
    [3] = 42,  // badge 3 (Fantina)
    [4] = 50,  // badge 4 (Maylene)
    [5] = 58,  // badge 5 (Crasher Wake)
    [6] = 66,  // badge 6 (Byron)
    [7] = 75,  // badge 7 (Candice)
    [8] = 85,  // badge 8 (Volkner): the Elite Four and Cynthia
};

static const u8 sLevelCapTable_Hard[] =
{
    [0] = 12,
    [1] = 21,
    [2] = 30,
    [3] = 39,
    [4] = 47,
    [5] = 55,
    [6] = 63,
    [7] = 72,
    [8] = 85,
};

// Pokemon Platinum's levels by stage: the level of each Gym Leader's ace, then Cynthia's, which the
// base game's trainers were made for
static const u8 sPlatinumLevelCaps[LEVEL_CAP_STAGE_CHAMPION + 1] = {14, 22, 26, 32, 37, 41, 44, 50, 62, MAX_LEVEL};

// The stage of the game the level caps go by: the badge count (0-8), then the League won
u32 GetLevelCapStage(void)
{
    u8 badgeCount = GetCurrentBadgeCount();

    if (FlagGet(FLAG_IS_CHAMPION))
        return LEVEL_CAP_STAGE_CHAMPION;
    return badgeCount > 8 ? 8 : badgeCount;
}

// The level cap at a stage with the player's level cap setting: the HARD table when it is HARD,
// the NORMAL table otherwise (also when the cap is off, so bosses keep their levels then)
u32 GetLevelCapAtStage(u32 stage)
{
    if (stage >= LEVEL_CAP_STAGE_CHAMPION)
        return MAX_LEVEL;
    if (gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap == 2)
        return sLevelCapTable_Hard[stage];
    return sLevelCapTable_Normal[stage];
}

// The level of every Pokemon of a boss: the level cap at the boss's stage (the earliest point its
// battle can happen) or at the player's, whichever comes later
u32 GetBossLevel(u32 bossStage)
{
    u32 stage = GetLevelCapStage();

    return GetLevelCapAtStage(stage > bossStage ? stage : bossStage);
}

// A level from Platinum's level curve on the player's: a trainer made a few levels below
// Platinum's level for its part of the game is as far below the cap there now, in proportion
u32 GetLevelOnCapCurve(u32 level)
{
    u32 stage, ptFrom = 1, capFrom = 1;

    if (level <= 1)
        return level;
    for (stage = 0; stage <= LEVEL_CAP_STAGE_CHAMPION; stage++)
    {
        u32 ptTo = sPlatinumLevelCaps[stage];
        u32 capTo = GetLevelCapAtStage(stage);

        if (level <= ptTo)
            return capFrom + ((level - ptFrom) * (capTo - capFrom) + (ptTo - ptFrom) / 2) / (ptTo - ptFrom);
        ptFrom = ptTo;
        capFrom = capTo;
    }
    return MAX_LEVEL;
}

// With a level cap on, no Pokemon the player meets or is given is above it
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

    u32 i;

    // Platinum Imperium: the challenge menu's LEVEL CAP
    if (gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap != 0)
        return GetLevelCapAtStage(GetLevelCapStage());

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
