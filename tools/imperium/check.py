#!/usr/bin/env python3
"""Platinum Imperium T0 checks and build measurements (ENGINE_NOTES 4.2, tier T0).

    tools/imperium/check.py            print the measurements of the last build
    tools/imperium/check.py --check    run the T0 checks; exit status 1 if any fails
    tools/imperium/check.py --json     the measurements as JSON
    tools/imperium/check.py --xmap other/main.nef.xMAP [--rom other.nds]   measure another build

Checks:
  1. Shared overlay slot: trainer_ai and battle_sub_menus load where battle_anim loads, and must
     not reach past its end (the start of the resident battle overlay). Read from
     build/main.nef.xMAP, the Metrowerks linker map.
  2. generated/vars_flags.txt: no duplicate names; every *_IMPERIUM_* flag and var has its own
     ID, outside the banned and special ranges (ENGINE_NOTES V3).
  3. generated/items.txt: the vanilla list (ITEM_NONE .. ITEM_SECRET_KEY = 467) is unchanged, new
     items come after it and before MAX_ITEMS, MAX_ITEMS is last and equals the item count (and the
     generated header, when built), and every new item has res/items/data/<stem>.json.
  4. Append-only tables keep their vanilla prefix: text banks (724), the script command table
     (ends at SCRCMD_BUFFERFLOORNUMBER) and the battle command table (ends at BTLCMD_END).
"""
import json
import os
import re
import struct
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
XMAP = os.path.join(ROOT, "build", "main.nef.xMAP")
ROM = os.path.join(ROOT, "build", "pokeplatinum.us.nds")

SLOT_OWNER = "battle_anim"
SLOT_SHARERS = ["trainer_ai", "battle_sub_menus"]

NUM_FLAGS = 2912
BANNED_FLAGS = {0x0000, 0x04E4, 0x0990} | set(range(0x03BF, 0x03DA)) | set(range(0x0974, 0x0977))
VANILLA_TEXT_BANKS = 724
VANILLA_LAST_ITEM = ("ITEM_SECRET_KEY", 467)


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# --- linker map ---------------------------------------------------------------------------------

def parse_xmap(path=None):
    """Linker-command symbols (#> lines): {name: value}."""
    path = path or XMAP
    syms = {}
    for m in re.finditer(r"^#>([0-9A-F]{8})\s+(\S+) \(linker command file\)", read(path), re.M):
        syms[m.group(2)] = int(m.group(1), 16)
    return syms


def overlays(syms):
    """{name: {start, end, bss_end, size, bss_size}} for every overlay in the map."""
    out = {}
    for key, value in syms.items():
        m = re.match(r"SDK_OVERLAY\.(\w+)\.(START|END|SIZE|BSS_END|BSS_SIZE)$", key)
        if m:
            out.setdefault(m.group(1), {})[m.group(2).lower()] = value
    return {k: v for k, v in out.items() if {"start", "end", "bss_end"} <= set(v)}


def measurements():
    syms = parse_xmap()
    ovs = overlays(syms)
    tallest = max(ovs.items(), key=lambda kv: kv[1]["bss_end"])
    m = {
        "main_text_data_end": syms.get("SDK_STATIC_END"),
        "main_bss_end": syms.get("SDK_STATIC_BSS_END"),
        "main_size": syms.get("SDK_STATIC_SIZE"),
        "arena_lo": syms.get("SDK_MAIN_ARENA_LO"),
        "arena_ex_start": syms.get("SDK_SECTION_ARENA_EX_START"),
        "tallest_overlay": tallest[0],
        "tallest_overlay_end": tallest[1]["bss_end"],
        "overlays": {name: ovs[name] for name in [SLOT_OWNER, "battle"] + SLOT_SHARERS if name in ovs},
        "overlay_count": len(ovs),
    }
    if os.path.exists(ROM):
        with open(ROM, "rb") as fh:
            header = fh.read(0x90)
        m["rom_used_size"] = struct.unpack_from("<I", header, 0x80)[0]
        m["rom_file_size"] = os.path.getsize(ROM)
    return m


def check_overlay_slot(errors):
    ovs = overlays(parse_xmap())
    owner = ovs.get(SLOT_OWNER)
    battle = ovs.get("battle")
    if owner is None or battle is None:
        errors.append("overlay map: battle_anim or battle missing from build/main.nef.xMAP")
        return
    limit = battle["start"]
    for name in SLOT_SHARERS:
        ov = ovs.get(name)
        if ov is None:
            errors.append(f"overlay map: {name} missing")
            continue
        if ov["start"] != owner["start"]:
            errors.append(f"overlay map: {name} starts at {ov['start']:#x}, not in battle_anim's slot ({owner['start']:#x})")
        if ov["bss_end"] > limit:
            errors.append(f"overlay map: {name} ends at {ov['bss_end']:#x}, past the start of battle ({limit:#x}) "
                          f"by {ov['bss_end'] - limit} bytes")
        if ov["bss_end"] - ov["start"] > owner["bss_end"] - owner["start"]:
            errors.append(f"overlay map: {name} ({ov['bss_end'] - ov['start']} bytes) is larger than battle_anim "
                          f"({owner['bss_end'] - owner['start']} bytes)")


