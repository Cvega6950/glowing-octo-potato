# Crystal Imperium: testing

## Automated checks

| Check | Command | What it proves |
|---|---|---|
| Data validation | `python3 tools/crystal_imperium/validate.py --check` | Trainer abilities are legal for their species; Gym aces match the level caps; reworked bosses have 4 moves their species can learn and explicit levels. Reports evolution-family availability. Identifier typos are rejected at build time by trainerproc and the compiler. |
| Generated data is current | `boss_teams.py --check`, `tm_list.py --check` (in `tools/crystal_imperium/`) | The boss parties, the TM list, the TM item data and the shop lists match their sources. |
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

Results on the 0.6.0 ROM (SHA-1 `e488bc80f06c9c184c3d8dd9d781ffbfab72b4ed`), 2026-10-24:
All 36 play tests pass on mGBA and on VBA-M. Numbers in brackets are sampled counts (hits/runs)
that each test requires to be inside its accepted range.

| Test | Covers | mGBA | VBA-M (Delta's core) |
|---|---|---|---|
| `autorun` | Real story path (clock scene, Mom's Running Shoes); AUTORUN off: walk, B runs; on: run, B walks | **PASS** | **PASS** |
| `bosses_e4` | Elite Four and Lance at cap 56: Koga vs the prepared six (naive, 6 tries); Will, Bruno, Karen and Lance vs sixes built for them playing a game plan (8, 6, 8 and 24 tries); each beaten at least once; every Mega happens | **PASS** (wins vs Koga 6/6, wins vs Will 3/8, wins vs Bruno 5/6, wins vs Karen 4/8, wins vs Lance 5/24) | **PASS** (wins vs Koga 4/6, wins vs Will 4/8, wins vs Bruno 6/6, wins vs Karen 6/8, wins vs Lance 2/24) |
| `bosses_m3` | Proton, the rival (Azalea, Burned Tower), Morty, every version of Chuck/Jasmine/Pryce, Clair: each battle plays to a result; the naive team loses; a prepared six at the cap beats each Gym Leader at least once in 8 (Pryce 16); every boss Mega Evolves | **PASS** (wins vs Morty 5/8, wins vs Chuck 6/8, wins vs Jasmine 6/8, wins vs Pryce 7/16, wins vs Clair 4/8) | **PASS** (wins vs Morty 6/8, wins vs Chuck 6/8, wins vs Jasmine 6/8, wins vs Pryce 3/16, wins vs Clair 6/8) |
| `bosses_m4` | Rocket executives (Hideout, Radio Tower), rival 4–5, the five Kimono Girls: each battle plays to a result against the prepared six at the cap; Archer's and the rival's Megas happen | **PASS** | **PASS** |
| `bosses_m5` | Kanto leaders at cap 70 vs the prepared six (one try each, tallied); a six built for Blue playing a game plan beats him at least once in 6; with the six at 100, every leader's and Blue's Mega happens | **PASS** (wins vs Brock 0/1, wins vs Misty 0/1, wins vs Lt. Surge 1/1, wins vs Erika 1/1, wins vs Janine 0/1, wins vs Sabrina 0/1, wins vs Blaine 0/1, wins vs Blue 6/6) | **PASS** (wins vs Brock 0/1, wins vs Misty 0/1, wins vs Lt. Surge 1/1, wins vs Erika 0/1, wins vs Janine 0/1, wins vs Sabrina 0/1, wins vs Blaine 0/1, wins vs Blue 6/6) |
| `bug_contest` | Wild Variety is skipped in Bug-Catching Contest mode (0 of 12) and applies outside it | **PASS** (variety_in_contest 0/12, variety_outside_contest 6/12) | **PASS** (variety_in_contest 0/12, variety_outside_contest 9/12) |
| `bugsy` | Bugsy leads Spinarak; naive team wins some, not all, of 5 sampled battles | **PASS** (wins vs Bugsy 2/5) | **PASS** (wins vs Bugsy 2/5) |
| `bw_ui` | BW summary screen from the party menu (IVs shown), the BW action box (FIGHT / BAG / POKÉMON / RUN) and the BW move box | **PASS** | **PASS** |
| `care_packages` | 8 badge packages, one per step, then the Champion package; bag contents checked | **PASS** | **PASS** |
| `dexnav` | With nothing seen, the area's Pokémon are shown; register Rattata with R, R-search, walk up (no sneaking), battle, catch; search level and chain rise | **PASS** | **PASS** |
| `dexnav_any` | Hidden row on Route 29; SELECT lists all 1,074 Pokémon (Ivysaur, Mewtwo); jump 100; register Squirtle; search Charmander, run up with Auto Run, battle | **PASS** | **PASS** |
| `dexnav_hidden` | Detector mode finds hidden Pokémon while walking; creeping up starts the battle | **PASS** (hidden_detected 1/12, hidden_battle 1/12) | **PASS** (hidden_detected 4/12, hidden_battle 4/12) |
| `dexnav_randomizer` | Randomizer on for wild Pokémon (map-seeded): DexNav lists Route 29's randomized Pokémon, not Hoothoot and Rattata, and every battle is listed | **PASS** (unrandomized 2/2, random_not_listed 0/12) | **PASS** (unrandomized 2/2, random_not_listed 0/12) |
| `dexnav_water_match` | New Bark Town: the water row lists Tentacool and 3 Water-type Wild Variety Pokémon; every surfing battle is listed; fishing gives the town's fishing Pokémon or listed ones | **PASS** (fish_battles 7/10, fish 0/10, surf 6/12, surf_not_listed 0/12) | **PASS** (fish_battles 6/10, fish 0/10, surf 5/12, surf_not_listed 0/12) |
| `dexnav_wild_match` | Route 29: DexNav lists the 2 own and 6 Wild Variety Pokémon and every battle is listed; the next day's set is new and its battles listed; the same day gives the same set; a listed Wild Variety Pokémon is searched for and battled; an outbreak is listed and met | **PASS** (day_a 6/12, day_a_not_listed 0/12, new_on_day_b 6/6, day_b_not_listed 0/8, changed_on_day_a 0/12, search_target 0/1, battle_target 0/1) | **PASS** (day_a 4/12, day_a_not_listed 0/12, new_on_day_b 6/6, day_b_not_listed 0/8, changed_on_day_a 0/12, search_target 0/1, battle_target 0/1) |
| `difficulty` | Falkner's party at 90% levels on EASY and 110% on HARD | **PASS** | **PASS** |
| `easy_catch` | Catch rate 3 caught by one Poké Ball with EASY CATCH on; two balls fail with it off | **PASS** | **PASS** |
| `falkner` | Minimal Grinding stats (31 IV / 0 EV); Falkner leads Pidgey; battle against the real AI runs to a result | **PASS** | **PASS** |
| `flower_shop` | Goldenrod Flower Shop sells Mints, Ability Capsule and Ability Patch after badge 3 | **PASS** | **PASS** |
| `gym_trainers_m2` | All eight Azalea/Goldenrod Gym trainer battles load; the singles play to a result | **PASS** | **PASS** |
| `hard_mode_rules` | HARD: trainer and wild battles play SET; BAG is refused in a trainer battle and opens in a wild one; NORMAL keeps SHIFT; the options menu shows SET, grayed out | **PASS** | **PASS** |
| `hm_field_moves` | A lone Magikarp (can't learn the moves) cuts the Route 29 tree, opens the Fly map from its party menu and surfs, with only the HMs and badges | **PASS** | **PASS** |
| `infinite_repel` | Infinite Repel on: 80 grass steps without a battle; off: a battle | **PASS** | **PASS** |
| `mega_evolution` | Player's Ampharos Mega Evolves with R; Lance's Gyarados Mega Evolves on turn 1 (against a Golem lead) | **PASS** | **PASS** |
| `mega_specialist` | Mega Ring gift after badge 3; stone shop tiers | **PASS** | **PASS** |
| `pokevial` | PokéVial in the bag from a new game; heals HP and poison, twice | **PASS** | **PASS** |
| `qol_items` | Rare Candy Box gives 999 candies and stops at the level cap; Box Link opens the PC on a route | **PASS** | **PASS** |
| `red` | No battle before the Kanto League; the summit battle is TRAINER_RED_HNS, after the Sinjoh story TRAINER_RED_POSTOBC_HNS; Pikachu keeps its EVs (294 Speed); a level-100 six with items and a Mega playing a game plan beats Red at least once in 12; Mega Charizard Y happens | **PASS** (wins vs Red 5/12) | **PASS** (wins vs Red 4/12) |
| `relearner_training_kit` | Training Kit natures and ability (checked in battle); party-menu relearner teaches an egg move | **PASS** | **PASS** |
| `save_load` | In-game save, hard reset, Continue | **PASS** | **PASS** |
| `story_opening` | Real story path, no debug: Elm's intro, Cyndaquil from the middle ball, Elm's errand, the aide's Potion, Route 29 and a wild battle | **PASS** | **PASS** |
| `tm_case` | TM163 Temper Flare teaches Cyndaquil (used in battle); all 198 TMs and 8 HMs fill the case; save, reset and Continue keep them | **PASS** | **PASS** |
| `tm_reusable` | One TM teaches two Pokémon and stays in the bag, then a third through the party menu's relearner; the move is used in battle | **PASS** | **PASS** |
| `tm_shop` | Goldenrod 5F TM shop: 71 / 155 / 178 / 198 TMs at 0 / 3 / 6 (without Jasmine's badge) / 8 badges; buying TM03 and TM01 works | **PASS** | **PASS** |
| `whitney` | Whitney leads Clefairy; naive team wins some, not all, of 12 sampled battles | **PASS** (wins vs Whitney 5/12) | **PASS** (wins vs Whitney 4/12) |
| `wild_variety` | Route 29 at 30%: other Gen 1–9 Pokémon appear; OFF: none, and DexNav lists only the route's own Pokémon | **PASS** (variety_30 5/12, variety_off 0/12) | **PASS** (variety_30 3/12, variety_off 0/12) |

Save compatibility (`old_save_test.sh`), same ROM, on mGBA and on VBA-M: **PASS** on both.
- A Heart & Soul 2.0.6 save (new game, one Pokémon, TM70, TM03 and HM01 from the debug menu,
  saved) continues in Crystal Imperium.
- The party is kept.
- The five key items and the DexNav are given.
- DexNav search levels read 0.
- The TMs keep their moves under the new numbering: TM70 Rock Climb is TM192 and TM03 Water
  Pulse is TM160 in the TM case (not TM70 Triple Axel or TM03 Flip Turn), HM01 is kept, and the
  old SaveBlock1 slots are cleared.
- DexNav opens.

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
  collision, `creep=True` holds A (DexNav), and targets can be read from memory.
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
4. START shows DEXNAV; on Route 29 it shows the route's Pokémon (not question marks), and
   SELECT opens the list of every Pokémon. The bag's Key Items hold the Rare Candy Box,
   Infinite Repel, Box Link, Training Kit and PokéVial.
5. Save in-game (START → SAVE), close Delta completely, reopen, choose CONTINUE: the game resumes.
6. Fight one wild battle and one trainer battle.
7. Check the in-game clock behaves. HnS can use the real-time clock or the ROM's fake clock
   (settings → Clock Type); try the fake clock if the RTC misbehaves on Delta.
