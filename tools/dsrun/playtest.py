#!/usr/bin/env python3
"""One play test in its own process: playtest.py <name> runs tests/playtests/<name>.py.

A test module defines run(t). t is a Test:
    t.ds              the DS (dsrun.DS), booted from power-on with the ROM
    t.shot(label)     screenshot to build/playtests/<name>/<n>_<label>.png
    t.check(cond, message)
    t.result(text)    one line for the summary
    t.sym(name)       address of a symbol in the ARM9 binary or its overlays (from the build's .map)
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


def symbols():
    """Symbol addresses from build/main.nef.xMAP (the Metrowerks linker map), name -> address.
    Overlays share address ranges; the first definition of a name wins."""
    global _SYMS
    if _SYMS is None:
        _SYMS = {}
        with open(os.path.join(ROOT, "build", "main.nef.xMAP"), errors="replace") as fh:
            for m in re.finditer(r"^\s+([0-9A-F]{8}) [0-9A-F]{8} \.\w+\s+(\w+)\t", fh.read(), re.M):
                _SYMS.setdefault(m.group(2), int(m.group(1), 16))
    return _SYMS


class Test:
    def __init__(self, name, rom, save=None):
        self.name = name
        self.out = os.path.join(ROOT, "build", "playtests", name)
        os.makedirs(self.out, exist_ok=True)
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

    def sym(self, name):
        s = symbols()
        if name not in s:
            raise TestFailure(f"symbol {name} not found in build/*.map")
        return s[name]


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
