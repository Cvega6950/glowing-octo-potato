#!/usr/bin/env python3
"""Crystal Imperium side battle sprites (DECISIONS.md D41): the battle pictures and overworld sprites of
the side battles' trainers (tools/crystal_imperium/side_battles.py), from their artists' free releases
(CREDITS.md). For each entry of the table below this writes a marked block, after Heart & Soul's own
entries, into the files that list them:

  include/constants/trainers.h                       TRAINER_PIC_FRONT_<NAME>_HNS
  src/data/graphics/trainers.h                       the picture's data and its gTrainerSprites entry
  include/constants/event_objects.h                  OBJ_EVENT_GFX_<NAME>_HNS (NUM_OBJ_EVENT_GFX moves
                                                     up) and OBJ_EVENT_PAL_TAG_<NAME>_HNS
  src/data/object_events/object_event_graphics.h     the overworld sprite's data and palette
  src/data/object_events/object_event_pic_tables.h   its frames
  src/data/object_events/object_event_graphics_info.h            its graphics info
  src/data/object_events/object_event_graphics_info_pointers.h   and its place in the table
  src/event_object_movement.c                        its palette's tag
  spritesheet_rules.mk                               how its PNG is cut into frames

  python3 tools/crystal_imperium/side_sprites.py          # rewrite the blocks
  python3 tools/crystal_imperium/side_sprites.py --check  # exit 1 if any is out of date

The files (tools/crystal_imperium/import_side_sprites.py makes them from the artists' releases):
  graphics/trainers/front_pics/<name>_hns.png        64x64, indexed, at most 16 colours, 0 transparent
  graphics/object_events/pics/people/<name>_hns.png  one row of 16x32 or 32x32 frames: 9 (stand and
                                                     walk) or 3 (stand only: its walking frames repeat
                                                     the standing ones, as Emerald's Roxanne does)
  graphics/object_events/palettes/<name>_hns.pal     the sprite's palette (JASC, 16 colours)

Appending to the overworld sprites moves OBJ_EVENT_GFX_VARS up: a save made on a map with VAR objects
(the bedroom's decorations, the Frontier's rooms) can show another sprite on one of them until the
player leaves that map (KNOWN_ISSUES.md). Adding every sprite in one release keeps that to once.
"""
import argparse
import os
import re
import struct
import sys
import zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# (name, True if it has a battle picture). Every name has an overworld sprite. The order is the
# IDs' order: append, never reorder (a saved map's objects keep their sprite's ID).
SPRITES = [
    # Sinnoh's Gym Leaders: battle pictures by iriv24 (Roark's by PurrfectDoodle), overworld
    # sprites by PurrfectDoodle (Eva), from Team Aqua's Asset Repo (CREDITS.md)
    ("candice", True), ("gardenia", True), ("fantina", True), ("maylene", True),
    ("wake", True), ("byron", True), ("roark", True), ("volkner", True),
    # Paldea's Gym Leaders: battle pictures and overworld sprites by RHcks, commissioned by
    # darklight177 (their Paldea Gym Leader Sprite Sheet)
    ("katy", True), ("brassius", True), ("iono", True), ("kofu", True),
    ("larry", True), ("ryme", True), ("tulip", True), ("grusha", True),
]

FRONT = "graphics/trainers/front_pics/{}_hns.png"
PEOPLE = "graphics/object_events/pics/people/{}_hns.png"
PALETTE = "graphics/object_events/palettes/{}_hns.pal"

# Heart & Soul's last entries, after which the blocks go
LAST_PIC = "TRAINER_PIC_FRONT_SAMSON_OAK_HNS"
LAST_GFX = "OBJ_EVENT_GFX_ALOLA_OAK_HNS"
LAST_PAL_TAG = "OBJ_EVENT_PAL_TAG_ALOLA_OAK_HNS"
# TrainerPicID is a packed enum: past 255 it grows to two bytes (struct Trainer with it)
MAX_PIC_ID = 255
# OBJ_EVENT_PAL_TAG_WHITE is 0x11FE
MAX_PAL_TAG = 0x11FD
# sObjectEventSpritePalettes is searched with a u8 index
MAX_PALETTES = 254

BEGIN = "Crystal Imperium side battle sprites (DECISIONS.md D41): written by tools/crystal_imperium/side_sprites.py"
END = "End of the side battle sprites"


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


def camel(name):
    return "".join(part.capitalize() for part in name.split("_"))


# --- PNG checks ---------------------------------------------------------------------------------------

