#ifndef GUARD_RAISE_TO_CAP_H
#define GUARD_RAISE_TO_CAP_H

// Crystal Imperium: the PC's RAISE TO LV. CAP (src/raise_to_cap.c, DECISIONS.md D63)
u32 GetRaiseToCapLevel(void);
bool32 CanUseRaiseToCap(void);
bool32 CanRaisePartyMonToLevel(struct Pokemon *mon, u32 level);
bool32 CanRaiseBoxMonToLevel(struct BoxPokemon *boxMon, u32 level);
void RaisePartyMonToLevel(struct Pokemon *mon, u32 level);
void RaiseBoxMonToLevel(struct BoxPokemon *boxMon, u32 level);
u32 CountMonsToRaise(u32 level);
u32 RaisePartyToLevel(u32 level);
u32 RaiseBoxToLevel(u32 boxId, u32 level);

#endif // GUARD_RAISE_TO_CAP_H
