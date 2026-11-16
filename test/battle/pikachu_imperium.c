// Crystal Imperium (DECISIONS.md D62): Pikachu keeps D51's stats, and Zippy Zap keeps its sure critical hit (the
// user's choice); what changed is the Light Ball, x1.5, checked in test/battle/hold_effect/light_ball.c
#include "global.h"
#include "test/battle.h"

TEST("Crystal Imperium: Zippy Zap keeps its sure critical hit, 80 power and +2 priority")
{
    EXPECT(MoveAlwaysCrits(MOVE_ZIPPY_ZAP));
    EXPECT_EQ(GetMovePower(MOVE_ZIPPY_ZAP), 80);
    EXPECT_EQ(GetMovePriority(MOVE_ZIPPY_ZAP), 2);
    EXPECT_EQ(GetMoveCategory(MOVE_ZIPPY_ZAP), DAMAGE_CATEGORY_PHYSICAL);
}

// criticalHit: FALSE makes the critical hit roll fail: a sure critical hit doesn't roll
SINGLE_BATTLE_TEST("Crystal Imperium: Zippy Zap goes first, is a critical hit whatever the roll and raises evasion")
{
    GIVEN {
        PLAYER(SPECIES_PIKACHU) { Speed(1); }
        OPPONENT(SPECIES_WOBBUFFET) { Speed(100); }
    } WHEN {
        TURN { MOVE(player, MOVE_ZIPPY_ZAP, criticalHit: FALSE); MOVE(opponent, MOVE_CELEBRATE); }
    } SCENE {
        ANIMATION(ANIM_TYPE_MOVE, MOVE_ZIPPY_ZAP, player);
        MESSAGE("A critical hit!");
        ANIMATION(ANIM_TYPE_GENERAL, B_ANIM_STATS_CHANGE, player);
        ANIMATION(ANIM_TYPE_MOVE, MOVE_CELEBRATE, opponent);
    } THEN {
        EXPECT_EQ(player->statStages[STAT_EVASION], DEFAULT_STAT_STAGE + 1);
    }
}
