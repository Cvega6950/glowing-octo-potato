"""The trainer standard's rules for the designed teams (the scratchpad's standard.md, rules tagged [V] and [W];
redesign plan 2.1 item 4 and 3.4): every team in boss_teams.TEAMS, ace_trainer_data.ACES and UPGRADES, read
with the build's own species, move and item data (species_db.py). validate.py runs them.

A finding is an ERROR (CI fails) or a WARNING. A [V] rule the designed teams of 0.15.2 still break is listed in
PENDING with the trainers that break it: their findings are warnings until the redesigned teams land, and any
other trainer's are errors. Once a team is fixed, it comes out of PENDING (validate.py says so), and once a
rule's list is empty the rule is an error everywhere. [W] rules are always warnings.

The evolution rules follow the battle code (GetTrainerMonEvolvedSpecies, src/battle_main.c): a team made for a
stage keeps its Pokemon as made up to its stage's cap; raised to a later cap it evolves as any trainer's does,
a level evolution at its level and any other from level 32, the first listed route that applies, two steps
at most, except that a named Eviolite species holding an Eviolite, or a Pikachu holding a Light Ball, stays as
it is (team_kit.NAMED_EVIOLITE).
"""
import collections
import glob
import json
import os
import re

import boss_teams
import ace_trainer_data
import species_db
import team_kit
from boss_teams import JOHTO_CHAMPION, KANTO_CHAMPION

ROOT = boss_teams.ROOT
STAGES = [0, 1, 2, 3, 4, 5, 6, 7, 8, JOHTO_CHAMPION, KANTO_CHAMPION]
STAGE_LABEL = {JOHTO_CHAMPION: "J", KANTO_CHAMPION: "K"}


def stage_index(stage):
    return STAGES.index(stage)


def label(stage):
    return STAGE_LABEL.get(stage, str(stage))


def cap(stage):
    return boss_teams.cap(stage)


# ---------------------------------------------------------------- rules whose 0.15.2 violations are warnings
# rule -> the trainers whose teams break it in 0.15.2 (the redesign plan's work groups F1-F5 fix them). P3 and
# V4 are the standard's additions (redesign plan 2.3, phase 1b): they are warnings until 1b lands, for every
# team. Written by `validate.py --pending` from the findings, and kept by hand from then on.
PENDING_EVERYWHERE = {"P3", "V4"}
PENDING = {rule: {f"TRAINER_{name}_HNS" for name in names.split()} for rule, names in {
    "A2": ("ACE_MTMOON_TOBIAS ACE_PPLANT_EVANGELINE ACE_R12_CORALIE BENJAMIN BLAINE BRIAN BROCK DEVIN ERIKA GAVEN "
             "GAVEN_2 GAVEN_3 KELLY LANCE_1 LI MEGAN RIVAL_CHIKORITA_3 RIVAL_CHIKORITA_4 RIVAL_CHIKORITA_5 "
             "RIVAL_CYNDAQUIL_3 RIVAL_CYNDAQUIL_4 RIVAL_CYNDAQUIL_5 RIVAL_TOTODILE_3 RIVAL_TOTODILE_4 "
             "RIVAL_TOTODILE_5 ROLAND SIDE_CANDICE SIDE_LARRY WHITNEY_1"),
    "E1": ("ACE_R29_KAITO ARCHER BEN BENJAMIN DEVIN GREG KATE MIKEY PETREL_2 PROTON_1 RIVAL_CHIKORITA_2 "
             "RIVAL_CHIKORITA_3 RIVAL_CHIKORITA_4 RIVAL_CHIKORITA_5 RIVAL_CYNDAQUIL_2 RIVAL_CYNDAQUIL_3 "
             "RIVAL_CYNDAQUIL_4 RIVAL_CYNDAQUIL_5 RIVAL_TOTODILE_2 RIVAL_TOTODILE_3 RIVAL_TOTODILE_4 "
             "RIVAL_TOTODILE_5 ROLAND"),
    "E2": ("ACE_NATPARK_SUNNIVA BEN BENJAMIN CHUCK_1 CHUCK_1_2 CHUCK_1_3 EUGENE GEORGE GREG JASMINE_1 JASMINE_1_2 "
             "JASMINE_1_3 RIVAL_CHIKORITA_2 RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_2 RIVAL_CYNDAQUIL_3 RIVAL_TOTODILE_2 "
             "RIVAL_TOTODILE_3 SIDE_GARDENIA WHITNEY_1"),
    "E6": ("AARON ACE_ILEX_CALDER ACE_NATPARK_SUNNIVA ACE_R29_KAITO ACE_R31_BRANT ACE_R32_NAIA ACE_R33_SILAS "
             "ACE_R35_ADELINE ACE_R46_TAMSIN ACE_UNIONCAVE_BRODIE BEN BENJAMIN BRYAN DEVIN EUGENE GEORGE GREG KATE "
             "MIKEY PETREL_1 ROLAND SIDE_CANDICE SIDE_GARDENIA"),
    "E8": ("RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_3 RIVAL_TOTODILE_3"),
    "I3": ("ACE_NATPARK_SUNNIVA ACE_PPLANT_EVANGELINE ACE_R24_MAGNUS ACE_R5_VERA ARIANA_1 ARIANA_2 BEN BENJAMIN "
             "BLAKE DEVIN EUGENE FALKNER_1 HERMAN KATE KEVIN LI LORI PETREL_1 PROTON_1 PROTON_2 RIVAL_CHIKORITA_2 "
             "RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_2 RIVAL_CYNDAQUIL_3 RIVAL_TOTODILE_2 RIVAL_TOTODILE_3 "
             "RIVAL_TOTODILE_6 ROBERT ROLAND SIDE_CANDICE SIDE_CYNTHIA SIDE_GARDENIA STEPHEN"),
    "I4": ("BRET GREG SIDE_GRUSHA SIDE_IONO SIDE_RYME SIDE_TULIP TIM"),
    "M2": ("ACE_R30_SELENE FALKNER_1 MIKEY PETREL_1 PROTON_1 RIVAL_CHIKORITA_2 RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_2 "
             "RIVAL_CYNDAQUIL_3 RIVAL_TOTODILE_2 RIVAL_TOTODILE_3 SIDE_KOFU WHITNEY_1"),
    "M4": ("EUSINE LTSURGE"),
    "M5": ("ACE_R19_MAREN RIVAL_CHIKORITA_2 RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_2 RIVAL_CYNDAQUIL_3 RIVAL_TOTODILE_2 "
             "RIVAL_TOTODILE_3"),
    "M6": ("AARON ACE_DARKCAVE_ZEPHYR ACE_DOJO_BRIGID ACE_MTMOONSQ_MISTRAL ACE_MTMOON_TOBIAS ACE_NATPARK_SUNNIVA "
             "ACE_R13_MARLOW ACE_R15_HAYATE ACE_R19_MAREN ACE_R39_MIRIAM ACE_R6_LUCIEN ACE_R7_MARIGOLD "
             "ACE_R8_MORDECAI ACE_R9_ROSALIND ACE_VR1F_OPHELIA ACE_VRB2F_ELIAS BETH BETH_2 BETH_3 BLAINE BLAKE BRET "
             "CAROL CLAIR_1 EUGENE EUSINE FALKNER_2 FALKNER_POSTOBC HERMAN JAKE JANINE JANINE_POSTOBC "
             "JASMINE_POSTOBC JOYCE KAREN_1 KAREN_2 KEVIN LANCE_1 LANCE_POSTOBC LTSURGE LTSURGE_POSTOBC MORTY_2 "
             "MORTY_POSTOBC OTIS PROTON_1 PRYCE_2 PRYCE_POSTOBC RED RED_POSTOBC RIVAL_CHIKORITA_4 RIVAL_CHIKORITA_6 "
             "RIVAL_CHIKORITA_7 RIVAL_CYNDAQUIL_4 RIVAL_CYNDAQUIL_5 RIVAL_CYNDAQUIL_6 RIVAL_CYNDAQUIL_7 "
             "RIVAL_TOTODILE_4 RIVAL_TOTODILE_6 RIVAL_TOTODILE_7 RYAN SABRINA SABRINA_POSTOBC SIDE_BRASSIUS "
             "SIDE_FANTINA SIDE_IONO SIDE_N SIDE_RYME SIDE_TULIP SIDE_VOLKNER STEPHEN WHITNEY_2 WILL_1 WILL_2 "
             "WILL_POSTOBC"),
    "M8": ("ACE_DARKCAVE_ZEPHYR ACE_R22_SERAPHINA ACE_R8_MORDECAI ACE_SEAFOAM_LENORE ACE_VR1F_OPHELIA ARCHER BLAINE "
             "BLAINE_POSTOBC BROCK CLAIR_2 ERIKA_POSTOBC EUSINE FALKNER_2 FALKNER_POSTOBC KAREN_1 KOGA_POSTOBC KUNI "
             "LANCE_2 LTSURGE LTSURGE_POSTOBC MEGAN MIKI MORTY_1 MORTY_POSTOBC NAOKO OTIS PETREL_1 PETREL_2 PRYCE_1 "
             "PRYCE_1_2 PRYCE_1_3 PRYCE_POSTOBC RED RED_POSTOBC RIVAL_CHIKORITA_3 RIVAL_CYNDAQUIL_3 "
             "RIVAL_TOTODILE_3 ROBERT SABRINA SABRINA_POSTOBC SAYO SIDE_ARCHIE SIDE_BRASSIUS SIDE_FANTINA "
             "SIDE_GRUSHA SIDE_IONO SIDE_KOFU SIDE_ROARK SIDE_RYME SIDE_TULIP SIDE_VOLKNER SIDE_WAKE SIDE_WALLACE "
             "WILL_1 WILL_2 WILL_POSTOBC ZUKI"),
    "N2": ("BLUE HERMAN SIDE_FANTINA WILL_1"),
    "P2": ("BLUE HERMAN SIDE_FANTINA SIDE_TULIP WILL_1"),
    "P4": ("BRUNO_1 KAREN_1 KOGA_1 LANCE_1 WILL_1"),
    "P6": ("AARON ACE_R17_RYKER ACE_R40_KAIA LOIS SIDE_BYRON SIDE_MAYLENE"),
    "R1": ("BETH_3 GAVEN_2 GAVEN_3"),
    "R2": ("BETH_3 GAVEN_2 GAVEN_3 REENA_3"),
    "S4": ("ACE_DARKCAVE_ZEPHYR ACE_DIGLETT_OSWALD ACE_DOJO_BRIGID ACE_ICEPATH_B1F_RHEA ACE_MTMOON_TOBIAS "
             "ACE_PPLANT_EVANGELINE ACE_R13_MARLOW ACE_R24_MAGNUS ACE_R2_SYLVIE ACE_R39_MIRIAM ACE_R48_SOLANA "
             "ACE_R4_ESTELLE ACE_R7_MARIGOLD ACE_R8_MORDECAI ACE_SEAFOAM_LENORE ACE_TOHJO_IMOGEN ACE_VRB1F_MAXIM "
             "ACE_WHIRL_NOLAN ARIANA_2 BRIAN BRUNO_1 CARA COLETTE CYBIL DWAYNE EMMA EUGENE GAVEN_3 GREG GWEN HERMAN "
             "JAKE JOYCE KAREN_1 KEVIN KOGA_1 LANCE_2 LORI OTIS PETREL_2 PROTON_2 PRYCE_1_3 QUINN REENA_3 "
             "RIVAL_CHIKORITA_2 RIVAL_CHIKORITA_4 RIVAL_CHIKORITA_5 RIVAL_CHIKORITA_6 RIVAL_CYNDAQUIL_2 "
             "RIVAL_CYNDAQUIL_4 RIVAL_CYNDAQUIL_5 RIVAL_CYNDAQUIL_6 ROBERT RYAN SEAN SIDE_BRASSIUS SIDE_CYNTHIA "
             "SIDE_CYRUS SIDE_GARDENIA_2 SIDE_GEETA SIDE_IRIS SIDE_MAXIE SIDE_MAYLENE SIDE_RYME SIDE_VOLKNER "
             "SIDE_WALLY STEPHEN WILL_1"),
    "V2": ("ACE_ILEX_CALDER ACE_R23_LEANDER ACE_R39_MIRIAM ACE_WHIRL_NOLAN BLUE HERMAN JASMINE_1 JASMINE_1_2 "
             "JASMINE_1_3 KEVIN MEGAN PETREL_1 PETREL_2 SIDE_FANTINA SIDE_TULIP WILL_1"),
    "V3": ("BRET"),
    "Z1": ("ARIANA_1"),
    "Z2": ("ARIANA_1"),
}.items()}

