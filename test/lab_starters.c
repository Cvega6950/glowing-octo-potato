// Crystal Imperium: PROF. ELM's three Poke Balls and the generation the player chose (src/lab_starters.c,
// DECISIONS.md D61)
#include "global.h"
#include "event_data.h"
#include "lab_starters.h"
#include "starter_choose.h"
#include "test/test.h"
#include "constants/vars.h"

#define ONE_TYPE_OFF 31 // src/challenge_menu.c: the One-Type Challenge off (a new game's setting)

static bool32 HasType(u16 species, enum Type type)
{
    return GetSpeciesType(species, 0) == type || GetSpeciesType(species, 1) == type;
}

// The rival's teams, the stolen ball and Jessica's trade are keyed on the ball (VAR_STARTER_MON), so
// every generation's three must be grass, fire and water in that order, and first stages
TEST("Lab starters: every generation's balls hold its grass, fire and water first partners")
{
    static const enum Type sBallTypes[] = { TYPE_GRASS, TYPE_FIRE, TYPE_WATER };
    u32 generation, ball;

    gSaveBlock3Ptr->challengeSettings.tx_Challenges_OneTypeChallenge = ONE_TYPE_OFF;
    VarSet(VAR_MONO_STARTER_TYPE, TYPE_NONE);
    for (generation = 1; generation <= 9; generation++)
    {
        VarSet(VAR_STARTER_GENERATION, generation);
        for (ball = 0; ball < ARRAY_COUNT(sBallTypes); ball++)
        {
            u16 species = GetLabBallSpecies(ball);

            EXPECT(IsSpeciesEnabled(species));
            EXPECT(HasType(species, sBallTypes[ball]));
            EXPECT_EQ(GetSpeciesPreEvolution(species), SPECIES_NONE);
            // the credits' last slide and Mom's doll read the same Pokemon
            EXPECT_EQ(GetStarterPokemon(ball), species);
        }
    }
}

TEST("Lab starters: a game that never chose (0, older saves) and an unknown value have Johto's")
{
    VarSet(VAR_MONO_STARTER_TYPE, TYPE_NONE);
    VarSet(VAR_STARTER_GENERATION, 0);
    EXPECT_EQ(GetLabBallSpecies(0), SPECIES_CHIKORITA);
    EXPECT_EQ(GetLabBallSpecies(1), SPECIES_CYNDAQUIL);
    EXPECT_EQ(GetLabBallSpecies(2), SPECIES_TOTODILE);
    VarSet(VAR_STARTER_GENERATION, 10);
    EXPECT_EQ(GetLabBallSpecies(1), SPECIES_CYNDAQUIL);
    VarSet(VAR_STARTER_GENERATION, 9);
    EXPECT_EQ(GetLabBallSpecies(0), SPECIES_SPRIGATITO);
    EXPECT_EQ(GetLabBallSpecies(1), SPECIES_FUECOCO);
    EXPECT_EQ(GetLabBallSpecies(2), SPECIES_QUAXLY);
}

TEST("Lab starters: the MONO code's type wins over the generation")
{
    VarSet(VAR_STARTER_GENERATION, 4);
    VarSet(VAR_MONO_STARTER_TYPE, TYPE_DRAGON);
    EXPECT_EQ(GetLabBallSpecies(0), SPECIES_BAGON);
    EXPECT_EQ(GetLabBallSpecies(1), SPECIES_GIBLE);
    EXPECT_EQ(GetLabBallSpecies(2), SPECIES_DRATINI);
    VarSet(VAR_MONO_STARTER_TYPE, TYPE_NONE);
    EXPECT_EQ(GetLabBallSpecies(1), SPECIES_CHIMCHAR);
}
