#!/usr/bin/env python3
"""Run a Crystal Imperium emulator play test.

Usage: tools/emurun/emu.py TEST.emu [--rom pokehns.gba] [--elf pokehns.elf] [--out DIR] [--save FILE]

A .emu file is an emurun script (see emurun.c) with two additions:
  {gSymbol} or {gSymbol+N}   replaced by the symbol's address from the ELF
  !macro(args)               expanded by the helpers below (Python expression)
"""
import argparse
import probe
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


START_MENU = {"POKEDEX": 0, "POKEMON": 1, "BAG": 2, "POKENAV": 3, "PLAYER": 4, "SAVE": 5, "OPTION": 6,
              "EXIT": 7, "DEXNAV": 14}


def start_menu(entry):
    """Open the start menu and choose an entry by name, wherever the cursor was left."""
    return ["press START", "wait 40",
            f"menuselect {{sStartMenuCursorPos}} {{sCurrentStartMenuActions}} {{sNumStartMenuActions}} {START_MENU[entry]}",
            "wait 120"]


def battle_style_set():
    """START > OPTION > BATTLE STYLE = SET, so trainer battles never ask "Will you switch?"."""
    out = start_menu("OPTION")
    out += ["press DOWN", "wait 10", "press DOWN", "wait 10", "press RIGHT", "wait 10", "shot options_set.png"]
    out += ["press B", "wait 120", "press B", "wait 60"]
    return out


def open_debug():
    return ["hold R 10", "hold R+START 6", "hold R 6", "wait 40"]


def give_mon(species, level):
    """Debug menu > Give X > Pokemon (Basic)."""
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(species) + ["press A", "wait 30"] + number(level) + ["press A", "wait 60", "mash B 60"]
    return out


def give_item(item_id, quantity=1):
    """Debug menu > Give X > Give item XYZ: item id, then quantity."""
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press A", "wait 30"]
    out += number(item_id) + ["press A", "wait 30"] + number(quantity) + ["press A", "wait 60", "mash B 60"]
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


def open_bag_at(pocket, index):
    """START > BAG, then move to `pocket` (constant name) and its index-th item, using the bag's
    own position data (it remembers the last pocket and cursor)."""
    v = probe.resolve({"pocket_off": "offsetof(struct BagPosition, pocket)",
                       "cursor_off": "offsetof(struct BagPosition, cursorPosition)",
                       pocket: pocket})
    cursor = f"{{gBagPosition+{v['cursor_off'] + 2 * v[pocket]}}}"
    return start_menu("BAG") + [f"seek8 {{gBagPosition+{v['pocket_off']}}} {v[pocket]} RIGHT LEFT", "wait 20",
                                f"seek16 {cursor} {index} DOWN UP", "wait 10"]


def use_key_item(index):
    """Use the index-th Key Item from the bag (USE is the first context-menu entry), then close the bag."""
    out = open_bag_at("POCKET_KEY_ITEMS", index)
    out += ["press A", "wait 20", "press A", "wait 120", "mash B 200", "wait 60"]
    return out


def expect_flag(flag, want, label=None):
    """Check an event flag by constant name, e.g. expect_flag("FLAG_INFINITE_REPEL_ON", 1)."""
    v = probe.resolve({"flags": "offsetof(struct SaveBlock1, flags)", flag: flag})
    return [f"expectflag {{gSaveBlock1Ptr}} {v['flags']} {v[flag]} {want} {label or flag.lower()}"]


def walkto(x, y, order="xy", soft=False):
    """Walk to map coordinates (x, y), reading the player's position from the save block.
    soft=True: being stopped (e.g. by a wild battle) is not a test failure."""
    return [f"walkto {{gSaveBlock1Ptr}} {x} {y} {order}" + (" soft" if soft else "")]


def pace(x1, x2, y, laps, soft=False):
    """Walk back and forth between (x1, y) and (x2, y) `laps` times, e.g. through tall grass.
    Without soft=True, being interrupted (e.g. by a wild battle) is a test failure."""
    out = []
    for _ in range(laps):
        out += walkto(x1, y, soft=soft) + walkto(x2, y, soft=soft)
    return out