# ---------------------------------------------------------------- the move, item and ability classes
ROLES = {
    "priority": {"AQUA_JET", "BULLET_PUNCH", "EXTREME_SPEED", "FAKE_OUT", "ICE_SHARD", "MACH_PUNCH", "QUICK_ATTACK",
                 "SHADOW_SNEAK", "SUCKER_PUNCH", "VACUUM_WAVE", "ACCELEROCK", "JET_PUNCH", "FIRST_IMPRESSION",
                 "GRASSY_GLIDE", "WATER_SHURIKEN", "FEINT", "THUNDERCLAP", "UPPER_HAND", "ZIPPY_ZAP"},
    "setup": {"SWORDS_DANCE", "DRAGON_DANCE", "NASTY_PLOT", "CALM_MIND", "BULK_UP", "QUIVER_DANCE", "SHELL_SMASH",
              "SHIFT_GEAR", "COIL", "HONE_CLAWS", "GROWTH", "AGILITY", "ROCK_POLISH", "AUTOTOMIZE", "VICTORY_DANCE",
              "FILLET_AWAY", "BELLY_DRUM", "CURSE", "WORK_UP", "TAIL_GLOW", "GEOMANCY", "CLANGOROUS_SOUL", "NO_RETREAT",
              "IRON_DEFENSE", "COSMIC_POWER", "HOWL", "TIDY_UP", "STOCKPILE", "ACID_ARMOR", "AMNESIA", "BARRIER",
              "DEFEND_ORDER", "MEDITATE", "SHARPEN", "POWER_UP_PUNCH", "CHARGE_BEAM", "FLAME_CHARGE", "TRAILBLAZE",
              "SCALE_SHOT", "AQUA_STEP", "ESPER_WING", "TORCH_SONG", "RAPID_SPIN"},
    "hazard": {"STEALTH_ROCK", "SPIKES", "TOXIC_SPIKES", "STICKY_WEB", "STONE_AXE", "CEASELESS_EDGE"},
    "pivot": {"U_TURN", "VOLT_SWITCH", "FLIP_TURN", "PARTING_SHOT", "TELEPORT", "SHED_TAIL", "BATON_PASS",
              "CHILLY_RECEPTION"},
    "recovery": {"RECOVER", "ROOST", "SLACK_OFF", "SOFT_BOILED", "SYNTHESIS", "MOONLIGHT", "MORNING_SUN", "WISH",
                 "STRENGTH_SAP", "REST", "SHORE_UP", "MILK_DRINK", "HEAL_ORDER", "LIFE_DEW", "JUNGLE_HEALING",
                 "LUNAR_BLESSING", "PURIFY", "LEECH_SEED", "PAIN_SPLIT"},
    "status": {"WILL_O_WISP", "THUNDER_WAVE", "TOXIC", "SPORE", "SLEEP_POWDER", "HYPNOSIS", "LOVELY_KISS", "DARK_VOID",
               "YAWN", "GLARE", "NUZZLE", "STUN_SPORE", "POISON_POWDER", "SING", "GRASS_WHISTLE", "TOXIC_THREAD",
               "SALT_CURE", "DIRE_CLAW", "MORTAL_SPIN"},
    "screens": {"REFLECT", "LIGHT_SCREEN", "AURORA_VEIL"},
    "trickroom": {"TRICK_ROOM"},
    "tailwind": {"TAILWIND"},
    "phazing": {"ROAR", "WHIRLWIND", "DRAGON_TAIL", "CIRCLE_THROW", "HAZE", "CLEAR_SMOG"},
    "hazard_control": {"RAPID_SPIN", "DEFOG", "MORTAL_SPIN", "TIDY_UP", "COURT_CHANGE"},
    "disruption": {"TAUNT", "ENCORE", "TRICK", "SWITCHEROO", "KNOCK_OFF", "DISABLE", "TORMENT", "SPIRIT_BREAK"},
}
SETUP_STATUS = ROLES["setup"] - {"POWER_UP_PUNCH", "CHARGE_BEAM", "FLAME_CHARGE", "TRAILBLAZE", "SCALE_SHOT", "AQUA_STEP",
                                 "ESPER_WING", "TORCH_SONG", "RAPID_SPIN"}
HAZARD_KIND = {"STEALTH_ROCK": "Stealth Rock", "STONE_AXE": "Stealth Rock", "SPIKES": "Spikes", "CEASELESS_EDGE": "Spikes",
               "TOXIC_SPIKES": "Toxic Spikes", "STICKY_WEB": "Sticky Web"}
# Rule M2's filler moves, and the ones that are filler only without their partner
FILLER = {"CONFUSE_RAY", "SUPERSONIC", "SWEET_KISS", "SMOKESCREEN", "SAND_ATTACK", "FLASH", "KINESIS", "SCARY_FACE",
          "CHARM", "GROWL", "LEER", "TAIL_WHIP", "BABY_DOLL_EYES", "HARDEN", "WITHDRAW", "ATTRACT", "CAPTIVATE",
          "METRONOME", "ME_FIRST", "POWER_SWAP", "GUARD_SWAP", "MIST"}
WEAK_SETUP = {"HOWL", "WORK_UP", "MEDITATE", "SHARPEN", "HONE_CLAWS", "GROWTH"}
WEATHER_SETTER_ABILITY = {"ABILITY_DROUGHT": "sun", "ABILITY_DRIZZLE": "rain", "ABILITY_SAND_STREAM": "sand",
                          "ABILITY_SNOW_WARNING": "snow", "ABILITY_DESOLATE_LAND": "sun", "ABILITY_PRIMORDIAL_SEA": "rain",
                          "ABILITY_ORICHALCUM_PULSE": "sun", "ABILITY_SAND_SPIT": "sand"}
WEATHER_MOVES = {"SUNNY_DAY": "sun", "RAIN_DANCE": "rain", "SANDSTORM": "sand", "HAIL": "snow", "SNOWSCAPE": "snow",
                 "CHILLY_RECEPTION": "snow"}
MAP_WEATHER = {"WEATHER_RAIN": "rain", "WEATHER_RAIN_THUNDERSTORM": "rain", "WEATHER_DOWNPOUR": "rain",
               "WEATHER_SANDSTORM": "sand", "WEATHER_DROUGHT": "sun", "WEATHER_SNOW": "snow"}
WEATHER_ABUSERS = {"ABILITY_CHLOROPHYLL": "sun", "ABILITY_SOLAR_POWER": "sun", "ABILITY_FLOWER_GIFT": "sun",
                   "ABILITY_LEAF_GUARD": "sun", "ABILITY_SWIFT_SWIM": "rain", "ABILITY_RAIN_DISH": "rain",
                   "ABILITY_HYDRATION": "rain", "ABILITY_SAND_RUSH": "sand", "ABILITY_SAND_FORCE": "sand",
                   "ABILITY_SAND_VEIL": "sand", "ABILITY_SLUSH_RUSH": "snow", "ABILITY_SNOW_CLOAK": "snow",
                   "ABILITY_ICE_BODY": "snow"}
WEATHER_ROCKS = {"ITEM_HEAT_ROCK": "sun", "ITEM_DAMP_ROCK": "rain", "ITEM_SMOOTH_ROCK": "sand", "ITEM_ICY_ROCK": "snow"}
TERRAIN_SETTERS = {"ABILITY_ELECTRIC_SURGE", "ABILITY_GRASSY_SURGE", "ABILITY_PSYCHIC_SURGE", "ABILITY_MISTY_SURGE",
                   "ABILITY_HADRON_ENGINE", "ABILITY_SEED_SOWER", "MOVE_ELECTRIC_TERRAIN", "MOVE_GRASSY_TERRAIN",
                   "MOVE_PSYCHIC_TERRAIN", "MOVE_MISTY_TERRAIN"}
ORB_ABILITIES = {"ABILITY_GUTS", "ABILITY_POISON_HEAL", "ABILITY_TOXIC_BOOST", "ABILITY_FLARE_BOOST", "ABILITY_QUICK_FEET",
                 "ABILITY_MARVEL_SCALE", "ABILITY_MAGIC_GUARD"}
SPECIES_ITEMS = {"ITEM_LEEK": ("SPECIES_FARFETCHD", "SPECIES_FARFETCHD_GALAR", "SPECIES_SIRFETCHD"),
                 "ITEM_THICK_CLUB": ("SPECIES_CUBONE", "SPECIES_MAROWAK", "SPECIES_MAROWAK_ALOLA"),
                 "ITEM_LIGHT_BALL": ("SPECIES_PIKACHU",), "ITEM_LUCKY_PUNCH": ("SPECIES_CHANSEY",),
                 "ITEM_DEEP_SEA_TOOTH": ("SPECIES_CLAMPERL",), "ITEM_DEEP_SEA_SCALE": ("SPECIES_CLAMPERL",),
                 "ITEM_METAL_POWDER": ("SPECIES_DITTO",), "ITEM_QUICK_POWDER": ("SPECIES_DITTO",)}
# Items the battle code reads as "keep me unevolved" for Heart & Soul's own teams (IsEvolutionBlockingItem)
BLOCKING = {"HOLD_EFFECT_EVIOLITE", "HOLD_EFFECT_PREVENT_EVOLVE", "HOLD_EFFECT_LIGHT_BALL", "HOLD_EFFECT_LUCKY_PUNCH",
            "HOLD_EFFECT_DEEP_SEA_TOOTH", "HOLD_EFFECT_DEEP_SEA_SCALE", "HOLD_EFFECT_METAL_POWDER", "HOLD_EFFECT_QUICK_POWDER"}
