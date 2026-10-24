#ifndef GUARD_WILD_VARIETY_H
#define GUARD_WILD_VARIETY_H

// Crystal Imperium: Wild Variety. Every route can also turn up any Gen 1-9 Pokemon (see
// src/wild_variety.c), and DexNav can search for any of them.

#include "wild_encounter.h"

u32 WildVariety_GetPercent(void);
u16 WildVariety_TryReplaceSpecies(u16 species, u8 level, enum WildPokemonArea area);
u16 WildVariety_EvolveForLevel(u16 species, u8 level);
bool32 WildVariety_IsSearchable(u16 species);
u32 WildVariety_GetSearchableSpecies(u16 *species, u32 max);

#endif // GUARD_WILD_VARIETY_H
