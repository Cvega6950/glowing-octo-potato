// Crystal Imperium: milestone care packages (data/scripts/care_packages.inc).
#include "global.h"
#include "care_packages.h"
#include "event_data.h"
#include "event_scripts.h"
#include "fieldmap.h"
#include "script.h"
#include "constants/flags.h"
#include "constants/map_groups.h"
#include "constants/map_types.h"
#include "constants/vars.h"

#define CARE_PACKAGE_COUNT 17

// Since 0.12.0, Emerald Imperium-style: the starting package and the location packages
// (tools/crystal_imperium/care_packages.py, PLACES), a bit each in VAR_CARE_PACKAGE_PLACES
#define CARE_PACKAGE_STARTING_BIT (1 << 15)

// The place, in the generator's order, and the badge count by which the player is past it for
// sure: a save that is past a place without having entered it since 0.12.0 still gets its package
// (on the next step on a route or in a town)
static const struct { u16 map; u8 pastAtBadges; } sCarePackagePlaces[] =
{
    { MAP_UNION_CAVE_1F_HNS,           2 },
    { MAP_ILEX_FOREST_HNS,             3 },
    { MAP_NATIONAL_PARK_NORMAL_HNS,    4 },
    { MAP_BURNED_TOWER_1F_HNS,         4 },
    { MAP_OLIVINE_CITY_LIGHTHOUSE_HNS, 6 },
    { MAP_MT_MORTAR_1F_SOUTH_HNS,      7 },
    { MAP_LAKE_OF_RAGE_HNS,            7 },
    { MAP_ICE_PATH_1F_HNS,             8 },
    { MAP_VICTORY_ROAD_KANTO_1F_HNS,   9 }, // 9: the Johto League won
};

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

// Called on each step: the next package arrives while milestones are ahead of the packages
// received, out on a route or in a town (like Mom's gift calls). A save from before 0.7.0 first
// gets the battle gear its packages didn't have then, one package per step, and a save from
// before 0.11.0 the rest of their stacks; a package received since brings both itself
// (VAR_CARE_PACKAGE_GEAR and VAR_CARE_PACKAGE_BULK keep up with VAR_CARE_PACKAGES).
static bool32 TryStartPlaceCarePackageScript(bool32 outdoors)
{
    u32 places = VarGet(VAR_CARE_PACKAGE_PLACES);
    u32 milestones = CountMilestones();
    u16 map = (gSaveBlock1Ptr->location.mapGroup << 8) | gSaveBlock1Ptr->location.mapNum;
    u32 i;

    if (!FlagGet(FLAG_SYS_POKEMON_GET))
        return FALSE;
    if (!(places & CARE_PACKAGE_STARTING_BIT))
    {
        if (!outdoors)
            return FALSE;
        VarSet(VAR_CARE_PACKAGE_PLACES, places | CARE_PACKAGE_STARTING_BIT);
        ScriptContext_SetupScript(EventScript_CarePackageStart);
        return TRUE;
    }
    for (i = 0; i < ARRAY_COUNT(sCarePackagePlaces); i++)
    {
        if (places & (1 << i))
            continue;
        if (sCarePackagePlaces[i].map == map || (outdoors && milestones >= sCarePackagePlaces[i].pastAtBadges))
        {
            VarSet(VAR_CARE_PACKAGE_PLACES, places | (1 << i));
            gSpecialVar_0x8004 = i;
            ScriptContext_SetupScript(EventScript_CarePackagePlace);
            return TRUE;
        }
    }
    return FALSE;
}

bool32 TryStartCarePackageScript(void)
{
    u32 received = VarGet(VAR_CARE_PACKAGES);
    u32 gear = VarGet(VAR_CARE_PACKAGE_GEAR);
    u32 bulk = VarGet(VAR_CARE_PACKAGE_BULK);
    u8 mapType = gMapHeader.mapType;
    bool32 outdoors = (mapType == MAP_TYPE_ROUTE || mapType == MAP_TYPE_OCEAN_ROUTE
                    || mapType == MAP_TYPE_CITY || mapType == MAP_TYPE_TOWN);

    if (TryStartPlaceCarePackageScript(outdoors))
        return TRUE;

    if (mapType != MAP_TYPE_ROUTE && mapType != MAP_TYPE_OCEAN_ROUTE
     && mapType != MAP_TYPE_CITY && mapType != MAP_TYPE_TOWN)
        return FALSE;

    if (gear < received && gear < CARE_PACKAGE_COUNT)
    {
        ScriptContext_SetupScript(EventScript_CarePackageGear);
        return TRUE;
    }
    if (bulk < received && bulk < CARE_PACKAGE_COUNT)
    {
        ScriptContext_SetupScript(EventScript_CarePackageBulk);
        return TRUE;
    }
    if (received >= CARE_PACKAGE_COUNT || received >= CountMilestones())
        return FALSE;

    ScriptContext_SetupScript(EventScript_CarePackage);
    return TRUE;
}
