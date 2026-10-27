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
eight, one per badge stage; Kanto has eight leaders from Unova, Kalos, Galar and Paldea; the postgame
has other regions' Champions and rivals around Johto and Kanto. Every one battles at the player's
level cap with six Pokemon (boss_teams.py, D21). A reward holds what this game doesn't already give
ten at a time (the care packages, D16): ten Gems of the trainer's type, TMs before the TM shops sell
them (D36), Mega Stones before the Goldenrod Mega shop sells them, an evolution item for the
trainer's own Pokemon, and items nothing else gives (the Rotom Catalog). It goes whole to the Bag,
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
    Battle("CANDICE", 653, "CANDICE", "Leader Hns", "Skier F Hns", "Female", "Hg Girl 1", "Light Blue",
           "OBJ_EVENT_GFX_SKIER_F_HNS", [("VioletCity_TrainerSchool_hns", 8, 3, "down")],
           ("badges", 0),
           [("ICE_GEM", 10), ("TM_TRIPLE_AXEL", 1), ("TM_ICE_PUNCH", 1)],
           {"challenge": ["Hi! I'm CANDICE, the GYM LEADER of SNOWPOINT CITY, way up north in SINNOH!",
                          "I'm visiting JOHTO's TRAINER SCHOOL to see how you train here. How about a battle? "
                          "I'll keep it cool!"],
            "declined": ["Aww, okay! I'll be right here practicing my diamond dust!"],
            "defeat": ["Brrr! Your focus cut right through my ice!"],
            "reward": ["You earned these! Take them with you!"],
            "after": ["Train with all your focus, and your POKéMON will sparkle like diamond dust!"]}),
    Battle("GARDENIA", 654, "GARDENIA", "Leader Hns", "Picnicker", "Female", "Hg Girl 1", "Green",
           "OBJ_EVENT_GFX_PICNICKER_HNS", [("IlexForest_hns", 25, 36, "down")],
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
    Battle("FANTINA", 656, "FANTINA", "Leader Hns", "Hex Maniac", "Female", "Hg Girl 1", "Purple",
           "OBJ_EVENT_GFX_CHANNELER_HNS", [("EcruteakCity_hns", 41, 41, "down")],
           ("badges", 3),
           [("GHOST_GEM", 10), ("TM_POLTERGEIST", 1), ("GENGARITE", 1), ("REAPER_CLOTH", 1)],
           {"not_yet": ["Bonjour! I am FANTINA, GYM LEADER of HEARTHOME CITY. I came to see the dances of "
                        "ECRUTEAK!", "Come back with three GYM BADGES. Then we dance a battle, yes?"],
            "challenge": ["Ah, three BADGES! Then you are ready to dance with my GHOST POKéMON! Shall we?"],
            "declined": ["Non? Then I watch the KIMONO GIRLS a little longer."],
            "defeat": ["Magnifique! You danced better than my POKéMON!"],
            "reward": ["A wonderful battle deserves a gift!"],
            "after": ["The dances of this city, they are like my GHOST POKéMON: graceful and a little "
                      "mysterious!"]}),
    Battle("MAYLENE", 657, "MAYLENE", "Leader Hns", "Battle Girl", "Female", "Hg Girl 1", "Orange",
           "OBJ_EVENT_GFX_BATTLE_GIRL_HNS", [("CianwoodCity_hns", 17, 46, "down")],
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
    Battle("WAKE", 658, "WAKE", "Leader Hns", "Black Belt", "Male", "Hg Boy 1", "Blue",
           "OBJ_EVENT_GFX_BLACK_BELT_HNS", [("LakeOfRage_hns", 49, 30, "left", ["LAYOUT_LAKE_OF_RAGE_LOW_TIDE_HNS"])],
           ("badges", 5),
           [("WATER_GEM", 10), ("GYARADOSITE", 1), ("KINGS_ROCK", 1)],
           {"not_yet": ["Wahahah! I'm CRASHER WAKE, PASTORIA CITY's GYM LEADER! I heard this lake makes "
                        "GYARADOS go wild!", "Come back with five GYM BADGES, and I'll crash right into you!"],
            "challenge": ["Five BADGES? Then hold on tight! My WATER POKéMON hit like a tidal wave! Ready?"],
            "declined": ["Wahahah! Scared of a little splash? I'll be waiting!"],
            "defeat": ["Wahahah! I got washed away!"],
            "reward": ["What a battle! Here, a prize from CRASHER WAKE!"],
            "after": ["Crash through anything in your way, just like a wave!"]}),
    Battle("BYRON", 659, "BYRON", "Leader Hns", "Hiker", "Male", "Hg Boy 1", "Dark Red",
           "OBJ_EVENT_GFX_HIKER_HNS", [("OlivineCity_hns", 41, 51, "down")],
           ("badges", 6),
           [("STEEL_GEM", 10), ("TM_STEEL_BEAM", 1), ("METAGROSSITE", 1), ("METAL_COAT", 1)],
           {"not_yet": ["Bwahahaha! I'm BYRON, GYM LEADER of CANALAVE CITY! I sailed here to see "
                        "JASMINE's STEEL POKéMON!", "Come back with six GYM BADGES, youngster!"],
            "challenge": ["Six BADGES! Bwahahaha! Then let's see if you can dent my STEEL POKéMON!"],
            "declined": ["Bwahahaha! Steel doesn't rust from waiting!"],
            "defeat": ["Bwahahaha! You cracked my steel!"],
            "reward": ["Take these! Fine work deserves fine rewards!"],
            "after": ["My son ROARK is somewhere in JOHTO too. He's always digging for fossils!"]}),
    Battle("ROARK", 660, "ROARK", "Leader Hns", "Engineer Hns", "Male", "Hg Boy 1", "Orange",
           "OBJ_EVENT_GFX_ENGINEER_HNS", [("Route44_hns", 69, 13, "down")],
           ("badges", 7),
           [("ROCK_GEM", 10), ("TM_EXPLOSION", 1), ("TYRANITARITE", 1), ("PROTECTOR", 1)],
           {"not_yet": ["I'm ROARK, OREBURGH CITY's GYM LEADER. I'm looking for fossils near the ICE PATH.",
                        "Come back with seven GYM BADGES, and my ROCK POKéMON will battle you!"],
            "challenge": ["Seven BADGES, huh? Then my ROCK POKéMON won't hold back! Let's battle!"],
            "declined": ["Okay. I'll keep digging."],
            "defeat": ["You smashed right through my ROCK POKéMON!"],
            "reward": ["Here, take these. I dug them up myself... well, some of them!"],
            "after": ["Dad's in OLIVINE CITY, looking at the lighthouse. He loves anything made of "
                      "steel!"]}),
    Battle("VOLKNER", 661, "VOLKNER", "Leader Hns", "Cooltrainer M", "Male", "Hg Boy 1", "Yellow",
           "OBJ_EVENT_GFX_COOLTRAINER_M_HNS", [("IndigoPlateau_hns", 13, 8, "down")],
           ("badges", 8),
           [("ELECTRIC_GEM", 10), ("ROTOM_CATALOG", 1), ("ELECTIRIZER", 1)],
           {"not_yet": ["...I'm VOLKNER. SUNYSHORE CITY's GYM LEADER. I'm waiting for a trainer worth "
                        "battling.", "Come back with all eight GYM BADGES."],
            "challenge": ["Eight BADGES. You might be the one who can make my battles exciting again. "
                          "Ready?"],
            "declined": ["...Fine. I'll wait."],
            "defeat": ["...Heh. That was fun. I haven't felt this charged up in ages."],
            "reward": ["Take these. You've earned them."],
            "after": ["Go win the POKéMON LEAGUE. Then come back and tell me about it."]}),
]

# Kanto's eight and the postgame's visitors are added once their sprites are in (DECISIONS.md D41)
KANTO = []
POSTGAME = []

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
    if start >= 0:
        end = text.index(OPP_END, start) + len(OPP_END) + 1
        text = text[:start] + text[end:].lstrip("\n")
    count = re.search(r"#define TRAINERS_COUNT_HNS\s+(\d+)", text)
    base = 653  # Heart & Soul's own trainers end at 652
    new_count = max([base - 1] + [tid for tid, _ in rows]) + 1
    text = text.replace(count.group(0), "\n".join(block) + "\n" + re.sub(r"\d+$", str(new_count), count.group(0)))
    return text


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

    def taken(self, x, y, script):
        for kind in ("object_events", "warp_events", "coord_events", "bg_events"):
            for e in self.json.get(kind) or []:
                if int(e["x"]) == x and int(e["y"]) == y and e.get("script") != script:
                    return kind
        return None


def place_objects(check_only):
    """Adds or updates each side battle's object on its maps; returns the maps out of date."""
    stale = []
    for b in BATTLES:
        for folder, x, y, facing, *layouts in b.places:
            m = MapData(folder)
            script = script_label(b)
            if not (0 <= x < m.w and 0 <= y < m.h):
                sys.exit(f"{b.key}: ({x},{y}) is outside {folder}")
            for layout in [None] + (layouts[0] if layouts else []):
                if m.tile(x, y, layout)[0]:
                    sys.exit(f"{b.key}: ({x},{y}) on {folder} ({layout or 'its layout'}) is blocked")
            other = m.taken(x, y, script)
            if other:
                sys.exit(f"{b.key}: ({x},{y}) on {folder} already has one of its {other}")
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
