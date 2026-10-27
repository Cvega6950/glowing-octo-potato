// Crystal Imperium (DECISIONS.md D41): the rewards of the side battles, the Gym Leaders from newer
// regions and the postgame's visitors. What each gives and the message listing it are generated into
// src/data/side_battle_rewards.h, the battles' scripts into data/scripts/side_battles.inc, by
// tools/crystal_imperium/side_battles.py.
#include "global.h"
#include "care_packages.h"
#include "event_data.h"
#include "item.h"
#include "script.h"
#include "side_battles.h"
#include "constants/item.h"
#include "constants/items.h"

struct SideBattleRewardItem
{
    u16 itemId;
    u16 quantity;
};

struct SideBattleReward
{
    const struct SideBattleRewardItem *items;
    u16 count;
    const u8 *text;
};

// The most items one reward holds (tools/crystal_imperium/side_battles.py checks it)
#define SIDE_BATTLE_REWARD_MAX_ITEMS 24

#include "data/side_battle_rewards.h"

// Where each item of a reward went, to take it back
enum
{
    REWARD_ITEM_NOWHERE = ITEM_NOWHERE,
    REWARD_ITEM_TO_BAG = ITEM_TO_BAG,
    REWARD_ITEM_TO_PC = ITEM_TO_PC,
    REWARD_ITEM_ALREADY_OWNED,
};

// callnative: the message listing reward VAR_0x8004, for the callstd MSGBOX_DEFAULT after it
void SideBattle_LoadRewardText(struct ScriptContext *ctx)
{
    ctx->data[0] = (uintptr_t)sSideBattleRewards[gSpecialVar_0x8004].text;
}

// A key item or a TM (kept after use, D19) the player already has isn't given again
static bool32 IsAlreadyOwned(u16 itemId)
{
    enum Pocket pocket = GetItemPocket(itemId);

    return (pocket == POCKET_KEY_ITEMS || pocket == POCKET_TM_HM) && CheckBagHasItem(itemId, 1);
}

// callnative: gives reward VAR_0x8004 whole, each item to the Bag, or to the PC when its pocket is
// full (AddItemToBagOrPC; VAR_0x8005 counts those), and VAR_RESULT is TRUE. If neither has room for one
// of them, what was added is taken back and VAR_RESULT is FALSE: talking to the trainer again tries
// once more, so nothing is lost.
void SideBattle_GiveReward(struct ScriptContext *ctx)
{
    const struct SideBattleReward *reward = &sSideBattleRewards[gSpecialVar_0x8004];
    u8 destination[SIDE_BATTLE_REWARD_MAX_ITEMS];
    u32 i;

    gSpecialVar_0x8005 = 0;
    for (i = 0; i < reward->count; i++)
    {
        u16 itemId = reward->items[i].itemId;

        destination[i] = IsAlreadyOwned(itemId) ? REWARD_ITEM_ALREADY_OWNED
                                                : AddItemToBagOrPC(itemId, reward->items[i].quantity);
        if (destination[i] == REWARD_ITEM_TO_PC)
            gSpecialVar_0x8005++;
        if (destination[i] != REWARD_ITEM_NOWHERE)
            continue;

        while (i-- > 0)
        {
            if (destination[i] == REWARD_ITEM_TO_BAG)
                RemoveBagItem(reward->items[i].itemId, reward->items[i].quantity);
            else if (destination[i] == REWARD_ITEM_TO_PC)
                RemovePCItemById(reward->items[i].itemId, reward->items[i].quantity);
        }
        gSpecialVar_0x8005 = 0;
        gSpecialVar_Result = FALSE;
        return;
    }
    gSpecialVar_Result = TRUE;
}
