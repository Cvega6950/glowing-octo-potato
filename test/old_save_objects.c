// Crystal Imperium (DECISIONS.md D64): Continue on a save made before its map gained an object, or before an
// object's hide flag changed, uses the map's own template for it (src/overworld.c LoadSaveblockObjEventScripts)
#include "global.h"
#include "fieldmap.h"
#include "overworld.h"
#include "test/test.h"
#include "constants/event_objects.h"
#include "constants/flags.h"

static const struct ObjectEventTemplate sMapObjects[] =
{
    {.localId = 1, .graphicsId = OBJ_EVENT_GFX_WALLACE, .x = 30, .y = 17, .flagId = FLAG_HIDE_SIDE_POSTGAME},
    {.localId = 2, .graphicsId = OBJ_EVENT_GFX_VOLKNER_HNS, .x = 21, .y = 26, .flagId = 0},
};

TEST("Old saves: on Continue a slot the map gained is filled from the map, and hide flags follow the map")
{
    struct MapEvents events = {.objectEventCount = ARRAY_COUNT(sMapObjects), .objectEvents = sMapObjects};
    const struct MapEvents *mapEvents = gMapHeader.events;
    struct ObjectEventTemplate *saved = gSaveBlock1Ptr->objectEventTemplates;

    // The save's templates: the first object without its hide flag, moved by a script; no second one
    CpuFill32(0, saved, sizeof(gSaveBlock1Ptr->objectEventTemplates));
    saved[0] = sMapObjects[0];
    saved[0].flagId = 0;
    saved[0].x = 7;
    gMapHeader.events = &events;
    LoadSaveblockObjEventScripts();
    gMapHeader.events = mapEvents;
    EXPECT_EQ(saved[0].flagId, FLAG_HIDE_SIDE_POSTGAME);
    EXPECT_EQ(saved[0].x, 7);
    EXPECT_EQ(saved[1].localId, 2);
    EXPECT_EQ(saved[1].graphicsId, OBJ_EVENT_GFX_VOLKNER_HNS);
    EXPECT_EQ(saved[1].x, 21);
    EXPECT_EQ(saved[1].y, 26);
    CpuFill32(0, saved, sizeof(gSaveBlock1Ptr->objectEventTemplates));
}
