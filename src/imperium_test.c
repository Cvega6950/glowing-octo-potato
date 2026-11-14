#include "imperium_test.h"

#include <nitro.h>

#include "constants/battle.h"
#include "constants/field/script_ranges.h"
#include "constants/heap.h"
#include "constants/player_avatar.h"
#include "constants/savedata/vars_flags.h"
#include "generated/items.h"

#include "struct_defs/player_data.h"

#include "field/field_system.h"

#include "bag.h"
#include "field_map_change.h"
#include "field_overworld_state.h"
#include "heap.h"
#include "imperium_settings.h"
#include "location.h"
#include "map_header.h"
#include "party.h"
#include "player_avatar.h"
#include "pokemon.h"
#include "save_player.h"
#include "savedata.h"
#include "script_manager.h"
#include "trainer_info.h"
#include "unk_02054884.h"
#include "vars_flags.h"

// res/field/scripts/unused_0397.s, entry 8: starts a trainer battle with VAR_0x8004.
#define IMPERIUM_TEST_SCRIPT_TRAINER_BATTLE SCRIPT_ID(UNUSED_0397, 8)

ImperiumTestMailbox gImperiumTest = {
    .magic = IMPERIUM_TEST_MAGIC,
    .layoutVersion = IMPERIUM_TEST_LAYOUT_VERSION,
    .numVars = NUM_VARS,
    .sizeofPokemon = sizeof(Pokemon),
};

void ImperiumTest_Refresh(FieldSystem *fieldSystem)
{
    ImperiumTestMailbox *box = &gImperiumTest;
    SaveData *saveData = fieldSystem->saveData;

    box->fieldSystem = fieldSystem;
    box->saveData = saveData;
    box->varsFlags = SaveData_GetVarsFlags(saveData);
    box->party = SaveData_GetParty(saveData);
    box->bag = SaveData_GetBag(saveData);
    box->trainerInfo = SaveData_GetTrainerInfo(saveData);
    box->options = SaveData_GetOptions(saveData);
    box->playerData = FieldOverworldState_GetPlayerData(SaveData_GetFieldOverworldState(saveData));
    box->levelCap = LevelCap_Get(saveData);
    box->fieldFrames++;

    if (fieldSystem->location != NULL) {
        box->mapHeaderID = fieldSystem->location->mapHeaderID;
    }

    if (fieldSystem->runningFieldMap && fieldSystem->playerAvatar != NULL) {
        box->playerX = PlayerAvatar_GetXPos(fieldSystem->playerAvatar);
        box->playerZ = PlayerAvatar_GetZPos(fieldSystem->playerAvatar);
    }

    if ((box->fieldFrames & 63) == 1) {
        box->saveBlockInfo = saveData->blockInfo;
        box->mainArenaFree = (u32)OS_GetMainArenaHi() - (u32)OS_GetMainArenaLo();
        box->appHeapFree = HeapExp_FndGetTotalFreeSize(HEAP_ID_APPLICATION);
        box->systemHeapFree = HeapExp_FndGetTotalFreeSize(HEAP_ID_SYSTEM);
    }
}

static void SetScriptVars(FieldSystem *fieldSystem, const u16 *values, int count)
{
    for (int i = 0; i < count; i++) {
        *FieldSystem_GetVarPointer(fieldSystem, VAR_0x8004 + i) = values[i];
    }
}

static void Finish(ImperiumTestMailbox *box, BOOL success)
{
    box->status = success ? IMPERIUM_TEST_STATUS_DONE : IMPERIUM_TEST_STATUS_ERROR;
    box->pendingCmd = IMPERIUM_TEST_CMD_NONE;
    box->cmd = IMPERIUM_TEST_CMD_NONE;
}

static void StartTask(ImperiumTestMailbox *box)
{
    box->pendingCmd = box->cmd;
    box->cmd = IMPERIUM_TEST_CMD_NONE;
    box->status = IMPERIUM_TEST_STATUS_BUSY;
}

BOOL ImperiumTest_Process(FieldSystem *fieldSystem)
{
    ImperiumTestMailbox *box = &gImperiumTest;

    // A command that started a field task is done once the field is free again. A command the test
    // wrote in the meantime stays queued for the next frame.
    if (box->pendingCmd != IMPERIUM_TEST_CMD_NONE) {
        box->pendingCmd = IMPERIUM_TEST_CMD_NONE;
        box->status = IMPERIUM_TEST_STATUS_DONE;
        return FALSE;
    }

    if (box->cmd == IMPERIUM_TEST_CMD_NONE) {
        return FALSE;
    }

    // Only while the player stands still: on the frame a step ends (PLAYER_MOVE_STATE_END), the
    // rest of FieldInput_Process runs the step's events (step counters, warps, wild encounters),
    // which a command started here would skip.
    if (PlayerAvatar_GetPlayerMoveState(fieldSystem->playerAvatar) != PLAYER_MOVE_STATE_NONE) {
        return FALSE;
    }

    SaveData *saveData = fieldSystem->saveData;
    box->result = 0;

    switch (box->cmd) {
    case IMPERIUM_TEST_CMD_RUN_SCRIPT:
        StartTask(box);
        ScriptManager_Set(fieldSystem, box->args[0], NULL);
        SetScriptVars(fieldSystem, &box->args[1], 3);
        return TRUE;

    case IMPERIUM_TEST_CMD_WARP:
        StartTask(box);
        FieldTask_StartMapChangeFly(fieldSystem, box->args[0], -1, box->args[1], box->args[2], FACE_DOWN);
        return TRUE;

    case IMPERIUM_TEST_CMD_START_TRAINER_BATTLE:
        StartTask(box);
        ScriptManager_Set(fieldSystem, IMPERIUM_TEST_SCRIPT_TRAINER_BATTLE, NULL);
        SetScriptVars(fieldSystem, &box->args[0], 1);
        return TRUE;

    case IMPERIUM_TEST_CMD_GIVE_ITEM:
        box->result = Bag_TryAddItem(SaveData_GetBag(saveData), box->args[0], box->args[1], HEAP_ID_FIELD1);
        Finish(box, box->result);
        return FALSE;

    case IMPERIUM_TEST_CMD_GIVE_MON:
        box->result = Pokemon_GiveMonFromScript(HEAP_ID_FIELD2, saveData, box->args[0], box->args[1], ITEM_NONE, MapHeader_GetMapLabelTextID(fieldSystem->location->mapHeaderID), TERRAIN_MAX);
        Finish(box, box->result);
        return FALSE;

    case IMPERIUM_TEST_CMD_PING:
        Finish(box, TRUE);
        return FALSE;

    default:
        Finish(box, FALSE);
        return FALSE;
    }
}

void ImperiumTest_RecordBattleStart(u32 battleType, u32 battleStatusMask, u8 levelCap)
{
    gImperiumTest.battleCount++;
    gImperiumTest.lastBattleType = battleType;
    gImperiumTest.lastBattleStatusMask = battleStatusMask;
    gImperiumTest.lastBattleLevelCap = levelCap;
}
