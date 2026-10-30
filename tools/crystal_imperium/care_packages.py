#!/usr/bin/env python3
"""Crystal Imperium care packages (DECISIONS.md D16): writes src/data/care_packages.h (what each
package holds and the message listing it) and data/scripts/care_packages.inc (the script that
delivers them) from the table below.

  python3 tools/crystal_imperium/care_packages.py           # rewrite both files
  python3 tools/crystal_imperium/care_packages.py --check   # exit 1 if either is out of date
  python3 tools/crystal_imperium/care_packages.py --report  # what each Bag pocket gets in all

Emerald Imperium's care packages are Radical Red's (its SO2Toxic packages, on by default): ten of
nearly every held item, Berry, booster and evolution item, plus big stacks of a few (153 Quick
Balls, 153 PP Max, 306 Ability Pills, 100 Beast Balls), spread over the early game; Imperium adds
a starting package from its professor, with the Shiny Charm, and packages waiting in places along
the story (the weather Rocks in Granite Cave, Light Clay on Route 110). Here they come from PROF.
ELM (src/care_packages.c):
  - package 0 on the first step on a route or in a town once the player has a Pokemon (Imperium's
    starting package and Radical Red's first ones);
  - packages 1-17 after each Gym Badge and becoming Champion: 1-8 for the Johto badges, 9 for the
    Champion, 10-17 for the Kanto badges (Radical Red's story-point packages, in their order, then
    big stacks of what a long post-game uses);
  - the location packages (PLACES) on the first step in their place, or on a step outside once the
    player has the badges to be past it (pastAtBadges).

Each package shows what's inside in one message, wrapped to the message box with the game's own
font widths (runs of three or more items with the same quantity read "×10 each: A, B, C"), then
src/care_packages.c adds the items. One whose Bag pocket is full goes to the PC; if the PC is full
too, the package stops there and the rest arrives on another map (VAR_CARE_PACKAGE_RESUME).

The TMs come in the packages too (DECISIONS.md D48): the starting package brings every TM the TM
shops sell from the start, and the milestone package of the k-th badge (k = 1-8) the ones they sell
from k badges on (tm_list.py's tiers), so there is nothing to buy. A TM the player has already, while
TMs are reusable (INFINITE TMS), isn't given twice. A save that received packages before 0.15.1
gets their TMs in one go on a step outside (CARE_PACKAGE_TMS; VAR_CARE_PACKAGE_TMS counts the tiers
that have arrived).

The starting package brings 999 PP Max (DECISIONS.md D54), a full stack, so no later package has
any: they fill the Bag up to 999 rather than adding to what it has (src/care_packages.c). A save
whose starting package came before 0.15.2 gets the rest up to 999 once, on a step outside
(CARE_PACKAGE_PP_MAX; FLAG_CARE_PACKAGE_PP_MAX is set once the Bag has had them).

Saves from before 0.12.0 received smaller milestone packages (a few of each item; before 0.7.0
only Poke Balls, healing and evolution items). VAR_CARE_PACKAGE_IMPERIUM counts the packages whose
0.12.0 contents have arrived: while it is behind VAR_CARE_PACKAGES, the next step brings the next of
those packages again, in full, on top of what the save already got. VAR_CARE_PACKAGE_PLACES has a
bit for each location package and bit 15 for the starting package (as in 0.12.0-experimental, whose
smaller starting package a save then gets again, bigger).
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tm_list  # noqa: E402  (the TMs and the badge count the shops sell each from)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HEADER_FILE = os.path.join(ROOT, "src", "data", "care_packages.h")
SCRIPT_FILE = os.path.join(ROOT, "data", "scripts", "care_packages.inc")

# Message box: 27 tiles (216 px) of FONT_NORMAL; lines are kept clear of the "more" arrow
LINE_WIDTH = 200
# src/care_packages.c keeps the index of the next item in 8 bits of VAR_CARE_PACKAGE_RESUME
MAX_ITEMS = 256

TYPE_BOOSTERS = ["SILK_SCARF", "CHARCOAL", "MYSTIC_WATER", "MIRACLE_SEED", "MAGNET", "NEVER_MELT_ICE", "BLACK_BELT",
                 "POISON_BARB", "SOFT_SAND", "SHARP_BEAK", "TWISTED_SPOON", "SILVER_POWDER", "HARD_STONE", "SPELL_TAG",
                 "DRAGON_FANG", "BLACK_GLASSES", "METAL_COAT", "FAIRY_FEATHER"]


RESIST_BERRIES = ["OCCA_BERRY", "PASSHO_BERRY", "WACAN_BERRY", "RINDO_BERRY", "YACHE_BERRY", "CHOPLE_BERRY",
                  "KEBIA_BERRY", "SHUCA_BERRY", "COBA_BERRY", "PAYAPA_BERRY", "TANGA_BERRY", "CHARTI_BERRY", "KASIB_BERRY",
                  "HABAN_BERRY", "COLBUR_BERRY", "BABIRI_BERRY", "CHILAN_BERRY", "ROSELI_BERRY"]


def each(n, *items):
    return [(item, n) for item in items]


# One list per package: (item without ITEM_, quantity). Radical Red's packages, by where they arrive
# there, are named in the comments; Emerald Imperium's own changes are marked EI. Since 0.15.0 the
# evolution items are Emerald Imperium's (D44, D45): the ones no evolution uses any more are gone, and
# so are the ones only a trade uses (Protector, Electirizer...: a Linking Cord evolves the same Pokemon).
PACKAGES = [
    # 0: the start (after the first Pokemon): RR's Route 2 and Viridian Forest packages; EI adds the
    #    Shiny Charm, and swaps RR's Pixie Plate for the Fairy Feather (all 18 type boosters here, with
    #    all 18 type-resist Berries and the staple held items); 999 PP Max, all there are (D54)
    [("SHINY_CHARM", 1), ("QUICK_BALL", 153), ("POKE_BALL", 20)] +
    each(10, "GREAT_BALL", "POTION", "SUPER_POTION", "REVIVE") + [("PP_MAX", 999)] +
    each(10, *TYPE_BOOSTERS, "LEFTOVERS", "FOCUS_SASH",
         "EVIOLITE", "EXPERT_BELT", "MUSCLE_BAND", "WISE_GLASSES", "SCOPE_LENS", "ABSORB_BULB", "LIGHT_BALL",
         "MENTAL_HERB", "SHELL_BELL", "CLEANSE_TAG", "DEEP_SEA_SCALE", "DEEP_SEA_TOOTH", "PSYCHIC_SEED", *RESIST_BERRIES,
         "ORAN_BERRY", "PECHA_BERRY", "ASPEAR_BERRY", "RAWST_BERRY", "PERSIM_BERRY", "SITRUS_BERRY", "LUM_BERRY",
         "NUGGET", "BIG_MUSHROOM", "TINY_MUSHROOM", "RED_SHARD", "BLUE_SHARD", "GREEN_SHARD"),
    # 1: Zephyr Badge: RR's Pewter City, Route 3 and Route 4 packages (50 Heal Balls)
    [("HEAL_BALL", 50), ("POKE_BALL", 30), ("GREAT_BALL", 20), ("SUPER_POTION", 20), ("CARBOS", 20),
     ("SWIFT_FEATHER", 20)] +
    each(10, "ETHER", "BERRY_JUICE", "PP_UP", "PROTEIN", "CALCIUM", "MUSCLE_FEATHER", "GENIUS_FEATHER",
         "THROAT_SPRAY", "LUCKY_EGG", "IRON_BALL", "WIDE_LENS", "CHERI_BERRY", "CHESTO_BERRY", "LEPPA_BERRY",
         "SITRUS_BERRY", "LUM_BERRY", "STARDUST", "STAR_PIECE", "MOON_STONE", "LINKING_CORD"),
    # 2: Hive Badge: RR's Nugget Bridge and Cerulean City packages (RR's 306 Ability Pills: 153 Ability
    #    Capsules and 153 Ability Patches)
    [("ABILITY_CAPSULE", 153), ("ABILITY_PATCH", 153), ("CLEVER_FEATHER", 50), ("RESIST_FEATHER", 50),
     ("GREAT_BALL", 30)] +
    each(10, "ULTRA_BALL", "REVIVE", "HP_UP", "IRON", "ZINC", "HEALTH_FEATHER", "LIFE_ORB",
         "TERRAIN_EXTENDER", "LEEK", "PEARL", "BIG_PEARL", "LEAF_STONE"),
    # 3: Plain Badge: RR's Vermilion City and Lt. Surge packages (50 Dream Balls), the Choice items
    [("DREAM_BALL", 50), ("ULTRA_BALL", 20), ("HYPER_POTION", 20)] +
    each(10, "GREAT_BALL", "CHOICE_BAND", "CHOICE_SPECS", "CHOICE_SCARF", "ROCKY_HELMET", "SHUCA_BERRY",
         "ROSELI_BERRY", "YELLOW_SHARD", "PRISM_SCALE", "FIRE_STONE", "WATER_STONE", "THUNDER_STONE", "SUN_STONE"),
    # 4: Fog Badge: RR's Route 9 and Lavender Town packages
    [("ULTRA_BALL", 20)] +
    each(10, "DIVE_BALL", "DUSK_BALL", "MOOMOO_MILK", "SMOKE_BALL", "THICK_CLUB", "EVERSTONE",
         "MISTY_SEED", "KASIB_BERRY", "BABIRI_BERRY", "BIG_NUGGET", "DUSK_STONE", "SHINY_STONE", "STRAWBERRY_SWEET",
         "BERRY_SWEET", "LOVE_SWEET", "STAR_SWEET", "CLOVER_SWEET", "FLOWER_SWEET", "RIBBON_SWEET"),
    # 5: 5th badge: RR's Celadon Gym package
    [("ULTRA_BALL", 20), ("FULL_HEAL", 20)] +
    each(10, "MAX_REVIVE", "ELECTRIC_SEED", "SITRUS_BERRY", "LUM_BERRY", "DAWN_STONE", "ICE_STONE"),
    # 6: 6th badge: RR's big Fuchsia City package (its 153 PP Max come with the starting package's 999)
    [("ULTRA_BALL", 20)] +
    each(10, "MAX_ELIXIR", "LEFTOVERS", "EXPERT_BELT", "X_ATTACK", "X_DEFENSE", "X_SP_ATK", "X_SP_DEF", "X_SPEED",
         "GRASSY_SEED", "KINGS_ROCK", "LUCKY_PUNCH", "METAL_POWDER", "RAZOR_CLAW", "QUICK_CLAW", "LIECHI_BERRY",
         "SALAC_BERRY", "PETAYA_BERRY", "HEART_SCALE", "RED_NECTAR", "YELLOW_NECTAR", "PINK_NECTAR", "PURPLE_NECTAR"),
    # 7: 7th badge: RR's Blaine package (Life Orb, Power Herb)
    [("MAX_POTION", 20), ("ULTRA_BALL", 20)] +
    each(10, "MAX_REVIVE", "LIFE_ORB", "POWER_HERB", "X_ACCURACY", "DIRE_HIT", "GUARD_SPEC", "BINDING_BAND",
         "GRIP_CLAW", "RAZOR_FANG", "METAL_ALLOY"),
    # 8: Rising Badge
    [("FULL_RESTORE", 20), ("ULTRA_BALL", 20)] +
    each(10, "MAX_REVIVE", "MAX_ELIXIR"),
    # 9: Champion: RR's Clair and post-game packages (100 Beast Balls; Choice items, Eviolites, Rocky
    #    Helmets), the rest of the pinch Berries
    [("MASTER_BALL", 1), ("BEAST_BALL", 100)] +
    each(20, "FULL_RESTORE", "SITRUS_BERRY", "LUM_BERRY") +
    each(10, "CHOICE_BAND", "CHOICE_SPECS", "CHOICE_SCARF", "EVIOLITE", "ROCKY_HELMET", "GANLON_BERRY",
         "APICOT_BERRY", "LANSAT_BERRY", "STARF_BERRY", "MICLE_BERRY", "CUSTAP_BERRY", "ENIGMA_BERRY",
         "JABOCA_BERRY", "ROWAP_BERRY", "KEE_BERRY", "MARANGA_BERRY"),
    # 10-17: Kanto badges: big stacks for the post-game, the last niche held items, every other Poke Ball
    [("ULTRA_BALL", 50), ("FULL_RESTORE", 20)] +
    each(10, "MAX_REVIVE", "MAX_ELIXIR", "ZOOM_LENS", "QUICK_POWDER", "FOCUS_BAND", "CELL_BATTERY", "SNOWBALL",
         "LUMINOUS_MOSS"),
    [("QUICK_BALL", 50), ("FULL_RESTORE", 20)] +
    each(10, "MAX_ETHER", "ELIXIR", "FOCUS_SASH", "LAGGING_TAIL", "STICKY_BARB", "RING_TARGET", "FIGY_BERRY",
         "WIKI_BERRY", "MAGO_BERRY", "AGUAV_BERRY", "IAPAPA_BERRY"),
    each(30, "DUSK_BALL", "TIMER_BALL") + [("FULL_RESTORE", 20)] +
    each(10, "MAX_REVIVE", "AIR_BALLOON", "ASSAULT_VEST", "SITRUS_BERRY", "LUM_BERRY", "AMULET_COIN", "SOOTHE_BELL"),
    each(30, "NET_BALL", "NEST_BALL", "REPEAT_BALL") + each(20, "FULL_RESTORE", "MAX_ELIXIR"),
    [("ULTRA_BALL", 50)] + each(30, "LUXURY_BALL", "PREMIER_BALL") + each(20, "MAX_REVIVE", "FULL_RESTORE"),
    each(20, "LEVEL_BALL", "LURE_BALL", "MOON_BALL", "FRIEND_BALL", "LOVE_BALL", "FAST_BALL", "HEAVY_BALL",
         "MAX_ELIXIR") + [("FULL_RESTORE", 30)],
    [("MASTER_BALL", 1), ("QUICK_BALL", 50), ("FULL_RESTORE", 30), ("MAX_REVIVE", 20)],
    [("MASTER_BALL", 1)] + each(50, "DREAM_BALL", "BEAST_BALL", "FULL_RESTORE") +
    each(30, "MAX_REVIVE", "MAX_ELIXIR") + each(20, "SITRUS_BERRY", "LUM_BERRY"),
]

# The location packages, Emerald Imperium's packages waiting in places along the story, each a
# themed set: (map, place name in the message, badge count by which the player is past it for sure
# (9: the Johto League won), items). They follow PACKAGES in src/data/care_packages.h, and their bits
# in VAR_CARE_PACKAGE_PLACES are in this order, so a place is only ever added at the end.
PLACES = [
    ("MAP_UNION_CAVE_1F_HNS", "UNION CAVE", 2,
     each(10, "DAMP_ROCK", "HEAT_ROCK", "SMOOTH_ROCK", "ICY_ROCK", "UTILITY_UMBRELLA", "SAFETY_GOGGLES")),
    ("MAP_ILEX_FOREST_HNS", "ILEX FOREST", 3,
     each(10, "LIGHT_CLAY", "WHITE_HERB", "POWER_HERB", "MIRROR_HERB", "BIG_ROOT", "BLACK_SLUDGE")),
    ("MAP_NATIONAL_PARK_NORMAL_HNS", "the NATIONAL PARK", 4,
     each(10, "CHOICE_BAND", "CHOICE_SPECS", "CHOICE_SCARF", "LIFE_ORB", "WEAKNESS_POLICY", "BOOSTER_ENERGY")),
    ("MAP_BURNED_TOWER_1F_HNS", "the BURNED TOWER", 4,
     each(10, "TOXIC_ORB", "FLAME_ORB", "ROCKY_HELMET", "ASSAULT_VEST", "HEAVY_DUTY_BOOTS", "AIR_BALLOON")),
    ("MAP_OLIVINE_CITY_LIGHTHOUSE_HNS", "the LIGHTHOUSE", 6,
     each(10, "RED_CARD", "EJECT_BUTTON", "EJECT_PACK", "COVERT_CLOAK", "CLEAR_AMULET", "PROTECTIVE_PADS",
          "SHED_SHELL")),
    ("MAP_MT_MORTAR_1F_SOUTH_HNS", "MT. MORTAR", 7,
     each(10, "LOADED_DICE", "PUNCHING_GLOVE", "BLUNDER_POLICY", "ROOM_SERVICE", "ADRENALINE_ORB", "ABILITY_SHIELD",
          "METRONOME")),
    ("MAP_LAKE_OF_RAGE_HNS", "the LAKE OF RAGE", 7,
     each(10, "ELECTRIC_SEED", "GRASSY_SEED", "MISTY_SEED", "PSYCHIC_SEED", "TERRAIN_EXTENDER")),
    ("MAP_ICE_PATH_1F_HNS", "the ICE PATH", 8,
     each(20, "MAX_ELIXIR", "FULL_RESTORE", "MAX_REVIVE")),
    ("MAP_VICTORY_ROAD_KANTO_1F_HNS", "VICTORY ROAD", 9,
     each(20, "FULL_RESTORE", "MAX_REVIVE", "MAX_ELIXIR") + [("ABILITY_PATCH", 10)]),
]

# The PP Max the Bag is filled up to (D54): the starting package's, the only one with any
PP_MAX_STOCK = dict(PACKAGES[0])["PP_MAX"]

# What each package's first message says: the starting package, the milestone packages, and the
# location packages ({PLACE} is the place's name)
INTROS = {
    "start": ["PROF. ELM sent a care package", "to start your journey!"],
    "milestone": ["A care package from PROF. ELM", "arrived for your progress!"],
    "place": ["A care package from PROF. ELM", "was waiting in {PLACE}!"],
}

# Fixed messages of the script: label -> lines (the last ends the message)
MESSAGES = {
    "CarePackage_Text_Champion": ["PROF. ELM: Congratulations,", "CHAMPION!",
                                  "Word is that rare and legendary {PKMN}", "now show up in the wild!"],
    "CarePackage_Text_Update": ["PROF. ELM sent a bigger version", "of an earlier care package!"],
    "CarePackage_Text_Resume": ["PROF. ELM sent the rest", "of the care package!"],
    "CarePackage_Text_SentToPC": ["Your BAG was full, so some of it", "was sent to your PC."],
    "CarePackage_Text_Full": ["Your BAG and PC are full!", "PROF. ELM will send the rest",
                              "once you make room."],
    "CarePackage_Text_TMs": ["PROF. ELM sent the TMs that go", "with your earlier care packages:",
                             "{STR_VAR_1} TMs went into your", "TM CASE!"],
    "CarePackage_Text_TMsHad": ["PROF. ELM sent the TMs that go", "with your earlier care packages,",
                                "but you had them all already!"],
    "CarePackage_Text_PPMax": ["PROF. ELM sent {STR_VAR_1} PP MAX,", f"so now you have {PP_MAX_STOCK}!"],
}

SCRIPT = """\
@ Generated by tools/crystal_imperium/care_packages.py: edit that, not this file.
@ Crystal Imperium: care packages from PROF. ELM (DECISIONS.md D16). src/care_packages.c starts
@ EventScript_CarePackage on a step, with VAR_0x8004 = the package (0: the start, 1-17: the
@ milestones, then the location packages) and VAR_0x8006 = CARE_PACKAGE_NEW, _UPDATE (a save from
@ before 0.12.0 gets an earlier package's new contents), _RESUME (the rest of a package that
@ stopped because the BAG and PC were full), _TMS (the TMs of the packages a save from before
@ 0.15.1 had received, D48) or _PP_MAX (PP Max up to 999 for a save whose starting package came
@ before 0.15.2, D54). The contents and their messages are in src/data/care_packages.h.
EventScript_CarePackage::
	lockall
	playse SE_EXP_MAX
	goto_if_eq VAR_0x8006, CARE_PACKAGE_RESUME, CarePackage_Resume
	goto_if_eq VAR_0x8006, CARE_PACKAGE_TMS, CarePackage_TMs
	goto_if_eq VAR_0x8006, CARE_PACKAGE_PP_MAX, CarePackage_PPMax
	goto_if_eq VAR_0x8006, CARE_PACKAGE_UPDATE, CarePackage_Update
	callnative CarePackage_LoadIntroText
	callstd MSGBOX_DEFAULT
	goto_if_ne VAR_0x8004, 9, CarePackage_Contents
	goto_if_unset FLAG_SYS_GAME_CLEAR, CarePackage_Contents
	msgbox CarePackage_Text_Champion, MSGBOX_DEFAULT
	goto CarePackage_Contents

