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
- Lists of facts about the game are design data, not code or assets: its TM list (D22), and
  since 0.11.0, at the user's request, which abilities and moves each species has (D35), taken
  from the public Radical Red dex that Imperium's own documentation follows; since 0.13.0 also
  which TM and tutor moves they learn, and Radical Red's six moves of its own, written anew from
  the dex's numbers and the effects its change lists give (D39). Base stats, sprites and
  Imperium's own Megas, moves and abilities stay out.

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
- Red and Heart & Soul's postgame rematch teams also get `Prediction` (D20 explains why the
  rest don't; D27).
- Ordinary trainers keep HnS's cheaper AI. AI time per turn matters on hardware and on phones.

## D6. Level caps stay tied to Gym aces

HnS's NORMAL cap table (`src/caps.c`) equaled the next Gym Leader's highest level. Reworked
leaders keep their ace at that cap, so the player can always match the ace's level.
`tools/crystal_imperium/validate.py` enforces this. Since 0.7.0 every boss Pokémon is at the
cap, and since 0.7.1 at the player's own cap table, HARD caps included (D21); nothing else the
player meets is above the cap (D28). Since 0.8.0 the tables themselves are Emerald
Imperium-style (D29).

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

- Measured ROM use: no Megas 94.5%; classic set (47 stone Megas plus Rayquaza) **98.75%**; adding
  the 48 Z-A Megas 99.19%. We enable the classic set and keep `P_GEN_9_MEGA_EVOLUTIONS`
  off, which leaves about 410 KB for later data work.
- **Fixed in 0.12.0:** the shop also sold Staraptite. Mega Staraptor is a Z-A Mega: its species
  data is behind `P_GEN_9_MEGA_EVOLUTIONS`, but pokeemerald-expansion put its form change behind
  `P_MEGA_EVOLUTIONS`, so a Staraptor holding Staraptite could Mega Evolve into a species that
  isn't in the ROM. The form change now has the species data's guard, and Staraptite is out of
  the shop: 47 stones.
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
  capped by the level cap; used several at a time since 0.9.0, D33), **Infinite Repel** (a switch), **Pokémon Box Link** (the PC
  anywhere), **Training Kit** (nature and ability changes, and IVs and EVs since 0.10.0) and
  **PokéVial** (full party heal outside battle, unlimited). The **DexNav** is in the start menu
  from the same moment (in the L menu since 0.10.0, with the other tools, D34).
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
  (HARD) of its levels, never above the player's level cap (D28). EASY also turns trainer
  items off; HARD selects HARD level caps.
- Since 0.7.1 bosses aren't scaled: they are at the player's level cap on every difficulty
  (D21). On HARD that is the HARD cap; before, HARD's 10% was added on top of the NORMAL cap
  and put Falkner at 12 against a cap of 8.
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
  for older saves): that share of land, surfing and fishing encounters is replaced by a
  Pokémon from the variety pool, at the encounter's own level. Surfing and fishing draw
  Water-type Pokémon. Since 0.5.1 the replacement comes from the area's set for the day,
  which DexNav lists (D24); before, it was any Pokémon of the pool. Rock Smash and hidden encounters are left alone, and so are the
  Bug-Catching Contest, the Battle Pike and the Battle Pyramid, which keep their own Pokémon.
- **The pool** (`src/wild_variety.c`) is built once at run time from the species data: every
  species with no pre-evolution, in its main form or a regional form, excluding battle-only and
  cosmetic forms (`randomizerMode == MON_RANDOMIZER_INVALID`, Megas, Gigantamax, Totems). That
  is 445 Pokémon. Legendary, Mythical, Ultra Beast and Paradox Pokémon (122 more) join after
  becoming Champion; before that, variety never produces them.
- **Level-appropriate evolution:** a variety Pokémon is evolved as far as the area's highest
  level allows (its own level before 0.5.1).
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
- **Battle gear, Emerald Imperium-style (0.7.0).** The user asked for "a ton of useful held items
  and stuff for battle like PP Maxes, just like Emerald Imperium". Emerald Imperium hands out
  competitive tools cheaply (Ability Capsules and Patches for 100 at Slateport, the type-resist
  Berries free, a Scope Lens gift, a stat editor and IV perfecter). The 17 packages (287 entries)
  now carry, besides balls, medicine and evolution items:
  - Competitive held items, the staples several times over the game: Leftovers 7, Focus Sash 8,
    Life Orb 5, Assault Vest 5, Heavy-Duty Boots 5, Choice Band and Specs 3 each and Choice Scarf
    4, Rocky Helmet 3, Weakness Policy 3, Booster Energy 4, Eviolite 3, Air Balloon 6, White Herb
    4; and Expert Belt, Muscle Band, Wise Glasses, Scope Lens, the Orbs, Light Clay, Black Sludge,
    the Herbs, Red Card, Eject Button and Pack, Safety Goggles, Covert Cloak, Clear Amulet,
    Protective Pads, Loaded Dice, Punching Glove, Throat Spray, Blunder Policy, Room Service,
    Utility Umbrella, Ability Shield, Adrenaline Orb, the weather Rocks, the Terrain Seeds and
    Extender, the species items (Light Ball, Thick Club, Leek, ...) and more.
  - All 18 type-boosting items (Charcoal to Fairy Feather), spread over packages 1–6.
  - All 18 type-resist Berries (two each, packages 2–4), the pinch Berries (Liechi to Custap,
    Jaboca to Maranga), 35 Sitrus and 19 Lum Berries.
  - **93 PP Max** and 8 PP Up (PP Max from the first package on: 3, then 5 a package, 10 for the
    Champion and the 16th badge), X items, Max Elixirs, Elixirs and Max Ethers.
  - No Mints or Ability Capsules beyond the Ability Patches already there: the Training Kit and
    the Goldenrod Flower Shop cover natures and abilities (D10).
- The table is in `tools/crystal_imperium/care_packages.py`, which writes the script (CI runs
  it with `--check`). A package shows its contents in one message, wrapped to the message box
  with the game's own font widths (two lines a page), then adds the items without a message each:
  with `giveitem` the bigger packages would take forty message boxes. An item whose Bag pocket is
  full goes to the PC instead (`addpcitem`), and the player is told. The Bag has room: 236 item
  slots, 92 medicine, 66 Berries.
- **Saves from before 0.7.0 get the gear too.** Their packages came with the earlier contents
  (the same in every release that had them, `EARLIER` in the generator). `VAR_CARE_PACKAGE_GEAR`
  (0x40E5, never referenced before) counts the packages whose gear has arrived; while it is behind
  `VAR_CARE_PACKAGES`, each step on a route or in a town brings one package's missing gear ("PROF.
  ELM sent the battle gear an earlier package didn't have!") before any new package. A package
  received since 0.7.0 brings its gear itself and moves both counters.