def paeth(a, b, c):
    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def png_info(path):
    """(width, height, palette entries, the highest pixel index used, the four corners' indices) of an
    indexed, non-interlaced PNG, read with the standard library only."""
    data = open(os.path.join(ROOT, path), "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit(f"{path}: not a PNG")
    pos, chunks, idat = 8, {}, b""
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IDAT":
            idat += body
        else:
            chunks.setdefault(kind, body)
        pos += 12 + length
    w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunks[b"IHDR"])
    if ctype != 3 or interlace or depth not in (1, 2, 4, 8):
        sys.exit(f"{path}: not an indexed, non-interlaced PNG")
    entries = len(chunks.get(b"PLTE", b"")) // 3
    raw = zlib.decompress(idat)
    stride = (w * depth + 7) // 8
    rows, prev = [], bytearray(stride)
    for y in range(h):
        kind = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - 1] if i else 0
            b = prev[i]
            c = prev[i - 1] if i else 0
            line[i] = (line[i] + (0, a, b, (a + b) // 2, paeth(a, b, c))[kind]) & 0xFF
        rows.append(line)
        prev = line
    per = 8 // depth

    def pixel(x, y):
        return (rows[y][x // per] >> (8 - depth * (x % per + 1))) & ((1 << depth) - 1)
    highest = max(pixel(x, y) for y in range(h) for x in range(w))
    corners = {pixel(0, 0), pixel(w - 1, 0), pixel(0, h - 1), pixel(w - 1, h - 1)}
    return w, h, entries, highest, corners


def check_picture(path):
    w, h, entries, highest, corners = png_info(path)
    if (w, h) != (64, 64):
        sys.exit(f"{path}: {w}x{h}, a battle picture is 64x64")
    if entries > 16 or highest > 15:
        sys.exit(f"{path}: more than 16 colours")
    if corners != {0}:
        sys.exit(f"{path}: the corners aren't index 0, the transparent colour")


def overworld_frames(path):
    """(frame width, frame count) of an overworld sheet: one row of 16x32 or 32x32 frames, 3 or 9."""
    w, h, entries, highest, corners = png_info(path)
    if entries > 16 or highest > 15:
        sys.exit(f"{path}: more than 16 colours")
    if 0 not in corners:
        sys.exit(f"{path}: index 0, the transparent colour, isn't in a corner")
    for fw in (16, 32):
        if h == 32 and w in (3 * fw, 9 * fw):
            return fw, w // fw
    sys.exit(f"{path}: {w}x{h}, an overworld sheet is a row of 3 or 9 frames of 16x32 or 32x32")


def check_palette(path):
    lines = read(path).replace("\r\n", "\n").split("\n")
    if lines[:2] != ["JASC-PAL", "0100"] or not lines[2].isdigit() or not 1 <= int(lines[2]) <= 16:
        sys.exit(f"{path}: not a JASC palette of at most 16 colours")
    for line in lines[3:3 + int(lines[2])]:
        if not re.fullmatch(r"\d{1,3} \d{1,3} \d{1,3}", line):
            sys.exit(f"{path}: bad colour line {line!r}")


# --- Blocks -------------------------------------------------------------------------------------------

def block(lines, comment="//", indent=""):
    return [f"{indent}{comment} {BEGIN}"] + lines + [f"{indent}{comment} {END}"]


def put_after(text, anchor_re, lines, path, comment="//", indent=""):
    """text with the marked block right after the line(s) anchor_re matches (replacing the block
    already there): an empty `lines` removes it."""
    m = re.search(anchor_re, text, re.M)
    if not m:
        sys.exit(f"{path}: anchor {anchor_re!r} not found")
    end = text.index("\n", m.end()) + 1
    begin_line = f"{indent}{comment} {BEGIN}\n"
    end_line = f"{indent}{comment} {END}\n"
    if text.startswith(begin_line, end):
        stop = text.find(end_line, end)
        if stop < 0:
            sys.exit(f"{path}: a side battle sprite block without its end")
        text = text[:end] + text[stop + len(end_line):]
    if not lines:
        return text
    return text[:end] + "\n".join(block(lines, comment, indent)) + "\n" + text[end:]


def render(sprites, texts):
    """The files' new texts."""
    pics = [n for n, has_pic in sprites if has_pic]
    out = dict(texts)
    gfx_ids = {}

    # Trainer pictures
    p = "include/constants/trainers.h"
    out[p] = put_after(out[p], r"^\s*" + LAST_PIC + r",[ \t]*$", [f"    TRAINER_PIC_FRONT_{n.upper()}_HNS," for n in pics],
                       p, indent="    ")
    p = "src/data/graphics/trainers.h"
    incbins = []
    for n in pics:
        incbins += [f'const u32 gTrainerFrontPic_{camel(n)}Hns[] = INCBIN_U32("graphics/trainers/front_pics/{n}_hns.4bpp.smol");',
                    f'const u16 gTrainerPalette_{camel(n)}Hns[] = INCBIN_U16("graphics/trainers/front_pics/{n}_hns.gbapal");']
    out[p] = put_after(out[p], r'^const u16 gTrainerPalette_SamsonOakHns\[\].*$', incbins, p)
    out[p] = put_after(out[p], r"^\s*TRAINER_SPRITE\(" + LAST_PIC + r",.*$",
                       [f"    TRAINER_SPRITE(TRAINER_PIC_FRONT_{n.upper()}_HNS, gTrainerFrontPic_{camel(n)}Hns, gTrainerPalette_{camel(n)}Hns),"
                        for n in pics], p, indent="    ")

    # Overworld sprites
    p = "include/constants/event_objects.h"
    text = out[p]
    last_gfx = int(re.search(r"#define " + LAST_GFX + r"\s+(\d+)", text).group(1))
    last_tag = int(re.search(r"#define " + LAST_PAL_TAG + r"\s+(0x[0-9A-Fa-f]+)", text).group(1), 16)
    defines, tags = [], []
    for i, (n, _) in enumerate(sprites):
        gfx_ids[n] = last_gfx + 1 + i
        defines.append(f"#define {('OBJ_EVENT_GFX_' + n.upper() + '_HNS').ljust(39)} {gfx_ids[n]}")
        tag = last_tag + 1 + i
        if tag > MAX_PAL_TAG:
            sys.exit("no palette tags left before OBJ_EVENT_PAL_TAG_WHITE")
        tags.append(f"#define {('OBJ_EVENT_PAL_TAG_' + n.upper() + '_HNS').ljust(41)} 0x{tag:04X}")
    text = put_after(text, r"^#define " + LAST_GFX + r"\s+\d+[ \t]*$", defines, p)
    text = re.sub(r"(?m)^(#define NUM_OBJ_EVENT_GFX\s+)\d+", lambda m: m.group(1) + str(last_gfx + 1 + len(sprites)), text)
    text = put_after(text, r"^#define " + LAST_PAL_TAG + r"\s+0x[0-9A-Fa-f]+[ \t]*$", tags, p)
    out[p] = text

    p = "src/data/object_events/object_event_graphics.h"
    out[p] = put_after(out[p], r'^const u32 gObjectEventPic_AlolaOak_hns\[\].*$',
                       [f'const u32 gObjectEventPic_{camel(n)}_hns[] = INCBIN_U32("graphics/object_events/pics/people/{n}_hns.4bpp");'
                        for n, _ in sprites], p)
    out[p] = put_after(out[p], r'^const u16 gObjectEventPal_AlolaOak_hns\[\].*$',
                       [f'const u16 gObjectEventPal_{camel(n)}_hns[] = INCBIN_U16("graphics/object_events/palettes/{n}_hns.gbapal");'
                        for n, _ in sprites], p)

    p = "src/data/object_events/object_event_pic_tables.h"
    tables = []
    sizes = {}
    for n, _ in sprites:
        fw, count = overworld_frames(PEOPLE.format(n))
        sizes[n] = fw
        frames = range(9) if count == 9 else (0, 1, 2, 0, 0, 1, 1, 2, 2)
        tables.append(f"static const struct SpriteFrameImage sPicTable_{camel(n)}_hns[] = {{")
        tables += [f"    overworld_frame(gObjectEventPic_{camel(n)}_hns, {fw // 8}, 4, {f})," for f in frames]
        tables.append("};")
    out[p] = put_after(out[p], r"^static const struct SpriteFrameImage sPicTable_AlolaOak_hns\[\] = \{(?:\n.*?)*?\n\};", tables, p)

    p = "src/data/object_events/object_event_graphics_info.h"
    infos = []
    for n, _ in sprites:
        fw = sizes[n]
        infos.append(f"const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_{camel(n)}_hns = {{TAG_NONE, "
                     f"OBJ_EVENT_PAL_TAG_{n.upper()}_HNS, OBJ_EVENT_PAL_TAG_NONE, {fw * 16}, {fw}, 32, 5, SHADOW_SIZE_M, "
                     f"FALSE, FALSE, TRACKS_FOOT, &gObjectEventBaseOam_{fw}x32, sOamTables_{fw}x32, sAnimTable_Standard, "
                     f"sPicTable_{camel(n)}_hns, gDummySpriteAffineAnimTable}};")
    out[p] = put_after(out[p], r"^const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_AlolaOak_hns = .*$", infos, p)

    p = "src/data/object_events/object_event_graphics_info_pointers.h"
    out[p] = put_after(out[p], r"^extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_AlolaOak_hns;$",
                       [f"extern const struct ObjectEventGraphicsInfo gObjectEventGraphicsInfo_{camel(n)}_hns;" for n, _ in sprites], p)
    out[p] = put_after(out[p], r"^\s*\[" + LAST_GFX + r"\] =\s*&gObjectEventGraphicsInfo_AlolaOak_hns,$",
                       [f"    {('[OBJ_EVENT_GFX_' + n.upper() + '_HNS] =').ljust(39)} &gObjectEventGraphicsInfo_{camel(n)}_hns,"
                        for n, _ in sprites], p, indent="    ")

    p = "src/event_object_movement.c"
    out[p] = put_after(out[p], r"^\s*\{gObjectEventPal_AlolaOak_hns, " + LAST_PAL_TAG + r"\},$",
                       [f"    {{gObjectEventPal_{camel(n)}_hns, OBJ_EVENT_PAL_TAG_{n.upper()}_HNS}}," for n, _ in sprites],
                       p, indent="    ")
    table = out[p][out[p].index("sObjectEventSpritePalettes[] ="):]
    if table[:table.index("};")].count("{gObjectEventPal") > MAX_PALETTES:
        sys.exit("too many overworld palettes for sObjectEventSpritePalettes' u8 index")

    p = "spritesheet_rules.mk"
    rules = []
    for n, _ in sprites:
        rules += ["", f"$(OBJEVENTGFXDIR)/people/{n}_hns.4bpp: %.4bpp: %.png",
                  f"\t$(GFX) $< $@ -mwidth {sizes[n] // 8} -mheight 4"]
    out[p] = put_after(out[p], r"^\$\(OBJEVENTGFXDIR\)/people/alola_oak_hns\.4bpp: %\.4bpp: %\.png\n\t.*$",
                       rules, p, comment="#")
    return out, gfx_ids


def check(sprites):
    names = [n for n, _ in sprites]
    if len(set(names)) != len(names):
        sys.exit("a sprite twice")
    for n, has_pic in sprites:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", n):
            sys.exit(f"{n}: a sprite's name is lower case")
        if has_pic:
            check_picture(FRONT.format(n))
        overworld_frames(PEOPLE.format(n))
        check_palette(PALETTE.format(n))


FILES = ["include/constants/trainers.h", "src/data/graphics/trainers.h", "include/constants/event_objects.h",
         "src/data/object_events/object_event_graphics.h", "src/data/object_events/object_event_pic_tables.h",
         "src/data/object_events/object_event_graphics_info.h",
         "src/data/object_events/object_event_graphics_info_pointers.h", "src/event_object_movement.c",
         "spritesheet_rules.mk"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    check(SPRITES)
    texts = {p: read(p) for p in FILES}
    new, _ = render(SPRITES, texts)
    # The picture IDs stay one byte: the front pictures, then the back ones from TRAINER_PIC_FRONT_COUNT
    enum = new["include/constants/trainers.h"]
    body = enum[enum.index("enum __attribute__((packed)) TrainerPicID"):]
    ids = re.findall(r"(?m)^\s*(TRAINER_PIC_\w+)", body[:body.index("};")])
    fronts, total = ids.index("TRAINER_PIC_FRONT_COUNT"), ids.index("TRAINER_PIC_COUNT")
    if fronts + (total - fronts - 1) > MAX_PIC_ID:  # TRAINER_PIC_COUNT's value
        sys.exit("TrainerPicID would grow past one byte: no room for more trainer pictures")
    stale = [p for p in FILES if new[p] != texts[p]]
    if args.check:
        if stale:
            print(f"{', '.join(stale)} out of date: run tools/crystal_imperium/side_sprites.py")
            return 1
        return 0
    for p in stale:
        with open(os.path.join(ROOT, p), "w", encoding="utf-8") as f:
            f.write(new[p])
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
