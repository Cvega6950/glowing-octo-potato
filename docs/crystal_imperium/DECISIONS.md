# Crystal Imperium: architecture decisions

Short records of decisions that shape the project. Newest last.

## D1. Foundation: Pokémon Heart & Soul 2.0.6

- **Base:** `PokemonHnS-Development/pokehns-expansion`, tag `2.0.6`, commit
  `167aa6d537b109bb229c231ddce4616974c4da71` (2026-09-16). The full upstream history is
  preserved; the remote is configured as `upstream`.
- **Why:** HnS already has the whole Johto story, the Kanto postgame, Red, day/night, HGSS music
  and a modern pokeemerald-expansion battle engine. Re-creating that on another base would cost
  far more than adding Imperium-style gameplay on top of it.
- **Build target:** `make hns` → `pokehns.gba`, copied to `CrystalImperium.gba` by
  `tools/crystal_imperium/build.sh` and CI.
- **No engine migration:** we do not merge newer RHH or Emerald Imperium engine code into HnS.
  Gameplay changes are made as HnS data and small, isolated engine hooks.

## D2. Emerald Imperium is a design reference, not a code source

- `iriv24/pokeemerald-expansion` (`release` branch, commit `2576d0f3`, 2025-09-01) has no
  license file. Its original assets (24 custom Megas, sprites, rebalanced species data) carry
  no grant to reuse them.
- Imperium is also built on an older expansion version, so its files do not drop into HnS.
- **Decision:** we re-implement Imperium *behaviours* (Minimal Grinding Mode, sleep clause,
  competitive trainers, cheap team-building items) as original code and data. We copy no
  Imperium source or assets unless the authors grant permission, which is tracked as a blocker
  in [FEATURE_MATRIX.md](FEATURE_MATRIX.md).

## D3. Minimal Grinding Mode is symmetric

- When on, `CalculateMonStats` treats **every** Pokémon (player, trainer and wild) as having
  31 IVs and 0 EVs. Stored IVs/EVs are untouched, so Hidden Power types still vary and turning
  the mode off restores normal stats.
- This matches Emerald Imperium's mode, which ignores EVs in its stat formula, and means boss
  stats don't depend on the player grinding.
- Turning it on in the menu also selects HnS's existing options for max player IVs, no EV gain,
  NORMAL level caps and ×1.5 EXP. Each one stays individually adjustable.
- **Save compatibility:** the flag uses spare bits of an existing `ChallengeSettings` byte
  (`SaveBlock3` layout and size unchanged). Older HnS saves load fine and read the mode as OFF.
  These saves can enable it from the in-game settings PC.

## D4. Sleep Clause is always on

`B_SLEEP_CLAUSE TRUE`. Bosses use Hypnosis/Sleep Powder; without the clause a single sleep move
can decide a fight. This applies to both sides, like Emerald Imperium.

## D5. Boss AI baseline

- Gym Leaders and mini-bosses: `Smart Trainer / Ace Pokemon / HP Aware`. Smart Trainer is
  omniscient, switches smartly and avoids PP stalling.
- Elite Four, Champion, Red and postgame bosses also get `Prediction`.
- Ordinary trainers keep HnS's cheaper AI. AI time per turn matters on hardware and on phones.

## D6. Level caps stay tied to Gym aces

HnS's NORMAL cap table (`src/caps.c`) equals the next Gym Leader's highest level. Reworked
leaders keep their ace at that cap, so the player can always match the ace's level.
`tools/crystal_imperium/validate.py` enforces this.

## D7. ROM budget

- The baseline ROM uses 94.5% of the 32 MB GBA address space, and EWRAM is at 94.6%.
- All Gen 1–9 species are already compiled in, but HnS disables Mega Evolution. Every new asset
  (Mega sprites, new maps) competes for about 1.7 MB.
- Measurements are recorded in [FEATURE_MATRIX.md](FEATURE_MATRIX.md) before enabling anything large.

## D8. Distribution

