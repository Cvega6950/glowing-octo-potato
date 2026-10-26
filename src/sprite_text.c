// Platinum Imperium: expansion 1.15's text on sprites, for the BW battle UI, on expansion 1.14.
// 1.14 prints only into windows, so a string for a row of sprites is printed into a temporary
// window holding a copy of the sprites' tiles, which then go back to the sprites: zero pixels of a
// glyph leave what is under them, as 1.15's sprite printer does. Text is drawn at once.
#include "global.h"
#include "malloc.h"
#include "menu.h"
#include "sprite.h"
#include "text.h"
#include "window.h"

#define nextX data[1]
#define nextY data[2]

static void StorePointerInSpriteData(struct Sprite *sprite, const u32 *ptr)
{
    sprite->data[3] = (s16)(((u32)ptr) & 0xFFFF);
    sprite->data[4] = (s16)(((u32)ptr) >> 16);
}

static u32 *GetSrcPtrFromSprite(struct Sprite *sprite)
{
    return (u32 *)((u16)sprite->data[3] | ((u16)sprite->data[4] << 16));
}

// Width and height in tiles of each OAM shape and size
static const u8 sOamSizeTiles[3][4][2] =
{
    [ST_OAM_SQUARE] = {{1, 1}, {2, 2}, {4, 4}, {8, 8}},
    [ST_OAM_H_RECTANGLE] = {{2, 1}, {4, 1}, {4, 2}, {8, 4}},
    [ST_OAM_V_RECTANGLE] = {{1, 2}, {1, 4}, {2, 4}, {4, 8}},
};

static u32 SpriteWidthTiles(struct Sprite *sprite)
{
    return sOamSizeTiles[sprite->oam.shape][sprite->oam.size][0];
}

static u32 SpriteHeightTiles(struct Sprite *sprite)
{
    return sOamSizeTiles[sprite->oam.shape][sprite->oam.size][1];
}

void SetupSpritesForTextPrinting(u8 *spriteIds, const u32 **spriteSrc, u32 numSpritesX, u32 numSpritesY)
{
    u32 x, y;

    for (y = 0; y < numSpritesY; y++)
    {
        for (x = 0; x < numSpritesX; x++)
        {
            struct Sprite *sprite = &gSprites[spriteIds[x + y * numSpritesX]];

            if (spriteSrc != NULL)
                StorePointerInSpriteData(sprite, spriteSrc[x + y * numSpritesX]);
            sprite->nextX = (x < numSpritesX - 1) ? spriteIds[x + y * numSpritesX + 1] : SPRITE_NONE;
            sprite->nextY = (y < numSpritesY - 1) ? spriteIds[x + (y + 1) * numSpritesX] : SPRITE_NONE;
        }
    }
}

// The longest row of sprites text is printed across
#define MAX_CHAIN_SPRITES 4

// The next sprite of a row, or SPRITE_NONE. Only the row is followed: 1.15 goes down to nextY only
// for text taller than the sprites, which the BW battle UI never prints, and its health boxes set
// nextX (data[1]) just for their printing while data[2] holds other things.
static u32 GetNextSpriteX(u32 spriteId)
{
    u32 next = (u16)gSprites[spriteId].nextX;

    if (next >= MAX_SPRITES || next == spriteId)
        return SPRITE_NONE;
    return next;
}

// The sprite of a row that holds tile (tileX, tileY) of the whole, and that tile within it
static u32 *GetChainTile(u32 spriteId, u32 tileX, u32 tileY, u32 **srcTile)
{
    struct Sprite *sprite = &gSprites[spriteId];
    u32 width = SpriteWidthTiles(sprite), height = SpriteHeightTiles(sprite);
    u32 tile, count = 0;

    if (tileY >= height)
        return NULL;
    while (tileX >= width)
    {
        u32 next = GetNextSpriteX(spriteId);

        if (next == SPRITE_NONE || ++count >= MAX_CHAIN_SPRITES)
            return NULL;
        tileX -= width;
        spriteId = next;
        sprite = &gSprites[spriteId];
    }

    tile = tileY * width + tileX;
    if (srcTile != NULL)
    {
        u32 *src = GetSrcPtrFromSprite(sprite);
        *srcTile = (src != NULL) ? src + tile * (TILE_SIZE_4BPP / 4) : NULL;
    }
    return (u32 *)(OBJ_VRAM0 + (sprite->oam.tileNum + tile) * TILE_SIZE_4BPP);
}

