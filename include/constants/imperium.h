#ifndef POKEPLATINUM_CONSTANTS_IMPERIUM_H
#define POKEPLATINUM_CONSTANTS_IMPERIUM_H

// Platinum Imperium settings. The values are stored in renamed vars and flags
// (generated/vars_flags.txt), so they must never change once a save exists.
// See docs/platinum_imperium/API.md.

// VAR_IMPERIUM_DIFFICULTY. 0 is the default, so a cleared var means NORMAL.
#define IMPERIUM_DIFFICULTY_NORMAL 0
#define IMPERIUM_DIFFICULTY_EASY   1
#define IMPERIUM_DIFFICULTY_HARD   2
#define IMPERIUM_DIFFICULTY_COUNT  3

// VAR_IMPERIUM_LEVEL_CAP_MODE. 0 is the default.
#define IMPERIUM_LEVEL_CAP_NORMAL 0
#define IMPERIUM_LEVEL_CAP_HARD   1
#define IMPERIUM_LEVEL_CAP_OFF    2
#define IMPERIUM_LEVEL_CAP_COUNT  3

// VAR_IMPERIUM_SETTINGS_VERSION: written by InitNewGame. 0 means a save made before
// Platinum Imperium (or by vanilla Platinum), whose settings were never initialized.
#define IMPERIUM_SETTINGS_VERSION 1

// The level every cap table gives once the game is completed, or when caps are off.
#define IMPERIUM_LEVEL_CAP_NONE 100

#endif // POKEPLATINUM_CONSTANTS_IMPERIUM_H