CONSUMABLE = {"HOLD_EFFECT_RESTORE_HP", "HOLD_EFFECT_RESTORE_PCT_HP", "HOLD_EFFECT_RESIST_BERRY", "HOLD_EFFECT_FOCUS_SASH",
              "HOLD_EFFECT_WHITE_HERB", "HOLD_EFFECT_MENTAL_HERB", "HOLD_EFFECT_POWER_HERB", "HOLD_EFFECT_BOOSTER_ENERGY",
              "HOLD_EFFECT_AIR_BALLOON", "HOLD_EFFECT_CURE_STATUS", "HOLD_EFFECT_CURE_PAR", "HOLD_EFFECT_CURE_SLP",
              "HOLD_EFFECT_CURE_PSN", "HOLD_EFFECT_CURE_BRN", "HOLD_EFFECT_CURE_FRZ", "HOLD_EFFECT_CURE_CONFUSION",
              "HOLD_EFFECT_SPEED_UP", "HOLD_EFFECT_ATTACK_UP", "HOLD_EFFECT_SP_ATTACK_UP", "HOLD_EFFECT_DEFENSE_UP",
              "HOLD_EFFECT_SP_DEFENSE_UP", "HOLD_EFFECT_CUSTAP_BERRY", "HOLD_EFFECT_WEAKNESS_POLICY",
              "HOLD_EFFECT_THROAT_SPRAY", "HOLD_EFFECT_GEMS", "HOLD_EFFECT_ROOM_SERVICE", "HOLD_EFFECT_ADRENALINE_ORB",
              "HOLD_EFFECT_BLUNDER_POLICY", "HOLD_EFFECT_EJECT_BUTTON", "HOLD_EFFECT_EJECT_PACK", "HOLD_EFFECT_RED_CARD",
              "HOLD_EFFECT_SEEDS", "HOLD_EFFECT_TERRAIN_SEED", "HOLD_EFFECT_CONFUSE_SPICY", "HOLD_EFFECT_CONFUSE_DRY",
              "HOLD_EFFECT_CONFUSE_SWEET", "HOLD_EFFECT_CONFUSE_BITTER", "HOLD_EFFECT_CONFUSE_SOUR", "HOLD_EFFECT_KEE_BERRY",
              "HOLD_EFFECT_MARANGA_BERRY", "HOLD_EFFECT_ENIGMA_BERRY", "HOLD_EFFECT_JABOCA_BERRY",
              "HOLD_EFFECT_ROWAP_BERRY", "HOLD_EFFECT_STAR_BERRY", "HOLD_EFFECT_MICLE_BERRY", "HOLD_EFFECT_LANSAT_BERRY",
              "HOLD_EFFECT_RANDOM_STAT_UP", "HOLD_EFFECT_CRITICAL_UP"}
# Items a Pokemon may use up as it comes into battle, before the first action menu (Booster Energy without sun
# or a terrain, a Terrain Seed or Room Service with theirs, an Adrenaline Orb or a White or Mirror Herb when an
# Intimidate meets it): a play test doesn't check them on a Pokemon on the field
SWITCH_IN_ITEMS = {"HOLD_EFFECT_BOOSTER_ENERGY", "HOLD_EFFECT_TERRAIN_SEED", "HOLD_EFFECT_ROOM_SERVICE",
                   "HOLD_EFFECT_ADRENALINE_ORB", "HOLD_EFFECT_WHITE_HERB", "HOLD_EFFECT_MIRROR_HERB"}
CHARGE_EFFECTS = {"EFFECT_SOLAR_BEAM", "EFFECT_TWO_TURNS_ATTACK", "EFFECT_METEOR_BEAM", "EFFECT_SEMI_INVULNERABLE",
                  "EFFECT_GEOMANCY", "EFFECT_ELECTRO_SHOT", "EFFECT_SKY_DROP"}
FIXED_DAMAGE = {"EFFECT_LEVEL_DAMAGE", "EFFECT_FIXED_DAMAGE_ARG", "EFFECT_SUPER_FANG", "EFFECT_ENDEAVOR",
                "EFFECT_PSYWAVE", "EFFECT_FINAL_GAMBIT", "EFFECT_COUNTER", "EFFECT_MIRROR_COAT", "EFFECT_METAL_BURST",
                "EFFECT_OHKO"}
VARIABLE_POWER = {"EFFECT_GYRO_BALL", "EFFECT_HEAT_CRASH", "EFFECT_LOW_KICK", "EFFECT_ELECTRO_BALL", "EFFECT_HEAVY_SLAM",
                  "EFFECT_PUNISHMENT", "EFFECT_TRUMP_CARD", "EFFECT_FLAIL", "EFFECT_WRING_OUT", "EFFECT_CRUSH_GRIP",
                  "EFFECT_HARD_PRESS", "EFFECT_MAGNITUDE", "EFFECT_PRESENT", "EFFECT_NATURAL_GIFT", "EFFECT_BEAT_UP",
                  "EFFECT_SPIT_UP"}
ATE = {"ABILITY_AERILATE": "TYPE_FLYING", "ABILITY_PIXILATE": "TYPE_FAIRY", "ABILITY_REFRIGERATE": "TYPE_ICE",
       "ABILITY_GALVANIZE": "TYPE_ELECTRIC"}
NATURES = {
    "Hardy": (None, None), "Lonely": ("Atk", "Def"), "Brave": ("Atk", "Spe"), "Adamant": ("Atk", "SpA"),
    "Naughty": ("Atk", "SpD"), "Bold": ("Def", "Atk"), "Docile": (None, None), "Relaxed": ("Def", "Spe"),
    "Impish": ("Def", "SpA"), "Lax": ("Def", "SpD"), "Timid": ("Spe", "Atk"), "Hasty": ("Spe", "Def"),
    "Serious": (None, None), "Jolly": ("Spe", "SpA"), "Naive": ("Spe", "SpD"), "Modest": ("SpA", "Atk"),
    "Mild": ("SpA", "Def"), "Quiet": ("SpA", "Spe"), "Bashful": (None, None), "Rash": ("SpA", "SpD"),
    "Calm": ("SpD", "Atk"), "Gentle": ("SpD", "Def"), "Sassy": ("SpD", "Spe"), "Careful": ("SpD", "SpA"),
    "Quirky": (None, None),
}
HIDDEN_POWER_TYPES = ["Fighting", "Flying", "Poison", "Ground", "Rock", "Bug", "Ghost", "Steel", "Fire", "Water", "Grass",
                      "Electric", "Psychic", "Ice", "Dragon", "Dark"]
# EI's median strongest attack by the badge segment matching each stage (rule M5's warning)
EI_MEDIAN_POWER = {0: 65, 1: 70, 2: 80, 3: 90, 4: 100, 5: 95, 6: 100, 7: 100, 8: 110, JOHTO_CHAMPION: 110,
                   KANTO_CHAMPION: 110}
TIER_A = 1.10
# Rule M6: an attack below this accuracy needs its enabler (No Guard, Compound Eyes, Mind Reader, Lock-On, or rain
# or snow for the moves they make sure to hit). The standard's text says 75%, so Focus Blast's 70% needs one too;
# its count of the 0.15.2 teams (1, Eugene's Dynamic Punch) only looked at the 50% moves.
M6_ACCURACY = 75


# ---------------------------------------------------------------- the teams
JOHTO_LEADERS = ("FALKNER", "BUGSY", "WHITNEY", "MORTY", "CHUCK", "JASMINE", "PRYCE", "CLAIR")
KANTO_LEADERS = ("BROCK", "MISTY", "LTSURGE", "ERIKA", "JANINE", "SABRINA", "BLAINE", "BLUE")
ELITE_FOUR = ("WILL", "KOGA", "BRUNO", "KAREN", "LANCE")
ROCKETS = ("PROTON", "PETREL", "ARIANA", "ARCHER")


class Team:
    """One designed battle: its trainer, stage, kind, Pokemon (team_kit.mon dicts) and the stages it can be fought at."""

    def __init__(self, tid, stage, kind, mons, items=""):
        self.tid, self.stage, self.kind, self.mons, self.items = tid, stage, kind, mons, items
        self.name = tid[len("TRAINER_"):-len("_HNS")]
        self.window = window(tid, stage, kind)

    def __repr__(self):
        return f"Team({self.tid}, {label(self.stage)})"


def boss_role(name):
    """A boss's line in the standard's table 4.1."""
    base = name.split("_")[0]
    if name.startswith("RIVAL_"):
        return "rival"
    if base in ROCKETS:
        return "rocket"
    if base == "LI":
        return "li"
    if f"TRAINER_{name}_HNS" in boss_teams.KIMONO:
        return "kimono"
    if name.endswith("_POSTOBC") or re.fullmatch(r"(?:%s)_2" % "|".join(JOHTO_LEADERS + ELITE_FOUR), name):
        return "rematch"
    if base in JOHTO_LEADERS and "_1" in name:
        return "gym"
    if base in ELITE_FOUR or base in KANTO_LEADERS or base == "RED":
        return "league"
    return "boss"


def window(tid, stage, kind):
    """The stages at which the battle can happen (the standard's section 1): a story battle fought once only at
    its stage; the Rocket Hideout with 4 to 6 badges; Gardenia's first team with 2 or 3; the Kanto leaders, the _2
    rematches and the rival at the Indigo Plateau from the Johto League to the Kanto League; everything else open
    to the end."""
    name = tid[len("TRAINER_"):-len("_HNS")]
    i = stage_index(stage)
    if name in ("PETREL_1", "ARIANA_1"):
        return STAGES[i:stage_index(6) + 1]
    if name == "SIDE_GARDENIA":
        return STAGES[i:stage_index(3) + 1]
    if kind == "boss":
        role = boss_role(name)
        if re.fullmatch(r"RIVAL_\w+_7", name) or role == "rematch" or name.split("_")[0] in KANTO_LEADERS:
            return STAGES[i:]
        if name != "EUSINE":
            return [stage]
    return STAGES[i:]


def rematch_families():
    """The HnS gRematchTable (src/battle_setup.c): first battle -> its tiers in order (repeated IDs once)."""
    with open(os.path.join(ROOT, "src", "battle_setup.c"), encoding="utf-8") as f:
        text = f.read()
    hns = text[text.index("#if IS_HNS"):text.index("#else", text.index("#if IS_HNS"))]
    out = {}
    for m in re.finditer(r"REMATCH\(([^)]*)\)", hns):
        ids = [p.strip() for p in m.group(1).split(",")][:5]
        out[ids[0]] = list(dict.fromkeys(i for i in ids if i != "0"))
    return out


REMATCH_FAMILIES = rematch_families()


def designed_teams():
    """Every designed team, in the tables' order."""
    out = []
    for tid, entry in boss_teams.TEAMS.items():
        stage, items, mons = entry[0], entry[1], entry[2]
        kind = "side" if tid.startswith("TRAINER_SIDE_") else "miniboss" if tid in boss_teams.ROUTE_BOSSES else "boss"
        out.append(Team(tid, stage, kind, mons, items))
    for a in ace_trainer_data.ACES:
        tid = f"TRAINER_ACE_{a['key']}_HNS"
        out.append(Team(tid, boss_teams.TEAM_STAGES[tid], "ace", a["team"]))
    for tid, mons in ace_trainer_data.UPGRADES.items():
        out.append(Team(tid, boss_teams.TEAM_STAGES[tid], "cooltrainer", mons))
    return out


