#!/usr/bin/env python3
"""Crystal Imperium side battles (DECISIONS.md D41): Gym Leaders from newer regions who wait somewhere
in Johto and Kanto (Emerald Imperium's "traveling Gym leaders"), and the postgame's visitors. Each is
an optional battle: talk to them, say YES, win, and they give a reward once. From the table below
this writes:

  include/constants/opponents_hns.h    their trainer IDs (appended after Heart & Soul's own: an ID
                                       indexes the saved defeat flag, so an ID never changes)
  src/data/trainers_hns.party          each trainer's header (name, class, picture, music);
                                       tools/crystal_imperium/boss_teams.py writes their Pokemon
  src/data/side_battle_rewards.h       what each reward holds and the message listing it
  data/scripts/side_battles.inc        the scripts and their texts
  data/maps/*/map.json                 each one's object on its map

  python3 tools/crystal_imperium/side_battles.py           # rewrite the files
  python3 tools/crystal_imperium/side_battles.py --check   # exit 1 if any is out of date

Run it before boss_teams.py, which needs the trainers' headers.

Emerald Imperium (1.3.1) has Sinnoh's eight Gym Leaders as side battles in Hoenn, each at a set place
from a set badge, with a YES/NO prompt, one battle and a bundle of TMs, held items and Mega Stones
(emeraldimperium.info/walkthrough.html). Here the same idea is written anew (D2): Johto has Sinnoh's
eight, one per badge stage; Kanto has Paldea's eight Gym Leaders; the postgame has other regions'
Champions, rivals and villains around Johto and Kanto. Every one battles at the player's level cap
with six Pokemon (boss_teams.py, D21). A reward holds what this game doesn't already give ten at a
time (the care packages, D16): ten Gems of the trainer's type, TMs before the TM shops sell
them (D36), Mega Stones before the Goldenrod Mega shop sells them, an evolution item for the
trainer's own Pokemon (since 0.15.0 the one Emerald Imperium's evolutions use, D44), and items
nothing else gives (the Rotom Catalog). It goes whole to the Bag,
or to the PC when a pocket is full; if neither has room, nothing is given and talking to the trainer
again tries once more (src/side_battles.c).
"""
import argparse
import json
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import care_packages  # noqa: E402  (message box widths, item names)
import tm_list        # noqa: E402  (TM numbers, the TM shops' badge counts)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OPPONENTS = os.path.join(ROOT, "include", "constants", "opponents_hns.h")
PARTY = os.path.join(ROOT, "src", "data", "trainers_hns.party")
REWARDS = os.path.join(ROOT, "src", "data", "side_battle_rewards.h")
SCRIPTS = os.path.join(ROOT, "data", "scripts", "side_battles.inc")

# src/side_battles.c: SIDE_BATTLE_REWARD_MAX_ITEMS
MAX_REWARD_ITEMS = 24
# TRAINER_NAME_LENGTH
MAX_NAME = 10
# include/constants/opponents_hns.h: MAX_TRAINERS_COUNT_HNS (the save's trainer flags)
MAX_TRAINER_ID = 863
# A map holds at most this many objects (OBJECT_EVENT_TEMPLATES_COUNT)
MAX_MAP_OBJECTS = 64
FACINGS = {"down": "MOVEMENT_TYPE_FACE_DOWN", "up": "MOVEMENT_TYPE_FACE_UP",
           "left": "MOVEMENT_TYPE_FACE_LEFT", "right": "MOVEMENT_TYPE_FACE_RIGHT"}
MUGSHOTS = {"Blue", "Dark Red", "Green", "Light Blue", "Orange", "Pink", "Purple", "Yellow"}

# The trainer of a stage: a badge count (0-8) before the Johto League, or a flag after it
JOHTO_CHAMPION_FLAG = "FLAG_IS_CHAMPION"
KANTO_CHAMPION_FLAG = "FLAG_IS_KANTO_CHAMPION"


class Battle:
    def __init__(self, key, trainer_id, name, trainer_class, pic, gender, music, mugshot, gfx, places,
                 gate, reward, texts, second=None):
        self.key = key                      # CANDICE: the labels' and the reward flag's name
        self.trainer = f"TRAINER_SIDE_{key}_HNS"
        self.trainer_id = trainer_id
        self.name = name
        self.trainer_class = trainer_class  # the party file's Class: value
        self.pic = pic                      # the party file's Pic: value
        self.gender = gender
        self.music = music                  # the party file's Music: value
        self.mugshot = mugshot
        self.gfx = gfx                      # OBJ_EVENT_GFX_* on the map
        self.places = places                # [(map folder, x, y, facing[, other layouts it shows])]
        self.gate = gate                    # ("badges", n) or ("flag", FLAG_*)
        self.reward = reward                # [(ITEM_ name without ITEM_, quantity)]
        self.texts = texts                  # challenge, not_yet, declined, defeat, reward, after
        self.second = second                # (trainer ID, badges, challenge text): a stronger team later
        self.reward_flag = f"FLAG_SIDE_REWARD_{key}"

    def trainers(self):
        out = [(self.trainer, self.trainer_id)]
        if self.second:
            out.append((f"TRAINER_SIDE_{self.key}_2_HNS", self.second[0]))
        return out


