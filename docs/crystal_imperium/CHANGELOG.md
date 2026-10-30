# Crystal Imperium changelog

## 0.15.1-experimental (2026-10-30)

### The TMs come in the care packages (DECISIONS.md D48)
- No more buying TMs: the starting care package brings the 71 TMs the shops sell from the start,
  and each Johto badge's package the ones the shops add with it (44 with the first, 40 with the
  second, 18 with the third: Ice Beam, Thunderbolt, Flamethrower...), all 198 by the eighth. A TM
  you have already isn't given twice.
- A save from an earlier version gets the TMs of the packages it already received, all at once, on
  its next step outside.
- The TM clerks stay, for anything missing (and, with INFINITE TMS off, more copies).

### Emerald Imperium's base stats (D50)
- 294 Pokémon have Imperium's base stats, from its official dex, most of them buffs to Pokémon
  that are weak in the official games: Farfetch'd (75 HP, 70 Defense), Sunflora (135 Sp. Atk),
  Parasect, Ledian (90 Attack), Raichu, Fearow (115 Speed), Tauros, Octillery, Ariados, Granbull,
  Qwilfish, Corsola and many more. Trainers' Pokémon change with them.

### Pikachu, strong without evolving (D51)
- Pikachu has 60 HP, 90 Attack, 60 Defense, 120 Speed, 90 Sp. Atk and 70 Sp. Def (490 in all,
  320 before), so you can use it all game without a Thunder Stone; with a Light Ball it hits
  harder than Raichu. Its cosplay and cap forms too.
- Pikachu shows its newest sprites (the Gen 4/5-style ones), front and back; the other Pokémon keep
  theirs.

### DexNav marks the Pokémon you've caught (D52)
- A small Poké Ball at the corner of each caught Pokémon's icon in DexNav, and after its name in
  the list of every Pokémon (SELECT).

### A code for shiny Pokémon (D49)
- **SHINYA** (or SHA, or ALLSHINY) at the NES in your room: every wild Pokémon, gift Pokémon and
  Egg is shiny until you enter it again.

### Fixes
- After the PokéVial healed a fainted lead, the Pokémon following you was still the one that had
  been next in line; now the healed lead follows again at once (D53).

### Tools
- `tools/crystal_imperium/care_packages.py` takes the TM tiers from `tm_list.py`; `tools/emurun`'s
  `no_care_packages()` marks the TMs as received too.
- `tools/crystal_imperium/imperium_species.py` writes the base stats
  (`species_info/imperium_stats.h`); `tools/emurun`: `expect_base_stat`, new play tests
  `imperium_stats`, `cheat_shiny_all`, `pikachu`, `dexnav_caught` and `pokevial_follower`;
  `expect_species_field`, `expect_follower_species`; the runner's `expectrectne` and `expectfind`.

## 0.15.0-experimental (2026-10-30)

### Emerald Imperium's evolutions (DECISIONS.md D44, D45)
Pokémon evolve the way they do in Emerald Imperium, from its official dex: 219 species change.
`docs/crystal_imperium/EVOLUTIONS.md` lists how every Pokémon evolves, generated from the game's data.
- **Trade evolutions take a Linking Cord too** (trading still works): Kadabra, Machoke,
  Graveler, Haunter, Rhydon, Electabuzz, Magmar, Porygon, Dusclops, Boldore, Gurdurr,
  Karrablast, Shelmet, Phantump and Pumpkaboo. They no longer evolve by level (Kadabra did at
  42). Others take Imperium's item: a Metal Coat for Onix and Scyther, a King's Rock for
  Slowpoke, Poliwhirl and Scyther's Kleavor, a Prism Scale for Seadra and Feebas, a Water or Sun
  Stone for Clamperl (Huntail, Gorebyss), a Dusk Stone for Porygon2, a Shiny Stone for Spritzee
  and Swirlix.
- **Regional forms, anywhere**, by time of day or an item: a Shiny Stone makes Alolan Raichu, a
  Sun Stone Alolan Exeggutor, an Ice Stone Galarian Mr. Mime and Hisuian Avalugg, a Leaf Stone
  Hisuian Lilligant, a Metal Coat Hisuian Sliggoo. At night Cubone becomes Alolan Marowak (28),
  Koffing Galarian Weezing (35), Quilava, Dewott and Rufflet their Hisuian forms (36); by day
  Dartrix becomes Hisuian Decidueye. Galarian Slowpoke becomes Galarian Slowbro at 37 and
  Galarian Slowking with a King's Rock. "Day" is any time but night (6:00 to 18:59).
- **Friendship, places and special methods** became levels or items: Munchlax and Riolu at 30,
  Alolan Meowth at 28, Crabrawler at 30; Magnezone and Vikavolt by Thunder Stone (or on Route
  10 and in the Power Plant), Probopass by Metal Coat, Leafeon and Glaceon by their stones only;
  Gliscor, Weavile and Porygon-Z with a Dusk Stone, Chansey from Happiny with a Shiny Stone.
  Kingambit and Archaludon at 50 (Archaludon also with a Metal Alloy), Sneasler at 47, Gholdengo
  at 45, Wyrdeer and Hydrapple at 44, Overqwil at 36, Runerigus at 35, Pawmot at 32, Sirfetch'd
  and Dipplin at 30, Brambleghast at 27, Rabsca at 16. Urshifu: a Dusk Stone (Single Strike) or a
  Water Stone (Rapid Strike); Armarouge and Ceruledge: a Sun or a Moon Stone; Polteageist: a Moon
  Stone. Basculegion from any Basculin at 44, its form by gender. Meltan becomes Melmetal with a
  Metal Coat. Ursaring becomes Ursaluna at 48 by day and Bloodmoon Ursaluna at 48 at night.
- **Moves:** Primeape evolves when it levels up knowing Shadow Punch, which it learns at 35;
  Tangela, Aipom, Yanma, Bonsly, Steenee and Mime Jr. evolve by their move too (no level).
  Lickilicky also at 35, Mamoswine at 45, Grapploct at 36. Sylveon: friendship with a Fairy-type
  move. Dunsparce: Two-Segment Dudunsparce by Hyper Drill, Three-Segment at 45.
- **Levels:** the starters at 16 and 36, most early two-stage Pokémon at 16 (Pidgey, Rattata,
  Hoothoot, Ledyba, Spinarak, Hoppip, Zigzagoon...), many earlier than before (Ponyta and Mienfoo
  28, Pawniard 36, Deino 44 and Zweilous 59, Noibat 36), a few later (Grimer 40, Ivysaur,
  Croconaw, Grotle and the Gen 7 and 8 starters 36, Cosmoem 64). Nincada becomes Ninjask at 20
  and no longer gives a Shedinja (as in Imperium; the DexNav finds Shedinja). Mantyke evolves at
  30, with no Remoraid needed.
