// Crystal Imperium: Wild Variety.
// Every Gen 1-9 Pokemon can be found on every route. A share of wild encounters (the WILD VARIETY
// option) is replaced by a random Pokemon from the variety pool, evolved as far as its level
// allows. The pool holds every base form (no pre-evolution), regional base forms included, but
// not battle-only forms or cosmetic form duplicates; Legendary, Mythical, Ultra Beast and Paradox
// Pokemon join it after the player becomes Champion. Besides that, DexNav can search for any
// Pokemon at all, in any evolution stage, on any route with wild encounters.
#include "global.h"
#include "battle_pike.h"
#include "battle_pyramid.h"
#include "bug_contest.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "wild_variety.h"
#include "constants/battle_pyramid.h"
#include "constants/flags.h"

#define VARIETY_POOL_SIZE 1100
#define VARIETY_POOL_MAGIC 0xC1A5
#define LEGEND_CHANCE 3 // percent of variety encounters after becoming Champion
#define POOL_PICK_TRIES 40

static EWRAM_DATA u16 sPool[VARIETY_POOL_SIZE] = {0};
static EWRAM_DATA u16 sPoolCount = 0;   // entries; the legendary ones come last
static EWRAM_DATA u16 sLegendStart = 0;
static EWRAM_DATA u16 sPoolMagic = 0;

// Stored in ChallengeSettings.tx_Features_WildVariety; 0 is the default (30%) so older saves get it
static const u8 sVarietyPercent[] = { 30, 60, 0, 15 };

u32 WildVariety_GetPercent(void)
{
    return sVarietyPercent[gSaveBlock3Ptr->challengeSettings.tx_Features_WildVariety];
}

static bool32 IsLegend(u16 species)
{
    const struct SpeciesInfo *info = &gSpeciesInfo[species];
    return info->isRestrictedLegendary || info->isSubLegendary || info->isMythical
        || info->isUltraBeast || info->isParadox;
}

static bool32 IsRegionalForm(u16 species)
{
    const struct SpeciesInfo *info = &gSpeciesInfo[species];
    return info->isAlolanForm || info->isGalarianForm || info->isHisuianForm || info->isPaldeanForm;
}

static bool32 IsWildForm(u16 species)
{
    const struct SpeciesInfo *info = &gSpeciesInfo[species];

    if (!IsSpeciesEnabled(species) || info->baseHP == 0 || info->randomizerMode == MON_RANDOMIZER_INVALID)
        return FALSE;
    if (info->isTotem || info->isMegaEvolution || info->isPrimalReversion || info->isUltraBurst
     || info->isGigantamax || info->isTeraForm)
        return FALSE;
    // One entry per Pokemon: its main form, plus regional forms
    return GET_BASE_SPECIES_ID(species) == species || IsRegionalForm(species);
}

static void BuildPool(void)
{
    u8 isEvolution[(NUM_SPECIES + 7) / 8] = {0};
    u32 species, i, pass;

    for (species = SPECIES_NONE + 1; species < NUM_SPECIES; species++)
    {
        const struct Evolution *evolutions;

        if (!IsSpeciesEnabled(species))
            continue;
        evolutions = GetSpeciesEvolutions(species);
        if (evolutions == NULL)
            continue;
        for (i = 0; evolutions[i].method != EVOLUTIONS_END; i++)
        {
            u32 target = SanitizeSpeciesId(evolutions[i].targetSpecies);
            if (evolutions[i].method != EVO_NONE)
                isEvolution[target / 8] |= 1 << (target % 8);
        }
    }

    sPoolCount = 0;
    for (pass = 0; pass < 2; pass++)
    {
        if (pass == 1)
            sLegendStart = sPoolCount;
        for (species = SPECIES_NONE + 1; species < NUM_SPECIES && sPoolCount < VARIETY_POOL_SIZE; species++)
        {
            if (isEvolution[species / 8] & (1 << (species % 8)))
                continue;
            if (!IsWildForm(species) || IsLegend(species) != (pass == 1))
                continue;
            sPool[sPoolCount++] = species;
        }
    }
    sPoolMagic = VARIETY_POOL_MAGIC;
}

static void BuildPoolIfNeeded(void)
{
    if (sPoolMagic != VARIETY_POOL_MAGIC)
        BuildPool();
}

