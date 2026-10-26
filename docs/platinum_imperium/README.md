# Pokémon Platinum Imperium

Sinnoh on the GBA, the Crystal Imperium way: the **Sinnoh base** from
[sinnoh-remakes/pokeemerald-platinum](https://github.com/sinnoh-remakes/pokeemerald-platinum) (a
Pokémon Platinum demake on pokeemerald-expansion, imported at `b8819936`), with the systems of
**Crystal Imperium** (this repository's `claude/pokemon-crystal-imperium-vsmmzc` branch) ported on
top: Emerald Imperium's team building, quality of life and competitive difficulty.

This is a GBA game (`PlatinumImperium.gba`, 32 MB), built from source like Crystal Imperium. It runs
in mGBA and in Delta's GBA core.

> **Status: early (0.1.0-experimental).** The Sinnoh base is unfinished upstream: Twinleaf Town
> through Eterna City are built (Routes 201–205, 207, 211 West and part of 219, Oreburgh, Floaroma,
> Valley Windworks, Eterna Forest, Lake Verity, the first room of Mt. Coronet), which is the
> first **two Gyms** (Roark and Gardenia). The rest of Sinnoh comes as the base project adds it.
> Nobody has played the whole stretch through yet.

## What you get

- **A challenge menu** after Rowan's intro (and the same options as Crystal Imperium):
  FEATURES (Easy Catch, Wild Variety 15/30/60%, Auto Run) and DIFFICULTY (EASY / NORMAL / HARD,
  Minimal Grinding, level caps OFF / NORMAL / HARD, EXP ×1 / ×1.5 / ×2 / ×0).
- **Minimal Grinding** (every Pokémon battles with 31 IVs and 0 EVs), **level caps** 15, 24, 33,
  42, 50, 58, 66, 75, 85 (HARD a few lower), **bosses at your cap**, other trainers on the same
  curve, and nothing wild or given above the cap.
- **Key items from the start:** Rare Candy Box, Infinite Repel, Pokémon Box Link, Training Kit
  (nature, ability, IV/EV editor), PokéVial.
- **The L menu:** PokéVial, a PC anywhere, DexNav, TIME (morning, day, evening, night), STATS,
  and the REPEL and AUTO RUN switches.
- **DexNav** with every Pokémon of each area, **Wild Variety** (a daily set of other Gen 1–9
  Pokémon everywhere), search for any Pokémon, hidden Pokémon.
- **Emerald Imperium's abilities, level-up moves and Egg Moves** (Radical Red's).
- **Emerald Imperium's 197 TMs**, reusable, ¥100 each, from a **TM clerk in every Poké Mart**,
  more with each badge.
- **Care packages** from Prof. Rowan, Emerald Imperium's (Radical Red's): a starting package (the
  Shiny Charm, 153 Quick Balls, 10 of every type-boosting item and type-resist Berry, the staple
  held items), one after every badge and for the Champion, and location packages in Oreburgh
  Mine, the Ravaged Path, Valley Windworks, Eterna Forest and Mt. Coronet.
- **Emerald Imperium's cheat codes** at the GameCube in your room: MEGA (every Mega Stone and the
  Mega Ring), CAUGHTALL, EZCATCH, MAXMONEY, SHINYS, MONO, SHINYR, DEXALL and their aliases.
- **Mega Evolution** (the classic Megas).
- **The smart AI for every trainer** (NORMAL and HARD), Sleep Clause; HARD plays SET with no Bag
  in trainer battles.
- **Imperium-style bosses with six Pokémon** at your cap: Barry on Route 203, Roark, Mars at
  Valley Windworks and Gardenia.
- **The Gen 5 look, as in Crystal Imperium:** mudskip's Black/White battle interface (health
  boxes, text box, the FIGHT / BAG / POKéMON / RUN box, a move box with type colours, PP and
  effectiveness symbols, move info on L, party-ball bars, ability pop-ups, outlined fonts) and
  RavePossum's Black/White summary screen (A on the skills page shows IVs, then EVs).
- Quick Rare Candies (several at once, no fanfare), Eggs hatching every 8 steps, the move
  relearner in the party menu, HMs usable by any Pokémon when you carry them, Flash lighting a
  whole cave, a bigger Bag.

**Not ported yet:** the route mini-bosses, the remaining Gyms and story (they don't exist in the
base yet), follower Pokémon.

The BW screens were written for expansion 1.15, and this base is 1.14. Three 1.15 features they
need are rebuilt here: text in four colours (the accent colour of the action box), text printed
onto sprites (`src/sprite_text.c`, through a temporary window), and sprite templates that leave out
their animations.

## Building

On Ubuntu 24.04 / Debian (or WSL2):

```sh
sudo apt install build-essential git libpng-dev gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi
# optional, for the emulator play tests:
sudo apt install libmgba-dev
git clone https://github.com/Cvega6950/glowing-octo-potato.git
cd glowing-octo-potato
git checkout claude/pokemon-platinum-imperium
tools/platinum_imperium/build.sh          # -> PlatinumImperium.gba
tools/platinum_imperium/build.sh --test   # also run the emulator play tests
```

You do not need a Pokémon ROM; the game is compiled from source. No ROM files are distributed
from this repository.

## Playing on Delta (iPhone)

Copy `PlatinumImperium.gba` to the phone (AirDrop, iCloud Drive or Files), then in Delta tap
**+** → **Files** and pick it. Save in the game (START → SAVE). Not yet tested on a device.

## Play tests

`tools/emurun/run_all.sh` boots the ROM in libmgba and plays: `l_menu` (key items, L menu, PokéVial,
switches), `care_packages` (starting, location and badge packages), `tm_clerk` (the TM shop),
`cheat_codes` (every code typed on the keyboard), `bw_ui` (the BW summary screen, action box,
move box and move info, and a battle played to a result), `bosses_m1` (Barry, Roark, Mars and Gardenia with
six at the cap, each battle played to a result). All pass on mGBA.

## Credits

- **pokeemerald-platinum** by the sinnoh-remakes team, on **pokeemerald-expansion** by RHH (Rom
  Hacking Hideout), on pret's **pokeemerald**.
- **mudskip** for the BW battle UI and **RavePossum** for the BW summary screen.
- **Crystal Imperium** and **Pokémon Heart & Soul** (the PokemonHnS-Development team) for the
  systems ported here; **Emerald Imperium** for the design they follow.
