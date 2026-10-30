#!/usr/bin/env python3
"""Run a Crystal Imperium emulator play test.

Usage: tools/emurun/emu.py TEST.emu [--rom pokehns.gba] [--elf pokehns.elf] [--out DIR] [--save FILE]
                           [--emulator mgba|vbam]

A .emu file is an emurun script (see emurun.c) with two additions:
  {gSymbol} or {gSymbol+N}   replaced by the symbol's address from the ELF
  !macro(args)               expanded by the helpers below (Python expression)
"""
import argparse
import bisect
import probe
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def number(target, initial=1):
    """Debug-menu numeric entry: UP adds 10^digit, RIGHT selects the next higher digit."""
    out = []
    digits = str(target - initial)[::-1]
    for i, d in enumerate(digits):
        out += ["press UP 2"] * int(d)
        if i < len(digits) - 1:
            out.append("press RIGHT 2")
    return out


def new_game(difficulty=None, easy_catch=True, variety=None, random_wild=False, level_cap=None,
             minimal_grinding=True, place_packages=False):
    """Power-on to the bedroom in New Bark Town with default settings (Minimal Grinding, Easy
    Catch and Wild Variety 30% ON). difficulty="EASY" or "HARD" picks that DIFFICULTY in the
    Difficulty tab; easy_catch=False turns EASY CATCH (first row of the Features tab) off;
    variety="OFF"/"15%"/"60%" sets WILD VARIETY (second row); random_wild=True turns the
    RANDOMIZER on with WILD randomized (MAP SEEDED stays ON); level_cap="OFF"/"NORMAL"/"HARD"
    sets LEVEL CAP (fourth row of the Difficulty tab; NORMAL, or HARD with the HARD preset);
    minimal_grinding=False turns MIN. GRINDING (second row of the Difficulty tab) off. PROF. ELM's
    starting and location care packages are marked as received, so they don't arrive on the first
    steps once the test has a Pokemon (the debug menu's Give Pokemon sets FLAG_SYS_POKEMON_GET);
    place_packages=True leaves them to arrive."""
    out = ["wait 1300", "press START", "wait 60", "press A", "wait 500", "mash A 900", "mash A 900", "mash A 700"]
    # Tabs: MODE, FEATURES, RANDOMIZER, NUZLOCKE, DIFFICULTY, CHALLENGES (confirm)
    out += ["press R", "wait 20"]
    if not easy_catch:
        out += ["press LEFT", "wait 20"]
    if variety:
        # OFF / 15% / 30% / 60%, starting at 30%
        out += ["press DOWN", "wait 20"] + {"OFF": ["press LEFT", "wait 20"] * 2, "15%": ["press LEFT", "wait 20"],
                                             "60%": ["press RIGHT", "wait 20"]}[variety]
    if not easy_catch or variety:
        out += ["shot features_tab.png"]
    out += ["press R", "wait 20"]
    if random_wild:
        # RANDOMIZER (first row) on, then WILD (third row)
        out += ["press RIGHT", "wait 20", "press DOWN", "wait 20", "press DOWN", "wait 20", "press RIGHT", "wait 20",
                "shot randomizer_tab.png"]
    out += ["press R", "wait 20"] * 2
    if difficulty:
        # DIFFICULTY is the first row and starts at NORMAL (EASY / NORMAL / HARD)
        out += ["press " + {"EASY": "LEFT", "HARD": "RIGHT"}[difficulty], "wait 20", "shot difficulty_tab.png"]
    row = 0
    if not minimal_grinding:
        # OFF / ON, starting at ON
        out += ["press DOWN", "wait 20", "press LEFT", "wait 20", "shot min_grinding_row.png"]
        row = 1
    if level_cap:
        caps = ["OFF", "NORMAL", "HARD"]
        steps = caps.index(level_cap) - caps.index("HARD" if difficulty == "HARD" else "NORMAL")
        out += ["press DOWN", "wait 20"] * (3 - row)
        out += ["press " + ("RIGHT" if steps > 0 else "LEFT"), "wait 20"] * abs(steps)
        out += ["shot level_cap_row.png"]
    out += ["press R", "wait 20"]
    out += ["wait 10", "press UP", "wait 30", "press A", "wait 120", "press A", "wait 120"]
    out += ["mash A 1500", "mash A 1200", "wait 300"]
    if not place_packages:
        out += set_flag("FLAG_RECEIVED_STARTING_CARE_PACKAGE") + set_var("VAR_CARE_PACKAGE_PLACES", 0xFFFF)
    return out


START_MENU = {"POKEDEX": 0, "POKEMON": 1, "BAG": 2, "POKENAV": 3, "PLAYER": 4, "SAVE": 5, "OPTION": 6,
              "EXIT": 7, "DEXNAV": 14}


def start_menu(entry):
    """Open the start menu and choose an entry by name, wherever the cursor was left."""
    return ["press START", "wait 40",
            f"menuselect {{sStartMenuCursorPos}} {{sCurrentStartMenuActions}} {{sNumStartMenuActions}} {START_MENU[entry]}",
            "wait 120"]


L_MENU = {"POKEVIAL": 0, "PC": 1, "DEXNAV": 2, "TIME": 3, "STATS": 4, "REPEL": 5, "FOLLOWER": 6, "AUTO_RUN": 7}


def l_menu(entry, open=True):
    """Open the L menu (src/l_menu.c) and choose an entry by name, wherever the cursor was left
    (open=False: the menu is open already)."""
    return (["press L", "wait 40"] if open else []) + [
            f"menuselect {{sLMenuCursorPos}} {{sLMenuActions}} {{sNumLMenuActions}} {L_MENU[entry]}",
            "wait 120"]


def leave_bedroom_get_running_shoes():
    """From the new-game bedroom: the wall-clock scene, downstairs, Mom's intro (Pokegear and
    Running Shoes), then out of the front door into New Bark Town at (20, 12). Real story path."""
    out = walkto(6, 6) + walkto(6, 4, "yx") + walkto(9, 4) + walkto(9, 3, "yx", soft=True)
    # "The clock is stopped..." -> clock screen: confirm, answer YES to "Is this the correct time?"
    out += ["wait 200", "mash A 400", "press A", "wait 120", "press UP", "wait 20", "press A", "wait 200",
            "mash A 200", "wait 300"]
    # The stairs are entered by walking left from (9, 2)
    out += walkto(9, 2, soft=True) + ["hold LEFT 16", "wait 200"]
    # 1F: stepping to (10, 3) starts Mom's intro
    out += walkto(10, 3, soft=True) + ["wait 100", "mash A 1500", "mash A 1500"]
    out += walkto(9, 8, soft=True) + ["hold DOWN 16", "wait 200"]
    return out


OPTION_ROWS = {"TEXTSPEED": 0, "BATTLESCENE": 1, "BATTLESTYLE": 2, "BUTTONMODE": 3, "FOLLOWER": 4,
               "LARGE_FOLLOWER": 5, "AUTORUN": 6}


def option_set(row, choice):
    """START > OPTION, move to `row` (main tab) and set it to choice index `choice` (0 = left-most,
    e.g. ON in an ON/OFF row). Leaving with B saves the options."""
    out = start_menu("OPTION") + ["press DOWN", "wait 10"] * OPTION_ROWS[row]
    out += ["press LEFT", "wait 10"] * 3 + ["press RIGHT", "wait 10"] * choice
    out += [f"shot option_{row.lower()}.png", "press B", "wait 120", "press B", "wait 60"]
    return out


BATTLE_OPTION_ROWS = {"FAST INTRO": 0, "FAST BATTLES": 1, "BATTLE TERRAIN": 2, "BALL PROMPT": 3, "QUICK RUN": 4,
                      "RUN PROMPT": 5}


def battle_option_toggle(row):
    """START > OPTION, R to the BATTLE tab, move to the ON/OFF `row` and switch it (the choices
    wrap around, so one RIGHT always switches). Leaving with B saves the options."""
    out = start_menu("OPTION") + ["press R", "wait 30"] + ["press DOWN", "wait 10"] * BATTLE_OPTION_ROWS[row]
    out += ["press RIGHT", "wait 10", f"shot option_{row.lower().replace(' ', '_')}.png"]
    out += ["press B", "wait 120", "press B", "wait 60"]
    return out


