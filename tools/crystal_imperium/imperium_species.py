#!/usr/bin/env python3
"""Crystal Imperium: Emerald Imperium's abilities, level-up moves and Egg Moves (DECISIONS.md D35).

Emerald Imperium takes its Pokemon data from Radical Red (its documentation sends players to the
Radical Red dex for it), with a short list of documented differences (IMPERIUM_CHANGES below).
This script reads the Radical Red dex's data file and writes, for every species it has:

  src/data/pokemon/level_up_learnsets/imperium.h   level-up moves (Heart & Soul's Gen 7 learnsets,
                                                   gen_7.h, for every species Radical Red lacks)
  src/data/pokemon/egg_moves_imperium.h            Egg Moves (egg_moves.h for the rest)
  src/data/pokemon/species_info/imperium_abilities.h   the abilities that differ, as overrides of
                                                   the species table (src/data/pokemon/species_info.h)

  python3 tools/crystal_imperium/imperium_species.py --rr-data PATH           # rewrite the files
  python3 tools/crystal_imperium/imperium_species.py --rr-data PATH --check   # exit 1 if out of date
  python3 tools/crystal_imperium/imperium_species.py --rr-data PATH --report  # what was left out

PATH is the Radical Red dex's data.js (RR_DATA_URL; these files came from RR_DATA_SHA256). It is
not kept in this repository. Its ability lists put the hidden ability first: [hidden, 1st, 2nd].
Radical Red has a few abilities and moves of its own that this engine doesn't have: a slot whose
ability doesn't exist keeps one of Heart & Soul's abilities for the species, and a move that
doesn't exist is left out (--report lists both). Radical Red's own forms (its Sevii forms and its
extra Megas) don't exist here and are skipped. TM and tutor compatibility stays Heart & Soul's:
Crystal Imperium's TM list is its own (tools/crystal_imperium/tm_list.py).
"""
import argparse
import ast
import hashlib
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RR_DATA_URL = "https://raw.githubusercontent.com/JwowSquared/Radical-Red-Pokedex/master/data.js"
RR_DATA_SHA256 = "04c9dc94b6a7e3d33f5dcb5e804487466e7a249f4d340cf19853d70f37596df9"

LEVEL_UP_BASE = "src/data/pokemon/level_up_learnsets/gen_7.h"  # P_LVL_UP_LEARNSETS is GEN_7
LEVEL_UP_OUT = "src/data/pokemon/level_up_learnsets/imperium.h"
EGG_BASE = "src/data/pokemon/egg_moves.h"
EGG_OUT = "src/data/pokemon/egg_moves_imperium.h"
ABILITIES_OUT = "src/data/pokemon/species_info/imperium_abilities.h"

MAX_LEVEL_UP_MOVES = 40     # include/constants/pokemon.h
EGG_MOVES_ARRAY_COUNT = 19  # include/constants/daycare.h: the daycare's and DexNav's buffers

# Radical Red keys whose constant isn't the key itself
SPECIES_ALIASES = {
    "Screamtail": "SPECIES_SCREAM_TAIL",
}

# Radical Red names (cut to its 12-letter limit) for this engine's moves
MOVE_ALIASES = {
    "Disarm Cry": "MOVE_DISARMING_VOICE",
    "Drain Kiss": "MOVE_DRAINING_KISS",
    "Crafty Guard": "MOVE_CRAFTY_SHIELD",
    "Flower Guard": "MOVE_FLOWER_SHIELD",
    "Prism Laser": "MOVE_PRISMATIC_LASER",
    "Inferno Parade": "MOVE_INFERNAL_PARADE",
}

# Radical Red ability names for this engine's abilities: cut names, both "As One"s (by Radical Red
# ID) and Valiant Shield, Radical Red's name for Dauntless Shield's effect ("Raises Defense on entry")
ABILITY_ALIASES = {
    "Neutralize Gas": "ABILITY_NEUTRALIZING_GAS",
    "Wandering Soul": "ABILITY_WANDERING_SPIRIT",
    "WaterCompaction": "ABILITY_WATER_COMPACTION",
    "ThermalExchange": "ABILITY_THERMAL_EXCHANGE",
    "Electromrphosis": "ABILITY_ELECTROMORPHOSIS",
    "SupremeOverlord": "ABILITY_SUPREME_OVERLORD",
    "OrichalcumPulse": "ABILITY_ORICHALCUM_PULSE",
    "Valiant Shield": "ABILITY_DAUNTLESS_SHIELD",
    ("As One", 73): "ABILITY_AS_ONE_SHADOW_RIDER",  # "Both Unnerve and Grim Neigh"
    ("As One", 77): "ABILITY_AS_ONE_ICE_RIDER",     # "Both Unnerve and Moxie" (Chilling Neigh)
}


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def constify(name, prefix):
    s = name.replace("♀", "-F").replace("♂", "-M").replace("é", "e").replace("%", "")
    s = re.sub(r"[’'.:]", "", s)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").upper()
    return prefix + s


