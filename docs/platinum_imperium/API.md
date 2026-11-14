# Platinum Imperium: the stage 2 registry (frozen API)

Stage 2 Phase 0 (ENGINE_NOTES §5.1) reserved every shared ID that the Phase 2 tracks need. This
file lists them. **Everything here is frozen**: the values are stored in saves, in scripts or in
append-only tables, so a track may use them but must not renumber, rename or reorder them. A track
that needs a new entry asks the Phase 0 owner, who adds it at the end of the right list.

Numbers are as built at the end of Phase 0. Symbol addresses change with every build; tests find them
through the linker map (`t.sym(name)`).

## 1. Settings

No save-layout change: every setting is a renamed var or flag in `generated/vars_flags.txt`, chosen
from the safe pool (ENGINE_NOTES [V3]) and referenced nowhere else before the rename.
`tools/imperium/check.py --check` keeps them out of the banned ranges.

### Vars

| Name | ID | Was | Values (0 is the default) |
|---|---|---|---|
| `VAR_IMPERIUM_DIFFICULTY` | 0x406C | `VAR_UNUSED_0x406C` | 0 NORMAL, 1 EASY, 2 HARD (`IMPERIUM_DIFFICULTY_*`) |
| `VAR_IMPERIUM_LEVEL_CAP_MODE` | 0x406D | `VAR_UNUSED_0x406D` | 0 NORMAL caps, 1 HARD caps, 2 OFF (`IMPERIUM_LEVEL_CAP_*`) |
| `VAR_IMPERIUM_CARE_PACKAGES` | 0x406E | `VAR_UNUSED_0x406E` | care packages given so far |
| `VAR_IMPERIUM_SETTINGS_VERSION` | 0x406F | `VAR_UNUSED_0x406F` | 1 (`IMPERIUM_SETTINGS_VERSION`) after a new game; 0 in a vanilla save |
| `VAR_IMPERIUM_SPARE_1` | 0x40EA | `VAR_UNUSED_0x40EA` | spare |
| `VAR_IMPERIUM_SPARE_2` | 0x40EB | `VAR_UNUSED_0x40EB` | spare |
| `VAR_IMPERIUM_SPARE_3` | 0x40EC | `VAR_UNUSED_0x40EC` | spare |
| `VAR_IMPERIUM_SPARE_4` | 0x40EE | `VAR_UNUSED_0x40EE` | spare |

Out-of-range values of the two mode vars read as NORMAL.

### Flags (a set flag means the feature is on)

| Name | ID | New game | Meaning |
|---|---|---|---|
| `FLAG_IMPERIUM_MINIMAL_GRINDING` | 0x053C | ON | 31 IVs / 0 EVs stat formula (track F) |
| `FLAG_IMPERIUM_FAST_BATTLES` | 0x053D | ON | fast text, waits and bars (track D) |
| `FLAG_IMPERIUM_FAST_INTRO` | 0x053E | ON | short battle intro (track D) |
| `FLAG_IMPERIUM_EXP_SHARE_ALL` | 0x053F | ON | EXP for the whole party (track D) |
| `FLAG_IMPERIUM_EXP_BOOST` | 0x0540 | ON | ×1.5 EXP (track D) |
| `FLAG_IMPERIUM_REUSABLE_TMS` | 0x0541 | ON | TMs are not used up (track C) |
| `FLAG_IMPERIUM_INFINITE_REPEL` | 0x0542 | OFF | Infinite Repel switched on (tracks A, C) |
| `FLAG_IMPERIUM_SLEEP_CLAUSE` | 0x0543 | ON | Sleep Clause (tracks D, E) |
| `FLAG_IMPERIUM_EASY_CATCH` | 0x0544 | OFF | easier catching (no track yet; no battle bit, see §2) |
| `FLAG_IMPERIUM_SETTINGS_INITIALIZED` | 0x0545 | ON | `InitNewGame` ran with Imperium defaults |
| `FLAG_IMPERIUM_SPARE_1` .. `_6` | 0x0546 .. 0x054B | OFF | spares |