def expect_challenge_bit(field, value, label):
    """Check a one-bit ChallengeSettings option in the save (HnS's ON/OFF options store 0 for ON,
    e.g. fastIntro, fastBattle)."""
    byte, mask = probe.bitfield("ChallengeSettings", field)
    v = probe.resolve({"off": "offsetof(struct SaveBlock3, challengeSettings)"})
    return [f"expectbits8 *{{gSaveBlock3Ptr}}+{v['off'] + byte} {mask} {mask if value else 0} {label}"]


def set_challenge_option(field, value):
    """Set a ChallengeSettings option in the save without the menu, e.g. ("fastBattle", 1) for FAST
    BATTLES OFF (HnS's ON/OFF options store 0 for ON) or ("runType", 3) for QUICK RUN with B."""
    byte, mask = probe.bitfield("ChallengeSettings", field)
    v = probe.resolve({"off": "offsetof(struct SaveBlock3, challengeSettings)"})
    shift = (mask & -mask).bit_length() - 1
    return [f"pokebits8 *{{gSaveBlock3Ptr}}+{v['off'] + byte} {mask} {value << shift}"]


def set_text_speed(choice):
    """Set TEXT SPEED in the save without the menu: 0 SLOW, 1 MID, 2 FAST (a new game's), 3 FASTER."""
    byte, mask = probe.bitfield("SaveBlock2", "optionsTextSpeed")
    shift = (mask & -mask).bit_length() - 1
    return [f"pokebits8 *{{gSaveBlock2Ptr}}+{byte} {mask} {choice << shift}"]


# Moves the battle refuses to choose without an eaten Berry: the sweep's A presses would choose them
# again and again
SWEEP_UNSELECTABLE = ("MOVE_BELCH", "MOVE_STUFF_CHEEKS")


def move_animation_sweep(state, opponent_hp=999, max_frames=3000, first=1, last=None):
    """From a battle saved at the player's action menu (`state`: the player's Pokemon against a
    one-Pokemon trainer), use every move once, 1 to MOVES_COUNT - 1 (no Z-Moves or Max Moves, and
    not SWEEP_UNSELECTABLE): load the state, put the move in the first slot with PP, give the
    opponent `opponent_hp` HP and max HP, in battle and in its party data alike (an HP above the
    party's max HP stalled multi-hit moves' HP bars), so damage doesn't end the battle, choose
    FIGHT and the move, and wait (tapping A for the battle's prompts) until the action menu is back
    or the battle is over (the user fainted, a one-hit KO). A battle animation that never ends
    fails the move's check."""
    v = probe.resolve({"count": "MOVES_COUNT", "pp": "offsetof(struct BattlePokemon, pp)",
                       "hp": "offsetof(struct BattlePokemon, hp)", "maxhp": "offsetof(struct BattlePokemon, maxHP)",
                       "size": "sizeof(struct BattlePokemon)", "moves": "offsetof(struct BattlePokemon, moves)",
                       "php": "offsetof(struct Pokemon, hp)", "pmax": "offsetof(struct Pokemon, maxHP)"})
    ids = probe.resolve({m: m for m in SWEEP_UNSELECTABLE})
    skip = {ids[m] for m in SWEEP_UNSELECTABLE}
    done = ("{gBattlerControllerFuncs}={HandleInputChooseAction@battle_controller_player},"
            "{gMain+4}={CB2_Overworld}")
    hp = []
    if opponent_hp:
        hp = [f"poke16 {{gBattleMons+{v['size'] + v['hp']}}} {opponent_hp}",
              f"poke16 {{gBattleMons+{v['size'] + v['maxhp']}}} {opponent_hp}",
              f"poke16 {{gEnemyParty+{v['php']}}} {opponent_hp}",
              f"poke16 {{gEnemyParty+{v['pmax']}}} {opponent_hp}"]
    out = []
    for move in range(first, (last or v["count"] - 1) + 1):
        if move in skip:
            continue
        out += [f"loadstate {state}",
                f"poke16 {{gBattleMons+{v['moves']}}} {move}",
                f"poke8 {{gBattleMons+{v['pp']}}} 10"] + hp
        out += ["press A", "wait 10", "press A",
                f"waituntilany32 {max_frames} A move_{move}_ends {done}"]
    return out


def wait_action_menu(label, max_frames=1500):
    """Wait for the battle's action menu (FIGHT / BAG / POKEMON / RUN). With FAST BATTLES on (the
    default) the battle's messages go on by themselves, so no button is pressed: an A pressed into
    the intro would land on the menu and choose FIGHT (DECISIONS.md D38)."""
    return [f"waituntil32 {{gBattlerControllerFuncs}} {{HandleInputChooseAction@battle_controller_player}} "
            f"{max_frames} - {label}"]


def battle_style_set():
    """START > OPTION > BATTLE STYLE = SET, so trainer battles never ask "Will you switch?"."""
    out = start_menu("OPTION")
    out += ["press DOWN", "wait 10", "press DOWN", "wait 10", "press RIGHT", "wait 10", "shot options_set.png"]
    out += ["press B", "wait 120", "press B", "wait 60"]
    return out


def open_debug():
    return ["hold R 10", "hold R+START 6", "hold R 6", "wait 40"]


def give_mon(species, level):
    """Debug menu > Give X > Pokemon (Basic)."""
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(species) + ["press A", "wait 30"] + number(level) + ["press A", "wait 60", "mash B 60"]
    return out


def give_egg(species):
    """Debug menu > Give X > Give Egg: an Egg of the species (number), with its egg cycles."""
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30"] + ["press DOWN"] * 3 + ["press A", "wait 30"]
    out += number(species) + ["press A", "wait 60", "mash B 60"]
    return out


def give_item(item_id, quantity=1):
    """Debug menu > Give X > Give item XYZ: item id (number or ITEM_ constant name), then quantity."""
    if isinstance(item_id, str):
        item_id = probe.resolve({item_id: item_id})[item_id]
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press A", "wait 30"]
    out += number(item_id) + ["press A", "wait 30"] + number(quantity) + ["press A", "wait 60", "mash B 60"]
    return out


def hold_item(item, party_slot=0, pocket="POCKET_ITEMS"):
    """Give the party Pokemon in party_slot an item to hold: the debug menu puts it in the bag,
    then Bag > pocket > its first item > GIVE (right of USE in the 2x2 menu) > the Pokemon. The
    pocket must hold no other item (give and hold one item at a time)."""
    out = give_item(item) + open_bag_at(pocket, 0)
    out += ["press A", "wait 20", "press RIGHT", "wait 10", "press A", "wait 120"]
    out += ["press DOWN", "wait 10"] * party_slot
    return out + ["press A", "wait 120", "mash B 200", "wait 60"]


def party_cursor(slot):
    """In the party menu, move the cursor to a party slot: it starts where the last party menu left
    it (after a GIVE to slot 4, on slot 4)."""
    v = probe.resolve({"off": "offsetof(struct PartyMenu, slotId)"})
    return [f"seek8 {{gPartyMenu+{v['off']}}} {slot} DOWN UP", "wait 10"]


def dex_flags_from_party():
    """Debug menu > Flags & Vars > Pokedex Flags Reset: the Pokedex lists exactly the Pokemon in
    the party and boxes as seen and caught (debug-given Pokemon are not registered otherwise)."""
    return open_debug() + ["press DOWN"] * 7 + ["press A", "wait 30"] + ["press DOWN"] * 3 + ["press A", "wait 60", "mash B 120"]


def debug_flags_menu(row):
    """Debug menu > Flags & Vars > the row-th entry (10: all badges, 11: game clear)."""
    return open_debug() + ["press DOWN"] * 7 + ["press A", "wait 30"] + ["press DOWN"] * row + ["press A", "wait 60", "mash B 120"]


def fill_tm_case():
    """Debug menu > PC/Bag > Fill > Fill Pocket TMHM: one of every TM and HM."""
    return open_debug() + ["press DOWN", "press A", "wait 30", "press DOWN", "press A", "wait 30"] + \
        ["press DOWN"] * 5 + ["press A", "wait 60", "mash B 60"]


