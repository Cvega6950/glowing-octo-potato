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
void GetLabStarterSpecies(struct ScriptContext *ctx);

#endif // GUARD_CHEAT_CODES_H
