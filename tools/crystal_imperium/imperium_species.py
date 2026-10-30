#!/usr/bin/env python3
"""Crystal Imperium: Emerald Imperium's abilities, level-up moves, Egg Moves (DECISIONS.md D35), TM
and tutor compatibility (D39) and, since 0.15.1, base stats (D50), from the official Emerald Imperium
dex (D45).

Until 0.15.0 these came from the Radical Red dex, which Imperium's documentation pointed to; since
then from Imperium's own dex (ei_dex.py, EI_DEX_URL), which has its documented differences from
Radical Red already. This script reads that dex and writes, for every species it has:

  src/data/pokemon/level_up_learnsets/imperium.h   level-up moves (Heart & Soul's Gen 7 learnsets,
                                                   gen_7.h, for every species the dex lacks)
  src/data/pokemon/egg_moves_imperium.h            Egg Moves (egg_moves.h for the rest)
  src/data/pokemon/species_info/imperium_abilities.h   the abilities that differ, as overrides of
                                                   the species table (src/data/pokemon/species_info.h)
  src/data/pokemon/species_info/imperium_stats.h   the base stats that differ (Imperium's buffs), as
                                                   overrides of the species table too
  src/data/pokemon/imperium_teachables.json        the moves Imperium teaches by TM or tutor, and
                                                   which of them each species learns, for
                                                   tools/learnset_helpers/make_teachables.py

  python3 tools/crystal_imperium/imperium_species.py --ei-dex PATH           # rewrite the files
  python3 tools/crystal_imperium/imperium_species.py --ei-dex PATH --check   # exit 1 if out of date
  python3 tools/crystal_imperium/imperium_species.py --ei-dex PATH --report  # what was left out

PATH is a saved copy of the dex's page script (ei_dex.EI_DEX_URL; these files came from
ei_dex.EI_DEX_SHA256). It is not kept in this repository. Imperium has abilities of its own that this
engine doesn't have (Striker, Feline Prowess, Bone Zone...): a slot whose ability doesn't exist keeps
one of Heart & Soul's abilities for the species (--report lists them). Its own Megas and Primal forms
don't exist here and are skipped (D2). Crystal Imperium's TM list is Emerald Imperium's
(tools/crystal_imperium/tm_list.py); make_teachables.py decides with Imperium's lists which species
learn the TMs and tutor moves Imperium also has, and makes its other ones tutor moves.
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ei_dex  # noqa: E402  (the official Emerald Imperium dex's data)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

LEVEL_UP_BASE = "src/data/pokemon/level_up_learnsets/gen_7.h"  # P_LVL_UP_LEARNSETS is GEN_7
LEVEL_UP_OUT = "src/data/pokemon/level_up_learnsets/imperium.h"
EGG_BASE = "src/data/pokemon/egg_moves.h"
EGG_OUT = "src/data/pokemon/egg_moves_imperium.h"
ABILITIES_OUT = "src/data/pokemon/species_info/imperium_abilities.h"
STATS_OUT = "src/data/pokemon/species_info/imperium_stats.h"
# The six base stats in the dex's order (the engine's: HP, Attack, Defense, Speed, Sp. Atk, Sp. Def)
STAT_FIELDS = ["baseHP", "baseAttack", "baseDefense", "baseSpeed", "baseSpAttack", "baseSpDefense"]
STAT_NAMES = ["HP", "Atk", "Def", "Spe", "SpA", "SpD"]
TEACHABLES_OUT = "src/data/pokemon/imperium_teachables.json"

MAX_LEVEL_UP_MOVES = 40     # include/constants/pokemon.h
EGG_MOVES_ARRAY_COUNT = 19  # include/constants/daycare.h: the daycare's and DexNav's buffers

# The dex's ability names shared by several abilities, by its ability ID (the same numbers here)
ABILITY_ALIASES = {
    266: "ABILITY_AS_ONE_ICE_RIDER",                # "Unnerve and Chilling Neigh."
    267: "ABILITY_AS_ONE_SHADOW_RIDER",             # "Unnerve and Grim Neigh."
    301: "ABILITY_EMBODY_ASPECT_TEAL_MASK",         # "Raises Speed."
    302: "ABILITY_EMBODY_ASPECT_HEARTHFLAME_MASK",  # "Raises Attack."
    303: "ABILITY_EMBODY_ASPECT_WELLSPRING_MASK",   # "Raises Sp. Def."
    304: "ABILITY_EMBODY_ASPECT_CORNERSTONE_MASK",  # "Raises Defense."
}


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def constify(name, prefix):
    s = name.replace("♀", "-F").replace("♂", "-M").replace("é", "e").replace("%", "")
    s = re.sub(r"[’'.:]", "", s)
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").upper()
    return prefix + s


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


def c_int(expr):
    """The value of a C integer expression as the preprocessor leaves it in the species table: numbers,
    parentheses, ?:, ||, &&, comparisons, + - * / and unary ! and - (P_UPDATED_STATS >= GEN_6 ? 90 : 80)."""
    toks = re.findall(r"\d+|\|\||&&|==|!=|<=|>=|[()?:<>+\-*/!]", expr)
    if "".join(toks) != re.sub(r"\s+", "", expr):
        raise ValueError(f"not a constant expression: {expr}")
    pos = [0]
    ops = {"*": lambda a, b: a * b, "/": lambda a, b: a // b, "+": lambda a, b: a + b, "-": lambda a, b: a - b,
           "<": lambda a, b: int(a < b), "<=": lambda a, b: int(a <= b), ">": lambda a, b: int(a > b),
           ">=": lambda a, b: int(a >= b), "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b),
           "&&": lambda a, b: int(bool(a) and bool(b)), "||": lambda a, b: int(bool(a) or bool(b))}

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def primary():
        t = take()
        if t == "(":
            v = ternary()
            if take() != ")":
                raise ValueError(expr)
            return v
        if t == "!":
            return int(not primary())
        if t == "-":
            return -primary()
        return int(t)

    def level(names, sub):
        def parse():
            v = sub()
            while peek() in names:
                op = take()
                v = ops[op](v, sub())
            return v
        return parse

    lor = level({"||"}, level({"&&"}, level({"==", "!="}, level({"<", "<=", ">", ">="},
                                                               level({"+", "-"}, level({"*", "/"}, primary))))))

    def ternary():
        c = lor()
        if peek() != "?":
            return c
        take()
        a = ternary()
        if take() != ":":
            raise ValueError(expr)
        b = ternary()
        return a if c else b

    v = ternary()
    if pos[0] != len(toks):
        raise ValueError(expr)
    return v


def species_table(pre):
    """number -> {abilities: [3 names], levelUp: symbol, egg: symbol, forms: symbol, stats: [6]} from the species
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
        for key, field in (("levelUp", "levelUpLearnset"), ("egg", "eggMoveLearnset"), ("teach", "teachableLearnset"),
                           ("forms", "formSpeciesIdTable")):
            f = re.search(rf"\.{field}\s*=\s*(\w+)", block)
            if f:
                info[key] = f.group(1)
        stats = [re.search(rf"\.{field}\s*=\s*([^,\n]+),", block) for field in STAT_FIELDS]
        if all(stats):
            info["stats"] = [c_int(x.group(1)) for x in stats]
        table[num] = info
        pos = end
    return table


