#include "global.h"
#include "blit.h"

// Crystal Imperium (DECISIONS.md D38): a rectangle of whole 8x8 tiles is copied a tile row (8 pixels,
// one word) at a time. Pixel by pixel, the BW battle UI's action and move boxes took 3 and 6 frames
// to draw, and the battle's menus waited for them
static bool32 TryBlitBitmapRect4BitTiles(const struct Bitmap *src, struct Bitmap *dst, s32 srcX, s32 srcY, s32 dstX, s32 dstY, s32 xEnd, s32 yEnd, u8 colorKey)
{
    s32 srcTilesPerRow = src->width >> 3, dstTilesPerRow = dst->width >> 3;
    s32 tileX, tileY, row;
    u32 key = (colorKey & 0xF) * 0x11111111u;

    if (((srcX | srcY | dstX | dstY | xEnd | yEnd | src->width | dst->width) & 7) != 0
     || xEnd <= srcX || yEnd <= srcY
     || (((uintptr_t)src->pixels | (uintptr_t)dst->pixels) & 3) != 0
     || src->pixels == dst->pixels)
        return FALSE;

    for (tileY = 0; tileY < (yEnd - srcY) >> 3; tileY++)
    {
        for (tileX = 0; tileX < (xEnd - srcX) >> 3; tileX++)
        {
            const u32 *srcRow = (const u32 *)(src->pixels + ((((srcY >> 3) + tileY) * srcTilesPerRow + (srcX >> 3) + tileX) << 5));
            u32 *dstRow = (u32 *)(dst->pixels + ((((dstY >> 3) + tileY) * dstTilesPerRow + (dstX >> 3) + tileX) << 5));

            for (row = 0; row < 8; row++)
            {
                u32 pixels = srcRow[row];

                if (colorKey <= 0xF)
                {
                    // The pixels not of the key's color: the nibbles of the XOR that aren't zero
                    u32 opaque = pixels ^ key;
                    opaque |= opaque >> 1;
                    opaque |= opaque >> 2;
                    opaque = (opaque & 0x11111111) * 0xF;
                    pixels = (pixels & opaque) | (dstRow[row] & ~opaque);
                }
                dstRow[row] = pixels;
            }
        }
    }
    return TRUE;
}

void BlitBitmapRect4BitWithoutColorKey(const struct Bitmap *src, struct Bitmap *dst, u16 srcX, u16 srcY, u16 dstX, u16 dstY, u16 width, u16 height)
{
    BlitBitmapRect4Bit(src, dst, srcX, srcY, dstX, dstY, width, height, 0xFF);
}

