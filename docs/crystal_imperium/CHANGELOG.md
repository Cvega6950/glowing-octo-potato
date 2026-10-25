# Crystal Imperium changelog

## 0.10.1-experimental (2026-10-25)

### Fixes
- **Battle health box names** (DECISIONS.md D26). After a switch, a shorter name kept the end of
  the longer one before it ("LARVITAR -|" after FERALIGATR, reported on Delta). The Black/White
  battle interface fits a name into 7 tiles but cleared only 6 of them first; now it clears all 7.

### Tooling
- New test `battle_healthbox_names` (it fails on the 0.10.0 ROM). `emurun` gains `snaprect` and
  `expectrect`, which compare a rectangle of the screen with the same rectangle earlier.

## 0.10.0-experimental (2026-10-25)

### Fixes
- **The start menu fits on the screen again** (DECISIONS.md D34). With the Pokédex and the
  Pokégear it had nine entries and EXIT ran off the bottom; the screen has room for eight. The
  DexNav moved to the new L menu.

### Quality of life
- **The L menu, after Emerald Imperium's** (D34). Press **L** in the field for:
  - **POKéVIAL**: heal the party.
  - **PC**: a Pokémon Center's whole PC (Pokémon boxes, item storage, challenges).
  - **DEXNAV**: B in it comes back to the L menu. Pressing L during a DexNav search ends it
    and keeps the chain.
  - **TIME**: MORNING, DAY, EVENING or NIGHT moves the clock forward to 8:00 AM, 12:00 PM,
    6:30 PM or 8:00 PM (the next day if that time has passed; the clock never goes back). The
    map reloads where you stand, so the light, the Pokémon seen by day or by night and the
    people who come at certain times follow at once.
  - **STATS**: the Training Kit (nature, ability) and a new **IVs & EVs** editor, Emerald
    Imperium's Stat Editor. A window shows each stat's IV, EV and value, Hidden Power's type and
    the EVs used; the d-pad picks one, A changes it (UP/DOWN by 1, LEFT/RIGHT by 10), START
    sets every IV to 31. EVs stop at 252 a stat and 510 in all. With Minimal Grinding on (the
    default) every Pokémon battles at 31 IVs and 0 EVs, so, as in Imperium, the EVs are locked
    and the IVs only set Hidden Power's type.
  - **REPEL**, **FOLLOWER** and **AUTO RUN** switches, green when on.
  - The clock and the time of day at the top right.

  It opens once you have a Pokémon, but not in link rooms, the Safari Zone, the Bug Catching
  Contest or the Battle Pike and Pyramid, nor with BUTTON MODE L=A (L is the A button then).
- The Training Kit in the bag has the IVs & EVs editor too.

### Tooling
- New tests `l_menu`, `l_menu_time`, `stat_editor` and `stat_editor_mgm`; `dexnav` checks that
  L ends a search and keeps the chain, and every DexNav test opens it from the L menu, as does
  `old_save_test.sh`. `emurun` gains `expectbits8/16/32` (bitfields); `emu.py` gains `l_menu`,
  `set_save2`, `set_save3`, `expect_follower`, `expect_battler_ivs` and `new_game(minimal_grinding=False)`.

## 0.9.0-experimental (2026-10-25)

### Quality of life
- **Quick Rare Candies** (DECISIONS.md D33). After choosing the Pokémon, pick how many to use;
  at first it's all of them up to the level cap (UP/DOWN change it by 1, LEFT/RIGHT by 10, B
  goes back). They are used at once, with one message and a short sound instead of the level-up
  jingle, so the map music keeps playing, and without the two stat pages. Moves of every level
  passed are still learned, then the Pokémon evolves; the party menu stays open.
- **Fast Egg hatching** (D32). An Egg cycle is 8 steps instead of 256: a Togepi Egg hatches in
  about 90 steps, a starter's in about 170. Flame Body and Magma Armor still halve it.

### TMs, the Emerald Imperium way (D22)
- **Every TM costs ¥100**, Imperium's price, in every shop (they were ¥1,500–8,000). The
  Goldenrod Dept. Store's badge tiers still decide when the strong ones go on sale.
