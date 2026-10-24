"""Resolve game constants and struct offsets by compiling a tiny C file with the game's own headers
and build flags, so play tests never hard-code numbers that change when the source changes."""
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_cache = {}


def resolve(exprs):
    """exprs: {name: C expression}. Returns {name: int}. Results are cached per expression."""
    todo = sorted({v for v in exprs.values() if v not in _cache})
    if todo:
        src = ['#include "global.h"', '#include "constants/flags.h"', '#include "constants/vars.h"',
               '#include "constants/items.h"', '#include "constants/species.h"', '#include "item_menu.h"', '#include "pokemon.h"', '#include "battle.h"',
               '#include "dexnav.h"', '#include "constants/opponents.h"']
        src += [f"const int kProbe_{i} = ({v});" for i, v in enumerate(todo)]
        # One file per process, so test runs in parallel don't overwrite each other's probe
        path = os.path.join(ROOT, "src", f"zz_emurun_probe_{os.getpid()}.c")
        with open(path, "w") as f:
            f.write("\n".join(src) + "\n")
        try:
            cc1 = subprocess.run(["arm-none-eabi-gcc", "-print-prog-name=cc1"], check=True,
                                 capture_output=True, text=True).stdout.strip()
            cmd = ("arm-none-eabi-cpp -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DPOKEMON_HNS -std=gnu17 "
                   f"{os.path.relpath(path, ROOT)} | tools/preproc/preproc -i {os.path.relpath(path, ROOT)} charmap.txt | "
                   f"{cc1} -quiet -mthumb -O2 -mabi=apcs-gnu -march=armv4t -std=gnu17 -o - -")
            res = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError("probe compile failed:\n" + res.stderr[-2000:])
            asm = res.stdout
        finally:
            os.remove(path)
        for i, val in re.findall(r"kProbe_(\d+):\s*\n\s*\.word\s+(-?\d+)", asm):
            _cache[todo[int(i)]] = int(val)
        # Zero-valued constants are emitted as ".space 4" rather than ".word 0"
        for i in re.findall(r"kProbe_(\d+):\s*\n\s*\.space\s+4", asm):
            _cache[todo[int(i)]] = 0
    return {k: _cache[v] for k, v in exprs.items()}