def save_and_continue():
    """START > SAVE, hard reset, then CONTINUE (the test runs with a real cartridge save)."""
    return start_menu("SAVE") + ["press A", "wait 400", "mash A 300", "reset", "wait 1300", "press START",
                                 "wait 320", "press A", "wait 100", "press A", "wait 900"]


def tm_case_slot(index, field=0):
    """Address of the TM case's index-th slot (plus `field` bytes): it lives in EWRAM
    (gBagPockets[POCKET_TM_HM].itemSlots)."""
    v = probe.resolve({"ptr": "POCKET_TM_HM * sizeof(struct BagPocket) + offsetof(struct BagPocket, itemSlots)",
                       "stride": "sizeof(struct ItemSlot)"})
    return f"*{{gBagPockets+{v['ptr']}}}+{index * v['stride'] + field}"


def take_from_tm_case(*items):
    """After fill_tm_case, which puts machine n in slot n - 1, take TMs ("ITEM_TM_SNATCH", ...) out of
    the TM case again: each one's slot is checked to hold it, then emptied."""
    out = []
    for item in items:
        v = probe.resolve({"slot": f"ENUM_TM_HM_{item[8:]}", "item": item, "qty": "offsetof(struct ItemSlot, quantity)"})
        out += [f"expect16 {tm_case_slot(v['slot'])} {v['item']} case_slot_{v['slot']}_{item[8:].lower()}",
                f"poke16 {tm_case_slot(v['slot'])} 0", f"poke16 {tm_case_slot(v['slot'], v['qty'])} 0"]
    return out


def expect_item_price(item, want, label):
    """Check an item's price in the item data (gItemsInfo), e.g. expect_item_price("ITEM_TM_TOXIC", 100, "l")."""
    v = probe.resolve({"off": f"{item} * sizeof(struct ItemInfo) + offsetof(struct ItemInfo, price)", "want": str(want)})
    return [f"expect32 {{gItemsInfo+{v['off']}}} {v['want']} {label}"]


# A shop's buy list (src/shop.c, whose structs no header has): struct MartInfo's listCount, the
# items before CANCEL; struct ShopData's selectedRow and scrollOffset, after its 0x2000 bytes of
# tilemap buffers, a u32 and a u16 (Task_BuyMenu copies them from the list every frame), then
# after maxQuantity the task of the scroll arrows (TASK_NONE, 0xFF, when there are none)
BUY_LIST_COUNT = "{sMartInfo+16}"
BUY_LIST_ROW = "*{sShopData}+8198"
BUY_LIST_SCROLL = "*{sShopData}+8200"
BUY_LIST_ARROWS = "*{sShopData}+8204"


def buy_list_entry(index):
    """Address of the item id of the buy list's index-th entry (sListMenuItems, struct ListMenuItem)."""
    v = probe.resolve({"id": "offsetof(struct ListMenuItem, id)", "size": "sizeof(struct ListMenuItem)"})
    return f"*{{sListMenuItems}}+{v['id'] + index * v['size']}"


def buy_one():
    """In a shop's buy list, buy the item under the cursor when it comes one at a time (a reusable TM):
    A, YES to "You wanted ...? That'll be ¥100.", then A after "Here you go! Thank you." Ends on the list."""
    return ["press A", "wait 90", "press A", "wait 90", "press A", "wait 60"]


def snap_buy_list_edge():
    """Remember the strip under the buy list's last row (left of its scroll arrow): only a message
    box covers it, so buy_one_on_time can see the list come back."""
    return ["snaprect buy_list_edge 120 145 36 6"]


def buy_one_on_time(frames, label):
    """buy_one, checking that the list is back on screen within `frames` frames of the last A, the
    strip snap_buy_list_edge remembered showing again (D43: 6 to 8 frames with 198 TMs on sale;
    0.14.2, which checked every TM again and drew the list twice, took 26 to 30)."""
    return ["press A", "wait 90", "press A", "wait 90", "hold A 1", f"expectrectwithin buy_list_edge {frames} {label}",
            "wait 60"]


def expect_buy_list(count, items, absent=(), label="buy_list"):
    """Check a shop's buy list: `count` items, the first ones `items` in order (all of them when
    len(items) == count), then CANCEL right after the last; and none of `absent`."""
    v = probe.resolve({i: i for i in list(items) + list(absent)} | {"LIST_CANCEL": "LIST_CANCEL",
                      "size": "sizeof(struct ListMenuItem)"})
    out = [f"expect16 {BUY_LIST_COUNT} {count} {label}_count_{count}"]
    out += [f"expect16 {buy_list_entry(n)} {v[i]} {label}_{n}_{i[8:].lower()}" for n, i in enumerate(items)]
    out.append(f"expect16 {buy_list_entry(count)} {v['LIST_CANCEL'] & 0xFFFF} {label}_cancel_last")
    out += [f"expectnotfind16 {buy_list_entry(0)} {count} {v['size']} {v[i]} {label}_lacks_{i[8:].lower()}" for i in absent]
    return out


def expect_buy_arrows(shown, label):
    """Check whether the buy list has its scroll arrows (only a list longer than the window does)."""
    return [f"expect{'ne' if shown else ''}8 {BUY_LIST_ARROWS} 255 {label}_{'arrows' if shown else 'no_arrows'}"]


def expect_buy_cursor(scroll, row, item, label):
    """Check the buy list's scroll offset and cursor row, and the item there ("LIST_CANCEL" for CANCEL)."""
    v = probe.resolve({item: item})
    return [f"expect16 {BUY_LIST_SCROLL} {scroll} {label}_scroll_{scroll}", f"expect16 {BUY_LIST_ROW} {row} {label}_row_{row}",
            f"expect16 {buy_list_entry(scroll + row)} {v[item] & 0xFFFF} {label}_on_{item.split('_', 2)[-1].lower()}"]


def expect_bag_has(pocket, item, label=None):
    """Check that a bag pocket (struct Bag field: items, keyItems, pokeBalls, ...) holds the item.
    "TMsHMs" is the TM case, which is not in SaveBlock1 any more (TMHM_POCKET_COUNT)."""
    if pocket == "TMsHMs":
        v = probe.resolve({"count": "TMHM_POCKET_COUNT", "stride": "sizeof(struct ItemSlot)", item: item})
        return [f"expectfind16 {tm_case_slot(0)} {v['count']} {v['stride']} {v[item]} {label or 'bag_has_' + item.lower()}"]
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})",
                       "count": f"ARRAY_COUNT(((struct SaveBlock1 *)0)->bag.{pocket})",
                       "stride": "sizeof(struct ItemSlot)", item: item})
    return [f"expectfind16 *{{gSaveBlock1Ptr}}+{v['off']} {v['count']} {v['stride']} {v[item]} {label or 'bag_has_' + item.lower()}"]


def expect_bag_lacks(pocket, item, label=None):
    """Check that a bag pocket (struct Bag field) doesn't hold the item."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})",
                       "count": f"ARRAY_COUNT(((struct SaveBlock1 *)0)->bag.{pocket})",
                       "stride": "sizeof(struct ItemSlot)", item: item})
    return [f"expectnotfind16 *{{gSaveBlock1Ptr}}+{v['off']} {v['count']} {v['stride']} {v[item]} "
            f"{label or 'bag_lacks_' + item.lower()}"]


def expect_bag_quantity(pocket, item, want, label=None):
    """Check how many of the item a bag pocket (struct Bag field) holds: quantities are stored XORed
    with the save's encryption key (src/item.c)."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})",
                       "count": f"ARRAY_COUNT(((struct SaveBlock1 *)0)->bag.{pocket})",
                       "stride": "sizeof(struct ItemSlot)", "key": "offsetof(struct SaveBlock2, encryptionKey)", item: item})
    return [f"expectqty16 *{{gSaveBlock1Ptr}}+{v['off']} {v['count']} {v['stride']} {v[item]} {want} "
            f"*{{gSaveBlock2Ptr}}+{v['key']} {label or 'bag_' + item.lower() + '_x' + str(want)}"]


