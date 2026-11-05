#!/usr/bin/env python3
"""Crystal Imperium boss teams (Emerald Imperium-style): writes the parties below into
src/data/trainers_hns.party, keeping each trainer's header (name, class, picture, music, mugshot)
and replacing its AI, bag items and Pokemon. Heart & Soul's own teams for the other bosses
(LEVEL_ONLY) keep their Pokemon and only get their levels set. The list of every boss, and of the
other teams made for a stage (the Ace Trainers and Heart & Soul's Cooltrainers with competitive
teams, ace_trainer_data.py: D56), goes to src/data/level_cap_bosses.h for the battle code.

  python3 tools/crystal_imperium/boss_teams.py          # rewrite the parties and the boss list
  python3 tools/crystal_imperium/boss_teams.py --check  # exit 1 if either file is out of date

Design rules (DECISIONS.md D21):
  * every Pokemon of a boss is at the player's level cap: the party file has the NORMAL cap
    (src/caps.c) of the earliest point in the game the battle can happen (its stage: a badge count,
    or the Johto or Kanto League won), and the battle code sets the cap of that stage or the
    player's, whichever is later, from the player's cap table, HARD caps included
    (src/battle_main.c)
  * every Pokemon has a held item, a nature, an ability chosen for the set and four moves it
    can learn (validate.py checks abilities and moves)
  * IVs are 31 (Minimal Grinding gives every Pokemon 31 IVs anyway; this covers games with it off),
    except where a set needs others: mon()'s ivs (tools/crystal_imperium/team_kit.py), such as 0 Speed
    on a Trick Room team, which the battle keeps
  * a team made for a stage keeps its Pokemon as made at its stage's cap; fought later, it evolves,
    except a named Eviolite species holding an Eviolite and a Pikachu holding a Light Ball, and an
    evolved Pokemon holds its raised_item instead (team_kit.py; src/data/level_cap_bosses.h lists
    both for the battle code)
  * from the 5th Gym on, each boss has one Mega Evolution, normally the ace
  * Red is the hardest battle in the game (D27): level 100, competitive EVs (which he keeps under
    Minimal Grinding), the prediction AI and the most Full Restores; validate.py checks it
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ace_trainer_data  # noqa: E402  (the Ace Trainers and the Cooltrainers' teams, and their stages)
import team_kit  # noqa: E402  (mon(), the party renderer, the named Eviolite species)
from team_kit import mon, FRIENDSHIP_MOVES, FULL_FRIENDSHIP  # noqa: E402,F401  (other tools read them here too)
PARTY = os.path.join(ROOT, "src", "data", "trainers_hns.party")
BOSS_LIST = os.path.join(ROOT, "src", "data", "level_cap_bosses.h")

BOSS_AI = "Smart Trainer / Ace Pokemon / HP Aware"
RED_AI = "Smart Trainer / Prediction / Ace Pokemon / HP Aware"

# Stages after the eighth badge: the Johto League won (FLAG_IS_CHAMPION; cap 90 for all of Kanto)
# and the Kanto League won (FLAG_IS_KANTO_CHAMPION; no cap left)
JOHTO_CHAMPION = "Johto Champion"
KANTO_CHAMPION = "Kanto Champion"
MAX_LEVEL = 100


def read_caps():
    """The NORMAL level caps by badge count and the Kanto cap, from src/caps.c."""
    with open(os.path.join(ROOT, "src", "caps.c"), encoding="utf-8") as f:
        text = f.read()
    table = re.search(r"sLevelCapTable_Normal\[\]\s*=\s*\{(.*?)\};", text, re.S).group(1)
    caps = [int(v) for v in re.findall(r"\]\s*=\s*(\d+)", table)]
    kanto = int(re.search(r"#define KANTO_MAX_LEVEL (\d+)", text).group(1))
    return caps, kanto


NORMAL_CAPS, KANTO_CAP = read_caps()


def cap(stage):
    """The NORMAL level cap at a stage: a badge count (0-8), JOHTO_CHAMPION or KANTO_CHAMPION."""
    if stage == KANTO_CHAMPION:
        return MAX_LEVEL
    if stage == JOHTO_CHAMPION:
        return KANTO_CAP
    return NORMAL_CAPS[stage]


# --- Falkner (1st Gym, no badges: cap 15) -----------------------------------------------------------
# Heart & Soul's Pidgey, Rookidee and Noctowl, and since 0.8.0 a full six: Magic Bounce Natu,
# Gale Wings Fletchling and Prankster Murkrow (Thunder Wave) for Speed control.
FALKNER = [
    mon("Murkrow", "Eviolite", "Prankster", "Bold", ["Tailwind", "Thunder Wave", "Foul Play", "Haze"]),
    mon("Natu", "Eviolite", "Magic Bounce", "Bold", ["Night Shade", "Air Cutter", "Teleport", "Wish"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Fletchling", "Oran Berry", "Gale Wings", "Jolly", ["Acrobatics", "Flame Charge", "U-turn", "Roost"]),
    mon("Trumbeak", "Muscle Band", "Skill Link", "Adamant", ["Rock Blast", "Bullet Seed", "Pluck", "Knock Off"]),
    mon("Squawkabilly", "Silk Scarf", "Intimidate", "Jolly", ["Parting Shot", "Dual Wingbeat", "Facade", "Quick Attack"]),
    mon("Pidgeotto", "Sitrus Berry", "No Guard", "Adamant", ["Wing Attack", "Steel Wing", "Quick Attack", "Roost"]),
]

# --- Bugsy (2nd Gym, 1 badge: cap 24) -------------------------------------------------------------
# Heart & Soul's team (Spinarak, Pineco, Ledian, Scyther with early moves) was no longer a fight at
# the Emerald Imperium-style caps (D29): a naive team won 19 battles in 20. Sticky Web and Toxic
# Thread from the lead, Rock coverage for the Fire and Flying types sent against him, screens,
# Sleep Powder, a Speed Boost Yanma and a Technician Scyther as the ace (six since D30).
BUGSY = [
    mon("Ariados", "Black Sludge", "No Guard", "Adamant", ["Sticky Web", "Toxic Thread", "Sucker Punch", "Lunge"]),
    mon("Pineco", "Sitrus Berry", "Sturdy", "Relaxed", ["Stealth Rock", "Rock Tomb", "Bug Bite", "Explosion"]),
    mon("Ledian", "Light Clay", "Iron Fist", "Calm", ["Reflect", "Light Screen", "Silver Wind", "Mach Punch"]),
    mon("Butterfree", "Silver Powder", "Compound Eyes", "Timid", ["Sleep Powder", "Bug Buzz", "Air Slash", "Psybeam"]),
    mon("Yanma", "Sitrus Berry", "Speed Boost", "Modest", ["Ancient Power", "Air Slash", "Bug Buzz", "Protect"]),
    mon("Scyther", "Eviolite", "Technician", "Jolly", ["Bug Bite", "Aerial Ace", "Quick Attack", "Fury Cutter"]),
]

# --- Whitney (3rd Gym, 2 badges: cap 33) ----------------------------------------------------------
# Heart & Soul's four and their moves, with held items: at the higher caps (D29) her team without
# items lost 13 battles in 20 to a naive team (0.7.0: 15 in 20 won by her). Furret and Girafarig
# make six (D30).
WHITNEY = [
    mon("Aipom", "Eviolite", "Skill Link", "Jolly", ["Fake Out", "Tail Slap", "U-turn", "Knock Off"]),
    mon("Clefable", "Leftovers", "Magic Guard", "Bold", ["Moonblast", "Thunder Wave", "Encore", "Soft-Boiled"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Furret", "Silk Scarf", "Adaptability", "Jolly", ["Double-Edge", "Sucker Punch", "Ice Punch", "Knock Off"]),
    mon("Stantler", "Sitrus Berry", "Intimidate", "Adamant", ["Body Slam", "Earthquake", "Megahorn", "Thunder Wave"]),
    mon("Girafarig", "Twisted Spoon", "Sap Sipper", "Modest", ["Nasty Plot", "Psychic", "Hyper Voice", "Thunderbolt"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Miltank", "Leftovers", "Thick Fat", "Impish", ["Rollout", "Defense Curl", "Body Slam", "Milk Drink"], "252 HP"),
]

# --- Morty (4th Gym, 3 badges: cap 42) ------------------------------------------------------------
MORTY = [
    mon("Marowak Alola", "Thick Club", "Lightning Rod", "Adamant", ["Stealth Rock", "Shadow Bone", "Bonemerang", "Fire Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Sableye", "Sitrus Berry", "Prankster", "Careful", ["Will O Wisp", "Knock Off", "Night Shade", "Recover"],
        "252 HP / 4 Def / 252 SpD"),
    mon("Misdreavus", "Eviolite", "Levitate", "Timid", ["Hex", "Thunder Wave", "Dazzling Gleam", "Pain Split"],
        "252 HP / 4 Def / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Drifblim", "Sitrus Berry", "Unburden", "Modest", ["Calm Mind", "Shadow Ball", "Air Slash", "Thunderbolt"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Swords Dance", "Play Rough", "Shadow Sneak", "Drain Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Focus Blast"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]

# --- Chuck, Jasmine, Pryce (5th to 7th Gym in any order) ------------------------------------------
# HnS picks the party by how many of the three the player has beaten: _1 with 4 badges (cap 50),
# _1_2 with 5 (cap 58), _1_3 with 6 (cap 66).
CHUCK = [
    mon("Hitmontop", "Rocky Helmet", "Intimidate", "Adamant", ["Fake Out", "Close Combat", "Sucker Punch", "Triple Axel"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Breloom", "Life Orb", "Technician", "Jolly", ["Spore", "Bullet Seed", "Mach Punch", "Rock Tomb"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Hawlucha", "Sitrus Berry", "Unburden", "Jolly", ["Swords Dance", "Close Combat", "Acrobatics", "Throat Chop"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Annihilape", "Leftovers", "Defiant", "Jolly", ["Bulk Up", "Rage Fist", "Drain Punch", "U-turn"],
        "252 HP / 252 Atk / 4 Spe"),
    mon("Poliwrath", "Sitrus Berry", "Water Absorb", "Adamant", ["Belly Drum", "Liquidation", "Close Combat", "Ice Punch"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Heracross", "Heracronite", "Moxie", "Jolly", ["Pin Missile", "Rock Blast", "Close Combat", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
]
CHUCK_1_3 = [
    mon("Iron Hands", "Booster Energy", "Quark Drive", "Adamant", ["Fake Out", "Drain Punch", "Supercell Slam", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Breloom", "Life Orb", "Technician", "Jolly", ["Spore", "Bullet Seed", "Mach Punch", "Rock Tomb"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Kommo-o", "Life Orb", "Bulletproof", "Jolly", ["Dragon Dance", "Close Combat", "Scale Shot", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Annihilape", "Leftovers", "Defiant", "Jolly", ["Bulk Up", "Rage Fist", "Drain Punch", "U-turn"],
        "252 HP / 252 Atk / 4 Spe"),
    mon("Poliwrath", "Sitrus Berry", "Water Absorb", "Adamant", ["Belly Drum", "Liquidation", "Close Combat", "Ice Punch"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Heracross", "Heracronite", "Moxie", "Jolly", ["Pin Missile", "Rock Blast", "Close Combat", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
]
CHUCK_1_2 = [
    mon("Iron Hands", "Booster Energy", "Quark Drive", "Adamant", ["Fake Out", "Drain Punch", "Supercell Slam", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Breloom", "Life Orb", "Technician", "Jolly", ["Spore", "Bullet Seed", "Mach Punch", "Rock Tomb"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Hawlucha", "Sitrus Berry", "Unburden", "Jolly", ["Swords Dance", "Close Combat", "Acrobatics", "Throat Chop"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Annihilape", "Leftovers", "Defiant", "Jolly", ["Bulk Up", "Rage Fist", "Drain Punch", "U-turn"],
        "252 HP / 252 Atk / 4 Spe"),
    mon("Poliwrath", "Sitrus Berry", "Water Absorb", "Adamant", ["Belly Drum", "Liquidation", "Close Combat", "Ice Punch"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Heracross", "Heracronite", "Moxie", "Jolly", ["Pin Missile", "Rock Blast", "Close Combat", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
]
JASMINE = [
    mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Drill Peck", "Roost", "Whirlwind"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Magnezone", "Air Balloon", "Magnet Pull", "Timid", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Thunder Wave"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Bronzong", "Leftovers", "Levitate", "Sassy", ["Stealth Rock", "Gyro Ball", "Earthquake", "Toxic"],
        "252 HP / 4 Atk / 252 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Mawile", "Sitrus Berry", "Intimidate", "Adamant", ["Iron Head", "Play Rough", "Sucker Punch", "Swords Dance"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Scizor", "Metal Coat", "Technician", "Adamant", ["Bullet Punch", "U-turn", "Knock Off", "Swords Dance"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Steelix", "Steelixite", "Sturdy", "Brave", ["Gyro Ball", "Earthquake", "Rock Slide", "Curse"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
]
JASMINE_1_3 = [
    mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Drill Peck", "Roost", "Whirlwind"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Magnezone", "Air Balloon", "Magnet Pull", "Timid", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Thunder Wave"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Iron Treads", "Booster Energy", "Quark Drive", "Jolly", ["Stealth Rock", "Earthquake", "Knock Off", "Rapid Spin"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Kingambit", "Black Glasses", "Supreme Overlord", "Adamant", ["Swords Dance", "Kowtow Cleave", "Sucker Punch", "Low Kick"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Scizor", "Metal Coat", "Technician", "Adamant", ["Bullet Punch", "U-turn", "Knock Off", "Swords Dance"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Steelix", "Steelixite", "Sturdy", "Brave", ["Gyro Ball", "Earthquake", "Rock Slide", "Curse"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
]
JASMINE_1_2 = [
    mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Drill Peck", "Roost", "Whirlwind"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Magnezone", "Air Balloon", "Magnet Pull", "Timid", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Thunder Wave"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Iron Treads", "Booster Energy", "Quark Drive", "Jolly", ["Stealth Rock", "Earthquake", "Knock Off", "Rapid Spin"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Mawile", "Sitrus Berry", "Intimidate", "Adamant", ["Iron Head", "Play Rough", "Sucker Punch", "Swords Dance"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Scizor", "Metal Coat", "Technician", "Adamant", ["Bullet Punch", "U-turn", "Knock Off", "Swords Dance"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Steelix", "Steelixite", "Sturdy", "Brave", ["Gyro Ball", "Earthquake", "Rock Slide", "Curse"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
]
PRYCE = [
    mon("Cloyster", "Focus Sash", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Shell Smash", "Liquidation"]),
    mon("Dewgong", "Leftovers", "Thick Fat", "Bold", ["Surf", "Ice Beam", "Toxic", "Protect"]),
    mon("Jynx", "Wise Glasses", "Dry Skin", "Timid", ["Lovely Kiss", "Ice Beam", "Psychic", "Nasty Plot"]),
    mon("Weavile", "Razor Claw", "Pressure", "Jolly", ["Ice Punch", "Knock Off", "Ice Shard", "Low Kick"]),
    mon("Mamoswine", "Never Melt Ice", "Thick Fat", "Adamant", ["Earthquake", "Icicle Crash", "Ice Shard", "Stone Edge"]),
    mon("Abomasnow", "Abomasite", "Snow Warning", "Quiet", ["Blizzard", "Energy Ball", "Ice Shard", "Earthquake"]),
]


# --- Clair (8th Gym, 7 badges: cap 75) ------------------------------------------------------------
CLAIR = [
    mon("Druddigon", "Rocky Helmet", "Rough Skin", "Adamant", ["Outrage", "Gunk Shot", "Sucker Punch", "Glare"]),
    mon("Flygon", "Choice Scarf", "Levitate", "Jolly", ["Earthquake", "Dragon Claw", "U Turn", "Fire Punch"]),
    mon("Dragalge", "Black Sludge", "Adaptability", "Modest", ["Sludge Bomb", "Dragon Pulse", "Focus Blast", "Toxic Spikes"]),
    mon("Altaria", "Altarianite", "Natural Cure", "Modest", ["Hyper Voice", "Dragon Pulse", "Fire Blast", "Roost"]),
    mon("Kommo O", "Life Orb", "Bulletproof", "Jolly", ["Scale Shot", "Close Combat", "Poison Jab", "Swords Dance"]),
    mon("Kingdra", "Wacan Berry", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Rain Dance"]),
]

# --- Side battles: Sinnoh's Gym Leaders visiting Johto (DECISIONS.md D41) ------------------------
# tools/crystal_imperium/side_battles.py places them and gates each by a badge count, its stage here.
# Each is a Gym Leader at its stage's cap: six Pokemon, the bag items of the real Gym Leaders of the
# stage, and from the 5th Gym's stage (4 badges) on one Mega Evolution. None is a Pokemon the Johto
# Gym Leaders of the stage use, so the side battle is a different fight.
#   Candice (no badges, Violet City's Trainer School): Fake Out and Icy Wind for Speed, Huge Power
#   Meditite and a Recover Cryogonal as the ace.
SIDE_CANDICE = [
    mon("Snover", "Icy Rock", "Snow Warning", "Quiet", ["Icy Wind", "Giga Drain", "Leech Seed", "Ice Shard"]),
    mon("Sneasel", "Never Melt Ice", "Inner Focus", "Jolly", ["Fake Out", "Icicle Crash", "Knock Off", "Ice Shard"]),
    mon("Snorunt", "Eviolite", "Ice Body", "Jolly", ["Spikes", "Ice Fang", "Crunch", "Disable"],
        raised_item="Focus Sash"),
    mon("Cubchoo", "Muscle Band", "Slush Rush", "Adamant", ["Ice Punch", "Liquidation", "Low Kick", "Play Rough"]),
    mon("Meditite", "Eviolite", "Huge Power", "Adamant", ["Drain Punch", "Zen Headbutt", "Ice Punch", "Bullet Punch"],
        raised_item="Life Orb"),
    mon("Cryogonal", "Leftovers", "Levitate", "Modest", ["Freeze Dry", "Flash Cannon", "Recover", "Reflect"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
#   Gardenia (2 badges, Ilex Forest): Cherrim's sun for Solar Beam, Weather Ball and a Harvest Dolliv;
#   from 4 badges her second team, with Mega Venusaur.
SIDE_GARDENIA = [
    mon("Whimsicott", "Heat Rock", "Prankster", "Timid", ["Sunny Day", "Leech Seed", "Moonblast", "U Turn"]),
    mon("Cherrim", "Miracle Seed", "Flower Gift", "Adamant", ["Solar Blade", "Play Rough", "Swords Dance", "Morning Sun"]),
    mon("Bellossom", "Leftovers", "Chlorophyll", "Modest", ["Quiver Dance", "Giga Drain", "Moonblast", "Strength Sap"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Grotle", "Eviolite", "Shell Armor", "Adamant", ["Shell Smash", "Seed Bomb", "Crunch", "Bulldoze"],
        raised_item="White Herb"),
    mon("Dolliv", "Sitrus Berry", "Harvest", "Bold", ["Energy Ball", "Earth Power", "Strength Sap", "Leech Seed"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Roserade", "Black Sludge", "Natural Cure", "Timid", ["Sludge Bomb", "Giga Drain", "Weather Ball", "Spikes"],
        "252 SpA", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
SIDE_GARDENIA_2 = [
    mon("Sudowoodo", "Sitrus Berry", "Rock Head", "Adamant", ["Stealth Rock", "Head Smash", "Sucker Punch", "Wood Hammer"]),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Modest", ["Sleep Powder", "Giga Drain", "Moonblast", "Sludge Bomb"]),
    mon("Arboliva", "Leftovers", "Seed Sower", "Modest", ["Hyper Voice", "Energy Ball", "Earth Power", "Strength Sap"]),
    mon("Torterra", "White Herb", "Shell Armor", "Adamant", ["Wood Hammer", "Earthquake", "Stone Edge", "Shell Smash"]),
    mon("Roserade", "Focus Sash", "Natural Cure", "Timid", ["Leaf Storm", "Sludge Bomb", "Shadow Ball", "Spikes"]),
    mon("Venusaur", "Venusaurite", "Chlorophyll", "Modest", ["Giga Drain", "Sludge Bomb", "Earth Power", "Synthesis"]),
]
#   Fantina (3 badges, Ecruteak City): Will-O-Wisp for Hex, Trick Room for the slow ones, an Illusion
#   Hisuian Zoroark.
SIDE_FANTINA = [
    mon("Cofagrigus", "Mental Herb", "Shadow Shield", "Sassy", ["Trick Room", "Will O Wisp", "Hex", "Pain Split"],
        "252 HP / 4 Def / 252 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Golurk", "Life Orb", "No Guard", "Brave", ["Stealth Rock", "Dynamic Punch", "Poltergeist", "Earthquake"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Cursola", "Spell Tag", "Perish Body", "Quiet", ["Hex", "Earth Power", "Strength Sap", "Power Gem"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Trevenant", "Sitrus Berry", "Harvest", "Brave", ["Trick Room", "Horn Leech", "Poltergeist", "Will O Wisp"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Mismagius", "Wise Glasses", "Levitate", "Timid", ["Nasty Plot", "Shadow Ball", "Mystical Fire", "Thunderbolt"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Dusknoir", "Dusknoirite", "Pressure", "Brave", ["Poltergeist", "Darkest Lariat", "Shadow Sneak", "Will O Wisp"],
        "252 HP / 252 Atk / 4 SpD", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
]
#   Maylene (4 badges, Cianwood City): fast Fighting types and Mega Lucario.
SIDE_MAYLENE = [
    mon("Medicham", "Sitrus Berry", "Huge Power", "Jolly", ["Fake Out", "High Jump Kick", "Zen Headbutt", "Bullet Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Mienshao", "Life Orb", "Regenerator", "Jolly", ["Close Combat", "U Turn", "Knock Off", "Triple Axel"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Poliwrath", "Mystic Water", "Swift Swim", "Adamant", ["Bulk Up", "Liquidation", "Drain Punch", "Ice Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Toxicroak", "Black Sludge", "Dry Skin", "Adamant", ["Swords Dance", "Gunk Shot", "Drain Punch", "Sucker Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Pawmot", "Expert Belt", "Iron Fist", "Jolly", ["Double Shock", "Mach Punch", "Ice Punch", "Thunder Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Lucario", "Lucarionite", "Inner Focus", "Jolly", ["Swords Dance", "Close Combat", "Meteor Mash", "Ice Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]
#   Wake (5 badges, Lake of Rage): Drizzle rain for Swift Swim, and Mega Gyarados.
SIDE_WAKE = [
    mon("Politoed", "Damp Rock", "Drizzle", "Bold", ["Scald", "Ice Beam", "Hypnosis", "Encore"]),
    mon("Floatzel", "Life Orb", "Technician", "Jolly", ["Wave Crash", "Ice Spinner", "Aqua Jet", "Bulk Up"]),
    mon("Quagsire", "Leftovers", "Unaware", "Impish", ["Earthquake", "Liquidation", "Recover", "Toxic"]),
    mon("Toedscruel", "Sitrus Berry", "Mold Breaker", "Timid", ["Spore", "Earth Power", "Giga Drain", "Rapid Spin"]),
    mon("Barraskewda", "Choice Band", "Swift Swim", "Adamant", ["Liquidation", "Close Combat", "Psychic Fangs", "Aqua Jet"]),
    mon("Gyarados", "Gyaradosite", "Moxie", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Dragon Dance"]),
]
#   Byron (6 badges, Olivine City): Steel walls and Mega Aggron.
SIDE_BYRON = [
    mon("Bastiodon", "Leftovers", "Dauntless Shield", "Impish", ["Stealth Rock", "Iron Defense", "Body Press", "Roar"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Empoleon", "Assault Vest", "Competitive", "Modest", ["Hydro Pump", "Flash Cannon", "Ice Beam", "Aqua Jet"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Excadrill", "Focus Sash", "Mold Breaker", "Jolly", ["Earthquake", "Iron Head", "Rapid Spin", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Magnezone", "Choice Specs", "Magnet Pull", "Timid", ["Thunder", "Flash Cannon", "Volt Switch", "Hidden Power"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 30 SpA / 31 SpD / 30 Spe"),
    mon("Corviknight", "Rocky Helmet", "Pressure", "Impish", ["Brave Bird", "Body Press", "Bulk Up", "Roost"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Aggron", "Aggronite", "Sturdy", "Adamant", ["Heavy Slam", "Earthquake", "Ice Punch", "Rock Polish"],
        "252 HP / 252 Atk / 4 SpD"),
]
#   Roark (7 badges, Route 44 by the Ice Path): hazards, Head Smash and Mega Tyranitar's sand.
SIDE_ROARK = [
    mon("Glimmora", "Focus Sash", "Toxic Debris", "Timid", ["Mortal Spin", "Power Gem", "Sludge Wave", "Stealth Rock"]),
    mon("Garganacl", "Leftovers", "Purifying Salt", "Careful", ["Salt Cure", "Body Press", "Iron Defense", "Recover"]),
    mon("Tyrantrum", "Life Orb", "Rock Head", "Jolly", ["Head Smash", "Dragon Claw", "Psychic Fangs", "Dragon Dance"]),
    mon("Kleavor", "Lum Berry", "Sharpness", "Jolly", ["Stone Axe", "X Scissor", "Close Combat", "Swords Dance"]),
    mon("Rampardos", "Choice Scarf", "Mold Breaker", "Adamant", ["Head Smash", "Earthquake", "Fire Punch", "Zen Headbutt"]),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Jolly", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
]
#   Volkner (8 badges, Indigo Plateau): fast Electric types, Rotom-Wash and Mega Manectric.
SIDE_VOLKNER = [
    mon("Jolteon", "Life Orb", "Volt Absorb", "Timid", ["Thunderbolt", "Shadow Ball", "Hyper Voice", "Calm Mind"]),
    mon("Raichu Alola", "Focus Sash", "Surge Surfer", "Timid", ["Thunderbolt", "Psychic", "Focus Blast", "Nasty Plot"]),
    mon("Luxray", "Choice Band", "Intimidate", "Adamant", ["Wild Charge", "Crunch", "Ice Fang", "Play Rough"]),
    mon("Rotom Wash", "Leftovers", "Levitate", "Bold", ["Hydro Pump", "Volt Switch", "Will O Wisp", "Pain Split"]),
    mon("Electivire", "Expert Belt", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Earthquake", "Cross Chop"]),
    mon("Manectric", "Manectite", "Lightning Rod", "Timid", ["Thunderbolt", "Flamethrower", "Volt Switch", "Snarl"]),
]
# --- Side battles: Paldea's Gym Leaders visiting Kanto (D41), after the Johto League ---------------
# Each at Kanto's cap like Kanto's own leaders: six Pokemon, two Full Restores and one Mega Evolution.
#   Katy (Pewter City): Sticky Web, Quiver Dance Volcarona, Guts Ursaluna and Mega Pinsir.
SIDE_KATY = [
    mon("Ribombee", "Focus Sash", "Shield Dust", "Timid", ["Sticky Web", "Moonblast", "Stun Spore", "U Turn"]),
    mon("Lokix", "Life Orb", "Tinted Lens", "Jolly", ["First Impression", "Sucker Punch", "Lunge", "Swords Dance"]),
    mon("Volcarona", "Heavy Duty Boots", "Flame Body", "Timid", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"]),
    mon("Golisopod", "Assault Vest", "Emergency Exit", "Adamant", ["First Impression", "Liquidation", "Leech Life", "Knock Off"]),
    mon("Ursaluna", "Flame Orb", "Guts", "Adamant", ["Facade", "Headlong Rush", "Crunch", "Swords Dance"]),
    mon("Pinsir", "Pinsirite", "Moxie", "Jolly", ["Double Edge", "Close Combat", "Earthquake", "Swords Dance"]),
]
#   Brassius (Route 25, Cerulean Cape): Grassy Surge Rillaboom and Mega Sceptile.
SIDE_BRASSIUS = [
    mon("Brambleghast", "Focus Sash", "Wind Rider", "Jolly", ["Spikes", "Power Whip", "Poltergeist", "Rapid Spin"]),
    mon("Meowscarada", "Choice Band", "Protean", "Jolly", ["Flower Trick", "Knock Off", "U Turn", "Play Rough"]),
    mon("Scovillain", "Life Orb", "Chlorophyll", "Modest", ["Fire Blast", "Energy Ball", "Sunny Day", "Solar Beam"]),
    mon("Tsareena", "Sitrus Berry", "Queenly Majesty", "Jolly", ["Power Whip", "High Jump Kick", "Triple Axel", "Rapid Spin"]),
    mon("Rillaboom", "Miracle Seed", "Grassy Surge", "Adamant", ["Grassy Glide", "Wood Hammer", "Knock Off", "U Turn"]),
    mon("Sceptile", "Sceptilite", "Unburden", "Timid", ["Leaf Storm", "Dragon Pulse", "Focus Blast", "Earthquake"]),
]
#   Iono (Lavender Town, by the Radio Tower): Volt Switch pivots, her Mismagius and Mega Ampharos.
SIDE_IONO = [
    mon("Galvantula", "Focus Sash", "Compound Eyes", "Timid", ["Sticky Web", "Thunder", "Energy Ball", "Volt Switch"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Kilowattrel", "Heavy Duty Boots", "Competitive", "Timid", ["Air Slash", "Thunderbolt", "Roost", "U Turn"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Bellibolt", "Leftovers", "Electromorphosis", "Bold", ["Discharge", "Muddy Water", "Slack Off", "Toxic"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Electrode Hisui", "Life Orb", "Soundproof", "Timid", ["Volt Switch", "Leaf Storm", "Thunderbolt", "Taunt"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Mismagius", "Spell Tag", "Levitate", "Timid", ["Nasty Plot", "Shadow Ball", "Thunderbolt", "Dazzling Gleam"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Luxray", "Luxrite", "Intimidate", "Jolly", ["Crunch", "Psychic Fangs", "Thunder Fang", "Quick Attack"],
        "4 HP / 252 Atk / 252 Spe"),
]
#   Kofu (Vermilion City's pier): Dondozo, Mega Launcher Clawitzer and Mega Sharpedo.
SIDE_KOFU = [
    mon("Wugtrio", "Focus Sash", "Gooey", "Jolly", ["Triple Dive", "Sucker Punch", "Memento", "Liquidation"]),
    mon("Veluza", "Life Orb", "Sharpness", "Adamant", ["Aqua Cutter", "Psycho Cut", "Night Slash", "Fillet Away"]),
    mon("Crabominable", "Sitrus Berry", "Iron Fist", "Adamant", ["Ice Hammer", "Close Combat", "Crabhammer", "Bulk Up"]),
    mon("Dondozo", "Leftovers", "Unaware", "Impish", ["Wave Crash", "Body Press", "Rest", "Curse"]),
    mon("Clawitzer", "Choice Specs", "Mega Launcher", "Modest", ["Water Pulse", "Dark Pulse", "Aura Sphere", "Dragon Pulse"]),
    mon("Sharpedo", "Sharpedonite", "Speed Boost", "Adamant", ["Waterfall", "Crunch", "Psychic Fangs", "Protect"]),
]
#   Larry (Viridian City): his Staraptor and Komala, Serene Grace Dudunsparce and Mega Kangaskhan.
SIDE_LARRY = [
    mon("Komala", "Assault Vest", "Comatose", "Adamant", ["Double Edge", "Wood Hammer", "Sucker Punch", "U Turn"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Dudunsparce", "Leftovers", "Serene Grace", "Careful", ["Coil", "Body Slam", "Earthquake", "Roost"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Staraptor", "Choice Scarf", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "Double Edge", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Flamigo", "Sharp Beak", "Scrappy", "Jolly", ["Swords Dance", "Brave Bird", "Close Combat", "Throat Chop"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Bewear", "Sitrus Berry", "Fluffy", "Adamant", ["Swords Dance", "Double Edge", "Drain Punch", "Darkest Lariat"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Slaking", "Slakite", "Truant", "Jolly", ["Double Edge", "Earthquake", "Knock Off", "Slack Off"],
        "4 HP / 252 Atk / 252 Spe"),
]
#   Ryme (Celadon City): Last Respects, Rage Fist, Gholdengo and Mega Gengar.
SIDE_RYME = [
    mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Swords Dance", "Play Rough", "Shadow Claw", "Drain Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Banette", "Spell Tag", "Insomnia", "Adamant", ["Poltergeist", "Knock Off", "Gunk Shot", "Will O Wisp"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Dragapult", "Focus Sash", "Infiltrator", "Jolly", ["Dragon Darts", "Phantom Force", "U Turn", "Dragon Dance"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gholdengo", "Choice Specs", "Good As Gold", "Modest", ["Make It Rain", "Shadow Ball", "Dazzling Gleam", "Trick"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Houndstone", "Choice Band", "Fluffy", "Adamant", ["Last Respects", "Play Rough", "Psychic Fangs", "Shadow Sneak"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Toxtricity", "Toxtricitite", "Punk Rock", "Timid", ["Boomburst", "Overdrive", "Sludge Bomb", "Volt Switch"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
#   Tulip (Saffron City): Armor Tail Farigiraf against priority, Calm Mind and Mega Gardevoir.
SIDE_TULIP = [
    mon("Farigiraf", "Sitrus Berry", "Armor Tail", "Modest", ["Nasty Plot", "Hyper Voice", "Psychic Noise", "Shadow Ball"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Gardevoir", "Leftovers", "Trace", "Calm", ["Moonblast", "Mystical Fire", "Wish", "Teleport"],
        "252 HP / 4 Def / 252 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Espathra", "Life Orb", "Speed Boost", "Timid", ["Calm Mind", "Stored Power", "Dazzling Gleam", "Lumina Crash"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Hatterene", "Expert Belt", "Magic Bounce", "Modest", ["Psyshock", "Draining Kiss", "Mystical Fire", "Nuzzle"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Florges", "Leftovers", "Natural Cure", "Calm", ["Moonblast", "Psychic", "Calm Mind", "Synthesis"],
        "252 HP / 4 Def / 252 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Gallade", "Galladite", "Sharpness", "Jolly", ["Swords Dance", "Sacred Sword", "Psycho Cut", "Shadow Sneak"],
        "4 HP / 252 Atk / 252 Spe"),
]
#   Grusha (Cinnabar Island): Alolan Ninetales' snow and Aurora Veil, Slush Rush and Mega Altaria.
SIDE_GRUSHA = [
    mon("Ninetales Alola", "Light Clay", "Snow Warning", "Timid", ["Aurora Veil", "Blizzard", "Moonblast", "Freeze Dry"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Sandslash Alola", "Leftovers", "Slush Rush", "Jolly", ["Stealth Rock", "Icicle Crash", "Iron Head", "Rapid Spin"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Frosmoth", "Heavy Duty Boots", "Ice Scales", "Timid", ["Quiver Dance", "Blizzard", "Bug Buzz", "Giga Drain"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Beartic", "Life Orb", "Slush Rush", "Adamant", ["Swords Dance", "Icicle Crash", "Close Combat", "Aqua Jet"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Cetitan", "Sitrus Berry", "Slush Rush", "Adamant", ["Belly Drum", "Icicle Crash", "Earthquake", "Ice Shard"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Altaria", "Altarianite", "Natural Cure", "Jolly", ["Dragon Dance", "Body Slam", "Earthquake", "Roost"],
        "4 HP / 252 Atk / 252 Spe"),
]
# --- Side battles: the postgame's visitors (D41), once the player has won the Kanto League ---------
# Level 100, when Red battles too. Red stays the hardest battle (D27): these have no EVs, the Ace AI
# without prediction and three Full Restores to his four.
POST_ITEMS = "Full Restore / Full Restore / Full Restore"
#   Cynthia (Ruins of Alph): her Platinum six, with Mega Garchomp.
POST_CYNTHIA = [
    mon("Spiritomb", "Leftovers", "Intimidate", "Careful", ["Foul Play", "Will O Wisp", "Sucker Punch", "Pain Split"]),
    mon("Roserade", "Focus Sash", "Natural Cure", "Timid", ["Spikes", "Leaf Storm", "Sludge Bomb", "Extrasensory"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Togekiss", "Leftovers", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Nasty Plot", "Roost"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Milotic", "Sitrus Berry", "Marvel Scale", "Bold", ["Scald", "Ice Beam", "Recover", "Dragon Tail"]),
    mon("Garchomp", "Loaded Dice", "Rough Skin", "Jolly", ["Swords Dance", "Scale Shot", "Earthquake", "Iron Head"]),
    mon("Lucario", "Lucarionite", "Inner Focus", "Timid", ["Nasty Plot", "Aura Sphere", "Flash Cannon", "Dark Pulse"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
#   Iris (Blackthorn City): her Champion team's dragons, Mega Aggron and her Haxorus.
POST_IRIS = [
    mon("Archeops", "Focus Sash", "Defeatist", "Jolly", ["Stone Edge", "Acrobatics", "Earthquake", "U Turn"]),
    mon("Lapras", "Leftovers", "Water Absorb", "Modest", ["Freeze Dry", "Hydro Pump", "Thunderbolt", "Ice Shard"]),
    mon("Hydreigon", "Choice Specs", "Levitate", "Timid", ["Draco Meteor", "Dark Pulse", "Flamethrower", "U Turn"]),
    mon("Aggron", "Aggronite", "Rock Head", "Adamant", ["Heavy Slam", "Earthquake", "Head Smash", "Ice Punch"]),
    mon("Dragonite", "Weakness Policy", "Multiscale", "Adamant", ["Dragon Dance", "Extreme Speed", "Earthquake", "Outrage"]),
    mon("Haxorus", "Lum Berry", "Mold Breaker", "Jolly", ["Swords Dance", "Outrage", "Earthquake", "Poison Jab"]),
]
#   Geeta (Route 28, before Mt. Silver): her Top Champion team, Kingambit last.
POST_GEETA = [
    mon("Glimmora", "Focus Sash", "Toxic Debris", "Timid", ["Stealth Rock", "Mortal Spin", "Power Gem", "Earth Power"]),
    mon("Espathra", "Life Orb", "Speed Boost", "Timid", ["Calm Mind", "Stored Power", "Dazzling Gleam", "Protect"]),
    mon("Gogoat", "Leftovers", "Sap Sipper", "Adamant", ["Horn Leech", "Earthquake", "Bulk Up", "Milk Drink"]),
    mon("Veluza", "Sitrus Berry", "Sharpness", "Adamant", ["Aqua Cutter", "Psycho Cut", "Night Slash", "Fillet Away"]),
    mon("Avalugg", "Rocky Helmet", "Sturdy", "Impish", ["Avalanche", "Body Press", "Rapid Spin", "Recover"]),
    mon("Kingambit", "Black Glasses", "Supreme Overlord", "Adamant", ["Kowtow Cleave", "Iron Head", "Sucker Punch", "Swords Dance"]),
]
#   N (National Park): his Black and White team; Zoroark's Illusion shows Zekrom.
POST_N = [
    mon("Zoroark", "Life Orb", "Illusion", "Timid", ["Night Daze", "Flamethrower", "Focus Blast", "Nasty Plot"]),
    mon("Carracosta", "White Herb", "Solid Rock", "Adamant", ["Shell Smash", "Liquidation", "Stone Edge", "Aqua Jet"]),
    mon("Vanilluxe", "Icy Rock", "Snow Warning", "Modest", ["Blizzard", "Freeze Dry", "Flash Cannon", "Explosion"]),
    mon("Archeops", "Choice Scarf", "Defeatist", "Adamant", ["Head Smash", "Dragon Claw", "Earthquake", "U Turn"]),
    mon("Klinklang", "Leftovers", "Clear Body", "Adamant", ["Shift Gear", "Gear Grind", "Wild Charge", "Substitute"]),
    mon("Zekrom", "Life Orb", "Teravolt", "Adamant", ["Bolt Strike", "Outrage", "Dragon Dance", "Crunch"]),
]
#   Cyrus (Mahogany Town): his Platinum team, Sneasler and Mega Houndoom.
POST_CYRUS = [
    mon("Crobat", "Black Sludge", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Taunt"]),
    mon("Honchkrow", "Life Orb", "Moxie", "Adamant", ["Brave Bird", "Sucker Punch", "Night Slash", "Heat Wave"]),
    mon("Gyarados", "Lum Berry", "Intimidate", "Jolly", ["Waterfall", "Bounce", "Earthquake", "Dragon Dance"]),
    mon("Weavile", "Razor Claw", "Pressure", "Jolly", ["Knock Off", "Triple Axel", "Ice Shard", "Swords Dance"]),
    mon("Sneasler", "Focus Sash", "Unburden", "Jolly", ["Dire Claw", "Close Combat", "Gunk Shot", "Swords Dance"]),
    mon("Houndoom", "Houndoominite", "Flash Fire", "Timid", ["Fire Blast", "Dark Pulse", "Sludge Bomb", "Nasty Plot"]),
]
#   Wallace (Cherrygrove City): Drizzle rain, Mega Swampert and his Milotic.
POST_WALLACE = [
    mon("Pelipper", "Damp Rock", "Drizzle", "Bold", ["Hurricane", "Scald", "U Turn", "Roost"]),
    mon("Ludicolo", "Life Orb", "Swift Swim", "Modest", ["Hydro Pump", "Giga Drain", "Ice Beam", "Rain Dance"]),
    mon("Starmie", "Choice Specs", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Thunderbolt", "Rapid Spin"]),
    mon("Whiscash", "Leftovers", "Hydration", "Adamant", ["Earthquake", "Waterfall", "Dragon Dance", "Stone Edge"]),
    mon("Swampert", "Swampertite", "Damp", "Adamant", ["Waterfall", "Earthquake", "Ice Punch", "Superpower"]),
    mon("Milotic", "Leftovers", "Competitive", "Bold", ["Scald", "Ice Beam", "Recover", "Dragon Tail"]),
]
#   Maxie (Fuchsia City): Drought sun and Mega Camerupt.
POST_MAXIE = [
    mon("Torkoal", "Heat Rock", "Drought", "Bold", ["Stealth Rock", "Lava Plume", "Rapid Spin", "Yawn"]),
    mon("Mightyena", "Choice Band", "Intimidate", "Jolly", ["Crunch", "Sucker Punch", "Play Rough", "Fire Fang"]),
    mon("Weezing", "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Fire Blast", "Will O Wisp", "Pain Split"]),
    mon("Arcanine", "Life Orb", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Wild Charge", "Morning Sun"]),
    mon("Blaziken", "Focus Sash", "Blaze", "Jolly", ["Flare Blitz", "Close Combat", "Stone Edge", "Swords Dance"]),
    mon("Camerupt", "Cameruptite", "Solid Rock", "Modest", ["Fire Blast", "Earth Power", "Ancient Power", "Flash Cannon"]),
]
#   Archie (Cerulean City): Drizzle rain and Mega Sharpedo.
POST_ARCHIE = [
    mon("Pelipper", "Damp Rock", "Drizzle", "Modest", ["Hurricane", "Hydro Pump", "Knock Off", "Roost"]),
    mon("Tentacruel", "Black Sludge", "Clear Body", "Timid", ["Scald", "Sludge Bomb", "Rapid Spin", "Toxic Spikes"]),
    mon("Muk", "Black Sludge", "Poison Touch", "Adamant", ["Gunk Shot", "Knock Off", "Drain Punch", "Shadow Sneak"]),
    mon("Crobat", "Life Orb", "Infiltrator", "Jolly", ["Brave Bird", "Poison Fang", "Super Fang", "Roost"]),
    mon("Crawdaunt", "Choice Band", "Adaptability", "Adamant", ["Crabhammer", "Knock Off", "Aqua Jet", "Close Combat"]),
    mon("Sharpedo", "Sharpedonite", "Speed Boost", "Adamant", ["Waterfall", "Crunch", "Close Combat", "Protect"]),
]
#   Wally (Pallet Town): his Omega Ruby team and Mega Gallade.
POST_WALLY = [
    mon("Altaria", "Leftovers", "Natural Cure", "Adamant", ["Dragon Dance", "Brave Bird", "Earthquake", "Roost"]),
    mon("Delcatty", "Silk Scarf", "Wonder Skin", "Jolly", ["Fake Out", "Double Edge", "Sucker Punch", "Thunder Wave"]),
    mon("Roserade", "Focus Sash", "Natural Cure", "Timid", ["Leaf Storm", "Sludge Bomb", "Shadow Ball", "Sleep Powder"]),
    mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Body Press"]),
    mon("Flygon", "Choice Scarf", "Levitate", "Jolly", ["Earthquake", "Dragon Claw", "U Turn", "Fire Punch"]),
    mon("Gallade", "Galladite", "Sharpness", "Jolly", ["Close Combat", "Psycho Cut", "Leaf Blade", "Swords Dance"]),
]
# Trainer -> (stage, bag items, Pokemon)
SIDE_BATTLES = {
    "TRAINER_SIDE_CANDICE_HNS": (0, "", SIDE_CANDICE),
    "TRAINER_SIDE_GARDENIA_HNS": (2, "Potion", SIDE_GARDENIA),
    "TRAINER_SIDE_GARDENIA_2_HNS": (4, "Hyper Potion / Hyper Potion", SIDE_GARDENIA_2),
    "TRAINER_SIDE_FANTINA_HNS": (3, "Hyper Potion / Hyper Potion", SIDE_FANTINA),
    "TRAINER_SIDE_MAYLENE_HNS": (4, "Hyper Potion / Hyper Potion", SIDE_MAYLENE),
    "TRAINER_SIDE_WAKE_HNS": (5, "Full Restore / Full Restore", SIDE_WAKE),
    "TRAINER_SIDE_BYRON_HNS": (6, "Full Restore / Full Restore", SIDE_BYRON),
    "TRAINER_SIDE_ROARK_HNS": (7, "Full Restore / Full Restore", SIDE_ROARK),
    "TRAINER_SIDE_VOLKNER_HNS": (8, "Full Restore / Full Restore", SIDE_VOLKNER),
    "TRAINER_SIDE_KATY_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_KATY),
    "TRAINER_SIDE_BRASSIUS_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_BRASSIUS),
    "TRAINER_SIDE_IONO_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_IONO),
    "TRAINER_SIDE_KOFU_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_KOFU),
    "TRAINER_SIDE_LARRY_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_LARRY),
    "TRAINER_SIDE_RYME_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_RYME),
    "TRAINER_SIDE_TULIP_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_TULIP),
    "TRAINER_SIDE_GRUSHA_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SIDE_GRUSHA),
    "TRAINER_SIDE_CYNTHIA_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_CYNTHIA),
    "TRAINER_SIDE_IRIS_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_IRIS),
    "TRAINER_SIDE_GEETA_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_GEETA),
    "TRAINER_SIDE_N_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_N),
    "TRAINER_SIDE_CYRUS_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_CYRUS),
    "TRAINER_SIDE_WALLACE_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_WALLACE),
    "TRAINER_SIDE_MAXIE_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_MAXIE),
    "TRAINER_SIDE_ARCHIE_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_ARCHIE),
    "TRAINER_SIDE_WALLY_HNS": (KANTO_CHAMPION, POST_ITEMS, POST_WALLY),
}

# --- Rival (Silver): TRAINER_RIVAL_<his starter>_<n>_HNS ------------------------------------------
# 2nd battle: Azalea Town after Bugsy (2 badges, cap 33). 3rd: Burned Tower (3 badges, cap 42).
RIVAL_STARTER = {
    2: {"CYNDAQUIL": mon("Quilava", "Charcoal", "Flash Fire", "Timid", ["Eruption", "Flamethrower", "Extrasensory", "Hidden Power"],
                         "252 SpA", ivs="30 HP / 0 Atk / 31 Def / 30 SpA / 31 SpD / 31 Spe"),
        "TOTODILE": mon("Croconaw", "Mystic Water", "Strong Jaw", "Adamant", ["Liquidation", "Crunch", "Ice Fang", "Aqua Jet"],
                        "252 Atk"),
        "CHIKORITA": mon("Bayleef", "Leftovers", "Overgrow", "Bold", ["Giga Drain", "Earth Power", "Leech Seed", "Synthesis"],
                         "252 HP", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe")},
    3: {"CYNDAQUIL": mon("Typhlosion", "Charcoal", "Flash Fire", "Timid", ["Eruption", "Flamethrower", "Shadow Ball", "Scorching Sands"],
                         "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        "TOTODILE": mon("Feraligatr", "Mystic Water", "Strong Jaw", "Adamant", ["Dragon Dance", "Liquidation", "Crunch", "Ice Fang"],
                        "4 HP / 252 Atk / 252 Spe"),
        "CHIKORITA": mon("Meganium", "Leftovers", "Triage", "Bold", ["Giga Drain", "Body Press", "Leech Seed", "Synthesis"],
                         "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe")},
}
RIVAL_TEAM = {
    2: [mon("Pupitar", "Focus Sash", "Shed Skin", "Adamant", ["Stealth Rock", "Rock Slide", "Earthquake", "Taunt"]),
        mon("Golbat", "Eviolite", "Infiltrator", "Impish", ["Brave Bird", "U Turn", "Roost", "Toxic"]),
        mon("Weavile", "Never Melt Ice", "Infiltrator", "Jolly", ["Knock Off", "Ice Spinner", "Ice Shard", "Low Kick"]),
        mon("Gengar", "Black Sludge", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Will O Wisp"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Magnezone", "Leftovers", "Analytic", "Modest", ["Flash Cannon", "Thunderbolt", "Volt Switch", "Thunder Wave"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe")],
    3: [mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Stealth Rock", "Stone Edge", "Earthquake", "Dragon Dance"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Taunt"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Weavile", "Life Orb", "Infiltrator", "Jolly", ["Knock Off", "Icicle Crash", "Ice Shard", "Low Kick"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Gengar", "Focus Sash", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Dazzling Gleam", "Destiny Bond"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Absol", "Absolite", "Pressure", "Jolly", ["Swords Dance", "Knock Off", "Sucker Punch", "Play Rough"],
            "4 HP / 252 Atk / 252 Spe")],
}

# --- Team Rocket: Proton in Slowpoke Well (1 badge, cap 24) -----------------------------------------
PROTON_1 = [
    mon("Koffing", "Eviolite", "Levitate", "Bold", ["Toxic Spikes", "Will O Wisp", "Sludge Bomb", "Pain Split"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Golbat", "Sharp Beak", "Infiltrator", "Jolly", ["Cross Poison", "Wing Attack", "U Turn", "Taunt"]),
    mon("Slowpoke", "Sitrus Berry", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Teleport"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Grimer Alola", "Eviolite", "Poison Touch", "Adamant", ["Knock Off", "Poison Jab", "Shadow Sneak", "Curse"]),
    mon("Raticate", "Flame Orb", "Guts", "Jolly", ["Facade", "Sucker Punch", "Super Fang", "U Turn"]),
    mon("Houndoom", "Charcoal", "Flash Fire", "Timid", ["Nasty Plot", "Flamethrower", "Dark Pulse", "Sludge Bomb"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]

# --- Team Rocket: Rocket Hideout (4 badges at the earliest: the Lake of Rage needs Surf; cap 50) ------
PETREL_1 = [
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Gyro Ball", "Earthquake", "Volt Switch"],
        "252 HP / 4 Atk / 252 Def", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Weezing", "Black Sludge", "Levitate", "Bold", ["Toxic Spikes", "Sludge Bomb", "Flamethrower", "Pain Split"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Golbat", "Eviolite", "Infiltrator", "Impish", ["Brave Bird", "U Turn", "Taunt", "Roost"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Zoroark", "Life Orb", "Illusion", "Timid", ["Nasty Plot", "Dark Pulse", "Flamethrower", "Sucker Punch"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Drapion", "Scope Lens", "Sniper", "Jolly", ["Night Slash", "Cross Poison", "Earthquake", "Ice Fang"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Sableye", "Sablenite", "Frisk", "Careful", ["Will O Wisp", "Recover", "Foul Play", "Taunt"],
        "252 HP / 4 Def / 252 SpD"),
]
ARIANA_1 = [
    mon("Persian Alola", "Sitrus Berry", "Fur Coat", "Jolly", ["Fake Out", "Icy Wind", "Parting Shot", "Foul Play"],
        "252 HP / 4 Atk / 252 Spe"),
    mon("Arbok", "Black Sludge", "Intimidate", "Adamant", ["Glare", "Gunk Shot", "Rock Slide", "Sucker Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Kangaskhan", "Kangaskhanite", "Inner Focus", "Jolly", ["Fake Out", "Double Edge", "Ice Punch", "Power Up Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]

# --- Eusine in Cianwood (4 badges at the earliest: cap 50) --------------------------------------------
# Heart & Soul's Politoed, Hypno and Electrode had 2 IVs and the basic AI. Since 0.8.0 a rain team
# of six around them: Drizzle Politoed, Thunder from Electrode and Lanturn.
EUSINE = [
    mon("Politoed", "Damp Rock", "Drizzle", "Bold", ["Hydro Pump", "Ice Beam", "Encore", "Hypnosis"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Electrode", "Focus Sash", "Galvanize", "Timid", ["Thunder", "Volt Switch", "Foul Play", "Explosion"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Hypno", "Leftovers", "Insomnia", "Calm", ["Nasty Plot", "Psychic", "Focus Blast", "Thunder Wave"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Gengar", "Black Sludge", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Shadow Sneak", "Destiny Bond"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Starmie", "Life Orb", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Thunder", "Rapid Spin"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Manectric", "Manectite", "Static", "Timid", ["Thunder", "Volt Switch", "Hidden Power", "Snarl"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 30 Def / 31 SpA / 31 SpD / 31 Spe"),
]

# --- Team Rocket: Radio Tower (7 badges, cap 75) ----------------------------------------------------
PROTON_2 = [
    mon("Rhydon", "Eviolite", "Lightning Rod", "Adamant", ["Stealth Rock", "Stone Edge", "Earthquake", "Megahorn"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Weezing", "Rocky Helmet", "Levitate", "Bold", ["Toxic Spikes", "Will O Wisp", "Sludge Bomb", "Fire Blast"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Muk", "Assault Vest", "Poison Touch", "Adamant", ["Gunk Shot", "Knock Off", "Shadow Sneak", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Nidoking", "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Thunderbolt"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Toxicroak", "Black Sludge", "Dry Skin", "Jolly", ["Bulk Up", "Drain Punch", "Gunk Shot", "Sucker Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Dazzling Gleam", "Destiny Bond"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
PETREL_2 = [
    mon("Forretress", "Rocky Helmet", "Sturdy", "Relaxed", ["Spikes", "Iron Head", "Volt Switch", "Rapid Spin"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Weezing Galar", "Black Sludge", "Neutralizing Gas", "Bold", ["Strange Steam", "Will O Wisp", "Pain Split", "Fire Blast"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Toxapex", "Leftovers", "Regenerator", "Calm", ["Toxic Spikes", "Scald", "Recover", "Haze"],
        "252 HP / 4 Def / 252 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Zoroark", "Focus Sash", "Illusion", "Timid", ["Nasty Plot", "Night Daze", "Sludge Bomb", "Sucker Punch"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Drapion", "Black Glasses", "Battle Armor", "Jolly", ["Swords Dance", "Knock Off", "Poison Jab", "Aqua Tail"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Sableye", "Sablenite", "Frisk", "Impish", ["Will O Wisp", "Recover", "Knock Off", "Parting Shot"],
        "252 HP / 252 Def / 4 SpD"),
]
ARIANA_2 = [
    mon("Persian Alola", "Focus Sash", "Fur Coat", "Jolly", ["Fake Out", "Foul Play", "Parting Shot", "Taunt"],
        "252 HP / 4 Atk / 252 Spe"),
    mon("Arbok", "Black Sludge", "Intimidate", "Jolly", ["Glare", "Gunk Shot", "Sucker Punch", "Earthquake"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Skuntank", "Assault Vest", "Aftermath", "Adamant", ["Crunch", "Gunk Shot", "Sucker Punch", "Temper Flare"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Gyarados", "Leftovers", "Intimidate", "Jolly", ["Dragon Dance", "Waterfall", "Earthquake", "Power Whip"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Honchkrow", "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Kangaskhan", "Kangaskhanite", "Inner Focus", "Adamant", ["Double Edge", "Earthquake", "Drain Punch", "Ice Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]
ARCHER = [
    mon("Kingambit", "Leftovers", "Supreme Overlord", "Adamant", ["Stealth Rock", "Kowtow Cleave", "Sucker Punch", "Iron Head"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Tauros", "Choice Band", "Intimidate", "Jolly", ["Double Edge", "Close Combat", "Earthquake", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Porygon Z", "Choice Scarf", "Adaptability", "Timid", ["Tri Attack", "Ice Beam", "Thunderbolt", "Dark Pulse"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Crawdaunt", "Life Orb", "Adaptability", "Adamant", ["Dragon Dance", "Crabhammer", "Knock Off", "Aqua Jet"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Slowbro", "Heavy Duty Boots", "Regenerator", "Relaxed", ["Scald", "Psyshock", "Slack Off", "Teleport"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Houndoom", "Houndoominite", "Flash Fire", "Timid", ["Nasty Plot", "Dark Pulse", "Heat Wave", "Sludge Bomb"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]

# --- Rival: Goldenrod Underground (7 badges, cap 75) and Victory Road (8 badges, cap 85) -------------
RIVAL_STARTER[4] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Extrasensory", "Scorching Sands"],
                     "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    "TOTODILE": mon("Feraligatr", "Life Orb", "Sheer Force", "Adamant", ["Dragon Dance", "Liquidation", "Ice Punch", "Earthquake"],
                    "4 HP / 252 Atk / 252 Spe"),
    "CHIKORITA": mon("Meganium", "Leftovers", "Triage", "Calm", ["Giga Drain", "Leech Seed", "Dragon Tail", "Synthesis"],
                     "252 HP / 4 Def / 252 SpD"),
}
RIVAL_STARTER[5] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Specs", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Shadow Ball", "Extrasensory"],
                     "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    "TOTODILE": mon("Feraligatr", "Mystic Water", "Sheer Force", "Adamant", ["Swords Dance", "Liquidation", "Crunch", "Aqua Jet"],
                    "252 HP / 252 Atk / 4 SpD"),
    "CHIKORITA": mon("Meganium", "Rocky Helmet", "Triage", "Bold", ["Body Press", "Giga Drain", "Knock Off", "Synthesis"],
                     "252 HP / 252 Def / 4 SpD"),
}
RIVAL_TEAM[4] = [
    mon("Crobat", "Black Sludge", "Infiltrator", "Jolly", ["Brave Bird", "U Turn", "Super Fang", "Roost"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Weavile", "Choice Band", "Infiltrator", "Jolly", ["Knock Off", "Triple Axel", "Ice Shard", "Low Kick"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Alakazam", "Life Orb", "Magic Guard", "Timid", ["Nasty Plot", "Psychic", "Shadow Ball", "Dazzling Gleam"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Gengar", "Choice Specs", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Energy Ball", "Thunderbolt"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Jolly", ["Dragon Dance", "Stone Edge", "Crunch", "Fire Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]
RIVAL_TEAM[5] = [
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Adamant", ["Stealth Rock", "Stone Edge", "Knock Off", "Earthquake"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Crobat", "Heavy Duty Boots", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Weavile", "Life Orb", "Infiltrator", "Jolly", ["Swords Dance", "Throat Chop", "Triple Axel", "Ice Shard"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gengar", "Black Sludge", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Energy Ball", "Destiny Bond"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Ursaluna", "Flame Orb", "Guts", "Adamant", ["Bulk Up", "Facade", "Headlong Rush", "Crunch"],
        "252 HP / 252 Atk / 4 SpD"),
]

# --- Kimono Girls: Ecruteak Dance Theater, one after another (8 badges, cap 85) ----------------------
KIMONO = {
    "TRAINER_ZUKI_HNS": [mon("Umbreon", "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Moonlight", "Protect", "Toxic"])],
    "TRAINER_NAOKO_HNS": [mon("Espeon", "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"])],
    "TRAINER_MIKI_HNS": [mon("Flareon", "Toxic Orb", "Toxic Boost", "Adamant", ["Flare Blitz", "Facade", "Superpower", "Quick Attack"])],
    "TRAINER_SAYO_HNS": [mon("Jolteon", "Choice Specs", "Volt Absorb", "Timid", ["Thunderbolt", "Shadow Ball", "Volt Switch", "Hyper Voice"])],
    "TRAINER_KUNI_HNS": [mon("Vaporeon", "Leftovers", "Water Absorb", "Bold", ["Scald", "Ice Beam", "Wish", "Protect"])],
}

# --- Elite Four and Lance (8 badges, cap 85) -----------------------------------------------------------
WILL = [
    mon("Xatu", "Light Clay", "Magic Bounce", "Timid", ["Reflect", "Light Screen", "U-turn", "Psychic"],
        "252 HP / 4 Def / 252 Spe"),
    mon("Bronzong", "Mental Herb", "Levitate", "Relaxed", ["Trick Room", "Stealth Rock", "Gyro Ball", "Earthquake"],
        "252 HP / 252 Atk / 4 Def", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Exeggutor", "Sitrus Berry", "Harvest", "Quiet", ["Trick Room", "Leaf Storm", "Psychic", "Sludge Bomb"],
        "252 HP / 252 SpA / 4 Def", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Cresselia", "Leftovers", "Levitate", "Relaxed", ["Calm Mind", "Moonlight", "Psyshock", "Ice Beam"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Farigiraf", "Life Orb", "Armor Tail", "Quiet", ["Trick Room", "Hyper Voice", "Psychic", "Sucker Punch"],
        "252 HP / 252 SpA / 4 Def", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
    mon("Slowbro", "Slowbronite", "Own Tempo", "Quiet", ["Scald", "Psyshock", "Fire Blast", "Slack Off"],
        "252 HP / 252 SpA / 4 Def", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
]
KOGA = [
    mon("Crobat", "Black Sludge", "Infiltrator", "Jolly", ["Brave Bird", "Super Fang", "U Turn", "Taunt"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Toxapex", "Rocky Helmet", "Regenerator", "Bold", ["Toxic Spikes", "Scald", "Recover", "Haze"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Muk Alola", "Assault Vest", "Poison Touch", "Adamant", ["Knock Off", "Poison Jab", "Ice Punch", "Shadow Sneak"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Venomoth", "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sludge Bomb", "Roost"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Munkidori", "Choice Specs", "Toxic Chain", "Timid", ["Sludge Bomb", "Psyshock", "Focus Blast", "U Turn"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Beedrill", "Beedrillite", "Sniper", "Jolly", ["Swords Dance", "Poison Jab", "U Turn", "Drill Run"],
        "4 HP / 252 Atk / 252 Spe"),
]
BRUNO = [
    mon("Hitmontop", "Rocky Helmet", "Intimidate", "Impish", ["Fake Out", "Close Combat", "Sucker Punch", "Rapid Spin"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Steelix", "Leftovers", "Sturdy", "Impish", ["Stealth Rock", "Heavy Slam", "Earthquake", "Stone Edge"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Conkeldurr", "Flame Orb", "Guts", "Adamant", ["Facade", "Drain Punch", "Mach Punch", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Lucario", "Life Orb", "Justified", "Jolly", ["Swords Dance", "Close Combat", "Meteor Mash", "Bullet Punch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Terrakion", "Choice Scarf", "Justified", "Jolly", ["Close Combat", "Stone Edge", "Earthquake", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Machamp", "Machampite", "No Guard", "Adamant", ["Close Combat", "Ice Punch", "Thunder Punch", "Bullet Punch"],
        "252 HP / 252 Atk / 4 SpD"),
]
KAREN = [
    mon("Umbreon", "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Wish", "Protect", "Toxic"],
        "252 HP / 4 Def / 252 SpD"),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Bold", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Leech Seed"],
        "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Honchkrow", "Choice Band", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gengar", "Focus Sash", "Levitate", "Timid", ["Nasty Plot", "Shadow Ball", "Sludge Bomb", "Focus Blast"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Darkrai", "Life Orb", "Bad Dreams", "Timid", ["Nasty Plot", "Dark Pulse", "Sludge Bomb", "Focus Blast"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Houndoom", "Houndoominite", "Flash Fire", "Timid", ["Nasty Plot", "Dark Pulse", "Flamethrower", "Sludge Bomb"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
# Lance leads Mega Gyarados (tools/emurun/tests/mega_evolution.emu checks it Mega Evolves on turn 1)
# One Dragon Dance sweeper (Dragonite): with Mega Gyarados and Salamence also setting up, the
# prepared six of the bosses_m4 play test lost all of six tries. Charizard attacks instead of
# Roosting: with the Full Restores it outlasted every team built for Lance in the play tests.
LANCE = [
    mon("Gyarados", "Gyaradosite", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Thunder Wave"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Aerodactyl", "Focus Sash", "Unnerve", "Jolly", ["Stealth Rock", "Stone Edge", "Dual Wingbeat", "Taunt"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Charizard", "Heavy-Duty Boots", "Blaze", "Timid", ["Fire Blast", "Air Slash", "Dragon Pulse", "Scorching Sands"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Raging Bolt", "Booster Energy", "Protosynthesis", "Modest", ["Thunderclap", "Draco Meteor", "Thunderbolt", "Calm Mind"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Latios", "Soul Dew", "Levitate", "Timid", ["Draco Meteor", "Luster Purge", "Aura Sphere", "Recover"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Dragonite", "Lum Berry", "Multiscale", "Adamant", ["Dragon Dance", "Extreme Speed", "Earthquake", "Outrage"],
        "4 HP / 252 Atk / 252 Spe"),
]

# --- Kanto Gym Leaders and Blue (after the Johto League: cap 90, any order) ------------------------
BROCK = [
    mon("Gigalith", "Smooth Rock", "Sand Stream", "Adamant", ["Stealth Rock", "Rock Slide", "Earthquake", "Explosion"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Omastar", "White Herb", "Weak Armor", "Modest", ["Shell Smash", "Surf", "Ice Beam", "Earth Power"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Kabutops", "Life Orb", "Sharpness", "Jolly", ["Razor Shell", "Stone Edge", "X-Scissor", "Aqua Jet"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Golem", "Weakness Policy", "Sturdy", "Adamant", ["Earthquake", "Stone Edge", "Sucker Punch", "Rock Polish"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Lycanroc-Midday", "Focus Sash", "Sand Rush", "Jolly", ["Accelerock", "Rock Slide", "Close Combat", "Psychic Fangs"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Aerodactyl", "Aerodactylite", "Unnerve", "Jolly", ["Dragon Dance", "Stone Edge", "Dual Wingbeat", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
]
MISTY = [
    mon("Pelipper", "Damp Rock", "Drizzle", "Bold", ["Scald", "Hurricane", "U Turn", "Roost"]),
    mon("Golduck", "Life Orb", "Swift Swim", "Timid", ["Hydro Pump", "Ice Beam", "Psychic", "Nasty Plot"]),
    mon("Lapras", "Leftovers", "Water Absorb", "Modest", ["Freeze Dry", "Hydro Pump", "Thunderbolt", "Ice Shard"]),
    mon("Milotic", "Leftovers", "Competitive", "Bold", ["Scald", "Ice Beam", "Recover", "Haze"]),
    mon("Blastoise", "Blastoisinite", "Torrent", "Modest", ["Water Pulse", "Aura Sphere", "Dark Pulse", "Ice Beam"]),
    mon("Starmie", "Wise Glasses", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Thunderbolt", "Ice Beam"]),
]
LT_SURGE = [
    mon("Electrode", "Focus Sash", "Galvanize", "Timid", ["Thunderbolt", "Volt Switch", "Taunt", "Explosion"]),
    mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Body Press"]),
    mon("Lanturn", "Leftovers", "Volt Absorb", "Bold", ["Scald", "Discharge", "Ice Beam", "Heal Bell"]),
    mon("Electivire", "Life Orb", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Earthquake", "Cross Chop"]),
    mon("Manectric", "Manectite", "Lightning Rod", "Timid", ["Thunderbolt", "Overheat", "Snarl", "Volt Switch"]),
    mon("Raichu", "Magnet", "Lightning Rod", "Timid", ["Thunderbolt", "Focus Blast", "Nasty Plot", "Grass Knot"]),
]
ERIKA = [
    mon("Whimsicott", "Heat Rock", "Prankster", "Timid", ["Sunny Day", "Encore", "Moonblast", "U-turn"],
        "252 HP / 4 Def / 252 Spe"),
    mon("Jumpluff", "Flying Gem", "Chlorophyll", "Jolly", ["Sleep Powder", "Leech Seed", "Acrobatics", "Strength Sap"],
        "252 HP / 4 Atk / 252 Spe"),
    mon("Victreebel", "Life Orb", "Chlorophyll", "Adamant", ["Swords Dance", "Power Whip", "Sucker Punch", "Poison Jab"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Tangrowth", "Assault Vest", "Regenerator", "Sassy", ["Power Whip", "Knock Off", "Earthquake", "Sludge Bomb"],
        "252 HP / 4 SpA / 252 SpD"),
    mon("Bellossom", "Sitrus Berry", "Chlorophyll", "Modest", ["Quiver Dance", "Solar Beam", "Moonblast", "Strength Sap"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Venusaur", "Venusaurite", "Chlorophyll", "Modest", ["Growth", "Giga Drain", "Sludge Bomb", "Weather Ball"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
JANINE = [
    mon("Weezing", "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
    mon("Nidoqueen", "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    mon("Muk", "Leftovers", "Poison Touch", "Adamant", ["Gunk Shot", "Knock Off", "Shadow Sneak", "Curse"]),
    mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Venomoth", "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sludge Bomb", "Sleep Powder"]),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Focus Blast", "Nasty Plot"]),
]
SABRINA = [
    mon("Mr Mime", "Light Clay", "Filter", "Timid", ["Light Screen", "Reflect", "Psychic", "Dazzling Gleam"]),
    mon("Wobbuffet", "Sitrus Berry", "Shadow Tag", "Bold", ["Counter", "Mirror Coat", "Encore", "Destiny Bond"]),
    mon("Slowbro", "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Thunder Wave"]),
    mon("Espeon", "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"]),
    mon("Alakazam", "Twisted Spoon", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Calm Mind"]),
    mon("Metagross", "Metagrossite", "Clear Body", "Jolly", ["Meteor Mash", "Zen Headbutt", "Earthquake", "Bullet Punch"]),
]
BLAINE = [
    mon("Torkoal", "Heat Rock", "Drought", "Bold", ["Stealth Rock", "Lava Plume", "Earth Power", "Yawn"],
        "252 HP / 4 SpA / 252 Def", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Rapidash", "Life Orb", "Flash Fire", "Jolly", ["Flare Blitz", "Wild Charge", "High Horsepower", "Morning Sun"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Magmortar", "Expert Belt", "Flame Body", "Modest", ["Fire Blast", "Thunderbolt", "Solar Beam", "Psychic"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Volcarona", "Charcoal", "Flame Body", "Timid", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Arcanine-Hisui", "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Flare Blitz", "Extreme Speed", "Wild Charge"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Camerupt", "Cameruptite", "Solid Rock", "Modest", ["Fire Blast", "Earth Power", "Solar Beam", "Will-O-Wisp"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
]
# Machamp has Close Combat, not No Guard Dynamic Punch: with the guaranteed confusion, Blue beat
# every play-test team in all six tries (Bruno's Machamp likewise).
BLUE = [
    mon("Rhyperior", "Rocky Helmet", "Solid Rock", "Adamant", ["Stealth Rock", "Stone Edge", "Earthquake", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Exeggutor", "Sitrus Berry", "Harvest", "Modest", ["Leaf Storm", "Psychic", "Sludge Bomb", "Sleep Powder"],
        "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Gyarados", "Lum Berry", "Moxie", "Jolly", ["Dragon Dance", "Waterfall", "Earthquake", "Stone Edge"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Arcanine", "Life Orb", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Close Combat", "Psychic Fangs"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Machamp", "Assault Vest", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Pidgeot", "Pidgeotite", "Frisk", "Timid", ["Hurricane", "Heat Wave", "U-turn", "Roost"],
        "4 HP / 252 SpA / 252 Spe"),
]

# --- Route mini-bosses (DECISIONS.md D30) -----------------------------------------------------------
# Strong trainers on the routes, as in Emerald Imperium: one existing trainer on most routes (none
# with phone rematches or double battles) gets a competitive team at the level cap, themed by the
# trainer's class. The stage is the earliest point the route can be reached, so a mini-boss is
# never above the player's cap and is raised to it when met later. 3 Pokemon before the first
# badge, 4 to 5 in mid-Johto, 6 from Route 45 on and in Kanto.
ROUTE_BOSSES = {
    # Route 30, Youngster Mikey: a Guts Rattata with a Flame Orb
    "TRAINER_MIKEY_HNS": (0, [
        mon("Pichu", "Eviolite", "Static", "Hasty", ["Fake Out", "Nuzzle", "Volt Switch", "Grass Knot"],
            raised_item="Focus Sash"),
        mon("Furret", "Sitrus Berry", "Adaptability", "Jolly", ["Body Slam", "U Turn", "Quick Attack", "Knock Off"]),
        mon("Rattata", "Flame Orb", "Guts", "Jolly", ["Facade", "Quick Attack", "Bite", "Sucker Punch"]),
    ]),
    # Route 32, Camper Roland
    "TRAINER_ROLAND_HNS": (0, [
        mon("Geodude", "Eviolite", "Sturdy", "Adamant", ["Stealth Rock", "Rock Tomb", "Bulldoze", "Explosion"],
            raised_item="Rocky Helmet"),
        mon("Flaaffy", "Eviolite", "Static", "Modest", ["Thunder Wave", "Volt Switch", "Discharge", "Power Gem"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe", raised_item="Leftovers"),
        mon("Bellsprout", "Salac Berry", "Gluttony", "Adamant", ["Sleep Powder", "Bullet Seed", "Poison Jab", "Sucker Punch"]),
    ]),
    # Route 34, Cooltrainer Kate
    "TRAINER_KATE_HNS": (1, [
        mon("Granbull", "Sitrus Berry", "Intimidate", "Adamant", ["Play Rough", "Crunch", "Thunder Wave", "Roar"]),
        mon("Shellder", "Eviolite", "Skill Link", "Adamant", ["Shell Smash", "Icicle Spear", "Rock Blast", "Liquidation"],
            raised_item="White Herb"),
        mon("Growlithe", "Charcoal", "Flash Fire", "Adamant", ["Fire Fang", "Wild Charge", "Crunch", "Will O Wisp"]),
        mon("Kadabra", "Eviolite", "Magic Guard", "Timid", ["Psyshock", "Dazzling Gleam", "Calm Mind", "Recover"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe", raised_item="Life Orb"),
    ]),
    # Route 35, Bird Keeper Bryan: a Leek Farfetch'd for critical hits
    "TRAINER_BRYAN_HNS": (1, [
        mon("Swablu", "Eviolite", "Natural Cure", "Calm", ["Toxic", "Roost", "Dragon Pulse", "Air Cutter"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe", raised_item="Leftovers"),
        mon("Farfetchd", "Leek", "Sharpness", "Jolly", ["Swords Dance", "Leaf Blade", "Night Slash", "Aerial Ace"]),
        mon("Fearow", "Sharp Beak", "Technician", "Jolly", ["Pluck", "Quick Attack", "Drill Run", "U Turn"]),
        mon("Noctowl", "Sitrus Berry", "Tinted Lens", "Modest", ["Air Slash", "Extrasensory", "Calm Mind", "Roost"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    ]),
    # Route 37, Psychic Greg
    "TRAINER_GREG_HNS": (2, [
        mon("Xatu", "Light Clay", "Magic Bounce", "Timid", ["Reflect", "Light Screen", "Air Slash", "U Turn"]),
        mon("Gallade", "Focus Sash", "Sharpness", "Adamant", ["Swords Dance", "Psycho Cut", "Sacred Sword", "Night Slash"]),
        mon("Grumpig", "Leftovers", "Thick Fat", "Modest", ["Psychic", "Shadow Ball", "Power Gem", "Calm Mind"],
            ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Espeon", "Twisted Spoon", "Magic Bounce", "Timid", ["Calm Mind", "Psychic", "Dazzling Gleam", "Shadow Ball"],
            "252 SpA", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    ]),
    # Route 38, Beauty Valerie: Fairy types
    "TRAINER_VALERIE_HNS": (2, [
        mon("Togetic", "Eviolite", "Serene Grace", "Calm", ["Air Slash", "Dazzling Gleam", "Thunder Wave", "Roost"]),
        mon("Granbull", "Sitrus Berry", "Intimidate", "Adamant", ["Play Rough", "Crunch", "Thunder Wave", "Bulk Up"]),
        mon("Azumarill", "Choice Band", "Thick Fat", "Adamant", ["Play Rough", "Aqua Tail", "Aqua Jet", "Superpower"]),
        mon("Clefable", "Leftovers", "Magic Guard", "Bold", ["Moonblast", "Thunder Wave", "Soft Boiled", "Calm Mind"]),
    ]),
    # Route 39, Sailor Eugene
    "TRAINER_EUGENE_HNS": (2, [
        mon("Tentacruel", "Black Sludge", "Liquid Ooze", "Calm", ["Toxic Spikes", "Scald", "Sludge Bomb", "Knock Off"]),
        mon("Poliwrath", "Leftovers", "Water Absorb", "Adamant", ["Bulk Up", "Waterfall", "Drain Punch", "Rock Slide"]),
        mon("Machamp", "Expert Belt", "No Guard", "Adamant", ["Dynamic Punch", "Stone Edge", "Knock Off", "Bullet Punch"]),
        mon("Kingler", "Life Orb", "Sheer Force", "Adamant", ["Swords Dance", "Liquidation", "Rock Slide", "Knock Off"],
            "252 Atk"),
    ]),
    # Route 40, Swimmer Simon: rain
    "TRAINER_SIMON_HNS": (3, [
        mon("Pelipper", "Damp Rock", "Drizzle", "Bold", ["Scald", "Hurricane", "U Turn", "Roost"]),
        mon("Floatzel", "Life Orb", "Water Veil", "Adamant", ["Waterfall", "Aqua Jet", "Crunch", "Bulk Up"]),
        mon("Seaking", "Mystic Water", "Lightning Rod", "Adamant", ["Waterfall", "Megahorn", "Drill Run", "Agility"]),
        mon("Golduck", "Wise Glasses", "Swift Swim", "Modest", ["Hydro Pump", "Ice Beam", "Psychic", "Calm Mind"]),
        mon("Quagsire", "Leftovers", "Unaware", "Impish", ["Earthquake", "Waterfall", "Recover", "Toxic"]),
    ]),
    # Route 41, Swimmer George
    "TRAINER_GEORGE_HNS": (3, [
        mon("Mantine", "Leftovers", "Swift Swim", "Timid", ["Hurricane", "Scald", "Roost", "Haze"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Barraskewda", "Life Orb", "Swift Swim", "Jolly", ["Liquidation", "Close Combat", "Psychic Fangs", "Aqua Jet"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Lanturn", "Assault Vest", "Volt Absorb", "Timid", ["Thunder", "Scald", "Ice Beam", "Volt Switch"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Starmie", "Expert Belt", "Analytic", "Timid", ["Hydro Pump", "Psyshock", "Ice Beam", "Recover"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Kingdra", "Choice Specs", "Swift Swim", "Timid", ["Hydro Pump", "Draco Meteor", "Hurricane", "Flip Turn"],
            "4 HP / 252 SpA / 252 Spe"),
    ]),
    # Route 42, Hiker Benjamin
    "TRAINER_BENJAMIN_HNS": (3, [
        mon("Hippowdon", "Smooth Rock", "Sand Stream", "Impish", ["Stealth Rock", "Earthquake", "Slack Off", "Whirlwind"],
            "252 HP / 252 Def / 4 SpD"),
        mon("Excadrill", "Life Orb", "Sand Rush", "Jolly", ["Swords Dance", "Earthquake", "Iron Head", "Rapid Spin"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Rhydon", "Eviolite", "Lightning Rod", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Roar"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Steelix", "Leftovers", "Sturdy", "Impish", ["Curse", "Heavy Slam", "Earthquake", "Rock Slide"],
            "252 HP / 252 Def / 4 SpD"),
        mon("Sudowoodo", "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Wood Hammer", "Sucker Punch", "Earthquake"],
            "252 HP / 252 Atk / 4 SpD"),
    ]),
    # Route 43, Pokemaniac Ben: rare Pokemon
    "TRAINER_BEN_HNS": (3, [
        mon("Aerodactyl", "Focus Sash", "Rock Head", "Jolly", ["Stealth Rock", "Stone Edge", "Double Edge", "Earthquake"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Kangaskhan", "Silk Scarf", "Scrappy", "Jolly", ["Fake Out", "Double Edge", "Sucker Punch", "Earthquake"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Slowbro", "Leftovers", "Regenerator", "Bold", ["Scald", "Psychic", "Slack Off", "Thunder Wave"],
            "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Lickilicky", "Sitrus Berry", "Unaware", "Careful", ["Swords Dance", "Body Slam", "Knock Off", "Power Whip"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Dragonair", "Eviolite", "Marvel Scale", "Jolly", ["Dragon Dance", "Outrage", "Extreme Speed", "Waterfall"],
            "4 HP / 252 Atk / 252 Spe", raised_item="Lum Berry"),
    ]),
    # Route 47, Hiker Devin
    "TRAINER_DEVIN_HNS": (3, [
        mon("Golem", "Sitrus Berry", "Sturdy", "Adamant", ["Stealth Rock", "Earthquake", "Stone Edge", "Sucker Punch"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Gligar", "Eviolite", "Immunity", "Jolly", ["Earthquake", "Knock Off", "U Turn", "Roost"],
            "252 HP / 4 Atk / 252 Spe"),
        mon("Aggron", "Life Orb", "Rock Head", "Adamant", ["Head Smash", "Iron Head", "Earthquake", "Rock Polish"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Marowak", "Thick Club", "Rock Head", "Adamant", ["Bonemerang", "Double Edge", "Fire Punch", "Swords Dance"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Hariyama", "Flame Orb", "Guts", "Adamant", ["Close Combat", "Knock Off", "Bullet Punch", "Fake Out"],
            "252 HP / 252 Atk / 4 SpD"),
    ]),
    # Route 44, Cooltrainer Cybil: sun
    "TRAINER_CYBIL_HNS": (4, [
        mon("Ninetales", "Heat Rock", "Drought", "Timid", ["Flamethrower", "Solar Beam", "Nasty Plot", "Will O Wisp"]),
        mon("Jumpluff", "Leftovers", "Chlorophyll", "Jolly", ["Acrobatics", "Sleep Powder", "Leech Seed", "U Turn"]),
        mon("Butterfree", "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sleep Powder", "Air Slash"]),
        mon("Arcanine", "Choice Band", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Wild Charge", "Close Combat"]),
        mon("Bellossom", "Life Orb", "Chlorophyll", "Modest", ["Quiver Dance", "Giga Drain", "Moonblast", "Sludge Bomb"]),
    ]),
    # Route 26, Cooltrainer Jake (the road to the Indigo Plateau; with Surf it can be reached earlier)
    "TRAINER_JAKE_HNS": (4, [
        mon("Tangrowth", "Rocky Helmet", "Regenerator", "Relaxed", ["Giga Drain", "Knock Off", "Earthquake", "Sleep Powder"]),
        mon("Electivire", "Life Orb", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Cross Chop", "Earthquake"]),
        mon("Magmortar", "Expert Belt", "Flame Body", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Psychic"]),
        mon("Togekiss", "Leftovers", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Thunder Wave", "Roost"]),
        mon("Kingdra", "Choice Specs", "Sniper", "Modest", ["Draco Meteor", "Hydro Pump", "Ice Beam", "Flash Cannon"]),
        mon("Gyarados", "Sitrus Berry", "Intimidate", "Jolly", ["Waterfall", "Earthquake", "Dragon Dance", "Ice Fang"]),
    ]),
    # Route 27, Cooltrainer Blake
    "TRAINER_BLAKE_HNS": (4, [
        mon("Scizor", "Choice Band", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Superpower"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Starmie", "Expert Belt", "Analytic", "Timid", ["Hydro Pump", "Psyshock", "Thunderbolt", "Rapid Spin"],
            "4 HP / 252 SpA / 252 Spe"),
        mon("Ampharos", "Leftovers", "Static", "Modest", ["Thunderbolt", "Dragon Pulse", "Hidden Power", "Volt Switch"],
            "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 30 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Houndoom", "Life Orb", "Flash Fire", "Timid", ["Nasty Plot", "Dark Pulse", "Fire Blast", "Sludge Bomb"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Heracross", "Choice Scarf", "Moxie", "Jolly", ["Megahorn", "Close Combat", "Stone Edge", "Knock Off"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Nidoking", "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Shadow Ball"],
            "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    ]),
    # Route 45, Cooltrainer Kelly
    "TRAINER_KELLY_HNS": (6, [
        mon("Froslass", "Focus Sash", "Stakeout", "Timid", ["Spikes", "Ice Beam", "Shadow Ball", "Destiny Bond"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Roserade", "Black Sludge", "Natural Cure", "Timid", ["Toxic Spikes", "Sludge Bomb", "Giga Drain", "Sleep Powder"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Azumarill", "Sitrus Berry", "Huge Power", "Adamant", ["Belly Drum", "Aqua Jet", "Play Rough", "Liquidation"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Gardevoir", "Choice Scarf", "Trace", "Timid", ["Moonblast", "Psychic", "Mystical Fire", "Thunderbolt"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Milotic", "Leftovers", "Competitive", "Calm", ["Scald", "Ice Beam", "Recover", "Flip Turn"],
            "252 HP / 4 Def / 252 SpD"),
        mon("Lopunny", "Lopunnite", "Limber", "Jolly", ["Fake Out", "Return", "High Jump Kick", "Ice Punch"],
            "4 HP / 252 Atk / 252 Spe"),
    ]),
    # Kanto (after the Johto League, cap 90)
    # Route 1, Cooltrainer Quinn: sand
    "TRAINER_QUINN_HNS": (JOHTO_CHAMPION, [
        mon("Hippowdon", "Leftovers", "Sand Stream", "Impish", ["Earthquake", "Slack Off", "Stealth Rock", "Whirlwind"],
            "252 HP / 4 Atk / 252 Def"),
        mon("Excadrill", "Life Orb", "Sand Rush", "Adamant", ["Earthquake", "Iron Head", "Rock Slide", "Swords Dance"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Gliscor", "Toxic Orb", "Poison Heal", "Impish", ["Earthquake", "Knock Off", "U Turn", "Roost"],
            "252 HP / 4 Atk / 252 Def"),
        mon("Sandslash", "Focus Sash", "Sand Rush", "Jolly", ["Earthquake", "Knock Off", "Swords Dance", "Rapid Spin"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Tyranitar", "Choice Band", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Ice Punch"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Garchomp", "Garchompite", "Rough Skin", "Jolly", ["Swords Dance", "Earthquake", "Outrage", "Fire Fang"],
            "4 HP / 252 Atk / 252 Spe"),
    ]),
    # Route 3, Firebreather Otis: sun
    "TRAINER_OTIS_HNS": (JOHTO_CHAMPION, [
        mon("Ninetales", "Heat Rock", "Drought", "Timid", ["Fire Blast", "Solar Beam", "Nasty Plot", "Will O Wisp"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Houndoom", "Black Glasses", "Flash Fire", "Timid", ["Dark Pulse", "Fire Blast", "Sludge Bomb", "Nasty Plot"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Chandelure", "Choice Specs", "Flash Fire", "Modest", ["Shadow Ball", "Fire Blast", "Energy Ball", "Trick"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Magmortar", "Expert Belt", "Flame Body", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Solar Beam"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Volcarona", "Heavy Duty Boots", "Flame Body", "Modest", ["Fiery Dance", "Bug Buzz", "Giga Drain", "U Turn"],
            "4 HP / 252 SpA / 252 Spe"),
        mon("Charizard", "Charizardite Y", "Blaze", "Timid", ["Fire Blast", "Solar Beam", "Air Slash", "Focus Blast"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    ]),
    # Route 8, Biker Dwayne
    "TRAINER_DWAYNE_HNS": (JOHTO_CHAMPION, [
        mon("Weezing", "Rocky Helmet", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
        mon("Muk", "Black Sludge", "Poison Touch", "Adamant", ["Gunk Shot", "Knock Off", "Shadow Sneak", "Curse"]),
        mon("Scrafty", "Leftovers", "Intimidate", "Careful", ["Drain Punch", "Knock Off", "Ice Punch", "Bulk Up"]),
        mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
        mon("Krookodile", "Choice Scarf", "Moxie", "Jolly", ["Earthquake", "Knock Off", "Stone Edge", "Gunk Shot"]),
        mon("Hydreigon", "Life Orb", "Levitate", "Timid", ["Dark Pulse", "Draco Meteor", "Flamethrower", "U Turn"]),
    ]),
    # Route 9, Hiker Tim
    "TRAINER_TIM_HNS": (JOHTO_CHAMPION, [
        mon("Steelix", "Leftovers", "Sturdy", "Impish", ["Stealth Rock", "Heavy Slam", "Earthquake", "Curse"],
            "252 HP / 4 Atk / 252 Def"),
        mon("Donphan", "Leftovers", "Sturdy", "Adamant", ["Earthquake", "Ice Shard", "Knock Off", "Rapid Spin"],
            "252 HP / 252 Atk / 4 Def"),
        mon("Golem", "Custap Berry", "Sturdy", "Adamant", ["Stone Edge", "Earthquake", "Sucker Punch", "Explosion"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Mamoswine", "Life Orb", "Thick Fat", "Jolly", ["Earthquake", "Icicle Crash", "Ice Shard", "Stone Edge"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Rhyperior", "Weakness Policy", "Solid Rock", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Ice Punch"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Aggron", "Aggronite", "Sturdy", "Impish", ["Iron Defense", "Body Press", "Heavy Slam", "Stone Edge"],
            "252 HP / 4 Atk / 252 Def"),
    ]),
    # Route 10, Pokefan Robert: Fairy types
    "TRAINER_ROBERT_HNS": (JOHTO_CHAMPION, [
        mon("Clefable", "Leftovers", "Magic Guard", "Bold", ["Stealth Rock", "Moonblast", "Soft-Boiled", "Thunder Wave"],
            "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Azumarill", "Sitrus Berry", "Huge Power", "Adamant", ["Belly Drum", "Aqua Jet", "Play Rough", "Ice Spinner"],
            "252 HP / 252 Atk / 4 Def"),
        mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Swords Dance", "Play Rough", "Shadow Sneak", "Wood Hammer"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Togekiss", "Heavy-Duty Boots", "Serene Grace", "Timid", ["Nasty Plot", "Air Slash", "Dazzling Gleam", "Aura Sphere"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Sylveon", "Throat Spray", "Pixilate", "Modest", ["Hyper Voice", "Calm Mind", "Shadow Ball", "Wish"],
            "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Mawile", "Mawilite", "Intimidate", "Adamant", ["Swords Dance", "Play Rough", "Sucker Punch", "Fire Fang"],
            "252 HP / 252 Atk / 4 SpD"),
    ]),
    # Route 11, Psychic Herman
    "TRAINER_HERMAN_HNS": (JOHTO_CHAMPION, [
        mon("Tapu Lele", "Terrain Extender", "Psychic Surge", "Timid", ["Calm Mind", "Psychic", "Moonblast", "Energy Ball"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Espathra", "Leftovers", "Speed Boost", "Timid", ["Calm Mind", "Expanding Force", "Dazzling Gleam", "Protect"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Alakazam", "Life Orb", "Magic Guard", "Timid", ["Nasty Plot", "Expanding Force", "Shadow Ball", "Energy Ball"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Slowking", "Leftovers", "Regenerator", "Bold", ["Scald", "Future Sight", "Teleport", "Slack Off"],
            "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Metagross", "Weakness Policy", "Tough Claws", "Jolly", ["Stealth Rock", "Meteor Mash", "Psychic Fangs", "Knock Off"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Gallade", "Galladite", "Sharpness", "Jolly", ["Swords Dance", "Psycho Cut", "Sacred Sword", "Leaf Blade"],
            "4 HP / 252 Atk / 252 Spe"),
    ]),
    # Route 12, Fisherman Stephen: rain
    "TRAINER_STEPHEN_HNS": (JOHTO_CHAMPION, [
        mon("Politoed", "Damp Rock", "Drizzle", "Bold", ["Scald", "Hypnosis", "Encore", "Haze"],
            "252 HP / 252 Def / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Kingdra", "Life Orb", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Rain Dance"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Ludicolo", "Choice Specs", "Swift Swim", "Modest", ["Hydro Pump", "Giga Drain", "Ice Beam", "Focus Blast"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Seismitoad", "Leftovers", "Swift Swim", "Modest", ["Hydro Pump", "Earth Power", "Sludge Wave", "Stealth Rock"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Lanturn", "Leftovers", "Volt Absorb", "Modest", ["Thunder", "Scald", "Ice Beam", "Volt Switch"],
            "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Gyarados", "Gyaradosite", "Moxie", "Jolly", ["Waterfall", "Earthquake", "Dragon Dance", "Bounce"],
            "4 HP / 252 Atk / 252 Spe"),
    ]),
    # Route 13, Juggler Bret: tricks
    "TRAINER_BRET_HNS": (JOHTO_CHAMPION, [
        mon("Klefki", "Light Clay", "Prankster", "Calm", ["Reflect", "Light Screen", "Spikes", "Foul Play"],
            "252 HP / 4 Def / 252 SpD"),
        mon("Rotom-Wash", "Leftovers", "Levitate", "Timid", ["Hydro Pump", "Thunderbolt", "Will-O-Wisp", "Pain Split"],
            "252 HP / 4 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Mr. Mime", "Life Orb", "Filter", "Timid", ["Nasty Plot", "Psychic", "Dazzling Gleam", "Thunderbolt"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Chandelure", "Choice Scarf", "Flash Fire", "Timid", ["Shadow Ball", "Flamethrower", "Energy Ball", "Trick"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Hidden Power"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 30 SpA / 31 SpD / 30 Spe"),
        mon("Sableye", "Sablenite", "Frisk", "Careful", ["Will-O-Wisp", "Encore", "Recover", "Foul Play"],
            "252 HP / 4 Def / 252 SpD"),
    ]),
    # Route 15, Expert Colette: Fighting
    "TRAINER_COLETTE_HNS": (JOHTO_CHAMPION, [
        mon("Hawlucha", "White Herb", "Unburden", "Jolly", ["High Jump Kick", "Acrobatics", "Swords Dance", "Roost"]),
        mon("Breloom", "Focus Sash", "Technician", "Jolly", ["Mach Punch", "Bullet Seed", "Rock Tomb", "Spore"]),
        mon("Machamp", "Sitrus Berry", "No Guard", "Adamant", ["Dynamic Punch", "Stone Edge", "Knock Off", "Bullet Punch"]),
        mon("Conkeldurr", "Flame Orb", "Guts", "Adamant", ["Drain Punch", "Mach Punch", "Knock Off", "Ice Punch"]),
        mon("Infernape", "Life Orb", "Iron Fist", "Jolly", ["Close Combat", "Flare Blitz", "Mach Punch", "U Turn"]),
        mon("Lucario", "Life Orb", "Justified", "Adamant", ["Close Combat", "Extreme Speed", "Meteor Mash", "Swords Dance"]),
    ]),
    # Route 18, Bird Keeper Boris
    "TRAINER_BORIS_HNS": (JOHTO_CHAMPION, [
        mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Brave Bird", "Roost", "Whirlwind"],
            "252 HP / 4 Atk / 252 Def"),
        mon("Staraptor", "Life Orb", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "Double-Edge", "U-turn"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Talonflame", "Sharp Beak", "Gale Wings", "Adamant", ["Brave Bird", "Flare Blitz", "U-turn", "Roost"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Togekiss", "Choice Scarf", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Aura Sphere", "Flamethrower"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Dragonite", "Lum Berry", "Multiscale", "Adamant", ["Extreme Speed", "Dual Wingbeat", "Earthquake", "Fire Punch"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Altaria", "Altarianite", "Natural Cure", "Adamant", ["Dragon Dance", "Double-Edge", "Earthquake", "Roost"],
            "4 HP / 252 Atk / 252 Spe"),
    ]),
    # Route 20, Swimmer Lori
    "TRAINER_LORI_HNS": (JOHTO_CHAMPION, [
        mon("Araquanid", "Sitrus Berry", "Water Bubble", "Adamant", ["Liquidation", "Leech Life", "Sticky Web", "Mirror Coat"]),
        mon("Starmie", "Life Orb", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Ice Beam", "Thunderbolt"]),
        mon("Vaporeon", "Leftovers", "Water Absorb", "Bold", ["Scald", "Ice Beam", "Wish", "Protect"]),
        mon("Lapras", "Choice Specs", "Water Absorb", "Modest", ["Freeze Dry", "Hydro Pump", "Thunderbolt", "Ice Beam"]),
        mon("Primarina", "Life Orb", "Liquid Voice", "Modest", ["Sparkling Aria", "Moonblast", "Ice Beam", "Calm Mind"]),
        mon("Milotic", "Leftovers", "Marvel Scale", "Bold", ["Scald", "Ice Beam", "Recover", "Haze"]),
    ]),
    # Route 25, Cooltrainer Kevin
    "TRAINER_KEVIN_HNS": (JOHTO_CHAMPION, [
        mon("Ferrothorn", "Rocky Helmet", "Iron Barbs", "Relaxed", ["Spikes", "Leech Seed", "Gyro Ball", "Knock Off"],
            "252 HP / 4 Atk / 252 Def", ivs="31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 0 Spe"),
        mon("Gengar", "Focus Sash", "Levitate", "Timid", ["Nasty Plot", "Shadow Ball", "Sludge Bomb", "Thunderbolt"],
            "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
        mon("Crawdaunt", "Choice Band", "Adaptability", "Adamant", ["Crabhammer", "Knock Off", "Aqua Jet", "Superpower"],
            "252 HP / 252 Atk / 4 SpD"),
        mon("Kommo-o", "Life Orb", "Bulletproof", "Jolly", ["Close Combat", "Dragon Claw", "Poison Jab", "Dragon Dance"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Salamence", "Life Orb", "Intimidate", "Jolly", ["Dragon Dance", "Dual Wingbeat", "Earthquake", "Fire Fang"],
            "4 HP / 252 Atk / 252 Spe"),
        mon("Scizor", "Scizorite", "Technician", "Adamant", ["Swords Dance", "Bullet Punch", "Bug Bite", "Roost"],
            "252 HP / 252 Atk / 4 SpD"),
    ]),
}

# --- Red on Mt. Silver: the hardest battle in the game (DECISIONS.md D27) ------------------------
# Red battles only the Kanto Champion, when no level cap is left: all six at 100, in his first
# battle and in the rematch after the Sinjoh storyline (TRAINER_RED_POSTOBC_HNS). Every Pokemon has
# a competitive EV spread, which Minimal Grinding leaves him (src/pokemon.c).
RED_SIX = [
    mon("Pikachu", "Light Ball", "Lightning Rod", "Hasty", ["Volt Tackle", "Surf", "Knock Off", "Fake Out"],
        "252 Atk / 4 SpA / 252 Spe"),
    mon("Espeon", "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Snorlax", "Leftovers", "Thick Fat", "Careful", ["Curse", "Body Slam", "Rest", "Sleep Talk"],
        "252 HP / 4 Atk / 252 SpD"),
    mon("Venusaur", "Life Orb", "Chlorophyll", "Modest", ["Sleep Powder", "Growth", "Giga Drain", "Sludge Bomb"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Blastoise", "White Herb", "Torrent", "Modest", ["Shell Smash", "Hydro Pump", "Ice Beam", "Aura Sphere"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Charizard", "Charizardite Y", "Solar Power", "Timid", ["Fire Blast", "Solar Beam", "Focus Blast", "Air Slash"],
        "4 HP / 252 SpA / 252 Spe"),
]
RED_ITEMS = "Full Restore / Full Restore / Full Restore / Full Restore"

# --- Rematch and postgame teams (DECISIONS.md D47) -----------------------------------------------
# Heart & Soul's own teams for the Johto leaders' and the Elite Four's rematches, every postgame
# (_POSTOBC) rematch, the rival's last two battles and Elder Li were only levelled to the cap until
# 0.15.0. These are Emerald Imperium-style teams in their place: six (Li three) with items, natures,
# abilities, EVs and one Mega Evolution, each rematch stronger than the last.

# Landorus-T leads: Intimidate, Stealth Rock, U-turn. Gale Wings Talonflame's priority Tailwind
# and Will-O-Wisp; Choice Band Staraptor breaks walls; Iron Defense Corviknight Body Presses the
# Rock, Ice and Steel types; Static Zapdos Volt Switches and paralyses on contact. Mega Pidgeot's No
# Guard
# Hurricane and Work Up close.
FALKNER_2 = [
    mon("Landorus-Therian", "Leftovers", "Intimidate", "Impish", ["Stealth Rock", "Earthquake", "Knock Off", "U-turn"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Talonflame", "Heavy-Duty Boots", "Gale Wings", "Jolly", ["Tailwind", "Brave Bird", "Will-O-Wisp", "U-turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Staraptor", "Choice Band", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "Double-Edge", "Quick Attack"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Corviknight", "Rocky Helmet", "Pressure", "Impish", ["Brave Bird", "Body Press", "Iron Defense", "Roost"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Zapdos", "Heavy-Duty Boots", "Static", "Timid", ["Thunderbolt", "Heat Wave", "Volt Switch", "Roost"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Pidgeot", "Pidgeotite", "No Guard", "Timid", ["Hurricane", "Heat Wave", "Hidden Power", "Roost"],
        "4 HP / 252 SpA / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 30 SpA / 30 SpD / 31 Spe"),
]

# Focus Sash Galvantula lays Sticky Web and Volt Switches out; Kleavor's Stone Axe leaves Stealth
# Rock. Quiver Dance Volcarona and Choice Band Pheromosa sweep the slowed side; Water Bubble
# Araquanid walls the Fire and Rock types. Mega Scizor closes: Swords Dance, Bullet Punch.
BUGSY_2 = [
    mon("Galvantula", "Focus Sash", "Compound Eyes", "Timid", ["Sticky Web", "Thunder", "Bug Buzz", "Volt Switch"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Kleavor", "Life Orb", "Sharpness", "Jolly", ["Stone Axe", "X Scissor", "Knock Off", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Volcarona", "Heavy Duty Boots", "Flame Body", "Timid", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Araquanid", "Leftovers", "Water Bubble", "Adamant", ["Liquidation", "Leech Life", "Mirror Coat", "Toxic"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Pheromosa", "Choice Band", "Beast Boost", "Jolly", ["Close Combat", "U Turn", "Triple Axel", "Poison Jab"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Scizor", "Scizorite", "Technician", "Adamant", ["Swords Dance", "Bullet Punch", "Bug Bite", "Close Combat"],
        "252 HP / 252 Atk / 4 SpD"),
]

# Ambipom leads: Fake Out, Skill Link Tail Slap, U-turn. Miltank sets Stealth Rock and paralyses;
# Assault Vest Ursaluna-Bloodmoon's Mind's Eye Blood Moon hits Ghosts; Hisuian Zoroark's Illusion
# shows the ace before Nasty Plot; Choice Specs Porygon-Z breaks walls. Mega Lopunny (Scrappy)
# closes.
WHITNEY_2 = [
    mon("Ambipom", "Silk Scarf", "Skill Link", "Jolly", ["Fake Out", "Tail Slap", "U Turn", "Knock Off"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Miltank", "Leftovers", "Thick Fat", "Impish", ["Stealth Rock", "Body Slam", "Earthquake", "Milk Drink"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Ursaluna Bloodmoon", "Assault Vest", "Minds Eye", "Modest", ["Blood Moon", "Earth Power", "Moonblast", "Vacuum Wave"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Zoroark Hisui", "Focus Sash", "Illusion", "Timid", ["Nasty Plot", "Bitter Malice", "Hyper Voice", "Focus Blast"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Porygon Z", "Choice Specs", "Adaptability", "Modest", ["Tri Attack", "Ice Beam", "Thunderbolt", "Shadow Ball"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Lopunny", "Lopunnite", "Limber", "Jolly", ["Fake Out", "Double Edge", "Close Combat", "Ice Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]

# Focus Sash Froslass lays Spikes, burns and Taunts. Booster Energy Flutter Mane and Swords Dance
# Mimikyu sweep; Aegislash's Sacred Sword answers the Dark and Normal types that wall Ghosts; Choice
# Scarf Hisuian Typhlosion's Eruption burns Steels. Mega Banette's Prankster Will-O-Wisp and Shadow
# Sneak close.
MORTY_2 = [
    mon("Froslass", "Focus Sash", "Stakeout", "Jolly", ["Spikes", "Will O Wisp", "Taunt", "Poltergeist"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Flutter Mane", "Booster Energy", "Protosynthesis", "Timid", ["Moonblast", "Shadow Ball", "Mystical Fire", "Calm Mind"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Swords Dance", "Play Rough", "Shadow Claw", "Shadow Sneak"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Aegislash", "Leftovers", "Stance Change", "Quiet", ["Shadow Ball", "Sacred Sword", "Shadow Sneak", "Kings Shield"],
        "252 HP / 4 Atk / 252 SpA"),
    mon("Typhlosion Hisui", "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Shadow Ball", "Focus Blast", "Fire Blast"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Banette", "Banettite", "Frisk", "Adamant", ["Poltergeist", "Gunk Shot", "Shadow Sneak", "Will O Wisp"],
        "252 HP / 252 Atk / 4 Def"),
]

# Booster Energy Great Tusk sets Stealth Rock and Knocks Off items; Loaded Dice Technician Breloom
# spreads Spore; Assault Vest Iron Hands Fake Outs and drains; Sneasler's Dire Claw hits Fairies,
# Throat Chop Psychics, and White Herb turns on Unburden. Bulk Up Poliwrath, then Mega Medicham's
# Huge Power Fake Out and Bullet Punch.
CHUCK_2 = [
    mon("Great Tusk", "Booster Energy", "Protosynthesis", "Jolly", ["Stealth Rock", "Headlong Rush", "Close Combat", "Knock Off"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Breloom", "Loaded Dice", "Technician", "Jolly", ["Spore", "Bullet Seed", "Mach Punch", "Rock Tomb"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Iron Hands", "Assault Vest", "Quark Drive", "Adamant", ["Fake Out", "Drain Punch", "Wild Charge", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Sneasler", "White Herb", "Unburden", "Jolly", ["Dire Claw", "Close Combat", "Throat Chop", "Swords Dance"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Poliwrath", "Leftovers", "Water Absorb", "Adamant", ["Bulk Up", "Drain Punch", "Liquidation", "Ice Punch"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Medicham", "Medichamite", "Huge Power", "Jolly", ["Fake Out", "High Jump Kick", "Zen Headbutt", "Bullet Punch"],
        "4 HP / 252 Atk / 252 Spe"),
]

# Sturdy Custap Berry Steelix sets Stealth Rock and Explodes; Choice Specs Magnezone traps Steels;
# Air Balloon Heatran's Flash Fire and Magma Storm take on Fire; Power Herb Celesteela's Meteor
# Beam, immune to Ground; Gholdengo's Nasty Plot, immune to Fighting. Mega Mawile's Huge Power
# Swords Dance and Sucker Punch close.
JASMINE_2 = [
    mon("Steelix", "Custap Berry", "Sturdy", "Adamant", ["Stealth Rock", "Heavy Slam", "Earthquake", "Explosion"],
        "252 HP / 252 Atk / 4 Def"),
    mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Body Press"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Heatran", "Air Balloon", "Flash Fire", "Timid", ["Magma Storm", "Earth Power", "Flash Cannon", "Taunt"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Celesteela", "Power Herb", "Beast Boost", "Modest", ["Meteor Beam", "Air Slash", "Flamethrower", "Giga Drain"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Gholdengo", "Leftovers", "Good As Gold", "Timid", ["Make It Rain", "Shadow Ball", "Nasty Plot", "Recover"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Mawile", "Mawilite", "Intimidate", "Adamant", ["Swords Dance", "Play Rough", "Iron Head", "Sucker Punch"],
        "252 HP / 252 Atk / 4 SpD"),
]

# Abomasnow's snow and Light Clay Aurora Veil open; Sword of Ruin Chien-Pao Swords Dances behind
# the veil, with Psychic Fangs for the Fighting types every Ice type fears; Booster Energy Iron
# Bundle's Freeze-Dry and Encore; Mamoswine lays Stealth Rock with Ice Shard priority; White Herb
# Shell Smash Cloyster. Mega Glalie's Refrigerate Double-Edge closes.
PRYCE_2 = [
    mon("Abomasnow", "Light Clay", "Snow Warning", "Modest", ["Aurora Veil", "Blizzard", "Giga Drain", "Focus Blast"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Chien Pao", "Life Orb", "Sword Of Ruin", "Jolly", ["Swords Dance", "Icicle Crash", "Sucker Punch", "Psychic Fangs"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Iron Bundle", "Booster Energy", "Quark Drive", "Timid", ["Freeze Dry", "Hydro Pump", "Encore", "Flip Turn"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Mamoswine", "Life Orb", "Thick Fat", "Adamant", ["Stealth Rock", "Earthquake", "Icicle Crash", "Ice Shard"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Cloyster", "White Herb", "Skill Link", "Jolly", ["Shell Smash", "Icicle Spear", "Rock Blast", "Drill Run"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Glalie", "Glalitite", "Refrigerate", "Naive", ["Double Edge", "Freeze Dry", "Earthquake", "Ice Shard"],
        "252 Atk / 4 SpA / 252 Spe"),
]

# Focus Sash Garchomp sets Stealth Rock; Kingdra brings its own rain for Swift Swim (and
# Archaludon's Electro Shot then skips its charge); Rock Head Tyrantrum Dragon Dances and Head
# Smashes; Flash Cannons answer Fairies; Throat Spray Kommo-o's Clangorous Soul. Mega Latios closes.
CLAIR_2 = [
    mon("Garchomp", "Focus Sash", "Rough Skin", "Jolly", ["Stealth Rock", "Earthquake", "Scale Shot", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Kingdra", "Life Orb", "Swift Swim", "Modest", ["Rain Dance", "Hydro Pump", "Draco Meteor", "Flash Cannon"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Tyrantrum", "Life Orb", "Rock Head", "Jolly", ["Dragon Dance", "Head Smash", "Outrage", "Earthquake"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Archaludon", "Power Herb", "Stamina", "Modest", ["Electro Shot", "Draco Meteor", "Flash Cannon", "Body Press"],
        "252 HP / 252 SpA / 4 SpD"),
    mon("Kommo O", "Throat Spray", "Bulletproof", "Timid", ["Clangorous Soul", "Clanging Scales", "Aura Sphere", "Flash Cannon"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Latios", "Latiosite", "Levitate", "Timid", ["Draco Meteor", "Psyshock", "Aura Sphere", "Recover"],
        "4 HP / 252 SpA / 252 Spe"),
]

# Prankster Thundurus leads with Taunt and U-turns out; Togekiss Defogs and flinches with Air Slash.
# Poison Heal Gliscor takes the Electric attacks; Moltres and Choice Scarf Galarian Zapdos hit the
# Steel, Rock and Ice types that beat Flying. Mega Salamence Dragon Dances last.
FALKNER_POSTOBC = [
    mon("Thundurus", "Focus Sash", "Prankster", "Timid", ["U Turn", "Taunt", "Thunderbolt", "Grass Knot"]),
    mon("Togekiss", "Heavy Duty Boots", "Serene Grace", "Timid", ["Air Slash", "Moonblast", "Defog", "Roost"]),
    mon("Moltres", "Heavy Duty Boots", "Flame Body", "Modest", ["Fire Blast", "Hurricane", "Scorching Sands", "Roost"]),
    mon("Zapdos Galar", "Choice Scarf", "Defiant", "Jolly", ["Close Combat", "Brave Bird", "Knock Off", "U Turn"]),
    mon("Gliscor", "Toxic Orb", "Poison Heal", "Impish", ["Earthquake", "Knock Off", "Toxic", "Roost"]),
    mon("Salamence", "Salamencite", "Intimidate", "Jolly", ["Dragon Dance", "Double Edge", "Earthquake", "Roost"]),
]

# Sturdy Forretress lays Spikes and Stealth Rock, spins and Volt Switches out. Speed Boost Yanmega
# and Swords Dance Scolipede outpace the field; Iron Moth burns Steels, Fairies. Golisopod's Water
# moves and Rock Slide cover Fire and Flying; Mega Pinsir's Aerilate Quick Attack and Double-Edge
# finish.
BUGSY_POSTOBC = [
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Stealth Rock", "Rapid Spin", "Volt Switch"]),
    mon("Yanmega", "Life Orb", "Speed Boost", "Modest", ["Bug Buzz", "Air Slash", "Giga Drain", "Protect"]),
    mon("Iron Moth", "Booster Energy", "Quark Drive", "Timid", ["Fiery Dance", "Sludge Wave", "Energy Ball", "Psychic"]),
    mon("Scolipede", "Focus Sash", "Speed Boost", "Jolly", ["Megahorn", "Poison Jab", "Earthquake", "Swords Dance"]),
    mon("Golisopod", "Assault Vest", "Emergency Exit", "Adamant", ["First Impression", "Liquidation", "Rock Slide", "Aqua Jet"]),
    mon("Pinsir", "Pinsirite", "Moxie", "Jolly", ["Swords Dance", "Double Edge", "Close Combat", "Quick Attack"]),
]

# Eviolite Chansey sets Stealth Rock and paralyzes; Cyclizar spins and Shed Tails a Substitute
# to the slow hitters. Throat Spray Farigiraf and Mega Kangaskhan strike twice with Parental Bond,
# Guts Ursaluna smashes walls and Skill Link Cinccino breaks Sashes and Substitutes.
WHITNEY_POSTOBC = [
    mon("Chansey", "Eviolite", "Natural Cure", "Bold", ["Stealth Rock", "Seismic Toss", "Soft Boiled", "Thunder Wave"]),
    mon("Cyclizar", "Heavy Duty Boots", "Regenerator", "Jolly", ["Shed Tail", "Rapid Spin", "Knock Off", "Double Edge"]),
    mon("Farigiraf", "Throat Spray", "Parental Bond", "Modest", ["Nasty Plot", "Hyper Voice", "Psyshock", "Shadow Ball"]),
    mon("Ursaluna", "Flame Orb", "Guts", "Adamant", ["Facade", "Headlong Rush", "Play Rough", "Crunch"]),
    mon("Cinccino", "Life Orb", "Skill Link", "Jolly", ["Tail Slap", "Bullet Seed", "Rock Blast", "Knock Off"]),
    mon("Kangaskhan", "Kangaskhanite", "Scrappy", "Jolly", ["Fake Out", "Double Edge", "Power Up Punch", "Sucker Punch"]),
]

# Golurk sets Stealth Rock behind a Focus Sash; Nasty Plot Spectrier snowballs with Grim Neigh and
# Bulk Up Annihilape grows Rage Fist. Choice Scarf Gholdengo revenge-kills and Tricks walls, Calm
# Mind Blacephalon breaks them; Mega Gengar's Shadow Tag traps the rest.
MORTY_POSTOBC = [
    mon("Golurk", "Focus Sash", "Iron Fist", "Adamant", ["Stealth Rock", "Earthquake", "Poltergeist", "Drain Punch"]),
    mon("Spectrier", "Life Orb", "Grim Neigh", "Timid", ["Nasty Plot", "Shadow Ball", "Dark Pulse", "Substitute"]),
    mon("Annihilape", "Leftovers", "Defiant", "Careful", ["Bulk Up", "Rage Fist", "Drain Punch", "Taunt"]),
    mon("Gholdengo", "Choice Scarf", "Good As Gold", "Timid", ["Make It Rain", "Shadow Ball", "Focus Blast", "Trick"]),
    mon("Blacephalon", "Life Orb", "Beast Boost", "Timid", ["Shadow Ball", "Fire Blast", "Psyshock", "Calm Mind"]),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Focus Blast", "Nasty Plot"]),
]

# Terrakion sets Stealth Rock and Stone Edges the Flying types; Choice Band Urshifu's Wicked Blow
# breaks Psychics and Ghosts; Calm Mind Iron Valiant handles Fairies and Assault Vest Hariyama Fake
# Outs and Heavy Slams them. Quaquaval adds Water and Ice; Mega Heracross (Skill Link) closes, his
# signature.
CHUCK_POSTOBC = [
    mon("Terrakion", "Focus Sash", "Sharpness", "Jolly", ["Stealth Rock", "Stone Edge", "Sacred Sword", "Earthquake"]),
    mon("Urshifu Single Strike", "Choice Band", "Unseen Fist", "Jolly", ["Wicked Blow", "Close Combat", "Sucker Punch", "U Turn"]),
    mon("Iron Valiant", "Booster Energy", "Quark Drive", "Timid", ["Calm Mind", "Moonblast", "Aura Sphere", "Shadow Ball"]),
    mon("Hariyama", "Assault Vest", "Thick Fat", "Adamant", ["Fake Out", "Close Combat", "Knock Off", "Heavy Slam"]),
    mon("Quaquaval", "Life Orb", "Moxie", "Jolly", ["Aqua Step", "Close Combat", "Ice Spinner", "Roost"]),
    mon("Heracross", "Heracronite", "Guts", "Jolly", ["Pin Missile", "Close Combat", "Rock Blast", "Knock Off"]),
]

# Tinkaton sets Stealth Rock and swings Gigaton Hammer behind a Focus Sash; Choice Specs Iron
# Crown's
# Sharpness Tachyon Cutter breaks Sashes, Choice Scarf Kartana revenge-kills, Empoleon takes Fire.
# Swords Dance Kingambit cleans up late and Mega Metagross closes with Tough Claws.
JASMINE_POSTOBC = [
    mon("Tinkaton", "Focus Sash", "Mold Breaker", "Jolly", ["Stealth Rock", "Gigaton Hammer", "Play Rough", "Encore"]),
    mon("Iron Crown", "Choice Specs", "Sharpness", "Timid", ["Tachyon Cutter", "Psyshock", "Focus Blast", "Volt Switch"]),
    mon("Kartana", "Choice Scarf", "Beast Boost", "Jolly", ["Leaf Blade", "Sacred Sword", "Smart Strike", "Knock Off"]),
    mon("Empoleon", "Leftovers", "Competitive", "Modest", ["Scald", "Flash Cannon", "Ice Beam", "Roost"]),
    mon("Kingambit", "Leftovers", "Supreme Overlord", "Adamant", ["Kowtow Cleave", "Iron Head", "Sucker Punch", "Swords Dance"]),
    mon("Metagross", "Metagrossite", "Clear Body", "Jolly", ["Meteor Mash", "Zen Headbutt", "Earthquake", "Ice Punch"]),
]

# Icy Rock Alolan Ninetales starts eight turns of snow and Aurora Veil; Slush Rush Arctozolt moves
# first and doubles Bolt Beak; Dragon Dance Baxcalibur sweeps behind the Veil. Assault Vest
# Glastrier soaks hits, Choice Scarf Galarian Darmanitan burns Steels; Mega Abomasnow brings the
# snow back as it switches in, then its Slush Rush doubles its Speed.
PRYCE_POSTOBC = [
    mon("Ninetales Alola", "Icy Rock", "Snow Warning", "Timid", ["Aurora Veil", "Blizzard", "Moonblast", "Encore"]),
    mon("Arctozolt", "Life Orb", "Slush Rush", "Adamant", ["Bolt Beak", "Icicle Crash", "Low Kick", "Stone Edge"]),
    mon("Baxcalibur", "Loaded Dice", "Thermal Exchange", "Jolly", ["Dragon Dance", "Icicle Spear", "Scale Shot", "Earthquake"]),
    mon("Glastrier", "Assault Vest", "Chilling Neigh", "Adamant", ["Icicle Crash", "High Horsepower", "Close Combat", "Heavy Slam"]),
    mon("Darmanitan Galar", "Choice Scarf", "Gorilla Tactics", "Jolly", ["Icicle Crash", "Flare Blitz", "U Turn", "Earthquake"]),
    mon("Abomasnow", "Abomasite", "Snow Warning", "Modest", ["Blizzard", "Energy Ball", "Earth Power", "Focus Blast"]),
]

# Focus Sash Dragapult leads with Will-O-Wisp and U-turn; Booster Energy Roaring Moon and Booster
# Energy Calm Mind Raging Bolt break through. Choice Specs Naganadel's Sludge Wave and Assault Vest
# Hisuian Goodra's Flash Cannon answer Fairies; Mega Charizard X (Fire/Dragon) Dragon Dances to
# finish.
CLAIR_POSTOBC = [
    mon("Dragapult", "Focus Sash", "Infiltrator", "Jolly", ["Dragon Darts", "Phantom Force", "Will O Wisp", "U Turn"]),
    mon("Roaring Moon", "Booster Energy", "Protosynthesis", "Jolly", ["Knock Off", "Outrage", "Acrobatics", "Earthquake"]),
    mon("Raging Bolt", "Booster Energy", "Protosynthesis", "Modest", ["Calm Mind", "Thunderbolt", "Dragon Pulse", "Thunderclap"]),
    mon("Naganadel", "Choice Specs", "Beast Boost", "Timid", ["Sludge Wave", "Draco Meteor", "Fire Blast", "U Turn"]),
    mon("Goodra Hisui", "Assault Vest", "Sap Sipper", "Modest", ["Draco Meteor", "Flash Cannon", "Fire Blast", "Thunderbolt"]),
    mon("Charizard", "Charizardite X", "Blaze", "Jolly", ["Dragon Dance", "Flare Blitz", "Dragon Claw", "Earthquake"]),
]

# Sand: Tyranitar's Smooth Rock sandstorm raises every Rock type's Sp. Def by half and doubles Sand
# Rush Lycanroc's Speed; Tyranitar also lays Stealth Rock and paralyses. Booster Energy Iron Thorns
# Dragon Dances and Choice Specs Nihilego breaks walls, Storm Drain Cradily soaks up Water moves and
# Curses, and Mega Aerodactyl Dragon Dances last.
BROCK_POSTOBC = [
    mon("Tyranitar", "Smooth Rock", "Sand Stream", "Careful", ["Stealth Rock", "Stone Edge", "Knock Off", "Thunder Wave"]),
    mon("Lycanroc Midday", "Life Orb", "Sand Rush", "Jolly", ["Swords Dance", "Accelerock", "Stone Edge", "Close Combat"]),
    mon("Nihilego", "Choice Specs", "Beast Boost", "Timid", ["Power Gem", "Sludge Wave", "Thunderbolt", "Psychic"]),
    mon("Iron Thorns", "Booster Energy", "Quark Drive", "Jolly", ["Dragon Dance", "Wild Charge", "Stone Edge", "Earthquake"]),
    mon("Cradily", "Leftovers", "Storm Drain", "Careful", ["Curse", "Recover", "Seed Bomb", "Stone Edge"]),
    mon("Aerodactyl", "Aerodactylite", "Unnerve", "Jolly", ["Dragon Dance", "Stone Edge", "Dual Wingbeat", "Earthquake"]),
]

# Rain: Pelipper's Drizzle (Damp Rock) and Tailwind, then U-turn. Swampert lays Stealth Rock,
# takes the Electric moves and Flip Turns; Swift Swim Choice Specs Kingdra and Urshifu (Surging
# Strikes always crit, Aqua Jet) attack; Misty Surge Tapu Fini blocks status and Calm Minds; Mega
# Blastoise closes with Shell Smash and Mega Launcher Water Pulse and Aura Sphere.
MISTY_POSTOBC = [
    mon("Pelipper", "Damp Rock", "Drizzle", "Modest", ["Hurricane", "Hydro Pump", "Tailwind", "U Turn"]),
    mon("Kingdra", "Choice Specs", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Flip Turn"]),
    mon("Urshifu Rapid Strike", "Life Orb", "Unseen Fist", "Jolly", ["Surging Strikes", "Close Combat", "Aqua Jet", "U Turn"]),
    mon("Swampert", "Leftovers", "Torrent", "Impish", ["Stealth Rock", "Earthquake", "Liquidation", "Flip Turn"]),
    mon("Tapu Fini", "Leftovers", "Misty Surge", "Bold", ["Calm Mind", "Moonblast", "Surf", "Draining Kiss"]),
    mon("Blastoise", "Blastoisinite", "Torrent", "Modest", ["Shell Smash", "Water Pulse", "Aura Sphere", "Ice Beam"]),
]

# Electric Terrain and screens: Tapu Koko sets both and Volt Switches out; Sandy Shocks lays Stealth
# Rock and Spikes and Earth Powers the Electric types. Motor Drive Electivire punches through,
# Rotom-Wash takes the Ground moves and burns, and Tail Glow Xurkitree and Agility Mega Ampharos
# (Thick Fat) sweep.
LTSURGE_POSTOBC = [
    mon("Tapu Koko", "Light Clay", "Electric Surge", "Timid", ["Reflect", "Light Screen", "Volt Switch", "Dazzling Gleam"]),
    mon("Sandy Shocks", "Booster Energy", "Protosynthesis", "Timid", ["Stealth Rock", "Spikes", "Earth Power", "Volt Switch"]),
    mon("Electivire", "Life Orb", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Earthquake", "Cross Chop"]),
    mon("Rotom Wash", "Leftovers", "Levitate", "Bold", ["Hydro Pump", "Volt Switch", "Will O Wisp", "Pain Split"]),
    mon("Xurkitree", "Life Orb", "Beast Boost", "Timid", ["Tail Glow", "Thunderbolt", "Energy Ball", "Dazzling Gleam"]),
    mon("Ampharos", "Ampharosite", "Static", "Modest", ["Agility", "Thunderbolt", "Dragon Pulse", "Focus Blast"]),
]

# Prankster Whimsicott leads with Tailwind, Encores set-up and U-turns out. Rillaboom's Grassy Surge
# powers Grassy Glide priority after Fake Out; Choice Band Tsareena (no priority against it) and
# Contrary Serperior sweep in the Tailwind; Rotom-Mow's Thunderbolt and Will-O-Wisp handle Steel and
# Flying types; Mega Venusaur's Thick Fat takes the Fire and Ice moves last.
ERIKA_POSTOBC = [
    mon("Whimsicott", "Focus Sash", "Prankster", "Timid", ["Tailwind", "Encore", "Moonblast", "U Turn"]),
    mon("Rillaboom", "Assault Vest", "Grassy Surge", "Adamant", ["Fake Out", "Grassy Glide", "Wood Hammer", "High Horsepower"]),
    mon("Tsareena", "Choice Band", "Queenly Majesty", "Jolly", ["High Jump Kick", "Power Whip", "Knock Off", "U Turn"]),
    mon("Serperior", "Leftovers", "Contrary", "Timid", ["Leaf Storm", "Glare", "Dragon Pulse", "Synthesis"]),
    mon("Rotom Mow", "Sitrus Berry", "Levitate", "Modest", ["Volt Switch", "Thunderbolt", "Leaf Storm", "Will O Wisp"]),
    mon("Venusaur", "Venusaurite", "Chlorophyll", "Modest", ["Giga Drain", "Sludge Bomb", "Earth Power", "Sleep Powder"]),
]

# A ninja's traps: Focus Sash Glimmora lays Stealth Rock and Spikes, and Toxic Debris adds Toxic
# Spikes when it is struck; Levitate Galarian Weezing burns and takes the Ground moves. White Herb
# Unburden Sneasler, Nasty Plot Naganadel and Fake Out Munkidori attack; Mega Gengar's Shadow Tag
# traps the poisoned and burned for Hex.
JANINE_POSTOBC = [
    mon("Glimmora", "Focus Sash", "Toxic Debris", "Timid", ["Stealth Rock", "Spikes", "Mortal Spin", "Earth Power"]),
    mon("Weezing Galar", "Black Sludge", "Levitate", "Bold", ["Strange Steam", "Flamethrower", "Will O Wisp", "Pain Split"]),
    mon("Sneasler", "White Herb", "Unburden", "Jolly", ["Swords Dance", "Close Combat", "Dire Claw", "Acrobatics"]),
    mon("Naganadel", "Life Orb", "Beast Boost", "Timid", ["Nasty Plot", "Sludge Wave", "Dragon Pulse", "Fire Blast"]),
    mon("Munkidori", "Assault Vest", "Toxic Chain", "Timid", ["Fake Out", "Sludge Wave", "Psychic", "Grass Knot"]),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Hex", "Sludge Wave", "Focus Blast", "Will O Wisp"]),
]

# Psychic Terrain: Tapu Lele sets it (no priority moves against her grounded Pokemon) and both
# screens. Weakness Policy Metagross lays Stealth Rock; Choice Specs Armarouge's Mega Launcher Aura
# Sphere and Dark Pulse and Choice Scarf Iron Boulder's blades break walls; Calm Mind Cresselia
# walls; Mega Alakazam's Nasty Plot Expanding Force closes.
SABRINA_POSTOBC = [
    mon("Tapu Lele", "Light Clay", "Psychic Surge", "Timid", ["Reflect", "Light Screen", "Psychic", "Moonblast"]),
    mon("Metagross", "Weakness Policy", "Tough Claws", "Adamant", ["Stealth Rock", "Meteor Mash", "Psychic Fangs", "Earthquake"]),
    mon("Iron Boulder", "Choice Scarf", "Sharpness", "Jolly", ["Mighty Cleave", "Psycho Cut", "Sacred Sword", "X Scissor"]),
    mon("Cresselia", "Leftovers", "Levitate", "Bold", ["Calm Mind", "Moonblast", "Psyshock", "Moonlight"]),
    mon("Armarouge", "Choice Specs", "Mega Launcher", "Timid", ["Armor Cannon", "Expanding Force", "Aura Sphere", "Dark Pulse"]),
    mon("Alakazam", "Alakazite", "Magic Guard", "Timid", ["Nasty Plot", "Expanding Force", "Shadow Ball", "Focus Blast"]),
]

# Sun: Ninetales' Drought (Heat Rock) and Encore; Air Balloon Heatran lays Stealth Rock and traps
# with Magma Storm. Choice Specs Chi-Yu's Beads of Ruin breaks walls, Protosynthesis Gouging Fire
# Dragon Dances, Gale Wings Talonflame has priority, and Mega Blaziken's Speed Boost and Swords
# Dance close.
BLAINE_POSTOBC = [
    mon("Ninetales", "Heat Rock", "Drought", "Timid", ["Fire Blast", "Solar Beam", "Scorching Sands", "Encore"]),
    mon("Heatran", "Air Balloon", "Flash Fire", "Modest", ["Stealth Rock", "Magma Storm", "Earth Power", "Solar Beam"]),
    mon("Chi Yu", "Choice Specs", "Beads Of Ruin", "Timid", ["Overheat", "Flamethrower", "Dark Pulse", "Psychic"]),
    mon("Gouging Fire", "Booster Energy", "Protosynthesis", "Adamant", ["Dragon Dance", "Flare Blitz", "Dragon Claw", "Earthquake"]),
    mon("Talonflame", "Heavy Duty Boots", "Gale Wings", "Jolly", ["Brave Bird", "Flare Blitz", "U Turn", "Roost"]),
    mon("Blaziken", "Blazikenite", "Blaze", "Adamant", ["Swords Dance", "Flare Blitz", "Close Combat", "Thunder Punch"]),
]

# Mega Pidgeot leads: Tailwind, No Guard Hurricane, U-turn out. Rhyperior lays Stealth Rock and
# takes the Electric moves, Intimidate Arcanine burns and has Extreme Speed, Moxie Gyarados Dragon
# Dances, Choice Band Scizor's Bullet Punch picks off; Thick Club Alolan Marowak, from his Heart &
# Soul postgame team, comes last.
BLUE_POSTOBC = [
    mon("Pidgeot", "Pidgeotite", "No Guard", "Timid", ["Tailwind", "Hurricane", "Heat Wave", "U Turn"]),
    mon("Rhyperior", "Leftovers", "Solid Rock", "Adamant", ["Stealth Rock", "Earthquake", "Stone Edge", "Megahorn"]),
    mon("Arcanine", "Rocky Helmet", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Will O Wisp", "Morning Sun"]),
    mon("Gyarados", "Heavy Duty Boots", "Moxie", "Jolly", ["Dragon Dance", "Waterfall", "Earthquake", "Ice Fang"]),
    mon("Scizor", "Choice Band", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Close Combat"]),
    mon("Marowak Alola", "Thick Club", "Rock Head", "Adamant", ["Shadow Bone", "Flare Blitz", "Earthquake", "Swords Dance"]),
]

# Focus Sash Azelf sets Stealth Rock, Taunts and U-turns out. Tapu Lele's Psychic Terrain stops
# Sucker Punch and other priority while its Choice Specs breaks walls. Assault Vest Galarian
# Slowking tanks, Magic Bounce Xatu paralyses and bounces hazards back; Gallade sweeps after Swords
# Dance, and Calm Mind Mega Gardevoir (Pixilate Hyper Voice) closes.
WILL_2 = [
    mon("Azelf", "Focus Sash", "Levitate", "Hasty", ["Stealth Rock", "Taunt", "Psychic", "U Turn"],
        "4 Atk / 252 SpA / 252 Spe"),
    mon("Tapu Lele", "Choice Specs", "Psychic Surge", "Timid", ["Psychic", "Moonblast", "Focus Blast", "Shadow Ball"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Slowking Galar", "Assault Vest", "Regenerator", "Calm", ["Sludge Bomb", "Psyshock", "Fire Blast", "Power Gem"],
        "252 HP / 4 SpA / 252 SpD"),
    mon("Xatu", "Rocky Helmet", "Magic Bounce", "Bold", ["Psychic", "Thunder Wave", "U Turn", "Roost"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Gallade", "Life Orb", "Sharpness", "Jolly", ["Swords Dance", "Sacred Sword", "Psycho Cut", "Leaf Blade"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Gardevoir", "Gardevoirite", "Trace", "Timid", ["Hyper Voice", "Psyshock", "Mystical Fire", "Calm Mind"],
        "4 HP / 252 SpA / 252 Spe"),
]

# Light Clay Uxie sets Reflect, Light Screen and Stealth Rock, then U-turns out. Speed Boost
# Espathra Calm Minds behind the screens; Magic Guard Reuniclus and Choice Specs Latias break walls,
# Choice Band Iron Leaves hits hard, and Sharpness Mega Gallade Swords Dances to finish.
WILL_POSTOBC = [
    mon("Uxie", "Light Clay", "Levitate", "Impish", ["Reflect", "Light Screen", "Stealth Rock", "U Turn"]),
    mon("Espathra", "Leftovers", "Speed Boost", "Timid", ["Calm Mind", "Stored Power", "Dazzling Gleam", "Roost"]),
    mon("Reuniclus", "Life Orb", "Magic Guard", "Modest", ["Psyshock", "Focus Blast", "Shadow Ball", "Recover"]),
    mon("Latias", "Choice Specs", "Levitate", "Timid", ["Draco Meteor", "Mist Ball", "Aura Sphere", "Mystical Fire"]),
    mon("Iron Leaves", "Choice Band", "Sharpness", "Jolly", ["Psyblade", "Leaf Blade", "Sacred Sword", "X Scissor"]),
    mon("Gallade", "Galladite", "Sharpness", "Jolly", ["Swords Dance", "Sacred Sword", "Psycho Cut", "Night Slash"]),
]

# Tentacruel lays Toxic Spikes and spins; Corrosion Crobat badly poisons even Steel types and
# U-turns. Galarian Weezing burns and walls Dragons; Overqwil's Barb Barrage doubles on poisoned
# foes. Sheer Force Nidoking breaks walls, and Mega Beedrill's Adaptability strikes last.
KOGA_2 = [
    mon("Tentacruel", "Black Sludge", "Clear Body", "Timid", ["Toxic Spikes", "Knock Off", "Rapid Spin", "Sludge Bomb"],
        "252 HP / 4 SpA / 252 Spe"),
    mon("Crobat", "Heavy Duty Boots", "Corrosion", "Jolly", ["Brave Bird", "U Turn", "Toxic", "Roost"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Weezing Galar", "Rocky Helmet", "Levitate", "Bold", ["Will O Wisp", "Strange Steam", "Fire Blast", "Pain Split"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Overqwil", "Life Orb", "Intimidate", "Adamant", ["Swords Dance", "Barb Barrage", "Crunch", "Aqua Jet"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Nidoking", "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Beedrill", "Beedrillite", "Sniper", "Jolly", ["Poison Jab", "U Turn", "Drill Run", "Knock Off"],
        "252 Atk / 4 SpD / 252 Spe"),
]

# Focus Sash Nihilego sets Stealth Rock and Grass Knots Ground types; Crobat Taunts and U-turns.
# Bulk Up Okidogi's Toxic Chain badly poisons; Scope Lens Sniper Drapion lands critical hits;
# Fezandipiti's Toxic Chain and Play Rough handle Dragons and Fighters. Swords Dance Mega Beedrill
# strikes last.
KOGA_POSTOBC = [
    mon("Nihilego", "Focus Sash", "Beast Boost", "Timid", ["Stealth Rock", "Power Gem", "Sludge Wave", "Grass Knot"]),
    mon("Crobat", "Heavy Duty Boots", "Infiltrator", "Jolly", ["Brave Bird", "U Turn", "Taunt", "Roost"]),
    mon("Okidogi", "Leftovers", "Toxic Chain", "Careful", ["Bulk Up", "Drain Punch", "Gunk Shot", "Knock Off"]),
    mon("Drapion", "Scope Lens", "Sniper", "Jolly", ["Swords Dance", "Night Slash", "Cross Poison", "Earthquake"]),
    mon("Fezandipiti", "Heavy Duty Boots", "Toxic Chain", "Careful", ["Play Rough", "Gunk Shot", "U Turn", "Roost"]),
    mon("Beedrill", "Beedrillite", "Sniper", "Jolly", ["Swords Dance", "Poison Jab", "Drill Run", "Knock Off"]),
]

# Focus Sash Cobalion (Steel blunts Psychic and Fairy moves) sets Stealth Rock and Volt Switches.
# White Herb Hawlucha's Close Combat turns on Unburden after Swords Dance; Guts Conkeldurr has Mach
# Punch; Nasty Plot Infernape hits physical walls. Choice Scarf Urshifu revenge-kills Psychics, and
# Mega Lucario's Adaptability (his Mega, as in his first team) closes.
BRUNO_2 = [
    mon("Cobalion", "Focus Sash", "Sharpness", "Jolly", ["Stealth Rock", "Sacred Sword", "Iron Head", "Volt Switch"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Hawlucha", "White Herb", "Unburden", "Jolly", ["Swords Dance", "Close Combat", "Acrobatics", "Poison Jab"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Conkeldurr", "Flame Orb", "Guts", "Adamant", ["Mach Punch", "Drain Punch", "Knock Off", "Ice Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Infernape", "Life Orb", "Blaze", "Timid", ["Nasty Plot", "Fire Blast", "Aura Sphere", "Grass Knot"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Urshifu Single Strike", "Choice Scarf", "Unseen Fist", "Jolly", ["Wicked Blow", "Close Combat", "U Turn", "Iron Head"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Lucario", "Lucarionite", "Inner Focus", "Jolly", ["Swords Dance", "Close Combat", "Meteor Mash", "Extreme Speed"],
        "4 HP / 252 Atk / 252 Spe"),
]

# Booster Energy Great Tusk sets Stealth Rock and spins away hazards; Bulk Up Buzzwole heals with
# Drain Punch and Leech Life. Choice Band No Guard Machamp and Choice Specs Lucario break physical
# and special walls; Scrappy Flamigo U-turns. Huge Power Mega Medicham finishes, with Bullet Punch
# for Fairies.
BRUNO_POSTOBC = [
    mon("Great Tusk", "Booster Energy", "Protosynthesis", "Jolly", ["Stealth Rock", "Rapid Spin", "Headlong Rush", "Close Combat"]),
    mon("Buzzwole", "Leftovers", "Beast Boost", "Careful", ["Bulk Up", "Drain Punch", "Leech Life", "Ice Punch"]),
    mon("Machamp", "Choice Band", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"]),
    mon("Lucario", "Choice Specs", "Inner Focus", "Timid", ["Dark Pulse", "Aura Sphere", "Flash Cannon", "Vacuum Wave"]),
    mon("Flamigo", "Life Orb", "Scrappy", "Jolly", ["Brave Bird", "Close Combat", "U Turn", "Roost"]),
    mon("Medicham", "Medichamite", "Huge Power", "Jolly", ["High Jump Kick", "Zen Headbutt", "Ice Punch", "Bullet Punch"]),
]

# Prankster Grimmsnarl sets Reflect and Light Screen, then Parting Shots into a sweeper. Focus Sash
# Weavile Swords Dances and has Ice Shard for Dragons; Booster Energy Iron Jugulis and Choice Scarf
# Moxie Krookodile attack behind the screens, then Mega Houndoom's Dark Aura Nasty Plot. Supreme
# Overlord Kingambit comes last, stronger for every fallen ally.
KAREN_2 = [
    mon("Grimmsnarl", "Light Clay", "Prankster", "Careful", ["Reflect", "Light Screen", "Parting Shot", "Spirit Break"],
        "252 HP / 4 Atk / 252 SpD"),
    mon("Weavile", "Focus Sash", "Infiltrator", "Jolly", ["Swords Dance", "Knock Off", "Triple Axel", "Ice Shard"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Iron Jugulis", "Booster Energy", "Quark Drive", "Timid", ["Hurricane", "Dark Pulse", "Earth Power", "Flamethrower"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Krookodile", "Choice Scarf", "Moxie", "Jolly", ["Earthquake", "Knock Off", "Close Combat", "Stone Edge"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Houndoom", "Houndoominite", "Flash Fire", "Timid", ["Nasty Plot", "Dark Pulse", "Fire Blast", "Sludge Bomb"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Kingambit", "Leftovers", "Supreme Overlord", "Adamant", ["Kowtow Cleave", "Sucker Punch", "Iron Head", "Low Kick"],
        "252 HP / 252 Atk / 4 SpD"),
]

# Ting-Lu sets Stealth Rock, halves HP with Ruination and Heavy Slams Fairies; it and Chien-Pao
# weaken the player with their Ruin abilities. Protean Meowscarada's Play Rough hits Fighting
# types, Incineroar Fake Outs and Parting Shots, Nasty Plot Galarian Moltres sweeps, and Mega
# Tyranitar Dragon Dances to finish.
KAREN_POSTOBC = [
    mon("Ting Lu", "Leftovers", "Vessel Of Ruin", "Careful", ["Stealth Rock", "Ruination", "Earthquake", "Heavy Slam"]),
    mon("Chien Pao", "Life Orb", "Sword Of Ruin", "Jolly", ["Swords Dance", "Icicle Crash", "Sucker Punch", "Sacred Sword"]),
    mon("Meowscarada", "Choice Band", "Protean", "Jolly", ["Flower Trick", "Knock Off", "Play Rough", "U Turn"]),
    mon("Incineroar", "Heavy Duty Boots", "Intimidate", "Careful", ["Fake Out", "Knock Off", "Flare Blitz", "Parting Shot"]),
    mon("Moltres Galar", "Heavy Duty Boots", "Berserk", "Timid", ["Nasty Plot", "Fiery Wrath", "Air Slash", "Agility"]),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Jolly", ["Dragon Dance", "Stone Edge", "Knock Off", "Earthquake"]),
]

# Light Clay Latias sets Reflect and Light Screen and Thunder Waves the fastest threat. Choice Specs
# Hydreigon and Choice Scarf Haxorus break walls and revenge-kill (Flash Cannon, Poison Jab for
# Fairies); Booster Energy Gouging Fire takes Ice and Fairy hits. Mega Salamence Dragon Dances
# behind the screens; Choice Band Dragonite's Extreme Speed closes.
LANCE_2 = [
    mon("Latias", "Light Clay", "Levitate", "Timid", ["Reflect", "Light Screen", "Draco Meteor", "Thunder Wave"],
        "252 HP / 4 SpA / 252 Spe"),
    mon("Hydreigon", "Choice Specs", "Levitate", "Timid", ["Draco Meteor", "Dark Pulse", "Flash Cannon", "Fire Blast"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Gouging Fire", "Booster Energy", "Protosynthesis", "Adamant", ["Flare Blitz", "Dragon Claw", "Earthquake", "Morning Sun"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Haxorus", "Choice Scarf", "Mold Breaker", "Jolly", ["Outrage", "Earthquake", "Close Combat", "Poison Jab"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Salamence", "Salamencite", "Intimidate", "Adamant", ["Dragon Dance", "Double Edge", "Earthquake", "Roost"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Dragonite", "Choice Band", "Multiscale", "Adamant", ["Extreme Speed", "Outrage", "Earthquake", "Iron Head"],
        "252 HP / 252 Atk / 4 Def"),
]

# Sturdy Archaludon sets Stealth Rock, its Custap Berry buying a last move; Booster Energy Walking
# Wake hits hard specially and Choice Band Baxcalibur brings Ice for opposing Dragons. Dragonite has
# Extreme Speed and Roost, Choice Specs Noivern's Draco Meteor and Hurricane break walls, and Mega
# Garchomp Swords Dances last.
LANCE_POSTOBC = [
    mon("Archaludon", "Custap Berry", "Sturdy", "Modest", ["Stealth Rock", "Draco Meteor", "Flash Cannon", "Thunderbolt"],
        ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Baxcalibur", "Choice Band", "Thermal Exchange", "Jolly", ["Glaive Rush", "Icicle Crash", "Earthquake", "Ice Shard"]),
    mon("Walking Wake", "Booster Energy", "Protosynthesis", "Timid", ["Surf", "Draco Meteor", "Flamethrower", "Flip Turn"]),
    mon("Dragonite", "Heavy-Duty Boots", "Multiscale", "Adamant", ["Extreme Speed", "Dual Wingbeat", "Earthquake", "Roost"]),
    mon("Noivern", "Choice Specs", "Infiltrator", "Timid", ["Draco Meteor", "Air Slash", "Flamethrower", "U-turn"]),
    mon("Charizard", "Charizardite X", "Blaze", "Jolly", ["Dragon Dance", "Flare Blitz", "Dragon Claw", "Thunder Punch"]),
]

# A temple bell, a haunted stump and the tower's Bellsprout. Bronzor leads with Stealth Rock,
# Rock Tomb for the Fire and Flying types and Light Screen; Heatproof and the Eviolite take
# Fire moves. Phantump burns for Hex and Leech Seeds; Weepinbell, the ace, puts one to sleep
# and heals with Strength Sap.
LI = [
    mon("Bronzor", "Eviolite", "Heatproof", "Relaxed", ["Stealth Rock", "Rock Tomb", "Payback", "Light Screen"]),
    mon("Phantump", "Eviolite", "Natural Cure", "Sassy", ["Will O Wisp", "Hex", "Leech Seed", "Horn Leech"]),
    mon("Weepinbell", "Liechi Berry", "Gluttony", "Adamant", ["Sleep Powder", "Bullet Seed", "Poison Jab", "Strength Sap"]),
]

# The rival's 6th battle: Mt. Moon, his Victory Road six grown up: Boots Crobat Taunts and U-turns,
# Life Orb Weavile
# strips items and has Ice Shard, Gengar burns the Fighting types Weavile and Tyranitar fear.
# Guts Ursaluna (his Ursaring evolved) and Dragon Dance Mega Tyranitar break walls;
# Choice Specs Typhlosion closes with Eruption.
RIVAL_TEAM[6] = [
    mon("Crobat", "Heavy Duty Boots", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Taunt"],
        "252 Atk / 4 SpD / 252 Spe"),
    mon("Weavile", "Life Orb", "Infiltrator", "Jolly", ["Knock Off", "Triple Axel", "Ice Shard", "Low Kick"],
        "252 Atk / 4 SpD / 252 Spe"),
    mon("Gengar", "Life Orb", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Dazzling Gleam", "Will O Wisp"],
        "252 SpA / 4 SpD / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    mon("Ursaluna", "Flame Orb", "Guts", "Adamant", ["Facade", "Headlong Rush", "Ice Punch", "Fire Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Jolly", ["Dragon Dance", "Stone Edge", "Knock Off", "Ice Punch"],
        "252 Atk / 4 SpD / 252 Spe"),
]
RIVAL_STARTER[6] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Specs", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Scorching Sands"],
                     "252 SpA / 4 SpD / 252 Spe", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
    "TOTODILE": mon("Feraligatr", "Mystic Water", "Sheer Force", "Jolly", ["Dragon Dance", "Liquidation", "Ice Punch", "Crunch"],
                    "252 Atk / 4 SpD / 252 Spe"),
    "CHIKORITA": mon("Meganium", "Leftovers", "Triage", "Calm", ["Giga Drain", "Leech Seed", "Earth Power", "Synthesis"],
                     "252 HP / 252 SpA / 4 SpD", ivs="31 HP / 0 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe"),
}

# The rival's 7th battle: Indigo Plateau, his best: Focus Sash Crobat sets Tailwind and Taunts,
# Weavile has Fake Out
# and Ice Shard, Choice Specs Gengar breaks the walls his physical attackers can't. Booster
# Energy Roaring Moon Dragon Dances (Iron Head for Fairies), Mega Tyranitar lays Stealth Rock;
# Choice Scarf Typhlosion's Eruption closes.
RIVAL_TEAM[7] = [
    mon("Crobat", "Focus Sash", "Infiltrator", "Jolly", ["Tailwind", "Taunt", "Brave Bird", "U Turn"],
        "252 Atk / 4 SpD / 252 Spe"),
    mon("Weavile", "Life Orb", "Infiltrator", "Jolly", ["Fake Out", "Knock Off", "Triple Axel", "Ice Shard"],
        "252 Atk / 4 SpD / 252 Spe"),
    mon("Gengar", "Choice Specs", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Focus Blast", "Thunderbolt"],
        "252 SpA / 4 SpD / 252 Spe"),
    mon("Roaring Moon", "Booster Energy", "Protosynthesis", "Jolly", ["Dragon Dance", "Knock Off", "Acrobatics", "Iron Head"],
        "252 Atk / 4 SpD / 252 Spe"),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Adamant", ["Stealth Rock", "Stone Edge", "Crunch", "Earthquake"],
        "252 HP / 252 Atk / 4 SpD"),
]
RIVAL_STARTER[7] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Scorching Sands"],
    "252 SpA / 4 SpD / 252 Spe"),
    "TOTODILE": mon("Feraligatr", "Life Orb", "Sheer Force", "Adamant", ["Swords Dance", "Liquidation", "Ice Punch", "Aqua Jet"],
    "252 HP / 252 Atk / 4 SpD"),
    "CHIKORITA": mon("Meganium", "Life Orb", "Triage", "Modest", ["Giga Drain", "Earth Power", "Dazzling Gleam", "Synthesis"],
    "252 HP / 252 SpA / 4 SpD"),
}

# Trainer -> (stage, bag items, Pokemon[, AI]). The stage is the earliest point in the game the
# battle can happen: its NORMAL level cap is every Pokemon's level.
TEAMS = {
    "TRAINER_BROCK_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", BROCK),
    "TRAINER_MISTY_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", MISTY),
    "TRAINER_LTSURGE_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", LT_SURGE),
    "TRAINER_ERIKA_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", ERIKA),
    "TRAINER_JANINE_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", JANINE),
    "TRAINER_SABRINA_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", SABRINA),
    "TRAINER_BLAINE_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", BLAINE),
    "TRAINER_BLUE_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", BLUE),
    "TRAINER_RED_HNS": (KANTO_CHAMPION, RED_ITEMS, RED_SIX, RED_AI),
    "TRAINER_RED_POSTOBC_HNS": (KANTO_CHAMPION, RED_ITEMS, RED_SIX, RED_AI),
    "TRAINER_PETREL_1_HNS": (4, "Full Restore / Full Restore", PETREL_1),
    "TRAINER_ARIANA_1_HNS": (4, "Full Restore / Full Restore", ARIANA_1),
    "TRAINER_PROTON_2_HNS": (7, "Full Restore / Full Restore", PROTON_2),
    "TRAINER_PETREL_2_HNS": (7, "Full Restore / Full Restore", PETREL_2),
    "TRAINER_ARIANA_2_HNS": (7, "Full Restore / Full Restore", ARIANA_2),
    "TRAINER_ARCHER_HNS": (7, "Full Restore / Full Restore", ARCHER),
    "TRAINER_WILL_1_HNS": (8, "Full Restore / Full Restore", WILL),
    "TRAINER_KOGA_1_HNS": (8, "Full Restore / Full Restore", KOGA),
    "TRAINER_BRUNO_1_HNS": (8, "Full Restore / Full Restore", BRUNO),
    "TRAINER_KAREN_1_HNS": (8, "Full Restore / Full Restore", KAREN),
    "TRAINER_LANCE_1_HNS": (8, "Full Restore / Full Restore", LANCE),
    "TRAINER_PROTON_1_HNS": (1, "Super Potion", PROTON_1),
    "TRAINER_FALKNER_1_HNS": (0, "", FALKNER),
    "TRAINER_BUGSY_1_HNS": (1, "Potion / Potion", BUGSY),
    "TRAINER_EUSINE_HNS": (4, "Full Restore / Full Restore", EUSINE),
    "TRAINER_WHITNEY_1_HNS": (2, "Potion", WHITNEY),
    "TRAINER_MORTY_1_HNS": (3, "Hyper Potion / Hyper Potion", MORTY),
    "TRAINER_CHUCK_1_HNS": (4, "Hyper Potion / Hyper Potion", CHUCK),
    "TRAINER_CHUCK_1_2_HNS": (5, "Full Restore / Full Restore", CHUCK_1_2),
    "TRAINER_CHUCK_1_3_HNS": (6, "Full Restore / Full Restore", CHUCK_1_3),
    "TRAINER_JASMINE_1_HNS": (4, "Hyper Potion / Hyper Potion", JASMINE),
    "TRAINER_JASMINE_1_2_HNS": (5, "Full Restore / Full Restore", JASMINE_1_2),
    "TRAINER_JASMINE_1_3_HNS": (6, "Full Restore / Full Restore", JASMINE_1_3),
    "TRAINER_PRYCE_1_HNS": (4, "Hyper Potion / Hyper Potion", PRYCE),
    "TRAINER_PRYCE_1_2_HNS": (5, "Full Restore / Full Restore", PRYCE),
    "TRAINER_PRYCE_1_3_HNS": (6, "Full Restore / Full Restore", PRYCE),
    "TRAINER_CLAIR_1_HNS": (7, "Full Restore / Full Restore", CLAIR),
}
TEAMS.update({
    "TRAINER_FALKNER_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", FALKNER_2),
    "TRAINER_BUGSY_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", BUGSY_2),
    "TRAINER_WHITNEY_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", WHITNEY_2),
    "TRAINER_MORTY_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", MORTY_2),
    "TRAINER_CHUCK_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", CHUCK_2),
    "TRAINER_JASMINE_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", JASMINE_2),
    "TRAINER_PRYCE_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", PRYCE_2),
    "TRAINER_CLAIR_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", CLAIR_2),
    "TRAINER_FALKNER_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", FALKNER_POSTOBC),
    "TRAINER_BUGSY_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", BUGSY_POSTOBC),
    "TRAINER_WHITNEY_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", WHITNEY_POSTOBC),
    "TRAINER_MORTY_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", MORTY_POSTOBC),
    "TRAINER_CHUCK_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", CHUCK_POSTOBC),
    "TRAINER_JASMINE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", JASMINE_POSTOBC),
    "TRAINER_PRYCE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", PRYCE_POSTOBC),
    "TRAINER_CLAIR_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", CLAIR_POSTOBC),
    "TRAINER_BROCK_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", BROCK_POSTOBC),
    "TRAINER_MISTY_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", MISTY_POSTOBC),
    "TRAINER_LTSURGE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", LTSURGE_POSTOBC),
    "TRAINER_ERIKA_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", ERIKA_POSTOBC),
    "TRAINER_JANINE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", JANINE_POSTOBC),
    "TRAINER_SABRINA_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", SABRINA_POSTOBC),
    "TRAINER_BLAINE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", BLAINE_POSTOBC),
    "TRAINER_BLUE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", BLUE_POSTOBC),
    "TRAINER_WILL_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", WILL_2),
    "TRAINER_WILL_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", WILL_POSTOBC),
    "TRAINER_KOGA_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", KOGA_2),
    "TRAINER_KOGA_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", KOGA_POSTOBC),
    "TRAINER_BRUNO_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", BRUNO_2),
    "TRAINER_BRUNO_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", BRUNO_POSTOBC),
    "TRAINER_KAREN_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", KAREN_2),
    "TRAINER_KAREN_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", KAREN_POSTOBC),
    "TRAINER_LANCE_2_HNS": (JOHTO_CHAMPION, "Full Restore / Full Restore", LANCE_2),
    "TRAINER_LANCE_POSTOBC_HNS": (KANTO_CHAMPION, "Full Restore / Full Restore / Full Restore", LANCE_POSTOBC),
    "TRAINER_LI_HNS": (0, "", LI),
})
TEAMS.update(SIDE_BATTLES)
TEAMS.update({tid: (8, "", mons) for tid, mons in KIMONO.items()})
TEAMS.update({tid: (stage, "", mons) for tid, (stage, mons) in ROUTE_BOSSES.items()})
for _n, _stage, _items in ((2, 2, "Super Potion"), (3, 3, "Super Potion / Super Potion"),
                           (4, 7, "Full Restore / Full Restore"), (5, 8, "Full Restore / Full Restore"),
                           (6, JOHTO_CHAMPION, "Full Restore / Full Restore"),
                           (7, JOHTO_CHAMPION, "Full Restore / Full Restore")):
    for _starter, _ace in RIVAL_STARTER[_n].items():
        TEAMS[f"TRAINER_RIVAL_{_starter}_{_n}_HNS"] = (_stage, _items, RIVAL_TEAM[_n] + [_ace])

# Heart & Soul's own teams for the other bosses: only their levels change, to the cap of the stage.
#   Sprout Tower (Li), Falkner, the rival in Cherrygrove: no badges. Bugsy: 1. Whitney: 2. Eusine in
#   Cianwood: 4 (Cianwood needs Surf, the 4th badge's field move). The rival on Mt. Moon and at the
#   Indigo Plateau, the Johto leaders' rematches in the Fighting Dojo and the Kanto League (the
#   Elite Four's and Lance's _2 teams) come after the Johto League; every _POSTOBC rematch after
#   the Kanto League. Not here: the bonus storylines' trainers (New Sinjoh, Melemele, Steven,
#   Giovanni), who are at or above the cap where they can first be fought, and the unused or
#   debug-only teams (validate.py lists them).
JOHTO_LEADERS = ["FALKNER", "BUGSY", "WHITNEY", "MORTY", "CHUCK", "JASMINE", "PRYCE", "CLAIR"]
KANTO_LEADERS = ["BROCK", "MISTY", "LTSURGE", "ERIKA", "JANINE", "SABRINA", "BLAINE", "BLUE"]
ELITE_FOUR = ["WILL", "KOGA", "BRUNO", "KAREN", "LANCE"]
STARTERS = ["CYNDAQUIL", "TOTODILE", "CHIKORITA"]
LEVEL_ONLY = {}
LEVEL_ONLY.update({f"TRAINER_RIVAL_{s}_1_HNS": 0 for s in STARTERS})

# Every boss and its stage
STAGES = {tid: entry[0] for tid, entry in TEAMS.items()}
STAGES.update(LEVEL_ONLY)

# The other teams made for a stage (D56): the Ace Trainers (tools/crystal_imperium/ace_trainers.py
# writes their parties) and Heart & Soul's Cooltrainers with competitive teams. Like the bosses, they
# keep their Pokemon as made until the player's cap is above their stage's; unlike a boss, a team is
# never above the player's cap, even met before its stage.
# (Their stage 9 is the Johto League won, 10 the Kanto League.)
def stage_of(stage):
    """A stage as ace_trainer_data.py may write it (0-8, 9 for the Johto League won, 10 for the Kanto
    League) as the other tables write it."""
    return {9: JOHTO_CHAMPION, 10: KANTO_CHAMPION}.get(stage, stage)


TEAM_STAGES = {f"TRAINER_ACE_{a['key']}_HNS": a["stage"] for a in ace_trainer_data.ACES}
TEAM_STAGES.update(ace_trainer_data.UPGRADE_STAGES)
TEAM_STAGES = {tid: stage_of(stage) for tid, stage in TEAM_STAGES.items()}


def designed_parties():
    """Every team designed in the tables, trainer -> its Pokemon in party order: the bosses' (TEAMS), the Ace
    Trainers' and the upgraded Cooltrainers' (ace_trainer_data.py)."""
    out = {tid: entry[2] for tid, entry in TEAMS.items()}
    out.update({f"TRAINER_ACE_{a['key']}_HNS": a["team"] for a in ace_trainer_data.ACES})
    out.update(ace_trainer_data.UPGRADES)
    return out


def raised_items():
    """[(trainer, index in its party data, item)] for every designed Pokemon with a raised_item."""
    return [(tid, i, m["raised_item"]) for tid, mons in sorted(designed_parties().items())
            for i, m in enumerate(mons) if m.get("raised_item")]


def render(tid, header, stage, items, mons, ai=BOSS_AI):
    lines = []
    for line in header.splitlines():
        if line.startswith("AI:"):
            line = "AI: " + ai
        elif line.startswith("Items:"):
            if not items:
                continue
            line = "Items: " + items
        lines.append(line)
    if items and not any(l.startswith("Items:") for l in lines):
        lines.append("Items: " + items)
    return "\n".join(lines) + "\n" + team_kit.render_mons(mons, cap(stage))


def set_levels(block, level):
    """A party block with every Pokemon's Level line set to level."""
    header, sep, body = block.partition("\n\n")
    mons = re.split(r"(\n\s*\n)", body)
    for i in range(0, len(mons), 2):
        lines = mons[i].split("\n")
        if not lines[0].strip():
            continue
        levels = [j for j, l in enumerate(lines) if re.match(r"\s*Level\s*:", l)]
        if levels:
            lines[levels[0]] = f"Level: {level}"
        else:
            lines.insert(1, f"Level: {level}")
        mons[i] = "\n".join(lines)
    return header + sep + "".join(mons)


