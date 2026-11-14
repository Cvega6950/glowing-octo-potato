#!/usr/bin/env python3
"""One play test in its own process: playtest.py <name> runs tests/playtests/<name>.py.

A test module defines run(t). t is a Test:
    t.ds              the DS (dsrun.DS), booted from power-on with the ROM
    t.shot(label)     screenshot to build/playtests/<name>/<n>_<label>.png
    t.check(cond, message)
    t.result(text)    one line for the summary
    t.sym(name)       address of a symbol in the ARM9 binary or its overlays (from the build's .map)
    t.const(name)     value of a generated constant (FLAG_*, VAR_*, ITEM_*, SPECIES_*, TRAINER_*, MAP_HEADER_*, ...)

Game-state helpers (Platinum Imperium test mailbox, src/imperium_test.c; docs/platinum_imperium/API.md):
    t.new_game()                  power-on to the first frame the player can move in a new game
    t.wait_field(timeout)         run until the field is free (no script or task running)
    t.mailbox_cmd(cmd, *args)     run a mailbox command (MB_* below) and wait for it to finish
    t.var(name) / t.flag(name)    read a saved var or flag (name or number); t.set_var / t.set_flag
    t.party_count(), t.party_species(slot), t.party_level(slot), t.bag_quantity(item)
    t.mb(field)                   read a mailbox field by name (see MAILBOX_FIELDS)
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from dsrun import DS  # noqa: E402


class TestFailure(Exception):
    pass


_SYMS = None
_CONSTS = None

# Test mailbox commands and statuses (include/imperium_test.h).
MB_RUN_SCRIPT, MB_WARP, MB_START_TRAINER_BATTLE, MB_GIVE_ITEM, MB_GIVE_MON, MB_PING = 1, 2, 3, 4, 5, 6
MB_IDLE, MB_BUSY, MB_DONE, MB_ERROR = 0, 1, 2, 3
IMPERIUM_TEST_MAGIC = 0x494D5054

# name: (offset, size) in struct ImperiumTestMailbox (include/imperium_test.h, layout version 1).
MAILBOX_FIELDS = {
    "magic": (0x00, 4), "layoutVersion": (0x04, 2), "numVars": (0x06, 2),
    "saveData": (0x08, 4), "varsFlags": (0x0C, 4), "party": (0x10, 4), "bag": (0x14, 4),
    "trainerInfo": (0x18, 4), "fieldSystem": (0x1C, 4), "options": (0x20, 4), "playerData": (0x24, 4),
    "fieldFrames": (0x28, 4), "cmd": (0x2C, 2), "args": (0x2E, 2), "status": (0x36, 2), "result": (0x38, 2),
    "sizeofPokemon": (0x3A, 2), "battleCount": (0x3C, 4), "lastBattleType": (0x40, 4),
    "lastBattleStatusMask": (0x44, 4), "lastBattleLevelCap": (0x48, 1), "levelCap": (0x49, 1),
    "mapHeaderID": (0x4A, 2), "playerX": (0x4C, 2), "playerZ": (0x4E, 2), "pendingCmd": (0x50, 2),
    "saveBlockInfo": (0x54, 4), "mainArenaFree": (0x58, 4), "appHeapFree": (0x5C, 4), "systemHeapFree": (0x60, 4),
}

# Struct layouts the helpers read (checked against the source; see API.md).
TRAINER_INFO_BADGE_MASK = 0x1A  # TrainerInfo: name[8] (16 bytes), id, money, gender, language, badgeMask
PARTY_COUNT = 0x04              # Party: int capacity, int currentCount, Pokemon pokemon[6]
PARTY_MONS = 0x08
BAG_SLOTS = 165 + 50 + 100 + 12 + 40 + 64 + 15 + 30  # every pocket, BagItem {u16 item, u16 quantity}
VARS_START = 0x4000
_BLOCK_ORDERS = ["ABCD", "ABDC", "ACBD", "ACDB", "ADBC", "ADCB", "BACD", "BADC", "BCAD", "BCDA", "BDAC", "BDCA",
                 "CABD", "CADB", "CBAD", "CBDA", "CDAB", "CDBA", "DABC", "DACB", "DBAC", "DBCA", "DCAB", "DCBA"]


def constants():
    """Generated constants, NAME -> value, from build/generated/*.h (metang's #define lines)."""
    global _CONSTS
    if _CONSTS is None:
        _CONSTS = {}
        gen = os.path.join(ROOT, "build", "generated")
        for fn in sorted(os.listdir(gen)):
            if fn.endswith(".h"):
                with open(os.path.join(gen, fn), errors="replace") as fh:
                    for m in re.finditer(r"^#define (\w+)\s+(-?(?:0x[0-9A-Fa-f]+|\d+))\s*$", fh.read(), re.M):
                        _CONSTS.setdefault(m.group(1), int(m.group(2), 0))
    return _CONSTS


_RI_STATES = None


def rowan_intro_states():
    """enum RowanIntroState, name -> value, parsed from the Rowan intro's source."""
    global _RI_STATES
    if _RI_STATES is None:
        src = open(os.path.join(ROOT, "src", "applications", "rowan_intro", "rowan_intro_app.c")).read()
        body = re.search(r"enum RowanIntroState \{(.*?)\};", src, re.S).group(1)
        _RI_STATES, n = {}, 0
        for line in body.splitlines():
            m = re.match(r"\s*(RI_STATE_\w+)\s*(?:=\s*(\d+))?\s*,", line)
            if m:
                n = int(m.group(2)) if m.group(2) else n
                _RI_STATES[m.group(1)] = n
                n += 1
    return _RI_STATES


def _decrypt(words, seed):
    out = []
    for w in words:
        seed = (seed * 0x41C64E6D + 0x6073) & 0xFFFFFFFF
        out.append(w ^ (seed >> 16))
    return out


def xmap_path():
    """The linker map of the ROM under test: $XMAP, else main.nef.xMAP next to $ROM (so a ROM from
    another build directory, such as a debug build, gets its own symbols), else build/main.nef.xMAP."""
    if os.environ.get("XMAP"):
        return os.environ["XMAP"]
    rom = os.environ.get("ROM")
    if rom and os.path.exists(os.path.join(os.path.dirname(os.path.abspath(rom)), "main.nef.xMAP")):
        return os.path.join(os.path.dirname(os.path.abspath(rom)), "main.nef.xMAP")
    return os.path.join(ROOT, "build", "main.nef.xMAP")


def symbols():
    """Symbol addresses from the build's main.nef.xMAP (the Metrowerks linker map), name -> address.
    Overlays share address ranges; the first definition of a name wins."""
    global _SYMS
    if _SYMS is None:
        _SYMS = {}
        with open(xmap_path(), errors="replace") as fh:
            for m in re.finditer(r"^\s+([0-9A-F]{8}) [0-9A-F]{8} \.\w+\s+(\w+)\t", fh.read(), re.M):
                _SYMS.setdefault(m.group(2), int(m.group(1), 16))
    return _SYMS


class Test:
    def __init__(self, name, rom, save=None):
        self.name = name
        self.out = os.path.join(ROOT, "build", "playtests", name)
        os.makedirs(self.out, exist_ok=True)
        for f in os.listdir(self.out):
            if f.endswith(".png"):
                os.remove(os.path.join(self.out, f))
        self.ds = DS(rom, save=save)
        self.n = 0
        self.summary = ""

    def shot(self, label):
        self.n += 1
        path = os.path.join(self.out, f"{self.n:02d}_{label}.png")
        self.ds.screenshot(path)
        return path

    def check(self, cond, message):
        if not cond:
            self.shot("failure")
            raise TestFailure(message)

    def result(self, text):
        self.summary = text

    def has_sym(self, name):
        return name in symbols()

    def sym(self, name):
        s = symbols()
        if name not in s:
            raise TestFailure(f"symbol {name} not found in {xmap_path()}")
        return s[name]

    def const(self, name):
        if isinstance(name, int):
            return name
        c = constants()
        if name not in c:
            raise TestFailure(f"constant {name} not found in build/generated/*.h")
        return c[name]

    # --- waiting ---
    def wait_until(self, cond, timeout=3000, step=4, what="condition"):
        """Run `step` frames at a time until cond() is true; fail after `timeout` frames."""
        start = self.ds.frame
        while not cond():
            if self.ds.frame - start > timeout:
                self.check(False, f"timed out after {timeout} frames waiting for {what}")
            self.ds.run(step)
        return self.ds.frame - start

    # --- new game fixture ---
    def _rowan_intro(self):
        """(state, appState) of the Rowan intro app if it is the running application, else None.
        Reads main.c's sApplication.currApplication (ApplicationManager: template.init at 0,
        procState at 20, data at 28) and RowanIntro.state (offset 12)."""
        app = self.ds.read32(self.sym("sApplication") + 4)
        if not 0x02000000 <= app < 0x02400000:
            return None
        if (self.ds.read32(app) & ~1) != (self.sym("RowanIntro_Init") & ~1):
            return None
        data = self.ds.read32(app + 28)
        if not 0x02000000 <= data < 0x02400000:
            return None
        return self.ds.read32(data + 12), self.ds.read32(app + 20)

    def new_game(self, timeout=60000):
        """From power-on to the first frame the player can move in a new game, as fast as the
        game allows: A through the title, NEW GAME and the dialogue; "no info needed"; the Poke
        Ball touch; boy; the default names (START then A on an empty keyboard); then A through
        the opening scene until the test mailbox answers a ping. Waits on game state, not on
        frame counts. Returns the number of frames it took."""
        ri = rowan_intro_states()
        start = self.ds.frame
        while True:
            if self.ds.frame - start > timeout:
                self.check(False, f"new_game: not in control after {timeout} frames")
            if self.in_field():
                if self.mailbox_cmd(MB_PING, timeout=12, quiet=True) == MB_DONE:
                    return self.ds.frame - start
                self.ds.press("A", frames=2, after=6)
                continue
            r = self._rowan_intro()
            if r is None:
                self.ds.press("A", frames=2, after=6)
                continue
            state, app_state = r
            if app_state == 4:  # RI_APP_STATE_CHANGE_APP: the naming screen is running
                self.ds.press("START", frames=2, after=10)
                self.ds.press("A", frames=2, after=10)
            elif state == ri["RI_STATE_INFO_CHOICE_BOX"]:
                self.ds.run(10)
                self.ds.press("DOWN", frames=2, after=6)
                self.ds.press("DOWN", frames=2, after=6)
                self.ds.press("A", frames=2, after=10)
            elif state == ri["RI_STATE_CONTROL_INFO_WAIT_INPUT"]:
                self.ds.touch(120, 76, frames=4, after=10)
            elif state == ri["RI_STATE_PKBL_WAIT_INPUT"]:
                self.ds.touch(128, 100, frames=4, after=10)
            else:
                self.ds.press("A", frames=2, after=6)

    # --- test mailbox ---
    def mbox(self):
        return self.sym("gImperiumTest")

    def mb(self, field, index=0):
        off, size = MAILBOX_FIELDS[field]
        a = self.mbox() + off + index * size
        return {1: self.ds.read8, 2: self.ds.read16, 4: self.ds.read32}[size](a)

    def in_field(self):
        return self.mb("magic") == IMPERIUM_TEST_MAGIC and self.mb("fieldSystem") != 0

    def wait_field(self, timeout=6000, what="the field to be free"):
        """Run until the player can move with no script or task running."""
        start = self.ds.frame
        while True:
            if self.in_field() and self.mailbox_cmd(MB_PING, timeout=16, quiet=True) == MB_DONE:
                return self.ds.frame - start
            if self.ds.frame - start > timeout:
                self.check(False, f"timed out after {timeout} frames waiting for {what}")
            self.ds.run(8)

    def mailbox_cmd(self, cmd, *args, timeout=6000, quiet=False, mash=None, on_frame=None):
        """Write args, then cmd; run until the game sets status DONE or ERROR and return the status.
        Without quiet, a timeout fails the test; with quiet, it returns None. mash="A" presses that
        key every few frames while waiting (to get through a battle or dialogue); on_frame(t) is
        called after every frame (to sample state while the command runs)."""
        box = self.mbox()
        args = list(args) + [0] * (4 - len(args))
        for i, v in enumerate(args[:4]):
            self.ds.write16(box + 0x2E + 2 * i, v & 0xFFFF)
        self.ds.write16(box + 0x38, 0)
        self.ds.write16(box + 0x36, MB_IDLE)
        self.ds.write16(box + 0x2C, cmd)
        start = self.ds.frame
        while True:
            if mash and (self.ds.frame - start) % 16 == 8:
                self.ds.hold(mash)
            elif mash and (self.ds.frame - start) % 16 == 12:
                self.ds.release()
            self.ds.run(1)
            if on_frame:
                on_frame(self)
            st = self.ds.read16(box + 0x36)
            if st in (MB_DONE, MB_ERROR) and self.ds.read16(box + 0x2C) == 0 and self.ds.read16(box + 0x50) == 0:
                if mash:
                    self.ds.release()
                return st
            if self.ds.frame - start >= timeout:
                if quiet:
                    self.ds.write16(box + 0x2C, 0)
                    return None
                self.check(False, f"mailbox command {cmd}{tuple(args)} timed out (status {st})")

    # --- saved state through the mailbox pointers ---
    def var_addr(self, name):
        vid = self.const(name)
        return self.mb("varsFlags") + 2 * (vid - VARS_START)

    def var(self, name):
        return self.ds.read16(self.var_addr(name))

    def set_var(self, name, value):
        self.ds.write16(self.var_addr(name), value)

    def flag_addr(self, name):
        fid = self.const(name)
        return self.mb("varsFlags") + 2 * self.mb("numVars") + fid // 8, 1 << (fid % 8)

    def flag(self, name):
        a, bit = self.flag_addr(name)
        return bool(self.ds.read8(a) & bit)

    def set_flag(self, name, on=True):
        a, bit = self.flag_addr(name)
        v = self.ds.read8(a)
        self.ds.write8(a, (v | bit) if on else (v & ~bit & 0xFF))

    def badge_mask(self):
        return self.ds.read8(self.mb("trainerInfo") + TRAINER_INFO_BADGE_MASK)

    def set_badge_mask(self, mask):
        self.ds.write8(self.mb("trainerInfo") + TRAINER_INFO_BADGE_MASK, mask & 0xFF)

    def party_count(self):
        return self.ds.read32(self.mb("party") + PARTY_COUNT)

    def _mon(self, slot):
        size = self.mb("sizeofPokemon")
        raw = self.ds.ram(self.mb("party") + PARTY_MONS + slot * size, size)
        return raw

    def party_level(self, slot):
        raw = self._mon(slot)
        pid = int.from_bytes(raw[0:4], "little")
        words = [int.from_bytes(raw[0x88 + i:0x8A + i], "little") for i in range(0, 6, 2)]
        party = _decrypt(words, pid)  # PartyPokemon, encrypted with the personality as the seed
        return party[2] & 0xFF  # PartyPokemon.level at 0x8C

    def party_species(self, slot):
        raw = self._mon(slot)
        pid = int.from_bytes(raw[0:4], "little")
        checksum = int.from_bytes(raw[6:8], "little")
        words = _decrypt([int.from_bytes(raw[8 + i:10 + i], "little") for i in range(0, 128, 2)], checksum)
        block_a = _BLOCK_ORDERS[((pid & 0x3E000) >> 13) % 24].index("A")
        return words[block_a * 16]  # PokemonDataBlockA.species

    def bag_quantity(self, item):
        item = self.const(item)
        raw = self.ds.ram(self.mb("bag"), BAG_SLOTS * 4)
        total = 0
        for i in range(BAG_SLOTS):
            if int.from_bytes(raw[4 * i:4 * i + 2], "little") == item:
                total += int.from_bytes(raw[4 * i + 2:4 * i + 4], "little")
        return total

    def running_shoes(self):
        return self.ds.read16(self.mb("playerData") + 2) == 1  # PlayerData {u16 cyclingGear, u16 runningShoes}

    def options_word(self):
        return self.ds.read16(self.mb("options"))


def main(name):
    rom = os.environ.get("ROM") or os.path.join(ROOT, "build", "pokeplatinum.us.nds")
    path = os.path.join(ROOT, "tests", "playtests", name + ".py")
    spec = importlib.util.spec_from_file_location("playtest_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    t = Test(name, rom, save=getattr(mod, "SAVE", None))
    try:
        mod.run(t)
    except TestFailure as e:
        print(f"RESULT FAIL: {e} (frame {t.ds.frame})")
        return 1
    print(f"RESULT {t.summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
