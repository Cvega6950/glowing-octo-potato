#!/usr/bin/env python3
"""Crystal Imperium: Emerald Imperium's evolution methods (DECISIONS.md D44).

Emerald Imperium's evolutions are Radical Red's: its developer answers "most evolutions are the same
as RR, so you can use RR Dex", and its changelogs fix a few to "match RR data". This script reads the
Radical Red dex's data file (the one imperium_species.py reads, RR_DATA_URL) and writes

  src/data/pokemon/species_info/imperium_evolutions.h   the evolutions that differ from Heart & Soul's,
                                                        as overrides of the species table

  python3 tools/crystal_imperium/imperium_evolutions.py --rr-data PATH           # rewrite the file
  python3 tools/crystal_imperium/imperium_evolutions.py --rr-data PATH --check   # exit 1 if out of date
  python3 tools/crystal_imperium/imperium_evolutions.py --rr-data PATH --report  # every change, readable

Each species takes Radical Red's methods in place of Heart & Soul's (the user chose "only Imperium's
ways"), ordinary levels included. Kept from Heart & Soul, because no Radical Red method reaches them:
the Alcremie flavours (stones and spins), Bloodmoon Ursaluna (a Peat Block at night in the Mt. Moon
area or in Sinjoh), Three-Segment Dudunsparce and the Family of Three (1 in 100, by personality value,
on each of Radical Red's methods) and Own Tempo Rockruff's Dusk Lycanroc. Imperium's own fixes on top
of Radical Red's data: White-Striped Basculin evolves like the other two stripes (changelog 1.2), and
Porygon also evolves with an Up-Grade, which Imperium's evolution shop sells (no other evolution uses
one). Radical Red's Link Cable is this engine's Linking Cord. Its "day" is "not at night" here
(6:00-18:59), its night 19:00-5:59 and its dusk the evening (18:00-18:59).

Radical Red lists some forms as several entries under one name (the three Burmy, both Shellos, the four
Deerling and Pumpkaboo); they are matched to this game's forms in order. A form Radical Red doesn't
list (the Vivillon patterns, Flabebe's colours, White-Striped Basculin...) takes its base form's
methods, each evolving into its own form.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import imperium_species as isp  # noqa: E402  (Radical Red's data, the species table)

OUT = "src/data/pokemon/species_info/imperium_evolutions.h"

ITEM_ALIASES = {"ThunderStone": "ITEM_THUNDER_STONE", "Link Cable": "ITEM_LINKING_CORD", "Up-Grade": "ITEM_UPGRADE"}
FRIENDSHIP = ("IF_MIN_FRIENDSHIP", "FRIENDSHIP_EVO_THRESHOLD")
NIGHT = ("IF_TIME", "TIME_NIGHT")
NOT_NIGHT = ("IF_NOT_TIME", "TIME_NIGHT")
EVENING = ("IF_TIME", "TIME_EVENING")
TIME_RANGES = {1041: NOT_NIGHT, 5144: NIGHT, 4372: EVENING}  # Radical Red's day, night and dusk


# --- The species table as Heart & Soul compiles it ----------------------------------------------------

def split_top(text, sep=","):
    """Split on sep outside (), {} and []."""
    out, depth, cur = [], 0, []
    for c in text:
        if c in "({[":
            depth += 1
        elif c in ")}]":
            depth -= 1
        if c == sep and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def braced_items(text):
    """The top-level {...} items inside text (which starts at a '{')."""
    items, i = [], 1
    while i < len(text):
        if text[i] == "{":
            j = isp.matching_brace(text, i)
            items.append(text[i + 1:j - 1].strip())
            i = j
        else:
            i += 1
    return items


class Game:
    def __init__(self):
        pre = isp.preprocessed_pokemon_c()
        self.consts = isp.species_constants()
        self.table = isp.species_table(pre)
        self.forms = isp.form_tables(pre)
        self.weather = {int(v): k for k, v in re.findall(r"#define\s+(WEATHER_\w+)\s+(\d+)",
                                                          isp.read("include/constants/weather.h"))}
        self.items = set(re.findall(r"^\s*(ITEM_\w+)\s*=", isp.read("include/constants/items.h"), re.M))
        self.names = self.canonical_names()
        self.evos = self.base_evolutions(pre)

    def canonical_names(self):
        """number -> the SPECIES_ name the species table uses for it."""
        names = {}
        for path in sorted(os.listdir(os.path.join(isp.ROOT, "src/data/pokemon/species_info"))):
            if not path.endswith("_families.h"):
                continue
            text = isp.read("src/data/pokemon/species_info/" + path)
            for name in re.findall(r"(?m)^\s*\[(SPECIES_\w+)\]\s*=", text):
                if name in self.consts:
                    names.setdefault(self.consts[name], name)
        return names

    def name(self, num):
        return self.names.get(num) or min((k for k, v in self.consts.items() if v == num), key=len)

    def base_evolutions(self, pre):
        """number -> [route]: each species' evolutions as compiled, without this script's overrides."""
        m = re.search(r"gSpeciesInfo\[\]\s*=\s*\{", pre)
        body = pre[m.end() - 1:isp.matching_brace(pre, m.end() - 1)]
        entry = re.compile(r"\[\s*\(?\s*(\d+)\s*\)?\s*\]\s*=\s*\{")
        evos, pos = {}, 0
        while True:
            m = entry.search(body, pos)
            if not m:
                break
            start = m.end() - 1
            end = isp.matching_brace(body, start)
            block = body[start:end]
            em = re.search(r"\.evolutions\s*=\s*\(const struct Evolution\[\]\)\s*\{", block)
            if em:
                lit = block[em.end() - 1:isp.matching_brace(block, em.end() - 1)]
                routes = [self.parse_route(it) for it in braced_items(lit)]
                evos[int(m.group(1))] = [r for r in routes if r]
            pos = end
        return evos

    def parse_route(self, text):
        parts = split_top(text)
        if not parts[0].startswith("EVO_") or parts[0] == "EVO_NONE":
            return None  # EVOLUTIONS_END, and EVO_NONE (a breeding hint, not an evolution)
        conds = []
        if len(parts) > 3:
            lit = parts[3][parts[3].index("{"):]
            for c in braced_items(lit):
                args = split_top(c)
                if args[0] != "CONDITIONS_END":
                    conds.append(self.norm_cond(args))
        param = parts[1]
        if parts[0] == "EVO_SPLIT_FROM_EVO":
            param = int(param)
        return (parts[0], param, int(parts[2]), tuple(conds))

    def norm_cond(self, args):
        name, rest = args[0], args[1:]
        if name == "IF_MIN_FRIENDSHIP" and rest and "220" in rest[0]:
            rest = ["FRIENDSHIP_EVO_THRESHOLD"]
        elif name == "IF_GENDER":
            rest = ["MON_MALE" if int(rest[0], 0) == 0 else "MON_FEMALE"]
        elif name == "IF_WEATHER":
            rest = [self.weather[int(rest[0])]]
        elif name in ("IF_SPECIES_IN_PARTY", "IF_TRADE_PARTNER_SPECIES", "IF_DEFEAT_X_WITH_ITEMS"):
            rest = [self.name(int(rest[0]))] + list(rest[1:])
        return tuple([name] + [str(a) for a in rest])

    def base(self, num):
        """The first species of num's form table (its base form)."""
        sym = self.table.get(num, {}).get("forms")
        return self.forms[sym][0] if sym in self.forms else num

    def form_list(self, num):
        sym = self.table.get(num, {}).get("forms")
        return self.forms.get(sym, [num])


