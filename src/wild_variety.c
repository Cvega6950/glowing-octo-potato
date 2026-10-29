// Crystal Imperium: Wild Variety.
// Every Gen 1-9 Pokemon can be found on the routes. Each area's grass and water get a set of extra
// Pokemon from the variety pool: up to six in the grass and three on the water, as many as fit in
// the DexNav row next to the area's own Pokemon (those of every time of day, D42), evolved as far
// as the area's highest level allows. The set is the area's own: it stays the same (since 0.14.1;
// it changed every day before). A share of wild encounters (the WILD VARIETY option) is one of
// them, and DexNav lists them with the area's own Pokemon, so what turns up in the wild is what
// DexNav shows. The pool holds every base form (no pre-evolution), regional base forms included, but
// not battle-only forms or cosmetic form duplicates; Legendary, Mythical, Ultra Beast and
// Paradox Pokemon join it after the player becomes Champion. Besides that, DexNav can search
// for any Pokemon at all, in any evolution stage, on any route with wild encounters.
#include "global.h"
#include "battle_pike.h"
#include "battle_pyramid.h"
#include "bug_contest.h"
#include "event_data.h"
#include "pokemon.h"
#include "random.h"
#include "randomizer.h"
#include "rtc.h"
#include "wild_variety.h"
#include "constants/battle_pyramid.h"
#include "constants/flags.h"

#define VARIETY_POOL_SIZE 600 // holds 446 Pokemon and 121 legends (dexnav_wild_match checks the counts)
#define VARIETY_POOL_MAGIC 0xC1A5
#define LAND_VARIETY_COUNT 6
#define WATER_VARIETY_COUNT 3
#define LEGEND_CHANCE 25 // percent of the areas' sets with a Legend in them, after becoming Champion
#define POOL_PICK_TRIES 200

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

static u16 EvolveForLevel(u16 species, u8 level, rng_value_t *rng)
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
        species = options[LocalRandom(rng) % count];
    }
    return species;
}

// The Bug-Catching Contest and the Battle Frontier keep their own Pokemon
static bool32 IsVarietyActive(void)
{
    return WildVariety_GetPercent() != 0 && !GetBugContestFlag() && !InBattlePike()
        && CurrentBattlePyramidLocation() == PYRAMID_LOCATION_NONE;
}

// DexNav lists one Pokemon per National Dex number
static bool32 IsOnList(const u16 *list, u32 count, u16 species)
{
    u32 i, dexNum = SpeciesToNationalPokedexNum(species);

    for (i = 0; i < count; i++)
    {
        if (SpeciesToNationalPokedexNum(list[i]) == dexNum)
            return TRUE;
    }
    return FALSE;
}

// Adds the Wild Variety Pokemon of the current map's land or water area to `list`, in the `free`
// slots left. The set only depends on the map, the area and the player (since 0.14.1 not on the
// day, D42: coming back to a route finds the same Pokemon).
static u32 AddVarietySet(enum WildPokemonArea area, u16 *list, u32 count, u32 free, u8 level)
{
    u32 i, tries, size = area == WILD_AREA_LAND ? LAND_VARIETY_COUNT : WATER_VARIETY_COUNT;
    bool32 legend;
    rng_value_t rng = LocalRandomSeed(((u32)gSaveBlock1Ptr->location.mapGroup << 24
                                     | (u32)gSaveBlock1Ptr->location.mapNum << 16 | area << 8)
                                     ^ READ_OTID_FROM_SAVE);

    BuildPoolIfNeeded();
    legend = LocalRandom(&rng) % 100 < LEGEND_CHANCE && FlagGet(FLAG_SYS_GAME_CLEAR) && sPoolCount > sLegendStart;
    if (size > free)
        size = free;
    for (i = 0; i < size; i++)
    {
        // The last one is the Legend, if there is one
        bool32 pickLegend = legend && i == size - 1;
        u32 first = pickLegend ? sLegendStart : 0;
        u32 poolCount = pickLegend ? sPoolCount - sLegendStart : sLegendStart;

        if (poolCount == 0)
            break;
        for (tries = 0; tries < POOL_PICK_TRIES; tries++)
        {
            u16 pick = sPool[first + LocalRandom(&rng) % poolCount];

            // Surfing and fishing turn up Water-type Pokemon
            if (area != WILD_AREA_LAND && !IsSpeciesOfType(pick, TYPE_WATER))
                continue;
            pick = EvolveForLevel(pick, level, &rng);
            if (!IsOnList(list, count, pick))
            {
                list[count++] = pick;
                break;
            }
        }
    }
    return count;
}

