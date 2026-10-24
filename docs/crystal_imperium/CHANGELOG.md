# Crystal Imperium changelog

## 0.5.0-experimental (2026-10-24)

### Gameplay
- **Smarter trainers:** on NORMAL and HARD every trainer uses the smart AI (it knows your
  team, picks the best move, switches smartly and plays around HP). EASY keeps the old AI.
- **Imperium-style bosses for the whole story:** Proton, Petrel, Ariana and Archer; every rival
  battle from Azalea to Victory Road; Morty, Chuck, Jasmine, Pryce (all three versions each)
  and Clair; the Kimono Girls; the Elite Four and Lance; the eight Kanto leaders, Blue and Red.
  Aces at the level cap (70 in Kanto; Red's is 90), full held items, natures, abilities and
  competitive moves. Every Gym Leader from the 5th Gym on, Archer, the rival on Victory Road,
  the Elite Four, Lance, Blue and Red Mega Evolve (Heracross, Steelix, Abomasnow, Altaria,
  Houndoom, Tyranitar, Alakazam, Beedrill, Lucario, Absol, Gyarados, Aerodactyl, Blastoise,
  Manectric, Venusaur, Gengar, Metagross, Camerupt, Pidgeot, Charizard Y).
- **Emerald Imperium's TMs:** 198 TMs. TM01–TM172 are Emerald Imperium's list in its order
  (all but its two custom moves, Dark Hole and Draco Barrage), TM173–TM198 the Heart & Soul
  TMs Imperium lacks. 28 TMs have a new number (TM03 Water Pulse is TM160, TM41 Torment TM179,
  TM70 Rock Climb TM192, TM92 Trick Room TM106, ...); the rest keep theirs.
  - The TM case holds all 198 TMs and 8 HMs, and each TM's description is its move's.
  - The Goldenrod Dept. Store 5F sells every TM: 71 from the start (including Heart & Soul's
    own stock, now cheaper), 155 from 3 badges, 178 from 6, all 198 from 8. Shop lists show
    each TM's move next to its number, as the bag does.
- **HMs without teaching:** carrying an HM, with its badge, is enough for any Pokémon in the
  party to use the field move (Cut, Surf, Strength, Rock Smash, Waterfall, Fly and Flash from
  the lead's party menu). Before, the Pokémon had to be able to learn the move.
- The Mega Stone shop's 6-badge tier counts badges (it unlocked with Jasmine's badge).
- Falkner's Rookidee knows Rock Smash instead of Steel Wing, which it can't learn.

### Fixes
- Teaching a move from the party menu's relearner (LEARN MOVES > TM MOVES) used up the TM even
  with REUSABLE TMS on.

### Save compatibility
- The TM case moved from SaveBlock1 to EWRAM, saved as counts in SaveBlock3. Saves from Heart &
  Soul 2.0.6 and earlier Crystal Imperium builds load: their TMs keep their moves (Heart &
  Soul's TM70 Rock Climb becomes TM192), including TMs in the item PC and held TMs.

### Tooling
- `tools/crystal_imperium/boss_teams.py` holds the boss teams; `validate.py` checks their
  moves are learnable and their aces sit at the cap, and resolves abilities given by macros.
- `tools/crystal_imperium/tm_list.py` holds the TM list and writes the TM constants, the item
  data (with descriptions wrapped to the bag box by glyph width), the shop lists and the old
  numbering for save conversion.
- Harness: Pokémon (Complex) from the debug menu, a prepared team for winnability checks,
  battles by trainer constant, `expectseen` for Mega forms; the autopilot skips moves with no
  PP. `set_var`, `fill_tm_case`, `save_and_continue`; bag checks read the TM case in EWRAM.
- New tests: `bosses_m3`, `bosses_m4`, `bosses_e4`, `bosses_m5`, `tm_case`, `tm_shop`,
  `hm_field_moves`.
  `tm_reusable` also teaches through the relearner; `old_save_test.sh` now saves Heart & Soul
  TMs and checks their conversion.
- `data/battle_anim_scripts.s` read the vanilla TM list (`IS_HNS` was undefined there), which
  only mattered once the TM list changed; `constants/tms_hms.h` now defines it for every user.

## 0.4.1-experimental (2026-10-24)

### Gameplay
- **DexNav shows every Pokémon on its main screen**, seen or not: no more question marks. Any
  of the area's Pokémon (land, water and hidden rows) can be registered with R and searched
  for with A right away. The top bar now reads SELECT: ALL, for the list of every Pokémon.
  A hidden Pokémon detected while walking still shows ??? until R is pressed or the player
  gets close.
- **DexNav searches no longer fail with "The Pokémon got away! Try moving more slowly."**
  Walking, running (Auto Run included) and biking all reach the Pokémon; sneaking with A is
  optional. Before, walking normally within 2 tiles or running/biking within 4 tiles scared
  it off, and with Auto Run on there was no way to sneak. A search now lasts 30 seconds
  (was 15).

### Tooling
- `dexnav` registers, searches for and catches a Rattata that has not been seen, walking up
  to it normally. `dexnav_any` turns Auto Run on and runs up to the Charmander it searched
  for. Both failed with "Try moving more slowly" before the fix.

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
