#ifndef POKEPLATINUM_SCRCMD_IMPERIUM_H
#define POKEPLATINUM_SCRCMD_IMPERIUM_H

#include "field_script_context.h"

// Platinum Imperium script commands (appended to include/data/scripts/scrcmd.h). Stage 2 phase 0
// reserves their IDs and argument layouts; the handlers are stubs until a track fills them in.
// See docs/platinum_imperium/API.md.

// FindPartySlotForFieldMove destVar, move
BOOL ScrCmd_FindPartySlotForFieldMove(ScriptContext *ctx);
// ImperiumToggleSetting flagID, destVar
BOOL ScrCmd_ImperiumToggleSetting(ScriptContext *ctx);
// ImperiumOpenQuickMenu destVar
BOOL ScrCmd_ImperiumOpenQuickMenu(ScriptContext *ctx);
// ImperiumGiveCarePackage destVar
BOOL ScrCmd_ImperiumGiveCarePackage(ScriptContext *ctx);

#endif // POKEPLATINUM_SCRCMD_IMPERIUM_H
