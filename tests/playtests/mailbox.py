"""Test mailbox: in a new game, every command does what it says. GIVE_ITEM puts items in the bag,
GIVE_MON adds a Pokemon to the party, WARP moves the player to another map, START_TRAINER_BATTLE
starts a real trainer battle (won here by mashing A with a level 100 Blaziken), and RUN_SCRIPT runs
a field script with its arguments in VAR_0x8004 and up. A command written while another is BUSY
runs after it instead of being dropped."""
from playtest import MB_DONE, MB_ERROR, MB_GIVE_ITEM, MB_GIVE_MON, MB_IDLE, MB_WARP, MB_START_TRAINER_BATTLE, MB_RUN_SCRIPT


def run(t):
    frames = t.new_game()
    t.check(t.mb("layoutVersion") == 1 and t.mb("numVars") == t.const("VARS_END") - t.const("VARS_START"),
            "mailbox layout version and NUM_VARS")

    # GIVE_ITEM: an ordinary item and one of the new key items
    t.check(t.bag_quantity("ITEM_POTION") == 0, "no Potions at the start")
    t.check(t.mailbox_cmd(MB_GIVE_ITEM, t.const("ITEM_POTION"), 3) == MB_DONE and t.mb("result") == 1, "GIVE_ITEM Potion")
    t.check(t.bag_quantity("ITEM_POTION") == 3, f"3 Potions in the bag, got {t.bag_quantity('ITEM_POTION')}")
    t.check(t.mailbox_cmd(MB_GIVE_ITEM, t.const("ITEM_RARE_CANDY_BOX"), 1) == MB_DONE, "GIVE_ITEM Rare Candy Box")
    t.check(t.bag_quantity("ITEM_RARE_CANDY_BOX") == 1, "the Rare Candy Box is in the bag")

    # GIVE_MON
    t.check(t.party_count() == 0, "a new game starts with no Pokemon")
    t.check(t.mailbox_cmd(MB_GIVE_MON, t.const("SPECIES_BLAZIKEN"), 100) == MB_DONE and t.mb("result") == 1, "GIVE_MON")
    t.check(t.party_count() == 1, f"one Pokemon in the party, got {t.party_count()}")
    t.check(t.party_species(0) == t.const("SPECIES_BLAZIKEN"), f"species {t.party_species(0)}")
    t.check(t.party_level(0) == 100, f"level {t.party_level(0)}")

    # WARP: from the bedroom to Twinleaf Town, in front of the player's house
    t.check(t.mb("mapHeaderID") == t.const("MAP_HEADER_TWINLEAF_TOWN_PLAYER_HOUSE_2F"), "starts in the bedroom")
    t.check(t.mailbox_cmd(MB_WARP, t.const("MAP_HEADER_TWINLEAF_TOWN"), 116, 886) == MB_DONE, "WARP")
    t.wait_field()
    t.shot("warped")
    t.check(t.mb("mapHeaderID") == t.const("MAP_HEADER_TWINLEAF_TOWN"), f"map {t.mb('mapHeaderID')}")
    t.check((t.mb("playerX"), t.mb("playerZ")) == (116, 886), f"position {(t.mb('playerX'), t.mb('playerZ'))}")

    # START_TRAINER_BATTLE: Youngster Tristan, through the same StartTrainerBattle an NPC uses
    battles = t.mb("battleCount")
    seen = {}

    def watch(tt):
        if tt.mb("battleCount") != battles and "frame" not in seen:
            seen["frame"] = tt.ds.frame
        if seen.get("frame") and tt.ds.frame - seen["frame"] == 400:
            tt.shot("battle")

    st = t.mailbox_cmd(MB_START_TRAINER_BATTLE, t.const("TRAINER_YOUNGSTER_TRISTAN"), timeout=20000, mash="A", on_frame=watch)
    t.check(st == MB_DONE, "START_TRAINER_BATTLE finished")
    t.check(t.mb("battleCount") == battles + 1, "one battle was started")
    t.check(t.mb("lastBattleType") & 1, f"it was a trainer battle (type {t.mb('lastBattleType'):#x})")  # BATTLE_TYPE_TRAINER
    t.check(t.party_count() == 1, "the party survived")
    t.shot("after_battle")

    # RUN_SCRIPT: the same trainer battle script, started by ID with the trainer in VAR_0x8004
    script = 9900 + 8  # SCRIPT_ID(UNUSED_0397, 8), ImperiumTest_TrainerBattle
    st = t.mailbox_cmd(MB_RUN_SCRIPT, script, t.const("TRAINER_YOUNGSTER_TRISTAN"), timeout=20000, mash="A")
    t.check(st == MB_DONE and t.mb("battleCount") == battles + 2, "RUN_SCRIPT ran the battle script")

    # A command written while another is BUSY waits its turn instead of being dropped
    box = t.mbox()
    potions = t.bag_quantity("ITEM_POTION")
    t.ds.write16(box + 0x2E, t.const("TRAINER_YOUNGSTER_TRISTAN"))
    t.ds.write16(box + 0x36, MB_IDLE)
    t.ds.write16(box + 0x2C, MB_START_TRAINER_BATTLE)
    t.wait_until(lambda: t.mb("pendingCmd") == MB_START_TRAINER_BATTLE, 600, 1, "the battle command to start")
    t.ds.write16(box + 0x2E, t.const("ITEM_POTION"))
    t.ds.write16(box + 0x30, 2)
    t.ds.write16(box + 0x2C, MB_GIVE_ITEM)
    start = t.ds.frame
    while not (t.mb("cmd") == 0 and t.mb("pendingCmd") == 0 and t.mb("status") == MB_DONE):
        t.check(t.ds.frame - start < 20000, "the queued command never finished")
        if (t.ds.frame - start) % 16 == 8:
            t.ds.hold("A")
        elif (t.ds.frame - start) % 16 == 12:
            t.ds.release()
        t.ds.run(1)
    t.ds.release()
    t.check(t.bag_quantity("ITEM_POTION") == potions + 2, "a GIVE_ITEM queued during a battle ran afterwards")

    # Unknown commands are refused
    t.check(t.mailbox_cmd(0x7F) == MB_ERROR, "an unknown command sets status ERROR")
    t.result(f"new game in {frames} frames; item, Pokemon, warp, trainer battle and script all observable")
