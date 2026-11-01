#!/usr/bin/env python3
"""Crystal Imperium's species, move and item data as the build compiles them: the build's own preprocessor
(the Makefile's CPP and flags for Heart & Soul) on src/pokemon.c, src/move.c and src/item.c, read from
gSpeciesInfo (with the designated overrides at its end applied: imperium_abilities.h, imperium_stats.h,
crystal_imperium_stats.h, imperium_evolutions.h), gMovesInfo and gItemsInfo. Every value is the one the game
uses: each evolution's method, parameter, target and conditions, base stats, types, abilities, the legendary
flags and the Mega Evolutions; moves' power, type, accuracy, category, priority, effect, flags and added
effects; items' hold effects. tools/crystal_imperium/validate.py checks the designed teams with it.

  python3 tools/crystal_imperium/species_db.py SPECIES_PUPITAR MOVE_U_TURN ITEM_EVIOLITE   # show them

The preprocessed text is about 13 MB and takes a few seconds to read; load() reads it once a process.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# The build's preprocessor and flags for Heart & Soul (Makefile: CPP, CPPFLAGS with GAME_VERSION POKEMON_HNS)
CPP = ["arm-none-eabi-cpp", "-P", "-iquote", "include", "-Wno-trigraphs", "-DMODERN=1", "-DTESTING=0",
       "-DPOKEMON_HNS", "-std=gnu17"]
STAT_FIELDS = {"baseHP": "HP", "baseAttack": "Atk", "baseDefense": "Def", "baseSpAttack": "SpA",
               "baseSpDefense": "SpD", "baseSpeed": "Spe"}
FLAGS = ("isLegendary", "isMythical", "isUltraBeast", "isParadox", "isSubLegendary", "isRestrictedLegendary",
         "isMegaEvolution", "isPrimalReversion", "isGigantamax", "isTotem", "isAlolanForm", "isGalarianForm",
         "isHisuianForm", "isPaldeanForm")
MOVE_FLAGS = ("multiHit", "makesContact", "soundMove", "punchingMove", "slicingMove", "bitingMove", "pulseMove", "windMove",
              "ballisticMove", "powderMove", "healingMove", "danceMove", "ignoresProtect", "alwaysHitsInRain",
              "alwaysHitsInHailSnow")
LEVEL_METHODS = ("EVO_LEVEL", "EVO_LEVEL_BATTLE_ONLY")
# GetTrainerEvolutionLevel (src/battle_main.c): an evolution by item, trade, friendship or a move, from here
TRAINER_OTHER_EVOLUTION_LEVEL = 32


def preprocess(path):
    return subprocess.run(CPP + [path], capture_output=True, text=True, cwd=ROOT, check=True).stdout


_BRACKETS = re.compile(r'[(){}\[\]"]')
_VALUE_END = re.compile(r'[(){}\[\],"]')
_FIELD = re.compile(r"\.(\w+)\s*=\s*")


def _string_end(text, j):
    """The index just past the string whose opening quote is at text[j - 1]."""
    while True:
        q = text.index('"', j)
        p = q - 1
        while text[p] == "\\":
            p -= 1
        if (q - 1 - p) % 2 == 0:
            return q + 1
        j = q + 1


def matching(text, start):
    """The index just past the bracket that closes the one at text[start] (strings skipped)."""
    depth, j = 0, start
    while True:
        m = _BRACKETS.search(text, j)
        if not m:
            raise ValueError("unbalanced brackets")
        c, j = m.group(0), m.end()
        if c == '"':
            j = _string_end(text, j)
        elif c in "({[":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                return j


def value_end(text, j):
    """The index of the top-level comma (or closing bracket) that ends the value starting at text[j]."""
    depth = 0
    while True:
        m = _VALUE_END.search(text, j)
        if not m:
            return len(text)
        c, j = m.group(0), m.end()
        if c == '"':
            j = _string_end(text, j)
        elif c in "({[":
            depth += 1
        elif c in ")}]":
            if depth == 0:
                return m.start()
            depth -= 1
        elif depth == 0:
            return m.start()


def c_value(expr):
    """A constant expression as the preprocessor leaves it (numbers, names, ?:, comparisons, + - * /, !,
    && and ||): an int, or a name (TYPE_FIRE) when it is one."""
    e = expr.strip()
    toks = re.findall(r"0x[0-9A-Fa-f]+|\d+|[A-Za-z_]\w*|\|\||&&|==|!=|<=|>=|<<|>>|[()?:<>+\-*/!|&~]", e)
    if "".join(toks) != re.sub(r"\s+", "", e):
        raise ValueError(f"not a constant: {expr!r}")
    pos = [0]

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
        if t == "~":
            return ~primary()
        if t in ("TRUE", "FALSE"):
            return int(t == "TRUE")
        if re.fullmatch(r"[A-Za-z_]\w*", t):
            return t
        return int(t, 0)

    ops = {"*": lambda a, b: a * b, "/": lambda a, b: a // b, "+": lambda a, b: a + b, "-": lambda a, b: a - b,
           "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b, "<": lambda a, b: int(a < b),
           "<=": lambda a, b: int(a <= b), ">": lambda a, b: int(a > b), ">=": lambda a, b: int(a >= b),
           "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b), "&": lambda a, b: a & b,
           "|": lambda a, b: a | b, "&&": lambda a, b: int(bool(a) and bool(b)),
           "||": lambda a, b: int(bool(a) or bool(b))}

    def level(names, sub):
        def parse():
            v = sub()
            while peek() in names:
                op = take()
                v = ops[op](v, sub())
            return v
        return parse

    lor = level({"||"}, level({"&&"}, level({"|"}, level({"&"}, level({"==", "!="}, level(
        {"<", "<=", ">", ">="}, level({"<<", ">>"}, level({"+", "-"}, level({"*", "/"}, primary)))))))))

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

    try:
        v = ternary()
    except (IndexError, TypeError, ZeroDivisionError):
        raise ValueError(f"not a constant: {expr!r}") from None
    if pos[0] != len(toks):
        raise ValueError(f"not a constant: {expr!r}")
    return v


def fields(block):
    """The top-level designated fields of an initializer's body, {name: text}."""
    out, i = {}, 0
    while True:
        m = _FIELD.search(block, i)
        if not m:
            return out
        j = value_end(block, m.end())
        out[m.group(1)] = block[m.end():j].strip()
        i = j + 1