def form_tables(pre):
    """symbol -> [species numbers] from the form species tables, base form first."""
    out = {}
    for m in re.finditer(r"static const u16 (s\w+FormSpeciesIdTable)\[\]\s*=\s*\{([^}]*)\}", pre):
        out[m.group(1)] = [int(x) for x in re.findall(r"\b(\d+)\b", m.group(2)) if int(x) != 0xFFFF]
    return out


def teachable_lists():
    """SPECIES_X -> s<Name>TeachableLearnset for each teachable learnset in the species tables, named
    as tools/learnset_helpers/make_teachables.py names them: <Name> in snake case."""
    names = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "src/data/pokemon/species_info/*_families.h"))):
        with open(path, encoding="utf-8") as f:
            names |= set(re.findall(r"\.teachableLearnset\s*=\s*s(\w+?)TeachableLearnset", f.read()))
    names.discard("None")
    return {"SPECIES_" + re.sub(r"(?!^)([A-Z]+)", r"_\1", n).upper(): f"s{n}TeachableLearnset" for n in names}


def render_teachables(universe, species):
    out = ["{",
           '  "comment": "Generated by tools/crystal_imperium/imperium_species.py: the moves Emerald Imperium '
           'teaches by TM or tutor, and which of them each species learns there (its dex, DECISIONS.md D39, '
           'D45). Edit the script, not this file.",',
           '  "moves": [']
    out.append(",\n".join(f"    {json.dumps(m)}" for m in universe))
    out += ["  ],", '  "species": {']
    out.append(",\n".join(f"    {json.dumps(sp)}: {json.dumps(moves)}" for sp, moves in species.items()))
    out += ["  }", "}"]
    return "\n".join(out) + "\n"


