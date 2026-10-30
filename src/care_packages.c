// Crystal Imperium: care packages from PROF. ELM (DECISIONS.md D16). What each holds and the
// messages listing it are generated into src/data/care_packages.h, the script that delivers them
// into data/scripts/care_packages.inc, by tools/crystal_imperium/care_packages.py.
#include "global.h"
#include "care_packages.h"
#include "event_data.h"
#include "event_scripts.h"
#include "fieldmap.h"
#include "item.h"
#include "script.h"
#include "string_util.h"
#include "constants/care_packages.h"
#include "constants/flags.h"
#include "constants/item.h"
#include "constants/map_groups.h"
#include "constants/map_types.h"
#include "constants/vars.h"

struct CarePackageItem
{
    u16 itemId;
    u16 quantity;
};

struct CarePackage
{
    const struct CarePackageItem *items;
    u16 count;
    const u8 *intro;
    const u8 *text;
};

struct CarePackagePlace
{
    u16 map;
    u8 pastAtMilestones;
};

struct CarePackageTMs
{
    const u16 *tms;
    u16 count;
};

#include "data/care_packages.h"

// Package 0 is the starting one, 1-CARE_PACKAGE_COUNT the milestone ones, then the location ones
#define FIRST_PLACE_PACKAGE (CARE_PACKAGE_COUNT + 1)
STATIC_ASSERT(ARRAY_COUNT(sCarePackages) == FIRST_PLACE_PACKAGE + ARRAY_COUNT(sCarePackagePlaces), CarePackageCount);
STATIC_ASSERT(ARRAY_COUNT(sCarePackageTMs) == CARE_PACKAGE_TM_TIERS && CARE_PACKAGE_TM_TIERS <= CARE_PACKAGE_COUNT + 1, CarePackageTMTiers);

// VAR_CARE_PACKAGE_PLACES: a bit for each location package in sCarePackagePlaces' order, and one
// for the starting package (set since 0.12.0-experimental, whose starting package was smaller)
#define PLACES_STARTING_BIT (1 << 15)

// VAR_CARE_PACKAGE_RESUME: a package that stopped because neither the Bag pocket nor the PC had
// room for its next item. Bits 0-7: that item's index; 8-12: the package; 13: it was an update.
#define RESUME_PENDING     (1 << 15)
#define RESUME_UPDATE      (1 << 13)
#define RESUME_PACKAGE(v)  (((v) >> 8) & 0x1F)
#define RESUME_INDEX(v)    ((v) & 0xFF)

// The map where a package last stopped, + 1: it tries again only once the player is on another
static EWRAM_DATA u16 sStoppedOnMap = 0;

// The items pocket keeps this many slots free for the story's one-time gifts (the Plates, ...):
// while the PC has room, a new kind of item from a care package or the MEGA code goes there instead
#define GIFT_ROOM_IN_ITEMS_POCKET 20

static u16 CurrentMap(void)
{
    return (gSaveBlock1Ptr->location.mapGroup << 8) | gSaveBlock1Ptr->location.mapNum;
}

// Milestones reached: one per Gym Badge, plus one for becoming Champion
static u32 CountMilestones(void)
{
    u32 i, count = FlagGet(FLAG_SYS_GAME_CLEAR) ? 1 : 0;

    for (i = FLAG_BADGE01_GET; i < FLAG_BADGE01_GET + NUM_BADGES; i++)
    {
        if (FlagGet(i))
            count++;
    }
    return count;
}

// Adds an item from a care package or a cheat code to the Bag, or to the PC when its pocket is full
// or the item would take the items pocket's gift room; to the gift room only when the PC is full too
enum ItemDestination AddItemToBagOrPC(u16 itemId, u16 quantity)
{
    bool32 keepGiftRoom = (GetItemPocket(itemId) == POCKET_ITEMS && !CheckBagHasItem(itemId, 1)
                        && CountFreeSlotsInBagPocket(POCKET_ITEMS) <= GIFT_ROOM_IN_ITEMS_POCKET);

    if (!keepGiftRoom && AddBagItem(itemId, quantity))
        return ITEM_TO_BAG;
    if (AddPCItem(itemId, quantity))
        return ITEM_TO_PC;
    if (keepGiftRoom && AddBagItem(itemId, quantity))
        return ITEM_TO_BAG;
    return ITEM_NOWHERE;
}

// The TM tiers due (D48): tier 0 with the starting package, tier k with the k-th milestone package
static u32 CarePackageTMTiersDue(void)
{
    u32 due;

    if (!FlagGet(FLAG_RECEIVED_STARTING_CARE_PACKAGE))
        return 0;
    due = VarGet(VAR_CARE_PACKAGES) + 1;
    return due < CARE_PACKAGE_TM_TIERS ? due : CARE_PACKAGE_TM_TIERS;
}

