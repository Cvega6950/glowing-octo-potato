// Crystal Imperium: milestone care packages (data/scripts/care_packages.inc).
#include "global.h"
#include "care_packages.h"
#include "event_data.h"
#include "event_scripts.h"
#include "fieldmap.h"
#include "script.h"
#include "constants/flags.h"
#include "constants/map_types.h"
#include "constants/vars.h"

#define CARE_PACKAGE_COUNT 17

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
// gets the battle gear its packages didn't have then, one package per step; a package received
// since brings its gear itself (VAR_CARE_PACKAGE_GEAR keeps up with VAR_CARE_PACKAGES).
bool32 TryStartCarePackageScript(void)
{
    u32 received = VarGet(VAR_CARE_PACKAGES);
    u32 gear = VarGet(VAR_CARE_PACKAGE_GEAR);
    u8 mapType = gMapHeader.mapType;

    if (mapType != MAP_TYPE_ROUTE && mapType != MAP_TYPE_OCEAN_ROUTE
     && mapType != MAP_TYPE_CITY && mapType != MAP_TYPE_TOWN)
        return FALSE;

    if (gear < received && gear < CARE_PACKAGE_COUNT)
    {
        ScriptContext_SetupScript(EventScript_CarePackageGear);
        return TRUE;
    }
    if (received >= CARE_PACKAGE_COUNT || received >= CountMilestones())
        return FALSE;

    ScriptContext_SetupScript(EventScript_CarePackage);
    return TRUE;
}
