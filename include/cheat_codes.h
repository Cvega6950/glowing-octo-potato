#ifndef GUARD_CHEAT_CODES_H
#define GUARD_CHEAT_CODES_H

struct ScriptContext;

void CheatCode_Find(struct ScriptContext *ctx);
void CheatCode_MarkAllCaught(struct ScriptContext *ctx);
void CheatCode_ToggleEasyCatch(struct ScriptContext *ctx);
void CheatCode_GiveMegaStones(struct ScriptContext *ctx);
void CheatCode_SetMaxMoney(struct ScriptContext *ctx);
void CheatCode_MakeRoamersShiny(struct ScriptContext *ctx);
void CheatCode_SetMonoType(struct ScriptContext *ctx);
u16 CheatCode_GetMonoStarter(u16 species, u32 ball);

#endif // GUARD_CHEAT_CODES_H
