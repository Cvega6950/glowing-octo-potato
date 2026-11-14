"""Debug assert hook (ENGINE_NOTES 1.6 rule 6): in a debug build (make debug, LOGGING_ENABLED) a
failed GF_ASSERT prints "GF_ASSERT failed, called from <address>" through the emulator's print port
and hangs. The test provokes one with a test-mailbox warp to map header 0xFFFF, which fails the
bounds check in MapHeader_IDBoundsCheck. On a release build it only checks that the hook is absent.

    make debug BUILD=build_debug
    ROM=build_debug/pokeplatinum.us.nds python3 tools/dsrun/run_tests.py debug_assert
"""
import ctypes
import os
import tempfile

from playtest import MB_WARP


def run(t):
    if not t.has_sym("ErrorHandling_AssertFailFrom"):
        t.result("release build: the assert hook is compiled out (run on a debug build to test it)")
        return
    t.new_game()
    libc = ctypes.CDLL(None)
    log = tempfile.TemporaryFile()
    libc.fflush(None)
    saved = os.dup(1)
    os.dup2(log.fileno(), 1)  # melonDS prints the game's no$gba-style messages on stdout
    try:
        t.mailbox_cmd(MB_WARP, 0xFFFF, 0, 0, timeout=600, quiet=True)
        frames = t.mb("fieldFrames")
        t.ds.run(120)
        hung = t.mb("fieldFrames") == frames
        libc.fflush(None)
    finally:
        os.dup2(saved, 1)
        os.close(saved)
    log.seek(0)
    text = log.read().decode(errors="replace")
    lines = [l for l in text.splitlines() if "GF_ASSERT" in l]
    t.shot("hung")
    t.check(lines, f"no GF_ASSERT message was printed (captured {len(text)} bytes)")
    t.check(hung, "the game kept running after the failed assertion")
    t.result(f"logged and hung: {lines[0].strip()}")