def learnset_blocks(text, kind):
    pattern = (r"(static const struct LevelUpMove (s\w+LevelUpLearnset)\[\] = \{\n)(.*?)(\};)" if kind == "levelUp"
               else r"(static const u16 (s\w+EggMoveLearnset)\[\] = \{\n)(.*?)(\};)")
    return re.compile(pattern, re.S)


# --- Mapping -------------------------------------------------------------------------------------

class Mapper:
    """The dex's species, moves, abilities, items and types as this engine's constants."""

    def __init__(self, ei):
        self.ei = ei
        self.consts = species_constants()
        self.moves = enum_names("include/constants/moves.h", "MOVE_")
        self.abilities = enum_names("include/constants/abilities.h", "ABILITY_")
        self.items = enum_names("include/constants/items.h", "ITEM_")
        self.missing_moves = Counter()
        self.missing_abilities = Counter()
        self.missing_items = Counter()

    def species(self, s):
        """SPECIES_X for a dex species, by its name key ("Raichu-Alola", "Furfrou-Heart-Trim")."""
        name = constify(s["nameKey"], "SPECIES_")
        for const in (name, re.sub(r"_TRIM$", "", name)):
            if const in self.consts:
                return const
        return None

    def species_by_id(self, sid):
        s = self.ei["species"].get(sid)
        return self.species(s) if s else None

    def move(self, move_id):
        m = self.ei["moves"].get(move_id)
        if not m:
            return None
        const = constify(m["name"], "MOVE_")
        if const in self.moves:
            return const
        self.missing_moves[m["name"]] += 1
        return None

    def ability(self, ab_id):
        if not ab_id:
            return "ABILITY_NONE"
        name = self.ei["abilities"][ab_id]["name"]
        const = ABILITY_ALIASES.get(ab_id, constify(name, "ABILITY_"))
        if const in self.abilities:
            return const
        self.missing_abilities[name.strip()] += 1
        return None

    def item(self, item_id):
        name = self.ei["items"][item_id]["Name"]
        const = constify(name, "ITEM_")
        for c in (const, const.replace("_", ""), const.replace("BLACKAUGURITE", "BLACK_AUGURITE")):
            if c in self.items:
                return c
        self.missing_items[name] += 1
        return None

    def type(self, type_id):
        return "TYPE_" + self.ei["types"][type_id]["typeName"].upper()


def imperium_ability_rules(data):
    """Edit data[SPECIES_X]["abilities"] in place where an ability of Imperium's own (None) shouldn't
    fall back to one of Heart & Soul's: "Removed Speed Boost from Torchic / Combusken / Blaziken, now
    get Blaze, Early Bird, Striker" (Imperium's differences from Radical Red). Striker isn't in this
    engine: no hidden ability, rather than Heart & Soul's Speed Boost."""
    for sp in ("SPECIES_TORCHIC", "SPECIES_COMBUSKEN", "SPECIES_BLAZIKEN"):
        if sp in data:
            data[sp]["abilities"] = [a or "ABILITY_NONE" for a in data[sp]["abilities"]]


def build(ei):
    mp = Mapper(ei)
    data = {}       # SPECIES_X -> {abilities: [1st, 2nd, hidden], levelUp, egg, teach, stats: [6]}
    unmatched = []
    for sid, s in sorted(ei["species"].items()):
        const = mp.species(s)
        if const is None:
            unmatched.append(s["nameKey"])
            continue
        if const in data:
            continue
        level_up = []
        for move_id, level in s.get("levelUpMoves") or []:
            m = mp.move(move_id)
            if m and (level, m) not in level_up:
                level_up.append((level, m))
        egg = []
        for move_id in s.get("eggMoves") or []:
            m = mp.move(move_id)
            if m and m not in egg:
                egg.append(m)
        teach = {mp.move(m) for m in s.get("tmMoves") or []}
        teach.discard(None)
        first, second, hidden = (mp.ability(a) for a in s["abilities"])
        data[const] = {"abilities": [first, second, hidden], "levelUp": level_up, "egg": egg, "teach": teach,
                       "stats": [int(x) for x in s["stats"]]}
    imperium_ability_rules(data)
    for d in data.values():
        d["levelUp"].sort(key=lambda e: e[0])  # stable: same-level moves keep the dex's order
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
    """learnset symbol -> SPECIES_X whose dex data it gets: the first species (lowest number) using
    the symbol that the dex has."""
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


