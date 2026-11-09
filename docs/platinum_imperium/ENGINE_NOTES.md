# Platinum Imperium: engine notes

Platinum Imperium brings Crystal Imperium's systems (`docs/crystal_imperium/README.md`) to
Pokémon Platinum on the DS. It is built on **pret/pokeplatinum** at `62bdaacdc` (2026-11-06).
RavePossum's debug menu comes from **ppexp** (merge `88a2d615b`, on top of pokeplatinum
`4ca3e1adc`, which is 406 commits behind our base).

These notes combine six read-only surveys: field/options/scripts, EXP/levels/items, trainers/AI/battle
speed, build/memory/save/text, species/Gen 5–9, and emulation/testing. Nothing in pokeplatinum has
been built or run yet. Every file path is relative to the pokeplatinum root unless it says otherwise.
Line numbers refer to `62bdaacdc`.

Where the surveys disagreed or were unsure, the source was checked directly (read and grep only).
Those checks are marked **[verified]**. The full list is in [§0](#0-verification-log).

---

## 0. Verification log

| # | Claim | Result |
|---|---|---|
| V1 | ppexp debug menu key: R+X (field survey) or R+START (infra and levels surveys) | **R held + X.** ppexp `src/overlay005/field_control.c:177-190` turns `input->menu` (X pressed) into `debugMenu` while `heldKeys & DEBUG_KEY` (`PAD_BUTTON_R`, `include/constants/debug_menu.h:11`). START works only with BUTTON MODE START=X (`src/system.c:398`). |
| V2 | The registered key item is on SELECT (levels survey) | **Wrong: it is Y.** `src/overlay005/field_control.c:134-135` sets `input->registeredItem` on `PAD_BUTTON_Y`. SELECT is not read in the field. |
| V3 | Number of free flags: 103 (field survey) or 159 (infra survey) | There are **103** `FLAG_UNUSED_0x....` entries, all below `NUM_FLAGS` 2912, so all of them are saved. Not all are free:<br>• `FLAG_UNUSED_0x0000` is flag 0. Do not use it.<br>• `FLAG_UNUSED_0x04E4` is **set** by `res/field/scripts/init_new_game.s:73`.<br>• `0x03BF–0x03D9` (27 flags) are inside `HIDDEN_ITEM_FLAGS_START..END` (lines 733–1018). Hidden-item flags are computed from the script ID (`src/script_manager.c:502`), so avoid these 27.<br>• `0x0974–0x0976` and `0x0990` are taken by the ppexp debug menu.<br>That leaves **about 70 safe flags**. The safest are 0x006D, 0x006F, 0x0094–0x0096, 0x0167–0x0171, 0x02CD–0x02D9 and 0x053C–0x054F.<br>All **20 `VAR_UNUSED_0x40xx`** are referenced nowhere in `src/`, `res/`, `include/` or `asm/`.<br>The figure 159 could not be reproduced. 138 flag lines contain "UNUSED", but names such as `FLAG_OBTAINED_HIDDEN_UNUSED_NUGGET_*` are real flags. |
| V4 | Rare Candy is removed from the bag at `party_menu/main.c:2700` and `callbacks.c:1118/1203` | **Only at `main.c:2700`.**<br>• `callbacks.c:1118` is in `TeachMove`, used for TMs.<br>• `callbacks.c:1203` is the PP-item path.<br>• **Trap:** `TeachMove` removes `usedItemID` whenever it is not `ITEM_NONE` and the move is not an HM. Vanilla avoids a double removal only because `start_menu.c:1029` resets `usedItemID` to `ITEM_NONE` for the level-up move round trip. A Rare Candy Box design that keeps the item ID through that round trip would make `TeachMove` remove the box. Guard both places. |
| V5 | `GF_ASSERT` does nothing offline | **Confirmed.** It is compiled in (`meson.build:72 -DPM_KEEP_ASSERTS`), but `ErrorHandling_AssertFail` acts only when `CommManager_IsInitialized()` (`src/error_handling.c:11-16`). Save-size, overlay-overlap and heap asserts are therefore silent. |
| V6 | How to build without the SHA-1 check | `all: release check` (`Makefile:96`). **`make release`** runs setup and `rom` without the check. `make debug` also builds `debug.nef` and `overlay.map`. |
| V7 | Trainer level scaling needs the save data passed down | `Trainer_Encounter(dto, saveData, heapID)` **already receives `saveData`** (`src/trainer_data.c:25`). Only the static `TrainerData_BuildParty(dto, battler, heapID)` (line 176) needs the extra parameter. |
| V8 | `battleStatusMask` bits 8 and up are free, and the first battle overwrites the mask | Bits 0–7 are used (`include/constants/battle.h:112-119`). `src/encounter.c:659` assigns `dto->battleStatusMask = BATTLE_STATUS_FIRST_BATTLE`, so OR new bits in after that. |
| V9 | Overlay layout of the battle chain | Confirmed in `platinum.us/main.lsf.in`: `overlay11` comes after `nintendo_wfc` (620); `battle_anim` (627), `battle_sub_menus` (655) and `trainer_ai` (670) all come after `overlay11`; `battle` comes after `battle_anim` (682). There are 122 overlays and 1012 `Object src/` lines. |
| V10 | Fixed limits | All confirmed:<br>• `Options` has 15 bits used and 1 spare (`include/game_options.h:8-16`).<br>• The options menu has `cursor : 3` and a literal `% 7` (`options_menu.c:83, 903, 912`).<br>• `MAX_START_MENU_OPTIONS` is 7.<br>• The day-care counter test is `steps == Daycare_GetEggCycleLength()` (`daycare.c:951`), and the length is 255 or 230.<br>• Trainer species uses `& 0x3FF` with `TRAINER_MON_FORM_SHIFT 10`.<br>• A learnset entry is `move : 9` / `level : 7` with `MAX_LEARNSET_ENTRIES 20`.<br>• `WaitButtonABTime 30` appears 395 times (plus 30×15, 8×60, 2×7).<br>• The `PlayerSave` padding is after `Options`, and `Options` is copied by value into the battle recording (`struct_0202F298.h:17`). |
| V11 | Emulation survey assumed HG/SS game codes (IPKE/IPGE, IR cartridge) | Our ROM is **Platinum, serial `CPUE`** (`platinum.us/rom_rev1.ini:4`). There is no IR cartridge. Keep `CPUE` so melonDS 0.9.5 in Delta picks the right save type. That the database entry is 512 KB flash is still **to verify**. |
| V12 | Trainer counts | 928 trainer JSON files (IDs 0–927), 180 of them `dummy_*`. `generated/species.txt` has 496 `SPECIES_*` lines. `ITEM_SECRET_KEY` = 467 and `MAX_ITEMS` = 468. |

---

## 1. Overview: build, toolchain, and the constraints behind every change

### 1.1 Build system

- **Driver.** The `Makefile` wraps meson and ninja. The first run downloads meson 1.12.0,
  **metroskrew 0.1.3** (native Linux runners for the Metrowerks `mwccarm`/`mwldarm`/`mwasmarm`),
  the NitroSDK/NitroSystem/NitroWiFi/NitroDWC/libvct wraps from `github.com/ntrtwl`, metang, and
  yyjson. The first build needs network access to GitHub and wrapdb. Host packages: `gcc-arm-none-eabi`
  (only to assemble script data), ninja, python3, bison and flex, libpng, `libc6:i386`.
- **Build targets.**
  - `make release`: the hack build, no SHA-1 check.
  - `make debug`: `build/debug.nef` and `overlay.map` for GDB, plus `EmulatorLog` (`src/debug.c`, `docs/logging.md`).
  - Plain `make` fails for us because it also runs `check` (SHA-1). Delete `check` from `all:` in our fork.
- **Output.** `build/pokeplatinum.us.nds`. To rename it, follow ppexp commit `dee08070d`: change the
  `meson.build` project and target name and the Makefile `rom:` target. Change the banner title in
  `platinum.us/rom_rev1.ini`.
  - **Keep `serial = CPUE`**: Delta's save-type detection depends on it (§4).
  - **Keep `maker = 01`**: `src/boot.c:41` calls `OS_Terminate` otherwise.
- **Adding code.** Add an `Object src/...c` line to `platinum.us/main.lsf.in`, under `Static main`
  or under an `Overlay` block. `tools/scripts/lsfgen.py` generates `platinum.us/main.lsf` and
  `src/meson.build`. **Never edit the generated files.**
- **Data pipeline.**
  - JSON goes through C processors in `tools/dataproc/src/` (`trainerproc`, `speciesproc`, `itemproc`, `moveproc`, …).
  - Text JSON goes through `tools/msgenc` into `pl_msg.narc`. Each bank gets a header, `res/text/bank/<bank>.h`.
  - Field, battle, AI and animation scripts are GNU-as macro bytecode (`asm/macros/*.inc`), built by `tools/scripts/make_script_bin.sh`.
  - Archives are packed by `tools/nitroarc` (`.narc` + `.naix`) and placed by `tools/nitrorom` using `platinum.us/filesys.csv`.
  - `generated/*.txt` enum lists go through metang into C headers.

### 1.2 Compiler

There is **no GCC or NONMATCHING path**. All game code is C compiled by `mwccarm` with
`-O4,p -enum int -char signed -ipa file -lang c99`, thumb by default (`include/pch/global_pch.h`).
Write C99, with no C11 features. Overlay addresses are laid out again from the `After` chains, and no
hard-coded RAM addresses were found in `src/`. Moving to GCC would mean porting the SDK subprojects;
that is out of scope.

### 1.3 Memory

- **Main RAM.** The main binary plus BSS ends near `0x021D0D80`. The tallest overlay chain is
  `nintendo_wfc → overlay11 → battle_anim → battle` and ends near `0x02271000`. The heap arena runs from
  there to about `0x023E0000`.
- **Root heaps.** They take `0x13B810` (`src/system.c:111-136`): SYSTEM `0xD200`, SAVE `0x20E00`,
  APPLICATION `0x10D800`. The estimated slack is **about 150–200 KB**. This was inferred from symbol names
  and must be measured.
  - The field uses FIELD1 `0xC4000`, FIELD2 `0x1C000` and FIELD3 `0x4000`. Battle uses `0xB0000`.
  - At most 24 child heaps can be alive at once.
- **Where code goes.**
  - Field code goes in `overlay5`, battle logic in `battle`, AI in `trainer_ai`.
  - Code called from several overlays goes in `Static main`, for example a level-cap helper or settings getters. Every byte there is permanent and pushes every overlay up.
  - `src/pokemon.c`, `trainer_data.c`, the party menu, the summary screen, `start_menu.c` and `item_use_pokemon.c` are already in main.
- **Shared overlay slot.** `battle_anim`, `trainer_ai` and `battle_sub_menus` take turns in one RAM
  slot, and `battle` sits directly after `battle_anim` **[V9]**. If `trainer_ai` or `battle_sub_menus`
  grows past the size of `battle_anim`, it overwrites the resident battle code, and the overlap
  assert does nothing **[V5]**. Every AI change must check the overlay sizes in `overlay.map`.

### 1.4 Save data

- **Flash.** 4 Mbit (512 KiB). Copy A is in sectors 0–63 and copy B in sectors 64–127. Each copy holds
  32 pages (`0x20000`) for the NORMAL and BOXES blocks, then extra saves at `SAVE_PAGE_MAX+0..11`
  (Hall of Fame, Battle Hall, 4 video slots). Pages +12..+31 appear free. To verify.
- **Headroom (from outside documentation, unverified).** NORMAL is about `0xCF2C` and BOXES about
  `0x121E4`, which leaves about 3.8 KB in total. NORMAL can grow only about **212 bytes** before it needs
  a 14th sector and breaks the sector-count assert at `src/savedata.c:875`.
- **Any change to the size of a saved struct invalidates existing saves** (the footer size check at
  `src/savedata.c:333`).
- **Policy for stage 2: no save-layout change.** All new state goes into:
  - renamed **`VAR_UNUSED_0x40xx`** (20 free) and safe **`FLAG_UNUSED_0x....`** (about 70 safe) **[V3]**;
  - the single spare **`Options` bit** (bit 15), reserved for AUTORUN;
  - if needed later, the 2 padding bytes after `Options` in `PlayerSave`, `padding_2A[2]`,
    `MiscSaveBlock.unused` (u32) and `padding : 3`.
- **Do not widen `Options`.** It is copied by value into the battle-recording struct, which is followed
  by a `u16` (`include/struct_defs/struct_0202F298.h:17`).
- **Do not grow `Trainer`/`TrainerHeader`.** `sizeof(Trainer)` is sent over link
  (`src/unk_0207A6DC.c`) and stored in battle recordings (`src/unk_0202F1D4.c`).

### 1.5 ROM space

`fill-tail` pads the ROM to a power of two. The retail ROM is 128 MiB, so the content is between 64 and
128 MiB. nitrorom switches to 256 MiB automatically. Stage 2 adds almost no assets. Stage 4 will
probably cross 128 MiB (see §6).

### 1.6 Rules that apply to every change

1. Gate every gameplay change against link, Frontier, recorded and Pal Park battles. Skip it when
   `battleType & (BATTLE_TYPE_LINK | BATTLE_TYPE_FRONTIER)` is set, or use `BATTLE_TYPE_NO_EXPERIENCE`
   for EXP. Battle recordings save `battleStatusMask`, so per-battle settings belong in it, not in live
   save reads.
2. Battle code has no `SaveData`. Read settings in the field and pass them down:
   `FieldBattleDTO_InitFromGameState` (`src/field_battle_data_transfer.c:234`) has `saveData` and ORs
   `BATTLE_STATUS_*` bits (bit 8 and up) into `dto->battleStatusMask` **[V8]**. Use `SaveData_Ptr()`
   (`src/savedata.c:101`) only where nothing else works.
3. `FieldSystem_RunScript` runs `init_new_game.s` and the ON_TRANSITION, ON_LOAD and ON_RESUME init
   scripts **synchronously**, so they cannot show messages or menus. Interactive scripts need ON_FRAME
   tables, step hooks or `ScriptManager_Set`.
4. Append-only lists: `generated/text_banks.txt`, `res/field/scripts.order`, the script command table
   (`include/data/scripts/scrcmd.h`), the battle command table (`sBattleCommands`, `battle_script.c:346`,
   which must match the order of `asm/macros/btlcmd.inc`), `generated/items.txt` (append before
   `MAX_ITEMS`), and script entries inside global script files.
5. Field-move tasks and bag "use from menu" functions cast `FieldTask_GetEnv` to `StartMenu`. They only
   work when started from the start menu's party menu or bag.
6. In a debug build, make `ErrorHandling_AssertFail` log through `EmulatorLog` and hang, so that silent
   overflows show up in tests **[V5]**. Do this early.

---

## 2. Hook map

**Difficulty:** L = low, M = medium, H = high. **Risk:** ⚠ = risky (see §5.4).

### 2.1 Field and quality of life

| Feature | Files and functions | Approach | Diff. |
|---|---|---|---|
| Auto-run (with an option) | `src/player_move.c`: `PlayerAvatar_IsRunButtonHeld` (2464). Local call sites at 1046 (`SetMovement_NormalOverworld`), 1124 (`SetMovement_DistortionFloor`) and 1171 (`UpdateMovement_NormalDistortion`). **Leave 2587 alone**: it is used for link and Underground avatars (`comm_player_manager.c:1053/1075`). | Add `PlayerAvatar_ShouldRun(pa, held)`: has shoes AND (autoRun ? !B : B). Use it at the 3 local sites. Store the setting in the spare `Options` bit with inverted meaning (bit = auto-run *off*), so it defaults to on. | L |
| Running Shoes from the start | `res/field/scripts/init_new_game.s` (`InitNewGame`); `res/field/maps/twinleaf_town_player_house_1f/scripts.s:133` | Add `GiveRunningShoes` to `InitNewGame` (no UI, so it works synchronously). Remove the hand-over from Mom's scene, or leave it (giving them again is harmless). | L |
| Options menu: AUTORUN, FAST BATTLES, FAST INTRO, EXP SHARE ALL, DIFFICULTY (read-only) | `src/applications/options_menu.c`: enum 58–69, `cursor : 3` (83), `% 7` (903/912), Init 149 / Exit 173, `SetupWindows` 608, five per-entry tables (`sEntryLabels` 679, `sNumChoicesPerEntry` 729, `sFirstChoicePerEntry` 739, `sEntryXOffsets` 767, `sEntryDescriptions` 957), `ChangesWereMade` 923; `include/applications/options_menu.h`; `res/text/options_menu.json` (message IDs below 256); `FieldSystem_OpenOptionsMenu` (`src/unk_0203D1B8.c:742`) passes only `Options*` | Add **pages** (GAME / BATTLE). The 7 rows already fill the 14-tile window, and the cursor bar tilemap is 2 tile rows. Widen the cursor field and replace the literal 7 with a row count. Reach `VarsFlags` through `SaveData_GetVarsFlags(SaveData_Ptr())`, or pass a struct with `SaveData*`. Make DIFFICULTY a row with one choice. | M ⚠ |
| HMs without teaching (HM item + badge) | `res/field/scripts/field_moves.s` (`FieldMoves_CutTree`, `_Rock`, `_Boulder`, `_RockyWall`, `_UseSurfFromField`, `_Waterfall`); `ScrCmd_FindPartySlotWithMove` (`src/scrcmd_party.c:140`); `Party_HasMonWithMove` (`src/unk_02054884.c:86`); C checks in `src/overlay005/field_control.c:216` (Waterfall descent) and `:690-694` (Surf prompt); party menu `GetContextMenuEntriesForPartyMon` (`party_menu/main.c:1791`), with at most 4 field-move rows (`PARTY_MENU_STR_MOVE0..3`) | Add a new script command, `FindPartySlotForFieldMove`: return a mon that knows the move; otherwise, if the HM item is in the bag, the first non-Egg slot; otherwise `MAX_PARTY_SIZE`. Append it to `scrcmd.h` and `scrcmd.inc`. Add a matching C helper for the two `field_control.c` sites. For Fly and Flash, add HM-granted entries for the **lead only** (as Crystal Imperium does). Badge checks stay as they are. | M |
| Allow forgetting HM moves | `Item_IsHMMove` (`src/item.c:306`), used by `party_menu/callbacks.c:1117`, the summary screen (`main.c:815`), `bag/main.c:2154` and `battle_party.c:1734` | Relax it once HMs no longer need teaching. Keep the `Item_IsHMMove` check in `TeachMove`, so HMs themselves are still never removed from the bag. | L |
| Fast egg hatching (8 steps) | `src/overlay005/daycare.c`: `Daycare_GetEggCycleLength` (900), test at 951 | Return 8, **and change `==` to `>=`**, because an old save's u8 counter can already be above 8. | L |
| Infinite Repel toggle | `src/overlay006/wild_encounters.c`: `ShouldGetRandomEncounter` (750); key item in `src/item_use_functions.c` | At the top: `if (flag INFINITE_REPEL) return FALSE;`. This blocks grass, surf and mud encounters; Poké Radar, fishing and honey trees still work (fishing is a decision, `WildEncounters_TryFishingEncounter` 380). ppexp's no-encounter flag hooks the same function. | L |
| L quick menu | `src/overlay005/field_control.c`: `FieldInput_Update` (118), `FieldInput_Process` (176, near 329–337); `include/overlay005/field_control.h` (`padding : 4`; ppexp takes 2 bits); `src/system.c:410` (L=A mode clears L and R) | Set `input->quickMenu` on L in the END/NONE move state. Start (a) a script list menu in `res/field/scripts/unused_0397.s` (9900, 8 free entries) for a quick first version, or (b) a C SysTask menu modelled on ppexp's `DebugMenu` (green on/off text, a clock, can start apps). Do not hook the Underground, Union Room, Colosseum or Battle Tower input functions. | M |
| PC anywhere (Box Link) | `res/field/scripts/common.s`: `CommonScript_PC` (entry 18), `CommonScript_AccessWhichPC` (932) | Add a new entry that jumps to `AccessWhichPC` and skips the boot (915) and shutdown (1141) animations, which expect a PC tile. | L |
| Heal anywhere (PokéVial) | `HealParty` script macro (`asm/macros/scrcmd.inc:1979`) | An L-menu entry or a key item, through `sub_02068540`/`sub_02068584` (`item_use_functions.c:251-294`), which start a field script with the item ID. | L |
| Care packages (start + after each badge) | `Field_ProcessStep` (`field_control.c:702`, the step hook; `Field_UpdateRepel` 858 is the model), or `FieldInput_Process` (per frame); `CommonScript_AddItemQuantity` (`common.s:804`); `ScrCmd_GiveBadge` (`scrcmd_system_flags.c:60`); gym scripts that call `GiveBadge` | **Global hook:** `VAR_CARE_PACKAGES_GIVEN` compared with the badge count, plus the starter test `SystemVars_GetPlayerStarter() != SPECIES_NONE`. When behind, `ScriptManager_Set(SCRIPT_ID(UNUSED_0397, n))`. The script increases the VAR only on success, so the package waits when the bag is full. There is no item PC to overflow into. | M |
| DexNav | No Platinum base. Nearest: `src/pokeradar.c`, `wild_encounters.c` `TryGenerateGrassEncounter_WithRadar` | Stage 3 or later. Could be a C app started from the L menu, or one of the 7 free Pokétch slots. | H |
| Debug menu (ppexp) | ppexp: `src/overlay005/debug_menu.c`, `debug_mon_menu.c`, `src/debug_game_start.c`, `include/constants/debug_menu.h`, `res/text/debug_menu*.json`. Hooks: `field_control.c` (FieldInput), `player_move.c:867` (no collision), `trainer_encounter.c:183` (no sight), `wild_encounters.c:750`, `title_screen.c` (R+X: debug new game), `game_start.c:144` (export `InitializeNewSave`), `pokemon.c` (`Pokemon_SetDefaultMoves`), town map `debugActive` | **Port, do not merge.** Copy the 9 new files and apply the roughly 12 hooks by hand. Rename the flags `FLAG_UNUSED_2420/2421/2422/2448` to `0x0974/0x0975/0x0976/0x0990`. Use `*_sseq` sound names, `HMCutIn_StartTask`/`EndTask` and `PlayerAvatar_GetGender`. Gate it behind a meson option. Key: R held + X **[V1]**. It adds about 2,350 lines to `overlay5`. | M |

### 2.2 EXP, levels, items, party and summary

| Feature | Files and functions | Approach | Diff. |
|---|---|---|---|
| Level cap source | New `src/level_cap.c` and `include/level_cap.h` in **Static main**; `TrainerInfo_BadgeCount` (`src/trainer_info.c:121`), `SystemFlag_CheckGameCompleted` (`system_flags.c:64`) | `u8 LevelCap_Get(const SaveData*)`: badges plus `VAR_LEVEL_CAP_MODE`/`VAR_DIFFICULTY` plus game-completed, returning 100 when off. The table values are a design decision (§7). | L |
| Cap on battle EXP | `src/battle/battle_script.c`: `BattleScript_GetExpTask` (9685), `!= MAX_POKEMON_LEVEL` at **9740**, EXP write near 9768–9776 | Read the cap **once, from a value computed in the DTO** (safer for recordings). If level ≥ cap, give 0 EXP and skip the message. Otherwise clamp the new EXP to `Pokemon_GetSpeciesBaseExpAt(species, cap)`, after Lucky Egg, trade and trainer multipliers. Make sure `SEQ_GET_EXP_CHECK_DONE` still clears the participant bit (10191). | M |
| ×1.5 EXP | `BtlCmd_CalcExpGain` (2187), or next to the trainer ×1.5 (about 9753) | Multiply when the flag is set. A u16 holds the result. | L |
| EXP Share for the whole party | `BtlCmd_CalcExpGain` 2196–2238; `GetExpTask` slot selection 9705–9712, shared EXP 9745 | Behind a flag: participants get the full EXP, other living non-Egg members half. Add `!isEgg` (the current loop does not check it). Optionally print one summary line instead of 6 messages. | M |
| Cap on Rare Candy | `src/item_use_pokemon.c:172` (check), `:292` (apply); party menu `ApplyItemEffectOnPokemon` (`main.c:2675`) | Replace `MAX_POKEMON_LEVEL` with the cap, read through `partyMenu->fieldSystem->saveData` (can be NULL in some modes) or `SaveData_Ptr()`. **Shared with `battle_party.c` and the Battle Castle**: keep Frontier at 100. Add a new message such as `PartyMenu_Text_LevelCapReached`. | L |
| Rare Candy Box (key item) | `generated/items.txt` (append before `MAX_ITEMS`); `res/items/data/rare_candy_box.json` (copy of `rare_candy.json`: `POCKET_KEY_ITEMS`, `preventToss`, price 0, `levelUp`); `ITEM_USE_FUNC_*` in `include/constants/items.h`; `sItemUseFuncs` (`item_use_functions.c:141`), modelled on the Gracidea (1022/1031) | Skip `Bag_TryRemoveItem` at `main.c:2700` for the box, **and in `TeachMove` (`callbacks.c:1116`) if the box ID is carried through the move round trip [V4]**. Use it from the bag (start-menu path; evolution and move-overwrite exits are handled). Registering it on **Y** competes with the Bicycle, and the field path (`RegisteredItem_GoToApp`) skips `StartMenu_ExitPartyMenu`, so evolution and forget-move exits would be lost. Make it bag-only at first. | M |
| Several candies at once, up to the cap | `party_menu/callbacks.c`: `PartyMenuCB_UseItem_RareCandy` (674), `PartyMenuCB_LevelUp` states (719–833), `PartyMenu_MoveSelection_Display` (1144, count picker); `start_menu.c`: `MenuOverwriteMoveData` (121), the `1009–1034` round trip, `StartMenu_ExitSummary` (1465–1510) | Choose a count, then level up **one level at a time** (`Pokemon_LevelUpMove` only learns moves for the exact level), skipping the stat windows. Loop while level < target and check evolution once at the end. Keep `targetLevel` (and the item) in `MenuOverwriteMoveData` and in the spare `PartyMenu` bytes. | H ⚠ |
| Reusable TMs | `TeachMove` (`callbacks.c:1105`, removal at 1118); `BagUI_PrintTMHMNumber` (`bag/windows.c:325`); selling in `bag/main.c:2583-2620` | `!Item_IsHMMove && !reusableTMs`. Hide the quantity and block selling (or set the price to 0). | L |
| Move relearner in the party menu | `move_reminder_data.c` (`MoveReminderData_GetMoves/HasMoves`), `FieldSystem_OpenMoveReminderMenu` (`unk_0203D1B8.c:1425`); `party_menu/context_menu.c` (`ACTION_*` 85–157), `defs.h` (`enum PartyMenuString`, exit codes), `windows.c:733/765`; `start_menu.c` `StartMenu_ExitPartyMenu` (948) | Insert `PARTY_MENU_STR_RELEARN` **and** `ACTION_RELEARN` at index 16 in both enums, so that `MOVE0 == ACTION_CUT` = 17 still holds. Add an exit code `PARTY_MENU_EXIT_CODE_MOVE_RELEARNER`, and a start-menu case that opens the reminder and returns to the party menu. Watch the context-menu height with 4 field moves. | M |
| Training Kit: IVs, EVs, ability | `Pokemon_SetValue(MON_DATA_*_IV/_EV)` then `Pokemon_CalcLevelAndStats` (`pokemon.c:554`); ability through PID bit 0 (`Pokemon_CalcAbility` 4741 runs again on evolution) | Edit IVs and EVs directly. Enforce 252 per stat and 510 in total by hand (Gen 4 allows 255). Change the ability slot by flipping PID bit 0 with the rewrite helper below. | L |
| Training Kit: nature | `sub_020780C4(mon, newPID)` (`pokemon.c:4768`), the safe PID rewrite. **Never write `MON_DATA_PERSONALITY` directly.** | Keep the low 16 bits (gender, ability bit, and the low half of the shiny XOR) and search the high 16 bits for PID % 25 == target, with the Wurmple half kept (65536 % 25 = 11, coprime with 25, so every nature can be reached). Shiny mons also need bits 8–15 of the low half varied. Export the helper as `Pokemon_ChangePersonality`. Box mons need a `BoxPokemon` variant. | M |
| Summary: IVs and EVs on A | `pokemon_summary_screen/main.h` (`PokemonSummaryMonData` 348–399); `main.c` `SetMonDataFromMon` (1056), `HandleInput_Main` (580); `window.c` `DrawSkillsPageWindows` (1145, windows at 453) | Add `ivs[6]`/`evs[6]` and a toggle on A, in `SUMMARY_MODE_NORMAL` only. | M |
| Minimal Grinding (31 IVs / 0 EVs) | `Pokemon_CalcStats` (`pokemon.c:564-648`), the only stat formula; battles copy the cached stats (`battle_lib.c:69/169`); `BattleScript_CalcEffortValues` (`battle_script.c:10214`); vitamins in `item_use_pokemon.c` | Override the IV and EV locals when the flag is set. **Cache the flag**, because this ARM9 code runs everywhere, including link, trade and GTS previews. Skip it for remote mons and for an exemption mark (Red-style bosses; for example a bit in `MON_DATA_UNUSED_114`). Recalculate the party when the flag changes. Lock EV gain. Hidden Power keeps reading the real IVs. | M ⚠ |

### 2.3 Trainers, AI and battle speed

| Feature | Files and functions | Approach | Diff. |
|---|---|---|---|
| Trainers at the level cap | `src/trainer_data.c`: `Trainer_Encounter` (25, already has `saveData` **[V7]**), `TrainerData_BuildParty` (176–316, four copies of the same code), seed at about 207/232/262/288, `Pokemon_InitWith` at 216/241/271/297; `BattleScript_CalcPrizeMoney` (`battle_script.c:3646`) | Pass `saveData` into `BuildParty`. Skip LINK, FRONTIER and Wi-Fi (`Encounter_NewVsWiFi` uses fake IDs). Seed with the **original** JSON level, so natures do not change with the cap. Scaled mons evolve through a small trainer-only evolution walk. Prize money: read the level from the battle party. Also fix the form-stats bug by calling `Pokemon_CalcStats` after setting `MON_DATA_FORM`. | M |
| Explicit nature, ability, IVs, EVs and ball for trainer mons | `include/struct_defs/trainer_data.h` (new `monDataType` bit, `TrainerMonFull`); `tools/dataproc/src/trainerproc.c` (`PackParty` 122, `ProcTrainer` 173); both readers of the party buffer (`BuildParty`, `CalcPrizeMoney` with its `sizeof(TrainerMonWithMovesAndItem)*6` buffer); `docs/datafiles/trainers.md` | Add a new optional data type, so the other 927 trainers stay byte-identical. Build the PID directly: low byte = gender, chosen against the ratio, with bit 0 = ability slot; high byte H = ((nature − L%25 + 25)·21) % 25 (21 is 256⁻¹ mod 25). Also set `MON_DATA_ABILITY` explicitly, then the EVs, then the form, then `Pokemon_CalcLevelAndStats`. **Do not touch `TrainerHeader`.** | M |
| Smart AI for every trainer | `TrainerAI_Init` (`trainer_ai.c:249` sets `thinkingMask`), or after `Trainer_Load` in `Trainer_Encounter` (37) | On NORMAL and HARD, force `BASIC|EVAL_ATTACK|EXPERT|CHECK_HP(|WEATHER)` for trainer battles that are not Frontier or link. Doing it in `Trainer_Encounter` avoids changing the AI partner. EASY keeps the flags from the data. Never add RISKY or PRIORITIZE_EXTREMES. | L |
| Smarter AI: knowledge and switching | `TrainerAI_RecordLastMove` (2705; copy the player's moves in Init instead); `AICmd_LoadBattlerAbility` (1170; use the real ability); damage roll (240; fix at 85); `TrainerAI_ShouldSwitch` (3894; add a matchup- and HP-based switch); `BattleAI_PostKOSwitchIn` (`battle_lib.c:7923`; u8 score overflow, scores with the fainted attacker); `script.s` BUG lines (78, 1165, 1172, 1718, …) | Steps 1–4 are in C. Step 5 is a new script routine on `AI_FLAG_UNUSED_11`. **Check the size of the `trainer_ai` overlay against `battle_anim` after every change [V9].** Keep it deterministic for recordings. | H ⚠ |
| FAST BATTLES: text | `BattleSystem_GetTextSpeed` (`battle_system.c:896`) | Return FAST (1 frame). `TEXT_SPEED_INSTANT` is unverified with `Task_WaitForBattleMessagePrint` and multi-page messages, so test it first. Keep trainer dialogue (`BattleMessage_PrintTrainerMessage` 1592) at normal speed. | L |
| FAST BATTLES: waits | `BtlCmd_WaitButtonABTime` (`battle_script.c:1823`; 395×30, 30×15, 8×60, 2×7 **[V10]**), `BtlCmd_WaitTime` (9353), the EXP message delay (9787) | Scale the frame count in the command handler, one change for every script. Scale `WaitTime` only together with the matching slide-in speed-ups. | L |
| FAST BATTLES: HP and EXP bars | `healthbox.c`: `HealthBox_DrawGauge` (1373; `UpdateGauge` fill offset at 1379, EXP branch 1383–1391) | HP: `fillOffset = max(1, maxHP/48)`. EXP: ×2–4. Check the number display and the low-HP sound. | L |
| FAST BATTLES: animations | `BattleAnimScriptCmd_Delay` (`battle_anim_system.c:832`), `Task_FlickerBattler` (`battle_display.c:4872`), `BtlCmd_PlayBattleAnimation` (3748) | Halve script delays, shorten the hit flash, and optionally skip stat and status animations. A true 2× speed is engine-wide and out of scope. | H ⚠ |
| FAST INTRO | `res/battle/scripts/subscripts/subscript_start_encounter.s` (WaitTime 96/112/122); `battle_display.c` `Task_SetTrainerEncounter` (2622; 28-frame delay, 8 px per frame); `HEALTHBOX_SCROLL_SPEED` (`healthbox.c:36`) | Add a `BATTLE_STATUS_FAST_INTRO` bit, a short script branch on `BTLVAR_BATTLE_SYS_STATUS`, and faster slide steps. | M |
| HARD: SET style | `BattleSystem_GetBattleStyle` (`battle_system.c:905`); the only reader is `battle_controller_player.c:4145` | In `Trainer_Encounter`, call `Options_SetBattleStyle(dto->options, SET)` (a per-battle copy), or return SET when HARD and TRAINER. | L |
| HARD: no Bag in trainer battles | `battle_controller_player.c:462` (`PLAYER_INPUT_ITEM`, which already refuses in Frontier and link) | Extend the condition with `(HARD bit && BATTLE_TYPE_TRAINER)`. Reusing the Frontier subscreen tilemap (`battle_subscreen.c:896`) is unverified. | L |
| Sleep Clause | `subscript_fall_asleep.s` (before `_147`); a new `BtlCmd` in `sBattleCommands` (346) and `btlcmd.inc`; AI `Basic_CheckCannotSleep` (`script.s:288`, `IfPartyMemberStatus` already exists) | A sleep move fails if a Pokémon on the target's side is already asleep (the opponent's doing). Rest uses a different path. Telling self-inflicted sleep apart needs a per-mon marker. | M |
| Boss teams | `res/trainers/data/leader_*.json`, `elite_four_*.json`, `champion_cynthia*.json`, `rival_*.json`, `galactic_boss_*.json`, `commander_*.json`; battle scripts in `res/field/maps/<map>/scripts.s`; `TrainerIsGymLeaderE4OrChampion` (`battle_main.c:1376`) | Data work, one JSON per boss. It can run in parallel once the new trainer format lands. New bosses reuse the 180 `dummy_*` slots, which need no new defeated-flags. | M |

---

## 3. Data formats we will edit

| Data | Path | Notes |
|---|---|---|
| Trainers | `res/trainers/data/<stem>.json`; IDs in `generated/trainers.txt` (ID = line − 1; 928 entries) | Keys: `name`, `class`, `items[≤4]`, `ai_flags[]`, `double_battle`, `party[]`, `messages[]`. Party members: `species`, `form`, `level` (u16), `item`, `moves[≤4]` or null (null = level-up moves), `iv_scale` (0–255; IVs = scale·31/255), `ball_seal`. **The first party member decides whether item and moves fields exist for the whole party.** Packed by `trainerproc` into `trdata.narc` (20-byte `TrainerHeader`) and `trpoke.narc`. Schema: `docs/datafiles/trainers.md`. Vanilla trainer mons: ability slot 1 always, gender from the trainer class (genderMod 136/120), nature seeded from ivScale+level+species+trainerID. Frontier trainers are separate (`res/trainers/frontier/`). |
| AI flags and script | `generated/ai_flags.txt`, `src/battle/trainer_ai/script.s`, `asm/macros/aicmd.inc` | Bit order = `FlagTable` order. Bits 11–28 are free. |
| Battle scripts | `res/battle/scripts/{effects,subscripts}/*.s`, `asm/macros/btlcmd.inc` | Commands are in `battle_script.c` `sBattleCommands`. Scripts read `battleStatusMask` through `BTLVAR_BATTLE_SYS_STATUS`. |
| Items | `generated/items.txt` (append before `MAX_ITEMS`; 0–467 now), `res/items/data/<stem>.json`, `res/items/icons/` (+ `meson.build`, `item_icon.order` for new icons only) | JSON: `fieldPocket`, `battlePocket`, `fieldUseFunc` (`ITEM_USE_FUNC_*`), `canRegister`, `preventToss`, `price`, `itemUseParams` (`levelUp`, `revive`, …), `teachesMove`. Built by `tools/dataproc/src/itemproc.c`. Free IDs: `ITEM_UNUSED_113..122`, or append (Pal Park and GTS do not know new IDs). Bag pockets: key items 50, balls 15, items 165 (`include/bag.h`). |
| Species (stage 4) | `res/pokemon/<stem>/{data.json, sprite_data.json, *.png(+.key), normal.pal, shiny.pal, icon.png, footprint.png, cry.txt, cry.wav, meson.build}`; `generated/species.txt` | See §6. `speciesproc.c` writes `pl_personal`, `evo`, `wotbl`, `height`, `zukan_data` and the other NARCs. |
| Moves (stage 4) | `res/moves/<stem>/{data.json, anim.s, script.s}`, `generated/moves.txt` | 16-byte `MoveTable`. The 8-bit flags field is fully used. `moveproc` pads IDs 468–500 with dummies. |
| Text | `res/text/<bank>.json` (`{"key": u16, "messages": [{"id", "en_US"}]}`), `generated/text_banks.txt` (724 banks, append-only), `tools/msgenc/charmap.txt` | C includes `res/text/bank/<bank>.h`. Load with `MessageLoader_Init(…, NARC_INDEX_MSGDATA__PL_MSG, TEXT_BANK_X, heap)`. Options menu label and choice tables are u8, so IDs there must stay below 256. Plan **one new bank per work track** (see §5). |
| Field scripts | `res/field/maps/<map>/{scripts.s, init.s, events.json, header.json}`, `res/field/scripts/*.s` + `scripts.order`, `include/constants/field/script_ranges.h`, `asm/macros/scrcmd.inc`, `include/data/scripts/scrcmd.h` | `SCRIPT_ID(chunk, n)`. `unused_0397.s` (offset 9900, `TEXT_BANK_COMMON_STRINGS`) has 8 free entries for global scripts. `CommonScript_*` IDs come from `tools/scripts/labelscan.py`. `header.json` `isRunningAllowed` is never read. |
| Vars and flags | `generated/vars_flags.txt` | Rename entries to add saved state. Safe pool: see **[V3]**. Map-local flags (0x01–0x40), script-local vars (0x8000+), daily flags (cleared each day), and the hidden-item and trainer-defeated ranges are not usable. |
| Options | `include/game_options.h`, `include/constants/game_options.h`, `src/game_options.c` (`Options_Init` 25) | u16 bitfield with 1 spare bit. |
| ROM identity | `platinum.us/rom_rev1.ini`, `platinum.us/icon.png` | Change only the banner and icon. Keep `CPUE` and `01`. |
| Code manifest | `platinum.us/main.lsf.in` | The only file to edit when adding a `.c` file. |

---

## 4. Test plan

### 4.1 Delta, the reference target

- **Core.** Delta (1.6 and later, including 2.0) runs **melonDS 0.9.5** from the `rileytestut/melonDS`
  fork, pinned at `a53f9ba` through the `MelonDSDeltaCore` submodule.
- **Configuration** (from `MelonDSEmulatorBridge.mm`): interpreter only (JIT commented out), threaded
  software renderer, always direct boot. It uses `bios7.bin`, `bios9.bin` and `firmware.bin` only if all
  three exist; otherwise FreeBIOS and a generated firmware. Most users will have **FreeBIOS**.
- **Save type.** It comes from melonDS 0.9.5's built-in game-code database. An unknown code falls back
  to an 8 KB EEPROM, which silently breaks saving. **Keep `CPUE` [V11].**
- **Saves.** Raw `.sav` bytes. Only raw in-game saves move between Delta and the test cores.
  Savestates never do.

### 4.2 Test tiers

| Tier | When | Emulator | Purpose |
|---|---|---|---|
| T0 | every build | none | `make release` succeeds. Overlay sizes from `overlay.map`: `trainer_ai` and `battle_sub_menus` ≤ `battle_anim`, and the highest overlay end below the old value plus our budget. Script that checks the `vars_flags.txt` renames (no duplicates, nothing in banned ranges). |
| T1, bulk | every commit | **melonDS DS** (JesseTG libretro core, melonDS 1.x, GPL-3.0) driven by **libretro.py** (MIT; Python ≥ 3.12; this machine has 3.13) and pytest, JIT on | Scenario play tests: boot to field, new game with settings, walk and run, battles, Rare Candy, L menu, saving and reloading. Input via `JoypadState`/`Pointer`. RAM through `memory_maps`/`get_memory` (≥ 1.4.0). Golden screenshots kept per core. |
| T1b, logic | every commit | **py-desmume** (manylinux wheels; `SDL_VIDEODRIVER=dummy`) | Fast in-ROM unit tests, as hg-engine does: a test build writes result codes to a fixed RAM word watched with `memory.register_write`. Covers the level-cap table, PID rewrite, stat override, EXP clamp and AI choices. |
| T2, Delta | before every release | **Headless build of `rileytestut/melonDS@a53f9ba`** (`-DBUILD_QT_SDL=OFF -DENABLE_JIT=OFF -DENABLE_OGLRENDERER=OFF`) plus a roughly 300-line `Platform::` shim copied from Delta's bridge, wrapped as a libretro core so the T1 tests run unchanged | The compatibility verdict. Run once with FreeBIOS (the default) and once with real BIOS files if they are available. A failure in T1 only (with JIT on) gets rerun with JIT off before it is filed. |

- **Debug aids.** Use `make debug` to get `debug.nef` and `overlay.map`; these give symbol addresses, for
  example to find `gSystem` and the save pointer for RAM checks. Use `EmulatorLog` (melonDS and no$gba
  print port). The ppexp debug new game (R+X on the title screen) gives fast test fixtures.
- **Assert hook.** Make the debug `GF_ASSERT` hook log and hang **[V5]**, so tests catch overflows.
- **Unsuitable tools.** Standalone melonDS, `desmume-cli` and BizHawk are not suitable for CI.

### 4.3 Still to verify

1. melonDS 0.9.5's ROMList has `CPUE` as 512 KB flash, and our hack ROM keeps that save type in Delta.
2. Our nitrorom-built ROM boots under **FreeBIOS direct boot**: the secure area must be decrypted, or
   KEY1 fails without a real `bios7.bin`.
3. The exact `Platform::` signatures in the rileytestut fork (WFC fields, the `Mic_Prepare` callback) before writing the shim.
4. Whether py-desmume's DeSmuME enables the dynarec (affects throughput).
5. The ROM size at stage 4, and iPhone memory: Delta keeps the ROM plus a buffer rounded up to the next power of two.
6. Whether Delta moves to melonDS 1.x. Recheck the submodule pointer before each release cycle.

---

## 5. Stage 2 implementation order: first playable (QoL and difficulty, Gen 1–4 only)

Principle: **no save-layout change in stage 2.** All new state lives in renamed vars and flags plus the
spare `Options` bit. The few shared "registry" files are edited only in Phase 0, by one agent, so that
the tracks in Phase 2 never touch the same file.

### 5.1 Phase 0: foundation (serial, one agent)

1. **Build.** Drop `check` from `all:`, run `make release` and `make debug`, and measure:
   - free heap (`HeapExp_FndGetTotalFreeSize`);
   - overlay ends and sizes from `overlay.map` (`battle_anim` vs `trainer_ai`/`battle_sub_menus`);
   - save block sizes (log `blockInfo[].size`);
   - ROM used size.

   Write the numbers into this file. Set up the debug assert hook **[V5]**.
2. **Settings registry (the key serialized change).**
   - Rename vars and flags in `generated/vars_flags.txt` from the safe pool **[V3]**:
     `VAR_DIFFICULTY`, `VAR_LEVEL_CAP_MODE`, `VAR_CARE_PACKAGES_GIVEN`, `VAR_IMPERIUM_SETTINGS_VERSION`,
     `FLAG_MINIMAL_GRINDING`, `FLAG_INFINITE_REPEL`, `FLAG_FAST_BATTLES`, `FLAG_FAST_INTRO`,
     `FLAG_EXP_SHARE_ALL`, `FLAG_REUSABLE_TMS`, `FLAG_SLEEP_CLAUSE`, plus spares.
   - Leave `0x0974–0x0976` and `0x0990` to the debug port.
   - Add `include/imperium_settings.h` and `src/imperium_settings.c` (Static main) with typed getters,
     and `LevelCap_Get` with a placeholder table.
   - Add the `Options` AUTORUN-off bit with its getter and setter.
   - Freeze this API.
3. **Battle plumbing.**
   - Add `BATTLE_STATUS_FAST_BATTLE`, `FAST_INTRO`, `HARD`, `SLEEP_CLAUSE`, `EXP_SHARE_ALL`,
     `MINIMAL_GRINDING` (bits 8 and up) in `include/constants/battle.h`.
   - Add a `levelCap` byte to `FieldBattleDTO` and copy it into `BattleSystem` in `BattleSys_New`.
     This is RAM only; check that the DTO is not saved.
   - Set the bits in `FieldBattleDTO_InitFromGameState`, and OR them in again after `encounter.c:659` **[V8]**.
4. **Reserve the append-only tables**, with stubs that do nothing:
   - new script commands in `scrcmd.h`/`scrcmd.inc` (`FindPartySlotForFieldMove`, `ToggleFlagMenuHelpers`, …);
   - the new battle command (`CheckSleepClause`) in `sBattleCommands` and `btlcmd.inc`;
   - new item IDs in `generated/items.txt` (Rare Candy Box, Infinite Repel, Box Link, PokéVial, Training Kit) with placeholder JSON;
   - new `ITEM_USE_FUNC_*` values;
   - new text banks in `text_banks.txt`, one per track (`imperium_field`, `imperium_party`, `imperium_battle`, `imperium_options`, `imperium_newgame`);
   - global-script entries in `unused_0397.s`;
   - empty `Object` lines (or new stub files) in `main.lsf.in` for every new `.c` file planned.
5. **Test harness, T1 and T1b.** Boot-to-field smoke test, plus a new-game fixture through the ppexp debug start (after Phase 1).

### 5.2 Phase 1: debug menu port (serial, one agent, right after Phase 0)

Port ppexp's menu, gated by a meson option. It touches hot files (`field_control.c`, `player_move.c`,
`wild_encounters.c`, `pokemon.c`, `game_start.c`, `title_screen.c`, `trainer_encounter.c`, town map),
so it must land **before** the tracks start. After this phase, each track rebases on it.
Expect a compile-fix pass: the port has never been compiled.