def battle_trainer(trainer_id):
    """Debug menu > Trainers > Trainer 1 = id > Try Battle."""
    out = open_debug() + ["press DOWN"] * 6 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(trainer_id, initial=0) + ["press A", "wait 30"]
    out += ["press DOWN"] * 5 + ["press A"]  # the cursor returns to the top after entry
    return out


def turn(*moves, shots=None, decline_switch=False):
    """One battle turn per argument: 0-3 picks that move slot. Battle text auto-advances.

    decline_switch=True presses B first, which answers a "Will you switch?" prompt with No
    and is harmless on the action menu (the cursor is reset right after)."""
    out = []
    for i, m in enumerate(moves):
        if decline_switch:
            out += ["press B", "wait 30"]
        out += ["press UP", "press LEFT", "press A", "wait 30", "press UP", "press LEFT"]
        if m & 1:
            out.append("press RIGHT")
        if m & 2:
            out.append("press DOWN")
        out += ["press A", "wait 700"]
        if shots:
            out.append(f"shot {shots}_{i:02d}.png")
    return out


def autobattle(moves, max_frames=60000):
    """Play the current battle to the end. moves: per party slot, the move slot (0-3) to use,
    e.g. "2,3,1,2"; add 'm' to Mega Evolve first ("2m"). Forced switches pick the first healthy
    Pokemon. Prints the outcome, turn count and remaining party HP."""
    keys = ["main={gMain}", "outcome={gBattleOutcome}", "ctrl={gBattlerControllerFuncs}",
            "act={HandleInputChooseAction@battle_controller_player}", "mov={HandleInputChooseMove}",
            "actcur={gActionSelectionCursor}", "movcur={gMoveSelectionCursor}",
            "partyidx={gBattlerPartyIndexes}", "party={gPlayerParty}", "count={gPlayerPartyCount}",
            "mons={gBattleMons}", "pmenu={gPartyMenu}",
            "pmenucb2={CB2_UpdatePartyMenu}", "battlecb2={BattleMainCB2}"]
    return [f"autobattle {moves} {max_frames} " + " ".join(keys)]


def sample_battle(trainer_id, moves, runs=5, min_wins=1, max_wins=None, state="team.ss"):
    """Fight trainer_id `runs` times from the saved team state, starting each battle a few frames
    later so the battle RNG differs, and require between min_wins and max_wins wins.
    Save the team first with `savestate team.ss` (paths are relative to the output directory)."""
    out = []
    for k in range(runs):
        out += [f"loadstate {state}", f"wait {1 + 37 * k}"] + battle_trainer(trainer_id) + autobattle(moves)
        out += [f"tally wins_vs_{trainer_id} {{gBattleOutcome}} 1"]
    out.append(f"expecttally wins_vs_{trainer_id} {min_wins} {runs if max_wins is None else max_wins}")
    return out


def send_out(slot):
    """Answer the 'Will you switch?' prompt / forced switch: party slot 1-5, then confirm."""
    return ["press A", "wait 150"] + ["press DOWN", "wait 10"] * slot + ["press A", "wait 30", "press A", "wait 500"]


def symbols(elf):
    """name -> address. Static functions that exist in several objects are also available as
    name@object (e.g. HandleInputChooseAction@battle_controller_player), resolved via the .map."""
    out = subprocess.run(["arm-none-eabi-nm", elf], check=True, capture_output=True, text=True).stdout
    table, dupes = {}, {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3:
            addr = int(parts[0], 16)
            table[parts[2]] = addr
            dupes.setdefault(parts[2], []).append(addr)
    mapfile = os.path.splitext(elf)[0] + ".map"
    if os.path.exists(mapfile):
        for line in open(mapfile):
            m = re.match(r"\s*\.text\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+\S*?([\w]+)\.o$", line)
            if not m:
                continue
            lo, size, obj = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
            for name, addrs in dupes.items():
                for a in addrs:
                    if lo <= a < lo + size:
                        table[f"{name}@{obj}"] = a
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
        if line.startswith("!"):
            lines += [re.sub(r"\{([\w@]+)(?:\+(\d+))?\}", sub, l) for l in eval(line[1:])]
        else:
            lines.append(re.sub(r"\{([\w@]+)(?:\+(\d+))?\}", sub, line))
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
