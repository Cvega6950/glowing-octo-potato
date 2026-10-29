#!/usr/bin/env python3
"""Crystal Imperium Ace Trainers (DECISIONS.md D47): more Ace Trainers on the routes, with competitive
teams, as Emerald Imperium has. From the tables in ace_trainer_data.py this writes:

  include/constants/opponents_hns.h    their trainer IDs (after the side battles': an ID indexes the
                                       saved defeat flag, so an ID never changes)
  src/data/trainers_hns.party          each one's party; and the teams of Heart & Soul's own Ace
                                       Trainers (Cooltrainers) that UPGRADES lists, at the stage of
                                       their Heart & Soul levels
  data/scripts/ace_trainers.inc        their scripts and texts
  data/maps/*/map.json                 each one's object on its route: a trainer that sees the player
                                       across its sight range, walks up and battles

  python3 tools/crystal_imperium/ace_trainers.py           # rewrite the files
  python3 tools/crystal_imperium/ace_trainers.py --check   # exit 1 if any is out of date

Run it after side_battles.py and before boss_teams.py. They are ordinary trainers, not bosses: their
levels follow the player's highest level, one to three below (src/battle_main.c, D46), never below
the cap curve's level for their party data's levels, which the script sets three below the cap of
the route's stage (party_levels). A spot is checked as a side battle's is (side_battles.MapData): on foot, not water,
not a ledge, nothing else on the tile, no door next to it, and it cuts no one off; its line of sight
is ground the trainer can walk and meets no other trainer's.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import side_battles as sb  # noqa: E402  (maps, texts, the trainer ID block's neighbour)
import ace_trainer_data as data  # noqa: E402  (the trainers and their teams)
import boss_teams  # noqa: E402  (the caps, from src/caps.c, and the friendship moves)

ROOT = sb.ROOT
OPPONENTS, PARTY = sb.OPPONENTS, sb.PARTY
SCRIPTS = os.path.join(ROOT, "data", "scripts", "ace_trainers.inc")
FIRST_ID = 679  # after the side battles' (Heart & Soul's own end at 652, D41's at 678)
OPP_START = "// Crystal Imperium Ace Trainers (DECISIONS.md D47): written by tools/crystal_imperium/ace_trainers.py"
OPP_END = "// End of the Ace Trainers"
GFX = {"Male": "OBJ_EVENT_GFX_COOLTRAINER_M_HNS", "Female": "OBJ_EVENT_GFX_COOLTRAINER_F_HNS"}
PIC = {"Male": "Cooltrainer M", "Female": "Cooltrainer F"}
MUSIC = {"Male": "Hg Suspicious 2", "Female": "Hg Girl 1"}
AI = "Smart Trainer / Ace Pokemon / HP Aware"
LEDGES = {"MB_JUMP_SOUTH", "MB_JUMP_NORTH", "MB_JUMP_EAST", "MB_JUMP_WEST", "MB_JUMP_SOUTHEAST",
          "MB_JUMP_SOUTHWEST", "MB_JUMP_NORTHEAST", "MB_JUMP_NORTHWEST"}
DIRS = {"down": (0, 1), "up": (0, -1), "left": (-1, 0), "right": (1, 0)}
HNS_CAPS = [11, 16, 21, 25, 31, 36, 38, 45, 56, 70, 100]  # src/caps.c sHnsLevelCaps


def trainer_const(ace):
    return f"TRAINER_ACE_{ace['key']}_HNS"


def label(ace):
    return "AceTrainer_" + ace["key"].title().replace("_", "")


def stage_cap(stage):
    """The NORMAL level cap at a stage (boss_teams.py's caps; 9 is after the Johto League)."""
    return boss_teams.cap(boss_teams.JOHTO_CHAMPION if stage >= 9 else stage)


def curve(level):
    """src/caps.c GetLevelOnCapCurve with the NORMAL caps: a Heart & Soul level on this game's curve."""
    if level <= 1:
        return level
    hns_from, cap_from = 1, 1
    for stage, hns_to in enumerate(HNS_CAPS):
        cap_to = stage_cap(stage) if stage < 10 else 100
        if level <= hns_to:
            return cap_from + ((level - hns_from) * (cap_to - cap_from) + (hns_to - hns_from) // 2) // (hns_to - hns_from)
        hns_from, cap_from = hns_to, cap_to
    return 100


def party_levels(stage, size):
    """The party data's levels: the strongest at the highest Heart & Soul level the cap curve puts at
    least three below the cap of the route's stage (its floor), the next one a level less, the others
    two less; the
    battle code then puts them one, two and three below the player's highest level
    (GetLevelBelowPlayer), never below their floors."""
    target = stage_cap(stage) - 3
    top = max(level for level in range(1, 101) if curve(level) <= target)
    return [top - min(2, i) for i in range(size)][::-1]


def render_mons(mons, levels):
    out = ""
    for m, level in zip(mons, levels):
        out += f"\n{m['species']} @ {m['item']}\nLevel: {level}\n"
        out += "IVs: 31 HP / 31 Atk / 31 Def / 31 SpA / 31 SpD / 31 Spe\n"
        if m.get("evs"):
            out += f"EVs: {m['evs']}\n"
        out += f"Ability: {m['ability']}\nNature: {m['nature']}\n"
        if boss_teams.FRIENDSHIP_MOVES & set(m["moves"]):
            out += f"Happiness: {boss_teams.FULL_FRIENDSHIP}\n"
        out += "".join(f"- {mv}\n" for mv in m["moves"])
    return out


def render_opponents(text):
    rows = [(FIRST_ID + i, trainer_const(a)) for i, a in enumerate(data.ACES)]
    block = [OPP_START] + [f"#define {t:<37} {tid}" for tid, t in rows] + [OPP_END, ""]
    start = text.find(OPP_START)
    if start >= 0:  # in place
        end = text.index(OPP_END, start) + len(OPP_END) + 1
        text = text[:start] + "\n".join(block) + text[end:]
    else:  # after the side battles' block, before the count
        count = re.search(r"#define TRAINERS_COUNT_HNS\s+(\d+)", text)
        text = text.replace(count.group(0), "\n".join(block) + "\n" + count.group(0))
    count = re.search(r"#define TRAINERS_COUNT_HNS\s+(\d+)", text)
    others = [int(v) for v in re.findall(r"(?m)^#define TRAINER_\w+\s+(\d+)\s*$", text)]
    new_count = max(others + [tid for tid, _ in rows]) + 1
    if new_count > sb.MAX_TRAINER_ID + 1:
        sys.exit(f"{new_count} trainers: the save has flags for {sb.MAX_TRAINER_ID + 1}")
    return text.replace(count.group(0), re.sub(r"\d+$", str(new_count), count.group(0)))


def render_party(text):
    trail = len(text) - len(text.rstrip("\n"))  # the file's own ending stays (boss_teams.py writes it too)
    text = text.rstrip("\n")
    # An Ace Trainer no longer in the table loses its block
    keep = {trainer_const(a) for a in data.ACES}
    for m in list(re.finditer(r"(?ms)^=== (TRAINER_ACE_\w+_HNS) ===\n.*?(?=^=== |\Z)", text))[::-1]:
        if m.group(1) not in keep:
            text = text[:m.start()] + text[m.end():]
    for a in data.ACES:
        t = trainer_const(a)
        block = (f"=== {t} ===\nName: {a['name']}\nClass: Cooltrainer Hns\nPic: {PIC[a['gender']]}\n"
                 f"Gender: {a['gender']}\nMusic: {MUSIC[a['gender']]}\nDouble Battle: No\nAI: {AI}\n"
                 + render_mons(a["team"], party_levels(a["stage"], len(a["team"]))))
        m = re.search(r"(?ms)^=== " + t + r" ===\n.*?(?=^=== |\Z)", text)
        if m:
            rest = text[m.end():].lstrip("\n")
            text = text[:m.start()] + block.rstrip("\n") + ("\n\n\n" + rest if rest else "")
        else:
            text = text.rstrip("\n") + "\n\n\n" + block.rstrip("\n")
    for t, mons in data.UPGRADES.items():
        m = re.search(r"(?ms)^=== " + t + r" ===\n.*?(?=^=== |\Z)", text)
        if not m:
            sys.exit(f"{t}: no such trainer in the party file")
        header = m.group(0).split("\n\n")[0]
        # The trainer keeps its place in the game: the stage of its Heart & Soul levels
        levels = [int(v) for v in re.findall(r"(?m)^Level: (\d+)", m.group(0))]
        stage = next(i for i, c in enumerate(HNS_CAPS) if max(levels) <= c or i == len(HNS_CAPS) - 1)
        header = re.sub(r"(?m)^AI: .*$", "AI: " + AI, header)
        new = header + "\n" + render_mons(mons, party_levels(stage, len(mons))).rstrip("\n")
        rest = text[m.end():].lstrip("\n")
        text = text[:m.start()] + new + ("\n\n\n" + rest if rest else "")
    return text.rstrip("\n") + "\n" * trail


def render_scripts(text):
    out = ["@ Crystal Imperium Ace Trainers (DECISIONS.md D47): written by tools/crystal_imperium/ace_trainers.py", ""]
    for a in data.ACES:
        lab, t = label(a), label(a).replace("AceTrainer_", "AceTrainer_Text_")
        out += [f"{lab}_EventScript::",
                f"\ttrainerbattle_single {trainer_const(a)}, {t}_Intro, {t}_Defeat",
                f"\tmsgbox {t}_After, MSGBOX_AUTOCLOSE", "\tend", ""]
        for name in ("intro", "defeat", "after"):
            out += text.inc(f"{t}_{name.title()}", a[name])
    return "\n".join(out).rstrip("\n") + "\n"


def check_spot(a, m, placed):
    """Why the spot can't take this trainer, or None."""
    x, y, facing, sight = a["x"], a["y"], a["facing"], a["sight"]
    surf = sb.surfable()

    def walkable(tx, ty):
        return (0 <= tx < m.w and 0 <= ty < m.h and not m.tile(tx, ty)[0]
                and m.behavior(tx, ty) not in surf and m.behavior(tx, ty) not in LEDGES)

    others = {(int(o["x"]), int(o["y"])) for o in m.json["object_events"] if o.get("script") != f"{label(a)}_EventScript"}
    others |= placed
    free = m.reachable(others)
    if not walkable(x, y) or (x, y) not in free:
        return "blocked, water, a ledge or out of reach"
    if m.taken(x, y, f"{label(a)}_EventScript"):
        return "something else is on the tile"
    if any(abs(int(e["x"]) - x) + abs(int(e["y"]) - y) <= 2 for e in m.json.get("warp_events") or []):
        return "next to a door or warp"
    dx, dy = DIRS[facing]
    for i in range(1, sight + 1):
        tx, ty = x + dx * i, y + dy * i
        if not walkable(tx, ty) or (tx, ty) not in free or m.taken(tx, ty, None) or (tx, ty) in others:
            return f"its line of sight meets ({tx},{ty}), which it can't walk"
    cut = free - m.reachable(others | {(x, y)}) - {(x, y)}
    if cut:
        return f"cuts off {sorted(cut)[:4]}"
    for o in m.json["object_events"]:
        if o.get("trainer_type") not in ("TRAINER_TYPE_NORMAL", "TRAINER_TYPE_SEE_ALL_DIRECTIONS") or o.get("script") == f"{label(a)}_EventScript":
            continue
        ox, oy, osight = int(o["x"]), int(o["y"]), int(o.get("trainer_sight_or_berry_tree_id") or 0)
        if abs(ox - x) + abs(oy - y) < 3:
            return f"too close to the trainer at ({ox},{oy})"
        for f in ("down", "up", "left", "right"):
            if o.get("movement_type", "").endswith(f.upper()) or o.get("trainer_type") == "TRAINER_TYPE_SEE_ALL_DIRECTIONS":
                ex, ey = DIRS[f]
                theirs = {(ox + ex * i, oy + ey * i) for i in range(1, osight + 1)}
                mine = {(x + dx * i, y + dy * i) for i in range(0, sight + 1)}
                if theirs & mine:
                    return f"its line of sight meets the trainer's at ({ox},{oy})"
    return None


def place_objects(check_only):
    stale, by_map = [], {}
    for a in data.ACES:
        by_map.setdefault(a["map"], []).append(a)
    # Maps with an Ace Trainer the table no longer has: its object goes
    scripts = {f"{label(a)}_EventScript" for a in data.ACES}
    for folder in sorted(os.listdir(os.path.join(ROOT, "data", "maps"))):
        path = os.path.join(ROOT, "data", "maps", folder, "map.json")
        if folder in by_map or not os.path.exists(path) or "AceTrainer_" not in sb.read(path):
            continue
        by_map[folder] = []
    for folder, aces in sorted(by_map.items()):
        m = sb.MapData(folder)
        placed = set()
        changed = False
        old = m.json["object_events"]
        m.json["object_events"] = [o for o in old if not str(o.get("script", "")).startswith("AceTrainer_")
                                   or o["script"] in scripts]
        changed = len(m.json["object_events"]) != len(old)
        for a in aces:
            why = check_spot(a, m, placed)
            if why:
                sys.exit(f"{a['key']} at ({a['x']},{a['y']}) on {folder}: {why}")
            placed.add((a["x"], a["y"]))
            obj = {"graphics_id": GFX[a["gender"]], "x": a["x"], "y": a["y"], "elevation": 0,
                   "movement_type": sb.FACINGS[a["facing"]], "movement_range_x": 0, "movement_range_y": 0,
                   "trainer_type": "TRAINER_TYPE_NORMAL", "trainer_sight_or_berry_tree_id": str(a["sight"]),
                   "script": f"{label(a)}_EventScript", "flag": "0"}
            objects = m.json["object_events"]
            mine = [i for i, o in enumerate(objects) if o.get("script") == obj["script"]]
            if mine:
                if objects[mine[0]] != obj:
                    objects[mine[0]] = obj
                    changed = True
            else:
                if len(objects) >= sb.MAX_MAP_OBJECTS:
                    sys.exit(f"{folder} has no room for another object")
                objects.append(obj)
                changed = True
        if changed:
            stale.append(os.path.relpath(m.path, ROOT))
            if not check_only:
                with open(m.path, "w", encoding="utf-8") as f:
                    json.dump(m.json, f, indent=2, ensure_ascii=False)
                    f.write("\n")
    return stale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    keys = [a["key"] for a in data.ACES]
    if len(set(keys)) != len(keys):
        sys.exit("two Ace Trainers share a key")
    for a in data.ACES:
        if len(a["name"]) > sb.MAX_NAME:
            sys.exit(f"{a['key']}: name {a['name']} is longer than {sb.MAX_NAME}")
    place_objects(True)  # every spot is checked before anything is written
    text = sb.Text()
    outputs = {OPPONENTS: render_opponents(sb.read(OPPONENTS)), PARTY: render_party(sb.read(PARTY)),
               SCRIPTS: render_scripts(text)}
    stale = []
    for path, new in outputs.items():
        old = sb.read(path) if os.path.exists(path) else ""
        if new != old:
            stale.append(os.path.relpath(path, ROOT))
            if not args.check:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
    stale += place_objects(args.check)
    if args.check and stale:
        print(f"{', '.join(stale)} out of date: run tools/crystal_imperium/ace_trainers.py")
        return 1
    for path in stale:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