- **Kept from Heart & Soul**, for the forms nothing else reaches: the Alcremie flavours (stones
  and spins holding a Sweet; Imperium's Shiny Stone gives Vanilla Cream).
- **Wild Variety:** Shedinja joins the Pokémon an area can have (it no longer comes from Nincada),
  Melmetal leaves the postgame legends (it comes from Meltan). Most areas have other Wild Variety
  Pokémon than in 0.14; each still keeps its own all day.

### Emerald Imperium's movesets (D45)
- Abilities, level-up moves, Egg Moves and TM and tutor moves come from Imperium's official dex
  (they came from the Radical Red dex, which it agrees with nearly everywhere): Empoleon learns
  Iron Head at 42, the Hoenn starters their first attack at 6, Heavy Slam, Gravity and Water Pulse
  are TM moves for many more Pokémon, Abomasnow has Slush Rush, Medicham Huge Power, Garbodor
  Stench, Emboar Blaze and Reckless. Radical Red's tutor moves Imperium doesn't have (Uproar, Hone
  Claws, Toxic Spikes, Frost Breath, Cosmic Power) and its moves Soul Robbery, Sonic Slash and
  Forbidden Spell leave the learnsets; Draco Barrage and Dark Hole stay as postgame TMs.
- Pikachu learns Zippy Zap at 55 and Raichu at 62, in Imperium as here.

### Evolution items and friendship Berries in Goldenrod
- The Goldenrod Dept. Store 2F clerk sells Emerald Imperium's fifteen evolution items for ¥500
  each, after the balls: the Fire, Thunder, Leaf, Water, Sun, Moon, Ice, Dusk, Dawn and Shiny
  Stones, the Prism Scale, the Linking Cord, the King's Rock, the Metal Coat and the Up-Grade.
  They cost ¥500 in every shop. After them come the six Berries that raise friendship (Pomeg,
  Kelpsy, Qualot, Hondew, Grepa, Tamato; ¥20).
- The Mahogany shop sells no evolution items any more (Rage Candy Bars, Never-Melt Ice and the
  Razor Fang and Claw). Items no evolution uses leave the care packages (the Dragon Scale,
  Protector, Electirizer, Magmarizer, Dubious Disc, Reaper Cloth, Oval Stone, Sachet, Whipped
  Dream, the apples, pots, teacups and armours, the Galarica items, Black Augurite, Peat Block,
  the Gimmighoul Coins, the Scrolls); the Metal Alloy stays. Side battles that gave one give the
  trainer's Pokémon's new item: Fantina and Volkner a Linking Cord, Roark a King's Rock, Katy a
  Leaf Stone and a Sun Stone. Two people who said the trade evolutions happen by level name the
  Linking Cord now.

### Harder trainers, as Emerald Imperium's (D46)
- **Ordinary trainers fight at your level:** their Pokémon are one to three levels below your
  strongest (Imperium's "Highest Lv -1 to -3"), never under their old level on the cap curve,
  never above the cap. A route's trainers stay a fight when you come back stronger.
- **Trainers' Pokémon are evolved** as far as their level allows: the Dragonair of Dragon's Den
  and the Blackthorn Gym are Dragonite now. A boss's team stays as designed at its own level; a
  boss you fight later, raised to a later cap, is evolved too, except its Eviolite Pokémon.
- **31 IVs:** Heart & Soul's ordinary trainers had 0 in every IV; Imperium's have 31, and so do
  these now.

### Competitive rematch and postgame bosses, and Ace Trainers (D47)
- **41 bosses get Emerald Imperium-style teams** in place of Heart & Soul's: the Johto Gym
  Leaders' rematches in the Fighting Dojo, the Elite Four's and Lance's rematches after the Johto
  League, every postgame rematch after the Kanto League (the sixteen Gym Leaders, Blue, the Elite
  Four and Lance), the rival's last two battles (Mt. Moon and the Indigo Plateau) and Elder Li.
  Each Pokémon has a job, an item, a nature, an ability and four moves; each team has a plan
  (hazards, weather, terrain, screens, Tailwind, pivots, setup) and one Mega Evolution. The
  postgame teams use up to three legendaries, Ultra Beasts or Paradox Pokémon each, none
  restricted, and no EVs, so Red is still the hardest battle. No more Dragonair and Shelgon in
  Clair's rematch.
- **59 Ace Trainers on the routes**, as in Emerald Imperium: 26 in Johto and 33 in Kanto, one on
  every route you walk (two on the long ones), standing where they see you on the main path.
  Three Pokémon on the first routes, up to six with competitive EVs in Kanto, each team built
  around a plan (sand, rain, sun, snow, Trick Room, hazards, screens, Tailwind, terrain). They
  fight at your level, like every trainer. The first, Kaito, waits at the end of Route 29, just
  before Cherrygrove City.
- **No Ace Trainer copies a boss.** A critic played through all 59 teams and the 26 Cooltrainer
  teams as a competitive player and 25 changed: Astrid had Grusha's sets, Hayate Janine's and
  Koga's, Vera Bruno's and Chuck's, Sable Karen's, Evangeline the Kimono Girls' Eeveelutions;
  the Blackthorn Gym's Fran had Lance's team and Cooltrainer Nick Red's; the Articuno and Zapdos
  that stood at their own catch spots are gone; Johto has fewer rain teams; wrong battle tips
  (screens with a Light Clay last eight turns, not five) are right now.
- **Heart & Soul's own Cooltrainers** have competitive teams too, keeping their themes (Gwen's
  Eeveelutions, the Blackthorn Gym's Dragons, Irene's and Jenn's Water types).

### Fixes
- Milcery never evolved after a short clockwise spin (the engine read it as no spin at all), so
  a Sweet gave no Vanilla or Matcha Cream that way. A spin that evolves nothing now starts the
  next one from zero, and a very long one no longer counts from zero again after 34 seconds.
- Five boss Pokémon had abilities their species no longer has (Medicham's Pure Power, now Huge
  Power; a Scrappy Bloodmoon Ursaluna, now Mind's Eye; a Poison Touch Overqwil, now Intimidate).
- A trainer's Return hit with power 1 (Cooltrainer Kelly's Lopunny): trainers' Pokémon have no
  friendship unless their team gives them some. Every trainer Pokémon that knows Return, Pika
  Papow or Veevee Volley now has full friendship, and the validator checks it. A Pokémon whose
  trainer gives it no moves and that learned Return by level (a Rocket Grunt's Raticate learns it
  at 28) gets full friendship in battle too.
- The trainer checker could pass an ability a Pokémon doesn't have in this game (Defiant
  Empoleon, Lightning Rod Zapdos: older games' abilities), or check the wrong form (Meowstic-F for
  a Meowstic, which is Meowstic-M here), or read an ability from a species macro shared by
  several forms for the wrong Pokémon; any of these would stop a battle with an error screen. It
  now reads the species data as the game is built.

### Tools
- `tools/crystal_imperium/ei_dex.py` reads the official Emerald Imperium dex's data (a saved copy
  of its page script, `--ei-dex`); `imperium_species.py` and `imperium_evolutions.py` write from
  it, and `imperium_evolutions.py` also writes `EVOLUTIONS.md`.
- `tools/crystal_imperium/ace_trainers.py` places Ace Trainers on the routes (`ace_trainer_data.py`).
- `tools/emurun`: `party_cursor`, `expect_bag_lacks`, `expect_battler(..., bits=8)` for a
  battler's one-byte fields, `expect_party_species` (the runner's `expectpartyspecies` decrypts a
  party member's species); new play tests `imperium_evolutions`, `trainer_levels`,
  `boss_rematches`, `ace_trainers_johto`, `ace_trainers_kanto`, `cooltrainers`, `ace_sight`.

## 0.14.3-experimental (2026-10-28)

### No pause after buying a TM (DECISIONS.md D43)
- 0.14.2 checked every TM on sale against the whole TM case again after each purchase, and drew
  the list twice: with eight badges and few TMs, "Here you go! Thank you very much." stayed on
  screen about 20 frames (a third of a second) longer, and BUY took 16 frames longer to show the
  list. Now the bought TM alone leaves the list, and opening it checks the TM case once: both are
  as quick as before 0.14.2.

### Tools
- `tools/emurun`: `snap_buy_list_edge` and `buy_one_on_time` (the list must be back on screen
  within some frames of a purchase), `expect_buy_arrows`; `tm_shop_owned` also buys the last TM
  while the list is longer than the window, and checks the scroll arrows.

## 0.14.2-experimental (2026-10-27)

### TM shops list only the TMs you don't have (DECISIONS.md D43)
- Every TM shop (the TM clerk in each Poké Mart, the Goldenrod Dept. Store 5F, Celadon's TM
  counter) leaves out the TMs you already have, in the TM case or in the PC, instead of marking
  them OWNED. A TM you buy leaves the list right away, with the cursor on the next one. Once you
  have every TM on sale, the list is just CANCEL: "You have every TM on sale here!"
- That's with INFINITE TMS on (the default). With it off, teaching uses a TM up, so the TMs you
  have stay on the list and you can buy more.

### Tools
- `tools/emurun`: `buy_one`, `expect_buy_list` and `expect_buy_cursor` for a shop's buy list,
  `take_from_tm_case`; new play test `tm_shop_owned`.

## 0.14.1-experimental (2026-10-27)

### The DexNav list is the same all day (DECISIONS.md D42)
Leaving a route and coming back could show other Pokémon in the DexNav: the route's own Pokémon
changed with the time of day, and its Wild Variety Pokémon every day. Now:
- **Each area keeps one list at every hour:** its morning, day and night Pokémon together, and
  the wild Pokémon match it (Route 29's Pidgey, Sentret and Hoppip turn up at night too, and its
  Hoothoot by day). The Pokédex's area map shows them whichever time of day it shows.
