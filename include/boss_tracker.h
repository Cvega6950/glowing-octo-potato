#ifndef GUARD_BOSS_TRACKER_H
#define GUARD_BOSS_TRACKER_H

// Crystal Imperium: the L menu's BOSSES list (src/boss_tracker.c). Its rows, page by page in play
// order, are generated into src/data/boss_tracker.h by tools/crystal_imperium/boss_tracker.py from its
// own table (the Gym Leaders, the Leagues, RED) and side_battles.py's (the 25 visitors, D41).

enum BossTrackerPage
{
    BOSS_TRACKER_JOHTO,
    BOSS_TRACKER_KANTO,
    BOSS_TRACKER_TO_RED,
    BOSS_TRACKER_PAGE_COUNT,
};

enum BossTrackerKind
{
    BOSS_KIND_GYM,
    BOSS_KIND_LEAGUE,
    BOSS_KIND_RED,
    BOSS_KIND_VISITOR, // a side battle (D41): optional. The others are on the way to Red.
};

// What opens a visitor's battle: as many badges, or a flag (its script's own test)
enum BossTrackerGate
{
    BOSS_GATE_BADGES,
    BOSS_GATE_FLAG,
};

enum BossTrackerState
{
    BOSS_STATE_NOT_YET, // on the way to Red, not beaten, not the next
    BOSS_STATE_NEXT,    // the first one on the way to Red not beaten yet
    BOSS_STATE_BEATEN,  // a visitor's reward received too
    BOSS_STATE_REWARD,  // a visitor beaten whose reward is still waiting
    BOSS_STATE_OPEN,    // a visitor ready to battle
    BOSS_STATE_LOCKED,  // a visitor whose battle isn't open yet
    BOSS_STATE_COUNT,
};

// BossTracker_GetNextRow when everyone on the way to Red is beaten
#define BOSS_TRACKER_NO_NEXT 0xFF

// The screen's columns, in pixels from the left of its list and info windows (28 tiles wide): the
// list's cursor, mark, name and place (BOSS_TRACKER_PLACE_X, after the widest name, is generated)
// and the info window's lines. A row's texts end by BOSS_TRACKER_LIST_RIGHT, clear of the scroll
// arrows at the list's right, and the info's by BOSS_TRACKER_TEXT_RIGHT: boss_tracker.py measures the
// generated ones and test/boss_tracker.c all of them.
#define BOSS_TRACKER_WINDOW_WIDTH 224
#define BOSS_TRACKER_MARK_X       8
#define BOSS_TRACKER_NAME_X       18
#define BOSS_TRACKER_INFO_X       4
#define BOSS_TRACKER_LIST_RIGHT   (BOSS_TRACKER_WINDOW_WIDTH - 20)
#define BOSS_TRACKER_TEXT_RIGHT   (BOSS_TRACKER_WINDOW_WIDTH - 4)
// The top bar's texts (FONT_SMALL) start this far from the screen's sides
#define BOSS_TRACKER_TOPBAR_MARGIN 4

struct BossTrackerRow
{
    const u8 *name;
    const u8 *info;      // what it is and what opens it: the info window's first line
    u16 flag;            // set once beaten: a Gym's badge, a League's champion flag, FLAG_DEFEATED_RED;
                         // a visitor's reward flag (set once its reward is given)
    u16 gate;            // a visitor's badge count or flag
    u16 trainers[2];     // a visitor's trainer IDs (TRAINER_NONE after the last)
    mapsec_u16_t mapsec; // where it is: its map's section
    u8 kind:2;           // enum BossTrackerKind
    u8 gateKind:1;       // enum BossTrackerGate
    u8 female:1;         // a visitor: "talk to her"
};

u32 BossTracker_GetRowCount(void);
const struct BossTrackerRow *BossTracker_GetRow(u32 row);
u32 BossTracker_GetPageStart(u32 page); // BOSS_TRACKER_PAGE_COUNT: the row count
u32 BossTracker_GetPage(u32 row);
u32 BossTracker_GetPlaceX(void);
bool32 BossTracker_IsRequired(u32 row);
bool32 BossTracker_IsBeaten(u32 row);
bool32 BossTracker_IsGateOpen(u32 row);
u32 BossTracker_GetNextRow(void);
enum BossTrackerState BossTracker_GetState(u32 row, u32 nextRow);
u32 BossTracker_CountBeaten(u32 page);
const u8 *BossTracker_GetStateText(u32 row, enum BossTrackerState state);
void BossTracker_BufferTopBarText(u8 *dest, u32 page, s32 side);
void Task_OpenBossTrackerFromLMenu(u8 taskId);

#endif // GUARD_BOSS_TRACKER_H
