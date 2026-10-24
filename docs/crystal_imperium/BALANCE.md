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
   With Minimal Grinding on (the default), every Pokémon battles at 31 IVs / 0 EVs anyway,
   except Red's, which keep their EVs (D27).
3. **Each boss has a signature strategy and a fair counter** that the player can catch
   before the fight. The counter should cost planning, not be a free win.
4. **Verify in the emulator.** Every reworked Gym Leader gets a play test with a realistic
   team of Pokémon that are obtainable before the fight.
5. **Measure win rates, not single runs.** The battle autopilot (`tools/emurun`) plays a
   deliberately naive line: no items, no voluntary switching, one fixed move per Pokémon.
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
| Early Johto (Falkner, Bugsy, Whitney; Proton, rival 2–3) | 11 / 16 / 21 | Reworked and play-tested (`falkner`, `bugsy`, `whitney`, `bosses_m3`) |
| Midgame Johto (Morty, Chuck, Jasmine, Pryce; Rocket Hideout) | 25 / 31 / 36 / 38 | Reworked; Chuck, Jasmine and Pryce in three versions for any order (`bosses_m3`, `bosses_m4`) |
| Late Johto (Radio Tower, rival 4, Clair, Kimono Girls, Victory Road) | 45 / 56 | Reworked (`bosses_m3`, `bosses_m4`) |
| Elite Four / Lance | 56 → 70 after the title | Reworked (`bosses_e4`) |
| Kanto leaders, Blue | 70 | Reworked (`bosses_m5`) |
| Red (Mt. Silver) | after the Kanto League, uncapped; 96–100 | Reworked: the hardest battle (`red`) |
| Rematches and other postgame battles | 70 / uncapped | HnS teams with the smart AI |

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
| Rookidee Lv 10 | – | Keen Eye | Adamant | Hone Claws, Power Trip, Peck, Rock Smash | Set-up threat; Rock Smash punishes Rock answers (0.5.0: was Steel Wing, which Rookidee cannot learn) |
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
| Cyndaquil | Pidgeotto (Gust) / Quilava (Flame Wheel) / Kadabra (Psybeam) / Machop (Low Sweep) | **3 of 12 RNG samples won** (`whitney.emu`, 2026-10-24). The first measurement (2026-10-23) was 3 of 5; after later code changes shifted the battle RNG, the same five samples all lost, so the test now samples twelve battles. The naive line wins about a quarter of the time. |
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

Boss Megas: Chuck (Heracross), Jasmine (Steelix), Pryce (Abomasnow), Clair (Altaria), Archer
(Houndoom), the rival on Victory Road (Tyranitar), Will (Alakazam), Koga (Beedrill), Bruno
(Lucario), Karen (Absol), Lance (Gyarados); Brock (Aerodactyl), Misty (Blastoise), Lt. Surge
(Manectric), Erika (Venusaur), Janine (Gengar), Sabrina (Metagross), Blaine (Camerupt), Blue
(Pidgeot), Red (Charizard Y); from Heart & Soul's rematch teams, Lance's rematch (Salamence)
and postgame battle (Charizard X). Steelixite and Abomasite come with the 6th badge, so Jasmine
or Pryce as the 5th Gym uses a stone the player can't buy yet; the others are on sale by then.

## Boss roster

Every boss from `tools/crystal_imperium/boss_teams.py` (the file has the natures, abilities and
moves). Each team's last Pokémon is its ace, kept back until the others are down. Healing items:
Super Potions for Proton in Slowpoke Well and the rival in Azalea and at the Burned Tower, two
Hyper Potions for Morty and the 5th-Gym versions, two Full Restores for everyone after that
except the Kimono Girls, who carry none, and Red, who carries four. The rival's team follows the player's starter choice;
the Cyndaquil versions are shown.