def top_level_items(body):
    """The comma-separated items of a brace list's body, nested brackets kept whole."""
    out, depth, cur = [], 0, []
    for c in body:
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        if c == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


class Evolution:
    __slots__ = ("method", "param", "target", "conditions")

    def __init__(self, method, param, target, conditions):
        self.method, self.param, self.target, self.conditions = method, param, target, conditions

    @property
    def kind(self):
        """"level" for a level evolution (EVO_LEVEL above level 1), else what it needs: "friendship",
        "move", "held item", "item", "trade" or "other" (the trainer standard's terms)."""
        c = " ".join(self.conditions)
        if self.method in LEVEL_METHODS:
            if isinstance(self.param, int) and self.param > 1:
                return "level"
            if "FRIENDSHIP" in c:
                return "friendship"
            if "KNOWS_MOVE" in c or "USED_MOVE" in c:
                return "move"
            if "HOLD_ITEM" in c:
                return "held item"
            return "other"
        return {"EVO_ITEM": "item", "EVO_TRADE": "trade"}.get(self.method, "other")

    @property
    def trainer_level(self):
        """GetTrainerEvolutionLevel (src/battle_main.c): the level a trainer's Pokemon takes it at; 0 never."""
        if self.method in LEVEL_METHODS:
            return self.param if isinstance(self.param, int) and self.param > 1 else TRAINER_OTHER_EVOLUTION_LEVEL
        if self.method in ("EVO_ITEM", "EVO_TRADE"):
            return TRAINER_OTHER_EVOLUTION_LEVEL
        return 0

    def __repr__(self):
        return f"{self.method}({self.param}) -> {self.target}" + (f" if {self.conditions}" if self.conditions else "")