# --- Radical Red's data --------------------------------------------------------------------------

def load_rr(path):
    with open(path, "rb") as f:
        raw = f.read()
    digest = hashlib.sha256(raw).hexdigest()
    src = raw.decode("utf-8").strip().rstrip(";")
    return ast.literal_eval(src), digest


# --- This game's data ----------------------------------------------------------------------------

def enum_names(path, prefix):
    return set(re.findall(rf"^\s*({prefix}\w+)\s*=", read(path), re.M))


def species_constants():
    """SPECIES_X -> number, following aliases (#define SPECIES_A SPECIES_B)."""
    raw = dict(re.findall(r"^#define\s+(SPECIES_\w+)\s+(\S+)", read("include/constants/species.h"), re.M))
    out = {}

    def value(name, depth=0):
        v = raw.get(name)
        if v is None or depth > 10:
            return None
        if re.fullmatch(r"\d+", v):
            return int(v)
        if v in raw:
            return value(v, depth + 1)
        return None

    for name in raw:
        v = value(name)
        if v is not None:
            out[name] = v
    return out


def preprocessed_pokemon_c():
    cmd = ["arm-none-eabi-cpp", "-iquote", "include", "-Wno-trigraphs", "-DMODERN=1", "-DTESTING=0",
           "-DPOKEMON_HNS", "-std=gnu17", "src/pokemon.c"]
    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if res.returncode != 0:
        sys.exit("preprocessing src/pokemon.c failed:\n" + res.stderr[-2000:])
    return res.stdout


def matching_brace(text, start):
    """Index just past the brace that closes the one at text[start]."""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced braces")


def species_table(pre):
    """number -> {abilities: [3 names], levelUp: symbol, egg: symbol, forms: symbol} from the species
    table as compiled (only its [N] = {...} entries: the overrides this script writes are skipped)."""
    m = re.search(r"gSpeciesInfo\[\]\s*=\s*\{", pre)
    body_start = m.end() - 1
    body_end = matching_brace(pre, body_start)
    body = pre[body_start + 1:body_end - 1]
    table = {}
    pos = 0
    entry = re.compile(r"\[\s*\(?\s*(\d+)\s*\)?\s*\]\s*=\s*\{")
    while True:
        m = entry.search(body, pos)
        if not m:
            break
        start = m.end() - 1
        end = matching_brace(body, start)
        block = body[start:end]
        num = int(m.group(1))
        info = {}
        a = re.search(r"\.abilities\s*=\s*\{([^}]*)\}", block)
        if a:
            abl = [x.strip() for x in a.group(1).split(",") if x.strip()]
            info["abilities"] = (abl + ["ABILITY_NONE"] * 3)[:3]
        for key, field in (("levelUp", "levelUpLearnset"), ("egg", "eggMoveLearnset"), ("forms", "formSpeciesIdTable")):
            f = re.search(rf"\.{field}\s*=\s*(\w+)", block)
            if f:
                info[key] = f.group(1)
        table[num] = info
        pos = end
    return table


def form_tables(pre):
    """symbol -> [species numbers] from the form species tables, base form first."""
    out = {}
    for m in re.finditer(r"static const u16 (s\w+FormSpeciesIdTable)\[\]\s*=\s*\{([^}]*)\}", pre):
        out[m.group(1)] = [int(x) for x in re.findall(r"\b(\d+)\b", m.group(2)) if int(x) != 0xFFFF]
    return out


def learnset_blocks(text, kind):
    pattern = (r"(static const struct LevelUpMove (s\w+LevelUpLearnset)\[\] = \{\n)(.*?)(\};)" if kind == "levelUp"
               else r"(static const u16 (s\w+EggMoveLearnset)\[\] = \{\n)(.*?)(\};)")
    return re.compile(pattern, re.S)


# --- Mapping -------------------------------------------------------------------------------------

