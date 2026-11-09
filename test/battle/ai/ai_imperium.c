#include "global.h"
#include "test/battle.h"
#include "battle_ai_util.h"

// Crystal Imperium (DECISIONS.md D60): the behaviours behind AI_FLAG_IMPERIUM, Emerald Imperium's AI
// re-implemented. Each test runs with the trainer AI that NORMAL and HARD give every trainer; four
// (Shell Smash with only physical or only special attacks, no boosting below 40% HP, no free charge
// turn) also run without AI_FLAG_IMPERIUM to show the old choice.
#define IMPERIUM_AI (AI_FLAG_BASIC_TRAINER | AI_FLAG_OMNISCIENT | AI_FLAG_SMART_SWITCHING | AI_FLAG_SMART_MON_CHOICES | AI_FLAG_IMPERIUM)
#define IMPERIUM_AI_OFF (IMPERIUM_AI & ~AI_FLAG_IMPERIUM)

AI_SINGLE_BATTLE_TEST("Imperium AI: a safe smasher with only physical attacks uses Shell Smash")
{
    u64 flags;
    PARAMETRIZE { flags = IMPERIUM_AI; }
    PARAMETRIZE { flags = IMPERIUM_AI_OFF; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SHELL_SMASH) == EFFECT_SHELL_SMASH);
        ASSUME(GetMoveCategory(MOVE_ICICLE_SPEAR) == DAMAGE_CATEGORY_PHYSICAL);
        ASSUME(GetMoveCategory(MOVE_ROCK_BLAST) == DAMAGE_CATEGORY_PHYSICAL);
        AI_FLAGS(flags);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_TACKLE); }
        OPPONENT(SPECIES_CLOYSTER) { Speed(100); Moves(MOVE_SHELL_SMASH, MOVE_ICICLE_SPEAR, MOVE_ROCK_BLAST); }
    } WHEN {
        if (flags & AI_FLAG_IMPERIUM)
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_SHELL_SMASH); }
        else
            TURN { MOVE(player, MOVE_TACKLE); NOT_EXPECT_MOVE(opponent, MOVE_SHELL_SMASH); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: a safe smasher with only special attacks uses Shell Smash")
{
    u64 flags;
    PARAMETRIZE { flags = IMPERIUM_AI; }
    PARAMETRIZE { flags = IMPERIUM_AI_OFF; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SHELL_SMASH) == EFFECT_SHELL_SMASH);
        ASSUME(GetMoveCategory(MOVE_WATER_PULSE) == DAMAGE_CATEGORY_SPECIAL);
        ASSUME(GetMoveCategory(MOVE_ICE_BEAM) == DAMAGE_CATEGORY_SPECIAL);
        AI_FLAGS(flags);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_TACKLE); }
        OPPONENT(SPECIES_BLASTOISE) { Speed(100); Moves(MOVE_SHELL_SMASH, MOVE_WATER_PULSE, MOVE_ICE_BEAM); }
    } WHEN {
        if (flags & AI_FLAG_IMPERIUM)
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_SHELL_SMASH); }
        else
            TURN { MOVE(player, MOVE_TACKLE); NOT_EXPECT_MOVE(opponent, MOVE_SHELL_SMASH); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: a slower smasher in KO range attacks, White Herb or not")
{
    u32 item;
    PARAMETRIZE { item = ITEM_NONE; }
    PARAMETRIZE { item = ITEM_WHITE_HERB; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SHELL_SMASH) == EFFECT_SHELL_SMASH);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_RAICHU) { Speed(100); Moves(MOVE_THUNDERBOLT); }
        OPPONENT(SPECIES_CLOYSTER) { Speed(1); Item(item); Moves(MOVE_SHELL_SMASH, MOVE_ICICLE_SPEAR); }
    } WHEN {
        TURN { MOVE(player, MOVE_THUNDERBOLT); EXPECT_MOVE(opponent, MOVE_ICICLE_SPEAR); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: a smasher with its Defense at -3 is held back")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SHELL_SMASH) == EFFECT_SHELL_SMASH);
        ASSUME(GetMoveEffect(MOVE_SCREECH) == EFFECT_DEFENSE_DOWN_2);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_SCREECH, MOVE_TACKLE); }
        OPPONENT(SPECIES_CLOYSTER) { Speed(100); Moves(MOVE_SHELL_SMASH, MOVE_ICICLE_SPEAR); }
    } WHEN {
        TURN { MOVE(player, MOVE_SCREECH); EXPECT_MOVE(opponent, MOVE_SHELL_SMASH); }
        TURN { MOVE(player, MOVE_SCREECH); EXPECT_MOVE(opponent, MOVE_ICICLE_SPEAR); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: no boosting below 40% HP")
{
    u64 flags;
    PARAMETRIZE { flags = IMPERIUM_AI; }
    PARAMETRIZE { flags = IMPERIUM_AI_OFF; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SWORDS_DANCE) == EFFECT_ATTACK_UP_2);
        AI_FLAGS(flags);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_TACKLE); }
        OPPONENT(SPECIES_SCIZOR) { Speed(100); HP(35); MaxHP(100); Moves(MOVE_SWORDS_DANCE, MOVE_X_SCISSOR); }
    } WHEN {
        if (flags & AI_FLAG_IMPERIUM)
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_X_SCISSOR); }
        else
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_SWORDS_DANCE); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: a safe Swords Dance still boosts at 60% HP (the floor is 40%)")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SWORDS_DANCE) == EFFECT_ATTACK_UP_2);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_TACKLE); }
        OPPONENT(SPECIES_SCIZOR) { Speed(100); HP(60); MaxHP(100); Moves(MOVE_SWORDS_DANCE, MOVE_X_SCISSOR); }
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_SWORDS_DANCE); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: a slower Calm Mind user that the foe 2HKOs attacks instead")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_CALM_MIND) == EFFECT_CALM_MIND);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_ALAKAZAM) { Speed(100); Moves(MOVE_PSYCHIC); }
        OPPONENT(SPECIES_MACHAMP) { Speed(1); Moves(MOVE_CALM_MIND, MOVE_FOCUS_BLAST); }
    } WHEN {
        TURN { MOVE(player, MOVE_PSYCHIC); EXPECT_MOVE(opponent, MOVE_FOCUS_BLAST); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: pivots out of a lost trade when faster")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_U_TURN) == EFFECT_HIT_ESCAPE);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_ZIGZAGOON) { Speed(1); Moves(MOVE_SCRATCH, MOVE_GROWL); }
        OPPONENT(SPECIES_ZIGZAGOON) { Speed(2); HP(9); MaxHP(20); Moves(MOVE_U_TURN, MOVE_STRENGTH); }
        OPPONENT(SPECIES_METAGROSS) { Speed(2); Moves(MOVE_METEOR_MASH); }
    } WHEN {
        TURN { MOVE(player, MOVE_GROWL); EXPECT_MOVE(opponent, MOVE_U_TURN); }
    }
}

