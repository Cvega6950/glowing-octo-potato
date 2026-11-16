// Crystal Imperium: the PC's RAISE TO LV. CAP (src/raise_to_cap.c, DECISIONS.md D63)
#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "pokemon_storage_system.h"
#include "raise_to_cap.h"
#include "test/test.h"
#include "constants/flags.h"

// The tests' zeroed save has every setting at 0: LEVEL CAP OFF, no Nuzlocke, no badges. CreateMon leaves the
// stats (and HP) at 0: CalculateMonStats works them out, as the game's own callers do

static void ClearCapFlags(void)
{
    u32 i;

    for (i = FLAG_BADGE01_GET; i < FLAG_BADGE01_GET + NUM_BADGES; i++)
        FlagClear(i);
    FlagClear(FLAG_IS_CHAMPION);
    FlagClear(FLAG_IS_KANTO_CHAMPION);
}

static void SetLevelCapSetting(u32 setting)
{
    gSaveBlock3Ptr->challengeSettings.tx_Challenges_LevelCap = setting;
}

static u32 ExpAt(u32 species, u32 level)
{
    return gExperienceTables[gSpeciesInfo[species].growthRate][level];
}

TEST("Raise to cap: the level is the level cap, and with the cap off the NORMAL cap of the player's progress")
{
    ClearCapFlags();
    SetLevelCapSetting(1); // NORMAL
    EXPECT_EQ(GetRaiseToCapLevel(), 15);
    SetLevelCapSetting(2); // HARD
    EXPECT_EQ(GetRaiseToCapLevel(), 12);
    SetLevelCapSetting(0); // OFF: not 100
    EXPECT_EQ(GetRaiseToCapLevel(), 15);

    FlagSet(FLAG_BADGE01_GET);
    SetLevelCapSetting(1);
    EXPECT_EQ(GetRaiseToCapLevel(), 24);
    SetLevelCapSetting(2);
    EXPECT_EQ(GetRaiseToCapLevel(), 21);
    SetLevelCapSetting(0);
    EXPECT_EQ(GetRaiseToCapLevel(), 24);

    FlagSet(FLAG_IS_CHAMPION);
    SetLevelCapSetting(1);
    EXPECT_EQ(GetRaiseToCapLevel(), 90);
    SetLevelCapSetting(0);
    EXPECT_EQ(GetRaiseToCapLevel(), 90);

    FlagSet(FLAG_IS_KANTO_CHAMPION);
    SetLevelCapSetting(2);
    EXPECT_EQ(GetRaiseToCapLevel(), 100);
    SetLevelCapSetting(0);
    EXPECT_EQ(GetRaiseToCapLevel(), 100);
    ClearCapFlags();
}

TEST("Raise to cap: a boxed Pokemon below the level gets that level's experience and nothing else changes")
{
    struct Pokemon mon;
    struct BoxPokemon *boxMon = &mon.box;
    u32 move1, friendship;

    CreateMon(&mon, SPECIES_CATERPIE, 5, 0, OTID_STRUCT_PLAYER_ID);
    move1 = GetBoxMonData(boxMon, MON_DATA_MOVE1);
    friendship = GetBoxMonData(boxMon, MON_DATA_FRIENDSHIP);
    EXPECT(CanRaiseBoxMonToLevel(boxMon, 15));
    RaiseBoxMonToLevel(boxMon, 15);
    EXPECT_EQ(GetLevelFromBoxMonExp(boxMon), 15);
    EXPECT_EQ(GetBoxMonData(boxMon, MON_DATA_EXP), ExpAt(SPECIES_CATERPIE, 15));
    EXPECT_EQ(GetBoxMonData(boxMon, MON_DATA_SPECIES), SPECIES_CATERPIE); // no evolution
    EXPECT_EQ(GetBoxMonData(boxMon, MON_DATA_MOVE1), move1); // no move learned
    EXPECT_EQ(GetBoxMonData(boxMon, MON_DATA_FRIENDSHIP), friendship);
    EXPECT(!CanRaiseBoxMonToLevel(boxMon, 15)); // at the level now
}

