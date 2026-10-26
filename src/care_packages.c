// Platinum Imperium: Crystal Imperium's care packages, from PROF. ROWAN
// (data/scripts/care_packages.inc, written by tools/platinum_imperium/care_packages.py).
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

// The badge packages: one for each Gym Badge, then one for becoming Champion
#define CARE_PACKAGE_COUNT 9

// The starting package and the location packages (the generator's PLACES), a bit each in
// VAR_CARE_PACKAGE_PLACES
#define CARE_PACKAGE_STARTING_BIT (1 << 15)

// The place, in the generator's order, and the badge count by which the player is past it for
// sure: a player who never entered a place still gets its package (on the next step outside)
static const struct { u16 map; u8 pastAtBadges; } sCarePackagePlaces[] =
{
    { MAP_OREBURGH_MINE_B1F, 1 },
    { MAP_RAVAGED_PATH,      2 },
    { MAP_VALLEY_WINDWORKS,  2 },
    { MAP_ETERNA_FOREST_1,   2 },
    { MAP_MT_CORONET_N1F1,   3 },
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

// Called on each step. The starting package arrives on a route or in a town once the player has a
// Pokemon; a location package on the first step in its place; the next badge package, out on a
// route or in a town, while milestones are ahead of the packages received.
bool32 TryStartCarePackageScript(void)
{
    u32 received = VarGet(VAR_CARE_PACKAGES);
    u8 mapType = gMapHeader.mapType;
    bool32 outdoors = (mapType == MAP_TYPE_ROUTE || mapType == MAP_TYPE_OCEAN_ROUTE
                    || mapType == MAP_TYPE_CITY || mapType == MAP_TYPE_TOWN);

    if (TryStartPlaceCarePackageScript(outdoors))
        return TRUE;
    if (!outdoors || received >= CARE_PACKAGE_COUNT || received >= CountMilestones())
        return FALSE;

    ScriptContext_SetupScript(EventScript_CarePackage);
    return TRUE;
}