CarePackage_Update:
	msgbox CarePackage_Text_Update, MSGBOX_DEFAULT
CarePackage_Contents:
	playfanfare MUS_OBTAIN_ITEM
	callnative CarePackage_LoadContentsText
	callstd MSGBOX_DEFAULT
	waitfanfare
	goto CarePackage_Give

CarePackage_Resume:
	msgbox CarePackage_Text_Resume, MSGBOX_DEFAULT
CarePackage_Give:
	callnative CarePackage_GiveItems
	goto_if_eq VAR_0x8005, 0, CarePackage_CheckFull
	msgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT
CarePackage_CheckFull:
	goto_if_eq VAR_RESULT, TRUE, CarePackage_End
	msgbox CarePackage_Text_Full, MSGBOX_DEFAULT
CarePackage_End:
	releaseall
	end

CarePackage_TMs:
	callnative CarePackage_GiveTMs
	goto_if_eq VAR_RESULT, 0, CarePackage_TMsHad
	playfanfare MUS_OBTAIN_TMHM
	msgbox CarePackage_Text_TMs, MSGBOX_DEFAULT
	waitfanfare
	goto CarePackage_End

CarePackage_TMsHad:
	msgbox CarePackage_Text_TMsHad, MSGBOX_DEFAULT
	goto CarePackage_End

