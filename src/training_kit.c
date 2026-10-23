// Crystal Imperium: Training Kit key item (Emerald Imperium-style instant nature/ability changes).
// The script side is data/scripts/training_kit.inc; these specials read the party slot chosen with
// ChoosePartyMon from VAR_0x8004.
#include "global.h"
#include "event_data.h"
#include "party_menu.h"
#include "pokemon.h"
#include "string_util.h"
#include "constants/abilities.h"

static struct Pokemon *GetChosenMon(void)
{
    return &gPlayerParty[gSpecialVar_0x8004];
}

// VAR_0x8005 = nature to set. Buffers the nickname in STR_VAR_1 and the nature in STR_VAR_2.
void TrainingKit_SetNature(void)
{
    struct Pokemon *mon = GetChosenMon();
    u32 nature = gSpecialVar_0x8005;

    if (nature >= NUM_NATURES)
        return;
    SetMonData(mon, MON_DATA_HIDDEN_NATURE, &nature);
    CalculateMonStats(mon);
    GetMonNickname(mon, gStringVar1);
    StringCopy(gStringVar2, gNaturesInfo[nature].name);
}

// Moves to the species' next distinct ability (slot 1 -> 2 -> Hidden -> 1).
// VAR_RESULT = FALSE if the species has only one ability. Buffers the nickname in STR_VAR_1
// and the new ability in STR_VAR_2.
void TrainingKit_CycleAbility(void)
{
    struct Pokemon *mon = GetChosenMon();
    u16 species = GetMonData(mon, MON_DATA_SPECIES);
    u32 current = GetMonData(mon, MON_DATA_ABILITY_NUM);
    enum Ability currentAbility = GetMonAbility(mon);

    GetMonNickname(mon, gStringVar1);
    gSpecialVar_Result = FALSE;
    for (u32 step = 1; step < NUM_ABILITY_SLOTS; step++)
    {
        u32 next = (current + step) % NUM_ABILITY_SLOTS;
        enum Ability ability = GetAbilityBySpecies(species, next);
        if (ability != ABILITY_NONE && ability != currentAbility && GetSpeciesAbility(species, next) != ABILITY_NONE)
        {
            SetMonData(mon, MON_DATA_ABILITY_NUM, &next);
            StringCopy(gStringVar2, gAbilitiesInfo[ability].name);
            gSpecialVar_Result = TRUE;
            return;
        }
    }
    StringCopy(gStringVar2, gAbilitiesInfo[currentAbility].name);
}
