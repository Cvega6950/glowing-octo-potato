#!/usr/bin/env python3
"""Crystal Imperium boss teams (Emerald Imperium-style): writes the parties below into
src/data/trainers_hns.party, keeping each trainer's header (name, class, picture, music, mugshot)
and replacing its AI, bag items and Pokemon.

  python3 tools/crystal_imperium/boss_teams.py          # rewrite the parties
  python3 tools/crystal_imperium/boss_teams.py --check  # exit 1 if the file is out of date

Design rules (DECISIONS.md D21):
  * the ace (last Pokemon) is at the NORMAL level cap the player has when the battle can happen,
    the others one or two levels below
  * every Pokemon has a held item, a nature, an ability chosen for the set and four moves it
    can learn (validate.py checks abilities and moves)
  * IVs are 31 (Minimal Grinding gives every Pokemon 31 IVs anyway; this covers games with it off)
  * from the 5th Gym on, each boss has one Mega Evolution, normally the ace
  * Red is the hardest battle in the game (D27): the highest levels, competitive EVs (which he
    keeps under Minimal Grinding), the prediction AI and four Full Restores; validate.py checks it
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PARTY = os.path.join(ROOT, "src", "data", "trainers_hns.party")

BOSS_AI = "Smart Trainer / Ace Pokemon / HP Aware"
RED_AI = "Smart Trainer / Prediction / Ace Pokemon / HP Aware"


def mon(species, level, item, ability, nature, moves, evs=None):
    return {"species": species, "level": level, "item": item, "ability": ability, "nature": nature, "moves": moves,
            "evs": evs}


def team(levels, mons):
    """The same Pokemon at different levels: levels[i] for mons[i] (a mon() with level None)."""
    return [dict(m, level=l) for l, m in zip(levels, mons)]


# --- Morty (4th Gym, 3 badges: cap 25) ------------------------------------------------------------
MORTY = [
    mon("Sableye", 23, "Sitrus Berry", "Prankster", "Careful", ["Will O Wisp", "Knock Off", "Night Shade", "Recover"]),
    mon("Misdreavus", 23, "Eviolite", "Levitate", "Timid", ["Hex", "Thunder Wave", "Dazzling Gleam", "Pain Split"]),
    mon("Drifblim", 24, "Sitrus Berry", "Unburden", "Modest", ["Shadow Ball", "Air Slash", "Thunderbolt", "Calm Mind"]),
    mon("Marowak Alola", 24, "Thick Club", "Lightning Rod", "Adamant", ["Shadow Bone", "Fire Punch", "Bonemerang", "Thunder Punch"]),
    mon("Gengar", 25, "Spell Tag", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Thunderbolt", "Hypnosis"]),
]

# --- Chuck, Jasmine, Pryce (5th to 7th Gym in any order) ------------------------------------------
# HnS picks the party by how many of the three the player has beaten: _1 with 4 badges (cap 31),
# _1_2 with 5 (cap 36), _1_3 with 6 (cap 38).
CHUCK = [
    mon("Hitmontop", None, "Sitrus Berry", "Intimidate", "Adamant", ["Fake Out", "Triple Kick", "Sucker Punch", "Rock Slide"]),
    mon("Breloom", None, "Focus Sash", "Technician", "Jolly", ["Mach Punch", "Bullet Seed", "Rock Tomb", "Spore"]),
    mon("Hawlucha", None, "White Herb", "Unburden", "Jolly", ["High Jump Kick", "Acrobatics", "Swords Dance", "Roost"]),
    mon("Primeape", None, "Eviolite", "Defiant", "Jolly", ["Rage Fist", "Drain Punch", "U Turn", "Bulk Up"]),
    mon("Poliwrath", None, "Leftovers", "Water Absorb", "Adamant", ["Waterfall", "Dynamic Punch", "Mind Reader", "Ice Punch"]),
    mon("Heracross", None, "Heracronite", "Guts", "Jolly", ["Pin Missile", "Rock Blast", "Close Combat", "Bullet Seed"]),
]
JASMINE = [
    mon("Skarmory", None, "Rocky Helmet", "Sturdy", "Impish", ["Spikes", "Drill Peck", "Roost", "Whirlwind"]),
    mon("Magneton", None, "Eviolite", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Thunder Wave"]),
    mon("Bronzong", None, "Leftovers", "Levitate", "Relaxed", ["Gyro Ball", "Earthquake", "Hypnosis", "Stealth Rock"]),
    mon("Mawile", None, "Sitrus Berry", "Intimidate", "Adamant", ["Iron Head", "Play Rough", "Sucker Punch", "Swords Dance"]),
    mon("Scizor", None, "Metal Coat", "Technician", "Adamant", ["Bullet Punch", "U Turn", "Knock Off", "Swords Dance"]),
    mon("Steelix", None, "Steelixite", "Sturdy", "Impish", ["Gyro Ball", "Earthquake", "Rock Slide", "Curse"]),
]
PRYCE = [
    mon("Cloyster", None, "Focus Sash", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Shell Smash", "Liquidation"]),
    mon("Dewgong", None, "Leftovers", "Thick Fat", "Bold", ["Surf", "Ice Beam", "Toxic", "Protect"]),
    mon("Jynx", None, "Wise Glasses", "Dry Skin", "Timid", ["Lovely Kiss", "Ice Beam", "Psychic", "Nasty Plot"]),
    mon("Weavile", None, "Razor Claw", "Pressure", "Jolly", ["Ice Punch", "Knock Off", "Ice Shard", "Low Kick"]),
    mon("Mamoswine", None, "Never Melt Ice", "Thick Fat", "Adamant", ["Earthquake", "Icicle Crash", "Ice Shard", "Stone Edge"]),
    mon("Abomasnow", None, "Abomasite", "Snow Warning", "Quiet", ["Blizzard", "Energy Ball", "Ice Shard", "Earthquake"]),
]


def five_of_six(mons, drop):
    return [m for i, m in enumerate(mons) if i != drop]


# --- Clair (8th Gym, 7 badges: cap 45) ------------------------------------------------------------
CLAIR = [
    mon("Druddigon", 43, "Rocky Helmet", "Rough Skin", "Adamant", ["Outrage", "Gunk Shot", "Sucker Punch", "Glare"]),
    mon("Flygon", 43, "Choice Scarf", "Levitate", "Jolly", ["Earthquake", "Dragon Claw", "U Turn", "Fire Punch"]),
    mon("Dragalge", 44, "Black Sludge", "Adaptability", "Modest", ["Sludge Bomb", "Dragon Pulse", "Focus Blast", "Toxic Spikes"]),
    mon("Altaria", 44, "Altarianite", "Natural Cure", "Modest", ["Hyper Voice", "Dragon Pulse", "Fire Blast", "Roost"]),
    mon("Kommo O", 44, "Life Orb", "Bulletproof", "Jolly", ["Scale Shot", "Close Combat", "Poison Jab", "Swords Dance"]),
    mon("Kingdra", 45, "Wacan Berry", "Swift Swim", "Modest", ["Hydro Pump", "Draco Meteor", "Ice Beam", "Rain Dance"]),
]

# --- Rival (Silver): TRAINER_RIVAL_<his starter>_<n>_HNS ------------------------------------------
# 2nd battle: Azalea Town after Bugsy (2 badges, cap 21). 3rd: Burned Tower (3 badges, cap 25).
RIVAL_STARTER = {
    2: {"CYNDAQUIL": mon("Quilava", 19, "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Quick Attack", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", 19, "Sitrus Berry", "Sheer Force", "Adamant", ["Ice Fang", "Bite", "Aqua Jet", "Scary Face"]),
        "CHIKORITA": mon("Bayleef", 19, "Sitrus Berry", "Overgrow", "Bold", ["Razor Leaf", "Reflect", "Poison Powder", "Synthesis"])},
    3: {"CYNDAQUIL": mon("Quilava", 24, "Sitrus Berry", "Blaze", "Timid", ["Lava Plume", "Extrasensory", "Flame Charge", "Smokescreen"]),
        "TOTODILE": mon("Croconaw", 24, "Sitrus Berry", "Sheer Force", "Adamant", ["Aqua Tail", "Ice Fang", "Crunch", "Dragon Dance"]),
        "CHIKORITA": mon("Bayleef", 24, "Sitrus Berry", "Overgrow", "Bold", ["Magical Leaf", "Leech Seed", "Reflect", "Synthesis"])},
}
RIVAL_TEAM = {
    2: [mon("Golbat", 17, "Eviolite", "Inner Focus", "Jolly", ["Wing Attack", "Bite", "Confuse Ray", "Toxic"]),
        mon("Larvitar", 18, "Eviolite", "Guts", "Adamant", ["Rock Slide", "Bite", "Bulldoze", "Scary Face"]),
        mon("Sneasel", 18, "Oran Berry", "Inner Focus", "Jolly", ["Faint Attack", "Ice Shard", "Quick Attack", "Icy Wind"])],
    3: [mon("Golbat", 22, "Eviolite", "Inner Focus", "Jolly", ["Air Cutter", "Bite", "Confuse Ray", "Toxic"]),
        mon("Sneasel", 22, "Razor Claw", "Inner Focus", "Jolly", ["Fake Out", "Ice Punch", "Faint Attack", "Ice Shard"]),
        mon("Weepinbell", 23, "Eviolite", "Chlorophyll", "Adamant", ["Bullet Seed", "Poison Jab", "Sleep Powder", "Knock Off"]),
        mon("Larvitar", 23, "Eviolite", "Guts", "Adamant", ["Rock Slide", "Crunch", "Bulldoze", "Dragon Dance"])],
}

# --- Team Rocket: Proton in Slowpoke Well (1 badge, cap 16) -----------------------------------------
PROTON_1 = [
    mon("Koffing", 13, "Eviolite", "Levitate", "Bold", ["Sludge", "Will O Wisp", "Clear Smog", "Smokescreen"]),
    mon("Slowpoke", 14, "Eviolite", "Regenerator", "Relaxed", ["Water Pulse", "Confusion", "Yawn", "Slack Off"]),
    mon("Houndour", 15, "Charcoal", "Flash Fire", "Timid", ["Incinerate", "Snarl", "Smog", "Nasty Plot"]),
]

# --- Team Rocket: Rocket Hideout (5 or 6 badges, cap 36 or 38: aces at 36) ------------------------
PETREL_1 = [
    mon("Weezing", 34, "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Fire Blast"]),
    mon("Forretress", 34, "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Pupitar", 35, "Eviolite", "Shed Skin", "Adamant", ["Rock Slide", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Drapion", 36, "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_1 = [
    mon("Arbok", 34, "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", 34, "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
    mon("Vileplume", 35, "Black Sludge", "Effect Spore", "Calm", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Honchkrow", 36, "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
]

# --- Team Rocket: Radio Tower (7 badges, cap 45) ----------------------------------------------------
PROTON_2 = [
    mon("Muk", 42, "Black Sludge", "Poison Touch", "Adamant", ["Gunk Shot", "Shadow Sneak", "Knock Off", "Curse"]),
    mon("Nidoqueen", 42, "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    mon("Weezing", 43, "Rocky Helmet", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
    mon("Nidoking", 43, "Life Orb", "Sheer Force", "Timid", ["Earth Power", "Sludge Wave", "Ice Beam", "Thunderbolt"]),
    mon("Rhydon", 44, "Eviolite", "Lightning Rod", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Swords Dance"]),
]
PETREL_2 = [
    mon("Forretress", 43, "Leftovers", "Sturdy", "Relaxed", ["Spikes", "Volt Switch", "Gyro Ball", "Rapid Spin"]),
    mon("Weezing Galar", 43, "Black Sludge", "Neutralizing Gas", "Bold", ["Strange Steam", "Sludge Bomb", "Will O Wisp", "Pain Split"]),
    mon("Pupitar", 43, "Eviolite", "Shed Skin", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Cloyster", 44, "Focus Sash", "Skill Link", "Adamant", ["Icicle Spear", "Rock Blast", "Shell Smash", "Liquidation"]),
    mon("Drapion", 44, "Black Glasses", "Sniper", "Jolly", ["Knock Off", "Poison Jab", "Earthquake", "Swords Dance"]),
]
ARIANA_2 = [
    mon("Arbok", 43, "Black Sludge", "Intimidate", "Adamant", ["Gunk Shot", "Sucker Punch", "Glare", "Earthquake"]),
    mon("Persian", 43, "Silk Scarf", "Technician", "Jolly", ["Fake Out", "Faint Attack", "U Turn", "Hypnosis"]),
    mon("Vileplume", 43, "Black Sludge", "Effect Spore", "Calm", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Gyarados", 44, "Sitrus Berry", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Honchkrow", 44, "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
]
ARCHER = [
    mon("Porygon Z", 43, "Choice Specs", "Adaptability", "Modest", ["Tri Attack", "Thunderbolt", "Ice Beam", "Shadow Ball"]),
    mon("Tauros", 43, "Life Orb", "Intimidate", "Jolly", ["Double Edge", "Earthquake", "Rock Slide", "Zen Headbutt"]),
    mon("Crawdaunt", 44, "Life Orb", "Adaptability", "Adamant", ["Crabhammer", "Knock Off", "Aqua Jet", "Swords Dance"]),
    mon("Slowbro", 44, "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Calm Mind"]),
    mon("Bisharp", 44, "Black Glasses", "Defiant", "Adamant", ["Sucker Punch", "Iron Head", "Knock Off", "Swords Dance"]),
    mon("Houndoom", 45, "Houndoominite", "Flash Fire", "Timid", ["Fire Blast", "Dark Pulse", "Sludge Bomb", "Nasty Plot"]),
]

# --- Rival: Goldenrod Underground (7 badges, cap 45) and Victory Road (8 badges, cap 56) -------------
RIVAL_STARTER[4] = {
    "CYNDAQUIL": mon("Typhlosion", 45, "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Extrasensory"]),
    "TOTODILE": mon("Feraligatr", 45, "Life Orb", "Sheer Force", "Adamant", ["Liquidation", "Ice Punch", "Crunch", "Dragon Dance"]),
    "CHIKORITA": mon("Meganium", 45, "Leftovers", "Overgrow", "Bold", ["Energy Ball", "Earth Power", "Leech Seed", "Synthesis"]),
}
RIVAL_STARTER[5] = {
    "CYNDAQUIL": mon("Typhlosion", 56, "Choice Scarf", "Flash Fire", "Timid", ["Eruption", "Fire Blast", "Focus Blast", "Extrasensory"]),
    "TOTODILE": mon("Feraligatr", 56, "Life Orb", "Sheer Force", "Adamant", ["Liquidation", "Ice Punch", "Crunch", "Dragon Dance"]),
    "CHIKORITA": mon("Meganium", 56, "Leftovers", "Overgrow", "Bold", ["Energy Ball", "Earth Power", "Leech Seed", "Synthesis"]),
}
RIVAL_TEAM[4] = [
    mon("Crobat", 43, "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Weavile", 43, "Life Orb", "Pressure", "Jolly", ["Knock Off", "Ice Punch", "Ice Shard", "Low Kick"]),
    mon("Victreebel", 44, "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Sleep Powder"]),
    mon("Pupitar", 44, "Eviolite", "Shed Skin", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
]
RIVAL_TEAM[5] = [
    mon("Crobat", 54, "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Weavile", 54, "Life Orb", "Pressure", "Jolly", ["Knock Off", "Ice Punch", "Ice Shard", "Low Kick"]),
    mon("Victreebel", 55, "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Sleep Powder"]),
    mon("Ursaring", 55, "Flame Orb", "Guts", "Adamant", ["Facade", "Close Combat", "Crunch", "Swords Dance"]),
    mon("Tyranitar", 55, "Tyranitarite", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
]

# --- Kimono Girls: Ecruteak Dance Theater, one after another (8 badges, cap 56) ----------------------
KIMONO = {
    "TRAINER_ZUKI_HNS": [mon("Umbreon", 54, "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Moonlight", "Protect", "Toxic"])],
    "TRAINER_NAOKO_HNS": [mon("Espeon", 54, "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"])],
    "TRAINER_MIKI_HNS": [mon("Flareon", 55, "Toxic Orb", "Guts", "Adamant", ["Flare Blitz", "Facade", "Superpower", "Quick Attack"])],
    "TRAINER_SAYO_HNS": [mon("Jolteon", 55, "Choice Specs", "Volt Absorb", "Timid", ["Thunderbolt", "Shadow Ball", "Volt Switch", "Hyper Voice"])],
    "TRAINER_KUNI_HNS": [mon("Vaporeon", 56, "Leftovers", "Water Absorb", "Bold", ["Scald", "Ice Beam", "Wish", "Protect"])],
}

# --- Elite Four and Lance (8 badges, cap 56) -----------------------------------------------------------
WILL = [
    mon("Xatu", 54, "Light Clay", "Magic Bounce", "Timid", ["Psychic", "Air Slash", "Roost", "Reflect"]),
    mon("Slowbro", 54, "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Calm Mind"]),
    mon("Bronzong", 54, "Leftovers", "Levitate", "Relaxed", ["Trick Room", "Gyro Ball", "Earthquake", "Stealth Rock"]),
    mon("Farigiraf", 55, "Sitrus Berry", "Armor Tail", "Modest", ["Twin Beam", "Hyper Voice", "Shadow Ball", "Nasty Plot"]),
    mon("Gardevoir", 55, "Choice Scarf", "Trace", "Timid", ["Moonblast", "Psychic", "Mystical Fire", "Focus Blast"]),
    mon("Alakazam", 55, "Alakazite", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Calm Mind"]),
]
KOGA = [
    mon("Toxapex", 54, "Black Sludge", "Regenerator", "Bold", ["Scald", "Toxic", "Recover", "Haze"]),
    mon("Muk Alola", 54, "Black Sludge", "Poison Touch", "Adamant", ["Knock Off", "Poison Jab", "Ice Punch", "Shadow Sneak"]),
    mon("Toxicroak", 54, "Life Orb", "Dry Skin", "Jolly", ["Gunk Shot", "Drain Punch", "Sucker Punch", "Swords Dance"]),
    mon("Venomoth", 55, "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sludge Bomb", "Sleep Powder"]),
    mon("Beedrill", 55, "Beedrillite", "Sniper", "Jolly", ["Poison Jab", "U Turn", "Drill Run", "Swords Dance"]),
    mon("Crobat", 55, "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
]
BRUNO = [
    mon("Hitmontop", 55, "Rocky Helmet", "Intimidate", "Impish", ["Fake Out", "Close Combat", "Sucker Punch", "Rapid Spin"]),
    mon("Steelix", 55, "Leftovers", "Sturdy", "Impish", ["Heavy Slam", "Earthquake", "Stone Edge", "Stealth Rock"]),
    mon("Hitmonlee", 55, "Life Orb", "Reckless", "Jolly", ["High Jump Kick", "Knock Off", "Blaze Kick", "Fake Out"]),
    mon("Hitmonchan", 55, "Punching Glove", "Iron Fist", "Adamant", ["Drain Punch", "Ice Punch", "Thunder Punch", "Mach Punch"]),
    mon("Machamp", 55, "Sitrus Berry", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"]),
    mon("Lucario", 56, "Lucarionite", "Inner Focus", "Adamant", ["Close Combat", "Meteor Mash", "Extreme Speed", "Swords Dance"]),
]
KAREN = [
    mon("Umbreon", 55, "Leftovers", "Inner Focus", "Calm", ["Foul Play", "Wish", "Protect", "Toxic"]),
    mon("Vileplume", 55, "Black Sludge", "Effect Spore", "Bold", ["Giga Drain", "Sludge Bomb", "Sleep Powder", "Strength Sap"]),
    mon("Gengar", 55, "Life Orb", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Focus Blast", "Nasty Plot"]),
    mon("Honchkrow", 55, "Scope Lens", "Super Luck", "Adamant", ["Brave Bird", "Night Slash", "Sucker Punch", "Heat Wave"]),
    mon("Absol", 55, "Absolite", "Super Luck", "Adamant", ["Knock Off", "Sucker Punch", "Play Rough", "Swords Dance"]),
    mon("Houndoom", 56, "Black Glasses", "Flash Fire", "Timid", ["Fire Blast", "Dark Pulse", "Sludge Bomb", "Nasty Plot"]),
]
# Lance leads Mega Gyarados (tools/emurun/tests/mega_evolution.emu checks it Mega Evolves on turn 1)
# One Dragon Dance sweeper (Dragonite): with Mega Gyarados and Salamence also setting up, the
# prepared six of the bosses_m4 play test lost all of six tries. Charizard attacks instead of
# Roosting: with the Full Restores it outlasted every team built for Lance in the play tests.
LANCE = [
    mon("Gyarados", 55, "Gyaradosite", "Intimidate", "Jolly", ["Waterfall", "Crunch", "Earthquake", "Thunder Wave"]),
    mon("Aerodactyl", 55, "Focus Sash", "Unnerve", "Jolly", ["Stone Edge", "Earthquake", "Taunt", "Stealth Rock"]),
    mon("Charizard", 55, "Charcoal", "Solar Power", "Timid", ["Fire Blast", "Air Slash", "Focus Blast", "Dragon Pulse"]),
    mon("Salamence", 56, "Life Orb", "Intimidate", "Jolly", ["Outrage", "Earthquake", "Fire Fang", "Dual Wingbeat"]),
    mon("Garchomp", 56, "Rocky Helmet", "Rough Skin", "Jolly", ["Earthquake", "Dragon Claw", "Stone Edge", "Swords Dance"]),
    mon("Dragonite", 56, "Lum Berry", "Multiscale", "Adamant", ["Extreme Speed", "Dragon Dance", "Earthquake", "Outrage"]),
]

# --- Kanto Gym Leaders and Blue (after the Johto League: cap 70, any order) ------------------------
BROCK = [
    mon("Golem", 68, "Leftovers", "Sturdy", "Adamant", ["Stealth Rock", "Earthquake", "Stone Edge", "Explosion"]),
    mon("Omastar", 68, "White Herb", "Swift Swim", "Modest", ["Shell Smash", "Hydro Pump", "Ice Beam", "Earth Power"]),
    mon("Kabutops", 68, "Life Orb", "Swift Swim", "Adamant", ["Stone Edge", "Liquidation", "Swords Dance", "Aqua Jet"]),
    mon("Relicanth", 69, "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Liquidation", "Earthquake", "Double Edge"]),
    mon("Kleavor", 69, "Focus Sash", "Sharpness", "Jolly", ["Stone Axe", "X Scissor", "Close Combat", "Swords Dance"]),
    mon("Aerodactyl", 70, "Aerodactylite", "Unnerve", "Jolly", ["Stone Edge", "Earthquake", "Crunch", "Ice Fang"]),
]
MISTY = [
    mon("Pelipper", 68, "Damp Rock", "Drizzle", "Bold", ["Scald", "Hurricane", "U Turn", "Roost"]),
    mon("Golduck", 68, "Life Orb", "Swift Swim", "Timid", ["Hydro Pump", "Ice Beam", "Psychic", "Nasty Plot"]),
    mon("Lapras", 68, "Leftovers", "Water Absorb", "Modest", ["Freeze Dry", "Hydro Pump", "Thunderbolt", "Ice Shard"]),
    mon("Milotic", 69, "Leftovers", "Competitive", "Bold", ["Scald", "Ice Beam", "Recover", "Haze"]),
    mon("Blastoise", 69, "Blastoisinite", "Torrent", "Modest", ["Water Pulse", "Aura Sphere", "Dark Pulse", "Ice Beam"]),
    mon("Starmie", 70, "Wise Glasses", "Analytic", "Timid", ["Hydro Pump", "Psychic", "Thunderbolt", "Ice Beam"]),
]
LT_SURGE = [
    mon("Electrode", 68, "Focus Sash", "Aftermath", "Timid", ["Thunderbolt", "Volt Switch", "Taunt", "Explosion"]),
    mon("Magnezone", 68, "Choice Specs", "Magnet Pull", "Modest", ["Thunderbolt", "Flash Cannon", "Volt Switch", "Body Press"]),
    mon("Lanturn", 68, "Leftovers", "Volt Absorb", "Bold", ["Scald", "Discharge", "Ice Beam", "Heal Bell"]),
    mon("Electivire", 69, "Life Orb", "Motor Drive", "Adamant", ["Wild Charge", "Ice Punch", "Earthquake", "Cross Chop"]),
    mon("Manectric", 69, "Manectite", "Lightning Rod", "Timid", ["Thunderbolt", "Overheat", "Snarl", "Volt Switch"]),
    mon("Raichu", 70, "Magnet", "Lightning Rod", "Timid", ["Thunderbolt", "Focus Blast", "Nasty Plot", "Grass Knot"]),
]
ERIKA = [
    mon("Jumpluff", 68, "Leftovers", "Infiltrator", "Jolly", ["Sleep Powder", "Leech Seed", "Acrobatics", "U Turn"]),
    mon("Roserade", 68, "Life Orb", "Technician", "Timid", ["Giga Drain", "Sludge Bomb", "Shadow Ball", "Spikes"]),
    mon("Tangrowth", 68, "Rocky Helmet", "Regenerator", "Relaxed", ["Giga Drain", "Knock Off", "Earthquake", "Sleep Powder"]),
    mon("Victreebel", 69, "Black Sludge", "Chlorophyll", "Adamant", ["Power Whip", "Sucker Punch", "Poison Jab", "Weather Ball"]),
    mon("Bellossom", 69, "Sitrus Berry", "Chlorophyll", "Modest", ["Quiver Dance", "Giga Drain", "Moonblast", "Strength Sap"]),
    mon("Venusaur", 70, "Venusaurite", "Chlorophyll", "Modest", ["Giga Drain", "Sludge Bomb", "Earth Power", "Synthesis"]),
]
JANINE = [
    mon("Weezing", 68, "Black Sludge", "Levitate", "Bold", ["Sludge Bomb", "Will O Wisp", "Pain Split", "Toxic Spikes"]),
    mon("Nidoqueen", 68, "Life Orb", "Sheer Force", "Modest", ["Earth Power", "Sludge Wave", "Ice Beam", "Flamethrower"]),
    mon("Muk", 68, "Leftovers", "Poison Touch", "Adamant", ["Gunk Shot", "Knock Off", "Shadow Sneak", "Curse"]),
    mon("Crobat", 69, "Sharp Beak", "Infiltrator", "Jolly", ["Brave Bird", "Cross Poison", "U Turn", "Roost"]),
    mon("Venomoth", 69, "Focus Sash", "Tinted Lens", "Timid", ["Quiver Dance", "Bug Buzz", "Sludge Bomb", "Sleep Powder"]),
    mon("Gengar", 70, "Gengarite", "Levitate", "Timid", ["Shadow Ball", "Sludge Bomb", "Focus Blast", "Nasty Plot"]),
]
SABRINA = [
    mon("Mr Mime", 68, "Light Clay", "Filter", "Timid", ["Light Screen", "Reflect", "Psychic", "Dazzling Gleam"]),
    mon("Wobbuffet", 68, "Sitrus Berry", "Shadow Tag", "Bold", ["Counter", "Mirror Coat", "Encore", "Destiny Bond"]),
    mon("Slowbro", 68, "Leftovers", "Regenerator", "Bold", ["Scald", "Psyshock", "Slack Off", "Thunder Wave"]),
    mon("Espeon", 69, "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"]),
    mon("Alakazam", 69, "Twisted Spoon", "Magic Guard", "Timid", ["Psychic", "Shadow Ball", "Focus Blast", "Calm Mind"]),
    mon("Metagross", 70, "Metagrossite", "Clear Body", "Jolly", ["Meteor Mash", "Zen Headbutt", "Earthquake", "Bullet Punch"]),
]
BLAINE = [
    mon("Torkoal", 68, "Heat Rock", "Drought", "Bold", ["Lava Plume", "Stealth Rock", "Rapid Spin", "Yawn"]),
    mon("Rapidash", 68, "Life Orb", "Flash Fire", "Jolly", ["Flare Blitz", "Wild Charge", "High Horsepower", "Morning Sun"]),
    mon("Magmortar", 68, "Expert Belt", "Vital Spirit", "Modest", ["Fire Blast", "Thunderbolt", "Focus Blast", "Psychic"]),
    mon("Volcarona", 69, "Charcoal", "Flame Body", "Timid", ["Quiver Dance", "Fiery Dance", "Bug Buzz", "Giga Drain"]),
    mon("Arcanine Hisui", 69, "Choice Band", "Rock Head", "Adamant", ["Head Smash", "Flare Blitz", "Extreme Speed", "Wild Charge"]),
    mon("Camerupt", 70, "Cameruptite", "Solid Rock", "Modest", ["Fire Blast", "Earth Power", "Ancient Power", "Stealth Rock"]),
]
# Machamp has Close Combat, not No Guard Dynamic Punch: with the guaranteed confusion, Blue beat
# every play-test team in all six tries (Bruno's Machamp likewise).
BLUE = [
    mon("Machamp", 69, "Sitrus Berry", "No Guard", "Adamant", ["Close Combat", "Stone Edge", "Knock Off", "Bullet Punch"]),
    mon("Exeggutor", 69, "Sitrus Berry", "Harvest", "Modest", ["Leaf Storm", "Psychic", "Sludge Bomb", "Trick Room"]),
    mon("Rhyperior", 69, "Weakness Policy", "Solid Rock", "Adamant", ["Stone Edge", "Earthquake", "Megahorn", "Rock Polish"]),
    mon("Arcanine", 70, "Choice Band", "Intimidate", "Adamant", ["Flare Blitz", "Extreme Speed", "Wild Charge", "Close Combat"]),
    mon("Tyranitar", 70, "Leftovers", "Sand Stream", "Adamant", ["Stone Edge", "Crunch", "Earthquake", "Dragon Dance"]),
    mon("Pidgeot", 70, "Pidgeotite", "Keen Eye", "Timid", ["Hurricane", "Heat Wave", "U Turn", "Roost"]),
]

# --- Red on Mt. Silver: the hardest battle in the game (DECISIONS.md D27) ------------------------
# No level cap once the player is Kanto Champion. His first battle is at 96-100, the rematch after
# the Sinjoh storyline (TRAINER_RED_POSTOBC_HNS) all at 100; every Pokemon has a competitive EV
# spread, which Minimal Grinding leaves him (src/pokemon.c).
RED_SIX = [
    mon("Pikachu", None, "Light Ball", "Lightning Rod", "Hasty", ["Volt Tackle", "Surf", "Knock Off", "Fake Out"],
        "252 Atk / 4 SpA / 252 Spe"),
    mon("Espeon", None, "Life Orb", "Magic Bounce", "Timid", ["Psychic", "Dazzling Gleam", "Shadow Ball", "Calm Mind"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Snorlax", None, "Leftovers", "Thick Fat", "Careful", ["Curse", "Body Slam", "Rest", "Sleep Talk"],
        "252 HP / 4 Atk / 252 SpD"),
    mon("Venusaur", None, "Life Orb", "Chlorophyll", "Modest", ["Sleep Powder", "Growth", "Giga Drain", "Sludge Bomb"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Blastoise", None, "White Herb", "Torrent", "Modest", ["Shell Smash", "Hydro Pump", "Ice Beam", "Aura Sphere"],
        "4 HP / 252 SpA / 252 Spe"),
    mon("Charizard", None, "Charizardite Y", "Solar Power", "Timid", ["Fire Blast", "Solar Beam", "Focus Blast", "Air Slash"],
        "4 HP / 252 SpA / 252 Spe"),
]
RED = team([96, 96, 97, 97, 98, 100], RED_SIX)
RED_REMATCH = team([100] * 6, RED_SIX)
RED_ITEMS = "Full Restore / Full Restore / Full Restore / Full Restore"

TEAMS = {
    "TRAINER_BROCK_HNS": ("Full Restore / Full Restore", BROCK),
    "TRAINER_MISTY_HNS": ("Full Restore / Full Restore", MISTY),
    "TRAINER_LTSURGE_HNS": ("Full Restore / Full Restore", LT_SURGE),
    "TRAINER_ERIKA_HNS": ("Full Restore / Full Restore", ERIKA),
    "TRAINER_JANINE_HNS": ("Full Restore / Full Restore", JANINE),
    "TRAINER_SABRINA_HNS": ("Full Restore / Full Restore", SABRINA),
    "TRAINER_BLAINE_HNS": ("Full Restore / Full Restore", BLAINE),
    "TRAINER_BLUE_HNS": ("Full Restore / Full Restore", BLUE),
    "TRAINER_RED_HNS": (RED_ITEMS, RED, RED_AI),
    "TRAINER_RED_POSTOBC_HNS": (RED_ITEMS, RED_REMATCH, RED_AI),
    "TRAINER_PETREL_1_HNS": ("Full Restore / Full Restore", PETREL_1),
    "TRAINER_ARIANA_1_HNS": ("Full Restore / Full Restore", ARIANA_1),
    "TRAINER_PROTON_2_HNS": ("Full Restore / Full Restore", PROTON_2),
    "TRAINER_PETREL_2_HNS": ("Full Restore / Full Restore", PETREL_2),
    "TRAINER_ARIANA_2_HNS": ("Full Restore / Full Restore", ARIANA_2),
    "TRAINER_ARCHER_HNS": ("Full Restore / Full Restore", ARCHER),
    "TRAINER_WILL_1_HNS": ("Full Restore / Full Restore", WILL),
    "TRAINER_KOGA_1_HNS": ("Full Restore / Full Restore", KOGA),
    "TRAINER_BRUNO_1_HNS": ("Full Restore / Full Restore", BRUNO),
    "TRAINER_KAREN_1_HNS": ("Full Restore / Full Restore", KAREN),
    "TRAINER_LANCE_1_HNS": ("Full Restore / Full Restore", LANCE),
    "TRAINER_PROTON_1_HNS": ("Super Potion", PROTON_1),
    "TRAINER_MORTY_1_HNS": ("Hyper Potion / Hyper Potion", MORTY),
    "TRAINER_CHUCK_1_HNS": ("Hyper Potion / Hyper Potion", team([29, 29, 30, 30, 31], five_of_six(CHUCK, 2))),
    "TRAINER_CHUCK_1_2_HNS": ("Full Restore / Full Restore", team([34, 34, 35, 35, 35, 36], CHUCK)),
    "TRAINER_CHUCK_1_3_HNS": ("Full Restore / Full Restore", team([36, 36, 37, 37, 37, 38], CHUCK)),
    "TRAINER_JASMINE_1_HNS": ("Hyper Potion / Hyper Potion", team([29, 29, 30, 30, 31], five_of_six(JASMINE, 2))),
    "TRAINER_JASMINE_1_2_HNS": ("Full Restore / Full Restore", team([34, 34, 35, 35, 35, 36], JASMINE)),
    "TRAINER_JASMINE_1_3_HNS": ("Full Restore / Full Restore", team([36, 36, 37, 37, 37, 38], JASMINE)),
    "TRAINER_PRYCE_1_HNS": ("Hyper Potion / Hyper Potion", team([29, 29, 30, 30, 31], five_of_six(PRYCE, 1))),
    "TRAINER_PRYCE_1_2_HNS": ("Full Restore / Full Restore", team([34, 34, 35, 35, 35, 36], PRYCE)),
    "TRAINER_PRYCE_1_3_HNS": ("Full Restore / Full Restore", team([36, 36, 37, 37, 37, 38], PRYCE)),
    "TRAINER_CLAIR_1_HNS": ("Full Restore / Full Restore", CLAIR),
}
TEAMS.update({tid: ("", mons) for tid, mons in KIMONO.items()})
for _n, _items in ((2, "Super Potion"), (3, "Super Potion / Super Potion"), (4, "Full Restore / Full Restore"),
                   (5, "Full Restore / Full Restore")):
    for _starter, _ace in RIVAL_STARTER[_n].items():
        TEAMS[f"TRAINER_RIVAL_{_starter}_{_n}_HNS"] = (_items, RIVAL_TEAM[_n] + [_ace])


def render(tid, header, items, mons, ai=BOSS_AI):
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
        out += f"Level: {m['level']}\n"
        out += "IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe\n"
        if m.get("evs"):
            out += f"EVs: {m['evs']}\n"
        out += f"Ability: {m['ability']}\n"
        out += f"Nature: {m['nature']}\n"
        out += "".join(f"- {mv}\n" for mv in m["moves"])
    return out


def apply(text):
    blocks = re.split(r"(?m)^(?==== )", text)
    seen = set()
    for i, block in enumerate(blocks):
        m = re.match(r"=== (\w+) ===", block)
        if not m or m.group(1) not in TEAMS:
            continue
        tid = m.group(1)
        seen.add(tid)
        header = block.split("\n\n", 1)[0]
        items, mons, *ai = TEAMS[tid]
        blocks[i] = render(tid, header, items, mons, *ai) + "\n"
    missing = set(TEAMS) - seen
    if missing:
        sys.exit(f"trainers not found: {sorted(missing)}")
    return "".join(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    text = open(PARTY, encoding="utf-8").read()
    new = apply(text)
    if args.check:
        if new != text:
            print("src/data/trainers_hns.party is out of date: run tools/crystal_imperium/boss_teams.py")
            return 1
        return 0
    if new != text:
        open(PARTY, "w", encoding="utf-8").write(new)
        print(f"updated {len(TEAMS)} boss parties")
    return 0


if __name__ == "__main__":
    sys.exit(main())