# ---------------------------------------------------------------- one Pokemon, as the battle code fields it
class Mon:
    """A designed Pokemon with its build data looked up."""

    def __init__(self, db, m):
        self.m = m
        self.name = m["species"]
        self.species = db.canonical(team_kit.species_constant(m["species"]))
        self.info = db.get(self.species)
        self.item = team_kit.constant("ITEM", m["item"]) if m.get("item") else None
        self.item_info = db.item(self.item) if self.item else None
        self.hold = self.item_info["hold_effect"] if self.item_info else None
        self.ability = team_kit.constant("ABILITY", m["ability"]) if m.get("ability") else None
        self.nature = m.get("nature")
        self.moves = [(mv, team_kit.constant("MOVE", mv)) for mv in m["moves"]]
        self.move_info = [(mv, db.move(k) or {}) for mv, k in self.moves]
        self.keys = [db.move_aliases.get(k, k)[len("MOVE_"):] for _, k in self.moves]
        self.raised_item = team_kit.constant("ITEM", m["raised_item"]) if m.get("raised_item") else None
        self.mega = (db.mega.get(self.item) or {}).get(self.species) if self.item else None
        # A Mega Stone holder is judged by its Mega's ability (it battles as the Mega)
        mega_info = db.get(self.mega) if self.mega else None
        self.battle_ability = (mega_info["abilities"][0] if mega_info else None) or self.ability
        self.types = (mega_info or self.info or {}).get("types", [])

    def attacks(self):
        return [(mv, mi) for mv, mi in self.move_info if is_attack(mi)]

    def attack_profile(self):
        """(physical attacks, special attacks), leaving out the ones that don't use the user's attacking stat."""
        phys = spec = 0
        for _, mi in self.attacks():
            if mi.get("effect") in FIXED_DAMAGE or mi.get("effect") in ("EFFECT_FOUL_PLAY", "EFFECT_BODY_PRESS"):
                continue
            if mi["category"] == "DAMAGE_CATEGORY_PHYSICAL":
                phys += 1
            else:
                spec += 1
        return phys, spec


def is_attack(mi):
    return mi.get("category") in ("DAMAGE_CATEGORY_PHYSICAL", "DAMAGE_CATEGORY_SPECIAL") and (mi.get("power") or 0) > 0


def has_secondary(mi):
    return any(not e["self"] for e in mi.get("effects", []))


def self_drop(mi):
    if mi.get("effect") in ("EFFECT_SHELL_SMASH", "EFFECT_MAKE_IT_RAIN", "EFFECT_SPIN_OUT"):
        return True
    return any(e["self"] and ("DOWN" in e["effect"] or "MINUS" in e["effect"] or e["effect"] == "MOVE_EFFECT_V_CREATE")
               for e in mi.get("effects", []))


def is_multi_hit(mi):
    return "multiHit" in mi.get("flags", set()) or (mi.get("strikeCount") or 0) > 1


def move_type(mi, ability):
    t = mi.get("type")
    if ability in ATE and t == "TYPE_NORMAL" and is_attack(mi):
        return ATE[ability]
    if ability == "ABILITY_LIQUID_VOICE" and "soundMove" in mi.get("flags", set()):
        return "TYPE_WATER"
    return t


def effective_power(mv, mi, mon, ctx):
    """An attack's power as rule M5 counts it (gaps.md 8): Technician, multi-hit moves, Facade with an Orb,
    Acrobatics without an item; 0 for fixed damage."""
    p, eff = mi.get("power") or 0, mi.get("effect")
    if eff in FIXED_DAMAGE:
        return 0
    if eff in VARIABLE_POWER or p == 1:
        p = 80
    if eff in ("EFFECT_RETURN", "EFFECT_FRUSTRATION"):
        p = 102
    adj = p
    if "multiHit" in mi.get("flags", set()):
        adj = p * (5 if mon.battle_ability == "ABILITY_SKILL_LINK" else 4.5 if mon.hold == "HOLD_EFFECT_LOADED_DICE" else 3)
    elif (mi.get("strikeCount") or 0) > 1:
        n = mi["strikeCount"]
        adj = p * (n * (n + 1) // 2 if eff == "EFFECT_TRIPLE_KICK" else (10 if mon.battle_ability == "ABILITY_SKILL_LINK" else 6)
                   if eff == "EFFECT_POPULATION_BOMB" else n)
    if eff == "EFFECT_FACADE" and (mon.hold in ("HOLD_EFFECT_FLAME_ORB", "HOLD_EFFECT_TOXIC_ORB")
                                   or mon.battle_ability == "ABILITY_COMATOSE"):
        adj = 140
    if eff == "EFFECT_ACROBATICS" and (not mon.hold or mon.hold in CONSUMABLE):
        adj = 110 if not mon.hold else 82
    if eff == "EFFECT_WEATHER_BALL" and ctx["weather"]:
        adj = 100
    if mon.battle_ability == "ABILITY_TECHNICIAN" and p <= 60:
        adj = adj * 1.5
    return adj


def set_role(mon):
    """"support" (at most one attack, or two attacks and two support moves), "attacker" or "mixed" (gaps.md 8)."""
    attacks = sum(1 for _, mi in mon.attacks() if mi.get("effect") not in FIXED_DAMAGE)
    support_moves = ROLES["recovery"] | ROLES["status"] | ROLES["hazard"] | ROLES["screens"] | ROLES["trickroom"] \
        | ROLES["phazing"] | ROLES["disruption"] | ROLES["tailwind"] | ROLES["hazard_control"] \
        | {"U_TURN", "VOLT_SWITCH", "FLIP_TURN", "PARTING_SHOT", "TELEPORT"}
    support = sum(1 for k, (_, mi) in zip(mon.keys, mon.move_info)
                  if k in support_moves or mi.get("effect") in FIXED_DAMAGE)
    if attacks <= 1 or (support >= 2 and attacks <= 2):
        return "support"
    if attacks >= 3 or (any(k in ROLES["setup"] for k in mon.keys) and attacks >= 2):
        return "attacker"
    return "mixed"


def stats(base, level, ivs, evs, nature):
    up, down = NATURES.get(nature or "Hardy", (None, None))
    out = {}
    for s in team_kit.STATS:
        v = (2 * base[s] + ivs[s] + evs[s] // 4) * level // 100
        if s == "HP":
            out[s] = v + level + 10
        else:
            v += 5
            out[s] = v * 110 // 100 if s == up else v * 90 // 100 if s == down else v
    return out


def bulk_ratios(db, species, target, level, nature=None, evs=None):
    """(physical, special): the species' HP x Def and HP x SpD with an Eviolite's 1.5 over the target's."""
    ivs = dict.fromkeys(team_kit.STATS, 31)
    evs = evs or dict.fromkeys(team_kit.STATS, 0)
    s, t = stats(db.get(species)["base"], level, ivs, evs, nature), stats(db.get(target)["base"], level, ivs, evs, nature)
    return s["HP"] * s["Def"] * 1.5 / (t["HP"] * t["Def"]), s["HP"] * s["SpD"] * 1.5 / (t["HP"] * t["SpD"])


def tier_a(db, species, level, nature=None, evs=None):
    """Rule E3's test: with the Eviolite, at least 1.10 times the bulk of every most-evolved form it could be at
    this level (item, trade, friendship and move steps always, a level step when due)."""
    finals = db.final_forms(species, level)
    return bool(finals) and all(min(bulk_ratios(db, species, f, level, nature, evs)) >= TIER_A for f in finals)


def named_eviolite_tiers(db):
    """{species: lowest bulk ratio} for every species whose next evolutions are all non-level ones and that is
    tier A at every cap from 33 to 100 (31 IVs, no EVs, a neutral nature): the standard's table 3.2."""
    out = {}
    for name in db.species:
        evos = db.evolutions(name)
        if not evos or any(e.kind == "level" for e in evos):
            continue
        worst = None
        for stage in STAGES[stage_index(2):]:
            for f in db.final_forms(name, cap(stage)):
                r = min(bulk_ratios(db, name, f, cap(stage)))
                worst = r if worst is None else min(worst, r)
        if worst is not None and worst >= TIER_A:
            out[name] = round(worst, 2)
    return out


def kept_unevolved(species, hold):
    """IsKeptUnevolved (src/battle_main.c): a named Eviolite species holding an Eviolite, a Pikachu a Light Ball."""
    if hold == "HOLD_EFFECT_EVIOLITE":
        return species in NAMED_CONSTANTS
    if hold == "HOLD_EFFECT_LIGHT_BALL":
        return species.startswith("SPECIES_PIKACHU")
    return False


NAMED_CONSTANTS = {team_kit.species_constant(n) for n in team_kit.NAMED_EVIOLITE}


def battle_species(db, mon, team_stage, stage):
    """GetTrainerMonEvolvedSpecies for a team made for a stage, at this stage's NORMAL cap."""
    level, sp = cap(stage), mon.species
    if level <= cap(team_stage):
        return sp
    for _ in range(2):
        if kept_unevolved(sp, mon.hold):
            break
        nxt = next((e.target for e in db.evolutions(sp) if 0 < e.trainer_level <= level), None)
        if nxt is None:
            break
        sp = nxt
    return sp


def battle_item(db, mon, team_stage, stage):
    """The item it holds there: its raised_item once it has evolved, if it has one."""
    if mon.raised_item and battle_species(db, mon, team_stage, stage) != mon.species:
        return mon.raised_item
    return mon.item


def item_works_for(db, item, species):
    """False when the item does nothing for this species: an Eviolite on a fully evolved one, an item for
    another species, an Everstone."""
    info = db.item(item) or {}
    hold = info.get("hold_effect")
    if hold == "HOLD_EFFECT_EVIOLITE":
        return bool(db.evolutions(species))
    if hold == "HOLD_EFFECT_PREVENT_EVOLVE":
        return False
    if item in SPECIES_ITEMS:
        return any(species == s or species.startswith(s + "_") for s in SPECIES_ITEMS[item])
    return True


# ---------------------------------------------------------------- where the trainers battle
TRAINERBATTLE = re.compile(r"^\s*([Tt]rainerbattle\w*|multi_2_vs_2)\s+(TRAINER_\w+)(?:\s*,\s*(?:\w+\s*,\s*)?(TRAINER_\w+))?", re.M)
LABEL = re.compile(r"^(\w+)::?\s*$", re.M)


def _labels(text):
    out = {}
    ms = list(LABEL.finditer(text))
    for i, m in enumerate(ms):
        out[m.group(1)] = text[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(text)]
    return out


def _battles_in(label, bodies, depth=0, seen=None):
    seen = set() if seen is None else seen
    if label in seen or depth > 4 or label not in bodies:
        return []
    seen.add(label)
    found = []
    for m in TRAINERBATTLE.finditer(bodies[label]):
        found.append((m.group(1), m.group(2), m.group(3)))
    for m in re.finditer(r"\b(goto|call)(?:_if\w*)?\b[^\n]*", bodies[label]):
        for tok in re.findall(r"\b([A-Z]\w+)\b", m.group(0)):
            if tok in bodies and tok != label:
                found += _battles_in(tok, bodies, depth + 1, seen)
    return found


class Maps:
    """Heart & Soul's maps: their weather, the trainer objects on them, and the trainers each map's scripts battle
    (gaps.md's placement method)."""

    def __init__(self):
        shared = {}
        for path in glob.glob(os.path.join(ROOT, "data", "scripts", "*.inc")):
            with open(path, encoding="utf-8") as f:
                shared.update(_labels(f.read()))
        self.weather, self.map_of, self.objects, self.pairs, self.ids, self.near = {}, {}, {}, [], {}, {}
        self.static = {}  # species -> the maps whose scripts give it or start a battle with it
        for path in sorted(glob.glob(os.path.join(ROOT, "data", "maps", "*_hns", "map.json"))):
            folder = os.path.basename(os.path.dirname(path))
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
            self.ids[d["id"]] = folder
            self.weather[folder] = MAP_WEATHER.get(d.get("weather"))
            self.near[folder] = {c["map"] for c in d.get("connections") or []} | \
                {w["dest_map"] for w in d.get("warp_events") or []}
            scripts = os.path.join(os.path.dirname(path), "scripts.inc")
            text = open(scripts, encoding="utf-8").read() if os.path.exists(scripts) else ""
            bodies = dict(shared)
            bodies.update(_labels(text))
            objs = []
            for o in d.get("object_events") or []:
                script = o.get("script")
                if not script or script == "NULL":
                    continue
                for macro, a, b in _battles_in(script, bodies):
                    objs.append({"trainer": a, "x": int(o["x"]), "y": int(o["y"]), "type": o.get("trainer_type"),
                                 "sight": int(o.get("trainer_sight_or_berry_tree_id") or 0),
                                 "facing": o.get("movement_type", "")})
                    self.map_of.setdefault(a, folder)
            self.objects[folder] = objs
            # The Pokemon the map's scripts make the player meet (Heart & Soul's static encounters are
            # seteventmon, which validate.py's encounter list doesn't read)
            for sp in re.findall(r"\b(?:seteventmon|setwildbattle|givemon|giveegg)\s*\(?\s*(SPECIES_\w+)", text):
                self.static.setdefault(sp, set()).add(folder)
            for m in TRAINERBATTLE.finditer(text):
                self.map_of.setdefault(m.group(2), folder)
                if m.group(3):
                    self.map_of.setdefault(m.group(3), folder)
                    self.pairs.append((m.group(1), m.group(2), m.group(3)))
        for a in ace_trainer_data.ACES:
            self.map_of[f"TRAINER_ACE_{a['key']}_HNS"] = a["map"]
        # A phone rematch tier battles where the first battle's trainer stands
        for first, tiers in REMATCH_FAMILIES.items():
            for tid in tiers[1:]:
                if first in self.map_of:
                    self.map_of.setdefault(tid, self.map_of[first])
        self.near = {k: {self.ids.get(v, v) for v in vs} for k, vs in self.near.items()}

    def sight_partners(self, tid):
        """The trainers on its map whose line of sight meets its own (a straight line of its sight range in the
        direction it faces, as ace_trainers.py checks it): they can see the player at once and battle together."""
        folder = self.map_of.get(tid)
        if not folder:
            return []
        dirs = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}

        def line(o):
            if o["type"] not in ("TRAINER_TYPE_NORMAL", "TRAINER_TYPE_SEE_ALL_DIRECTIONS") or o["sight"] <= 0:
                return set()
            facings = list(dirs) if o["type"] == "TRAINER_TYPE_SEE_ALL_DIRECTIONS" else \
                [d for d in dirs if o["facing"].endswith(d)]
            return {(o["x"] + dx * i, o["y"] + dy * i) for d in facings for dx, dy in [dirs[d]]
                    for i in range(1, o["sight"] + 1)}
        mine = [o for o in self.objects[folder] if o["trainer"] == tid]
        out = set()
        for me in mine:
            ours = line(me)
            for o in self.objects[folder]:
                if o["trainer"] != tid and ours & line(o):
                    out.add(o["trainer"])
        return sorted(out)


