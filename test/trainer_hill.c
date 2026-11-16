// Crystal Imperium (KNOWN_ISSUES #97, #98): where every Pokemon is treated as Lv. 50 (FLAG_LIMIT_TO_50, the
// Trainer Hill), nothing works from the stored Lv. 50: no level-up item, and the PC moves no Pokemon
// (src/pokemon_storage_system.c, tools/emurun/tests/raise_to_cap.emu)
#include "global.h"
#include "event_data.h"
#include "nuzlocke.h"
#include "pokemon.h"
#include "test/test.h"
#include "constants/flags.h"
#include "constants/items.h"

TEST("Trainer Hill: the Lv. 50 rule is FLAG_LIMIT_TO_50")
{
    FlagSet(FLAG_LIMIT_TO_50);
    EXPECT(ArePokemonTreatedAsLevel50());
    FlagClear(FLAG_LIMIT_TO_50);
    EXPECT(!ArePokemonTreatedAsLevel50());
}

// A Rare Candy worked from the stored Lv. 50: a Lv. 70 Pokemon came out Lv. 51 after the Hill
TEST("Trainer Hill: a Rare Candy can't be used while every Pokemon is treated as Lv. 50, and nothing is lowered")
{
    u32 exp;

    ZeroPlayerPartyMons();
    CreateMon(&gPlayerParty[0], SPECIES_CYNDAQUIL, 70, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&gPlayerParty[0]);
    exp = GetMonData(&gPlayerParty[0], MON_DATA_EXP);
    FlagSet(FLAG_LIMIT_TO_50);
    CalculateMonStats(&gPlayerParty[0]); // the Hill's OnLoad
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 50);
    EXPECT(PokemonUseItemEffects(&gPlayerParty[0], ITEM_RARE_CANDY, 0, 0, FALSE)); // can't be used
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_EXP), exp);
    FlagClear(FLAG_LIMIT_TO_50);
    CalculateMonStats(&gPlayerParty[0]); // leaving the Hill
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 70);
    // Outside the Hill it works as before
    EXPECT(!PokemonUseItemEffects(&gPlayerParty[0], ITEM_RARE_CANDY, 0, 0, FALSE));
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_LEVEL), 71);
    ZeroPlayerPartyMons();
}

// A Nuzlocke's sweep (after field poison) moved a fainted Pokemon into the PC with the HP it lost against Lv. 50
TEST("Trainer Hill: a Nuzlocke's fainted Pokemon stays in the party while every Pokemon is treated as Lv. 50")
{
    u32 hp = 0;

    ZeroPlayerPartyMons();
    FlagSet(FLAG_SYS_POKEMON_GET);
    FlagSet(FLAG_START_NUZLOCKE);
    FlagClear(FLAG_END_NUZLOCKE);
    gSaveBlock3Ptr->challengeSettings.tx_Challenges_Nuzlocke = 1;
    CreateMon(&gPlayerParty[0], SPECIES_QUILAVA, 70, 0, OTID_STRUCT_PLAYER_ID);
    CreateMon(&gPlayerParty[1], SPECIES_RATTATA, 70, 0, OTID_STRUCT_PLAYER_ID);
    CalculateMonStats(&gPlayerParty[0]);
    CalculateMonStats(&gPlayerParty[1]);
    FlagSet(FLAG_LIMIT_TO_50);
    CalculateMonStats(&gPlayerParty[0]);
    CalculateMonStats(&gPlayerParty[1]);
    SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
    NuzlockeDeleteFaintedPartyPokemon();
    EXPECT_EQ(GetMonData(&gPlayerParty[0], MON_DATA_SPECIES), SPECIES_QUILAVA);
    FlagClear(FLAG_LIMIT_TO_50);
    gSaveBlock3Ptr->challengeSettings.tx_Challenges_Nuzlocke = 0;
    FlagClear(FLAG_START_NUZLOCKE);
    FlagClear(FLAG_SYS_POKEMON_GET);
    ZeroPlayerPartyMons();
}
