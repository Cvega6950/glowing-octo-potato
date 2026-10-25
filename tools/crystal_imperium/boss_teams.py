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

# Stages after the eighth badge: the Johto League won (FLAG_IS_CHAMPION; cap 70 for all of Kanto)
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


def mon(species, item, ability, nature, moves, evs=None):
    return {"species": species, "item": item, "ability": ability, "nature": nature, "moves": moves, "evs": evs}


# --- Morty (4th Gym, 3 badges: cap 25) ------------------------------------------------------------
MORTY = [
    mon("Sableye", "Sitrus Berry", "Prankster", "Careful", ["Will O Wisp", "Knock Off", "Night Shade", "Recover"]),
    mon("Misdreavus", "Eviolite", "Levitate", "Timid", ["Hex", "Thunder Wave", "Dazzling Gleam", "Pain Split"]),
    mon("Drifblim", "Sitrus Berry", "Unburden", "Modest", ["Shadow Ball", "Air Slash", "Thunderbolt", "Calm Mind"]),
    mon("Marowak Alola", "Thick Club", "Lightning Rod", "Adamant", ["Shadow Bone", "Fire Punch", "Bonemerang", "Thunder Punch"]),
    mon("Gengar", "Spell Tag", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Hypnosis"]),
]

# --- Chuck, Jasmine, Pryce (5th to 7th Gym in any order) ------------------------------------------
# HnS picks the party by how many of the three the player has beaten: _1 with 4 badges (cap 31),
# _1_2 with 5 (cap 36), _1_3 with 6 (cap 38).
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


def five_of_six(mons, drop):
    return [m for i, m in enumerate(mons) if i != drop]


# --- Clair (8th Gym, 7 badges: cap 45) ------------------------------------------------------------
CLAIR = [
    mon("Druddigon", "Rocky Helmet", "Rough Skin", "Adamant", ["Outrage", "Gunk Shot", "Sucker Punch", "Glare"]),
    mon("Flygon", "Choice Scarf", "Levitate", "Jolly", ["Earthquake", "Dragon Claw", "U Turn", "Fire Punch"]),
    mon("Dragalge", "Black Sludge", "Adaptability", "Modest", ["Sludge Bomb", "Dragon Pulse", "Focus Blast", "Toxic Spikes"]),
    mon("Altaria", "Altarianite", "Natural Cure", "Modest", ["Hyper Voice", "Dragon Pulse", "Fire Blast", "Roost"]),
    mon("Kommo O", "Life Orb", "Bulletproof", "Jolly", ["Scale Shot", "Close Combat", "Poison Jab", "Swords Dance"]),
    mon("Kingdra", "Wacan Berry", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Rain Dance"]),
]

# --- Rival (Silver): TRAINER_RIVAL_<his starter>_<n>_HNS ------------------------------------------
# 2nd battle: Azalea Town after Bugsy (2 badges, cap 21). 3rd: Burned Tower (3 badges, cap 25).
RIVAL_STARTER = {
    2: {"CYNDAQUIL": mon("Quilava", "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Quick Attack", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", "Sitrus Berry", "Sheer Force", "Adamant", ["Ice Fang", "Bite", "Aqua Jet", "Scary Face"]),
        "CHIKORITA": mon("Bayleef", "Sitrus Berry", "Overgrow", "Bold", ["Razor Leaf", "Reflect", "Poison Powder", "Synthesis"])},
    3: {"CYNDAQUIL": mon("Quilava", "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Flame Charge", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", "Sitrus Berry", "Sheer Force", "Adamant", ["Aqua Tail", "Ice Fang", "Crunch", "Dragon Dance"]),
        "CHIKORITA": mon("Bayleef", "Sitrus Berry", "Overgrow", "Bold", ["Magical Leaf", "Leech Seed", "Reflect", "Synthesis"])},
}
RIVAL_TEAM = {
    2: [mon("Golbat", "Eviolite", "Inner Focus", "Jolly", ["Wing Attack", "Bite", "Confuse Ray", "Toxic"]),
        mon("Larvitar", "Eviolite", "Guts", "Adamant", ["Rock Slide", "Bite", "Bulldoze", "Scary Face"]),
        mon("Sneasel", "Oran Berry", "Inner Focus", "Jolly", ["Faint Attack", "Ice Shard", "Quick Attack", "Icy Wind"])],
    3: [mon("Golbat", "Eviolite", "Inner Focus", "Jolly", ["Air Cutter", "Bite", "Confuse Ray", "Toxic"]),
        mon("Sneasel", "Razor Claw", "Inner Focus", "Jolly", ["Fake Out", "Ice Punch", "Faint Attack", "Ice Shard"]),
        mon("Weepinbell", "Eviolite", "Chlorophyll", "Adamant", ["Bullet Seed", "Poison Jab", "Sleep Powder", "Knock Off"]),
        mon("Larvitar", "Eviolite", "Guts", "Adamant", ["Rock Slide", "Crunch", "Bulldoze", "Dragon Dance"])],
}

# --- Team Rocket: Proton in Slowpoke Well (1 badge, cap 16) -----------------------------------------
PROTON_1 = [
    mon("Koffing", "Eviolite", "Levitate", "Bold", ["Sludge", "Will O Wisp", "Clear Smog", "Smokescreen"]),
    mon("Slowpoke", "Eviolite", "Regenerator", "Relaxed", ["Water Pulse", "Confusion", "Yawn", "Slack Off"]),
    mon("Houndour", "Charcoal", "Flash Fire", "Timid", ["Incinerate", "Snarl", "Smog", "Nasty Plot"]),
]

# --- Team Rocket: Rocket Hideout (4 badges at the earliest: the Lake of Rage needs Surf; cap 31) ------
PETREL_1 = [
    mon("Weezing", "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Fire Blast"]),
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Rock Slide", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Drapion", "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_1 = [
    mon("Arbok", "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
    mon("Vileplume", "Black Sludge", "Effect Spore", "Calm", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Honchkrow", "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
]

# --- Team Rocket: Radio Tower (7 badges, cap 45) ----------------------------------------------------
PROTON_2 = [
    mon("Muk", "Black Sludge", "Poison Touch", "Adamant", ["Gunk Shot", "Shadow Sneak", "Knock Off", "Curse"]),
    mon("Nidoqueen", "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    mon("Weezing", "Rocky Helmet", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
    mon("Nidoking", "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Thunderbolt"]),
    mon("Rhydon", "Eviolite", "Lightning Rod", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Swords Dance"]),
]
PETREL_2 = [
    mon("Forretress", "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Weezing Galar", "Black Sludge", "Neutralizing Gas", "Bold", ["Strange Steam", "Sludge Bomb", "Will O Wisp", "Pain Split"]),
    mon("Pupitar", "Eviolite", "Shed Skin", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Cloyster", "Focus Sash", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Shell Smash", "Liquidation"]),
    mon("Drapion", "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_2 = [
    mon("Arbok", "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
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

# --- Rival: Goldenrod Underground (7 badges, cap 45) and Victory Road (8 badges, cap 56) -------------
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

# --- Kimono Girls: Ecruteak Dance Theater, one after another (8 badges, cap 56) ----------------------
KIMONO = {
    "TRAINER_ZUKI_HNS": [mon("Umbreon", "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Moonlight", "Protect", "Toxic"])],
    "TRAINER_NAOKO_HNS": [mon("Espeon", "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"])],
    "TRAINER_MIKI_HNS": [mon("Flareon", "Toxic Orb", "Guts", "Adamant", ["Flare Blitz", "Facade", "Superpower", "Quick Attack"])],
    "TRAINER_SAYO_HNS": [mon("Jolteon", "Choice Specs", "Volt Absorb", "Timid", ["Thunderbolt", "Shadow Ball", "Volt Switch", "Hyper Voice"])],
    "TRAINER_KUNI_HNS": [mon("Vaporeon", "Leftovers", "Water Absorb", "Bold", ["Scald", "Ice Beam", "Wish", "Protect"])],
}

# --- Elite Four and Lance (8 badges, cap 56) -----------------------------------------------------------
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

# --- Kanto Gym Leaders and Blue (after the Johto League: cap 70, any order) ------------------------
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
    mon("Electrode", "Focus Sash", "Aftermath", "Timid", ["Thunderbolt", "Volt Switch", "Taunt", "Explosion"]),
    mon("Magnezone", "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Body Press"]),
    mon("Lanturn", "Leftovers", "Volt Absorb", "Bold", ["Scald", "Discharge", "Ice Beam", "Heal Bell"]),
    mon("Electivire", "Life Orb", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Earthquake", "Cross Chop"]),
    mon("Manectric", "Manectite", "Lightning Rod", "Timid", ["Thunderbolt", "Overheat", "Snarl", "Volt Switch"]),
    mon("Raichu", "Magnet", "Lightning Rod", "Timid", ["Thunderbolt", "Focus Blast", "Nasty Plot", "Grass Knot"]),
]
ERIKA = [
    mon("Jumpluff", "Leftovers", "Infiltrator", "Jolly", ["Sleep Powder", "Leech Seed", "Acrobatics", "U Turn"]),
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
    mon("Magmortar", "Expert Belt", "Vital Spirit", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Psychic"]),
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
    mon("Pidgeot", "Pidgeotite", "Keen Eye", "Timid", ["Hurricane", "Heat Wave", "U Turn", "Roost"]),
]

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
    "TRAINER_MORTY_1_HNS": (3, "Hyper Potion / Hyper Potion", MORTY),
    "TRAINER_CHUCK_1_HNS": (4, "Hyper Potion / Hyper Potion", five_of_six(CHUCK, 2)),
    "TRAINER_CHUCK_1_2_HNS": (5, "Full Restore / Full Restore", CHUCK),
    "TRAINER_CHUCK_1_3_HNS": (6, "Full Restore / Full Restore", CHUCK),
    "TRAINER_JASMINE_1_HNS": (4, "Hyper Potion / Hyper Potion", five_of_six(JASMINE, 2)),
    "TRAINER_JASMINE_1_2_HNS": (5, "Full Restore / Full Restore", JASMINE),
    "TRAINER_JASMINE_1_3_HNS": (6, "Full Restore / Full Restore", JASMINE),
    "TRAINER_PRYCE_1_HNS": (4, "Hyper Potion / Hyper Potion", five_of_six(PRYCE, 1)),
    "TRAINER_PRYCE_1_2_HNS": (5, "Full Restore / Full Restore", PRYCE),
    "TRAINER_PRYCE_1_3_HNS": (6, "Full Restore / Full Restore", PRYCE),
    "TRAINER_CLAIR_1_HNS": (7, "Full Restore / Full Restore", CLAIR),
}
TEAMS.update({tid: (8, "", mons) for tid, mons in KIMONO.items()})
for _n, _stage, _items in ((2, 2, "Super Potion"), (3, 3, "Super Potion / Super Potion"),
                           (4, 7, "Full Restore / Full Restore"), (5, 8, "Full Restore / Full Restore")):
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
LEVEL_ONLY = {"TRAINER_LI_HNS": 0, "TRAINER_FALKNER_1_HNS": 0, "TRAINER_BUGSY_1_HNS": 1,
              "TRAINER_WHITNEY_1_HNS": 2, "TRAINER_EUSINE_HNS": 4}
LEVEL_ONLY.update({f"TRAINER_RIVAL_{s}_1_HNS": 0 for s in STARTERS})
LEVEL_ONLY.update({f"TRAINER_RIVAL_{s}_{n}_HNS": JOHTO_CHAMPION for s in STARTERS for n in (6, 7)})
LEVEL_ONLY.update({f"TRAINER_{l}_2_HNS": JOHTO_CHAMPION for l in JOHTO_LEADERS + ELITE_FOUR})
LEVEL_ONLY.update({f"TRAINER_{l}_POSTOBC_HNS": KANTO_CHAMPION for l in JOHTO_LEADERS + KANTO_LEADERS + ELITE_FOUR})

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