| Boss | Levels | Team (held item) |
|---|---|---|
| Proton (Slowpoke Well) | 13–15 | Koffing (Eviolite), Slowpoke (Eviolite), Houndour (Charcoal) |
| Rival 2 (Azalea; Cyndaquil version shown) | 17–19 | Golbat (Eviolite), Larvitar (Eviolite), Sneasel (Oran Berry), Quilava (Sitrus Berry) |
| Rival 3 (Burned Tower) | 22–24 | Golbat (Eviolite), Sneasel (Razor Claw), Weepinbell (Eviolite), Larvitar (Eviolite), Quilava (Sitrus Berry) |
| Morty | 23–25 | Sableye (Sitrus Berry), Misdreavus (Eviolite), Drifblim (Sitrus Berry), Marowak Alola (Thick Club), Gengar (Spell Tag) |
| Chuck (as 5th Gym) | 29–31 | Hitmontop (Sitrus Berry), Breloom (Focus Sash), Primeape (Eviolite), Poliwrath (Leftovers), Heracross (Heracronite) |
| Chuck (as 6th Gym) | 34–36 | Hitmontop (Sitrus Berry), Breloom (Focus Sash), Hawlucha (White Herb), Primeape (Eviolite), Poliwrath (Leftovers), Heracross (Heracronite) |
| Chuck (as 7th Gym) | 36–38 | Hitmontop (Sitrus Berry), Breloom (Focus Sash), Hawlucha (White Herb), Primeape (Eviolite), Poliwrath (Leftovers), Heracross (Heracronite) |
| Jasmine (as 5th Gym) | 29–31 | Skarmory (Rocky Helmet), Magneton (Eviolite), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Jasmine (as 6th Gym) | 34–36 | Skarmory (Rocky Helmet), Magneton (Eviolite), Bronzong (Leftovers), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Jasmine (as 7th Gym) | 36–38 | Skarmory (Rocky Helmet), Magneton (Eviolite), Bronzong (Leftovers), Mawile (Sitrus Berry), Scizor (Metal Coat), Steelix (Steelixite) |
| Pryce (as 5th Gym) | 29–31 | Cloyster (Focus Sash), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Pryce (as 6th Gym) | 34–36 | Cloyster (Focus Sash), Dewgong (Leftovers), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Pryce (as 7th Gym) | 36–38 | Cloyster (Focus Sash), Dewgong (Leftovers), Jynx (Wise Glasses), Weavile (Razor Claw), Mamoswine (Never Melt Ice), Abomasnow (Abomasite) |
| Petrel (Rocket Hideout) | 34–36 | Weezing (Black Sludge), Forretress (Leftovers), Pupitar (Eviolite), Drapion (Black Glasses) |
| Ariana (Rocket Hideout) | 34–36 | Arbok (Black Sludge), Persian (Silk Scarf), Vileplume (Black Sludge), Honchkrow (Scope Lens) |
| Proton (Radio Tower) | 42–44 | Muk (Black Sludge), Nidoqueen (Life Orb), Weezing (Rocky Helmet), Nidoking (Life Orb), Rhydon (Eviolite) |
| Petrel (Radio Tower) | 43–44 | Forretress (Leftovers), Weezing Galar (Black Sludge), Pupitar (Eviolite), Cloyster (Focus Sash), Drapion (Black Glasses) |
| Ariana (Radio Tower) | 43–44 | Arbok (Black Sludge), Persian (Silk Scarf), Vileplume (Black Sludge), Gyarados (Sitrus Berry), Honchkrow (Scope Lens) |
| Archer (Radio Tower) | 43–45 | Porygon Z (Choice Specs), Tauros (Life Orb), Crawdaunt (Life Orb), Slowbro (Leftovers), Bisharp (Black Glasses), Houndoom (Houndoominite) |
| Rival 4 (Goldenrod Underground) | 43–45 | Crobat (Sharp Beak), Weavile (Life Orb), Victreebel (Black Sludge), Pupitar (Eviolite), Typhlosion (Choice Scarf) |
| Clair | 43–45 | Druddigon (Rocky Helmet), Flygon (Choice Scarf), Dragalge (Black Sludge), Altaria (Altarianite), Kommo O (Life Orb), Kingdra (Wacan Berry) |
| Rival 5 (Victory Road) | 54–56 | Crobat (Sharp Beak), Weavile (Life Orb), Victreebel (Black Sludge), Ursaring (Flame Orb), Tyranitar (Tyranitarite), Typhlosion (Choice Scarf) |
| Zuki | 54 | Umbreon (Leftovers) |
| Naoko | 54 | Espeon (Life Orb) |
| Miki | 55 | Flareon (Toxic Orb) |
| Sayo | 55 | Jolteon (Choice Specs) |
| Kuni | 56 | Vaporeon (Leftovers) |
| Will | 54–55 | Xatu (Light Clay), Slowbro (Leftovers), Bronzong (Leftovers), Farigiraf (Sitrus Berry), Gardevoir (Choice Scarf), Alakazam (Alakazite) |
| Koga | 54–55 | Toxapex (Black Sludge), Muk Alola (Black Sludge), Toxicroak (Life Orb), Venomoth (Focus Sash), Beedrill (Beedrillite), Crobat (Sharp Beak) |
| Bruno | 55–56 | Hitmontop (Rocky Helmet), Steelix (Leftovers), Hitmonlee (Life Orb), Hitmonchan (Punching Glove), Machamp (Sitrus Berry), Lucario (Lucarionite) |
| Karen | 55–56 | Umbreon (Leftovers), Vileplume (Black Sludge), Gengar (Life Orb), Honchkrow (Scope Lens), Absol (Absolite), Houndoom (Black Glasses) |
| Lance | 55–56 | Gyarados (Gyaradosite), Aerodactyl (Focus Sash), Charizard (Charcoal), Salamence (Life Orb), Garchomp (Rocky Helmet), Dragonite (Lum Berry) |
| Brock | 68–70 | Golem (Leftovers), Omastar (White Herb), Kabutops (Life Orb), Relicanth (Choice Band), Kleavor (Focus Sash), Aerodactyl (Aerodactylite) |
| Misty | 68–70 | Pelipper (Damp Rock), Golduck (Life Orb), Lapras (Leftovers), Milotic (Leftovers), Blastoise (Blastoisinite), Starmie (Wise Glasses) |
| Lt. Surge | 68–70 | Electrode (Focus Sash), Magnezone (Choice Specs), Lanturn (Leftovers), Electivire (Life Orb), Manectric (Manectite), Raichu (Magnet) |
| Erika | 68–70 | Jumpluff (Leftovers), Roserade (Life Orb), Tangrowth (Rocky Helmet), Victreebel (Black Sludge), Bellossom (Sitrus Berry), Venusaur (Venusaurite) |
| Janine | 68–70 | Weezing (Black Sludge), Nidoqueen (Life Orb), Muk (Leftovers), Crobat (Sharp Beak), Venomoth (Focus Sash), Gengar (Gengarite) |
| Sabrina | 68–70 | Mr Mime (Light Clay), Wobbuffet (Sitrus Berry), Slowbro (Leftovers), Espeon (Life Orb), Alakazam (Twisted Spoon), Metagross (Metagrossite) |
| Blaine | 68–70 | Torkoal (Heat Rock), Rapidash (Life Orb), Magmortar (Expert Belt), Volcarona (Charcoal), Arcanine Hisui (Choice Band), Camerupt (Cameruptite) |
| Blue | 69–70 | Machamp (Sitrus Berry), Exeggutor (Sitrus Berry), Rhyperior (Weakness Policy), Arcanine (Choice Band), Tyranitar (Leftovers), Pidgeot (Pidgeotite) |
| Red | 96–100 (rematch: 100) | Pikachu (Light Ball), Espeon (Life Orb), Snorlax (Leftovers), Venusaur (Life Orb), Blastoise (White Herb), Charizard (Charizardite Y); EVs on all six |