- **Each area's Wild Variety Pokémon stay the same** (they changed every day). They fill the
  DexNav row's free icons, so a route with many Pokémon of its own has fewer of them.
- **Hidden Pokémon:** a map's three hidden Pokémon are the same at every hour (its day and night
  tables had three each); every family that had a hidden spot still has one.
- Sinjoh Ruins keeps its daytime Pokémon at night: its night ones would not fit in the DexNav
  row (they are all found elsewhere).

### Tools
- `gen_hidden_encounters.py`: one hidden set per map; Water and Ice families the water-only maps
  have no room for go to the caves and the grass.
- `tools/emurun`: `wild_variety_sample(..., not_in=...)` tallies battles against more lists.

## 0.14.0-experimental (2026-10-27)

### Side battles (DECISIONS.md D41)
Optional battles with Gym Leaders from newer regions, Emerald Imperium-style, and the postgame's
visitors before Red. Talk to one, answer YES, win, and they give you a reward once. Each battles
once, at your level cap with six Pokémon; lose, and they wait for another try.
- **Johto: Sinnoh's eight Gym Leaders**, one for each badge count:
  - Candice: Violet City's Trainer School, from the start.
  - Gardenia: Ilex Forest, by the Route 34 gate, from 2 badges. Her stronger team comes out from 4.
  - Fantina: Ecruteak City, 3 badges.
  - Maylene: Cianwood City, 4 badges.
  - Crasher Wake: Lake of Rage, 5 badges.
  - Byron: Olivine City by the lighthouse, 6 badges.
  - Roark: Route 44 by the Ice Path, 7 badges.
  - Volkner: Indigo Plateau, 8 badges.
- **Kanto: Paldea's eight Gym Leaders**, after the Johto League:
  - Katy in Pewter City, Larry in Viridian City, Brassius on Route 25, Kofu on Vermilion City's
    pier, Iono by Lavender Town's Radio Tower, Ryme in Celadon City, Tulip in Saffron City and
    Grusha on Cinnabar Island.
- **The postgame, after the Kanto League**, at level 100 like Red:
  - Cynthia at the Ruins of Alph, Iris in Blackthorn City, Geeta on Route 28 on the way to
    Mt. Silver, N in the National Park, Cyrus in Mahogany Town, Wallace in Cherrygrove City,
    Maxie in Fuchsia City, Archie in Cerulean City and Wally in Pallet Town.
  - Red is still the hardest battle, and still needs only the Kanto League.
- **Battle music:** Johto's Gym Leader theme for Sinnoh's eight, Kanto's for Paldea's eight, and
  the Champion theme for the postgame (Maxie and Archie: Emerald's Team Magma and Team Aqua leader
  theme).
- **Rewards:**
  - Ten Gems of the trainer's type, which nothing else gives.
  - TMs before the TM shops sell them.
  - Mega Stones before the Goldenrod Mega shop stocks them (Gengarite, Lucarionite, Gyaradosite,
    Metagrossite, Tyranitarite).
  - Evolution items, and the Rotom Catalog (Volkner).
  - The Exp. Charm (Larry) and the Catching Charm (Iono).
  - From the postgame: a Master Ball, Ability Patches, an Ability Capsule, the Oval Charm and
    PP Maxes.
  - A reward goes whole to the Bag, or to the PC when a pocket is full. If neither has room,
    nothing is given until you come back with room.
- **Their own sprites**, in battle and on the map, from their artists' free releases (CREDITS.md):
  iriv24 (Emerald Imperium's author), PurrfectDoodle, RHcks (commissioned by darklight177), Kasen,
  Galaxeeh and PurpleZaffre. Wallace, Maxie, Archie and Wally use Emerald's sprites.

### Tools
- `tools/crystal_imperium/side_battles.py` and `side_sprites.py` generate the side battles and
  their sprites' entries, with checks: each trainer stands on land, can be walked up to and blocks
  no path, a reward's TMs and Mega Stones aren't on sale yet, the sprites fit the GBA's formats.
- `tools/emurun`: `waituntil8`, and `yes_no()` in `emu.py` to answer a YES/NO box once it is up.
  `probe.py` compiles under `build/emurun/probe/` instead of `src/`, where a build running at the
  same time as the tests picked its file up and failed to link.
- New play test `side_battles`.

## 0.13.0-experimental (2026-10-27)

### Quality of life
- **Faster battles** (DECISIONS.md D38). A trainer battle against one Pokémon takes about a third
  less time, with nothing left out:
  - The battle no longer spends a frame on each step of its scripts, and no longer waits for a
    Pokémon's cry to end before going on.
  - With **FAST BATTLES** (START > OPTION > BATTLE, on by default): the battle's intro, move
    animations and the Pokémon's own animations play at double speed; a hit Pokémon blinks
    twice instead of four times; the HP bar and trainers sliding in move twice as fast; and
    messages like "fainted!", "gained Exp. Points!" or "You got ¥… for winning!" go on by
    themselves after a moment (A or B still goes on at once). A trainer's words still wait for
    you.
  - **"X used Y!" at once** (with FAST BATTLES): the message appears whole instead of letter by
    letter, and animations no longer wait for their last sound to end, at the start or at the end
    (a stat change's "Attack fell!" comes half a second sooner).
  - **A chosen move starts at once** (DECISIONS.md D40). The steps between picking a move and
    the Pokémon moving (the choice confirmed, the turn order, the move's checks, "X used Y!")
    now share frames: the move's animation starts 3 frames (a twentieth of a second) after you
    pick it, against 46 in 0.12.0, and the next Pokémon's move starts 3 frames after the first
    one's HP bar stops. A turn of two moves takes 211 frames from your choice to the next menu
    (0.12.0: 489). The shared frames work with FAST BATTLES off too.
  - With FAST BATTLES, the animations' colour changes (a darkened background, a flash, poison's
    purple pulse) play at the same double speed as the rest of them, Growl-type cries no longer
    hold the battle until they end, "fainted!" and "gained Exp. Points!" go on after about 0.4 s
    (A or B still at once), a Pokémon sent out during the battle (a trainer's ball tray, the ball,
    the health box sliding in) plays at double speed, and the Exp. bar fills as its sound starts.
    Knocking out a trainer's Pokémon and seeing the next one sent out takes a third less time.
  - **The battle's menus no longer freeze the game** (FAST BATTLES or not): the moves take input
    5 frames after FIGHT (10 before), each turn's action menu comes 4 frames sooner, and going
    back from the moves with B pauses 1 frame (5 before). They look exactly as before.
  - **FAST INTRO** (no slide-in at the start of a battle) is on for new games.
  - Saves from earlier versions get FAST INTRO and FAST BATTLES turned on once. Turn either off
    in START > OPTION > BATTLE for the classic pace; TEXT SPEED FASTER prints text almost at once.

### Pokémon
- **Emerald Imperium's and Radical Red's move pools** (DECISIONS.md D39). Level-up moves and Egg
  Moves were already Radical Red's (0.11.0); now TMs and tutor moves are too:
  - Each Pokémon learns the TMs and tutor moves Radical Red teaches it: TYPHLOSION gets Aura
    Sphere and Mystical Fire, but no longer Shadow Ball or Body Slam. TMs and tutor moves Radical
    Red doesn't have work as before. Pokémon keep the moves they already know.
  - Radical Red's other TM and tutor moves are tutor moves here, in the move relearner (party
    menu > LEARN MOVES > TUTOR MOVES): Cosmic Power, Hone Claws, Toxic Spikes, Uproar and
    Celebrate, and after the Hall of Fame Draco Barrage and Dark Hole (Emerald Imperium's
    postgame TMs).
  - **Radical Red's own moves**: Aqua Fang (Gyarados, Feraligatr, Sharpedo...), Dark Hole
    (Darkrai, and a tutor move), Soul Robbery (Mewtwo), Sonic Slash (Ninjask), Draco Barrage
    (Tropius, Hydreigon, Kommo-o, Guzzlord, and a tutor move for most Dragons) and Forbidden
    Spell (Unown, Chimecho), with their effects: Draco Barrage hits Fairy-types, uses the
    stronger of Attack and Sp. Atk and hurts the user; Forbidden Spell calls one of eight moves.
  - Imperium's changes: Jirachi learns Moonblast, Dragapult Shadow Claw, Galarian Moltres Trick
    Room, and Dusclops and Dusknoir Amnesia.
  - Terapagos follows Radical Red's (its Terastal Form's) list too, and female Basculegion has a
    list of its own, as in Radical Red.

