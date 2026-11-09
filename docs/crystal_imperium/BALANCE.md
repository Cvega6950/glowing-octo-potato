# Crystal Imperium: battle balance

The machine-readable data is in `data/trainer_balance.json` and `data/encounters.json`,
generated from the game's source files by `tools/crystal_imperium/validate.py`. This page
explains the *why*.

## Principles

1. **Levels come from the level-cap table, set like Emerald Imperium's** (since 0.8.0, D29): 15,
   24, 33, 42, 50, 58, 66, 75 and 85 for the Elite Four, the highest cap before the Elite Four is
   first beaten, as in Emerald Imperium; then 90 for Kanto and uncapped (100) after the Kanto
   League. HARD level caps are 12, 21, 30, 39, 47, 55, 63, 72, then 85 and 90. **Every boss
   Pokémon sits at the cap** of the earliest point its battle can happen (since 0.7.0; before,
   only the ace did), and a boss fought later is raised to the player's cap then (D21); other
   trainers' Heart & Soul levels are mapped onto the curve. With the Rare Candy Box the player
   can always match a boss, never beat it: difficulty comes from teams, not levels. Before
   0.8.0 the caps were Heart & Soul's (11, 16, 21, 25, 31, 36, 38, 45, 56, then 70); the win rates
   below were measured at the NORMAL caps of the version named.
