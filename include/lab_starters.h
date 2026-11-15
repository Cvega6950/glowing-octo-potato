#ifndef GUARD_LAB_STARTERS_H
#define GUARD_LAB_STARTERS_H

struct ScriptContext;

// Crystal Imperium: PROF. ELM's three Poke Balls and the generation they come from (src/lab_starters.c, D61)
u16 GetLabBallSpecies(u32 ball);
void GetLabStarterSpecies(struct ScriptContext *ctx);
void StarterGeneration_CanChoose(struct ScriptContext *ctx);
void StarterGeneration_GetMenuRow(struct ScriptContext *ctx);
void StarterGeneration_Set(struct ScriptContext *ctx);
void StarterGeneration_BufferBallSpecies(struct ScriptContext *ctx);

#endif // GUARD_LAB_STARTERS_H