CarePackage_PPMax:
	callnative CarePackage_TopUpPPMax
	goto_if_eq VAR_RESULT, FALSE, CarePackage_PPMaxFull
	playfanfare MUS_OBTAIN_ITEM
	msgbox CarePackage_Text_PPMax, MSGBOX_DEFAULT
	waitfanfare
	goto_if_eq VAR_0x8005, 0, CarePackage_End
	msgbox CarePackage_Text_SentToPC, MSGBOX_DEFAULT
	goto CarePackage_End

CarePackage_PPMaxFull:
	msgbox CarePackage_Text_Full, MSGBOX_DEFAULT
	goto CarePackage_End
"""


def tm_tiers():
    """The TMs each package brings (D48): tier 0 with the starting package, tier k with the k-th
    milestone's, the ones the TM shops sell from k badges on (tm_list.badges_needed)."""
    moves_info = tm_list.read("src/data/moves_info.h")
    tiers = [[] for _ in range(tm_list.MAX_BADGES + 1)]
    for move in tm_list.TMS:
        tiers[tm_list.badges_needed(moves_info, move)].append(move)
    return tiers


def all_packages():
    """Every package's items, in src/data/care_packages.h's order: PACKAGES, then the places."""
    return PACKAGES + [items for _, _, _, items in PLACES]


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def items_data():
    """ITEM_X -> (in-game name, pocket), from src/data/items.h."""
    data = {}
    for m in re.finditer(r"\[(ITEM_\w+)\]\s*=\s*\{(.*?)\n    \}", read("src/data/items.h"), re.S):
        name = re.search(r'\.name\s*=\s*ITEM_NAME\("([^"]*)"\)', m.group(2))
        pocket = re.search(r"\.pocket\s*=\s*(\w+)", m.group(2))
        if name and pocket:
            data[m.group(1)] = (name.group(1), pocket.group(1))
    return data


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