// The current map's land or water Pokemon, as DexNav lists them and wild encounters turn them
// up: the area's own Pokemon of every time of day (D42; as the randomizer turns them out when it
// is map-based), a mass outbreak's Pokemon in the grass, then the area's Wild Variety Pokemon.
// Fishing uses the water list. `list` needs room for DexNav's row: LAND_WILD_COUNT or
// WATER_WILD_COUNT entries. Returns the number of entries; *varietyStart is the index of the
// first Wild Variety one.
u32 WildVariety_GetAreaList(enum WildPokemonArea area, u16 *list, u32 *varietyStart)
{
    u32 headerId = GetCurrentMapWildMonHeaderId();
    const struct WildPokemonInfo *infos[TIMES_OF_DAY_COUNT];
    u32 i, t, tables, rowSize, count = 0;
    u8 maxLevel = 1;
    bool32 encounters = FALSE;

    *varietyStart = 0;
    if (area == WILD_AREA_FISHING)
        area = WILD_AREA_WATER;
    if (headerId == HEADER_NONE || (area != WILD_AREA_LAND && area != WILD_AREA_WATER))
        return 0;

    rowSize = area == WILD_AREA_LAND ? LAND_WILD_COUNT : WATER_WILD_COUNT;
    tables = GetWildMonsInfos(headerId, area, infos, NULL);
    for (t = 0; t < tables; t++)
    {
        const struct WildPokemonInfo *info = infos[t];

        if (info->encounterRate == 0)
            continue;
        encounters = TRUE;
        for (i = 0; i < rowSize; i++)
        {
            u16 species = info->wildPokemon[i].species;

            if (species == SPECIES_NONE)
                continue;
        #if RANDOMIZER_AVAILABLE == TRUE
            // Without map seeding, or in chaos mode, every encounter is a new random Pokemon
            if (gSaveBlock3Ptr->challengeSettings.tx_Random_MapBased && !gSaveBlock3Ptr->challengeSettings.tx_Random_Chaos)
                species = RandomizeWildEncounter(species, gSaveBlock1Ptr->location.mapNum, gSaveBlock1Ptr->location.mapGroup, area, i);
        #endif
            if (count < rowSize && !IsOnList(list, count, species))
                list[count++] = species;
            if (info->wildPokemon[i].maxLevel > maxLevel)
                maxLevel = info->wildPokemon[i].maxLevel;
        }
    }
    if (!encounters)
        return 0;

    if (area == WILD_AREA_LAND && gSaveBlock1Ptr->outbreakPokemonSpecies != SPECIES_NONE
     && gSaveBlock1Ptr->location.mapNum == gSaveBlock1Ptr->outbreakLocationMapNum
     && gSaveBlock1Ptr->location.mapGroup == gSaveBlock1Ptr->outbreakLocationMapGroup
     && count < rowSize && !IsOnList(list, count, gSaveBlock1Ptr->outbreakPokemonSpecies))
        list[count++] = gSaveBlock1Ptr->outbreakPokemonSpecies;

    *varietyStart = count;
    if (IsVarietyActive())
        count = AddVarietySet(area, list, count, rowSize - count, maxLevel);
    return count;
}

u16 WildVariety_TryReplaceSpecies(u16 species, enum WildPokemonArea area)
{
    u16 list[LAND_WILD_COUNT];
    u32 start, count, slot;

    if (area == WILD_AREA_FISHING)
        area = WILD_AREA_WATER;
    if ((area != WILD_AREA_LAND && area != WILD_AREA_WATER) || !IsVarietyActive())
        return species;
    if (Random() % 100 >= WildVariety_GetPercent())
        return species;
    // Each Pokemon of a full set turns up as often; a set cut short by a full DexNav row
    // turns up less often in all
    slot = Random() % (area == WILD_AREA_LAND ? LAND_VARIETY_COUNT : WATER_VARIETY_COUNT);
    count = WildVariety_GetAreaList(area, list, &start);
    if (start + slot >= count)
        return species;
    return list[start + slot];
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
