// Platinum Imperium: every boss and its stage, the earliest point in the game its battle can
// happen (a badge count or LEVEL_CAP_STAGE_*). CreateNPCTrainerParty (src/battle_main.c) puts all
// of a boss's Pokemon at GetBossLevel(stage), the player's level cap (Crystal Imperium's rule).
// The rival's first battle, on Route 201 with a level-5 starter, stays as it is.
static const struct LevelCapBoss
{
    u16 trainerId;
    u8 stage;
} sLevelCapBosses[] =
{
    {TRAINER_RIVAL_ROUTE_203_PIPLUP, 0},
    {TRAINER_RIVAL_ROUTE_203_TURTWIG, 0},
    {TRAINER_RIVAL_ROUTE_203_CHIMCHAR, 0},
    {TRAINER_PT_ROARK, 0},
    {TRAINER_VALLEY_WINDWORKS_MARS, 1},
    {TRAINER_PT_GARDENIA, 1},
    // Route mini-bosses: one strong trainer on each route
    {TRAINER_PT_NATALIE, 0},
    {TRAINER_PT_SEBASTIAN, 0},
    {TRAINER_PT_MASON, 0},
    {TRAINER_PT_SARAH, 0},
    {TRAINER_PT_TAYLOR, 1},
    {TRAINER_PT_KELSEY, 1},
    {TRAINER_PT_KODY, 1},
    {TRAINER_PT_ZACHARY, 1},
    {TRAINER_PT_LOUIS, 1},
};