- **A TM clerk in the Violet City Mart** (the second clerk at the counter), from the Zephyr
  Badge on: Imperium's first vendor TMs, Electroweb, Icy Wind, Aerial Ace, Low Kick, Pluck,
  Snarl and Smack Down. The first time, the clerk also gives Bullet Seed, Bulldoze, Bug Bite and
  Stomping Tantrum, the TMs Imperium gives away before its second Gym; a save that already has
  the badge gets them too.

### Tooling
- New tests `rare_candy`, `egg_hatch` and `tm_clerk`; `qol_items` follows the Rare Candy
  question. `emu.py` gains `give_egg` and `expect_item_price`.

## 0.8.1-experimental (2026-10-25)

### Fixes
- **DexNav works in Dark Cave after Flash** (DECISIONS.md D31). It said it was too dark to
  search even after Flash, because Flash only widened the lit circle. Flash now lights the
  whole cave, as in Gold, Silver and Crystal. A save made in Dark Cave after Flash continues
  fully lit.
- **The DexNav Pokémon no longer runs away in caves and on water** (D31). It moved to another
  tile, up to twice, as you came close. Now it stays where it appeared, as in grass.

### Tooling
- New tests `dexnav_caves` (Dark Cave before and after Flash, a save made there before 0.8.1,
  Union Cave) and `dexnav_surf` (a DexNav search while surfing). Both fail on the 0.8.0 ROM.
- The play tests' path finding follows the target's elevation, so it doesn't route through
  water; `emu.py` has `set_save1` and `expect_save1` for SaveBlock1 fields.

## 0.8.0-experimental (2026-10-25)

### Gameplay
- **Emerald Imperium-style level caps** (DECISIONS.md D29): the cap is 85 before you beat the
  Elite Four the first time, as in Emerald Imperium, and climbs to it gym by gym:

  | Stage | No badges | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 (Elite Four) | Kanto | After the Kanto League |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | NORMAL caps | 15 | 24 | 33 | 42 | 50 | 58 | 66 | 75 | 85 | 90 | none (100) |
  | HARD caps | 12 | 21 | 30 | 39 | 47 | 55 | 63 | 72 | 85 | 90 | none (100) |
  | 0.7.x NORMAL | 11 | 16 | 21 | 25 | 31 | 36 | 38 | 45 | 56 | 70 | none |

  Every boss is at the cap (D21), so Falkner is 15, Clair 75, the Elite Four and Lance 85, the
  Kanto Gym Leaders and Blue 90, and Red stays at 100.
- **Other trainers follow the new curve.** Heart & Soul's trainers were made a few levels below
  its old caps; at battle time their levels are mapped onto the new caps in proportion (a
  Rocket Grunt's level-20 Koffing is 31 now; on Routes 26 and 27, the way to the Indigo
  Plateau, trainers go from 42–50 to 71–80). EASY and HARD still scale them by 10%, and none is
  above your cap.
- Wild Pokémon keep Heart & Soul's levels, as in Emerald Imperium: catch them and use the Rare
  Candy Box to bring them up to the cap. They are never above the cap.
- **Every Gym Leader has six Pokémon** (D30), and so do the rival from his second battle on, the
  Rocket executives in all their battles and Eusine. Falkner adds Natu, Fletchling and Murkrow
  to Heart & Soul's three; Bugsy has an Imperium-style team (Ariados, Pineco, Ledian,
  Butterfree, Yanma, Scyther); Whitney adds Furret and Girafarig and her team holds items;
  Morty adds Mimikyu; Chuck, Jasmine and Pryce bring all six as the 5th Gym too; Eusine has a
  rain team.
- **Route mini-bosses, as in Emerald Imperium** (D30): 28 trainers on the routes, 16 in Johto
  and 12 in Kanto, now have competitive teams at your level cap: held items, natures, abilities
  and chosen moves, themed by their class (a Hiker's Rock types, a Swimmer's rain team), with
  the smart boss AI. They have 3 Pokémon on the first routes, up to 6 later on and in Kanto.
  BALANCE.md lists them.

### Tooling
- `GetLevelOnCapCurve` (`src/caps.c`) maps a Heart & Soul level onto the current cap curve;
  `boss_teams.py` has the six-Pokémon teams and the route mini-bosses (`ROUTE_BOSSES`), 126
  bosses in all. `validate.py` reads a form's learnset from its base species when the form has
  none of its own.