def expect_summary_nature(nature, label):
    """Check the nature the summary screen just put in its text: the dynamic placeholder it is
    printed through ({DYNAMIC 2}) points at that nature's name (src/bw_summary_screen.c)."""
    v = probe.resolve({"off": f"{nature} * sizeof(struct NatureInfo) + offsetof(struct NatureInfo, name)"})
    return [f"expectsame32 {{sStringPointers+8}} {{gNaturesInfo+{v['off']}}} {label}"]


def fill_pocket(pocket, item, slots=None):
    """Fill every slot of a bag pocket (struct Bag field) with one item, so no other item fits; or
    only the first `slots` slots."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})",
                       "count": f"ARRAY_COUNT(((struct SaveBlock1 *)0)->bag.{pocket})",
                       "stride": "sizeof(struct ItemSlot)", item: item})
    return [f"poke16 *{{gSaveBlock1Ptr}}+{v['off'] + i * v['stride']} {v[item]}"
            for i in range(v["count"] if slots is None else slots)]


def expect_pocket_slot_empty(pocket, index, label):
    """Check that slot `index` of a bag pocket (struct Bag field) holds no item."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})", "stride": "sizeof(struct ItemSlot)"})
    return [f"expect16 *{{gSaveBlock1Ptr}}+{v['off'] + index * v['stride']} 0 {label}"]


def empty_pocket(pocket):
    """Undo fill_pocket: every slot of the bag pocket (struct Bag field) back to ITEM_NONE (the bag
    sets a slot's quantity when it next puts an item there)."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, bag.{pocket})",
                       "count": f"ARRAY_COUNT(((struct SaveBlock1 *)0)->bag.{pocket})",
                       "stride": "sizeof(struct ItemSlot)"})
    return [f"poke16 *{{gSaveBlock1Ptr}}+{v['off'] + i * v['stride']} 0" for i in range(v["count"])]


def fill_pc(item):
    """Fill every slot of the PC's item storage (SaveBlock1 pcItems) with one item."""
    v = probe.resolve({"off": "offsetof(struct SaveBlock1, pcItems)", "count": "PC_ITEMS_COUNT",
                       "stride": "sizeof(struct ItemSlot)", item: item})
    return [f"poke16 *{{gSaveBlock1Ptr}}+{v['off'] + i * v['stride']} {v[item]}" for i in range(v["count"])]


def expect_pc_has(item, label=None):
    """Check that the PC's item storage (SaveBlock1 pcItems) holds the item."""
    v = probe.resolve({"off": "offsetof(struct SaveBlock1, pcItems)", "count": "PC_ITEMS_COUNT",
                       "stride": "sizeof(struct ItemSlot)", item: item})
    return [f"expectfind16 *{{gSaveBlock1Ptr}}+{v['off']} {v['count']} {v['stride']} {v[item]} {label or 'pc_has_' + item.lower()}"]


def care_package_steps(count):
    """Step back and forth on Route 29's (33,11)-(34,11), starting with (33,11) (so not from there),
    and read through each package that arrives."""
    out = []
    for k in range(count):
        out += walkto(33 if k % 2 == 0 else 34, 11, soft=True) + ["wait 30", f"shot care_package_{k:02d}.png", "mash A 2400"]
    return out


def cheat_start():
    """Debug menu > Utilities > Cheat start (sets all eight badge flags, among others)."""
    return open_debug() + ["press A", "wait 30"] + ["press DOWN"] * 6 + ["press A", "wait 300", "mash B 120"]


def max_money():
    """Debug menu > Give X > Max Money."""
    return open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30"] + ["press DOWN"] * 5 + ["press A", "wait 60", "mash B 60"]


def warp(group, num, warp_id=0):
    """Debug menu > Utilities > Warp to map warp: map group, map number, warp id."""
    out = open_debug() + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(group, initial=0) + ["press A", "wait 20"]
    out += number(num, initial=0) + ["press A", "wait 20"]
    out += number(warp_id, initial=0) + ["press A", "wait 400"]
    return out


def yes_no(yes, label, shot=None):
    """At a script message that ends in a YES/NO box (MSGBOX_YESNO): B through the message until the
    box is up (the script then waits: sGlobalScriptContextStatus is CONTEXT_WAITING, 1 in
    src/script.c), then A for YES or B for NO."""
    out = [f"waituntil8 {{sGlobalScriptContextStatus}} 1 1500 B {label}", "wait 10"]
    if shot:
        out.append(f"shot {shot}")
    return out + [f"press {'A' if yes else 'B'}", "wait 30"]


def walk(*steps):
    """walk("UP", 4, "RIGHT", 2): one tile is 16 frames at walking speed; hold B is not used."""
    out = []
    for d, n in zip(steps[::2], steps[1::2]):
        out += [f"hold {d} {16 * n}", "wait 10"]
    return out


def open_bag_at(pocket, index):
    """START > BAG, then move to `pocket` (constant name) and its index-th item, using the bag's
    own position data (it remembers the last pocket and cursor)."""
    v = probe.resolve({"pocket_off": "offsetof(struct BagPosition, pocket)",
                       "cursor_off": "offsetof(struct BagPosition, cursorPosition)",
                       pocket: pocket})
    cursor = f"{{gBagPosition+{v['cursor_off'] + 2 * v[pocket]}}}"
    return start_menu("BAG") + [f"seek8 {{gBagPosition+{v['pocket_off']}}} {v[pocket]} RIGHT LEFT", "wait 20",
                                f"seek16 {cursor} {index} DOWN UP", "wait 10"]


def use_key_item(index):
    """Use the index-th Key Item from the bag (USE is the first context-menu entry), then close the bag."""
    out = open_bag_at("POCKET_KEY_ITEMS", index)
    out += ["press A", "wait 20", "press A", "wait 120", "mash B 200", "wait 60"]
    return out


def set_flag(flag, value=1):
    """Set (1) or clear (0) an event flag by constant name, e.g. set_flag("FLAG_SYS_GAME_CLEAR")."""
    v = probe.resolve({"flags": "offsetof(struct SaveBlock1, flags)", flag: flag})
    return [f"setflag {{gSaveBlock1Ptr}} {v['flags']} {v[flag]} {value}"]


def expect_flag(flag, want, label=None):
    """Check an event flag by constant name, e.g. expect_flag("FLAG_INFINITE_REPEL_ON", 1)."""
    v = probe.resolve({"flags": "offsetof(struct SaveBlock1, flags)", flag: flag})
    return [f"expectflag {{gSaveBlock1Ptr}} {v['flags']} {v[flag]} {want} {label or flag.lower()}"]


def set_var(var, value):
    """Set a script variable (VAR_*) in the save block; value may be a number or a C expression."""
    v = probe.resolve({"vars": "offsetof(struct SaveBlock1, vars)", var: f"({var} - VARS_START) * 2",
                       "value": str(value)})
    return [f"poke16 *{{gSaveBlock1Ptr}}+{v['vars'] + v[var]} {v['value']}"]


def no_care_packages():
    """Mark every care package as received (the starting one, the location ones and the 17
    milestone packages, with the catch-up counters of earlier releases and the TMs' nine tiers, D48),
    so none arrives during the test."""
    return (set_flag("FLAG_RECEIVED_STARTING_CARE_PACKAGE") + set_var("VAR_CARE_PACKAGE_PLACES", 0xFFFF)
            + set_var("VAR_CARE_PACKAGES", 17) + set_var("VAR_CARE_PACKAGE_IMPERIUM", 17)
            + set_var("VAR_CARE_PACKAGE_GEAR", 17) + set_var("VAR_CARE_PACKAGE_BULK", 17)
            + set_var("VAR_CARE_PACKAGE_TMS", 9))