def apply(text):
    blocks = re.split(r"(?m)^(?==== )", text)
    seen = set()
    for i, block in enumerate(blocks):
        m = re.match(r"=== (\w+) ===", block)
        if not m or m.group(1) not in STAGES:
            continue
        tid = m.group(1)
        seen.add(tid)
        if tid in TEAMS:
            header = block.split("\n\n", 1)[0]
            blocks[i] = render(tid, header, *TEAMS[tid]) + "\n"
        else:
            blocks[i] = set_levels(block, cap(LEVEL_ONLY[tid]))
    missing = set(STAGES) - seen
    if missing:
        sys.exit(f"trainers not found: {sorted(missing)}")
    return "".join(blocks)


def stage_constant(stage):
    """A stage as src/data/level_cap_bosses.h spells it (include/caps.h)."""
    return {JOHTO_CHAMPION: "LEVEL_CAP_STAGE_JOHTO_CHAMPION", KANTO_CHAMPION: "LEVEL_CAP_STAGE_KANTO_CHAMPION"}.get(stage, str(stage))


def boss_list():
    out = ("// Generated by tools/crystal_imperium/boss_teams.py: do not edit.\n"
           "// Every boss and its stage, the earliest point in the game its battle can happen (a badge count or\n"
           "// LEVEL_CAP_STAGE_*). CreateNPCTrainerParty (src/battle_main.c) puts all of a boss's Pokemon at\n"
           "// GetBossLevel(stage), the player's level cap (DECISIONS.md D21).\n"
           "static const struct LevelCapBoss\n{\n    u16 trainerId;\n    u8 stage;\n} sLevelCapBosses[] =\n{\n")
    out += "".join(f"    {{{tid}, {stage_constant(STAGES[tid])}}},\n" for tid in sorted(STAGES))
    out += "};\n\n"
    out += ("// The other teams made for a stage of the game (D56): the Ace Trainers and Heart & Soul's\n"
            "// Cooltrainers with competitive teams, every Pokemon at its stage's cap in the party data, and the\n"
            "// stage. Like any trainer's, they are at the player's level cap; like a boss's, they keep their\n"
            "// Pokemon as made unless that cap is above their party data's levels. A rematch tier listed here is\n"
            "// offered from its stage on (GetMaxRematchStageForBadges, src/battle_setup.c).\n"
            "static const struct LevelCapBoss sTeamsMadeForStage[] =\n{\n")
    out += "".join(f"    {{{tid}, {stage_constant(TEAM_STAGES[tid])}}},\n" for tid in sorted(TEAM_STAGES))
    out += "};\n\n"
    out += ("// The named Eviolite species (tools/crystal_imperium/team_kit.py): raised to a later stage's cap, a\n"
            "// team made for a stage keeps one of these as made while it holds an Eviolite, and a Pikachu while it\n"
            "// holds a Light Ball; any other Pokemon evolves as any trainer's does (GetTrainerMonEvolvedSpecies).\n"
            "static const u16 sKeptUnevolvedSpecies[] =\n{\n")
    out += "".join(f"    {team_kit.species_constant(sp)},\n" for sp in team_kit.NAMED_EVIOLITE)
    out += "};\n\n"
    out += ("// The item a designed Pokemon holds instead once it has evolved in a battle fought after its team's\n"
            "// stage (mon()'s raised_item): the trainer, the Pokemon's index in the party data, the item.\n"
            "static const struct RaisedItem\n{\n    u16 trainerId;\n    u8 monIndex;\n    u16 item;\n} sRaisedItems[] =\n{\n")
    out += "".join(f"    {{{tid}, {i}, {team_kit.constant('ITEM', item)}}},\n" for tid, i, item in raised_items())
    return out + "};\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = open(PARTY, encoding="utf-8").read()
    new = apply(text)
    old_list = open(BOSS_LIST, encoding="utf-8").read() if os.path.exists(BOSS_LIST) else ""
    new_list = boss_list()
    if args.check:
        stale = [os.path.relpath(p, ROOT) for p, a, b in ((PARTY, text, new), (BOSS_LIST, old_list, new_list)) if a != b]
        if stale:
            print(f"{', '.join(stale)} out of date: run tools/crystal_imperium/boss_teams.py")
            return 1
        return 0
    if new != text:
        open(PARTY, "w", encoding="utf-8").write(new)
        print(f"updated {len(TEAMS)} boss parties and the levels of {len(LEVEL_ONLY)} more")
    if new_list != old_list:
        open(BOSS_LIST, "w", encoding="utf-8").write(new_list)
        print(f"wrote {os.path.relpath(BOSS_LIST, ROOT)} ({len(STAGES)} bosses, {len(TEAM_STAGES)} other teams made for a "
              f"stage, {len(team_kit.NAMED_EVIOLITE)} named Eviolite species, {len(raised_items())} raised items)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
