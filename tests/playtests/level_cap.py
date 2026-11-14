"""Level caps: LevelCap_Get follows the badge table, the cap mode and the game-completed flag, and a
trainer battle receives that cap and the settings bits (FieldBattleDTO -> BattleSystem). Each battle
is started through the test mailbox and won with a level 100 Blaziken."""
from playtest import MB_DONE, MB_GIVE_MON, MB_START_TRAINER_BATTLE

NORMAL = [15, 24, 33, 42, 50, 58, 66, 75, 85]
HARD = [12, 21, 30, 39, 47, 55, 63, 72, 85]
DEFAULT_BITS = (1 << 8) | (1 << 9) | (1 << 11) | (1 << 12) | (1 << 13) | (1 << 14)  # API.md
BATTLE_STATUS_HARD = 1 << 10
BATTLE_STATUS_EASY = 1 << 15


def field_cap(t):
    t.ds.run(2)  # the mailbox refreshes the cap every field frame
    return t.mb("levelCap")


def battle(t, label):
    n = t.mb("battleCount")
    st = t.mailbox_cmd(MB_START_TRAINER_BATTLE, t.const("TRAINER_YOUNGSTER_TRISTAN"), timeout=20000, mash="A")
    t.check(st == MB_DONE and t.mb("battleCount") == n + 1, f"{label}: the trainer battle ran")
    return t.mb("lastBattleLevelCap"), t.mb("lastBattleStatusMask")


def run(t):
    t.new_game()
    t.check(t.mailbox_cmd(MB_GIVE_MON, t.const("SPECIES_BLAZIKEN"), 100) == MB_DONE, "GIVE_MON")

    # The table, read in the field for every badge count and both cap modes.
    for mode, table in ((0, NORMAL), (1, HARD)):
        t.set_var("VAR_IMPERIUM_LEVEL_CAP_MODE", mode)
        for badges in range(9):
            t.set_badge_mask((1 << badges) - 1)
            got = field_cap(t)
            t.check(got == table[badges], f"mode {mode}, {badges} badges: cap {got}, want {table[badges]}")
    t.set_var("VAR_IMPERIUM_LEVEL_CAP_MODE", 2)
    t.check(field_cap(t) == 100, "cap mode OFF: 100")
    t.set_var("VAR_IMPERIUM_LEVEL_CAP_MODE", 7)
    t.set_badge_mask(0)
    t.check(field_cap(t) == 15, "an out-of-range cap mode reads as NORMAL")
    t.set_var("VAR_IMPERIUM_LEVEL_CAP_MODE", 0)

    # What a battle receives: 0 badges.
    t.set_badge_mask(0)
    cap, bits = battle(t, "0 badges")
    t.check(cap == 15, f"0 badges: the battle's cap is {cap}, want 15")
    t.check(bits & 0xFF00 == DEFAULT_BITS, f"default settings bits {bits & 0xFF00:#06x}, want {DEFAULT_BITS:#06x}")

    # 8 badges, HARD difficulty.
    t.set_badge_mask(0xFF)
    t.set_var("VAR_IMPERIUM_DIFFICULTY", 2)
    cap, bits = battle(t, "8 badges")
    t.check(cap == 85, f"8 badges: the battle's cap is {cap}, want 85")
    t.check(bits & BATTLE_STATUS_HARD and not bits & BATTLE_STATUS_EASY, f"HARD bit set: {bits:#06x}")

    # Game completed, EASY difficulty, settings flags off.
    t.set_flag("FLAG_GAME_COMPLETED")
    t.set_var("VAR_IMPERIUM_DIFFICULTY", 1)
    t.set_flag("FLAG_IMPERIUM_FAST_BATTLES", False)
    t.set_flag("FLAG_IMPERIUM_EXP_BOOST", False)
    cap, bits = battle(t, "game completed")
    t.check(cap == 100, f"game completed: the battle's cap is {cap}, want 100")
    want = (DEFAULT_BITS & ~((1 << 8) | (1 << 14))) | BATTLE_STATUS_EASY
    t.check(bits & 0xFF00 == want, f"bits {bits & 0xFF00:#06x}, want {want:#06x}")
    t.result("cap table (NORMAL, HARD, OFF) and battle caps 15 / 85 / 100 with the settings bits")
