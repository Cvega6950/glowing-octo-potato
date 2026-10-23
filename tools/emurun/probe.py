"""Resolve game constants and struct offsets by compiling a tiny C file with the game's own headers
and build flags, so play tests never hard-code numbers that change when the source changes."""
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_cache = {}


def resolve(exprs):
    """exprs: {name: C expression}. Returns {name: int}."""
    todo = {k: v for k, v in exprs.items() if k not in _cache}
    if todo:
        src = ['#include "global.h"', '#include "constants/flags.h"', '#include "constants/vars.h"',
               '#include "constants/items.h"', '#include "constants/species.h"', '#include "item_menu.h"']
        src += [f"const int kProbe_{k} = ({v});" for k, v in todo.items()]
        path = os.path.join(ROOT, "src", "zz_emurun_probe.c")
        with open(path, "w") as f:
            f.write("\n".join(src) + "\n")
        try:
            cc1 = subprocess.run(["arm-none-eabi-gcc", "-print-prog-name=cc1"], check=True,
                                 capture_output=True, text=True).stdout.strip()
            cmd = ("arm-none-eabi-cpp -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DPOKEMON_HNS -std=gnu17 "
                   "src/zz_emurun_probe.c | tools/preproc/preproc -i src/zz_emurun_probe.c charmap.txt | "
                   f"{cc1} -quiet -mthumb -O2 -mabi=apcs-gnu -march=armv4t -std=gnu17 -o - -")
            res = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError("probe compile failed:\n" + res.stderr[-2000:])
            asm = res.stdout
        finally:
            os.remove(path)
        for name, val in re.findall(r"kProbe_(\w+):\s*\n\s*\.word\s+(-?\d+)", asm):
            _cache[name] = int(val)
    return {k: _cache[k] for k in exprs}