# In a message, a complete set reads as one phrase
GROUPS = {"every type-boosting item": TYPE_BOOSTERS, "every type-resist BERRY": RESIST_BERRIES}
# Neighbouring names that end in the same word read "OCCA, PASSHO and RINDO BERRIES"
PLURALS = {"BERRY": "BERRIES", "SHARD": "SHARDS", "SWEET": "SWEETS", "STONE": "STONES", "MUSHROOM": "MUSHROOMS",
           "NECTAR": "NECTARS", "FEATHER": "FEATHERS", "ROCK": "ROCKS", "BALL": "BALLS", "SEED": "SEEDS",
           "HERB": "HERBS", "ORB": "ORBS", "APPLE": "APPLES", "TEACUP": "TEACUPS", "POT": "POTS", "ARMOR": "ARMOR",
           "LENS": "LENSES", "CLAW": "CLAWS", "POWDER": "POWDERS", "CUFF": "CUFFS"}


def list_phrases(run, names):
    """The names in a run of items with the same quantity, groups and shared last words merged: one
    list of words per phrase (a name or a quantity is never split over two lines)."""
    labels, grouped = [], set()  # grouped: the indices of GROUPS labels, which never merge
    i = 0
    while i < len(run):
        for label, group in GROUPS.items():
            if run[i:i + len(group)] == group:
                grouped.add(len(labels))
                labels.append(label)
                i += len(group)
                break
        else:
            labels.append(names["ITEM_" + run[i]])
            i += 1
    phrases = []
    i = 0
    while i < len(labels):
        last = labels[i].rsplit(" ", 1)
        j = i + 1
        if len(last) == 2 and last[1] in PLURALS and i not in grouped:
            while (j < len(labels) and j not in grouped and labels[j].rsplit(" ", 1)[-1] == last[1]
                   and " " in labels[j]):
                j += 1
        if j - i >= 2:
            heads = [label.rsplit(" ", 1)[0] for label in labels[i:j]]
            phrases.append([h + "," for h in heads[:-2]] + [heads[-2], "and", f"{heads[-1]} {PLURALS[last[1]]}"])
        elif i in grouped:
            phrases.append(labels[i].split(" "))  # a group's label is words, not a name: it may wrap
        else:
            phrases.append([labels[i]])
        i = j
    return phrases