# ---------------------------------------------------------------- the checks
class Findings:
    def __init__(self):
        self.rows = []  # [severity the rule gives it, rule, trainer, text]

    def add(self, rule, team, text, warn=False):
        self.rows.append(("WARNING" if warn else "ERROR", rule, team.tid if hasattr(team, "tid") else team, text))

    def settle(self):
        """The findings with the severity they have now: a [V] rule's finding is a warning while the rule is
        pending for its trainer."""
        return [["WARNING" if sev == "ERROR" and (rule in PENDING_EVERYWHERE or tid in PENDING.get(rule, ())) else sev,
                 rule, tid, text] for sev, rule, tid, text in self.rows]


def team_context(db, team, mons, maps):
    weather, tr_setters = set(), 0
    for mon in mons:
        for ab in (mon.ability, mon.battle_ability):
            if ab in WEATHER_SETTER_ABILITY:
                weather.add(WEATHER_SETTER_ABILITY[ab])
        for k in mon.keys:
            if k in WEATHER_MOVES:
                weather.add(WEATHER_MOVES[k])
        tr_setters += "TRICK_ROOM" in mon.keys
    folder = maps.map_of.get(team.tid)
    map_weather = maps.weather.get(folder) if folder else None
    if map_weather:
        weather.add(map_weather)
    slow = sum(1 for m in mons if m.info and m.info["base"]["Spe"] <= 60)
    return {"weather": weather, "map_weather": map_weather, "map": folder, "trick_room": tr_setters > 0,
            "tr_setters": tr_setters, "slow": slow, "tr_team": tr_setters >= 2 or (tr_setters == 1 and slow >= 3)}