# --- Johto: Sinnoh's eight Gym Leaders, Emerald Imperium's side battles, one per badge stage --------
# Imperium's order and spots in Hoenn: Candice (Route 116, before badge 1), Gardenia (Petalburg Woods,
# badge 1, a stronger team from badge 3), Fantina (Route 117, badge 2), Maylene (Jagged Pass, badge 3),
# Wake (Route 118, badge 5), Byron (Route 121, badge 6), Roark (Route 125, badge 6), Volkner
# (Evergrande City, badge 8). Here Gardenia waits for badge 2 (Cut) and Maylene for badge 4
# (Cianwood needs Surf); Roark stands beside the Ice Path, not in it.
JOHTO = [
    Battle("CANDICE", 653, "CANDICE", "Leader Hns", "Candice Hns", "Female", "Hg Girl 1", "Light Blue",
           "OBJ_EVENT_GFX_CANDICE_HNS", [("VioletCity_TrainerSchool_hns", 8, 3, "down")],
           ("badges", 0),
           [("ICE_GEM", 10), ("TM_TRIPLE_AXEL", 1), ("TM_ICE_PUNCH", 1)],
           {"challenge": ["Hi! I'm CANDICE, the GYM LEADER of SNOWPOINT CITY, way up north in SINNOH!",
                          "I'm visiting JOHTO's TRAINER SCHOOL to see how you train here. How about a battle? "
                          "I'll keep it cool!"],
            "declined": ["Aww, okay! I'll be right here practicing my diamond dust!"],
            "defeat": ["Brrr! Your focus cut right through my ice!"],
            "reward": ["You earned these! Take them with you!"],
            "after": ["Train with all your focus, and your POKéMON will sparkle like diamond dust!"]}),
    Battle("GARDENIA", 654, "GARDENIA", "Leader Hns", "Gardenia Hns", "Female", "Hg Girl 1", "Green",
           "OBJ_EVENT_GFX_GARDENIA_HNS", [("IlexForest_hns", 18, 17, "right")],
           ("badges", 2),
           [("GRASS_GEM", 10), ("TM_ENERGY_BALL", 1), ("TM_LEAF_BLADE", 1), ("LEAF_STONE", 1)],
           {"not_yet": ["Hi there! I'm GARDENIA, ETERNA CITY's GYM LEADER. This forest is just wonderful!",
                        "Come back with two GYM BADGES, and we'll have a battle among the trees!"],
            "challenge": ["Two BADGES already? Then let's see how you handle GRASS-type POKéMON!"],
            "declined": ["Okay! I'm not going anywhere. These trees are too nice to leave!"],
            "defeat": ["Wow! You and your POKéMON are as tough as old roots!"],
            "reward": ["You beat me fair and square! These are for you!"],
            "after": ["The trees here have been growing for ages. Grow strong like them, okay?"]},
           second=(655, 4, ["Four BADGES? Then I'll use the team I've been raising in this forest! "
                            "It's grown a lot, just like you!"])),
    Battle("FANTINA", 656, "FANTINA", "Leader Hns", "Fantina Hns", "Female", "Hg Girl 1", "Purple",
           "OBJ_EVENT_GFX_FANTINA_HNS", [("EcruteakCity_hns", 41, 41, "down")],
           ("badges", 3),
           [("GHOST_GEM", 10), ("TM_POLTERGEIST", 1), ("GENGARITE", 1), ("LINKING_CORD", 1)],
           {"not_yet": ["Bonjour! I am FANTINA, GYM LEADER of HEARTHOME CITY. I came to see the dances of "
                        "ECRUTEAK!", "Come back with three GYM BADGES. Then we dance a battle, yes?"],
            "challenge": ["Ah, three BADGES! Then you are ready to dance with my GHOST POKéMON! Shall we?"],
            "declined": ["Non? Then I watch the KIMONO GIRLS a little longer."],
            "defeat": ["Magnifique! You danced better than my POKéMON!"],
            "reward": ["A wonderful battle deserves a gift!"],
            "after": ["The dances of this city, they are like my GHOST POKéMON: graceful and a little "
                      "mysterious!"]}),
    Battle("MAYLENE", 657, "MAYLENE", "Leader Hns", "Maylene Hns", "Female", "Hg Girl 1", "Orange",
           "OBJ_EVENT_GFX_MAYLENE_HNS", [("CianwoodCity_hns", 17, 46, "down")],
           ("badges", 4),
           [("FIGHTING_GEM", 10), ("TM_CLOSE_COMBAT", 1), ("LUCARIONITE", 1)],
           {"not_yet": ["I'm MAYLENE, GYM LEADER of VEILSTONE CITY. I came to train with CHUCK!",
                        "Come back with four GYM BADGES, and I'll battle you with everything I've got!"],
            "challenge": ["Four BADGES! Okay... I'm ready. Let's give this battle everything we have!"],
            "declined": ["Alright. I'll keep training by the waterfall until you're ready."],
            "defeat": ["...I lost. You and your POKéMON are really strong."],
            "reward": ["Please, take these. You earned them!"],
            "after": ["Training with CHUCK under the waterfall is cold, but I'm getting stronger every "
                      "day!"]}),
    Battle("WAKE", 658, "WAKE", "Leader Hns", "Wake Hns", "Male", "Hg Boy 1", "Blue",
           "OBJ_EVENT_GFX_WAKE_HNS", [("LakeOfRage_hns", 49, 30, "left", ["LAYOUT_LAKE_OF_RAGE_LOW_TIDE_HNS"])],
           ("badges", 5),
           [("WATER_GEM", 10), ("GYARADOSITE", 1), ("KINGS_ROCK", 1)],
           {"not_yet": ["Wahahah! I'm CRASHER WAKE, PASTORIA CITY's GYM LEADER! I heard this lake makes "
                        "GYARADOS go wild!", "Come back with five GYM BADGES, and I'll crash right into you!"],
            "challenge": ["Five BADGES? Then hold on tight! My WATER POKéMON hit like a tidal wave! Ready?"],
            "declined": ["Wahahah! Scared of a little splash? I'll be waiting!"],
            "defeat": ["Wahahah! I got washed away!"],
            "reward": ["What a battle! Here, a prize from CRASHER WAKE!"],
            "after": ["Crash through anything in your way, just like a wave!"]}),
    Battle("BYRON", 659, "BYRON", "Leader Hns", "Byron Hns", "Male", "Hg Boy 1", "Dark Red",
           "OBJ_EVENT_GFX_BYRON_HNS", [("OlivineCity_hns", 41, 51, "left")],
           ("badges", 6),
           [("STEEL_GEM", 10), ("TM_STEEL_BEAM", 1), ("METAGROSSITE", 1), ("METAL_COAT", 1)],
           {"not_yet": ["Bwahahaha! I'm BYRON, GYM LEADER of CANALAVE CITY! I sailed here to see "
                        "JASMINE's STEEL POKéMON!", "Come back with six GYM BADGES, youngster!"],
            "challenge": ["Six BADGES! Bwahahaha! Then let's see if you can dent my STEEL POKéMON!"],
            "declined": ["Bwahahaha! Steel doesn't rust from waiting!"],
            "defeat": ["Bwahahaha! You cracked my steel!"],
            "reward": ["Take these! Fine work deserves fine rewards!"],
            "after": ["My son ROARK is somewhere in JOHTO too. He's always digging for fossils!"]}),
    Battle("ROARK", 660, "ROARK", "Leader Hns", "Roark Hns", "Male", "Hg Boy 1", "Orange",
           "OBJ_EVENT_GFX_ROARK_HNS", [("Route44_hns", 69, 13, "down")],
           ("badges", 7),
           [("ROCK_GEM", 10), ("TM_EXPLOSION", 1), ("TYRANITARITE", 1), ("KINGS_ROCK", 1)],
           {"not_yet": ["I'm ROARK, OREBURGH CITY's GYM LEADER. I'm looking for fossils near the ICE PATH.",
                        "Come back with seven GYM BADGES, and my ROCK POKéMON will battle you!"],
            "challenge": ["Seven BADGES, huh? Then my ROCK POKéMON won't hold back! Let's battle!"],
            "declined": ["Okay. I'll keep digging."],
            "defeat": ["You smashed right through my ROCK POKéMON!"],
            "reward": ["Here, take these. I dug them up myself... well, some of them!"],
            "after": ["Dad's in OLIVINE CITY, looking at the lighthouse. He loves anything made of "
                      "steel!"]}),
    Battle("VOLKNER", 661, "VOLKNER", "Leader Hns", "Volkner Hns", "Male", "Hg Boy 1", "Yellow",
           "OBJ_EVENT_GFX_VOLKNER_HNS", [("IndigoPlateau_hns", 13, 8, "down")],
           ("badges", 8),
           [("ELECTRIC_GEM", 10), ("ROTOM_CATALOG", 1), ("LINKING_CORD", 1)],
           {"not_yet": ["...I'm VOLKNER. SUNYSHORE CITY's GYM LEADER. I'm waiting for a trainer worth "
                        "battling.", "Come back with all eight GYM BADGES."],
            "challenge": ["Eight BADGES. You might be the one who can make my battles exciting again. "
                          "Ready?"],
            "declined": ["...Fine. I'll wait."],
            "defeat": ["...Heh. That was fun. I haven't felt this charged up in ages."],
            "reward": ["Take these. You've earned them."],
            "after": ["Go win the POKéMON LEAGUE. Then come back and tell me about it."]}),
]

