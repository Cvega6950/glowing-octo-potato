#include "error_handling.h"

#include <nitro.h>
#include <string.h>

#include "comm_manager.h"
#include "error_message_reset.h"

#ifdef LOGGING_ENABLED
#include "debug.h"
#endif

void ErrorHandling_AssertFail(void);

#ifdef LOGGING_ENABLED

// Platinum Imperium debug builds (make debug): a failed GF_ASSERT logs the caller through the
// emulator print port and hangs, so silent overflows show up in tests (ENGINE_NOTES 1.6 rule 6).
// The release build keeps the vanilla behavior below.

void ErrorHandling_AssertFailFrom(u32 caller);

void ErrorHandling_AssertFailFrom(u32 caller)
{
    EmulatorLog("GF_ASSERT failed, called from %08X", caller);
    OS_DisableInterrupts();

    for (;;) {
        // Hang here so a test (or a debugger) sees the failure where it happened.
    }
}

// clang-format off
#include <nitro/code32.h>
asm void ErrorHandling_AssertFail(void)
{
    // r0 = the return address, i.e. the instruction after the failed assertion's call.
    mov r0, lr
    ldr r1, = ErrorHandling_AssertFailFrom
    bx r1
}
#include <nitro/codereset.h>
// clang-format on

#else

void ErrorHandling_AssertFail(void)
{
    if (CommManager_IsInitialized() && (OS_GetProcMode() != OS_PROCMODE_IRQ)) {
        ErrorMessageReset_PrintErrorAndReset();
    }
}

#endif