Free safe flags left for later: 0x006D, 0x006F, 0x0094–0x0096, 0x0167–0x0171, 0x02CD–0x02D9,
0x054C–0x054F. Free vars: the other `VAR_UNUSED_0x40xx` entries. `0x0974–0x0976` and `0x0990` stay
reserved for the debug-menu port.

### New-game defaults

`res/field/scripts/init_new_game.s` (`InitNewGame`, run synchronously once per new game) sets the
flags above, sets the vars (`VAR_IMPERIUM_SETTINGS_VERSION` = 1), sets
`FLAG_IMPERIUM_SETTINGS_INITIALIZED` and runs `GiveRunningShoes`. Mom's later hand-over in
`twinleaf_town_player_house_1f/scripts.s` is untouched (giving the shoes again is harmless).

### Options: auto-run

`Options` keeps its size (u16). Its spare bit 15 is now `autoRunOff`: **0 = auto-run on**, which is
what `Options_Init` and every vanilla save already hold.

```c
BOOL Options_GetAutoRunOff(const Options *options);
void Options_SetAutoRunOff(Options *options, BOOL autoRunOff);
```

### C API (`include/imperium_settings.h`, `src/imperium_settings.c`, Static main)

```c
int  Imperium_GetDifficulty(SaveData *);            void Imperium_SetDifficulty(SaveData *, int);
int  Imperium_GetLevelCapMode(SaveData *);          void Imperium_SetLevelCapMode(SaveData *, int);
BOOL Imperium_IsMinimalGrinding(SaveData *);        void Imperium_SetMinimalGrinding(SaveData *, BOOL);
BOOL Imperium_AreFastBattlesOn(SaveData *);         void Imperium_SetFastBattles(SaveData *, BOOL);
BOOL Imperium_IsFastIntroOn(SaveData *);            void Imperium_SetFastIntro(SaveData *, BOOL);
BOOL Imperium_IsExpShareAllOn(SaveData *);          void Imperium_SetExpShareAll(SaveData *, BOOL);
BOOL Imperium_IsExpBoostOn(SaveData *);             void Imperium_SetExpBoost(SaveData *, BOOL);
BOOL Imperium_AreTMsReusable(SaveData *);           void Imperium_SetReusableTMs(SaveData *, BOOL);
BOOL Imperium_IsInfiniteRepelOn(SaveData *);        void Imperium_SetInfiniteRepel(SaveData *, BOOL);
BOOL Imperium_IsSleepClauseOn(SaveData *);          void Imperium_SetSleepClause(SaveData *, BOOL);
BOOL Imperium_IsEasyCatchOn(SaveData *);            void Imperium_SetEasyCatch(SaveData *, BOOL);
u16  Imperium_GetCarePackagesGiven(SaveData *);     void Imperium_SetCarePackagesGiven(SaveData *, u16);
u16  Imperium_GetSettingsVersion(SaveData *);       BOOL Imperium_AreSettingsInitialized(SaveData *);

// For code that already holds a VarsFlags* (e.g. pokemon.c through SaveData_Ptr()).
int  Imperium_VarsFlags_GetDifficulty(VarsFlags *);
int  Imperium_VarsFlags_GetLevelCapMode(VarsFlags *);
BOOL Imperium_VarsFlags_IsMinimalGrinding(VarsFlags *);
BOOL Imperium_VarsFlags_CheckSetting(VarsFlags *, u16 flagID);
void Imperium_VarsFlags_SetSetting(VarsFlags *, u16 flagID, BOOL on);

u32  Imperium_FieldBattleStatusBits(SaveData *);    // §2
u8   LevelCap_Get(SaveData *);                       // §3
u8   LevelCap_ForBadges(int badges, int mode, BOOL champion);
```

