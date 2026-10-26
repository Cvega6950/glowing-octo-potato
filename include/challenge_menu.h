#ifndef GUARD_CHALLENGE_MENU_H
#define GUARD_CHALLENGE_MENU_H

#include "main.h"

struct ScriptContext;

void CB2_InitChallengeMenu(void);
void ChallengeMenu_OpenForNewGame(MainCallback returnCallback);
bool32 ChallengeMenu_WereNewGameSettingsChosen(void);
void Script_OpenChallengeMenu(struct ScriptContext *ctx);

#endif // GUARD_CHALLENGE_MENU_H