TEST("Raise to cap: Eggs, marked Pokemon and those at or above the level are left as they are")
{
    struct Pokemon mon;
    u32 data;

    CreateMon(&mon, SPECIES_TOGEPI, 5, 0, OTID_STRUCT_PLAYER_ID);
    data = TRUE;
    SetMonData(&mon, MON_DATA_IS_EGG, &data);
    EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));
    EXPECT(!CanRaisePartyMonToLevel(&mon, 15));

    for (data = 1; data <= 8; data <<= 1)
    {
        CreateMon(&mon, SPECIES_PIDGEY, 5, 0, OTID_STRUCT_PLAYER_ID);
        SetMonData(&mon, MON_DATA_MARKINGS, &data);
        EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));
        EXPECT(!CanRaisePartyMonToLevel(&mon, 15));
    }

    CreateMon(&mon, SPECIES_PIDGEY, 15, 0, OTID_STRUCT_PLAYER_ID);
    EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));
    EXPECT(!CanRaisePartyMonToLevel(&mon, 15));
    CreateMon(&mon, SPECIES_PIDGEY, 20, 0, OTID_STRUCT_PLAYER_ID); // never lowered
    EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));
    EXPECT(!CanRaisePartyMonToLevel(&mon, 15));

    ZeroMonData(&mon); // an empty slot
    EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));
}

TEST("Raise to cap: a boxed Pokemon keeps the HP it lost, and a fainted one stays fainted when withdrawn")
{
    struct Pokemon mon, withdrawn;
    u32 hp;

    CreateMon(&mon, SPECIES_RATTATA, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&mon);
    hp = GetMonData(&mon, MON_DATA_MAX_HP) - 3;
    SetMonData(&mon, MON_DATA_HP, &hp);
    RaiseBoxMonToLevel(&mon.box, 15);
    BoxMonToMon(&mon.box, &withdrawn);
    EXPECT_EQ(GetMonData(&withdrawn, MON_DATA_LEVEL), 15);
    EXPECT_EQ(GetMonData(&withdrawn, MON_DATA_HP), GetMonData(&withdrawn, MON_DATA_MAX_HP) - 3);

    CreateMon(&mon, SPECIES_RATTATA, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&mon);
    hp = 0;
    SetMonData(&mon, MON_DATA_HP, &hp);
    RaiseBoxMonToLevel(&mon.box, 15);
    BoxMonToMon(&mon.box, &withdrawn);
    EXPECT_EQ(GetMonData(&withdrawn, MON_DATA_LEVEL), 15);
    EXPECT_EQ(GetMonData(&withdrawn, MON_DATA_HP), 0);
}

TEST("Raise to cap: a party Pokemon's stats follow and its HP goes up by the max HP it gains")
{
    struct Pokemon withdrawn;
    u32 hp, oldMaxHp;

    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_CYNDAQUIL, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&gPlayerParty[0]);
    oldMaxHp = GetMonData(&gPlayerParty[0], MON_DATA_MAX_HP);
    hp = oldMaxHp - 2;
    SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
    RaisePartyMonToLevel(&gPlayerParty[0], 15);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 15);
    EXPECT_GT(GetMonData(&gPlayerParty[0], MON_DATA_MAX_HP), oldMaxHp);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_HP), GetMonData(&gPlayerParty[0], MON_DATA_MAX_HP) - 2);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_SPECIES), SPECIES_CYNDAQUIL);

    // A fainted one stays fainted, also when it goes through the PC (the box keeps the HP it lost)
    CreateMon(&gPlayerParty[1], SPECIES_SENTRET, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&gPlayerParty[1]);
    hp = 0;
    SetMonData(&gPlayerParty[1], MON_DATA_HP, &hp);
    RaisePartyMonToLevel(&gPlayerParty[1], 15);
    EXPECT_EQ(GetMonData(&gPlayerParty[1], MON_DATA_LEVEL), 15);
    EXPECT_EQ(GetMonData(&gPlayerParty[1], MON_DATA_HP), 0);
    BoxMonToMon(&gPlayerParty[1].box, &withdrawn);
    EXPECT_EQ(GetMonData(&withdrawn, MON_DATA_HP), 0);
    ZeroPlayerPartyMons();
}