Scripts can use the constants in `include/constants/imperium.h` (included by `asm/macros/scrcmd.inc`).

## 2. Battle plumbing

Battle code has no `SaveData`. Settings reach a battle through the `FieldBattleDTO`:

- **`battleStatusMask` bits 8–15** (`include/constants/battle.h`):

  | Bit | Name | Set when |
  |---|---|---|
  | 8 | `BATTLE_STATUS_FAST_BATTLE` | `FLAG_IMPERIUM_FAST_BATTLES` |
  | 9 | `BATTLE_STATUS_FAST_INTRO` | `FLAG_IMPERIUM_FAST_INTRO` |
  | 10 | `BATTLE_STATUS_HARD` | difficulty HARD |
  | 11 | `BATTLE_STATUS_SLEEP_CLAUSE` | `FLAG_IMPERIUM_SLEEP_CLAUSE` |
  | 12 | `BATTLE_STATUS_EXP_SHARE_ALL` | `FLAG_IMPERIUM_EXP_SHARE_ALL` |
  | 13 | `BATTLE_STATUS_MINIMAL_GRINDING` | `FLAG_IMPERIUM_MINIMAL_GRINDING` |
  | 14 | `BATTLE_STATUS_EXP_BOOST` | `FLAG_IMPERIUM_EXP_BOOST` |
  | 15 | `BATTLE_STATUS_EASY` | difficulty EASY |

  `BATTLE_STATUS_IMPERIUM_SETTINGS` masks all eight. Battle scripts can test them with
  `CompareVarToValue OPCODE_FLAG_SET, BTLVAR_BATTLE_SYS_STATUS, BATTLE_STATUS_...`; C code with
  `BattleSystem_GetBattleStatusMask(battleSys) & BATTLE_STATUS_...`.
- **`FieldBattleDTO.levelCap`** (u8, at the end of the struct) is `LevelCap_Get` at battle start.
  `BattleSys_New` copies it into `BattleSystem.levelCap`; read it with
  `u8 BattleSystem_GetLevelCap(BattleSystem *)`, which returns `MAX_POKEMON_LEVEL` when the stored
  cap is 0 (no cap).

Both are written by `FieldBattleDTO_ApplyImperiumSettings(dto, saveData)`
(`src/field_battle_data_transfer.c`), called at the end of `FieldBattleDTO_InitFromGameState` and
again in `Encounter_NewVsFirstBattle` after it overwrites the mask (ENGINE_NOTES [V8]). It does
nothing when `battleType & (BATTLE_TYPE_LINK | BATTLE_TYPE_FRONTIER)`. Battles that never call
`InitFromGameState` (link and Union Room through `InitWithPartyOrder`, Wi-Fi through
`InitWithNormalizedMonLevels`) get neither. Frontier facilities call `InitFromGameState` with
`BATTLE_TYPE_FRONTIER` already set, so they are skipped too. Safari, Pal Park and the catching
tutorial do receive the bits; a track that changes gameplay must still gate its own effect
(ENGINE_NOTES §1.6 rule 1, e.g. `BATTLE_TYPE_NO_EXPERIENCE` for EXP).

**Is the DTO saved or sent?** No. `FieldBattleDTO` is allocated on a heap for one battle
(`FieldBattleDTO_New`, and `frscrcmd.c` for the Frontier). Nothing copies it whole: the link code
sends parties, `TrainerInfo` and `Trainer` structs, never the DTO. The battle recorder
(`src/unk_0202F1D4.c`, `sub_0202F8AC`) copies selected fields one by one, including
`battleStatusMask` but not `levelCap`; recordings are only made of link and Frontier battles, which
never get the Imperium bits or a cap, and a played-back recording has `levelCap` 0, which reads as
"no cap". The new field is at the end, so no existing offset moved.

No behavior uses the bits or the cap yet; the tracks will.

## 3. Level caps