2. **Bosses have perfect IVs, defined natures, abilities, items and four chosen moves.**
   With Minimal Grinding on (the default), every Pokémon battles at 31 IVs / 0 EVs anyway,
   except Red's, which keep their EVs (D27). Since 0.17.0 every designed team follows the
   trainer standard (`TRAINER_STANDARD.md`, D59): its Pokémon as evolved as their level allows
   wherever the battle can be fought (but a named Eviolite species holding its Eviolite and a
   Light Ball Pikachu), sets that fit a plan and, from the 3rd badge (Morty, the 4th Gym, on), a
   setup move, priority and a pivot or hazards on the boss teams, a Mega on each, and EV spreads
   through the Johto League (none at 100 but Red's), which count with Minimal Grinding off.
3. **Each boss has a signature strategy and a fair counter** that the player can catch
   before the fight. The counter should cost planning, not be a free win.
4. **Verify in the emulator.** Every reworked Gym Leader gets a play test with a realistic
   team of Pokémon that are obtainable before the fight.
5. **Measure win rates, not single runs.** The battle autopilot (`tools/emurun`) plays a
   deliberately naive line: no voluntary switching, one fixed move per Pokémon, and since 0.7.0
   held items only from the care packages the player has by then (before, no items).
   For each Starter, at least one line obtainable at the cap must win, and a naive line
   should win some but not all of its RNG samples (five, or twelve where the naive win rate
   is low). For the Elite Four from Will on, Blue and Red the autopilot plays a simple game
   plan instead, as a player would: for each of the boss's Pokémon some of the team have a
   move to use, and one of them is switched in when the Pokémon out has none. The number of
   tries follows the measured win rate, so that a correct game passes all but about one run in
   a hundred. A human who heals, switches and reads the opponent does better than these numbers.
6. **Every trainer plays with Emerald Imperium's boss AI** on NORMAL and HARD (since 0.18.0, D60):
   it knows the player's team, picks its moves for KOs and effects, switches and chooses its
   next Pokémon smartly, and plays with Emerald Imperium's own behaviours (Shell Smash, set-up
   only when it survives the player's best roll, pivots out of lost trades, phazing into hazards
   and more). The `AI:` lines below are the party data's own flags: EASY plays with them, and on
   NORMAL and HARD `Random Switch-ins`, `HP Aware`, `PP Stall Prevention` and `Ace Pokemon` are
   taken off (the ace can come in whenever it is the best choice). On HARD the player's Pokémon
   also get no badge boosts (Emerald Imperium's rule; D25, D60). The AI is measured with a
   player AI that switches and sets up (`tools/emurun/ai_measure.py`, TESTING.md).

## Progression snapshot

| Segment | Level cap | Status |
|---|---|---|
| Early Johto (Falkner, Bugsy, Whitney; Proton, rival 2–3) | 15 / 24 / 33 | Reworked and play-tested (`falkner`, `bugsy`, `whitney`, `bosses_m3`) |
| Midgame Johto (Morty, Chuck, Jasmine, Pryce; Rocket Hideout) | 42 / 50 / 58 / 66 | Reworked; Chuck, Jasmine and Pryce in three versions for any order (`bosses_m3`, `bosses_m4`) |
| Late Johto (Radio Tower, rival 4, Clair, Kimono Girls, Victory Road) | 75 / 85 | Reworked (`bosses_m3`, `bosses_m4`) |
| Elite Four / Lance | 85 → 90 after the title | Reworked (`bosses_e4`) |
| Kanto leaders, Blue | 90 | Reworked (`bosses_m5`) |
| Red (Mt. Silver) | after the Kanto League, uncapped; 100 | Reworked: the hardest battle (`red`) |
| Rematches and other postgame battles | 90 / uncapped (100) | Emerald Imperium-style teams since 0.15.0 (D47), at the cap (`boss_rematches`) |

## Early Johto: the path to Falkner

Pokémon the player can catch before Falkner (from `encounters.json`): Route 29–31 (Pidgey,
Sentret, Hoothoot, Ledyba, Spinarak, Hoppip, Exeggcute, Pineco, Caterpie, Weedle, Poliwag,
Bellsprout, **Mareep**, **Pichu**, Gastly at night), Route 46 (**Geodude**, **Phanpy**,
Heracross, Aipom, Spearow) and Dark Cave (**Larvitar**, Teddiursa, Dunsparce, Geodude, Zubat).
Bold entries resist or hit Flying types super-effectively.

| Trainer | Team | Role |
|---|---|---|
| Bird Keeper Rod | Pidgey 8, Natu 8 (11 and 11 on the 0.8.0 cap curve) | Teaches accuracy drops (Sand Attack) and Night Shade |
| Bird Keeper Abe | Hoothoot 8, Spearow 9 @ Oran Berry (11 and 12 on the curve) | Hypnosis preview before Falkner |
| Elder Li (Sprout Tower) | Bronzor (Eviolite), Phantump (Eviolite), Weepinbell (Liechi Berry), all 15 (0.15.0 to 0.16.0: the same three, Weepinbell with an Eviolite and Chlorophyll, all with EVs; before 0.15.0: Gastly, Hoppip, Bellsprout @ Oran Berry; 0.7.x: 11; 0.6.0: 8, 8, 10) | Mini-boss: Stealth Rock and Light Screen, burns for Hex, a Gluttony Weepinbell ace that sleeps and heals |

### Falkner (Violet Gym), all at level 15 = cap 15 (11 before 0.8.0)

AI: `Smart Trainer / Ace Pokemon / HP Aware`. No healing items. Since 0.17.0 (the trainer
standard, D59):

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Murkrow Lv 15 | Eviolite | Prankster | Bold | Tailwind, Thunder Wave, Foul Play, Haze | Lead: priority Tailwind and Thunder Wave; Haze for anything that sets up on it |
| Natu Lv 15 | Eviolite | Magic Bounce | Bold | Night Shade, Air Cutter, Teleport, Wish | Bounces back status and hazards; passes Wish with Teleport |
| Fletchling Lv 15 | Oran Berry | Gale Wings | Jolly | Acrobatics, Flame Charge, U-turn, Roost | Priority Acrobatics at full HP, doubled once its Berry is eaten |
| Trumbeak Lv 15 | Muscle Band | Skill Link | Adamant | Rock Blast, Bullet Seed, Pluck, Knock Off | Five-hit Bullet Seed for Geodude and Onix, Rock Blast for Ice and Bug types |
| Squawkabilly Lv 15 | Silk Scarf | Intimidate | Jolly | Parting Shot, Dual Wingbeat, Facade, Quick Attack | Intimidate, then Parting Shot weakens the next attacker too |
| Pidgeotto Lv 15 (ace) | Sitrus Berry | No Guard | Adamant | Wing Attack, Steel Wing, Quick Attack, Roost | The ace, in place of Heart & Soul's Noctowl; a Steel Wing that never misses for Rock types |

**Signature strategy:** Tailwind and pivots, the first Gym's lesson in speed. Priority Tailwind,
Wish passed with Teleport and Parting Shot bring each attacker in fast and healthy, and the two
hitters carry moves for the Rock, Ice and Bug types a player brings against a Flying Gym.

From 0.8.0 to 0.16.0 his six were Pidgey (Tailwind), Natu, Fletchling, Murkrow, Rookidee (Hone Claws
and Power Trip) and a Tinted Lens Noctowl with Hypnosis and Reflect. The notes below are from his
three before 0.8.0 (Pidgey, Rookidee and Noctowl).

**Emulator results** (`tools/emurun/tests/falkner.emu`; team Cyndaquil / Mareep / Geodude,
all Lv 11, no items; measured when Pidgey and Rookidee were 9 and 10, before 0.7.0):
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

- **Before Bugsy (cap 24; 16 before 0.8.0), from `encounters.json`:**
  - Rock: Geodude and Onix (Union Cave), the main Bug/Flying answers.
  - Flying: Pidgey, Spearow, Zubat.
  - Fighting: Machop (Route 33).
  - Other: Heracross (Rock Smash in Azalea), Mareep → Flaaffy, and the Fire Starter.
- **Before Whitney (cap 33; 21 before 0.8.0):**
  - Everything above, plus Abra on Route 34 (Kadabra at 16, which turns out to be the best
    answer to Whitney's first three).
  - Mankey, Snubbull, Growlithe, Yanma, Drowzee and Ditto.
  - Scyther and Pinsir from the National Park.
  - Gastly (Ghost) from Route 32 at night, though Whitney's Scrappy Miltank still hits it.

### Bugsy (Azalea Gym), all at level 24 = cap 24 (16 before 0.8.0)

AI: `Smart Trainer / Ace Pokemon / HP Aware`. Items: Potion ×2 (unchanged from HnS).

Since 0.8.0 (`boss_teams.py`):

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Ariados Lv 24 | Black Sludge | No Guard (Insomnia before 0.11.0) | Adamant | Sticky Web, Toxic Thread, Sucker Punch, Lunge | Sticky Web and Toxic Thread lead |
| Pineco Lv 24 | Sitrus Berry | Sturdy | Relaxed | Stealth Rock, Rock Tomb, Bug Bite, Explosion | Stealth Rock; Rock Tomb punishes the Fire/Flying answers |
| Ledian Lv 24 | Light Clay | Iron Fist (Early Bird before 0.11.0) | Calm | Reflect, Light Screen, Silver Wind, Mach Punch | Screens for the rest; Mach Punch hits Rock answers |
| Butterfree Lv 24 | Silver Powder | Compound Eyes | Timid | Sleep Powder, Bug Buzz, Air Slash, Psybeam | 100%-accurate Sleep Powder |
| Yanma Lv 24 | Sitrus Berry | Speed Boost | Modest | Ancient Power, Air Slash, Bug Buzz, Protect | Speed Boost with Protect; Ancient Power hits Fire and Flying |
| Scyther Lv 24 (ace) | Eviolite | Technician | Jolly | Bug Bite, Aerial Ace, Quick Attack, Fury Cutter | Technician-boosted cleaner |

**Signature strategy:** hazards and Speed control, then Speed Boost and a bulky Technician
Scyther. Rock and Fire answers still win, but they take hits from Rock Tomb and Ancient Power.

**Iterations (emulator, 0.8.0, against the Cyndaquil line below):**
- At cap 24 Heart & Soul's team (0.7.x below) lost 19 of 20 to the naive line: its early moves
  didn't keep up with the player's.
- v1 (Focus Sash Ariados, Eviolite Pineco and Yanma, Swords Dance Scyther): the line won 2 of
  20. A Sitrus Berry for Yanma: 1 of 20. Fury Cutter for Swords Dance, as in 0.5.0's v1: 2 of 20.
- Ariados with Black Sludge and Pineco with a Sitrus Berry instead of the Focus Sash and
  Eviolite: 4 of 20 against the naive four.
- **Shipped: six Pokémon** (D30), adding Ledian back (screens) and Butterfree (Compound Eyes Sleep
  Powder). The naive line, now six with Heracross and Onix, won 2 of 24 with the Charcoal and
  **3 of 20** with the Charcoal and the first package's two Eviolites (`bugsy.emu` asks for at
  least one win and one loss in 40: 5 of 40 on mGBA, 4 of 40 on VBA-M). Over half the line's
  Pokémon fall while Butterfree is out: a team that never switches can't play around sleep. Bugsy
  is meant to be hard; a player who switches, or holds the package's Lum Berries, does better.
- **0.11.0, Emerald Imperium's abilities and movesets** (D35): Ariados and Ledian have the
  abilities their old slots now hold, No Guard and Iron Fist. The naive line's default moves at
  24 changed (Quilava's slot had Double Kick instead of Flame Wheel, Flaaffy's Flash: Mareep's line
  has no Thunder Shock any more), and it won 0 of 40, so the test now gives each Pokémon the move
  a player would have kept: Flame Wheel, Rock Tomb, Power Gem and Dual Wingbeat (both learned on
  evolving), Aerial Ace and Smack Down. With Rock Head Geodude and Onix it still lost the first
  four; with Sturdy (the Training Kit sets it) it won **10 of 40** on mGBA and 5 of 40 on VBA-M.

0.5.0 to 0.7.x (Heart & Soul's Bugsy with items, all at the cap of 16 since 0.7.0): Spinarak
(Focus Sash; Sticky Web, Night Shade, Poison Sting, Infestation), Pineco (Spikes, Rock Tomb,
Bug Bite, Protect), Ledian (Sitrus Berry; Reflect, Light Screen, Silver Wind, Mach Punch),
Scyther (Eviolite, Technician; Fury Cutter, Wing Attack, Bug Bite, Quick Attack). Its v1
Scyther had Swords Dance and one-shot Quilava, Geodude, Flaaffy and Pidgey in a row at +2.

**Results:**

| Starter | Line | Result |
|---|---|---|
| Cyndaquil | Quilava (Flame Wheel, Charcoal) / Geodude (Rock Tomb, Sturdy) / Flaaffy (Power Gem, Eviolite) / Pidgeotto (Dual Wingbeat) / Heracross (Aerial Ace) / Onix (Smack Down, Sturdy, Eviolite), all at 24 | **10 of 40 RNG samples won** against the six (0.11.0, `bugsy.emu` on mGBA; 5 of 40 on VBA-M) |
| Cyndaquil | Before 0.11.0: Quilava (Flame Wheel, Charcoal) / Geodude (Rock Throw) / Flaaffy (Thunder Shock, Eviolite) / Pidgeotto (Wing Attack) / Heracross (Aerial Ace) / Onix (Smack Down, Eviolite), all at 24 | **5 of 40** against the six (0.8.0, mGBA; 4 of 40 on VBA-M); the first four alone beat his four 4 of 20; 0.7.0 at 16 with Pidgey: 9 of 20 |
| Chikorita | Onix lead (Stealth Rock) / Pidgey / Flaaffy / Bayleef | **Win** (0.5.0, at 16) |
| Totodile | Croconaw (Bite) / Geodude / Flaaffy / Pidgey | **Win** (0.5.0, at 16) |

### Whitney (Goldenrod Gym), all at level 33 = cap 33 (21 before 0.8.0)

AI: `Smart Trainer / Ace Pokemon / HP Aware`. Items: one Potion (HnS had Super Potion + Potion).
Since 0.17.0 (the trainer standard, D59):

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Aipom Lv 33 | Eviolite | Skill Link | Jolly | Fake Out, Tail Slap, U-turn, Knock Off | Lead: Fake Out, a five-hit Tail Slap, U-turn out (one of the standard's named Eviolite species) |
| Clefable Lv 33 | Leftovers | Magic Guard | Bold | Moonblast, Thunder Wave, Encore, Soft-Boiled | Paralyses, Encores setup moves, heals |
| Furret Lv 33 | Silk Scarf | Adaptability | Jolly | Double-Edge, Sucker Punch, Ice Punch, Knock Off | Fast Adaptability attacker; Ice Punch and Knock Off for what walls Normal moves |
| Stantler Lv 33 | Sitrus Berry | Intimidate | Adamant | Body Slam, Earthquake, Megahorn, Thunder Wave | Intimidate; Earthquake for Rock and Steel types, Megahorn for Psychic and Dark ones |
| Girafarig Lv 33 | Twisted Spoon | Sap Sipper | Modest | Nasty Plot, Psychic, Hyper Voice, Thunderbolt | Special setup behind the others |
| Miltank Lv 33 (ace) | Leftovers | Thick Fat | Impish | Rollout, Defense Curl, Body Slam, Milk Drink | Heart & Soul's Rollout behind Defense Curl, healed by Milk Drink; Thick Fat halves Fire and Ice moves; the team's only EVs (252 HP) |

**Signature strategy:** Normal-type pressure around Whitney's Miltank, with coverage for the Rock,
Steel and Ghost types that wall Normal moves. The play test's six (below: the Pokémon a player has
by then, holding the starting care package's boosters), with its game plan and with a second plan
that brought Golbat for Clefable and Haunter for the Normal types, took two to four of her six in
each battle and won none of 36 on mGBA and VBA-M when her team was made (naively, none of 24 on mGBA
and one on VBA-M), so `whitney.emu` reports her battles instead of requiring a win; the autopilot
never heals or uses the Bag. She is meant to be one of the hard early battles.

From 0.8.0 to 0.16.0 her six were Clefairy (Eviolite, Encore and Charm), a Pickup Aipom, Furret,
Stantler with Hypnosis, Girafarig and a Scrappy Miltank with Attract; the notes below are from those
teams and her four before them.

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
   Since 0.7.0 the supporting three are at 21 too.
6. **0.8.0, at cap 33:** without items the naive line below won 13 of 20, so the team holds
   items again: Clefairy an Eviolite, Aipom a Silk Scarf, Stantler a Sitrus Berry, Miltank
   Leftovers. The line then won **8 of 20**. The line now gives each Pokémon a move a player at
   33 would keep: the default movesets at 33 leave Quilava without a Fire move and give Kadabra
   the physical Psycho Cut, and with those the line lost all 20.
7. **Shipped: six Pokémon** (D30), adding Furret and Girafarig; the naive line is six too, with
   Scyther and Primeape. It won **3 of 24** on mGBA and 5 of 24 on VBA-M (`whitney.emu` asks
   for at least one win and two losses in 24).
8. **0.11.0** (D35): with Emerald Imperium's learnsets Primeape has Brick Break at 33 where it had
   Cross Chop (Imperium's Primeape learns Cross Chop at 53), and the line won **2 of 24** on mGBA
   and 3 of 24 on VBA-M. Whitney's own team is unchanged.

**Results** (shipped version, autopilot, no items, all Pokémon at Lv 21; Whitney's at 18–21, before 0.7.0):

| Starter | Line | Result |
|---|---|---|
| Cyndaquil | Pidgeotto (Wing Attack) / Quilava (Flame Wheel) / Kadabra (Psybeam) / Scyther (Wing Attack) / Primeape (Brick Break; Cross Chop before 0.11.0) / Machoke (Low Sweep, Eviolite), all at 33 | **2 of 24** against her six (0.11.0, `whitney.emu` on mGBA; 3 of 24 on VBA-M; with Cross Chop in 0.8.0: 3 and 5 of 24); the first four against her four with items: 8 of 20 |
| Cyndaquil | 0.7.0 at 21: Pidgeotto (Gust) / Quilava (Flame Wheel) / Kadabra (Psybeam) / Machop (Low Sweep) | **3 of 12 RNG samples won** (`whitney.emu`, 2026-10-24). The first measurement (2026-10-23) was 3 of 5; after later code changes shifted the battle RNG, the same five samples all lost, so the test now samples twelve battles. The naive line wins about a quarter of the time. |
| Cyndaquil | Quilava or Kadabra leads with the same Pokémon | Loss (Miltank left at 1 HP in one) |
| Chikorita | Bayleef (Mega Drain) / Kadabra / Pidgeotto / Machop | **Win** (3 Pokémon left) |
| Totodile | Kadabra / Croconaw (Ice Fang) / Pidgeotto / Machop | **Win** |
| Totodile | Pidgeotto / Croconaw / Flaaffy / Machop | **Win** |
| Totodile | Croconaw / Machop / Geodude / Flaaffy | Loss |

### Gym trainers

All now have defined movesets and abilities and use `Basic Trainer` AI. Their Heart & Soul
levels (below) sat 2–4 levels under the old cap; since 0.8.0 they are mapped onto the new cap
curve at battle time (D29): the Azalea trainers' 12–14 become 17–20 (cap 24) and the Goldenrod
trainers' 18–19 become 28–29 (cap 33).

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

| Stage | Stones sold by the Goldenrod Mega Specialist (each tier keeps the ones before) |
|---|---|
| Badge 3 (Mega Ring given) | Beedrill, Pidgeot, Ampharos, Heracross, Pinsir, Audino, Lopunny, Manectric, Sableye, Banette; Emerald Imperium's Butterfree, Luxray, Roserade, Garbodor, Orbeetle, Coalossal, Flapple and Appletun (Applite), Sandaconda, Toxtricity, Centiskorch (20 stones) |
| Badge 6 | Venusaur, Charizard X/Y, Blastoise, Sceptile, Blaziken, Swampert, Gengar, Alakazam, Slowbro, Steelix, Scizor, Houndoom, Absol, Glalie, Abomasnow, Altaria, Camerupt, Sharpedo, Aggron, Medicham, Gardevoir, Gallade, Aerodactyl, Kangaskhan, Mawile; Imperium's Machamp, Kingler, Lapras, Snorlax, Torterra, Infernape, Empoleon O and D, Dusknoir, Drednaw (56) |
| Badge 8 | Gyarados, Lucario, Tyranitar, Salamence, Metagross, Garchomp; Imperium's Slaking, Grimmsnarl, Copperajah (65) |
| Johto Champion | Mewtwo X/Y, Latias, Latios, Diancie (70) |
| Side battles (D41) | Fantina (3 badges): Gengarite, Dusknoirite; Maylene (4): Lucarionite, Machampite; Crasher Wake (5): Gyaradosite, Drednawite, Laprasite; Byron (6): Metagrossite, Copperajite. Each before the shop sells it |

The first tier is mostly weaker Megas, so having a Mega around Whitney/Morty adds options
without breaking the level-cap curve. Medicham (Pure Power) and Kangaskhan (Parental Bond)
are held back to badge 6 on purpose. Staraptor's stone left the first tier in 0.12.0 (its Mega,
a Legends: Z-A one, isn't in the game: D9).

Emerald Imperium's 23 stones (D58) go to the tier of the classic stones Imperium gives at the same
place: the Winstrate family's, Wattson's and the first Trick House puzzles' to badge 3; the Fortree
creators' starters, Dawn's, the next puzzles' and the four the side battles give first to badge 6;
Wally's Slakite (Mega Slaking: 700 base stats and Comatose), Juan's Grimmite and Byron's Copperajite
to badge 8. Since the trainer standard (D59) thirteen of their Megas are on designed teams: Bruno's
Mega Machamp; the side battles' Dusknoir (Fantina), Roserade (Gardenia's second team), Luxray
(Volkner, Iono), Slaking (Larry), Toxtricity (Ryme) and Lapras (Iris); Colette's Infernape on Route
15; and the Ace Trainers' and Cooltrainers' Coalossal, Flapple, Garbodor, Kingler (Gaven's three
teams) and Snorlax, with Dusknoir, Lapras and Toxtricity again.

Boss Megas (D59), in story order: the rival from the Burned Tower (Absol; Tyranitar from the
Goldenrod Underground on), Morty (Gengar), Chuck (Heracross), Jasmine (Steelix), Pryce (Abomasnow),
Petrel (Sableye), Ariana (Kangaskhan), Eusine (Manectric), Proton in the Radio Tower (Gengar),
Archer (Houndoom), Clair (Altaria), Will (Slowbro), Koga (Beedrill), Bruno (Machamp), Karen
(Houndoom), Lance (Gyarados); Brock (Aerodactyl), Misty (Blastoise), Lt. Surge (Manectric), Erika
(Venusaur), Janine (Gengar), Sabrina (Metagross), Blaine (Camerupt), Blue (Pidgeot), Red (Charizard
Y). Every rematch and postgame boss has one too (Lance's rematch Salamence, his postgame Charizard
X), and so do the side battles from Fantina's on (not Geeta or N), Kelly and ten of Kanto's twelve
route mini-bosses, and the Ace Trainers and Cooltrainers by the standard's share: none on the teams
made for fewer than seven badges, 10 of the 19 made for seven or eight, 26 of the 37 made for after
the Johto League. Steelixite and Abomasite come with the 6th badge, so Jasmine or Pryce as the 5th
or 6th Gym uses a stone the player can't buy yet, and so do Morty's Gengarite and the Burned Tower
rival's Absolite (6th badge; Fantina gives a Gengarite at three badges), Ariana's Kangaskhanite in
the Rocket Hideout (6th badge) and the Goldenrod Underground rival's Tyranitarite (8th badge); the
others are on sale by then.

## Boss roster

Every boss from `tools/crystal_imperium/boss_teams.py` (the file has the natures, abilities and
moves). Each team's last Pokémon is its ace: on EASY it is kept back until the others are down; on
NORMAL and HARD, since 0.18.0, it comes in whenever it is the best choice (D60). Since 0.8.0 every
Gym Leader and the big story bosses have six (D30), but for Ariana in the Rocket Hideout, who has
three since 0.17.0: she battles beside Grunt 23 in a tag battle, where each opponent brings its
first three (D59, `tag_battle`). Healing items: Potions for Bugsy and Whitney, Super Potions for
Proton in Slowpoke Well and the rival in Azalea and at the Burned Tower, two Hyper Potions for Morty
and the 5th-Gym versions, two Full Restores for everyone after that (three for the postgame
rematches at 100) except the Kimono Girls, who carry none, and Red, who carries four; Falkner and
Elder Li carry none. The rival's team follows the player's starter choice; the Cyndaquil versions
are shown.

| Boss | Level (every Pokémon) | Team (held item) |
|---|---|---|
| Falkner | 15 | Murkrow (Eviolite), Natu (Eviolite), Fletchling (Oran Berry), Trumbeak (Muscle Band), Squawkabilly (Silk Scarf), Pidgeotto (Sitrus Berry) |
| Proton (Slowpoke Well) | 24 | Koffing (Eviolite), Golbat (Sharp Beak), Slowpoke (Sitrus Berry), Grimer Alola (Eviolite), Raticate (Flame Orb), Houndoom (Charcoal) |
| Bugsy | 24 | Ariados (Black Sludge), Pineco (Sitrus Berry), Ledian (Light Clay), Butterfree (Silver Powder), Yanma (Sitrus Berry), Scyther (Eviolite) |
| Rival 2 (Azalea; Cyndaquil version shown) | 33 | Pupitar (Focus Sash), Golbat (Eviolite), Weavile (Never Melt Ice), Gengar (Black Sludge), Magnezone (Leftovers), Quilava (Charcoal) |
| Whitney (Heart & Soul's Miltank and Clefairy, now a Clefable, and four more) | 33 | Aipom (Eviolite), Clefable (Leftovers), Furret (Silk Scarf), Stantler (Sitrus Berry), Girafarig (Twisted Spoon), Miltank (Leftovers) |
| Rival 3 (Burned Tower) | 42 | Pupitar (Eviolite), Crobat (Sharp Beak), Weavile (Life Orb), Gengar (Focus Sash), Absol (Absolite), Typhlosion (Charcoal) |
| Morty | 42 | Marowak Alola (Thick Club), Sableye (Sitrus Berry), Misdreavus (Eviolite), Drifblim (Sitrus Berry), Mimikyu (Life Orb), Gengar (Gengarite) |
| Chuck (as the 5th Gym) | 50 | Hitmontop (Rocky Helmet), Breloom (Life Orb), Hawlucha (Sitrus Berry), Annihilape (Leftovers), Poliwrath (Sitrus Berry), Heracross (Heracronite) |
| Chuck (as the 6th Gym) | 58 | Iron Hands (Booster Energy), Breloom (Life Orb), Hawlucha (Sitrus Berry), Annihilape (Leftovers), Poliwrath (Sitrus Berry), Heracross (Heracronite) |
| Chuck (as the 7th Gym) | 66 | Iron Hands (Booster Energy), Breloom (Life Orb), Kommo-o (Life Orb), Annihilape (Leftovers), Poliwrath (Sitrus Berry), Heracross (Heracronite) |
| Jasmine (as the 5th Gym) | 50 | Skarmory (Rocky Helmet), Magnezone (Air Balloon), Bronzong (Leftovers), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Jasmine (as the 6th Gym) | 58 | Skarmory (Rocky Helmet), Magnezone (Air Balloon), Iron Treads (Booster Energy), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Jasmine (as the 7th Gym) | 66 | Skarmory (Rocky Helmet), Magnezone (Air Balloon), Iron Treads (Booster Energy), Kingambit (Black Glasses), Scizor (Metal Coat), Steelix (Steelixite) |
| Pryce (as the 5th Gym) | 50 | Cloyster (Focus Sash), Dewgong (Leftovers), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Pryce (as the 6th Gym) | 58 | Cloyster (Focus Sash), Iron Bundle (Booster Energy), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Pryce (as the 7th Gym) | 66 | Cloyster (Focus Sash), Iron Bundle (Booster Energy), Baxcalibur (Life Orb), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Petrel (Rocket Hideout) | 50 (58 or 66 with five or six badges) | Forretress (Leftovers), Weezing (Black Sludge), Golbat (Eviolite), Zoroark (Life Orb), Drapion (Scope Lens), Sableye (Sablenite) |
| Ariana (Rocket Hideout) | 50 (58 or 66 with five or six badges) | Persian Alola (Sitrus Berry), Arbok (Black Sludge), Kangaskhan (Kangaskhanite) |
| Eusine (Cianwood) | 50 | Politoed (Damp Rock), Electrode (Focus Sash), Hypno (Leftovers), Gengar (Black Sludge), Starmie (Life Orb), Manectric (Manectite) |
| Proton (Radio Tower) | 75 | Rhydon (Eviolite), Weezing (Rocky Helmet), Muk (Assault Vest), Nidoking (Life Orb), Toxicroak (Black Sludge), Gengar (Gengarite) |
| Petrel (Radio Tower) | 75 | Forretress (Rocky Helmet), Weezing Galar (Black Sludge), Toxapex (Leftovers), Zoroark (Focus Sash), Drapion (Black Glasses), Sableye (Sablenite) |
| Ariana (Radio Tower) | 75 | Persian Alola (Focus Sash), Arbok (Black Sludge), Skuntank (Assault Vest), Gyarados (Leftovers), Honchkrow (Scope Lens), Kangaskhan (Kangaskhanite) |
| Archer (Radio Tower) | 75 | Kingambit (Leftovers), Tauros (Choice Band), Porygon Z (Choice Scarf), Crawdaunt (Life Orb), Slowbro (Heavy-Duty Boots), Houndoom (Houndoominite) |
| Rival 4 (Goldenrod Underground) | 75 | Crobat (Black Sludge), Weavile (Choice Band), Alakazam (Life Orb), Gengar (Choice Specs), Tyranitar (Tyranitarite), Typhlosion (Choice Scarf) |
| Clair | 75 | Druddigon (Rocky Helmet), Flygon (Choice Scarf), Dragalge (Black Sludge), Altaria (Altarianite), Kommo O (Life Orb), Kingdra (Wacan Berry) |
| Rival 5 (Victory Road) | 85 | Tyranitar (Tyranitarite), Crobat (Heavy-Duty Boots), Weavile (Life Orb), Gengar (Black Sludge), Ursaluna (Flame Orb), Typhlosion (Choice Specs) |
| Zuki | 85 | Umbreon (Leftovers) |
| Naoko | 85 | Espeon (Leftovers) |
| Miki | 85 | Flareon (Toxic Orb) |
| Sayo | 85 | Jolteon (Leftovers) |
| Kuni | 85 | Vaporeon (Leftovers) |
| Will | 85 | Xatu (Light Clay), Bronzong (Mental Herb), Exeggutor (Sitrus Berry), Cresselia (Leftovers), Farigiraf (Life Orb), Slowbro (Slowbronite) |
| Koga | 85 | Crobat (Black Sludge), Toxapex (Rocky Helmet), Muk Alola (Assault Vest), Venomoth (Focus Sash), Munkidori (Choice Specs), Beedrill (Beedrillite) |
| Bruno | 85 | Hitmontop (Rocky Helmet), Steelix (Leftovers), Conkeldurr (Flame Orb), Lucario (Life Orb), Terrakion (Choice Scarf), Machamp (Machampite) |
| Karen | 85 | Umbreon (Leftovers), Vileplume (Black Sludge), Honchkrow (Choice Band), Gengar (Focus Sash), Darkrai (Life Orb), Houndoom (Houndoominite) |
| Lance | 85 | Gyarados (Gyaradosite), Aerodactyl (Focus Sash), Charizard (Heavy-Duty Boots), Raging Bolt (Booster Energy), Latios (Soul Dew), Dragonite (Lum Berry) |
| Brock | 90 | Gigalith (Smooth Rock), Omastar (White Herb), Kabutops (Life Orb), Golem (Weakness Policy), Lycanroc Midday (Focus Sash), Aerodactyl (Aerodactylite) |
| Misty | 90 | Pelipper (Damp Rock), Golduck (Life Orb), Lapras (Leftovers), Milotic (Leftovers), Blastoise (Blastoisinite), Starmie (Wise Glasses) |
| Lt. Surge | 90 | Electrode (Focus Sash), Magnezone (Choice Specs), Lanturn (Leftovers), Electivire (Life Orb), Manectric (Manectite), Raichu (Magnet) |
| Erika | 90 | Whimsicott (Heat Rock), Jumpluff (Flying Gem), Victreebel (Life Orb), Tangrowth (Assault Vest), Bellossom (Sitrus Berry), Venusaur (Venusaurite) |
| Janine | 90 | Weezing (Black Sludge), Nidoqueen (Life Orb), Muk (Leftovers), Crobat (Sharp Beak), Venomoth (Focus Sash), Gengar (Gengarite) |
| Sabrina | 90 | Mr Mime (Light Clay), Wobbuffet (Sitrus Berry), Slowbro (Leftovers), Espeon (Life Orb), Alakazam (Twisted Spoon), Metagross (Metagrossite) |
| Blaine | 90 | Torkoal (Heat Rock), Rapidash (Life Orb), Magmortar (Expert Belt), Volcarona (Charcoal), Arcanine Hisui (Choice Band), Camerupt (Cameruptite) |
| Blue | 90 | Rhyperior (Rocky Helmet), Exeggutor (Sitrus Berry), Gyarados (Lum Berry), Arcanine (Life Orb), Machamp (Assault Vest), Pidgeot (Pidgeotite) |
| Red | 100 (rematch too) | Pikachu (Light Ball), Espeon (Life Orb), Snorlax (Chesto Berry), Venusaur (Life Orb), Blastoise (White Herb), Charizard (Charizardite Y); EVs on all six |

Every Pokémon is at the level shown, the NORMAL cap of the earliest point the battle can happen
(with HARD level caps, the HARD cap there). A boss fought later is raised to the player's cap then
(D21): the Kanto Gym teams, which are also the Fighting Dojo rematches, are at 100 after the Kanto
League, like every Heart & Soul rematch then.

## Side battles

Optional battles, one each (D41), every Pokémon at the level cap of the battle's stage like the
bosses above. Bag items: none for Candice, a Potion for Gardenia's first team, two Hyper Potions at
3 and 4 badges, two Full Restores from 5 badges and in Kanto, three for the postgame's visitors at
100 (Red keeps four, and the only EVs under Minimal Grinding). One Mega Evolution from the 3rd
badge's stage on (Fantina's Mega Dusknoir first; not Geeta or N), and EV spreads from it through the
Johto League, as the bosses have (D59).

| Trainer | Where | Level (every Pokémon) | Team (held item) |
|---|---|---|---|
| Candice | Violet City Trainer School | 15 | Snover (Icy Rock), Sneasel (Never Melt Ice), Snorunt (Eviolite), Cubchoo (Muscle Band), Meditite (Eviolite), Cryogonal (Leftovers) |
| Gardenia | Ilex Forest | 33 | Whimsicott (Heat Rock), Cherrim (Miracle Seed), Bellossom (Leftovers), Grotle (Eviolite), Dolliv (Sitrus Berry), Roserade (Black Sludge) |
| Gardenia (second team) | Ilex Forest (4 badges) | 50 | Sudowoodo (Sitrus Berry), Tangrowth (Assault Vest), Arboliva (Leftovers), Torterra (White Herb), Ferrothorn (Rocky Helmet), Roserade (Roseradite) |
| Fantina | Ecruteak City | 42 | Cofagrigus (Mental Herb), Golurk (Life Orb), Cursola (Spell Tag), Trevenant (Sitrus Berry), Mismagius (Wise Glasses), Dusknoir (Dusknoirite) |
| Maylene | Cianwood City | 50 | Medicham (Sitrus Berry), Mienshao (Life Orb), Poliwrath (Mystic Water), Toxicroak (Black Sludge), Pawmot (Expert Belt), Lucario (Lucarionite) |
| Crasher Wake | Lake of Rage | 58 | Politoed (Damp Rock), Floatzel (Life Orb), Quagsire (Leftovers), Toedscruel (Sitrus Berry), Barraskewda (Choice Band), Gyarados (Gyaradosite) |
| Byron | Olivine City | 66 | Bastiodon (Leftovers), Empoleon (Assault Vest), Excadrill (Focus Sash), Magnezone (Choice Specs), Corviknight (Rocky Helmet), Aggron (Aggronite) |
| Roark | Route 44 | 75 | Glimmora (Focus Sash), Garganacl (Leftovers), Lycanroc Dusk (Life Orb), Kleavor (Lum Berry), Rampardos (Choice Scarf), Aerodactyl (Aerodactylite) |
| Volkner | Indigo Plateau | 85 | Jolteon (Life Orb), Raichu Alola (Focus Sash), Manectric (Life Orb), Rotom Wash (Rocky Helmet), Electivire (Expert Belt), Luxray (Luxrite) |
| Katy | Pewter City | 90 | Ribombee (Focus Sash), Lokix (Life Orb), Volcarona (Heavy-Duty Boots), Golisopod (Assault Vest), Ursaluna (Flame Orb), Pinsir (Pinsirite) |
| Brassius | Route 25 | 90 | Brambleghast (Focus Sash), Meowscarada (Choice Band), Scovillain (Life Orb), Tsareena (Sitrus Berry), Rillaboom (Miracle Seed), Sceptile (Sceptilite) |
| Iono | Lavender Town | 90 | Galvantula (Focus Sash), Kilowattrel (Heavy-Duty Boots), Bellibolt (Leftovers), Electrode Hisui (Life Orb), Mismagius (Spell Tag), Luxray (Luxrite) |
| Kofu | Vermilion City | 90 | Wugtrio (Focus Sash), Veluza (Life Orb), Crabominable (Sitrus Berry), Dondozo (Chesto Berry), Clawitzer (Choice Specs), Sharpedo (Sharpedonite) |
| Larry | Viridian City | 90 | Komala (Assault Vest), Dudunsparce (Leftovers), Staraptor (Choice Scarf), Flamigo (Sharp Beak), Bewear (Sitrus Berry), Slaking (Slakite) |
| Ryme | Celadon City | 90 | Mimikyu (Life Orb), Banette (Spell Tag), Dragapult (Focus Sash), Gholdengo (Choice Specs), Houndstone (Choice Band), Toxtricity (Toxtricitite) |
| Tulip | Saffron City | 90 | Farigiraf (Sitrus Berry), Gardevoir (Leftovers), Espathra (Life Orb), Hatterene (Expert Belt), Florges (Leftovers), Gallade (Galladite) |
| Grusha | Cinnabar Island | 90 | Ninetales Alola (Light Clay), Sandslash Alola (Leftovers), Frosmoth (Heavy-Duty Boots), Beartic (Life Orb), Cetitan (Sitrus Berry), Altaria (Altarianite) |
| Cynthia | Ruins of Alph | 100 | Spiritomb (Leftovers), Roserade (Focus Sash), Togekiss (Leftovers), Milotic (Sitrus Berry), Garchomp (Loaded Dice), Lucario (Lucarionite) |
| Iris | Blackthorn City | 100 | Archeops (Focus Sash), Lapras (Laprasite), Hydreigon (Choice Specs), Aggron (Choice Band), Dragonite (Weakness Policy), Haxorus (Lum Berry) |
| Geeta | Route 28 | 100 | Glimmora (Focus Sash), Espathra (Life Orb), Gogoat (Leftovers), Veluza (Sitrus Berry), Avalugg (Rocky Helmet), Kingambit (Black Glasses) |
| N | National Park | 100 | Zoroark (Life Orb), Carracosta (White Herb), Vanilluxe (Icy Rock), Archeops (Choice Scarf), Klinklang (Leftovers), Zekrom (Life Orb) |
| Cyrus | Mahogany Town | 100 | Crobat (Black Sludge), Honchkrow (Life Orb), Gyarados (Lum Berry), Weavile (Razor Claw), Sneasler (Focus Sash), Houndoom (Houndoominite) |
| Wallace | Cherrygrove City | 100 | Pelipper (Damp Rock), Ludicolo (Life Orb), Starmie (Choice Specs), Whiscash (Leftovers), Swampert (Swampertite), Milotic (Leftovers) |
| Maxie | Fuchsia City | 100 | Torkoal (Heat Rock), Mightyena (Choice Band), Weezing (Black Sludge), Arcanine (Life Orb), Blaziken (Focus Sash), Camerupt (Cameruptite) |
| Archie | Cerulean City | 100 | Pelipper (Damp Rock), Tentacruel (Black Sludge), Muk (Black Sludge), Crobat (Life Orb), Crawdaunt (Choice Band), Sharpedo (Sharpedonite) |
| Wally | Pallet Town | 100 | Altaria (Leftovers), Delcatty (Silk Scarf), Roserade (Focus Sash), Magnezone (Choice Specs), Flygon (Choice Scarf), Gallade (Galladite) |


## Route mini-bosses

Since 0.8.0 one trainer on most routes has a competitive team at the level cap, like Emerald
Imperium's route mini-bosses (D30). Each holds an item, and has a nature, an ability and four chosen
moves on every Pokémon (`ROUTE_BOSSES` in `boss_teams.py`); the boss AI. The level shown is the
NORMAL cap of the earliest point the route can be reached; met later, a mini-boss is at the player's
cap. They carry no healing items, which keeps them below the Gym Leaders. Since the trainer standard
(D59) their teams follow it as the bosses' do (EV spreads from the 3rd badge; from the 5th, a setup
move or priority and a pivot or hazards), and Kelly and ten of Kanto's twelve Mega Evolve: the
standard's share for mini-bosses and Ace Trainers (one team in three from the 5th badge, two in
three from the 8th and in Kanto).

Against the prepared six at the cap played naively (one move per Pokémon, never switching;
`route_bosses`), the Johto mini-bosses lost 13 of 16 battles on mGBA (Greg, Blake and Kelly won) and
the Kanto ones won 10 of 12 (Dwayne and Tim lost), about as the Kanto Gym Leaders do against that
line (`bosses_m5`). On VBA-M, whose battle RNG differs, the Johto ones lost 13 of 16 too (Jake,
Blake and Kelly won) and the Kanto ones won 9 of 12. A player who switches and plays to matchups
does better (0.17.0's teams; TESTING.md has every count).

| Route | Trainer | Level | Team (held item) |
|---|---|---|---|
| 30 | Youngster Mikey | 15 | Pichu (Eviolite), Furret (Sitrus Berry), Rattata (Flame Orb) |
| 32 | Camper Roland | 15 | Geodude (Eviolite), Flaaffy (Eviolite), Bellsprout (Salac Berry) |
| 34 | Cooltrainer Kate | 24 | Granbull (Sitrus Berry), Shellder (Eviolite), Growlithe (Charcoal), Kadabra (Eviolite) |
| 35 | Bird Keeper Bryan | 24 | Swablu (Eviolite), Farfetchd (Leek), Fearow (Sharp Beak), Noctowl (Sitrus Berry) |
| 37 | Psychic M Greg | 33 | Xatu (Light Clay), Gallade (Focus Sash), Grumpig (Leftovers), Espeon (Twisted Spoon) |
| 38 | Beauty Valerie | 33 | Togetic (Eviolite), Granbull (Sitrus Berry), Azumarill (Choice Band), Clefable (Leftovers) |
| 39 | Sailor Eugene | 33 | Tentacruel (Black Sludge), Poliwrath (Leftovers), Machamp (Expert Belt), Kingler (Life Orb) |
| 40 | Swimmer M Simon | 42 | Pelipper (Damp Rock), Floatzel (Life Orb), Seaking (Mystic Water), Golduck (Wise Glasses), Quagsire (Leftovers) |
| 41 | Swimmer M George | 42 | Mantine (Leftovers), Barraskewda (Life Orb), Lanturn (Assault Vest), Starmie (Expert Belt), Kingdra (Choice Specs) |
| 42 | Hiker Benjamin | 42 | Hippowdon (Smooth Rock), Excadrill (Life Orb), Rhydon (Eviolite), Steelix (Leftovers), Sudowoodo (Choice Band) |
| 43 | Pokemaniac Ben | 42 | Aerodactyl (Focus Sash), Kangaskhan (Silk Scarf), Slowbro (Leftovers), Lickilicky (Sitrus Berry), Dragonair (Eviolite) |
| 47 | Hiker Devin | 42 | Golem (Sitrus Berry), Gligar (Eviolite), Aggron (Life Orb), Marowak (Thick Club), Hariyama (Flame Orb) |
| 44 | Cooltrainer Cybil | 50 | Ninetales (Heat Rock), Jumpluff (Leftovers), Butterfree (Focus Sash), Arcanine (Choice Band), Bellossom (Life Orb) |
| 26 | Cooltrainer Jake | 50 | Tangrowth (Rocky Helmet), Electivire (Life Orb), Magmortar (Expert Belt), Togekiss (Leftovers), Kingdra (Choice Specs), Gyarados (Sitrus Berry) |
| 27 | Cooltrainer Blake | 50 | Scizor (Choice Band), Starmie (Expert Belt), Ampharos (Leftovers), Houndoom (Life Orb), Heracross (Choice Scarf), Nidoking (Life Orb) |
| 45 | Cooltrainer Kelly | 66 | Froslass (Focus Sash), Roserade (Black Sludge), Azumarill (Sitrus Berry), Gardevoir (Choice Scarf), Milotic (Leftovers), Lopunny (Lopunnite) |
| 1 | Cooltrainer Quinn | 90 | Hippowdon (Leftovers), Excadrill (Life Orb), Gliscor (Toxic Orb), Sandslash (Focus Sash), Tyranitar (Choice Band), Garchomp (Garchompite) |
| 3 | Firebreather Otis | 90 | Ninetales (Heat Rock), Houndoom (Black Glasses), Chandelure (Choice Specs), Magmortar (Expert Belt), Volcarona (Heavy-Duty Boots), Charizard (Charizardite Y) |
| 8 | Biker Dwayne | 90 | Overqwil (Rocky Helmet), Muk Alola (Black Sludge), Scrafty (Leftovers), Crobat (Sharp Beak), Krookodile (Choice Scarf), Hydreigon (Life Orb) |
| 9 | Hiker Tim | 90 | Steelix (Leftovers), Donphan (Leftovers), Golem (Custap Berry), Mamoswine (Life Orb), Rhyperior (Weakness Policy), Aggron (Aggronite) |
| 10 | Pokefan Robert | 90 | Clefable (Leftovers), Azumarill (Sitrus Berry), Mimikyu (Life Orb), Togekiss (Heavy-Duty Boots), Sylveon (Throat Spray), Mawile (Mawilite) |
| 11 | Psychic M Herman | 90 | Tapu Lele (Terrain Extender), Espathra (Leftovers), Alakazam (Life Orb), Slowking (Leftovers), Metagross (Weakness Policy), Gallade (Galladite) |
| 12 | Fisherman Stephen | 90 | Politoed (Damp Rock), Kingdra (Life Orb), Ludicolo (Choice Specs), Seismitoad (Leftovers), Lanturn (Leftovers), Gyarados (Gyaradosite) |
| 13 | Juggler Bret | 90 | Klefki (Light Clay), Rotom Wash (Leftovers), Mr. Mime (Life Orb), Chandelure (Choice Scarf), Magnezone (Choice Specs), Sableye (Sablenite) |
| 15 | Expert Colette | 90 | Hawlucha (White Herb), Breloom (Focus Sash), Machamp (Sitrus Berry), Toxicroak (Life Orb), Lucario (Life Orb), Infernape (Infernapite) |
| 18 | Bird Keeper Boris | 90 | Skarmory (Rocky Helmet), Staraptor (Life Orb), Talonflame (Sharp Beak), Togekiss (Choice Scarf), Dragonite (Lum Berry), Altaria (Altarianite) |
| 20 | Swimmer F Lori | 90 | Araquanid (Sitrus Berry), Greninja (Life Orb), Vaporeon (Leftovers), Samurott (Choice Band), Primarina (Life Orb), Milotic (Flame Orb) |
| 25 | Cooltrainer Kevin | 90 | Ferrothorn (Rocky Helmet), Gengar (Focus Sash), Crawdaunt (Choice Band), Kommo-o (Life Orb), Salamence (Life Orb), Scizor (Scizorite) |

### Notes from the play tests

The naive autopilot (no switching, one move per Pokémon) and the game-plan autopilot both play
worse than a person, so their win counts are lower bounds. Since 0.7.0 every boss Pokémon is at
the cap, and the test teams hold items from the care packages the player has by then (before,
no items). The regression's counts for both emulators are in TESTING.md.

- **Emerald Imperium's AI** (0.18.0, D60) made most of the same battles harder for the test teams.
  Over the 15 sampled battles from Bugsy to Red they won 37.6% (mGBA) and 42.5% (VBA-M) of the
  time, against 44.6% on both with 0.17.0's AI; they won less often against 9 trainers and more often
  against 5. By battle (mGBA, then VBA-M; 0.17.0's counts in brackets):
  - worse: Lance 10 and 9 of 24 (16 and 17), Will 5 and 6 of 8 (8 and 8), Morty 16 and 13 of 24
    (19 and 18), Pryce 5 and 8 of 16 (6 and 5 of 8: his Mega Abomasnow, no longer kept back as his
    ace, now comes in second, so his six gets 16 tries), and Bugsy's naive six 11 and 10 of 40 (17
    and 11);
  - about as before (within two wins over both emulators): Chuck, Bruno, Karen, Jasmine and
    Whitney;
  - better: Clair 5 and 10 of 16 (5 and 5), Blue 7 and 10 of 16 (7 and 5), Red 10 and 8 of 24 (7
    and 7) and Koga 7 and 7 of 8 (4 and 7).

  Only Lance's and Will's changes are beyond these samples' spread. The autopilot plays a fixed
  plan, so the AI-vs-AI measurement (D60), whose player switches and chooses, is the fairer test
  of the AI.

- **The trainer standard** (0.17.0, D59). Whitney's six, naive and with two game plans, won 0 of 36
  battles on mGBA and 1 on VBA-M, so her battles are reported, not judged. Koga, Morty and Jasmine
  are fought with game plans now: played naively the prepared six lost all 6 to Koga, won 2 and 0 of
  24 against Morty's Mega Gengar and 3 and 1 of 16 against Jasmine, whose Air Balloon Magnezone,
  Levitate Bronzong and Skarmory its Ground moves miss; with the plans it won 4 and 7 of 8, 19 and
  18 of 24, and 4 and 5 of 16 (mGBA, VBA-M). Karen (Darkrai, Mega Houndoom) was beaten 3 and 4 times
  in 12 and gets 18 tries (7 and 8 wins). Blue's Dragon Dance Gyarados swept the six built for him
  from full health, so the six holds care-package items, Mega Evolves Ampharos and brings a
  Rotom-Wash, which the Gyarados can't sweep, and an Intimidate Staraptor and a Garchomp: with a
  Gardevoir and a Lucario in their place it won 1 and 2 of 24 (Machamp's Knock Off and Stone Edge
  met Blue's switch-ins), with them 7 and 5 of 16. Red was beaten 7 times in 24 on both emulators.

- **Johto Gyms at the cap** (0.7.0): the naive lines lost more. Bugsy's naive four won 5 of 20
  without items, 9 and 11 of 20 with the first package's Charcoal on Quilava, and every try with
  Charcoal, two Eviolites and a Focus Sash; the test keeps the Charcoal. Whitney's naive four,
  Machop holding an Eviolite, won 5 and 4 of 20 (mGBA, VBA-M), so her test takes 24 samples. The
  prepared six with items still beats Morty and Jasmine most of the time and Clair about half
  the time; against Pryce (Shell Smash Cloyster, Mega Abomasnow in snow) it won once in 16, so
  Pryce, like Chuck, is fought by a six built for him with a game plan: Assault Vest Magnezone
  for Cloyster, Tyranitar for Jynx, Focus Sash Lucario for Weavile, Gyarados for Mamoswine and
  Choice Band Arcanine and Metagross for Abomasnow. It won 13 and 16 of 16.

- **The Elite Four** (`bosses_e4`, cap 56): with every Pokémon at 56 (0.7.0), the planned six
  without items lost all 8 tries to Will on mGBA; holding items from the first eight packages
  (no Choice items, since a plan changes moves) the sixes beat Will 9 and 7 times in 16, Bruno
  10 and 9, and Lance 6 and 9 times in 24. Before 0.7.0: the prepared six beats Koga most of the time
  played naively. Naive play rarely beat Will (3 of 60 tries with the prepared six, on two ROM
  builds) or Lance (13 of 60 with a six built for him), and its results against Bruno and Karen
  swung between the emulators (5 and 0 of 6; 2 and 0 of 6). Played with a game plan, sixes
  built for them beat Will 3 times in 6, Bruno 5 in 6, Karen 3 in 6 and Lance 3 in 12, so the
  test gave them 8, 6, 8 and 24 tries (since 0.7.0: 8, 12, 12 and 24).
- **Lance** first had three Dragon Dance users (Mega Gyarados, Salamence, Dragonite): the
  all-round six lost all six tries on mGBA. With only Dragonite setting up, his Charizard still
  Roosted behind two Full Restores, and three different sixes built for him lost all nine tries
  on VBA-M. Now Charizard attacks (Dragon Pulse instead of Roost), and a six built for him wins
  2 / 1 times in six. He is still the wall of the Johto League: bring answers to Dragons and
  Mega Gyarados.
- **Bruno's and Blue's Machamp** have Close Combat instead of No Guard Dynamic Punch, which
  confused a non-switching team every turn (Blue beat every team in all six tries before).
- **Kanto** is level 70 everywhere, so the leaders can be taken in any order. In one try each
  at the cap, the prepared six beat Lt. Surge and Erika on both emulators, Sabrina on mGBA and
  Blaine on VBA-M, and lost to the others. A six built for Blue beat him once in 12 tries
  played naively and 10 times in 12 with a game plan.
- **Red** is the hardest battle (D27). With all six at 100 (0.7.0; 96–100 before) the planned
  six with items won 5 and 2 times in 12 (mGBA, VBA-M), so the test gives it 24 tries. Before
  0.7.0: every team at level 100 played naively lost: 30 tries
  with five different sixes, among them six legendary Dragons, and 24 more against weaker
  versions of Red (two Full Restores, or no prediction AI). A game plan without held items lost
  12 of 12. A six with held items and a Mega played with a game plan (Life Orb Garchomp for
  Pikachu, Kingambit for Espeon, Flame Orb Conkeldurr for Snorlax, Talonflame with Safety
  Goggles against Sleep Powder for Venusaur, Mega Ampharos for Blastoise, Assault Vest
  Tyranitar for Charizard) beat him 4 times in 12; before Talonflame had the goggles, 6 times
  in 48. With two Full Restores and no EVs the plan without items won 2 of 6 and the naive six
  1 of 6, against none of 6 each with the EVs: the EVs are what set him apart.