TEST("Raise to cap: in a Nuzlocke a fainted Pokemon isn't raised")
{
    struct Pokemon mon;
    u32 hp = 0;

    FlagSet(FLAG_SYS_POKEMON_GET);
    FlagSet(FLAG_START_NUZLOCKE);
    FlagClear(FLAG_END_NUZLOCKE);
    gSaveBlock3Ptr->challengeSettings.tx_Challenges_Nuzlocke = 1;

    CreateMon(&mon, SPECIES_RATTATA, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&mon);
    EXPECT(CanRaisePartyMonToLevel(&mon, 15));
    EXPECT(CanRaiseBoxMonToLevel(&mon.box, 15));
    SetMonData(&mon, MON_DATA_HP, &hp);
    EXPECT(!CanRaisePartyMonToLevel(&mon, 15));
    EXPECT(!CanRaiseBoxMonToLevel(&mon.box, 15));

    gSaveBlock3Ptr->challengeSettings.tx_Challenges_Nuzlocke = 0;
    EXPECT(CanRaisePartyMonToLevel(&mon, 15)); // without a Nuzlocke it is raised, and stays fainted
    EXPECT(CanRaiseBoxMonToLevel(&mon.box, 15));
    FlagClear(FLAG_START_NUZLOCKE);
    FlagClear(FLAG_SYS_POKEMON_GET);
}

TEST("Raise to cap: the count asked about is the count raised, party and boxes")
{
    u32 counted, raised, box, i;

    ZeroPlayerPartyMons();
    for (box = 0; box < TOTAL_BOXES_COUNT; box++)
    {
        for (i = 0; i < IN_BOX_COUNT; i++)
            ZeroBoxMonData(GetBoxedMonPtr(box, i));
    }
    CreateMon(&gPlayerParty[0], SPECIES_CYNDAQUIL, 5, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&gPlayerParty[0]);
    CreateMon(&gPlayerParty[1], SPECIES_MAGIKARP, 20, 0, OTID_STRUCT_PLAYER_ID); // above: left alone
    CalculateMonStats(&gPlayerParty[1]);
    CreateBoxMon(GetBoxedMonPtr(0, 0), SPECIES_RATTATA, 3, 0, OTID_STRUCT_PLAYER_ID);
    CreateBoxMon(GetBoxedMonPtr(0, 29), SPECIES_CATERPIE, 4, 0, OTID_STRUCT_PLAYER_ID);
    CreateBoxMon(GetBoxedMonPtr(TOTAL_BOXES_COUNT - 1, 7), SPECIES_SPEAROW, 5, 0, OTID_STRUCT_PLAYER_ID);

    counted = CountMonsToRaise(15);
    EXPECT_EQ(counted, 4);
    raised = RaisePartyToLevel(15);
    for (box = 0; box < TOTAL_BOXES_COUNT; box++)
        raised += RaiseBoxToLevel(box, 15);
    EXPECT_EQ(raised, counted);
    EXPECT_EQ(CountMonsToRaise(15), 0);
    EXPECT_EQ(GetMonData(&gPlayerParty[1], MON_DATA_LEVEL), 20);
    EXPECT_EQ(GetLevelFromBoxMonExp(GetBoxedMonPtr(TOTAL_BOXES_COUNT - 1, 7)), 15);
    ZeroPlayerPartyMons();
    ZeroBoxMonData(GetBoxedMonPtr(0, 0));
    ZeroBoxMonData(GetBoxedMonPtr(0, 29));
    ZeroBoxMonData(GetBoxedMonPtr(TOTAL_BOXES_COUNT - 1, 7));
}

// Inside the Trainer Hill FLAG_LIMIT_TO_50 stores Lv. 50 for every party Pokemon: what counts is the level its
// experience gives, so a Lv. 100 Pokemon there isn't set down to Lv. 90's experience
TEST("Raise to cap: a party Pokemon's level is the one its experience gives, so one held at Lv. 50 isn't lowered")
{
    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_CYNDAQUIL, 100, 0, OTID_STRUCT_PLAYER_ID);
    FlagSet(FLAG_LIMIT_TO_50);
    CalculateMonStats(&gPlayerParty[0]);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 50);
    EXPECT(!CanRaisePartyMonToLevel(&gPlayerParty[0], 90));
    FlagClear(FLAG_LIMIT_TO_50);
    CalculateMonStats(&gPlayerParty[0]);
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 100);
    ZeroPlayerPartyMons();
}

// There a boxed Pokemon's HP is also worked out at Lv. 50, so one that fainted can read as alive: the menu refuses
TEST("Raise to cap: it can't be used while every Pokemon is held at Lv. 50")
{
    FlagSet(FLAG_LIMIT_TO_50);
    EXPECT(!CanUseRaiseToCap());
    FlagClear(FLAG_LIMIT_TO_50);
    EXPECT(CanUseRaiseToCap());
}
