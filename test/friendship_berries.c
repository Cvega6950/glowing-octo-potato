// Crystal Imperium (DECISIONS.md D67): the six friendship Berries (Pomeg, Kelpsy, Qualot, Hondew, Grepa,
// Tamato) raise friendship to the maximum in one use and still lower their EV by 10 (src/pokemon.c,
// tools/emurun/tests/friendship_berries.emu)
#include "global.h"
#include "pokemon.h"
#include "test/test.h"
#include "constants/items.h"
#include "constants/species.h"

static const u16 sFriendshipBerries[] = {
    ITEM_POMEG_BERRY, ITEM_KELPSY_BERRY, ITEM_QUALOT_BERRY, ITEM_HONDEW_BERRY, ITEM_GREPA_BERRY, ITEM_TAMATO_BERRY,
};

// The EV each Berry lowers, in the same order
static const u8 sBerryEvs[] = {
    MON_DATA_HP_EV, MON_DATA_ATK_EV, MON_DATA_DEF_EV, MON_DATA_SPATK_EV, MON_DATA_SPDEF_EV, MON_DATA_SPEED_EV,
};

static void SetFriendshipAndEv(struct Pokemon *mon, u8 friendship, u32 evField, u8 ev)
{
    SetMonData(mon, MON_DATA_FRIENDSHIP, &friendship);
    SetMonData(mon, evField, &ev);
}

TEST("Friendship Berries: the six are the ones the rule covers")
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sFriendshipBerries); i++)
        EXPECT(IsMaxFriendshipBerry(sFriendshipBerries[i]));
    EXPECT(!IsMaxFriendshipBerry(ITEM_HP_UP));
    EXPECT(!IsMaxFriendshipBerry(ITEM_ORAN_BERRY));
    EXPECT(!IsMaxFriendshipBerry(ITEM_SOOTHE_BELL));
}

TEST("Friendship Berries: one raises friendship to the maximum and lowers its EV by 10")
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sFriendshipBerries); i++)
    {
        ZeroPlayerPartyMons();
        CreateMon(&gPlayerParty[0], SPECIES_GOLBAT, 20, 0, OTID_STRUCT_PLAYER_ID);
        SetFriendshipAndEv(&gPlayerParty[0], 70, sBerryEvs[i], 100);
        CalculateMonStats(&gPlayerParty[0]);
        EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], sFriendshipBerries[i], 0, 0)); // used
        EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_FRIENDSHIP), MAX_FRIENDSHIP);
        EXPECT_EQ(GetMonData(&gPlayerParty[0], sBerryEvs[i]), 90);
    }
    ZeroPlayerPartyMons();
}

TEST("Friendship Berries: with no EV to lower one still raises friendship to the maximum")
{
    u32 i;

    for (i = 0; i < ARRAY_COUNT(sFriendshipBerries); i++)
    {
        ZeroPlayerPartyMons();
        CreateMon(&gPlayerParty[0], SPECIES_GOLBAT, 20, 0, OTID_STRUCT_PLAYER_ID);
        SetFriendshipAndEv(&gPlayerParty[0], 0, sBerryEvs[i], 0);
        CalculateMonStats(&gPlayerParty[0]);
        EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], sFriendshipBerries[i], 0, 0));
        EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_FRIENDSHIP), MAX_FRIENDSHIP);
        EXPECT_EQ(GetMonData(&gPlayerParty[0], sBerryEvs[i]), 0);
    }
    ZeroPlayerPartyMons();
}

TEST("Friendship Berries: at maximum friendship one only lowers the EV, and then changes nothing")
{
    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_GOLBAT, 20, 0, OTID_STRUCT_PLAYER_ID);
    SetFriendshipAndEv(&gPlayerParty[0], MAX_FRIENDSHIP, MON_DATA_HP_EV, 15);
    CalculateMonStats(&gPlayerParty[0]);
    EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], ITEM_POMEG_BERRY, 0, 0));
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_FRIENDSHIP), MAX_FRIENDSHIP);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_HP_EV), 5);
    EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], ITEM_POMEG_BERRY, 0, 0));
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_HP_EV), 0);
    // Nothing left to change: friendship stays 255 and the EV 0. The item code reports the Berry as
    // used either way (as before); the party menu compares the two values and says it won't have any
    // effect, keeping the Berry (ItemUseCB_ReduceEV; tools/emurun/tests/friendship_berries.emu)
    ExecuteTableBasedItemEffect(&gPlayerParty[0], ITEM_POMEG_BERRY, 0, 0);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_FRIENDSHIP), MAX_FRIENDSHIP);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_HP_EV), 0);
    ZeroPlayerPartyMons();
}

TEST("Friendship Berries: after one, a friendship evolution happens at the next level-up")
{
    bool32 canStopEvo = TRUE;

    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_GOLBAT, 20, 0, OTID_STRUCT_PLAYER_ID);
    SetFriendshipAndEv(&gPlayerParty[0], 70, MON_DATA_HP_EV, 0);
    CalculateMonStats(&gPlayerParty[0]);
    EXPECT_EQ(GetEvolutionTargetSpecies(&gPlayerParty[0], EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_NONE);
    EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], ITEM_POMEG_BERRY, 0, 0));
    EXPECT_EQ(GetEvolutionTargetSpecies(&gPlayerParty[0], EVO_MODE_NORMAL, ITEM_NONE, NULL, &canStopEvo, CHECK_EVO), SPECIES_CROBAT);
    ZeroPlayerPartyMons();
}

TEST("Friendship Berries: other items keep their small friendship change (a vitamin)")
{
    u32 friendship;

    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_GOLBAT, 20, 0, OTID_STRUCT_PLAYER_ID);
    SetFriendshipAndEv(&gPlayerParty[0], 70, MON_DATA_HP_EV, 0);
    CalculateMonStats(&gPlayerParty[0]);
    EXPECT(!ExecuteTableBasedItemEffect(&gPlayerParty[0], ITEM_HP_UP, 0, 0));
    friendship = GetMonData(&gPlayerParty[0], MON_DATA_FRIENDSHIP);
    EXPECT_GT(friendship, 70);
    EXPECT_LT(friendship, 80);
    ZeroPlayerPartyMons();
}
