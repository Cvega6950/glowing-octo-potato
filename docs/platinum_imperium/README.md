# Pokémon Platinum Imperium

A hack of **Pokémon Platinum** for the Nintendo DS that brings the systems of our GBA game
**Crystal Imperium** 0.17.0 (Emerald Imperium-style difficulty, Minimal Grinding, level caps,
unlimited Rare Candies, DexNav and the rest; see the `claude/pokemon-crystal-imperium-vsmmzc`
branch) to Platinum's own Sinnoh adventure. It is built on **pret/pokeplatinum**, the
decompilation of Platinum (US), so the whole game is compiled from source and every change is
made in Platinum's own engine.

> **Status: stage 1 of 4 (setup) done; no gameplay changes yet.** What works today is listed
> below with how it was tested. Nothing is marked done unless it was tested in an emulator.

## Stages

| Stage | Contents | Status |
|---|---|---|
| 1. Setup | Platinum builds from source; a play-test runner on the exact emulator core Delta uses | **Done** (see Evidence) |
| 2. First playable | Auto-run, level caps, Rare Candy Box, reusable TMs, EXP Share for all, faster battles and text, move relearner, nature/IV/ability tools, Minimal Grinding, smart AI, redesigned boss teams; Gen 1–4 Pokémon | Not started |
| 3. DexNav | A DexNav for the DS screens | Not started |
| 4. Gen 5–9 Pokémon | New species, the Fairy type, modern moves and abilities, Megas | Not started |

The engineering plan, with where every feature hooks into Platinum's code, is in
[ENGINE_NOTES.md](ENGINE_NOTES.md).

## Evidence (2026-11-14)

| Check | Result |
|---|---|
| Vanilla build from this repository (`make`) | The ROM's SHA-1 is `0862ec35b24de5c7e2dcb88c9eea0873110d755c`, Platinum (US) Rev 1, byte for byte |
| Delta-core runner (`tools/dsrun/`) | Builds melonDS 0.9.5 from `rileytestut/melonDS` at `a53f9ba`, the commit Delta's DS core pins, set up as Delta sets it up (no JIT, threaded software renderer, direct boot, no BIOS files needed) |
| Play test `boot` | **PASS**: the ROM boots without BIOS files and runs its intro (about 400 frames a second, 6.7× real time) |

## Building

You do not need a Pokémon ROM; the game is compiled from source.

On Ubuntu 24.04 / Debian (or WSL2 on Windows):

```sh
sudo dpkg --add-architecture i386 && sudo apt update
sudo apt install bison flex g++ gcc-arm-none-eabi git make ninja-build pkg-config wget python3 xz-utils nasm libc6:i386 libpng-dev cmake
git clone https://github.com/Cvega6950/glowing-octo-potato.git
cd glowing-octo-potato
git checkout claude/jolly-darwin-21v99a
tools/imperium/build.sh          # -> PlatinumImperium.nds
tools/imperium/build.sh --test   # also build the Delta-core runner and run the play tests
```

The first build downloads the compiler (mid-kid's metroskrew), meson and the DS libraries, and
takes a few minutes. `make` alone builds unchanged Platinum and checks its SHA-1.

## Playing on Delta (iPhone)

1. Get `PlatinumImperium.nds` onto the phone. Either build it as above and copy it over
   (AirDrop, iCloud Drive or Files), or make this GitHub repository **private** and download it
   from *Actions → Platinum Imperium → latest run → Artifacts*. CI only uploads the ROM for
   private repositories, because it contains Nintendo's game.
2. In Delta, tap **+** and pick `PlatinumImperium.nds`. No BIOS files are needed (Delta 1.6 or
   later).
3. Save in the game (X → SAVE). Delta keeps the cartridge save.

The game keeps Platinum's game code (`CPUE`), which Delta's melonDS uses to pick the save type.

No ROM files are distributed from this repository.

## Credits

- **pret** and the pokeplatinum contributors: the decompilation this hack is built on.
- **mid-kid**: metroskrew, the packaged compiler the build uses. **ntrtwl**: the DS libraries.
- **melonDS** (Arisotura and contributors) and **Riley Testut**'s fork of it inside Delta: the
  play-test runner's emulator core.
- **Pokémon Emerald Imperium** (iriv24 and team): the design of the systems, by way of Crystal
  Imperium.
- Pokémon is © Nintendo / Creatures Inc. / GAME FREAK inc. This is a non-commercial fan
  project; do not sell or redistribute ROM files.