// The machines in the TM case and the items in the PC, a bit each, from one pass over each (as the
// TM shops find the TMs the player has, src/shop.c)
static void FindOwnedTMs(u32 *owned)
{
    u32 i;

    memset(owned, 0, sizeof(u32) * ((ITEMS_COUNT + 31) / 32));
    for (i = 0; i < gBagPockets[POCKET_TM_HM].capacity; i++)
    {
        struct ItemSlot slot = GetBagItemIdAndQuantity(POCKET_TM_HM, i);

        if (slot.itemId != ITEM_NONE && slot.itemId < ITEMS_COUNT && slot.quantity != 0)
            owned[slot.itemId / 32] |= 1u << (slot.itemId % 32);
    }
    for (i = 0; i < PC_ITEMS_COUNT; i++)
    {
        u16 itemId = gSaveBlock1Ptr->pcItems[i].itemId;

        if (itemId != ITEM_NONE && itemId < ITEMS_COUNT && gSaveBlock1Ptr->pcItems[i].quantity != 0)
            owned[itemId / 32] |= 1u << (itemId % 32);
    }
}

// Gives a tier's TMs and returns how many: a TM the player has already isn't given again while TMs
// are reusable (INFINITE TMS: GetItemImportance); with INFINITE TMS off, a TM is used up by teaching
static u32 GiveCarePackageTMs(u32 tier, const u32 *owned)
{
    u32 i, given = 0;

    for (i = 0; i < sCarePackageTMs[tier].count; i++)
    {
        u16 tm = sCarePackageTMs[tier].tms[i];

        if (GetItemImportance(tm) && (owned[tm / 32] & (1u << (tm % 32))))
            continue;
        if (AddItemToBagOrPC(tm, 1) != ITEM_NOWHERE)
            given++;
    }
    return given;
}

static bool32 StartCarePackage(u32 package, u32 kind)
{
    gSpecialVar_0x8004 = package;
    gSpecialVar_0x8006 = kind;
    ScriptContext_SetupScript(EventScript_CarePackage);
    return TRUE;
}

// Called on each step. A location package arrives on the first step in its place; the others out
// on a route or in a town (like Mom's gift calls): first the rest of one that stopped, then the
// starting package once the player has a Pokemon, then each location package the player is past,
// then, for a save from before 0.12.0, each milestone package it received again with its 0.12.0
// contents, then, for a save from before 0.15.1, the TMs of the packages it received (D48), then one
// per milestone reached. (VAR_CARE_PACKAGE_GEAR and VAR_CARE_PACKAGE_BULK, the
// catch-ups of earlier releases, are kept level with VAR_CARE_PACKAGES but no longer read: the
// 0.12.0 contents hold everything those brought.)
bool32 TryStartCarePackageScript(void)
{
    u32 received = VarGet(VAR_CARE_PACKAGES);
    u32 updated = VarGet(VAR_CARE_PACKAGE_IMPERIUM);
    u32 places = VarGet(VAR_CARE_PACKAGE_PLACES);
    u32 resume = VarGet(VAR_CARE_PACKAGE_RESUME);
    u32 milestones = CountMilestones();
    u8 mapType = gMapHeader.mapType;
    bool32 outdoors = (mapType == MAP_TYPE_ROUTE || mapType == MAP_TYPE_OCEAN_ROUTE
                    || mapType == MAP_TYPE_CITY || mapType == MAP_TYPE_TOWN);
    u32 i;

    if (resume & RESUME_PENDING)
    {
        if (!outdoors || sStoppedOnMap == CurrentMap() + 1 || RESUME_PACKAGE(resume) >= ARRAY_COUNT(sCarePackages))
            return FALSE;
        return StartCarePackage(RESUME_PACKAGE(resume), CARE_PACKAGE_RESUME);
    }
    if (!FlagGet(FLAG_SYS_POKEMON_GET))
        return FALSE;
    if (outdoors && !FlagGet(FLAG_RECEIVED_STARTING_CARE_PACKAGE))
        return StartCarePackage(0, (places & PLACES_STARTING_BIT) ? CARE_PACKAGE_UPDATE : CARE_PACKAGE_NEW);
    for (i = 0; i < ARRAY_COUNT(sCarePackagePlaces); i++)
    {
        if (places & (1 << i))
            continue;
        if (sCarePackagePlaces[i].map == CurrentMap() || (outdoors && milestones >= sCarePackagePlaces[i].pastAtMilestones))
            return StartCarePackage(FIRST_PLACE_PACKAGE + i, CARE_PACKAGE_NEW);
    }
    if (!outdoors)
        return FALSE;
    if (updated < received && updated < CARE_PACKAGE_COUNT)
        return StartCarePackage(updated + 1, CARE_PACKAGE_UPDATE);
    if (VarGet(VAR_CARE_PACKAGE_TMS) < CarePackageTMTiersDue())
        return StartCarePackage(0, CARE_PACKAGE_TMS);
    if (received < CARE_PACKAGE_COUNT && received < milestones)
        return StartCarePackage(received + 1, CARE_PACKAGE_NEW);
    return FALSE;
}