def parse_evolutions(lit, names):
    """[Evolution] from '(const struct Evolution[]) { {EVO_LEVEL, 16, 2}, ..., { 0xFFFF }, }'."""
    start = lit.find("{")
    body = lit[start + 1:matching(lit, start) - 1]
    out = []
    for item in top_level_items(body):
        item = item.strip()
        if not item.startswith("{"):
            continue
        inner = item[1:matching(item, 0) - 1]
        parts = top_level_items(inner)
        if not parts or parts[0] in ("0xFFFF", "EVOLUTIONS_END"):
            break
        conditions = []
        if len(parts) > 3:
            conditions = [re.sub(r"\s+", " ", c).strip() for c in re.findall(r"\{([^{}]*)\}", parts[3])
                          if "CONDITIONS_END" not in c]
        try:
            param = c_value(parts[1])
        except ValueError:
            param = parts[1]
        out.append(Evolution(parts[0], param, names.get(int(c_value(parts[2])), parts[2]), conditions))
    return out


def species_numbers():
    """{SPECIES_ constant: number} for every name in include/constants/species.h, aliases included."""
    with open(os.path.join(ROOT, "include", "constants", "species.h"), encoding="utf-8") as f:
        raw = dict(re.findall(r"(?m)^#define\s+(SPECIES_\w+)\s+(.+?)\s*(?://.*)?$", f.read()))
    out = {}

    def value(name, depth=0):
        if name in out:
            return out[name]
        text = raw.get(name)
        if text is None or depth > 20:
            return None
        expr = re.sub(r"SPECIES_\w+", lambda m: str(value(m.group(0), depth + 1)), text)
        try:
            v = c_value(expr)
        except ValueError:
            return None
        if isinstance(v, int):
            out[name] = v
        return out.get(name)

    for name in raw:
        value(name)
    return out


