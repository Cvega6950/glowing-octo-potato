#!/usr/bin/env python3
"""Crystal Imperium milestone care packages (DECISIONS.md D16): writes data/scripts/care_packages.inc
from the table below.

  python3 tools/crystal_imperium/care_packages.py          # rewrite the script
  python3 tools/crystal_imperium/care_packages.py --check  # exit 1 if it is out of date

A package arrives after each Gym Badge and after becoming Champion (src/care_packages.c): packages
1-8 for the Johto badges, 9 for the Champion, 10-17 for the Kanto badges. Emerald Imperium-style,
each one is full of battle gear: competitive held items (every staple several times over the game,
every type-boosting item, every type-resist and pinch Berry), PP Up and PP Max, X items and Elixirs,
besides Poke Balls, healing and the evolution items found nowhere else in the game. Since 0.11.0
the gear comes in stacks, enough to kit out a whole team (STACKS: 10 of each type-boosting item,
10 Sitrus and Lum Berries, 3 to 5 of each staple held item, 20 Poke Balls of a kind).

The script shows what's inside in one message, wrapped to the message box with the game's own font
widths, then adds the items without a message each. An item whose Bag pocket is full goes to the PC
instead, and the player is told.

Saves from before 0.7.0 received the packages' earlier contents (EARLIER below, the same in every
release that had them). VAR_CARE_PACKAGE_GEAR counts the packages whose battle gear has arrived:
while it is behind VAR_CARE_PACKAGES, the next step brings the gear that package didn't have then.
Saves from 0.7.0 to 0.10.x received GEAR_PACKAGES (the gear one at a time); VAR_CARE_PACKAGE_BULK
counts the packages whose stacks have arrived, and the next step brings the rest of one package.
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

# One list per package: (item without ITEM_, quantity), as received from 0.7.0 to 0.10.x
GEAR_PACKAGES = [
    # 1: Zephyr Badge (cap 16)
    [("POKE_BALL", 10), ("GREAT_BALL", 5), ("SUPER_POTION", 5), ("PP_UP", 5), ("PP_MAX", 3),
     ("LEFTOVERS", 1), ("FOCUS_SASH", 2), ("EVIOLITE", 2), ("SITRUS_BERRY", 5), ("LUM_BERRY", 3),
     ("CHARCOAL", 1), ("MYSTIC_WATER", 1), ("MIRACLE_SEED", 1),
     ("LINKING_CORD", 1), ("SWEET_APPLE", 1), ("TART_APPLE", 1)],
    # 2: Hive Badge (cap 21)
    [("GREAT_BALL", 10), ("REVIVE", 3), ("PP_MAX", 5),
     ("LIFE_ORB", 1), ("EXPERT_BELT", 1), ("MUSCLE_BAND", 1), ("WISE_GLASSES", 1), ("SCOPE_LENS", 1),
     ("MAGNET", 1), ("SHARP_BEAK", 1), ("SILK_SCARF", 1)] + RESIST_BERRIES_1 +
    [("UPGRADE", 1), ("SACHET", 1), ("WHIPPED_DREAM", 1), ("SYRUPY_APPLE", 1)],
    # 3: Plain Badge (cap 25)
    [("ULTRA_BALL", 5), ("HYPER_POTION", 5), ("PP_MAX", 5),
     ("CHOICE_BAND", 1), ("CHOICE_SPECS", 1), ("CHOICE_SCARF", 1), ("ROCKY_HELMET", 1), ("BLACK_SLUDGE", 1),
     ("HARD_STONE", 1), ("SOFT_SAND", 1), ("SPELL_TAG", 1)] + RESIST_BERRIES_2 +
    [("PRISM_SCALE", 1), ("SUN_STONE", 3), ("LINKING_CORD", 1)],
    # 4: Fog Badge (cap 31)
    [("ULTRA_BALL", 5), ("PP_MAX", 5),
     ("ASSAULT_VEST", 2), ("LEFTOVERS", 1), ("TOXIC_ORB", 1), ("FLAME_ORB", 1),
     ("NEVER_MELT_ICE", 1), ("BLACK_BELT", 1), ("TWISTED_SPOON", 1)] + RESIST_BERRIES_3 +
    [("STRAWBERRY_SWEET", 1), ("BERRY_SWEET", 1), ("LOVE_SWEET", 1), ("STAR_SWEET", 1),
     ("CLOVER_SWEET", 1), ("FLOWER_SWEET", 1), ("RIBBON_SWEET", 1)],
    # 5: 5th badge (cap 36)
    [("FULL_HEAL", 5), ("MAX_REVIVE", 1), ("PP_MAX", 5),
     ("HEAVY_DUTY_BOOTS", 2), ("LIGHT_CLAY", 1), ("AIR_BALLOON", 2), ("WHITE_HERB", 2), ("POWER_HERB", 1),
     ("MENTAL_HERB", 1), ("EVIOLITE", 1), ("POISON_BARB", 1), ("SILVER_POWDER", 1), ("DRAGON_FANG", 1),
     ("SITRUS_BERRY", 5), ("LUM_BERRY", 3),
     ("CRACKED_POT", 1), ("CHIPPED_POT", 1), ("UNREMARKABLE_TEACUP", 1), ("MASTERPIECE_TEACUP", 1)],
    # 6: 6th badge (cap 38)
    [("ULTRA_BALL", 10), ("PP_UP", 3), ("PP_MAX", 5), ("MAX_ELIXIR", 3),
     ("WEAKNESS_POLICY", 2), ("LIFE_ORB", 1), ("CHOICE_SCARF", 1), ("RAZOR_CLAW", 1), ("QUICK_CLAW", 1),
     ("SHELL_BELL", 1), ("BIG_ROOT", 1), ("BLACK_GLASSES", 1), ("METAL_COAT", 1), ("FAIRY_FEATHER", 1)] + X_ITEMS +
    [("LEADERS_CREST", 1), ("AUSPICIOUS_ARMOR", 1), ("MALICIOUS_ARMOR", 1)],
    # 7: 7th badge (cap 45)
    [("MAX_POTION", 5), ("MAX_REVIVE", 2), ("PP_MAX", 5),
     ("RED_CARD", 1), ("EJECT_BUTTON", 1), ("EJECT_PACK", 1), ("SAFETY_GOGGLES", 1), ("COVERT_CLOAK", 1),
     ("CLEAR_AMULET", 1), ("PROTECTIVE_PADS", 1), ("SHED_SHELL", 1), ("BINDING_BAND", 1), ("GRIP_CLAW", 1),
     ("DAMP_ROCK", 1), ("HEAT_ROCK", 1), ("SMOOTH_ROCK", 1), ("ICY_ROCK", 1),
     ("X_ACCURACY", 2), ("DIRE_HIT", 2), ("GUARD_SPEC", 2),
     ("METAL_ALLOY", 1), ("LINKING_CORD", 1)],
    # 8: Rising Badge (cap 56)
    [("FULL_RESTORE", 3), ("PP_MAX", 5), ("ABILITY_PATCH", 1),
     ("FOCUS_SASH", 2), ("LEFTOVERS", 1), ("ASSAULT_VEST", 1), ("BOOSTER_ENERGY", 2), ("LOADED_DICE", 1),
     ("PUNCHING_GLOVE", 1), ("MIRROR_HERB", 1), ("THROAT_SPRAY", 1), ("BLUNDER_POLICY", 1),
     ("ELECTRIC_SEED", 1), ("GRASSY_SEED", 1), ("MISTY_SEED", 1), ("PSYCHIC_SEED", 1), ("TERRAIN_EXTENDER", 1),
     ("UTILITY_UMBRELLA", 1), ("ROOM_SERVICE", 1),
     ("GIMMIGHOUL_COIN", 999)],
    # 9: Champion (cap 70)
    [("MASTER_BALL", 1), ("PP_MAX", 10), ("ABILITY_PATCH", 2),
     ("LEFTOVERS", 2), ("LIFE_ORB", 1), ("CHOICE_BAND", 1), ("CHOICE_SPECS", 1), ("CHOICE_SCARF", 1),
     ("SITRUS_BERRY", 10), ("LUM_BERRY", 5), ("LIECHI_BERRY", 2), ("GANLON_BERRY", 2), ("SALAC_BERRY", 2),
     ("PETAYA_BERRY", 2), ("APICOT_BERRY", 2), ("STARF_BERRY", 1), ("LANSAT_BERRY", 1), ("CUSTAP_BERRY", 2),
     ("SCROLL_OF_DARKNESS", 1), ("SCROLL_OF_WATERS", 1)],
    # 10: 9th badge, the first in Kanto
    [("ULTRA_BALL", 10), ("FULL_RESTORE", 3), ("PP_MAX", 5),
     ("ROCKY_HELMET", 1), ("BLACK_SLUDGE", 1), ("ZOOM_LENS", 1), ("WIDE_LENS", 1), ("KINGS_ROCK", 1),
     ("RAZOR_FANG", 1), ("METRONOME", 1), ("LIGHT_BALL", 1), ("THICK_CLUB", 1), ("LEEK", 1), ("LUCKY_PUNCH", 1),
     ("METAL_POWDER", 1), ("QUICK_POWDER", 1), ("DEEP_SEA_TOOTH", 1), ("DEEP_SEA_SCALE", 1),
     ("SUN_STONE", 3)],
    # 11: 10th badge
    [("ULTRA_BALL", 10), ("MAX_REVIVE", 3), ("PP_MAX", 5), ("MAX_ELIXIR", 3),
     ("FOCUS_SASH", 2), ("HEAVY_DUTY_BOOTS", 2), ("AIR_BALLOON", 2), ("TOXIC_ORB", 1), ("FLAME_ORB", 1),
     ("MUSCLE_BAND", 1), ("WISE_GLASSES", 1), ("SCOPE_LENS", 1)],
    # 12: 11th badge
    [("QUICK_BALL", 10), ("FULL_RESTORE", 5), ("PP_MAX", 5),
     ("LEFTOVERS", 1), ("ASSAULT_VEST", 1), ("EXPERT_BELT", 1), ("LUM_BERRY", 3)] + X_ITEMS,
    # 13: 12th badge
    [("DUSK_BALL", 10), ("MAX_ELIXIR", 3), ("PP_MAX", 5), ("ABILITY_PATCH", 1),
     ("LIFE_ORB", 1), ("WEAKNESS_POLICY", 1), ("WHITE_HERB", 2), ("ADRENALINE_ORB", 1), ("ABILITY_SHIELD", 1),
     ("JABOCA_BERRY", 2), ("ROWAP_BERRY", 2), ("KEE_BERRY", 2), ("MARANGA_BERRY", 2)],
    # 14: 13th badge
    [("ULTRA_BALL", 15), ("MAX_REVIVE", 3), ("PP_MAX", 5), ("MAX_ETHER", 5), ("ELIXIR", 5),
     ("CHOICE_BAND", 1), ("CHOICE_SPECS", 1), ("CHOICE_SCARF", 1), ("POWER_HERB", 1), ("MENTAL_HERB", 1),
     ("SITRUS_BERRY", 5)],
    # 15: 14th badge
    [("LUXURY_BALL", 10), ("FULL_RESTORE", 5), ("MAX_ELIXIR", 3), ("PP_MAX", 5),
     ("BOOSTER_ENERGY", 2), ("ROCKY_HELMET", 1), ("COVERT_CLOAK", 1), ("CLEAR_AMULET", 1), ("LOADED_DICE", 1),
     ("EJECT_BUTTON", 1), ("RED_CARD", 1)],
    # 16: 15th badge
    [("MASTER_BALL", 1), ("MAX_REVIVE", 5), ("FULL_RESTORE", 5), ("PP_MAX", 5),
     ("LIGHT_CLAY", 1), ("AIR_BALLOON", 2), ("FOCUS_BAND", 1), ("IRON_BALL", 1), ("LAGGING_TAIL", 1),
     ("STICKY_BARB", 1), ("RING_TARGET", 1), ("ABSORB_BULB", 1), ("CELL_BATTERY", 1), ("SNOWBALL", 1),
     ("LUMINOUS_MOSS", 1)],
    # 17: 16th badge
    [("MASTER_BALL", 1), ("PP_MAX", 10), ("ABILITY_PATCH", 2), ("FULL_RESTORE", 5), ("MAX_ELIXIR", 5),
     ("LEFTOVERS", 1), ("LIFE_ORB", 1), ("FOCUS_SASH", 2), ("ASSAULT_VEST", 1), ("HEAVY_DUTY_BOOTS", 1),
     ("SITRUS_BERRY", 10), ("LUM_BERRY", 5)],
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

# Since 0.12.0, Emerald Imperium-style: a starting package from PROF. ELM as soon as the player has a
# Pokemon (Emerald Imperium's comes from PROF. BIRCH at the start, with the Shiny Charm and the
# type-boosting items), so the type-boosting items, the type-resist Berries and the staples are there
# from the first battles
STARTING = ([("SHINY_CHARM", 1)] + [(item, 10) for item in TYPE_BOOSTERS] + [(berry, 5) for berry in RESIST_BERRIES] +
            [("SITRUS_BERRY", 10), ("LUM_BERRY", 10), ("LEFTOVERS", 3), ("FOCUS_SASH", 5), ("EVIOLITE", 5),
             ("EXPERT_BELT", 3), ("MUSCLE_BAND", 3), ("WISE_GLASSES", 3), ("SCOPE_LENS", 3), ("PP_MAX", 10),
             ("POKE_BALL", 20), ("GREAT_BALL", 10), ("SUPER_POTION", 10), ("REVIVE", 5)])

# ...and location packages along the story, waiting for the player the first time they enter the
# place (Emerald Imperium has them in Granite Cave, on Route 110 and elsewhere), each a themed set of
# gear. (map id, place name, items); src/care_packages.c has the same maps in the same order.
PLACES = [
    ("MAP_UNION_CAVE_1F_HNS", "UNION CAVE",
     [("DAMP_ROCK", 3), ("HEAT_ROCK", 3), ("SMOOTH_ROCK", 3), ("ICY_ROCK", 3), ("UTILITY_UMBRELLA", 2),
      ("SAFETY_GOGGLES", 3)]),
    ("MAP_ILEX_FOREST_HNS", "ILEX FOREST",
     [("LIGHT_CLAY", 3), ("WHITE_HERB", 5), ("POWER_HERB", 5), ("MENTAL_HERB", 5), ("MIRROR_HERB", 3),
      ("BIG_ROOT", 3), ("BLACK_SLUDGE", 2)]),
    ("MAP_NATIONAL_PARK_NORMAL_HNS", "NATIONAL PARK",
     [("CHOICE_BAND", 2), ("CHOICE_SPECS", 2), ("CHOICE_SCARF", 2), ("LIFE_ORB", 3), ("WEAKNESS_POLICY", 3),
      ("BOOSTER_ENERGY", 5)]),
    ("MAP_BURNED_TOWER_1F_HNS", "BURNED TOWER",
     [("TOXIC_ORB", 3), ("FLAME_ORB", 3), ("ROCKY_HELMET", 3), ("ASSAULT_VEST", 3), ("HEAVY_DUTY_BOOTS", 3),
      ("AIR_BALLOON", 5)]),
    ("MAP_OLIVINE_CITY_LIGHTHOUSE_HNS", "the LIGHTHOUSE",
     [("RED_CARD", 3), ("EJECT_BUTTON", 3), ("EJECT_PACK", 3), ("COVERT_CLOAK", 3), ("CLEAR_AMULET", 3),
      ("PROTECTIVE_PADS", 3), ("SHED_SHELL", 3)]),
    ("MAP_MT_MORTAR_1F_SOUTH_HNS", "MT. MORTAR",
     [("LOADED_DICE", 3), ("PUNCHING_GLOVE", 3), ("THROAT_SPRAY", 3), ("BLUNDER_POLICY", 3), ("ROOM_SERVICE", 3),
      ("ADRENALINE_ORB", 3), ("ABILITY_SHIELD", 3), ("METRONOME", 2)]),
    ("MAP_LAKE_OF_RAGE_HNS", "the LAKE OF RAGE",
     [("ELECTRIC_SEED", 5), ("GRASSY_SEED", 5), ("MISTY_SEED", 5), ("PSYCHIC_SEED", 5), ("TERRAIN_EXTENDER", 3)]),
    ("MAP_ICE_PATH_1F_HNS", "the ICE PATH",
     [("PP_MAX", 10), ("MAX_ELIXIR", 5), ("FULL_RESTORE", 5), ("MAX_REVIVE", 5)]),
    ("MAP_VICTORY_ROAD_KANTO_1F_HNS", "VICTORY ROAD",
     [("FULL_RESTORE", 10), ("MAX_REVIVE", 10), ("MAX_ELIXIR", 10), ("ABILITY_PATCH", 3)]),
]

# What each package held before 0.7.0 (every earlier release had these), for the catch-up
EARLIER = [
    [("POKE_BALL", 10), ("GREAT_BALL", 5), ("SUPER_POTION", 5), ("LINKING_CORD", 1), ("SWEET_APPLE", 1),
     ("TART_APPLE", 1)],
    [("GREAT_BALL", 10), ("REVIVE", 3), ("UPGRADE", 1), ("SACHET", 1), ("WHIPPED_DREAM", 1), ("SYRUPY_APPLE", 1)],
    [("ULTRA_BALL", 5), ("HYPER_POTION", 5), ("PRISM_SCALE", 1), ("SUN_STONE", 3), ("LINKING_CORD", 1)],
    [("ULTRA_BALL", 5), ("STRAWBERRY_SWEET", 1), ("BERRY_SWEET", 1), ("LOVE_SWEET", 1), ("STAR_SWEET", 1),
     ("CLOVER_SWEET", 1), ("FLOWER_SWEET", 1), ("RIBBON_SWEET", 1)],
    [("FULL_HEAL", 5), ("MAX_REVIVE", 1), ("CRACKED_POT", 1), ("CHIPPED_POT", 1), ("UNREMARKABLE_TEACUP", 1),
     ("MASTERPIECE_TEACUP", 1)],
    [("ULTRA_BALL", 10), ("PP_UP", 3), ("LEADERS_CREST", 1), ("AUSPICIOUS_ARMOR", 1), ("MALICIOUS_ARMOR", 1)],
    [("MAX_POTION", 5), ("MAX_REVIVE", 2), ("METAL_ALLOY", 1), ("LINKING_CORD", 1)],
    [("FULL_RESTORE", 3), ("ABILITY_PATCH", 1), ("GIMMIGHOUL_COIN", 999)],
    [("MASTER_BALL", 1), ("PP_MAX", 3), ("SCROLL_OF_DARKNESS", 1), ("SCROLL_OF_WATERS", 1)],
    [("ULTRA_BALL", 10), ("FULL_RESTORE", 3), ("SUN_STONE", 3)],
    [("ULTRA_BALL", 10), ("MAX_REVIVE", 3), ("PP_MAX", 2)],
    [("QUICK_BALL", 10), ("FULL_RESTORE", 5)],
    [("DUSK_BALL", 10), ("MAX_ELIXIR", 3), ("ABILITY_PATCH", 1)],
    [("ULTRA_BALL", 15), ("MAX_REVIVE", 3), ("PP_MAX", 2)],
    [("LUXURY_BALL", 10), ("FULL_RESTORE", 5), ("MAX_ELIXIR", 3)],
    [("MASTER_BALL", 1), ("MAX_REVIVE", 5), ("FULL_RESTORE", 5)],
    [("MASTER_BALL", 1), ("PP_MAX", 5), ("ABILITY_PATCH", 2)],
]


def extra(k, before, after, when):
    """What package k (1-17) has in after beyond before, in after's order."""
    had = dict(before[k - 1])
    out = []
    for item, n in after[k - 1]:
        more = n - had.pop(item, 0)
        if more < 0:
            sys.exit(f"package {k}: fewer {item} than {when}")
        if more:
            out.append((item, more))
    if had:
        sys.exit(f"package {k}: no longer has {sorted(had)}")
    return out


