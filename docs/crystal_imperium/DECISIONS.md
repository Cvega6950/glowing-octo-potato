# Crystal Imperium: architecture decisions

Short records of decisions that shape the project. Newest last.

## D1. Foundation: Pokémon Heart & Soul 2.0.6

- **Base:** `PokemonHnS-Development/pokehns-expansion`, tag `2.0.6`, commit
  `167aa6d537b109bb229c231ddce4616974c4da71` (2026-09-16). The full upstream history is
  preserved; the remote is configured as `upstream`.
- **Why:** HnS already has the whole Johto story, the Kanto postgame, Red, day/night, HGSS music
  and a modern pokeemerald-expansion battle engine. Re-creating that on another base would cost
  far more than adding Imperium-style gameplay on top of it.
- **Build target:** `make hns` → `pokehns.gba`, copied to `CrystalImperium.gba` by
  `tools/crystal_imperium/build.sh` and CI.
- **No engine migration:** we do not merge newer RHH or Emerald Imperium engine code into HnS.
  Gameplay changes are made as HnS data and small, isolated engine hooks.

## D2. Emerald Imperium is a design reference, not a code source

- `iriv24/pokeemerald-expansion` (`release` branch, commit `2576d0f3`, 2025-09-01) has no
  license file. Its original assets (24 custom Megas, sprites, rebalanced species data) carry
  no grant to reuse them.
- Imperium is also built on an older expansion version, so its files do not drop into HnS.
- **Decision:** we re-implement Imperium *behaviours* (Minimal Grinding Mode, sleep clause,
  competitive trainers, cheap team-building items) as original code and data. We copy no
  Imperium source or assets unless the authors grant permission, which is tracked as a blocker
  in [FEATURE_MATRIX.md](FEATURE_MATRIX.md).

## D3. Minimal Grinding Mode is symmetric

- When on, `CalculateMonStats` treats **every** Pokémon (player, trainer and wild) as having
  31 IVs and 0 EVs. Stored IVs/EVs are untouched, so Hidden Power types still vary and turning
  the mode off restores normal stats.
- This matches Emerald Imperium's mode, which ignores EVs in its stat formula, and means boss
  stats don't depend on the player grinding.
- Turning it on in the menu also selects HnS's existing options for max player IVs, no EV gain,
  NORMAL level caps and ×1.5 EXP. Each one stays individually adjustable.
- **Save compatibility:** the flag uses spare bits of an existing `ChallengeSettings` byte
  (`SaveBlock3` layout and size unchanged). Older HnS saves load fine and read the mode as OFF.
  These saves can enable it from the in-game settings PC.

## D4. Sleep Clause is always on

`B_SLEEP_CLAUSE TRUE`. Bosses use Hypnosis/Sleep Powder; without the clause a single sleep move
can decide a fight. This applies to both sides, like Emerald Imperium.

## D5. Boss AI baseline

- Gym Leaders and mini-bosses: `Smart Trainer / Ace Pokemon / HP Aware`. Smart Trainer is
  omniscient, switches smartly and avoids PP stalling.
- Elite Four, Champion, Red and postgame bosses also get `Prediction`.
- Ordinary trainers keep HnS's cheaper AI. AI time per turn matters on hardware and on phones.

## D6. Level caps stay tied to Gym aces

HnS's NORMAL cap table (`src/caps.c`) equals the next Gym Leader's highest level. Reworked
leaders keep their ace at that cap, so the player can always match the ace's level.
`tools/crystal_imperium/validate.py` enforces this.

## D7. ROM budget

- The baseline ROM uses 94.5% of the 32 MB GBA address space, and EWRAM is at 94.6%.
- All Gen 1–9 species are already compiled in, but HnS disables Mega Evolution. Every new asset
  (Mega sprites, new maps) competes for about 1.7 MB.
- Measurements are recorded in [FEATURE_MATRIX.md](FEATURE_MATRIX.md) before enabling anything large.

## D8. Distribution

- This repository is public, so the built ROM (which contains Nintendo's copyrighted assets) is
  **not** published from it.
- CI uploads `CrystalImperium.gba` as a run artifact only when the repository is private.
- Public releases should be patches plus build-from-source instructions, never ROM files.
- Building from source needs no Nintendo ROM; the decomp tool chain produces the ROM itself.