# --- Radical Red's evolutions in this engine's terms --------------------------------------------------

class Translator:
    def __init__(self, rr, game):
        self.rr = rr
        self.game = game
        self.mp = isp.Mapper(rr)

    def species_num(self, rr_id):
        s = self.rr["species"].get(rr_id)
        const = self.mp.species(s) if s else None
        return self.game.consts[const] if const else None

    def item(self, item_id):
        name = self.rr["items"][item_id]["name"]
        const = ITEM_ALIASES.get(name, isp.constify(name, "ITEM_"))
        if const not in self.game.items:
            sys.exit(f"Radical Red's evolution item {name} has no constant here ({const})")
        return const

    def type(self, type_id):
        return "TYPE_" + self.rr["types"][type_id]["name"].upper()

    def routes(self, rr_species):
        """Radical Red's evolutions of one species as routes (method, param, target, conditions)."""
        out = []
        for method, p, tgt, x in rr_species.get("evolutions", []):
            if method in (253, 254):
                continue  # Mega Evolution and Gigantamax, not evolutions
            target = self.species_num(tgt)
            if target is None:
                continue  # one of Radical Red's own forms
            out.append(self.route(method, p, target, x))
        return out

    def route(self, method, p, target, x):
        if method == 1:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP,))
        if method == 2:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, NOT_NIGHT))
        if method == 3:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, NIGHT))
        if method == 4 or method == 13:
            return ("EVO_LEVEL", str(p), target, ())
        if method == 7:
            item = self.item(p)
            if item == "ITEM_DAWN_STONE":  # Radical Red's Dawn Stone routes are Gallade's and Froslass's
                return ("EVO_ITEM", item, target, (("IF_GENDER", "MON_FEMALE" if x == 254 else "MON_MALE"),))
            return ("EVO_ITEM", item, target, ())
        if method in (8, 9, 10):
            return ("EVO_LEVEL", str(p), target, ({8: "IF_ATK_GT_DEF", 9: "IF_ATK_EQ_DEF", 10: "IF_ATK_LT_DEF"}[method],))
        if method in (11, 12):  # Wurmple: Heart & Soul's personality split, as Radical Red's 50%
            cond = ("IF_PID_UPPER_MODULO_10_GT", "4") if method == 11 else ("IF_PID_UPPER_MODULO_10_LT", "5")
            return ("EVO_LEVEL", str(p), target, (cond,))
        if method == 14:  # Shedinja: a free party slot and a Poke Ball, when Nincada becomes Ninjask
            return ("EVO_SPLIT_FROM_EVO", self.game.consts["SPECIES_NINJASK"], target,
                    (("IF_BAG_ITEM_COUNT", "ITEM_POKE_BALL", "1"),))
        if method == 16:  # rain in the overworld; Heart & Soul's fog route stays with it (see below)
            return ("EVO_LEVEL", str(p), target, (("IF_WEATHER", "WEATHER_RAIN"),))
        if method == 17:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, ("IF_KNOWS_MOVE_TYPE", self.type(p))))
        if method == 18:
            return ("EVO_LEVEL", str(p), target, (("IF_TYPE_IN_PARTY", self.type(x)),))
        if method in (20, 21):
            return ("EVO_LEVEL", str(p), target, (("IF_GENDER", "MON_MALE" if method == 20 else "MON_FEMALE"),))
        if method in (22, 23):
            return ("EVO_LEVEL", str(p), target, (NIGHT if method == 22 else NOT_NIGHT,))
        if method == 26:
            move = self.mp.move(p)
            if move is None:
                sys.exit(f"Radical Red's evolution move {self.rr['moves'][p]['name']} isn't in this engine")
            return ("EVO_LEVEL", "0", target, (("IF_KNOWS_MOVE", move),))
        if method == 27:
            return ("EVO_LEVEL", "0", target, (("IF_SPECIES_IN_PARTY", self.game.name(self.species_num(p))),))
        if method == 28:
            return ("EVO_LEVEL", str(p), target, (TIME_RANGES[x],))
        if method in (30, 31):
            return ("EVO_LEVEL", str(p), target, ("IF_AMPED_NATURE" if method == 30 else "IF_LOW_KEY_NATURE",))
        sys.exit(f"unknown Radical Red evolution method {method}")


