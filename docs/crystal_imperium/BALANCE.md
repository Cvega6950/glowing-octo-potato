# Crystal Imperium: battle balance

The machine-readable data is in `data/trainer_balance.json` and `data/encounters.json`,
generated from the game's source files by `tools/crystal_imperium/validate.py`. This page
explains the *why*.

## Principles

1. **Levels come from the level-cap table, not from Emerald Imperium.** HnS's NORMAL cap
   (`src/caps.c`) is the next Gym ace's level: 11, 16, 21, 25, 31, 36, 38, 45, 56; then 70
   for Kanto and uncapped after the Kanto League. A leader's ace sits *at* the cap, so a
   capped player is never under-levelled. Difficulty comes from teams, not levels.
2. **Bosses have perfect IVs, defined natures, abilities, items and four chosen moves.**
   With Minimal Grinding on (the default), every Pokémon battles at 31 IVs / 0 EVs anyway.
3. **Each boss has a signature strategy and a fair counter** that the player can catch
   before the fight. The counter should cost planning, not be a free win.
4. **Verify in the emulator.** Every reworked Gym Leader gets a play test with a realistic
   team of Pokémon that are obtainable before the fight.

## Progression snapshot

| Segment | Level cap | Status |
|---|---|---|
| Early Johto (Falkner, Bugsy, Whitney) | 11 / 16 / 21 | Falkner reworked; others HnS |
| Midgame Johto (Morty, Chuck, Jasmine, Pryce) | 25 / 31 / 36 / 38 | HnS. Pryce's ace (33) is below his cap (38), noted by the validator. |
| Late Johto (Clair, Victory Road) | 45 / 56 | HnS |
| Elite Four / Lance | 56 → 70 after the title | HnS |
| Kanto, Mt. Silver, postgame | ≤ 70, then uncapped | HnS |

## Early Johto: the path to Falkner

Pokémon the player can catch before Falkner (from `encounters.json`): Route 29–31 (Pidgey,
Sentret, Hoothoot, Ledyba, Spinarak, Hoppip, Exeggcute, Pineco, Caterpie, Weedle, Poliwag,
Bellsprout, **Mareep**, **Pichu**, Gastly at night), Route 46 (**Geodude**, **Phanpy**,
Heracross, Aipom, Spearow) and Dark Cave (**Larvitar**, Teddiursa, Dunsparce, Geodude, Zubat).
Bold entries resist or hit Flying types super-effectively.

| Trainer | Team | Role |
|---|---|---|
| Bird Keeper Rod | Pidgey 8, Natu 8 | Teaches accuracy drops (Sand Attack) and Night Shade |
| Bird Keeper Abe | Hoothoot 8, Spearow 9 @ Oran Berry | Hypnosis preview before Falkner |
| Elder Li (Sprout Tower) | Gastly 8, Hoppip 8, Bellsprout 10 @ Oran Berry | Mini-boss: Mean Look + Hypnosis trap, Growth sweeper ace |

### Falkner (Violet Gym), ace level 11 = cap 11

AI: `Smart Trainer / Ace Pokemon / HP Aware`. All Pokémon have 31 IVs.

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Pidgey Lv 9 | Oran Berry | Big Pecks | Timid | Tailwind, Gust, Sand Attack, Quick Attack | Speed control + accuracy chip lead |
| Rookidee Lv 10 | – | Keen Eye | Adamant | Hone Claws, Power Trip, Peck, Steel Wing | Set-up threat; Steel Wing punishes Rock answers |
| Noctowl Lv 11 (ace) | Sitrus Berry | Tinted Lens | Modest | Hypnosis, Air Cutter, Reflect, Mud-Slap | Tinted Lens beats resists; Reflect blunts Rollout; Mud-Slap hits Electric/Rock |

**Signature strategy:** a Tailwind lead into a Hone Claws/Power Trip set-up. The ace
punishes the classic Rock/Electric answers instead of folding to them.

**Emulator results** (`tools/emurun/tests/falkner.emu`; team Cyndaquil / Mareep / Geodude,
all Lv 11, no items):
- First version: Geodude's Defense Curl + Rollout soloed Rookidee and Noctowl. Too easy, so
  Rookidee got Steel Wing and Noctowl got Reflect in place of Leer and Confusion.
- Retuned version, line A: Cyndaquil Embers Pidgey; Geodude Curl/Rollout takes Rookidee and
  falls to Noctowl; Mareep's Thunder Wave + Thunder Shock finishes Noctowl. **Win.**
- Retuned version, line B: the same plan, but RNG went the other way. Noctowl beats Mareep
  too, and Cyndaquil at 13 HP loses. **Loss.**
- Conclusion: winnable with three Pokémon and no items, but not automatic. Using Potions, a
  fourth Pokémon (Larvitar, Pichu, Phanpy) or leading Mareep into Noctowl improves the odds.
  This is the intended Gym 1 difficulty.

## Planned Gym designs (Milestones 2–3)

Every leader keeps a recognisable signature Pokémon. These designs are drafts until they are
implemented and play-tested.

| # | Leader | Signature | Strategy idea |
|---|---|---|---|
| 2 | Bugsy | Scyther | Sticky Web lead, U-turn pivoting, Technician Scyther ace |
| 3 | Whitney | Miltank | Attract/Fake Out disruption, Scrappy Miltank with Rollout + Milk Drink |
| 4 | Morty | Gengar (Haunter at cap) | Hypnosis + Hex, Curse/Destiny Bond, Ghost immunity pivots |
| 5 | Chuck | Poliwrath | Bulk Up, Mach Punch priority, Intimidate and Guts users |
| 6 | Jasmine | Steelix | Stealth Rock, Sturdy, Magnemite Electric coverage |
| 7 | Pryce | Piloswine / Mamoswine | Hail team, Slush Rush, Ice Shard priority |
| 8 | Clair | Kingdra | Rain Swift Swim Kingdra, Dragon Dance, Dragonite/Dudunsparce bulk |
| 9–16 | Kanto leaders | Raichu, Alakazam, Vileplume, Crobat, Starmie, Onix/Steelix, Arcanine, Blue's mixed team | Themes per the project brief, with weather/terrain cores where they fit |
