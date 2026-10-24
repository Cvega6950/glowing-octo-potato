# Crystal Imperium changelog

## 0.4.1-experimental (2026-10-24)

### Gameplay
- **DexNav shows every Pokémon on its main screen**, seen or not: no more question marks. Any
  of the area's Pokémon (land, water and hidden rows) can be registered with R and searched
  for with A right away. The top bar now reads SELECT: ALL, for the list of every Pokémon.
  A hidden Pokémon detected while walking still shows ??? until R is pressed or the player
  sneaks close.

### Tooling
- `dexnav` registers, searches for and catches a Rattata that has not been seen.

## 0.4.0-experimental (2026-10-24)

### Gameplay
- **Key items from the first step:**
  - Rare Candy Box (unlimited Rare Candies, capped by the level cap; also without a Nuzlocke).
  - Infinite Repel (now an on/off switch that works).
  - Pokémon Box Link (the PC anywhere).
  - **Training Kit:** change a Pokémon's nature or cycle its ability any time.
  - **PokéVial:** full party heal outside battle, never runs out.

  Older saves receive whichever of them they lack on Continue.
- **DexNav** in the start menu from the first step:
  - Area lists with three **hidden Pokémon** per area; hidden Pokémon are also detected while
    walking.
  - Search levels and chains; R searches for the registered Pokémon.
  - **SELECT lists every Gen 1–9 Pokémon** (all 1,074: every evolution stage, regional
    forms, Legendaries), and any of them can be searched for in any area with wild Pokémon,
    at that area's levels. LEFT/RIGHT jump 100 entries.
- **Wild Variety** (Features tab, 30% by default): that share of wild encounters are any
  Gen 1–9 Pokémon, evolved as far as their level allows. Legendary and Mythical Pokémon join
  Wild Variety's random encounters after becoming Champion.
- 258 evolution families that had no source in the game now appear as hidden Pokémon on 249
  maps.
- **Easy Catch** (Features tab, on by default): every Poké Ball catches.
- **Difficulty selection** (Difficulty tab): EASY (trainer levels −10%, no trainer items),
  NORMAL, HARD (trainer levels +10%, HARD level caps).
- **Milestone care packages** from Prof. Elm after each badge and after becoming Champion,
  with supplies and every evolution item the game had nowhere: Linking Cord, Upgrade,
  Prism Scale, Sachet, Whipped Dream, Sun Stones, Apples, Sweets, Pots, Teacups, Armors,
  Leader's Crest, Metal Alloy, 999 Gimmighoul Coins, Scrolls.
- **Move relearner** in the party menu (level-up, egg, TM and tutor moves).

### Fixes
- DexNav no longer fails at random in small patches of grass.
- Wild Variety leaves the Bug-Catching Contest, the Battle Pike and the Battle Pyramid alone.
- A game saved during a DexNav search loads cleanly.

### Tooling
- The play tests also run on **VBA-M** at the commit Delta's GBA core pins
  (`tools/emurun/build_vbam_core.sh`, `run_all.sh vbam`), locally and in a second CI job. They have a pathfinding walker,
  bag checks and pointer-following addresses.
- New tests:
  - `qol_items`, `infinite_repel`, `relearner_training_kit`, `difficulty`, `autorun`
  - `pokevial`, `easy_catch`, `tm_reusable`
  - `dexnav`, `dexnav_any`, `dexnav_hidden`, `wild_variety`, `bug_contest`, `care_packages`
  - `story_opening`: the real story path from New Game to Elm's lab (starter, errand, Potion)
    and the first wild battle on Route 29, with no debug menu
  - `old_save_test.sh`: a Heart & Soul 2.0.6 save continued in Crystal Imperium
- `whitney` samples 12 battles (the naive team wins about 25%). `falkner` uses the autopilot.
- `tools/crystal_imperium/gen_hidden_encounters.py` generates the hidden tables. The validator
  reads the National Dex from `pokedex.h` (HnS numbers some forms below 1025) and parses nested
  evolution lists. It now reports 449 of 571 families with a source; the other 122 are
  legendary (DexNav's list from the start, Wild Variety after the Champion).
- Play tests run on a fixed cartridge clock (2026-10-24 01:30 UTC, advancing with emulated time),
  so they give the same results at any hour and on any host.

## 0.3.0-experimental (2026-10-23)

### Gameplay
- **Bugsy** rebuilt: Focus Sash Spinarak (Sticky Web), Pineco (Spikes, Rock Tomb), Ledian
  (Reflect, Light Screen), Eviolite Technician Scyther (Fury Cutter). Smart AI.
- **Whitney** rebuilt: Clefairy (Magic Guard; Metronome, Encore, Charm), Aipom (Fake Out,
  U-turn), Intimidate Stantler (Hypnosis), Scrappy Miltank (Rollout, Body Slam, Milk Drink,
  Attract). Smart AI; one Potion instead of Super Potion + Potion.
- Azalea and Goldenrod Gym trainers get defined movesets, abilities and levels close to the cap.

### Tooling
- Battle autopilot (`autobattle`) and win-rate sampling (`sample_battle`, `tally`,
  `expecttally`) in the emulator harness. `names.py` labels logs with species and move names.
- New tests: `bugsy`, `whitney`, `gym_trainers_m2`. Macros: `battle_style_set`.
- The validator now covers Bugsy and Whitney. It caught Aipom being given Technician
  (Ambipom's ability) during the rework.

## 0.2.0-experimental (2026-10-23)

### Gameplay
- **Mega Evolution** enabled for the 48 classic stone Megas and Mega Rayquaza. Press **R** in the move menu to Mega
  Evolve.
- A Mega Specialist on Goldenrod Dept. Store 5F gives the **Mega Ring** after the third badge
  and sells Mega Stones (₽10,000). More stones unlock at badges 6 and 8 and after becoming
  Champion.
- Boss Megas: Lance (Gyarados), Lance rematch (Salamence), Lance postgame (Charizard X),
  Red (Charizard Y).

### Fixes
- The gimmick trigger moved from START (taken by HnS's move info) to R.

### Tooling
- New play tests: `mega_evolution`, `mega_specialist`. New harness macro `give_item`.

## 0.1.0-experimental (2026-10-23)

Based on Pokémon Heart & Soul 2.0.6 (`167aa6d5`).

### Gameplay
- New **Minimal Grinding Mode** (Difficulty tab, ON by default). Every Pokémon battles with
  31 IVs and 0 EVs. Turning it on also enables max player IVs, no EV gain, NORMAL level caps
  and ×1.5 EXP.
- **Falkner** rebuilt: Pidgey (Tailwind), Rookidee (Hone Claws, Power Trip, Steel Wing) and
  Noctowl (Tinted Lens; Hypnosis, Air Cutter, Reflect, Mud-Slap); perfect IVs; Smart AI.
- Bird Keepers Rod and Abe and Elder Li get defined movesets, abilities and items.
- **Sleep Clause** is always on.
- The Goldenrod Flower Shop sells **Ability Capsule** (₽20,000) and **Ability Patch**
  (₽40,000) after the third badge.

### Tooling
- `tools/emurun`: a headless mGBA play-test harness with tests for Falkner, save/load and the
  Flower Shop.
- `tools/crystal_imperium/validate.py`: data validation and generated trainer/encounter
  databases.
- `tools/crystal_imperium/build.sh` and a CI workflow.
- Fixed `make check BUILD=hns` compilation (`fake_rtc.h` include order).