`LevelCap_Get(saveData)` = `LevelCap_ForBadges(TrainerInfo_BadgeCount(...), VAR_IMPERIUM_LEVEL_CAP_MODE, SystemFlag_CheckGameCompleted(...))`.

| Badges | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Game completed |
|---|---|---|---|---|---|---|---|---|---|---|
| NORMAL (mode 0) | 15 | 24 | 33 | 42 | 50 | 58 | 66 | 75 | 85 | 100 |
| HARD (mode 1) | 12 | 21 | 30 | 39 | 47 | 55 | 63 | 72 | 85 | 100 |
| OFF (mode 2) | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |

The badge count is the number of set bits in `TrainerInfo.badgeMask`; counts above 8 read as 8.

## 4. Reserved append-only IDs (stubs)

### Script commands (`include/data/scripts/scrcmd.h`, `asm/macros/scrcmd.inc`, `src/scrcmd_imperium.c`)

| ID | Macro | Stub result |
|---|---|---|
| 0x348 | `FindPartySlotForFieldMove destVar, move` | `destVar` = 6 (`MAX_PARTY_SIZE`, none) |
| 0x349 | `ImperiumToggleSetting flagID, destVar` | `destVar` = FALSE, nothing toggled |
| 0x34A | `ImperiumOpenQuickMenu destVar` | `destVar` = 0, no menu |
| 0x34B | `ImperiumGiveCarePackage destVar` | `destVar` = FALSE, nothing given |

The argument layouts are frozen. `move` and `flagID` go through `ScriptContext_GetVar`, so they may
be values or vars.

### Battle command (`include/data/scripts/btlcmd.h`, `asm/macros/btlcmd.inc`, `battle_script.c`)

| ID | Macro | Stub |
|---|---|---|
| 0xDF | `CheckSleepClause battler, jump` | reads both arguments, never jumps |

### Items (`generated/items.txt`, before `MAX_ITEMS` = 473)

| ID | Constant | Data | `fieldUseFunc` | Icon (reused) |
|---|---|---|---|---|
| 468 | `ITEM_RARE_CANDY_BOX` | `res/items/data/rare_candy_box.json` | `ITEM_USE_FUNC_RARE_CANDY_BOX` (25) | Rare Candy |
| 469 | `ITEM_INFINITE_REPEL` | `infinite_repel.json` | `ITEM_USE_FUNC_INFINITE_REPEL` (26) | Repel / Max Repel palette |
| 470 | `ITEM_BOX_LINK` | `box_link.json` | `ITEM_USE_FUNC_BOX_LINK` (27) | Vs. Recorder |
| 471 | `ITEM_POKE_VIAL` | `poke_vial.json` | `ITEM_USE_FUNC_POKE_VIAL` (28) | Potion |
| 472 | `ITEM_TRAINING_KIT` | `training_kit.json` | `ITEM_USE_FUNC_TRAINING_KIT` (29) | Explorer Kit |

All five are key items (`POCKET_KEY_ITEMS`), price 0, `preventToss`, no battle use, placeholder
descriptions. `sItemUseFuncs` (`src/item_use_functions.c`) has placeholder rows that behave like
`ITEM_USE_FUNC_BAG_MESSAGE` (USE prints the "can't use" message). Pal Park and the GTS do not know
these IDs (`gbaID` is `GBA_ITEM_NONE`).

### Text banks (`generated/text_banks.txt`)

| ID | Bank | File | Owner |
|---|---|---|---|
| 724 | `TEXT_BANK_IMPERIUM_FIELD` | `res/text/imperium_field.json` | track B |
| 725 | `TEXT_BANK_IMPERIUM_PARTY` | `res/text/imperium_party.json` | track C |
| 726 | `TEXT_BANK_IMPERIUM_BATTLE` | `res/text/imperium_battle.json` | track D |
| 727 | `TEXT_BANK_IMPERIUM_OPTIONS` | `res/text/imperium_options.json` | track G |
| 728 | `TEXT_BANK_IMPERIUM_NEWGAME` | `res/text/imperium_newgame.json` | track G |