static void GetChainSizeTiles(u32 spriteId, u32 *width, u32 *height)
{
    u32 id, count = 0;

    *width = 0;
    for (id = spriteId; id != SPRITE_NONE && count < MAX_CHAIN_SPRITES; id = GetNextSpriteX(id), count++)
        *width += SpriteWidthTiles(&gSprites[id]);
    *height = SpriteHeightTiles(&gSprites[spriteId]);
}

// Fills a rectangle of a sprite chain with a color, or (useSource) with the source graphics of the sprites
static void FillSpriteRect(u32 spriteId, u32 left, u32 top, u32 width, u32 height, bool32 useSource, u32 color)
{
    u32 x, y;

    for (y = top; y < top + height; y++)
    {
        for (x = left; x < left + width; )
        {
            u32 *srcTile = NULL;
            u32 *tile = GetChainTile(spriteId, x / 8, y / 8, useSource ? &srcTile : NULL);
            u32 first = x % 8, count = 8 - first, mask, value;

            if (tile == NULL)
                break;
            if (count > left + width - x)
                count = left + width - x;
            mask = (count == 8 ? 0xFFFFFFFF : ((1u << (count * 4)) - 1)) << (first * 4);
            if (useSource)
                value = (srcTile != NULL) ? srcTile[y % 8] : 0;
            else
                value = color * 0x11111111;
            tile[y % 8] = (tile[y % 8] & ~mask) | (value & mask);
            x += count;
        }
    }
}

void FillSpriteRectColor(u32 spriteId, u32 left, u32 top, u32 width, u32 height, u32 color)
{
    FillSpriteRect(spriteId, left, top, width, height, FALSE, color);
}

void FillSpriteRectSprite(u32 spriteId, u32 left, u32 top, u32 width, u32 height)
{
    FillSpriteRect(spriteId, left, top, width, height, TRUE, 0);
}

void AddSpriteTextPrinterParameterized6(u8 spriteId, u8 fontId, u8 left, u8 top, u8 letterSpacing, u8 lineSpacing, const union TextColor color, s8 speed, const u8 *str)
{
    struct WindowTemplate template = {0};
    u32 width, height, x, y, windowId;
    u8 *pixels;

    GetChainSizeTiles(spriteId, &width, &height);
    template.width = width;
    template.height = height;
    windowId = AddWindow(&template);
    if (windowId == WINDOW_NONE)
        return;

    pixels = (u8 *)GetWindowAttribute(windowId, WINDOW_TILE_DATA);
    for (y = 0; y < height; y++)
        for (x = 0; x < width; x++)
        {
            u32 *tile = GetChainTile(spriteId, x, y, NULL);
            if (tile != NULL)
                CpuCopy32(tile, pixels + (y * width + x) * TILE_SIZE_4BPP, TILE_SIZE_4BPP);
        }

    AddTextPrinterParameterized6(windowId, fontId, left, top, letterSpacing, lineSpacing, color, TEXT_SKIP_DRAW, str);

    for (y = 0; y < height; y++)
        for (x = 0; x < width; x++)
        {
            u32 *tile = GetChainTile(spriteId, x, y, NULL);
            if (tile != NULL)
                CpuCopy32(pixels + (y * width + x) * TILE_SIZE_4BPP, tile, TILE_SIZE_4BPP);
        }

    RemoveWindow(windowId);
}

bool32 IsTextPrinterActiveOnSprite(u32 spriteId)
{
    return FALSE;
}
