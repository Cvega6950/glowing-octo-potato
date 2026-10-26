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
   except Red's, which keep their EVs (D27).
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

## Progression snapshot

| Segment | Level cap | Status |
|---|---|---|
| Early Johto (Falkner, Bugsy, Whitney; Proton, rival 2–3) | 15 / 24 / 33 | Reworked and play-tested (`falkner`, `bugsy`, `whitney`, `bosses_m3`) |
| Midgame Johto (Morty, Chuck, Jasmine, Pryce; Rocket Hideout) | 42 / 50 / 58 / 66 | Reworked; Chuck, Jasmine and Pryce in three versions for any order (`bosses_m3`, `bosses_m4`) |
| Late Johto (Radio Tower, rival 4, Clair, Kimono Girls, Victory Road) | 75 / 85 | Reworked (`bosses_m3`, `bosses_m4`) |
| Elite Four / Lance | 85 → 90 after the title | Reworked (`bosses_e4`) |
| Kanto leaders, Blue | 90 | Reworked (`bosses_m5`) |
| Red (Mt. Silver) | after the Kanto League, uncapped; 100 | Reworked: the hardest battle (`red`) |
| Rematches and other postgame battles | 90 / uncapped (100) | HnS teams with the smart AI, at the cap |

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
| Elder Li (Sprout Tower) | Gastly, Hoppip, Bellsprout @ Oran Berry, all 15 (0.7.x: 11; 0.6.0: 8, 8, 10) | Mini-boss: Mean Look + Hypnosis trap, Growth sweeper ace |

### Falkner (Violet Gym), all at level 15 = cap 15 (11 before 0.8.0)

AI: `Smart Trainer / Ace Pokemon / HP Aware`. All Pokémon have 31 IVs.

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Pidgey Lv 15 | Oran Berry | Big Pecks | Timid | Tailwind, Gust, Sand Attack, Quick Attack | Speed control + accuracy chip lead |
| Natu Lv 15 (0.8.0) | Eviolite | Magic Bounce | Bold | Night Shade, Peck, Confuse Ray, Wish | Bounces status back; Night Shade chip |
| Fletchling Lv 15 (0.8.0) | Eviolite | Gale Wings | Jolly | Acrobatics, Quick Attack, Agility, Flail | Priority Flying moves at full HP |
| Murkrow Lv 15 (0.8.0) | Eviolite | Prankster | Calm | Foul Play, Peck, Thunder Wave, Haze | Priority Thunder Wave; Haze undoes set-up |
| Rookidee Lv 15 | Eviolite (0.8.0) | Keen Eye | Adamant | Hone Claws, Power Trip, Peck, Rock Smash | Set-up threat; Rock Smash punishes Rock answers (0.5.0: was Steel Wing, which Rookidee cannot learn) |
| Noctowl Lv 15 (ace) | Sitrus Berry | Tinted Lens | Modest | Hypnosis, Air Cutter, Reflect, Mud-Slap | Tinted Lens beats resists; Reflect blunts Rollout; Mud-Slap hits Electric/Rock |

**Signature strategy:** a Tailwind lead into a Hone Claws/Power Trip set-up. The ace
punishes the classic Rock/Electric answers instead of folding to them.

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

