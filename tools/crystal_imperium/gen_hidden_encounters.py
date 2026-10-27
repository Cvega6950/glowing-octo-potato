#!/usr/bin/env python3
"""Generate DexNav hidden Pokemon tables (hidden_mons) for every Heart & Soul map with wild
Pokemon, and write them into src/data/wild_encounters.json.

The hidden slots are filled with the evolution families that have no other source in the game
(the families validate.py reports), matched to the area: Water and Ice families on water,
Rock/Ground/Steel/Ghost/Dark/Dragon families in caves, the rest in grass. Families are dealt out
round-robin, so every family appears in several areas; a map's tables for every time of day get
the same ones (since 0.14.1, D42: DexNav's list is the same at every hour). Levels are the range
of the area's own Pokemon.

  python3 tools/crystal_imperium/gen_hidden_encounters.py          # rewrite hidden_mons
  python3 tools/crystal_imperium/gen_hidden_encounters.py --list   # print the assignment
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate  # noqa: E402

ROOT = validate.ROOT
JSON_PATH = os.path.join(ROOT, "src", "data", "wild_encounters.json")
HIDDEN_FIELD = {"type": "hidden_mons", "encounter_rates": [50, 35, 15]}
HIDDEN_SLOTS = len(HIDDEN_FIELD["encounter_rates"])
LEGEND_FLAGS = ("isRestrictedLegendary", "isSubLegendary", "isMythical", "isUltraBeast", "isParadox")
CAVE_WORDS = ("CAVE", "TUNNEL", "MT_", "MOUNT", "RUINS", "WELL", "ICE_PATH", "VICTORY_ROAD", "SEAFOAM",
              "DIGLETT", "WHIRL", "DRAGONS_DEN", "TOHJO", "SILVER", "TOWER", "ROCK", "GROTTO", "CLIFF")
CAVE_TYPES = {"TYPE_ROCK", "TYPE_GROUND", "TYPE_STEEL", "TYPE_GHOST", "TYPE_DARK", "TYPE_DRAGON"}
WATER_TYPES = {"TYPE_WATER", "TYPE_ICE"}


def expand_species_macro(text, body):
    """Species defined as NAME_SPECIES_INFO(args): the macro's definition with the arguments put
    in, so its .types and flags can be read (e.g. ARCEUS_SPECIES_INFO(TYPE_NORMAL, ...))."""
    call = re.match(r"\s*(\w+)\((.*?)\)\s*,", body, re.S)
    if not call:
        return body
    definition = re.search(rf"#define {call.group(1)}\(([^)]*)\)((?:.*\\\n)*.*)", text)
    if not definition:
        return body
    params = [p.strip() for p in definition.group(1).split(",")]
    args = [a.strip() for a in call.group(2).split(",")]
    expanded = definition.group(2)
    for param, arg in zip(params, args):
        expanded = re.sub(rf"\b{re.escape(param)}\b", arg, expanded)
    return expanded


def species_details():
    """SPECIES_X -> {"types": [...], "legend": bool} from the species info headers."""
    details = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "src/data/pokemon/species_info/*.h"))):
        text = open(path, encoding="utf-8").read()
        parts = re.split(r"(?m)^\s*\[(SPECIES_\w+)\]\s*=", text)
        for name, body in zip(parts[1::2], parts[2::2]):
            body = expand_species_macro(text, body)
            m = re.search(r"\.types\s*=\s*MON_TYPES\(([^)]*)\)", body)
            types = [t.strip() for t in m.group(1).split(",")] if m else []
            legend = any(re.search(rf"\.{flag}\s*=\s*TRUE", body) for flag in LEGEND_FLAGS)
            details[name] = {"types": types, "legend": legend}
    return details


def habitat_of_family(types):
    if WATER_TYPES & set(types):
        return "water"
    if CAVE_TYPES & set(types):
        return "cave"
    return "grass"


def habitat_of_map(mapname, entry):
    if "land_mons" not in entry:
        return "water"
    return "cave" if any(word in mapname for word in CAVE_WORDS) else "grass"


def level_range(table):
    return (min(m["min_level"] for m in table["mons"]), max(m["max_level"] for m in table["mons"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="print the assignment without writing")
    args = ap.parse_args()

    species = validate.parse_species()
    details = species_details()
    fam = validate.families(species)
    # Sources other than hidden slots: wild tables and scripts
    with open(JSON_PATH, encoding="utf-8") as f:
        original_text = f.read()
    data = json.loads(original_text)
    group = next(g for g in data["wild_encounter_groups"] if g["label"] == "gWildMonHeaders")
    for entry in group["encounters"]:
        entry.pop("hidden_mons", None)
    found = validate.parse_encounters(data)
    obtainable = {fam.get(s, s) for s in found}
    roots = sorted({fam[s] for s in validate.national_species() if s in fam})
    missing = [r for r in roots if r not in obtainable and not details.get(r, {}).get("legend")]

    families_by_habitat = {"grass": [], "cave": [], "water": []}
    for root in missing:
        families_by_habitat[habitat_of_family(details.get(root, {}).get("types", []))].append(root)

    # A map's tables for every time of day, in the JSON's order
    tables_by_map = {}
    for entry in group["encounters"]:
        mapname = entry.get("map", "")
        if not mapname.endswith("_HNS") or not ("land_mons" in entry or "water_mons" in entry):
            continue
        tables_by_map.setdefault(mapname, []).append(entry)
    maps_by_habitat = {"grass": {}, "cave": {}, "water": {}}
    for mapname, entries in tables_by_map.items():
        land = next((e for e in entries if "land_mons" in e), entries[0])
        maps_by_habitat[habitat_of_map(mapname, land)][mapname] = entries
    # A habitat without maps hands its families to grass
    for habitat in ("cave", "water"):
        if not maps_by_habitat[habitat]:
            families_by_habitat["grass"] += families_by_habitat[habitat]
            families_by_habitat[habitat] = []

    # One set per map, the same in its tables for every time of day: DexNav's list is the same at
    # every hour (DECISIONS.md D42), and its hidden row has room for three
    # Water first: the few water-only maps have fewer slots than the Water and Ice families, so
    # those that don't fit go to the caves (Ice) and the grass (the rest)
    assignment = []
    for habitat in ("water", "cave", "grass"):
        maps = maps_by_habitat[habitat]
        pool = families_by_habitat[habitat] or families_by_habitat["grass"]
        if not pool or not maps:
            continue
        for root in pool[HIDDEN_SLOTS * len(maps):] if habitat != "grass" else []:
            to = "cave" if "TYPE_ICE" in details.get(root, {}).get("types", []) and habitat == "water" else "grass"
            families_by_habitat[to].append(root)
        cursor = 0
        key = "water_mons" if habitat == "water" else "land_mons"
        for mapname, entries in maps.items():
            ranges = [level_range(e[key]) for e in entries if key in e]
            low, high = min(r[0] for r in ranges), max(r[1] for r in ranges)
            picks = []
            for _ in range(HIDDEN_SLOTS):
                picks.append(pool[cursor % len(pool)])
                cursor += 1
            for entry in entries:
                entry["hidden_mons"] = {"encounter_rate": 1 if habitat == "water" else 0,
                                        "mons": [{"min_level": low, "max_level": high, "species": p} for p in picks]}
                assignment.append((entry["base_label"], habitat, picks))

    if args.list:
        for label, habitat, mons in assignment:
            print(f"{label:48} {habitat:6} {', '.join(mons)}")
    covered = {m for _, _, mons in assignment for m in mons}
    print(f"families with no other source: {len(missing)}; in hidden slots: {len(covered & set(missing))}; "
          f"maps given hidden Pokemon: {len(assignment)}", file=sys.stderr)
    if args.list:
        return 0

    fields = group["fields"]
    if not any(f["type"] == "hidden_mons" for f in fields):
        fields.append(HIDDEN_FIELD)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