def norm(route):
    """Conditions as tuples, so that ('IF_ATK_GT_DEF',) and 'IF_ATK_GT_DEF' compare equal."""
    method, param, target, conds = route
    return (method, param, target, tuple(c if isinstance(c, tuple) else (c,) for c in conds))


def plan(rr, game):
    """number -> (old routes, new routes) for every species whose evolutions change."""
    tr = Translator(rr, game)
    by_num = {}  # number -> [Radical Red species], in Radical Red's order
    for s in sorted(rr["species"].values(), key=lambda s: s["ID"]):
        const = tr.mp.species(s)
        if const:
            by_num.setdefault(game.consts[const], []).append(s)

    # Radical Red's routes for each of this game's species: duplicates (one name, several forms) in
    # form-table order, other forms from their base form
    rr_routes = {}
    for num, entries in by_num.items():
        forms = [f for f in game.form_list(num) if f not in by_num or f == num]
        if len(entries) > 1 and len(entries) <= len(forms):
            for form, s in zip(forms, entries):
                rr_routes[form] = tr.routes(s)
        else:
            rr_routes[num] = tr.routes(entries[0])
    for num in game.evos:
        if num not in rr_routes and game.base(num) in rr_routes and game.evos[num]:
            rr_routes[num] = list(rr_routes[game.base(num)])

    changes = {}
    for num, routes in sorted(rr_routes.items()):
        old = [norm(r) for r in game.evos.get(num, [])]
        if not routes and old:
            continue  # Radical Red lists the species without its evolutions: keep Heart & Soul's
        new = adapt(num, [norm(r) for r in routes], old, game)
        if sorted(map(repr, new)) != sorted(map(repr, old)):  # the same routes in another order: no change
            changes[num] = (old, new)
    return changes


