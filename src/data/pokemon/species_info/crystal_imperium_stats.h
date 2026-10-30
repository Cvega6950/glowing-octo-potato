// Crystal Imperium's own base stats (DECISIONS.md D51), after Emerald Imperium's (imperium_stats.h).
// Included at the end of gSpeciesInfo (src/data/pokemon/species_info.h): each line replaces the base
// stats of one species. Written by hand.

// Pikachu, strong enough to use without evolving: 60 HP, 90 Attack, 60 Defense, 120 Speed, 90 Sp. Atk
// and 70 Sp. Def, 490 in all (35/55/40/90/50/50, 320, in the official games; Let's Go's Partner
// Pikachu has 430). Emerald Imperium's Raichu has 515; with a Light Ball, Pikachu hits harder. Its
// cosplay, cap, Partner and World forms are the same Pikachu.
#define CRYSTAL_IMPERIUM_PIKACHU_STATS(species)                                                         \
    [species].baseHP = 60, [species].baseAttack = 90, [species].baseDefense = 60,                        \
    [species].baseSpeed = 120, [species].baseSpAttack = 90, [species].baseSpDefense = 70,

    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU)
#if P_COSPLAY_PIKACHU_FORMS
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_COSPLAY)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_ROCK_STAR)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_BELLE)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_POP_STAR)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_PHD)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_LIBRE)
#endif //P_COSPLAY_PIKACHU_FORMS
#if P_CAP_PIKACHU_FORMS
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_ORIGINAL)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_HOENN)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_SINNOH)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_UNOVA)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_KALOS)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_ALOLA)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_PARTNER)
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_WORLD)
#endif //P_CAP_PIKACHU_FORMS
#if P_GIGANTAMAX_FORMS
    CRYSTAL_IMPERIUM_PIKACHU_STATS(SPECIES_PIKACHU_GMAX)
#endif //P_GIGANTAMAX_FORMS
#undef CRYSTAL_IMPERIUM_PIKACHU_STATS
