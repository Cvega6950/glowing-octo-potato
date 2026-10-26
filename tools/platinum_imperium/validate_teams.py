#!/usr/bin/env python3
"""Platinum Imperium: checks the hand-made teams of the bosses and route mini-bosses
(src/data/level_cap_bosses.h) in src/data/trainers.party against the data the ROM is built with:
every ability is one of the species' (Emerald Imperium's, species_info/imperium_abilities.h), and
every move is learned by level up at the boss's level or below (by the species or one it evolves
from), is an Egg Move of its family, or is teachable (a TM or tutor). Levels are the cap of the
boss's stage, as the game sets them (src/caps.c).

Usage: tools/platinum_imperium/validate_teams.py   (exit status 1 on a problem)
"""
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def const(name, prefix):
    name = name.replace("é", "e").replace("'", "").replace(".", "").replace(":", "")
    return prefix + re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


def load_species():
    """SPECIES_X -> {abilities, levelup, teachable, egg, evolutions}, and display name -> SPECIES_X."""
    species, by_name = {}, {}
    for path in sorted(glob.glob(os.path.join(ROOT, "src/data/pokemon/species_info/gen_*_families.h"))):
        text = open(path, encoding="utf-8").read()
        for m in re.finditer(r"\n    \[(SPECIES_\w+)\] =\n    \{(.*?)\n    \},", text, re.S):
            body = m.group(2)
            info = {"abilities": [], "levelup": None, "teachable": None, "egg": None, "evolutions": []}
            a = re.search(r"\.abilities = \{([^}]*)\}", body)
            if a:
                info["abilities"] = [x.strip() for x in a.group(1).split(",")]
            for field, key in (("levelUpLearnset", "levelup"), ("teachableLearnset", "teachable"),
                               ("eggMoveLearnset", "egg")):
                f = re.search(r"\.%s = (\w+)" % field, body)
                if f:
                    info[key] = f.group(1)
            e = re.search(r"\.evolutions = EVOLUTION\((.*?)\),\n", body, re.S)
            if e:
                info["evolutions"] = re.findall(r"SPECIES_\w+", e.group(1))
            n = re.search(r'\.speciesName = _\("([^"]*)"\)', body)
            species.setdefault(m.group(1), info)
            if n:
                by_name.setdefault(n.group(1), m.group(1))
    for m in re.finditer(r"\[(SPECIES_\w+)\]\.abilities = \{([^}]*)\}",
                         read("src/data/pokemon/species_info/imperium_abilities.h")):
        if m.group(1) in species:
            species[m.group(1)]["abilities"] = [x.strip() for x in m.group(2).split(",")]
    return species, by_name


def load_tables(path, kind):
    tables = {}
    for m in re.finditer(r"static const (?:struct LevelUpMove|u16) (s\w+)\[\] = \{(.*?)\};", read(path), re.S):
        if kind == "levelup":
            tables[m.group(1)] = [(int(l), mv) for l, mv in re.findall(r"LEVEL_UP_MOVE\(\s*(\d+),\s*(MOVE_\w+)\)", m.group(2))]
        else:
            tables[m.group(1)] = re.findall(r"MOVE_\w+", m.group(2))
    return tables


def load_bosses():
    stages = dict(re.findall(r"\{(TRAINER_\w+), (\d+)\}", read("src/data/level_cap_bosses.h")))
    caps = re.search(r"sLevelCapTable_Normal\[\] =\s*\{(.*?)\};", read("src/caps.c"), re.S).group(1)
    caps = re.sub(r"//[^\n]*", "", caps)
    caps = [int(v) for _, v in re.findall(r"\[(\d+)\] = (\d+)", caps)]
    return {t: caps[int(s)] for t, s in stages.items()}


def load_parties():
    parties = {}
    for block in re.split(r"\n(?==== TRAINER_)", read("src/data/trainers.party")):
        m = re.match(r"=== (TRAINER_\w+) ===", block)
        if not m:
            continue
        mons = []
        for chunk in re.split(r"\n\s*\n", block)[1:]:
            lines = [l.strip() for l in chunk.strip().split("\n") if l.strip()]
            if not lines or lines[0].startswith("#"):
                continue
            head = re.match(r"(.+?)(?: \((?:M|F)\))?(?: @ (.+))?$", lines[0])
            mon = {"species": head.group(1).strip(), "ability": None, "moves": []}
            for l in lines[1:]:
                if l.startswith("Ability:"):
                    mon["ability"] = l.split(":", 1)[1].strip()
                elif l.startswith("- "):
                    mon["moves"].append(l[2:].strip())
            mons.append(mon)
        parties[m.group(1)] = mons
    return parties


def main():
    species, by_name = load_species()
    levelup = load_tables("src/data/pokemon/level_up_learnsets/imperium.h", "levelup")
    teach = load_tables("src/data/pokemon/teachable_learnsets.h", "moves")
    egg = load_tables("src/data/pokemon/egg_moves_imperium.h", "moves")
    prevo = {}
    for s, info in species.items():
        for e in info["evolutions"]:
            prevo.setdefault(e, s)
    bosses, parties = load_bosses(), load_parties()
    problems = 0
    for trainer, level in sorted(bosses.items()):
        for mon in parties.get(trainer, []):
            sp = by_name.get(mon["species"])
            if sp is None:
                print(f"{trainer}: unknown species {mon['species']}")
                problems += 1
                continue
            family, s = [], sp
            while s:
                family.append(s)
                s = prevo.get(s)
            if mon["ability"] and const(mon["ability"], "ABILITY_") not in species[sp]["abilities"]:
                print(f"{trainer}: {mon['species']} can't have {mon['ability']} ({', '.join(species[sp]['abilities'])})")
                problems += 1
            for move in mon["moves"]:
                mv = const(move, "MOVE_")
                ok = mv in teach.get(species[sp]["teachable"], [])
                for s in family:
                    ok = ok or any(l <= level and m == mv for l, m in levelup.get(species[s]["levelup"], []))
                    ok = ok or mv in egg.get(species[s]["egg"], [])
                if not ok:
                    print(f"{trainer}: {mon['species']} (Lv{level}) can't learn {move}")
                    problems += 1
    print(f"{len(bosses)} bosses checked, {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