class Mapper:
    def __init__(self, rr):
        self.rr = rr
        self.consts = species_constants()
        self.moves = enum_names("include/constants/moves.h", "MOVE_")
        self.abilities = enum_names("include/constants/abilities.h", "ABILITY_")
        self.missing_moves = Counter()
        self.missing_abilities = Counter()

    def species(self, s):
        name = SPECIES_ALIASES.get(s["key"], constify(s["key"], "SPECIES_"))
        return name if name in self.consts else None

    def move(self, move_id):
        name = self.rr["moves"][move_id]["name"]
        const = MOVE_ALIASES.get(name, constify(name, "MOVE_"))
        if const in self.moves:
            return const
        self.missing_moves[name] += 1
        return None

    def ability(self, slot):
        ab_id, index = slot
        if not ab_id:
            return "ABILITY_NONE"
        names = self.rr["abilities"][ab_id]["names"]
        name = names[index] if index < len(names) else names[0]
        for const in (ABILITY_ALIASES.get((name, ab_id)), ABILITY_ALIASES.get(name), constify(name, "ABILITY_"),
                      constify(names[0], "ABILITY_")):  # names sharing a Radical Red ID work the same there
            if const in self.abilities:
                return const
        self.missing_abilities[name.strip()] += 1
        return None


# Emerald Imperium's documented differences from Radical Red ("New Mega Evolutions" page of its
# documentation), as far as they touch abilities, level-up moves and Egg Moves
def imperium_changes(data):
    """Edit data[SPECIES_X] = {abilities, levelUp: [(level, MOVE)], egg: [MOVE]} in place. In
    abilities, None marks a Radical Red ability this engine doesn't have."""
    for sp in ("SPECIES_TORCHIC", "SPECIES_COMBUSKEN", "SPECIES_BLAZIKEN"):
        # "Removed Speed Boost ... now get Blaze, Early Bird, Striker" (Striker isn't in this
        # engine: no hidden ability, rather than Heart & Soul's Speed Boost)
        if sp in data:
            data[sp]["abilities"] = ["ABILITY_BLAZE", "ABILITY_EARLY_BIRD", "ABILITY_NONE"]
    if "SPECIES_BLAZIKEN" in data:
        data["SPECIES_BLAZIKEN"]["levelUp"].append((64, "MOVE_THUNDEROUS_KICK"))
    for sp, move in (("SPECIES_LATIOS", "MOVE_MEMENTO"), ("SPECIES_LATIAS", "MOVE_HEALING_WISH")):
        # "Latios/Latias learn Memento/Healing Wish at level 71 instead of 61"
        if sp in data:
            data[sp]["levelUp"] = [(71 if (lv, m) == (61, move) else lv, m) for lv, m in data[sp]["levelUp"]]
    if "SPECIES_MAROWAK_ALOLA" in data:
        # "Alolan Marowak has Battle Armor instead of Bone Zone"
        abl = data["SPECIES_MAROWAK_ALOLA"]["abilities"]
        data["SPECIES_MAROWAK_ALOLA"]["abilities"] = ["ABILITY_BATTLE_ARMOR" if a is None else a for a in abl]
    for sp, move in (("SPECIES_URSHIFU_SINGLE_STRIKE", "MOVE_WICKED_BLOW"),
                     ("SPECIES_URSHIFU_RAPID_STRIKE", "MOVE_SURGING_STRIKES")):
        # "Urshifu gets signature move upon evolution"
        if sp in data and (0, move) not in data[sp]["levelUp"]:
            data[sp]["levelUp"].insert(0, (0, move))


def build(rr):
    mp = Mapper(rr)
    data = {}       # SPECIES_X -> {abilities, levelUp, egg}
    unmatched = []
    seen = set()
    for s in rr["species"].values():
        const = mp.species(s)
        if const is None:
            unmatched.append(s["key"])
            continue
        if const in seen:
            continue
        seen.add(const)
        level_up = []
        for move_id, level in s["levelupMoves"]:
            m = mp.move(move_id)
            if m and (level, m) not in level_up:
                level_up.append((level, m))
        egg = []
        for move_id in s.get("eggMoves", []):
            m = mp.move(move_id)
            if m and m not in egg:
                egg.append(m)
        hidden, first, second = (mp.ability(a) for a in s["abilities"])
        if first == "ABILITY_NONE":
            first, second = second, "ABILITY_NONE"
        data[const] = {"abilities": [first, second, hidden], "levelUp": level_up, "egg": egg}
    imperium_changes(data)
    for d in data.values():
        d["levelUp"].sort(key=lambda e: e[0])  # stable: same-level moves keep Radical Red's order
    return mp, data, unmatched