| Pokémon | Item | Ability | Nature | Moves | Job |
|---|---|---|---|---|---|
| Clefairy Lv 33 | Eviolite (0.8.0) | Magic Guard | Bold | Double Slap, Metronome, Encore, Charm | Disruption: Encore locks set-up, Charm blunts physical attackers |
| Aipom Lv 33 | Silk Scarf (0.8.0) | Pickup | Jolly | Fake Out, Double Hit, U-turn, Astonish | Pivot that chips and keeps momentum |
| Furret Lv 33 (0.8.0) | Sitrus Berry | Frisk | Jolly | Double-Edge, Sucker Punch, U-turn, Coil | Fast physical attacker |
| Stantler Lv 33 | Sitrus Berry (0.8.0) | Intimidate | Adamant | Hypnosis, Stomp, Zen Headbutt, Take Down | Intimidate weakens the Fighting answer; one sleeper under Sleep Clause |
| Girafarig Lv 33 (0.8.0) | Twisted Spoon | Inner Focus | Modest | Psybeam, Shadow Ball, Thunderbolt, Nasty Plot | Special set-up; Shadow Ball hits Ghosts and Psychics |
| Miltank Lv 33 (ace) | Leftovers (0.8.0) | Scrappy | Impish | Rollout, Body Slam, Milk Drink, Attract | The classic: Rollout snowball, Attract, Milk Drink; Scrappy hits Ghosts |

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

| Stage | Stones sold by the Goldenrod Mega Specialist |
|---|---|
| Badge 3 (Mega Ring given) | Beedrill, Pidgeot, Ampharos, Heracross, Pinsir, Audino, Lopunny, Manectric, Sableye, Banette, Staraptor |
| Badge 6 | Venusaur, Charizard X/Y, Blastoise, Sceptile, Blaziken, Swampert, Gengar, Alakazam, Slowbro, Steelix, Scizor, Houndoom, Absol, Glalie, Abomasnow, Altaria, Camerupt, Sharpedo, Aggron, Medicham, Gardevoir, Gallade, Aerodactyl, Kangaskhan, Mawile |
| Badge 8 | Gyarados, Lucario, Tyranitar, Salamence, Metagross, Garchomp |
| Johto Champion | Mewtwo X/Y, Latias, Latios, Diancie |

The first tier is mostly weaker Megas, so having a Mega around Whitney/Morty adds options
without breaking the level-cap curve. Medicham (Pure Power) and Kangaskhan (Parental Bond)
are held back to badge 6 on purpose.

Boss Megas: Chuck (Heracross), Jasmine (Steelix), Pryce (Abomasnow), Clair (Altaria), Archer
(Houndoom), the rival on Victory Road (Tyranitar), Will (Alakazam), Koga (Beedrill), Bruno
(Lucario), Karen (Absol), Lance (Gyarados); Brock (Aerodactyl), Misty (Blastoise), Lt. Surge
(Manectric), Erika (Venusaur), Janine (Gengar), Sabrina (Metagross), Blaine (Camerupt), Blue
(Pidgeot), Red (Charizard Y); from Heart & Soul's rematch teams, Lance's rematch (Salamence)
and postgame battle (Charizard X). Steelixite and Abomasite come with the 6th badge, so Jasmine
or Pryce as the 5th Gym uses a stone the player can't buy yet; the others are on sale by then.

## Boss roster

Every boss from `tools/crystal_imperium/boss_teams.py` (the file has the natures, abilities and
moves). Each team's last Pokémon is its ace, kept back until the others are down. Since 0.8.0
every Gym Leader and the big story bosses have six (D30). Healing items: Potions for Bugsy and
Whitney, Super Potions for Proton in Slowpoke Well and the rival in Azalea and at the Burned
Tower, two Hyper Potions for Morty and the 5th-Gym versions, two Full Restores for everyone after
that except the Kimono Girls, who carry none, and Red, who carries four; Falkner carries none. The rival's team follows the player's starter choice;
the Cyndaquil versions are shown.