def care_package_total(item, packages):
    """How many of the item (without ITEM_) the given care packages (0: the start, 1-17: the
    milestones, 18 on: the location packages) hold in all, from
    tools/crystal_imperium/care_packages.py's table."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "care_packages", os.path.join(HERE, "..", "crystal_imperium", "care_packages.py"))
    table = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(table)
    return sum(n for k in packages for name, n in table.all_packages()[k] if name == item)


def expect_var(var, want, label=None):
    """Check a script variable (VAR_*) in the save block; want may be a number or a C expression."""
    v = probe.resolve({"vars": "offsetof(struct SaveBlock1, vars)", var: f"({var} - VARS_START) * 2",
                       "want": str(want)})
    return [f"expect16 *{{gSaveBlock1Ptr}}+{v['vars'] + v[var]} {v['want']} {label or var.lower()}"]


def set_save(block, field, value, size=8):
    """Write a save block field, e.g. set_save(1, "outbreakPokemonSpecies", "SPECIES_PIKACHU", 16);
    value may be a number or a C expression."""
    ptr = {1: "gSaveBlock1Ptr", 2: "gSaveBlock2Ptr", 3: "gSaveBlock3Ptr"}[block]
    v = probe.resolve({"off": f"offsetof(struct SaveBlock{block}, {field})", "value": str(value)})
    return [f"poke{size} *{{{ptr}}}+{v['off']} {v['value'] & ((1 << size) - 1)}"]


def expect_battle_style(const, label):
    """In battle: the style the battle plays (gBattleScripting.battleStyle) is OPTIONS_BATTLE_STYLE_SET
    or _SHIFT."""
    v = probe.resolve({"off": "offsetof(struct BattleScripting, battleStyle)", const: const})
    return [f"expect8 {{gBattleScripting+{v['off']}}} {v[const]} {label}"]


def expect_window(window, field, want, label):
    """A window's template field (e.g. tilemapLeft) in gWindows; window is a constant such as
    B_WIN_ACTION_MENU."""
    v = probe.resolve({"off": f"offsetof(struct Window, window.{field}) + sizeof(struct Window) * {window}"})
    return [f"expect8 {{gWindows+{v['off']}}} {want} {label}"]


def expect_listed(base, count, const, label):
    """One of `count` 16-bit entries from `base` (e.g. a DexNav row) is the game constant `const`."""
    v = probe.resolve({const: const})
    return [f"expectfind16 {base} {count} 2 {v[const]} {label}"]


def set_save1(field, value, size=8):
    """Write a SaveBlock1 field, e.g. set_save1("flashLevel", 1)."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, {field})", "value": str(value)})
    return [f"poke{size} *{{gSaveBlock1Ptr}}+{v['off']} {v['value']}"]


def expect_save1(field, want, label, size=8):
    """Check a SaveBlock1 field, e.g. expect_save1("flashLevel", 0, "label")."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock1, {field})", "want": str(want)})
    return [f"expect{size} *{{gSaveBlock1Ptr}}+{v['off']} {v['want']} {label}"]


def set_save2(field, value, size=8):
    """Write a SaveBlock2 field, e.g. set_save2("optionsButtonMode", "OPTIONS_BUTTON_MODE_L_EQUALS_A")."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock2, {field})", "value": str(value)})
    return [f"poke{size} *{{gSaveBlock2Ptr}}+{v['off']} {v['value']}"]


def set_save3(field, value, size=8):
    """Write a SaveBlock3 field, e.g. set_save3("dexNavChain", 7)."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock3, {field})", "value": str(value)})
    return [f"poke{size} *{{gSaveBlock3Ptr}}+{v['off']} {v['value']}"]


def expect_save3(field, want, label, size=8):
    """Check a SaveBlock3 field, e.g. expect_save3("dexNavSearchLevels[19]", 1, "label")."""
    v = probe.resolve({"off": f"offsetof(struct SaveBlock3, {field})", "want": str(want)})
    return [f"expect{size} *{{gSaveBlock3Ptr}}+{v['off']} {v['want']} {label}"]


def expect_easy_catch(on, label):
    """Check EASY CATCH (ChallengeSettings.tx_Features_EasyCatchOff, 0 when on)."""
    byte, mask = probe.bitfield("ChallengeSettings", "tx_Features_EasyCatchOff")
    v = probe.resolve({"off": "offsetof(struct SaveBlock3, challengeSettings)"})
    return [f"expectbits8 *{{gSaveBlock3Ptr}}+{v['off'] + byte} {mask} {0 if on else mask} {label}"]


def expect_money(want, label=None):
    """Check the player's money: stored XORed with the save's encryption key (src/money.c)."""
    v = probe.resolve({"money": "offsetof(struct SaveBlock1, money)", "key": "offsetof(struct SaveBlock2, encryptionKey)",
                       "want": str(want)})
    return [f"expectxor32 *{{gSaveBlock1Ptr}}+{v['money']} *{{gSaveBlock2Ptr}}+{v['key']} {v['want']} "
            f"{label or 'money'}"]


def expect_dex_caught(species, want, label=None):
    """Check a Pokemon's caught flag in the Pokedex (SaveBlock1 dexCaught, a bit per National Dex
    number from 1), through the event-flag check on that bit array."""
    v = probe.resolve({"off": "offsetof(struct SaveBlock1, dexCaught)", "num": "NATIONAL_DEX_" + species[len("SPECIES_"):]})
    return [f"expectflag {{gSaveBlock1Ptr}} {v['off']} {v['num'] - 1} {want} {label or 'caught_' + species.lower()}"]


# The code naming screen's upper-case keyboard (src/naming_screen.c sKeyboardChars)
NAMING_KEYS = ["ABCDEF .", "GHIJKL ,", "MNOPQRS ", "TUVWXYZ "]


def type_code(text):
    """On the code naming screen (upper-case letters, the cursor on A): move to each letter of the
    text and press A, then START (the cursor to OK) and A."""
    out, x, y = [], 0, 0
    for ch in text.upper():
        ty = next(r for r, row in enumerate(NAMING_KEYS) if ch in row)
        tx = NAMING_KEYS[ty].index(ch)
        out += ["press RIGHT 2", "wait 8"] * max(tx - x, 0) + ["press LEFT 2", "wait 8"] * max(x - tx, 0)
        out += ["press DOWN 2", "wait 8"] * max(ty - y, 0) + ["press UP 2", "wait 8"] * max(y - ty, 0)
        out += ["press A 2", "wait 12"]
        x, y = tx, ty
    return out + ["wait 20", "press START 2", "wait 30", "press A 2", "wait 60"]


def nes_code(text, shot=None):
    """At the NES in the bedroom (from (4, 3), facing it): turn it on, YES to "Enter a code?", type
    the code; the result's message is on screen after."""
    out = walkto(4, 3, path=True) + ["press UP", "wait 20", "press A", "wait 150", "press A", "wait 250"]
    if shot:
        out += [f"shot {shot}"]
    return out + type_code(text) + ["wait 250"]


def expect_follower(on, label):
    """Check the follower Pokemon setting: followerEnable, the first bit of ChallengeSettings, is 0
    when a Pokemon follows (on=True)."""
    v = probe.resolve({"off": "offsetof(struct SaveBlock3, challengeSettings)"})
    return [f"expectbits8 *{{gSaveBlock3Ptr}}+{v['off']} 1 {0 if on else 1} {label}"]


def tally_species_not_in(name, *species, addr="{gBattleMons+136}"):
    """Count a run as a hit when the wild Pokemon (battler 1), or the species at `addr`, is none
    of the given species (SPECIES_ constants, or numbers such as "0")."""
    v = probe.resolve({s: s for s in species if not s.isdigit()})
    return [f"tallynotin {name} {addr} " + ",".join(s if s.isdigit() else str(v[s]) for s in species)]


ROUTE29_SPECIES = ("SPECIES_PIDGEY", "SPECIES_SENTRET", "SPECIES_HOPPIP", "SPECIES_RATTATA", "SPECIES_HOOTHOOT")
NATIONAL_PARK_SPECIES = ("SPECIES_CATERPIE", "SPECIES_NIDORAN_F", "SPECIES_NIDORAN_M", "SPECIES_SCYTHER", "SPECIES_SUNKERN",
                         "SPECIES_WEEDLE", "SPECIES_HOOTHOOT", "SPECIES_MURKROW", "SPECIES_PSYDUCK", "SPECIES_SPINARAK",
                         "SPECIES_VENONAT")


