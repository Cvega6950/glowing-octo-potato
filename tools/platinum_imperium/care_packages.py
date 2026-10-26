#!/usr/bin/env python3
"""Platinum Imperium care packages: writes data/scripts/care_packages.inc from the tables below.

  python3 tools/platinum_imperium/care_packages.py          # rewrite the script
  python3 tools/platinum_imperium/care_packages.py --check  # exit 1 if it is out of date

Crystal Imperium's care packages (its tools/crystal_imperium/care_packages.py), from PROF. ROWAN,
the Emerald Imperium way: a starting package as soon as the player has a Pokemon (the Shiny Charm,
10 of every type-boosting item, every type-resist Berry, a starter kit of held items), location
packages waiting in places along the story, each a themed set of gear, and a package after each
Gym Badge and after becoming Champion (Crystal Imperium's first nine, in stacks).

The script shows what's inside in one message, wrapped to the message box with the game's own font
widths, then adds the items without a message each. An item whose Bag pocket is full goes to the PC
instead, and the player is told. src/care_packages.c starts the scripts.
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPT = os.path.join(ROOT, "data", "scripts", "care_packages.inc")

# Message box: 27 tiles (216 px) of FONT_NORMAL; lines are kept clear of the "more" arrow
LINE_WIDTH = 200

RESIST_BERRIES_1 = [("OCCA_BERRY", 2), ("PASSHO_BERRY", 2), ("WACAN_BERRY", 2), ("RINDO_BERRY", 2),
                    ("YACHE_BERRY", 2), ("CHOPLE_BERRY", 2)]
RESIST_BERRIES_2 = [("KEBIA_BERRY", 2), ("SHUCA_BERRY", 2), ("COBA_BERRY", 2), ("PAYAPA_BERRY", 2),
                    ("TANGA_BERRY", 2), ("CHARTI_BERRY", 2)]
RESIST_BERRIES_3 = [("KASIB_BERRY", 2), ("HABAN_BERRY", 2), ("COLBUR_BERRY", 2), ("BABIRI_BERRY", 2),
                    ("CHILAN_BERRY", 2), ("ROSELI_BERRY", 2)]
X_ITEMS = [("X_ATTACK", 3), ("X_SP_ATK", 3), ("X_SPEED", 3), ("X_DEFENSE", 3), ("X_SP_DEF", 3)]

# One list per package: (item without ITEM_, quantity), Crystal Imperium's packages 1-9
GEAR_PACKAGES = [
    # 1: Coal Badge (Roark)
    [("POKE_BALL", 10), ("GREAT_BALL", 5), ("SUPER_POTION", 5), ("PP_UP", 5), ("PP_MAX", 3),
     ("LEFTOVERS", 1), ("FOCUS_SASH", 2), ("EVIOLITE", 2), ("SITRUS_BERRY", 5), ("LUM_BERRY", 3),
     ("CHARCOAL", 1), ("MYSTIC_WATER", 1), ("MIRACLE_SEED", 1),
     ("LINKING_CORD", 1), ("SWEET_APPLE", 1), ("TART_APPLE", 1)],
    # 2: Forest Badge (Gardenia)
    [("GREAT_BALL", 10), ("REVIVE", 3), ("PP_MAX", 5),
     ("LIFE_ORB", 1), ("EXPERT_BELT", 1), ("MUSCLE_BAND", 1), ("WISE_GLASSES", 1), ("SCOPE_LENS", 1),
     ("MAGNET", 1), ("SHARP_BEAK", 1), ("SILK_SCARF", 1)] + RESIST_BERRIES_1 +
    [("UPGRADE", 1), ("SACHET", 1), ("WHIPPED_DREAM", 1), ("SYRUPY_APPLE", 1)],
    # 3: Relic Badge (Fantina)
    [("ULTRA_BALL", 5), ("HYPER_POTION", 5), ("PP_MAX", 5),
     ("CHOICE_BAND", 1), ("CHOICE_SPECS", 1), ("CHOICE_SCARF", 1), ("ROCKY_HELMET", 1), ("BLACK_SLUDGE", 1),
     ("HARD_STONE", 1), ("SOFT_SAND", 1), ("SPELL_TAG", 1)] + RESIST_BERRIES_2 +
    [("PRISM_SCALE", 1), ("SUN_STONE", 3), ("LINKING_CORD", 1)],
    # 4: Cobble Badge (Maylene)
    [("ULTRA_BALL", 5), ("PP_MAX", 5),
     ("ASSAULT_VEST", 2), ("LEFTOVERS", 1), ("TOXIC_ORB", 1), ("FLAME_ORB", 1),
     ("NEVER_MELT_ICE", 1), ("BLACK_BELT", 1), ("TWISTED_SPOON", 1)] + RESIST_BERRIES_3 +
    [("STRAWBERRY_SWEET", 1), ("BERRY_SWEET", 1), ("LOVE_SWEET", 1), ("STAR_SWEET", 1),
     ("CLOVER_SWEET", 1), ("FLOWER_SWEET", 1), ("RIBBON_SWEET", 1)],
    # 5: Fen Badge (Crasher Wake)
    [("FULL_HEAL", 5), ("MAX_REVIVE", 1), ("PP_MAX", 5),
     ("HEAVY_DUTY_BOOTS", 2), ("LIGHT_CLAY", 1), ("AIR_BALLOON", 2), ("WHITE_HERB", 2), ("POWER_HERB", 1),
     ("MENTAL_HERB", 1), ("EVIOLITE", 1), ("POISON_BARB", 1), ("SILVER_POWDER", 1), ("DRAGON_FANG", 1),
     ("SITRUS_BERRY", 5), ("LUM_BERRY", 3),
     ("CRACKED_POT", 1), ("CHIPPED_POT", 1), ("UNREMARKABLE_TEACUP", 1), ("MASTERPIECE_TEACUP", 1)],
    # 6: Mine Badge (Byron)
    [("ULTRA_BALL", 10), ("PP_UP", 3), ("PP_MAX", 5), ("MAX_ELIXIR", 3),
     ("WEAKNESS_POLICY", 2), ("LIFE_ORB", 1), ("CHOICE_SCARF", 1), ("RAZOR_CLAW", 1), ("QUICK_CLAW", 1),
     ("SHELL_BELL", 1), ("BIG_ROOT", 1), ("BLACK_GLASSES", 1), ("METAL_COAT", 1), ("FAIRY_FEATHER", 1)] + X_ITEMS +
    [("LEADERS_CREST", 1), ("AUSPICIOUS_ARMOR", 1), ("MALICIOUS_ARMOR", 1)],
    # 7: Icicle Badge (Candice)
    [("MAX_POTION", 5), ("MAX_REVIVE", 2), ("PP_MAX", 5),
     ("RED_CARD", 1), ("EJECT_BUTTON", 1), ("EJECT_PACK", 1), ("SAFETY_GOGGLES", 1), ("COVERT_CLOAK", 1),
     ("CLEAR_AMULET", 1), ("PROTECTIVE_PADS", 1), ("SHED_SHELL", 1), ("BINDING_BAND", 1), ("GRIP_CLAW", 1),
     ("DAMP_ROCK", 1), ("HEAT_ROCK", 1), ("SMOOTH_ROCK", 1), ("ICY_ROCK", 1),
     ("X_ACCURACY", 2), ("DIRE_HIT", 2), ("GUARD_SPEC", 2),
     ("METAL_ALLOY", 1), ("LINKING_CORD", 1)],
    # 8: Beacon Badge (Volkner)
    [("FULL_RESTORE", 3), ("PP_MAX", 5), ("ABILITY_PATCH", 1),
     ("FOCUS_SASH", 2), ("LEFTOVERS", 1), ("ASSAULT_VEST", 1), ("BOOSTER_ENERGY", 2), ("LOADED_DICE", 1),
     ("PUNCHING_GLOVE", 1), ("MIRROR_HERB", 1), ("THROAT_SPRAY", 1), ("BLUNDER_POLICY", 1),
     ("ELECTRIC_SEED", 1), ("GRASSY_SEED", 1), ("MISTY_SEED", 1), ("PSYCHIC_SEED", 1), ("TERRAIN_EXTENDER", 1),
     ("UTILITY_UMBRELLA", 1), ("ROOM_SERVICE", 1),
     ("GIMMIGHOUL_COIN", 999)],
    # 9: Champion
    [("MASTER_BALL", 1), ("PP_MAX", 10), ("ABILITY_PATCH", 2),
     ("LEFTOVERS", 2), ("LIFE_ORB", 1), ("CHOICE_BAND", 1), ("CHOICE_SPECS", 1), ("CHOICE_SCARF", 1),
     ("SITRUS_BERRY", 10), ("LUM_BERRY", 5), ("LIECHI_BERRY", 2), ("GANLON_BERRY", 2), ("SALAC_BERRY", 2),
     ("PETAYA_BERRY", 2), ("APICOT_BERRY", 2), ("STARF_BERRY", 1), ("LANSAT_BERRY", 1), ("CUSTAP_BERRY", 2),
     ("SCROLL_OF_DARKNESS", 1), ("SCROLL_OF_WATERS", 1)],
]

# Since 0.11.0 each item comes at least this many times (Emerald Imperium-style stacks)
TYPE_BOOSTERS = ["CHARCOAL", "MYSTIC_WATER", "MIRACLE_SEED", "MAGNET", "SHARP_BEAK", "SILK_SCARF", "HARD_STONE",
                 "SOFT_SAND", "SPELL_TAG", "NEVER_MELT_ICE", "BLACK_BELT", "TWISTED_SPOON", "POISON_BARB",
                 "SILVER_POWDER", "DRAGON_FANG", "BLACK_GLASSES", "METAL_COAT", "FAIRY_FEATHER"]
RESIST_BERRIES = [b for b, _ in RESIST_BERRIES_1 + RESIST_BERRIES_2 + RESIST_BERRIES_3]
STACKS = dict(
    [(item, 10) for item in TYPE_BOOSTERS] + [(berry, 5) for berry in RESIST_BERRIES] +
    [(ball, 20) for ball in ("POKE_BALL", "GREAT_BALL", "ULTRA_BALL", "QUICK_BALL", "DUSK_BALL", "LUXURY_BALL")] +
    [(med, 10) for med in ("SUPER_POTION", "HYPER_POTION", "MAX_POTION", "FULL_RESTORE", "FULL_HEAL", "ELIXIR",
                           "MAX_ETHER", "PP_MAX")] +
    [(med, 5) for med in ("REVIVE", "MAX_REVIVE", "MAX_ELIXIR", "PP_UP")] +
    [(x, 5) for x in ("X_ATTACK", "X_SP_ATK", "X_SPEED", "X_DEFENSE", "X_SP_DEF", "X_ACCURACY", "DIRE_HIT", "GUARD_SPEC")] +
    [("SITRUS_BERRY", 10), ("LUM_BERRY", 10)] +
    [(berry, 5) for berry in ("LIECHI_BERRY", "GANLON_BERRY", "SALAC_BERRY", "PETAYA_BERRY", "APICOT_BERRY",
                              "CUSTAP_BERRY", "JABOCA_BERRY", "ROWAP_BERRY", "KEE_BERRY", "MARANGA_BERRY")] +
    [("STARF_BERRY", 3), ("LANSAT_BERRY", 3)] +
    # Held items that are used up, then the ones a team wants several of
    [(item, 5) for item in ("FOCUS_SASH", "EVIOLITE", "AIR_BALLOON", "WHITE_HERB", "POWER_HERB", "MENTAL_HERB",
                            "RED_CARD", "EJECT_BUTTON", "EJECT_PACK", "WEAKNESS_POLICY", "BOOSTER_ENERGY",
                            "MIRROR_HERB", "THROAT_SPRAY", "BLUNDER_POLICY", "ROOM_SERVICE", "ADRENALINE_ORB",
                            "ELECTRIC_SEED", "GRASSY_SEED", "MISTY_SEED", "PSYCHIC_SEED", "ABSORB_BULB",
                            "CELL_BATTERY", "SNOWBALL", "LUMINOUS_MOSS")] +
    [(item, 3) for item in ("LEFTOVERS", "LIFE_ORB", "ASSAULT_VEST", "ROCKY_HELMET", "HEAVY_DUTY_BOOTS",
                            "EXPERT_BELT", "MUSCLE_BAND", "WISE_GLASSES", "SCOPE_LENS", "LIGHT_CLAY", "TOXIC_ORB",
                            "FLAME_ORB", "SAFETY_GOGGLES", "COVERT_CLOAK", "CLEAR_AMULET", "PROTECTIVE_PADS",
                            "SHED_SHELL", "DAMP_ROCK", "HEAT_ROCK", "SMOOTH_ROCK", "ICY_ROCK", "QUICK_CLAW",
                            "SHELL_BELL", "BIG_ROOT", "LOADED_DICE", "PUNCHING_GLOVE", "TERRAIN_EXTENDER",
                            "UTILITY_UMBRELLA", "ABILITY_SHIELD", "ABILITY_PATCH")] +
    [(item, 2) for item in ("CHOICE_BAND", "CHOICE_SPECS", "CHOICE_SCARF", "BLACK_SLUDGE", "RAZOR_CLAW",
                            "BINDING_BAND", "GRIP_CLAW", "ZOOM_LENS", "WIDE_LENS", "KINGS_ROCK", "RAZOR_FANG",
                            "METRONOME", "FOCUS_BAND", "IRON_BALL", "LAGGING_TAIL", "STICKY_BARB", "RING_TARGET")])

PACKAGES = [[(item, max(n, STACKS.get(item, 0))) for item, n in package] for package in GEAR_PACKAGES]

PACKAGES = [[(item, max(n, STACKS.get(item, 0))) for item, n in package] for package in GEAR_PACKAGES]

# Since 0.12.0, Emerald Imperium-style: a starting package from PROF. ROWAN as soon as the player has a
# Pokemon (Emerald Imperium's comes from PROF. BIRCH at the start, with the Shiny Charm and the
# type-boosting items), so the type-boosting items, the type-resist Berries and the staples are there
# from the first battles
STARTING = ([("SHINY_CHARM", 1)] + [(item, 10) for item in TYPE_BOOSTERS] + [(berry, 5) for berry in RESIST_BERRIES] +
            [("SITRUS_BERRY", 10), ("LUM_BERRY", 10), ("LEFTOVERS", 3), ("FOCUS_SASH", 5), ("EVIOLITE", 5),
             ("EXPERT_BELT", 3), ("MUSCLE_BAND", 3), ("WISE_GLASSES", 3), ("SCOPE_LENS", 3), ("PP_MAX", 10),
             ("POKE_BALL", 20), ("GREAT_BALL", 10), ("SUPER_POTION", 10), ("REVIVE", 5)])

# ...and location packages, waiting for the player the first time they enter the place (Emerald
# Imperium has them in Granite Cave, on Route 110 and elsewhere), each a themed set of gear. (map id,
# place name, items); src/care_packages.c has the same maps in the same order. Only the places this
# game has so far: more come with the rest of Sinnoh.
PLACES = [
    ("MAP_OREBURGH_MINE_B1F", "OREBURGH MINE",
     [("DAMP_ROCK", 3), ("HEAT_ROCK", 3), ("SMOOTH_ROCK", 3), ("ICY_ROCK", 3), ("UTILITY_UMBRELLA", 2),
      ("SAFETY_GOGGLES", 3)]),
    ("MAP_RAVAGED_PATH", "RAVAGED PATH",
     [("LIGHT_CLAY", 3), ("WHITE_HERB", 5), ("POWER_HERB", 5), ("MENTAL_HERB", 5), ("MIRROR_HERB", 3),
      ("BIG_ROOT", 3), ("BLACK_SLUDGE", 2)]),
    ("MAP_VALLEY_WINDWORKS", "VALLEY WINDWORKS",
     [("CHOICE_BAND", 2), ("CHOICE_SPECS", 2), ("CHOICE_SCARF", 2), ("LIFE_ORB", 3), ("WEAKNESS_POLICY", 3),
      ("BOOSTER_ENERGY", 5)]),
    ("MAP_ETERNA_FOREST_1", "ETERNA FOREST",
     [("TOXIC_ORB", 3), ("FLAME_ORB", 3), ("ROCKY_HELMET", 3), ("ASSAULT_VEST", 3), ("HEAVY_DUTY_BOOTS", 3),
      ("AIR_BALLOON", 5)]),
    ("MAP_MT_CORONET_N1F1", "MT. CORONET",
     [("RED_CARD", 3), ("EJECT_BUTTON", 3), ("EJECT_PACK", 3), ("COVERT_CLOAK", 3), ("CLEAR_AMULET", 3),
      ("PROTECTIVE_PADS", 3), ("SHED_SHELL", 3)]),
]


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def item_names():
    """ITEM_X -> its in-game name, from src/data/items.h."""
    names = {}
    for m in re.finditer(r"\[(ITEM_\w+)\]\s*=\s*\{(.*?)\n    \}", read("src/data/items.h"), re.S):
        n = re.search(r'\.name\s*=\s*ITEM_NAME\("([^"]*)"\)', m.group(2))
        if n:
            names[m.group(1)] = n.group(1)
    return names


def glyph_widths():
    """Character -> width in pixels in FONT_NORMAL (src/fonts.c), through charmap.txt."""
    table = re.search(r"gFontNormalLatinGlyphWidths\[\]\s*=\s*\{(.*?)\};", read("src/fonts.c"), re.S).group(1)
    widths = [int(v) for v in re.findall(r"\d+", table)]
    chars = {}
    for line in read("charmap.txt").splitlines():
        m = re.match(r"'(\\'|[^'])'\s*=\s*([0-9A-Fa-f]{2})\s*$", line)
        if m:
            chars.setdefault(m.group(1).replace("\\'", "'"), widths[int(m.group(2), 16)])
    return chars


def text_width(text, widths):
    return sum(widths[c] for c in text)


def contents_text(items, names, widths):
    """The package's contents as message lines: two lines a page, each within LINE_WIDTH."""
    words = [names["ITEM_" + item] + (f" ×{n}" if n > 1 else "") for item, n in items]
    words = [w + "," for w in words[:-1]] + [words[-1] + "."]
    words[0] = "Inside: " + words[0]
    lines, line = [], ""
    for w in words:
        candidate = (line + " " + w) if line else w
        if text_width(candidate, widths) <= LINE_WIDTH:
            line = candidate
        else:
            lines.append(line)
            line = w
    lines.append(line)
    out = []
    for i, line in enumerate(lines):
        end = "$" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p")
        out.append(f'\t.string "{line}{end}"')
    return out


