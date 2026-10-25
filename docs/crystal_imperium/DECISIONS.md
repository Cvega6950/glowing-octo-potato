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
- Red and Heart & Soul's postgame rematch teams also get `Prediction` (D20 explains why the
  rest don't; D27).
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
- The evolution items found nowhere else in HnS stay where they were: Linking Cord, Upgrade,
  Sachet, Whipped Dream, Prism Scale, Sun Stone, Sweet/Tart/Syrupy Apple, the Alcremie Sweets,
  Cracked/Chipped Pot, both Teacups, Leader's Crest, both Armors, Metal Alloy, 999 Gimmighoul
  Coins and, for the Champion, both Scrolls.
- All 30 trade evolutions also have a non-trade method in the data, so no evolution needs a
  link cable.
- Evidence: `care_packages` (one package per milestone, the held items, PP Max, X items and
  Berries in the Bag after the eight Johto badges and the Champion, a full Berries pocket
  sending the first package's Berries to the PC, and a save with eight packages and no gear
  getting the eight packages' gear before the Champion's package).

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
- In caves and on water the Pokémon still moves away up to twice when the player gets close
  at low search levels (upstream behaviour).

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
  - **Every Pokémon is at the NORMAL level cap** (since 0.7.0; before, only the ace was, and the
    others were one or two levels below). The user asked for every boss's and Gym Leader's
    Pokémon to be at the level cap, to make the game harder. Each boss has a *stage*, the
    earliest point in the game its battle can happen (a badge count, the Johto League won or the
    Kanto League won), and its levels are that stage's cap from `src/caps.c` (11, 16, 21, 25, 31,
    36, 38, 45, 56, then 70 and 100). With the Rare Candy Box the player can always be at the cap.
  - **A boss fought later is raised to the cap then.** `CreateNPCTrainerParty`
    (`src/battle_main.c`) raises a boss's Pokémon to the player's NORMAL cap (whatever the level
    cap setting) when that is above the party's levels; the list of bosses is generated into
    `src/data/level_cap_bosses.h`. This covers the battles whose badge count varies: the Rocket
    Hideout (the Lake of Rage needs Surf, so four to six badges: 31, 36 or 38), Eusine in
    Cianwood, and the battles that are also rematches after the Kanto League (the Kanto Gym
    teams in the Fighting Dojo, the Johto leaders' and the Elite Four's `_2` teams before the
    Sinjoh story, the rival at the Indigo Plateau): at 100 then. EASY and HARD still scale the
    result to 90% and 110%. Other trainers are untouched (`boss_levels` checks a Grunt).
  - Heart & Soul's own teams for the other bosses keep their Pokémon and only get the levels
    (`LEVEL_ONLY` in `boss_teams.py`): Li, Falkner, Bugsy, Whitney, the first rival battle and
    Eusine; the rival on Mt. Moon and at the Indigo Plateau, the Fighting Dojo rematches and the
    Kanto League (70); and every rematch after it (`_POSTOBC`: 100). The bonus storylines'
    trainers (New Sinjoh, Samson Oak, Steven, Giovanni) are at or above the cap where they can
    first be fought and keep their levels; the unused and debug-only teams too.
  - Every Pokémon has a held item, a nature, an ability chosen for the set and four moves its
    species or a pre-evolution can learn (`validate.py` checks abilities, moves, that every
    boss is at its stage's cap and that no boss trainer is missing from the list).
  - Team size grows: 3–4 for early story bosses, 5 for Morty and for a 5th Gym, 6 after that.
  - From the 5th Gym on, each boss has one Mega Evolution with a stone from the Mega shop's
    tiers (D9). The stone isn't always on sale before the boss who uses it: Steelixite and
    Abomasite come with the 6th badge, and Jasmine or Pryce can be the 5th Gym. Morty has none
    (the player's Mega Ring arrives only one badge earlier).
  - Chuck, Jasmine and Pryce have three versions each, picked by how many of the three the
    player has beaten (HnS's `_1`, `_1_2`, `_1_3`): caps 31, 36 and 38.
  - The Kanto leaders and Blue are at 70 (the cap for all of Kanto). Red, with no cap left, was
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
  has by then, D16; `boss_levels` checks the raise to the cap, `validate.py` every level):
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
  (TM171), which the engine doesn't have and D2 keeps out. Crystal Imperium has the other 172,
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
  Prices are ₽1,500 / 3,000 / 5,000 / 8,000 by tier; Heart & Soul charged ₽10,000 for its 5F
  TMs. Shop lists show each TM's move next to its number ("TM03 FLIP TURN"), as the bag does;
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
  tree, opens the Fly map from its party menu and surfs, with only the HMs and badges.

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
  same time (16 badges), and the level cap stays at 70 until the Kanto League is won; at the
  cap a level-100 team with EVs is out of reach. Before the Kanto League Red now stays
  silent ("RED seems to be waiting for the KANTO CHAMPION."), so he is the last battle and the
  player can bring a level-100 team. Heart & Soul let him be fought after 16 badges.
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