def wild_variety_sample(name, runs, state="route29.ss", grass=(24, 21, 25, 14), species=ROUTE29_SPECIES, listed=None,
                        not_in=()):
    """From a saved state at a grass edge, walk into the grass until a wild battle starts, `runs`
    times at different frame offsets, tallying wild Pokemon that are not one of the area's own
    `species`. grass = (entry x, pace from x, pace to x, row y), Route 29's by default. Each
    battle is left by loading the state again. listed="LIST" also tallies, as NAME_not_listed,
    wild Pokemon missing from a list remembered by snap_dexnav_rows (DexNav's rows). A run without
    a battle (an NPC talked first) counts for neither; NAME_battles counts the runs with one.
    not_in=(("SUFFIX", "LIST"), ...) tallies, as NAME_SUFFIX, wild Pokemon missing from each other
    remembered LIST."""
    entry, x1, x2, y = grass
    out = []
    for k in range(runs):
        out += [f"loadstate {state}", f"wait {1 + 23 * k}", "poke16 {gBattleMons+136} 0"]
        out += walkto(entry, y, soft=True) + pace(x1, x2, y, 10, soft=True)
        out += ["wait 300", f"shot {name}_{k:02d}.png", f"tally32 {name}_battles {{gMain+4}} {{BattleMainCB2+1}}"]
        out += tally_species_not_in(name, *species, "0")
        if listed:
            out += [f"tallynotin {name}_not_listed {{gBattleMons+136}} @{listed},0"]
        out += [f"tallynotin {name}_{suffix} {{gBattleMons+136}} @{other},0" for suffix, other in not_in]
    return out


def fish_sample(name, runs, state, rod_index, listed, species=()):
    """From a saved state facing water, cast the rod at `rod_index` in the Key Items pocket `runs`
    times at different frame offsets (HnS's default FISHING setting needs no timing: a bite is
    hooked, and A starts the battle). Tallies as NAME the wild Pokemon that are neither on the
    list `listed` (remembered by snap_dexnav_rows) nor one of `species` (the area's fishing
    Pokemon), and as NAME_battles the casts that led to a battle."""
    v = probe.resolve({s: s for s in species})
    allowed = ",".join([f"@{listed}", "0"] + [str(v[s]) for s in species])
    out = []
    for k in range(runs):
        out += [f"loadstate {state}", f"wait {1 + 17 * k}", "poke16 {gBattleMons+136} 0"]
        out += open_bag_at("POCKET_KEY_ITEMS", 0) + ["press DOWN", "wait 10"] * rod_index
        out += ["press A", "wait 20", "press A", "wait 300", "mash A 120", "wait 400", f"shot {name}_{k:02d}.png"]
        out += [f"tally32 {name}_battles {{gMain+4}} {{BattleMainCB2+1}}", f"tallynotin {name} {{gBattleMons+136}} {allowed}"]
    return out


def snap_dexnav_rows(name):
    """With DexNav open, remember its land and water rows (sDexNavUiDataPtr->landSpecies at +6,
    twelve entries, then waterSpecies, five) as the list NAME."""
    return [f"snap16 {name} *{{sDexNavUiDataPtr}}+6 17"]


def expect_const(addr, const, label, size=16, negate=False):
    """Check a memory value against a game constant, e.g. expect_const("*{ptr}+0", "SPECIES_X", "l")."""
    v = probe.resolve({const: const})
    return [f"expect{'ne' if negate else ''}{size} {addr} {v[const]} {label}"]


def expect_const_seen(species, label):
    """An autobattle since the last seenreset saw the opponent's battler as this species."""
    return [f"expectseen {probe.resolve({species: species})[species]} {label}"]


def var_addr(var):
    """Address expression of a script variable (VAR_*) in the save block."""
    v = probe.resolve({"addr": f"offsetof(struct SaveBlock1, vars) + ({var} - VARS_START) * 2"})
    return f"*{{gSaveBlock1Ptr}}+{v['addr']}"


def dexnav_hidden_sample(runs, state="grass.ss"):
    """DexNav detector mode: from a saved state standing in grass, set the hidden-Pokemon step
    counter one short of its 100-step check, take a step (a 25% chance of a detection), and if a
    hidden Pokemon was found, creep up on it. Tallies detections and the battles they lead to."""
    out = []
    for k in range(runs):
        out += [f"loadstate {state}", f"wait {1 + 13 * k}", f"poke16 {var_addr('VAR_DEXNAV_STEP_COUNTER')} 99"]
        out += walkto(23, 14, soft=True) + ["wait 40", f"shot hidden_{k:02d}.png"]
        out += ["tallynotin hidden_detected {sDexNavSearchDataPtr} 0"]
        out += walkto("@*{sDexNavSearchDataPtr}+18~7", "@*{sDexNavSearchDataPtr}+20~7", creep=True, path=True, soft=True)
        out += ["wait 400", f"shot hidden_battle_{k:02d}.png", "tally32 hidden_battle {gMain+4} {BattleMainCB2+1}"]
    return out


def expect_battler(battler, field, const, label=None, negate=False, bits=16):
    """Check a gBattleMons field (species, ability, moves[N], hp, ...) of a battler against a game
    constant or a number (negate: it must differ); bits=8 for a u8 field such as friendship."""
    v = probe.resolve({f"bm_{field}".replace("[", "_").replace("]", ""): f"offsetof(struct BattlePokemon, {field})",
                       "bm_size": "sizeof(struct BattlePokemon)", const: const})
    off = v[f"bm_{field}".replace("[", "_").replace("]", "")] + battler * v["bm_size"]
    return [f"expect{'ne' if negate else ''}{bits} {{gBattleMons+{off}}} {v[const]} {label or field + '_is_' + const.lower()}"]


def expect_party_species(party, slot, species, label):
    """Check the species of a Pokemon of gPlayerParty or gEnemyParty (party, a symbol) at slot 0-5,
    which is in the encrypted part of struct Pokemon (the runner decrypts it: expectpartyspecies)."""
    v = probe.resolve({"mon_size": "sizeof(struct Pokemon)", "secure": "offsetof(struct BoxPokemon, secure)",
                       "substruct": "NUM_SUBSTRUCT_BYTES", species: species})
    return [f"expectpartyspecies {{{party}+{slot * v['mon_size']}}} {v['secure']} {v['substruct']} {v[species]} {label}"]


def expect_battler_ivs(battler, want, label):
    """Check a battler's six IVs (gBattleMons: 5-bit fields hpIV..spDefenseIV, lowest bits first,
    in the word before statStages) against `want` (the low 30 bits)."""
    v = probe.resolve({"ivs": "offsetof(struct BattlePokemon, statStages) - 4", "bm_size": "sizeof(struct BattlePokemon)"})
    return [f"expectbits32 {{gBattleMons+{v['ivs'] + battler * v['bm_size']}}} 0x3FFFFFFF {want:#x} {label}"]


# Tutor moves the relearner offers only once the game is cleared (src/move_relearner.c, DECISIONS.md D39)
POSTGAME_TUTOR_MOVES = ("MOVE_DARK_HOLE", "MOVE_DRACO_BARRAGE")


def relearner_list(learnset, category, known=(), game_clear=False):
    """The moves the party-menu relearner lists under TM MOVES (every TM and HM in the Bag, as after
    fill_tm_case) or TUTOR MOVES for a Pokemon with the teachable learnset s<learnset>TeachableLearnset
    that knows the moves `known`, in the relearner's order: TMs then HMs, or gTutorMoves' (without
    POSTGAME_TUTOR_MOVES unless game_clear). Read from the files the build generated
    (src/data/pokemon/teachable_learnsets.h, src/data/tutor_moves.h)."""
    root = os.path.join(HERE, "..", "..")
    with open(os.path.join(root, "src/data/pokemon/teachable_learnsets.h")) as f:
        m = re.search(rf"static const u16 s{learnset}TeachableLearnset\[\] = \{{(.*?)\}};", f.read(), re.S)
    teachable = set(re.findall(r"MOVE_\w+", m.group(1)))
    if category == "MOVE_RELEARNER_TM_MOVES":
        sys.path.insert(0, os.path.join(root, "tools", "learnset_helpers"))
        import make_teachables
        cwd = os.getcwd()
        os.chdir(root)
        try:
            order = list(make_teachables.extract_repo_tms("POKEMON_HNS"))
        finally:
            os.chdir(cwd)
    else:
        with open(os.path.join(root, "src/data/tutor_moves.h")) as f:
            order = [mv for mv in re.findall(r"MOVE_\w+", f.read()) if game_clear or mv not in POSTGAME_TUTOR_MOVES]
    return [mv for mv in order if mv in teachable and mv != "MOVE_UNAVAILABLE" and mv not in known]