def pc_label(item, n):
    return f"CarePackage_ToPC_{item}_{n}"


def item_lines(items, end_label):
    """additem for each item, each followed by its PC fallback, then a jump to end_label."""
    out = []
    for item, n in items:
        out += [f"\tadditem ITEM_{item}, {n}", f"\tcall_if_eq VAR_RESULT, FALSE, {pc_label(item, n)}"]
    return out + [f"\tgoto {end_label}", ""]


# Fixed messages: label -> lines (the last ends the message)
MESSAGES = {
    "CarePackage_Text_Arrived": ["A care package from PROF. ROWAN", "arrived for your progress!"],
    "CarePackage_Text_Champion": ["PROF. ROWAN: Congratulations,", "CHAMPION!",
                                  "Word is that rare and legendary {PKMN}", "now show up in the wild!"],
    "CarePackage_Text_SentToPC": ["Your BAG was full, so some of it", "was sent to your PC."],
    "CarePackage_Text_StartArrived": ["PROF. ROWAN sent a care package", "to start your journey!"],
}


def message_lines(lines, widths):
    out = []
    for i, line in enumerate(lines):
        if text_width(line.replace("{PKMN}", "PK"), widths) > LINE_WIDTH:
            sys.exit(f"message line too wide: {line}")
        end = "$" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p")
        out.append(f'\t.string "{line}{end}"')
    return out