def contents_words(items, names, tms=0):
    """The package's contents as one sentence, in words to wrap: a run of three or more items with the
    same quantity reads "×10 each: A, B, C"; other items "A ×10" (or just "A" when there is one); the
    package's TMs, if any, come last ("and 71 TMs")."""
    runs = []
    for item, n in items:
        if runs and runs[-1][0] == n:
            runs[-1][1].append(item)
        else:
            runs.append((n, [item]))
    parts = []  # (lead or None, [phrases]) per part
    for n, run in runs:
        if len(run) >= 3 and n > 1:
            parts.append((f"×{n} each:", list_phrases(run, names)))
        else:
            parts += [(None, [[names["ITEM_" + item] + (f" ×{n}" if n > 1 else "")]]) for item in run]
    if tms:
        parts.append((None, [["and", str(tms), "TMs"]]))
    words = ["Inside:"]
    for i, (lead, phrases) in enumerate(parts):
        last = i == len(parts) - 1
        # A list after "each:" ends with a semicolon, so the next part doesn't read as one of them
        end = "." if last else (";" if lead or parts[i + 1][0] else ",")
        if lead:
            words.append(lead)
        for k, phrase in enumerate(phrases):
            words += phrase[:-1] + [phrase[-1] + (end if k == len(phrases) - 1 else ",")]
    return words