# --- vars and flags -----------------------------------------------------------------------------

def enum_values(path):
    """metang enum semantics: each line is NAME or NAME = EXPR (an int or an earlier NAME); the next
    implicit value is the previous value + 1. Returns [(name, value, is_alias)] in file order."""
    values, out, nxt = {}, [], 0
    for lineno, raw in enumerate(read(path).splitlines(), 1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        if "=" in line:
            name, expr = (p.strip() for p in line.split("=", 1))
            if re.fullmatch(r"-?(0x[0-9A-Fa-f]+|\d+)", expr):
                value = int(expr, 0)
            elif expr in values:
                value = values[expr]
            else:
                raise ValueError(f"{path}:{lineno}: unknown value {expr}")
            alias = expr in values
        else:
            name, value, alias = line, nxt, False
        out.append((name, value, alias, lineno))
        values[name] = value
        nxt = value + 1
    return out


def check_vars_flags(errors):
    path = os.path.join(ROOT, "generated", "vars_flags.txt")
    entries = enum_values(path)
    names = {}
    for name, value, alias, lineno in entries:
        if name in names:
            errors.append(f"vars_flags.txt:{lineno}: duplicate name {name} (first at line {names[name]})")
        names[name] = lineno
    v = {name: value for name, value, _, _ in entries}
    by_value = {}
    for name, value, alias, _ in entries:
        by_value.setdefault(value, []).append(name)

    flag_ranges = [
        ("map-local flags", 1, v["MAP_LOCAL_FLAGS_END"]),
        ("hidden-item flags", v["HIDDEN_ITEM_FLAGS_START"], v["HIDDEN_ITEM_FLAGS_END"]),
        ("trainer-defeated flags", v["TRAINER_DEFEATED_FLAGS_START"], v["TRAINER_DEFEATED_FLAGS_END"]),
        ("daily flags", v["DAILY_FLAGS_START"], v["DAILY_FLAGS_END"]),
    ]
    var_ranges = [
        ("map-local vars", v["MAP_LOCAL_VARS_START"], v["MAP_LOCAL_VARS_END"]),
        ("object graphics vars", v["VAR_OBJ_GFX_ID_0"], v["VAR_OBJ_GFX_ID_F"]),
    ]
    count = 0
    for name, value, alias, lineno in entries:
        if "_IMPERIUM_" not in name:
            continue
        count += 1
        others = [n for n in by_value[value] if n != name]
        if alias or others:
            errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#x} shares its ID with {others}")
        if name.startswith("FLAG_"):
            if value in BANNED_FLAGS:
                errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#06x} is in a banned range (ENGINE_NOTES V3)")
            if not 0 < value < NUM_FLAGS:
                errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#06x} is not a saved flag (< {NUM_FLAGS})")
            for label, lo, hi in flag_ranges:
                if lo <= value <= hi:
                    errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#06x} is in the {label}")
        elif name.startswith("VAR_"):
            if not v["VARS_START"] <= value < v["VARS_END"]:
                errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#06x} is not a saved var")
            for label, lo, hi in var_ranges:
                if lo <= value <= hi:
                    errors.append(f"vars_flags.txt:{lineno}: {name} = {value:#06x} is in the {label}")
        else:
            errors.append(f"vars_flags.txt:{lineno}: {name} is neither a FLAG_ nor a VAR_")
    if count == 0:
        errors.append("vars_flags.txt: no *_IMPERIUM_* entries")
    header = os.path.join(ROOT, "build", "generated", "vars_flags.h")
    if os.path.exists(header):
        built = dict((m.group(1), int(m.group(2)))
                     for m in re.finditer(r"^#define (\w+)\s+(\d+)\s*$", read(header), re.M))
        for name, value, _, lineno in entries:
            if "_IMPERIUM_" in name and name in built and built[name] != value:
                errors.append(f"vars_flags.txt:{lineno}: {name} computed {value}, built header says {built[name]} "
                              "(rebuild, or this script's enum rules are wrong)")
    return count


# --- items --------------------------------------------------------------------------------------

def check_items(errors):
    path = os.path.join(ROOT, "generated", "items.txt")
    entries = enum_values(path)
    names = [e[0] for e in entries]
    if names[-1] != "MAX_ITEMS":
        errors.append("items.txt: MAX_ITEMS is not the last entry")
        return []
    if len(set(names)) != len(names):
        errors.append("items.txt: duplicate item names")
    last, last_id = VANILLA_LAST_ITEM
    if last not in names or names.index(last) != last_id or names[0] != "ITEM_NONE":
        errors.append(f"items.txt: the vanilla list changed ({last} must stay at {last_id}, ITEM_NONE at 0)")
        return []
    for name, value, alias, lineno in entries:
        if alias or value != names.index(name):
            errors.append(f"items.txt:{lineno}: {name} has an explicit or aliased value; append plain names only")
    max_items = dict((e[0], e[1]) for e in entries)["MAX_ITEMS"]
    if max_items != len(names) - 1:
        errors.append(f"items.txt: MAX_ITEMS = {max_items}, but there are {len(names) - 1} items")
    new = names[last_id + 1:-1]
    for name in new:
        stem = name[len("ITEM_"):].lower()
        data = os.path.join(ROOT, "res", "items", "data", stem + ".json")
        if not os.path.exists(data):
            errors.append(f"items.txt: {name} has no res/items/data/{stem}.json")
            continue
        item = json.loads(read(data))
        if item.get("fieldPocket") == "POCKET_KEY_ITEMS" and not item.get("preventToss"):
            errors.append(f"{stem}.json: key items must set preventToss")
    header = os.path.join(ROOT, "build", "generated", "items.h")
    if os.path.exists(header):
        m = re.search(r"^#define MAX_ITEMS\s+(\d+)", read(header), re.M)
        if m and int(m.group(1)) != max_items:
            errors.append(f"items.txt: MAX_ITEMS {max_items} but the built header says {m.group(1)} (rebuild)")
    return new


# --- append-only tables -------------------------------------------------------------------------

def check_append_only(errors):
    banks = [l.strip() for l in read(os.path.join(ROOT, "generated", "text_banks.txt")).splitlines() if l.strip()]
    if len(banks) < VANILLA_TEXT_BANKS or banks[VANILLA_TEXT_BANKS - 1] != "TEXT_BANK_SPECIES_CATEGORY_JP":
        errors.append("text_banks.txt: the vanilla 724 banks changed (TEXT_BANK_SPECIES_CATEGORY_JP must stay at 723)")
    for bank in banks[VANILLA_TEXT_BANKS:]:
        stem = bank[len("TEXT_BANK_"):].lower()
        if not os.path.exists(os.path.join(ROOT, "res", "text", stem + ".json")):
            errors.append(f"text_banks.txt: {bank} has no res/text/{stem}.json")
    for table, last in (("scrcmd.h", "SCRCMD_BUFFERFLOORNUMBER"), ("btlcmd.h", "BTLCMD_END")):
        cmds = re.findall(r"^ScriptCommand\((\w+),", read(os.path.join(ROOT, "include", "data", "scripts", table)), re.M)
        if last not in cmds:
            errors.append(f"{table}: {last} is missing")
            continue
        added = cmds[cmds.index(last) + 1:]
        if len(set(cmds)) != len(cmds):
            errors.append(f"{table}: duplicate commands")
        if table == "btlcmd.h":
            inc = read(os.path.join(ROOT, "asm", "macros", "btlcmd.inc"))
            for cmd in added:
                if f".long {cmd}" not in inc:
                    errors.append(f"btlcmd.inc: no macro emits {cmd}")
        else:
            inc = read(os.path.join(ROOT, "asm", "macros", "scrcmd.inc"))
            for cmd in added:
                if f".short {cmd}" not in inc:
                    errors.append(f"scrcmd.inc: no macro emits {cmd}")
    return banks[VANILLA_TEXT_BANKS:]


def main(argv):
    global XMAP, ROM
    if "--xmap" in argv:  # measure another build: --xmap path/to/main.nef.xMAP [--rom path/to.nds]
        XMAP = argv[argv.index("--xmap") + 1]
        ROM = argv[argv.index("--rom") + 1] if "--rom" in argv else ROM
    if "--check" in argv:
        errors = []
        if os.path.exists(XMAP):
            check_overlay_slot(errors)
        else:
            errors.append("build/main.nef.xMAP not found: build first (make release)")
        n = check_vars_flags(errors)
        items = check_items(errors)
        banks = check_append_only(errors)
        for e in errors:
            print("FAIL", e)
        if errors:
            print(f"T0: {len(errors)} problem(s)")
            return 1
        m = measurements()
        ov = m["overlays"]
        room = ov["battle"]["start"] - max(ov[n]["bss_end"] for n in SLOT_SHARERS)
        print(f"T0: OK ({n} Imperium vars/flags, {len(items)} new items, {len(banks)} new text banks; "
              f"shared slot headroom {room} bytes; tallest overlay {m['tallest_overlay']} ends {m['tallest_overlay_end']:#x})")
        return 0
    m = measurements()
    if "--json" in argv:
        print(json.dumps(m, indent=2))
        return 0
    print(f"main: ends {m['main_text_data_end']:#x} (text+data {m['main_size']:#x} bytes), bss ends {m['main_bss_end']:#x}")
    print(f"arena: {m['arena_lo']:#x} .. {m['arena_ex_start']:#x} ({m['arena_ex_start'] - m['arena_lo']} bytes before heaps)")
    print(f"tallest overlay: {m['tallest_overlay']} ends {m['tallest_overlay_end']:#x}")
    for name, o in m["overlays"].items():
        print(f"  {name:18} {o['start']:#x}..{o['bss_end']:#x}  {o['bss_end'] - o['start']:7} bytes")
    if "rom_used_size" in m:
        print(f"ROM: {m['rom_used_size']} bytes used ({m['rom_used_size'] / 2**20:.2f} MiB) of a {m['rom_file_size'] // 2**20} MiB file")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
