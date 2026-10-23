# Crystal Imperium changelog

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