Each holds one placeholder message (`<Bank>_Text_Placeholder`) so it builds. Remember that the
options menu tables are u8: message IDs used there must stay below 256.

### Global scripts (`res/field/scripts/unused_0397.s`)

| Script ID | Label | Use |
|---|---|---|
| 9900–9907 | `Unused397_Dummy1..8` | vanilla, unreferenced; free for track B |
| 9908 (`SCRIPT_ID(UNUSED_0397, 8)`) | `ImperiumTest_TrainerBattle` | test mailbox: trainer battle with `VAR_0x8004` |

The range has room up to 9949.

### New source files (`platinum.us/main.lsf.in`, Static main)

`src/imperium_settings.c`, `src/imperium_test.c`, `src/scrcmd_imperium.c`.

## 5. Test mailbox

`ImperiumTestMailbox gImperiumTest` (`include/imperium_test.h`, `src/imperium_test.c`, Static main)
lets a play test drive the game. It is always present and does nothing while `cmd` is 0.

- `src/field_system.c` `HandleFieldInput` calls `ImperiumTest_Refresh` every field frame.
- `src/overlay005/field_control.c` `FieldInput_Process` calls `ImperiumTest_Process` after the
  frame-table scripts and trainer sight checks, so commands run only on a frame where the field is
  processing input: no script or field task running, and the player standing still
  (`PLAYER_MOVE_STATE_NONE`). The frame a step ends is skipped, so a command never preempts that
  step's events (step counters, warps, wild encounters). A command written while an earlier one is
  still BUSY waits for the next frame instead of being dropped.
- `BattleSys_New` calls `ImperiumTest_RecordBattleStart`.

### Layout (layout version 1)

| Offset | Field | |
|---|---|---|
| 0x00 | `u32 magic` | `0x494D5054` ('IMPT') |
| 0x04 | `u16 layoutVersion` | 1 |
| 0x06 | `u16 numVars` | `NUM_VARS`; `VarsFlags` = `u16 vars[numVars]`, then `u8 flags[]` |
| 0x08 | `SaveData *saveData` | refreshed every field frame |
| 0x0C | `VarsFlags *varsFlags` | |
| 0x10 | `Party *party` | `{int capacity; int count; Pokemon mons[6]}` |
| 0x14 | `Bag *bag` | every pocket in a row, `BagItem {u16 item, u16 quantity}` |
| 0x18 | `TrainerInfo *trainerInfo` | `badgeMask` at +0x1A |
| 0x1C | `FieldSystem *fieldSystem` | 0 until the field first runs |
| 0x20 | `Options *options` | bit 15 = `autoRunOff` |
| 0x24 | `PlayerData *playerData` | `runningShoes` (u16) at +2 |
| 0x28 | `u32 fieldFrames` | |
| 0x2C | `u16 cmd` | write last |
| 0x2E | `u16 args[4]` | |
| 0x36 | `u16 status` | 0 idle, 1 busy, 2 done, 3 error |
| 0x38 | `u16 result` | 1 if the item or Pokémon was added |
| 0x3A | `u16 sizeofPokemon` | 0xEC |
| 0x3C | `u32 battleCount` | battles started since power-on |
| 0x40 | `u32 lastBattleType` | |
| 0x44 | `u32 lastBattleStatusMask` | as the battle received it |
| 0x48 | `u8 lastBattleLevelCap` | `BattleSystem_GetLevelCap` of the last battle |
| 0x49 | `u8 levelCap` | `LevelCap_Get`, every field frame |
| 0x4A | `u16 mapHeaderID` | every field frame |
| 0x4C | `u16 playerX`, `u16 playerZ` | every field frame |
| 0x50 | `u16 pendingCmd` | internal |
| 0x54 | `SaveBlockInfo *saveBlockInfo` | `&saveData->blockInfo[0]`, 12 bytes each; every 64 field frames |
| 0x58 | `u32 mainArenaFree` | main RAM no heap uses |
| 0x5C | `u32 appHeapFree`, `u32 systemHeapFree` | free bytes in the APPLICATION and SYSTEM heaps |

