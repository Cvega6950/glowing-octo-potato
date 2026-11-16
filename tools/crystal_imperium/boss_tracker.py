#!/usr/bin/env python3
"""Crystal Imperium: the L menu's BOSSES list (src/boss_tracker.c). Three pages, JOHTO, KANTO and TO
RED, of every Gym Leader, both POKéMON LEAGUES, the 25 visiting challengers of the side battles
(DECISIONS.md D41) and RED, in play order: each Gym followed by the visitor who battles after it.
From the table below and side_battles.py's (each visitor's name, trainer IDs, reward flag, gate and
place) this writes

  src/data/boss_tracker.h    the rows, page by page

  python3 tools/crystal_imperium/boss_tracker.py           # rewrite it
  python3 tools/crystal_imperium/boss_tracker.py --check   # exit 1 if it is out of date

Run it after side_battles.py: a visitor who moves, or opens at another point, moves in the list too
(its place is the map section of its first map, its gate the one its script tests). Both runs stop
when a side battle is missing from the pages, or a page names one that isn't in side_battles.py.

A row on the way to Red is beaten when its flag is set: a Gym's badge (the Gym's own script sets it;
Whitney's and Clair's come after their battles), a League's champion flag (the Hall of Fame), RED's
FLAG_DEFEATED_RED. A visitor is beaten when one of its trainer flags is (goto_if_defeated) or its
reward flag, and its reward waits until its reward flag is set. Every name, place and info line is
measured in the game's FONT_NORMAL against the screen's columns (include/boss_tracker.h), as
test/boss_tracker.c measures them, and the state texts, with the game's own code.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import care_packages  # noqa: E402  (FONT_NORMAL widths)
import side_battles as sb  # noqa: E402  (the visitors)

ROOT = sb.ROOT
OUTPUT = os.path.join(ROOT, "src", "data", "boss_tracker.h")
HEADER = "include/boss_tracker.h"

# Between the widest name and the place column
COLUMN_GAP = 8


class Main:
    """A boss on the way to Red: beaten when its flag is set (set_in: the map whose script sets it)."""
    def __init__(self, key, name, kind, flag, place, set_in=None, gym=None, info=None):
        self.key = key
        self.name = name
        self.kind = kind          # "gym", "league" or "red"
        self.flag = flag
        self.place = place        # the map whose map section is the place shown
        self.set_in = set_in or place
        self.gym = gym            # a Gym's number in its region
        self.info = info          # a League's or RED's info line: what opens it


# The 16 Gyms by badge (FLAG_BADGE01_GET to FLAG_BADGE16_GET): key, name, the Gym's map, the map whose
# script gives the badge when it isn't the Gym's. Blaine's Gym is in the Seafoam Islands; Whitney's
# badge comes when she is talked to again after crying, Clair's from the Dragon's Den's elder (both
# after their battles, so they stay NEXT until then).
GYM_LEADERS = [
    ("FALKNER", "FALKNER", "VioletCity_Gym_hns", None),
    ("BUGSY", "BUGSY", "AzaleaTown_Gym_hns", None),
    ("WHITNEY", "WHITNEY", "GoldenrodCity_Gym_hns", None),
    ("MORTY", "MORTY", "EcruteakCity_Gym_hns", None),
    ("CHUCK", "CHUCK", "CianwoodGym_hns", None),
    ("JASMINE", "JASMINE", "OlivineCity_Gym_hns", None),
    ("PRYCE", "PRYCE", "MahoganyTown_Gym_hns", None),
    ("CLAIR", "CLAIR", "BlackthornCity_Gym_hns", "DragonsDen_Shrine_hns"),
    ("BROCK", "BROCK", "PewterCity_Gym_hns", None),
    ("MISTY", "MISTY", "CeruleanCity_Gym_hns", None),
    ("LT_SURGE", "LT. SURGE", "VermilionCity_Gym_hns", None),
    ("ERIKA", "ERIKA", "CeladonCity_Gym_hns", None),
    ("SABRINA", "SABRINA", "SaffronCity_Gym_hns", None),
    ("JANINE", "JANINE", "FuchsiaCity_Gym_hns", None),
    ("BLAINE", "BLAINE", "SeafoamIslands_Gym_hns", None),
    ("BLUE", "BLUE", "ViridianCity_Gym_hns", None),
]

MAIN = [Main(key, name, "gym", f"FLAG_BADGE{n:02d}_GET", place, set_in, gym=(n - 1) % 8 + 1)
        for n, (key, name, place, set_in) in enumerate(GYM_LEADERS, 1)]
MAIN += [
    # The Reception Gate's officer wants the eighth badge (ReceptionGate_hns); after the first win a
    # Black Belt bars the League until Blue's badge, the sixteenth, sends him away (ViridianCity_Gym_hns)
    Main("JOHTO_LEAGUE", "JOHTO LEAGUE", "league", sb.JOHTO_CHAMPION_FLAG, "PokemonLeague_ChampionsRoom_hns",
         "PokemonLeague_HallOfFame_hns", info="ELITE FOUR - OPENS WITH 8 BADGES"),
    Main("KANTO_LEAGUE", "KANTO LEAGUE", "league", sb.KANTO_CHAMPION_FLAG, "PokemonLeague_ChampionsRoom_hns",
         "PokemonLeague_HallOfFame_hns", info="ELITE FOUR - OPENS WITH 16 BADGES"),
    # Red battles once the player has won the Kanto League (MtSilver_SummitDay_hns); the postgame's
    # visitors before him on the page are optional (DECISIONS.md D41)
    Main("RED", "RED", "red", "FLAG_DEFEATED_RED", "MtSilver_SummitDay_hns",
         info="LAST BOSS - AFTER THE KANTO LEAGUE"),
]

# The pages in play order, by key: a Gym's leader, a League, RED, or a side battle (side_battles.py)
PAGES = [
    ("JOHTO", ["CANDICE", "FALKNER", "BUGSY", "GARDENIA", "WHITNEY", "FANTINA", "MORTY", "MAYLENE", "CHUCK",
               "WAKE", "JASMINE", "BYRON", "PRYCE", "ROARK", "CLAIR", "VOLKNER", "JOHTO_LEAGUE"]),
    ("KANTO", ["BROCK", "KATY", "MISTY", "KOFU", "LT_SURGE", "IONO", "ERIKA", "BRASSIUS", "SABRINA", "TULIP",
               "JANINE", "RYME", "BLAINE", "GRUSHA", "BLUE", "LARRY", "KANTO_LEAGUE"]),
    ("TO RED", ["WALLACE", "CYNTHIA", "N", "CYRUS", "IRIS", "WALLY", "ARCHIE", "MAXIE", "GEETA", "RED"]),
]
PAGE_ENUM = {"JOHTO": "BOSS_TRACKER_JOHTO", "KANTO": "BOSS_TRACKER_KANTO", "TO RED": "BOSS_TRACKER_TO_RED"}

# What a flag gate's info says: a Gym's badge names its leader
FLAG_GATES = {sb.JOHTO_CHAMPION_FLAG: "OPENS AFTER THE JOHTO LEAGUE",
              sb.KANTO_CHAMPION_FLAG: "OPENS AFTER THE KANTO LEAGUE"}
FLAG_GATES.update({m.flag: f"OPENS AFTER {m.name}'S BADGE" for m in MAIN if m.kind == "gym"})


def fail(message):
    sys.exit(f"boss_tracker.py: {message}")


def layout():
    """The screen's columns (include/boss_tracker.h): name -> pixels."""
    text = sb.read(HEADER)
    values = {}
    for name in ("WINDOW_WIDTH", "NAME_X", "INFO_X"):
        m = re.search(rf"#define BOSS_TRACKER_{name}\s+(\d+)", text)
        if not m:
            fail(f"no BOSS_TRACKER_{name} in {HEADER}")
        values[name] = int(m.group(1))
    for name in ("LIST_RIGHT", "TEXT_RIGHT"):
        m = re.search(rf"#define BOSS_TRACKER_{name}\s+\(BOSS_TRACKER_WINDOW_WIDTH - (\d+)\)", text)
        if not m:
            fail(f"no BOSS_TRACKER_{name} in {HEADER}")
        values[name] = values["WINDOW_WIDTH"] - int(m.group(1))
    return values


