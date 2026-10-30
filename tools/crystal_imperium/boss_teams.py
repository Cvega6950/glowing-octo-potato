#!/usr/bin/env python3
"""Crystal Imperium boss teams (Emerald Imperium-style): writes the parties below into
src/data/trainers_hns.party, keeping each trainer's header (name, class, picture, music, mugshot)
and replacing its AI, bag items and Pokemon. Heart & Soul's own teams for the other bosses
(LEVEL_ONLY) keep their Pokemon and only get their levels set. The list of every boss goes to
src/data/level_cap_bosses.h for the battle code.

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
  * IVs are 31 (Minimal Grinding gives every Pokemon 31 IVs anyway; this covers games with it off)
  * from the 5th Gym on, each boss has one Mega Evolution, normally the ace
  * Red is the hardest battle in the game (D27): level 100, competitive EVs (which he keeps under
    Minimal Grinding), the prediction AI and the most Full Restores; validate.py checks it
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PARTY = os.path.join(ROOT, "src", "data", "trainers_hns.party")
BOSS_LIST = os.path.join(ROOT, "src", "data", "level_cap_bosses.h")

BOSS_AI = "Smart Trainer / Ace Pokemon / HP Aware"
RED_AI = "Smart Trainer / Prediction / Ace Pokemon / HP Aware"

# Stages after the eighth badge: the Johto League won (FLAG_IS_CHAMPION; cap 90 for all of Kanto)
# and the Kanto League won (FLAG_IS_KANTO_CHAMPION; no cap left)
JOHTO_CHAMPION = "Johto Champion"
KANTO_CHAMPION = "Kanto Champion"
MAX_LEVEL = 100

# Moves whose power comes from friendship. A trainer's Pokemon has its party entry's Happiness,
# 0 when it has none (CreateNPCTrainerPartyFromTrainer), which would leave Return at power 1.
FRIENDSHIP_MOVES = {"Return", "Pika Papow", "Veevee Volley"}
FULL_FRIENDSHIP = 255


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


def mon(species, item, ability, nature, moves, evs=None):
    return {"species": species, "item": item, "ability": ability, "nature": nature, "moves": moves, "evs": evs}


# --- Falkner (1st Gym, no badges: cap 15) -----------------------------------------------------------
# Heart & Soul's Pidgey, Rookidee and Noctowl, and since 0.8.0 a full six: Magic Bounce Natu,
# Gale Wings Fletchling and Prankster Murkrow (Thunder Wave) for Speed control.
FALKNER = [
    mon("Pidgey", "Oran Berry", "No Guard", "Timid", ["Tailwind", "Gust", "Sand Attack", "Quick Attack"]),
    mon("Natu", "Eviolite", "Magic Bounce", "Bold", ["Night Shade", "Peck", "Confuse Ray", "Wish"]),
    mon("Fletchling", "Eviolite", "Gale Wings", "Jolly", ["Acrobatics", "Quick Attack", "Agility", "Flail"]),
    mon("Murkrow", "Eviolite", "Prankster", "Calm", ["Foul Play", "Peck", "Thunder Wave", "Haze"]),
    mon("Rookidee", "Eviolite", "Frisk", "Adamant", ["Hone Claws", "Power Trip", "Peck", "Rock Smash"]),
    mon("Noctowl", "Sitrus Berry", "Tinted Lens", "Modest", ["Hypnosis", "Air Cutter", "Reflect", "Mud Slap"]),
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
    mon("Clefairy", "Eviolite", "Magic Guard", "Bold", ["Double Slap", "Metronome", "Encore", "Charm"]),
    mon("Aipom", "Silk Scarf", "Pickup", "Jolly", ["Fake Out", "Double Hit", "U Turn", "Astonish"]),
    mon("Furret", "Sitrus Berry", "Frisk", "Jolly", ["Double Edge", "Sucker Punch", "U Turn", "Coil"]),
    mon("Stantler", "Sitrus Berry", "Intimidate", "Adamant", ["Hypnosis", "Stomp", "Zen Headbutt", "Take Down"]),
    mon("Girafarig", "Twisted Spoon", "Inner Focus", "Modest", ["Psybeam", "Shadow Ball", "Thunderbolt", "Nasty Plot"]),
    mon("Miltank", "Leftovers", "Scrappy", "Impish", ["Rollout", "Body Slam", "Milk Drink", "Attract"]),
]

# --- Morty (4th Gym, 3 badges: cap 42) ------------------------------------------------------------
MORTY = [
    mon("Sableye", "Sitrus Berry", "Prankster", "Careful", ["Will O Wisp", "Knock Off", "Night Shade", "Recover"]),
    mon("Misdreavus", "Eviolite", "Levitate", "Timid", ["Hex", "Thunder Wave", "Dazzling Gleam", "Pain Split"]),
    mon("Drifblim", "Sitrus Berry", "Unburden", "Modest", ["Shadow Ball", "Air Slash", "Thunderbolt", "Calm Mind"]),
    mon("Marowak Alola", "Thick Club", "Lightning Rod", "Adamant", ["Shadow Bone", "Fire Punch", "Bonemerang", "Thunder Punch"]),
    mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Shadow Claw", "Play Rough", "Shadow Sneak", "Swords Dance"]),
    mon("Gengar", "Spell Tag", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Hypnosis"]),
]

# --- Chuck, Jasmine, Pryce (5th to 7th Gym in any order) ------------------------------------------
# HnS picks the party by how many of the three the player has beaten: _1 with 4 badges (cap 50),
# _1_2 with 5 (cap 58), _1_3 with 6 (cap 66).
CHUCK = [
    mon("Hitmontop", "Sitrus Berry", "Intimidate", "Adamant", ["Fake Out", "Triple Kick", "Sucker Punch", "Rock Slide"]),
    mon("Breloom", "Focus Sash", "Technician", "Jolly", ["Mach Punch", "Bullet Seed", "Rock Tomb", "Spore"]),
    mon("Hawlucha", "White Herb", "Unburden", "Jolly", ["High Jump Kick", "Acrobatics", "Swords Dance", "Roost"]),
    mon("Primeape", "Eviolite", "Defiant", "Jolly", ["Rage Fist", "Drain Punch", "U Turn", "Bulk Up"]),
    mon("Poliwrath", "Leftovers", "Water Absorb", "Adamant", ["Waterfall", "Dynamic Punch", "Mind Reader", "Ice Punch"]),
    mon("Heracross", "Heracronite", "Guts", "Jolly", ["Pin Missile", "Rock Blast", "Close Combat", "Bullet Seed"]),
]
JASMINE = [
    mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Drill Peck", "Roost", "Whirlwind"]),
    mon("Magneton", "Eviolite", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Thunder Wave"]),
    mon("Bronzong", "Leftovers", "Levitate", "Relaxed", ["Gyro Ball", "Earthquake", "Hypnosis", "Stealth Rock"]),
    mon("Mawile", "Sitrus Berry", "Intimidate", "Adamant", ["Iron Head", "Play Rough", "Sucker Punch", "Swords Dance"]),
    mon("Scizor", "Metal Coat", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Swords Dance"]),
    mon("Steelix", "Steelixite", "Sturdy", "Impish", ["Gyro Ball", "Earthquake", "Rock Slide", "Curse"]),
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
    mon("Snover", "Eviolite", "Ice Body", "Modest", ["Icy Wind", "Razor Leaf", "Leech Seed", "Ice Shard"]),
    mon("Sneasel", "Eviolite", "Inner Focus", "Jolly", ["Fake Out", "Ice Shard", "Bite", "Quick Attack"]),
    mon("Spheal", "Eviolite", "Thick Fat", "Bold", ["Ice Ball", "Defense Curl", "Brine", "Yawn"]),
    mon("Cetoddle", "Eviolite", "Thick Fat", "Adamant", ["Ice Shard", "Ice Fang", "Bulldoze", "Body Slam"]),
    mon("Meditite", "Eviolite", "Huge Power", "Adamant", ["Force Palm", "Ice Punch", "Bullet Punch", "Detect"]),
    mon("Cryogonal", "Sitrus Berry", "Levitate", "Calm", ["Freeze Dry", "Icy Wind", "Recover", "Reflect"]),
]
#   Gardenia (2 badges, Ilex Forest): Cherrim's sun for Solar Beam, Weather Ball and a Harvest Dolliv;
#   from 4 badges her second team, with Mega Venusaur.
SIDE_GARDENIA = [
    mon("Sudowoodo", "Sitrus Berry", "Sturdy", "Adamant", ["Stealth Rock", "Rock Slide", "Sucker Punch", "Wood Hammer"]),
    mon("Cherrim", "Miracle Seed", "Flower Gift", "Modest", ["Sunny Day", "Solar Beam", "Weather Ball", "Growth"]),
    mon("Gloom", "Eviolite", "Chlorophyll", "Modest", ["Sleep Powder", "Giga Drain", "Sludge Bomb", "Moonblast"]),
    mon("Dolliv", "Sitrus Berry", "Harvest", "Bold", ["Energy Ball", "Earth Power", "Strength Sap", "Leech Seed"]),
    mon("Grotle", "Eviolite", "Shell Armor", "Adamant", ["Seed Bomb", "Bite", "Bulldoze", "Synthesis"]),
    mon("Roserade", "Black Sludge", "Natural Cure", "Timid", ["Giga Drain", "Sludge Bomb", "Dazzling Gleam", "Toxic Spikes"]),
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
    mon("Spiritomb", "Sitrus Berry", "Intimidate", "Careful", ["Will O Wisp", "Foul Play", "Shadow Sneak", "Sucker Punch"]),
    mon("Dusclops", "Eviolite", "Frisk", "Relaxed", ["Night Shade", "Trick Room", "Pain Split", "Ice Beam"]),
    mon("Cursola", "Life Orb", "Weak Armor", "Modest", ["Hex", "Earth Power", "Power Gem", "Strength Sap"]),
    mon("Zoroark Hisui", "Focus Sash", "Illusion", "Timid", ["Shadow Ball", "Hyper Voice", "Focus Blast", "Nasty Plot"]),
    mon("Banette", "Spell Tag", "Insomnia", "Adamant", ["Poltergeist", "Gunk Shot", "Knock Off", "Shadow Sneak"]),
    mon("Mismagius", "Wise Glasses", "Levitate", "Timid", ["Shadow Ball", "Mystical Fire", "Dazzling Gleam", "Nasty Plot"]),
]
#   Maylene (4 badges, Cianwood City): fast Fighting types and Mega Lucario.
SIDE_MAYLENE = [
    mon("Medicham", "Sitrus Berry", "Huge Power", "Jolly", ["Fake Out", "High Jump Kick", "Zen Headbutt", "Bullet Punch"]),
    mon("Mienshao", "Life Orb", "Regenerator", "Jolly", ["Drain Punch", "U Turn", "Knock Off", "Stone Edge"]),
    mon("Pawmot", "Shell Bell", "Iron Fist", "Jolly", ["Double Shock", "Close Combat", "Mach Punch", "Ice Punch"]),
    mon("Machamp", "Expert Belt", "No Guard", "Adamant", ["Dynamic Punch", "Knock Off", "Stone Edge", "Ice Punch"]),
    mon("Toxicroak", "Black Sludge", "Dry Skin", "Adamant", ["Drain Punch", "Sucker Punch", "Gunk Shot", "Swords Dance"]),
    mon("Lucario", "Lucarionite", "Inner Focus", "Jolly", ["Close Combat", "Meteor Mash", "Extreme Speed", "Swords Dance"]),
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
    mon("Bastiodon", "Leftovers", "Dauntless Shield", "Impish", ["Stealth Rock", "Iron Defense", "Body Press", "Roar"]),
    mon("Copperajah", "Sitrus Berry", "Heavy Metal", "Adamant", ["Heavy Slam", "Play Rough", "Superpower", "Earthquake"]),
    mon("Excadrill", "Focus Sash", "Mold Breaker", "Jolly", ["Iron Head", "Earthquake", "Rapid Spin", "Swords Dance"]),
    mon("Kingambit", "Black Glasses", "Supreme Overlord", "Adamant", ["Kowtow Cleave", "Iron Head", "Sucker Punch", "Swords Dance"]),
    mon("Corviknight", "Leftovers", "Pressure", "Impish", ["Brave Bird", "Body Press", "Bulk Up", "Roost"]),
    mon("Aggron", "Aggronite", "Sturdy", "Impish", ["Heavy Slam", "Earthquake", "Body Press", "Iron Defense"]),
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
    mon("Kilowattrel", "Choice Specs", "Volt Absorb", "Timid", ["Thunderbolt", "Hurricane", "Volt Switch", "Roost"]),
    mon("Bellibolt", "Leftovers", "Electromorphosis", "Bold", ["Discharge", "Muddy Water", "Slack Off", "Toxic"]),
    mon("Toxtricity", "Throat Spray", "Punk Rock", "Modest", ["Overdrive", "Boomburst", "Sludge Bomb", "Volt Switch"]),
    mon("Electrode Hisui", "Focus Sash", "Soundproof", "Timid", ["Volt Switch", "Leaf Storm", "Thunderbolt", "Taunt"]),
    mon("Mismagius", "Life Orb", "Levitate", "Timid", ["Shadow Ball", "Thunderbolt", "Nasty Plot", "Dazzling Gleam"]),
    mon("Ampharos", "Ampharosite", "Static", "Modest", ["Thunderbolt", "Dragon Pulse", "Focus Blast", "Volt Switch"]),
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
    mon("Komala", "Assault Vest", "Comatose", "Adamant", ["Wood Hammer", "Sucker Punch", "Earthquake", "Rapid Spin"]),
    mon("Dudunsparce", "Leftovers", "Serene Grace", "Bold", ["Hyper Drill", "Glare", "Roost", "Boomburst"]),
    mon("Staraptor", "Choice Band", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "Double Edge", "U Turn"]),
    mon("Porygon Z", "Choice Specs", "Adaptability", "Timid", ["Tri Attack", "Shadow Ball", "Ice Beam", "Thunderbolt"]),
    mon("Bewear", "Sitrus Berry", "Fluffy", "Adamant", ["Double Edge", "Close Combat", "Drain Punch", "Swords Dance"]),
    mon("Kangaskhan", "Kangaskhanite", "Scrappy", "Jolly", ["Fake Out", "Double Edge", "Earthquake", "Sucker Punch"]),
]
#   Ryme (Celadon City): Last Respects, Rage Fist, Gholdengo and Mega Gengar.
SIDE_RYME = [
    mon("Houndstone", "Choice Band", "Fluffy", "Adamant", ["Last Respects", "Body Press", "Play Rough", "Trick"]),
    mon("Annihilape", "Leftovers", "Defiant", "Adamant", ["Rage Fist", "Drain Punch", "Bulk Up", "Gunk Shot"]),
    mon("Ceruledge", "Life Orb", "Flash Fire", "Adamant", ["Bitter Blade", "Poltergeist", "Close Combat", "Swords Dance"]),
    mon("Gholdengo", "Choice Scarf", "Good As Gold", "Timid", ["Make It Rain", "Shadow Ball", "Nasty Plot", "Recover"]),
    mon("Dragapult", "Focus Sash", "Infiltrator", "Jolly", ["Dragon Darts", "Phantom Force", "U Turn", "Dragon Dance"]),
    mon("Gengar", "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Focus Blast", "Nasty Plot"]),
]
#   Tulip (Saffron City): Armor Tail Farigiraf against priority, Calm Mind and Mega Gardevoir.
SIDE_TULIP = [
    mon("Farigiraf", "Sitrus Berry", "Armor Tail", "Modest", ["Hyper Voice", "Psychic", "Nasty Plot", "Shadow Ball"]),
    mon("Espathra", "Life Orb", "Speed Boost", "Timid", ["Lumina Crash", "Dazzling Gleam", "Calm Mind", "Stored Power"]),
    mon("Florges", "Leftovers", "Natural Cure", "Calm", ["Moonblast", "Psychic", "Calm Mind", "Synthesis"]),
    mon("Hatterene", "Focus Sash", "Magic Bounce", "Quiet", ["Psychic", "Draining Kiss", "Mystical Fire", "Trick Room"]),
    mon("Gallade", "Choice Band", "Sharpness", "Jolly", ["Sacred Sword", "Psycho Cut", "Leaf Blade", "Swords Dance"]),
    mon("Gardevoir", "Gardevoirite", "Trace", "Timid", ["Hyper Voice", "Psyshock", "Focus Blast", "Calm Mind"]),
]
#   Grusha (Cinnabar Island): Alolan Ninetales' snow and Aurora Veil, Slush Rush and Mega Altaria.
SIDE_GRUSHA = [
    mon("Ninetales Alola", "Light Clay", "Snow Warning", "Timid", ["Aurora Veil", "Blizzard", "Moonblast", "Freeze Dry"]),
    mon("Frosmoth", "Heavy Duty Boots", "Ice Scales", "Timid", ["Quiver Dance", "Ice Beam", "Bug Buzz", "Giga Drain"]),
    mon("Beartic", "Life Orb", "Slush Rush", "Adamant", ["Icicle Crash", "Close Combat", "Aqua Jet", "Swords Dance"]),
    mon("Cetitan", "Sitrus Berry", "Slush Rush", "Adamant", ["Icicle Crash", "Earthquake", "Ice Shard", "Belly Drum"]),
    mon("Baxcalibur", "Loaded Dice", "Thermal Exchange", "Jolly", ["Glaive Rush", "Icicle Crash", "Earthquake", "Dragon Dance"]),
    mon("Altaria", "Altarianite", "Natural Cure", "Adamant", ["Hyper Voice", "Dragon Dance", "Earthquake", "Roost"]),
]
# --- Side battles: the postgame's visitors (D41), once the player has won the Kanto League ---------
# Level 100, when Red battles too. Red stays the hardest battle (D27): these have no EVs, the Ace AI
# without prediction and three Full Restores to his four.
POST_ITEMS = "Full Restore / Full Restore / Full Restore"
#   Cynthia (Ruins of Alph): her Platinum six, with Mega Garchomp.
POST_CYNTHIA = [
    mon("Spiritomb", "Leftovers", "Pressure", "Careful", ["Foul Play", "Will O Wisp", "Sucker Punch", "Pain Split"]),
    mon("Roserade", "Black Sludge", "Natural Cure", "Timid", ["Giga Drain", "Sludge Bomb", "Dazzling Gleam", "Toxic Spikes"]),
    mon("Togekiss", "Leftovers", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Nasty Plot", "Roost"]),
    mon("Lucario", "Life Orb", "Inner Focus", "Timid", ["Aura Sphere", "Flash Cannon", "Vacuum Wave", "Nasty Plot"]),
    mon("Milotic", "Leftovers", "Marvel Scale", "Bold", ["Scald", "Ice Beam", "Recover", "Haze"]),
    mon("Garchomp", "Garchompite", "Rough Skin", "Jolly", ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"]),
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
    2: {"CYNDAQUIL": mon("Quilava", "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Quick Attack", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", "Sitrus Berry", "Sheer Force", "Adamant", ["Ice Fang", "Bite", "Aqua Jet", "Scary Face"]),
        "CHIKORITA": mon("Bayleef", "Sitrus Berry", "Overgrow", "Bold", ["Razor Leaf", "Reflect", "Poison Powder", "Synthesis"])},
    3: {"CYNDAQUIL": mon("Quilava", "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Flame Charge", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", "Sitrus Berry", "Sheer Force", "Adamant", ["Aqua Tail", "Ice Fang", "Crunch", "Dragon Dance"]),
        "CHIKORITA": mon("Bayleef", "Sitrus Berry", "Overgrow", "Bold", ["Magical Leaf", "Leech Seed", "Reflect", "Synthesis"])},
}
RIVAL_TEAM = {
    2: [mon("Golbat", "Eviolite", "Infiltrator", "Jolly", ["Wing Attack", "Bite", "Confuse Ray", "Toxic"]),
        mon("Haunter", "Eviolite", "Levitate", "Timid", ["Hex", "Sludge Bomb", "Hypnosis", "Dazzling Gleam"]),
        mon("Magneton", "Eviolite", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Thunder Wave", "Volt Switch"]),
        mon("Larvitar", "Eviolite", "Guts", "Adamant", ["Rock Slide", "Bite", "Bulldoze", "Scary Face"]),
        mon("Sneasel", "Oran Berry", "Inner Focus", "Jolly", ["Faint Attack", "Ice Shard", "Quick Attack", "Icy Wind"])],
    3: [mon("Golbat", "Eviolite", "Infiltrator", "Jolly", ["Air Cutter", "Bite", "Confuse Ray", "Toxic"]),
        mon("Sneasel", "Razor Claw", "Inner Focus", "Jolly", ["Fake Out", "Ice Punch", "Faint Attack", "Ice Shard"]),
        mon("Haunter", "Eviolite", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Hypnosis", "Dazzling Gleam"]),
        mon("Weepinbell", "Eviolite", "Chlorophyll", "Adamant", ["Bullet Seed", "Poison Jab", "Sleep Powder", "Knock Off"]),
        mon("Larvitar", "Eviolite", "Guts", "Adamant", ["Rock Slide", "Crunch", "Bulldoze", "Dragon Dance"])],
}

# --- Team Rocket: Proton in Slowpoke Well (1 badge, cap 24) -----------------------------------------
PROTON_1 = [
    mon("Koffing", "Eviolite", "Levitate", "Bold", ["Sludge", "Will O Wisp", "Clear Smog", "Smokescreen"]),
    mon("Golbat", "Eviolite", "Infiltrator", "Jolly", ["Wing Attack", "Bite", "Confuse Ray", "Toxic"]),
    mon("Slowpoke", "Eviolite", "Regenerator", "Relaxed", ["Water Pulse", "Confusion", "Yawn", "Slack Off"]),
    mon("Grimer", "Eviolite", "Poison Touch", "Adamant", ["Poison Jab", "Shadow Sneak", "Disable", "Rock Tomb"]),
    mon("Raticate", "Silk Scarf", "Hustle", "Jolly", ["Super Fang", "Sucker Punch", "Crunch", "Quick Attack"]),
    mon("Houndour", "Charcoal", "Flash Fire", "Timid", ["Incinerate", "Snarl", "Smog", "Nasty Plot"]),
]

# --- Team Rocket: Rocket Hideout (4 badges at the earliest: the Lake of Rage needs Surf; cap 50) ------
PETREL_1 = [
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Weezing", "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Fire Blast"]),
    mon("Golbat", "Eviolite", "Infiltrator", "Jolly", ["Cross Poison", "Crunch", "Confuse Ray", "U Turn"]),
    mon("Houndoom", "Black Glasses", "Flash Fire", "Timid", ["Dark Pulse", "Flamethrower", "Sludge Bomb", "Nasty Plot"]),
    mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Rock Slide", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Drapion", "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_1 = [
    mon("Arbok", "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
    mon("Liepard", "Sitrus Berry", "Prankster", "Jolly", ["Foul Play", "Thunder Wave", "U Turn", "Encore"]),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Calm", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Gyarados", "Sitrus Berry", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Honchkrow", "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
]

# --- Eusine in Cianwood (4 badges at the earliest: cap 50) --------------------------------------------
# Heart & Soul's Politoed, Hypno and Electrode had 2 IVs and the basic AI. Since 0.8.0 a rain team
# of six around them: Drizzle Politoed, Thunder from Electrode and Lanturn.
EUSINE = [
    mon("Politoed", "Damp Rock", "Drizzle", "Bold", ["Scald", "Ice Beam", "Hypnosis", "Encore"]),
    mon("Hypno", "Leftovers", "Insomnia", "Calm", ["Psychic", "Thunder Wave", "Focus Blast", "Nasty Plot"]),
    mon("Electrode", "Focus Sash", "Galvanize", "Timid", ["Thunder", "Volt Switch", "Thunder Wave", "Explosion"]),
    mon("Lanturn", "Sitrus Berry", "Volt Absorb", "Modest", ["Thunder", "Scald", "Ice Beam", "Volt Switch"]),
    mon("Gengar", "Black Sludge", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Destiny Bond"]),
    mon("Starmie", "Life Orb", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Thunder", "Rapid Spin"]),
]

# --- Team Rocket: Radio Tower (7 badges, cap 75) ----------------------------------------------------
PROTON_2 = [
    mon("Muk", "Black Sludge", "Poison Touch", "Adamant", ["Gunk Shot", "Shadow Sneak", "Knock Off", "Curse"]),
    mon("Nidoqueen", "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    mon("Weezing", "Rocky Helmet", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
    mon("Nidoking", "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Thunderbolt"]),
    mon("Toxicroak", "Life Orb", "Dry Skin", "Jolly", ["Drain Punch", "Gunk Shot", "Sucker Punch", "Swords Dance"]),
    mon("Rhydon", "Eviolite", "Lightning Rod", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Swords Dance"]),
]
PETREL_2 = [
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Weezing Galar", "Black Sludge", "Neutralizing Gas", "Bold", ["Strange Steam", "Sludge Bomb", "Will O Wisp", "Pain Split"]),
    mon("Toxapex", "Black Sludge", "Regenerator", "Bold", ["Scald", "Toxic", "Recover", "Haze"]),
    mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Cloyster", "Focus Sash", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Shell Smash", "Liquidation"]),
    mon("Drapion", "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_2 = [
    mon("Arbok", "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
    mon("Skuntank", "Black Sludge", "Aftermath", "Adamant", ["Sucker Punch", "Crunch", "Poison Jab", "Fire Blast"]),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Calm", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Gyarados", "Sitrus Berry", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Honchkrow", "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
]
ARCHER = [
    mon("Porygon Z", "Choice Specs", "Adaptability", "Modest", ["Tri Attack", "Thunderbolt", "Ice Beam", "Shadow Ball"]),
    mon("Tauros", "Life Orb", "Intimidate", "Jolly", ["Double Edge", "Earthquake", "Rock Slide", "Zen Headbutt"]),
    mon("Crawdaunt", "Life Orb", "Adaptability", "Adamant", ["Crabhammer", "Knock Off", "Aqua Jet", "Swords Dance"]),
    mon("Slowbro", "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Calm Mind"]),
    mon("Bisharp", "Black Glasses", "Defiant", "Adamant", ["Sucker Punch", "Iron Head", "Knock Off", "Swords Dance"]),
    mon("Houndoom", "Houndoominite", "Flash Fire", "Timid", ["Fire Blast", "Dark Pulse", "Sludge Bomb", "Nasty Plot"]),
]

# --- Rival: Goldenrod Underground (7 badges, cap 75) and Victory Road (8 badges, cap 85) -------------
RIVAL_STARTER[4] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Extrasensory"]),
    "TOTODILE": mon("Feraligatr", "Life Orb", "Sheer Force", "Adamant", ["Liquidation", "Ice Punch", "Crunch", "Dragon Dance"]),
    "CHIKORITA": mon("Meganium", "Leftovers", "Overgrow", "Bold", ["Energy Ball", "Earth Power", "Leech Seed", "Synthesis"]),
}
RIVAL_STARTER[5] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Extrasensory"]),
    "TOTODILE": mon("Feraligatr", "Life Orb", "Sheer Force", "Adamant", ["Liquidation", "Ice Punch", "Crunch", "Dragon Dance"]),
    "CHIKORITA": mon("Meganium", "Leftovers", "Overgrow", "Bold", ["Energy Ball", "Earth Power", "Leech Seed", "Synthesis"]),
}
RIVAL_TEAM[4] = [
    mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Weavile", "Life Orb", "Pressure", "Jolly", ["Knock Off", "Ice Punch", "Ice Shard", "Low Kick"]),
    mon("Alakazam", "Focus Sash", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Calm Mind"]),
    mon("Victreebel", "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Sleep Powder"]),
    mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
]
RIVAL_TEAM[5] = [
    mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Weavile", "Life Orb", "Pressure", "Jolly", ["Knock Off", "Ice Punch", "Ice Shard", "Low Kick"]),
    mon("Victreebel", "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Sleep Powder"]),
    mon("Ursaring", "Flame Orb", "Guts", "Adamant", ["Facade", "Close Combat", "Crunch", "Swords Dance"]),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
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
    mon("Xatu", "Light Clay", "Magic Bounce", "Timid", ["Psychic", "Air Slash", "Roost", "Reflect"]),
    mon("Slowbro", "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Calm Mind"]),
    mon("Bronzong", "Leftovers", "Levitate", "Relaxed", ["Trick Room", "Gyro Ball", "Earthquake", "Stealth Rock"]),
    mon("Farigiraf", "Sitrus Berry", "Armor Tail", "Modest", ["Twin Beam", "Hyper Voice", "Shadow Ball", "Nasty Plot"]),
    mon("Gardevoir", "Choice Scarf", "Trace", "Timid", ["Moonblast", "Psychic", "Mystical Fire", "Focus Blast"]),
    mon("Alakazam", "Alakazite", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Calm Mind"]),
]
KOGA = [
    mon("Toxapex", "Black Sludge", "Regenerator", "Bold", ["Scald", "Toxic", "Recover", "Haze"]),
    mon("Muk Alola", "Black Sludge", "Poison Touch", "Adamant", ["Knock Off", "Poison Jab", "Ice Punch", "Shadow Sneak"]),
    mon("Toxicroak", "Life Orb", "Dry Skin", "Jolly", ["Gunk Shot", "Drain Punch", "Sucker Punch", "Swords Dance"]),
    mon("Venomoth", "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sludge Bomb", "Sleep Powder"]),
    mon("Beedrill", "Beedrillite", "Sniper", "Jolly", ["Poison Jab", "U Turn", "Drill Run", "Swords Dance"]),
    mon("Crobat", "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
]
BRUNO = [
    mon("Hitmontop", "Rocky Helmet", "Intimidate", "Impish", ["Fake Out", "Close Combat", "Sucker Punch", "Rapid Spin"]),
    mon("Steelix", "Leftovers", "Sturdy", "Impish", ["Heavy Slam", "Earthquake", "Stone Edge", "Stealth Rock"]),
    mon("Hitmonlee", "Life Orb", "Reckless", "Jolly", ["High Jump Kick", "Knock Off", "Blaze Kick", "Fake Out"]),
    mon("Hitmonchan", "Punching Glove", "Iron Fist", "Adamant", ["Drain Punch", "Ice Punch", "Thunder Punch", "Mach Punch"]),
    mon("Machamp", "Sitrus Berry", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"]),
    mon("Lucario", "Lucarionite", "Inner Focus", "Adamant", ["Close Combat", "Meteor Mash", "Extreme Speed", "Swords Dance"]),
]
KAREN = [
    mon("Umbreon", "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Wish", "Protect", "Toxic"]),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Bold", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Gengar", "Life Orb", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Focus Blast", "Nasty Plot"]),
    mon("Honchkrow", "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
    mon("Absol", "Absolite", "Super Luck", "Adamant", ["Knock Off", "Sucker Punch", "Play Rough", "Swords Dance"]),
    mon("Houndoom", "Black Glasses", "Flash Fire", "Timid", ["Fire Blast", "Dark Pulse", "Sludge Bomb", "Nasty Plot"]),
]
# Lance leads Mega Gyarados (tools/emurun/tests/mega_evolution.emu checks it Mega Evolves on turn 1)
# One Dragon Dance sweeper (Dragonite): with Mega Gyarados and Salamence also setting up, the
# prepared six of the bosses_m4 play test lost all of six tries. Charizard attacks instead of
# Roosting: with the Full Restores it outlasted every team built for Lance in the play tests.
LANCE = [
    mon("Gyarados", "Gyaradosite", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Thunder Wave"]),
    mon("Aerodactyl", "Focus Sash", "Unnerve", "Jolly", ["Stone Edge", "Earthquake", "Taunt", "Stealth Rock"]),
    mon("Charizard", "Charcoal", "Solar Power", "Timid", ["Fire Blast", "Air Slash", "Focus Blast", "Dragon Pulse"]),
    mon("Salamence", "Life Orb", "Intimidate", "Jolly", ["Outrage", "Earthquake", "Fire Fang", "Dual Wingbeat"]),
    mon("Garchomp", "Rocky Helmet", "Rough Skin", "Jolly", ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"]),
    mon("Dragonite", "Lum Berry", "Multiscale", "Adamant", ["Extreme Speed", "Dragon Dance", "Earthquake", "Outrage"]),
]

# --- Kanto Gym Leaders and Blue (after the Johto League: cap 90, any order) ------------------------
BROCK = [
    mon("Golem", "Leftovers", "Sturdy", "Adamant", ["Stealth Rock", "Earthquake", "Stone Edge", "Explosion"]),
    mon("Omastar", "White Herb", "Swift Swim", "Modest", ["Shell Smash", "Hydro Pump", "Ice Beam", "Earth Power"]),
    mon("Kabutops", "Life Orb", "Swift Swim", "Adamant", ["Stone Edge", "Liquidation", "Swords Dance", "Aqua Jet"]),
    mon("Relicanth", "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Liquidation", "Earthquake", "Double Edge"]),
    mon("Kleavor", "Focus Sash", "Sharpness", "Jolly", ["Stone Axe", "X Scissor", "Close Combat", "Swords Dance"]),
    mon("Aerodactyl", "Aerodactylite", "Unnerve", "Jolly", ["Stone Edge", "Earthquake", "Crunch", "Ice Fang"]),
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
    mon("Jumpluff", "Leftovers", "Aerilate", "Jolly", ["Sleep Powder", "Leech Seed", "Acrobatics", "U Turn"]),
    mon("Roserade", "Life Orb", "Technician", "Timid", ["Giga Drain", "Sludge Bomb", "Shadow Ball", "Spikes"]),
    mon("Tangrowth", "Rocky Helmet", "Regenerator", "Relaxed", ["Giga Drain", "Knock Off", "Earthquake", "Sleep Powder"]),
    mon("Victreebel", "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Weather Ball"]),
    mon("Bellossom", "Sitrus Berry", "Chlorophyll", "Modest", ["Quiver Dance", "Giga Drain", "Moonblast", "Strength Sap"]),
    mon("Venusaur", "Venusaurite", "Chlorophyll", "Modest", ["Giga Drain", "Sludge Bomb", "Earth Power", "Synthesis"]),
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
    mon("Torkoal", "Heat Rock", "Drought", "Bold", ["Lava Plume", "Stealth Rock", "Rapid Spin", "Yawn"]),
    mon("Rapidash", "Life Orb", "Flash Fire", "Jolly", ["Flare Blitz", "Wild Charge", "High Horsepower", "Morning Sun"]),
    mon("Magmortar", "Expert Belt", "Mega Launcher", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Psychic"]),
    mon("Volcarona", "Charcoal", "Flame Body", "Timid", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"]),
    mon("Arcanine Hisui", "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Flare Blitz", "Extreme Speed", "Wild Charge"]),
    mon("Camerupt", "Cameruptite", "Solid Rock", "Modest", ["Fire Blast", "Earth Power", "Ancient Power", "Stealth Rock"]),
]
# Machamp has Close Combat, not No Guard Dynamic Punch: with the guaranteed confusion, Blue beat
# every play-test team in all six tries (Bruno's Machamp likewise).
BLUE = [
    mon("Machamp", "Sitrus Berry", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"]),
    mon("Exeggutor", "Sitrus Berry", "Harvest", "Modest", ["Leaf Storm", "Psychic", "Sludge Bomb", "Trick Room"]),
    mon("Rhyperior", "Weakness Policy", "Solid Rock", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Rock Polish"]),
    mon("Arcanine", "Choice Band", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Wild Charge", "Close Combat"]),
    mon("Tyranitar", "Leftovers", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Pidgeot", "Pidgeotite", "Frisk", "Timid", ["Hurricane", "Heat Wave", "U Turn", "Roost"]),
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
        mon("Pichu", "Eviolite", "Static", "Timid", ["Nuzzle", "Thunder Shock", "Sweet Kiss", "Fake Out"]),
        mon("Sentret", "Eviolite", "Frisk", "Jolly", ["U Turn", "Quick Attack", "Fury Swipes", "Defense Curl"]),
        mon("Rattata", "Flame Orb", "Guts", "Jolly", ["Facade", "Quick Attack", "Bite", "Sucker Punch"]),
    ]),
    # Route 32, Camper Roland
    "TRAINER_ROLAND_HNS": (0, [
        mon("Bellsprout", "Eviolite", "Chlorophyll", "Adamant", ["Vine Whip", "Sleep Powder", "Acid", "Growth"]),
        mon("Mareep", "Eviolite", "Static", "Modest", ["Thunder Shock", "Thunder Wave", "Cotton Spore", "Take Down"]),
        mon("Geodude", "Eviolite", "Sturdy", "Adamant", ["Rock Throw", "Bulldoze", "Stealth Rock", "Rollout"]),
    ]),
    # Route 34, Cooltrainer Kate
    "TRAINER_KATE_HNS": (1, [
        mon("Shellder", "Eviolite", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Ice Shard", "Protect"]),
        mon("Growlithe", "Eviolite", "Intimidate", "Adamant", ["Fire Fang", "Bite", "Will O Wisp", "Roar"]),
        mon("Snubbull", "Eviolite", "Intimidate", "Impish", ["Play Rough", "Bite", "Thunder Wave", "Roar"]),
        mon("Kadabra", "Eviolite", "Magic Guard", "Timid", ["Psybeam", "Dazzling Gleam", "Calm Mind", "Recover"]),
    ]),
    # Route 35, Bird Keeper Bryan: a Leek Farfetch'd for critical hits
    "TRAINER_BRYAN_HNS": (1, [
        mon("Swablu", "Eviolite", "Natural Cure", "Bold", ["Dragon Breath", "Peck", "Sing", "Roost"]),
        mon("Farfetchd", "Leek", "Inner Focus", "Jolly", ["Leaf Blade", "Brave Bird", "Night Slash", "Swords Dance"]),
        mon("Fearow", "Sharp Beak", "Frisk", "Jolly", ["Drill Peck", "Drill Run", "Pursuit", "Quick Attack"]),
        mon("Noctowl", "Sitrus Berry", "Tinted Lens", "Modest", ["Air Slash", "Extrasensory", "Hypnosis", "Roost"]),
    ]),
    # Route 37, Psychic Greg
    "TRAINER_GREG_HNS": (2, [
        mon("Xatu", "Light Clay", "Magic Bounce", "Timid", ["Psychic", "Air Slash", "Thunder Wave", "Roost"]),
        mon("Grumpig", "Leftovers", "Thick Fat", "Modest", ["Psychic", "Shadow Ball", "Power Gem", "Calm Mind"]),
        mon("Kirlia", "Eviolite", "Trace", "Modest", ["Psychic", "Dazzling Gleam", "Calm Mind", "Thunderbolt"]),
        mon("Espeon", "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"]),
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
        mon("Tentacruel", "Black Sludge", "Clear Body", "Timid", ["Scald", "Sludge Bomb", "Toxic Spikes", "Rapid Spin"]),
        mon("Poliwhirl", "Eviolite", "Water Absorb", "Bold", ["Scald", "Hypnosis", "Ice Beam", "Encore"]),
        mon("Machoke", "Eviolite", "Guts", "Adamant", ["Dynamic Punch", "Knock Off", "Bullet Punch", "Bulk Up"]),
        mon("Kingler", "Life Orb", "Sheer Force", "Adamant", ["Crabhammer", "Knock Off", "Rock Slide", "Swords Dance"]),
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
        mon("Mantine", "Leftovers", "Water Absorb", "Calm", ["Scald", "Air Slash", "Haze", "Roost"]),
        mon("Octillery", "Life Orb", "Sniper", "Modest", ["Hydro Pump", "Ice Beam", "Fire Blast", "Gunk Shot"]),
        mon("Seadra", "Eviolite", "Sniper", "Modest", ["Hydro Pump", "Dragon Pulse", "Ice Beam", "Focus Energy"]),
        mon("Lapras", "Sitrus Berry", "Water Absorb", "Modest", ["Freeze Dry", "Surf", "Thunderbolt", "Ice Shard"]),
        mon("Starmie", "Life Orb", "Analytic", "Timid", ["Surf", "Psychic", "Thunderbolt", "Rapid Spin"]),
    ]),
    # Route 42, Hiker Benjamin
    "TRAINER_BENJAMIN_HNS": (3, [
        mon("Graveler", "Eviolite", "Sturdy", "Adamant", ["Stealth Rock", "Earthquake", "Rock Slide", "Explosion"]),
        mon("Onix", "Eviolite", "Sturdy", "Impish", ["Stealth Rock", "Rock Slide", "Earthquake", "Curse"]),
        mon("Rhyhorn", "Eviolite", "Rock Head", "Adamant", ["Rock Blast", "Earthquake", "Megahorn", "Stealth Rock"]),
        mon("Piloswine", "Eviolite", "Thick Fat", "Adamant", ["Earthquake", "Icicle Crash", "Ice Shard", "Stealth Rock"]),
        mon("Sudowoodo", "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Wood Hammer", "Sucker Punch", "Earthquake"]),
    ]),
    # Route 43, Pokemaniac Ben: rare Pokemon
    "TRAINER_BEN_HNS": (3, [
        mon("Lickitung", "Eviolite", "Own Tempo", "Careful", ["Body Slam", "Knock Off", "Power Whip", "Swords Dance"]),
        mon("Kangaskhan", "Silk Scarf", "Scrappy", "Adamant", ["Fake Out", "Double Edge", "Sucker Punch", "Earthquake"]),
        mon("Slowbro", "Leftovers", "Regenerator", "Bold", ["Scald", "Psychic", "Slack Off", "Thunder Wave"]),
        mon("Aerodactyl", "Focus Sash", "Rock Head", "Jolly", ["Stone Edge", "Double Edge", "Earthquake", "Stealth Rock"]),
        mon("Dragonair", "Eviolite", "Shed Skin", "Adamant", ["Dragon Dance", "Extreme Speed", "Aqua Tail", "Iron Tail"]),
    ]),
    # Route 47, Hiker Devin
    "TRAINER_DEVIN_HNS": (3, [
        mon("Gligar", "Eviolite", "Immunity", "Jolly", ["Earthquake", "Knock Off", "U Turn", "Roost"]),
        mon("Lairon", "Eviolite", "Rock Head", "Adamant", ["Head Smash", "Iron Head", "Earthquake", "Stealth Rock"]),
        mon("Marowak", "Thick Club", "Rock Head", "Adamant", ["Bonemerang", "Rock Slide", "Fire Punch", "Swords Dance"]),
        mon("Hariyama", "Flame Orb", "Guts", "Adamant", ["Close Combat", "Knock Off", "Bullet Punch", "Fake Out"]),
        mon("Golem", "Sitrus Berry", "Sturdy", "Adamant", ["Stealth Rock", "Earthquake", "Stone Edge", "Sucker Punch"]),
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
        mon("Scizor", "Choice Band", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Superpower"]),
        mon("Starmie", "Life Orb", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Ice Beam", "Thunderbolt"]),
        mon("Ampharos", "Leftovers", "Static", "Modest", ["Thunderbolt", "Dragon Pulse", "Focus Blast", "Volt Switch"]),
        mon("Houndoom", "Life Orb", "Flash Fire", "Timid", ["Dark Pulse", "Fire Blast", "Sludge Bomb", "Nasty Plot"]),
        mon("Heracross", "Choice Scarf", "Moxie", "Jolly", ["Megahorn", "Close Combat", "Stone Edge", "Knock Off"]),
        mon("Nidoking", "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    ]),
    # Route 45, Cooltrainer Kelly
    "TRAINER_KELLY_HNS": (6, [
        mon("Roserade", "Focus Sash", "Technician", "Timid", ["Giga Drain", "Sludge Bomb", "Shadow Ball", "Sleep Powder"]),
        mon("Lopunny", "Life Orb", "Limber", "Jolly", ["Return", "High Jump Kick", "Fake Out", "Ice Punch"]),
        mon("Froslass", "Focus Sash", "Stakeout", "Timid", ["Ice Beam", "Shadow Ball", "Spikes", "Destiny Bond"]),
        mon("Azumarill", "Choice Band", "Huge Power", "Adamant", ["Play Rough", "Aqua Jet", "Waterfall", "Superpower"]),
        mon("Gardevoir", "Choice Scarf", "Trace", "Timid", ["Moonblast", "Psychic", "Mystical Fire", "Thunderbolt"]),
        mon("Milotic", "Leftovers", "Marvel Scale", "Bold", ["Scald", "Ice Beam", "Recover", "Haze"]),
    ]),
    # Kanto (after the Johto League, cap 90)
    # Route 1, Cooltrainer Quinn: sand
    "TRAINER_QUINN_HNS": (JOHTO_CHAMPION, [
        mon("Hippowdon", "Leftovers", "Sand Stream", "Impish", ["Earthquake", "Slack Off", "Stealth Rock", "Whirlwind"]),
        mon("Excadrill", "Life Orb", "Sand Rush", "Adamant", ["Earthquake", "Iron Head", "Rock Slide", "Swords Dance"]),
        mon("Gliscor", "Toxic Orb", "Poison Heal", "Impish", ["Earthquake", "Knock Off", "Toxic", "Roost"]),
        mon("Sandslash", "Focus Sash", "Sand Rush", "Jolly", ["Earthquake", "Knock Off", "Swords Dance", "Rapid Spin"]),
        mon("Garchomp", "Rocky Helmet", "Rough Skin", "Jolly", ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"]),
        mon("Tyranitar", "Choice Band", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Ice Punch"]),
    ]),
    # Route 3, Firebreather Otis: sun
    "TRAINER_OTIS_HNS": (JOHTO_CHAMPION, [
        mon("Ninetales", "Heat Rock", "Drought", "Timid", ["Fire Blast", "Solar Beam", "Nasty Plot", "Will O Wisp"]),
        mon("Houndoom", "Black Glasses", "Flash Fire", "Timid", ["Dark Pulse", "Fire Blast", "Sludge Bomb", "Nasty Plot"]),
        mon("Chandelure", "Choice Specs", "Flash Fire", "Modest", ["Shadow Ball", "Fire Blast", "Energy Ball", "Trick"]),
        mon("Magmortar", "Expert Belt", "Flame Body", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Psychic"]),
        mon("Volcarona", "Leftovers", "Flame Body", "Modest", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"]),
        mon("Charizard", "Life Orb", "Solar Power", "Timid", ["Fire Blast", "Solar Beam", "Air Slash", "Focus Blast"]),
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
        mon("Donphan", "Leftovers", "Sturdy", "Adamant", ["Earthquake", "Ice Shard", "Knock Off", "Rapid Spin"]),
        mon("Steelix", "Leftovers", "Sturdy", "Impish", ["Heavy Slam", "Earthquake", "Stealth Rock", "Curse"]),
        mon("Golem", "Focus Sash", "Sturdy", "Adamant", ["Stone Edge", "Earthquake", "Sucker Punch", "Explosion"]),
        mon("Mamoswine", "Life Orb", "Thick Fat", "Adamant", ["Earthquake", "Icicle Crash", "Ice Shard", "Stone Edge"]),
        mon("Aggron", "Sitrus Berry", "Rock Head", "Adamant", ["Head Smash", "Heavy Slam", "Earthquake", "Rock Polish"]),
        mon("Rhyperior", "Weakness Policy", "Solid Rock", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Ice Punch"]),
    ]),
    # Route 10, Pokefan Robert: Fairy types
    "TRAINER_ROBERT_HNS": (JOHTO_CHAMPION, [
        mon("Granbull", "Leftovers", "Intimidate", "Impish", ["Play Rough", "Earthquake", "Thunder Wave", "Heal Bell"]),
        mon("Azumarill", "Choice Band", "Huge Power", "Adamant", ["Play Rough", "Aqua Jet", "Waterfall", "Superpower"]),
        mon("Mimikyu", "Life Orb", "Disguise", "Jolly", ["Play Rough", "Shadow Claw", "Shadow Sneak", "Swords Dance"]),
        mon("Togekiss", "Leftovers", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Aura Sphere", "Roost"]),
        mon("Sylveon", "Choice Specs", "Pixilate", "Modest", ["Hyper Voice", "Psyshock", "Shadow Ball", "Mystical Fire"]),
        mon("Clefable", "Leftovers", "Magic Guard", "Bold", ["Moonblast", "Flamethrower", "Soft Boiled", "Calm Mind"]),
    ]),
    # Route 11, Psychic Herman
    "TRAINER_HERMAN_HNS": (JOHTO_CHAMPION, [
        mon("Bronzong", "Leftovers", "Levitate", "Relaxed", ["Gyro Ball", "Earthquake", "Stealth Rock", "Hypnosis"]),
        mon("Hatterene", "Life Orb", "Magic Bounce", "Quiet", ["Psychic", "Dazzling Gleam", "Mystical Fire", "Trick Room"]),
        mon("Gallade", "Choice Band", "Justified", "Adamant", ["Psycho Cut", "Close Combat", "Leaf Blade", "Knock Off"]),
        mon("Reuniclus", "Life Orb", "Magic Guard", "Modest", ["Psychic", "Focus Blast", "Shadow Ball", "Calm Mind"]),
        mon("Alakazam", "Focus Sash", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Nasty Plot"]),
        mon("Metagross", "Life Orb", "Clear Body", "Adamant", ["Meteor Mash", "Zen Headbutt", "Bullet Punch", "Earthquake"]),
    ]),
    # Route 12, Fisherman Stephen: rain
    "TRAINER_STEPHEN_HNS": (JOHTO_CHAMPION, [
        mon("Politoed", "Damp Rock", "Drizzle", "Bold", ["Scald", "Ice Beam", "Encore", "Hypnosis"]),
        mon("Kingdra", "Life Orb", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Rain Dance"]),
        mon("Ludicolo", "Life Orb", "Swift Swim", "Modest", ["Hydro Pump", "Giga Drain", "Ice Beam", "Focus Blast"]),
        mon("Seismitoad", "Leftovers", "Swift Swim", "Modest", ["Hydro Pump", "Earth Power", "Sludge Wave", "Stealth Rock"]),
        mon("Lanturn", "Leftovers", "Volt Absorb", "Modest", ["Thunder", "Scald", "Ice Beam", "Volt Switch"]),
        mon("Gyarados", "Sitrus Berry", "Moxie", "Jolly", ["Waterfall", "Earthquake", "Dragon Dance", "Bounce"]),
    ]),
    # Route 13, Juggler Bret: tricks
    "TRAINER_BRET_HNS": (JOHTO_CHAMPION, [
        mon("Klefki", "Light Clay", "Prankster", "Bold", ["Spikes", "Thunder Wave", "Foul Play", "Play Rough"]),
        mon("Sableye", "Leftovers", "Prankster", "Careful", ["Will O Wisp", "Knock Off", "Recover", "Foul Play"]),
        mon("Ambipom", "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Double Hit", "U Turn", "Knock Off"]),
        mon("Mr Mime", "Life Orb", "Filter", "Timid", ["Psychic", "Dazzling Gleam", "Focus Blast", "Nasty Plot"]),
        mon("Rotom", "Leftovers", "Levitate", "Timid", ["Thunderbolt", "Shadow Ball", "Will O Wisp", "Volt Switch"]),
        mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Hidden Power"]),
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
        mon("Skarmory", "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Brave Bird", "Roost", "Whirlwind"]),
        mon("Staraptor", "Choice Band", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "U Turn", "Double Edge"]),
        mon("Talonflame", "Sharp Beak", "Gale Wings", "Adamant", ["Brave Bird", "Flare Blitz", "U Turn", "Roost"]),
        mon("Corviknight", "Leftovers", "Pressure", "Impish", ["Brave Bird", "Iron Head", "Bulk Up", "Roost"]),
        mon("Togekiss", "Choice Scarf", "Serene Grace", "Timid", ["Air Slash", "Dazzling Gleam", "Aura Sphere", "Flamethrower"]),
        mon("Dragonite", "Lum Berry", "Multiscale", "Adamant", ["Dragon Dance", "Extreme Speed", "Earthquake", "Fire Punch"]),
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
        mon("Gengar", "Focus Sash", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Focus Blast", "Nasty Plot"]),
        mon("Scizor", "Life Orb", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Swords Dance"]),
        mon("Ferrothorn", "Leftovers", "Iron Barbs", "Relaxed", ["Gyro Ball", "Power Whip", "Leech Seed", "Spikes"]),
        mon("Crawdaunt", "Life Orb", "Adaptability", "Adamant", ["Crabhammer", "Knock Off", "Aqua Jet", "Swords Dance"]),
        mon("Kommo O", "Life Orb", "Bulletproof", "Jolly", ["Close Combat", "Dragon Claw", "Poison Jab", "Dragon Dance"]),
        mon("Salamence", "Life Orb", "Intimidate", "Adamant", ["Dragon Dance", "Dual Wingbeat", "Earthquake", "Fire Fang"]),
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
    mon("Landorus Therian", "Focus Sash", "Intimidate", "Jolly", ["Stealth Rock", "Earthquake", "Stone Edge", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Talonflame", "Heavy Duty Boots", "Gale Wings", "Jolly", ["Tailwind", "Brave Bird", "Will O Wisp", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Staraptor", "Choice Band", "Reckless", "Jolly", ["Brave Bird", "Close Combat", "Double Edge", "U Turn"],
        "4 HP / 252 Atk / 252 Spe"),
    mon("Corviknight", "Rocky Helmet", "Pressure", "Impish", ["Brave Bird", "Body Press", "Iron Defense", "Roost"],
        "252 HP / 4 Atk / 252 Def"),
    mon("Zapdos", "Heavy Duty Boots", "Static", "Timid", ["Thunderbolt", "Hurricane", "Volt Switch", "Roost"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Pidgeot", "Pidgeotite", "No Guard", "Timid", ["Hurricane", "Heat Wave", "Work Up", "Roost"],
        "4 HP / 252 SpA / 252 Spe"),
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
    mon("Archaludon", "Custap Berry", "Sturdy", "Modest", ["Stealth Rock", "Draco Meteor", "Flash Cannon", "Thunderbolt"]),
    mon("Baxcalibur", "Choice Band", "Thermal Exchange", "Jolly", ["Glaive Rush", "Icicle Crash", "Earthquake", "Ice Shard"]),
    mon("Walking Wake", "Booster Energy", "Protosynthesis", "Timid", ["Surf", "Draco Meteor", "Flamethrower", "Flip Turn"]),
    mon("Dragonite", "Heavy Duty Boots", "Multiscale", "Adamant", ["Extreme Speed", "Earthquake", "Fire Punch", "Roost"]),
    mon("Noivern", "Choice Specs", "Infiltrator", "Timid", ["Draco Meteor", "Hurricane", "Flamethrower", "U Turn"]),
    mon("Garchomp", "Garchompite", "Rough Skin", "Jolly", ["Swords Dance", "Scale Shot", "Earthquake", "Iron Head"]),
]

# A temple bell, a haunted stump and the tower's Bellsprout. Bronzor leads with Stealth Rock,
# Rock Tomb for the Fire and Flying types and Light Screen; Heatproof and the Eviolite take
# Fire moves. Phantump burns for Hex and Leech Seeds; Weepinbell, the ace, puts one to sleep
# and heals with Strength Sap.
LI = [
    mon("Bronzor", "Eviolite", "Heatproof", "Relaxed", ["Stealth Rock", "Rock Tomb", "Payback", "Light Screen"],
        "252 HP / 252 Def / 4 SpD"),
    mon("Phantump", "Eviolite", "Natural Cure", "Sassy", ["Will O Wisp", "Hex", "Leech Seed", "Horn Leech"],
        "252 HP / 4 Def / 252 SpD"),
    mon("Weepinbell", "Eviolite", "Chlorophyll", "Adamant", ["Sleep Powder", "Bullet Seed", "Poison Jab", "Strength Sap"],
        "252 HP / 252 Atk / 4 Def"),
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
    mon("Gengar", "Life Orb", "Levitate", "Timid", ["Shadow Ball", "Sludge Wave", "Focus Blast", "Will O Wisp"],
        "252 SpA / 4 SpD / 252 Spe"),
    mon("Ursaluna", "Flame Orb", "Guts", "Adamant", ["Facade", "Headlong Rush", "Ice Punch", "Fire Punch"],
        "252 HP / 252 Atk / 4 SpD"),
    mon("Tyranitar", "Tyranitarite", "Sand Stream", "Jolly", ["Dragon Dance", "Stone Edge", "Knock Off", "Earthquake"],
        "252 Atk / 4 SpD / 252 Spe"),
]
RIVAL_STARTER[6] = {
    "CYNDAQUIL": mon("Typhlosion", "Choice Specs", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Scorching Sands"],
    "252 SpA / 4 SpD / 252 Spe"),
    "TOTODILE": mon("Feraligatr", "Life Orb", "Sheer Force", "Jolly", ["Dragon Dance", "Liquidation", "Ice Punch", "Crunch"],
    "252 Atk / 4 SpD / 252 Spe"),
    "CHIKORITA": mon("Meganium", "Leftovers", "Triage", "Calm", ["Giga Drain", "Leech Seed", "Earth Power", "Synthesis"],
    "252 HP / 252 SpA / 4 SpD"),
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
    "TRAINER_CHUCK_1_2_HNS": (5, "Full Restore / Full Restore", CHUCK),
    "TRAINER_CHUCK_1_3_HNS": (6, "Full Restore / Full Restore", CHUCK),
    "TRAINER_JASMINE_1_HNS": (4, "Hyper Potion / Hyper Potion", JASMINE),
    "TRAINER_JASMINE_1_2_HNS": (5, "Full Restore / Full Restore", JASMINE),
    "TRAINER_JASMINE_1_3_HNS": (6, "Full Restore / Full Restore", JASMINE),
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
    out = "\n".join(lines) + "\n"
    for m in mons:
        out += f"\n{m['species']} @ {m['item']}\n"
        out += f"Level: {cap(stage)}\n"
        out += "IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe\n"
        if m.get("evs"):
            out += f"EVs: {m['evs']}\n"
        out += f"Ability: {m['ability']}\n"
        out += f"Nature: {m['nature']}\n"
        if FRIENDSHIP_MOVES & set(m["moves"]):
            out += f"Happiness: {FULL_FRIENDSHIP}\n"
        out += "".join(f"- {mv}\n" for mv in m["moves"])
    return out


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
        print(f"wrote {os.path.relpath(BOSS_LIST, ROOT)} ({len(STAGES)} bosses)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
