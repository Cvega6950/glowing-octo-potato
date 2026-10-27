# Crystal Imperium: testing

## Automated checks

| Check | Command | What it proves |
|---|---|---|
| Data validation | `python3 tools/crystal_imperium/validate.py --check` | Trainer abilities are legal for their species; every boss Pokémon is at the level cap of the boss's stage, and no boss trainer is missing from the list; reworked bosses have 4 moves their species can learn and explicit levels; Red stays the strongest. Reports evolution-family availability. Identifier typos are rejected at build time by trainerproc and the compiler. |
| Generated data is current | `boss_teams.py --check`, `care_packages.py --check`, `tm_list.py --check` (in `tools/crystal_imperium/`) | The boss parties and boss list, the care package table and script, the TM list, the TM item data and the shop lists match their sources. |
| Imperium species data is current | `imperium_species.py --rr-data data.js --check` (in `tools/crystal_imperium/`; `--report` lists what was left out) | The abilities, level-up learnsets and Egg Moves match the Radical Red dex's data file. The file isn't in the repository, so CI doesn't run this. |
| ROM build | `make hns` | Compiles and links within ROM/EWRAM/IWRAM limits; gbafix writes a valid header. |
| Play tests on mGBA | `tools/emurun/run_all.sh` | Real gameplay in libmgba from power-on: see below. |
| Play tests on VBA-M (Delta's core) | `EMURUN_CORE=... tools/emurun/run_all.sh vbam` | The same tests on VBA-M at the commit Delta's GBA core pins. `tools/emurun/build_vbam_core.sh` builds the core. |
| Patches | `tools/crystal_imperium/make_patches.sh` | The BPS patch rebuilds the ROM byte for byte from the HnS 2.0.6 ROM. |
| Save compatibility | `tools/emurun/old_save_test.sh` (`EMURUN_EMULATOR=vbam` for VBA-M) | A save made with Heart & Soul 2.0.6 continues in Crystal Imperium. |

CI (`.github/workflows/crystal_imperium.yml`) runs the validation and generator checks, the build and the mGBA tests in
one job, and the build plus the VBA-M tests in a second job, on pushes to Crystal Imperium
branches.

## Emulator play tests (`tools/emurun/tests/`)

Every test boots the ROM from power-on and drives it with button presses. Assertions read game
memory (party data, battle state, flags, vars, the bag); screenshots are written to
`build/emurun/<test>/` (mGBA) or `build/emurun-vbam/<test>/` (VBA-M).

The tests are deterministic. The same ROM and the same inputs give the same run, and the
cartridge clock starts at a fixed time (2026-10-24 01:30 UTC, night in the game) and advances
with emulated time on both emulators. Battle results depend on the RNG, which depends on the
code and on the emulator, so balance checks sample several battles and accept a range.

Results on the 0.12.0 ROM (SHA-1 `3f3475987c7109fc466e5108652908677ae50952`), 2026-10-26:
All 53 play tests pass on both emulators. Numbers in brackets are sampled counts (hits/runs)
that each test requires to be inside its accepted range.

| Test | Covers | mGBA | VBA-M (Delta's core) |
|---|---|---|---|
| `autorun` | Real story path (clock scene, Mom's Running Shoes); AUTORUN off: walk, B runs; on: run, B walks | **PASS** | **PASS** |
| `battle_healthbox_names` | Falkner battle: ONIX, then FERALIGATR, then ONIX again; ONIX's name strip in the health box matches the first time pixel for pixel (nothing of FERALIGATR's name is left; 8 pixels differ on the 0.10.0 ROM) | **PASS** | **PASS** |
| `boss_levels` | Boss Pokémon at the player's cap at the start of a battle: Petrel at 50 with no badges, 66 with six; Brock at 90 as Johto Champion, 100 as Kanto Champion; a Rocket Grunt's level-20 Koffing on the cap curve, 31, with six badges, held at 15 with none. HARD level caps: Falkner at 12, Petrel at 47, 63 with six badges, the Grunt's Koffing at 12 | **PASS** | **PASS** |
| `bosses_e4` | Elite Four and Lance, every Pokémon at the cap (85): Koga vs the prepared six (naive, 6 tries); Will, Bruno, Karen and Lance vs sixes built for them playing a game plan (8, 12, 12 and 24 tries); all hold care-package items; each beaten at least once; every Mega happens | **PASS** (wins vs Koga 6/6, wins vs Will 3/8, wins vs Bruno 10/12, wins vs Karen 10/12, wins vs Lance 8/24) | **PASS** (wins vs Koga 5/6, wins vs Will 4/8, wins vs Bruno 10/12, wins vs Karen 11/12, wins vs Lance 8/24) |
| `bosses_m3` | Proton, the rival (Azalea, Burned Tower), Morty, every version of Chuck/Jasmine/Pryce, Clair, all with six Pokémon at the cap: each battle plays to a result against a naive team; the prepared six with care-package items beats Morty and Jasmine at least once in 8 and Clair in 16; sixes built for Chuck and Pryce, playing a game plan, beat them at least once in 8; every boss Mega Evolves | **PASS** (wins vs Morty 2/8, wins vs Jasmine 4/8, wins vs Chuck 8/8, wins vs Pryce 6/8, wins vs Clair 6/16) | **PASS** (wins vs Morty 2/8, wins vs Jasmine 2/8, wins vs Chuck 8/8, wins vs Pryce 7/8, wins vs Clair 6/16) |
| `bosses_m4` | Rocket executives (Hideout, Radio Tower), rival 4–5, the five Kimono Girls: each battle plays to a result against the prepared six at the cap, holding care-package items; with the six at 100, Archer's and the rival's Megas happen | **PASS** | **PASS** |
| `bosses_m5` | Kanto leaders at cap 90 vs the prepared six (one try each, tallied); a six built for Blue playing a game plan beats him at least once in 6; every leader's Mega happens within three battles of the prepared six at 100, and Blue's with the six built for him at 100 | **PASS** (wins vs Brock 0/1, wins vs Misty 0/1, wins vs Lt. Surge 1/1, wins vs Erika 0/1, wins vs Janine 1/1, wins vs Sabrina 0/1, wins vs Blaine 0/1, wins vs Blue 3/6, wins vs Brock (mega) 1/3, wins vs Misty (mega) 3/3, wins vs Lt. Surge (mega) 3/3, wins vs Erika (mega) 3/3, wins vs Janine (mega) 3/3, wins vs Sabrina (mega) 1/3, wins vs Blaine (mega) 2/3) | **PASS** (wins vs Brock 0/1, wins vs Misty 0/1, wins vs Lt. Surge 1/1, wins vs Erika 0/1, wins vs Janine 1/1, wins vs Sabrina 0/1, wins vs Blaine 0/1, wins vs Blue 5/6, wins vs Brock (mega) 2/3, wins vs Misty (mega) 1/3, wins vs Lt. Surge (mega) 3/3, wins vs Erika (mega) 3/3, wins vs Janine (mega) 3/3, wins vs Sabrina (mega) 0/3, wins vs Blaine (mega) 1/3) |
| `bug_contest` | Wild Variety is skipped in Bug-Catching Contest mode (0 of 12) and applies outside it | **PASS** (variety_in_contest 0/12, variety_outside_contest 6/12) | **PASS** (variety_in_contest 0/12, variety_outside_contest 9/12) |
| `bugsy` | Bugsy's Imperium-style six (all at the cap, 24) leads Ariados; the naive six (Quilava's Flame Wheel with the first care package's Charcoal, Flaaffy's Power Gem and Pidgeotto's Dual Wingbeat from evolving, Geodude and Onix with Sturdy, two Eviolites) wins some, not all, of 40 sampled battles | **PASS** (wins vs Bugsy 10/40) | **PASS** (wins vs Bugsy 5/40) |
| `bw_ui` | BW summary screen from the party menu (IVs shown), the BW action box (FIGHT / BAG / POKÉMON / RUN) and the BW move box | **PASS** | **PASS** |
| `care_packages` | The starting package on the first step with a Pokémon (Shiny Charm, 153 Quick Balls, 10 of every type booster and resist Berry); 8 badge packages, one per step, then the Champion package, Radical Red's contents (50 Heal and Dream Balls, 153 Ability Capsules and Patches, PP Max with the 153, 20 Leftovers and Life Orbs, 999 Gimmighoul Coins, 100 Beast Balls...); a full Berries pocket sends the Berries to the PC; with 20 free items-pocket slots, the held items go to the PC and the 20 stay free; a full items pocket and PC stop a package at its first held item until another map, then the rest arrives and nothing twice; a save from before 0.12.0 with three badges gets the starting package and its three packages again with the new contents, then the fourth badge's | **PASS** | **PASS** |
| `care_packages_start` | The starting package once (Shiny Charm, 10 of every type booster and resist Berry, 10 Leftovers and Focus Sashes, 153 Quick Balls); Union Cave's location package on the first step inside (10 Damp and Icy Rocks); a save with four badges gets the Union Cave, Ilex Forest, National Park and Burned Tower packages, then the four badge packages; a 0.12.0-experimental save gets the bigger starting package (20 Charcoal, one Shiny Charm) | **PASS** | **PASS** |
| `cheat_codes` | At the bedroom NES, each code typed on the keyboard: a wrong code does nothing; MEGA gives the Mega Ring and the 47 Mega Stones, and nothing twice; MMY the maximum money; CAL every Pokémon caught and the National Pokédex; EZCATCH turns Easy Catch off, EZC on again; SHINYR shiny roamers; DXA a message; NO the NES's old line; with a Pokémon already, MONO and SHS are refused; SHINYS and MONO (Dragon): PROF. ELM's middle Poké Ball holds a shiny Gible | **PASS** | **PASS** |
| `dexnav` | Opened from the L menu: with nothing seen, the area's Pokémon are shown; register Rattata with R, R-search; L ends the search and keeps the chain; R-search again, walk up (no sneaking), battle, catch; search level and chain rise | **PASS** | **PASS** |
| `dexnav_any` | Hidden row on Route 29; SELECT lists all 1,074 Pokémon (Ivysaur, Mewtwo); jump 100; register Squirtle; search Charmander, run up with Auto Run, battle | **PASS** | **PASS** |
| `dexnav_caves` | Dark Cave: DexNav is too dark before Flash; Flash from the party menu (HM05, Zephyr Badge) lights the whole cave and DexNav searches; a save made there with the old lit circle continues fully lit; Union Cave 1F: the DexNav Geodude stays on its tile, the battle starts, caught | **PASS** | **PASS** |
| `dexnav_hidden` | Detector mode finds hidden Pokémon while walking; creeping up starts the battle | **PASS** (hidden_detected 4/12, hidden_battle 4/12) | **PASS** (hidden_detected 3/12, hidden_battle 3/12) |
| `dexnav_randomizer` | Randomizer on for wild Pokémon (map-seeded): DexNav lists Route 29's randomized Pokémon, not Hoothoot and Rattata, and every battle is listed | **PASS** (unrandomized 2/2, random_not_listed 0/12) | **PASS** (unrandomized 2/2, random_not_listed 0/12) |
| `dexnav_surf` | New Bark Town: Tentacool registered from the water row; surfing up to the tile where it appeared, it stays there, the battle starts, caught | **PASS** | **PASS** |
| `dexnav_water_match` | New Bark Town: the water row lists Tentacool and 3 Water-type Wild Variety Pokémon; every surfing battle is listed; fishing gives the town's fishing Pokémon or listed ones | **PASS** (fish_battles 8/10, fish 0/10, surf 5/12, surf_not_listed 0/12) | **PASS** (fish_battles 9/10, fish 0/10, surf 3/12, surf_not_listed 0/12) |
| `dexnav_wild_match` | Route 29: DexNav lists the 2 own and 6 Wild Variety Pokémon and every battle is listed; the next day's set is new and its battles listed; the same day gives the same set; a listed Wild Variety Pokémon is searched for and battled; an outbreak is listed and met | **PASS** (day_a 9/12, day_a_not_listed 0/12, new_on_day_b 6/6, day_b_not_listed 0/8, changed_on_day_a 0/12, search_target 0/1, battle_target 0/1) | **PASS** (day_a 1/12, day_a_not_listed 0/12, new_on_day_b 6/6, day_b_not_listed 0/8, changed_on_day_a 0/12, search_target 0/1, battle_target 0/1) |
| `difficulty` | Bosses stay at the cap on every difficulty: Falkner's party at 15 on EASY (NORMAL caps), 12 on HARD (HARD caps); Youngster Albert's level-7 Pokémon on the cap curve, then scaled: 8 (EASY) and 9 (HARD); a Grunt's Koffing held at the cap, 12, on HARD | **PASS** | **PASS** |
| `easy_catch` | Catch rate 3 caught by one Poké Ball with EASY CATCH on; two balls fail with it off | **PASS** | **PASS** |
| `egg_hatch` | Fast Egg hatching: a Togepi Egg (10 cycles) from the debug menu hatches during a 126-step walk across New Bark Town (8 steps a cycle; Heart & Soul needs over 2,800) | **PASS** | **PASS** |
| `falkner` | Minimal Grinding stats (31 IV / 0 EV) at level 15; Falkner leads Pidgey; battle against the real AI runs to a result | **PASS** | **PASS** |
| `flower_shop` | Goldenrod Flower Shop sells Mints, Ability Capsule and Ability Patch after badge 3 | **PASS** | **PASS** |
| `gym_trainers_m2` | All eight Azalea/Goldenrod Gym trainer battles load; the singles play to a result | **PASS** | **PASS** |
| `hard_mode_rules` | HARD: trainer and wild battles play SET; BAG is refused in a trainer battle and opens in a wild one; NORMAL keeps SHIFT; the options menu shows SET, grayed out | **PASS** | **PASS** |
| `hm_field_moves` | A lone Magikarp (can't learn the moves) cuts the Route 29 tree, opens the Fly map from its party menu and surfs, with only the HMs and badges | **PASS** | **PASS** |
| `infinite_repel` | Infinite Repel on: 80 grass steps without a battle; off: a battle | **PASS** | **PASS** |
| `l_menu` | Start menu with the Pokédex and Pokégear: eight entries, no DEXNAV, EXIT last. L menu: all eight entries; REPEL, FOLLOWER and AUTO RUN switch with A and stay; B and L close it; no menu with BUTTON MODE L=A; POKéVIAL heals HP and poison; PC opens SOMEONE'S PC's Pokémon Storage System and logs off; AUTO RUN on turns a 2-tile walk into a 4-tile run | **PASS** | **PASS** |
| `l_menu_time` | TIME from 1:3x AM: MORNING 8:00, DAY 12:00, EVENING 6:30 PM, NIGHT 8:00 PM the same day, then MORNING the next day (never back); the map reloads with the time of day's light and the day/night Pokémon flags; the DexNav chain is kept; the current time of day changes nothing; surfing in New Bark Town, still surfing on the same tile after the reload | **PASS** | **PASS** |
| `level_cap_wild` | Nothing above the level cap: DexNav with a chain of 100 (search window and battle), a level-50 outbreak (also with catching off), Zapdos and the Cianwood fisher's Tentacool gift all at 15 with NORMAL caps; the DexNav Pokémon and the gift at 12 with HARD caps | **PASS** | **PASS** |
| `mega_evolution` | Player's Ampharos Mega Evolves with R; Lance's Gyarados Mega Evolves on turn 1 (against a Golem lead) | **PASS** | **PASS** |
| `mega_specialist` | Mega Ring gift after badge 3; stone shop tiers | **PASS** | **PASS** |
| `pokevial` | PokéVial in the bag from a new game; heals HP and poison, twice | **PASS** | **PASS** |
| `qol_items` | Rare Candy Box gives 999 candies, the Rare Candy question starts at the 10 levels to the cap, and they stop at the level cap (15); Box Link opens the PC on a route | **PASS** | **PASS** |
| `rare_candy` | Rare Candies several at a time: the count starts at the cap (10) and DOWN takes one off; 9 used at once with no level-up fanfare; one more without a question; B uses none; Caterpie gets 10 at once, learns Bug Bite and evolves; at the cap one more candy evolves Metapod | **PASS** | **PASS** |
| `red` | No battle before the Kanto League; the summit battle is TRAINER_RED_HNS, after the Sinjoh story TRAINER_RED_POSTOBC_HNS; Pikachu (level 100) keeps its EVs (306 Speed); a level-100 six with items and a Mega playing a game plan beats Red at least once in 24; Mega Charizard Y happens | **PASS** (wins vs Red 10/24) | **PASS** (wins vs Red 6/24) |
| `relearner_training_kit` | Training Kit natures and ability (checked in battle); the party-menu relearner teaches the egg move Fury Swipes in place of Tackle (checked in battle) | **PASS** | **PASS** |
| `route_bosses` | The 28 route mini-bosses, in groups by the earliest point their routes can be reached: each has its whole team (3 to 6) at the player's cap (15 to 90) and plays to a result against the prepared six | **PASS** | **PASS** |
| `save_load` | In-game save, hard reset, Continue | **PASS** | **PASS** |
| `stat_editor` | Minimal Grinding off, level-50 HARDY Cyndaquil from L > STATS: START sets IVs to 31 (114 HP); HP IV 31 UP goes round to 0 (99 HP), B undoes an edit; 252 HP EVs (130 HP) and 252 Attack EVs (104 Attack); Defense EVs stop at the 6 left of 510 (64 Defense) | **PASS** | **PASS** |
| `stat_editor_mgm` | Minimal Grinding on: EVs locked (RIGHT stays on the IVs), stats unchanged; HP IV 30 with the rest at 31 reaches the battle (gBattleMons IVs) | **PASS** | **PASS** |
| `story_opening` | Real story path, no debug: Elm's intro, Cyndaquil from the middle ball, Elm's errand, the aide's Potion, the starting care package on the first step outside (Shiny Charm, 153 Quick Balls), Route 29 and a wild battle | **PASS** | **PASS** |
| `summary_nature` | A Cyndaquil born HARDY set to MODEST with L > STATS: its stats follow MODEST and the summary prints MODEST (its nature text points at MODEST's name; HARDY's on the 0.10.1 ROM) | **PASS** | **PASS** |
| `tm_case` | TM163 Temper Flare teaches Cyndaquil (used in battle); all 198 TMs and 8 HMs fill the case; save, reset and Continue keep them | **PASS** | **PASS** |
| `tm_clerk` | TMs cost ¥100 (price data); the Violet City Mart TM clerk sells 71 TMs and gives nothing before the Zephyr Badge; with it, Bullet Seed, Bulldoze, Bug Bite and Stomping Tantrum once, then 115 TMs; Flip Turn bought; the next talk goes straight to the shop | **PASS** | **PASS** |
| `tm_clerks` | TM clerks behind the counters: Cherrygrove City Mart 71 TMs with no badges, Azalea Town Mart 155 with two, Pewter City Mart 198 with eight (TM01 bought), Indigo Plateau 198 | **PASS** | **PASS** |
| `tm_reusable` | One TM teaches two Pokémon and stays in the bag, then a third through the party menu's relearner; the move is used in battle | **PASS** | **PASS** |
| `tm_shop` | Goldenrod 5F TM shop: 71 / 115 / 173 / 191 / 198 TMs at 0 / 1 / 3 / 6 (without Jasmine's badge) / 8 badges; buying TM03 and TM01 works; an owned TM shows OWNED | **PASS** | **PASS** |
| `whitney` | Whitney's six (all at the cap, 33, holding items) leads Clefairy; the naive six, Machoke holding the first care package's Eviolite, wins some, not all, of 24 sampled battles | **PASS** (wins vs Whitney 2/24) | **PASS** (wins vs Whitney 3/24) |
| `wild_variety` | Route 29 at 30%: other Gen 1–9 Pokémon appear; OFF: none, and DexNav lists only the route's own Pokémon | **PASS** (variety_30 5/12, variety_off 0/12) | **PASS** (variety_30 3/12, variety_off 0/12) |

Save compatibility (`old_save_test.sh`), same ROM, on mGBA and on VBA-M: **PASS** on both.
- A Heart & Soul 2.0.6 save (new game, one Pokémon, TM70, TM03 and HM01 from the debug menu,
  saved) continues in Crystal Imperium.
- The party is kept.
- The five key items and the DexNav are given, so the L menu has all eight entries.
- DexNav search levels read 0.
- The TMs keep their moves under the new numbering: TM70 Rock Climb is TM192 and TM03 Water
  Pulse is TM160 in the TM case (not TM70 Triple Axel or TM03 Flip Turn), HM01 is kept, and the
  old SaveBlock1 slots are cleared.
- DexNav opens from the L menu.
- The first step outside (Route 29) brings PROF. ELM's starting care package: a 2.0.6 save
  never had one.

The BPS patch applied to the HnS 2.0.6 ROM gives this ROM byte for byte (`make_patches.sh`).
The source patch series applied with `git am` to tag 2.0.6 gives a tree identical to the branch.

### Battle autopilot

`!autobattle("2,3,1,2")` plays the current battle to the end. It reads the game's state
every frame: which battle controller is waiting for input, whether the party menu is open,
and the battle outcome. Then it answers:
- Each party slot uses one fixed move slot; `m` after the slot number Mega Evolves first.
- Forced switches send out the first healthy Pokémon.
- Text is nudged along.

It logs every turn with both sides' HP, and each Pokémon's moveset the first time it is sent
out. Pipe the output through `tools/emurun/names.py` to get species and move names.
Battle Style should be SET (`!battle_style_set()`) so the AI's free switch prompts don't appear.

`!sample_battle(trainer, moves, runs, min_wins, max_wins)` replays a saved team state at
different frame offsets and asserts the win count is inside the range: winnable, but not a
free badge. The autopilot cannot drive double battles yet.

### Other harness features

- `walkto` reads the player's position; `path=True` routes around walls using the loaded map's
  collision, `creep=True` holds A (DexNav), and targets can be read from memory. A soft walk lets
  go of the d-pad as soon as a battle starts (`stop=` on `gMain.inBattle`): since the battle's
  intro goes on by itself (D38), a walk that kept pressing would move the battle's menu cursor.
- `!wait_action_menu(label)` waits for the battle's action menu without pressing anything; tests
  no longer press A through a battle's intro, which would now choose FIGHT.
- `trace FRAMES ADDR,ADDR... [KEY]` prints the 32-bit values at up to 8 addresses on every frame
  one of them changes (D38's measurements: the battle's main function, each controller, the
  battle script's position); `waituntilany32` waits for one of several values.
- `!move_animation_sweep(state)` uses every move once from a saved battle (`battle_anims`).
- `!open_relearner(slot, presses, category, label)` opens a party Pokémon's move relearner on a
  category (checked); `!expect_relearner_list(...)` checks the list on screen, its length (then
  CANCEL) and the moves it must and mustn't have, against the moves `relearner_list()` reads from
  the teachable learnsets the build generated; `!close_relearner()` leaves it (`move_pools`).
  `expectfind16` / `expectnotfind16` check whether one of a table's entries holds a value.
- `snaprect` remembers a screen rectangle; `expectrect` compares it on one frame, and
  `expectrectwithin NAME FRAMES` on the first of the next FRAMES that matches: the player's
  health box bobs during the action menu, and the bob doesn't always start in the same phase
  (`battle_healthbox_names`).
- Addresses can follow pointers: `*PTR+OFF`, `**PTR+A+B`.
- `expect_flag`, `expect_var`, `expect_save3`, `expect_bag_has`, `expect_battler`,
  `expect_const` resolve game constants and struct offsets by compiling against the game's own
  headers (`probe.py`), so tests don't hard-code numbers that move when the source changes.

## Upstream unit-test suite

`make check` (the Emerald variant, as upstream CI runs it) does not compile on HnS 2.0.6:
`src/braille_puzzles.c` uses `FLAG_RECEIVED_TOGEPI_EGG`, which HnS removed.

`make check BUILD=hns` compiles after our `fake_rtc.h` include fix. Baseline before any
gameplay change (partial run; one worker hung and the run was stopped):
1852 PASS, 1464 FAIL, 477 TO_DO, 27 ASSUMPTION_FAIL, 12 INVALID, 7 KNOWN_FAILING, 1 CRASH.
Many failures come from HnS's runtime challenge settings, which the zeroed test save does
not set. **This suite is not yet a usable regression gate** (KNOWN_ISSUES.md #3).

## Manual test checklist (whole game)

Status: ☐ not yet tested · ☑ tested and passed · ☒ tested and failed

- ☑ ROM boots to the title screen (mGBA, VBA-M)
- ☑ New Game, Oak intro, name entry, settings menu, bedroom
- ☑ Clock scene, Mom's intro (Pokégear, Running Shoes), New Bark Town (`autorun`)
- ☑ Elm's intro, choose a starter, Elm's errand, the aide's Potion (real story path, no debug: `story_opening`)
- ☑ New Bark Town → Route 29, first wild battle with the starter (`story_opening`)
- ☐ Cherrygrove, Mr. Pokémon, the rival battle, Violet City, played through normally
- ☑ Falkner, Bugsy and Whitney battles (debug-started, real AI and party data)
- ☑ Every other reworked boss battle, Morty to Red (debug-started, real AI and party data:
  `bosses_m3`, `bosses_m4`, `bosses_e4`, `bosses_m5`)
- ☐ Badges 4–8 (Morty … Clair), reached in the story
- ☐ Team Rocket radio tower, Kimono Girls, Lugia/Ho-Oh events
- ☐ Elite Four and Lance, reached in the story
- ☐ Kanto access (S.S. Aqua), Kanto badges 1–8, reached in the story
- ☐ Mt. Silver and Red, reached in the story
- ☑ TMs: teaching a TM past TM100, the full TM case through a save, the 5F shop tiers
  (`tm_case`, `tm_shop`, `tm_reusable`)
- ☑ HMs without teaching: Cut, Fly and Surf with a Pokémon that can't learn them (`hm_field_moves`)
- ☑ The L menu (every entry, the time changer, the IV/EV editor) and a start menu that fits the
  screen (`l_menu`, `l_menu_time`, `stat_editor`, `stat_editor_mgm`)
- ☑ Save / reset / Continue (mGBA, VBA-M)
- ☐ Save survives a full-story playthrough across major map transitions
- ☐ Credits / Hall of Fame

## Delta (iPhone) checklist

The emulator code Delta uses has passed the play tests above; the app itself has not been
tried on a phone yet.
1. Get `CrystalImperium.gba` (see the README) and import it into Delta (Files → Delta).
2. The title screen appears and START responds.
3. New Game reaches the bedroom; the settings menu shows MIN. GRINDING ON, EASY CATCH ON and
   WILD VARIETY 30%.
4. The START menu fits on the screen (EXIT is visible). L opens the L menu (Delta's L button);
   its DEXNAV on Route 29 shows the route's Pokémon (not question marks), and SELECT opens the
   list of every Pokémon. The bag's Key Items hold the Rare Candy Box, Infinite Repel, Box
   Link, Training Kit and PokéVial.
5. Save in-game (START → SAVE), close Delta completely, reopen, choose CONTINUE: the game resumes.
6. Fight one wild battle and one trainer battle.
7. Check the in-game clock behaves. HnS can use the real-time clock or the ROM's fake clock
   (settings → Clock Type); try the fake clock if the RTC misbehaves on Delta.
