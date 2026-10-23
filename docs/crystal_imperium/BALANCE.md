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
5. **Measure win rates, not single runs.** The battle autopilot (`tools/emurun`) plays a
   deliberately naive line: no items, no voluntary switching, one fixed move per Pokémon.
   For each Starter, at least one line obtainable at the cap must win, and a naive line
   should win some but not all of five RNG samples. A human who heals and switches does
   better than these numbers.

## Progression snapshot

| Segment | Level cap | Status |
|---|---|---|
| Early Johto (Falkner, Bugsy, Whitney) | 11 / 16 / 21 | All three reworked and play-tested |
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

## Azalea and Goldenrod: Bugsy and Whitney

### What the player can have

- **Before Bugsy (cap 16), from `encounters.json`:**
  - Rock: Geodude and Onix (Union Cave), the main Bug/Flying answers.
  - Flying: Pidgey, Spearow, Zubat.
  - Fighting: Machop (Route 33).
  - Other: Heracross (Rock Smash in Azalea), Mareep → Flaaffy, and the Fire Starter.
- **Before Whitney (cap 21):**
  - Everything above, plus Abra on Route 34 (Kadabra at 16, which turns out to be the best
    answer to Whitney's first three).
  - Mankey, Snubbull, Growlithe, Yanma, Drowzee and Ditto.
  - Scyther and Pinsir from the National Park.
  - Gastly (Ghost) from Route 32 at night, though Whitney's Scrappy Miltank still hits it.

### Bugsy (Azalea Gym), ace level 16 = cap 16

AI: `Smart Trainer / Ace Pokemon / HP Aware`. Items: Potion ×2 (unchanged from HnS).

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Spinarak Lv 14 | Focus Sash | Insomnia | Jolly | Sticky Web, Night Shade, Poison Sting, Infestation | Guaranteed Sticky Web |
| Pineco Lv 15 | – | Sturdy | Relaxed | Spikes, Rock Tomb, Bug Bite, Protect | Spikes; Rock Tomb punishes the Fire/Flying answers |
| Ledian Lv 15 | Sitrus Berry | Early Bird | Calm | Reflect, Light Screen, Silver Wind, Mach Punch | Screens for the ace; Mach Punch hits Rock answers |
| Scyther Lv 16 (ace) | Eviolite | Technician | Jolly | Fury Cutter, Wing Attack, Bug Bite, Quick Attack | Technician-boosted cleaner; Fury Cutter escalates |

**Signature strategy:** hazards and screens, then a bulky Technician Scyther. Rock types
are 4× effective on Scyther and Ledian, and Stealth Rock alone takes half their HP.

**Iterations (emulator):**
- v1 Scyther had Swords Dance. At +2 it one-shot Quilava, Geodude, Flaaffy and Pidgey in a
  row. Sticky Web plus base 105 Speed meant Rock types never moved first. Swords Dance became
  Fury Cutter, Bugsy's HGSS signature.

**Results** (v2, autopilot, no items, all Pokémon at Lv 16):

| Starter | Line | Result |
|---|---|---|
| Cyndaquil | Quilava (Ember) / Geodude (Rock Throw) / Flaaffy (Thunder Shock) / Pidgey (Gust) | **3 of 5 RNG samples won** (`bugsy.emu`) |
| Chikorita | Onix lead (Stealth Rock) / Pidgey / Flaaffy / Bayleef | **Win** (2 Pokémon left) |
| Chikorita | Bayleef, Geodude or Onix (Rock Throw) leads | Loss: Spinarak (Bug/Poison) walls Grass |
| Totodile | Croconaw (Bite) / Geodude / Flaaffy / Pidgey | **Win** (2 Pokémon left) |
| Totodile | Croconaw (Water Gun), or Onix leads | Loss |

### Whitney (Goldenrod Gym), ace level 21 = cap 21

AI: `Smart Trainer / Ace Pokemon / HP Aware`. Items: one Potion (HnS had Super Potion + Potion).

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Clefairy Lv 18 | – | Magic Guard | Bold | Double Slap, Metronome, Encore, Charm | Disruption: Encore locks set-up, Charm blunts physical attackers |
| Aipom Lv 19 | – | Pickup | Jolly | Fake Out, Double Hit, U-turn, Astonish | Pivot that chips and keeps momentum |
| Stantler Lv 19 | – | Intimidate | Adamant | Hypnosis, Stomp, Zen Headbutt, Take Down | Intimidate weakens the Fighting answer; one sleeper under Sleep Clause |
| Miltank Lv 21 (ace) | – | Scrappy | Impish | Rollout, Body Slam, Milk Drink, Attract | The classic: Rollout snowball, Attract, Milk Drink; Scrappy hits Ghosts |

**Signature strategy:** wear the player down with disruption, then a Miltank that can't be
walled by Ghosts. The answers are female Pokémon (Attract fails on them), a fresh Fighting
type held back for Miltank, and Kadabra for the support cast.

**Iterations (emulator).** Each version lost every naive line, so each was cut back:
1. v1 Clefairy had Eviolite and Moonlight; Stantler had Hypnosis, Confuse Ray and a Sitrus
   Berry. Battles stalled for 14+ turns.
2. v2 Clefairy (Fairy-type with the Fairy option on) still resisted both classic answers,
   Fighting and Dark. Cute Charm plus Thunder Wave cost Quilava nine turns in a row.
3. v3 Aipom's Skill Link Fury Swipes acted as a second ace.
4. v4 Miltank alone beat four Pokémon with three heal sources (Milk Drink, Sitrus Berry,
   Super Potion).
5. **Shipped (v5):** Clefairy without Eviolite, Thunder Wave or Cute Charm; Aipom as a
   Pickup pivot; supporting levels 18/19/19; Miltank without a Sitrus Berry; one Potion.

**Results** (shipped version, autopilot, no items, all Pokémon at Lv 21):

| Starter | Line | Result |
|---|---|---|
| Cyndaquil | Pidgeotto (Gust) / Quilava (Flame Wheel) / Kadabra (Psybeam) / Machop (Low Sweep) | **3 of 5 RNG samples won** (`whitney.emu`) |
| Cyndaquil | Quilava or Kadabra leads with the same Pokémon | Loss (Miltank left at 1 HP in one) |
| Chikorita | Bayleef (Mega Drain) / Kadabra / Pidgeotto / Machop | **Win** (3 Pokémon left) |
| Totodile | Kadabra / Croconaw (Ice Fang) / Pidgeotto / Machop | **Win** |
| Totodile | Pidgeotto / Croconaw / Flaaffy / Machop | **Win** |
| Totodile | Croconaw / Machop / Geodude / Flaaffy | Loss |

### Gym trainers

All now have defined movesets and abilities. They sit 2–4 levels under the cap and use
`Basic Trainer` AI.

| Gym | Trainer | Team |
|---|---|---|
| Azalea | Bug Catcher Benny | Kakuna 12, Beedrill 14 (Swarm; Twineedle) |
| Azalea | Bug Catcher Al | Metapod 12, Butterfree 14 (Compound Eyes Sleep Powder) |
| Azalea | Bug Catcher Josh | Yanma 14 (Speed Boost, Detect) |
| Azalea | Twins Amy & May (double) | Ledyba 13, Spinarak 13 |
| Goldenrod | Lass Carrie | Snubbull 18 (Intimidate), Happiny 18 @ Eviolite |
| Goldenrod | Lass Bridget | Aipom 18 (Fake Out), Munchlax 19 (Thick Fat, Recycle + Oran Berry) |
| Goldenrod | Beauty Victoria | Teddiursa 18, Furret 19 (Rest) |
| Goldenrod | Beauty Samantha | Meowth 19 (Technician Fake Out), Girafarig 19 |

## Mega Evolution

| Stage | Stones sold by the Goldenrod Mega Specialist |
|---|---|
| Badge 3 (Mega Ring given) | Beedrill, Pidgeot, Ampharos, Heracross, Pinsir, Audino, Lopunny, Manectric, Sableye, Banette, Staraptor |
| Badge 6 | Venusaur, Charizard X/Y, Blastoise, Sceptile, Blaziken, Swampert, Gengar, Alakazam, Slowbro, Steelix, Scizor, Houndoom, Absol, Glalie, Abomasnow, Altaria, Camerupt, Sharpedo, Aggron, Medicham, Gardevoir, Gallade, Aerodactyl, Kangaskhan, Mawile |
| Badge 8 | Gyarados, Lucario, Tyranitar, Salamence, Metagross, Garchomp |
| Johto Champion | Mewtwo X/Y, Latias, Latios, Diancie |

The first tier is mostly weaker Megas, so having a Mega around Whitney/Morty adds options
without breaking the level-cap curve. Medicham (Pure Power) and Kangaskhan (Parental Bond)
are held back to badge 6 on purpose.

Boss Megas so far: Lance (Gyarados), Lance rematch (Salamence), Lance postgame (Charizard X),
Red and Red postgame (Charizard Y). Each one uses a stone the player can buy before that fight.

## Planned Gym designs (Milestones 2–3)

Every leader keeps a recognisable signature Pokémon. These designs are drafts until they are
implemented and play-tested.

| # | Leader | Signature | Strategy idea |
|---|---|---|---|
| 2 | Bugsy | Scyther | **Done**: see above |
| 3 | Whitney | Miltank | **Done**: see above |
| 4 | Morty | Gengar (Haunter at cap) | Hypnosis + Hex, Curse/Destiny Bond, Ghost immunity pivots |
| 5 | Chuck | Poliwrath | Bulk Up, Mach Punch priority, Intimidate and Guts users |
| 6 | Jasmine | Steelix | Stealth Rock, Sturdy, Magnemite Electric coverage |
| 7 | Pryce | Piloswine / Mamoswine | Hail team, Slush Rush, Ice Shard priority |
| 8 | Clair | Kingdra | Rain Swift Swim Kingdra, Dragon Dance, Dragonite/Dudunsparce bulk |
| 9–16 | Kanto leaders | Raichu, Alakazam, Vileplume, Crobat, Starmie, Onix/Steelix, Arcanine, Blue's mixed team | Themes per the project brief, with weather/terrain cores where they fit |
