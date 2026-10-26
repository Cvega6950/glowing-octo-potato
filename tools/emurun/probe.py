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
               '#include "dexnav.h"', '#include "money.h"', '#include "constants/opponents.h"', '#include "window.h"', '#include "battle_setup.h"']
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


def bitfield(struct, field):
    """(byte offset, mask) of a bitfield of `struct` that lies within one byte: compiles a constant
    whose field is all ones and reads its bytes back from the assembly."""
    key = ("bitfield", struct, field)
    if key not in _cache:
        src = ['#include "global.h"', '#include "main.h"', f"const struct {struct} kBitfieldProbe = {{ .{field} = -1 }};"]
        path = os.path.join(ROOT, "src", f"zz_emurun_probe_{os.getpid()}.c")
        with open(path, "w") as f:
            f.write("\n".join(src) + "\n")
        try:
            cc1 = subprocess.run(["arm-none-eabi-gcc", "-print-prog-name=cc1"], check=True,
                                 capture_output=True, text=True).stdout.strip()
            cmd = ("arm-none-eabi-cpp -iquote include -Wno-trigraphs -DMODERN=1 -DTESTING=0 -DPOKEMON_HNS -std=gnu17 "
                   f"{os.path.relpath(path, ROOT)} | tools/preproc/preproc -i {os.path.relpath(path, ROOT)} charmap.txt | "
                   f"{cc1} -quiet -w -mthumb -O2 -mabi=apcs-gnu -march=armv4t -std=gnu17 -o - -")
            res = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError("probe compile failed:\n" + res.stderr[-2000:])
        finally:
            os.remove(path)
        data = bytearray()
        sizes = {".byte": 1, ".short": 2, ".2byte": 2, ".hword": 2, ".word": 4, ".4byte": 4}
        body = res.stdout.split("kBitfieldProbe:", 1)[1]
        for line in body.splitlines()[1:]:
            parts = line.split()
            if not parts or parts[0].endswith(":") or parts[0] in (".size", ".section", ".global", ".align"):
                break
            if parts[0] == ".space":
                data += bytes(int(parts[1]))
            elif parts[0] in sizes:
                data += (int(parts[1], 0) & ((1 << (8 * sizes[parts[0]])) - 1)).to_bytes(sizes[parts[0]], "little")
        nonzero = [i for i, b in enumerate(data) if b]
        if len(nonzero) != 1:
            raise RuntimeError(f"{struct}.{field} is not within one byte: {data.hex()}")
        _cache[key] = (nonzero[0], data[nonzero[0]])
    return _cache[key]