### Fixes
- The move relearner's TM MOVES list held 60 moves. With most TMs in the Bag, opening it for
  MEW, or any Pokémon that learns more than 60 of them, could crash the game; it now holds all
  206 TMs and HMs.
- The party menu showed only three entries for a Pokémon that had nine (a lead with LEARN MOVES,
  three field moves, SWITCH, ITEM and FOLLOWER: one more than the menu held), and B then froze
  the game. It now shows all nine (since 0.4.0).
- The summary screen's START (relearn moves) opened the kind of moves last used in the party
  menu's relearner, often an empty list; it now opens one the Pokémon has moves in, and leaves
  the one set before as it was (so Blackthorn's Move Tutor teaches level-up moves even after a
  summary was opened from its PC).

## 0.12.0-experimental (2026-10-26)

### Quality of life
- **Emerald Imperium's care packages** (DECISIONS.md D16). Imperium's are Radical Red's: 10 of
  nearly every held item, Berry, booster and evolution item, and big stacks. About 6,500 items in
  all now, against about 2,500 before.
  - A **starting package** from PROF. ELM as soon as you have a Pokémon, as Imperium's from PROF.
    BIRCH: the Shiny Charm, 153 Quick Balls, 10 of every type-boosting item and every type-resist
    Berry, and 10 Leftovers, Focus Sashes, Eviolites and more.
  - The **badge packages** follow Radical Red's, 10 of each item: 50 Heal Balls after the first
    badge, 153 Ability Capsules and 153 Ability Patches after the second, 50 Dream Balls and the
    Choice items after the third, 153 PP Max after the sixth, 100 Beast Balls for the Champion.
  - **Nine location packages** wait along the story, each with a theme: the weather Rocks in Union
    Cave, Light Clay and the Herbs in Ilex Forest, the Choice items in the National Park, the Orbs,
    Assault Vests and Heavy-Duty Boots in the Burned Tower, and more in the Lighthouse, Mt. Mortar,
    the Lake of Rage, the Ice Path and Victory Road.
  - When the Bag and the PC are both full, a package waits for room instead of losing items.
  - Saves from earlier versions get every package they already received again, with the new
    contents, and the location packages for places they are past.
- **Emerald Imperium's cheat codes at the NES** in your room (DECISIONS.md D37): "Enter a code?",
  then type it, in any case. **MEGA** gives the Mega Ring and every Mega Stone (47), **MAXMONEY**
  (MMY) the most money, **CAUGHTALL** (CAL) every Pokémon caught in the National Pokédex,
  **EZCATCH** (EZC) switches Easy Catch, **SHINYS** (SHS) makes PROF. ELM's Pokémon shiny,
  **MONO** lets you pick a type for PROF. ELM's three Pokémon (Imperium's monotype starters),
  **SHINYR** (SHR) makes the roaming Pokémon shiny, and **DEXALL** (DXA) is always on already.

### Fixes
- The Goldenrod Mega Specialist no longer sells Staraptite: Mega Staraptor isn't in this game, and a
  Staraptor holding the stone could Mega Evolve into a missing species (DECISIONS.md D9).
- The care packages and the MEGA code keep 20 slots of the Bag's items pocket free for the
  story's one-time gifts, such as the Plates, by sending new items to the PC while it has room.

## 0.11.0-experimental (2026-10-25)

### Pokémon
- **Emerald Imperium's abilities and movesets** (DECISIONS.md D35). Imperium takes its Pokémon
  data from Radical Red, so every species both games have now has Radical Red's abilities, level-up
  moves (evolution moves included) and Egg Moves, with Imperium's own changes (Blaziken's line has
  Blaze and Early Bird instead of Speed Boost and learns Thunderous Kick, Latios and Latias learn
  Memento and Healing Wish at 71). That is 1,098 learnsets, 415 Egg Move lists, and new abilities
  for 491 species: Pidgey has Frisk and No Guard, Spearow Technician, Golbat Infiltrator, Sniper
  and Corrosion. The few abilities and moves Radical Red made itself aren't in this engine: that
  ability slot keeps a Heart & Soul ability, and those moves are left out. TM compatibility, base
  stats and types are unchanged.
- Pokémon in a save keep their ability slot, so they take the new ability of that slot.
- 50 trainer Pokémon had an ability their species no longer has; each gets the one now in its
  slot (Falkner's Pidgey: No Guard).

### Quality of life
- **A TM clerk in every Poké Mart** (D36), behind the counter next to the clerk, in all 13 marts and
  at the Indigo Plateau. Their stock grows with every badge: 71 TMs with none, 115 with one, 155,
  173 (Ice Beam, Thunderbolt and Flamethrower with three, as in Imperium), 178, 181, 191, 196, and
  all 198 with eight. ¥100 each. The Goldenrod Dept. Store 5F and Celadon's TM counter sell the same.
  The Violet City clerk now sells from the start and still gives its four TMs with the Zephyr Badge.
- **Bigger badge packages** (D16): everything comes in stacks, enough for a whole team. That
  means 10 of each type-boosting item (10 Charcoal, 10 Mystic Water, 10 Miracle Seed in the first),
  10 Sitrus and Lum Berries, 5 of each type-resist Berry, 3 to 5 of each staple held item
  (Leftovers, Life Orb, Focus Sash, Eviolite, Assault Vest, ...) and 20 Poké Balls. The packages
  hold 2,541 items now, up from 1,650. A save that already has some packages gets the rest of each,
  one per step ("PROF. ELM sent more of the gear from an earlier package!").

### Fixes
- **The summary shows the nature set with the Training Kit.** It showed the nature the Pokémon
  was born with, while its stats (and the summary's red and blue stat names) followed the new one.
- In shops, a TM you have shows OWNED; SOLD OUT ran into long TM names ("TM01 FOCUS PUNCH").

### Tooling
- `tools/crystal_imperium/imperium_species.py` writes the Imperium species data from the Radical
  Red dex's data file (`--rr-data`, not kept in the repository; `--report` lists what was left
  out). `validate.py` reads the new abilities.
- New tests `summary_nature` (fails on 0.10.1) and `tm_clerks`. `care_packages` checks
  quantities and the top-up for older saves; `tm_shop` and `tm_clerk` check the per-badge lists.
  `emurun` gains `expectqty16` (Bag quantities, which the game stores XORed with a key) and
  `expectsame32`.
- With the new learnsets, Pokémon given from the debug menu know other moves, so `bugsy` gives its
  six the moves a player would have kept, with Sturdy for Geodude and Onix (10 of 40 wins on mGBA,
  5 on VBA-M); `falkner`'s Mareep keeps Tackle; `relearner_training_kit` teaches Fury Swipes step by
  step. All 51 play tests and the old-save test pass on mGBA and VBA-M (TESTING.md).
- 0.10.1 was checked with `battle_healthbox_names` and the battle tests; this is the first full
  run since 0.10.0.

## 0.10.1-experimental (2026-10-25)

### Fixes
- **Battle health box names** (DECISIONS.md D26). After a switch, a shorter name kept the end of
  the longer one before it ("LARVITAR -|" after FERALIGATR, reported on Delta). The Black/White
  battle interface fits a name into 7 tiles but cleared only 6 of them first; now it clears all 7.

### Tooling
- New test `battle_healthbox_names` (it fails on the 0.10.0 ROM). `emurun` gains `snaprect` and
  `expectrect`, which compare a rectangle of the screen with the same rectangle earlier.

## 0.10.0-experimental (2026-10-25)

### Fixes
- **The start menu fits on the screen again** (DECISIONS.md D34). With the Pokédex and the
  Pokégear it had nine entries and EXIT ran off the bottom; the screen has room for eight. The
  DexNav moved to the new L menu.

### Quality of life
- **The L menu, after Emerald Imperium's** (D34). Press **L** in the field for:
  - **POKéVIAL**: heal the party.
  - **PC**: a Pokémon Center's whole PC (Pokémon boxes, item storage, challenges).
  - **DEXNAV**: B in it comes back to the L menu. Pressing L during a DexNav search ends it
    and keeps the chain.
  - **TIME**: MORNING, DAY, EVENING or NIGHT moves the clock forward to 8:00 AM, 12:00 PM,
    6:30 PM or 8:00 PM (the next day if that time has passed; the clock never goes back). The
    map reloads where you stand, so the light, the Pokémon seen by day or by night and the
    people who come at certain times follow at once.
  - **STATS**: the Training Kit (nature, ability) and a new **IVs & EVs** editor, Emerald
    Imperium's Stat Editor. A window shows each stat's IV, EV and value, Hidden Power's type and
    the EVs used; the d-pad picks one, A changes it (UP/DOWN by 1, LEFT/RIGHT by 10), START
    sets every IV to 31. EVs stop at 252 a stat and 510 in all. With Minimal Grinding on (the
    default) every Pokémon battles at 31 IVs and 0 EVs, so, as in Imperium, the EVs are locked
    and the IVs only set Hidden Power's type.
  - **REPEL**, **FOLLOWER** and **AUTO RUN** switches, green when on.
  - The clock and the time of day at the top right.

  It opens once you have a Pokémon, but not in link rooms, the Safari Zone, the Bug Catching
  Contest or the Battle Pike and Pyramid, nor with BUTTON MODE L=A (L is the A button then).
- The Training Kit in the bag has the IVs & EVs editor too.

### Tooling
- New tests `l_menu`, `l_menu_time`, `stat_editor` and `stat_editor_mgm`; `dexnav` checks that
  L ends a search and keeps the chain, and every DexNav test opens it from the L menu, as does
  `old_save_test.sh`. `emurun` gains `expectbits8/16/32` (bitfields); `emu.py` gains `l_menu`,
  `set_save2`, `set_save3`, `expect_follower`, `expect_battler_ivs` and `new_game(minimal_grinding=False)`.

## 0.9.0-experimental (2026-10-25)

### Quality of life
- **Quick Rare Candies** (DECISIONS.md D33). After choosing the Pokémon, pick how many to use;
  at first it's all of them up to the level cap (UP/DOWN change it by 1, LEFT/RIGHT by 10, B
  goes back). They are used at once, with one message and a short sound instead of the level-up
  jingle, so the map music keeps playing, and without the two stat pages. Moves of every level
  passed are still learned, then the Pokémon evolves; the party menu stays open.