// The level a wild Pokemon of the given evolution stage (0 = base form) needs to have evolved
// by this method. Level-up evolutions use their own level; friendship and other condition-only
// level-ups, stones, trades and special methods use fixed levels.
static u32 GetEvolutionLevel(const struct Evolution *evolution, u32 stage)
{
    switch (evolution->method)
    {
    case EVO_LEVEL:
    case EVO_LEVEL_BATTLE_ONLY:
        if (evolution->param != 0)
            return evolution->param;
        return stage == 0 ? 18 : 35;
    case EVO_ITEM:
    case EVO_TRADE:
    case EVO_SPIN:
    case EVO_SCRIPT_TRIGGER:
    case EVO_BATTLE_END:
        return stage == 0 ? 30 : 40;
    default:
        return MAX_LEVEL + 1; // never, e.g. Shedinja's split
    }
}

u16 WildVariety_EvolveForLevel(u16 species, u8 level)
{
    u32 stage;

    for (stage = 0; stage < 3; stage++)
    {
        const struct Evolution *evolutions = GetSpeciesEvolutions(species);
        u16 options[16];
        u32 i, count = 0;

        if (evolutions == NULL)
            break;
        for (i = 0; evolutions[i].method != EVOLUTIONS_END && count < ARRAY_COUNT(options); i++)
        {
            u32 target = SanitizeSpeciesId(evolutions[i].targetSpecies);
            if (!IsSpeciesEnabled(target) || gSpeciesInfo[target].randomizerMode == MON_RANDOMIZER_INVALID)
                continue;
            if (level >= GetEvolutionLevel(&evolutions[i], stage))
                options[count++] = target;
        }
        if (count == 0)
            break;
        species = options[Random() % count];
    }
    return species;
}

u16 WildVariety_TryReplaceSpecies(u16 species, u8 level, enum WildPokemonArea area)
{
    u32 percent = WildVariety_GetPercent();
    u32 first = 0, count, tries;
    bool32 water = (area == WILD_AREA_WATER || area == WILD_AREA_FISHING);

    if (percent == 0 || (area != WILD_AREA_LAND && !water))
        return species;
    // The Bug-Catching Contest and the Battle Frontier keep their own Pokemon
    if (GetBugContestFlag() || InBattlePike() || CurrentBattlePyramidLocation() != PYRAMID_LOCATION_NONE)
        return species;
    if (Random() % 100 >= percent)
        return species;

    BuildPoolIfNeeded();
    count = sLegendStart;
    if (FlagGet(FLAG_SYS_GAME_CLEAR) && sPoolCount > sLegendStart && Random() % 100 < LEGEND_CHANCE)
    {
        first = sLegendStart;
        count = sPoolCount - sLegendStart;
    }
    if (count == 0)
        return species;

    // Surfing and fishing turn up Water-type Pokemon
    for (tries = 0; tries < POOL_PICK_TRIES; tries++)
    {
        u16 pick = sPool[first + Random() % count];
        if (!water || first != 0 || IsSpeciesOfType(pick, TYPE_WATER))
            return WildVariety_EvolveForLevel(pick, level);
    }
    return species;
}

// DexNav can search for every Pokemon of Gen 1-9, in its main form and its regional forms
bool32 WildVariety_IsSearchable(u16 species)
{
    return species > SPECIES_NONE && species < NUM_SPECIES && IsWildForm(species)
        && SpeciesToNationalPokedexNum(species) != 0;
}

// Fills `species` with every Pokemon DexNav can search for, in National Dex order. HnS gives
// regional forms their own National Dex numbers, after Pecharunt's.
u32 WildVariety_GetSearchableSpecies(u16 *species, u32 max)
{
    u32 j, count = 0;
    u16 entry;

    for (entry = SPECIES_NONE + 1; entry < NUM_SPECIES && count < max; entry++)
    {
        u32 dexNum;

        if (!WildVariety_IsSearchable(entry))
            continue;
        // Insertion sort; species constants are almost in National Dex order already
        dexNum = SpeciesToNationalPokedexNum(entry);
        for (j = count; j > 0 && SpeciesToNationalPokedexNum(species[j - 1]) > dexNum; j--)
            species[j] = species[j - 1];
        species[j] = entry;
        count++;
    }
    return count;
}
