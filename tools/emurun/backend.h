// Emulator backend used by emurun: mGBA (backend_mgba.c) or any libretro GBA core
// (backend_libretro.c, used with VBA-M, the emulator Delta is built on).
#ifndef EMURUN_BACKEND_H
#define EMURUN_BACKEND_H

#include <stdint.h>

// The cartridge clock (RTC) starts at this time (2026-10-24 01:30 UTC, night in the game) and
// advances with emulated time, so play tests behave the same at any hour and on any host
#define EMURUN_EPOCH 1792805400

// Loads the ROM; `save` (may be NULL) is the cartridge save file, created if missing and
// written back by Backend_Deinit.
int Backend_Init(const char *rom, const char *save);
void Backend_Deinit(void);
// One frame with the given keys held (bit 0 A, 1 B, 2 SELECT, 3 START, 4 RIGHT, 5 LEFT, 6 UP,
// 7 DOWN, 8 R, 9 L)
void Backend_RunFrame(unsigned keys);
uint32_t Backend_Read(int size, uint32_t addr);
void Backend_Write(int size, uint32_t addr, uint32_t value);
// The last frame, 240x160, one 0x00BBGGRR word per pixel
const uint32_t *Backend_Video(unsigned *width, unsigned *height);
void Backend_Reset(void);
int Backend_SaveState(const char *path);
int Backend_LoadState(const char *path);
const char *Backend_Name(void);

#endif