- **Fast Egg hatching** (D32). An Egg cycle is 8 steps instead of 256: a Togepi Egg hatches in
  about 90 steps, a starter's in about 170. Flame Body and Magma Armor still halve it.

### TMs, the Emerald Imperium way (D22)
- **Every TM costs ¥100**, Imperium's price, in every shop (they were ¥1,500–8,000). The
  Goldenrod Dept. Store's badge tiers still decide when the strong ones go on sale.
- **A TM clerk in the Violet City Mart** (the second clerk at the counter), from the Zephyr
  Badge on: Imperium's first vendor TMs, Electroweb, Icy Wind, Aerial Ace, Low Kick, Pluck,
  Snarl and Smack Down. The first time, the clerk also gives Bullet Seed, Bulldoze, Bug Bite and
  Stomping Tantrum, the TMs Imperium gives away before its second Gym; a save that already has
  the badge gets them too.

### Tooling
- New tests `rare_candy`, `egg_hatch` and `tm_clerk`; `qol_items` follows the Rare Candy
  question. `emu.py` gains `give_egg` and `expect_item_price`.

## 0.8.1-experimental (2026-10-25)

### Fixes
- **DexNav works in Dark Cave after Flash** (DECISIONS.md D31). It said it was too dark to
  search even after Flash, because Flash only widened the lit circle. Flash now lights the
  whole cave, as in Gold, Silver and Crystal. A save made in Dark Cave after Flash continues
  fully lit.
- **The DexNav Pokémon no longer runs away in caves and on water** (D31). It moved to another
  tile, up to twice, as you came close. Now it stays where it appeared, as in grass.

### Tooling
- New tests `dexnav_caves` (Dark Cave before and after Flash, a save made there before 0.8.1,
  Union Cave) and `dexnav_surf` (a DexNav search while surfing). Both fail on the 0.8.0 ROM.
- The play tests' path finding follows the target's elevation, so it doesn't route through
  water; `emu.py` has `set_save1` and `expect_save1` for SaveBlock1 fields.

## 0.8.0-experimental (2026-10-25)

### Gameplay
- **Emerald Imperium-style level caps** (DECISIONS.md D29): the cap is 85 before you beat the
  Elite Four the first time, as in Emerald Imperium, and climbs to it gym by gym:

  | Stage | No badges | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 (Elite Four) | Kanto | After the Kanto League |
  |---|---|---|---|---|---|---|---|---|---|---|---|
  | NORMAL caps | 15 | 24 | 33 | 42 | 50 | 58 | 66 | 75 | 85 | 90 | none (100) |
  | HARD caps | 12 | 21 | 30 | 39 | 47 | 55 | 63 | 72 | 85 | 90 | none (100) |
  | 0.7.x NORMAL | 11 | 16 | 21 | 25 | 31 | 36 | 38 | 45 | 56 | 70 | none |

  Every boss is at the cap (D21), so Falkner is 15, Clair 75, the Elite Four and Lance 85, the
  Kanto Gym Leaders and Blue 90, and Red stays at 100.
- **Other trainers follow the new curve.** Heart & Soul's trainers were made a few levels below
  its old caps; at battle time their levels are mapped onto the new caps in proportion (a
  Rocket Grunt's level-20 Koffing is 31 now; on Routes 26 and 27, the way to the Indigo
  Plateau, trainers go from 42–50 to 71–80). EASY and HARD still scale them by 10%, and none is
  above your cap.
- Wild Pokémon keep Heart & Soul's levels, as in Emerald Imperium: catch them and use the Rare
  Candy Box to bring them up to the cap. They are never above the cap.
- **Every Gym Leader has six Pokémon** (D30), and so do the rival from his second battle on, the
  Rocket executives in all their battles and Eusine. Falkner adds Natu, Fletchling and Murkrow
  to Heart & Soul's three; Bugsy has an Imperium-style team (Ariados, Pineco, Ledian,
  Butterfree, Yanma, Scyther); Whitney adds Furret and Girafarig and her team holds items;
  Morty adds Mimikyu; Chuck, Jasmine and Pryce bring all six as the 5th Gym too; Eusine has a
  rain team.
- **Route mini-bosses, as in Emerald Imperium** (D30): 28 trainers on the routes, 16 in Johto
  and 12 in Kanto, now have competitive teams at your level cap: held items, natures, abilities
  and chosen moves, themed by their class (a Hiker's Rock types, a Swimmer's rain team), with
  the smart boss AI. They have 3 Pokémon on the first routes, up to 6 later on and in Kanto.
  BALANCE.md lists them.

### Tooling
- `GetLevelOnCapCurve` (`src/caps.c`) maps a Heart & Soul level onto the current cap curve;
  `boss_teams.py` has the six-Pokémon teams and the route mini-bosses (`ROUTE_BOSSES`), 126
  bosses in all. `validate.py` reads a form's learnset from its base species when the form has
  none of its own.
