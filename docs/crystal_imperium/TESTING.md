# Crystal Imperium: testing

## Automated checks

| Check | Command | What it proves |
|---|---|---|
| Data validation | `python3 tools/crystal_imperium/validate.py --check` | Trainer abilities are legal for their species; Gym aces match the level caps; reworked bosses have 4 moves and explicit levels. Identifier typos are rejected at build time by trainerproc and the compiler. |
| ROM build | `make hns` | Compiles and links within ROM/EWRAM/IWRAM limits; gbafix writes a valid header. |
| Emulator play tests | `tools/emurun/run_all.sh` | Real gameplay in libmgba from power-on: see below. |

All three run in CI (`.github/workflows/crystal_imperium.yml`) on pushes to Crystal Imperium branches.

### Emulator play tests (`tools/emurun/tests/`)

The tests are deterministic: the same ROM and the same inputs always produce the same run.
After gameplay or timing changes a test may need its inputs re-recorded. The assertions avoid
depending on RNG where possible.

| Test | Covers | Latest result |
|---|---|---|
| `falkner.emu` | Boot, intro, settings menu (Minimal Grinding ON by default), debug-given team at the cap, 31 IV / 0 EV max HP for Cyndaquil and Geodude, Falkner leads Pidgey, full battle against the real AI runs to completion | PASS (2026-10-23) |
| `save_load.emu` | In-game save to Flash, hard reset, Continue, party restored, game playable | PASS (2026-10-23) |
| `mega_specialist.emu` | Goldenrod Dept. Store 5F: Mega Ring gift dialogue after badge 3, stone shop shows the 8-badge tier (ends at Garchompite; Champion-tier stones absent) | PASS (2026-10-23). Checked by screenshot; no memory assertion. |
| `mega_evolution.emu` | Player's Ampharos holding Ampharosite Mega Evolves with R in the move menu (species 181 → 921); Lance's lead Gyarados Mega Evolves on turn 1 (130 → 917) | PASS (2026-10-23) |
| `bugsy.emu` | Bugsy leads Spinarak; five autopilot battles (different RNG) with a naive Cyndaquil-starter team must include at least one win and one loss | PASS (2026-10-23): 3/5 won |
| `whitney.emu` | Whitney leads Clefairy; five autopilot battles must include at least one win and one loss | PASS (2026-10-23): 3/5 won |
| `gym_trainers_m2.emu` | All eight Azalea/Goldenrod Gym trainer battles load; the seven single battles play to a result | PASS (2026-10-23) |
| `flower_shop.emu` | Debug warp to the Goldenrod Flower Shop; Mints, Ability Capsule (₽20,000) and Ability Patch (₽40,000) listed after badge 3 | PASS (2026-10-23). Checked by screenshot only; the test has no memory assertion yet, so it only fails on a crash. |

Screenshots from each run are written to `build/emurun/<test>/`.

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

Battle RNG depends on frame timing, so one recorded win is not a stable regression check.
`!sample_battle(trainer, moves, runs=5, min_wins=1, max_wins=4)` replays a saved team state
at five different frame offsets. It asserts the win count is inside the range: winnable,
but not a free badge. The autopilot cannot drive double battles yet.

## Upstream unit-test suite

`make check` (the Emerald variant, as upstream CI runs it) does not compile on HnS 2.0.6:
`src/braille_puzzles.c` uses `FLAG_RECEIVED_TOGEPI_EGG`, which HnS removed.

`make check BUILD=hns` compiles after our `fake_rtc.h` include fix. Baseline before any
gameplay change (partial run; one worker hung and the run was stopped):
1852 PASS, 1464 FAIL, 477 TO_DO, 27 ASSUMPTION_FAIL, 12 INVALID, 7 KNOWN_FAILING, 1 CRASH.
Many failures come from HnS's runtime challenge settings, which the zeroed test save does
not set. **This suite is not yet a usable regression gate.** Making it one, by giving tests
default HnS settings, is tracked in KNOWN_ISSUES.md.

## Manual test checklist (whole game)

Status: ☐ not yet tested · ☑ tested and passed · ☒ tested and failed

- ☑ ROM boots to the title screen (mGBA)
- ☑ New Game, Oak intro, name entry, settings menu, bedroom
- ☐ Choose a starter at Elm's lab (real story path, no debug)
- ☐ Route 29 → Cherrygrove rival → Violet City, played through normally
- ☑ Falkner battle (debug-started, real AI and party data)
- ☑ Bugsy and Whitney battles (debug-started, real AI and party data, sampled win rates)
- ☐ Badges 4–8 (Morty … Clair)
- ☐ Team Rocket radio tower, Kimono Girls, Lugia/Ho-Oh events
- ☐ Elite Four and Lance
- ☐ Kanto access (S.S. Aqua), Kanto badges 1–8
- ☐ Mt. Silver and Red
- ☑ Save / reset / Continue
- ☐ Save survives a full-story playthrough across major map transitions
- ☐ Credits / Hall of Fame

## Delta (iPhone) checklist

No iOS device is available to the development environment, so this has **not** been run yet.
1. Get `CrystalImperium.gba` (see the README) and import it into Delta (Files → Delta).
2. The title screen appears and START responds.
3. New Game reaches the bedroom; the settings menu shows MIN. GRINDING ON.
4. Save in-game (START → SAVE), close Delta completely, reopen, choose CONTINUE: the game resumes.
5. Fight one wild battle and one trainer battle.
6. Check the in-game clock behaves. HnS can use the real-time clock or the ROM's fake clock
   (settings → Clock Type); try the fake clock if the RTC misbehaves on Delta.