def adapt(num, new, old, game):
    """This game's forms for Radical Red's targets, then what Heart & Soul keeps."""
    name = game.name(num)
    old_targets = {r[2] for r in old}
    fixed = []
    for method, param, target, conds in new:
        if target not in old_targets:
            same_base = {t for t in old_targets if game.base(t) == game.base(target)}
            if len(same_base) == 1:
                target = same_base.pop()  # the matching form: Burmy Sandy's Mothim is Sandy Mothim
        fixed.append((method, param, target, conds))
    new = fixed

    if name in ("SPECIES_DUNSPARCE", "SPECIES_TANDEMAUS"):
        # Each of Radical Red's routes splits by personality value like Heart & Soul's: 1 in 100
        # Three-Segment Dudunsparce, or the Family of Three
        split = [(r[2], r[3][-1]) for r in old]  # (form, its IF_PID_MODULO_100 condition)
        new = [(m, p, form, conds + (pid,)) for m, p, _, conds in new for form, pid in split]
    if name == "SPECIES_URSARING":
        # Bloodmoon Ursaluna: Heart & Soul's Peat Block at night in the Mt. Moon area or in Sinjoh
        new += [r for r in old if game.name(r[2]) == "SPECIES_URSALUNA_BLOODMOON"]
    if name == "SPECIES_MILCERY":
        # The other flavours: Heart & Soul's stones and spins (Radical Red's Shiny Stone is among them)
        new += [r for r in old if r not in new]
    if name == "SPECIES_ROCKRUFF_OWN_TEMPO":
        new = old  # Dusk Lycanroc in the evening, as Radical Red's Rockruff
    if name == "SPECIES_PORYGON":
        new.append(("EVO_ITEM", "ITEM_UPGRADE", game.consts["SPECIES_PORYGON2"], ()))
    for r in old:
        # Goodra: rain or fog, as Heart & Soul (Radical Red's dex calls it overworld rain)
        if ("IF_WEATHER", "WEATHER_FOG") in r[3] and any(("IF_WEATHER", "WEATHER_RAIN") in n[3] for n in new):
            new.append(r)
    # First match wins: Sylveon before Espeon and Umbreon, Dusk Lycanroc before Midday
    new.sort(key=lambda r: 0 if r[0] == "EVO_LEVEL" and any(c[0] == "IF_KNOWS_MOVE_TYPE" or c == EVENING
                                                            for c in r[3]) else 1)
    return new


# --- Output -------------------------------------------------------------------------------------------

def render_route(route, game):
    method, param, target, conds = route
    if method == "EVO_SPLIT_FROM_EVO":
        param = game.name(param)
    text = f"{{{method}, {param}, {game.name(target)}"
    if conds:
        text += ", CONDITIONS(" + ", ".join("{" + ", ".join(c) + "}" for c in conds) + ")"
    return text + "}"