- New test `route_bosses` (every mini-boss's team size and levels at the cap, and a battle to a
  result). Tests follow the new levels; `bugsy` and `whitney` bring six Pokémon (`bugsy` with
  the first care package's Charcoal and Eviolites, in 40 tries; `whitney` in 24), `whitney`'s
  Pokémon keep moves a player at 33 would keep (the default movesets at 33 drop Quilava's Fire
  moves), and `bosses_m5` checks Blue's Mega with the six built for him and gives each Kanto
  leader up to three battles to bring out the Mega.

## 0.7.1-experimental (2026-10-25)

### Gameplay
- **Bosses are at your level cap, HARD caps included** (DECISIONS.md D21). Every boss Pokémon
  is at the cap from your own LEVEL CAP setting: NORMAL (11, 16, 21, 25, 31, 36, 38, 45, 56,
  then 70) or HARD (8, 15, 20, 23, 29, 33, 37, 42, 54, then 70), on every difficulty. 0.7.0 used
  the NORMAL caps whatever the setting and added HARD's 10%, so with HARD caps Falkner was 12
  against your cap of 8; now he is 8. EASY no longer lowers bosses either (Falkner 11 with
  NORMAL caps); it still lowers other trainers by 10% and takes their items away.
- **Nothing is above your level cap** (D28). DexNav's level bonus (a fifth of the DexNav chain,
  and in 4% of searches 10 more) could give a Pokémon above the cap, such as a level-12 Turtwig
  at a cap of 8. Every Pokémon you meet or are given is now held at the cap:
  - DexNav (the level in the search window too), random encounters, fishing, Rock Smash, mass
    outbreaks, scripted wild battles, legendaries (e.g. Zapdos, 50, is met at 11 with no badges),
    roaming Pokémon, and gifts such as the Cianwood fisher's level-25 Tentacool.
  - Other trainers: their levels (after EASY's or HARD's scaling) are held at your cap. E.g. a
    Rocket Grunt's level-20 Koffing is 11 if you meet him with no badges (8 on HARD caps).
  - Wild battles where catching is off too: Route 41's level-100 Tentacruel and the post-game
    wild bosses (up to 100) are at the cap if you meet them before it reaches their level.
  - Levels are only ever lowered, never raised, and nothing changes with LEVEL CAP OFF.