def gear(k):
    """The battle gear package k didn't have before 0.7.0."""
    return extra(k, EARLIER, GEAR_PACKAGES, "before 0.7.0")


def bulk(k):
    """The stacks package k didn't have before 0.11.0."""
    return extra(k, GEAR_PACKAGES, PACKAGES, "before 0.11.0")


HEADER = """\
@ Generated by tools/crystal_imperium/care_packages.py from its table: edit that, not this file.
@ Crystal Imperium: milestone care packages from PROF. ELM (DECISIONS.md D16).
@ src/care_packages.c starts EventScript_CarePackage on the player's next step after a milestone:
@ each Gym Badge and becoming Champion. VAR_CARE_PACKAGES counts the packages received; while
@ milestones are ahead of it, the next package arrives (so a save from an older build catches up
@ one package per step). Packages 1-8: Johto badges, 9: Champion, 10-17: Kanto badges.
@ Each package lists its contents in one message, then the items go to the Bag; one whose pocket
@ is full goes to the PC (VAR_0x8005 counts those).
@ EventScript_CarePackageGear brings a save from before 0.7.0 the battle gear its packages didn't
@ have then, one package per step (VAR_CARE_PACKAGE_GEAR counts the packages whose gear arrived);
@ EventScript_CarePackageBulk then brings a save from before 0.11.0 the rest of each package's stacks
@ (VAR_CARE_PACKAGE_BULK).
@ Since 0.12.0, EventScript_CarePackageStart is the starting package (once the player has a Pokemon)
@ and EventScript_CarePackagePlace the location package VAR_0x8004 names (the first time the player
@ enters its place); VAR_CARE_PACKAGE_PLACES has a bit for each, set by src/care_packages.c.
"""


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
    "CarePackage_Text_Arrived": ["A care package from PROF. ELM", "arrived for your progress!"],
    "CarePackage_Text_Champion": ["PROF. ELM: Congratulations,", "CHAMPION!",
                                  "Word is that rare and legendary {PKMN}", "now show up in the wild!"],
    "CarePackage_Text_GearArrived": ["PROF. ELM sent the battle gear", "an earlier package didn't have!"],
    "CarePackage_Text_BulkArrived": ["PROF. ELM sent more of the gear", "from an earlier package!"],
    "CarePackage_Text_SentToPC": ["Your BAG was full, so some of it", "was sent to your PC."],
    "CarePackage_Text_StartArrived": ["PROF. ELM sent a care package", "to start your journey!"],
}