// callnative: the first message of package VAR_0x8004, for the callstd MSGBOX_DEFAULT after it
void CarePackage_LoadIntroText(struct ScriptContext *ctx)
{
    ctx->data[0] = (uintptr_t)sCarePackages[gSpecialVar_0x8004].intro;
}

// callnative: the contents message of package VAR_0x8004, for the callstd MSGBOX_DEFAULT after it
void CarePackage_LoadContentsText(struct ScriptContext *ctx)
{
    ctx->data[0] = (uintptr_t)sCarePackages[gSpecialVar_0x8004].text;
}

// callnative: adds package VAR_0x8004 (VAR_0x8006 says how it started) to the Bag, or to the PC
// (AddItemToBagOrPC; VAR_0x8005 counts those). VAR_RESULT is TRUE once all of it is in; if neither
// has room for an item, VAR_RESULT is FALSE and VAR_CARE_PACKAGE_RESUME keeps the rest for later.
// A key item the player already has isn't added again.
void CarePackage_GiveItems(struct ScriptContext *ctx)
{
    u32 package = gSpecialVar_0x8004;
    u32 resume = VarGet(VAR_CARE_PACKAGE_RESUME);
    bool32 update = (gSpecialVar_0x8006 == CARE_PACKAGE_UPDATE);
    const struct CarePackage *contents = &sCarePackages[package];
    u32 i = 0;

    if (gSpecialVar_0x8006 == CARE_PACKAGE_RESUME)
    {
        i = RESUME_INDEX(resume);
        update = (resume & RESUME_UPDATE) != 0;
    }

    gSpecialVar_0x8005 = 0;
    for (; i < contents->count; i++)
    {
        u16 itemId = contents->items[i].itemId;
        u16 quantity = contents->items[i].quantity;

        if (GetItemPocket(itemId) == POCKET_KEY_ITEMS && CheckBagHasItem(itemId, 1))
            continue;
        switch (AddItemToBagOrPC(itemId, quantity))
        {
        case ITEM_TO_BAG:
            break;
        case ITEM_TO_PC:
            gSpecialVar_0x8005++;
            break;
        case ITEM_NOWHERE:
            // Neither the Bag nor the PC has room: the rest waits for another map
            VarSet(VAR_CARE_PACKAGE_RESUME, RESUME_PENDING | (update ? RESUME_UPDATE : 0) | (package << 8) | i);
            sStoppedOnMap = CurrentMap() + 1;
            gSpecialVar_Result = FALSE;
            return;
        }
    }

    VarSet(VAR_CARE_PACKAGE_RESUME, 0);
    sStoppedOnMap = 0;
    // A new starting or milestone package brings its TMs (D48) once the earlier tiers are in (a save
    // from before 0.15.1 gets those first, CARE_PACKAGE_TMS); an update or a location package brings none
    if (!update && package < CARE_PACKAGE_TM_TIERS && VarGet(VAR_CARE_PACKAGE_TMS) == package)
    {
        u32 owned[(ITEMS_COUNT + 31) / 32];

        FindOwnedTMs(owned);
        GiveCarePackageTMs(package, owned);
        VarSet(VAR_CARE_PACKAGE_TMS, package + 1);
    }
    if (package == 0)
    {
        FlagSet(FLAG_RECEIVED_STARTING_CARE_PACKAGE);
        VarSet(VAR_CARE_PACKAGE_PLACES, VarGet(VAR_CARE_PACKAGE_PLACES) | PLACES_STARTING_BIT);
    }
    else if (package >= FIRST_PLACE_PACKAGE)
    {
        VarSet(VAR_CARE_PACKAGE_PLACES, VarGet(VAR_CARE_PACKAGE_PLACES) | (1 << (package - FIRST_PLACE_PACKAGE)));
    }
    else if (update)
    {
        VarSet(VAR_CARE_PACKAGE_IMPERIUM, package);
    }
    else
    {
        VarSet(VAR_CARE_PACKAGES, package);
        VarSet(VAR_CARE_PACKAGE_IMPERIUM, package);
        VarSet(VAR_CARE_PACKAGE_GEAR, package);
        VarSet(VAR_CARE_PACKAGE_BULK, package);
    }
    gSpecialVar_Result = TRUE;
}

// callnative: the TMs of the packages a save from before 0.15.1 had received (D48), every tier due at
// once. VAR_RESULT and STR_VAR_1: how many TMs it gave (0 when the player had them all).
void CarePackage_GiveTMs(struct ScriptContext *ctx)
{
    u32 owned[(ITEMS_COUNT + 31) / 32];
    u32 tier, due = CarePackageTMTiersDue(), given = 0;

    FindOwnedTMs(owned);
    for (tier = VarGet(VAR_CARE_PACKAGE_TMS); tier < due; tier++)
        given += GiveCarePackageTMs(tier, owned);
    if (VarGet(VAR_CARE_PACKAGE_TMS) < due)
        VarSet(VAR_CARE_PACKAGE_TMS, due);
    ConvertIntToDecimalStringN(gStringVar1, given, STR_CONV_MODE_LEFT_ALIGN, 3);
    gSpecialVar_Result = given;
}
