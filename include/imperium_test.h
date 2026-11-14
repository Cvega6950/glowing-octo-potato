#ifndef POKEPLATINUM_IMPERIUM_TEST_H
#define POKEPLATINUM_IMPERIUM_TEST_H

#include "struct_defs/player_data.h"

#include "field/field_system_decl.h"

#include "bag.h"
#include "game_options.h"
#include "party.h"
#include "savedata.h"
#include "trainer_info.h"
#include "vars_flags.h"

// Platinum Imperium test mailbox (docs/platinum_imperium/API.md, "Test mailbox").
//
// A play test finds gImperiumTest through the linker map, writes args[] and status = 0, then cmd.
// The field runs the command on the next frame in which the player could move and no script or
// other field task is running, and sets status to DONE (or ERROR). Commands that start a field task
// (a script, a warp, a battle) stay BUSY until the field is free again. With cmd == 0 nothing
// happens, so the mailbox is harmless in a normal game.

#define IMPERIUM_TEST_MAGIC          0x494D5054 // 'IMPT'
#define IMPERIUM_TEST_LAYOUT_VERSION 1

enum ImperiumTestCommand {
    IMPERIUM_TEST_CMD_NONE = 0,
    IMPERIUM_TEST_CMD_RUN_SCRIPT, // args: scriptID, then VAR_0x8004..VAR_0x8006
    IMPERIUM_TEST_CMD_WARP, // args: mapHeaderID, x, z
    IMPERIUM_TEST_CMD_START_TRAINER_BATTLE, // args: trainerID
    IMPERIUM_TEST_CMD_GIVE_ITEM, // args: item, quantity
    IMPERIUM_TEST_CMD_GIVE_MON, // args: species, level
    IMPERIUM_TEST_CMD_PING, // no action: DONE on the next frame the player is free
    IMPERIUM_TEST_CMD_MAX,
};

enum ImperiumTestStatus {
    IMPERIUM_TEST_STATUS_IDLE = 0,
    IMPERIUM_TEST_STATUS_BUSY,
    IMPERIUM_TEST_STATUS_DONE,
    IMPERIUM_TEST_STATUS_ERROR,
};

// Offsets are part of the frozen test API: tools/dsrun/playtest.py reads them.
typedef struct ImperiumTestMailbox {
    /* 0x00 */ u32 magic;
    /* 0x04 */ u16 layoutVersion;
    /* 0x06 */ u16 numVars; // VarsFlags is u16 vars[numVars] then u8 flags[]
    /* 0x08 */ SaveData *saveData;
    /* 0x0C */ VarsFlags *varsFlags;
    /* 0x10 */ Party *party;
    /* 0x14 */ Bag *bag;
    /* 0x18 */ TrainerInfo *trainerInfo;
    /* 0x1C */ FieldSystem *fieldSystem; // NULL outside the field
    /* 0x20 */ Options *options;
    /* 0x24 */ PlayerData *playerData;
    /* 0x28 */ u32 fieldFrames; // counts field frames; stops outside the field
    /* 0x2C */ u16 cmd;
    /* 0x2E */ u16 args[4];
    /* 0x36 */ u16 status;
    /* 0x38 */ u16 result; // command-specific: 1 if the item or Pokemon was added
    /* 0x3A */ u16 sizeofPokemon;
    /* 0x3C */ u32 battleCount; // battles started (BattleSys_New) since power-on
    /* 0x40 */ u32 lastBattleType;
    /* 0x44 */ u32 lastBattleStatusMask;
    /* 0x48 */ u8 lastBattleLevelCap; // BattleSystem_GetLevelCap of the last battle
    /* 0x49 */ u8 levelCap; // LevelCap_Get, refreshed every field frame
    /* 0x4A */ u16 mapHeaderID; // refreshed every field frame
    /* 0x4C */ u16 playerX;
    /* 0x4E */ u16 playerZ;
    /* 0x50 */ u16 pendingCmd; // internal: the command that is BUSY
    /* 0x52 */ u16 padding;
    // Measurements, refreshed every 64 field frames.
    /* 0x54 */ const void *saveBlockInfo; // &saveData->blockInfo[0]: SAVE_BLOCK_ID_MAX x SaveBlockInfo (12 bytes)
    /* 0x58 */ u32 mainArenaFree; // main RAM between the root heaps and the arena's end, used by nothing
    /* 0x5C */ u32 appHeapFree; // HeapExp_FndGetTotalFreeSize(HEAP_ID_APPLICATION)
    /* 0x60 */ u32 systemHeapFree; // HeapExp_FndGetTotalFreeSize(HEAP_ID_SYSTEM)
} ImperiumTestMailbox;

extern ImperiumTestMailbox gImperiumTest;

// Called every field frame (src/field_system.c) to refresh the pointers.
void ImperiumTest_Refresh(FieldSystem *fieldSystem);
// Called from FieldInput_Process when the player is free. TRUE if a field task was started.
BOOL ImperiumTest_Process(FieldSystem *fieldSystem);
// Called by BattleSys_New.
void ImperiumTest_RecordBattleStart(u32 battleType, u32 battleStatusMask, u8 levelCap);

#endif // POKEPLATINUM_IMPERIUM_TEST_H