class DB:
    def __init__(self):
        numbers = species_numbers()
        # The name each number is defined with (not an alias such as SPECIES_MIMIKYU)
        with open(os.path.join(ROOT, "include", "constants", "species.h"), encoding="utf-8") as f:
            literal = {name for name, v in re.findall(r"(?m)^#define\s+(SPECIES_\w+)\s+(\S+)", f.read())
                       if not re.fullmatch(r"SPECIES_\w+", v)}
        self.names = {}
        for name, num in sorted(numbers.items(), key=lambda kv: (kv[0] not in literal, kv[0])):
            self.names.setdefault(num, name)
        self.numbers = numbers
        self.species = self._species(preprocess("src/pokemon.c"))
        self.moves = self._moves(preprocess("src/move.c"))
        self.items = self._items(preprocess("src/item.c"))
        self.mega = {}  # Mega Stone -> {species: its Mega}
        for name, sp in self.species.items():
            for item, target in sp["mega"]:
                self.mega.setdefault(item, {})[name] = target
        self.parents = {}
        for name, sp in self.species.items():
            for e in sp["evolutions"]:
                self.parents.setdefault(e.target, []).append((name, e))

    # ---- species
    def _species(self, pre):
        tables = {}
        for m in re.finditer(r"static const struct FormChange (\w+)\[\]\s*=\s*\{", pre):
            body = pre[m.end() - 1:matching(pre, m.end() - 1)]
            rows = [top_level_items(x) for x in re.findall(r"\{([^{}]*)\}", body)]
            tables[m.group(1)] = [r for r in rows if r and r[0] != "FORM_CHANGE_TERMINATOR"]
        i = pre.index("const struct SpeciesInfo gSpeciesInfo[] =")
        start = pre.index("{", i)
        table = pre[start + 1:matching(pre, start) - 1]
        out, last = {}, 0
        for m in re.finditer(r"\n    \[(\d+)\] =\s*\{", table):
            if m.start() < last:
                continue
            b0 = m.end() - 1
            b1 = matching(table, b0)
            num = int(m.group(1))
            out[num] = self._species_entry(num, fields(table[b0 + 1:b1 - 1]), tables)
            last = b1
        # The designated overrides after the entries ([N].field = value, ...)
        tail = table[last:]
        for m in re.finditer(r"\[(\d+)\]\.(\w+)\s*=\s*", tail):
            num, field = int(m.group(1)), m.group(2)
            value = tail[m.end():value_end(tail, m.end())].strip()
            if num in out:
                self._species_field(out[num], field, value, tables)
        named = {}
        for num, sp in out.items():
            if num in self.names:
                sp["name"] = self.names[num]
                named[sp["name"]] = sp
        return named

    def _species_entry(self, num, f, tables):
        sp = {"num": num, "base": {}, "types": [], "abilities": [], "evolutions": [], "flags": set(), "mega": [],
              "begin_battle": None, "display": ""}
        for field, value in f.items():
            self._species_field(sp, field, value, tables)
        return sp

    def _species_field(self, sp, field, value, tables):
        if field in STAT_FIELDS:
            sp["base"][STAT_FIELDS[field]] = c_value(value)
        elif field == "types":
            sp["types"] = list(dict.fromkeys(str(c_value(t)) for t in top_level_items(value.strip()[1:-1])))
        elif field == "abilities":
            sp["abilities"] = [str(c_value(a)) for a in top_level_items(value.strip()[1:-1])]
        elif field == "evolutions":
            sp["evolutions"] = parse_evolutions(value, self.names)
        elif field in FLAGS:
            if c_value(value):
                sp["flags"].add(field)
            else:
                sp["flags"].discard(field)
        elif field == "speciesName":
            m = re.search(r'_\("([^"]*)"\)', value)
            sp["display"] = m.group(1) if m else ""
        elif field == "formChangeTable":
            sp["mega"], sp["begin_battle"] = [], None
            for row in tables.get(value.strip(), []):
                if row[0] in ("FORM_CHANGE_BATTLE_MEGA_EVOLUTION_ITEM", "FORM_CHANGE_BATTLE_PRIMAL_REVERSION") and len(row) > 2:
                    sp["mega"].append((row[2], self.names.get(int(c_value(row[1])), row[1])))
                elif row[0] == "FORM_CHANGE_BEGIN_BATTLE":
                    sp["begin_battle"] = (self.names.get(int(c_value(row[1])), row[1]), row[2] if len(row) > 2 else None)

    def get(self, species):
        """A species' data by its constant, aliases resolved (SPECIES_MIMIKYU is SPECIES_MIMIKYU_DISGUISED)."""
        num = self.numbers.get(species)
        return self.species.get(self.names.get(num)) if num is not None else None

    def canonical(self, species):
        num = self.numbers.get(species)
        return self.names.get(num, species) if num is not None else species

    def evolutions(self, species):
        sp = self.get(species)
        return [e for e in (sp["evolutions"] if sp else []) if e.target in self.species and e.method != "EVO_SPLIT_FROM_EVO"]

    def reach_level(self, species, depth=0):
        """The lowest level at which the species exists by level-up from its base form: the highest level
        evolution on its line (an item, trade, friendship or move step adds nothing)."""
        best = None
        for parent, e in self.parents.get(self.canonical(species), []):
            if depth > 6:
                break
            lv = self.reach_level(parent, depth + 1)
            if e.kind == "level":
                lv = max(lv, e.param)
            best = lv if best is None else min(best, lv)
        return best or 1

    def final_forms(self, species, level=None, depth=0):
        """The most evolved forms the species could be at this level: an item, trade, friendship or move step
        always, a level step only when due (every level step with level None)."""
        out = []
        for e in self.evolutions(species):
            if e.kind == "level" and level is not None and e.param > level:
                continue
            for f in (self.final_forms(e.target, level, depth + 1) if depth < 4 else []) or [e.target]:
                if f not in out:
                    out.append(f)
        return out

    def legend_kind(self, species):
        flags = (self.get(species) or {}).get("flags", set())
        for f in ("isRestrictedLegendary", "isMythical", "isUltraBeast", "isParadox", "isSubLegendary", "isLegendary"):
            if f in flags:
                return f[2:]
        return None

    # ---- moves
    def _moves(self, pre):
        i = re.search(r"(?m)^const struct MoveInfo gMovesInfo\[[^\]]*\]\s*=", pre).end()
        start = pre.index("{", i)
        table = pre[start + 1:matching(pre, start) - 1]
        out, last = {}, 0
        for m in re.finditer(r"\[(MOVE_\w+)\]\s*=\s*\{", table):
            if m.start() < last:
                continue
            b0 = m.end() - 1
            b1 = matching(table, b0)
            f = fields(table[b0 + 1:b1 - 1])
            last = b1
            mv = {"name": m.group(1), "flags": set(), "effects": []}
            mm = re.search(r'_\("([^"]*)"\)', f.get("name", ""))
            mv["display"] = mm.group(1) if mm else m.group(1)
            for key in ("effect", "type", "category", "target"):
                mv[key] = str(c_value(f[key])) if key in f else None
            for key in ("power", "accuracy", "priority", "strikeCount", "criticalHitStage", "recoil", "pp"):
                try:
                    mv[key] = c_value(f[key]) if key in f else 0
                except ValueError:
                    mv[key] = 0
            mv["argument"] = f.get("argument", "")
            for key in MOVE_FLAGS:
                if key in f:
                    try:
                        if c_value(f[key]):
                            mv["flags"].add(key)
                    except ValueError:
                        pass
            if "additionalEffects" in f:
                for eff in re.findall(r"\{([^{}]*)\}", f["additionalEffects"]):
                    ef = fields(eff)
                    if "moveEffect" not in ef:
                        continue
                    try:
                        chance = c_value(ef.get("chance", "0"))
                    except ValueError:
                        chance = 0
                    mv["effects"].append({"effect": ef["moveEffect"].strip(), "chance": chance,
                                          "self": bool(c_value(ef["self"])) if "self" in ef else False})
            out[m.group(1)] = mv
        with open(os.path.join(ROOT, "include", "constants", "moves.h"), encoding="utf-8") as f:
            self.move_aliases = dict(re.findall(r"(?m)^\s*(MOVE_\w+)\s*=\s*(MOVE_\w+)\s*,", f.read()))
        return out

    def move(self, constant):
        constant = self.move_aliases.get(constant, constant)
        return self.moves.get(constant)

    # ---- items
    def _items(self, pre):
        i = pre.index("gItemsInfo[] =")
        start = pre.index("{", i)
        table = pre[start + 1:matching(pre, start) - 1]
        out, last = {}, 0
        for m in re.finditer(r"\[(ITEM_\w+)\]\s*=\s*\{", table):
            if m.start() < last:
                continue
            b0 = m.end() - 1
            b1 = matching(table, b0)
            f = fields(table[b0 + 1:b1 - 1])
            last = b1
            it = {"name": m.group(1)}
            it["hold_effect"] = str(c_value(f["holdEffect"])) if "holdEffect" in f else "HOLD_EFFECT_NONE"
            for key in ("holdEffectParam", "secondaryId"):
                try:
                    it[key] = c_value(f[key]) if key in f else 0
                except ValueError:
                    it[key] = f[key]
            it["pocket"] = f.get("pocket", "")
            out[m.group(1)] = it
        return out

    def item(self, constant):
        return self.items.get(constant)


_db = None


def load():
    """The build's data, read once a process."""
    global _db
    if _db is None:
        _db = DB()
    return _db


def main():
    db = load()
    print(f"{len(db.species)} species ({sum(1 for s in db.species.values() if s['evolutions'])} with evolutions), "
          f"{len(db.moves)} moves, {len(db.items)} items, {len(db.mega)} Mega Stones")
    for name in sys.argv[1:]:
        if name.startswith("SPECIES_"):
            sp = db.get(name)
            print(name, {k: v for k, v in sp.items() if k != "evolutions"} if sp else None)
            if sp:
                print("  evolutions:", db.evolutions(name), " reach level:", db.reach_level(name))
        elif name.startswith("MOVE_"):
            print(name, db.move(name))
        elif name.startswith("ITEM_"):
            print(name, db.item(name))


if __name__ == "__main__":
    main()
