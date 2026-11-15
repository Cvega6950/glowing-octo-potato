// Crystal Imperium: PROF. ELM's three Poke Balls (DECISIONS.md D61). As in Emerald Imperium, the
// player may fill them with the first partners of any generation, 1 to 9, and change them until one
// is taken: ELM asks at the end of his intro and whenever the player talks to him before taking one
// (data/maps/NewBarkTown_Lab_hns/scripts.inc). VAR_STARTER_GENERATION holds the generation; 0 (a game
// that never chose, an older save) means Johto's.
//
// The balls stay grass, fire and water (VAR_STARTER_MON 0-2), so everything keyed on the ball works
// as before: the rival's teams, which are Johto's counter to the player's ball as Emerald Imperium's
// rival keeps Hoenn's, the stolen ball in the police scene, Jessica's Tauros trade.
#include "global.h"
#include "challenge_menu.h"
#include "cheat_codes.h"
#include "event_data.h"
#include "lab_starters.h"
#include "pokemon.h"
#include "randomizer.h"
#include "script.h"
#include "string_util.h"
#include "constants/species.h"
#include "constants/vars.h"

#define STARTER_GENERATION_COUNT 9
#define STARTER_GENERATION_JOHTO 2

// Each generation's grass, fire and water first partners, the balls' order
static const u16 sGenerationStarters[STARTER_GENERATION_COUNT][3] =
{
    { SPECIES_BULBASAUR,  SPECIES_CHARMANDER, SPECIES_SQUIRTLE },
    { SPECIES_CHIKORITA,  SPECIES_CYNDAQUIL,  SPECIES_TOTODILE },
    { SPECIES_TREECKO,    SPECIES_TORCHIC,    SPECIES_MUDKIP },
    { SPECIES_TURTWIG,    SPECIES_CHIMCHAR,   SPECIES_PIPLUP },
    { SPECIES_SNIVY,      SPECIES_TEPIG,      SPECIES_OSHAWOTT },
    { SPECIES_CHESPIN,    SPECIES_FENNEKIN,   SPECIES_FROAKIE },
    { SPECIES_ROWLET,     SPECIES_LITTEN,     SPECIES_POPPLIO },
    { SPECIES_GROOKEY,    SPECIES_SCORBUNNY,  SPECIES_SOBBLE },
    { SPECIES_SPRIGATITO, SPECIES_FUECOCO,    SPECIES_QUAXLY },
};

// 1-9
static u32 GetStarterGeneration(void)
{
    u32 generation = VarGet(VAR_STARTER_GENERATION);

    if (generation < 1 || generation > STARTER_GENERATION_COUNT)
        return STARTER_GENERATION_JOHTO;
    return generation;
}

// The Pokemon in PROF. ELM's Poke Ball `ball` (0 grass, 1 fire, 2 water): the MONO code's type's
// (D37), else the chosen generation's. The starter randomizer and the One-Type Challenge replace it
// when the ball is looked at (ScrCmd_showmonpic), as they did the Johto starters.
u16 GetLabBallSpecies(u32 ball)
{
    u16 species;

    ball %= ARRAY_COUNT(sGenerationStarters[0]);
    species = GetMonoStarterSpecies(ball);
    if (species == SPECIES_NONE)
        species = sGenerationStarters[GetStarterGeneration() - 1][ball];
    return species;
}

// callnative (PROF. ELM's lab): VAR_RESULT = the Pokemon in Poke Ball VAR_STARTER_MON
void GetLabStarterSpecies(struct ScriptContext *ctx)
{
    gSpecialVar_Result = GetLabBallSpecies(VarGet(VAR_STARTER_MON));
}

// callnative: VAR_RESULT = TRUE if ELM offers the generations, FALSE while the MONO code, the
// One-Type Challenge or the starter randomizer decides his Pokemon (the choice would change nothing,
// or only which random Pokemon came out)
void StarterGeneration_CanChoose(struct ScriptContext *ctx)
{
    gSpecialVar_Result = GetMonoStarterSpecies(0) == SPECIES_NONE && !IsOneTypeChallengeActive();
#if RANDOMIZER_AVAILABLE
    if (RandomizerFeatureEnabled(RANDOMIZE_STARTER_AND_GIFT_MON))
        gSpecialVar_Result = FALSE;
#endif
}

// callnative: VAR_0x8004 = the menu row of the current generation, where the cursor starts
void StarterGeneration_GetMenuRow(struct ScriptContext *ctx)
{
    gSpecialVar_0x8004 = GetStarterGeneration() - 1;
}

// callnative: the generation from the menu's row in VAR_RESULT
void StarterGeneration_Set(struct ScriptContext *ctx)
{
    if (gSpecialVar_Result < STARTER_GENERATION_COUNT)
        VarSet(VAR_STARTER_GENERATION, gSpecialVar_Result + 1);
}

// callnative: STR_VAR_1-3 = the names of the three balls' Pokemon
void StarterGeneration_BufferBallSpecies(struct ScriptContext *ctx)
{
    StringCopy(gStringVar1, GetSpeciesName(GetLabBallSpecies(0)));
    StringCopy(gStringVar2, GetSpeciesName(GetLabBallSpecies(1)));
    StringCopy(gStringVar3, GetSpeciesName(GetLabBallSpecies(2)));
}