- This repository is public, so the built ROM (which contains Nintendo's copyrighted assets) is
  **not** published from it.
- CI uploads `CrystalImperium.gba` as a run artifact only when the repository is private.
- Public releases should be patches plus build-from-source instructions, never ROM files.
- Building from source needs no Nintendo ROM; the decomp tool chain produces the ROM itself.

## D9. Mega Evolution: classic set, progression-gated

- Measured ROM use: no Megas 94.5%; classic set (48 stone Megas plus Rayquaza) **98.75%**; adding
  the 48 Z-A Megas 99.19%. We enable the classic set and keep `P_GEN_9_MEGA_EVOLUTIONS`
  off, which leaves about 410 KB for later data work.
- The player gets the **Mega Ring** from a Mega Specialist on Goldenrod Dept. Store 5F after
  the 3rd badge (`FLAG_RECEIVED_MEGA_RING`, formerly the unused flag 0x307). Older saves have
  it clear.
- The same NPC sells stones for ₽10,000. Stock grows with progress so Megas don't outpace the
  level-cap curve: badge 3 (early-route Megas), badge 6 (starters and most Gen 1–3 Megas),
  badge 8 (pseudo-legendaries, Gyarados, Lucario), Johto Champion (Mewtwo X/Y, Latias, Latios,
  Diancie).
- **Trigger button:** HnS uses START for move info, which blocked the Mega trigger. The
  trigger is now on R (`B_GIMMICK_TRIGGER_BUTTON` in `include/config/battle.h`).
- Bosses: one signature Mega each (the engine allows one Mega per trainer per battle).
  Lance has Gyarados, his rematch has Salamence and his postgame team has Charizard X. Red's
  teams have Charizard Y. Gym Leaders get Megas as they are reworked.

## D10. Team-building key items from the first step

- A new game starts with five key items: **Rare Candy Box** (999 Rare Candies whenever used,
  capped by the level cap), **Infinite Repel** (a switch), **Pokémon Box Link** (the PC
  anywhere), **Training Kit** (nature and ability changes) and **PokéVial** (full party heal
  outside battle, unlimited). The **DexNav** is in the start menu from the same moment.
- They are handed out by `GiveQoLKeyItems()` on New Game and again on every Continue, which
  adds only what the bag is missing. Saves from older builds therefore get new items without a
  new game. `FLAG_RECEIVED_QOL_KEY_ITEMS` (0x305) is still set but no longer read; it stays
  reserved because older saves have it set.
- With a Nuzlocke running, the PokéVial does not revive fainted Pokémon (the Pokémon Center
  behaviour is kept for the Center).

## D11. Difficulty selection

- Challenge menu > Difficulty > **DIFFICULTY**: EASY / NORMAL / HARD, stored in two spare
  `ChallengeSettings` bits with 0 meaning NORMAL (older saves stay NORMAL).
- `GetCurrentDifficultyLevel()` returns it, so the engine's per-difficulty trainer parties are
  used where they exist. Trainers without one keep their NORMAL party at 90% (EASY) or 110%
  (HARD) of its levels. EASY also turns trainer items off; HARD selects HARD level caps.
- Mid-game the setting can only be made easier (the menu's one-way lock).

## D12. Easy Catch is on by default

- The user asked for every Pokémon to be a 100% catch. **EASY CATCH** (Features tab) makes
  `ComputeCaptureOdds` return a guaranteed capture, like a Master Ball. Nuzlocke and
  species-clause rules still decide whether a ball may be thrown at all.
- Stored inverted (`tx_Features_EasyCatchOff`), so 0 is ON for new games and for older saves.

## D13. DexNav configuration

- `DEXNAV_ENABLED`, with the free extended flags 79–81 and the free vars 0x40C2/0x40C9.
  Detector mode (finding hidden Pokémon while walking) is on from the start.
- R in the overworld searches for the registered Pokémon. In HnS, R only switches bike
  gears, and only while riding, so off the bike R was unused.
- Search levels (which raise the chances of egg moves, Hidden Abilities and items) need one
  byte per entry. Indexed by species they would overflow `SaveBlock3` by one byte, so they are
  indexed by National Dex number (forms share one) and placed **last** in `SaveBlock3`: older
  saves load with every level at 0 (the save writer zero-fills the unused part of a sector).
  `SaveBlock3` is now 1,132 of 1,624 bytes.
- The search flag is saved, but a search's state is not, so Continue clears the flag. Without
  that, a game saved mid-search would dereference a NULL search on the next warp.
- Upstream DexNav picks the target tile at random among nearby grass tiles (about 6% each) and
  gives up when none is picked, which happens in small patches of grass. A random suitable
  tile is now used when the weighted pick finds none.

## D14. Every Gen 1–9 Pokémon on every route: Wild Variety and the DexNav list

The user wants every Gen 1–9 Pokémon available on every route. Fitting ~1,000 species into
12-slot tables is impossible, so the routes keep their tables and two systems sit on top:

- **Wild Variety** (Features tab: OFF / 15% / 30% / 60%, default 30%, stored so that 0 is 30%
  for older saves): that share of land, surfing and fishing encounters is replaced by a random
  Pokémon from the variety pool, at the encounter's own level. Surfing and fishing draw
  Water-type Pokémon. Rock Smash and hidden encounters are left alone, and so are the
  Bug-Catching Contest, the Battle Pike and the Battle Pyramid, which keep their own Pokémon.
- **The pool** (`src/wild_variety.c`) is built once at run time from the species data: every
  species with no pre-evolution, in its main form or a regional form, excluding battle-only and
  cosmetic forms (`randomizerMode == MON_RANDOMIZER_INVALID`, Megas, Gigantamax, Totems). That
  is 445 Pokémon. Legendary, Mythical, Ultra Beast and Paradox Pokémon (122 more) join after
  becoming Champion; before that, variety never produces them.
- **Level-appropriate evolution:** a variety Pokémon is evolved as far as its level allows.
  Level-up evolutions use their level. Friendship and other condition-only level-ups use 18
  (from a base form) or 35. Stones, trades and special methods use 30 or 40.
- **Targeted hunting:** a random draw from 445 Pokémon can't be relied on to find one in
  particular, so SELECT in DexNav lists **every** Pokémon: all 1,074 National Dex entries
  (every evolution stage, HnS's regional-form entries, Legendaries), from the start of the
  game, in National Dex order. The user asked for DexNav to show all species (or offer a
  cheat). A searches for the chosen Pokémon in the current area right away; START registers it
  for R; LEFT/RIGHT jump 100 entries. DexNav finds it at the area's levels: on the water if it is
  Water-type and the area has water encounters, otherwise in the grass. The species is used as
  chosen (an evolved Pokémon can appear at a low level).
- **Cheat menu:** HnS's debug menu is compiled in (`DEBUG_OVERWORLD_MENU`): hold R and press
  START in the overworld. It can give any Pokémon or item and set Pokédex flags. It is HnS's own
  tool and can also change story flags, so it is documented as a cheat, not a feature.

## D15. Hidden Pokémon fill the gaps

- `tools/crystal_imperium/gen_hidden_encounters.py` writes `hidden_mons` tables (3 slots,
  weights 50/35/15) into `src/data/wild_encounters.json` for 249 map tables. They hold the 258
  non-legendary evolution families that had no wild, gift or scripted source.
- Families are matched to the area by type: Water and Ice on water, Rock, Ground, Steel, Ghost,
  Dark and Dragon in caves, the rest in grass. They are dealt out round-robin, so each family
  appears in several places, and a map's Day and Night tables differ. Levels follow the
  area's own Pokémon.
- DexNav lists them in its HIDDEN row. Detector mode finds them while walking (DexNav's
  15% hidden-table share of detections).
- The validator now reads the National Dex from `pokedex.h`. HnS numbers some forms (Megas)
  below 1025, which made the old count report Megas as missing families. Result: 449 of 571
  families have a source in the encounter and script data. The other 122 are all legendary,
  mythical, Ultra Beast or Paradox: the DexNav list has them from the start, Wild Variety's
  random encounters after the Champion, besides HnS's own legendary events.

## D16. Milestone care packages

- On the first step on a route or in a town after each Gym Badge (16) and after becoming
  Champion, a care package from Prof. Elm arrives (`src/care_packages.c`,
  `data/scripts/care_packages.inc`, counter `VAR_CARE_PACKAGES` = 0x40CA). Several missed
  milestones are caught up one package per step.
- Besides balls and medicine they carry every evolution item found nowhere else in HnS: Linking
  Cord, Upgrade, Sachet, Whipped Dream, Prism Scale, Sun Stone, Sweet/Tart/Syrupy Apple, the
  Alcremie Sweets, Cracked/Chipped Pot, both Teacups, Leader's Crest, both Armors, Metal Alloy,
  999 Gimmighoul Coins and, for the Champion, both Scrolls.
- All 30 trade evolutions also have a non-trade method in the data, so no evolution needs a
  link cable.

## D17. Delta compatibility is tested on VBA-M

- Delta's GBA core (`rileytestut/GBADeltaCore`) is VBA-M, pinned to commit `453fa0de`. It
  reads `vba-over.ini` by game code. This ROM keeps `BPEE`, whose entry gives RTC on and
  128 KB Flash. The ROM contains the `FLASH1M_V103` signature that VBA-M's save detection
  looks for.
- The play-test harness has a libretro backend. `tools/emurun/build_vbam_core.sh` builds
  VBA-M's libretro core at that same commit, and `tools/emurun/run_all.sh vbam` runs every
  play test on it.
- What this covers: the same CPU, video, Flash save and RTC emulation code as Delta, driven
  through the whole test suite. What it does not cover: Delta's iOS front end (touch
  controls, its own save-file handling, app suspension), which still needs a device.

## D18. DexNav reveals every Pokémon

- Upstream DexNav draws a Pokémon the player has not seen as a question mark, hides its name
  and types, and refuses to register or search for it. On a new game that makes every area
  a row of question marks. The user reported exactly that ("it's just showing question
  marks") after asking for DexNav to show all species.
- Now the area lists (land, water, hidden) draw every Pokémon's icon with its name and types,
  and any of them can be registered or searched for. A revealed search shows the name and the
  normal icon (no whited-out silhouette).
- Two things still depend on the Pokédex: the Hidden Ability line says "Capture first!" until
  the Pokémon is caught, and DexNav only gives Hidden Abilities to Pokémon caught before
  (upstream rules that reward catching).
- A hidden Pokémon detected while walking (detector mode) still starts as ???; R or sneaking
  close reveals it. That is the detector's surprise, not a seen rule.
