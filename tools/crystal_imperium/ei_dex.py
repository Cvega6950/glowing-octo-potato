#!/usr/bin/env python3
"""Crystal Imperium: the official Emerald Imperium dex's data (DECISIONS.md D45).

The dex at https://dex.emeraldimperium.net ("Official online Pokedex tool for Pokemon Emerald
Imperium") keeps its data in its page script: one table each of species (abilities, level-up, TM and
tutor moves, Egg Moves, evolutions), moves, items, abilities and types, written as JavaScript object
literals. load_ei() reads them from a saved copy of that script (EI_DEX_URL) without running it:
the literals are parsed as data. The file isn't kept in this repository; what imperium_species.py
and imperium_evolutions.py write from it is.

Its numbers are Emerald Imperium's: species, moves and items by its own IDs, evolutions as
[method, target species, parameter] with the method numbers of the expansion version Imperium is
built on (EI_METHODS), ability lists as [first, second, hidden].
"""
import hashlib
import re

EI_DEX_URL = "https://dex.emeraldimperium.net/assets/index-Cgh1ktsP.js"
EI_DEX_SHA256 = "7eddbfdc272941a1e7d98bd2b08b4da2ec0b2bc93b84eae2bbce8a83947abdbb"

# The script's variable for each table, found by its first entry's field
TABLE_FIELDS = {"types": "typeID", "items": "itemId", "abilities": "abilityId", "species": "speciesId", "moves": "moveId"}

# The dex's own names for its evolution methods (its "evolution" labels), for reports
EI_METHODS = {
    0: "none", 1: "friendship", 2: "friendship by day", 3: "friendship at night", 4: "level", 5: "trade",
    6: "trade holding an item", 7: "item", 8: "level, Attack > Defense", 9: "level, Attack = Defense",
    10: "level, Attack < Defense", 11: "level, Silcoon personality", 12: "level, Cascoon personality",
    13: "level (Ninjask)", 14: "level (Shedinja)", 15: "beauty", 16: "level, female", 17: "level, male",
    18: "level at night", 19: "level by day", 20: "level at dusk", 21: "level holding an item by day",
    22: "level holding an item at night", 23: "level knowing a move", 24: "friendship, knowing a move of a type",
    25: "level in a place", 26: "item, male", 27: "item, female", 28: "level in rain", 29: "level with a species in the party",
    30: "level with a Dark type in the party", 31: "trade for a species", 32: "level on a map", 33: "level, amped nature",
    34: "level, low-key nature", 35: "critical hits", 36: "damage, then a trigger", 37: "Scroll of Darkness",
    38: "Scroll of Waters", 39: "item at night", 40: "item by day", 41: "level holding an item", 42: "level in fog",
    43: "level knowing a move, personality % 100 != 0", 44: "level knowing a move, personality % 100 == 0",
    45: "level, personality % 100 == 0", 46: "level, personality % 100 != 0", 47: "level after using a move 20 times",
    48: "level after recoil, male", 49: "level after recoil, female", 50: "level with 999 of an item",
    51: "level after defeating three holding an item", 52: "level after steps",
}


class _Literal:
    """A parser for the JavaScript literals a minifier writes: objects (with bare or quoted keys), arrays,
    strings, numbers (1e3), !0 and !1, null. Anything else (a function, a variable) is an error."""

    NUMBER = re.compile(r"-?(?:\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+)")
    WORD = re.compile(r"[A-Za-z_$][\w$]*")
    KEY = re.compile(r"[\w$]+")

    def __init__(self, text, pos):
        self.s, self.i = text, pos

    def skip(self):
        while self.s[self.i] in " \t\r\n":
            self.i += 1

    def value(self):
        self.skip()
        c = self.s[self.i]
        if c == "{":
            return self.object()
        if c == "[":
            return self.array()
        if c in "\"'":
            return self.string(c)
        if c == "!" and self.s[self.i + 1] in "01":
            self.i += 2
            return self.s[self.i - 1] == "0"
        m = self.NUMBER.match(self.s, self.i)
        if m:
            self.i = m.end()
            v = float(m.group(0))
            return int(v) if v.is_integer() and "." not in m.group(0) else v
        m = self.WORD.match(self.s, self.i)
        if m and m.group(0) in ("null", "true", "false"):
            self.i = m.end()
            return {"null": None, "true": True, "false": False}[m.group(0)]
        raise ValueError(f"not a data literal at {self.i}: {self.s[self.i:self.i + 40]!r}")

    def string(self, quote):
        self.i += 1
        out = []
        while self.s[self.i] != quote:
            c = self.s[self.i]
            if c == "\\":
                n = self.s[self.i + 1]
                if n == "u":
                    out.append(chr(int(self.s[self.i + 2:self.i + 6], 16)))
                    self.i += 6
                    continue
                out.append({"n": "\n", "t": "\t", "r": "\r"}.get(n, n))
                self.i += 2
                continue
            out.append(c)
            self.i += 1
        self.i += 1
        return "".join(out)

    def key(self):
        self.skip()
        if self.s[self.i] in "\"'":
            return self.string(self.s[self.i])
        m = self.KEY.match(self.s, self.i)
        self.i = m.end()
        k = m.group(0)
        return str(int(float(k))) if re.fullmatch(r"\d+(?:[eE]\d+)?", k) else k  # 1e3 is 1000

    def object(self):
        self.i += 1
        out = {}
        while True:
            self.skip()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            k = self.key()
            self.skip()
            if self.s[self.i] != ":":
                raise ValueError(f"not a data literal at {self.i}: shorthand property {k}")
            self.i += 1
            out[k] = self.value()
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1

    def array(self):
        self.i += 1
        out = []
        while True:
            self.skip()
            if self.s[self.i] == "]":
                self.i += 1
                return out
            out.append(self.value())
            self.skip()
            if self.s[self.i] == ",":
                self.i += 1


def load_ei(path):
    """{types, items, abilities, species, moves}: each {ID: entry}, and the file's SHA-256."""
    with open(path, "rb") as f:
        raw = f.read()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    data = {}
    for name, field in TABLE_FIELDS.items():
        m = re.search(r"[\w$]+=\{1:\{" + field + r":", text)
        if not m:
            raise ValueError(f"{path}: no {name} table")
        start = text.index("{", m.start())
        table = _Literal(text, start).value()
        data[name] = {int(k): v for k, v in table.items()}
    return data, digest
