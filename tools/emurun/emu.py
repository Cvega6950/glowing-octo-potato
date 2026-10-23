#!/usr/bin/env python3
"""Run a Crystal Imperium emulator play test.

Usage: tools/emurun/emu.py TEST.emu [--rom pokehns.gba] [--elf pokehns.elf] [--out DIR] [--save FILE]

A .emu file is an emurun script (see emurun.c) with two additions:
  {gSymbol} or {gSymbol+N}   replaced by the symbol's address from the ELF
  !macro(args)               expanded by the helpers below (Python expression)
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def number(target, initial=1):
    """Debug-menu numeric entry: UP adds 10^digit, RIGHT selects the next higher digit."""
    out = []
    digits = str(target - initial)[::-1]
    for i, d in enumerate(digits):
        out += ["press UP 2"] * int(d)
        if i < len(digits) - 1:
            out.append("press RIGHT 2")
    return out


def new_game():
    """Power-on to the bedroom in New Bark Town with default settings (Minimal Grinding ON)."""
    out = ["wait 1300", "press START", "wait 60", "press A", "wait 500", "mash A 900", "mash A 900", "mash A 700"]
    out += ["press R", "wait 20"] * 5 + ["wait 10", "press UP", "wait 30", "press A", "wait 120", "press A", "wait 120"]
    out += ["mash A 1500", "mash A 1200", "wait 300"]
    return out


def open_debug():
    return ["hold R 10", "hold R+START 6", "hold R 6", "wait 40"]


def give_mon(species, level):
    """Debug menu > Give X > Pokemon (Basic)."""
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(species) + ["press A", "wait 30"] + number(level) + ["press A", "wait 60", "mash B 60"]
    return out


def cheat_start():
    """Debug menu > Utilities > Cheat start (sets all eight badge flags, among others)."""
    return open_debug() + ["press A", "wait 30"] + ["press DOWN"] * 6 + ["press A", "wait 300", "mash B 120"]


def max_money():
    """Debug menu > Give X > Max Money."""
    return open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30"] + ["press DOWN"] * 5 + ["press A", "wait 60", "mash B 60"]


def warp(group, num, warp_id=0):
    """Debug menu > Utilities > Warp to map warp: map group, map number, warp id."""
    out = open_debug() + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(group, initial=0) + ["press A", "wait 20"]
    out += number(num, initial=0) + ["press A", "wait 20"]
    out += number(warp_id, initial=0) + ["press A", "wait 400"]
    return out


def walk(*steps):
    """walk("UP", 4, "RIGHT", 2): one tile is 16 frames at walking speed; hold B is not used."""
    out = []
    for d, n in zip(steps[::2], steps[1::2]):
        out += [f"hold {d} {16 * n}", "wait 10"]
    return out


def battle_trainer(trainer_id):
    """Debug menu > Trainers > Trainer 1 = id > Try Battle."""
    out = open_debug() + ["press DOWN"] * 6 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(trainer_id, initial=0) + ["press A", "wait 30"]
    out += ["press DOWN"] * 5 + ["press A"]  # the cursor returns to the top after entry
    return out


def turn(*moves, shots=None):
    """One battle turn per argument: 0-3 picks that move slot. Battle text auto-advances."""
    out = []
    for i, m in enumerate(moves):
        out += ["press UP", "press LEFT", "press A", "wait 30", "press UP", "press LEFT"]
        if m & 1:
            out.append("press RIGHT")
        if m & 2:
            out.append("press DOWN")
        out += ["press A", "wait 700"]
        if shots:
            out.append(f"shot {shots}_{i:02d}.png")
    return out


def send_out(slot):
    """Answer the 'Will you switch?' prompt / forced switch: party slot 1-5, then confirm."""
    return ["press A", "wait 150"] + ["press DOWN", "wait 10"] * slot + ["press A", "wait 30", "press A", "wait 500"]


def symbols(elf):
    out = subprocess.run(["arm-none-eabi-nm", elf], check=True, capture_output=True, text=True).stdout
    table = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3:
            table[parts[2]] = int(parts[0], 16)
    return table


def expand(path, syms):
    lines = []
    for raw in open(path):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        def sub(m):
            name, off = m.group(1), int(m.group(2) or 0)
            if name not in syms:
                sys.exit(f"{path}: unknown symbol {name}")
            return hex(syms[name] + off)
        line = re.sub(r"\{(\w+)(?:\+(\d+))?\}", sub, line)
        if line.startswith("!"):
            lines += eval(line[1:])
        else:
            lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("test")
    ap.add_argument("--rom", default="pokehns.gba")
    ap.add_argument("--elf", default="pokehns.elf")
    ap.add_argument("--out", default="build/emurun")
    ap.add_argument("--save", help="attach a fresh save file (removed before the run) at this path")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    script = os.path.join(args.out, os.path.basename(args.test) + ".txt")
    with open(script, "w") as f:
        f.write("\n".join(expand(args.test, symbols(args.elf))) + "\n")
    emurun = os.path.join(HERE, "emurun")
    if not os.path.exists(emurun):
        subprocess.run(["make", "-C", HERE], check=True)
    # Screenshot paths in tests are relative to the output directory
    cmd = [emurun, os.path.abspath(args.rom), os.path.abspath(script)]
    if args.save:
        if os.path.exists(args.save):
            os.remove(args.save)
        cmd.append(os.path.abspath(args.save))
    res = subprocess.run(cmd, cwd=args.out)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
