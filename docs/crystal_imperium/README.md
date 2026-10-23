# Pokémon Crystal Imperium

The Johto and Kanto adventure of **Pokémon Heart & Soul** (a Gen 2 remake on the
pokeemerald-expansion GBA engine), rebuilt with the competitive difficulty and no-grind team
building of **Pokémon Emerald Imperium**.

> **Status: early development (Milestone 1, experimental).** The game is fully playable
> because it is the complete Heart & Soul adventure. Only the first block of Crystal Imperium
> changes is in so far; see the progress report below.

## Progress report (2026-10-23)

**Done and verified in the emulator**
- Baseline: HnS 2.0.6 (`167aa6d5`) builds reproducibly and boots in mGBA.
- **Minimal Grinding Mode**: a new Difficulty option, ON by default. Every Pokémon battles as
  if it had 31 IVs / 0 EVs. Turning it on also enables max player IVs, no EV gain, NORMAL
  level caps and ×1.5 EXP.
- **Falkner** rebuilt as a competitive boss (Tailwind Pidgey → Hone Claws/Power Trip/Steel Wing
  Rookidee → Tinted Lens Noctowl with Reflect and Hypnosis, Smart AI). Play-tested to be
  beatable with Pokémon catchable before him, but not free.
- **Ability Capsule and Ability Patch** sold at the Goldenrod Flower Shop with the Mints.
- **Save, hard reset and Continue** work.
- Level caps block EXP at the cap during battle.

**Done, build-verified only**
- Sleep Clause always on.
- Violet Gym trainers and Elder Li (Sprout Tower) reworked.

**Not started / incomplete**
- Gyms 2–16, rivals, Rockets, Kimono Girls, Elite Four, Lance, Red (Milestones 2–5).
- Gen 4–9 encounter roll-out: 373 national-dex families have no in-game source yet.
- Megas, DexNav, menu move relearner and portable PC.
- A full story playthrough. Only New Game → bedroom is played without debug tools.

**Blocked**
- Emerald Imperium's custom Megas and assets: no license to reuse them (DECISIONS.md D2).
- Enabling every standard Mega: ROM budget (99.2% of 32 MB); must be curated.
- Delta testing: needs a real iPhone.

Details: [FEATURE_MATRIX.md](FEATURE_MATRIX.md) · [BALANCE.md](BALANCE.md) ·
[TESTING.md](TESTING.md) · [DECISIONS.md](DECISIONS.md) · [KNOWN_ISSUES.md](KNOWN_ISSUES.md) ·
[CHANGELOG.md](CHANGELOG.md)

## Building

You do **not** need a Pokémon ROM; the game is compiled entirely from source.

On Ubuntu 24.04 / Debian (or WSL2 on Windows):

```sh
sudo apt install build-essential git libpng-dev gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi
# optional, for the emulator play tests:
sudo apt install libmgba-dev
git clone https://github.com/Cvega6950/glowing-octo-potato.git
cd glowing-octo-potato
git checkout claude/pokemon-crystal-imperium-vsmmzc
tools/crystal_imperium/build.sh          # -> CrystalImperium.gba
tools/crystal_imperium/build.sh --test   # also run the emulator play tests
```

The first build takes a few minutes. Tested tool chain: arm-none-eabi-gcc 13.2.1, libmgba 0.10.2.

## Playing on Delta (iPhone)

1. Get `CrystalImperium.gba` onto the phone. Either:
   - build it as above and copy it over (AirDrop, iCloud Drive or Files), or
   - make this GitHub repository **private**, then open *Actions → Crystal Imperium → latest
     run → Artifacts* and download `CrystalImperium-<commit>` on the phone. CI only uploads
     the ROM for private repositories, because the ROM contains Nintendo's copyrighted
     assets.
2. In Delta, tap **+** → **Files** and pick `CrystalImperium.gba`.
3. Use the in-game SAVE (START → SAVE). Delta keeps the cartridge save between sessions.
4. If the day/night clock misbehaves, open the settings PC in your house and set Clock Type
   to the ROM's fake clock.

Device testing on Delta has not been done yet. Please report what happens using the checklist
in [TESTING.md](TESTING.md).

## Saves

Saves from Heart & Soul 2.0.6 load in Crystal Imperium; Minimal Grinding starts OFF for them
and can be turned on from the settings PC. No save invalidation has been needed so far.

## Credits

- **Pokémon Heart & Soul**: the PokemonHnS-Development team (see the repository's
  `CREDITS.md`). The whole Johto/Kanto adventure, maps, scripts, music and features come
  from them.
- **pokeemerald-expansion**: the Rom Hacking Hideout (RHH) contributors, and **pret** for the
  pokeemerald decompilation.
- **Pokémon Emerald Imperium** (iriv24 and team): the design inspiration for Minimal Grinding
  Mode, Sleep Clause and competitive trainer philosophy. No Imperium code or assets are used.
- Pokémon is © Nintendo / Creatures Inc. / GAME FREAK inc. This is a non-commercial fan
  project; do not sell or redistribute ROM files.
