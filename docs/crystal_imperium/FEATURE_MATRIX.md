# Crystal Imperium: feature compatibility matrix

Status values:
- **Done**: implemented in this repository and verified (the evidence column says how).
- **Existing**: already in Heart & Soul 2.0.6. Unchanged unless noted.
- **Missing**: not implemented yet.
- **Blocked**: cannot be done as specified. The reason and the alternative are given.
- **Unverified**: present in the code but not yet tested by us.

Evidence key: *emu* = emulator play test in `tools/emurun/tests/` (screenshots plus memory
assertions; run on mGBA and on VBA-M, Delta's emulator core); *build* = compiles into the ROM;
*val* = `tools/crystal_imperium/validate.py`.

## Core game (Section 4, 15)

| Feature | Status | Evidence / notes |
|---|---|---|
| Johto story (New Bark → Lance), rival, Rockets, beasts, Kimono Girls, Ho-Oh/Lugia | Existing / Unverified | HnS content, untouched by our changes. Played so far on the real story path: New Game → clock scene → Mom's intro (Pokégear, Running Shoes) → New Bark Town (emu: `autorun`) → Elm's lab: starter, Elm's errand, the aide's Potion → Route 29 and a wild battle (emu: `story_opening`). |
| Kanto postgame, 16 badges, Mt. Silver, Red | Existing / Partly verified | HnS content. Red's summit event is tested (`red`); the rest of the Kanto postgame is not reached in testing. |
| Day/night system, HGSS music | Existing | Visible in play (night palettes, the clock in the start menu). |
| Boot, title screen, New Game, settings menu | Done | emu: every test boots from power-on. |
| Save / hard reset / Continue | Done | emu: `save_load` (Flash 128K save file), on mGBA and VBA-M. |
| Saves from Heart & Soul 2.0.6 | Done | emu: `old_save_test.sh` on mGBA and VBA-M (party kept; key items and DexNav given). |
| Whiteout after a lost battle | Done | emu: lost autopilot battles return to the overworld. |

## Difficulty and trainers (Sections 5, 6, 11, 12)

| Feature | Status | Evidence / notes |
|---|---|---|
| Difficulty selection EASY / NORMAL / HARD | Done | emu: `difficulty` (bosses stay at the cap: Falkner 15/15/15 on EASY with NORMAL caps, 12/12/12 on HARD with HARD caps; Youngster Albert's level-7 Pokémon, 9 on the cap curve, at 8 on EASY and 9 on HARD; a Grunt's Koffing held at the cap, 12). DECISIONS.md D11. |
| HARD: SET battle style and no Bag in trainer battles (Emerald Imperium / Radical Red rules) | Done | emu: `hard_mode_rules` (SET in trainer and wild battles, BAG refused in a trainer battle and open in a wild one; NORMAL keeps SHIFT). D25. |
| Smart AI for every trainer (omniscient, smart switching, HP aware) | Done | NORMAL/HARD; EASY keeps HnS's AI. D20. emu: whole suite; no extra time per turn. |
| Sleep Clause | Done | build. Imperium behaviour, both sides. |
| Falkner competitive team (six since 0.8.0) | Done | emu: `falkner` (all six at the cap, 15). See BALANCE.md. D30. |
| Violet Gym trainers, Elder Li | Done | build + val. Not yet battled in the emulator. |
| Bugsy competitive team (six since 0.8.0) | Done | emu: `bugsy` (all six at the cap, 24; a naive six holding the first care package's Charcoal and two Eviolites wins some, not all, of 40 samples; TESTING.md has the counts) plus per-Starter lines in BALANCE.md. D30. |
| Whitney competitive team (six since 0.8.0) | Done | emu: `whitney` (all six at the cap, 33; a naive six, Machoke with an Eviolite, wins some, not all, of 24 samples; TESTING.md has the counts) plus per-Starter lines in BALANCE.md. D30. |
| Azalea and Goldenrod Gym trainers | Done | emu: `gym_trainers_m2` (every battle loads and resolves). |
| Morty, Chuck, Jasmine, Pryce (3 versions each), Clair | Done | emu: `bosses_m3` (all at the cap; the prepared six with care-package items beats Morty and Jasmine ≥1 of 8 and Clair ≥1 of 16; sixes built for Chuck and Pryce, with a game plan, ≥1 of 8; Megas trigger). D21. |
| 8 Kanto leaders, Blue | Done | emu: `bosses_m5` (every battle plays to a result at cap 90; a six built for Blue, played with a game plan, beats him ≥1 of 6; each Mega triggers: Blue's against the six built for him, each leader's within three battles of the prepared six at 100). D21. |
| Rival (Azalea, Burned Tower), Proton (Slowpoke Well) | Done | emu: `bosses_m3`. D21. |
| Rival (Goldenrod Underground, Victory Road), Petrel, Ariana, Proton, Archer, Kimono Girls | Done | emu: `bosses_m4` (every battle plays to a result at the cap; Archer's and the rival's Megas trigger against a level-100 six). D21. |
| Every boss Pokémon at the player's level cap, NORMAL or HARD caps (raised to the player's cap when fought later) | Done | `validate.py` (every boss at its stage's cap, none missing); emu: `boss_levels` (Petrel at 50, and 66 with six badges, Brock at 90, then 100 after the Kanto League; with HARD caps Falkner at 12 and Petrel at 47, 63 with six badges; a Grunt at 31 with six badges and held at the cap with none), `difficulty`. D21. |
| Elite Four, Lance | Done | emu: `bosses_e4` (cap 85: Koga by the prepared six; Will, Bruno, Karen and Lance by sixes built for them, played with a game plan; all holding care-package items; each beaten at least once in 6–24 tries; Megas trigger). D21. |
| Red: the hardest battle (all six at level 100, EVs kept under Minimal Grinding, prediction AI, four Full Restores; only for the Kanto Champion) | Done | emu: `red` (no battle before the Kanto League; summit battle and rematch IDs; Pikachu's EV Speed; a level-100 six with items and a Mega beats him ≥1 of 24; Mega Charizard Y); `validate.py` keeps his parties the strongest. D27. |
| Gym Leader and Elite Four rematches, other postgame battles | Existing | HnS rematch teams with the smart AI. Not reworked. |
| Side battles (Emerald Imperium-style): Sinnoh's eight Gym Leaders in Johto, one per badge count; Paldea's eight in Kanto after the Johto League; nine postgame visitors at level 100 after the Kanto League (Cynthia, Iris, Geeta, N, Cyrus, Wallace, Maxie, Archie, Wally); one battle and one reward each, with their own sprites | Done | emu: `side_battles` (Candice: NO, YES, her six at the cap, the reward once, a full Bag and PC then the reward later; Gardenia's badge gate and second team; Iono's gate and her six at 90; Cynthia's gate and her six at 100; sprite screenshots). `side_battles.py --check` (walk-up spots, no path cut off, TMs and Mega Stones not yet on sale), `side_sprites.py --check`, `validate.py`. D41. |
| Machine-readable trainer balance table | Done | `docs/crystal_imperium/data/trainer_balance.json`, generated by val. |

## Minimal Grinding and team building (Section 8, Imperium QoL)

| Feature | Status | Evidence / notes |
|---|---|---|
| Minimal Grinding Mode (default ON) | Done | emu: `falkner` (Lv 15 Cyndaquil 41 max HP = 31 IV / 0 EV). |
| Level caps (optional, NORMAL by default) | Existing, defaulted ON | emu: `qol_items` (Rare Candies stop at the cap), 0 EXP at the cap in battle. |
| Six Pokémon for every Gym Leader, the rival (from his 2nd battle), the Rocket executives and Eusine | Done | `validate.py`; emu: `bugsy`, `whitney`, `bosses_m3`, `bosses_m4` (each battle loads and plays to a result). D30. |
| Route mini-bosses: 28 route trainers with competitive teams at the cap (16 Johto, 12 Kanto) | Done | `validate.py` (moves, abilities, levels); emu: `route_bosses` (team size, levels at the cap, battle to a result for each). D30. |
| Ordinary trainers at the player's level (one to three below the strongest Pokémon), evolved as their level allows, with 31 IVs; bosses as designed at their own level, evolved when raised to a later cap | Done | `src/battle_main.c`; emu: `trainer_levels` (Dragon Tamer Paul's Dratini and Dragonair as Dragonite at 69 and 71 against a level-72 player, 31 IVs; Whitney's Aipom and Stantler at her 33, Ambipom and Wyrdeer raised to 85; a raised boss's Eviolite Lickitung kept; the cap curve's floor; the cap), `boss_levels`, `difficulty`, `whitney`. D46. |
| Emerald Imperium-style teams for every rematch and postgame boss: the Johto leaders' and the Elite Four's rematches after the Johto League, every postgame rematch after the Kanto League, the rival's last two battles, Elder Li (41 teams; one Mega each, no EVs and no restricted legendary at level 100) | Done | `tools/crystal_imperium/boss_teams.py`; val (abilities in this build, learnable moves, the cap of each stage); emu: `boss_rematches` (all 41 load at their caps and play to a result), `bosses_m4`, `bosses_e4`, `red`. D47. |
| Ace Trainers on the routes: 59 new Ace Trainers (26 in Johto, 33 in Kanto) where their sight crosses the route's main path, with Imperium-style teams by stage; Heart & Soul's own Cooltrainers (26 teams) with competitive ones | Done | `tools/crystal_imperium/ace_trainers.py` and `ace_trainer_data.py`; val; emu: `ace_trainers_johto`, `ace_trainers_kanto`, `cooltrainers` (team sizes and levels one to three below the player, a result), `ace_sight` (Kaito sees the player at the end of Route 29, walks up, battles, stays beaten), `ace_sight_town` (the first step out of Cherrygrove is in his line). D47. |
| The trainer checker reads the species data as the game is built (the compiled `#if` branches; a name resolves to the form trainerproc creates) | Done | `tools/crystal_imperium/validate.py` (used by every team generator's checks). D47. |
| Emerald Imperium-style caps: 85 for the Elite Four, 90 in Kanto; other trainers at least on the same curve (and at the player's level, D46) | Done | `validate.py` (every boss at its stage's cap); emu: `qol_items` (Rare Candies stop at 15 with no badges), `boss_levels`, `difficulty` (trainers on the curve), the boss samples at the new caps (`bugsy`, `whitney`, `bosses_m3`, `bosses_m4`, `bosses_e4`, `bosses_m5`). D29. |
| Nothing above the level cap: trainers, wild, DexNav, legendary and gift Pokémon | Done | emu: `level_cap_wild` (DexNav with a chain of 100, a level-50 outbreak with catching on and off, Zapdos and the Cianwood Tentacool gift, all at 15 with NORMAL caps and the DexNav and gift checks at 12 with HARD caps), `boss_levels`, `difficulty`. Roaming Pokémon are covered by the code only. D28. |
| Rare Candy Box: unlimited Rare Candies from the start, regardless of Nuzlocke | Done | emu: `qol_items` (new game, no Nuzlocke, before the first Gym). |
| Rare Candies several at a time: choose how many, no level-up jingle (the music goes on), no stat pages | Done | emu: `rare_candy` (the count starts at the cap and changes with the d-pad; B uses none; moves of the levels passed and evolution after; no fanfare). D33. |
| Fast Egg hatching: an Egg cycle every 8 steps | Done | emu: `egg_hatch` (a Togepi Egg hatches within 126 steps; it doesn't on the 0.8.0 ROM). D32. |
| Infinite Repel (on/off) | Done | emu: `infinite_repel` (80 grass steps without a battle when on, a battle when off). |
| Portable PC (Pokémon Box Link) | Done | emu: `qol_items` (opens Pokémon Storage on Route 29). |
| Move relearner in the party menu (level-up, egg, TM, tutor moves) | Done | emu: `relearner_training_kit` (an egg move taught and used in battle), `party_menu_actions` (a lead with all nine menu entries; B froze the game before 0.13.0), `summary_relearner` (the summary's START opens a category with moves, and gives the one set before back), `tutor_category` (Blackthorn's Move Tutor still teaches level-up moves after a summary's relearner was opened from its PC). |
| Nature and ability changes (Training Kit) | Done | emu: `relearner_training_kit` (Adamant/Modest stats, Flash Fire in battle), `summary_nature` (the summary shows the nature set, not the one the Pokémon was born with; fails on 0.10.1). |
| Reusable TMs | Existing, defaulted ON | emu: `tm_reusable` (one TM teaches two Pokémon and stays in the bag; the move is used in battle). |
| Emerald Imperium's TM list (198 TMs) | Done | emu: `tm_case` (TM163 taught and used in battle; all 206 machines in the case; save + reset keeps them), `tm_shop` (Goldenrod 5F: 71/115/173/191/198 TMs at 0/1/3/6/8 badges, counted), `old_save_test.sh` (HnS TMs converted by move). D22. Imperium's two custom moves are not included (D2). |
| TMs the Emerald Imperium way: ¥100 each; a TM clerk in every Poké Mart, more TMs with every badge; four free ones in Violet with the first badge | Done | emu: `tm_clerks` (Cherrygrove 71 with no badges, Azalea 155 with two, Pewter 198 with eight and a purchase, Indigo Plateau 198), `tm_clerk` (Violet: price data ¥100; 71 before the badge; the four TMs given once; 115 with it; one bought). D22, D36. |
| TM shops list only the TMs the player doesn't have (TM case or PC); a TM bought leaves the list at once; with INFINITE TMS off every TM stays | Done | emu: `tm_shop_owned` (nine of ten listed, one in the PC; the last bought with the list longer than the window and once it fits, then the first and a middle one: list, scroll offset, cursor and scroll arrows checked after each; every TM had: CANCEL alone and its description; INFINITE TMS off: 71 listed, a second Flip Turn bought), `tm_clerk` (the four gift TMs left out), `tm_clerks` (the Pewter list of 197 back on screen within 8 frames of a purchase; 26 in 0.14.2), `tm_shop`. D43. |
| The TMs come free in the care packages: the starting package the 71 the shops sell from the start, each Johto badge's package the ones the shops add with it, all 198 by the 8th badge; a TM the player has isn't given twice; earlier saves get their packages' TMs at once | Done | `tools/crystal_imperium/care_packages.py` (tiers from `tm_list.py`), `src/care_packages.c`; emu: `care_packages` (each tier's TM, the catch-up for a 0.12.0–0.15.0 save: 173 TMs with three badges, once). D48. |
| PokéVial: full party heal outside battle, unlimited | Done | emu: `pokevial` (HP and poison healed twice). Fainted Pokémon stay fainted in a Nuzlocke. |
| After the PokéVial, the healed lead is the follower again | Done | `src/item_use.c`; emu: `pokevial_follower`. D53. |
| Easy Catch: every ball catches (default ON) | Done | emu: `easy_catch` (catch rate 3 caught by one Poké Ball when on; two balls fail when off). |
| Faster battles: scripts without idle frames, no wait for cries; with FAST BATTLES (default ON) the intro and animations at double speed, a shorter hit flash, a faster HP bar and trainer slides, prompts that go on by themselves (trainers' words still wait), "X used Y!" at once and no wait for an animation's sounds or cries, colour fades and Pokémon sent out at double speed, shorter prompts; the turn's bookkeeping in shared frames (always), so a chosen move starts at once; battle menus drawn without freezing the game (FIGHT → moves 10 → 5 frames); FAST INTRO ON for new games and once for old saves | Done | emu: `battle_speed` (no button to the first menu and on to the defeat text, which waits for A; with FAST BATTLES off the intro waits), `battle_anims` (every move used once at double speed returns to the menu or ends the battle), `old_save_test.sh` (both options on after Continue); a one-Pokémon trainer battle 1,518 → 968 frames; choosing a move to its animation 46 → 3 frames and a two-move turn 489 → 211 (`battle_turn_flow`: within 6 frames of A and of the HP bar); menus measured with `profile` (screenshots identical). D38, D40. |
| Milestone care packages (16 badges + Champion) | Done | emu: `care_packages` (8 badge packages and the Champion package; a full pocket sends items to the PC; a full Bag and PC make a package wait for another map). D16. |
| Emerald Imperium's (Radical Red's) care packages: 10 of nearly every held item, Berry, booster and evolution item; 153 Quick Balls, 153 Ability Capsules and Patches, 100 Beast Balls... | Done | 333 entries, about 5,900 items of 248 kinds over 27 packages, generated by `tools/crystal_imperium/care_packages.py`; emu: `care_packages` (the big stacks and ten of each item after eight badges; 20 items-pocket slots kept free for gifts; a save from before 0.12.0 gets its packages again with the new contents), `old_save_test.sh` (a Heart & Soul 2.0.6 save gets the starting package). D16. |
| Starting care package (Shiny Charm, 153 Quick Balls, 999 PP Max, every type booster and resist Berry ×10) and nine location packages (Union Cave, Ilex Forest, National Park, Burned Tower, Lighthouse, Mt. Mortar, Lake of Rage, Ice Path, Victory Road) | Done | emu: `care_packages_start` (the starting package; Union Cave's on the first step inside; a save with four badges gets four location packages; a 0.12.0-experimental save gets the bigger starting package), `story_opening` (the starting package on the real story path). D16. |
| 999 PP Max with the starting package, none in later packages; a save from before 0.15.2 gets the rest up to 999 once | Done | `tools/crystal_imperium/care_packages.py` (PP Max only in the starting package), `src/care_packages.c` (fills the Bag up to 999); emu: `care_packages_start` (999), `care_packages` (still 999 after eight badges; a 0.12.0–0.15.0 save with 40 gets 959, once). D54. |
| Emerald Imperium's cheat codes at the bedroom NES: MEGA, MAXMONEY/MMY, CAUGHTALL/CAL, EZCATCH/EZC, SHINYS/SHS, MONO, SHINYR/SHR, DEXALL/DXA | Done | emu: `cheat_codes` (each typed on the keyboard; the Mega Ring and 47 Mega Stones, nothing twice; max money; every Pokémon caught; Easy Catch off and on; shiny roamers; MONO Dragon and SHINYS give a shiny Gible in PROF. ELM's middle Poké Ball). D37. |
| A cheat code for shiny Pokémon: SHINYA (SHA, ALLSHINY) at the NES makes every wild Pokémon, gift Pokémon and Egg shiny until entered again | Done | `src/cheat_codes.c` (`FLAG_CODE_SHINY_ALL` = `P_FLAG_FORCE_SHINY`); emu: `cheat_shiny_all` (on, off, on; a shiny gift and a shiny wild Pidgey). D49. |
| Mints, Ability Capsule / Patch in shops | Done | emu: `flower_shop` (Goldenrod Flower Shop after badge 3). |
| Emerald Imperium's evolutions, from its official dex: trades also with a Linking Cord, regional forms by time of day or item, levels in place of friendship and special methods, earlier levels; Heart & Soul's ways kept only for the Alcremie flavours and Magnezone's and Vikavolt's places; the Milcery short clockwise spin fixed | Done | `tools/crystal_imperium/imperium_evolutions.py --ei-dex` (219 species; also writes EVOLUTIONS.md); emu: `imperium_evolutions` (Linking Cord on Kadabra, Shiny Stone on Pikachu for Alolan Raichu, Munchlax at 30 with a Rare Candy above the cap, a level-45 Kadabra not evolving, a short clockwise spin by day evolving Milcery); val (the overrides in the families). D44, D45. |
| IV/EV editor (Imperium's Stat Editor): L > STATS > IVs & EVs, or the Training Kit | Done | emu: `stat_editor` (Minimal Grinding off: IV 0 and 252 EVs change HP, UP goes round, B undoes, the 510 total stops Defense at 6 EVs), `stat_editor_mgm` (Minimal Grinding on: EVs locked, the edited IVs in battle). D34. |

## Pokémon availability (Section 7)

| Feature | Status | Evidence / notes |
|---|---|---|
| Gen 1–9 species data, Fairy type, Hidden Abilities, sprites | Existing | All `P_GEN_*_POKEMON TRUE`. Fairy type is an option (default ON). |
| Emerald Imperium's abilities, level-up moves and Egg Moves, from its official dex (the Radical Red dex's until 0.15.0) | Done | `tools/crystal_imperium/imperium_species.py --ei-dex` (1,099 learnsets, 416 Egg Move lists, 474 species with Imperium's abilities); val (trainer abilities); the whole emu suite. Imperium's own abilities (Striker, Bone Zone...) and its own Megas aren't in the engine; stats and types are Heart & Soul's. D35, D45. |
| Emerald Imperium's base stats, from its official dex: 294 species (mostly buffs to weak Pokémon), trainers' Pokémon too | Done | `tools/crystal_imperium/imperium_species.py --ei-dex` (`species_info/imperium_stats.h`); emu: `imperium_stats` (base stats in the ROM, a level-50 Farfetch'd's 150 HP). D50. |
| Pikachu competitive without evolving (60/90/60/120/90/70, BST 490; its forms too) and with its newest (Gen 4/5-style) sprites | Done | `species_info/crystal_imperium_stats.h`, `P_GBA_STYLE_PIKACHU_GFX`; emu: `pikachu` (stats, 135 HP at level 50, sprite sizes, summary and battle screenshots), `red` (372 Speed). D51. |
| Emerald Imperium's TM and tutor compatibility, from its official dex; its TM and tutor moves missing here as tutor moves (Dark Hole and Draco Barrage after the Hall of Fame) | Done | `imperium_species.py` (`imperium_teachables.json`) and `tools/learnset_helpers/make_teachables.py`; emu: `move_pools` (Typhlosion's TM and tutor lists, Terapagos's, Mew's 206 TMs and HMs, Mew's tutor list: Scald and Work Up, not Radical Red's Cosmic Power; Draco Barrage after the Hall of Fame, used in battle), `tutor_category`. D39, D45. |
| Gen 1–9 Pokémon on every route: Wild Variety (default 30%), a set per area, the same every day since 0.14.1 | Done | emu: `wild_variety` (Wild Variety Pokémon among 12 Route 29 battles; none with it OFF, and DexNav lists none), `dexnav_wild_match` (the same set the next day and at noon). D14, D24, D42. |
| Search for any Pokémon anywhere (DexNav list) | Done | emu: `dexnav_any` (all 1,074 Pokémon listed from the start, including Ivysaur and Mewtwo; LEFT/RIGHT jump 100; Charmander searched for and battled on Route 29). |
| Legendary and Mythical Pokémon | Done | On the DexNav list from the start (`dexnav_any`); after becoming Champion, a quarter of the areas' Wild Variety sets end with one (one set a day until 0.14.1, D42). HnS's own legendary events are unchanged. D24. |
| Cheat menu (any Pokémon or item) | Existing | HnS's debug menu, compiled in: hold R and press START in the overworld (the play tests use it). |
| Families with no source in the base game | Done | 258 non-legendary families placed in DexNav hidden slots on 249 map tables, a map's tables for every time of day sharing one set of three (`gen_hidden_encounters.py`, D42). val: 449 of 571 families have a wild, hidden or scripted source; the remaining 122 are all legendary/mythical (see above). |
| Evolution items | Done | Emerald Imperium's fifteen at the Goldenrod Dept. Store 2F for ¥500 each, and in the care packages; the ones no evolution uses are out of the packages, the Mahogany shop and the side-battle rewards. emu: `imperium_evolutions` (the 2F list and prices), `care_packages`. D16, D44. |
| Encounter availability database | Done | `docs/crystal_imperium/data/encounters.json` (val). |
| Randomizer with all Gen 1–9 species | Existing | HnS option. Not needed for the normal game. |

## DexNav

| Feature | Status | Evidence / notes |
|---|---|---|
| DexNav from the start (in the L menu since 0.10.0; START or L ends a search and keeps the chain) | Done | emu: `dexnav` (opened from the L menu; L ends a search, the chain kept), every DexNav test through the L menu. D34. |
| Area lists (land, water, hidden) | Done | emu: `dexnav`, `dexnav_any` (hidden row on Route 29). |
| Register (R in DexNav) and search with R in the overworld | Done | emu: `dexnav`. |
| Search, walk or run up (no sneaking needed), battle | Done | emu: `dexnav` (walking), `dexnav_any` (Auto Run), `dexnav_hidden` (sneaking with A). D19. |
| DexNav in caves and on water: the Pokémon stays on its tile; Dark Cave after Flash | Done | emu: `dexnav_caves` (Dark Cave too dark before Flash, fully lit after it, DexNav searches, also on a save continued there; Union Cave 1F: walk up, battle, catch), `dexnav_surf` (New Bark Town: surf up, battle, catch). D31. |
| Search levels and chain | Done | emu: `dexnav` (search level 1 and chain 1 after one DexNav catch). Stored per National Dex number (D13). |
| Hidden Pokémon detection while walking | Done | emu: `dexnav_hidden` (detections lead to battles). |
| Area lists show every Pokémon, seen or not (no question marks) | Done | emu: `dexnav` (nothing seen yet; Rattata is shown, registered with R, searched and caught). D18. |
| Area lists match the wild Pokémon you meet (Wild Variety, randomizer, outbreaks) | Done | emu: `dexnav_wild_match` (12 grass battles all listed; a listed Wild Variety Pokémon searched for and battled; outbreak listed), `dexnav_water_match` (surfing and fishing), `dexnav_randomizer` (map-seeded randomizer), `bug_contest` (National Park battles outside the contest). D24. |
| The same list at every hour and every day: an area's morning, day and night Pokémon together, all of them met at any hour; Wild Variety and hidden Pokémon fixed per area | Done | emu: `dexnav_wild_match` (Route 29's five own and six Wild Variety Pokémon at night, the next day and at noon; the day's Pokémon met at night; every battle listed), `dexnav`, `level_cap_wild`, `bug_contest`. Sinjoh Ruins keeps its daytime table (the night one would overfill the row). D42. |
| DexNav marks caught Pokémon: a Poké Ball on caught Pokémon's icons and in the SELECT list | Done | `src/dexnav.c`; emu: `dexnav_caught` (marks drawn where nothing was before). D52. |

## Battle mechanics (Section 9)

| Feature | Status | Evidence / notes |
|---|---|---|
| Physical/special split, modern moves/abilities/crits/weather | Existing | RHH engine. Split is an option (default ON). |
| Mega Evolution (47 classic stone Megas + Rayquaza) | Done | emu: `mega_evolution` (player Ampharos → Mega with R; Lance's Gyarados on turn 1) and `mega_specialist`. |
| Primal Reversion | Missing | ROM budget. |
| Emerald Imperium's 24 custom Megas | **Blocked** | No license or permission to reuse their sprites and data (D2). |
| Tera / Dynamax / Z-Moves | Existing in the engine, unused | Not part of the Crystal Imperium design. |

## Quality of life (Section 10)

| Feature | Status | Evidence / notes |
|---|---|---|
| Auto Run in the Options menu | Done | emu: `autorun` (OFF: walk, B runs; ON: run, B walks). HnS's default is OFF; a new game asks nothing, the toggle is START > OPTION > AUTORUN, and AUTO RUN in the L menu (`l_menu`: walking 2 tiles, then running 4). |
| Emerald Imperium's L menu: POKéVIAL, PC, DEXNAV, TIME, STATS, and the REPEL, FOLLOWER and AUTO RUN switches, with the clock | Done | emu: `l_menu` (every entry; switches green when on; B and L close it; no menu with BUTTON MODE L=A; the PokéVial heals; the whole PC opens the Pokémon Storage System), `old_save_test.sh` (complete on a Heart & Soul save). D34. |
| Time changer (L > TIME: morning, day, evening, night) | Done | emu: `l_menu_time` (8 AM, noon, 6:30 PM, 8 PM; the same day or the next, never back; light, time of day and day/night Pokémon follow; DexNav chain kept; still surfing). D34. |
| A start menu that fits on the screen (eight entries) | Done | emu: `l_menu` (eight entries with the Pokédex and the Pokégear, EXIT last; the DexNav moved to the L menu). D34. |
| Fast surf, fast battle text, follower Pokémon | Existing | HnS options. |
| HM field moves without teaching | Done | Carrying the HM and its badge is enough for any Pokémon (HnS needed one that could learn the move). emu: `hm_field_moves` (a Magikarp cuts, flies, surfs), `dexnav_caves` (a Cyndaquil uses Flash, which lights the whole cave since 0.8.1). D23, D31. |
| HGSS-style Pokédex | Existing | `POKEDEX_PLUS_HGSS TRUE`. |
| Gen 5 look: BW battle interface | Done | mudskip's BW Battle UI. emu: `bw_ui` (BW action box, BW move box), `battle_healthbox_names` (a name after a switch keeps nothing of the longer one before it); every battle test. D26. |
| Gen 5 look: BW summary screen (IVs/EVs on the skills page) | Done | RavePossum's BW Summary Screen. emu: `bw_ui` (opens from the party menu, A shows IVs). D26. |
| Gen 5 look: party menu, bag, start menu | Missing | Heart & Soul's look (KNOWN_ISSUES 25). |
| Clean difficulty options UI | Done | All new options live in HnS's existing challenge menu. |

## Postgame (Section 13)

| Feature | Status | Evidence / notes |
|---|---|---|
| 16 leader rematches, Battle Frontier and Tents | Existing / Unverified | HnS. |
| Repeatable boss challenge system, superbosses | Missing | Later milestone. |

## Platform (Section 17)

| Feature | Status | Evidence / notes |
|---|---|---|
| Valid GBA ROM (header fixed by gbafix, 32 MB) | Done | build. ROM 99.74% of 32 MB (about 86 KB free), EWRAM 99.14%, SaveBlock1 15,760 / 15,872 bytes, SaveBlock3 1,548 / 1,624 bytes. |
| mGBA (libmgba 0.10.2) | Done | emu: full suite. |
| Delta (iOS) emulator core: VBA-M at GBADeltaCore's pinned commit `453fa0de` | Done | emu: full suite on `run_all.sh vbam` (see TESTING.md for the run). ROM keeps game code `BPEE` → Delta's `vba-over.ini` gives RTC on and 128 KB Flash, matching the game. |
| Delta app on an iPhone | **Unverified** | No iOS device here. The app layer (touch controls, save files, suspend/resume) needs the device checklist in TESTING.md. |