def map_json(folder):
    path = os.path.join(ROOT, "data", "maps", folder, "map.json")
    if not os.path.exists(path):
        fail(f"no map {folder}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def section_names():
    """MAPSEC_ -> its name in the two tables GetMapName reads: Heart & Soul's generated one
    (src/data/region_map/region_map_sections.json) and src/region_map.c's sRegionMapEntries_Johto,
    used once Kanto is visited (GetActiveRegionMapEntries)."""
    with open(os.path.join(ROOT, "src", "data", "region_map", "region_map_sections.json"), encoding="utf-8") as f:
        generated = {s["id"]: s["name"] for s in json.load(f)["hns_map_sections"] if "name" in s}
    block = re.search(r"sRegionMapEntries_Johto\[\]\s*=\s*\{(.*?)\n\};", sb.read("src/region_map.c"), re.S)
    if not block:
        fail("no sRegionMapEntries_Johto in src/region_map.c")
    johto = dict(re.findall(r'\[(MAPSEC_\w+)\]\s*=\s*\{[^}]*COMPOUND_STRING\("([^"]*)"\)', block.group(1)))
    return generated, johto


def place_name(mapsec, names):
    generated, johto = names
    if mapsec not in generated or mapsec not in johto:
        fail(f"{mapsec} has no name in both region map tables")
    if generated[mapsec] != johto[mapsec]:
        fail(f"{mapsec} is {generated[mapsec]!r} in one region map table and {johto[mapsec]!r} in the other")
    return generated[mapsec]


def gate_info(gate):
    kind, value = gate
    if kind == "badges":
        if value == 0:
            return "OPEN FROM THE START"
        return f"OPENS WITH {value} BADGE" + ("" if value == 1 else "S")
    if value not in FLAG_GATES:
        fail(f"no words for the gate {value}: add them to FLAG_GATES")
    return FLAG_GATES[value]


def rows():
    """[(page, row)]: a row is a dict of the generated fields, in page order."""
    battles = {b.key: b for b in sb.BATTLES}
    main = {m.key: m for m in MAIN}
    if set(battles) & set(main):
        fail(f"{sorted(set(battles) & set(main))} both a side battle and a boss on the way to Red")
    listed = [key for _, keys in PAGES for key in keys]
    twice = sorted({key for key in listed if listed.count(key) > 1})
    if twice:
        fail(f"{twice} on the pages twice")
    unknown = sorted(set(listed) - set(battles) - set(main))
    if unknown:
        fail(f"{unknown} on the pages but not side battles (side_battles.py) or bosses here")
    missing = sorted((set(battles) | set(main)) - set(listed))
    if missing:
        fail(f"{missing} missing from the pages: add each where it battles")
    if listed[-1] != "RED":
        fail("RED is the last row")
    names = section_names()
    out = []
    for page, keys in PAGES:
        for key in keys:
            if key in main:
                m = main[key]
                mapsec = map_json(m.place)["region_map_section"]
                place = place_name(mapsec, names)
                scripts = sb.read(os.path.join("data", "maps", m.set_in, "scripts.inc"))
                if not re.search(r"^\s*setflag " + m.flag + r"\b", scripts, re.M):
                    fail(f"{key}: {m.set_in}'s script doesn't set {m.flag}")
                info = f"GYM {m.gym} - {place}" if m.kind == "gym" else m.info
                out.append((page, {"key": key, "name": m.name, "kind": f"BOSS_KIND_{m.kind.upper()}",
                                   "flag": m.flag, "mapsec": mapsec, "place": place, "info": info}))
            else:
                b = battles[key]
                mapsec = map_json(b.places[0][0])["region_map_section"]
                kind, value = b.gate
                if kind not in ("badges", "flag"):
                    fail(f"{key}: a gate of {kind}")
                if b.gender not in ("Female", "Male"):
                    fail(f"{key}: {b.gender}, neither her nor him")
                out.append((page, {"key": key, "name": b.name, "kind": "BOSS_KIND_VISITOR", "flag": b.reward_flag,
                                   "mapsec": mapsec, "place": place_name(mapsec, names),
                                   "info": "OPTIONAL - " + gate_info(b.gate),
                                   "gateKind": "BOSS_GATE_BADGES" if kind == "badges" else "BOSS_GATE_FLAG",
                                   "gate": str(value), "trainers": [t for t, _ in b.trainers()],
                                   "female": b.gender == "Female"}))
    return out


def check_widths(table, columns):
    """Every name, place and info line fits the screen (FONT_NORMAL); returns the place column's x."""
    widths = care_packages.glyph_widths()

    def width(text):
        try:
            return care_packages.text_width(text, widths)
        except KeyError as e:
            fail(f"{text!r}: no glyph for {e}")

    place_x = columns["NAME_X"] + max(width(r["name"]) for _, r in table) + COLUMN_GAP
    for _, r in table:
        for t in (r["name"], r["info"]):
            if '"' in t or "\\" in t or "{" in t:
                fail(f"{r['key']}: {t!r} has a quote, a backslash or a brace")
        if place_x + width(r["place"]) > columns["LIST_RIGHT"]:
            fail(f"{r['key']}: {r['place']} doesn't fit the list ({place_x + width(r['place'])} > "
                 f"{columns['LIST_RIGHT']})")
        if columns["INFO_X"] + width(r["info"]) > columns["TEXT_RIGHT"]:
            fail(f"{r['key']}: {r['info']!r} doesn't fit the info window ({columns['INFO_X'] + width(r['info'])} > "
                 f"{columns['TEXT_RIGHT']})")
    return place_x


def render(table, place_x):
    out = ["// Generated by tools/crystal_imperium/boss_tracker.py from its table and side_battles.py's: edit",
           "// those, not this file. Crystal Imperium: the L menu's BOSSES list (src/boss_tracker.c), page by",
           "// page in play order.", "",
           "// The place column, after the widest name", f"#define BOSS_TRACKER_PLACE_X {place_x}", ""]
    longest = max(len(keys) for _, keys in PAGES)
    out += ["// The rows, and the longest page's", f"#define BOSS_TRACKER_ROW_COUNT {len(table)}",
            f"#define BOSS_TRACKER_MAX_PAGE_ROWS {longest}", ""]
    infos = []
    for _, r in table:
        if r["info"] not in infos:
            infos.append(r["info"])
    out += [f'static const u8 sBossTrackerInfo{i}[] = _("{info}");' for i, info in enumerate(infos)]
    out += ["", "static const struct BossTrackerRow sBossTrackerRows[BOSS_TRACKER_ROW_COUNT] =", "{"]
    page = None
    for i, (p, r) in enumerate(table):
        if p != page:
            out.append(f"    // {p}")
            page = p
        fields = [f'.name = COMPOUND_STRING("{r["name"]}")', f'.info = sBossTrackerInfo{infos.index(r["info"])}',
                  f'.kind = {r["kind"]}', f'.flag = {r["flag"]}']
        if r["kind"] == "BOSS_KIND_VISITOR":
            fields += [f'.gateKind = {r["gateKind"]}', f'.gate = {r["gate"]}',
                       ".trainers = {" + ", ".join(r["trainers"]) + "}", f'.female = {"TRUE" if r["female"] else "FALSE"}']
        fields.append(f'.mapsec = {r["mapsec"]}')
        out.append(f'    [{i}] = {{{", ".join(fields)}}}, // {r["place"]}')
    out += ["};", ""]
    starts, n = [], 0
    for name, keys in PAGES:
        starts.append(f"[{PAGE_ENUM[name]}] = {n}")
        n += len(keys)
    starts.append("[BOSS_TRACKER_PAGE_COUNT] = BOSS_TRACKER_ROW_COUNT")
    out += ["// Each page's first row, and the row count",
            "static const u8 sBossTrackerPageStart[BOSS_TRACKER_PAGE_COUNT + 1] =", "{"]
    out += [f"    {s}," for s in starts] + ["};", ""]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    table = rows()
    if len(table) >= 0xFF:  # BOSS_TRACKER_NO_NEXT
        fail("too many rows")
    new = render(table, check_widths(table, layout()))
    old = sb.read(OUTPUT) if os.path.exists(OUTPUT) else ""
    if new == old:
        return 0
    if args.check:
        print(f"{os.path.relpath(OUTPUT, ROOT)} out of date: run tools/crystal_imperium/boss_tracker.py")
        return 1
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"wrote {os.path.relpath(OUTPUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
