# Crystal Imperium: bug and compatibility log

| # | Area | Issue | Status |
|---|---|---|---|
| 1 | Tests | Upstream `make check` (Emerald variant) fails to compile on HnS 2.0.6: `FLAG_RECEIVED_TOGEPI_EGG` is undefined in `src/braille_puzzles.c`. | Open (upstream) |
| 2 | Tests | `make check BUILD=hns` failed to compile because `test/test_runner.c` included `fake_rtc.h` before `global.h`. | **Fixed** (commit "Fix HnS test build") |
| 3 | Tests | The HnS test suite runs, but about 1.4k tests fail because the zeroed test save leaves HnS's runtime toggles in non-default states. `mgba-rom-test-hydra` also grew to about 13 GB RAM before one worker hung. | Open |
| 4 | Balance | Pryce's ace (Lv 33) is below the NORMAL level cap for 6 badges (38), so capped players can out-level him. | Open, Milestone 2 |
| 5 | Data | `TRAINER_FALKNER_2_HNS` (rematch) gives Swellow no `Level:` line, so trainerproc's default applies. | Open, Milestone 5 rematch rework |
| 6 | ROM budget | With the classic Megas the ROM is at 98.75% of 32 MB (about 410 KB free); EWRAM is at 94.6%. New graphics must be budgeted. | Constraint (DECISIONS.md D7, D9) |
| 7 | Build | Interrupting `make` (e.g. piping it into `head`) can leave an empty object such as `build/hns/src/region_map.o`, which breaks the link. Delete that object and rebuild. | Note |
| 8 | Platform | Delta compatibility has not been tested on a device. | Open |
| 9 | Branding | The title screen and ROM header still say Heart & Soul / `POKEMON HNS`. | Open (cosmetic) |
| 10 | Battle UI | HnS maps START to move info, which made the Mega trigger unreachable once Megas were enabled. | **Fixed**: the trigger is on R |
| 11 | Battle UI | The in-battle hint only says "START: MOVE INFO"; nothing on screen tells the player that R toggles Mega Evolution (the Mega Specialist explains it). | Open (cosmetic) |