def relearner_index(learnset, category, known, move, game_clear=False):
    """DOWN presses from the top of the relearner's list to `move` (see relearner_list)."""
    return ["press DOWN", "wait 10"] * relearner_list(learnset, category, known, game_clear).index(move)


def open_relearner(slot, presses, category, label):
    """START > POKEMON > the Pokemon in party slot `slot` > MOVES > the category `presses` DOWN
    presses down the list of those it has moves in (LEVEL UP, EGG, TM, TUTOR), which must be
    `category` (MOVE_RELEARNER_*_MOVES)."""
    out = start_menu("POKEMON") + ["press DOWN", "wait 10"] * slot
    out += ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += ["press DOWN", "wait 10"] * presses + ["press A", "wait 120"]
    return out + expect_const("{gMoveRelearnerState}", category, f"{label}_category", size=8)


def expect_relearner_list(learnset, category, known=(), present=(), absent=(), label="relearner", game_clear=False,
                          moves=None):
    """With the relearner's list open (open_relearner), check that it holds relearner_list(...)'s
    number of moves (or the moves `moves`: relearner_list reads TM and tutor lists only), then
    CANCEL, and has the moves `present` and not the moves `absent`."""
    moves = list(moves) if moves is not None else relearner_list(learnset, category, known, game_clear)
    v = probe.resolve({"items": "offsetof(struct ListMenuTemplate, items)",
                       "count_word": "offsetof(struct ListMenuTemplate, itemPrintFunc) + sizeof(void *)",
                       "size": "sizeof(struct ListMenuItem)", "id": "offsetof(struct ListMenuItem, id)",
                       **{mv: mv for mv in tuple(present) + tuple(absent)}})
    base = f"*{{gMultiuseListMenuTemplate+{v['items']}}}+{v['id']}"
    cancel = f"*{{gMultiuseListMenuTemplate+{v['items']}}}+{v['id'] + len(moves) * v['size']}"
    out = [f"expectbits32 {{gMultiuseListMenuTemplate+{v['count_word']}}} 0xFFF {len(moves) + 1} {label}_{len(moves)}_moves_and_cancel",
           f"expect16 {cancel} 0xFFFE {label}_cancel_after_{len(moves)}_moves"]
    out += [f"expectfind16 {base} {len(moves)} {v['size']} {v[mv]} {label}_has_{mv[5:].lower()}" for mv in present]
    out += [f"expectnotfind16 {base} {len(moves)} {v['size']} {v[mv]} {label}_lacks_{mv[5:].lower()}" for mv in absent]
    return out


def close_relearner():
    """B on the relearner's list, YES to giving up, back to the party menu; then out to the field."""
    return ["press B", "wait 60", "press A", "waituntil32 {gMain+4} {CB2_UpdatePartyMenu} 600 - back_in_party_menu",
            "wait 30", "mash B 120", "wait 60"]


def walkto(x, y, order="xy", soft=False, creep=False, path=False):
    """Walk to map coordinates (x, y), reading the player's position from the save block.
    soft=True: being stopped (e.g. by a wild battle) is not a test failure, and the d-pad is let go
    as soon as a battle starts (gMain.inBattle), so the walk doesn't move the battle's menu
    cursor. creep=True holds A (sneaking up on a DexNav target). path=True finds a way around
    walls, trees and water using the loaded map's collision and elevation. x/y may be
    "@ADDR~BIAS" to read the target from memory."""
    stop = ""
    if soft:
        byte, mask = probe.bitfield("Main", "inBattle")
        stop = f" stop={{gMain+{byte}}}/{mask}"
    return [f"walkto {{gSaveBlock1Ptr}} {x} {y} {order}" + (" soft" if soft else "") + (" creep" if creep else "")
            + (" path={gBackupMapLayout}" if path else "") + stop]


def pace(x1, x2, y, laps, soft=False):
    """Walk back and forth between (x1, y) and (x2, y) `laps` times, e.g. through tall grass.
    Without soft=True, being interrupted (e.g. by a wild battle) is a test failure."""
    out = []
    for _ in range(laps):
        out += walkto(x1, y, soft=soft) + walkto(x2, y, soft=soft)
    return out


def battle_trainer(trainer_id):
    """Debug menu > Trainers > Trainer 1 = id > Try Battle."""
    out = open_debug() + ["press DOWN"] * 6 + ["press A", "wait 30", "press DOWN", "press A", "wait 30"]
    out += number(trainer_id, initial=0) + ["press A", "wait 30"]
    out += ["press DOWN"] * 5 + ["press A"]  # the cursor returns to the top after entry
    return out


def battle(trainer):
    """Start a battle against a trainer given by its constant, e.g. battle("TRAINER_MORTY_1_HNS")."""
    return battle_trainer(probe.resolve({trainer: trainer})[trainer])


def give_mon_complex(species, level, nature, ability_slot, moves):
    """Debug menu > Give X > Pokemon (Complex): species, level, nature (NATURE_*), ability (UP
    presses from slot 0: 1 is the next non-empty slot) and four moves (MOVE_*). Not shiny, no
    Tera/Dynamax changes; IVs and EVs are left at 0, which Minimal Grinding turns into 31/0."""
    v = probe.resolve({x: x for x in [species, nature] + list(moves)})
    out = open_debug() + ["press DOWN"] * 3 + ["press A", "wait 30", "press DOWN", "press DOWN", "press A", "wait 30"]
    out += number(v[species]) + ["press A", "wait 10"] + number(level) + ["press A", "wait 10"]
    out += ["press A", "wait 10"]  # shiny: no
    out += number(v[nature] + 1, initial=0) + ["press A", "wait 10"]
    out += ["press UP 2", "wait 4"] * ability_slot + ["press A", "wait 10"]
    out += ["press A", "wait 10"] * 3  # Tera type, Dynamax level, Gigantamax factor
    out += ["press A", "wait 6"] * 12  # IVs and EVs
    for m in moves:
        out += number(v[m], initial=0) + ["press A", "wait 10"]
    out += ["wait 60", "mash B 60"]
    return out


# Held items for the prepared six (prepared_team with items=True), in party order: all from the
# first three care packages, so a player has them from the 3rd badge on (DECISIONS.md D16)
PREPARED_TEAM_ITEMS = ["ITEM_LIFE_ORB", "ITEM_LEFTOVERS", "ITEM_CHOICE_SPECS", "ITEM_FOCUS_SASH",
                       "ITEM_CHOICE_BAND", "ITEM_EXPERT_BELT"]


def prepared_team(level, items=False):
    """A strong, well-built six: what a player can put together with DexNav, Rare Candies, the
    relearner, TMs and the Training Kit. With items, each holds one of PREPARED_TEAM_ITEMS."""
    out = []
    for sp, nature, ability, moves in (
            ("SPECIES_TYRANITAR", "NATURE_ADAMANT", 0, ["MOVE_CRUNCH", "MOVE_STONE_EDGE", "MOVE_EARTHQUAKE", "MOVE_DRAGON_DANCE"]),
            ("SPECIES_GYARADOS", "NATURE_ADAMANT", 0, ["MOVE_WATERFALL", "MOVE_ICE_FANG", "MOVE_EARTHQUAKE", "MOVE_DRAGON_DANCE"]),
            ("SPECIES_GARDEVOIR", "NATURE_MODEST", 0, ["MOVE_MOONBLAST", "MOVE_PSYCHIC", "MOVE_MYSTICAL_FIRE", "MOVE_CALM_MIND"]),
            ("SPECIES_GARCHOMP", "NATURE_JOLLY", 1, ["MOVE_EARTHQUAKE", "MOVE_DRAGON_CLAW", "MOVE_FIRE_FANG", "MOVE_SWORDS_DANCE"]),
            ("SPECIES_ARCANINE", "NATURE_ADAMANT", 0, ["MOVE_FLARE_BLITZ", "MOVE_EXTREME_SPEED", "MOVE_WILD_CHARGE", "MOVE_CRUNCH"]),
            ("SPECIES_AMPHAROS", "NATURE_MODEST", 0, ["MOVE_THUNDERBOLT", "MOVE_DRAGON_PULSE", "MOVE_FOCUS_BLAST", "MOVE_POWER_GEM"])):
        out += give_mon_complex(sp, level, nature, ability, moves)
    if items:
        for slot, item in enumerate(PREPARED_TEAM_ITEMS):
            out += hold_item(item, slot)
    return out