### Notes from the play tests

The naive autopilot (no switching, no items, one move per Pokémon) and the game-plan autopilot
both play worse than a person, so their win counts are lower bounds. The regression's counts
for both emulators are in TESTING.md.

- **The Elite Four** (`bosses_e4`, cap 56): the prepared six beats Koga most of the time
  played naively. Naive play rarely beat Will (3 of 60 tries with the prepared six, on two ROM
  builds) or Lance (13 of 60 with a six built for him), and its results against Bruno and Karen
  swung between the emulators (5 and 0 of 6; 2 and 0 of 6). Played with a game plan, sixes
  built for them beat Will 3 times in 6, Bruno 5 in 6, Karen 3 in 6 and Lance 3 in 12, so the
  test gives them 8, 6, 8 and 24 tries.
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
- **Red** is the hardest battle (D27). Every team at level 100 played naively lost: 30 tries
  with five different sixes, among them six legendary Dragons, and 24 more against weaker
  versions of Red (two Full Restores, or no prediction AI). A game plan without held items lost
  12 of 12. A six with held items and a Mega played with a game plan (Life Orb Garchomp for
  Pikachu, Kingambit for Espeon, Flame Orb Conkeldurr for Snorlax, Talonflame with Safety
  Goggles against Sleep Powder for Venusaur, Mega Ampharos for Blastoise, Assault Vest
  Tyranitar for Charizard) beat him 4 times in 12; before Talonflame had the goggles, 6 times
  in 48. With two Full Restores and no EVs the plan without items won 2 of 6 and the naive six
  1 of 6, against none of 6 each with the EVs: the EVs are what set him apart.
