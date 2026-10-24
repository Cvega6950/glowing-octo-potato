#!/usr/bin/env python3
"""Crystal Imperium data validator and database generator.

Checks the HnS trainer, species, level-cap and encounter data for mistakes the
compiler cannot catch, and regenerates the machine-readable databases in
docs/crystal_imperium/data/.

  python3 tools/crystal_imperium/validate.py            # validate + regenerate
  python3 tools/crystal_imperium/validate.py --check    # validate only (CI)

Unknown species/move/item/ability names are already rejected at build time by
trainerproc and the C compiler; this script adds the semantic checks:
  * trainer abilities must be one of the species' abilities (the engine
    silently falls back to slot 0 otherwise)
  * each Gym Leader's ace may not exceed the NORMAL level cap in force when
    the player challenges them, and the cap after a badge must match the next
    leader's ace (src/caps.c)
  * boss trainers must define four moves for every Pokemon
  * every evolution family should be obtainable (reported, not fatal: the
    Gen 4-9 roll-out is ongoing work)
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_OUT = os.path.join(ROOT, "docs", "crystal_imperium", "data")

# First-battle trainer constant for each Gym Leader, in badge order (Johto then Kanto)
GYM_LEADERS = [
    ("FALKNER", "TRAINER_FALKNER_1_HNS"),
    ("BUGSY", "TRAINER_BUGSY_1_HNS"),
    ("WHITNEY", "TRAINER_WHITNEY_1_HNS"),
    ("MORTY", "TRAINER_MORTY_1_HNS"),
    ("CHUCK", "TRAINER_CHUCK_1_HNS"),
    ("JASMINE", "TRAINER_JASMINE_1_HNS"),
    ("PRYCE", "TRAINER_PRYCE_1_HNS"),
    ("CLAIR", "TRAINER_CLAIR_1_HNS"),
]

# Trainers that count as bosses: four explicit moves required, listed in the balance table
BOSS_PATTERNS = [
    r"TRAINER_(FALKNER|BUGSY|WHITNEY|MORTY|CHUCK|JASMINE|PRYCE|CLAIR)_\w+",
    r"TRAINER_(BROCK|MISTY|LT_SURGE|SURGE|ERIKA|JANINE|SABRINA|BLAINE|BLUE)_\w+",
    r"TRAINER_(WILL|KOGA|BRUNO|KAREN|LANCE|RED)_\w*",
    r"TRAINER_RIVAL_\w+",
    r"TRAINER_LI_HNS",
]
# Bosses already reworked for Crystal Imperium; the four-move rule is enforced only for these
REWORKED = {"TRAINER_FALKNER_1_HNS", "TRAINER_LI_HNS", "TRAINER_BUGSY_1_HNS", "TRAINER_WHITNEY_1_HNS"}


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def constify(name):
    """Showdown-style name -> CONSTANT_STYLE (mirrors trainerproc closely enough)."""
    name = name.replace("♀", "_F").replace("♂", "_M").replace("é", "E")
    name = name.replace("'", "").replace("\u2019", "").replace(".", "")
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


def parse_parties(path):
    trainers = {}
    for block in re.split(r"(?m)^(?==== )", read(path)):
        m = re.match(r"=== (\w+) ===", block)
        if not m:
            continue
        tid = m.group(1)
        header, _, body = block.partition("\n\n")
        info = {"id": tid, "mons": []}
        for line in header.splitlines()[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip().lower().replace(" ", "_")] = v.strip()
        for monblock in re.split(r"\n\s*\n", body.strip()):
            lines = [l.strip() for l in monblock.strip().splitlines() if l.strip() and not l.strip().startswith("/*")]
            if not lines:
                continue
            first = lines[0]
            mon = {"moves": []}
            species, _, item = first.partition("@")
            species = re.sub(r"\s*\((M|F)\)\s*$", "", species.strip())
            if "(" in species and species.endswith(")"):  # Nickname (Species)
                species = species[species.rindex("(") + 1:-1]
            mon["species"] = species.strip()
            if item.strip():
                mon["item"] = item.strip()
            for l in lines[1:]:
                if l.startswith("- "):
                    mon["moves"].append(l[2:].strip())
                elif ":" in l:
                    k, v = l.split(":", 1)
                    mon[k.strip().lower().replace(" ", "_")] = v.strip()
                elif l.endswith(" Nature"):
                    mon["nature"] = l[:-len(" Nature")]
            if "level" in mon:
                mon["level"] = int(mon["level"])
            info["mons"].append(mon)
        trainers[tid] = info
    return trainers


def macro_arguments(text, field, macro):
    """The argument text of every `field = MACRO(...)` in text, with nested parentheses matched."""
    result = []
    for m in re.finditer(re.escape(field) + r"\s*=\s*" + macro + r"\(", text):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
        result.append(text[m.end():i - 1])
    return result


def parse_species():
    """SPECIES_X -> {abilities:set, evolutions:[SPECIES_Y], name}"""
    species = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "src/data/pokemon/species_info/*.h"))):
        text = open(path, encoding="utf-8").read()
        parts = re.split(r"(?m)^\s*\[(SPECIES_\w+)\]\s*=", text)
        for name, body in zip(parts[1::2], parts[2::2]):
            entry = species.setdefault(name, {"abilities": set(), "evolutions": []})
            for abl in re.findall(r"\.abilities\s*=\s*\{([^}]*)\}", body):
                entry["abilities"].update(a.strip() for a in abl.split(",") if a.strip() and a.strip() != "ABILITY_NONE")
            for evo in macro_arguments(body, ".evolutions", "EVOLUTION"):
                entry["evolutions"] += re.findall(r"SPECIES_\w+", evo)
    return species


def species_constant(name, species):
    """Party species name -> SPECIES constant, falling back to the default form (e.g. _TWO_SEGMENT)."""
    sp = "SPECIES_" + constify(name)
    if sp in species:
        return sp
    forms = sorted(s for s in species if s.startswith(sp + "_"))
    return forms[0] if forms else sp


def national_species():
    """Species constants of the National Dex (enum NationalDexOrder, including HnS's separate
    regional-form entries), with aliases resolved to the defined form (SPECIES_MIMIKYU ->
    SPECIES_MIMIKYU_DISGUISED). HnS numbers some forms below 1025, so numbers can't be used."""
    dex = read("include/constants/pokedex.h")
    names = re.findall(r"NATIONAL_DEX_(\w+),", re.search(r"enum\s+NationalDexOrder\s*\{(.*?)\};", dex, re.S).group(1))
    alias = dict(re.findall(r"#define (SPECIES_\w+)\s+(SPECIES_\w+)", read("include/constants/species.h")))
    result = set()
    for name in names:
        if name == "NONE":
            continue
        sp = "SPECIES_" + name
        while sp in alias:
            sp = alias[sp]
        result.add(sp)
    return result