- The challenge menu's descriptions say so: LEVEL CAP lists each table's caps ("Bosses are at
  the cap."), and EASY and HARD say their ±10% leaves bosses alone.

### Tooling
- `boss_teams.py` writes each boss's stage into `src/data/level_cap_bosses.h`; the battle
  computes the boss's level from the player's cap table (`GetBossLevel`, `src/caps.c`).
- Harness: `new_game(level_cap=...)` picks LEVEL CAP in the Difficulty tab.
- New test `level_cap_wild` (DexNav with a chain of 100, a level-50 outbreak, Zapdos and the
  Tentacool gift at the cap, on NORMAL and HARD caps). `boss_levels` adds HARD caps (Falkner at
  8, Petrel at 29 and 37) and a Grunt held at the cap; `difficulty` checks that EASY and HARD
  leave Falkner at the cap and scale Youngster Albert.

## 0.7.0-experimental (2026-10-25)

### Gameplay
- **Every boss Pokémon is at the level cap** (DECISIONS.md D21), not just the ace: every Gym
  Leader (all versions and rematches), the rival, Team Rocket's executives, Eusine, the Kimono
  Girls, the Elite Four, Lance, Blue and Red. Each battle's level is the NORMAL cap of the
  earliest point it can happen: 11 for Sprout Tower, Falkner and the first rival battle, then
  16, 21, 25, 31, 36, 38, 45 and 56 up to the Johto League, 70 for Kanto (the Kanto leaders,
  Blue, the Fighting Dojo rematches, the Kanto League) and 100 after the Kanto League (Red and
  every rematch then). With the Rare Candy Box you can always match a boss, never out-level it.
  - A boss fought later than its earliest point is raised to your cap when the battle starts:
    the Rocket Hideout with five or six badges (36 or 38), and the Kanto Gym teams in the
    Fighting Dojo or the Elite Four's rematch after the Kanto League (100). EASY and HARD
    still scale the result to 90% and 110%.
  - Petrel and Ariana in the Rocket Hideout are at 31 if you go there with four badges (the
    Lake of Rage needs Surf, the 4th badge's move); 0.6.0 had them at 34–36.
  - Red: all six at 100 in both battles (0.6.0: 96–100). He stays the hardest battle: the
    only Pokémon with EVs under Minimal Grinding, four Full Restores, prediction AI (D27).
- **Care packages are full of battle gear, Emerald Imperium-style** (D16). The 17 packages now
  hold 287 entries: competitive held items with the staples several times over the game
  (Leftovers ×7, Focus Sash ×8, Life Orb ×5, Assault Vest ×5, Heavy-Duty Boots ×5, Choice
  Band and Choice Specs ×3 each, Choice Scarf ×4, Weakness Policy ×3, Booster Energy ×4 and
  dozens more), all 18
  type-boosting items, all 18 type-resist Berries and the pinch Berries, 35 Sitrus and 19 Lum
  Berries, **93 PP Max** and 8 PP Up, X items, Max Elixirs, Elixirs and Max Ethers, besides
  the balls, healing and evolution items they had.
  - A package lists its contents in one message (two lines a page) instead of one message per
    item. An item whose Bag pocket is full goes to your PC, and you're told.
  - **Continuing an older save?** The gear for the packages you already received arrives too,
    one package per step out on a route or in a town ("PROF. ELM sent the battle gear an
    earlier package didn't have!").

### Tooling
- `tools/crystal_imperium/boss_teams.py` gives every boss a stage and sets its levels from
  `src/caps.c`; Heart & Soul's own boss teams get only their levels (`LEVEL_ONLY`). It also writes
  the boss list the battle code uses (`src/data/level_cap_bosses.h`).
- `tools/crystal_imperium/care_packages.py` writes the care package script from a table (item
  names and line widths come from the game's own data); CI checks it with `--check`. New var
  `VAR_CARE_PACKAGE_GEAR` (0x40E5) for the catch-up.
- `validate.py`: every boss at its stage's cap, no boss trainer missing from the list (Lt.
  Surge's teams were not matched by the boss patterns before), and Red's guard now asks for
  the most Full Restores, since the post-League rematches are at 100 like him.
- Harness: `fill_pocket`, `expect_pc_has`, `no_care_packages` (marks the packages and their gear
  as received, for tests that mustn't be interrupted); `prepared_team(level, items=True)` holds Life Orb,
  Leftovers, Choice Specs, Focus Sash, Choice Band and Expert Belt, all from the first three
  care packages.
- New test `boss_levels` (a boss raised to the cap with six badges and after the Kanto League;
  a Grunt unchanged). `care_packages` checks the new gear, the PC fallback and an older save
  catching up. The boss samples' teams hold items from the care packages the player has by then:
  the prepared six in `bosses_m3`, `bosses_m4` and for Koga, the planned sixes for Will, Bruno,
  Karen and Lance (Bruno and Karen now 12 tries), Bugsy's naive four a Charcoal (12 samples) and Whitney's
  Machop an Eviolite (24 samples). Chuck and Pryce are fought by sixes built for them with a game
  plan (the prepared six won once in 16 against Pryce). `bosses_m4` checks Archer's and the
  rival's Megas with a level-100 six, since at the cap the six can lose before the ace comes out;
  `bosses_m5`'s Janine check no longer leads with Earthquake against Levitate Weezing. `red`
  takes 24 tries (it won 5 and 2 of 12). `difficulty` and `red` expectations follow the new
  levels.

## 0.6.0-experimental (2026-10-24)

### Gameplay
- **HARD plays by Emerald Imperium's and Radical Red's rules.** On HARD every battle uses the
  SET style, so the game never asks "Will you switch Pokémon?" after you knock one out, and
  the Bag can't be used in trainer battles ("Items can't be used now."). Wild battles keep the
  Bag. START > OPTION shows BATTLE STYLE as SET, grayed out. HARD still raises trainer levels
  by 10% and uses HARD level caps. EASY and NORMAL are unchanged.
- **A Gen 5 look:**
  - **Battles** use mudskip's Black/White-style interface: BW healthboxes and text box,
    FIGHT / BAG / POKÉMON / RUN buttons, a move box with each move's type, PP and
    effectiveness, the party-ball bars and ability pop-ups.
  - **The summary screen** is RavePossum's Black/White-style one: a scrolling background, the
    Pokémon with a shadow and idle animation, Gen 5 type and status icons and move
    categories. A on the skills page cycles stats, IVs and EVs. START on the moves pages opens
    the move relearner, as before.
  - Move info in battle is on L (the BW box labels it L; Heart & Soul used START). R still
    toggles Mega Evolution, and throws the last-used ball from the action menu.
  - Moves can no longer be reordered with SELECT during a battle (Gen 4 and later behave this
    way, and the BW interface needs it); reorder them on the summary screen.
  - The options menu's BATTLE UI row (Heart & Soul's GEN 3 / GEN 4 healthboxes) is gone; the
    BW interface replaces both.
- **Red is the hardest battle in the game** (DECISIONS.md D27):
  - Levels 96–100 (the rematch after the Sinjoh story: all 100). Pikachu has Light Ball,
    Espeon Life Orb, Snorlax Leftovers, Venusaur Life Orb, Blastoise White Herb and Charizard
    Charizardite Y.
  - Competitive EVs on all six, and his are the only Pokémon that keep their EVs under
    Minimal Grinding.
  - The boss AI with move and switch prediction, and four Full Restores.
  - A sun team: Mega Charizard Y's Drought powers Chlorophyll Venusaur and Solar Beam.
  - He battles only the Kanto Champion: before the Kanto League he waits ("RED seems to be
    waiting for the KANTO CHAMPION."), so the level cap is gone when you fight him.

### Technical
- The heap is 8 KB larger (EWRAM 99.12% used): the BW battle windows take about 8 KB more
  during a battle, and without it boss battles that decompress big graphics mid-battle ran
  out of memory in the play tests. The Wild Variety pool shrank to the 567 Pokémon it holds.

### Tooling
- emurun: `waituntil32` runs until a value matches (e.g. the battle controller reaching the
  action menu), tapping a key meanwhile; `dump` writes memory to a file (the heap dump found
  the out-of-memory cause). Harness: `expect_battle_style`, `expect_window`.
- The battle autopilot can play a **game plan** (`plan=` in `autobattle`): for each of the
  opponent's Pokémon, which of yours attack it with which move, and which to switch in when
  the one out has none. `hold_item` gives a party Pokémon a held item; `sample_battle` takes
  a plan and a frame limit.
- Autopilot fixes: a forced switch compared menu slots (battle order) with party slots (field
  order) and could keep choosing a fainted Pokémon until the battle timed out; it now finds
  Pokémon by personality value and never retries a slot the game refused. A move the game
  refuses (Choice lock, Taunt, Encore) no longer stalls a battle.
- New tests: `hard_mode_rules`, `bw_ui`, `red`; `dexnav_wild_match` checks the variety pool's
  size. The boss samples got more tries, sized by measured win rates (`bosses_m3`: 8, Pryce
  16; Lance 24). Will, Bruno, Karen, Lance (`bosses_e4`) and Blue (`bosses_m5`) are fought by sixes
  playing a game plan. Red moved from `bosses_m5` to `red`. `validate.py` checks that Red's
  parties stay the strongest in the game.

## 0.5.1-experimental (2026-10-24)

### Fixes
- **DexNav's lists now match the wild Pokémon you meet.** Before, Wild Variety turned 30% of
  encounters into a random pick from about 445 Pokémon that DexNav couldn't list (on Route 29
  at night DexNav showed Hoothoot and Rattata while 6 of 12 test battles were other Pokémon),
  and with the randomizer on for wild Pokémon DexNav showed the unrandomized ones (12 of 12
  battles unlisted).
  - Wild Variety now gives each area a set for the day: up to six Pokémon in the grass and
    three Water-types on the water, in the DexNav row's free slots, evolved for the area's
    highest level. Variety encounters (still 30% by default, 5% per Pokémon in the grass) are
    one of the set, and DexNav lists the set after the area's own Pokémon. The sets change at
    midnight and differ between saves.
  - With the randomizer on and MAP SEEDED on, DexNav lists each slot's randomized Pokémon.
  - A mass outbreak's Pokémon is listed in the grass.
  - Fishing's variety Pokémon come from the water set. DexNav's detector finds what an
    encounter would turn up, and the caught-all marks count the variety Pokémon.
  - After becoming Champion, about a quarter of the day's sets end with a Legendary, Mythical,
    Ultra Beast or Paradox Pokémon (Water-types on the water), instead of 3% of variety
    encounters everywhere.
  - DECISIONS.md D24.

### Tooling
- emurun: `snap16` remembers a list of values (a DexNav row) and `tallynotin` checks against
  it (`@LIST`). Harness: `snap_dexnav_rows`, `fish_sample`, `set_save`, `expect_listed`,
  `new_game(random_wild=True)`.
- New tests: `dexnav_wild_match`, `dexnav_water_match`, `dexnav_randomizer`; `wild_variety`
  checks that DexNav lists no variety Pokémon with WILD VARIETY off.

## 0.5.0-experimental (2026-10-24)

### Gameplay
- **Smarter trainers:** on NORMAL and HARD every trainer uses the smart AI (it knows your
  team, picks the best move, switches smartly and plays around HP). EASY keeps the old AI.
- **Imperium-style bosses for the whole story:** Proton, Petrel, Ariana and Archer; every rival
  battle from Azalea to Victory Road; Morty, Chuck, Jasmine, Pryce (all three versions each)
  and Clair; the Kimono Girls; the Elite Four and Lance; the eight Kanto leaders, Blue and Red.
  Aces at the level cap (70 in Kanto; Red's is 90), full held items, natures, abilities and
  competitive moves. Every Gym Leader from the 5th Gym on, Archer, the rival on Victory Road,
  the Elite Four, Lance, Blue and Red Mega Evolve (Heracross, Steelix, Abomasnow, Altaria,
  Houndoom, Tyranitar, Alakazam, Beedrill, Lucario, Absol, Gyarados, Aerodactyl, Blastoise,
  Manectric, Venusaur, Gengar, Metagross, Camerupt, Pidgeot, Charizard Y).
- **Emerald Imperium's TMs:** 198 TMs. TM01–TM172 are Emerald Imperium's list in its order
  (all but its two custom moves, Dark Hole and Draco Barrage), TM173–TM198 the Heart & Soul
  TMs Imperium lacks. 28 TMs have a new number (TM03 Water Pulse is TM160, TM41 Torment TM179,
  TM70 Rock Climb TM192, TM92 Trick Room TM106, ...); the rest keep theirs.
  - The TM case holds all 198 TMs and 8 HMs, and each TM's description is its move's.
  - The Goldenrod Dept. Store 5F sells every TM: 71 from the start (including Heart & Soul's
    own stock, now cheaper), 155 from 3 badges, 178 from 6, all 198 from 8. Shop lists show
    each TM's move next to its number, as the bag does.
- **HMs without teaching:** carrying an HM, with its badge, is enough for any Pokémon in the
  party to use the field move (Cut, Surf, Strength, Rock Smash, Waterfall, Fly and Flash from
  the lead's party menu). Before, the Pokémon had to be able to learn the move.
- The Mega Stone shop's 6-badge tier counts badges (it unlocked with Jasmine's badge).
- Falkner's Rookidee knows Rock Smash instead of Steel Wing, which it can't learn.

### Fixes
- Teaching a move from the party menu's relearner (LEARN MOVES > TM MOVES) used up the TM even
  with REUSABLE TMS on.

### Save compatibility
- The TM case moved from SaveBlock1 to EWRAM, saved as counts in SaveBlock3. Saves from Heart &
  Soul 2.0.6 and earlier Crystal Imperium builds load: their TMs keep their moves (Heart &
  Soul's TM70 Rock Climb becomes TM192), including TMs in the item PC and held TMs.

### Tooling
- `tools/crystal_imperium/boss_teams.py` holds the boss teams; `validate.py` checks their
  moves are learnable and their aces sit at the cap, and resolves abilities given by macros.
- `tools/crystal_imperium/tm_list.py` holds the TM list and writes the TM constants, the item
  data (with descriptions wrapped to the bag box by glyph width), the shop lists and the old
  numbering for save conversion.
- Harness: Pokémon (Complex) from the debug menu, a prepared team for winnability checks,
  battles by trainer constant, `expectseen` for Mega forms; the autopilot skips moves with no
  PP. `set_var`, `fill_tm_case`, `save_and_continue`; bag checks read the TM case in EWRAM.
- New tests: `bosses_m3`, `bosses_m4`, `bosses_e4`, `bosses_m5`, `tm_case`, `tm_shop`,
  `hm_field_moves`.
  `tm_reusable` also teaches through the relearner; `old_save_test.sh` now saves Heart & Soul
  TMs and checks their conversion.
- `data/battle_anim_scripts.s` read the vanilla TM list (`IS_HNS` was undefined there), which
  only mattered once the TM list changed; `constants/tms_hms.h` now defines it for every user.

## 0.4.1-experimental (2026-10-24)

### Gameplay
- **DexNav shows every Pokémon on its main screen**, seen or not: no more question marks. Any
  of the area's Pokémon (land, water and hidden rows) can be registered with R and searched
  for with A right away. The top bar now reads SELECT: ALL, for the list of every Pokémon.
  A hidden Pokémon detected while walking still shows ??? until R is pressed or the player
  gets close.
- **DexNav searches no longer fail with "The Pokémon got away! Try moving more slowly."**
  Walking, running (Auto Run included) and biking all reach the Pokémon; sneaking with A is
  optional. Before, walking normally within 2 tiles or running/biking within 4 tiles scared
  it off, and with Auto Run on there was no way to sneak. A search now lasts 30 seconds
  (was 15).

### Tooling
- `dexnav` registers, searches for and catches a Rattata that has not been seen, walking up
  to it normally. `dexnav_any` turns Auto Run on and runs up to the Charmander it searched
  for. Both failed with "Try moving more slowly" before the fix.

## 0.4.0-experimental (2026-10-24)

### Gameplay
- **Key items from the first step:**
  - Rare Candy Box (unlimited Rare Candies, capped by the level cap; also without a Nuzlocke).
  - Infinite Repel (now an on/off switch that works).
  - Pokémon Box Link (the PC anywhere).
  - **Training Kit:** change a Pokémon's nature or cycle its ability any time.
  - **PokéVial:** full party heal outside battle, never runs out.

  Older saves receive whichever of them they lack on Continue.
- **DexNav** in the start menu from the first step:
  - Area lists with three **hidden Pokémon** per area; hidden Pokémon are also detected while
    walking.
  - Search levels and chains; R searches for the registered Pokémon.
  - **SELECT lists every Gen 1–9 Pokémon** (all 1,074: every evolution stage, regional
    forms, Legendaries), and any of them can be searched for in any area with wild Pokémon,
    at that area's levels. LEFT/RIGHT jump 100 entries.
- **Wild Variety** (Features tab, 30% by default): that share of wild encounters are any
  Gen 1–9 Pokémon, evolved as far as their level allows. Legendary and Mythical Pokémon join
  Wild Variety's random encounters after becoming Champion.
- 258 evolution families that had no source in the game now appear as hidden Pokémon on 249
  maps.
- **Easy Catch** (Features tab, on by default): every Poké Ball catches.
- **Difficulty selection** (Difficulty tab): EASY (trainer levels −10%, no trainer items),
  NORMAL, HARD (trainer levels +10%, HARD level caps).
- **Milestone care packages** from Prof. Elm after each badge and after becoming Champion,
  with supplies and every evolution item the game had nowhere: Linking Cord, Upgrade,
  Prism Scale, Sachet, Whipped Dream, Sun Stones, Apples, Sweets, Pots, Teacups, Armors,
  Leader's Crest, Metal Alloy, 999 Gimmighoul Coins, Scrolls.
- **Move relearner** in the party menu (level-up, egg, TM and tutor moves).

### Fixes
- DexNav no longer fails at random in small patches of grass.
- Wild Variety leaves the Bug-Catching Contest, the Battle Pike and the Battle Pyramid alone.
- A game saved during a DexNav search loads cleanly.

### Tooling
- The play tests also run on **VBA-M** at the commit Delta's GBA core pins
  (`tools/emurun/build_vbam_core.sh`, `run_all.sh vbam`), locally and in a second CI job. They have a pathfinding walker,
  bag checks and pointer-following addresses.
- New tests:
  - `qol_items`, `infinite_repel`, `relearner_training_kit`, `difficulty`, `autorun`
  - `pokevial`, `easy_catch`, `tm_reusable`
  - `dexnav`, `dexnav_any`, `dexnav_hidden`, `wild_variety`, `bug_contest`, `care_packages`
  - `story_opening`: the real story path from New Game to Elm's lab (starter, errand, Potion)
    and the first wild battle on Route 29, with no debug menu
  - `old_save_test.sh`: a Heart & Soul 2.0.6 save continued in Crystal Imperium
- `whitney` samples 12 battles (the naive team wins about 25%). `falkner` uses the autopilot.
- `tools/crystal_imperium/gen_hidden_encounters.py` generates the hidden tables. The validator
  reads the National Dex from `pokedex.h` (HnS numbers some forms below 1025) and parses nested
  evolution lists. It now reports 449 of 571 families with a source; the other 122 are
  legendary (DexNav's list from the start, Wild Variety after the Champion).
- Play tests run on a fixed cartridge clock (2026-10-24 01:30 UTC, advancing with emulated time),
  so they give the same results at any hour and on any host.

## 0.3.0-experimental (2026-10-23)

### Gameplay
- **Bugsy** rebuilt: Focus Sash Spinarak (Sticky Web), Pineco (Spikes, Rock Tomb), Ledian
  (Reflect, Light Screen), Eviolite Technician Scyther (Fury Cutter). Smart AI.
- **Whitney** rebuilt: Clefairy (Magic Guard; Metronome, Encore, Charm), Aipom (Fake Out,
  U-turn), Intimidate Stantler (Hypnosis), Scrappy Miltank (Rollout, Body Slam, Milk Drink,
  Attract). Smart AI; one Potion instead of Super Potion + Potion.
- Azalea and Goldenrod Gym trainers get defined movesets, abilities and levels close to the cap.

### Tooling
- Battle autopilot (`autobattle`) and win-rate sampling (`sample_battle`, `tally`,
  `expecttally`) in the emulator harness. `names.py` labels logs with species and move names.
- New tests: `bugsy`, `whitney`, `gym_trainers_m2`. Macros: `battle_style_set`.
- The validator now covers Bugsy and Whitney. It caught Aipom being given Technician
  (Ambipom's ability) during the rework.

## 0.2.0-experimental (2026-10-23)

### Gameplay
- **Mega Evolution** enabled for the 48 classic stone Megas and Mega Rayquaza. Press **R** in the move menu to Mega
  Evolve.
- A Mega Specialist on Goldenrod Dept. Store 5F gives the **Mega Ring** after the third badge
  and sells Mega Stones (₽10,000). More stones unlock at badges 6 and 8 and after becoming
  Champion.
- Boss Megas: Lance (Gyarados), Lance rematch (Salamence), Lance postgame (Charizard X),
  Red (Charizard Y).

### Fixes
- The gimmick trigger moved from START (taken by HnS's move info) to R.

### Tooling
- New play tests: `mega_evolution`, `mega_specialist`. New harness macro `give_item`.

## 0.1.0-experimental (2026-10-23)

Based on Pokémon Heart & Soul 2.0.6 (`167aa6d5`).

### Gameplay
- New **Minimal Grinding Mode** (Difficulty tab, ON by default). Every Pokémon battles with
  31 IVs and 0 EVs. Turning it on also enables max player IVs, no EV gain, NORMAL level caps
  and ×1.5 EXP.
- **Falkner** rebuilt: Pidgey (Tailwind), Rookidee (Hone Claws, Power Trip, Steel Wing) and
  Noctowl (Tinted Lens; Hypnosis, Air Cutter, Reflect, Mud-Slap); perfect IVs; Smart AI.
- Bird Keepers Rod and Abe and Elder Li get defined movesets, abilities and items.
- **Sleep Clause** is always on.
- The Goldenrod Flower Shop sells **Ability Capsule** (₽20,000) and **Ability Patch**
  (₽40,000) after the third badge.

### Tooling
- `tools/emurun`: a headless mGBA play-test harness with tests for Falkner, save/load and the
  Flower Shop.
- `tools/crystal_imperium/validate.py`: data validation and generated trainer/encounter
  databases.
- `tools/crystal_imperium/build.sh` and a CI workflow.
- Fixed `make check BUILD=hns` compilation (`fake_rtc.h` include order).