def wrap(words, widths):
    """Words -> lines within LINE_WIDTH."""
    lines, line = [], ""
    for w in words:
        candidate = (line + " " + w) if line else w
        if text_width(candidate, widths) <= LINE_WIDTH:
            line = candidate
        elif not line:
            sys.exit(f"word too wide for the message box: {w}")
        else:
            lines.append(line)
            line = w
    lines.append(line)
    return lines


def c_string(lines):
    """Message lines -> the C literal lines: two lines a page."""
    out = []
    for i, line in enumerate(lines):
        end = "" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p")
        out.append(f'    "{line}{end}"')
    return out


def message_lines(lines, widths):
    out = []
    for i, line in enumerate(lines):
        if text_width(line.replace("{PKMN}", "PK").replace("{STR_VAR_1}", "000"), widths) > LINE_WIDTH:
            sys.exit(f"message line too wide: {line}")
        end = "$" if i == len(lines) - 1 else ("\\n" if i % 2 == 0 else "\\p")
        out.append(f'\t.string "{line}{end}"')
    return out


def check(data):
    if len(PACKAGES) != 18:
        sys.exit("needs the starting package and 17 milestone packages")
    # src/care_packages.c keeps the package in 5 bits of VAR_CARE_PACKAGE_RESUME, a place in 1 of
    # 15 bits of VAR_CARE_PACKAGE_PLACES (bit 15 is the starting package)
    if len(all_packages()) > 32 or len(PLACES) > 15:
        sys.exit("too many packages")
    for k, items in enumerate(all_packages()):
        if not items or len(items) > MAX_ITEMS:
            sys.exit(f"package {k}: needs 1 to {MAX_ITEMS} items")
        seen = set()
        for item, n in items:
            if "ITEM_" + item not in data:
                sys.exit(f"package {k}: unknown item ITEM_{item}")
            if item in seen:
                sys.exit(f"package {k}: ITEM_{item} twice")
            if not 0 < n <= 999:
                sys.exit(f"package {k}: {n} ITEM_{item}")
            seen.add(item)
    for place, name, past, items in PLACES:
        if not 1 <= past <= 17:
            sys.exit(f"{place}: past at {past} milestones")
    # src/care_packages.c fills the Bag's PP Max up to the starting package's (D54): no other has any
    if [k for k, items in enumerate(all_packages()) if "PP_MAX" in dict(items)] != [0]:
        sys.exit("PP Max only in the starting package")
    tiers = tm_tiers()
    # src/care_packages.c: CARE_PACKAGE_TM_TIERS, the starting package and the first eight milestones
    if len(tiers) != 9 or sum(len(t) for t in tiers) != len(tm_list.TMS) or not all(tiers):
        sys.exit("the TMs need nine tiers, every TM in one")


