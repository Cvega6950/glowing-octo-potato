#include "global.h"
#include "difficulty.h"
#include "event_data.h"
#include "test/battle.h"

// Crystal Imperium (DECISIONS.md D25, D60): HARD plays by Emerald Imperium's rules, where Gym Badges
// don't boost stats; NORMAL keeps Heart & Soul's Gen 3 boosts.
WILD_BATTLE_TEST("Crystal Imperium: badge boosts on NORMAL, none on HARD", s16 dmg)
{
    u32 difficulty = 0, badge = 0;
    PARAMETRIZE { difficulty = DIFFICULTY_NORMAL; badge = FALSE; }
    PARAMETRIZE { difficulty = DIFFICULTY_NORMAL; badge = TRUE; }
    PARAMETRIZE { difficulty = DIFFICULTY_HARD; badge = FALSE; }
    PARAMETRIZE { difficulty = DIFFICULTY_HARD; badge = TRUE; }
    GIVEN {
        // (the test build reads the difficulty from a variable, not the save's challenge settings)
        SetCurrentDifficultyLevel(difficulty);
        if (badge)
            FlagSet(B_FLAG_BADGE_BOOST_ATTACK);
        else
            FlagClear(B_FLAG_BADGE_BOOST_ATTACK);
        WITH_CONFIG(B_BADGE_BOOST, GEN_3);
        PLAYER(SPECIES_WOBBUFFET);
        OPPONENT(SPECIES_WOBBUFFET);
    } WHEN {
        TURN { MOVE(player, MOVE_SCRATCH); }
    } SCENE {
        HP_BAR(opponent, captureDamage: &results[i].dmg);
    } FINALLY {
        SetCurrentDifficultyLevel(DIFFICULTY_NORMAL);
        FlagClear(B_FLAG_BADGE_BOOST_ATTACK);
        EXPECT_GT(results[1].dmg, results[0].dmg);
        EXPECT_EQ(results[3].dmg, results[2].dmg);
    }
}