def message_lines(lines, widths):
    out = []
    for i, line in enumerate(lines):
        if text_width(line.replace("{PKMN}", "PK"), widths) > LINE_WIDTH:
            sys.exit(f"message line too wide: {line}")
        end = "$" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p")
        out.append(f'\t.string "{line}{end}"')
    return out


def render():
    names, widths = item_names(), glyph_widths()
    for k, items in enumerate(PACKAGES, 1):
        for item, n in items:
            if "ITEM_" + item not in names:
                sys.exit(f"package {k}: unknown item ITEM_{item}")
    if len(EARLIER) != len(PACKAGES):
        sys.exit("EARLIER needs one entry per package")
    if len(GEAR_PACKAGES) != len(PACKAGES):
        sys.exit("GEAR_PACKAGES needs one entry per package")
    for label, items in [("starting", STARTING)] + [(name, items) for _, name, items in PLACES]:
        for item, n in items:
            if "ITEM_" + item not in names:
                sys.exit(f"{label} package: unknown item ITEM_{item}")
    gears = [gear(k) for k in range(1, len(PACKAGES) + 1)]
    bulks = [bulk(k) for k in range(1, len(PACKAGES) + 1)]
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
            "CarePackage_Done::", "\taddvar VAR_CARE_PACKAGES, 1", "\tcopyvar VAR_CARE_PACKAGE_GEAR, VAR_CARE_PACKAGES",
            "\tcopyvar VAR_CARE_PACKAGE_BULK, VAR_CARE_PACKAGES", "\treleaseall", "\tend", ""]
    out += ["EventScript_CarePackageGear::", "\tlockall", "\tplayse SE_EXP_MAX",
            "\tmsgbox CarePackage_Text_GearArrived, MSGBOX_DEFAULT", "\tsetvar VAR_0x8005, 0",
            "\tswitch VAR_CARE_PACKAGE_GEAR"]
    out += [f"\tcase {k - 1}, CarePackageGear_{k}" for k in range(1, len(PACKAGES) + 1)]
    out += ["\tgoto CarePackageGear_Done", ""]
    for k, items in enumerate(gears, 1):
        out += [f"CarePackageGear_{k}::", "\tplayfanfare MUS_OBTAIN_ITEM",
                f"\tmsgbox CarePackageGear_Text_{k}, MSGBOX_DEFAULT", "\twaitfanfare"]
        out += item_lines(items, "CarePackageGear_End")
    out += ["CarePackageGear_End:", "\tgoto_if_eq VAR_0x8005, 0, CarePackageGear_Done",
            "\tmsgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT",
            "CarePackageGear_Done::", "\taddvar VAR_CARE_PACKAGE_GEAR, 1", "\treleaseall", "\tend", ""]
    out += ["EventScript_CarePackageBulk::", "\tlockall", "\tplayse SE_EXP_MAX",
            "\tmsgbox CarePackage_Text_BulkArrived, MSGBOX_DEFAULT", "\tsetvar VAR_0x8005, 0",
            "\tswitch VAR_CARE_PACKAGE_BULK"]
    out += [f"\tcase {k - 1}, CarePackageBulk_{k}" for k in range(1, len(PACKAGES) + 1) if bulks[k - 1]]
    out += ["\tgoto CarePackageBulk_Done", ""]
    for k, items in enumerate(bulks, 1):
        if not items:
            continue
        out += [f"CarePackageBulk_{k}::", "\tplayfanfare MUS_OBTAIN_ITEM",
                f"\tmsgbox CarePackageBulk_Text_{k}, MSGBOX_DEFAULT", "\twaitfanfare"]
        out += item_lines(items, "CarePackageBulk_End")
    out += ["CarePackageBulk_End:", "\tgoto_if_eq VAR_0x8005, 0, CarePackageBulk_Done",
            "\tmsgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT",
            "CarePackageBulk_Done::", "\taddvar VAR_CARE_PACKAGE_BULK, 1", "\treleaseall", "\tend", ""]
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
    for item, n in sorted({(item, n) for items in PACKAGES + gears + bulks + extras for item, n in items}):
        out += [f"{pc_label(item, n)}:", f"\taddpcitem ITEM_{item}, {n}", "\taddvar VAR_0x8005, 1", "\treturn", ""]
    for label, lines in MESSAGES.items():
        out += [f"{label}:"] + message_lines(lines, widths) + [""]
    out += ["CarePackageStart_Text:"] + contents_text(STARTING, names, widths) + [""]
    for k, (_, name, items) in enumerate(PLACES):
        out += [f"CarePackagePlace_Text_Arrived_{k}:"] + message_lines(
            ["A care package from PROF. ELM", f"was waiting in {name}!"], widths) + [""]
        out += [f"CarePackagePlace_Text_{k}:"] + contents_text(items, names, widths) + [""]
    for k, items in enumerate(PACKAGES, 1):
        out += [f"CarePackage_Text_{k}:"] + contents_text(items, names, widths) + [""]
    for k, items in enumerate(gears, 1):
        out += [f"CarePackageGear_Text_{k}:"] + contents_text(items, names, widths) + [""]
    for k, items in enumerate(bulks, 1):
        if items:
            out += [f"CarePackageBulk_Text_{k}:"] + contents_text(items, names, widths) + [""]
    return "\n".join(out).rstrip("\n") + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    new = render()
    old = read(SCRIPT) if os.path.exists(SCRIPT) else ""
    if args.check:
        if new != old:
            print("data/scripts/care_packages.inc is out of date: run tools/crystal_imperium/care_packages.py")
            return 1
        return 0
    if new != old:
        with open(SCRIPT, "w", encoding="utf-8") as f:
            f.write(new)
        total = sum(len(p) for p in PACKAGES)
        print(f"wrote {os.path.relpath(SCRIPT, ROOT)}: {len(PACKAGES)} packages, {total} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