### Commands

| cmd | Name | Args | Done when |
|---|---|---|---|
| 1 | RUN_SCRIPT | scriptID, then `VAR_0x8004..0x8006` | the script has ended and the field is free |
| 2 | WARP | mapHeaderID, x, z | the map change (Fly's map-change task, facing down) is over |
| 3 | START_TRAINER_BATTLE | trainerID | the battle is over (script 9908: `StartTrainerBattle`, black out if lost) |
| 4 | GIVE_ITEM | item, quantity | at once (`Bag_TryAddItem`; ERROR if the bag is full) |
| 5 | GIVE_MON | species, level | at once (`Pokemon_GiveMonFromScript`; ERROR if the party is full) |
| 6 | PING | – | at once; tells a test the field is free |
| other | – | – | ERROR at once |

Protocol: write `args`, `status = 0`, then `cmd`. The game clears `cmd` when it takes the command;
wait for `status` 2 or 3 with `cmd` and `pendingCmd` both 0.

### Python helpers (`tools/dsrun/playtest.py`)

| Helper | |
|---|---|
| `t.new_game()` | power-on to the first frame the player can move in a new game (about 7,900 frames, 20 s) |
| `t.wait_field()` | run until the field is free (a PING succeeds) |
| `t.mailbox_cmd(cmd, *args, timeout=6000, mash=None, on_frame=None)` | run a command; `mash="A"` presses A while waiting (battles, dialogue) |
| `t.mb(field)` | read a mailbox field by name |
| `t.const(name)` | a generated constant (`FLAG_*`, `VAR_*`, `ITEM_*`, `SPECIES_*`, `TRAINER_*`, `MAP_HEADER_*`, ...) |
| `t.var(name)`, `t.set_var(name, v)`, `t.flag(name)`, `t.set_flag(name, on)` | saved vars and flags |
| `t.badge_mask()`, `t.set_badge_mask(m)` | `TrainerInfo.badgeMask` |
| `t.party_count()`, `t.party_species(slot)`, `t.party_level(slot)` | the party (decrypts the Pokémon data) |
| `t.bag_quantity(item)`, `t.running_shoes()`, `t.options_word()` | |
| `t.wait_until(cond, timeout)` | |

`t.new_game()` waits on game state, not frame counts: it reads the running application from
`main.c`'s `sApplication` and the Rowan intro's state (`RowanIntro.state`, parsed from the enum in
`rowan_intro_app.c`). It presses A through the title and NEW GAME, chooses NO INFO NEEDED, touches
YES or the Poké Ball when those screens wait for a touch, keeps the default boy, accepts the default
names (START, then A on an empty keyboard), and presses A through the opening scene until a PING
succeeds. A track that changes the intro (track G) must keep it working.

### Play tests

| Test | Checks |
|---|---|
| `boot` | the ROM boots without BIOS files and runs its intro |
| `settings_defaults` | every Imperium flag and var after a new game, Running Shoes owned, Options bit 15 clear, cap 15 |
| `level_cap` | the cap table for every badge count in NORMAL and HARD, OFF, and the cap and settings bits three trainer battles receive (0 badges: 15; 8 badges: 85 with HARD; game completed: 100 with EASY) |
| `mailbox` | GIVE_ITEM, GIVE_MON, WARP, START_TRAINER_BATTLE, RUN_SCRIPT, a command queued while another is BUSY, ERROR on an unknown command |
| `measure` | save block sizes (fails unless they equal vanilla's), unused main RAM and free heap with the field running |