def check_mon(db, f, team, mon, slot, ctx):
    """The rules on one Pokemon."""
    who = f"{mon.name} (slot {slot + 1})"
    if not mon.info:
        f.add("A1", team, f"{who}: unknown species {mon.species}")
        return
    # ---- E1 to E7: evolution, at every stage of the battle's window as the battle code fields it
    if mon.hold == "HOLD_EFFECT_PREVENT_EVOLVE":
        f.add("E7", team, f"{who}: an Everstone does nothing in battle and keeps a raised Pokemon unevolved")
    found = collections.defaultdict(list)  # rule -> [(stage, text)]
    evolved_somewhere = False
    for stage in team.window:
        level, sp = cap(stage), battle_species(db, mon, team.stage, stage)
        name = sp[8:].replace("_", " ").title()
        due = [e for e in db.evolutions(sp) if e.kind == "level" and e.param <= level]
        if due:
            found["E1"].append((stage, f"{name} at {level}, past {due[0].target[8:].replace('_', ' ').title()}'s "
                                       f"{due[0].param}"))
        other = [e for e in db.evolutions(sp) if e.kind != "level" and e.trainer_level == species_db.TRAINER_OTHER_EVOLUTION_LEVEL]
        kept = kept_unevolved(sp, mon.hold)
        if other and stage_index(stage) >= 2 and not kept:
            found["E2"].append((stage, f"{name} at {level} unevolved: it evolves by {other[0].kind} into "
                                       f"{other[0].target[8:].replace('_', ' ').title()}, and from stage 2 only a named "
                                       f"Eviolite species holding an Eviolite, or a Pikachu holding a Light Ball, stays"))
        if kept and mon.hold == "HOLD_EFFECT_EVIOLITE" and other and stage_index(stage) >= 2 and not tier_a(
                db, sp, level, mon.nature, team_kit.evs_of(mon.m)):
            found["E3"].append((stage, f"{name} at {level}: with its nature and EVs its Eviolite bulk is under 1.10 times "
                                       f"its evolutions'"))
        if sp != mon.species:
            evolved_somewhere = True
            held = battle_item(db, mon, team.stage, stage)
            if held and not item_works_for(db, held, sp):
                found["E6"].append((stage, f"{name} at {level}, holding its {held[5:].replace('_', ' ').title()}, which "
                                           f"does nothing for it: it needs a raised_item"))
    for rule, hits in found.items():
        stages = [label(s) for s, _ in hits]
        where = f"stage {stages[0]}" if len(stages) == 1 else f"stages {', '.join(stages)}"
        f.add(rule, team, f"{who}, fought at {where}: {hits[0][1]}")
    if mon.raised_item and not evolved_somewhere:
        f.add("E6", team, f"{who}: raised_item {mon.m['raised_item']}, but it never evolves in its battle's window "
                          f"(stages {label(team.window[0])} to {label(team.window[-1])})", warn=True)
    if mon.raised_item and not db.item(mon.raised_item):
        f.add("E6", team, f"{who}: raised_item {mon.m['raised_item']} is no item ({mon.raised_item})")
    if mon.hold == "HOLD_EFFECT_EVIOLITE" and kept_unevolved(mon.species, mon.hold) and stage_index(team.stage) >= 2:
        roles = {r for r in ("recovery", "status", "hazard", "pivot", "screens", "trickroom", "phazing")
                 if any(k in ROLES[r] for k in mon.keys)}
        if not roles:
            f.add("E3", team, f"{who}: a named Eviolite species whose set uses none of its bulk (no recovery, status, "
                              f"hazards, pivot, screens, Trick Room or phazing)", warn=True)
    ahead = db.reach_level(mon.species) - cap(team.stage)
    if ahead > 6:
        f.add("E5", team, f"{who}: {ahead} levels before its line reaches it by level-up "
                          f"({db.reach_level(mon.species)}, its team's level {cap(team.stage)})")
    # ---- I1, I4, I7: held items
    if not mon.item:
        f.add("I1", team, f"{who} holds no item")
    elif mon.item_info is None:
        f.add("I1", team, f"{who}: {mon.m['item']} is no item ({mon.item})")
    else:
        check_item(db, f, team, mon, who, ctx)
    # ---- A2: an ability that does something here
    dead = dead_ability(db, mon, ctx)
    if dead:
        f.add("A2", team, f"{who}: {dead}")
    # ---- N1, N2, V2, V3: nature and IVs
    phys, spec = mon.attack_profile()
    up, down = NATURES.get(mon.nature or "", (None, None))
    role = set_role(mon)
    if not mon.nature:
        f.add("N1", team, f"{who} has no nature (trainerproc writes Hardy)")
    elif ((phys >= 2 and not spec) or (phys == 1 and not spec and role == "attacker")) and down == "Atk":
        f.add("N1", team, f"{who}: {mon.nature} lowers the Attack its physical set attacks with")
    elif spec and not phys and down == "SpA":
        f.add("N1", team, f"{who}: {mon.nature} lowers the Sp. Atk its special set attacks with")
    gyro = any(mi.get("effect") == "EFFECT_GYRO_BALL" for _, mi in mon.move_info)
    # A Trick Room setter, a member of a Trick Room team (rule P2's: on a fast team with one setter, rule P2 fails
    # the team instead), or a Gyro Ball user
    slow_set = "TRICK_ROOM" in mon.keys or gyro or ctx["tr_team"]
    why = "with Gyro Ball" if gyro else "setting Trick Room" if "TRICK_ROOM" in mon.keys else "on a Trick Room team"
    base_speed = mon.info["base"]["Spe"]
    if slow_set and down != "Spe" and base_speed > 30:
        f.add("N2", team, f"{who}: {why} with {mon.nature}, which doesn't lower Speed (base {base_speed})")
    if ctx["tr_team"] and up == "Spe":
        f.add("P2", team, f"{who}: {mon.nature} raises Speed on a Trick Room team")
    ivs = team_kit.ivs_of(mon.m)
    if slow_set and ivs["Spe"] != 0:
        f.add("V2", team, f"{who}: {ivs['Spe']} Speed IVs {why} (ivs=\"0 Spe\")")
    if "HIDDEN_POWER" in mon.keys:
        bits = sum((ivs[s] & 1) << i for i, s in enumerate(("HP", "Atk", "Def", "Spe", "SpA", "SpD")))
        hp_type = HIDDEN_POWER_TYPES[bits * 15 // 63]
        if not mon.m.get("ivs"):
            f.add("V3", team, f"{who}: Hidden Power with 31 IVs is {hp_type}; its ivs must give the type it is meant to be")
    # ---- M2 to M7: moves
    check_moves(db, f, team, mon, who, ctx, role)


def check_item(db, f, team, mon, who, ctx):
    hold, item, keys = mon.hold, mon.item, set(mon.keys)
    attacks = mon.attacks()
    phys, spec = mon.attack_profile()
    problems = []
    if hold in ("HOLD_EFFECT_CHOICE_BAND", "HOLD_EFFECT_CHOICE_SPECS", "HOLD_EFFECT_CHOICE_SCARF"):
        status = [mv for mv, mi in mon.move_info if not is_attack(mi) and mi.get("effect") not in ("EFFECT_TRICK",)]
        if status:
            problems.append(f"{mon.m['item']} with status or setup moves it would be locked into: {', '.join(status)}")
    if hold == "HOLD_EFFECT_ASSAULT_VEST":
        status = [mv for mv, mi in mon.move_info if not is_attack(mi)]
        if status:
            problems.append(f"an Assault Vest forbids status moves: {', '.join(status)}")
    if item == "ITEM_LIGHT_CLAY" and not keys & ROLES["screens"]:
        problems.append("Light Clay without Reflect, Light Screen or Aurora Veil")
    if hold == "HOLD_EFFECT_LOADED_DICE" and not any(is_multi_hit(mi) for _, mi in mon.move_info):
        problems.append("Loaded Dice without a multi-hit move")
    if item in WEATHER_ROCKS:
        own = WEATHER_SETTER_ABILITY.get(mon.ability) == WEATHER_ROCKS[item] or any(
            WEATHER_MOVES.get(k) == WEATHER_ROCKS[item] for k in keys)
        if not own:
            problems.append(f"{mon.m['item']} without its own {WEATHER_ROCKS[item]} setter")
    if hold == "HOLD_EFFECT_POWER_HERB" and not any(mi.get("effect") in CHARGE_EFFECTS for _, mi in mon.move_info):
        problems.append("a Power Herb without a charging move")
    if hold == "HOLD_EFFECT_WHITE_HERB" and not (any(self_drop(mi) for _, mi in mon.move_info)
                                                 or mon.battle_ability == "ABILITY_UNBURDEN"):
        problems.append("a White Herb without Shell Smash or a move that lowers its own stats")
    if hold in ("HOLD_EFFECT_FLAME_ORB", "HOLD_EFFECT_TOXIC_ORB") and mon.battle_ability not in ORB_ABILITIES \
            and "FACADE" not in keys and "PSYCHO_SHIFT" not in keys:
        problems.append(f"a {mon.m['item']} without Guts, Poison Heal, Toxic Boost, Flare Boost, Quick Feet, Marvel "
                        f"Scale or Facade")
    if hold == "HOLD_EFFECT_EVIOLITE" and not db.evolutions(mon.species):
        problems.append("an Eviolite on a fully evolved Pokemon")
    if hold == "HOLD_EFFECT_FOCUS_SASH" and mon.battle_ability == "ABILITY_STURDY":
        problems.append("a Focus Sash on a Sturdy Pokemon")
    if hold in ("HOLD_EFFECT_TYPE_POWER", "HOLD_EFFECT_PLATE", "HOLD_EFFECT_GEMS"):
        ty = mon.item_info.get("secondaryId")
        if isinstance(ty, str) and ty.startswith("TYPE_") and not any(
                move_type(mi, mon.battle_ability) == ty for _, mi in attacks):
            problems.append(f"{mon.m['item']} boosts {ty[5:].title()} attacks; the set has none")
    if item in SPECIES_ITEMS and not item_works_for(db, item, mon.species):
        problems.append(f"{mon.m['item']} works only for {', '.join(s[8:].title() for s in SPECIES_ITEMS[item])}")
    if hold == "HOLD_EFFECT_MEGA_STONE" and not mon.mega:
        problems.append(f"{mon.m['item']} is not {mon.name}'s Mega Stone")
    if hold == "HOLD_EFFECT_BLACK_SLUDGE" and "TYPE_POISON" not in (mon.info or {}).get("types", []) \
            and mon.battle_ability not in ("ABILITY_MAGIC_GUARD", "ABILITY_KLUTZ"):
        problems.append("Black Sludge hurts a holder that is not Poison-type")
    if hold == "HOLD_EFFECT_THROAT_SPRAY" and not any("soundMove" in mi.get("flags", set()) for _, mi in mon.move_info):
        problems.append("a Throat Spray without a sound move")
    for p in problems:
        f.add("I4", team, f"{who}: {p}")
    # I7: the deliberate pairs
    if hold == "HOLD_EFFECT_BOOSTER_ENERGY" and mon.battle_ability not in ("ABILITY_PROTOSYNTHESIS", "ABILITY_QUARK_DRIVE"):
        f.add("I7", team, f"{who}: Booster Energy without Protosynthesis or Quark Drive")
    if item == "ITEM_TERRAIN_EXTENDER" and not ({mon.battle_ability} | {f"MOVE_{k}" for k in keys}) & TERRAIN_SETTERS:
        f.add("I7", team, f"{who}: a Terrain Extender without a terrain setter")
    if item in WEATHER_ROCKS and WEATHER_ROCKS[item] not in ctx["weather"]:
        f.add("I7", team, f"{who}: {mon.m['item']} without a {WEATHER_ROCKS[item]} setter on the team")
    # I5 (warning): weak items for a designed set
    stage2 = stage_index(team.stage) >= 2
    if (item in ("ITEM_ORAN_BERRY", "ITEM_BERRY_JUICE") and stage2) or item in (
            "ITEM_SHELL_BELL", "ITEM_QUICK_CLAW", "ITEM_BRIGHT_POWDER", "ITEM_LAX_INCENSE") or (
            item == "ITEM_KINGS_ROCK" and mon.battle_ability != "ABILITY_SERENE_GRACE"):
        f.add("I5", team, f"{who}: {mon.m['item']} is a weak item for a designed set", warn=True)


def dead_ability(db, mon, ctx):
    """Rule A2: why the ability does nothing in this set, or None. A Mega Stone holder battles with its Mega's."""
    ak = mon.battle_ability
    infos = [mi for _, mi in mon.move_info]
    if mon.mega:
        return None
    others = [a for a in mon.info.get("abilities", []) if a not in ("ABILITY_NONE", ak)]
    has = (", it has " + ", ".join(a[8:].replace("_", " ").title() for a in others)) if others else ""
    if ak in WEATHER_ABUSERS and WEATHER_ABUSERS[ak] not in ctx["weather"]:
        return f"{mon.m['ability']} without {WEATHER_ABUSERS[ak]} on the team or the map{has}"
    if ak == "ABILITY_TECHNICIAN" and not any(is_attack(mi) and 1 < (mi.get("power") or 0) <= 60 for mi in infos):
        return f"Technician without a move of 60 power or less{has}"
    if ak == "ABILITY_ROCK_HEAD" and not any(mi.get("effect") == "EFFECT_RECOIL" for mi in infos):
        return f"Rock Head without a recoil move{has}"
    if ak == "ABILITY_RECKLESS" and not any(mi.get("effect") in ("EFFECT_RECOIL", "EFFECT_RECOIL_IF_MISS") for mi in infos):
        return f"Reckless without a recoil move{has}"
    for ability, flag, what in (("ABILITY_IRON_FIST", "punchingMove", "a punching move"),
                                ("ABILITY_STRONG_JAW", "bitingMove", "a biting move"),
                                ("ABILITY_MEGA_LAUNCHER", "pulseMove", "a pulse move"),
                                ("ABILITY_SHARPNESS", "slicingMove", "a slicing move"),
                                ("ABILITY_PUNK_ROCK", "soundMove", "a sound move"),
                                ("ABILITY_LIQUID_VOICE", "soundMove", "a sound move")):
        if ak == ability and not any(flag in mi.get("flags", set()) for mi in infos):
            return f"{mon.m['ability']} without {what}{has}"
    if ak == "ABILITY_SKILL_LINK" and not any("multiHit" in mi.get("flags", set()) for mi in infos):
        return f"Skill Link without a multi-hit move{has}"
    if ak in ("ABILITY_SERENE_GRACE", "ABILITY_SHEER_FORCE") and not any(is_attack(mi) and has_secondary(mi) for mi in infos):
        return f"{mon.m['ability']} without a move with a secondary effect{has}"
    if ak in ("ABILITY_HARVEST", "ABILITY_RIPEN", "ABILITY_CHEEK_POUCH", "ABILITY_GLUTTONY") and not (
            mon.item_info and mon.item_info.get("pocket") == "POCKET_BERRIES"):
        return f"{mon.m['ability']} without a Berry{has}"
    if ak == "ABILITY_UNBURDEN" and mon.hold not in CONSUMABLE:
        return f"Unburden with an item that is never used up{has}"
    if ak in ATE and not any(mi.get("type") == "TYPE_NORMAL" and is_attack(mi) for mi in infos):
        return f"{mon.m['ability']} without a Normal-type attack{has}"
    if ak == "ABILITY_POISON_HEAL" and mon.item != "ITEM_TOXIC_ORB":
        return f"Poison Heal without a Toxic Orb{has}"
    if ak in ("ABILITY_TOXIC_BOOST", "ABILITY_FLARE_BOOST") and mon.item not in ("ITEM_TOXIC_ORB", "ITEM_FLAME_ORB"):
        return f"{mon.m['ability']} without its Orb{has}"
    if ak in ("ABILITY_PICKUP", "ABILITY_RUN_AWAY", "ABILITY_HONEY_GATHER", "ABILITY_BALL_FETCH", "ABILITY_ILLUMINATE"):
        return f"{mon.m['ability']} does nothing in a trainer battle{has}"
    if ak == "ABILITY_PRANKSTER" and all(is_attack(mi) for mi in infos):
        return f"Prankster without a status move{has}"
    if ak == "ABILITY_CONTRARY" and not any(self_drop(mi) for mi in infos):
        return f"Contrary without a move that lowers its own stats{has}"
    return None


def check_moves(db, f, team, mon, who, ctx, role):
    keys = set(mon.keys)
    attacks = mon.attacks()
    if mon.keys == ["TRANSFORM"]:
        return  # Ditto: Transform alone (rule M2's one exemption)
    filler = [mv for (mv, _), k in zip(mon.moves, mon.keys) if k in FILLER]
    hold = mon.hold
    if "FOCUS_ENERGY" in keys and mon.battle_ability not in ("ABILITY_SNIPER", "ABILITY_SUPER_LUCK"):
        filler.append("Focus Energy")
    if keys & {"MIND_READER", "LOCK_ON"} and not any(0 < (mi.get("accuracy") or 0) < 75 for _, mi in mon.move_info):
        filler.append("Mind Reader" if "MIND_READER" in keys else "Lock-On")
    if "DEFENSE_CURL" in keys and not keys & {"ROLLOUT", "ICE_BALL"}:
        filler.append("Defense Curl")
    if "DREAM_EATER" in keys and not keys & {"SPORE", "SLEEP_POWDER", "HYPNOSIS", "LOVELY_KISS", "DARK_VOID", "SING",
                                              "GRASS_WHISTLE", "YAWN"}:
        filler.append("Dream Eater")
    if "REST" in keys and not ("SLEEP_TALK" in keys or mon.battle_ability in ("ABILITY_SHED_SKIN", "ABILITY_NATURAL_CURE")
                               or mon.item in ("ITEM_CHESTO_BERRY", "ITEM_LUM_BERRY")):
        filler.append("Rest")
    if filler:
        f.add("M2", team, f"{who}: filler: {', '.join(filler)}")
    weak = [mv for (mv, _), k in zip(mon.moves, mon.keys) if k in WEAK_SETUP and not (
        k == "GROWTH" and "sun" in ctx["weather"]) and not keys & {"POWER_TRIP", "STORED_POWER"}]
    if weak:
        f.add("M7", team, f"{who}: weak setup: {', '.join(weak)}", warn=True)
    if role == "support":
        return
    stab_types = set(mon.types) | set((mon.info or {}).get("types", []))
    if attacks and not any(move_type(mi, mon.battle_ability) in stab_types for _, mi in attacks) \
            and not any(mi.get("effect") in FIXED_DAMAGE for _, mi in attacks):
        f.add("M3", team, f"{who}: no attack of its own type", warn=True)
    types = {move_type(mi, mon.battle_ability) for _, mi in attacks if mi.get("effect") not in FIXED_DAMAGE}
    if len(types) < 2:
        f.add("M4", team, f"{who}: an attacker with {'one attacking type' if types else 'no attack'}")
    if stage_index(team.stage) >= 2 and attacks:
        best = max(effective_power(mv, mi, mon, ctx) for mv, mi in attacks)
        if 0 < best < 70:
            f.add("M5", team, f"{who}: its strongest attack has {best:g} power")
    for mv, mi in mon.move_info:
        acc = mi.get("accuracy") or 0
        if not (0 < acc < M6_ACCURACY) or not is_attack(mi):
            continue
        enabled = mon.battle_ability in ("ABILITY_NO_GUARD", "ABILITY_COMPOUND_EYES") or keys & {"MIND_READER", "LOCK_ON"}
        if "alwaysHitsInRain" in mi.get("flags", set()) and "rain" in ctx["weather"]:
            enabled = True
        if "alwaysHitsInHailSnow" in mi.get("flags", set()) and "snow" in ctx["weather"]:
            enabled = True
        if not enabled:
            f.add("M6", team, f"{who}: {mv} at {acc}% accuracy without its enabler")


WEATHER_TYPES = {"rain": "TYPE_WATER", "sun": "TYPE_FIRE", "sand": "TYPE_ROCK", "snow": "TYPE_ICE"}
WEATHER_ACCURACY = {"rain": "alwaysHitsInRain", "snow": "alwaysHitsInHailSnow"}
SUN_MOVES = {"SOLAR_BEAM", "SOLAR_BLADE", "GROWTH", "SYNTHESIS", "MORNING_SUN", "MOONLIGHT", "WEATHER_BALL"}


def uses_weather(mon, weather):
    """The Pokemon profits from the weather: an ability for it, a move it makes sure to hit, Weather Ball, or an
    attack of the type it boosts (rain: Water, sun: Fire) or a type it shields (sand: Rock, snow: Ice)."""
    if WEATHER_ABUSERS.get(mon.battle_ability) == weather or mon.battle_ability == "ABILITY_DRY_SKIN" and weather == "rain":
        return True
    for k, (_, mi) in zip(mon.keys, mon.move_info):
        if k == "WEATHER_BALL" or WEATHER_ACCURACY.get(weather) in mi.get("flags", set()):
            return True
        if weather in ("rain", "sun") and is_attack(mi) and move_type(mi, mon.battle_ability) == WEATHER_TYPES[weather]:
            return True
    return weather in ("sand", "snow") and WEATHER_TYPES[weather] in mon.types


def needs_weather(mon, weather):
    """The Pokemon's set depends on a weather: an ability that works only in it, or (sun) a move that needs it."""
    if WEATHER_ABUSERS.get(mon.battle_ability) == weather:
        return True
    return weather == "sun" and any(k in ("SOLAR_BEAM", "SOLAR_BLADE") for k in mon.keys) and mon.hold != "HOLD_EFFECT_POWER_HERB"


def check_team(db, f, team, maps, all_teams, encounters):
    mons = [Mon(db, m) for m in team.mons]
    ctx = team_context(db, team, mons, maps)
    for slot, mon in enumerate(mons):
        check_mon(db, f, team, mon, slot, ctx)
    st = stage_index(team.stage)
    # ---- Z1: team size (the standard's table 4.1)
    want = team_size(team)
    if want and not want[0] <= len(mons) <= want[1]:
        f.add("Z1", team, f"{len(mons)} Pokemon; its kind has {want[0]}" + (f" to {want[1]}" if want[1] != want[0] else "")
              + f" at stage {label(team.stage)}")
    # ---- I3: no item more than twice, at most one item twice, Eviolites
    items = collections.Counter(m.item for m in mons if m.item)
    thrice = [f"{i[5:].replace('_', ' ').title()} x{n}" for i, n in items.items() if n > 2]
    twice = [i for i, n in items.items() if n == 2]
    eviolites = items.get("ITEM_EVIOLITE", 0)
    if thrice:
        f.add("I3", team, f"an item more than twice: {', '.join(thrice)}")
    if len(twice) > 1:
        f.add("I3", team, f"{len(twice)} items twice: {', '.join(i[5:].replace('_', ' ').title() for i in twice)}")
    if eviolites > (1 if st >= 2 else 2) and not thrice:
        f.add("I3", team, f"{eviolites} Eviolites at stage {label(team.stage)}")
    # ---- M8: team roles
    keys = [k for m in mons for k in m.keys]
    setup = any(k in SETUP_STATUS for k in keys)
    priority = any(k in ROLES["priority"] or (m.move_info[i][1].get("priority", 0) > 0 and is_attack(m.move_info[i][1]))
                   for m in mons for i, k in enumerate(m.keys))
    pivot_or_hazard = any(k in ROLES["pivot"] or k in ROLES["hazard"] for k in keys)
    if team.kind in ("boss", "side") and st >= 3:
        missing = [what for what, ok in (("setup move", setup), ("priority move", priority),
                                         ("pivot or hazard", pivot_or_hazard)) if not ok]
        if missing:
            f.add("M8", team, f"no {', no '.join(missing)} on the team")
        setters = collections.Counter(HAZARD_KIND[k] for m in mons for k in set(m.keys) if k in HAZARD_KIND)
        two = [h for h, n in setters.items() if n > 1]
        if two:
            f.add("M8", team, f"more than one {', '.join(two)} setter")
    elif team.kind in ("miniboss", "ace", "cooltrainer") and st >= 5:
        if not (setup or priority) or not pivot_or_hazard:
            f.add("M8", team, "needs setup or priority, and a pivot or a hazard")
    # ---- P2: Trick Room is a whole team
    if ctx["tr_setters"] and not ctx["tr_team"]:
        fast = [m.name for m in mons if NATURES.get(m.nature or "", (None, None))[0] == "Spe"]
        f.add("P2", team, f"Trick Room from {ctx['tr_setters']} setter on a team with {ctx['slow']} members of base Speed "
                          f"60 or less" + (f", and {', '.join(fast)} with Speed-raising natures" if fast else ""))
    # ---- V4: EVs by stage (phase 1b: a warning everywhere until it lands)
    with_evs = [m for m in mons if m.m.get("evs")]
    red = team.name.startswith("RED")
    if st <= 1 and with_evs:
        f.add("V4", team, f"EVs at stage {label(team.stage)}: {', '.join(m.name for m in with_evs)}")
    elif st == 2 and (len(with_evs) > 1 or any(sum(1 for v in team_kit.evs_of(m.m).values() if v) > 1 for m in with_evs)):
        f.add("V4", team, "at stage 2 one Pokemon, the ace, may have EVs, in one stat")
    elif 3 <= st <= stage_index(JOHTO_CHAMPION):
        short = [m.name for m in mons if sum(team_kit.evs_of(m.m).values()) < 508]
        if short:
            f.add("V4", team, f"no full EV spread from stage 3 on: {', '.join(short)}")
    elif team.stage == KANTO_CHAMPION and with_evs and not red:
        f.add("V4", team, f"EVs after the Kanto League, where only Red has them: {', '.join(m.name for m in with_evs)}")
    # ---- P3: Mega Evolution
    megas = [m for m in mons if m.mega]
    if len(megas) > 1:
        f.add("P3", team, f"{len(megas)} Mega Stones: one Mega a battle")
    if team.kind in ("boss", "side") and st >= 3 and not megas and boss_role(team.name) != "kimono" \
            and team.name not in ("SIDE_GEETA", "SIDE_N"):
        f.add("P3", team, "no Mega Evolution (required on every boss and side battle from stage 3)")
    # ---- P4: legendary-tier Pokemon
    legends = [(m, db.legend_kind(m.species)) for m in mons if db.legend_kind(m.species)]
    for m, kind in legends:
        if kind == "RestrictedLegendary" and not (team.name.endswith("_N") and m.species == "SPECIES_ZEKROM"):
            f.add("P4", team, f"{m.name}: a restricted legendary (N's Zekrom is the one exception)")
    tiered = [m for m, kind in legends if kind != "RestrictedLegendary"]
    if tiered:
        role = boss_role(team.name) if team.kind == "boss" else team.kind
        if st < 5:
            f.add("P4", team, f"legendary-tier Pokemon before stage 5: {', '.join(m.name for m in tiered)}")
        elif team.kind in ("miniboss", "ace", "cooltrainer"):
            if st < stage_index(JOHTO_CHAMPION) or len(tiered) > 1:
                f.add("P4", team, f"{len(tiered)} legendary-tier Pokemon on a mini-boss or Ace team "
                                  f"({'none in Johto' if st < stage_index(JOHTO_CHAMPION) else 'one in Kanto'})")
        elif st >= stage_index(JOHTO_CHAMPION):
            if len(tiered) > 3:
                f.add("P4", team, f"{len(tiered)} legendary-tier Pokemon after the Johto League (three at most)")
        else:
            cap_n = 2 if team.name.startswith("LANCE") else 1
            if len(tiered) > cap_n:
                f.add("P4", team, f"{len(tiered)} legendary-tier Pokemon")
            if st < 7 and any(db.legend_kind(m.species) not in ("Paradox", "UltraBeast") for m in tiered):
                f.add("P4", team, "a sub-legendary or mythical before stage 7")
    if team.kind == "boss" and boss_role(team.name) == "league" and team.name.split("_")[0] in ELITE_FOUR \
            and team.stage == 8 and not tiered:
        f.add("P4", team, "an Elite Four member without a legendary-tier Pokemon")
    # ---- P5: not on the map where the player meets it, or next to it
    folder = ctx["map"]
    if folder and legends:
        here = {folder} | maps.near.get(folder, set())
        for m, _ in legends:
            met = {e["map"] for e in encounters.get(m.species, [])} | maps.static.get(m.species, set())
            met = {maps.ids.get(x, x) for x in met}
            if met & here:
                f.add("P5", team, f"{m.name}: the player meets it on {', '.join(sorted(met & here))}")
    # ---- P6: the map's weather (the battle starts in it): the team uses it, or sets another of its own, and no
    # Pokemon depends on a weather the map cancels
    weather = ctx["map_weather"]
    if weather:
        own = {w for m in mons for w in ([WEATHER_SETTER_ABILITY.get(m.battle_ability)] +
                                         [WEATHER_MOVES.get(k) for k in m.keys]) if w} - {weather}
        if not own:
            if not sum(uses_weather(m, weather) for m in mons) >= 2:
                f.add("P6", team, f"{folder} has {weather}: fewer than two of the team use it, and it sets no weather of "
                                  f"its own")
            for m in mons:
                needs = [w for w in ("sun", "rain", "sand", "snow") if w != weather and needs_weather(m, w)]
                if needs:
                    f.add("P6", team, f"{m.name} depends on {needs[0]}, which {folder}'s {weather} cancels")
    # ---- S1: no species twice
    species = collections.Counter(m.species for m in mons)
    twice = [s[8:].title() for s, n in species.items() if n > 1]
    if twice:
        f.add("S1", team, f"a species more than once: {', '.join(twice)}")
    # ---- E8: the rival's starter
    m8 = re.fullmatch(r"RIVAL_(CYNDAQUIL|TOTODILE|CHIKORITA)_(\d)", team.name)
    if m8 and st >= 2:
        starter = mons[-1]
        line = {"CYNDAQUIL": ("SPECIES_QUILAVA", "SPECIES_TYPHLOSION"), "TOTODILE": ("SPECIES_CROCONAW", "SPECIES_FERALIGATR"),
                "CHIKORITA": ("SPECIES_BAYLEEF", "SPECIES_MEGANIUM")}[m8.group(1)]
        want = line[1] if cap(team.stage) >= 36 else line[0]
        if starter.species != want:
            f.add("E8", team, f"his starter is a {starter.name} at {cap(team.stage)}: a {want[8:].title()} there")
    # ---- E5's warning: more than one Pokemon ahead of its line
    ahead = [m.name for m in mons if db.reach_level(m.species) > cap(team.stage)]
    if len(ahead) > 1:
        f.add("E5", team, f"{len(ahead)} Pokemon ahead of their lines: {', '.join(ahead)}", warn=True)
    return mons, ctx


def team_size(team):
    """(fewest, most) Pokemon for the team's kind at its stage, the standard's table 4.1."""
    st, name = stage_index(team.stage), team.name
    if team.kind == "side":
        return (6, 6)
    if team.kind == "miniboss":
        return [(3, 3), (4, 4), (4, 4), (5, 5), (5, 6)][st] if st <= 4 else (6, 6)
    if team.kind == "ace":
        return [(3, 3), (4, 4), (5, 5), (5, 5)][st] if st <= 3 else (6, 6)
    if team.kind == "cooltrainer":
        return {3: (5, 5), 4: (5, 5), 7: (5, 6)}.get(st, (6, 6))
    role = boss_role(name)
    if role == "li":
        return (3, 3)
    if role == "kimono":
        return (1, 1)
    if name == "ARIANA_1":
        return (3, 3)
    return (6, 6)


# ---------------------------------------------------------------- across teams
def version_group(tid):
    """Teams that are versions of one battle (the rival's three, the Gym versions, Red's two, a rematch family,
    Gardenia's two): the same group key."""
    name = tid[len("TRAINER_"):-len("_HNS")]
    m = re.fullmatch(r"RIVAL_(?:CYNDAQUIL|TOTODILE|CHIKORITA)_(\d)", name)
    if m:
        return f"RIVAL_{m.group(1)}"
    m = re.fullmatch(r"(CHUCK|JASMINE|PRYCE)_1(?:_[23])?", name)
    if m:
        return m.group(1) + "_1"
    if name.startswith("RED"):
        return "RED"
    if name.startswith("SIDE_GARDENIA"):
        return "SIDE_GARDENIA"
    for family in REMATCH_FAMILIES.values():
        if tid in family:
            return family[0]
    return tid




def check_across(db, f, teams, mons_of, maps):
    by_tid = {t.tid: t for t in teams}
    # ---- R1, R2: phone rematch tiers of designed teams
    for first, tiers in REMATCH_FAMILIES.items():
        if not any(t in by_tid for t in tiers):
            continue
        prev = None
        for i, tid in enumerate(tiers):
            team = by_tid.get(tid)
            if team is None:
                f.add("R1", first, f"tier {i + 1}, {tid}, is not a designed team made for a stage")
                continue
            if prev is not None:
                if i == 1 and stage_index(team.stage) < max(3, stage_index(prev.stage)):
                    f.add("R1", team, f"tier 2 at stage {label(team.stage)}: rematches start at three badges and "
                                      f"after the first battle's stage {label(prev.stage)}")
                if stage_index(team.stage) <= stage_index(prev.stage):
                    f.add("R1", team, f"tier {i + 1} at stage {label(team.stage)}, not after tier {i}'s "
                                      f"({label(prev.stage)}): the rematch gate tells tiers apart by their stages")
                if len(team.mons) < len(prev.mons):
                    f.add("Z3", team, f"tier {i + 1} has {len(team.mons)} Pokemon, fewer than tier {i}'s {len(prev.mons)}")
                elif len(team.mons) > len(prev.mons) + 1:
                    f.add("Z3", team, f"tier {i + 1} has {len(team.mons) - len(prev.mons)} more Pokemon than tier {i}",
                          warn=True)
                same = [a for a, b in zip(prev.mons, team.mons) if (a["species"], a["item"], a["ability"], a["moves"]) ==
                        (b["species"], b["item"], b["ability"], b["moves"])]
                if len(same) == len(prev.mons) == len(team.mons):
                    f.add("R2", team, f"tier {i + 1} is a copy of tier {i}'s team")
            prev = team
    # ---- S4: exact sets on two teams, and teams too close to a boss's
    sets = collections.defaultdict(list)
    for t in teams:
        for m in t.mons:
            sets[(m["species"], m["item"], m["ability"], tuple(sorted(m["moves"])))].append(t)
    for key, ts in sets.items():
        groups = {version_group(t.tid) for t in ts}
        if len(groups) > 1:
            names = sorted({t.tid for t in ts})
            f.add("S4", ts[-1], f"{key[0]} @ {key[1]} ({key[2]}; {', '.join(key[3])}) is on {', '.join(names)}")
    bosses = [t for t in teams if t.kind == "boss"]
    seen = set()
    for t in teams:
        mine = {m.species for m in mons_of[t.tid]}
        for b in bosses:
            pair = frozenset((version_group(t.tid), version_group(b.tid)))
            if len(pair) == 1 or pair in seen or stage_index(b.stage) - stage_index(t.stage) not in (0, 1):
                continue
            shared = mine & {m.species for m in mons_of[b.tid]}
            if len(shared) > 3:
                seen.add(pair)
                f.add("S4", t, f"shares {len(shared)} species with {b.tid} (stage {label(b.stage)}): "
                               f"{', '.join(sorted(s[8:].replace('_', ' ').title() for s in shared))}")
    # ---- Z2, DB2: two-opponent battles fight with three Pokemon from each
    for macro, a, b in maps.pairs:
        for tid in (a, b):
            if tid in by_tid:
                team = by_tid[tid]
                if len(team.mons) != 3:
                    f.add("Z2", team, f"fought only in a two-opponent battle ({macro} with {b if tid == a else a}): it "
                                      f"battles with its first three of {len(team.mons)}; it should have exactly 3")
                check_first_three(f, team, mons_of[tid], f"{macro} with {b if tid == a else a}")
    for t in teams:
        partners = [p for p in maps.sight_partners(t.tid) if p != t.tid]
        if partners:
            check_first_three(f, t, mons_of[t.tid], f"its line of sight meets {', '.join(partners)}'s")


def check_first_three(f, team, mons, why):
    """DB2: in a two-opponent battle a team battles with its first three: the Mega must be among them."""
    if any(m.mega for m in mons) and not any(m.mega for m in mons[:3]):
        f.add("DB2", team, f"{why}: it battles with its first three, and its Mega is not among them")


# ---------------------------------------------------------------- running them
def check(encounters):
    """Every finding on the designed teams: [severity, rule, trainer, text], and the teams' raised forms."""
    db = species_db.load()
    maps = Maps()
    teams = designed_teams()
    f = Findings()
    mons_of, raised = {}, {}
    for t in teams:
        mons, _ = check_team(db, f, t, maps, teams, encounters)
        mons_of[t.tid] = mons
        raised[t.tid] = raised_forms(db, t, mons)
    check_across(db, f, teams, mons_of, maps)
    # The named Eviolite species are the build's tier A ones (the standard's table 3.2)
    computed = named_eviolite_tiers(db)
    named = {db.canonical(team_kit.species_constant(n)) for n in team_kit.NAMED_EVIOLITE}
    left_out = {db.canonical(team_kit.species_constant(n)) for n in team_kit.NOT_NAMED}
    for sp in sorted(set(computed) - named - left_out):
        f.add("E3", "NAMED_EVIOLITE", f"{sp[8:].title()} is tier A ({computed[sp]}) in this build but not in "
                                      f"team_kit.NAMED_EVIOLITE or NOT_NAMED")
    for sp in sorted(named - set(computed)):
        f.add("E3", "NAMED_EVIOLITE", f"{sp[8:].title()} is in team_kit.NAMED_EVIOLITE but not tier A in this build")
    return f, raised, teams


def raised_forms(db, team, mons):
    """[(stage, [species or None for each slot])] for each later stage of its window where a Pokemon evolves."""
    out = []
    for stage in team.window[1:]:
        forms = [battle_species(db, m, team.stage, stage) for m in mons]
        items = [battle_item(db, m, team.stage, stage) for m in mons]
        if any(sp != m.species for sp, m in zip(forms, mons)):
            out.append((stage, forms, items))
    return out


def stale_pending(rows):
    """PENDING entries whose trainer no longer breaks the rule."""
    seen = {(rule, tid) for _, rule, tid, _ in rows}
    return sorted((rule, tid) for rule, tids in PENDING.items() for tid in tids if (rule, tid) not in seen)


def report(rows, raised, teams):
    """Every team's findings and raised forms, as text."""
    by = collections.defaultdict(list)
    for sev, rule, tid, text in rows:
        by[tid].append(f"  {sev} {rule}: {text}")
    out = ["Crystal Imperium designed teams against the trainer standard (validate.py; tools/crystal_imperium/"
           "trainer_rules.py)", ""]
    for t in teams:
        out.append(f"{t.tid} ({t.kind}, stage {label(t.stage)}, fought at stages {label(t.window[0])} to "
                   f"{label(t.window[-1])})")
        out += by.pop(t.tid, [])
        groups = []  # consecutive stages with the same raised team
        for stage, forms, items in raised[t.tid]:
            if groups and groups[-1][1:] == (forms, items):
                groups[-1][0].append(stage)
            else:
                groups.append(([stage], forms, items))
        for stages, forms, items in groups:
            levels = str(cap(stages[0])) + (f" to {cap(stages[-1])}" if len(stages) > 1 else "")
            out.append(f"  raised to {levels}: " + ", ".join(
                sp[8:].replace("_", " ").title() + (f" @ {it[5:].replace('_', ' ').title()}" if it else "")
                for sp, it in zip(forms, items)))
    for tid, lines in sorted(by.items()):
        out.append(tid)
        out += lines
    return "\n".join(out) + "\n"


def pending_table(findings):
    """PENDING as the [V] rules' findings give it (validate.py --pending), as this file writes it."""
    out = collections.defaultdict(set)
    for sev, rule, tid, _ in findings.rows:
        if sev == "ERROR" and rule not in PENDING_EVERYWHERE and tid.startswith("TRAINER_"):
            out[rule].add(tid[len("TRAINER_"):-len("_HNS")])
    lines = ["PENDING = {rule: {f\"TRAINER_{name}_HNS\" for name in names.split()} for rule, names in {"]
    for rule, names in sorted(out.items(), key=lambda kv: (kv[0][0], int(kv[0][1:]))):
        text, line = [], f'    "{rule}": ("'
        for n in sorted(names):
            if len(line) + len(n) + 1 > 116:
                text.append(line.rstrip() + ' "')
                line = '             "'
            line += n + " "
        text.append(line.rstrip() + '"),')
        lines += text
    return "\n".join(lines + ["}.items()}"])