def team(level, *species):
    """Give the player these Pokemon (species constants) at one level."""
    ids = probe.resolve({s: s for s in species})
    out = []
    for s in species:
        out += give_mon(ids[s], level)
    return out


def turn(*moves, shots=None, decline_switch=False):
    """One battle turn per argument: 0-3 picks that move slot. Battle text auto-advances.

    decline_switch=True presses B first, which answers a "Will you switch?" prompt with No
    and is harmless on the action menu (the cursor is reset right after)."""
    out = []
    for i, m in enumerate(moves):
        if decline_switch:
            out += ["press B", "wait 30"]
        out += ["press UP", "press LEFT", "press A", "wait 30", "press UP", "press LEFT"]
        if m & 1:
            out.append("press RIGHT")
        if m & 2:
            out.append("press DOWN")
        out += ["press A", "wait 700"]
        if shots:
            out.append(f"shot {shots}_{i:02d}.png")
    return out


def autobattle(moves, max_frames=60000, plan=None):
    """Play the current battle to the end. moves: per party slot, the move slot (0-3) to use,
    e.g. "2,3,1,2"; add 'm' to Mega Evolve first ("2m"). Forced switches pick the first healthy
    Pokemon. Prints the outcome, turn count and remaining party HP.
    plan: a game plan, {opponent species constant: (party slot, move slot), or a list of them}:
    against that Pokemon, a party Pokemon with a rule attacks with its move; otherwise the first
    listed Pokemon that can still fight is switched in (once each time the opponent comes in),
    and forced switches send it in too."""
    keys = ["main={gMain}", "outcome={gBattleOutcome}", "ctrl={gBattlerControllerFuncs}",
            "act={HandleInputChooseAction@battle_controller_player}", "mov={HandleInputChooseMove}",
            "actcur={gActionSelectionCursor}", "movcur={gMoveSelectionCursor}",
            "partyidx={gBattlerPartyIndexes}", "party={gPlayerParty}", "count={gPlayerPartyCount}",
            "mons={gBattleMons}", "pmenu={gPartyMenu}",
            "pmenucb2={CB2_UpdatePartyMenu}", "battlecb2={BattleMainCB2}"]
    keys.append("ppoff=%d" % probe.resolve({"ppoff": "offsetof(struct BattlePokemon, pp)"})["ppoff"])
    if plan:
        ids = probe.resolve({sp: sp for sp in plan})
        rules = [(sp, r) for sp, rs in plan.items() for r in (rs if isinstance(rs, list) else [rs])]
        keys.append("plan=" + "/".join(f"{ids[sp]}:{slot}.{move}" for sp, (slot, move) in rules))
    return [f"autobattle {moves} {max_frames} " + " ".join(keys)]


def sample_battle(trainer_id, moves, runs=5, min_wins=1, max_wins=None, state="team.ss", tag="", plan=None,
                  max_frames=60000):
    """Fight trainer_id (a number or a TRAINER_ constant) `runs` times from the saved team state,
    starting each battle a few frames later so the battle RNG differs, and require between
    min_wins and max_wins wins. Save the team first with `savestate team.ss` (paths are relative
    to the output directory). A tag keeps two samples against the same trainer apart. plan and
    max_frames go to autobattle."""
    if isinstance(trainer_id, str):
        trainer_id = probe.resolve({trainer_id: trainer_id})[trainer_id]
    name = f"wins_vs_{trainer_id}{tag}"
    out = []
    for k in range(runs):
        out += [f"loadstate {state}", f"wait {1 + 37 * k}"] + battle_trainer(trainer_id) + autobattle(moves, max_frames, plan)
        out += [f"tally {name} {{gBattleOutcome}} 1"]
    out.append(f"expecttally {name} {min_wins} {runs if max_wins is None else max_wins}")
    return out


def send_out(slot):
    """Answer the 'Will you switch?' prompt / forced switch: party slot 1-5, then confirm."""
    return ["press A", "wait 150"] + ["press DOWN", "wait 10"] * slot + ["press A", "wait 30", "press A", "wait 500"]


def symbols(elf):
    """name -> address. Static functions and variables that exist in several objects are also
    available as name@object (e.g. HandleInputChooseAction@battle_controller_player, sMenu@menu),
    resolved via the .map."""
    out = subprocess.run(["arm-none-eabi-nm", elf], check=True, capture_output=True, text=True).stdout
    table, by_addr = {}, []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3:
            addr = int(parts[0], 16)
            table[parts[2]] = addr
            by_addr.append((addr, parts[2]))
    by_addr.sort()
    addrs = [a for a, _ in by_addr]
    mapfile = os.path.splitext(elf)[0] + ".map"
    if os.path.exists(mapfile):
        for line in open(mapfile):
            m = re.match(r"\s*\.(?:text|rodata|data|bss|sbss)\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+\S*?([\w]+)\.o$", line)
            if not m:
                continue
            lo, size, obj = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
            # Sections the linker discarded are listed at 0 (below EWRAM); the absolute assembler
            # symbols there aren't variables
            if lo < 0x02000000:
                continue
            for i in range(bisect.bisect_left(addrs, lo), bisect.bisect_left(addrs, lo + size)):
                table[f"{by_addr[i][1]}@{obj}"] = by_addr[i][0]
    return table


def expand(path, syms):
    lines = []
    for raw in open(path):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        def sub(m):
            name, off = m.group(1), int(m.group(2) or 0)
            if name not in syms:
                sys.exit(f"{path}: unknown symbol {name}")
            return hex(syms[name] + off)
        if line.startswith("!"):
            lines += [re.sub(r"\{([\w@]+)(?:\+(\d+))?\}", sub, l) for l in eval(line[1:])]
        else:
            lines.append(re.sub(r"\{([\w@]+)(?:\+(\d+))?\}", sub, line))
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("test")
    ap.add_argument("--rom", default="pokehns.gba")
    ap.add_argument("--elf", default="pokehns.elf")
    ap.add_argument("--out", default="build/emurun")
    ap.add_argument("--save", help="attach a fresh save file (removed before the run) at this path")
    ap.add_argument("--keep-save", action="store_true", help="keep an existing --save file (e.g. made by another ROM)")
    ap.add_argument("--emulator", default=os.environ.get("EMURUN_EMULATOR", "mgba"), choices=("mgba", "vbam"),
                    help="mgba (libmgba) or vbam (VBA-M's libretro core, the emulator Delta's GBA core is built "
                         "on; EMURUN_CORE names the core, see tools/emurun/build_vbam_core.sh)")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    script = os.path.join(args.out, os.path.basename(args.test) + ".txt")
    with open(script, "w") as f:
        f.write("\n".join(expand(args.test, symbols(args.elf))) + "\n")
    emurun = os.path.join(HERE, "emurun" if args.emulator == "mgba" else "emurun-libretro")
    # Always ask make: a driver older than emurun.c would fail on the commands it doesn't know. Only
    # the backend in use, so a VBA-M-only setup doesn't need libmgba
    subprocess.run(["make", "-s", "-C", HERE, os.path.basename(emurun)], check=True)
    # Screenshot paths in tests are relative to the output directory
    cmd = [emurun, os.path.abspath(args.rom), os.path.abspath(script)]
    if args.save:
        if os.path.exists(args.save) and not args.keep_save:
            os.remove(args.save)
        cmd.append(os.path.abspath(args.save))
    res = subprocess.run(cmd, cwd=args.out)
    sys.exit(res.returncode)


if __name__ == "__main__":
    main()