def c_text(name, lines):
    """A C text array of message lines."""
    lines = c_string(lines)
    return [f"static const u8 {name}[] = _("] + lines[:-1] + [lines[-1] + ");", ""]


def intro_lines(kind, widths, place=None):
    lines = [line.replace("{PLACE}", place or "") for line in INTROS[kind]]
    for line in lines:
        if text_width(line, widths) > LINE_WIDTH:
            sys.exit(f"message line too wide: {line}")
    return lines


def render_header(data, widths):
    names = {k: v[0] for k, v in data.items()}
    out = ["// Generated by tools/crystal_imperium/care_packages.py from its table: edit that, not this file.",
           "// Crystal Imperium care packages (DECISIONS.md D16): package 0 at the start, 1-17 for the",
           f"// milestones, {len(PACKAGES)}-{len(all_packages()) - 1} the location packages (sCarePackagePlaces).", "",
           "// The PP Max the Bag is filled up to (D54): the starting package's",
           f"#define CARE_PACKAGE_PP_MAX_STOCK {PP_MAX_STOCK}", ""]
    out += c_text("sCarePackageIntroStart", intro_lines("start", widths))
    out += c_text("sCarePackageIntroMilestone", intro_lines("milestone", widths))
    for k, (_, name, _, _) in enumerate(PLACES):
        out += c_text(f"sCarePackageIntroPlace{k}", intro_lines("place", widths, name))
    intros = (["sCarePackageIntroStart"] + ["sCarePackageIntroMilestone"] * (len(PACKAGES) - 1) +
              [f"sCarePackageIntroPlace{k}" for k in range(len(PLACES))])
    tiers = tm_tiers()
    for k, items in enumerate(all_packages()):
        out.append(f"static const struct CarePackageItem sCarePackage{k}[] =")
        out.append("{")
        out += [f"    {{ITEM_{item}, {n}}}," for item, n in items]
        out += ["};", ""]
        tms = len(tiers[k]) if k < len(tiers) else 0
        out += c_text(f"sCarePackageText{k}", wrap(contents_words(items, names, tms), widths))
    out.append("static const struct CarePackage sCarePackages[] =")
    out.append("{")
    out += [f"    {{sCarePackage{k}, ARRAY_COUNT(sCarePackage{k}), {intros[k]}, sCarePackageText{k}}},"
            for k in range(len(all_packages()))]
    out += ["};", ""]
    out.append("// The TMs of the starting package (tier 0) and of the first eight milestones' (D48): the ones the")
    out.append("// TM shops sell from that badge count on (tools/crystal_imperium/tm_list.py)")
    for k, tier in enumerate(tiers):
        out.append(f"static const u16 sCarePackageTMs{k}[] =")
        out.append("{")
        out += [f"    ITEM_TM_{move}," for move in tier]
        out += ["};", ""]
    out.append("static const struct CarePackageTMs sCarePackageTMs[] =")
    out.append("{")
    out += [f"    {{sCarePackageTMs{k}, ARRAY_COUNT(sCarePackageTMs{k})}}," for k in range(len(tiers))]
    out += ["};", ""]
    out.append("// Where each location package waits, and the milestones by which the player is past it")
    out.append("static const struct CarePackagePlace sCarePackagePlaces[] =")
    out.append("{")
    out += [f"    {{{place}, {past}}}," for place, _, past, _ in PLACES]
    out += ["};", ""]
    return "\n".join(out)


