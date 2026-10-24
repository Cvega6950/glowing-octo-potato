# Crystal Imperium: bug and compatibility log

| # | Area | Issue | Status |
|---|---|---|---|
| 1 | Tests | Upstream `make check` (Emerald variant) fails to compile on HnS 2.0.6: `FLAG_RECEIVED_TOGEPI_EGG` is undefined in `src/braille_puzzles.c`. | Open (upstream) |
| 2 | Tests | `make check BUILD=hns` failed to compile because `test/test_runner.c` included `fake_rtc.h` before `global.h`. | **Fixed** (commit "Fix HnS test build") |
| 3 | Tests | The HnS test suite runs, but about 1.4k tests fail because the zeroed test save leaves HnS's runtime toggles in non-default states. `mgba-rom-test-hydra` also grew to about 13 GB RAM before one worker hung. | Open |
| 4 | Balance | Pryce's ace (Lv 33) is below the NORMAL level cap for 6 badges (38), so capped players can out-level him. | Open, Milestone 2 |
| 5 | Data | `TRAINER_FALKNER_2_HNS` (rematch) gives Swellow no `Level:` line, so trainerproc's default applies. | Open, Milestone 5 rematch rework |
| 6 | ROM budget | ROM 99.37% of 32 MB (about 208 KB free); EWRAM 99.12% (about 2.3 KB free, after the BW battle UI's +8 KB heap); SaveBlock3 1,548 of 1,624 bytes. New graphics and EWRAM buffers must be budgeted. | Constraint (DECISIONS.md D7, D9, D26) |
| 7 | Build | Interrupting `make` (e.g. piping it into `head`) can leave an empty object such as `build/hns/src/region_map.o`, which breaks the link. Delete that object and rebuild. | Note |
| 8 | Platform | Delta's emulator core (VBA-M at GBADeltaCore's pinned commit) runs the full play-test suite, but the Delta app itself (touch controls, its save-file handling, suspend/resume) has not been tested on an iPhone. | Open (needs a device) |
| 9 | Branding | The title screen and ROM header still say Heart & Soul / `POKEMON HNS`. | Open (cosmetic) |
| 10 | Battle UI | HnS maps START to move info, which made the Mega trigger unreachable once Megas were enabled. | **Fixed**: the trigger is on R |
| 11 | Battle UI | The in-battle hint only says "START: MOVE INFO"; nothing on screen tells the player that R toggles Mega Evolution (the Mega Specialist explains it). | Open (cosmetic) |
| 12 | Tests | The battle autopilot cannot drive double battles (no target selection), so double battles are only checked to load. | Open |
| 13 | Tests | Both emulators used the host's clock for the cartridge RTC, so tests gave different results at different hours and on CI (e.g. the time-of-day encounter table, battle RNG). | **Fixed**: emurun pins the clock (D17, CHANGELOG 0.4.0) |
| 14 | Tests | The `whitney` balance check used five samples; the naive team wins about 25%, so all five could lose without any change to the game. | **Fixed**: twelve samples |
| 15 | Tests | `falkner` replayed fixed battle inputs, which fell out of step on VBA-M (different RNG seed). | **Fixed**: the battle autopilot plays it |
| 16 | DexNav | A Pokémon chosen from the "any Pokémon" list appears at the area's level as chosen, so an evolved Pokémon (e.g. Garchomp) can be found at a low level early on. | By design (the user asked for no limits); see D14 |
| 17 | Wild Variety | Random variety encounters can be baby Pokémon (e.g. Pichu) where the main games would use the middle stage, because the pool holds base forms. | By design (D14) |
| 18 | Options | Auto Run is OFF on a new game (Heart & Soul's default); turn it on in START > OPTION > AUTORUN. | Note |
| 19 | Cheats | HnS's debug menu (R + START) is reachable in normal play. It can break the story if story flags are changed. | Note (documented as a cheat menu) |
| 20 | Validator | Counts of families are by evolution family root from the source headers; species defined through nested macros (e.g. Alcremie's forms) are matched through their pre-evolution. | Note |
| 21 | DexNav | DexNav's lists didn't match the wild Pokémon met: Wild Variety picked from the whole pool, and the randomizer's Pokémon weren't shown. | **Fixed** in 0.5.1 (D24) |
| 22 | DexNav | With the randomizer's MAP SEEDED off or CHAOS on, every wild encounter is a new random Pokémon; DexNav lists the area's own Pokémon then. | By design (D24) |
| 23 | DexNav | Fishing Pokémon have no DexNav row (as in the expansion's DexNav), and roaming Pokémon aren't listed. Fishing's Wild Variety Pokémon are the water row's. | By design (D24) |
| 24 | Wild Variety | The grass set can include Pokémon that live in water (e.g. Goldeen, Dondozo): only the water set is limited to Water-types. | By design (D14: every Pokémon on every route) |
| 25 | UI | The party menu, bag, start menu and Pokédex keep Heart & Soul's look; only battles and the summary screen are Black/White-style. | Open (D26) |
| 26 | Battle UI | Moves can't be reordered with SELECT in battle any more (Gen 4+ behaviour, required by the BW interface); the summary screen still reorders them. | By design (D26) |
| 27 | Battle UI | Move info is on L; with BUTTON MODE set to L=A, L acts as A and move info isn't available in battle. | By design (D26) |
| 28 | Story | Red battles only the Kanto Champion; Heart & Soul allowed the battle after 16 badges, while the level cap is still 70. | By design (D27) |
| 29 | Tests | The battle autopilot's forced switches compared party-menu slots (battle order) with party slots (field order): it could keep choosing a fainted Pokémon until the battle timed out. | **Fixed** in 0.6.0 |
| 30 | Tests | The expansion's AI-vs-AI test mode (`B_FLAG_AI_VS_AI_BATTLE`) stops in this build after the player's first Pokémon faints (the switch-in message never completes), so it is not used; the autopilot's game plan stands in for a thinking player. | Open (test tooling only) |