def effective_abilities(abl):
    """The ability a Pokemon with each ability number gets (GetAbilityBySpecies: an empty hidden slot
    falls back to another hidden one, then any empty slot to the first ability there is)."""
    out = []
    for n in range(3):
        a = abl[n]
        if a == "ABILITY_NONE" and n >= 2:
            a = next((x for x in abl[2:] if x != "ABILITY_NONE"), a)
        if a == "ABILITY_NONE":
            a = next((x for x in abl if x != "ABILITY_NONE"), a)
        out.append(a)
    return out


def form_change_abilities():
    """Abilities a form change needs (src/data/pokemon/form_change_tables.h, such as Silvally's RKS
    System for its Memories), and the ones the battle engine changes forms with by itself."""
    found = set(re.findall(r"\bABILITY_\w+", read("src/data/pokemon/form_change_tables.h")))
    return found | {"ABILITY_STANCE_CHANGE", "ABILITY_POWER_CONSTRUCT", "ABILITY_BATTLE_BOND", "ABILITY_ZERO_TO_HERO",
                    "ABILITY_FORECAST", "ABILITY_FLOWER_GIFT", "ABILITY_TERA_SHIFT", "ABILITY_MULTITYPE", "ABILITY_RKS_SYSTEM"}


def render_level_up(entries):
    return "".join(f"    LEVEL_UP_MOVE({lv:2d}, {m}),\n" for lv, m in entries) + "    LEVEL_UP_END,\n"


def render_egg(entries):
    return "".join(f"    {m},\n" for m in entries) + "    MOVE_UNAVAILABLE,\n"


def symbol_sources(table, consts, data, key):
    """learnset symbol -> SPECIES_X whose Radical Red data it gets: the first species (lowest number)
    using the symbol that Radical Red has."""
    by_number = defaultdict(list)
    for name, num in consts.items():
        by_number[num].append(name)
    out = {}
    for num in sorted(table):
        sym = table[num].get(key)
        if not sym or sym in out:
            continue
        for name in sorted(by_number[num], key=lambda n: (n not in data, len(n))):
            if name in data:
                out[sym] = name
                break
    return out


