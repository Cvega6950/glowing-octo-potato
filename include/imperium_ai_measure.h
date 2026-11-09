#ifndef GUARD_IMPERIUM_AI_MEASURE_H
#define GUARD_IMPERIUM_AI_MEASURE_H

// Crystal Imperium AI measurement builds (tools/emurun/ai_measure.py, DECISIONS.md D60). With
// IMPERIUM_AI_MEASURE at 1, a play test can hand the player's side to a fixed AI by setting
// gImperiumAiVsAi before a trainer battle. Trainer AI changes are then compared over many battles
// against a player that switches, sets up and picks its moves. A release keeps it at 0, and none
// of this is compiled.
#define IMPERIUM_AI_MEASURE 0

// The player's AI in a measured battle: Emerald Imperium's boss set. It doesn't change with the
// trainer AI being measured.
#define IMPERIUM_AI_MEASURE_PLAYER_FLAGS (AI_FLAG_CHECK_BAD_MOVE | AI_FLAG_TRY_TO_FAINT | AI_FLAG_CHECK_VIABILITY \
                                        | AI_FLAG_OMNISCIENT | AI_FLAG_SMART_SWITCHING | AI_FLAG_SMART_MON_CHOICES)

#if IMPERIUM_AI_MEASURE
extern u8 gImperiumAiVsAi;
#endif

#endif // GUARD_IMPERIUM_AI_MEASURE_H