def render_script(widths):
    out = SCRIPT.splitlines()
    out.append("")
    for label, lines in MESSAGES.items():
        out += [f"{label}:"] + message_lines(lines, widths) + [""]
    return "\n".join(out).rstrip("\n") + "\n"


# This build combines the Bag pockets (I_COMBINE_BAG_POCKETS): treasures go in the items pocket,
# battle items in the medicine pocket (include/constants/item.h)
COMBINED_POCKETS = {"POCKET_TREASURES": "POCKET_ITEMS", "POCKET_BATTLE_ITEMS": "POCKET_MEDICINE"}


def report(data):
    pockets = {}
    for items in all_packages():
        for item, n in items:
            pocket = data["ITEM_" + item][1]
            pocket = COMBINED_POCKETS.get(pocket, pocket)
            pockets.setdefault(pocket, {})
            pockets[pocket][item] = pockets[pocket].get(item, 0) + n
    for pocket, items in sorted(pockets.items()):
        print(f"{pocket}: {len(items)} kinds, {sum(items.values())} items")
    print(f"{sum(len(p) for p in all_packages())} entries in {len(all_packages())} packages")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    data, widths = items_data(), glyph_widths()
    check(data)
    if args.report:
        report(data)
        return 0
    outputs = {HEADER_FILE: render_header(data, widths), SCRIPT_FILE: render_script(widths)}
    stale = []
    for path, new in outputs.items():
        old = read(path) if os.path.exists(path) else ""
        if new == old:
            continue
        if args.check:
            stale.append(os.path.relpath(path, ROOT))
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            print(f"wrote {os.path.relpath(path, ROOT)}")
    if stale:
        print(f"{', '.join(stale)} out of date: run tools/crystal_imperium/care_packages.py")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