def generate(rr, report=False):
    mp, data, unmatched = build(rr)
    pre = preprocessed_pokemon_c()
    table = species_table(pre)
    forms = form_tables(pre)
    consts = mp.consts
    names_of = defaultdict(list)
    for name, num in consts.items():
        names_of[num].append(name)
    notes = []

    # Level-up learnsets
    level_src = symbol_sources(table, consts, data, "levelUp")
    base = read(LEVEL_UP_BASE)

    def level_sub(m):
        sym = m.group(2)
        sp = level_src.get(sym)
        if not sp:
            return m.group(0)
        entries = data[sp]["levelUp"]
        if len(entries) > MAX_LEVEL_UP_MOVES:
            notes.append(f"{sp}: {len(entries)} level-up moves, kept the first {MAX_LEVEL_UP_MOVES}")
            entries = entries[:MAX_LEVEL_UP_MOVES]
        if not entries:
            return m.group(0)
        return m.group(1) + render_level_up(entries) + m.group(4)

    level_out = learnset_blocks(base, "levelUp").sub(level_sub, base)
    level_out = (f"// Generated by tools/crystal_imperium/imperium_species.py: Radical Red's level-up moves (Emerald\n"
                 f"// Imperium's, DECISIONS.md D35) for {len(level_src)} learnsets, Heart & Soul's Gen 7 ones ({LEVEL_UP_BASE})\n"
                 f"// for the rest. Edit the script, not this file.\n") + level_out

    # Egg Moves
    egg_src = symbol_sources(table, consts, data, "egg")
    base = read(EGG_BASE)

    def egg_sub(m):
        sym = m.group(2)
        sp = egg_src.get(sym)
        if not sp or sym == "sNoneEggMoveLearnset":
            return m.group(0)
        entries = data[sp]["egg"]
        if len(entries) > EGG_MOVES_ARRAY_COUNT:
            notes.append(f"{sp}: {len(entries)} Egg Moves, kept the first {EGG_MOVES_ARRAY_COUNT}")
            entries = entries[:EGG_MOVES_ARRAY_COUNT]
        if not entries:
            return m.group(0)
        return m.group(1) + render_egg(entries) + m.group(4)

    egg_out = learnset_blocks(base, "egg").sub(egg_sub, base)
    egg_out = (f"// Generated by tools/crystal_imperium/imperium_species.py: Radical Red's Egg Moves (Emerald\n"
               f"// Imperium's, DECISIONS.md D35) for {len(egg_src)} species, Heart & Soul's ({EGG_BASE}) for the rest.\n"
               f"// Edit the script, not this file.\n") + egg_out

    # Abilities: species Radical Red has; a form it lacks that had the same abilities and level-up
    # moves as its base form (a Gigantamax form, a cosmetic form) follows the base form
    new_abilities = {}
    protected = form_change_abilities()
    for num in sorted(table):
        info = table[num]
        if "abilities" not in info or num == 0:
            continue
        src = next((n for n in sorted(names_of[num], key=len) if n in data), None)
        if src is None and info.get("forms") in forms:
            base_num = forms[info["forms"]][0]
            binfo = table.get(base_num, {})
            if base_num != num and binfo.get("abilities") == info["abilities"] and binfo.get("levelUp") == info.get("levelUp"):
                src = next((n for n in sorted(names_of[base_num], key=len) if n in data), None)
        if src is None:
            continue
        rr_abl = data[src]["abilities"]
        old = info["abilities"]
        new = []
        for i, r in enumerate(rr_abl):
            if r is None:  # Radical Red's own ability: one of Heart & Soul's not in the list yet
                keep = [old[i]] + [a for a in old if a != old[i]] if i < len(old) else old
                r = next((a for a in keep if a != "ABILITY_NONE" and a not in rr_abl and a not in new), "ABILITY_NONE")
            new.append(r)
        if new[0] == "ABILITY_NONE":
            new[0] = old[0]
        lost = [a for a in old if a in protected and a not in new]
        if lost:  # its form change would stop working: Heart & Soul's abilities stay
            notes.append(f"{names_of[num][0]}: kept {', '.join(lost)} (a form change needs it), so its abilities stay")
            continue
        if effective_abilities(new) != effective_abilities(old):
            new_abilities[num] = (new, old)
    lines = ["// Generated by tools/crystal_imperium/imperium_species.py: Radical Red's abilities (Emerald",
             "// Imperium's, DECISIONS.md D35) where they differ from Heart & Soul's. Included at the end of",
             "// gSpeciesInfo (src/data/pokemon/species_info.h): each line replaces one species' abilities.",
             "// Edit the script, not this file.", ""]
    for num, (new, old) in sorted(new_abilities.items()):
        name = min((n for n in names_of[num]), key=lambda n: (n not in data, len(n)))
        lines.append(f"    [{name}].abilities = {{ {', '.join(new)} }}, // was {', '.join(a.replace('ABILITY_', '') for a in old)}")
    abilities_out = "\n".join(lines) + "\n"

    stats = {"level": len(level_src), "egg": len(egg_src), "abilities": len(new_abilities)}
    if report:
        print(f"Radical Red species matched: {len(data)}; not in this game: {len(unmatched)}")
        print("  " + ", ".join(unmatched))
        print(f"learnsets from Radical Red: {stats['level']} level-up, {stats['egg']} Egg Move lists; "
              f"{stats['abilities']} species with new abilities")
        print("moves left out (not in this engine): " + ", ".join(f"{k} ({v})" for k, v in mp.missing_moves.most_common()))
        print("abilities kept as Heart & Soul's (not in this engine): "
              + ", ".join(f"{k} ({v})" for k, v in mp.missing_abilities.most_common()))
        for n in notes:
            print(n)
    return {LEVEL_UP_OUT: level_out, EGG_OUT: egg_out, ABILITIES_OUT: abilities_out}, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rr-data", required=True, help="the Radical Red dex's data.js (" + RR_DATA_URL + ")")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    rr, digest = load_rr(args.rr_data)
    if digest != RR_DATA_SHA256:
        print(f"note: {args.rr_data} has SHA-256 {digest}, not the {RR_DATA_SHA256} these files came from")
    files, stats = generate(rr, args.report)
    stale = [p for p, text in files.items() if not os.path.exists(os.path.join(ROOT, p)) or read(p) != text]
    if args.check:
        for p in stale:
            print(f"{p} is out of date: run tools/crystal_imperium/imperium_species.py")
        return 1 if stale else 0
    for p in stale:
        with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
            f.write(files[p])
        print(f"wrote {p}")
    print(f"{stats['level']} level-up learnsets and {stats['egg']} Egg Move lists from Radical Red; "
          f"{stats['abilities']} species with new abilities")
    return 0


if __name__ == "__main__":
    sys.exit(main())
