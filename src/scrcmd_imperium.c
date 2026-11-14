#include "scrcmd_imperium.h"

#include <nitro.h>

#include "constants/pokemon.h"

#include "field_script_context.h"
#include "inlines.h"

// Stubs: each reads its arguments, so scripts that use the command already parse correctly, and
// stores the "nothing happened" result. Tracks B and G replace the bodies.

BOOL ScrCmd_FindPartySlotForFieldMove(ScriptContext *ctx)
{
    u16 *destVar = ScriptContext_GetVarPointer(ctx);
    u16 move = ScriptContext_GetVar(ctx);

    (void)move;
    *destVar = MAX_PARTY_SIZE;
    return FALSE;
}

BOOL ScrCmd_ImperiumToggleSetting(ScriptContext *ctx)
{
    u16 flagID = ScriptContext_GetVar(ctx);
    u16 *destVar = ScriptContext_GetVarPointer(ctx);

    (void)flagID;
    *destVar = FALSE;
    return FALSE;
}

BOOL ScrCmd_ImperiumOpenQuickMenu(ScriptContext *ctx)
{
    u16 *destVar = ScriptContext_GetVarPointer(ctx);

    *destVar = 0;
    return FALSE;
}

BOOL ScrCmd_ImperiumGiveCarePackage(ScriptContext *ctx)
{
    u16 *destVar = ScriptContext_GetVarPointer(ctx);

    *destVar = FALSE;
    return FALSE;
}
