#!/usr/bin/env python3
"""Crystal Imperium: Emerald Imperium's evolution methods (DECISIONS.md D44, D45).

This script reads the official Emerald Imperium dex (ei_dex.py: the dex's page script, EI_DEX_URL) and
writes

  src/data/pokemon/species_info/imperium_evolutions.h   the evolutions that differ from Heart & Soul's,
                                                        as overrides of the species table

  python3 tools/crystal_imperium/imperium_evolutions.py --ei-dex PATH           # rewrite the file
  python3 tools/crystal_imperium/imperium_evolutions.py --ei-dex PATH --check   # exit 1 if out of date
  python3 tools/crystal_imperium/imperium_evolutions.py --ei-dex PATH --report  # every change, readable

Each species takes Imperium's methods in place of Heart & Soul's (the user chose "only Imperium's
ways"), ordinary levels included; its trade routes stay beside its items, as in Imperium. Imperium's
changelog fix on top of the dex's data: Tandemaus evolves without a battle (1.2). Kept from Heart &
Soul: the Alcremie flavours other than Vanilla Cream (Imperium's nine Shiny Stone routes give Vanilla
Cream only), and the places for Magnezone and Vikavolt (Route 10, the Power Plant), standing in for
Imperium's Hoenn one. Its "day" is "not at night" here (6:00-18:59), its night 19:00-5:59 and its dusk
the evening (18:00-18:59). A form the dex lacks takes its base form's methods, evolving into its own
form; a species the dex lists without evolutions keeps Heart & Soul's.

Until 0.15.0's first build the data was the Radical Red dex's, which Imperium's documentation sends
players to; its own dex differs in some places (D45).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ei_dex  # noqa: E402  (the official Emerald Imperium dex's data)
import imperium_species as isp  # noqa: E402  (its mapping onto this engine, the species table)

OUT = "src/data/pokemon/species_info/imperium_evolutions.h"

FRIENDSHIP = ("IF_MIN_FRIENDSHIP", "FRIENDSHIP_EVO_THRESHOLD")
NIGHT = ("IF_TIME", "TIME_NIGHT")
NOT_NIGHT = ("IF_NOT_TIME", "TIME_NIGHT")
EVENING = ("IF_TIME", "TIME_EVENING")


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


# --- Imperium's evolutions in this engine's terms -----------------------------------------------------

PLACE = "PLACE"  # Imperium's "level up in a place" (Hoenn's): Heart & Soul's places for it stay (adapt)


class Translator:
    def __init__(self, ei, game):
        self.ei = ei
        self.game = game
        self.mp = isp.Mapper(ei)

    def species_num(self, sid):
        const = self.mp.species_by_id(sid)
        return self.game.consts[const] if const else None

    def item(self, item_id):
        const = self.mp.item(item_id)
        if const is None:
            sys.exit(f"Imperium's evolution item {self.ei['items'][item_id]['Name']} has no constant here")
        return const

    def move(self, move_id):
        const = self.mp.move(move_id)
        if const is None:
            sys.exit(f"Imperium's evolution move {self.ei['moves'][move_id]['name']} isn't in this engine")
        return const

    def routes(self, s):
        """The dex's evolutions of one species, [method, target, parameter], as routes (method, param,
        target, conditions)."""
        out = []
        for method, tgt, p in s.get("evolutions") or []:
            if method == 0:
                continue  # EVO_NONE: a Totem form, not an evolution
            target = self.species_num(tgt)
            if target is None:
                continue  # one of Imperium's own forms
            out.append(self.route(method, p, target))
        return out

    def route(self, method, p, target):
        lv = str(p)
        if method == 1:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP,))
        if method == 2:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, NOT_NIGHT))
        if method == 3:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, NIGHT))
        if method in (4, 13):  # 13: Nincada into Ninjask; Imperium has no Shedinja route (14)
            return ("EVO_LEVEL", lv, target, ())
        if method == 5:
            return ("EVO_TRADE", "0", target, ())
        if method == 6:
            return ("EVO_TRADE", "0", target, (("IF_HOLD_ITEM", self.item(p)),))
        if method == 7:
            return ("EVO_ITEM", self.item(p), target, ())
        if method in (8, 9, 10):
            return ("EVO_LEVEL", lv, target, ({8: "IF_ATK_GT_DEF", 9: "IF_ATK_EQ_DEF", 10: "IF_ATK_LT_DEF"}[method],))
        if method in (11, 12):  # Wurmple: Heart & Soul's personality split
            cond = ("IF_PID_UPPER_MODULO_10_GT", "4") if method == 11 else ("IF_PID_UPPER_MODULO_10_LT", "5")
            return ("EVO_LEVEL", lv, target, (cond,))
        if method == 15:
            return ("EVO_LEVEL", "0", target, (("IF_MIN_BEAUTY", lv),))
        if method in (16, 17):
            return ("EVO_LEVEL", lv, target, (("IF_GENDER", "MON_FEMALE" if method == 16 else "MON_MALE"),))
        if method in (18, 19, 20):
            return ("EVO_LEVEL", lv, target, ({18: NIGHT, 19: NOT_NIGHT, 20: EVENING}[method],))
        if method in (21, 22):
            return ("EVO_LEVEL", "0", target, (("IF_HOLD_ITEM", self.item(p)), NOT_NIGHT if method == 21 else NIGHT))
        if method == 23:
            return ("EVO_LEVEL", "0", target, (("IF_KNOWS_MOVE", self.move(p)),))
        if method == 24:
            return ("EVO_LEVEL", "0", target, (FRIENDSHIP, ("IF_KNOWS_MOVE_TYPE", self.mp.type(p))))
        if method == 25:
            return (PLACE, "0", target, ())
        if method in (26, 27):
            return ("EVO_ITEM", self.item(p), target, (("IF_GENDER", "MON_MALE" if method == 26 else "MON_FEMALE"),))
        if method in (28, 42):
            return ("EVO_LEVEL", lv, target, (("IF_WEATHER", "WEATHER_RAIN" if method == 28 else "WEATHER_FOG"),))
        if method == 29:
            return ("EVO_LEVEL", "0", target, (("IF_SPECIES_IN_PARTY", self.game.name(self.species_num(p))),))
        if method == 30:
            return ("EVO_LEVEL", lv, target, (("IF_TYPE_IN_PARTY", "TYPE_DARK"),))
        if method == 31:
            return ("EVO_TRADE", "0", target, (("IF_TRADE_PARTNER_SPECIES", self.game.name(self.species_num(p))),))
        if method in (33, 34):
            return ("EVO_LEVEL", lv, target, ("IF_AMPED_NATURE" if method == 33 else "IF_LOW_KEY_NATURE",))
        if method in (43, 44):
            pid = ("IF_PID_MODULO_100_GT", "0") if method == 43 else ("IF_PID_MODULO_100_EQ", "0")
            return ("EVO_LEVEL", "0", target, (("IF_KNOWS_MOVE", self.move(p)), pid))
        if method in (45, 46):  # Imperium 1.2: "no longer require leveling up in battle"
            pid = ("IF_PID_MODULO_100_EQ", "0") if method == 45 else ("IF_PID_MODULO_100_GT", "0")
            return ("EVO_LEVEL", lv, target, (pid,))
        sys.exit(f"Imperium evolution method {method} ({ei_dex.EI_METHODS.get(method)}) has no translation here")


def norm(route):
    """Conditions as tuples, so that ('IF_ATK_GT_DEF',) and 'IF_ATK_GT_DEF' compare equal."""
    method, param, target, conds = route
    return (method, param, target, tuple(c if isinstance(c, tuple) else (c,) for c in conds))


def plan(ei, game):
    """number -> (old routes, new routes) for every species whose evolutions change."""
    tr = Translator(ei, game)
    ei_routes = {}  # number -> Imperium's routes; the dex has one entry for each form
    for sid, s in sorted(ei["species"].items()):
        const = tr.mp.species(s)
        if const:
            ei_routes.setdefault(game.consts[const], tr.routes(s))
    for num in game.evos:  # a form the dex lacks takes its base form's routes, into its own form (adapt)
        if num not in ei_routes and game.base(num) in ei_routes and game.evos[num]:
            ei_routes[num] = list(ei_routes[game.base(num)])

    changes = {}
    for num, routes in sorted(ei_routes.items()):
        old = [norm(r) for r in game.evos.get(num, [])]
        if not routes:
            continue  # no evolution in the dex: Heart & Soul's stay, if any (no form becomes unreachable)
        new = adapt(num, [norm(r) for r in routes], old, game)
        if sorted(map(repr, new)) != sorted(map(repr, old)):  # the same routes in another order: no change
            changes[num] = (old, new)
    return changes


def adapt(num, new, old, game):
    """This game's forms for Imperium's targets, then what Heart & Soul keeps."""
    name = game.name(num)
    old_targets = {r[2] for r in old}
    routes = []
    for method, param, target, conds in new:
        if target not in old_targets:
            same_base = {t for t in old_targets if game.base(t) == game.base(target)}
            if len(same_base) == 1:
                target = same_base.pop()  # the matching form: Burmy Sandy's Mothim is Sandy Mothim
        if method == PLACE:
            # Imperium's place is in Hoenn (New Mauville for Magnezone and Vikavolt): Heart & Soul's
            # places for the same evolution stand in for it
            routes += [r for r in old if r[2] == target and r not in routes
                       and any(c[0] in ("IF_IN_MAPSEC", "IF_IN_MAP") for c in r[3])]
        elif (method, param, target, conds) not in routes:
            routes.append((method, param, target, conds))
    if name == "SPECIES_MILCERY":
        # Imperium lists a Shiny Stone for each of the nine creams; the first route that applies wins,
        # so it gives Vanilla Cream. Heart & Soul's stones and spins give the other flavours.
        first, seen = [], set()
        for r in routes:
            if (r[0], r[1], r[3]) not in seen:
                seen.add((r[0], r[1], r[3]))
                first.append(r)
        routes = first + [r for r in old if r not in first]
    # First match wins: Sylveon before Espeon and Umbreon, Dusk Lycanroc before Midday
    routes.sort(key=lambda r: 0 if r[0] == "EVO_LEVEL" and any(c[0] == "IF_KNOWS_MOVE_TYPE" or c == EVENING
                                                               for c in r[3]) else 1)
    return routes


# --- Output -------------------------------------------------------------------------------------------

def render_route(route, game):
    method, param, target, conds = route
    if method == "EVO_SPLIT_FROM_EVO":
        param = game.name(param)
    text = f"{{{method}, {param}, {game.name(target)}"
    if conds:
        text += ", CONDITIONS(" + ", ".join("{" + ", ".join(c) + "}" for c in conds) + ")"
    return text + "}"


ITEM_WORDS = {"ITEM_LINKING_CORD": "Linking Cord", "ITEM_UPGRADE": "Up-Grade", "ITEM_UP_GRADE": "Up-Grade",
              "ITEM_KINGS_ROCK": "King's Rock", "ITEM_LEADERS_CREST": "Leader's Crest",
              "ITEM_SCROLL_OF_DARKNESS": "Scroll of Darkness", "ITEM_SCROLL_OF_WATERS": "Scroll of Waters"}
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
    "IF_MIN_BEAUTY": lambda a: f"beauty {a[0]}",
    "IF_TRADE_PARTNER_SPECIES": lambda a: "for " + words(a[0], "SPECIES_"),
    "IF_PID_MODULO_100_GT": lambda a: "personality % 100 > " + a[0],
    "IF_PID_MODULO_100_EQ": lambda a: "personality % 100 = " + a[0],
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


def generate(ei, game):
    changes = plan(ei, game)
    lines = ["// Generated by tools/crystal_imperium/imperium_evolutions.py: Emerald Imperium's evolution methods",
             "// (its dex, DECISIONS.md D44, D45) where they differ from Heart & Soul's. Included at the end of",
             "// gSpeciesInfo (src/data/pokemon/species_info.h): each line replaces one species' evolutions.",
             "// Edit the script, not this file.",
             ""]
    for num, (old, new) in changes.items():
        was = "; ".join(describe(r, game) for r in old) or "no evolution"
        routes = ",\n        ".join(render_route(r, game) for r in new)
        lines.append(f"    // was: {was}")
        lines.append(f"    [{game.name(num)}].evolutions = EVOLUTION({routes}),")
    return "\n".join(lines) + "\n", changes


# --- The evolution guide (docs/crystal_imperium/EVOLUTIONS.md) ----------------------------------------

GUIDE = "docs/crystal_imperium/EVOLUTIONS.md"
REGIONAL = {"ALOLA": "Alolan", "GALAR": "Galarian", "HISUI": "Hisuian", "PALDEA": "Paldean"}
HOURS = {"night": "at night (19:00-5:59)", "day": "by day (6:00-18:59)", "evening": "in the evening (18:00-18:59)",
         "daytime": "in the daytime (10:00-17:59)", "morning": "in the morning (6:00-9:59)"}
NATURE_GROUPS = {"IF_AMPED_NATURE": "an Amped nature (Hardy, Brave, Adamant, Naughty, Docile, Impish, Lax, Hasty, Jolly, "
                                    "Naive, Rash, Sassy, Quirky)",
                 "IF_LOW_KEY_NATURE": "a Low Key nature (Lonely, Bold, Relaxed, Timid, Serious, Modest, Mild, Quiet, "
                                      "Bashful, Calm, Gentle, Careful)"}
PLACES = {"MAPSEC_ROUTE_10": "on Route 10", "MAPSEC_POWER_PLANT": "in the Power Plant", "MAPSEC_MT_MOON": "in the Mt. Moon area"}


def display_names(ei, game):
    """number -> a readable name: the dex's ("Mr. Mime", "Flabebe (Red)", "Alolan Raichu"), else the constant's."""
    mp = isp.Mapper(ei)
    out = {}
    for sid, s in sorted(ei["species"].items()):
        const = mp.species(s)
        if not const or game.consts[const] in out:
            continue
        name = s["speciesName"]
        base_key = isp.constify(name, "")
        key = isp.constify(s["nameKey"], "")
        suffix = s["nameKey"][len(s["nameKey"]) - (len(key) - len(base_key)) + 1:] if key.startswith(base_key + "_") else ""
        if suffix.upper() in REGIONAL:
            out[game.consts[const]] = f"{REGIONAL[suffix.upper()]} {name}"
        elif suffix:
            label = {"F": "Female", "M": "Male"}.get(suffix, suffix)
            if not re.search(r"Striped|Segment", label):
                label = label.replace("-", " ")
            out[game.consts[const]] = f"{name} ({label})"
        else:
            out[game.consts[const]] = name
    return out


def article(item):
    """ "a Moon Stone", "an Ice Stone" """
    name = item_words(item)
    return ("an " if name[0] in "AEIOU" else "a ") + name


def guide_name(num, game, names):
    if num in names:
        return names[num]
    return words(game.name(num), "SPECIES_")


def how(route, game, names):
    """A route in a player's words: "Level 36 at night", "Use a Linking Cord"."""
    method, param, target, conds = route
    parts = []
    if method in ("EVO_LEVEL", "EVO_LEVEL_BATTLE_ONLY"):
        parts.append(f"Level {param}" if param != "0" else "Level up")
        if method == "EVO_LEVEL_BATTLE_ONLY":
            parts.append("in a battle")
    elif method == "EVO_ITEM":
        parts.append(f"Use {article(param)}")
    elif method == "EVO_TRADE":
        parts.append("Trade it")
    elif method == "EVO_SPIN":
        parts.append("Spin in place")
    elif method == "EVO_BATTLE_END":
        parts.append("At the end of a battle")
    elif method == "EVO_SCRIPT_TRIGGER":
        parts.append("At a special place")
    elif method == "EVO_SPLIT_FROM_EVO":
        parts.append(f"When it becomes a {guide_name(param, game, names)}")
    else:
        parts.append(words(method, "EVO_").lower())
    for c in conds:
        name, args = c[0], c[1:]
        if c == FRIENDSHIP:
            parts.append("with high friendship")
        elif c == NIGHT:
            parts.append(HOURS["night"])
        elif c == NOT_NIGHT:
            parts.append(HOURS["day"])
        elif c == EVENING:
            parts.append(HOURS["evening"])
        elif name == "IF_TIME":
            parts.append(HOURS.get(args[0][5:].lower().replace("day", "daytime"), args[0]))
        elif name == "IF_GENDER":
            parts.append("if female" if args[0] == "MON_FEMALE" else "if male")
        elif name == "IF_KNOWS_MOVE":
            parts.append("knowing " + words(args[0], "MOVE_"))
        elif name == "IF_KNOWS_MOVE_TYPE":
            parts.append(f"knowing a {words(args[0], 'TYPE_')}-type move")
        elif name == "IF_SPECIES_IN_PARTY":
            parts.append(f"with {guide_name(game.consts[args[0]], game, names)} in the party")
        elif name == "IF_TYPE_IN_PARTY":
            parts.append(f"with a {words(args[0], 'TYPE_')}-type Pokémon in the party")
        elif name == "IF_TRADE_PARTNER_SPECIES":
            parts.append(f"for a {guide_name(game.consts[args[0]], game, names)}")
        elif name == "IF_HOLD_ITEM":
            parts.append(f"holding {article(args[0])}")
        elif name == "IF_WEATHER":
            parts.append({"WEATHER_RAIN": "in the rain", "WEATHER_FOG": "in fog"}.get(args[0], "in " + words(args[0], "WEATHER_")))
        elif name == "IF_MIN_BEAUTY":
            parts.append(f"with Beauty {args[0]} or more")
        elif name == "IF_IN_MAPSEC":
            parts.append(PLACES.get(args[0], "in " + words(args[0], "MAPSEC_")))
        elif name == "IF_PID_MODULO_100_EQ":
            parts.append("(1 in 100, by its personality)")
        elif name == "IF_PID_MODULO_100_GT":
            parts.append("(99 in 100, by its personality)")
        elif name in ("IF_PID_UPPER_MODULO_10_GT", "IF_PID_UPPER_MODULO_10_LT"):
            parts.append("(half of them, by personality)")
        elif name in ("IF_ATK_GT_DEF", "IF_ATK_EQ_DEF", "IF_ATK_LT_DEF"):
            parts.append({"IF_ATK_GT_DEF": "with Attack above Defense", "IF_ATK_EQ_DEF": "with Attack equal to Defense",
                          "IF_ATK_LT_DEF": "with Attack below Defense"}[name])
        elif name in NATURE_GROUPS:
            parts.append("with " + NATURE_GROUPS[name])
        elif name in ("IF_REGION", "IF_NOT_REGION"):
            region = "Sinjoh" if args[0] == "REGION_HISUI" else words(args[0], "REGION_")  # Heart & Soul's Hisui
            parts.append(("in " if name == "IF_REGION" else "outside ") + region)
        elif name == "IF_IN_MAP":
            parts.append("in " + words(args[0], "MAP_").replace(" Hns", ""))
        elif name == "IF_USED_MOVE_X_TIMES":
            parts.append(f"after using {words(args[0], 'MOVE_')} {args[1]} times")
        elif name == "IF_MIN_OVERWORLD_STEPS":
            parts.append(f"after walking {args[0]} steps with it")
        elif name == "IF_BAG_ITEM_COUNT":
            parts.append(f"with {args[1]} {item_words(args[0])} in the Bag")
        elif name == "IF_RECOIL_DAMAGE_GE":
            parts.append(f"after losing {args[0]} HP to recoil")
        elif name == "IF_CRITICAL_HITS_GE":
            parts.append(f"after {args[0]} critical hits in a battle")
        elif name == "IF_CURRENT_DAMAGE_GE":
            parts.append(f"after losing {args[0]} HP")
        elif name == "IF_DEFEAT_X_WITH_ITEMS":
            parts.append(f"after defeating {args[2]} {guide_name(game.consts.get(args[0], 0), game, names)} holding {article(args[1])}")
        else:
            parts.append(words(name, "IF_").lower() + (" " + " ".join(args) if args else ""))
    return " ".join(parts)


