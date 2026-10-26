#ifndef GUARD_WILD_VARIETY_H
#define GUARD_WILD_VARIETY_H

// Crystal Imperium: Wild Variety. Every route also turns up a daily set of other Gen 1-9
// Pokemon, which DexNav lists with the area's own (see src/wild_variety.c), and DexNav can
// search for any Pokemon.

#include "wild_encounter.h"

u32 WildVariety_GetPercent(void);
u32 WildVariety_GetAreaList(enum WildPokemonArea area, u16 *list, u32 *varietyStart);
u16 WildVariety_TryReplaceSpecies(u16 species, enum WildPokemonArea area);
bool32 WildVariety_IsSearchable(u16 species);
u32 WildVariety_GetSearchableSpecies(u16 *species, u32 max);

#endif // GUARD_WILD_VARIETY_H
