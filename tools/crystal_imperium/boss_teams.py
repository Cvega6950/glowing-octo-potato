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
"""
import argparse
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PARTY = os.path.join(ROOT, "src", "data", "trainers_hns.party")

BOSS_AI = "Smart Trainer / Ace Pokemon / HP Aware"


def mon(species, level, item, ability, nature, moves):
    return {"species": species, "level": level, "item": item, "ability": ability, "nature": nature, "moves": moves}


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

TEAMS = {
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
for _n, _items in ((2, "Super Potion"), (3, "Super Potion / Super Potion")):
    for _starter, _ace in RIVAL_STARTER[_n].items():
        TEAMS[f"TRAINER_RIVAL_{_starter}_{_n}_HNS"] = (_items, RIVAL_TEAM[_n] + [_ace])


def render(tid, header, items, mons):
    lines = []
    for line in header.splitlines():
        if line.startswith("AI:"):
            line = "AI: " + BOSS_AI
        elif line.startswith("Items:"):
            line = "Items: " + items
        lines.append(line)
    if not any(l.startswith("Items:") for l in lines):
        lines.append("Items: " + items)
    out = "\n".join(lines) + "\n"
    for m in mons:
        out += f"\n{m['species']} @ {m['item']}\n"
        out += f"Level: {m['level']}\n"
        out += "IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe\n"
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
        items, mons = TEAMS[tid]
        blocks[i] = render(tid, header, items, mons) + "\n"
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