- **Stacks (0.11.0).** The user wanted "more gifted items after each badge, like 10x charcoal etc
  like emerald imperium". Imperium's own badge rewards aren't documented (its documented battle
  rewards are single items: [battle rewards](https://pokemonemeraldimperium.com/battle-rewards/)),
  so the packages follow the user's example: every item now comes at least `STACKS` times in
  the generator. 10 of each type-boosting item, 5 of each type-resist Berry, 10 Sitrus and Lum
  Berries, 5 of each pinch Berry (3 Starf, 3 Lansat); 5 of each held item that is used up or
  that a team wants several of (Focus Sash, Eviolite, Air Balloon, the Herbs, Red Card, Eject
  Button and Pack, Weakness Policy, Booster Energy, the Terrain Seeds, ...), 3 of each staple
  (Leftovers, Life Orb, Assault Vest, Rocky Helmet, Heavy-Duty Boots, Expert Belt, the Orbs and
  Rocks, ...), 2 of each Choice item and of the rarer ones; 20 Poké Balls of a kind, 10 PP Max a
  package, 5 of each X item. The packages hold 2,541 items now (1,650 before): after the eighth
  badge the Bag has 10 Charcoal, 9 Leftovers, 10 Focus Sashes and 20 Sitrus Berries.
- **Saves from before 0.11.0 get the stacks too.** `VAR_CARE_PACKAGE_BULK` (0x40F7, never
  referenced before) counts the packages whose stacks have arrived; while it is behind
  `VAR_CARE_PACKAGES`, each step on a route or in a town brings the rest of one package ("PROF.
  ELM sent more of the gear from an earlier package!"), after the 0.7.0 gear (which a save from
  before 0.7.0 gets first) and before any new package. `GEAR_PACKAGES` in the generator keeps what
  the packages held from 0.7.0 to 0.10.x.
- The evolution items found nowhere else in HnS stay where they were: Linking Cord, Upgrade,
  Sachet, Whipped Dream, Prism Scale, Sun Stone, Sweet/Tart/Syrupy Apple, the Alcremie Sweets,
  Cracked/Chipped Pot, both Teacups, Leader's Crest, both Armors, Metal Alloy, 999 Gimmighoul
  Coins and, for the Champion, both Scrolls.
- All 30 trade evolutions also have a non-trade method in the data, so no evolution needs a
  link cable.
- **Emerald Imperium's care packages (0.12.0).** The user found the packages "lackluster" and
  asked for them to match Emerald Imperium. Imperium's care packages are Radical Red's: its
  cheat-code doc says "SO2Toxic and Woyaopp (Rare Candies and Item Care Packages from Radical Red)
  are enabled by default" ([Imperium docs](https://drive.google.com/drive/folders/1auRPBg8Ts50NByIskMy6b2XHnmNqIKtV)).
  Radical Red 4.1's sixteen packages give 10 of nearly every item otherwise found only by
  grinding or stealing, and big stacks of a few: 153 Quick Balls on Route 2, 50 Heal Balls, 306
  Ability Pills, 50 Dream Balls, 153 PP Max in Fuchsia, 100 Beast Balls
  ([list](https://www.emulatorhacks.com/2026/02/pokemon-radical-red-v41-z-crystals-and.html)).
  Imperium's changelog adds a starting package from PROF. BIRCH with the Shiny Charm and the
  type-boosting items ("Starting Care Package Pixie Plate and Iron Plate replaced with Fairy
  Feather and Steel Feather"), and packages waiting in places along the story ("Damp Rocks, Icy
  Rocks, and Smooth Rocks given as part of Granite Cave care package", "Light Clay added to care
  package given on Route 110") ([changelog](https://pokemonemeraldimperium.com/changelog/),
  [features](https://pokemonemeraldimperium.com/features/)). Its exact lists aren't published.
  Now (`tools/crystal_imperium/care_packages.py`):
  - **The starting package** (package 0) arrives on the first step on a route or in a town once
    the player has a Pokémon: the Shiny Charm, 153 Quick Balls, 10 of every type-boosting item
    and every type-resist Berry, the staple held items (Leftovers, Focus Sash, Eviolite, Expert
    Belt, Muscle Band, Wise Glasses, Scope Lens), the status Berries, Sitrus and Lum, and the rest
    of Radical Red's Route 2 and Viridian Forest packages, 10 of each.
  - **The badge and Champion packages** (1–17) are Radical Red's story-point packages in their
    order, 10 of each item: Pewter, Route 3 and Route 4 after the first badge (50 Heal Balls,
    the vitamins, Lucky Eggs), Nugget Bridge and Cerulean after the second (153 Ability Capsules
    and 153 Ability Patches for the 306 Ability Pills), Vermilion and Lt. Surge after the third
    (50 Dream Balls, the Choice items), Route 9 and Lavender, Celadon, then Fuchsia after the
    sixth (153 PP Max), Blaine, and Clair and the post-game for the Champion (100 Beast Balls,
    the Master Ball, more Choice items). The Kanto packages bring big stacks for the post-game
    and every other Poké Ball.
  - **Nine location packages** wait along the story, each a themed set (another session's
    0.12.0-experimental design, kept and raised to 10 of each): Union Cave (the four weather
    Rocks, Utility Umbrella, Safety Goggles), Ilex Forest (Light Clay and the Herbs), the National
    Park (the Choice items, Life Orb, Weakness Policy, Booster Energy), the Burned Tower (the
    Orbs, Rocky Helmet, Assault Vest, Heavy-Duty Boots, Air Balloon), the Lighthouse (the pivoting
    items), Mt. Mortar (the Paldea items), the Lake of Rage (the Terrain Seeds and Extender), the
    Ice Path and Victory Road (20 Full Restores, Max Revives and Max Elixirs). One arrives on the
    first step in its place, or on a step outside once the player has the badges to be past it.
  - About 6,500 items of 275 kinds in all (0.11.0: about 2,500 of 183), and by every badge at
    least as many of each item as 0.11.0 gave. The Bag's items pocket has 236 slots; all the
    packages together use 172 of them.
  - The items pocket keeps 20 slots free for the story's one-time gifts (the Plates, given with
    `giveitem` and no second chance): while the PC has room, a new kind of item from a package (or
    the MEGA code, D37) goes there instead (`AddItemToBagOrPC`), and only with the PC full does it
    take those slots.
  - The contents live in a C table (`src/data/care_packages.h`, generated with their messages)
    that `src/care_packages.c` adds to the Bag, instead of a script of `additem`s, which saves
    about 23 KB of ROM. An item whose pocket is full goes to the PC. If the PC is full too, the
    package stops, says so, and the rest arrives once the player is on another map
    (`VAR_CARE_PACKAGE_RESUME`, 0x40FA).
  - The messages list the contents with the game's font widths: a run of three or more items with
    the same quantity reads "×10 each: A, B, C", names that end in the same word merge ("OCCA,
    PASSHO and RINDO BERRIES"), and the full sets read "every type-boosting item" and "every
    type-resist BERRY". The longest, the starting package's, is seven pages.
  - Saves: `VAR_CARE_PACKAGE_PLACES` (0x40F8) has a bit for each location package and bit 15 for
    the starting package, as in 0.12.0-experimental. `FLAG_RECEIVED_STARTING_CARE_PACKAGE`
    marks the new starting package, so a save that got the experimental one gets the new one as
    "a bigger version". `VAR_CARE_PACKAGE_IMPERIUM` (0x40F9) counts the milestone packages whose
    0.12.0 contents have arrived: a save from before 0.12.0 gets each package it received again,
    in full, one per step. That replaces the 0.7.0 and 0.11.0 catch-ups
    (`VAR_CARE_PACKAGE_GEAR` and `_BULK` stay level with `VAR_CARE_PACKAGES` but aren't read).
- Evidence: `care_packages` (the starting package, one package per milestone with the big stacks
  and ten of each item after the eight Johto badges and the Champion, a full Berries pocket sending
  the Berries to the PC, 20 free slots in the items pocket kept by sending the held items to the
  PC, a full Bag and PC stopping a package until another map, and a save from before 0.12.0
  getting its three packages again), `care_packages_start` (the starting package, the
  Union Cave package on the first step inside, four location packages for a save with four badges,
  and an experimental save's bigger starting package), `story_opening` (the starting package on
  the real story path) and `old_save_test.sh` (a Heart & Soul 2.0.6 save gets it on its first
  step on Route 29).

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
- A hidden Pokémon detected while walking (detector mode) still starts as ???; R or getting
  close reveals it. That is the detector's surprise, not a seen rule.

## D19. DexNav needs no sneaking

- Upstream DexNav ends a search with "The Pokémon got away! Try moving more slowly." when the
  player walks normally within 2 tiles of the Pokémon (sneaking means holding A) or runs or
  bikes within 4 tiles. With Auto Run on, the player runs by default, and holding A doesn't
  sneak (the run takes precedence in the movement code), so searches always failed. The user
  reported it.
- Both rules are removed: walking, running and biking all reach the Pokémon, and holding A
  still sneaks for those who like it. The search ends only when the player moves more than
  20 tiles away or after `DEXNAV_TIMEOUT`, raised from 15 to 30 seconds.
- In caves and on water the Pokémon still moved away up to twice when the player got close at
  low search levels (upstream behaviour) until 0.8.1; since then it stays on its tile there too
  (D31).

## D20. Smart AI for every trainer

- Heart & Soul gives most ordinary trainers `Check Bad Move` only (427 of 651), which picks at
  random among moves that don't fail; 193 more use `Basic Trainer`. The user asked for a much
  smarter AI, as in Emerald Imperium.
- On NORMAL and HARD, `GetAiFlags()` (`src/battle_ai_main.c`) now adds the expansion's
  `Smart Trainer` and `HP Aware` to every trainer from the trainer data: it knows the
  player's Pokémon, moves, abilities and items, compares damage to pick the best move, goes
  for KOs, switches out of bad match-ups and picks its next Pokémon for the match-up, avoids
  PP stalling, and plays around HP (no setup at low HP, no healing at high HP). Trainers keep
  their own extra flags (Ace Pokémon and so on). EASY keeps each trainer's Heart & Soul AI.
  This replaces D5's "ordinary trainers keep HnS's cheaper AI".
- `Prediction` is not added. It makes the AI guess, half the time, that the player will
  switch whenever the AI would switch in the player's place, and then aim at the expected
  switch-in. Against a player who stays in, that wastes the turn: the battle autopilot (which
  never switches) beat Whitney 8 of 12 times with it and 3 of 12 without, and Bugsy 4 of 5
  against 3 of 5. Emerald Imperium predates the prediction flags.
- Cost: none measurable. In `gym_trainers_m2` a turn takes 562 frames on average against 568
  before (most of a turn is animation and text).

## D21. Imperium-style boss teams

- `tools/crystal_imperium/boss_teams.py` holds the reworked bosses and writes them into
  `src/data/trainers_hns.party`, keeping each trainer's header. Rules:
  - **Every Pokémon is at the player's level cap** (since 0.7.0; before, only the ace was, and
    the others were one or two levels below). The user asked for every boss's and Gym Leader's
    Pokémon to be at the level cap, to make the game harder. Each boss has a *stage*, the
    earliest point in the game its battle can happen (a badge count, the Johto League won or the
    Kanto League won). The party file holds that stage's NORMAL cap from `src/caps.c` (15, 24,
    33, 42, 50, 58, 66, 75, 85, then 90 and 100 since 0.8.0, D29). With the Rare Candy Box the
    player can always be at the cap.
  - **The battle sets the level from the player's cap table** (0.7.1). `CreateNPCTrainerParty`
    (`src/battle_main.c`) puts every Pokémon of a boss at `GetBossLevel` (`src/caps.c`): the cap
    at the boss's stage or the player's, whichever is later, from the HARD table when the LEVEL
    CAP option is HARD (the HARD preset picks it) and the NORMAL table otherwise (also with the
    cap OFF). The bosses and their stages are generated into `src/data/level_cap_bosses.h`.
    - In 0.7.0 the battle used the NORMAL table whatever the setting, and EASY and HARD scaled
      the result to 90% and 110%. A player on HARD met Falkner at 12 with a cap of 8, and
      reported that the level cap didn't match the bosses' levels. Bosses now aren't scaled by
      the difficulty: on HARD caps Falkner is at 12, on NORMAL caps at 15 (8 and 11 in 0.7.1),
      on every difficulty.
    - A boss fought later than its stage is raised to the player's cap then. This covers the
      battles whose badge count varies: the Rocket Hideout (the Lake of Rage needs Surf, so four
      to six badges: 50, 58 or 66 on NORMAL caps), Eusine in Cianwood, and the battles that are
      also rematches after the Kanto League (the Kanto Gym teams in the Fighting Dojo, the Johto
      leaders' and the Elite Four's `_2` teams before the Sinjoh story, the rival at the Indigo
      Plateau): at 100 then.
    - Other trainers' Heart & Soul levels are mapped onto the cap curve (D29) and scaled by EASY
      and HARD, and are never above the player's cap (D28): `boss_levels` checks a Grunt's
      level-20 Koffing, at 31 with six badges and at the cap (15, or 12 on HARD caps) with none.
  - Heart & Soul's own teams for the other bosses keep their Pokémon and only get the levels
    (`LEVEL_ONLY` in `boss_teams.py`): Li and the first rival battle; the rival on Mt. Moon and
    at the Indigo Plateau, the Fighting Dojo rematches and the Kanto League (90); and every
    rematch after it (`_POSTOBC`: 100). Falkner, Bugsy, Whitney and Eusine had Heart & Soul's
    teams until 0.8.0 (D29, D30). The bonus storylines'
    trainers (New Sinjoh, Samson Oak, Steven, Giovanni) are at or above the cap where they can
    first be fought and keep their levels; the unused and debug-only teams too.
  - Every Pokémon has a held item, a nature, an ability chosen for the set and four moves its
    species or a pre-evolution can learn (`validate.py` checks abilities, moves, that every
    boss is at its stage's cap and that no boss trainer is missing from the list).
  - Six Pokémon for every Gym Leader, the rival from his second battle, Proton, Petrel, Ariana,
    Archer, Eusine, the Elite Four, Lance, Blue and Red (since 0.8.0, D30; before, 3–4 for the
    early story bosses and 5 for Morty and a 5th Gym). Li keeps three, the first rival battle his
    starter, and each Kimono Girl her one Eeveelution.
  - From the 5th Gym on, each boss has one Mega Evolution with a stone from the Mega shop's
    tiers (D9). The stone isn't always on sale before the boss who uses it: Steelixite and
    Abomasite come with the 6th badge, and Jasmine or Pryce can be the 5th Gym. Morty has none
    (the player's Mega Ring arrives only one badge earlier).
  - Chuck, Jasmine and Pryce have three versions each, picked by how many of the three the
    player has beaten (HnS's `_1`, `_1_2`, `_1_3`): caps 50, 58 and 66.
  - The Kanto leaders and Blue are at 90 (the cap for all of Kanto). Red, with no cap left, was
    at 86–90; since 0.6.0 he is the hardest battle, and since 0.7.0 all six are at 100 (D27).
- Done: Proton (Slowpoke Well and Radio Tower), Petrel and Ariana (Rocket Hideout and Radio
  Tower), Archer; the rival's 2nd–5th battles (Azalea, Burned Tower, Goldenrod Underground,
  Victory Road; all three starter versions); Morty, Chuck, Jasmine, Pryce, Clair; the five
  Kimono Girls; Will, Koga, Bruno, Karen, Lance; the eight Kanto leaders, Blue and Red.
- Megas: Chuck's Heracross, Jasmine's Steelix, Pryce's Abomasnow, Clair's Altaria, Archer's
  Houndoom, the rival's Tyranitar (Victory Road), Will's Alakazam, Koga's Beedrill, Bruno's
  Lucario, Karen's Absol, Lance's Gyarados; Brock's Aerodactyl, Misty's Blastoise, Lt. Surge's
  Manectric, Erika's Venusaur, Janine's Gengar, Sabrina's Metagross, Blaine's Camerupt, Blue's
  Pidgeot, Red's Charizard (Y).
- Evidence (since 0.7.0 the player's test teams hold items from the care packages the player
  has by then, D16; `boss_levels` checks the bosses at the player's NORMAL and HARD caps and the
  raise to the cap, `difficulty` that EASY and HARD leave bosses at the cap, `validate.py` every
  level in the party file):
  - `bosses_m3`: the naive play-test team (3–5 Pokémon at the cap with their default moves)
    loses every one of these battles. A prepared six at the cap (good natures and moves, items
    from the first three packages, one move per Pokémon, never switching) wins at least once
    against Morty and Jasmine in eight tries and Clair in sixteen (Clair: 8 and 6 of 16). With
    every boss Pokémon at the cap it beat Pryce once in 16 with items (twice with a game plan
    too) and Chuck 1 to 5 times in 8, so Chuck and Pryce face sixes built for them, played with a
    game plan (16 of 16 against Chuck; 13 of 16 and 16 of 16 against Pryce), in eight tries.
    Every boss Mega Evolution happens.
  - `bosses_m4`: every Rocket executive, rival and Kimono Girl battle plays to a result against
    the prepared six at the cap. Archer's and the rival's Megas, on their aces, are checked
    with the six at level 100: at the cap the six lost to Archer before Houndoom came out.
  - `bosses_e4`: at cap 56. In 0.5.0 the prepared six beat Will 2 and 1 times in six
    (mGBA, VBA-M) and Koga 5 and 5 times; sixes built for them beat Bruno 2 and 3 times, Karen
    2 and 1 times and Lance 2 and 1 times. Those naive samples turned out too unreliable to
    require a win (Will about 1 try in 20 over 60 tries), so since 0.6.0 Will, Bruno, Karen and
    Lance face sixes played with a game plan, in 8, 6, 8 and 24 tries (D27). With every boss
    Pokémon at the cap (0.7.0) and no items, Will beat the planned six in all 8 tries on mGBA;
    holding items from the first eight packages the sixes beat Will 9 and 7 times in 16, Bruno
    10 and 9, and Lance 6 and 9 times in 24. Bruno and Karen now get 12 tries. Every Mega
    Evolution happens.
  - `bosses_m5`: at cap 70 the prepared six won one try each against Lt. Surge and Erika on
    both emulators, Sabrina on mGBA and Blaine on VBA-M, and lost the others; a six built for
    Blue beat him 2 and 1 times in 3 (0.5.0; since 0.6.0 it plays a game plan, 10 of 12). With
    the prepared six at level 100 every Kanto leader's and Blue's Mega Evolution happens. Red,
    reworked as the hardest battle in 0.6.0, has his own test (`red`, D27).
- The naive autopilot never switches and uses one move per Pokémon, and the game-plan mode
  only switches to a counter, so these are lower bounds; a player who switches, heals and reads
  the opponent does better. Each boss was checked to be beatable by some team (before 0.7.0
  without items); the ones it couldn't beat were changed:
  - Lance first had three Dragon Dance users, and the all-round six lost all six tries. With
    only Dragonite setting up, his Roosting Charizard and two Full Restores still beat three
    different sixes built for him in all nine tries on VBA-M. Now Mega Gyarados has Thunder
    Wave, Salamence Dual Wingbeat, and Charizard Dragon Pulse instead of Roost.
  - Blue's and Bruno's Machamp have Close Combat instead of No Guard Dynamic Punch (a
    guaranteed confusion every turn): Blue had beaten every team in all six tries.
- Still Heart & Soul teams (with the smart AI), now at the cap too: Gym Leader and Elite Four
  rematches and the other postgame battles.

## D22. Emerald Imperium's TM list

- The user asked for the same TMs as Emerald Imperium. Its official TM guide lists TM001–TM174
  ([pokemonemeraldimperium.com](https://pokemonemeraldimperium.com/all-tms-and-hms-location-guide/)).
  Two of them teach moves Imperium made itself, "Dark Hole" (TM161) and "Draco Barrage"
  (TM171), which the engine doesn't have and D2 keeps out (Radical Red's moves, in fact; since
  0.13.0 the engine has them, as postgame tutor moves, D39). Crystal Imperium has the other 172,
  in Imperium's order, as TM01–TM172; from Imperium's TM162 on the numbers are one lower here,
  and from its TM172 on two lower. A list of move names is design data, not Imperium code or
  assets.
- TM173–TM198 are the 26 Heart & Soul TMs Imperium's list lacks (Hail, Hyper Beam, Safeguard,
  Frustration, Double Team, Shock Wave, Torment, Secret Power, Attract, Skill Swap, Snatch,
  False Swipe, Brine, Fling, Endure, Embargo, Payback, Recycle, Giga Impact, Rock Climb,
  Avalanche, Psych Up, Captivate, Natural Gift, Dream Eater, Swagger), so every TM the story
  hands out still exists. `tools/crystal_imperium/tm_list.py` holds both lists and writes the
  TM list, the item data and the shop lists.
- Imperium numbers many TMs as Gen 4 did, so 64 of Heart & Soul's 92 TMs keep their number.
  28 move, for example TM03 Water Pulse → TM160, TM41 Torment → TM179, TM70 Rock Climb →
  TM192, TM92 Trick Room → TM106. The two script texts that named a moved number now give the
  new one. TM101–TM198 are new item ids after the last item, so item ids in older saves keep
  their meaning.
- Each TM's description is its move's description, re-wrapped by glyph width (read from the
  game's font tables) to fit the bag's 3-line box; nine long ones use the small font.
- **The TM case.** 206 machines don't fit SaveBlock1's 160 TM slots, and SaveBlock1 has no room
  to grow (15,760 of 15,872 bytes). The case now lives in EWRAM (208 slots) and is saved in
  SaveBlock3 as one count per machine plus a version byte (SaveBlock3: 1,548 of 1,624 bytes).
  Its quantities aren't XOR-encrypted like the other pockets, since no save block holds it.
- **Older saves** (Heart & Soul 2.0.6 and earlier Crystal Imperium builds) have version 0
  there. When one loads, its TMs move from SaveBlock1 into the counts, converted by move: Heart
  & Soul's TM70 Rock Climb becomes TM192 Rock Climb, not TM70 Triple Axel. TMs stored in the
  item PC or held by Pokémon in the party, the boxes and the Day-Care are renumbered the same
  way. HMs are unchanged.
- **Where to get them.** Imperium's TM locations are on its Hoenn map, so they can't be
  copied. Heart & Soul's own TM gifts and item balls are unchanged (same moves as before), and
  the Goldenrod Dept. Store 5F sells every TM, more with each badge tier:
  - from the start: status moves and moves below 70 power, plus Heart & Soul's own 5F stock
    (71 TMs);
  - 3 badges: strong setup and hazard moves, multi-hit and variable-power moves, 70–89 power
    (155);
  - 6 badges: 90–109 power (178);
  - 8 badges: the rest, 110+ power and Explosion (198).

  The badges are counted (Gyms 5–7 come in any order, so a badge flag alone wouldn't do).
  Since 0.11.0 the shop has a list for every badge count and every Poké Mart has a TM clerk with
  the same lists (D36).
  Every TM costs ¥100 since 0.9.0, Emerald Imperium's price (its TM vendors and Game Corner
  counter: [PokéMarts guide](https://pokemonemeraldimperium.com/pokemarts-guide/)); before,
  ₽1,500 / 3,000 / 5,000 / 8,000 by tier, and Heart & Soul charged ₽10,000 for its 5F TMs.
- **Early TMs (0.9.0).** The user found few TMs after the first badge (two), where Emerald
  Imperium has many: its first vendors, Dewford Town's outdoor clerks after its first Gym, sell
  seven TMs at $100, and four more are free before its second Gym (Bullet Seed from a man on
  Route 104, Bulldoze from Roxanne, Bug Bite and Stomping Tantrum on the ground: [TM
  guide](https://pokemonemeraldimperium.com/all-tms-and-hms-location-guide/)). A second clerk
  in the Violet City Mart, at (2,2) behind the counter, sells those seven (Electroweb, Icy Wind,
  Aerial Ace, Low Kick, Pluck, Snarl, Smack Down) from the Zephyr Badge on, and the first time
  gives the four (`FLAG_RECEIVED_VIOLET_TMS`). A clerk reaches saves that already have the first
  badge, which a TM in the first care package wouldn't. Same numbers as Imperium's, as the
  list is in its order. Shop lists show each TM's move next to its number ("TM03 FLIP TURN"), as the bag does;
  with up to 198 entries, numbers alone weren't usable. The Mega Stone shop's 6-badge tier now counts badges the same way (it read Jasmine's
  badge flag).
- TMs stay reusable (Heart & Soul's REUSABLE TMS option, on by default).

## D23. HMs work without teaching them

- Heart & Soul already let a Pokémon that *can learn* an HM move use it while the player
  carries the HM. In its challenge runs (Nuzlocke, Mirror, random moves, party limit, one
  type) carrying the HM was enough for any Pokémon. The user asked to use HMs without teaching
  them, so that rule (`HMsOverwriteOptionActive`) is now always on. Each field move still
  needs its badge.
- Cut, Rock Smash, Strength and Waterfall use the first Pokémon in the party that isn't an
  Egg; Surf works when facing water; Fly and Flash appear in the lead Pokémon's party menu (a
  lead that could learn Fly keeps the entry it had without HM02). Rock Climb, a TM here, works
  the same way through the same code.
- Evidence: `hm_field_moves`. A Magikarp, which can learn none of these moves, cuts the Route 29
  tree, opens the Fly map from its party menu and surfs, with only the HMs and badges. In
  `dexnav_caves` a Cyndaquil uses Flash from its party menu with HM05 and the Zephyr Badge; since
  0.8.1 Flash lights the whole cave (D31).

## D24. DexNav lists the Pokémon you meet

The user found that the Pokémon DexNav lists didn't match the ones met in the wild. Three
things caused it in 0.5.0:

- Wild Variety (D14) replaced 30% of encounters with a random pick from about 445 Pokémon,
  which no list can show. On Route 29 at night, DexNav listed Hoothoot and Rattata while 6 of
  12 test battles were other Pokémon.
- With Heart & Soul's randomizer on for wild Pokémon, DexNav listed the unrandomized Pokémon:
  12 of 12 battles were unlisted.
- A mass outbreak's Pokémon wasn't listed.

Now one function, `WildVariety_GetAreaList` (`src/wild_variety.c`), makes the list that
DexNav shows and that wild encounters draw from:

- **The area's own Pokémon** as encounters turn them out. With the randomizer on for wild
  Pokémon and MAP SEEDED on, each encounter slot always gives the same randomized Pokémon, and
  DexNav lists those (one per slot, so the land row is often full).
- **A mass outbreak's Pokémon**, in the grass.
- **The day's Wild Variety set** in the free slots of DexNav's row (12 in the grass, 5 on the
  water): up to six Pokémon in the grass and three Water-type ones on the water. The set is
  drawn from the variety pool with a seed made of the map, the area, the RTC day counter (real
  clock or Heart & Soul's fake clock) and the trainer ID, and evolved for the area's highest
  level. It stays the same all day, changes at midnight, and differs between saves. A Wild
  Variety encounter is one of the set: each of its Pokémon is (WILD VARIETY share) / 6 of grass
  encounters (5% each at 30%) and / 3 on the water. About one land table in five has 7 or
  more of its own Pokémon (12 at most); there the set is smaller and variety rarer, rather
  than unlisted.
- **Legends after becoming Champion:** a quarter of the day's sets (rolled per area and day)
  end with a Legendary, Mythical, Ultra Beast or Paradox Pokémon, Water-type ones on the
  water. The rest of the set stays as it was before becoming Champion. In 0.5.0, 3% of variety
  encounters everywhere were legendary; the average is similar (about 1.25% of grass
  encounters), but now DexNav shows where one is.
- Fishing gives the area's fishing Pokémon, or a Pokémon of the water set (DexNav has no
  fishing row, as in the expansion's DexNav). The detector finds what an encounter would turn
  up (randomizer and Wild Variety included). The caught-all marks count the listed Pokémon.
- A listed Pokémon is searched for with A like any other; Wild Variety and randomized ones are
  found at the area's levels.
- **Not listable:** with the randomizer's MAP SEEDED off, or CHAOS on, every encounter is a new
  random Pokémon, so DexNav lists the area's own Pokémon. Roaming Pokémon aren't listed (as in
  the main games). The Bug-Catching Contest, the Battle Pike and the Battle Pyramid have no
  Wild Variety, and DexNav lists none there.
- Evidence: `dexnav_wild_match` (Route 29: the two own Pokémon and six Wild Variety ones
  listed, 12 battles all listed, 6 of them Wild Variety; the next day's set is new and its
  battles are listed; the first day's set comes back unchanged; a Wild Variety Pokémon picked
  in DexNav is searched for and battled; an outbreak's Pikachu is listed and met),
  `dexnav_water_match` (New Bark Town: Tentacool and three Water-type Wild Variety Pokémon
  listed; 12 surfing battles all listed; 7 bites in 10 casts on mGBA, 6 on VBA-M, all the town's
  fishing Pokémon or listed ones), `dexnav_randomizer` (randomized Route 29: 12 Pokémon listed, 12 battles all
  listed) and `wild_variety` (OFF: only the route's own Pokémon listed and met). On the 0.5.0
  ROM the same checks found 6 of 12 and 12 of 12 battles unlisted. Over 16 days after becoming
  Champion, 4 of Route 29's sets had a legend.

## D25. HARD plays by Emerald Imperium's and Radical Red's rules

- The user asked for HARD to match Emerald Imperium's or Radical Red's settings, with no
  "Will you switch Pokémon?" prompt. Emerald Imperium's main mode forces the SET battle style
  and disables the Bag in trainer battles (its Easy mode allows both)
  ([difficulty modes](https://pkmnemeraldimperium.com/difficulty-mode/)); Radical Red's
  Hardcore mode is described the same way by its community wiki. Radical Red's restrictions on
  the player's own moves and abilities are left out: the user asked for the battle settings.
- On HARD, `ClearSetBScriptingStruct` sets `gBattleScripting.battleStyle` to SET whatever the
  option says (the fainted-Pokémon script reads it before asking), and `IsAllowedToUseBag`
  refuses the Bag in trainer battles with the engine's "Items can't be used now." Wild battles
  keep the Bag (Poké Balls, healing). The options menu shows BATTLE STYLE as SET and grayed
  out on HARD.
- HARD keeps +10% trainer levels and HARD level caps (D11). EASY and NORMAL are unchanged.
- Evidence: `hard_mode_rules` (HARD: a trainer battle and a wild battle play SET; BAG in the
  trainer battle is refused and the battle continues; in the wild battle the Bag opens; a
  NORMAL wild battle keeps the option's SHIFT).

## D26. A Gen 5 look: BW battle interface and BW summary screen

- The user asked for the screens to have a Gen 5-and-up feel, like Radical Red. Two community
  feature branches for pokeemerald-expansion give the two most-used screens a Black/White
  look, and their authors allow use with credit (README credits):
  - **BW Battle UI** by mudskip (`mudskipper13/pokeemerald`, branch `feature/bwBattleUI`, on
    expansion 1.15.3, ours is 1.15.2): healthboxes, text box, the FIGHT / BAG / POKÉMON / RUN
    box, the move box with types, PP and effectiveness, party-ball bars, ability pop-ups,
    outlined fonts.
  - **BW Summary Screen** by RavePossum (`ravepossum/pokeemerald-expansion`, branch
    `bw_summary_screen_expansion`, on expansion 1.14.0) and the contributors it credits.
- Porting: the branches' changes were applied over Heart & Soul's code by hand where they
  conflicted. Their `INCGFX` graphics (a newer build-system feature) became `INCBIN` with
  explicit `graphics_file_rules.mk` rules. The summary screen was adapted to expansion 1.15's
  APIs (stats, Poké Ball sprites, Pokérus, the naming screen, the move relearner), and the
  vanilla summary entry points forward to it, so every caller (party menu, PC, evolution,
  move learning, relearner, trades) opens the BW screen. Pokémon opened from the PC show no
  relearner prompt (the PC has its own).
- Settings: IVs and EVs show as exact numbers on the skills page (Heart & Soul showed them);
  move info moved from START to L, which the BW move box labels; Gen 4+ move order in battle
  (`B_MOVE_REARRANGEMENT_IN_BATTLE`), which the BW interface requires. Heart & Soul's BATTLE UI
  option (GEN 3 / GEN 4 healthboxes) is removed and `UseGen4BattleUI()` returns FALSE.
- Cost: about 180 KB of ROM (98.82% → 99.37% of 32 MB, about 208 KB left). The BW battle
  windows (the move box, the action box, the move-name windows) take about 8 KB more heap
  during a battle; with Heart & Soul's heap, battles that decompress big graphics mid-battle
  ran out of memory (Blaine's Drought lead, Will's Farigiraf, Archer and Proton in the play
  tests). The heap is 8 KB larger (0x1E500), and the Wild Variety pool was cut to the 567
  Pokémon it holds, so EWRAM is 99.12% used (about 2.3 KB free).
- Not changed: the party menu, bag, start menu and Pokédex keep Heart & Soul's look. A
  Gen 5-style party menu exists for vanilla pokeemerald (Archie's), but its colors and tiles
  don't match Heart & Soul's party graphics or the BW screens.
- Evidence: `bw_ui` (the BW summary screen opens from the party menu and shows IVs; the battle
  action box is the BW one; FIGHT opens the BW move box), the whole suite on both emulators,
  and screenshots of every page.
- Fix (0.10.1): the battle health box clears all 7 tiles a Pokémon's name can take (the BW
  battle UI cleared 6, so a shorter name kept the end of a longer one after a switch, e.g.
  "LARVITAR -|" after FERALIGATR). None of the four health boxes (singles and doubles, player
  and opponent) has art there; the Safari box, which has, doesn't print a name. Evidence:
  `battle_healthbox_names` (ONIX's name strip, after switching to FERALIGATR and back, matches
  the first one pixel for pixel; 8 pixels differ on the 0.10.0 ROM).

## D27. Red is the hardest battle in the game

- The user asked for the battle with Red to be the hardest in the game. Red's two parties
  (`TRAINER_RED_HNS`, and `TRAINER_RED_POSTOBC_HNS` after the Sinjoh story) are the strongest in
  the game, and `validate.py` keeps them so:
  - All six at level 100, in both battles (since 0.7.0; 96–100 in 0.6.0). With every boss at
    the level cap (D21) the rematches after the Kanto League are at 100 too, so what sets Red
    apart is below: no other trainer keeps EVs, carries four Full Restores or has his sets.
  - Competitive EVs on all six, and Red's are the only Pokémon whose EVs Minimal Grinding keeps
    (`IsRedsPokemon` in `CalculateMonStats`, `src/pokemon.c`). Everyone else, the player
    included, battles at 31 IVs and 0 EVs when it is on (the default). His lead Pikachu has 306
    Speed instead of 237.
  - The boss AI with `Prediction` (it predicts switches and moves and punishes them), Ace
    Pokémon and HP Aware, and four Full Restores (other bosses carry two at most).
  - A sun team: Mega Charizard Y's Drought powers Venusaur's Chlorophyll and Growth and
    Charizard's Solar Beam; Light Ball Pikachu leads with Fake Out; Magic Bounce Espeon, a
    Curse/Rest Snorlax and a White Herb Shell Smash Blastoise.
- **Red battles only the Kanto Champion.** Oak opens Mt. Silver and the Kanto League at the
  same time (16 badges), and the level cap stays at 90 (70 before 0.8.0) until the Kanto League
  is won; at the cap a level-100 team with EVs is out of reach. Before the Kanto League Red
  now stays silent ("RED seems to be waiting for the KANTO CHAMPION."), so he is the last
  battle and the player can bring a level-100 team. Heart & Soul let him be fought after 16
  badges.
- **How hard, and is he beatable?** The battle autopilot can't prove a person's chances, but
  its numbers bound them (BALANCE.md has the details):
  - Played naively (one move per Pokémon, no switching, no items) every team at level 100
    lost all 30 tries, legendary Dragons included. Against the other bosses naive teams win
    some tries at those bosses' caps.
  - With a game plan (a counter for each of Red's Pokémon, switched in when needed) and no
    held items it lost 12 of 12. With held items and a Mega, as a player would bring, it won
    4 of 12 (`red` requires at least one win in 12 tries).
  - Two Full Restores instead of four, or no prediction AI, still lost every try; without
    the EVs naive and planned teams won some. The EVs are the biggest single factor.
- The autopilot's game-plan mode (`plan=` in emurun's autobattle, `plan` in `emu.py`) was
  written for this and is now also used for the hardest Elite Four battles and Blue, whose
  naive samples were too unreliable to require a win (Will was beaten about 1 try in 20).
  Expansion's own AI-vs-AI mode (`B_FLAG_AI_VS_AI_BATTLE`) was tried first; in this build
  the player's side stops after its first Pokémon faints, so it isn't used.
- Evidence: `red` (no battle before the Kanto League; the summit battle is `TRAINER_RED_HNS`
  and after the Sinjoh story `TRAINER_RED_POSTOBC_HNS`; Pikachu's EV Speed; the game-plan win;
  Mega Charizard Y); `validate.py` (no trainer with a higher average level, EVs on all six,
  prediction AI, more Full Restores than any other trainer).

## D28. Nothing above the level cap

- With a level cap on (LEVEL CAP NORMAL or HARD), no Pokémon the player meets or is given is
  above it (0.7.1). A player reported catching a level-12 Turtwig with DexNav at a cap of 8:
  DexNav adds a fifth of the DexNav chain to the area's level, and in 4% of searches 10 more,
  and nothing checked the cap. The player can't level past the cap, so a Pokémon above it
  could only be caught, not raised, and gave a head start the cap is meant to prevent.
- `src/caps.c`: `GetLevelWithinCap` holds a level at `GetCurrentLevelCap()` (no change with the
  cap OFF). Levels are only lowered, never raised.
- Battles where catching is off (`FLAG_NO_WILD_CATCHING`) are held at the cap too: the player
  asked for the bosses to match the level cap, and those are wild boss battles. They are Route
  41's level-100 Tentacruel (a joke for poking it three times; it heals the party after), the
  post-game wild bosses (Alola's totems at 60, the Hisuian Pokémon such as Kleavor and
  Ursaluna at 75–80, the Sinjoh Ruins' Arceus at 80 and 100: held only when met before the Kanto
  League, at 90) and the Saffron Fighting Dojo's level-1 training battles (below every cap).
- Where it applies:
  - Random encounters, fishing, Rock Smash, mass outbreaks, Wild Variety and the randomizer's
    Pokémon: `CreateWildMon` (`src/wild_encounter.c`).
  - DexNav: the search's level (shown in the search window) and the battle
    (`DexNavTryGenerateMonLevel`, `src/dexnav.c`).
  - Scripted wild battles (`setwildbattle`, berry trees, the Bug-Catching Contest's area) and
    legendaries and other event Pokémon (`seteventmon`): `src/script_pokemon_util.c` and
    `CreateEnemyEventMon` (`src/pokemon.c`). E.g. Zapdos (50) is met at 15 with no badges.
  - Roaming Pokémon (`CreateRoamerMonInstance`, `src/roamer.c`). A roamer keeps its own level
    and HP between meetings; met below its level it has at most that level's max HP, and if it
    is left unhurt its stored HP doesn't drop (`UpdateRoamerHPStatus`).
  - Gift Pokémon from `givemon` (e.g. the Cianwood Pokémon Center fisher's level-25 Tentacool,
    Mt. Mortar's Tyrogue, the revived fossils). The debug menu's Give Pokémon isn't held, so the
    play tests can still give any level.
  - Trainers (D11, D21): bosses are at the cap; other trainers' levels, after EASY's or HARD's
    scaling, are held at the cap. This also holds Steven at Sinjoh Ruins (77–79, 92–93 on the
    0.8.0 cap curve) at 90 when he is fought before the Kanto League (KNOWN_ISSUES #34).
- In-game trades keep the level of the player's Pokémon traded away, which is within the cap.
- Evidence: `level_cap_wild` (DexNav with a chain of 100, a level-50 outbreak with catching on
  and off, Zapdos, the Tentacool gift; 15 on NORMAL caps and 12 on HARD caps), `boss_levels` and
  `difficulty` for trainers.

## D29. Emerald Imperium-style level caps

- The user asked for higher level caps, as in Emerald Imperium, where the highest cap before
  the Elite Four is first beaten is 85. Heart & Soul's caps topped out at 56 for the Elite Four
  and 70 for Kanto. Emerald Imperium publishes no cap table (its site lists built-in level caps
  and a nurse that sets Pokémon to the cap), so the curve ends at that 85 and climbs to it in
  steps of 8–10 levels a badge:

  | Stage | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 (Elite Four) | Johto League won (Kanto) | Kanto League won |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | NORMAL | 15 | 24 | 33 | 42 | 50 | 58 | 66 | 75 | 85 | 90 | none (100) |
  | HARD | 12 | 21 | 30 | 39 | 47 | 55 | 63 | 72 | 85 | 90 | none (100) |
  | Heart & Soul | 11 | 16 | 21 | 25 | 31 | 36 | 38 | 45 | 56 | 70 | none |

  - The Elite Four's cap is 85 on HARD caps too: the user plays with them and asked for 85.
    Before it, HARD stays 3 levels lower. Lower caps are harder although the bosses are at the
    cap as well, because a boss's moves and evolutions don't depend on its level and the
    player's do.
  - Kanto is at 90: above the Johto League, below Red's 100 (D27). As in Heart & Soul, the Kanto
    badges don't raise it; winning the Kanto League removes the cap.
- **Bosses** are at the cap (D21), so they move with the table: `boss_teams.py` reads it from
  `src/caps.c` and writes every boss's levels.
- **Other trainers** keep their Heart & Soul party data. Their levels were made a few levels
  under Heart & Soul's caps, so at battle time `GetLevelOnCapCurve` (`src/caps.c`) maps a level
  linearly between the caps of the stages around it onto the player's table: a trainer half
  way between the 1- and 2-badge caps (16 and 21) stays half way (24 and 33). E.g. Route 30's
  2–4 stay 2–5, the Azalea Gym's 12–14 become 17–20, a Rocket Grunt's 20 becomes 31, Routes
  26–27's 42–50 become 71–80. EASY and HARD then scale them by 10%, and the cap holds them
  (D28). Without the mapping the regular trainers late in Johto would have been up to 35 levels
  below the bosses and the player. Phone rematches pick their team by Heart & Soul's levels and badges
  (`sRematchLevelCeilingByBadges`), so they come at the same points of the game as before.
  Prize money uses the party data's levels (KNOWN_ISSUES #39).
- **Wild Pokémon** keep Heart & Soul's levels, as Emerald Imperium's do: the player catches
  them low and brings them up with the Rare Candy Box (Emerald Imperium has a nurse that sets
  the party to the cap). They are never above the cap (D28).
- Early bosses with Heart & Soul's own teams fell behind at the higher caps. Their teams kept
  their early moves while the player's level-up moves got stronger:
  - Bugsy got an Imperium-style team (BALANCE.md): the naive test line had beaten Heart & Soul's
    team 19 times in 20.
  - Whitney keeps Heart & Soul's team and moves, now with held items: without them the same
    line won 13 of 20.
  - Li and the first rival keep Heart & Soul's teams; Falkner and Eusine got six-Pokémon
    teams with the other bosses (D30).

## D30. Six-Pokémon bosses and route mini-bosses

- The user asked for most big boss battles, especially the Gym Leaders, to have six Pokémon, and
  for strong trainers with competitive teams on the routes, as in Emerald Imperium (its route
  mini-bosses).
- **Six Pokémon** (`boss_teams.py`) for every Gym Leader (Falkner, Bugsy, Whitney and Morty
  were at 3, 4, 4 and 5; Chuck, Jasmine and Pryce as the 5th Gym at 5), the rival from his
  second battle on (4–5 before), the Rocket executives in all their battles (Proton at the
  Slowpoke Well 3, Petrel and Ariana 4–5) and Eusine (3).
  - Falkner keeps Heart & Soul's Pidgey, Rookidee and Noctowl and adds Magic Bounce Natu, Gale Wings
    Fletchling and Prankster Murkrow; Bugsy adds Butterfree and Yanma, his Spinarak now an Ariados,
    with new sets (BALANCE.md); Whitney Furret and Girafarig; Morty Mimikyu; Proton Golbat, Grimer
    and Raticate; the rival Haunter and Magneton (Azalea), Haunter (Burned Tower), Alakazam
    (Goldenrod Underground); Petrel Golbat and Houndoom, then Toxapex; Ariana Liepard and Gyarados,
    then Skuntank; Proton at the Radio Tower Toxicroak. Eusine has a rain team (Drizzle Politoed,
    Thunder from Electrode and Lanturn) instead of Heart & Soul's three with 2 IVs.
  - Unchanged: Li (three, before the first Gym), the first rival battle (his starter, just after
    the player gets theirs) and the Kimono Girls (one Eeveelution each, five battles in a row).
- **Route mini-bosses** (`ROUTE_BOSSES` in `boss_teams.py`): 28 existing route trainers, 16 in
  Johto and 12 in Kanto, have competitive teams like the bosses': a held item, nature, ability
  and four chosen moves on every Pokémon, themed by the trainer's class (a Hiker's Rock and
  Ground types, a Swimmer's rain team, a Psychic's Psychic types), with the boss AI.
  - They are bosses for the level code (D21): at the level cap. Their stage is the earliest
    point their route can be reached, set low where it isn't certain (Route 26 and 27 can be
    reached with Surf before the 8th badge), so a mini-boss is never above the player's cap and
    is raised to it when met later.
  - Team size grows with the stage: 3 before the first badge (Routes 30 and 32), 4 on Routes 34
    to 39, 5 in the rest of Johto, 6 on Routes 26, 27 and 45 and in Kanto.
  - Chosen from trainers without phone rematches (whose later teams would still be Heart &
    Soul's) and without double battles, one per route: Route 30 Mikey, 32 Roland, 34 Kate, 35
    Bryan, 37 Greg, 38 Valerie, 39 Eugene, 40 Simon, 41 George, 42 Benjamin, 43 Ben, 44 Cybil, 45
    Kelly, 47 Devin, 26 Jake, 27 Blake; in Kanto Route 1 Quinn, 3 Otis, 8 Dwayne, 9 Tim, 10
    Robert, 11 Herman, 12 Stephen, 13 Bret, 15 Colette, 18 Boris, 20 Lori, 25 Kevin.
  - Their names, places and lines are Heart & Soul's; only the teams changed.
- `validate.py` checks them like the bosses (moves, abilities, levels at the stage's cap); it now
  reads a form's learnset from its base species when the form has none of its own (Mimikyu).
- Evidence: `route_bosses` (every mini-boss's team size, its lead's and ace's levels at the cap,
  and a battle against the prepared six to a result), `boss_levels`, `bosses_m3`, `bosses_m4`,
  `bugsy` and `whitney` for the six-Pokémon bosses.

## D31. DexNav in caves and on water

- The user reported two DexNav problems in caves:
  - In Dark Cave DexNav said "It's too dark to search for a Pokémon!" even after Flash. DexNav
    doesn't search while the flash level is above 0, and Flash only brought it down to 1, the
    widest lit circle (Heart & Soul kept Emerald's Flash). Dark Cave's two maps are the only
    ones that need Flash.
  - In a lit cave the Pokémon "ran away": the expansion's DexNav moves it to another tile, up to
    twice, when the player comes within 2 to 4 tiles in a cave or on water.
- **Flash lights the whole cave**, as in Gold, Silver and Crystal. The Flash script animates to
  flash level 0, full brightness (the light spreads 4 pixels a step, so it takes about as long
  as the old circle), and a cave entered while Flash is in use is fully lit
  (`SetDefaultFlashLevel`).
  - Relaxing DexNav's check instead wasn't enough: outside the lit circle only text boxes are
    drawn, so DexNav's icons and the rustling spot would have been hidden.
  - A save made in Dark Cave after Flash with 0.8.0 or earlier holds flash level 1; it continues
    fully lit (`CB2_ContinueSavedGame`).
  - DexNav's detector for hidden Pokémon has the same darkness check, so it works after Flash
    too (not play-tested). Battles in Dark Cave after Flash open with the cave transition, not
    the dark one.
- **The Pokémon stays on its tile** in caves and on water, as in grass: the move is removed
  (D19 removed the sneaking rules).
- Evidence:
  - `dexnav_caves`, in Dark Cave: DexNav is too dark before Flash. Flash from a Cyndaquil's
    party menu brings the flash level to 0, and DexNav searches. A save made there with flash
    level 1 continues at 0, and DexNav searches.
  - `dexnav_caves`, in Union Cave 1F: the DexNav Geodude stays put, the battle starts, and it is
    caught.
  - `dexnav_surf`: in New Bark Town the DexNav Tentacool stays put while the player surfs up to
    it.
  - On the 0.8.0 ROM both tests fail at those steps: DexNav is too dark after Flash, and the
    Geodude and the Tentacool move away.
- The play tests' path finding (`walkto ... path`) now follows the target's elevation, so a walk
  on a cave floor doesn't route through water.

## D32. Fast Egg hatching

- The user asked for fast Egg hatching. An Egg cycle now passes every 8 steps
  (`P_EGG_CYCLE_STEPS`, `src/daycare.c`) instead of every 256 (Heart & Soul, as Gen 3): 32 times
  faster. An Egg hatches after its species' egg cycles plus one: a Togepi Egg (10 cycles) in
  about 90 steps, a starter's (20) in about 170, a Dratini's (40) in about 330. Flame Body,
  Magma Armor and Steam Engine still halve that.
- The Day-Care still makes Eggs at Heart & Soul's pace (a chance every 256 steps).
- Evidence: `egg_hatch` (a Togepi Egg from the debug menu hatches during a 126-step walk; 97
  steps here; with 256 steps a cycle, on the 0.8.0 ROM, the same walk doesn't hatch it).

## D33. Rare Candies several at a time

- The user found giving Rare Candies clunky, and the music stopped every time: each candy played
  the level-up fanfare, which pauses the map music, then waited for it, and showed two stat
  pages. Emerald Imperium 1.3 removed the stat pages after its Infinite Candy "so less mashing
  of A is required" ([changelog](https://pokemonemeraldimperium.com/changelog/)); the user
  pointed to Radical Red, whose exact Rare Candy behaviour no source documents, so this follows
  the user's description (faster, music on) and the later games' "how many?" choice.
- With `I_QUICK_RARE_CANDY` (`include/config/item.h`, `src/party_menu.c`):
  - After the Pokémon is chosen, the party menu asks "How many will you use?" with the count
    ("×010") beside it: at first all the candies up to the level cap (or the bag's count, if
    lower); UP/DOWN change it by 1, LEFT/RIGHT by 10, A uses them, B goes back to choosing a
    Pokémon. With one level left there's no question.
  - They are used at once: one message ("... was elevated to Lv. N."), a short sound
    (`SE_EXP_MAX`) instead of the fanfare, so the map music goes on, and no stat pages.
  - The moves of every level passed are still offered in order, then the Pokémon evolves; the
    party menu stays open for the next Pokémon. At the cap a candy gives no level, but a
    Pokémon that can evolve still does (Heart & Soul's behaviour), so a second stage needs one
    more candy.
  - Exp. Candies get the same message, sound and missing stat pages, one at a time.
- Evidence: `rare_candy` (Magikarp: 10 at first, 9 with DOWN, used at once with no fanfare,
  then one more with no question; B uses none; Caterpie: 10 at once, Bug Bite on the way,
  Metapod, then Butterfree with one more candy at the cap), `qol_items` (the cap stops them).

## D34. The L menu, and a start menu that fits

- The user's start menu ran off the bottom of the screen. With the Pokédex and the Pokégear it
  had nine entries (POKéDEX, DEXNAV, POKéMON, BAG, POKéGEAR, the player, SAVE, OPTION, EXIT);
  the window starts on the second tile row and takes two rows an entry plus its frame, so the
  20-row screen has room for eight, and EXIT and the frame's bottom were off it. The DexNav
  entry (D13) was the ninth. The user asked for Emerald Imperium's L button menu instead, "with
  all the options available without having to go in the bag".
- What Imperium's L menu has, from its guides and changelog: the DexNav, the Infinite Repel and
  the PokéVial are "accessed by pressing the L button", and it can "access your PC instantly,
  change the time of day, set yourself to always run, or change the Pokémon you have following
  you" ([Retro Dodo](https://retrododo.com/pokemon-emerald-imperium-cheats/)); 1.3 made the whole
  PC available from the L menu's "PC" and added a NuzVial, and in 1.2 L or START cancels a
  DexNav search "which will not break a DexNav chain"
  ([changelog](https://pokemonemeraldimperium.com/changelog/)); its Stat Editor edits EVs and
  IVs, and with Minimal Grinding on it "can only change IVs" and "cannot change EVs"
  ([features](https://pokemonemeraldimperium.com/features/)). The user's screenshot showed
  PokéVial, PC, DexNav, Time and Stats, then Repel, Follower and Auto Run in green. As with
  everything from Imperium (D2), this is our own code.
- **L in the field** opens it (`src/l_menu.c`): on the left POKéVIAL, PC, DEXNAV, TIME, STATS,
  then the REPEL, FOLLOWER and AUTO RUN switches with ON or OFF, green when on; at the top right
  the clock and the time of day. B or L closes it. It opens once you have a Pokémon, not where
  the start menu is cut down (link rooms, the Safari Zone, the Bug Catching Contest, the Battle
  Pike and Pyramid), and not with BUTTON MODE L=A, where L is the A button.
  - POKéVIAL heals the party like the key item (fainted Pokémon stay fainted in a Nuzlocke, so
    there is no separate NuzVial).
  - PC is a Pokémon Center's whole PC (SOMEONE'S PC, the player's PC with item storage,
    CHALLENGES, and the HALL OF FAME after the League), with nothing on the map to light up.
  - DEXNAV is the DexNav, gone from the start menu; B in it comes back to the L menu, and on a
    map without wild Pokémon it says so. Pressing L during a search ends it, as START does, and
    keeps the DexNav chain.
  - TIME asks for MORNING, DAY, EVENING or NIGHT and moves the clock **forward** to 8:00 AM,
    12:00 PM, 6:30 PM or 8:00 PM: the same day if that time is still ahead, otherwise the next
    day. Those are the times each one shows best (`UpdateTimeOfDay` blends night into morning
    until 8:00, and the hour before evening and night). The clock never goes back, so berry
    trees and daily events only see time pass; Imperium documents its time changer no further.
    Choosing the time of day it already is changes nothing. Then the map reloads where the player
    stands (as the debug menu's time change does), surfing or biking as before, so its light,
    the Pokémon seen by day or by night (`FLAG_DAY_POKEMON` / `FLAG_NIGHT_POKEMON`) and the
    time-based people and events follow at once. The DexNav chain is kept; anything else a map
    reset resets on re-entering (moved boulders, temporary flags) resets too.
  - STATS is the Training Kit's menu, now NATURE, ABILITY and **IVs & EVs**, Imperium's Stat
    Editor: a window with the IV, EV and stat of each of the six, the nature's raised and
    lowered stats in red and blue, Hidden Power's type, and the EVs used. The d-pad picks an IV
    or an EV; A changes it (UP/DOWN by 1, going round, LEFT/RIGHT by 10), A keeps it, B puts it
    back; START sets every IV to 31; B leaves. EVs stay within 252 a stat and 510 in all, and
    editing an IV clears that stat's Hyper Training. With Minimal Grinding on (the default, D3)
    every Pokémon battles at 31 IVs and 0 EVs anyway, so, as in Imperium, the EVs are locked
    (grayed, LEFT/RIGHT stay on the IVs) and the IVs only set Hidden Power's type. Like the
    other tools it is there from the start (D10); the Training Kit in the bag opens the same menu.
  - REPEL is the Infinite Repel, FOLLOWER the setting of the party menu's FOLLOWER (and the
    options' follower setting), AUTO RUN that of OPTION > AUTORUN.
- **The start menu** keeps Heart & Soul's entries without DEXNAV: eight at most, which fit.
- Not included: a Rare Candy entry (Imperium keeps its Infinite Candy in the bag too).
- Save compatibility: nothing new is saved. Saves from older builds get the key items when
  they are loaded (D10), so their L menu is complete.
- Evidence: `l_menu` (eight start menu entries without DEXNAV; the L menu's entries and
  switches, B and L close it, no menu with L=A; the PokéVial heals and cures; the PC opens the
  Pokémon Storage System; AUTO RUN changes walking into running), `l_menu_time` (the clock
  moves forward, the same day or the next; light, time of day and day/night Pokémon follow; the
  DexNav chain is kept; still surfing on the same tile), `stat_editor` (with Minimal Grinding off:
  IV and EV changes in the stats, going round, undo, the 510 limit), `stat_editor_mgm` (EVs
  locked, the IVs in battle), `dexnav` (L ends a search and keeps the chain; every DexNav test
  opens it from the L menu), `old_save_test.sh` (the L menu complete on a Heart & Soul save).

## D35. Emerald Imperium's abilities and movesets

- The user asked to "mirror the movesets and abilities from emerald imperium". Imperium takes its
  Pokémon data from Radical Red: its documentation sends players to the Radical Red dex for
  Pokémon information, and its list of changes is written as "Differences from Radical Red", "as
  this game is heavily inspired by it" ([New Mega Evolutions](https://pokemonemeraldimperium.com/new-mega-evolutions/)).
  So Crystal Imperium mirrors Radical Red's abilities and moves, with Imperium's documented
  changes on top.
- **Source.** The Radical Red dex's data file ([JwowSquared/Radical-Red-Pokedex](https://github.com/JwowSquared/Radical-Red-Pokedex)
  `data.js`, SHA-256 `04c9dc94…5596df9`), read by `tools/crystal_imperium/imperium_species.py`.
  The file isn't kept in this repository; what the script writes is. It is design data (D2):
  which abilities and moves each species has, not code or assets.
- **What it writes**, for the 1,244 species and forms both games have:
  - every species' three ability slots (`species_info/imperium_abilities.h`: 491 species whose
    abilities change; the others already had Radical Red's ability for each slot, or their
    lists differ only where the game falls back to another slot, as a Mega's empty slots do);
  - the level-up moves, evolution moves included (`level_up_learnsets/imperium.h`: 1,098
    learnsets; Heart & Soul's Gen 7 ones, `gen_7.h`, for the rest);
  - the Egg Moves (`egg_moves_imperium.h`: 415 lists).
  `P_IMPERIUM_SPECIES_DATA` in `include/config/pokemon.h` switches them on. The ability lines
  override the species table at its end (`-Woverride-init` is silenced for it). ROM: +896 bytes.
- The data file lists the hidden ability first: Bulbasaur is "Chlorophyll, Overgrow, —" and
  Geodude "Sand Veil, Rock Head, Sturdy". Every species checked fits [hidden, 1st, 2nd].
- **Radical Red's own content isn't in this engine:**
  - 11 abilities it made (Feline Prowess, Striker, Fatal Precision, Sage Power, Bone Zone, Bull
    Rush, Quill Rush, Self Sufficient, Blazing Soul, Phoenix Down, Bad Company). That slot keeps
    one of the species' Heart & Soul abilities not already in its list: Typhlosion has Flash
    Fire and Blaze for Radical Red's Flash Fire and Blazing Soul.
  - 6 moves it made (Aqua Fang, Draco Barrage, Soul Robbery, Forbidden Spell, Sonic Slash, Dark
    Hole) are left out of the learnsets. Since 0.13.0 the engine has them (D39).
  - 43 forms it made (its Sevii forms, the Megas of Butterfree, Machamp, Kingler, Lapras, Snorlax
    and other Gigantamax Pokémon, Primal Dialga, Surfing and Flying Pikachu, Chillet).
  - Names cut to its 12 letters are matched to the full ones: Disarm Cry (Disarming Voice),
    Drain Kiss, Crafty Guard, Flower Guard, Prism Laser, Inferno Parade, Neutralize Gas,
    Wandering Soul, WaterCompaction, ThermalExchange, Electromrphosis, SupremeOverlord,
    OrichalcumPulse. Abilities that share a Radical Red ID work the same there, so they map to
    the official one; its Valiant Shield ("Raises Defense on entry") is Dauntless Shield.
- **Imperium's changes**, from its list: Torchic, Combusken and Blaziken get Blaze and Early
  Bird without Speed Boost (its third, Striker, isn't in the engine, so they have no hidden
  ability rather than Speed Boost); Blaziken learns Thunderous Kick at 64; Latios and Latias
  learn Memento and Healing Wish at 71, not 61; Urshifu learns Wicked Blow or Surging Strikes
  on evolving; Alolan Marowak has Battle Armor instead of Bone Zone. Its TM-only changes
  (Jirachi's Moonblast, Dragapult's Shadow Claw, Galarian Moltres's Trick Room) don't apply
  (they do since 0.13.0, D39, as does "Dusclops/Dusknoir get access to Amnesia", missed here).
- **Kept:** an ability a form change needs stays (`form_change_tables.h`). Radical Red gives
  Silvally Battle Armor, but here its Memories change its type only with RKS System, so all
  Silvally keep their abilities. Gigantamax and cosmetic forms that had their base form's
  abilities and level-up moves follow its new ones (Unown's letters, Vivillon's patterns).
- **Not mirrored:** TM and tutor compatibility (Crystal Imperium's TM list is its own, D22, and
  Radical Red's has 128 TMs; mirrored since 0.13.0, D39), base stats and types (not asked for). Engine limits: a level-up
  list holds 40 moves and an Egg Move list 19 (the Day-Care's buffer), so Farfetch'd keeps 19 of
  its 20 Egg Moves.
- **Trainers.** Fifty trainer Pokémon had an ability their species no longer has, which the
  engine would silently swap for slot 0 (`validate.py` checks this). Each now has the ability in
  the slot its old one had, which is what happens to a player's Pokémon: Falkner's Pidgey goes
  from Big Pecks to No Guard, the rival's Golbat from Inner Focus to Infiltrator, Blaine's
  postgame Blaziken from Speed Boost to Blaze. `boss_teams.py` has the same changes. Bosses list
  their moves; other trainers get the last moves of their new learnsets.
- **Save compatibility.** A Pokémon keeps its ability slot, so a saved Pokémon has its species'
  new ability for that slot (a Pidgey with Keen Eye now has Frisk). Known moves stay, and new
  ones come from the new learnsets.
- Evidence: the built ROM's species table read back (Pidgey "Frisk, —, No Guard" with Radical
  Red's moves; Cyndaquil "Blaze, —, Flash Fire" with Fury Swipes first among its Egg Moves);
  `validate.py`; `imperium_species.py --check`; the whole play-test suite on both emulators.

## D36. A TM clerk in every Poké Mart

- The user asked to "add someone to every pokemart that you can buy progressive tms from".
  Emerald Imperium sells TMs at $100 from vendors in its towns, stronger ones further on: seven
  in Dewford after its first Gym, then the Mauville Game Corner's 23, then Lavaridge's Ice Beam,
  Thunderbolt, Flamethrower, Sludge Bomb, Energy Ball, Dark Pulse and Hyper Voice after its third
  Gym ([PokéMarts guide](https://pokemonemeraldimperium.com/pokemarts-guide/)).
- **Where.** Every Poké Mart (Cherrygrove, Violet, Azalea, Ecruteak, Olivine, Blackthorn,
  Viridian, Pewter, Cerulean, Vermilion, Lavender, Saffron, Fuchsia) has a TM clerk at (2,2),
  behind the counter next to the clerk, talked to across it. The Indigo Plateau's shop has one at
  (11,10). The Goldenrod Dept. Store 5F and Celadon's 3F TM counter sell the same lists. Violet's
  clerk (D22) now sells them too, from the start, and still gives its four TMs once with the
  Zephyr Badge. Mahogany's shop has no clerk: it sells evolution items and has no free spot
  behind its counter.
- **What.** One shop (`EventScript_TMShop`, written by `tools/crystal_imperium/tm_list.py`)
  with a list for every badge count. From the start come status moves and moves below 70 power,
  with Heart & Soul's own 5F stock (71 TMs). Then one band a badge: multi-hit and variable-power
  moves and 70–79 power with the 1st (115); strong setup and hazard moves and 80–89 with the 2nd
  (155); 90–99 with the 3rd, as Imperium's Lavaridge vendor (173); then 100–109 (178),
  110–119 (181), 120–129 (191), 130 and more (196), and Explosion and Misty Explosion with the
  8th (all 198). That is earlier than D22's tiers (3, 6 and 8 badges): Thunderbolt at 3 badges
  instead of 6, Close Combat at 6 instead of 8. ¥100 each, as before.
- A TM the player has shows OWNED instead of its price. SOLD OUT ran into the longest names
  ("TM01 FOCUS PUNCH").
- Evidence: `tm_clerks` (Cherrygrove with no badges 71, Azalea with two 155, Pewter with eight
  198 and a purchase, Indigo Plateau 198), `tm_shop` (Goldenrod 5F: 71, 115, 173, 191, 198, the
  badge count deciding), `tm_clerk` (Violet: 71 before the badge, then the gift once and 115).

## D37. Emerald Imperium's cheat codes at the NES

- The user asked for Imperium's codes: "I could also punch codes into the nes and get things
  like MEGA gets you all the mega stones". In Emerald Imperium, "cheat codes can be entered by
  talking to the GameCube in either the Player's house or the Rival's house": DexAll, CaughtAll,
  EZCatch, Mega, ShinyS, MaxMoney, Mono and ShinyR, with the aliases Dxa, Cal, Ezc, Shs, Mmy and
  Shr ([Imperium docs](https://drive.google.com/drive/folders/1auRPBg8Ts50NByIskMy6b2XHnmNqIKtV),
  "Cheat Codes"). Imperium's code isn't used (D2); the codes and what they do come from its docs.
- **Where.** The NES in the player's room in New Bark Town (`data/scripts/cheat_codes.inc`):
  "{PLAYER} turned on the NES. Enter a code?" YES opens the pokeemerald-expansion code naming
  screen (`special EnterCode`, 11 characters). NO keeps the NES's old line ("…Okay! It's time
  to go!"). Case and spaces don't matter; anything else is "Nothing happened…".
- **The codes** (`src/cheat_codes.c`):
  - **MEGA**: the Mega Ring if the player hasn't got it (from the third badge, the Goldenrod Mega
    Specialist then goes straight to his shop), and one of each of the 47 Mega Stones whose Megas
    this game has (D9: the Specialist's full stock), only those not already in the Bag or the PC.
    If the Bag and PC are full, it says how many didn't fit, and entering MEGA again brings them.
  - **MAXMONEY** / MMY: money to the maximum (¥9,999,999).
  - **CAUGHTALL** / CAL: every Pokémon seen and caught in the Pokédex, and the National Pokédex
    on, so they show.
  - **EZCATCH** / EZC: switches EASY CATCH (D12's option, on by default) off or on.
  - **SHINYS** / SHS: switches shiny starters. PROF. ELM's three Poké Balls then all hold shiny
    Pokémon (the starter preview's shiny roll, `ScrCmd_showmonpic`, always comes up shiny).
    Before the first Pokémon only.
  - **MONO**: a menu of 15 types (or OFF). PROF. ELM's three Poké Balls then hold that type's
    Pokémon, Imperium's lists from its 1.3 changelog: Fighting Mankey, Machop, Timburr; Flying
    Hoppip, Fletchling, Rookidee; Poison Budew, Venipede, Koffing; Ground Trapinch, Geodude,
    Wooper (Imperium has Tympole, which is Water only until Palpitoad here); Rock Rolycoly, Alolan Geodude, Nacli; Bug Grubbin, Blipbug, Scatterbug; Ghost
    Gastly, Litwick, Duskull; Steel Tinkatink, Honedge, Klink; Electric Pichu, Shinx, Mareep;
    Psychic Hatenna, Solosis, Gothita; Ice Snover, Swinub, Spheal; Dragon Bagon, Gible, Dratini;
    Dark Pawniard, Galarian Zigzagoon, Sandile; Normal Whismur, Lillipup, Smoliv; Fairy Cottonee,
    Igglybuff, Impidimp (Fire, Water and Grass have no list there either). Before the first
    Pokémon only. The rival keeps the Johto starters.
  - **SHINYR** / SHR: the roaming Pokémon shiny, those roaming now and those to come.
  - **DEXALL** / DXA: Imperium's switch for showing every Pokémon in the DexNav. Here the DexNav
    always does (D18), so the NES says so.
- Imperium's other two default codes, SO2Toxic (the care packages, D16) and Woyaopp (Rare
  Candies: the Rare Candy Box, D10), are on from the start here too.
- **Saves.** `FLAG_CODE_SHINY_STARTERS` and `FLAG_CODE_SHINY_ROAMERS` (extended content flags
  84 and 85) and `VAR_MONO_STARTER_TYPE` (0x40FB), all unreferenced before.
- **Bag space.** The 47 Mega Stones take 47 of the items pocket's 236 slots, beside the care
  packages' 172 kinds (D16). Like the packages, MEGA leaves 20 of them free for the story's gifts
  while the PC (50 slots) has room, and nothing is lost: what fits nowhere comes with the next MEGA.
- Evidence: `cheat_codes` (types each code on the keyboard: a wrong code, MEGA twice (47 stones,
  then none), MMY, CAL, EZCATCH and EZC, SHINYR, DXA, NO; MONO and SHS refused once the player has a
  Pokémon; then SHINYS and MONO with Dragon, and PROF. ELM's middle Poké Ball holds a shiny Gible).

## D38. Faster battles

- The user: "the battling feels a little clunky, can you speed it up a bit". Emerald Imperium
  documents no battle-speed feature (its text one is "Hold R to speed through NPC dialogue",
  [Imperium features](https://pokemonemeraldimperium.com/features/)). The Archipelago Emerald
  build is a precedent for the kind of change: battle pauses "shorter by 62.5%" and the opening
  slide "at double speed"
  ([Archipelago rom changes](https://git.hollymcfarland.com/monorail/Archipelago/src/commit/e33ea0147bd19bcf4b03bb2cd25ff1d18aaa89f8/worlds/pokemon_emerald/docs/rom%20changes.md)).
- **Measured first** (the new `trace` command of `tools/emurun` prints the battle's main function,
  each battler's controller and the battle script's position on every frame they change). In
  0.12.0, a trainer battle against one Lv 4 Pokémon, pressing A whenever the game waited, took
  1,518 frames (25 s), 704 of them before the first menu:
  - FAST INTRO (Heart & Soul's option to skip the slide-in) was off: 152 frames of slide.
  - The Pokémon sent out plays its own animation and the intro waits for it: TYPHLOSION's took
    129 frames. The intro also waited for its cry to end.
  - The battle script ran one command a frame: about 15% of a turn was bookkeeping with nothing
    on screen.
  - A hit Pokémon blinks for 32 frames; after a knockout the battle waits for the winner's own
    animation (68 frames for TYPHLOSION); a trainer slides in at 2 pixels a frame.
  - FAST BATTLES (on by default) already skipped the pauses after messages, but a message ending
    in a prompt ("fainted!", "gained Exp. Points!", "You got ¥… for winning!", "You are challenged
    by…") stopped the battle until a button was pressed.
- **Always** (no visual change; `src/battle_main.c`, `src/battle_controllers.c` and the player's and
  opponent's controllers):
  - The battle script's commands run back to back while each finishes at once. A command that
    waits (for a controller, a message or a pause) still ends the frame, as does one that ends the
    action, the turn or the battle.
  - The intro and the switch-ins no longer wait for the cry to end: a task turns the music back up
    when it does, as Game Freak's code already did for the player's switch-ins.
  - **The battle's menus.** The game stood still while it drew them. Measured with the play-time
    counter (it counts the frames whose work the main loop finished) and a CPU profiler added to
    `tools/emurun` for this (`profile`, `profile.py`): 8 frames after FIGHT, 4 before each turn's
    action menu, 5 after B from the moves. The BW battle UI's action box and move boxes were
    copied pixel by pixel (`BlitBitmapRect4Bit`, 40% of the time after FIGHT), and the moves'
    screen decompressed the whole text box tilemap each time. Rectangles of whole tiles are now
    copied a tile row (8 pixels, one word) at a time (`src/blit.c`, for every screen): the same
    pixels as Game Freak's routine on 2,000,000 random rectangles, and the menus' screenshots are
    identical. The move box copies the tilemap from an uncompressed copy (4 KB of ROM). The moves
    take input 5 frames after FIGHT (10 before), each turn's action menu comes 4 frames sooner,
    B from the moves pauses 1 frame; what remains is printing the moves' names and PP.
- **With FAST BATTLES on** (`IsFastBattleOn`; HnS's option, on by default):
  - The intro (Poké Balls thrown, Pokémon sent out), battle animations (moves, stat changes,
    status, Poké Balls) and the Pokémon's own animations (sent out, after a knockout) play at
    double speed: `BattleMainCB2` runs a second step of the battle, its sprites and its tasks,
    without the frame's button presses (the rest of the frame, its text printers and tasks, still
    gets them: D40). Not while the player chooses an action: a Pokémon's own
    animation can outlast its switch-in, and the menu (its cursor, the bouncing health box, the
    input handler) keeps the usual speed. Text prints at the TEXT SPEED chosen, and palettes fade
    at their usual speed: a hardware fade counts its end in a one-bit field cleared at VBlank,
    and a second `UpdatePaletteFade` in a frame wrapped it to zero, so the fade never ended (the
    first build hung on Tailwind's sky; `falkner` found it).
  - A hit Pokémon blinks twice instead of four times (16 frames), the HP bar moves two steps a
    frame, and trainers slide in and away twice as fast.
  - **From choosing a move to the Pokémon moving** (the user's follow-up: "It's more so when you
    pick a move and the Pokemon move that it's more clunky in battle"). "X used Y!" is printed
    at once instead of letter by letter, and stays up during the animation (`src/battle_message.c`,
    `STRINGID_USEDMOVE` only; it fits the box's two lines, so it never has a prompt to wait at).
    A move's animation no longer waits for the last sound effect to end (`IsBattleSEPlaying`, up to
    30 steps in 0.12.0, typically between one Pokémon's hit and the next one's move); the
    animation's own sounds take over. Nor does an animation's end (`Cmd_end`, `src/battle_anim.c`,
    which waited up to 90 frames for the animation's last sound): with its pictures at double
    speed, a stat change's sound outlasted its arrows by 27 frames, and the battle waited for it
    before "fell!". The sound plays on under the next message; contests keep the wait. Traced on mGBA (TYPHLOSION's Swift against Whitney's first
    Pokémon, which used Charm): from the frame the move is chosen to its animation, 15 frames
    (0.12.0: 46); from the opponent's "used" message to its animation, 7 frames (0.12.0: 45).
    The 15 left were the turn's own steps (each battler's choice confirmed, the turn order, the
    move's first checks), a frame or so each: D40 runs them in 3.
  - A battle message's prompt goes on by itself after 49 frames (`NUM_FRAMES_AUTO_SCROLL_DELAY`);
    A or B goes on at once, as before. A trainer's words (win and lose texts, the speeches before
    a last Pokémon) still wait for the player, and so do the Bag and party menus opened from the
    battle (`gTextFlags.autoContinuePrompt`, battle screen only).
  - The option's descriptions say so ("No pauses after messages, and battle animations at double
    speed").
- **FAST INTRO** is on for a new game. Saves from before 0.13.0 get FAST INTRO and FAST BATTLES
  turned on once (save version 6, `src/save.c`); both can be turned off again in START > OPTION >
  BATTLE.
- Link and recorded battles keep Game Freak's timing (one command a frame, single steps, cries
  waited for, prompts waiting), as does pokeemerald-expansion's test runner.
- Not changed: sounds and cries play in real time; every other message prints at the TEXT SPEED
  chosen (FASTER is nearly instant). The opponent's AI (D20) thinks once a turn, before the
  action menu: about 9 frames against a trainer with six Pokémon, most of it working out the
  damage of each move its party could use (pokeemerald-expansion's design; the profile shows no
  single slow step to cut). BATTLE SCENE OFF (START > OPTION, first page) skips move animations
  altogether.
- Results (mGBA): the trainer battle above takes 968 frames, 36% less (first menu after 440
  frames, 0.12.0: 704); with no button pressed, the battle now runs from "Try Battle" to the
  trainer's defeat text by itself. A turn against Whitney (Swift, then Charm, back to the action
  menu) takes 254 frames from choosing the move (0.12.0: 489); Charm's stat drop takes 46 of
  them (74 while its animation still waited for its sound).
- Evidence: `battle_speed` (new game defaults; the first menu with no button pressed; the battle
  runs to the defeat text, which waits for A; with FAST BATTLES off the intro's message waits
  again), `battle_anims` (every move from 1 to the last, Z-Moves and Max Moves aside, used once at
  double speed: each gets back to the action menu or ends the battle), the old-save test (both
  options on after Continue), and the rest of the play tests at the new speed.
- **Tests.** The harness's soft walks let go of the d-pad when a battle starts (they kept walking
  into the battle's menu once the intro stopped waiting for A), and tests that pressed A through
  the intro wait for the action menu instead (`wait_action_menu`).

## D39. Emerald Imperium's and Radical Red's move pools

- The user: "Also make the move pool and learnsets for the Pokemon like emerald imperium and
  radical red". Level-up moves and Egg Moves are Radical Red's since 0.11.0 (D35). The rest of a
  move pool is the TM and tutor moves a species learns, and Radical Red has six moves of its own.
  Emerald Imperium sends players to the Radical Red dex for Pokémon information
  ([Imperium documentation](https://pokemonemeraldimperium.com/documentation/)), has "Move-tutor
  moves converted to TMs" ([Imperium features](https://pokemonemeraldimperium.com/features/)),
  and lists its differences from Radical Red
  ([New Mega Evolutions](https://pokemonemeraldimperium.com/new-mega-evolutions/)).
- **TM and tutor compatibility.** `imperium_species.py` also writes
  `src/data/pokemon/imperium_teachables.json`: the 182 moves Radical Red teaches by TM or tutor,
  and the ones each species learns there, for 1,100 teachable learnsets. As for level-up moves, a
  list takes the data of the first species using it that Radical Red has: Deoxys-Normal's list is
  Radical Red's "Deoxys", and Terapagos's (shared by its forms) the Terastal Form's, the only one
  Radical Red has; only white-striped Basculin isn't in it. A form whose Radical Red list differs
  from its base form's needs a list of its own: female Basculegion has one now (Radical Red
  teaches it five moves fewer), and `make_teachables.py` gives a form without official data its
  base species'. The forms that share a list but that Radical Red teaches a few more moves (Rotom's
  appliance forms: Hydro Pump for Rotom-Wash...; Origin Dialga and Palkia; the Cosplay Pikachus)
  can't be obtained in this game, where nothing gives their items; `--report` lists them.
  `make_teachables.py`, which writes the teachable learnsets at build time, applies it with
  `P_IMPERIUM_SPECIES_DATA`:
  - For a move Radical Red teaches by TM or tutor, Radical Red decides. TYPHLOSION gains Aura
    Sphere and Mystical Fire, and loses Body Slam, Fire Fang, Iron Head, Shadow Ball and Zen
    Headbutt, which Scarlet and Violet's TMs teach it (and Gen 3's tutors Body Slam).
  - The other TMs and tutor moves (61: Hyper Beam, Frustration, Heart & Soul's tutors...) follow
    the official rule as before: a species learns one if it does in any official game.
  - An HM move stays teachable to a species that learns it in an official game too: Radical Red's
    HM lists leave out 136 such cases, mostly newer forms (Alolan Geodude's Rock Smash, Galarian
    Slowking's Strength). Using HMs in the field doesn't depend on it (D23).
  - Radical Red's TM and tutor moves that are neither TMs nor tutor moves here become tutor moves,
    which the move relearner teaches: Celebrate, Cosmic Power, Dark Hole, Draco Barrage, Hone
    Claws, Toxic Spikes and Uproar (67 tutor moves, 60 before). The tutor list is now written
    for the build's own TM list (`--build`, as the teachable learnsets are).
  - **Dark Hole and Draco Barrage wait for the postgame.** They are Imperium's TM161 ("Post game")
    and TM171 ("Post game Mart at the Battle Frontier"), per its
    [TM guide](https://pokemonemeraldimperium.com/all-tms-and-hms-location-guide/), and the
    relearner offers every tutor move from the start: a 100-power move with a 40% chance of sleep
    would come a whole game early. The relearner lists them once `FLAG_SYS_GAME_CLEAR` is set
    (the first Hall of Fame). As tutor moves rather than TMs they keep the TM numbers of D22. The
    Pokémon that learn them by level (Darkrai 81, Hydreigon 85...) do so at any time.
  - Imperium's changes: Jirachi learns Moonblast, Dragapult Shadow Claw and Galarian Moltres
    Trick Room. "Dusclops/Dusknoir get access to Amnesia": no TM or tutor teaches Amnesia in
    either game, so it is a level 1 move, which the relearner teaches at any time.
  - 1,059 of the 1,100 teachable learnsets change; 60,692 entries become 60,996.
- **Radical Red's own moves**, after the official ones (`include/constants/moves.h`: no saved
  move number changes, and Metronome, which calls official moves only, doesn't call them), with
  the dex's type, power, accuracy and PP and the effects its change lists give
  ([PokéPorto: all Pokémon changes](https://www.pokeporto.com/pokemon-radical-red-all-pokemon-changes/),
  [PokéPorto: changelog](https://www.pokeporto.com/pokemon-radical-red-changelog/)):
  - **Aqua Fang**: Water, physical, 80, 100%, 10 PP, a biting move (Strong Jaw). Level-up:
    Gyarados 30, Basculin 42, Feraligatr 45, Bruxish 48, Huntail 50, Drednaw 72, Sharpedo 75.
  - **Dark Hole**: Dark, special, 100, 100%, 5 PP, a 40% chance of sleep, through Substitute.
    Darkrai 81, and a Radical Red tutor move (58 species).
  - **Soul Robbery**: Psychic, special, 100, 100%, 5 PP; steals the target's stat boosts, then
    attacks (Spectral Thief's effect). Mewtwo 100.
  - **Sonic Slash**: Flying, physical, 100%, 10 PP; 140 power at 3 times the target's Speed or
    more, 120 at twice, 80 below (`EFFECT_SONIC_SLASH`). Ninjask 54.
  - **Draco Barrage**: Dragon, 100, 100%, 5 PP; physical or special, whichever of the user's
    Attack and Sp. Atk is higher (as Photon Geyser); hits Fairy-types (neutral damage); recoil of
    a third of the damage dealt (Radical Red 3.0). Tropius 52, Kommo-o and Guzzlord 77, Hydreigon
    85, and a Radical Red TM (111 species), a tutor move here.
  - **Forbidden Spell**: Dark, status; calls Shell Smash, Healing Wish, Dark Hole, Tail Glow, Roar
    of Time, Quiver Dance, No Retreat or Soul Robbery, one time in eight each
    (`EFFECT_FORBIDDEN_SPELL`, through Metronome's code). Unown 34, Chimecho 50. 1 PP, as in the
    dex; the change list that names the eight moves gave it 5.
  - Each borrows an official move's animation: Fishious Rend, Dark Void, Spectral Thief, Aerial
    Ace, Draco Meteor and Nasty Plot. Dark Void's hits both foes: Dark Hole plays a copy for its
    target alone, the user's partner too, with Dark Void's black holes (`gBattleAnimMove_DarkHole`;
    the 0.13.0 reviews found it showed Destiny Bond's white shadows and slid the other foe away in a
    double battle, then that a partner it was aimed at got no black hole).
  - Imperium hasn't added Draco Barrage and Soul Robbery ("not yet added", its list); Radical Red
    has them, and the user asked for both games' move pools.
  - With them, and "Soupercell Slam" matched to Supercell Slam (Radical Red's spelling), no Radical
    Red move is left out any more: 18 more level-up moves (Feraligatr's Aqua Fang...).
- **Fix: the move relearner listed at most 60 moves** (`MAX_RELEARNER_MOVES`, set upstream so Mew
  could see all of Emerald's TMs), and its lists didn't stop there. TM MOVES lists every TM and
  HM in the Bag the Pokémon learns: up to 206 here (D22), so with most TMs bought, opening it for
  MEW (or any Pokémon that learns more than 60 of them) overran the list. The build before this
  fix stopped on an "INVALID MOVE" assertion in `move_pools`. The limit is 250, checked against
  the number of machines when compiling, and every list stops at it.
- Trainers keep their moves. Five boss moves aren't teachable to a player's Pokémon of the same
  species any more: Chuck's Primeape's Drain Punch (his three versions) and the rival's
  Meganium's Earth Power (two battles). Trainer Pokémon can know any move; `validate.py` checks
  boss moves against the official games, as before.
- Players' Pokémon keep the moves they know. ROM: +1,792 bytes (with the relearner fix).
- Evidence: `move_pools` (new), on mGBA and VBA-M. In the party menu's relearner, with every TM
  and HM in the Bag: TYPHLOSION's TM list has Aura Sphere and Mystical Fire and not Shadow Ball,
  its tutor list Blast Burn and not Body Slam; MEW's TM list has all 206 TMs and HMs, its tutor
  list 61 moves, then 63 with Dark Hole and Draco Barrage once the game is cleared; DRAGONITE
  then learns Draco Barrage from its tutor list, and in battle knocks out Whitney's CLEFAIRY (99
  HP, Eviolite) with it in one hit and takes 32 HP of recoil. A special Draco Barrage would do
  79–93 damage, and without the Fairy rule none. `battle_anims` uses the six new moves with the
  rest. `hm_field_moves`: MAGIKARP's party menu now has LEARN MOVES (Celebrate) above FLY.
  `imperium_species.py --check`.

## D40. A chosen move starts at once

- The user, again: "It's more so when you pick a move and the Pokemon move that it's more clunky
  in battle". After D38, 15 frames still passed between A on a move and its animation, and 10
  between one Pokémon's HP bar and the next one's "used" message, with nothing changing on
  screen. Three sweeps measured where each frame went (traces of the battle's functions, the
  script, the controllers and the play-time counter, a screenshot a frame, CPU profiles; TYPHLOSION's
  Swift against Whitney's lead, which used Charm), and the animation sweep tried its two changes
  on patched copies of the ROM before anything was built.
- **The bookkeeping shares frames** (always, outside link and recorded battles and the expansion's
  test runner: `IsBattleBatchOn`, the gate D38's batching already had; nothing is drawn
  differently, the same steps run in the same order):
  - The choice is confirmed in the frame it is read (`HandleTurnActionSelectionState` falls through
    its three states; each took a frame), then the turn order is set and the first action starts
    in that frame. A Quick Claw or Quick Draw message, a gimmick (Mega Evolution, Dynamax,
    Terastallization) or a Focus Punch-like move's script ends it there, where Game Freak's frame
    ended.
  - The turn's actions run on while each one moves on at once (`RunTurnActionsFunctions`, at most 8
    a frame): a move's script ends, the next battler's move is set up, and its checks run up to its
    "used" message, which gets the next frame to itself (printing it is the most expensive step of
    a move, about 40% of a frame). A controller at work, a battle script started (a fainted
    Pokémon, a gimmick, the end of the turn) or an action that waits ends the frame, as before.
    The turn's state is reset in the frame its last action ends (`HandleEndTurn_ContinueBattle`);
    the end of the turn's effects (`BattleTurnPassed`) has the next frame.
  - Commands that work through a list of their own (the checks before a move, a move's additional
    effects, the steps after it: `attackcanceler`, `setpreattackadditionaleffect`,
    `setadditionaleffects`, `moveend`) return after some of its entries and are called again; an
    entry done now counts as progress in D38's batching, like a command that moved on.
  - Commands that every controller finishes in the call (a write to the party, a sprite shown or
    hidden, a sound effect, the end of the action menu's bounce) are handled at once
    (`TryRunInstantControllerCommands`), instead of ending the frame for the controllers' turn.
  - An animation's background is cleared in one go: Game Freak's fill went entry by entry, about a
    frame of CPU, and the frame it fell in (every stat change) was dropped.
- **With FAST BATTLES on:**
  - "X used Y!", printed whole (D38), is done in the frame it's printed; the move's animation
    starts in the frame its command arrives and the controller is done in the frame it ends. A
    Pokémon behind a substitute still waits for it to move aside.
  - An animation's palette fades (a background change, a colour blend, a status's pulse) run at
    the animations' double speed: `BattleMainCB2` gives the fade a second step
    (`UpdatePaletteFadeSecondStep`). Normal and hardware fades only, and a hardware fade's finish
    is left to VBlank (D38's Tailwind hang). This also fixes a bug of D38's mixed speeds: an
    animation's second fade could be refused while its first, slower one still ran, so Ice Shard
    left the foe tinted blue (Shadow Force and Magical Torque left background palettes changed).
  - The animation doesn't wait for a cry to end (Growl 119 frames, now 26; Parting Shot, Disarming
    Voice): the cry plays on under the next message, with the music kept down until it ends (the
    animation's end turned it back up at once, under the cry, until the review found it:
    `Cmd_end` leaves it to the cry's own task). Contests keep the wait.
  - A battle message's prompt goes on after 24 frames, not 49 ("fainted!", "gained Exp. Points!"),
    and the Exp. bar fills as its sound starts (it waited 13 frames). The sound still plays at least
    8 frames, both rises of its chirp: a gain under 1/16 of a level, or none at the level cap, fills
    the bar at once, and stopping the sound there cut it to a click until the review found it.
  - A Pokémon sent out during the battle plays at double speed, as the intro already did (D38):
    the party's balls before a trainer's next Pokémon (47 frames, not 94), the ball (33, not 64)
    and the health box sliding in (12, not 23) (`BtlController_IsSwitchInPlaying` in
    `IsBattleAnimationPlaying`). The Pokémon's own animation was already at double speed.
- **Fixed by the review** (from D38, with FAST BATTLES on):
  - The second step took the frame's button presses away from the text printers and tasks too, not
    only from its own run of the battle: A or B didn't answer the intro's message, which waited for
    its auto-continue, and QUICK RUN with B (START > OPTION > BATTLE) never ran from a wild battle,
    since the prompt went on by itself after B was let go. The second step now runs without the
    presses and gives them back for the rest of the frame (`BattleMainCB2`), so the battle and the
    text printers each see a press once, as in Game Freak's frame.
  - A prompt's auto-continue counted the printer's runs, and at TEXT SPEED FASTER the printers run
    up to 12 times a frame: "fainted!" or "gained Exp. Points!" stayed up 2 frames. It counts
    frames now (`TextPrinterWaitWithDownArrow`).
  - `battle_prompts` (new) checks both: it fails on the first 0.13.0 build and passes on this one.
- **Results** (mGBA, the same turn as D38): from A on Swift to its animation, 3 frames (D38: 15;
  0.12.0: 46); from the end of Swift's HP bar to Charm's animation, 3 frames (D38: 16); the turn,
  from A to the next action menu, 211 frames (D38: 253; 0.12.0: 489). With FAST BATTLES off the
  same turn takes 487 frames (D38: 520). A knockout of Whitney's lead to the next action menu, her
  next Pokémon sent out on the way: 395 frames (D38: 585; "fainted!" and "gained Exp. Points!" 57 and
  59 frames instead of 82 and 84). `battle_anims` uses every move once in
  207,278 frames (D38: 285,972), 851 of 851 back at the menu or the battle's end.
- **The same battles.** In ordinary battles the random number generator also steps once a frame
  (at VBlank), so a battle that takes fewer frames draws other numbers, with the same odds. With
  that step switched off in two experiment builds, the code before and after D40 played 32
  battles against Morty and 32 against Pryce turn for turn the same (moves, HP, results), once the
  test autopilot's A nudge was kept off the menus (TESTING.md: it can skip a planned switch, and
  timing decides when). With the step on, 80 battles against Morty (19 and 18 wins, before and
  after D40) and 127 against Pryce (101 and 83; 98 and 83 with the nudge kept off the menus; 72
  and 65 of the 95 after the first sample) show no clear difference: the first sample of 32, which
  raised the question, was the outlier. Two of `bosses_m3`'s samples were too small for this:
  the prepared six beat Morty about 1 time in 5, so 8 tries found no win about 18% of the time
  (the first D40 build's did); Morty now gets 24 tries and Jasmine 16.
- Not changed: the animations' own choreography (already at double speed), the hit blink (16
  frames, D38), messages typed at the TEXT SPEED chosen, the stat change's blend and hold, the
  held-item animation, and the opponent's AI's think time (D38; KNOWN_ISSUES #67). Link and
  recorded battles keep Game Freak's timing.
- Evidence: `battle_turn_flow` (new: the animation within 6 frames of A, the opposing Pokémon's
  within 6 of the HP bar; it needs `within8/16/32`, a new `tools/emurun` command that checks timing
  to the frame), `battle_prompts` (new), `battle_anims`, `battle_speed`, the Gym Leaders' and
  bosses' autobattles, `mega_evolution` and the rest of the play tests.