- New test `route_bosses` (every mini-boss's team size and levels at the cap, and a battle to a
  result). Tests follow the new levels; `bugsy` and `whitney` bring six Pokémon (`bugsy` with
  the first care package's Charcoal and Eviolites, in 40 tries; `whitney` in 24), `whitney`'s
  Pokémon keep moves a player at 33 would keep (the default movesets at 33 drop Quilava's Fire
  moves), and `bosses_m5` checks Blue's Mega with the six built for him and gives each Kanto
  leader up to three battles to bring out the Mega.

## 0.7.1-experimental (2026-10-25)

### Gameplay
- **Bosses are at your level cap, HARD caps included** (DECISIONS.md D21). Every boss Pokémon
  is at the cap from your own LEVEL CAP setting: NORMAL (11, 16, 21, 25, 31, 36, 38, 45, 56,
  then 70) or HARD (8, 15, 20, 23, 29, 33, 37, 42, 54, then 70), on every difficulty. 0.7.0 used
  the NORMAL caps whatever the setting and added HARD's 10%, so with HARD caps Falkner was 12
  against your cap of 8; now he is 8. EASY no longer lowers bosses either (Falkner 11 with
  NORMAL caps); it still lowers other trainers by 10% and takes their items away.
- **Nothing is above your level cap** (D28). DexNav's level bonus (a fifth of the DexNav chain,
  and in 4% of searches 10 more) could give a Pokémon above the cap, such as a level-12 Turtwig
  at a cap of 8. Every Pokémon you meet or are given is now held at the cap:
  - DexNav (the level in the search window too), random encounters, fishing, Rock Smash, mass
    outbreaks, scripted wild battles, legendaries (e.g. Zapdos, 50, is met at 11 with no badges),
    roaming Pokémon, and gifts such as the Cianwood fisher's level-25 Tentacool.
  - Other trainers: their levels (after EASY's or HARD's scaling) are held at your cap. E.g. a
    Rocket Grunt's level-20 Koffing is 11 if you meet him with no badges (8 on HARD caps).
  - Wild battles where catching is off too: Route 41's level-100 Tentacruel and the post-game
    wild bosses (up to 100) are at the cap if you meet them before it reaches their level.
  - Levels are only ever lowered, never raised, and nothing changes with LEVEL CAP OFF.