def generate(ei, report=False):
    mp, data, unmatched = build(ei)
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
    level_out = (f"// Generated by tools/crystal_imperium/imperium_species.py: Emerald Imperium's level-up moves (its\n"
                 f"// dex, DECISIONS.md D35, D45) for {len(level_src)} learnsets, Heart & Soul's Gen 7 ones ({LEVEL_UP_BASE})\n"
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
        return m.group(1) + render_egg(entries) + m.group(4)  # none in the dex: none here (Scatterbug)

    egg_out = learnset_blocks(base, "egg").sub(egg_sub, base)
    # A species the dex gives Egg Moves that has no list in Heart & Soul (Impidimp, Voltorb) gets one,
    # and an override line beside the abilities' (egg_lines)
    egg_symbols = set(re.findall(r"static const u16 (s\w+EggMoveLearnset)\[\]", egg_out))
    egg_lines = []
    for num in sorted(table):
        if table[num].get("egg") not in (None, "sNoneEggMoveLearnset"):
            continue
        sp = next((n for n in sorted(names_of[num], key=len) if n in data and data[n]["egg"]), None)
        if sp is None:
            continue
        sym = "s" + "".join(w.capitalize() for w in sp[len("SPECIES_"):].split("_")) + "EggMoveLearnset"
        if sym in egg_symbols:
            raise SystemExit(f"{sp}: {sym} already exists")
        egg_symbols.add(sym)
        egg_out += f"\nstatic const u16 {sym}[] = {{\n" + render_egg(data[sp]["egg"][:EGG_MOVES_ARRAY_COUNT]) + "};\n"
        egg_lines.append(f"    [{sp}].eggMoveLearnset = {sym}, // Heart & Soul has no Egg Move list for it")
    egg_out = (f"// Generated by tools/crystal_imperium/imperium_species.py: Emerald Imperium's Egg Moves (its\n"
               f"// dex, DECISIONS.md D35, D45) for {len(egg_src)} species, Heart & Soul's ({EGG_BASE}) for the rest.\n"
               f"// Edit the script, not this file.\n") + egg_out

    # Abilities: species the dex has; a form it lacks that had the same abilities and level-up
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
            if r is None:  # Imperium's own ability: one of Heart & Soul's not in the list yet
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
    lines = ["// Generated by tools/crystal_imperium/imperium_species.py: Emerald Imperium's abilities (its",
             "// dex, DECISIONS.md D35, D45) where they differ from Heart & Soul's, and the Egg Move lists of",
             "// species Heart & Soul gave none. Included at the end of gSpeciesInfo",
             "// (src/data/pokemon/species_info.h): each line replaces one field of one species.",
             "// Edit the script, not this file.", ""]
    for num, (new, old) in sorted(new_abilities.items()):
        name = min((n for n in names_of[num]), key=lambda n: (n not in data, len(n)))
        lines.append(f"    [{name}].abilities = {{ {', '.join(new)} }}, // was {', '.join(a.replace('ABILITY_', '') for a in old)}")
    lines += egg_lines
    abilities_out = "\n".join(lines) + "\n"

    # TM and tutor compatibility: every move Imperium teaches by TM or tutor (its dex lists both as
    # one), and the ones each teachable learnset's Pokemon learn there. As for level-up learnsets, a
    # list gets the data of the first species using it that the dex has
    universe = sorted(set().union(*(d["teach"] for d in data.values())))
    teach_src = symbol_sources(table, consts, data, "teach")
    compiled = {info.get("teach") for info in table.values()}
    by_number = {}
    for sp in sorted(data, key=len):
        by_number.setdefault(consts.get(sp), sp)
    teach = {}
    for sp, sym in sorted(teachable_lists().items()):
        src = teach_src.get(sym)
        if src is None and sym not in compiled:  # a list this build compiles out (P_FUSION_FORMS): by its name
            src = sp if sp in data else by_number.get(consts.get(sp)) if sp in consts else None
        if src:
            teach[sp] = sorted(data[src]["teach"])
        else:
            notes.append(f"{sp}: no dex data, its TM and tutor moves stay the official ones")
    # A form that shares a list but that Imperium teaches more moves (Rotom's appliance forms, Origin
    # Dialga and Palkia) needs a list of its own (in species_info) to learn them
    for num in sorted(table):
        sym = table[num].get("teach")
        src = teach_src.get(sym)
        other = next((n for n in sorted(names_of[num], key=len) if n in data), None)
        if src and other and other != src and data[other]["teach"] - data[src]["teach"]:
            extra = ", ".join(m[5:] for m in sorted(data[other]["teach"] - data[src]["teach"]))
            notes.append(f"{other}: shares {src}'s TM and tutor list; Imperium also teaches it {extra}")
    teachables_out = render_teachables(universe, teach)

    # Base stats (D50): a species whose own name the dex has gets its six base stats; a form the dex
    # doesn't list keeps its own
    new_stats = {}
    for num, info in sorted(table.items()):
        if num == 0 or "stats" not in info:
            continue
        src = next((n for n in sorted(names_of[num], key=len) if n in data), None)
        if src and data[src]["stats"] != info["stats"]:
            new_stats[num] = (src, data[src]["stats"], info["stats"])
    lines = ["// Generated by tools/crystal_imperium/imperium_species.py: Emerald Imperium's base stats (its",
             "// dex, DECISIONS.md D50) where they differ from Heart & Soul's: its buffs. Included at the end",
             "// of gSpeciesInfo (src/data/pokemon/species_info.h), after imperium_abilities.h: each line",
             "// replaces the changed base stats of one species. Edit the script, not this file.", ""]
    for num, (name, new, old) in new_stats.items():
        fields = ", ".join(f"[{name}].{STAT_FIELDS[i]} = {new[i]}" for i in range(6) if new[i] != old[i])
        was = ", ".join(f"{STAT_NAMES[i]} {old[i]}" for i in range(6) if new[i] != old[i])
        lines.append(f"    {fields}, // was {was}; BST {sum(old)} -> {sum(new)}")
    stats_out = "\n".join(lines) + "\n"

    stats = {"level": len(level_src), "egg": len(egg_src), "abilities": len(new_abilities), "teach": len(teach),
             "stats": len(new_stats)}
    if report:
        print(f"dex species matched: {len(data)}; not in this game: {len(unmatched)}")
        print("  " + ", ".join(unmatched))
        print(f"learnsets from the dex: {stats['level']} level-up, {stats['egg']} Egg Move lists, "
              f"{stats['teach']} TM and tutor lists; {stats['abilities']} species with new abilities, "
              f"{stats['stats']} with new base stats")
        print("moves left out (not in this engine): " + ", ".join(f"{k} ({v})" for k, v in mp.missing_moves.most_common()))
        print("abilities kept as Heart & Soul's (Imperium's own, not in this engine): "
              + ", ".join(f"{k} ({v})" for k, v in mp.missing_abilities.most_common()))
        for n in notes:
            print(n)
    return {LEVEL_UP_OUT: level_out, EGG_OUT: egg_out, ABILITIES_OUT: abilities_out, STATS_OUT: stats_out,
            TEACHABLES_OUT: teachables_out}, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ei-dex", required=True, help="a saved copy of the Emerald Imperium dex's script (" + ei_dex.EI_DEX_URL + ")")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    ei, digest = ei_dex.load_ei(args.ei_dex)
    if digest != ei_dex.EI_DEX_SHA256:
        print(f"note: {args.ei_dex} has SHA-256 {digest}, not the {ei_dex.EI_DEX_SHA256} these files came from")
    files, stats = generate(ei, args.report)
    stale = [p for p, text in files.items() if not os.path.exists(os.path.join(ROOT, p)) or read(p) != text]
    if args.check:
        for p in stale:
            print(f"{p} is out of date: run tools/crystal_imperium/imperium_species.py")
        return 1 if stale else 0
    for p in stale:
        with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
            f.write(files[p])
        print(f"wrote {p}")
    print(f"{stats['level']} level-up learnsets, {stats['egg']} Egg Move lists and {stats['teach']} TM and tutor "
          f"lists from the Emerald Imperium dex; {stats['abilities']} species with new abilities, "
          f"{stats['stats']} with new base stats")
    return 0


if __name__ == "__main__":
    sys.exit(main())