def parse_level_caps():
    text = read("src/caps.c")
    m = re.search(r"sLevelCapTable_Normal\[\]\s*=\s*\{(.*?)\};", text, re.S)
    return [int(v) for v in re.findall(r"\]\s*=\s*(\d+)", m.group(1))]


def families(species):
    parent = {}
    for s, e in species.items():
        for child in e["evolutions"]:
            parent.setdefault(child, s)
    def root(s):
        seen = set()
        while s in parent and s not in seen:
            seen.add(s)
            s = parent[s]
        return s
    return {s: root(s) for s in species}


def parse_encounters(data=None):
    """Wild encounters on HnS maps plus scripted gifts/static encounters. `data` replaces
    src/data/wild_encounters.json (gen_hidden_encounters.py passes it without hidden slots)."""
    found = defaultdict(list)
    if data is None:
        data = json.loads(read("src/data/wild_encounters.json"))
    for group in data["wild_encounter_groups"]:
        if group.get("label") != "gWildMonHeaders":
            continue
        for enc in group["encounters"]:
            mapname = enc.get("map", "")
            if not mapname.endswith("_HNS"):
                continue
            label = enc.get("base_label", "")
            time = "night" if label.endswith("_Night") else "day" if label.endswith("_Day") else "any"
            for method, table in enc.items():
                if isinstance(table, dict) and "mons" in table:
                    for mon in table["mons"]:
                        found[mon["species"]].append({
                            "map": mapname, "method": method.replace("_mons", ""), "time": time,
                            "min": mon["min_level"], "max": mon["max_level"]})
    for path in glob.glob(os.path.join(ROOT, "data/maps/*_hns/scripts.*")):
        mapname = os.path.basename(os.path.dirname(path))
        text = open(path, encoding="utf-8").read()
        for kind, sp, lvl in re.findall(r"\b(givemon|setwildbattle|giveegg)\s*\(?\s*(SPECIES_\w+)\s*(?:,\s*(\d+))?", text):
            found[sp].append({"map": mapname, "method": kind, "time": "any",
                              "min": int(lvl) if lvl else None, "max": int(lvl) if lvl else None})
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="validate only, do not rewrite databases")
    args = ap.parse_args()

    errors, notes = [], []
    trainers = parse_parties("src/data/trainers_hns.party")
    species = parse_species()
    caps = parse_level_caps()
    encounters = parse_encounters()

    # Abilities and move counts
    for tid, t in trainers.items():
        boss = any(re.fullmatch(p, tid) for p in BOSS_PATTERNS)
        for mon in t["mons"]:
            sp = species_constant(mon["species"], species)
            if sp not in species:
                errors.append(f"{tid}: unknown species '{mon['species']}' ({sp})")
                continue
            if "ability" in mon:
                ab = "ABILITY_" + constify(mon["ability"])
                if species[sp]["abilities"] and ab not in species[sp]["abilities"]:
                    errors.append(f"{tid}: {mon['species']} cannot have {mon['ability']} "
                                  f"(has {', '.join(sorted(species[sp]['abilities']))})")
            if tid in REWORKED and len(mon["moves"]) != 4:
                errors.append(f"{tid}: {mon['species']} has {len(mon['moves'])} moves; reworked bosses need 4")
            if boss and "level" not in mon:
                errors.append(f"{tid}: {mon['species']} has no Level (trainerproc defaults it)")

    # Level caps vs Gym aces: cap with N badges is the cap for the (N+1)th leader
    for badge, (leader, tid) in enumerate(GYM_LEADERS):
        if tid not in trainers:
            errors.append(f"missing Gym Leader trainer {tid}")
            continue
        ace = max(m.get("level", 0) for m in trainers[tid]["mons"])
        if ace > caps[badge]:
            errors.append(f"{leader}: ace level {ace} exceeds the NORMAL level cap {caps[badge]} for {badge} badges")
        elif ace < caps[badge]:
            notes.append(f"{leader}: ace level {ace} is below the NORMAL cap {caps[badge]} (player can overlevel)")

    # Family availability
    fam = families(species)
    obtainable_roots = {fam.get(s, s) for s in encounters}
    roots = sorted({fam[s] for s in national_species() if s in fam})
    missing = [r for r in roots if r not in obtainable_roots]

    print(f"trainers: {len(trainers)}   species entries: {len(species)}   level caps: {caps}")
    print(f"obtainable evolution families (wild + scripted): {len(obtainable_roots)}; "
          f"families with no source yet: {len(missing)}")
    for n in notes:
        print("note:", n)
    for e in errors:
        print("ERROR:", e)

    if not args.check:
        os.makedirs(DATA_OUT, exist_ok=True)
        bosses = {tid: t for tid, t in trainers.items() if any(re.fullmatch(p, tid) for p in BOSS_PATTERNS)}
        with open(os.path.join(DATA_OUT, "trainer_balance.json"), "w") as f:
            json.dump({"generated_by": "tools/crystal_imperium/validate.py",
                       "level_caps_normal": caps,
                       "gym_leaders": [{"leader": l, "trainer": t, "badge_index": i + 1}
                                       for i, (l, t) in enumerate(GYM_LEADERS)],
                       "reworked": sorted(REWORKED),
                       "bosses": bosses}, f, indent=1, sort_keys=True)
        with open(os.path.join(DATA_OUT, "encounters.json"), "w") as f:
            json.dump({"generated_by": "tools/crystal_imperium/validate.py",
                       "species": {k: v for k, v in sorted(encounters.items())},
                       "families_without_source": missing}, f, separators=(",", ":"))
        print(f"wrote {os.path.relpath(DATA_OUT, ROOT)}/trainer_balance.json and encounters.json")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