### 5.3 Phase 2: parallel tracks

Each track owns a disjoint set of files. Cross-track requests go through the Phase 0 API, or wait.

| Track | Owns (files) | Features |
|---|---|---|
| **A. Movement and encounters** | `src/player_move.c`, `src/overlay005/daycare.c`, `src/overlay006/wild_encounters.c`, `res/field/scripts/init_new_game.s`, `twinleaf_town_player_house_1f/scripts.s` | Auto-run, Running Shoes at start, 8-step eggs (`>=`), Infinite Repel hook |
| **B. Field input and scripts** | `src/overlay005/field_control.c`, `field_control.h`, `res/field/scripts/field_moves.s`, `common.s`, `unused_0397.s`, `src/scrcmd_party.c`, `src/unk_02054884.c`, the 8 gym `scripts.s` if needed, `imperium_field` bank | HM field use (script and C checks), L quick menu (script version first), PC anywhere, PokéVial, care-package step hook and scripts |
| **C. Party menu and items** | `src/applications/party_menu/*`, `include/applications/party_menu/defs.h`, `src/start_menu.c`, `src/item_use_functions.c`, `src/item_use_pokemon.c`, `src/item.c`, `src/applications/bag/*`, `res/items/data/*`, `imperium_party` bank | Rare Candy cap, Rare Candy Box, multi-candy ⚠, reusable TMs, move relearner, HM context entries for the lead (Fly, Flash), relaxing HM forgetting, Infinite Repel and Box Link item functions |
| **D. Battle engine** | `src/battle/battle_script.c`, `battle_system.c`, `battle_controller_player.c`, `healthbox.c`, `battle_display.c`, `battle_anim_system.c`, `res/battle/scripts/**`, `imperium_battle` bank | EXP cap, ×1.5, EXP Share for all, EV lock, fast battles, fast intro, HARD (SET, no Bag), Sleep Clause (engine side), prize money from the battle party |
| **E. Trainers and AI** | `src/trainer_data.c`, `include/struct_defs/trainer_data.h`, `tools/dataproc/src/trainerproc.c`, `docs/datafiles/trainers.md`, `src/battle/trainer_ai/*`, `src/battle/battle_lib.c` (AI functions only), `generated/ai_flags.txt` | Level scaling plus a trainer evolution walk, explicit spread format, forced smart flags, AI knowledge and switch fixes ⚠, Sleep Clause (AI side). Needs D's prize-money change: either D does it or E sends the patch to D. |
| **F. Pokémon data and summary** | `src/pokemon.c`, `include/pokemon.h`, `src/applications/pokemon_summary_screen/*` | Minimal Grinding in `Pokemon_CalcStats` ⚠, exported PID-rewrite helper (nature and ability), IV/EV summary toggle. Training Kit backend; its UI goes to B or C later. |
| **G. Settings UI** | `src/applications/options_menu.c`, `include/applications/options_menu.h`, `res/text/options_menu.json`, `res/graphics/options_menu/*`, new challenge-menu app (`src/applications/imperium_challenge/*`), `src/applications/rowan_intro/rowan_intro_app.c` (`RowanIntro_Exit` 450), bedroom PC (`twinleaf_town_player_house_2f/scripts.s`), `imperium_options` and `imperium_newgame` banks | Options pages and new rows ⚠, new-game challenge menu (EASY/NORMAL/HARD, Minimal Grinding, cap mode) inserted between `RowanIntro_Exit` and `gGameStartNewSaveAppTemplate`, settings PC |
| **H. Content** (after E's format lands) | `res/trainers/data/<boss>.json`: one agent per boss group (gyms, E4 and champion, rival, Galactic) | Boss teams to the trainer standard (`docs/crystal_imperium/TRAINER_STANDARD.md` adapted). Care-package item lists (data for B). |
| **T. Tests** | test repo or directory outside `pokeplatinum/src` | T0–T2 harnesses, scenario tests per feature as each track lands |

### 5.4 What must be serialized, and the riskiest items

**Serialized.** Everything in Phase 0 and Phase 1:

- `generated/vars_flags.txt`
- `generated/items.txt`
- `generated/text_banks.txt`
- the script and battle command tables
- `BATTLE_STATUS` bits
- the `Options` bit
- `FieldBattleDTO`
- `main.lsf.in`
- any later save-format change (none planned for stage 2)

If a track needs a new registry entry later, it asks the Phase 0 owner, who lands it alone.

Order within tracks:

- **B.** HM changes come before the L menu, because both edit `FieldInput_Process`.
- **C.** Rare Candy Box comes before multi-candy, which comes before the relearner, because all three edit `StartMenu_ExitPartyMenu`.
- **D.** EXP cap before EXP Share (same function), then FAST BATTLES, then FAST INTRO.

**Riskiest items (⚠), roughly in order:**

1. **AI rewrite (E):** overlay overlap with the resident `battle` overlay goes undetected **[V5, V9]**, and changes must stay deterministic for recordings. Check sizes in T0 on every build.
2. **Multi-candy (C):** state has to survive the summary round trip, and the `TeachMove` removal trap applies **[V4]**.
3. **Static main growth** (settings, level cap, Minimal Grinding, debug hooks): every byte shrinks the heap arena, which has only about 150–200 KB of slack. Measure in Phase 0.
4. **Options paging and the new-game challenge app (G):** graphics, VRAM and BG state, and the Rowan intro sub-app restore.
5. **Minimal Grinding in `Pokemon_CalcStats` (F):** hot shared code, which also runs for link and trade mons.
6. **Fast animations and instant text (D):** desync risks.
7. **Debug port (Phase 1):** never compiled, and it touches many hot files.

---

## 6. Stage 4 (Gen 5–9 species): feasibility and the limits to lift

**Verdict:** feasible, with a large amount of work. Inserting species before `SPECIES_EGG` lets most
arrays resize automatically (`MAX_SPECIES = SPECIES_BAD_EGG`, `NATIONAL_DEX_COUNT = MAX_SPECIES − 2`).
The parts that cost the most are not the data:

- the **save layout**: Pokédex bitfields and the Battle Hall table;
- **abilities and moves**: about 190 new abilities and about 390 new moves without Gen 4 effects or animations;
- **sprites**: DS 80×80 frames against GBA 64×64.

Stage 4 breaks vanilla save compatibility. Decide that before starting.

| Limit | Where | Needed change |
|---|---|---|
| Trainer species 10 bits (max 1023; Terapagos 1024 and Pecharunt 1025 do not fit) | `trainer_data.c` `& 0x3FF`, `TRAINER_MON_FORM_SHIFT 10` | Shift 11 with mask `0x7FF`, or a separate form byte |
| Learnset `move:9` (511 moves) and `level:7`, 20 entries; move reminder buffer of 22 | `include/struct_defs/species.h`, `speciesproc.c:472`, decoders in `pokemon.c` (3831, 3945, 4137, 4586), `move_reminder_data.c`, day-care buffer | u32 entries (`u16 move, u16 level`), up to about 32 entries; size every buffer from the struct |
| Hard-coded form NARC indices 496–503 | `Pokemon_GetFormNarcIndex` (`pokemon.c:4929`) | `SPECIES_BAD_EGG + 1 + offset`, or a generated form table |
| The Shaymin-Sky cry sits at SDAT bank and wave archive 494; free slots 495–699; `BANK_BASIC` at 700 | `res/sound/pl_sound_data.json`, `sound_playback.c:326` | Move Shaymin-Sky; add about 330 slots before `BANK_BASIC` (referenced by naix symbol, so safe) |
| Contest and Dress-Up use prebuilt DP sprite NARCs (0–493) | `pokemon.c:3031+, 3279+`; `overlay017`, `overlay022` | Fall back to the PL archives for species > 493 |
| Abilities u8, 2 slots, no hidden ability | `BoxPokemon` block A, `SpeciesData.abilities[2]`, `BattleMon`, `BoxPokemon_CalcAbility` | Widen in `SpeciesData`/`BattleMon`; add a hidden-ability flag in a spare `BoxPokemon` byte (block B `unused1`/`unused2`, D `unused`); implement each new ability in the `battle_lib.c` triggers and the AI |
| Move flags u8 full; 277 effects | `include/move_table.h`, `generated/move_battle_effects.txt`, `res/battle/scripts/effects/` | Spare `MoveContestData.padding02` for new flags (sound, punch, …); new effect scripts and commands. Remove `moveproc`'s dummy IDs 468–500 first. |
| TM mask 128 bits, `tmID` u8 | `species.h`, `CanPokemonFormLearnTM` (`pokemon.c:4716`) | Wider mask array for Crystal Imperium's 198 TMs; contiguous TM item IDs |
| `MAX_EVOLUTIONS` 7, 27 methods; `MAX_EGG_MOVES` 16 | `species.h`, `evolution_methods.txt`, `daycare.h` | 10 or more evolutions (Eevee); new methods, or have the converter simplify them; 20 egg moves |
| `baseExpReward` u8 | `SpeciesData` | u16, or keep Gen 4 yields |
| `MON_NAME_LEN` 10 (33 names are longer); dex numbers have 3 digits; 6 dex languages required | `include/constants/string.h`, `speciesproc.c:734-866`, summary `window.c:1051` | Abbreviate the names (widening breaks `BoxPokemon`); make the other languages optional; 4-digit numbers; fix the Japanese digit macro |
| Pokédex save grows by about 800 bytes at 1025 species; Battle Hall streaks (3 × u16 × `MAX_SPECIES`) overflow their single 4 KB sector at about 6.1 KB | `include/pokedex.h`, `battle_hall_win_records.h`, `save_table.c` | Raise `SAVE_PAGE_MAX` (moving the extra blocks) or shrink `recordedLanguages`; give the Battle Hall 2 sectors or limit it to Gen 1–4; add a save version magic |
| Fairy type | `generated/pokemon_types.txt`, type chart (`battle_lib.c:2399`), type icons, `pokemon_type_names.json`, Pokédex filter, Pokétch Move Tester, Battle Hall tables, Easy Chat; Fairy Arceus needs `pl_otherpoke` reindexed (index 132 is the Egg) | Append `TYPE_FAIRY` (18) and update every type-indexed UI; Hidden Power is unaffected |
| Icon palettes: 3 shared, and 3 is hard-coded in about 23 loaders | `pl_poke_icon.pal` | Remap GBA palettes 3–5 to 0–2, or load 6 everywhere |
| Sprites | `make_pl_pokegra.py`; `.key` files required; 4-bit PNGs | Stopgap: paste each GBA 64×64 frame at (8,16) inside 80×80 (about 80% of native size). Native art later. |
| Easy Chat 12-bit word IDs | `easy_chat_words.c` | About 2,250 words fits under 4096; update the sorted word lists |

**Converter.** Evaluate the GBA tables with the C preprocessor and compiler, not regex: values depend on
`P_UPDATED_*`/`B_UPDATED_MOVE_DATA` macros and on the Imperium override headers.
- Map species by `.natDexNum`.
- Map types and moves above 467 by name. Ability IDs 0–123 and move IDs 0–467 are identical.
- For Gen 1–4 species, overwrite only gameplay fields and keep the Platinum assets.

**Asset licences.** hg-engine has no LICENSE file. Its README allows reuse only for non-commercial,
freely available projects that copy its credits. Most of its sprites are from the Smogon Sprite Project
(non-profit use, with credit). Keep such assets in a separate directory with its own NOTICE.

---

## 7. Open questions to settle by experiment once the build runs

1. **Free main RAM:** read the real arena start from `overlay.map`, and the runtime free memory with `HeapExp_FndGetTotalFreeSize`. Is it 150–200 KB? Set a RAM budget for Static main additions.
2. **Overlay sizes:** `battle_anim` vs `trainer_ai` vs `battle_sub_menus`. How much room does the AI have? Does makelcf accept several `After` parents?
3. **Save block sizes:** log `blockInfo[].size`. Are NORMAL `0xCF2C` and BOXES `0x121E4` right? Do the extra saves end at page 43?
4. **Instant battle text:** is `TEXT_SPEED_INSTANT` safe with `Task_WaitForBattleMessagePrint` and multi-page messages, or must FAST stay at 1 frame?
5. **Frontier subscreen** (`battle_subscreen.c:896`, index 170): is it the command screen without BAG, reusable for HARD?
6. **`PlayerSave` padding bytes:** are they zeroed on a new game and in vanilla saves? This matters only if they are ever used.
7. **Delta:** does our ROM keep `CPUE` with 512 KB flash in melonDS 0.9.5? Does it boot with FreeBIOS (secure area)? Are a T2 save and a Delta save byte-identical?
8. **Rival class:** can Barry's `TRAINER_CLASS_RIVAL` ever reach the female genderMod branch? Check in a battle with the debug menu.
9. **Debug menu port:** which further renamed symbols appear in the first compile?
10. **Level caps:** the Sinnoh values (8 gyms, E4, postgame; HARD offsets), and whether story flags count as well as badges. This is a design question, but it should be tuned by play tests.
11. **Infinite Repel:** should it also block fishing and honey trees? Check how it feels in play.
12. **AI cost:** how many frames does a smart-flag AI turn take on the interpreter (Delta, T2)? Make sure it never stalls a turn.
13. **Fast battles:** frame counts for one trainer battle with FAST BATTLES off and on, measured in T1. The target is about a third less time, as in Crystal Imperium.