HEADER = """\
@ Generated by tools/platinum_imperium/care_packages.py from its tables: edit that, not this file.
@ Platinum Imperium: care packages from PROF. ROWAN. src/care_packages.c starts them on a step:
@ EventScript_CarePackageStart (once the player has a Pokemon), EventScript_CarePackagePlace (the
@ location package VAR_0x8004 names, the first time the player enters its place; a bit each in
@ VAR_CARE_PACKAGE_PLACES), and EventScript_CarePackage after each milestone (each Gym Badge and
@ becoming Champion; VAR_CARE_PACKAGES counts them). Each package lists its contents in one message,
@ then the items go to the Bag; one whose pocket is full goes to the PC (VAR_0x8005 counts those).
"""


def render():
    names, widths = item_names(), glyph_widths()
    for label, items in ([(f"package {k}", p) for k, p in enumerate(PACKAGES, 1)] + [("starting", STARTING)]
                         + [(name, items) for _, name, items in PLACES]):
        for item, n in items:
            if "ITEM_" + item not in names:
                sys.exit(f"{label}: unknown item ITEM_{item}")
    out = HEADER.splitlines()
    out += ["EventScript_CarePackage::", "\tlockall", "\tplayse SE_EXP_MAX",
            "\tmsgbox CarePackage_Text_Arrived, MSGBOX_DEFAULT", "\tsetvar VAR_0x8005, 0",
            "\tswitch VAR_CARE_PACKAGES"]
    out += [f"\tcase {k - 1}, CarePackage_{k}" for k in range(1, len(PACKAGES) + 1)]
    out += ["\tgoto CarePackage_Done", ""]
    for k, items in enumerate(PACKAGES, 1):
        out.append(f"CarePackage_{k}::")
        if k == 9:
            out += ["\tgoto_if_unset FLAG_SYS_GAME_CLEAR, CarePackage_9_Items",
                    "\tmsgbox CarePackage_Text_Champion, MSGBOX_DEFAULT", "CarePackage_9_Items:"]
        out += ["\tplayfanfare MUS_OBTAIN_ITEM", f"\tmsgbox CarePackage_Text_{k}, MSGBOX_DEFAULT", "\twaitfanfare"]
        out += item_lines(items, "CarePackage_End")
    out += ["CarePackage_End:", "\tgoto_if_eq VAR_0x8005, 0, CarePackage_Done",
            "\tmsgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT",
            "CarePackage_Done::", "\taddvar VAR_CARE_PACKAGES, 1", "\treleaseall", "\tend", ""]
    out += ["EventScript_CarePackageStart::", "\tlockall", "\tplayse SE_EXP_MAX",
            "\tmsgbox CarePackage_Text_StartArrived, MSGBOX_DEFAULT", "\tsetvar VAR_0x8005, 0",
            "\tplayfanfare MUS_OBTAIN_ITEM", "\tmsgbox CarePackageStart_Text, MSGBOX_DEFAULT", "\twaitfanfare"]
    out += item_lines(STARTING, "CarePackagePlace_End")
    out += ["EventScript_CarePackagePlace::", "\tlockall", "\tplayse SE_EXP_MAX", "\tsetvar VAR_0x8005, 0",
            "\tswitch VAR_0x8004"]
    out += [f"\tcase {k}, CarePackagePlace_{k}" for k in range(len(PLACES))]
    out += ["\tgoto CarePackagePlace_Done", ""]
    for k, (_, name, items) in enumerate(PLACES):
        out += [f"CarePackagePlace_{k}::", f"\tmsgbox CarePackagePlace_Text_Arrived_{k}, MSGBOX_DEFAULT",
                "\tplayfanfare MUS_OBTAIN_ITEM", f"\tmsgbox CarePackagePlace_Text_{k}, MSGBOX_DEFAULT", "\twaitfanfare"]
        out += item_lines(items, "CarePackagePlace_End")
    out += ["CarePackagePlace_End:", "\tgoto_if_eq VAR_0x8005, 0, CarePackagePlace_Done",
            "\tmsgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT",
            "CarePackagePlace_Done::", "\treleaseall", "\tend", ""]
    extras = [STARTING] + [items for _, _, items in PLACES]
    for item, n in sorted({(item, n) for items in PACKAGES + extras for item, n in items}):
        out += [f"{pc_label(item, n)}:", f"\taddpcitem ITEM_{item}, {n}", "\taddvar VAR_0x8005, 1", "\treturn", ""]
    for label, lines in MESSAGES.items():
        out += [f"{label}:"] + message_lines(lines, widths) + [""]
    out += ["CarePackageStart_Text:"] + contents_text(STARTING, names, widths) + [""]
    for k, (_, name, items) in enumerate(PLACES):
        out += [f"CarePackagePlace_Text_Arrived_{k}:"] + message_lines(
            ["A care package from PROF. ROWAN", f"was waiting in {name}!"], widths) + [""]
        out += [f"CarePackagePlace_Text_{k}:"] + contents_text(items, names, widths) + [""]
    for k, items in enumerate(PACKAGES, 1):
        out += [f"CarePackage_Text_{k}:"] + contents_text(items, names, widths) + [""]
    return "\n".join(out).rstrip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    new = render()
    old = read(SCRIPT) if os.path.exists(SCRIPT) else ""
    if args.check:
        if new != old:
            print("data/scripts/care_packages.inc is out of date: run tools/platinum_imperium/care_packages.py")
            return 1
        return 0
    if new != old:
        with open(SCRIPT, "w", encoding="utf-8") as f:
            f.write(new)
        total = sum(len(p) for p in PACKAGES)
        print(f"wrote {os.path.relpath(SCRIPT, ROOT)}: {len(PACKAGES)} badge packages, {total} entries, "
              f"a starting package and {len(PLACES)} location packages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