- The challenge menu's descriptions say so: LEVEL CAP lists each table's caps ("Bosses are at
  the cap."), and EASY and HARD say their ±10% leaves bosses alone.

### Tooling
- `boss_teams.py` writes each boss's stage into `src/data/level_cap_bosses.h`; the battle
  computes the boss's level from the player's cap table (`GetBossLevel`, `src/caps.c`).
- Harness: `new_game(level_cap=...)` picks LEVEL CAP in the Difficulty tab.
- New test `level_cap_wild` (DexNav with a chain of 100, a level-50 outbreak, Zapdos and the
  Tentacool gift at the cap, on NORMAL and HARD caps). `boss_levels` adds HARD caps (Falkner at
  8, Petrel at 29 and 37) and a Grunt held at the cap; `difficulty` checks that EASY and HARD
  leave Falkner at the cap and scale Youngster Albert.

## 0.7.0-experimental (2026-10-25)

### Gameplay
- **Every boss Pokémon is at the level cap** (DECISIONS.md D21), not just the ace: every Gym
  Leader (all versions and rematches), the rival, Team Rocket's executives, Eusine, the Kimono
  Girls, the Elite Four, Lance, Blue and Red. Each battle's level is the NORMAL cap of the
  earliest point it can happen: 11 for Sprout Tower, Falkner and the first rival battle, then
  16, 21, 25, 31, 36, 38, 45 and 56 up to the Johto League, 70 for Kanto (the Kanto leaders,
  Blue, the Fighting Dojo rematches, the Kanto League) and 100 after the Kanto League (Red and
  every rematch then). With the Rare Candy Box you can always match a boss, never out-level it.
  - A boss fought later than its earliest point is raised to your cap when the battle starts:
    the Rocket Hideout with five or six badges (36 or 38), and the Kanto Gym teams in the
    Fighting Dojo or the Elite Four's rematch after the Kanto League (100). EASY and HARD
    still scale the result to 90% and 110%.
  - Petrel and Ariana in the Rocket Hideout are at 31 if you go there with four badges (the
    Lake of Rage needs Surf, the 4th badge's move); 0.6.0 had them at 34–36.
  - Red: all six at 100 in both battles (0.6.0: 96–100). He stays the hardest battle: the
    only Pokémon with EVs under Minimal Grinding, four Full Restores, prediction AI (D27).
- **Care packages are full of battle gear, Emerald Imperium-style** (D16). The 17 packages now
  hold 287 entries: competitive held items with the staples several times over the game
  (Leftovers ×7, Focus Sash ×8, Life Orb ×5, Assault Vest ×5, Heavy-Duty Boots ×5, Choice
  Band and Choice Specs ×3 each, Choice Scarf ×4, Weakness Policy ×3, Booster Energy ×4 and
  dozens more), all 18
  type-boosting items, all 18 type-resist Berries and the pinch Berries, 35 Sitrus and 19 Lum
  Berries, **93 PP Max** and 8 PP Up, X items, Max Elixirs, Elixirs and Max Ethers, besides
  the balls, healing and evolution items they had.
  - A package lists its contents in one message (two lines a page) instead of one message per
    item. An item whose Bag pocket is full goes to your PC, and you're told.
  - **Continuing an older save?** The gear for the packages you already received arrives too,
    one package per step out on a route or in a town ("PROF. ELM sent the battle gear an
    earlier package didn't have!").

### Tooling
- `tools/crystal_imperium/boss_teams.py` gives every boss a stage and sets its levels from
  `src/caps.c`; Heart & Soul's own boss teams get only their levels (`LEVEL_ONLY`). It also writes
  the boss list the battle code uses (`src/data/level_cap_bosses.h`).
- `tools/crystal_imperium/care_packages.py` writes the care package script from a table (item
  names and line widths come from the game's own data); CI checks it with `--check`. New var
  `VAR_CARE_PACKAGE_GEAR` (0x40E5) for the catch-up.
- `validate.py`: every boss at its stage's cap, no boss trainer missing from the list (Lt.
  Surge's teams were not matched by the boss patterns before), and Red's guard now asks for
  the most Full Restores, since the post-League rematches are at 100 like him.
- Harness: `fill_pocket`, `expect_pc_has`, `no_care_packages` (marks the packages and their gear
  as received, for tests that mustn't be interrupted); `prepared_team(level, items=True)` holds Life Orb,
  Leftovers, Choice Specs, Focus Sash, Choice Band and Expert Belt, all from the first three
  care packages.
- New test `boss_levels` (a boss raised to the cap with six badges and after the Kanto League;
  a Grunt unchanged). `care_packages` checks the new gear, the PC fallback and an older save
  catching up. The boss samples' teams hold items from the care packages the player has by then:
  the prepared six in `bosses_m3`, `bosses_m4` and for Koga, the planned sixes for Will, Bruno,
  Karen and Lance (Bruno and Karen now 12 tries), Bugsy's naive four a Charcoal (12 samples) and Whitney's
  Machop an Eviolite (24 samples). Chuck and Pryce are fought by sixes built for them with a game
  plan (the prepared six won once in 16 against Pryce). `bosses_m4` checks Archer's and the
  rival's Megas with a level-100 six, since at the cap the six can lose before the ace comes out;
  `bosses_m5`'s Janine check no longer leads with Earthquake against Levitate Weezing. `red`
  takes 24 tries (it won 5 and 2 of 12). `difficulty` and `red` expectations follow the new
  levels.

## 0.6.0-experimental (2026-10-24)

### Gameplay
- **HARD plays by Emerald Imperium's and Radical Red's rules.** On HARD every battle uses the
  SET style, so the game never asks "Will you switch Pokémon?" after you knock one out, and
  the Bag can't be used in trainer battles ("Items can't be used now."). Wild battles keep the
  Bag. START > OPTION shows BATTLE STYLE as SET, grayed out. HARD still raises trainer levels
  by 10% and uses HARD level caps. EASY and NORMAL are unchanged.
- **A Gen 5 look:**
  - **Battles** use mudskip's Black/White-style interface: BW healthboxes and text box,
    FIGHT / BAG / POKÉMON / RUN buttons, a move box with each move's type, PP and
    effectiveness, the party-ball bars and ability pop-ups.
  - **The summary screen** is RavePossum's Black/White-style one: a scrolling background, the
    Pokémon with a shadow and idle animation, Gen 5 type and status icons and move
    categories. A on the skills page cycles stats, IVs and EVs. START on the moves pages opens
    the move relearner, as before.
  - Move info in battle is on L (the BW box labels it L; Heart & Soul used START). R still
    toggles Mega Evolution, and throws the last-used ball from the action menu.
  - Moves can no longer be reordered with SELECT during a battle (Gen 4 and later behave this
    way, and the BW interface needs it); reorder them on the summary screen.
  - The options menu's BATTLE UI row (Heart & Soul's GEN 3 / GEN 4 healthboxes) is gone; the
    BW interface replaces both.
- **Red is the hardest battle in the game** (DECISIONS.md D27):
  - Levels 96–100 (the rematch after the Sinjoh story: all 100). Pikachu has Light Ball,
    Espeon Life Orb, Snorlax Leftovers, Venusaur Life Orb, Blastoise White Herb and Charizard
    Charizardite Y.
  - Competitive EVs on all six, and his are the only Pokémon that keep their EVs under
    Minimal Grinding.
  - The boss AI with move and switch prediction, and four Full Restores.
  - A sun team: Mega Charizard Y's Drought powers Chlorophyll Venusaur and Solar Beam.
  - He battles only the Kanto Champion: before the Kanto League he waits ("RED seems to be
    waiting for the KANTO CHAMPION."), so the level cap is gone when you fight him.

### Technical
- The heap is 8 KB larger (EWRAM 99.12% used): the BW battle windows take about 8 KB more
  during a battle, and without it boss battles that decompress big graphics mid-battle ran
  out of memory in the play tests. The Wild Variety pool shrank to the 567 Pokémon it holds.

### Tooling
- emurun: `waituntil32` runs until a value matches (e.g. the battle controller reaching the
  action menu), tapping a key meanwhile; `dump` writes memory to a file (the heap dump found
  the out-of-memory cause). Harness: `expect_battle_style`, `expect_window`.
- The battle autopilot can play a **game plan** (`plan=` in `autobattle`): for each of the
  opponent's Pokémon, which of yours attack it with which move, and which to switch in when
  the one out has none. `hold_item` gives a party Pokémon a held item; `sample_battle` takes
  a plan and a frame limit.
- Autopilot fixes: a forced switch compared menu slots (battle order) with party slots (field
  order) and could keep choosing a fainted Pokémon until the battle timed out; it now finds
  Pokémon by personality value and never retries a slot the game refused. A move the game
  refuses (Choice lock, Taunt, Encore) no longer stalls a battle.
- New tests: `hard_mode_rules`, `bw_ui`, `red`; `dexnav_wild_match` checks the variety pool's
  size. The boss samples got more tries, sized by measured win rates (`bosses_m3`: 8, Pryce
  16; Lance 24). Will, Bruno, Karen, Lance (`bosses_e4`) and Blue (`bosses_m5`) are fought by sixes
  playing a game plan. Red moved from `bosses_m5` to `red`. `validate.py` checks that Red's
  parties stay the strongest in the game.

## 0.5.1-experimental (2026-10-24)

### Fixes
- **DexNav's lists now match the wild Pokémon you meet.** Before, Wild Variety turned 30% of
  encounters into a random pick from about 445 Pokémon that DexNav couldn't list (on Route 29
  at night DexNav showed Hoothoot and Rattata while 6 of 12 test battles were other Pokémon),
  and with the randomizer on for wild Pokémon DexNav showed the unrandomized ones (12 of 12
  battles unlisted).
  - Wild Variety now gives each area a set for the day: up to six Pokémon in the grass and
    three Water-types on the water, in the DexNav row's free slots, evolved for the area's
    highest level. Variety encounters (still 30% by default, 5% per Pokémon in the grass) are
    one of the set, and DexNav lists the set after the area's own Pokémon. The sets change at
    midnight and differ between saves.
  - With the randomizer on and MAP SEEDED on, DexNav lists each slot's randomized Pokémon.
  - A mass outbreak's Pokémon is listed in the grass.
  - Fishing's variety Pokémon come from the water set. DexNav's detector finds what an
    encounter would turn up, and the caught-all marks count the variety Pokémon.
  - After becoming Champion, about a quarter of the day's sets end with a Legendary, Mythical,
    Ultra Beast or Paradox Pokémon (Water-types on the water), instead of 3% of variety
    encounters everywhere.
  - DECISIONS.md D24.

### Tooling
- emurun: `snap16` remembers a list of values (a DexNav row) and `tallynotin` checks against
  it (`@LIST`). Harness: `snap_dexnav_rows`, `fish_sample`, `set_save`, `expect_listed`,
  `new_game(random_wild=True)`.
- New tests: `dexnav_wild_match`, `dexnav_water_match`, `dexnav_randomizer`; `wild_variety`
  checks that DexNav lists no variety Pokémon with WILD VARIETY off.

## 0.5.0-experimental (2026-10-24)

### Gameplay
- **Smarter trainers:** on NORMAL and HARD every trainer uses the smart AI (it knows your
  team, picks the best move, switches smartly and plays around HP). EASY keeps the old AI.
- **Imperium-style bosses for the whole story:** Proton, Petrel, Ariana and Archer; every rival
  battle from Azalea to Victory Road; Morty, Chuck, Jasmine, Pryce (all three versions each)
  and Clair; the Kimono Girls; the Elite Four and Lance; the eight Kanto leaders, Blue and Red.
  Aces at the level cap (70 in Kanto; Red's is 90), full held items, natures, abilities and
  competitive moves. Every Gym Leader from the 5th Gym on, Archer, the rival on Victory Road,
  the Elite Four, Lance, Blue and Red Mega Evolve (Heracross, Steelix, Abomasnow, Altaria,
  Houndoom, Tyranitar, Alakazam, Beedrill, Lucario, Absol, Gyarados, Aerodactyl, Blastoise,
  Manectric, Venusaur, Gengar, Metagross, Camerupt, Pidgeot, Charizard Y).
- **Emerald Imperium's TMs:** 198 TMs. TM01–TM172 are Emerald Imperium's list in its order
  (all but its two custom moves, Dark Hole and Draco Barrage), TM173–TM198 the Heart & Soul
  TMs Imperium lacks. 28 TMs have a new number (TM03 Water Pulse is TM160, TM41 Torment TM179,
  TM70 Rock Climb TM192, TM92 Trick Room TM106, ...); the rest keep theirs.
  - The TM case holds all 198 TMs and 8 HMs, and each TM's description is its move's.
  - The Goldenrod Dept. Store 5F sells every TM: 71 from the start (including Heart & Soul's
    own stock, now cheaper), 155 from 3 badges, 178 from 6, all 198 from 8. Shop lists show
    each TM's move next to its number, as the bag does.
- **HMs without teaching:** carrying an HM, with its badge, is enough for any Pokémon in the
  party to use the field move (Cut, Surf, Strength, Rock Smash, Waterfall, Fly and Flash from
  the lead's party menu). Before, the Pokémon had to be able to learn the move.
- The Mega Stone shop's 6-badge tier counts badges (it unlocked with Jasmine's badge).
- Falkner's Rookidee knows Rock Smash instead of Steel Wing, which it can't learn.

### Fixes
- Teaching a move from the party menu's relearner (LEARN MOVES > TM MOVES) used up the TM even
  with REUSABLE TMS on.

### Save compatibility
- The TM case moved from SaveBlock1 to EWRAM, saved as counts in SaveBlock3. Saves from Heart &
  Soul 2.0.6 and earlier Crystal Imperium builds load: their TMs keep their moves (Heart &
  Soul's TM70 Rock Climb becomes TM192), including TMs in the item PC and held TMs.

### Tooling
- `tools/crystal_imperium/boss_teams.py` holds the boss teams; `validate.py` checks their
  moves are learnable and their aces sit at the cap, and resolves abilities given by macros.
- `tools/crystal_imperium/tm_list.py` holds the TM list and writes the TM constants, the item
  data (with descriptions wrapped to the bag box by glyph width), the shop lists and the old
  numbering for save conversion.
- Harness: Pokémon (Complex) from the debug menu, a prepared team for winnability checks,
  battles by trainer constant, `expectseen` for Mega forms; the autopilot skips moves with no
  PP. `set_var`, `fill_tm_case`, `save_and_continue`; bag checks read the TM case in EWRAM.
- New tests: `bosses_m3`, `bosses_m4`, `bosses_e4`, `bosses_m5`, `tm_case`, `tm_shop`,
  `hm_field_moves`.
  `tm_reusable` also teaches through the relearner; `old_save_test.sh` now saves Heart & Soul
  TMs and checks their conversion.
- `data/battle_anim_scripts.s` read the vanilla TM list (`IS_HNS` was undefined there), which
  only mattered once the TM list changed; `constants/tms_hms.h` now defines it for every user.

## 0.4.1-experimental (2026-10-24)

### Gameplay
- **DexNav shows every Pokémon on its main screen**, seen or not: no more question marks. Any
  of the area's Pokémon (land, water and hidden rows) can be registered with R and searched
  for with A right away. The top bar now reads SELECT: ALL, for the list of every Pokémon.
  A hidden Pokémon detected while walking still shows ??? until R is pressed or the player
  gets close.
- **DexNav searches no longer fail with "The Pokémon got away! Try moving more slowly."**
  Walking, running (Auto Run included) and biking all reach the Pokémon; sneaking with A is
  optional. Before, walking normally within 2 tiles or running/biking within 4 tiles scared
  it off, and with Auto Run on there was no way to sneak. A search now lasts 30 seconds
  (was 15).

### Tooling
- `dexnav` registers, searches for and catches a Rattata that has not been seen, walking up
  to it normally. `dexnav_any` turns Auto Run on and runs up to the Charmander it searched
  for. Both failed with "Try moving more slowly" before the fix.

## 0.4.0-experimental (2026-10-24)

### Gameplay
- **Key items from the first step:**
  - Rare Candy Box (unlimited Rare Candies, capped by the level cap; also without a Nuzlocke).
  - Infinite Repel (now an on/off switch that works).
  - Pokémon Box Link (the PC anywhere).
  - **Training Kit:** change a Pokémon's nature or cycle its ability any time.
  - **PokéVial:** full party heal outside battle, never runs out.

  Older saves receive whichever of them they lack on Continue.
- **DexNav** in the start menu from the first step:
  - Area lists with three **hidden Pokémon** per area; hidden Pokémon are also detected while
    walking.
  - Search levels and chains; R searches for the registered Pokémon.
  - **SELECT lists every Gen 1–9 Pokémon** (all 1,074: every evolution stage, regional
    forms, Legendaries), and any of them can be searched for in any area with wild Pokémon,
    at that area's levels. LEFT/RIGHT jump 100 entries.
- **Wild Variety** (Features tab, 30% by default): that share of wild encounters are any
  Gen 1–9 Pokémon, evolved as far as their level allows. Legendary and Mythical Pokémon join
  Wild Variety's random encounters after becoming Champion.
- 258 evolution families that had no source in the game now appear as hidden Pokémon on 249
  maps.
- **Easy Catch** (Features tab, on by default): every Poké Ball catches.
- **Difficulty selection** (Difficulty tab): EASY (trainer levels −10%, no trainer items),
  NORMAL, HARD (trainer levels +10%, HARD level caps).
- **Milestone care packages** from Prof. Elm after each badge and after becoming Champion,
  with supplies and every evolution item the game had nowhere: Linking Cord, Upgrade,
  Prism Scale, Sachet, Whipped Dream, Sun Stones, Apples, Sweets, Pots, Teacups, Armors,
  Leader's Crest, Metal Alloy, 999 Gimmighoul Coins, Scrolls.
- **Move relearner** in the party menu (level-up, egg, TM and tutor moves).

### Fixes
- DexNav no longer fails at random in small patches of grass.
- Wild Variety leaves the Bug-Catching Contest, the Battle Pike and the Battle Pyramid alone.
- A game saved during a DexNav search loads cleanly.

### Tooling
- The play tests also run on **VBA-M** at the commit Delta's GBA core pins
  (`tools/emurun/build_vbam_core.sh`, `run_all.sh vbam`), locally and in a second CI job. They have a pathfinding walker,
  bag checks and pointer-following addresses.
- New tests:
  - `qol_items`, `infinite_repel`, `relearner_training_kit`, `difficulty`, `autorun`
  - `pokevial`, `easy_catch`, `tm_reusable`
  - `dexnav`, `dexnav_any`, `dexnav_hidden`, `wild_variety`, `bug_contest`, `care_packages`
  - `story_opening`: the real story path from New Game to Elm's lab (starter, errand, Potion)
    and the first wild battle on Route 29, with no debug menu
  - `old_save_test.sh`: a Heart & Soul 2.0.6 save continued in Crystal Imperium
- `whitney` samples 12 battles (the naive team wins about 25%). `falkner` uses the autopilot.
- `tools/crystal_imperium/gen_hidden_encounters.py` generates the hidden tables. The validator
  reads the National Dex from `pokedex.h` (HnS numbers some forms below 1025) and parses nested
  evolution lists. It now reports 449 of 571 families with a source; the other 122 are
  legendary (DexNav's list from the start, Wild Variety after the Champion).
- Play tests run on a fixed cartridge clock (2026-10-24 01:30 UTC, advancing with emulated time),
  so they give the same results at any hour and on any host.

## 0.3.0-experimental (2026-10-23)

### Gameplay
- **Bugsy** rebuilt: Focus Sash Spinarak (Sticky Web), Pineco (Spikes, Rock Tomb), Ledian
  (Reflect, Light Screen), Eviolite Technician Scyther (Fury Cutter). Smart AI.
- **Whitney** rebuilt: Clefairy (Magic Guard; Metronome, Encore, Charm), Aipom (Fake Out,
  U-turn), Intimidate Stantler (Hypnosis), Scrappy Miltank (Rollout, Body Slam, Milk Drink,
  Attract). Smart AI; one Potion instead of Super Potion + Potion.
- Azalea and Goldenrod Gym trainers get defined movesets, abilities and levels close to the cap.

### Tooling
- Battle autopilot (`autobattle`) and win-rate sampling (`sample_battle`, `tally`,
  `expecttally`) in the emulator harness. `names.py` labels logs with species and move names.
- New tests: `bugsy`, `whitney`, `gym_trainers_m2`. Macros: `battle_style_set`.
- The validator now covers Bugsy and Whitney. It caught Aipom being given Technician
  (Ambipom's ability) during the rework.

## 0.2.0-experimental (2026-10-23)

### Gameplay
- **Mega Evolution** enabled for the 48 classic stone Megas and Mega Rayquaza. Press **R** in the move menu to Mega
  Evolve.
- A Mega Specialist on Goldenrod Dept. Store 5F gives the **Mega Ring** after the third badge
  and sells Mega Stones (₽10,000). More stones unlock at badges 6 and 8 and after becoming
  Champion.
- Boss Megas: Lance (Gyarados), Lance rematch (Salamence), Lance postgame (Charizard X),
  Red (Charizard Y).

### Fixes
- The gimmick trigger moved from START (taken by HnS's move info) to R.

### Tooling
- New play tests: `mega_evolution`, `mega_specialist`. New harness macro `give_item`.

## 0.1.0-experimental (2026-10-23)

Based on Pokémon Heart & Soul 2.0.6 (`167aa6d5`).

### Gameplay
- New **Minimal Grinding Mode** (Difficulty tab, ON by default). Every Pokémon battles with
  31 IVs and 0 EVs. Turning it on also enables max player IVs, no EV gain, NORMAL level caps
  and ×1.5 EXP.
- **Falkner** rebuilt: Pidgey (Tailwind), Rookidee (Hone Claws, Power Trip, Steel Wing) and
  Noctowl (Tinted Lens; Hypnosis, Air Cutter, Reflect, Mud-Slap); perfect IVs; Smart AI.
- Bird Keepers Rod and Abe and Elder Li get defined movesets, abilities and items.
- **Sleep Clause** is always on.
- The Goldenrod Flower Shop sells **Ability Capsule** (₽20,000) and **Ability Patch**
  (₽40,000) after the third badge.

### Tooling
- `tools/emurun`: a headless mGBA play-test harness with tests for Falkner, save/load and the
  Flower Shop.
- `tools/crystal_imperium/validate.py`: data validation and generated trainer/encounter
  databases.
- `tools/crystal_imperium/build.sh` and a CI workflow.
- Fixed `make check BUILD=hns` compilation (`fake_rtc.h` include order).