# --- Kanto: Paldea's eight Gym Leaders, after the Johto League (all at Kanto's cap) ------------------
# One in each of eight Kanto towns, near a place that suits them; Kanto's Gym Leader class, for its
# battle music. Every TM and Mega Stone is on sale by then, so a reward is ten Gems and an item of
# the leader's own: Larry's Exp. Charm and Iono's Catching Charm are the only ones in the game.
KANTO = [
    Battle("KATY", 662, "KATY", "Leader Kanto Hns", "Katy Hns", "Female", "Hg Girl 1", "Orange",
           "OBJ_EVENT_GFX_KATY_HNS", [("PewterCity_hns", 22, 12, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("BUG_GEM", 10), ("LEAF_STONE", 1), ("SUN_STONE", 1)],
           {"not_yet": ["Hi there! I'm KATY, CORTONDO's GYM LEADER in PALDEA. I'm on a tour of KANTO's "
                        "bakeries!", "Once you're JOHTO's CHAMPION, let's have a battle, okay?"],
            "challenge": ["Hi there! I'm KATY, CORTONDO's GYM LEADER in PALDEA. I'm on a tour of KANTO's "
                          "bakeries!", "My BUG POKéMON are as sweet as my cakes, but they still sting! "
                          "Shall we battle?"],
            "declined": ["Okay! I'll go find more sweets while I wait."],
            "defeat": ["Oh my! That battle was sweeter than any cake!"],
            "reward": ["A sweet battle deserves a sweet treat! Here you go!"],
            "after": ["If you ever visit PALDEA, come by my bakery in CORTONDO!"]}),
    Battle("BRASSIUS", 663, "BRASSIUS", "Leader Kanto Hns", "Brassius Hns", "Male", "Hg Boy 1", "Green",
           "OBJ_EVENT_GFX_BRASSIUS_HNS", [("Route25_hns", 80, 15, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("GRASS_GEM", 10), ("SUN_STONE", 1), ("GRASSY_SEED", 3)],
           {"not_yet": ["I am BRASSIUS, artist and GYM LEADER of ARTAZON! The flowers by this sea inspire "
                        "me!", "Return as JOHTO's CHAMPION, and we shall create art together!"],
            "challenge": ["I am BRASSIUS, artist and GYM LEADER of ARTAZON! The flowers by this sea inspire "
                          "me!", "Will you join me in a battle? A living work of art!"],
            "declined": ["Inspiration cannot be rushed. I shall wait."],
            "defeat": ["Magnificent! Our battle was a masterpiece!"],
            "reward": ["Take these, as thanks for the inspiration!"],
            "after": ["Art and battles both bloom when you pour your heart into them!"]}),
    Battle("IONO", 664, "IONO", "Leader Kanto Hns", "Iono Hns", "Female", "Hg Girl 1", "Yellow",
           "OBJ_EVENT_GFX_IONO_HNS", [("LavenderTown_hns", 23, 9, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("ELECTRIC_GEM", 10), ("CATCHING_CHARM", 1)],
           {"not_yet": ["Ello, ello, hola! It's your electrifying streamer, IONO! I'm live from KANTO's "
                        "RADIO TOWER!", "Become JOHTO's CHAMPION, and you can star in my stream!"],
            "challenge": ["Ello, ello, hola! It's your electrifying streamer, IONO! I'm live from KANTO's "
                          "RADIO TOWER!", "Wanna star in my stream? Let's battle, and make it shocking!"],
            "declined": ["Boo! My chat is sad now! Come back soon, 'kay?"],
            "defeat": ["Ack! My chat is going wild! You zapped me good!"],
            "reward": ["Here's a little something from your favorite streamer!"],
            "after": ["Thanks for being on my stream! The views are through the roof!"]}),
    Battle("KOFU", 665, "KOFU", "Leader Kanto Hns", "Kofu Hns", "Male", "Hg Boy 1", "Blue",
           "OBJ_EVENT_GFX_KOFU_HNS", [("VermilionCity_hns", 49, 27, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("WATER_GEM", 10), ("PRISM_SCALE", 1), ("DAMP_ROCK", 1)],
           {"not_yet": ["Hola! I'm KOFU, CASCARRAFA's GYM LEADER! I came to VERMILION for the freshest "
                        "seafood!", "Once you're JOHTO's CHAMPION, we'll have a battle, fresh off the "
                        "boat!"],
            "challenge": ["Hola! I'm KOFU, CASCARRAFA's GYM LEADER! I came to VERMILION for the freshest "
                          "seafood!", "You look like a fine catch! Let's battle, and see who's freshest!"],
            "declined": ["No? Then I'll go haggle with the fishermen!"],
            "defeat": ["Whoa! You cooked me but good!"],
            "reward": ["A great battle earns a great prize! Take it!"],
            "after": ["Life is like the sea: full of surprises, and full of flavor!"]}),
    Battle("LARRY", 666, "LARRY", "Leader Kanto Hns", "Larry Hns", "Male", "Hg Boy 1", "Dark Red",
           "OBJ_EVENT_GFX_LARRY_HNS", [("ViridianCity_hns", 22, 23, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("NORMAL_GEM", 10), ("EXP_CHARM", 1)],
           {"not_yet": ["...I'm LARRY. GYM LEADER of MEDALI, in PALDEA. I'm on a business trip. Again.",
                        "Come back when you're JOHTO's CHAMPION. I'll be here. Working."],
            "challenge": ["...I'm LARRY. GYM LEADER of MEDALI, in PALDEA. I'm on a business trip. Again.",
                          "A battle? Fine. Let's get it over with. I won't go easy, though."],
            "declined": ["Good. I'd rather sit down for a while anyway."],
            "defeat": ["...You're strong. I'll put that in my report."],
            "reward": ["My boss said to hand these out. Here."],
            "after": ["Ordinary is best. Remember that, kid."]}),
    Battle("RYME", 667, "RYME", "Leader Kanto Hns", "Ryme Hns", "Female", "Hg Girl 1", "Purple",
           "OBJ_EVENT_GFX_RYME_HNS", [("CeladonCity_hns", 36, 22, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("GHOST_GEM", 10), ("DUSK_STONE", 1), ("SPELL_TAG", 1)],
           {"not_yet": ["Yo! MC RYME, from MONTENEVERA, in the house! CELADON's crowd better be ready!",
                        "Come back as JOHTO's CHAMPION, and we'll take the stage together!"],
            "challenge": ["Yo! MC RYME, from MONTENEVERA, in the house! CELADON's crowd better be ready!",
                          "Step up to the mic! Let's battle, and drop some beats!"],
            "declined": ["Nah? Then I'll keep the crowd warm for ya!"],
            "defeat": ["Mic drop! You stole the whole show!"],
            "reward": ["A star performance deserves some love! Here!"],
            "after": ["Keep your rhythm, and your POKéMON will follow your beat!"]}),
    Battle("TULIP", 668, "TULIP", "Leader Kanto Hns", "Tulip Hns", "Female", "Hg Girl 1", "Pink",
           "OBJ_EVENT_GFX_TULIP_HNS", [("SaffronCity_hns", 34, 33, "down")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("PSYCHIC_GEM", 10), ("DAWN_STONE", 1), ("PSYCHIC_SEED", 3)],
           {"not_yet": ["Hello. I'm TULIP, GYM LEADER of ALFORNADA, and a makeup artist. SAFFRON's style "
                        "is... interesting.", "Come back as JOHTO's CHAMPION. Then we'll battle."],
            "challenge": ["Hello. I'm TULIP, GYM LEADER of ALFORNADA, and a makeup artist. SAFFRON's style "
                          "is... interesting.", "Shall we battle? I'll show you how beautiful PSYCHIC "
                          "POKéMON can be."],
            "declined": ["Then I'll wait. Beauty is worth waiting for."],
            "defeat": ["How lovely. You and your POKéMON shine brighter than I do."],
            "reward": ["Please accept these. You've earned them."],
            "after": ["True beauty comes from the bond you share with your POKéMON."]}),
    Battle("GRUSHA", 669, "GRUSHA", "Leader Kanto Hns", "Grusha Hns", "Male", "Hg Boy 1", "Light Blue",
           "OBJ_EVENT_GFX_GRUSHA_HNS", [("CinnabarIsland_hns", 42, 34, "left")],
           ("flag", JOHTO_CHAMPION_FLAG),
           [("ICE_GEM", 10), ("ICY_ROCK", 1), ("RAZOR_CLAW", 1)],
           {"not_yet": ["I'm GRUSHA, GYM LEADER of GLASEADO. This island is way too hot for me.",
                        "Come back once you're JOHTO's CHAMPION."],
            "challenge": ["I'm GRUSHA, GYM LEADER of GLASEADO. This island is way too hot for me.",
                          "...Fine, let's battle. I'll cool you down."],
            "declined": ["Your loss."],
            "defeat": ["...You've got real heat. I respect that."],
            "reward": ["Here. You earned these."],
            "after": ["Even on a hot island, ice holds its own. So should you."]}),
]

# --- Postgame: Champions, rivals and villains of other regions, before Red ------------------------------
# They wait around Johto and Kanto from the start and battle once the player has won the Kanto League,
# the point where Red on Mt. Silver battles too; each at level 100 like him. Wallace, Maxie, Archie and
# Wally use the sprites Emerald already has.
POSTGAME = [
    Battle("CYNTHIA", 670, "CYNTHIA", "Champion Hns", "Cynthia Hns", "Female", "Hg Girl 1", "Dark Red",
           "OBJ_EVENT_GFX_CYNTHIA_HNS", [("RuinsOfAlph_Outside_hns", 33, 19, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("GROUND_GEM", 10), ("MASTER_BALL", 1)],
           {"not_yet": ["I'm CYNTHIA, SINNOH's CHAMPION. These ruins hold so many mysteries...",
                        "Once you've won the KANTO LEAGUE, I'd love to see how strong you've become."],
            "challenge": ["I'm CYNTHIA, SINNOH's CHAMPION. These ruins hold so many mysteries...",
                          "You won the KANTO LEAGUE? Then show me. A battle worthy of two CHAMPIONS!"],
            "declined": ["I'll be here. The UNOWN have plenty to teach me while I wait."],
            "defeat": ["Splendid! That was the best battle I've had in a long time!"],
            "reward": ["You're truly strong. Please, take these."],
            "after": ["RED is waiting atop MT. SILVER. I think you're ready for him."]}),
    Battle("IRIS", 671, "IRIS", "Champion Hns", "Iris Hns", "Female", "Hg Girl 1", "Purple",
           "OBJ_EVENT_GFX_IRIS_HNS", [("BlackthornCity_hns", 29, 15, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("DRAGON_GEM", 10), ("ABILITY_PATCH", 1)],
           {"not_yet": ["Hiya! I'm IRIS, UNOVA's CHAMPION! BLACKTHORN's DRAGONS are super cool!",
                        "Win the KANTO LEAGUE, and then we can battle, okay?"],
            "challenge": ["Hiya! I'm IRIS, UNOVA's CHAMPION! BLACKTHORN's DRAGONS are super cool!",
                          "You're a CHAMPION too? Yay! My DRAGONS and I won't hold back!"],
            "declined": ["Aww! I'll go play in the DRAGON'S DEN until you're ready!"],
            "defeat": ["Wow! You and your POKéMON really trust each other!"],
            "reward": ["That was super fun! Here, these are for you!"],
            "after": ["CLAIR told me all about RED. I bet you can beat him!"]}),
    Battle("GEETA", 672, "GEETA", "Champion Hns", "Geeta Hns", "Female", "Hg Girl 1", "Dark Red",
           "OBJ_EVENT_GFX_GEETA_HNS", [("Route28_hns", 49, 14, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("STEEL_GEM", 10), ("OVAL_CHARM", 1)],
           {"not_yet": ["I am GEETA, chairwoman of PALDEA's POKéMON LEAGUE. I came to see the trainer on "
                        "MT. SILVER.", "Win the KANTO LEAGUE first. Then I will judge your strength myself."],
            "challenge": ["I am GEETA, chairwoman of PALDEA's POKéMON LEAGUE. I came to see the trainer on "
                          "MT. SILVER.", "A KANTO CHAMPION. Very well. Consider this your final interview "
                          "before MT. SILVER."],
            "declined": ["Come back when you are prepared. I do not grade on effort."],
            "defeat": ["...Remarkable. You pass, with distinction."],
            "reward": ["Accept these, with the LEAGUE's compliments."],
            "after": ["The road ahead leads to MT. SILVER. Show RED what you showed me."]}),
    Battle("N", 673, "N", "Pkmn Trainer 1 Hns", "N Hns", "Male", "Hg Boy 1", "Green",
           "OBJ_EVENT_GFX_N_HNS", [("NationalPark_Normal_hns", 30, 30, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("ELECTRIC_GEM", 10), ("ABILITY_CAPSULE", 1)],
           {"not_yet": ["...I'm N. I came to hear the voices of the POKéMON in this park.",
                        "Win the KANTO LEAGUE. Then let me hear your POKéMON's voices in battle."],
            "challenge": ["...I'm N. I came to hear the voices of the POKéMON in this park.",
                          "Your POKéMON say they trust you. Let me see that truth for myself!"],
            "declined": ["...I see. I'll keep listening to the POKéMON here."],
            "defeat": ["Your POKéMON... they're happy. That is the answer I was looking for."],
            "reward": ["Please, take these. For you, and for your friends."],
            "after": ["POKéMON and people can understand each other. You've shown me that."]}),
    Battle("CYRUS", 674, "CYRUS", "Pkmn Trainer 1 Hns", "Cyrus Hns", "Male", "Hg Boy 1", "Blue",
           "OBJ_EVENT_GFX_CYRUS_HNS", [("Mahoganytown_hns", 12, 10, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("DARK_GEM", 10), ("PP_MAX", 3)],
           {"not_yet": ["I am CYRUS. I seek a world without spirit... and the strength to make it real.",
                        "Win the KANTO LEAGUE. Then you will be worth my time."],
            "challenge": ["I am CYRUS. I seek a world without spirit... and the strength to make it real.",
                          "A CHAMPION. Let us see whether your bonds are strength... or weakness."],
            "declined": ["Hmph. Hesitation is the weakness of spirit."],
            "defeat": ["...So this is the strength that spirit gives. Interesting."],
            "reward": ["Take these. I have no use for sentiment."],
            "after": ["Go. Seek your answer atop MT. SILVER, as I seek mine."]}),
    Battle("WALLACE", 675, "WALLACE", "Champion Hns", "Champion Wallace", "Male", "Hg Boy 1", "Light Blue",
           "OBJ_EVENT_GFX_WALLACE", [("CherrygroveCity_hns", 30, 17, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("WATER_GEM", 10), ("ABILITY_PATCH", 1)],
           {"not_yet": ["I'm WALLACE, HOENN's CHAMPION. JOHTO's sea breeze is simply exquisite!",
                        "Win the KANTO LEAGUE, and we shall battle with elegance!"],
            "challenge": ["I'm WALLACE, HOENN's CHAMPION. JOHTO's sea breeze is simply exquisite!",
                          "A KANTO CHAMPION! Then let us create a battle as beautiful as the sea!"],
            "declined": ["Ah, a pity! I'll admire the waves a while longer."],
            "defeat": ["Magnificent! A battle of true elegance!"],
            "reward": ["Please, accept these with my sincerest admiration."],
            "after": ["Beauty and strength flow together, like the tide."]}),
    Battle("MAXIE", 676, "MAXIE", "Magma Leader", "Magma Leader Maxie", "Male", "Hg Boy 1", "Dark Red",
           "OBJ_EVENT_GFX_MAXIE", [("FuchsiaCity_hns", 25, 9, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("FIRE_GEM", 10), ("HEAT_ROCK", 1)],
           {"not_yet": ["I am MAXIE of TEAM MAGMA. I am studying KANTO's land... purely for science.",
                        "Win the KANTO LEAGUE. Then I shall test your strength."],
            "challenge": ["I am MAXIE of TEAM MAGMA. I am studying KANTO's land... purely for science.",
                          "A CHAMPION. Fufufu... let's see if you can withstand the heat of the land!"],
            "declined": ["Prudence. I can respect that."],
            "defeat": ["Fufufu... I miscalculated. Again."],
            "reward": ["Take these. A token of my recalculated respect."],
            "after": ["The land and the sea must stay in balance. I have learned that, at least."]}),
    Battle("ARCHIE", 677, "ARCHIE", "Aqua Leader", "Aqua Leader Archie", "Male", "Hg Boy 1", "Blue",
           "OBJ_EVENT_GFX_ARCHIE", [("CeruleanCity_hns", 18, 8, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("POISON_GEM", 10), ("DEEP_SEA_TOOTH", 1), ("DEEP_SEA_SCALE", 1)],
           {"not_yet": ["Bwahahaha! ARCHIE of TEAM AQUA here! I came to see KANTO's seas!",
                        "Win the KANTO LEAGUE, and I'll show you the power of the sea!"],
            "challenge": ["Bwahahaha! ARCHIE of TEAM AQUA here! I came to see KANTO's seas!",
                          "A CHAMPION, eh? Let's see if you can swim against the tide!"],
            "declined": ["Scared of a little water? Bwahahaha!"],
            "defeat": ["Bwahahaha! You sank me fair and square!"],
            "reward": ["Here! Treasures from the bottom of the sea!"],
            "after": ["The sea is vast, and so is your strength. Bwahahaha!"]}),
    Battle("WALLY", 678, "WALLY", "Pkmn Trainer 1 Hns", "Wally", "Male", "Hg Boy 1", "Green",
           "OBJ_EVENT_GFX_WALLY", [("PalletTown_hns", 8, 9, "down")],
           ("flag", KANTO_CHAMPION_FLAG),
           [("PSYCHIC_GEM", 10), ("DAWN_STONE", 1), ("SHINY_STONE", 1)],
           {"not_yet": ["Hi! I'm WALLY. I came to see the town where RED grew up!",
                        "When you've won the KANTO LEAGUE, will you battle me? I've gotten a lot stronger!"],
            "challenge": ["Hi! I'm WALLY. I came to see the town where RED grew up!",
                          "You won the KANTO LEAGUE? Then please, battle me! I want to see how far I've "
                          "come!"],
            "declined": ["Okay... I'll keep training until you're ready!"],
            "defeat": ["I lost... but I'm not sad. You're amazing!"],
            "reward": ["Please take these! Thank you for battling me!"],
            "after": ["Someday I'll be strong enough to battle RED too!"]}),
]

BATTLES = JOHTO + KANTO + POSTGAME


def read(path):
    with open(os.path.join(ROOT, path) if not os.path.isabs(path) else path, encoding="utf-8") as f:
        return f.read()


def tm_numbers():
    """TM_<MOVE> -> its number, from include/constants/tms_hms.h (Heart & Soul's list)."""
    text = read("include/constants/tms_hms.h")
    start = text.index("#if IS_HNS")
    block = text[start:text.index("#define FOREACH_HM(F)", start)]
    return {f"TM_{m}": n for n, m in enumerate(re.findall(r"F\((\w+)\)", block), 1)}


def item_names():
    """Reward item -> its name in messages: the Bag's name, and a TM's move ("TM70 TRIPLE AXEL")."""
    names = {k[len("ITEM_"):]: v[0] for k, v in care_packages.items_data().items()}
    moves = read("src/data/moves_info.h")
    for tm, n in tm_numbers().items():
        m = re.search(r"\[MOVE_" + tm[3:] + r"\]\s*=\s*\{\s*\.name\s*=\s*COMPOUND_STRING\(\"([^\"]+)\"\)", moves)
        names[tm] = f"TM{n:02d} {m.group(1)}" if m else f"TM{n:02d}"
    return names


# --- Messages -----------------------------------------------------------------------------------------

class Text:
    def __init__(self):
        self.widths = care_packages.glyph_widths()
        # A placeholder's widest text: the player's name, 7 characters
        self.placeholders = {"{PLAYER}": max(self.widths.values()) * 7}

    def width(self, text):
        w = 0
        for ph, pw in self.placeholders.items():
            w += text.count(ph) * pw
            text = text.replace(ph, "")
        return w + care_packages.text_width(text, self.widths)

    def wrap(self, paragraph):
        lines, line = [], ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            if self.width(candidate) <= care_packages.LINE_WIDTH:
                line = candidate
            elif not line:
                sys.exit(f"word too wide for the message box: {word}")
            else:
                lines.append(line)
                line = word
        return lines + [line]

    def pages(self, paragraphs):
        """Paragraphs -> lines with their endings: two lines a box, a new box for each paragraph."""
        out = []
        for p, paragraph in enumerate(paragraphs):
            lines = self.wrap(paragraph)
            for i, line in enumerate(lines):
                if i == len(lines) - 1:
                    end = "$" if p == len(paragraphs) - 1 else "\\p"
                else:
                    end = "\\n" if i == 0 else "\\l"
                out.append((line, end))
        return out

    def inc(self, label, paragraphs):
        return [f"{label}:"] + [f'\t.string "{line}{end}"' for line, end in self.pages(paragraphs)] + [""]

    def c(self, name, paragraphs):
        lines = self.pages(paragraphs)
        body = [f'    "{line}{"" if end == "$" else end}"' for line, end in lines]
        return [f"static const u8 {name}[] = _("] + body[:-1] + [body[-1] + ");", ""]


def reward_sentence(battle, names):
    items = []
    for item, n in battle.reward:
        items.append(f"{names[item]} ×{n}" if n > 1 else names[item])
    listed = items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]
    return [f"{{PLAYER}} received {listed}!"]


# --- Outputs --------------------------------------------------------------------------------------------

def render_rewards(text, names):
    out = ["// Generated by tools/crystal_imperium/side_battles.py from its table: edit that, not this file.",
           "// Crystal Imperium side battles (DECISIONS.md D41): each reward and the message listing it.", ""]
    for k, b in enumerate(BATTLES):
        out.append(f"static const struct SideBattleRewardItem sSideBattleReward{k}[] =  // {b.name}")
        out.append("{")
        out += [f"    {{ITEM_{item}, {n}}}," for item, n in b.reward]
        out += ["};", ""]
        out += text.c(f"sSideBattleRewardText{k}", reward_sentence(b, names))
    out.append("static const struct SideBattleReward sSideBattleRewards[] =")
    out.append("{")
    out += [f"    {{sSideBattleReward{k}, ARRAY_COUNT(sSideBattleReward{k}), sSideBattleRewardText{k}}},"
            for k in range(len(BATTLES))]
    out += ["};", ""]
    return "\n".join(out)


SHARED = """\
@ Generated by tools/crystal_imperium/side_battles.py from its table: edit that, not this file.
@ Crystal Imperium side battles (DECISIONS.md D41): Gym Leaders from newer regions and the postgame's
@ visitors. Each waits on its map (map.json), talks, offers a battle (YES/NO) once its badges or flag
@ allow it, and after a win gives its reward once (src/side_battles.c, src/data/side_battle_rewards.h).

@ VAR_0x8004: the reward. VAR_RESULT is TRUE once it is given; FALSE when neither the BAG nor the PC
@ had room for all of it (nothing is given then, and talking to the trainer again tries once more)
SideBattle_EventScript_GiveReward::
	callnative SideBattle_GiveReward
	goto_if_eq VAR_RESULT, FALSE, SideBattle_EventScript_NoRoom
	playfanfare MUS_OBTAIN_ITEM
	callnative SideBattle_LoadRewardText
	callstd MSGBOX_DEFAULT
	waitfanfare
	goto_if_eq VAR_0x8005, 0, SideBattle_EventScript_GiveRewardDone
	msgbox SideBattle_Text_SentToPC, MSGBOX_DEFAULT
SideBattle_EventScript_GiveRewardDone:
	setvar VAR_RESULT, TRUE
	return

SideBattle_EventScript_NoRoom:
	msgbox SideBattle_Text_NoRoom, MSGBOX_DEFAULT
	setvar VAR_RESULT, FALSE
	return

SideBattle_EventScript_Release:
	release
	end
"""

SHARED_TEXTS = {
    "SideBattle_Text_SentToPC": ["Some of it didn't fit in the BAG, so it was sent to your PC."],
    "SideBattle_Text_NoRoom": ["Your BAG and PC are both full! Make some room, then come back for it."],
}


def gate_lines(b, label):
    kind, value = b.gate
    if kind == "badges":
        if value == 0:
            return []
        return ["\tspecialvar VAR_RESULT, GetBadgeCount", f"\tgoto_if_lt VAR_RESULT, {value}, {label}_NotYet"]
    return [f"\tgoto_if_unset {value}, {label}_NotYet"]


def battle_script(b, k, text):
    label = f"SideBattle_{b.key.title().replace('_', '')}"
    t = f"SideBattle_Text_{b.key.title().replace('_', '')}"
    out = [f"{label}_EventScript::", "\tlock", "\tfaceplayer",
           f"\tgoto_if_set {b.reward_flag}, {label}_After"]
    out += [f"\tgoto_if_defeated {trainer}, {label}_Reward" for trainer, _ in b.trainers()]
    out += gate_lines(b, label)
    if b.second:
        out += ["\tspecialvar VAR_RESULT, GetBadgeCount", f"\tgoto_if_ge VAR_RESULT, {b.second[1]}, {label}_Second"]
    out += [f"\tmsgbox {t}_Challenge, MSGBOX_YESNO", f"\tgoto_if_eq VAR_RESULT, NO, {label}_Declined",
            f"\ttrainerbattle_no_intro {b.trainer}, {t}_Defeat", f"\tgoto {label}_Reward", ""]
    if b.second:
        out += [f"{label}_Second:", f"\tmsgbox {t}_Challenge2, MSGBOX_YESNO",
                f"\tgoto_if_eq VAR_RESULT, NO, {label}_Declined",
                f"\ttrainerbattle_no_intro TRAINER_SIDE_{b.key}_2_HNS, {t}_Defeat", f"\tgoto {label}_Reward", ""]
    out += [f"{label}_Reward:", f"\tmsgbox {t}_Reward, MSGBOX_DEFAULT", f"\tsetvar VAR_0x8004, {k}",
            "\tcall SideBattle_EventScript_GiveReward",
            "\tgoto_if_eq VAR_RESULT, FALSE, SideBattle_EventScript_Release", f"\tsetflag {b.reward_flag}",
            f"{label}_After:", f"\tmsgbox {t}_After, MSGBOX_DEFAULT", "\trelease", "\tend", ""]
    if b.gate != ("badges", 0):
        out += [f"{label}_NotYet:", f"\tmsgbox {t}_NotYet, MSGBOX_DEFAULT", "\trelease", "\tend", ""]
    out += [f"{label}_Declined:", f"\tmsgbox {t}_Declined, MSGBOX_DEFAULT", "\trelease", "\tend", ""]
    texts = {"Challenge": b.texts["challenge"], "Declined": b.texts["declined"], "Defeat": b.texts["defeat"],
             "Reward": b.texts["reward"], "After": b.texts["after"]}
    if b.gate != ("badges", 0):
        texts["NotYet"] = b.texts["not_yet"]
    if b.second:
        texts["Challenge2"] = b.second[2]
    for name, paragraphs in texts.items():
        out += text.inc(f"{t}_{name}", paragraphs)
    return out


def script_label(b):
    return f"SideBattle_{b.key.title().replace('_', '')}_EventScript"


def render_scripts(text):
    out = SHARED.splitlines() + [""]
    for label, paragraphs in SHARED_TEXTS.items():
        out += text.inc(label, paragraphs)
    for k, b in enumerate(BATTLES):
        out += battle_script(b, k, text)
    return "\n".join(out).rstrip("\n") + "\n"


OPP_START = "// Crystal Imperium side battles (DECISIONS.md D41): written by tools/crystal_imperium/side_battles.py"
OPP_END = "// End of the side battles"


def render_opponents(text):
    rows = sorted((tid, trainer) for b in BATTLES for trainer, tid in b.trainers())
    block = [OPP_START] + [f"#define {trainer:<37} {tid}" for tid, trainer in rows] + [OPP_END, ""]
    start = text.find(OPP_START)
    if start >= 0:  # in place, so that the Ace Trainers' block (ace_trainers.py) stays after it
        end = text.index(OPP_END, start) + len(OPP_END) + 1
        text = text[:start] + "\n".join(block) + text[end:]
    else:
        count = re.search(r"#define TRAINERS_COUNT_HNS\s+(\d+)", text)
        text = text.replace(count.group(0), "\n".join(block) + "\n" + count.group(0))
    count = re.search(r"#define TRAINERS_COUNT_HNS\s+(\d+)", text)
    base = 653  # Heart & Soul's own trainers end at 652
    # Every trainer ID counts, the Ace Trainers' too
    others = [int(v) for v in re.findall(r"(?m)^#define TRAINER_\w+\s+(\d+)\s*$", text)]
    new_count = max([base - 1] + others + [tid for tid, _ in rows]) + 1
    return text.replace(count.group(0), re.sub(r"\d+$", str(new_count), count.group(0)))


def header_block(b, trainer):
    return (f"=== {trainer} ===\nName: {b.name}\nClass: {b.trainer_class}\nPic: {b.pic}\nGender: {b.gender}\n"
            f"Music: {b.music}\nDouble Battle: No\nAI: Smart Trainer / Ace Pokemon / HP Aware\nMugshot: {b.mugshot}\n")


def render_party(text):
    """Each side battle trainer's block: its header lines from the table; an existing block keeps its AI
    and bag items lines and its Pokemon (boss_teams.py writes those)."""
    for b in BATTLES:
        for trainer, _ in b.trainers():
            m = re.search(r"(?ms)^=== " + trainer + r" ===\n.*?(?=^=== |\Z)", text)
            if not m:
                text = text.rstrip("\n") + "\n\n" + header_block(b, trainer)
                continue
            block = m.group(0)
            lines = block.split("\n")
            end = lines.index("") if "" in lines else len(lines)
            ai = [l for l in lines[1:end] if l.startswith("AI:")]
            items = [l for l in lines[1:end] if l.startswith("Items:")]
            # The order boss_teams.py's render() keeps: the AI line in place, the bag items last
            new = [ai[0] if ai and l.startswith("AI:") else l
                   for l in header_block(b, trainer).rstrip("\n").split("\n")] + items
            text = text[:m.start()] + "\n".join(new + lines[end:]) + text[m.end():]
    return text


# --- Maps ---------------------------------------------------------------------------------------------

_CACHE = {}


def behaviors():
    """MB_* names in order (include/constants/metatile_behaviors.h)"""
    if "behaviors" not in _CACHE:
        _CACHE["behaviors"] = re.findall(r"^\s*(MB_\w+)", read("include/constants/metatile_behaviors.h"), re.M)
    return _CACHE["behaviors"]


def surfable():
    """The water behaviors (TILE_FLAG_SURFABLE in src/metatile_behavior.c)"""
    if "surfable" not in _CACHE:
        _CACHE["surfable"] = set(re.findall(r"\[(MB_\w+)\]\s*=[^,\n]*TILE_FLAG_SURFABLE", read("src/metatile_behavior.c")))
    return _CACHE["surfable"]


def tileset_attributes(tileset):
    """A tileset's metatile attributes file (src/data/tilesets/headers.h, metatiles.h)"""
    if tileset not in _CACHE:
        header = re.search(r"const struct Tileset " + tileset + r"\s*=\s*\{(.*?)\};", read("src/data/tilesets/headers.h"), re.S)
        symbol = re.search(r"\.metatileAttributes\s*=\s*(\w+)", header.group(1)).group(1)
        path = re.search(symbol + r"\[\]\s*=\s*INCBIN_U16\(\"([^\"]+)\"\)", read("src/data/tilesets/metatiles.h")).group(1)
        _CACHE[tileset] = open(os.path.join(ROOT, path), "rb").read()
    return _CACHE[tileset]


class MapData:
    """A map's tiles (collision, elevation) and what stands on them, for a side battle's spot."""
    def __init__(self, folder):
        self.path = os.path.join(ROOT, "data", "maps", folder, "map.json")
        self.json = json.loads(read(self.path))
        self.layouts = {l["id"]: l for l in json.loads(read("data/layouts/layouts.json"))["layouts"] if "id" in l}
        lay = self.layouts[self.json["layout"]]
        self.w, self.h = lay["width"], lay["height"]

    def tile(self, x, y, layout=None):
        """(collision, elevation) at (x, y), on the map's layout or another it switches to (the Lake of
        Rage's low tide)"""
        lay = self.layouts[layout or self.json["layout"]]
        w, h = lay["width"], lay["height"]
        data = open(os.path.join(ROOT, lay["blockdata_filepath"]), "rb").read()[:w * h * 2]
        c = struct.unpack(f"<{w * h}H", data)[y * w + x]
        return (c >> 10) & 3, c >> 12

    def behavior(self, x, y, layout=None):
        """The metatile behavior (MB_*) at (x, y): Heart & Soul's layouts keep 16-bit attributes, the
        behavior in the low byte, and 640 metatiles in a primary tileset (include/fieldmap.h)"""
        lay = self.layouts[layout or self.json["layout"]]
        if lay.get("layout_version") != "hns":
            sys.exit(f"{lay['id']}: only Heart & Soul's layouts are read here")
        w, h = lay["width"], lay["height"]
        data = open(os.path.join(ROOT, lay["blockdata_filepath"]), "rb").read()[:w * h * 2]
        metatile = struct.unpack(f"<{w * h}H", data)[y * w + x] & 0x3FF
        primary = metatile < 640
        attributes = tileset_attributes(lay["primary_tileset" if primary else "secondary_tileset"])
        return behaviors()[struct.unpack_from("<H", attributes, 2 * (metatile if primary else metatile - 640))[0] & 0xFF]

    def taken(self, x, y, script):
        for kind in ("object_events", "warp_events", "coord_events", "bg_events"):
            for e in self.json.get(kind) or []:
                if int(e["x"]) == x and int(e["y"]) == y and e.get("script") != script:
                    return kind
        return None

    def reachable(self, blocked, layout=None):
        """The tiles the player can walk to from where they come in (the warps, and the map's edges
        toward its connections), not over the blocked tiles, with the game's elevation rule
        (IsElevationMismatchAt: a move between two different elevations is blocked unless one of
        them is 0; 15, a bridge, keeps the elevation). No ledges, sideways stairs' one-way steps or
        field moves; the edge of a water connection starts on the water, as if surfing in. A warp is
        a start even where its tile blocks walking (a door): the player comes out of it."""
        lay = self.layouts[layout or self.json["layout"]]
        w, h = lay["width"], lay["height"]
        warps = [(int(e["x"]), int(e["y"])) for e in self.json.get("warp_events") or []]
        edges = []
        for c in self.json.get("connections") or []:
            edges += {"up": [(x, 0) for x in range(w)], "down": [(x, h - 1) for x in range(w)],
                      "left": [(0, y) for y in range(h)], "right": [(w - 1, y) for y in range(h)]}.get(c["direction"], [])
        seen, todo = set(), []
        for x, y in warps + edges:
            if ((x, y) not in blocked and 0 <= x < w and 0 <= y < h
                    and ((x, y) in warps or self.tile(x, y, layout)[0] == 0)):
                todo.append((x, y, self.tile(x, y, layout)[1]))
        seen.update(todo)
        while todo:
            x, y, elevation = todo.pop()
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                    continue
                collision, e = self.tile(nx, ny, layout)
                if collision or (elevation and e not in (0, 15) and e != elevation):
                    continue
                step = (nx, ny, elevation if e == 15 else e)
                if step not in seen:
                    seen.add(step)
                    todo.append(step)
        return {(x, y) for x, y, _ in seen}


def place_objects(check_only):
    """Adds or updates each side battle's object on its maps; returns the maps out of date."""
    stale = []
    for b in BATTLES:
        for folder, x, y, facing, *layouts in b.places:
            m = MapData(folder)
            script = script_label(b)
            if not (0 <= x < m.w and 0 <= y < m.h):
                sys.exit(f"{b.key}: ({x},{y}) is outside {folder}")
            dx, dy = {"down": (0, 1), "up": (0, -1), "left": (-1, 0), "right": (1, 0)}[facing]
            for layout in [None] + (layouts[0] if layouts else []):
                if m.tile(x, y, layout)[0]:
                    sys.exit(f"{b.key}: ({x},{y}) on {folder} ({layout or 'its layout'}) is blocked")
                # Not in the water, and the player talks from land
                for tx, ty in ((x, y), (x + dx, y + dy)):
                    if m.behavior(tx, ty, layout) in surfable():
                        sys.exit(f"{b.key}: ({tx},{ty}) on {folder} ({layout or 'its layout'}) is water")
            other = m.taken(x, y, script)
            if other:
                sys.exit(f"{b.key}: ({x},{y}) on {folder} already has one of its {other}")
            # The player can walk up to talk, and the trainer cuts no one off: every other object
            # counts as standing in the way, wherever its flag hides it
            others = {(int(o["x"]), int(o["y"])) for o in m.json["object_events"] if o.get("script") != script}
            for layout in [None] + (layouts[0] if layouts else []):
                free = m.reachable(others, layout)
                there = m.reachable(others | {(x, y)}, layout)
                if (x + dx, y + dy) not in there:
                    sys.exit(f"{b.key}: on {folder} ({layout or 'its layout'}), no way to ({x + dx},{y + dy}) to talk")
                cut_off = free - there - {(x, y)}
                if cut_off:
                    sys.exit(f"{b.key}: at ({x},{y}) on {folder} ({layout or 'its layout'}), cuts off {sorted(cut_off)[:5]}")
            obj = {"graphics_id": b.gfx, "x": x, "y": y, "elevation": 0, "movement_type": FACINGS[facing],
                   "movement_range_x": 0, "movement_range_y": 0, "trainer_type": "TRAINER_TYPE_NONE",
                   "trainer_sight_or_berry_tree_id": "0", "script": script, "flag": "0"}
            objects = m.json["object_events"]
            mine = [i for i, o in enumerate(objects) if o.get("script") == script]
            if mine:
                if objects[mine[0]] == obj:
                    continue
                objects[mine[0]] = obj
            else:
                if len(objects) >= MAX_MAP_OBJECTS:
                    sys.exit(f"{folder} has no room for another object")
                objects.append(obj)
            stale.append(os.path.relpath(m.path, ROOT))
            if not check_only:
                with open(m.path, "w", encoding="utf-8") as f:
                    json.dump(m.json, f, indent=2, ensure_ascii=False)
                    f.write("\n")
    return stale


# --- Checks -------------------------------------------------------------------------------------------

def mega_shop():
    """The Goldenrod Dept. Store 5F Mega Stone shop's lists, by the badge count each starts at (its
    script: 3, 6, 8 badges; the last one once the player is Champion, here 9)."""
    text = read("data/maps/GoldenrodCity_DepartmentStore_5F_hns/scripts.inc")
    lists = dict(re.findall(r"GoldenrodDeptStore5_MegaStones(\d)::?\n(.*?)pokemartlistend", text, re.S))
    if sorted(lists) != ["1", "2", "3", "4"]:
        sys.exit("the Mega Stone shop's lists weren't found")
    return {start: set(re.findall(r"ITEM_(\w+)", lists[n])) for n, start in (("1", 3), ("2", 6), ("3", 8), ("4", 9))}


def on_sale_at(shop, badges):
    """The Mega Stones the shop sells at a badge count (9: after the Johto League)."""
    starts = [start for start in shop if start <= badges]
    return shop[max(starts)] if starts else set()


def check(names):
    defined = read("include/constants/flags_hns.h") + read("include/constants/flags.h")
    pics = read("include/constants/trainers.h")
    gfx = read("include/constants/event_objects.h")
    moves_info = read("src/data/moves_info.h")
    shop = mega_shop()
    every_stone = set().union(*shop.values())
    seen_ids, seen_keys = set(), set()
    for b in BATTLES:
        if b.key in seen_keys:
            sys.exit(f"{b.key} twice")
        seen_keys.add(b.key)
        for trainer, tid in b.trainers():
            if tid in seen_ids or not 653 <= tid <= MAX_TRAINER_ID:
                sys.exit(f"{trainer}: trainer ID {tid} taken or out of range")
            seen_ids.add(tid)
        if len(b.name) > MAX_NAME:
            sys.exit(f"{b.key}: name longer than {MAX_NAME}")
        if not re.search(r"#define " + b.reward_flag + r"\b", defined):
            sys.exit(f"{b.key}: {b.reward_flag} isn't defined (include/constants/flags_hns.h)")
        pic = "TRAINER_PIC_FRONT_" + re.sub(r"\W+", "_", b.pic).upper()
        if not re.search(r"\b" + pic + r"\b", pics):
            sys.exit(f"{b.key}: no {pic}")
        if not re.search(r"#define " + b.gfx + r"\b", gfx):
            sys.exit(f"{b.key}: no {b.gfx}")
        if b.mugshot not in MUGSHOTS:
            sys.exit(f"{b.key}: mugshot {b.mugshot}")
        kind, value = b.gate
        if kind == "flag" and not re.search(r"#define " + value + r"\b", defined):
            sys.exit(f"{b.key}: {value} isn't defined")
        if not 1 <= len(b.reward) <= MAX_REWARD_ITEMS:
            sys.exit(f"{b.key}: 1 to {MAX_REWARD_ITEMS} reward items")
        if len({item for item, _ in b.reward}) != len(b.reward):
            sys.exit(f"{b.key}: an item twice in the reward")
        for item, n in b.reward:
            if item not in names:
                sys.exit(f"{b.key}: no ITEM_{item}")
            if not 0 < n <= 999:
                sys.exit(f"{b.key}: {n} {item}")
            # A TM in a Johto reward comes before the TM shops sell it
            if item.startswith("TM_") and kind == "badges" and tm_list.badges_needed(moves_info, item[3:]) <= value:
                sys.exit(f"{b.key}: TM_{item[3:]} is on sale already at {value} badges")
            # A Mega Stone comes before the Mega shop sells it
            if item in every_stone and item in on_sale_at(shop, value if kind == "badges" else 9):
                sys.exit(f"{b.key}: {item} is on sale already")
        needed = {"challenge", "declined", "defeat", "reward", "after"} | ({"not_yet"} if b.gate != ("badges", 0) else set())
        if set(b.texts) != needed:
            sys.exit(f"{b.key}: texts {sorted(set(b.texts) ^ needed)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    names = item_names()
    check(names)
    text = Text()
    outputs = {
        OPPONENTS: render_opponents(read(OPPONENTS)),
        PARTY: render_party(read(PARTY)),
        REWARDS: render_rewards(text, names),
        SCRIPTS: render_scripts(text),
    }
    stale = []
    for path, new in outputs.items():
        old = read(path) if os.path.exists(path) else ""
        if new == old:
            continue
        stale.append(os.path.relpath(path, ROOT))
        if not args.check:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
    stale += place_objects(args.check)
    if args.check and stale:
        print(f"{', '.join(stale)} out of date: run tools/crystal_imperium/side_battles.py")
        return 1
    for path in stale:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
