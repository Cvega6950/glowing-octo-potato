#!/usr/bin/env python3
"""Crystal Imperium TM list: Emerald Imperium's TMs plus Heart & Soul's own.

  python3 tools/crystal_imperium/tm_list.py          # rewrite the generated files
  python3 tools/crystal_imperium/tm_list.py --check  # exit 1 if they are out of date

TM001-TM172 are Emerald Imperium's TM001-TM174 in its order (official TM guide:
pokemonemeraldimperium.com/all-tms-and-hms-location-guide/) without its two custom moves, which the
engine doesn't have ("Dark Hole" TM161, "Draco Barrage" TM171). They are followed by the Heart &
Soul TMs Imperium lacks, so every TM the story hands out still exists. The HMs are Heart & Soul's.

Writes:
  include/constants/tms_hms.h          FOREACH_TM for HnS (between the generated markers)
  src/data/items_tms_hns.h             item data for every TM: name, price, and the move's own
                                       description re-wrapped to the bag's 3-line description box
  data/scripts/tm_shop_hns.inc         the TM shop of every Poke Mart's TM clerk and the Goldenrod
                                       Dept. Store 5F: one list per badge count, and the script
  src/data/tms_old_hns.h               Heart & Soul 2.0.6's TM moves in its order, for older saves
Save compatibility: OLD_HNS_TMS is Heart & Soul 2.0.6's list. src/item.c converts TMs in older saves
by move, so a TM keeps teaching the same move (DECISIONS.md D22).
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

IMPERIUM = """FOCUS_PUNCH DRAGON_CLAW FLIP_TURN CALM_MIND ROAR TOXIC SNOWSCAPE BULK_UP BULLET_SEED HIDDEN_POWER
SUNNY_DAY TAUNT ICE_BEAM BLIZZARD ELECTROWEB LIGHT_SCREEN PROTECT RAIN_DANCE GIGA_DRAIN HYPER_VOICE
ICY_WIND SOLAR_BEAM IRON_TAIL THUNDERBOLT THUNDER EARTHQUAKE RETURN DIG PSYCHIC SHADOW_BALL
BRICK_BREAK SOLAR_BLADE REFLECT TELEPORT FLAMETHROWER SLUDGE_BOMB SANDSTORM FIRE_BLAST ROCK_TOMB AERIAL_ACE
DRAGON_DANCE FACADE DEFOG REST DRAINING_KISS THIEF STEEL_WING METEOR_BEAM LEECH_LIFE OVERHEAT
ROOST FOCUS_BLAST ENERGY_BALL GRASSY_GLIDE EXPANDING_FORCE POWER_UP_PUNCH CHARGE_BEAM RISING_VOLTAGE DRAGON_PULSE DRAIN_PUNCH
WILL_O_WISP SILVER_WIND VENOSHOCK EXPLOSION SHADOW_CLAW DAZZLING_GLEAM POLTERGEIST DUAL_CHOP ROCK_POLISH TRIPLE_AXEL
STONE_EDGE PSYSHOCK THUNDER_WAVE GYRO_BALL SWORDS_DANCE STEALTH_ROCK FLAME_CHARGE LOW_SWEEP DARK_PULSE ROCK_SLIDE
X_SCISSOR SLEEP_TALK SCALD POISON_JAB FUTURE_SIGHT GRASS_KNOT LOW_KICK PLUCK U_TURN SUBSTITUTE
FLASH_CANNON VOLT_SWITCH DRAGON_TAIL TRAILBLAZE ACROBATICS BULLDOZE SNARL WORK_UP WILD_CHARGE DUAL_WINGBEAT
SUPERPOWER SCORCHING_SANDS SMACK_DOWN HEAT_CRASH BODY_PRESS TRICK_ROOM BRAVE_BIRD ICE_SPINNER BUG_BITE STOMPING_TANTRUM
FIRE_PUNCH ICE_PUNCH THUNDER_PUNCH FIRE_FANG ICE_FANG THUNDER_FANG PSYCHIC_FANGS POISON_FANG IRON_HEAD LIQUIDATION
HYDRO_PUMP DRILL_RUN BLAZE_KICK PAIN_SPLIT ZEN_HEADBUTT WEATHER_BALL AIR_SLASH HEX MYSTICAL_FIRE SEED_BOMB
LEAF_BLADE KNOCK_OFF POWER_GEM ROCK_BLAST PIN_MISSILE ICICLE_SPEAR TAIL_SLAP ARM_THRUST FOUL_PLAY IRON_DEFENSE
NASTY_PLOT EARTH_POWER AURA_SPHERE HEAT_WAVE HURRICANE POWER_WHIP HIGH_HORSEPOWER BUG_BUZZ PHANTOM_FORCE FLARE_BLITZ
STORED_POWER GUNK_SHOT TAILWIND MEGAHORN DRACO_METEOR CLOSE_COMBAT MOONBLAST BODY_SLAM PLAY_ROUGH WATER_PULSE
SLUDGE_WAVE SUPERCELL_SLAM TEMPER_FLARE SCALE_SHOT PSYCHIC_NOISE ALLURING_VOICE VACUUM_WAVE SPIKES STEEL_BEAM
HEAVY_SLAM GRAVITY MISTY_EXPLOSION""".split()

# Heart & Soul 2.0.6's TM01-TM92, for converting older saves and for the moves Imperium lacks
OLD_HNS_TMS = """FOCUS_PUNCH DRAGON_CLAW WATER_PULSE CALM_MIND ROAR TOXIC HAIL BULK_UP BULLET_SEED HIDDEN_POWER
SUNNY_DAY TAUNT ICE_BEAM BLIZZARD HYPER_BEAM LIGHT_SCREEN PROTECT RAIN_DANCE GIGA_DRAIN SAFEGUARD
FRUSTRATION SOLAR_BEAM IRON_TAIL THUNDERBOLT THUNDER EARTHQUAKE RETURN DIG PSYCHIC SHADOW_BALL
BRICK_BREAK DOUBLE_TEAM REFLECT SHOCK_WAVE FLAMETHROWER SLUDGE_BOMB SANDSTORM FIRE_BLAST ROCK_TOMB AERIAL_ACE
TORMENT FACADE SECRET_POWER REST ATTRACT THIEF STEEL_WING SKILL_SWAP SNATCH OVERHEAT
ROOST FOCUS_BLAST ENERGY_BALL FALSE_SWIPE BRINE FLING CHARGE_BEAM ENDURE DRAGON_PULSE DRAIN_PUNCH
WILL_O_WISP SILVER_WIND EMBARGO EXPLOSION SHADOW_CLAW PAYBACK RECYCLE GIGA_IMPACT ROCK_POLISH ROCK_CLIMB
STONE_EDGE AVALANCHE THUNDER_WAVE GYRO_BALL SWORDS_DANCE STEALTH_ROCK PSYCH_UP CAPTIVATE DARK_PULSE ROCK_SLIDE
X_SCISSOR SLEEP_TALK NATURAL_GIFT POISON_JAB DREAM_EATER GRASS_KNOT SWAGGER PLUCK U_TURN SUBSTITUTE
FLASH_CANNON TRICK_ROOM""".split()

TMS = IMPERIUM + [m for m in OLD_HNS_TMS if m not in IMPERIUM]

# Shop lists by badge count (DECISIONS.md D36): damaging moves by power, these special cases by what
# they do.
STRONG_STATUS = {"SWORDS_DANCE", "CALM_MIND", "BULK_UP", "NASTY_PLOT", "DRAGON_DANCE", "IRON_DEFENSE",
                 "ROCK_POLISH", "STEALTH_ROCK", "SPIKES", "TRICK_ROOM", "TAILWIND", "GRAVITY", "ROOST",
                 "PAIN_SPLIT", "SUBSTITUTE", "DEFOG"}
MULTI_OR_VARIABLE = {"BULLET_SEED", "ROCK_BLAST", "PIN_MISSILE", "ICICLE_SPEAR", "TAIL_SLAP", "ARM_THRUST",
                     "SCALE_SHOT", "TRIPLE_AXEL", "DUAL_WINGBEAT", "DUAL_CHOP", "LOW_KICK", "GRASS_KNOT",
                     "HEAT_CRASH", "HEAVY_SLAM", "GYRO_BALL", "RETURN", "FRUSTRATION", "STORED_POWER", "FLING",
                     "NATURAL_GIFT", "HEX", "VENOSHOCK", "BODY_PRESS", "FOUL_PLAY", "WEATHER_BALL"}
SELF_KO = {"EXPLOSION", "MISTY_EXPLOSION"}
# Heart & Soul's own Goldenrod Dept. Store 5F stock: still on sale from the start.
HNS_5F_SHOP = {"LIGHT_SCREEN", "PROTECT", "REFLECT", "NATURAL_GIFT", "BLIZZARD", "HYPER_BEAM",
               "SOLAR_BEAM", "THUNDER", "FIRE_BLAST", "FOCUS_BLAST"}
# Every TM costs Emerald Imperium's price, ₽100 (its TM vendors and Game Corner counter); the badge
# tiers above still decide when the strong ones go on sale (DECISIONS.md D22)
TM_PRICE = 100
# Badges needed by power: below 70 from the start, then one band a badge (Emerald Imperium sells
# Ice Beam, Thunderbolt and Flamethrower after its 3rd Gym); Explosion waits for the 8th badge
POWER_BANDS = [(70, 0), (80, 1), (90, 2), (100, 3), (110, 4), (120, 5), (130, 6)]
MAX_BADGES = 8


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def move_power(moves_info, move):
    m = re.search(r"\[MOVE_" + move + r"\]\s*=\s*\{(.*?)\n    \},", moves_info, re.S)
    if not m:
        sys.exit(f"MOVE_{move} not found in src/data/moves_info.h")
    body = m.group(1)
    p = re.search(r"\.power\s*=\s*([^,\n]+),", body)
    if not p:
        return 0
    expr = p.group(1)
    if "?" in expr:  # B_UPDATED_MOVE_DATA >= GEN_x ? new : old
        expr = expr.split("?")[1].split(":")[0]
    return int(re.search(r"\d+", expr).group(0))


def badges_needed(moves_info, move):
    """How many badges the TM shops want before they sell this TM."""
    if move in HNS_5F_SHOP:
        return 0
    if move in SELF_KO:
        return MAX_BADGES
    if move in MULTI_OR_VARIABLE:
        return 1
    if move in STRONG_STATUS:
        return 2
    power = move_power(moves_info, move)
    for below, badges in POWER_BANDS:
        if power < below:
            return badges
    return 7


def tm_name(n):
    return f"TM{n:02d}"


# The bag and the shop print item descriptions with FONT_NORMAL at x=3 in a 14-tile (112 px) window
# three lines tall. Move descriptions are wrapped for the wider summary screen, so they are
# re-wrapped here by glyph width; the few that need four lines in FONT_NORMAL use FONT_SMALL.
DESC_WIDTH = 108
DESC_LINES = 3


class Glyphs:
    def __init__(self):
        fonts = read("src/fonts.c")
        self.widths = {}
        for font, table in (("{FONT_NORMAL}", "gFontNormalLatinGlyphWidths"),
                            ("{FONT_SMALL}", "gFontSmallLatinGlyphWidths")):
            body = re.search(r"const u8 " + table + r"\[\]\s*=\s*\{(.*?)\};", fonts, re.S).group(1)
            self.widths[font] = [int(x) for x in re.findall(r"\d+", body)]
        self.chars, self.codes = {}, {}
        for line in read("charmap.txt").splitlines():
            line = line.split("@")[0].rstrip()
            m = re.match(r"^'(\\'|.)'\s*=\s*([0-9A-F]{2})$", line)
            if m:
                self.chars[m.group(1).replace("\\'", "'")] = [int(m.group(2), 16)]
                continue
            m = re.match(r"^([A-Z0-9_]+)\s*=\s*([0-9A-F]{2}(?: [0-9A-F]{2})*)$", line)
            if m:
                self.codes[m.group(1)] = [int(b, 16) for b in m.group(2).split()]

    def width(self, text, font):
        total, i = 0, 0
        while i < len(text):
            if text[i] == "{":
                j = text.index("}", i)
                glyphs, i = self.codes[text[i + 1:j]], j + 1
            else:
                glyphs, i = self.chars[text[i]], i + 1
            total += sum(self.widths[font][g] for g in glyphs)
        return total

    def wrap(self, text, font):
        lines = []
        for word in text.split():
            joined = lines[-1] + " " + word if lines else word
            if lines and self.width(joined, font) <= DESC_WIDTH:
                lines[-1] = joined
            else:
                lines.append(word)
        return lines


def move_description(moves_info, move):
    body = re.search(r"\[MOVE_" + move + r"\]\s*=\s*\{(.*?)\n    \},", moves_info, re.S).group(1)
    m = re.search(r"\.description\s*=\s*COMPOUND_STRING\((.*?)\),\n", body, re.S)
    if not m:  # a shared description: the first definition, which is the one the config selects
        name = re.search(r"\.description\s*=\s*(\w+)", body).group(1)
        m = re.search(r"static const u8 " + name + r"\[\]\s*=\s*_\((.*?)\);", moves_info, re.S)
    text = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1)))
    return " ".join(text.replace("\\n", " ").split())


def item_description(glyphs, moves_info, move):
    text = move_description(moves_info, move)
    for font in ("{FONT_NORMAL}", "{FONT_SMALL}"):
        lines = glyphs.wrap(text, font)
        if len(lines) <= DESC_LINES:
            if font != "{FONT_NORMAL}":
                lines[0] = font + lines[0]
            return lines
    sys.exit(f"MOVE_{move}: description doesn't fit the bag's description box: {text}")


def foreach_tm():
    return "#define FOREACH_TM(F) \\\n" + " \\\n".join(f"    F({m})" for m in TMS) + "\n"


def items_header(moves_info):
    glyphs = Glyphs()
    out = ["// Generated by tools/crystal_imperium/tm_list.py: every Crystal Imperium TM, described by its",
           "// move's own description.", ""]
    for n, move in enumerate(TMS, 1):
        lines = item_description(glyphs, moves_info, move)
        desc = [f"            \"{line}\\n\"" for line in lines[:-1]] + [f"            \"{lines[-1]}\"),"]
        out += [f"    [ITEM_TM{n:02d}] = // {move.replace('_', ' ').title()}",
                "    {",
                f"        .name = ITEM_NAME(\"{tm_name(n)}\"),",
                f"        .price = {TM_PRICE},",
                "        .description = COMPOUND_STRING("] + desc + [
                "        .importance = I_REUSABLE_TMS,",
                "        .pocket = POCKET_TM_HM,",
                "        .type = ITEM_USE_PARTY_MENU,",
                "        .fieldUseFunc = ItemUseOutOfBattle_TMHM,",
                "    },",
                ""]
    return "\n".join(out)


def shop_inc(moves_info):
    out = ["@ Generated by tools/crystal_imperium/tm_list.py: the TM shops (DECISIONS.md D36), the TM clerk in",
           "@ every Poke Mart and the Goldenrod Dept. Store 5F. One list per badge count (the 8th: every TM),",
           "@ each with the TMs the badges so far unlock; Heart & Soul's own 5F stock is there from the start.",
           "",
           "@ The TM clerk in every Poke Mart (behind the counter, next to the clerk)",
           "EventScript_TMClerk::", "\tlock", "\tfaceplayer", "\tmessage TMShop_Text_Welcome", "\twaitmessage",
           "\tcall EventScript_TMShop", "\tmsgbox gText_PleaseComeAgain, MSGBOX_DEFAULT", "\trelease", "\tend", "",
           "@ Opens the shop with the list for the player's badge count",
           "EventScript_TMShop::", "\tspecialvar VAR_RESULT, GetBadgeCount"]
    out += [f"\tgoto_if_ge VAR_RESULT, {b}, TMShop_{b}" for b in range(MAX_BADGES, 0, -1)]
    for b in range(MAX_BADGES + 1):
        out += [f"TMShop_{b}:", f"\tpokemart TMShop_List{b}", "\treturn"]
    out += ["", "TMShop_Text_Welcome:", '\t.string "Welcome to the TM counter!\\n"',
            '\t.string "Every TM is ¥100.\\p"', '\t.string "More TMs go on sale with each\\n"',
            '\t.string "GYM BADGE you earn!$"', ""]
    for b in range(MAX_BADGES + 1):
        out += ["\t.align 2", f"TMShop_List{b}:"]
        out += [f"\t.2byte ITEM_TM_{move}" for move in TMS if badges_needed(moves_info, move) <= b]
        out += ["\tpokemartlistend", ""]
    return "\n".join(out)


def old_tms_header():
    return "\n".join(["// Generated by tools/crystal_imperium/tm_list.py: Heart & Soul 2.0.6's TMs in its order. Saves",
                      "// from before Emerald Imperium's TM list number their TMs this way (src/item.c).",
                      "static const u16 sOldHnsTmMoves[] =",
                      "{"] + [f"    MOVE_{m}," for m in OLD_HNS_TMS] + ["};", ""])


def generated():
    moves_info = read("src/data/moves_info.h")
    tms = read("include/constants/tms_hms.h")
    start = tms.index("#if IS_HNS\n") + len("#if IS_HNS\n\n")
    end = tms.index("#define FOREACH_HM(F)", start)
    new_tms = tms[:start] + foreach_tm() + "\n" + tms[end:]
    return {
        "include/constants/tms_hms.h": new_tms,
        "src/data/items_tms_hns.h": items_header(moves_info),
        "data/scripts/tm_shop_hns.inc": shop_inc(moves_info),
        "src/data/tms_old_hns.h": old_tms_header(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    stale = []
    for path, text in generated().items():
        full = os.path.join(ROOT, path)
        old = open(full, encoding="utf-8").read() if os.path.exists(full) else None
        if old != text:
            stale.append(path)
            if not args.check:
                with open(full, "w", encoding="utf-8") as f:
                    f.write(text)
    if args.check and stale:
        print("out of date (run tools/crystal_imperium/tm_list.py):", ", ".join(stale))
        return 1
    if not args.check:
        print(f"{len(TMS)} TMs; wrote {', '.join(stale) if stale else 'nothing (up to date)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
