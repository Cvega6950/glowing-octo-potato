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
| `flower_shop.emu` | Debug warp to the Goldenrod Flower Shop; Mints, Ability Capsule (₽20,000) and Ability Patch (₽40,000) listed after badge 3 | PASS (2026-10-23). Checked by screenshot only; the test has no memory assertion yet, so it only fails on a crash. |

Screenshots from each run are written to `build/emurun/<test>/`.

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
- ☐ Badges 2–8 (Bugsy … Clair)
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
