#!/usr/bin/env python3
"""Crystal Imperium milestone care packages (DECISIONS.md D16): writes data/scripts/care_packages.inc
from the table below.

  python3 tools/crystal_imperium/care_packages.py          # rewrite the script
  python3 tools/crystal_imperium/care_packages.py --check  # exit 1 if it is out of date

A package arrives after each Gym Badge and after becoming Champion (src/care_packages.c): packages
1-8 for the Johto badges, 9 for the Champion, 10-17 for the Kanto badges. Emerald Imperium-style,
each one is full of battle gear: competitive held items (every staple several times over the game,
every type-boosting item, every type-resist and pinch Berry), PP Up and PP Max, X items and Elixirs,
besides Poke Balls, healing and the evolution items found nowhere else in the game.

The script shows what's inside in one message, wrapped to the message box with the game's own font
widths, then adds the items without a message each. An item whose Bag pocket is full goes to the PC
instead, and the player is told.

Saves from before 0.7.0 received the packages' earlier contents (EARLIER below, the same in every
release that had them). VAR_CARE_PACKAGE_GEAR counts the packages whose battle gear has arrived:
while it is behind VAR_CARE_PACKAGES, the next step brings the gear that package didn't have then.
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

# One list per package: (item without ITEM_, quantity)
PACKAGES = [
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


def gear(k):
    """What package k (1-17) has beyond its EARLIER contents, in PACKAGES order."""
    earlier = dict(EARLIER[k - 1])
    out = []
    for item, n in PACKAGES[k - 1]:
        extra = n - earlier.pop(item, 0)
        if extra < 0:
            sys.exit(f"package {k}: fewer {item} than before 0.7.0")
        if extra:
            out.append((item, extra))
    if earlier:
        sys.exit(f"package {k}: no longer has {sorted(earlier)}")
    return out


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
@ have then, one package per step (VAR_CARE_PACKAGE_GEAR counts the packages whose gear arrived).
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
    "CarePackage_Text_SentToPC": ["Your BAG was full, so some of it", "was sent to your PC."],
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
    gears = [gear(k) for k in range(1, len(PACKAGES) + 1)]
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
            "\treleaseall", "\tend", ""]
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
    for item, n in sorted({(item, n) for items in PACKAGES + gears for item, n in items}):
        out += [f"{pc_label(item, n)}:", f"\taddpcitem ITEM_{item}, {n}", "\taddvar VAR_0x8005, 1", "\treturn", ""]
    for label, lines in MESSAGES.items():
        out += [f"{label}:"] + message_lines(lines, widths) + [""]
    for k, items in enumerate(PACKAGES, 1):
        out += [f"CarePackage_Text_{k}:"] + contents_text(items, names, widths) + [""]
    for k, items in enumerate(gears, 1):
        out += [f"CarePackageGear_Text_{k}:"] + contents_text(items, names, widths) + [""]
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