// The HP-percentage fix reaches every AI (KNOWN_ISSUES #91); it is tested here with the Imperium AI
AI_SINGLE_BATTLE_TEST("Imperium AI: a pivot is still judged at 45% HP after a healing move is scored first")
{
    u32 move1, move2;
    PARAMETRIZE { move1 = MOVE_ROOST; move2 = MOVE_U_TURN; }
    PARAMETRIZE { move1 = MOVE_U_TURN; move2 = MOVE_ROOST; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_U_TURN) == EFFECT_HIT_ESCAPE);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_ZIGZAGOON) { Speed(1); Moves(MOVE_SCRATCH, MOVE_GROWL); }
        OPPONENT(SPECIES_ZIGZAGOON) { Speed(2); HP(9); MaxHP(20); Moves(move1, move2, MOVE_STRENGTH); }
        OPPONENT(SPECIES_METAGROSS) { Speed(2); Moves(MOVE_METEOR_MASH); }
    } WHEN {
        TURN { MOVE(player, MOVE_GROWL); EXPECT_MOVE(opponent, MOVE_U_TURN); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: no pivot without a good switch-in")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_U_TURN) == EFFECT_HIT_ESCAPE);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_ZIGZAGOON) { Speed(1); Moves(MOVE_SCRATCH, MOVE_GROWL); }
        OPPONENT(SPECIES_ZIGZAGOON) { Speed(2); HP(9); MaxHP(20); Moves(MOVE_U_TURN, MOVE_STRENGTH); }
        OPPONENT(SPECIES_ZIGZAGOON) { Speed(1); Level(1); }
    } WHEN {
        TURN { MOVE(player, MOVE_GROWL); EXPECT_MOVE(opponent, MOVE_STRENGTH); }
    }
}

AI_SINGLE_BATTLE_TEST("Imperium AI: never gives a free charge turn")
{
    u64 flags;
    PARAMETRIZE { flags = IMPERIUM_AI; }
    PARAMETRIZE { flags = IMPERIUM_AI_OFF; }
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_SOLAR_BEAM) == EFFECT_SOLAR_BEAM);
        AI_FLAGS(flags);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_TACKLE); }
        OPPONENT(SPECIES_VENUSAUR) { Speed(100); Moves(MOVE_SOLAR_BEAM, MOVE_VINE_WHIP); }
    } WHEN {
        if (flags & AI_FLAG_IMPERIUM)
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_VINE_WHIP); }
        else
            TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_SOLAR_BEAM); }
    }
}

// The six boosts counted as Encore bait are a data fix for every AI; tested here with the Imperium AI
AI_SINGLE_BATTLE_TEST("Imperium AI: no Quiver Dance into a foe with Encore")
{
    GIVEN {
        ASSUME(GetMoveEffect(MOVE_QUIVER_DANCE) == EFFECT_QUIVER_DANCE);
        ASSUME(GetMoveEffect(MOVE_ENCORE) == EFFECT_ENCORE);
        AI_FLAGS(IMPERIUM_AI);
        PLAYER(SPECIES_WOBBUFFET) { Speed(1); Moves(MOVE_ENCORE, MOVE_TACKLE); }
        OPPONENT(SPECIES_VOLCARONA) { Speed(100); Moves(MOVE_QUIVER_DANCE, MOVE_BUG_BUZZ); }
    } WHEN {
        TURN { MOVE(player, MOVE_TACKLE); EXPECT_MOVE(opponent, MOVE_BUG_BUZZ); }
    }
}