def guide(ei, game, changes):
    names = display_names(ei, game)
    final = {num: list(routes) for num, routes in game.evos.items()}
    for num, (old, new) in changes.items():
        final[num] = new

    def plain(routes):
        return all(r[0] == "EVO_LEVEL" and r[1] != "0" and not r[3] for r in routes)

    def key(routes):
        return sorted(repr((r[0], r[1], game.base(r[2]), r[3])) for r in routes)

    def order(num):
        return (game.base(num), num)

    special, levels = [], []
    for num in sorted((n for n, r in final.items() if r), key=order):
        routes = final[num]
        base = game.base(num)
        if base != num and base in final and key(final[base]) == key(routes):
            continue  # a form evolving as its base form does, into its own form
        old = [norm(r) for r in game.evos.get(num, [])]
        if plain(routes) and plain(old):
            was = {r[2]: r[1] for r in old}
            for r in routes:
                before = was.get(r[2])
                levels.append((guide_name(num, game, names), guide_name(r[2], game, names), r[1],
                               before if before and before != r[1] else ""))
        else:
            if game.name(num) == "SPECIES_MILCERY":
                special.append(("Milcery", "Alcremie", "Use a Shiny Stone (Vanilla Cream), another stone, or spin in place "
                                "holding a Sweet: see Alcremie below", ""))
                continue
            targets = list(dict.fromkeys(r[2] for r in routes))
            changed = sorted(map(repr, old)) != sorted(map(repr, [norm(r) for r in routes]))
            def joined(ways):
                ways = list(dict.fromkeys(ways))
                return ways[0] + "".join(", or " + w[0].lower() + w[1:] for w in ways[1:])
            for i, target in enumerate(targets):
                cell = joined([how(r, game, names) for r in routes if r[2] == target])
                before = ""
                if changed:
                    was = ([how(r, game, names) for r in old if r[2] == target]
                           or [how(r, game, names) for r in old if game.base(r[2]) == game.base(target)])
                    before = joined(was) if was else "no evolution"
                    if before == cell:
                        before = ""
                special.append((guide_name(num, game, names), guide_name(target, game, names), cell, before))

    out = ["# Crystal Imperium: how every Pokémon evolves", "",
           "Generated by `tools/crystal_imperium/imperium_evolutions.py --guide` from the game's own data: the",
           "evolutions of Emerald Imperium's official dex (DECISIONS.md D44, D45). Edit the script, not this file.", "",
           "## What you need", "",
           "- **Evolution items:** the Goldenrod Dept. Store 2F clerk sells Emerald Imperium's fifteen for ¥500 each: the",
           "  Fire, Thunder, Leaf, Water, Sun, Moon, Ice, Dusk, Dawn and Shiny Stones, the Prism Scale, the Linking Cord,",
           "  the King's Rock, the Metal Coat and the Up-Grade. Use one from the Bag on the Pokémon. Most are in the",
           "  care packages too; the Metal Alloy (Duraludon) comes in the 7th badge's, the Sweets (Alcremie) in the 4th's.",
           "- **Trade evolutions** also take a Linking Cord, so no trade is needed.",
           "- **Friendship:** the same clerk sells the Pomeg, Kelpsy, Qualot, Hondew, Grepa and Tamato Berries (¥20), which",
           "  raise it (and lower an EV each). Walking, battling and a Soothe Bell raise it too.",
           "- **Time of day:** night is 19:00-5:59, \"by day\" 6:00-18:59, the evening 18:00-18:59. The L button menu's",
           "  TIME sets the morning, day, evening or night.",
           "- **\"Level up knowing a move\":** teach the move with the party menu's LEARN MOVES, then level up once. A Rare",
           "  Candy works, even at the level cap: a Pokémon at the cap still evolves (D33).", "",
           "## Special evolutions", "",
           "Everything that isn't a plain level, and the ones that used to be special. *Before* is Heart & Soul's way, where",
           "it changed.", "",
           "| Pokémon | Becomes | How | Before |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in special]
    out += ["", "### Alcremie", "",
            "Milcery's cream comes from what you use or how you spin (holding a Sweet, which gives the decoration):", "",
            "| Way | Cream |", "|---|---|"]
    milcery = final.get(game.consts["SPECIES_MILCERY"], [])
    seen = set()
    for r in milcery:
        target = guide_name(r[2], game, names)
        cream = target.split("(", 1)[-1].rstrip(")").replace("Strawberry ", "") if "(" in target else target
        way = how(r, game, names)
        if r[0] == "EVO_SPIN":
            spin = {"SPIN_CW_SHORT": "clockwise, under 5 s", "SPIN_CW_LONG": "clockwise, over 5 s", "SPIN_CCW_SHORT":
                    "counterclockwise, under 5 s", "SPIN_CCW_LONG": "counterclockwise, over 5 s"}.get(r[1], "either way, over 10 s")
            times = [how(("EVO_LEVEL", "0", 0, (c,)), game, names).replace("Level up ", "") for c in r[3] if c[0] in ("IF_TIME", "IF_NOT_TIME")]
            way = f"Spin {spin}, holding a Sweet, {' '.join(times)}"
            if "Strawberry" not in target:
                continue  # the same spins with the other Sweets: their decoration
        if (way, cream) not in seen:
            seen.add((way, cream))
            out.append(f"| {way} | {cream} |")
    out += ["", "## Level evolutions", "",
            "*Before* is Heart & Soul's level, where it changed. A regional or other form evolves at its base form's",
            "level, into its own form, unless it is listed.", "",
            "| Pokémon | Becomes | Level | Before |", "|---|---|---|---|"]
    out += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in levels]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ei-dex", required=True, help="a saved copy of the Emerald Imperium dex's script (" + ei_dex.EI_DEX_URL + ")")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()  # the guide (GUIDE) is written and checked with the header
    ei, digest = ei_dex.load_ei(args.ei_dex)
    if digest != ei_dex.EI_DEX_SHA256:
        sys.exit(f"{args.ei_dex} isn't the dex script these files came from (SHA-256 {digest})")
    game = Game()
    text, changes = generate(ei, game)
    if args.report:
        for num, (old, new) in changes.items():
            print(words(game.name(num), "SPECIES_"))
            print("   old: " + ("; ".join(describe(r, game) for r in old) or "no evolution"))
            print("   new: " + "; ".join(describe(r, game) for r in new))
        print(f"{len(changes)} species change")
        return
    outputs = {OUT: text, GUIDE: guide(ei, game, changes)}
    stale = [p for p, new in outputs.items() if not os.path.exists(os.path.join(isp.ROOT, p))
             or open(os.path.join(isp.ROOT, p), encoding="utf-8").read() != new]
    if args.check:
        if stale:
            sys.exit(f"{', '.join(stale)} out of date: run tools/crystal_imperium/imperium_evolutions.py")
        print(f"{OUT} and {GUIDE} are up to date ({len(changes)} species)")
        return
    for p in stale:
        with open(os.path.join(isp.ROOT, p), "w", encoding="utf-8") as f:
            f.write(outputs[p])
        print(f"wrote {p}")
    print(f"{len(changes)} species with Imperium's evolutions")


if __name__ == "__main__":
    main()