void BlitBitmapRect4Bit(const struct Bitmap *src, struct Bitmap *dst, u16 srcX, u16 srcY, u16 dstX, u16 dstY, u16 width, u16 height, u8 colorKey)
{
    s32 xEnd;
    s32 yEnd;
    s32 multiplierSrcY;
    s32 multiplierDstY;
    s32 loopSrcY, loopDstY;
    s32 loopSrcX, loopDstX;
    const u8 *pixelsSrc;
    u8 *pixelsDst;
    s32 toOrr;
    s32 toAnd;
    s32 toShift;

    if (dst->width - dstX < width)
        xEnd = (dst->width - dstX) + srcX;
    else
        xEnd = srcX + width;

    if (dst->height - dstY < height)
        yEnd = (dst->height - dstY) + srcY;
    else
        yEnd = height + srcY;

    multiplierSrcY = (src->width + (src->width & 7)) >> 3;
    multiplierDstY = (dst->width + (dst->width & 7)) >> 3;

    if (TryBlitBitmapRect4BitTiles(src, dst, srcX, srcY, dstX, dstY, xEnd, yEnd, colorKey))
        return;

    if (colorKey == 0xFF)
    {
        for (loopSrcY = srcY, loopDstY = dstY; loopSrcY < yEnd; loopSrcY++, loopDstY++)
        {
            for (loopSrcX = srcX, loopDstX = dstX; loopSrcX < xEnd; loopSrcX++, loopDstX++)
            {
                pixelsSrc = src->pixels + ((loopSrcX >> 1) & 3) + ((loopSrcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1B);
                pixelsDst = dst->pixels + ((loopDstX >> 1) & 3) + ((loopDstX >> 3) << 5) + (((loopDstY >> 3) * multiplierDstY) << 5) + ((u32)(loopDstY << 0x1d) >> 0x1B);
                toOrr = ((*pixelsSrc >> ((loopSrcX & 1) << 2)) & 0xF);
                toShift = ((loopDstX & 1) << 2);
                toOrr <<= toShift;
                toAnd = 0xF0 >> (toShift);
                *pixelsDst = toOrr | (*pixelsDst & toAnd);
            }
        }
    }
    else
    {
        for (loopSrcY = srcY, loopDstY = dstY; loopSrcY < yEnd; loopSrcY++, loopDstY++)
        {
            for (loopSrcX = srcX, loopDstX = dstX; loopSrcX < xEnd; loopSrcX++, loopDstX++)
            {
                pixelsSrc = src->pixels + ((loopSrcX >> 1) & 3) + ((loopSrcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1B);
                pixelsDst = dst->pixels + ((loopDstX >> 1) & 3) + ((loopDstX >> 3) << 5) + (((loopDstY >> 3) * multiplierDstY) << 5) + ((u32)(loopDstY << 0x1d) >> 0x1B);
                toOrr = ((*pixelsSrc >> ((loopSrcX & 1) << 2)) & 0xF);
                if (toOrr != colorKey)
                {
                    toShift = ((loopDstX & 1) << 2);
                    toOrr <<= toShift;
                    toAnd = 0xF0 >> (toShift);
                    *pixelsDst = toOrr | (*pixelsDst & toAnd);
                }
            }
        }
    }
}

void FillBitmapRect4Bit(struct Bitmap *surface, u16 x, u16 y, u16 width, u16 height, u8 fillValue)
{
    s32 xEnd;
    s32 yEnd;
    s32 multiplierY;
    s32 loopX, loopY;
    u8 toOrr1, toOrr2;

    xEnd = x + width;
    if (xEnd > surface->width)
        xEnd = surface->width;

    yEnd = y + height;
    if (yEnd > surface->height)
        yEnd = surface->height;

    multiplierY = (surface->width + (surface->width & 7)) >> 3;
    toOrr1 = fillValue << 4;
    toOrr2 = fillValue & 0xF;

    for (loopY = y; loopY < yEnd; loopY++)
    {
        for (loopX = x; loopX < xEnd; loopX++)
        {
            u8 *pixels = surface->pixels + ((loopX >> 1) & 3) + ((loopX >> 3) << 5) + (((loopY >> 3) * multiplierY) << 5) + ((u32)(loopY << 0x1d) >> 0x1B);
            if ((loopX << 0x1F) != 0)
                *pixels = toOrr1 | (*pixels & 0xF);
            else
                *pixels = toOrr2 | (*pixels & 0xF0);
        }
    }
}

void BlitBitmapRect4BitTo8Bit(const struct Bitmap *src, struct Bitmap *dst, u16 srcX, u16 srcY, u16 dstX, u16 dstY, u16 width, u16 height, u8 colorKey, u8 paletteOffset)
{
    s32 palOffsetBits;
    s32 xEnd;
    s32 yEnd;
    s32 multiplierSrcY;
    s32 multiplierDstY;
    s32 loopSrcY, loopDstY;
    s32 loopSrcX, loopDstX;
    const u8 *pixelsSrc;
    u8 *pixelsDst;
    s32 colorKeyBits;

    palOffsetBits = (u32)(paletteOffset << 0x1C) >> 0x18;
    colorKeyBits = (u32)(colorKey << 0x1C) >> 0x18;

    if (dst->width - dstX < width)
        xEnd = (dst->width - dstX) + srcX;
    else
        xEnd = width + srcX;

    if (dst->height - dstY < height)
        yEnd = (srcY + dst->height) - dstY;
    else
        yEnd = srcY + height;

    multiplierSrcY = (src->width + (src->width & 7)) >> 3;
    multiplierDstY = (dst->width + (dst->width & 7)) >> 3;

    if (colorKey == 0xFF)
    {
        for (loopSrcY = srcY, loopDstY = dstY; loopSrcY < yEnd; loopSrcY++, loopDstY++)
        {
            pixelsSrc = src->pixels + ((srcX >> 1) & 3) + ((srcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1b);
            for (loopSrcX = srcX, loopDstX = dstX; loopSrcX < xEnd; loopSrcX++, loopDstX++)
            {
                pixelsDst = dst->pixels + (loopDstX & 7) + ((loopDstX >> 3) << 6) + (((loopDstY >> 3) * multiplierDstY) << 6) + ((u32)(loopDstY << 0x1d) >> 0x1a);
                if (loopSrcX & 1)
                {
                    *pixelsDst = palOffsetBits + (*pixelsSrc >> 4);
                }
                else
                {
                    pixelsSrc = src->pixels + ((loopSrcX >> 1) & 3) + ((loopSrcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1b);
                    *pixelsDst = palOffsetBits + (*pixelsSrc & 0xF);
                }
            }
        }
    }
    else
    {
        for (loopSrcY = srcY, loopDstY = dstY; loopSrcY < yEnd; loopSrcY++, loopDstY++)
        {
            pixelsSrc = src->pixels + ((srcX >> 1) & 3) + ((srcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1b);
            for (loopSrcX = srcX, loopDstX = dstX; loopSrcX < xEnd; loopSrcX++, loopDstX++)
            {
                if (loopSrcX & 1)
                {
                    if ((*pixelsSrc & 0xF0) != colorKeyBits)
                    {
                        pixelsDst = dst->pixels + (loopDstX & 7) + ((loopDstX >> 3) << 6) + (((loopDstY >> 3) * multiplierDstY) << 6) + ((u32)(loopDstY << 0x1d) >> 0x1a);
                        *pixelsDst = palOffsetBits + (*pixelsSrc >> 4);
                    }
                }
                else
                {
                    pixelsSrc = src->pixels + ((loopSrcX >> 1) & 3) + ((loopSrcX >> 3) << 5) + (((loopSrcY >> 3) * multiplierSrcY) << 5) + ((u32)(loopSrcY << 0x1d) >> 0x1b);
                    if ((*pixelsSrc & 0xF) != colorKey)
                    {
                        pixelsDst = dst->pixels + (loopDstX & 7) + ((loopDstX >> 3) << 6) + (((loopDstY >> 3) * multiplierDstY) << 6) + ((u32)(loopDstY << 0x1d) >> 0x1a);
                        *pixelsDst = palOffsetBits + (*pixelsSrc & 0xF);
                    }
                }
            }
        }
    }
}

void FillBitmapRect8Bit(struct Bitmap *surface, u16 x, u16 y, u16 width, u16 height, u8 fillValue)
{
    s32 xEnd;
    s32 yEnd;
    s32 multiplierY;
    s32 loopX, loopY;

    xEnd = x + width;
    if (xEnd > surface->width)
        xEnd = surface->width;

    yEnd = y + height;
    if (yEnd > surface->height)
        yEnd = surface->height;

    multiplierY = (surface->width + (surface->width & 7)) >> 3;

    for (loopY = y; loopY < yEnd; loopY++)
    {
        for (loopX = x; loopX < xEnd; loopX++)
        {
            u8 *pixels = surface->pixels + (loopX & 7) + ((loopX >> 3) << 6) + (((loopY >> 3) * multiplierY) << 6) + ((u32)(loopY << 0x1d) >> 0x1a);
            *pixels = fillValue;
        }
    }
}
