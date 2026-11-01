#!/usr/bin/env python3
"""Crystal Imperium's trainer play tests, written from the team tables (redesign plan 3.6) so they always match
them. This first version writes tools/emurun/tests/designed_species.emu: every designed battle (boss_teams.TEAMS,
ace_trainer_data.ACES and UPGRADES) started from the debug menu with the player at the team's own stage, and its
whole team checked as the battle code fields it there: the team size, every Pokemon at its stage's cap, as the
species it was made as (a team made for a stage keeps its Pokemon as made at its stage's cap,
GetTrainerMonEvolvedSpecies) and holding its item.

  python3 tools/crystal_imperium/trainer_tests.py           # rewrite the test
  python3 tools/crystal_imperium/trainer_tests.py --check   # exit 1 if it is out of date
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import boss_teams  # noqa: E402
import team_kit  # noqa: E402
import trainer_rules  # noqa: E402

ROOT = boss_teams.ROOT
TEST = os.path.join(ROOT, "tools", "emurun", "tests", "designed_species.emu")
PLAYER = 157  # the player's TYPHLOSION (its level doesn't matter: every trainer battles at the player's cap)


def label(tid):
    return tid[len("TRAINER_"):-len("_HNS")].lower()


def stage_name(stage):
    return {boss_teams.JOHTO_CHAMPION: "the Johto League won", boss_teams.KANTO_CHAMPION: "the Kanto League won"}.get(
        stage, f"{stage} badge{'s' if stage != 1 else ''}")


def stage_flags(stage):
    i = trainer_rules.stage_index(stage)
    out = [f'!set_flag("FLAG_BADGE0{b}_GET")' for b in range(1, min(i, 8) + 1)]
    if i >= 9:
        out.append('!set_flag("FLAG_IS_CHAMPION")')
    if i >= 10:
        out.append('!set_flag("FLAG_IS_KANTO_CHAMPION")')
    return out


def battle(team):
    """One battle's lines: start it, wait for the action menu, check the whole team."""
    name, level = label(team.tid), trainer_rules.cap(team.stage)
    out = [f"loadstate stage_{trainer_rules.label(team.stage).lower()}.ss",
           f'!battle("{team.tid}")',
           f"waituntil32 {{gBattlerControllerFuncs}} {{HandleInputChooseAction@battle_controller_player}} 4000 B "
           f"{name}_action_menu",
           f"expect8 {{gEnemyPartyCount}} {len(team.mons)} {name}_has_{len(team.mons)}"]
    db = trainer_rules.species_db.load()
    for slot, m in enumerate(team.mons):
        species = team_kit.species_constant(m["species"])
        item = team_kit.constant("ITEM", m["item"]) if m.get("item") else "ITEM_NONE"
        tag = f"{name}_{slot + 1}_{species[len('SPECIES_'):].lower()}"
        out += [f"expect8 {{gEnemyParty+{84 + 100 * slot}}} {level} {tag}_at_{level}",
                f'!expect_party_species("gEnemyParty", {slot}, "{species}", "{tag}")']
        if slot == 0 and (db.item(item) or {}).get("hold_effect") in trainer_rules.SWITCH_IN_ITEMS:
            out.append(f"# its {m['item']} may be used up as it comes in: not checked")
        else:
            out.append(f'!expect_party_item("gEnemyParty", {slot}, "{item}", "{tag}_{item[len("ITEM_"):].lower()}")')
    return out


def render():
    teams = trainer_rules.designed_teams()
    out = ["# Crystal Imperium play test, written by tools/crystal_imperium/trainer_tests.py from the team tables:",
           "# do not edit. Every designed battle (the bosses, the side battles, the route mini-bosses, the Ace",
           "# Trainers and the upgraded Cooltrainers) started with the player at its team's own stage: the whole",
           "# team, every Pokemon at the stage's NORMAL cap, as the species it was made as (a team made for a stage",
           "# keeps its Pokemon as made there, src/battle_main.c GetTrainerMonEvolvedSpecies) and holding its item",
           "# (the lead's item unless it can be used up as it comes in: Booster Energy, a Terrain Seed...).",
           "# fought_later.emu checks the same teams fought after their stages.",
           "# gEnemyParty: 100 bytes a Pokemon, level at +84; species and item are in the encrypted substructs.",
           "!new_game()", "!battle_style_set()", "!no_care_packages()", f"!give_mon({PLAYER}, 50)", "savestate base.ss"]
    # Every constant the checks name, resolved in one compile
    names = sorted({t.tid for t in teams} | {team_kit.species_constant(m["species"]) for t in teams for m in t.mons}
                   | {team_kit.constant("ITEM", m["item"]) if m.get("item") else "ITEM_NONE" for t in teams for m in t.mons})
    out.insert(out.index("!new_game()"), "!prefetch(" + ", ".join(f'"{n}"' for n in names) + ")")
    for stage in trainer_rules.STAGES:
        group = [t for t in teams if t.stage == stage]
        if not group:
            continue
        tag = trainer_rules.label(stage).lower()
        out += ["", f"# Stage {trainer_rules.label(stage)}, {stage_name(stage)}: cap {trainer_rules.cap(stage)}, "
                    f"{len(group)} battles", "loadstate base.ss"] + stage_flags(stage) + [f"savestate stage_{tag}.ss"]
        for team in group:
            out += battle(team)
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    new = render()
    old = open(TEST, encoding="utf-8").read() if os.path.exists(TEST) else ""
    if new == old:
        return 0
    if args.check:
        print(f"{os.path.relpath(TEST, ROOT)} out of date: run tools/crystal_imperium/trainer_tests.py")
        return 1
    with open(TEST, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"wrote {os.path.relpath(TEST, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