| Boss | Level (every Pokémon) | Team (held item) |
|---|---|---|
| Falkner | 15 | Pidgey (Oran Berry), Natu (Eviolite), Fletchling (Eviolite), Murkrow (Eviolite), Rookidee (Eviolite), Noctowl (Sitrus Berry) |
| Proton (Slowpoke Well) | 24 | Koffing (Eviolite), Golbat (Eviolite), Slowpoke (Eviolite), Grimer (Eviolite), Raticate (Silk Scarf), Houndour (Charcoal) |
| Bugsy | 24 | Ariados (Black Sludge), Pineco (Sitrus Berry), Ledian (Light Clay), Butterfree (Silver Powder), Yanma (Sitrus Berry), Scyther (Eviolite) |
| Rival 2 (Azalea; Cyndaquil version shown) | 33 | Golbat (Eviolite), Haunter (Eviolite), Magneton (Eviolite), Larvitar (Eviolite), Sneasel (Oran Berry), Quilava (Sitrus Berry) |
| Whitney (Heart & Soul's four and two more) | 33 | Clefairy (Eviolite), Aipom (Silk Scarf), Furret (Sitrus Berry), Stantler (Sitrus Berry), Girafarig (Twisted Spoon), Miltank (Leftovers) |
| Rival 3 (Burned Tower) | 42 | Golbat (Eviolite), Sneasel (Razor Claw), Haunter (Eviolite), Weepinbell (Eviolite), Larvitar (Eviolite), Quilava (Sitrus Berry) |
| Morty | 42 | Sableye (Sitrus Berry), Misdreavus (Eviolite), Drifblim (Sitrus Berry), Marowak Alola (Thick Club), Mimikyu (Life Orb), Gengar (Spell Tag) |
| Chuck (5th, 6th or 7th Gym) | 50 / 58 / 66 | Hitmontop (Sitrus Berry), Breloom (Focus Sash), Hawlucha (White Herb), Primeape (Eviolite), Poliwrath (Leftovers), Heracross (Heracronite) |
| Jasmine (5th, 6th or 7th Gym) | 50 / 58 / 66 | Skarmory (Rocky Helmet), Magneton (Eviolite), Bronzong (Leftovers), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Pryce (5th, 6th or 7th Gym) | 50 / 58 / 66 | Cloyster (Focus Sash), Dewgong (Leftovers), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Petrel (Rocket Hideout) | 50 (58 or 66 with five or six badges) | Forretress (Leftovers), Weezing (Black Sludge), Golbat (Eviolite), Houndoom (Black Glasses), Pupitar (Eviolite), Drapion (Black Glasses) |
| Ariana (Rocket Hideout) | 50 (58 or 66 with five or six badges) | Arbok (Black Sludge), Persian (Silk Scarf), Liepard (Sitrus Berry), Vileplume (Black Sludge), Gyarados (Sitrus Berry), Honchkrow (Scope Lens) |
| Eusine (Cianwood) | 50 | Politoed (Damp Rock), Hypno (Leftovers), Electrode (Focus Sash), Lanturn (Sitrus Berry), Gengar (Black Sludge), Starmie (Life Orb) |
| Proton (Radio Tower) | 75 | Muk (Black Sludge), Nidoqueen (Life Orb), Weezing (Rocky Helmet), Nidoking (Life Orb), Toxicroak (Life Orb), Rhydon (Eviolite) |
| Petrel (Radio Tower) | 75 | Forretress (Leftovers), Weezing Galar (Black Sludge), Toxapex (Black Sludge), Pupitar (Eviolite), Cloyster (Focus Sash), Drapion (Black Glasses) |
| Ariana (Radio Tower) | 75 | Arbok (Black Sludge), Persian (Silk Scarf), Skuntank (Black Sludge), Vileplume (Black Sludge), Gyarados (Sitrus Berry), Honchkrow (Scope Lens) |
| Archer (Radio Tower) | 75 | Porygon Z (Choice Specs), Tauros (Life Orb), Crawdaunt (Life Orb), Slowbro (Leftovers), Bisharp (Black Glasses), Houndoom (Houndoominite) |
| Rival 4 (Goldenrod Underground) | 75 | Crobat (Sharp Beak), Weavile (Life Orb), Alakazam (Focus Sash), Victreebel (Black Sludge), Pupitar (Eviolite), Typhlosion (Choice Scarf) |
| Clair | 75 | Druddigon (Rocky Helmet), Flygon (Choice Scarf), Dragalge (Black Sludge), Altaria (Altarianite), Kommo O (Life Orb), Kingdra (Wacan Berry) |
| Rival 5 (Victory Road) | 85 | Crobat (Sharp Beak), Weavile (Life Orb), Victreebel (Black Sludge), Ursaring (Flame Orb), Tyranitar (Tyranitarite), Typhlosion (Choice Scarf) |
| Zuki | 85 | Umbreon (Leftovers) |
| Naoko | 85 | Espeon (Life Orb) |
| Miki | 85 | Flareon (Toxic Orb) |
| Sayo | 85 | Jolteon (Choice Specs) |
| Kuni | 85 | Vaporeon (Leftovers) |
| Will | 85 | Xatu (Light Clay), Slowbro (Leftovers), Bronzong (Leftovers), Farigiraf (Sitrus Berry), Gardevoir (Choice Scarf), Alakazam (Alakazite) |
| Koga | 85 | Toxapex (Black Sludge), Muk Alola (Black Sludge), Toxicroak (Life Orb), Venomoth (Focus Sash), Beedrill (Beedrillite), Crobat (Sharp Beak) |
| Bruno | 85 | Hitmontop (Rocky Helmet), Steelix (Leftovers), Hitmonlee (Life Orb), Hitmonchan (Punching Glove), Machamp (Sitrus Berry), Lucario (Lucarionite) |
| Karen | 85 | Umbreon (Leftovers), Vileplume (Black Sludge), Gengar (Life Orb), Honchkrow (Scope Lens), Absol (Absolite), Houndoom (Black Glasses) |
| Lance | 85 | Gyarados (Gyaradosite), Aerodactyl (Focus Sash), Charizard (Charcoal), Salamence (Life Orb), Garchomp (Rocky Helmet), Dragonite (Lum Berry) |
| Brock | 90 | Golem (Leftovers), Omastar (White Herb), Kabutops (Life Orb), Relicanth (Choice Band), Kleavor (Focus Sash), Aerodactyl (Aerodactylite) |
| Misty | 90 | Pelipper (Damp Rock), Golduck (Life Orb), Lapras (Leftovers), Milotic (Leftovers), Blastoise (Blastoisinite), Starmie (Wise Glasses) |
| Lt. Surge | 90 | Electrode (Focus Sash), Magnezone (Choice Specs), Lanturn (Leftovers), Electivire (Life Orb), Manectric (Manectite), Raichu (Magnet) |
| Erika | 90 | Jumpluff (Leftovers), Roserade (Life Orb), Tangrowth (Rocky Helmet), Victreebel (Black Sludge), Bellossom (Sitrus Berry), Venusaur (Venusaurite) |
| Janine | 90 | Weezing (Black Sludge), Nidoqueen (Life Orb), Muk (Leftovers), Crobat (Sharp Beak), Venomoth (Focus Sash), Gengar (Gengarite) |
| Sabrina | 90 | Mr Mime (Light Clay), Wobbuffet (Sitrus Berry), Slowbro (Leftovers), Espeon (Life Orb), Alakazam (Twisted Spoon), Metagross (Metagrossite) |
| Blaine | 90 | Torkoal (Heat Rock), Rapidash (Life Orb), Magmortar (Expert Belt), Volcarona (Charcoal), Arcanine Hisui (Choice Band), Camerupt (Cameruptite) |
| Blue | 90 | Machamp (Sitrus Berry), Exeggutor (Sitrus Berry), Rhyperior (Weakness Policy), Arcanine (Choice Band), Tyranitar (Leftovers), Pidgeot (Pidgeotite) |
| Red | 100 (rematch too) | Pikachu (Light Ball), Espeon (Life Orb), Snorlax (Leftovers), Venusaur (Life Orb), Blastoise (White Herb), Charizard (Charizardite Y); EVs on all six |

Every Pokémon is at the level shown, the NORMAL cap of the earliest point the battle can happen
(with HARD level caps, the HARD cap there). A boss fought later is raised to the player's cap then
(D21): the Kanto Gym teams, which are also the Fighting Dojo rematches, are at 100 after the Kanto
League, like every Heart & Soul rematch then.

## Route mini-bosses

Since 0.8.0 one trainer on most routes has a competitive team at the level cap, like Emerald
Imperium's route mini-bosses (D30). Each holds an item, and has a nature, an ability and four
chosen moves on every Pokémon (`ROUTE_BOSSES` in `boss_teams.py`); the boss AI. The level shown
is the NORMAL cap of the earliest point the route can be reached; met later, a mini-boss is at
the player's cap. They carry no healing items and have no Mega Evolutions, which keeps them below
the Gym Leaders.

Against the prepared six at the cap played naively (one move per Pokémon, never switching;
`route_bosses` on mGBA), the Johto mini-bosses lost 14 of 16 battles (Cybil's sun team and
Jake won) and the Kanto ones won 10 of 12 (Otis and Bret lost), about as the Kanto Gym Leaders
do against that line (`bosses_m5`). On VBA-M, whose battle RNG differs, they lost 15 of 16
(Blake won) and won 9 of 12. A player who switches and plays to matchups does better.

| Route | Trainer | Level | Team (held item) |
|---|---|---|---|
| 30 | Youngster Mikey | 15 | Pichu (Eviolite), Sentret (Eviolite), Rattata (Flame Orb) |
| 32 | Camper Roland | 15 | Bellsprout (Eviolite), Mareep (Eviolite), Geodude (Eviolite) |
| 34 | Cooltrainer Kate | 24 | Shellder (Eviolite), Growlithe (Eviolite), Snubbull (Eviolite), Kadabra (Eviolite) |
| 35 | Bird Keeper Bryan | 24 | Swablu (Eviolite), Farfetchd (Leek), Fearow (Sharp Beak), Noctowl (Sitrus Berry) |
| 37 | Psychic M Greg | 33 | Xatu (Light Clay), Grumpig (Leftovers), Kirlia (Eviolite), Espeon (Life Orb) |
| 38 | Beauty Valerie | 33 | Togetic (Eviolite), Granbull (Sitrus Berry), Azumarill (Choice Band), Clefable (Leftovers) |
| 39 | Sailor Eugene | 33 | Tentacruel (Black Sludge), Poliwhirl (Eviolite), Machoke (Eviolite), Kingler (Life Orb) |
| 40 | Swimmer M Simon | 42 | Pelipper (Damp Rock), Floatzel (Life Orb), Seaking (Mystic Water), Golduck (Wise Glasses), Quagsire (Leftovers) |
| 41 | Swimmer M George | 42 | Mantine (Leftovers), Octillery (Life Orb), Seadra (Eviolite), Lapras (Sitrus Berry), Starmie (Life Orb) |
| 42 | Hiker Benjamin | 42 | Graveler (Eviolite), Onix (Eviolite), Rhyhorn (Eviolite), Piloswine (Eviolite), Sudowoodo (Choice Band) |
| 43 | Pokemaniac Ben | 42 | Lickitung (Eviolite), Kangaskhan (Silk Scarf), Slowbro (Leftovers), Aerodactyl (Focus Sash), Dragonair (Eviolite) |
| 47 | Hiker Devin | 42 | Gligar (Eviolite), Lairon (Eviolite), Marowak (Thick Club), Hariyama (Flame Orb), Golem (Sitrus Berry) |
| 44 | Cooltrainer Cybil | 50 | Ninetales (Heat Rock), Jumpluff (Leftovers), Butterfree (Focus Sash), Arcanine (Choice Band), Bellossom (Life Orb) |
| 26 | Cooltrainer Jake | 50 | Tangrowth (Rocky Helmet), Electivire (Life Orb), Magmortar (Expert Belt), Togekiss (Leftovers), Kingdra (Choice Specs), Gyarados (Sitrus Berry) |
| 27 | Cooltrainer Blake | 50 | Scizor (Choice Band), Starmie (Life Orb), Ampharos (Leftovers), Houndoom (Life Orb), Heracross (Choice Scarf), Nidoking (Life Orb) |
| 45 | Cooltrainer Kelly | 66 | Roserade (Focus Sash), Lopunny (Life Orb), Froslass (Focus Sash), Azumarill (Choice Band), Gardevoir (Choice Scarf), Milotic (Leftovers) |
| 1 | Cooltrainer Quinn | 90 | Hippowdon (Leftovers), Excadrill (Life Orb), Gliscor (Toxic Orb), Sandslash (Focus Sash), Garchomp (Rocky Helmet), Tyranitar (Choice Band) |
| 3 | Firebreather Otis | 90 | Ninetales (Heat Rock), Houndoom (Black Glasses), Chandelure (Choice Specs), Magmortar (Expert Belt), Volcarona (Leftovers), Charizard (Life Orb) |
| 8 | Biker Dwayne | 90 | Weezing (Rocky Helmet), Muk (Black Sludge), Scrafty (Leftovers), Crobat (Sharp Beak), Krookodile (Choice Scarf), Hydreigon (Life Orb) |
| 9 | Hiker Tim | 90 | Donphan (Leftovers), Steelix (Leftovers), Golem (Focus Sash), Mamoswine (Life Orb), Aggron (Sitrus Berry), Rhyperior (Weakness Policy) |
| 10 | Pokefan Robert | 90 | Granbull (Leftovers), Azumarill (Choice Band), Mimikyu (Life Orb), Togekiss (Leftovers), Sylveon (Choice Specs), Clefable (Leftovers) |
| 11 | Psychic M Herman | 90 | Bronzong (Leftovers), Hatterene (Life Orb), Gallade (Choice Band), Reuniclus (Life Orb), Alakazam (Focus Sash), Metagross (Life Orb) |
| 12 | Fisherman Stephen | 90 | Politoed (Damp Rock), Kingdra (Life Orb), Ludicolo (Life Orb), Seismitoad (Leftovers), Lanturn (Leftovers), Gyarados (Sitrus Berry) |
| 13 | Juggler Bret | 90 | Klefki (Light Clay), Sableye (Leftovers), Ambipom (Silk Scarf), Mr Mime (Life Orb), Rotom (Leftovers), Magnezone (Choice Specs) |
| 15 | Expert Colette | 90 | Hawlucha (White Herb), Breloom (Focus Sash), Machamp (Sitrus Berry), Conkeldurr (Flame Orb), Infernape (Life Orb), Lucario (Life Orb) |
| 18 | Bird Keeper Boris | 90 | Skarmory (Rocky Helmet), Staraptor (Choice Band), Talonflame (Sharp Beak), Corviknight (Leftovers), Togekiss (Choice Scarf), Dragonite (Lum Berry) |
| 20 | Swimmer F Lori | 90 | Araquanid (Sitrus Berry), Starmie (Life Orb), Vaporeon (Leftovers), Lapras (Choice Specs), Primarina (Life Orb), Milotic (Leftovers) |
| 25 | Cooltrainer Kevin | 90 | Gengar (Focus Sash), Scizor (Life Orb), Ferrothorn (Leftovers), Crawdaunt (Life Orb), Kommo O (Life Orb), Salamence (Life Orb) |

### Notes from the play tests

The naive autopilot (no switching, one move per Pokémon) and the game-plan autopilot both play
worse than a person, so their win counts are lower bounds. Since 0.7.0 every boss Pokémon is at
the cap, and the test teams hold items from the care packages the player has by then (before,
no items). The regression's counts for both emulators are in TESTING.md.

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
