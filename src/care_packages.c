// Platinum Imperium: care packages from PROF. ROWAN (Crystal Imperium's). What each holds and the
// messages listing it are generated into src/data/care_packages.h, the script that delivers them
// into data/scripts/care_packages.inc, by tools/platinum_imperium/care_packages.py.
#include "global.h"
#include "care_packages.h"
#include "event_data.h"
#include "event_scripts.h"
#include "fieldmap.h"
#include "item.h"
#include "script.h"
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

#include "data/care_packages.h"

// Package 0 is the starting one, 1-CARE_PACKAGE_COUNT the milestone ones, then the location ones
#define FIRST_PLACE_PACKAGE (CARE_PACKAGE_COUNT + 1)
STATIC_ASSERT(ARRAY_COUNT(sCarePackages) == FIRST_PLACE_PACKAGE + ARRAY_COUNT(sCarePackagePlaces), CarePackageCount);

// VAR_CARE_PACKAGE_PLACES: a bit for each location package in sCarePackagePlaces' order, and one
// for the starting package
#define PLACES_STARTING_BIT (1 << 15)

// VAR_CARE_PACKAGE_RESUME: a package that stopped because neither the Bag pocket nor the PC had
// room for its next item. Bits 0-7: that item's index; 8-12: the package.
#define RESUME_PENDING     (1 << 15)
#define RESUME_PACKAGE(v)  (((v) >> 8) & 0x1F)
#define RESUME_INDEX(v)    ((v) & 0xFF)

// The map where a package last stopped, + 1: it tries again only once the player is on another
static EWRAM_DATA u16 sStoppedOnMap = 0;

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

static bool32 StartCarePackage(u32 package, u32 kind)
{
    gSpecialVar_0x8004 = package;
    gSpecialVar_0x8006 = kind;
    ScriptContext_SetupScript(EventScript_CarePackage);
    return TRUE;
}

// Called on each step. A location package arrives on the first step in its place; the others out
// on a route or in a town: first the rest of one that stopped, then the starting package once the
// player has a Pokemon, then each location package the player is past, then one per milestone
// reached.
bool32 TryStartCarePackageScript(void)
{
    u32 received = VarGet(VAR_CARE_PACKAGES);
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
    if (!(places & PLACES_STARTING_BIT))
    {
        if (!outdoors)
            return FALSE;
        return StartCarePackage(0, CARE_PACKAGE_NEW);
    }
    for (i = 0; i < ARRAY_COUNT(sCarePackagePlaces); i++)
    {
        if (places & (1 << i))
            continue;
        if (sCarePackagePlaces[i].map == CurrentMap() || (outdoors && milestones >= sCarePackagePlaces[i].pastAtMilestones))
            return StartCarePackage(FIRST_PLACE_PACKAGE + i, CARE_PACKAGE_NEW);
    }
    if (outdoors && received < CARE_PACKAGE_COUNT && received < milestones)
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

// callnative: adds package VAR_0x8004 (VAR_0x8006 says how it started) to the Bag, each item whose
// pocket is full to the PC (VAR_0x8005 counts those). VAR_RESULT is TRUE once all of it is in; if
// neither has room for an item, VAR_RESULT is FALSE and VAR_CARE_PACKAGE_RESUME keeps the rest for
// later. A key item the player already has isn't added again.
void CarePackage_GiveItems(struct ScriptContext *ctx)
{
    u32 package = gSpecialVar_0x8004;
    u32 resume = VarGet(VAR_CARE_PACKAGE_RESUME);
    const struct CarePackage *contents = &sCarePackages[package];
    u32 i = 0;

    if (gSpecialVar_0x8006 == CARE_PACKAGE_RESUME)
        i = RESUME_INDEX(resume);

    gSpecialVar_0x8005 = 0;
    for (; i < contents->count; i++)
    {
        u16 itemId = contents->items[i].itemId;
        u16 quantity = contents->items[i].quantity;

        if (GetItemPocket(itemId) == POCKET_KEY_ITEMS && CheckBagHasItem(itemId, 1))
            continue;
        if (AddBagItem(itemId, quantity))
            continue;
        if (!AddPCItem(itemId, quantity))
        {
            VarSet(VAR_CARE_PACKAGE_RESUME, RESUME_PENDING | (package << 8) | i);
            sStoppedOnMap = CurrentMap() + 1;
            gSpecialVar_Result = FALSE;
            return;
        }
        gSpecialVar_0x8005++;
    }

    VarSet(VAR_CARE_PACKAGE_RESUME, 0);
    sStoppedOnMap = 0;
    if (package == 0)
    {
        VarSet(VAR_CARE_PACKAGE_PLACES, VarGet(VAR_CARE_PACKAGE_PLACES) | PLACES_STARTING_BIT);
    }
    else if (package >= FIRST_PLACE_PACKAGE)
    {
        VarSet(VAR_CARE_PACKAGE_PLACES, VarGet(VAR_CARE_PACKAGE_PLACES) | (1 << (package - FIRST_PLACE_PACKAGE)));
    }
    else
    {
        VarSet(VAR_CARE_PACKAGES, package);
    }
    gSpecialVar_Result = TRUE;
}
