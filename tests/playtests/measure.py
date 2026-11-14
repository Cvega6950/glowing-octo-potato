"""Measurements in a running game (ENGINE_NOTES "Measurements"): the save block sizes the game
computes (SaveData.blockInfo), the main RAM no heap uses, and the free space in the SYSTEM and
APPLICATION heaps with the field running in Twinleaf Town. Fails only if the save blocks outgrow
their sectors."""
import json
import os

SECTOR = 0x1000
FOOTER = 16  # SaveCheckFooter


def run(t):
    t.new_game()
    t.ds.run(130)  # the mailbox refreshes its measurements every 64 field frames
    info = t.mb("saveBlockInfo")
    t.check(info, "the mailbox has the save block info")
    blocks = []
    for i, name in enumerate(["NORMAL", "BOXES"]):
        b = t.ds.ram(info + 12 * i, 12)
        sectors, offset, size = b[2], int.from_bytes(b[4:8], "little"), int.from_bytes(b[8:12], "little")
        room = sectors * SECTOR - size - FOOTER
        t.check(room >= 0, f"{name} block ({size:#x} bytes) does not fit its {sectors} sectors")
        blocks.append({"block": name, "size": size, "sectors": sectors, "offset": offset, "room": room})
    m = {"save_blocks": blocks, "main_arena_free": t.mb("mainArenaFree"),
         "app_heap_free": t.mb("appHeapFree"), "system_heap_free": t.mb("systemHeapFree")}
    with open(os.path.join(t.out, "measurements.json"), "w") as fh:
        json.dump(m, fh, indent=2)
    t.result(", ".join(f"{b['block']} {b['size']:#x} ({b['sectors']} sectors, {b['room']} bytes free)" for b in blocks)
             + f"; arena unused {m['main_arena_free']}; APPLICATION free {m['app_heap_free']}, SYSTEM free {m['system_heap_free']}")