ITEM_WORDS = {"ITEM_LINKING_CORD": "Linking Cord", "ITEM_UPGRADE": "Up-Grade", "ITEM_KINGS_ROCK": "King's Rock"}
COND_WORDS = {
    "IF_MIN_FRIENDSHIP": lambda a: "friendship",
    "IF_TIME": lambda a: {"TIME_NIGHT": "at night", "TIME_EVENING": "in the evening", "TIME_DAY": "by day"}[a[0]],
    "IF_NOT_TIME": lambda a: "not at night" if a[0] == "TIME_NIGHT" else "not " + a[0],
    "IF_GENDER": lambda a: "male" if a[0] == "MON_MALE" else "female",
    "IF_KNOWS_MOVE": lambda a: "knowing " + words(a[0], "MOVE_"),
    "IF_KNOWS_MOVE_TYPE": lambda a: "knowing a " + words(a[0], "TYPE_") + " move",
    "IF_SPECIES_IN_PARTY": lambda a: "with " + words(a[0], "SPECIES_") + " in the party",
    "IF_TYPE_IN_PARTY": lambda a: "with a " + words(a[0], "TYPE_") + " type in the party",
    "IF_HOLD_ITEM": lambda a: "holding " + item_words(a[0]),
    "IF_IN_MAPSEC": lambda a: "in " + words(a[0], "MAPSEC_"),
    "IF_IN_MAP": lambda a: "in " + words(a[0], "MAP_"),
    "IF_REGION": lambda a: "in " + words(a[0], "REGION_"),
    "IF_NOT_REGION": lambda a: "outside " + words(a[0], "REGION_"),
    "IF_WEATHER": lambda a: "in " + words(a[0], "WEATHER_"),
    "IF_BAG_ITEM_COUNT": lambda a: f"{a[1]} {item_words(a[0])} in the Bag",
}


def words(const, prefix):
    return const[len(prefix):].replace("_", " ").title() if const.startswith(prefix) else const


def item_words(const):
    return ITEM_WORDS.get(const, words(const, "ITEM_"))


def describe(route, game):
    method, param, target, conds = route
    if method == "EVO_ITEM":
        head = item_words(param)
    elif method == "EVO_TRADE":
        head = "trade"
    elif method in ("EVO_LEVEL", "EVO_LEVEL_BATTLE_ONLY"):
        head = f"level {param}" if param != "0" else "level up"
        if method == "EVO_LEVEL_BATTLE_ONLY":
            head += " in battle"
    elif method == "EVO_SPLIT_FROM_EVO":
        head = "with Ninjask"
    else:
        head = words(method, "EVO_").lower() + (f" {param}" if param not in ("0", 0) else "")
    parts = [head]
    for c in conds:
        fn = COND_WORDS.get(c[0])
        parts.append(fn(c[1:]) if fn else words(c[0], "IF_").lower() + (" " + " ".join(c[1:]) if c[1:] else ""))
    return ", ".join(parts) + " -> " + words(game.name(target), "SPECIES_")


def generate(rr, game):
    changes = plan(rr, game)
    lines = ["// Generated by tools/crystal_imperium/imperium_evolutions.py: Emerald Imperium's evolution methods",
             "// (Radical Red's, DECISIONS.md D44) where they differ from Heart & Soul's. Included at the end of",
             "// gSpeciesInfo (src/data/pokemon/species_info.h): each line replaces one species' evolutions.",
             "// Edit the script, not this file.",
             ""]
    for num, (old, new) in changes.items():
        was = "; ".join(describe(r, game) for r in old) or "no evolution"
        routes = ",\n        ".join(render_route(r, game) for r in new)
        lines.append(f"    // was: {was}")
        lines.append(f"    [{game.name(num)}].evolutions = EVOLUTION({routes}),")
    return "\n".join(lines) + "\n", changes


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rr-data", required=True, help="the Radical Red dex's data.js")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    rr, digest = isp.load_rr(args.rr_data)
    if digest != isp.RR_DATA_SHA256:
        sys.exit(f"{args.rr_data} isn't the data file these files came from (SHA-256 {digest})")
    game = Game()
    text, changes = generate(rr, game)
    if args.report:
        for num, (old, new) in changes.items():
            print(words(game.name(num), "SPECIES_"))
            print("   old: " + ("; ".join(describe(r, game) for r in old) or "no evolution"))
            print("   new: " + "; ".join(describe(r, game) for r in new))
        print(f"{len(changes)} species change")
        return
    path = os.path.join(isp.ROOT, OUT)
    current = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if args.check:
        if current != text:
            sys.exit(f"{OUT} is out of date: run tools/crystal_imperium/imperium_evolutions.py")
        print(f"{OUT} is up to date ({len(changes)} species)")
        return
    if current != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    print(f"wrote {OUT}: {len(changes)} species")


if __name__ == "__main__":
    main()
