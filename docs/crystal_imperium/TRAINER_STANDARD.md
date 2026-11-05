# Crystal Imperium: trainer standard

This is the standard Crystal Imperium's trainer teams are designed to: what a team must do, how it
is checked, and the evidence behind each rule. `tools/crystal_imperium/validate.py` checks the rules
tagged [V] and [W] (`tools/crystal_imperium/trainer_rules.py`), and the critic reads every team
against the rules tagged [C] (section 0.2). DECISIONS.md D59 records why the standard was written.

The standard covers every trainer team: bosses, the rival, Team Rocket, the Elite Four, rematches,
side battles, route mini-bosses, Ace Trainers, Heart & Soul's Cooltrainers and every ordinary
trainer. The user asked for it after the rival's battle in the Burned Tower:

> "You need to review every trainer team and do a better job, I just fought my rival in the tower
> and he had a level 39 quilava and a 39 weepingbell. Study the way imperium and radical red are
> built I need this on that same level"

The standard was written against the teams of 0.15.2. Where a rule's evidence counts what our teams
do or break, and in the last columns of tables 11.1 and 16, the counts describe those 0.15.2 teams.
0.17.0's designed teams meet the standard: 193 of the 234 were redesigned to it, and the other 41
already met every rule a script checks (D59). Rules settled after it was written say "Decided after
the standard was written".

The evidence comes from two studies written for this standard, of Radical Red 4.1's and Emerald
Imperium 1.3.1's public documents and data, from an audit of 0.15.2's teams against them, from
DECISIONS.md and from the battle code (section 0.1). A few numbers were computed for this standard
(section 0.3). We study both games' documents and data only for their rules. DECISIONS.md D2 says:
"we re-implement Imperium *behaviours* ... as original code and data". No Crystal Imperium team may
copy a Radical Red or Emerald Imperium team (rule S6).

Contents: 0 sources and checks; 1 terms; 2 levels and stages; 3 evolution; 4 team size; 5 held and
Bag items; 6 natures; 7 IVs and EVs; 8 abilities; 9 movesets; 10 plans, Megas and legendaries; 11
class themes; 12 doubles; 13 rematches; 14 variety and no copying; 15 the difficulty curve; 16 the
rules in one table.

## 0. Sources and how the rules are checked

### 0.1 Sources

| Id | Source | Used for |
|---|---|---|
| RR | Radical Red 4.1's public documents and data. The main one is "Default Mode Bosses v4.1 (with EVs) - Radical Red", https://docs.google.com/spreadsheets/d/1ES8L4OzeJ8rCuMWFNvrDaZKArqR7Vys2ytFxjx2pbwE (tabs Main gid 704367260, Kanto Leaders 1410111071, Rivals 1150799580, Team Rocket 1998272076, Mini Bosses 1752505021, Optional Bosses 739017967, Indigo League 1411568458, Postgame 2140479091). The others are Rudo2204's 4.1 trainer dumps (https://gist.github.com/Rudo2204/7f9e4a3ceaf077d623d3c37b1f921601 and the three other gists listed there) and the changelog mirror at https://www.pokeporto.com/pokemon-radical-red-changelog/ | Radical Red's rules |
| EI | Emerald Imperium 1.3.1's public data and documents: the `release` branch of https://github.com/iriv24/pokeemerald-expansion (`src/data/trainer_parties.h`, `src/data/trainers.h`, `src/battle_main.c`, `src/caps.c`); the official "Boss Battles" sheet, https://docs.google.com/spreadsheets/d/1A9iN3N2bZ8-0YCVrhfeZ0qo2runkbHd-HCgaH_TVyr4; and the changelogs V1.1 to V1.3.1 in the official Documentation folder (https://drive.google.com/drive/folders/1auRPBg8Ts50NByIskMy6b2XHnmNqIKtV) | Emerald Imperium's rules |
| Audit | the audit of 0.15.2's designed teams and of Heart & Soul's ordinary trainers against both games, made with this standard | 0.15.2's shortfalls |
| D# | `docs/crystal_imperium/DECISIONS.md` | decisions this standard keeps or changes |
| code | `src/battle_main.c`, `src/battle_setup.c`, `src/caps.c`, `src/pokemon.c`, `src/field_move.c`, `include/config/*.h`, `tools/trainerproc/main.c` at 0.15.2's commit d05ccbdd; the evolution of teams fought later and the rematch gate changed with the standard (section 1, rules E6 and R1) | what the engine does with a team |
| Counts | counts made from the build's data and the sources above (section 0.3) | numbers computed for this standard |

A citation such as "RR 4.3" or "EI 6" gives the number of a finding in the study of that game
written for this standard from the sources above; the studies are not in the repository. A quotation
after such a citation gives the study's words for what the sources show, unless the text names the
document it quotes. RR's phases are the study's parts of Radical Red's game by Normal level cap: A
15–27, B 34–47, C 56–68 and D 73–85.

The quotations relied on most were checked against the downloaded sources. The RR sheet's Main tab
has "Generally, if a Pokemon has Gyro Ball in its moveset or is part of a Trick Room team, you can
safely assume 0 speed IVs.", "All speed stats are determined based on the point when you're expected
to battle with the trainer at that specific juncture in the game." and "After you become the
Champion, every level scale (excluding Postgame trainers) will be two levels higher." EI's V1.1
changelog has "Removed EVs from Pokemon found before Wattson (only effects non-MGM)", and its V1.2
changelog has "Elite 4 will now scale to level 100 after you become the Champion".

### 0.2 Check kinds

| Tag | Meaning |
|---|---|
| [V] | `tools/crystal_imperium/validate.py` refuses the team: an error, and CI fails |
| [W] | the validator warns: the critic must accept the warning, with a reason, in the review notes |
| [C] | the critic checks it by reading the team as a competitive player, as D47's critic did |
| [P] | the play tests check it (`tools/emurun/tests/`) |

A rule marked "exists" was in `validate.py` before the standard: legal abilities (A1), four
learnable moves on reworked teams (M1), the cap of each team's stage (L1) and Return's happiness
(L5), as was I8's check of Red. R3 has no check of its own: S4's exact-set test refuses a set a boss
rematch shares with its first battle. The other [V] and [W] rules came with the standard, in
`trainer_rules.py`, which reads the build's own species, move and item data through its preprocessor
(`species_db.py`). While the redesign was under way, a [V] rule that a 0.15.2 team still broke only
warned for that team, listed in `trainer_rules.PENDING` (`validate.py --pending` prints the list),
and P3 and V4 warned for every team from `PENDING_EVERYWHERE`. Since 0.17.0 both are empty: every
designed team meets every rule the validator runs (0 errors, 0 warnings).

In 0.17.0, `validate.py` runs the [V] and [W] rules on the designed teams except V1, V5, N3, A3, C1,
P3's Mega shares for mini-bosses and Aces, M5's stage medians and I8 beyond Red's items. Rules on
Heart & Soul's ordinary trainers wait for their redesign: E9, Z4, I2, A4, M10, DB1, S2 and S3, and
the parts of other rules that name them. L3 waits for the stage tool and G1 for the trainer
document. S6 runs in review.

### 0.3 Numbers computed for this standard

- How far ahead of its line's level-up evolution level each game fields a Pokémon (rule E5), and the
  Eviolite bulk of every species whose next evolution is not by level (rule E3).
- 0.15.2's designed Pokémon that pass at their own stage but fall below it when their battle is
  fought later (rule E6). The audit judged each team only at its own stage.
- The designer packets for the ordinary trainers' redesign: 21 groups of 10 to 25 trainers, one
  designer's work each. A packet keeps a map's trainers together, and each rematch family with its
  first battle (rule S3).

## 1. Terms

- **Stage.** The stage of the game the level caps go by: 0 to 8 badges, J (the Johto League won) or
  K (the Kanto League won). A team's stage is the earliest stage at which the player can meet it
  (D21, D30: "set low where it isn't certain").
- **Caps** (`src/caps.c`, D29). NORMAL 15, 24, 33, 42, 50, 58, 66, 75, 85 for stages 0 to 8, then 90
  for J (`#define KANTO_MAX_LEVEL 90`) and 100 for K. HARD 12, 21, 30, 39, 47, 55, 63, 72, then 85,
  90 and 100. Levels are written NORMAL / HARD.
- **Window.** The stages at which a battle can happen. It starts at the team's stage. A story battle
  fought once has a closed window: the Gym Leaders, the rival, Proton in the Slowpoke Well, the
  Radio Tower, the Elite Four's first battles, the Kimono Girls and Red. A few windows are known
  ranges. The Rocket Hideout is fought with 4 to 6 badges (D21: "the Lake of Rage needs Surf, so
  four to six badges: 50, 58 or 66"). Gardenia's first team is fought with two or three badges, her
  second from four (D41: "her first team with two, her second with four"). The Kanto leaders, the
  `_2` rematches and the rival at the Indigo Plateau are fought from J to K (D21: "at 100 then").
  Every other battle is open to K: Eusine, the other side battles, route mini-bosses, Ace Trainers,
  Cooltrainers, ordinary trainers and rematch tiers.
- **Team made for a stage** (D56). Its party data has every Pokémon at its stage's NORMAL cap. The
  battle keeps its species while the battle level is at or below that level
  (`if (sTeamMadeForStage && level <= teamLevel) return species;`, `GetTrainerMonEvolvedSpecies`).
  Raised to a later cap, the team evolves: by level when a level evolution is due, by item, trade,
  friendship or move from level 32 (`#define TRAINER_OTHER_EVOLUTION_LEVEL 32`). A named Eviolite
  species holding an Eviolite and a Pikachu holding a Light Ball stay as they are
  (`IsKeptUnevolved`), and a Pokémon that evolves into one of them stops there. An evolved Pokémon
  holds its `raised_item` if its team gives it one (`sRaisedItems`). This came with the standard
  (rule E6). Heart & Soul's own trainers keep 0.15.2's rule: a Pokémon holding an Eviolite, an
  Everstone or an item for its own species never evolves (`IsEvolutionBlockingItem`). Every team in
  this standard is made for a stage. In 0.17.0 that covers the bosses, route mini-bosses and side
  battles (`sLevelCapBosses`), the Ace Trainers and the upgraded Cooltrainers
  (`sTeamsMadeForStage`). After the ordinary trainers' redesign it covers every trainer.
- **Trainer kinds** (RR 1: "three tiers of trainers"; EI 1.1: "three tiers"):
  - *Boss*: the Gym Leaders, the rival, the Rocket executives, Eusine, Li, the Kimono Girls, the
    Elite Four and Lance, the Kanto leaders, Blue, Red, and the boss rematches (`_2`, `_POSTOBC`).
  - *Side battle*: D41's 34 battles.
  - *Mini-boss*: D30's route mini-bosses (`ROUTE_BOSSES`) and any ordinary trainer promoted to one.
  - *Ace*: D47's Ace Trainers and Heart & Soul's Cooltrainers with competitive teams (`UPGRADES`).
  - *Ordinary*: every other Heart & Soul trainer, including the phone rematch tiers.
  - *Postgame tier*: ordinary trainers whose stage is K (the bonus areas). They are designed as
    bosses (rule Z4, RR 13.4: "Postgame: everyone becomes a boss").
  - "Designed teams" below means bosses, side battles, mini-bosses, Aces and the postgame tier.
- **Evolution data.** The build's compiled table: the species files with `imperium_evolutions.h`
  applied (D44, D45). The 0.15.2 audit used it, and `species_db.py` reads it for the validator. A
  *level evolution* is `EVO_LEVEL` or `EVO_LEVEL_BATTLE_ONLY` with a level above 1. Every other
  method is a *non-level evolution*: item, trade, friendship, a known move, a held item, "other".
  Our levels are not vanilla's. Rhyhorn evolves at 42, Piloswine at 45 (or knowing Ancient Power),
  Bayleef at 36, Lickitung at 35 and Duraludon at 50 (or with a Metal Alloy).
- **Reach level.** The lowest level at which a species exists by level-up from its base form: the
  highest level evolution on its line. A non-level step adds nothing. A Pokémon is *ahead* by its
  reach level minus its level.
- **Named Eviolite species.** The species of rule E3, the only ones that may stay unevolved with an
  Eviolite from stage 2 on.

## 2. Levels and stages

The levels are not a design choice. Every opponent battles at the player's level cap (D56: "Keep
everything consistent I want to fight teams with the same level cap as me"). What the designer
controls is the stage a team is made for.

| Rule | Check | Rule text |
|---|---|---|
| L1 | [V] exists | The party data puts every Pokémon of a team at its stage's NORMAL cap (D21, D56; `validate.py`: "not at the cap {want} for its stage"). |
| L2 | engine | The battle level is the player's cap (`GetTrainerBattleLevel`). A boss battles at the cap of its stage or the player's, whichever is later (`GetBossLevel`). Any other team is never above the player's cap, even met before its stage (D56). HARD caps are 3 levels lower until the Elite Four; the species stay as made. |
| L3 | [V] | A team's stage is the earliest stage the player can meet it. It comes from the stage tool, planned with the ordinary trainers' redesign, which reads map access, field moves and story flags. It never comes from Heart & Soul's levels. A team's stage may be lower than the tool's, never higher. A team made for a later stage than the player's would field its species at a lower level (L2), ahead of their level evolutions. |
| L4 | [V] | Every rule of section 3 holds at every stage of the team's window (section 1), as the battle code will field the team there. |
| L5 | [V] exists | Return, Pika Papow and Veevee Volley need Happiness 255 (`boss_teams.FRIENDSHIP_MOVES`, D47). |

Evidence. RR's bosses sit at the cap or 1 to 2 under it (RR 2.1). Its mini-bosses scale with the
player (RR 2.3: "Highest Lv -3", "-5"). EI's are the same (EI 2.3). Both games' ordinary trainers
are fixed well under the cap (RR 2.5: "cap -6 to -12"; EI 2.3: "about 3–15 below the cap"). Ours are
at the cap with 31 IVs and the smart AI, so harder than both. This standard keeps that and puts the
work into the teams themselves.

## 3. Evolution stage by level (the user's complaint)

### 3.1 The rules

| Rule | Check | Rule text |
|---|---|---|
| E1 | [V] | **No Pokémon is at or past the level of a level evolution it has not taken.** Checked at the NORMAL cap of every stage in its window, for the species the battle code fields there. There are no exceptions, with or without an Eviolite. |
| E2 | [V] | **From stage 2 (cap 33), a Pokémon whose next evolution is not by level must be evolved.** The only exceptions are the named Eviolite species holding an Eviolite (E3) and Pikachu with a Light Ball (E4). At stages 0 and 1 an unevolved item, trade, friendship or move evolver is allowed, with or without an Eviolite. |
| E3 | [V] | **The named Eviolite species** (table 3.2) may stay unevolved with an Eviolite from stage 2 on. A named Pokémon must be "tier A" at its battle level, nature and EVs: its HP x Defense and HP x Sp. Def with the Eviolite's 1.5 are at least 1.10 times those of every most-evolved form it could be at that level. [W] if its set does not use the bulk (no recovery, status, hazards, pivot, screens, Trick Room or phazing). Rule I3 limits a team to one Eviolite from stage 2. |
| E4 | [V] | **Signature exception: Pikachu with a Light Ball**, at any stage. D51 made Pikachu strong without evolving, and RR 4.3 lists "Pikachu-Surfing @ Focus Sash ... signature form". No other signature exception exists unless this table is amended. |
| E5 | [V] | **Not too far ahead.** No Pokémon may be more than 6 levels before its reach level at its team's NORMAL level. [W] if more than one Pokémon on a team is ahead at all. |
| E6 | [V] | **Fought later.** In a battle fought after its stage, a Pokémon holding an evolution-blocking item (Eviolite, Everstone, Light Ball, Lucky Punch, Deep Sea Tooth or Scale, Metal or Quick Powder) must still pass E1 to E3 at every stage of its window. With 0.15.2's battle code this refused an Eviolite on a level evolver in an open window, and on any non-named species from stage 2. Since the battle-code change that came with the standard (section 1), such a Pokémon evolves when raised, and the rule requires a `raised_item` for it instead where its own item would do nothing for the evolved form. |
| E7 | [V] | **No Everstone** on any team. It does nothing in battle, and for Heart & Soul's own teams the battle code reads it as "keep me unevolved". |
| E8 | [V] | **The rival's starter** is the middle stage below 36 and the final stage from 36 (stage 3 on). RR 4.2: "It is fully evolved (and Mega) as soon as its level allows"; EI 4: "EI never fields a starter at or past its final evolution level". |
| E9 | [V] | **Ordinary trainers too.** A redesigned ordinary team is made for its stage. Its party species must pass E1 to E6 at that stage. It may not rely on the battle code evolving it there. |

How the validator applies E1 to E6 to one Pokémon, in the battle code's own order:

```
for stage in window(team):                        # section 1
    L = normal_cap(stage)
    sp = species if L <= normal_cap(team.stage) else battle_evolve(species, L, item)   # GetTrainerMonEvolvedSpecies
    if any level evolution of sp is due at L:                                          error E1
    if stage >= 2 and sp has a non-level evolution:
        if not (item == Eviolite and sp in NAMED and tier_A(sp, L, nature, evs))
           and not (sp == Pikachu and item == Light Ball):                             error E2 / E3
ahead = reach_level(species) - normal_cap(team.stage);  if ahead > 6:                  error E5
```

`battle_evolve` mirrors `GetTrainerMonEvolvedSpecies`: a level evolution at its level, any other
from 32, the first route listed that applies, two steps at most, never past a named Eviolite species
holding an Eviolite or a Pikachu holding a Light Ball (`trainer_rules.battle_species`).

### 3.2 The named Eviolite species

Computed for this standard from the build's base stats (D50) and evolutions. A species is listed
when it reaches tier A against each most-evolved form it could be, at every level from 33 to 100.
The test assumes 31 IVs, no EVs and a neutral nature. Item, trade, friendship and move steps always
count; a level step counts only when due (the 0.15.2 audit's test). The list is
`team_kit.NAMED_EVIOLITE`: `boss_teams.py` writes it into the battle code as
`sKeptUnevolvedSpecies`, and `validate.py` recomputes the tiers from the build's data and fails if
the list differs.

| Species | Next evolution | Lowest bulk ratio (physical / special) |
|---|---|---|
| Porygon2 | item (Porygon-Z) | 1.82 / 1.80 |
| Dusclops | trade or item (Dusknoir) | 1.39 / 1.39 |
| Charjabug | item or other (Vikavolt) | 1.35 / 1.30 |
| Swadloon | friendship (Leavanny) | 1.42 / 1.29 |
| Shelmet | trade or item (Accelgor) | 2.11 / 1.27 |
| Golbat | friendship (Crobat) | 1.26 / 1.32 |
| Pikachu | item (Raichu, Alolan Raichu) | 1.48 / 1.25 |
| Electabuzz | trade or item (Electivire) | 1.22 / 1.39 |
| Magmar | trade or item (Magmortar) | 1.22 / 1.27 |
| Rhydon | trade or item (Rhyperior) | 1.32 / 1.22 |
| Gligar | item (Gliscor) | 1.20 / 1.24 |
| Chansey | friendship (Blissey) | 1.20 / 1.19 |
| Scyther | trade or item (Scizor, Kleavor) | 1.18 / 1.50 |
| Eelektrik | item (Eelektross) | 1.17 / 1.17 |
| Misdreavus | item (Mismagius) | 1.23 / 1.17 |
| Sneasel | item (Weavile) | 1.17 / 1.21 |
| Aipom | move (Ambipom) | 1.12 / 1.12 |
| Togetic | item (Togekiss) | 1.10 / 1.12 |
| Type: Null | friendship (Silvally) | 1.38 / 1.38; sub-legendary, so rule P4 applies |
| Poipole | move (Naganadel) | 1.34 / 1.34; Ultra Beast, so rule P4 applies |

Left out: Porygon, which also reaches 1.31 against Porygon-Z. Its own evolution, Porygon2, is on the
list and is far bulkier with the same Eviolite. Not on the list are the tier B species, 0.95 to
1.10: Gurdurr, Lampent, Machoke, Gloom, Magneton, Roselia, Swirlix, Haunter, Woobat, Nidorino,
Tangela, Kadabra, Murkrow, Lombre, Graveler and others. Also left out are all of tier C, below 0.95:
Onix, Weepinbell, Clefairy, Primeape, Poliwhirl, Seadra, Shellder, Growlithe and 56 more. Each is
allowed only at stages 0 and 1.

Evidence for E1 to E5:

- RR 4.1, over 567 boss Pokémon whose level is known: "**0** sit at or past the level of a level
  evolution they have not taken".
- RR 4.3: "So: past level 30 RR keeps an unevolved Pokemon only when (a) its evolution is not a
  level one, and (b) it is a known Eviolite user or a deliberate signature (Pikachu-Surfing,
  Duraludon, Bisharp). Weak NFEs (Weepinbell, Gloom, Haunter as a plain attacker...) do not appear
  at those levels." RR's Eviolite users past 30 are Golbat, Sneasel-H, Scyther, Dipplin, Porygon2,
  Piloswine, Chansey and Qwilfish-H. Each is either on table 3.2, or a level evolver in our build
  that rule E1 allows only below its level (Piloswine 45, Dipplin 44).
- RR 4.4: "Under level 30, unevolved item evolvers are normal, often with Eviolite". Hence E2's
  stages 0 and 1.
- EI 4: "So none of the 678 designed Pokémon is at or past its level evolution without an
  Eviolite", and "From the 4th-badge segment (cap 44) on, designed teams are fully evolved: 1 of 96
  is not at caps 44–47, 0 of 314 at caps 71–85". EI's tier B Eviolite users stop at Wattson's
  Magneton, cap 34. E2 takes RR's stricter line at our stage 2: the user's Weepinbell and Haunter
  are the very examples RR 4.3 names.
- The battle code evolves an ordinary trainer's item and trade evolvers from 32
  (`TRAINER_OTHER_EVOLUTION_LEVEL`). E2's stage 2, cap 33, is the first cap above it, so designed
  and ordinary teams agree.
- Rule E5, from a count made for this standard. RR fields almost nothing ahead of its level-up line.
  Of 780 boss-sheet Pokémon with a known level, 4 are ahead. Two are one level ahead at 20 to 29.
  The other two are on the optional, player-scaled Whitney (Farigiraf and Tinkaton at "Highest Lv
  -2"). EI is looser early. Of 676 designed Pokémon with a level in the data, 15 of 46 at levels 1
  to 19 are ahead, by up to 10 (Hattrem 18 on the Rustboro rival, whose line reaches it at 28). Nine
  at 30 to 39 are ahead, by up to 16 (Sneasler 31 on Wally), and none from level 50. Gardenia's
  second team is left out: the data gives it her map's first cap, but it is fought after the 3rd
  badge. 0.15.2's teams: 4 of 1,318, at most 6 ahead (Li's Weepinbell at 15, Miriam's Ursaluna at
  42). E5 keeps the game there.

### 3.3 What this means for the battle the user reported

The rival's third battle, `TRAINER_RIVAL_<starter>_3_HNS`, is stage 3: 42 on NORMAL caps, 39 on
HARD. Under E1, Quilava, Croconaw and Bayleef must be Typhlosion, Feraligatr and Meganium (36), and
Larvitar must be at least Pupitar (30). Under E2, Weepinbell must be Victreebel, Haunter Gengar and
Sneasel Weavile, or a Sneasel holding an Eviolite (it is on table 3.2). 0.15.2's Golbat with an
Eviolite is allowed (table 3.2), but its moves failed M2 and M5. Rule P3 adds a Mega, and V4 EVs.
0.17.0's team, redesigned to the standard, is Pupitar, Crobat, Weavile, Gengar, Mega Absol and the
final stage of his starter, all with full EV spreads.

## 4. Team size by stage and trainer kind

| Rule | Check | Rule text |
|---|---|---|
| Z1 | [V] | Team sizes follow table 4.1 for the team's kind and stage. |
| Z2 | [V] | A team fought only in a two-opponent battle has exactly 3 Pokémon. The battle takes "at most three Pokémon from each" (`if (battleTypeFlags & BATTLE_TYPE_TWO_OPPONENTS) { if (trainer->partySize > PARTY_SIZE / 2) monsCount = PARTY_SIZE / 2;`). A team that can meet the player either alone or with another trainer has its best three first (rule DB2). |
| Z3 | [V] | A phone rematch tier has at least as many Pokémon as the tier before it. [W] if it has more than one extra. |
| Z4 | [V] | A postgame-tier trainer (stage K) has 4 to 6 Pokémon with full designed sets: the boss rules apply to it. |

### 4.1 Sizes

| Kind | Stage 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | J | K |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Gym Leader (D30) | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | | 6 | 6 |
| Rival | 1 (D30) | | 6 | 6 | | | | 6 | 6 | 6 | |
| Rocket executive | | 6 | | | 6 (Ariana in the tag battle: 3) | | | 6 | | | |
| Elite Four, Lance, Kanto leaders, Blue, Red, boss rematches | | | | | | | | | 6 | 6 | 6 |
| Li (D30), Kimono Girls (D30) | Li 3 | | | | | | | | Kimono 1 each | | |
| Side battle (D41) | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| Route mini-boss (D30) | 3 | 4 | 4 | 5 | 5 to 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| Ace Trainer (D47) | 3 | 4 | 5 | 5 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| Heart & Soul Cooltrainer with a competitive team (D47) | | | | 5 | 5 | 6 | 6 | 5 to 6 | 6 | 6 | |
| Ordinary trainer | 1 to 2 | 1 to 3 | 2 to 3 | 2 to 3 | 2 to 4 | 2 to 4 | 2 to 4 | 2 to 4 | 2 to 4 | 2 to 4 | postgame tier: 4 to 6 |
| Ordinary double battle (both trainers together) | 2 | 2 | 2 to 4 | 2 to 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 to 6 |

Notes. Our bosses have six from the first Gym because the user asked for it (D30). That is above
both games: RR's Gyms have "4, 4, 5, 5, then 6 from the fifth gym" (RR 16.2) and EI's "4, 5 and 5
Pokémon, then 6 from the 4th gym" (EI 1.3). The ordinary sizes keep both games' light route trainers
(RR 3.2: "ordinary trainers 1 to 3"; EI 3: "Filler: 1 (121 trainers), 2 (206), 3 (41), 4 (6)"). They
let a theme team of four stand from stage 4 on, and drop the lone Pokémon after stage 1 (a single
Pokémon at the cap is a free win or a cheap knockout). In 0.15.2, Heart & Soul's ordinary trainers
had 95 with 1, 150 with 2, 121 with 3, 43 with 4, 11 with 5 and 5 with 6. Mini-boss and Ace sizes
are D30's and D47's ("three Pokémon on the first routes, four after the first badge, five to the
fourth, six from the fifth and on the routes past Cianwood and Mahogany"), and the Cooltrainers' are
0.15.2's (Beth's and Reena's first battles had 5, their rematch tiers 6). The double-battle row
counts both trainers' Pokémon together. In 0.15.2, Thom & Kae, Duff & Eda, Jo & Zoe and Meg & Peg
had 2 at stages 4 and J, which the table raises to 4.

## 5. Held items and Bag items

| Rule | Check | Rule text |
|---|---|---|
| I1 | [V] | Every Pokémon on a designed team holds an item. RR 5.1: "Every boss and mini-boss Pokemon holds an item; ordinary ones do not"; EI 5: "Every designed Pokémon holds one". |
| I2 | [V] | Ordinary trainers hold no item, with two exceptions. A class item is allowed: a Black Belt's Black Belt, a Swimmer's or Fisherman's Mystic Water, a Bird Keeper's Sharp Beak, a Burglar's or Firebreather's Charcoal (RR 5.1: "Black Belt class trainers hold the Black Belt item: 20 of the 25"). So is a Pikachu's Light Ball. No Eviolite: an ordinary trainer's Pokémon is evolved for its stage. |
| I3 | [V] | No item more than twice on a team, and at most one item twice. From stage 2, at most one Eviolite; at stages 0 and 1, at most two. [C] may accept a stated gimmick instead (RR 5.3: "Ace Haley: 4 Power Herb"), such as Li's three Eviolite Pokémon (D47). Evidence, from the 0.15.2 audit: "104 of 234 battles repeat a held item (44%), against EI's 22 of 132 (17%) and RR's 39 of 166 (23%, 'usually twice')". |
| I4 | [V] | No item that does nothing in its set. Refused: a Choice item with a status or setup move; Light Clay without Reflect, Light Screen or Aurora Veil; Loaded Dice without a multi-hit move; a weather rock without its weather's setter on the team; Power Herb without a charge move; White Herb without Shell Smash or a self-lowering move; Toxic or Flame Orb without Guts, Poison Heal, Toxic Boost, Flare Boost, Quick Feet, Marvel Scale or Facade; Eviolite on a fully evolved Pokémon; Focus Sash on Sturdy; a type booster or Gem of a type the Pokémon has no attack of; Leek off Farfetch'd and Sirfetch'd, Thick Club off Cubone and Marowak, Light Ball off Pikachu. |
| I5 | [W] | An item weak for its stage: Oran Berry or Berry Juice from stage 2 (EI 5 shows them only at caps 15–25), Shell Bell, Quick Claw, Bright Powder, Lax Incense, King's Rock without Serene Grace. |
| I6 | [C] | Item strength follows the stage, as in EI's table of first appearances (EI 5). Berries, Eviolite, Muscle Band and type boosters come first. Focus Sash, Leftovers, Expert Belt and Rocky Helmet come by stage 2. Life Orb, the Choice items, Scope Lens and the weather rocks come by stage 3, and Assault Vest, Booster Energy and Weakness Policy by stage 4. 0.15.2's designed teams already carried strong items early, which the standard allows. |
| I7 | [V] | Deliberate item and ability pairs are checked together (RR 5.2: "Item-ability and item-move pairs are deliberate"): an Orb needs its ability or Facade, Booster Energy needs Protosynthesis or Quark Drive, Terrain Extender a terrain setter, Heat Rock, Damp Rock, Smooth Rock or Icy Rock their weather setter. |
| I8 | [V] | Bag items. A boss carries at most two (Potions to Full Restores by stage, as `boss_teams.TEAMS` does). Postgame bosses carry three. Red carries four, the most (D27, D41, D47; `validate.py` checks Red). Side battles carry what their stage's Gym Leaders carry (D41). Mini-bosses, Aces, ordinary trainers and the postgame tier carry none. EI has none at all (EI 5: "**No trainer in EI uses items from the Bag.**"). Ours are a deliberate difference that makes bosses harder, and EASY turns them off (D56). |

## 6. Natures

| Rule | Check | Rule text |
|---|---|---|
| N1 | [V] | Every Pokémon has a nature set in its data (designed and ordinary teams alike; trainerproc otherwise writes `NATURE_HARDY`). The nature may not lower the stat the set attacks with (Attack on a physical set, Sp. Atk on a special one). Foul Play and fixed-damage users are exempt. |
| N2 | [V] | A Trick Room setter or member (rule P2 says which members), or a Gyro Ball user, has a nature that lowers Speed (Brave, Quiet, Relaxed or Sassy), or base Speed 30 or less. Under Minimal Grinding, the default, the nature is the only Speed lever. `CalculateMonStats` (`src/pokemon.c`) says: "Minimal Grinding: every Pokémon (player, trainer and wild) uses perfect IVs and no EVs, except Red's, which keep their EVs". RR 6.1: "Trick Room teams take minus-Speed natures". |
| N3 | [W] | From stage 3, at least 40% of a stage's designed Pokémon have Jolly or Timid. EI 6: "Jolly and Timid are 52–74% of the designed Pokémon in each band from the 4th badge on". RR 6.1 phase D: "Jolly 86, Timid 59, Adamant 36, Modest 18 of 222". 0.15.2's were 36%, 35%, 42% and 48% at stages 0–2, 3–5, 6–8 and after the Johto League. |
| N4 | [C] | Neutral natures are allowed on the first mini-bosses and on ordinary trainers. RR 6.2: "The very first mini-bosses use neutral natures"; RR 6.3: ordinary trainers' "natures are arbitrary". |

## 7. IVs and EVs

| Rule | Check | Rule text |
|---|---|---|
| V1 | [V] | IVs are 31 in every stat, except where the set needs otherwise. The designed teams' `mon()` (`team_kit.py`) has an `ivs` field for this. The battle code keeps a designed uneven spread: "an opponent's even spread below 31 is 31s. Other spreads (a special attacker's 0 Attack) stay as the party data has them" (`CreateNPCTrainerPartyFromTrainer`). |
| V2 | [V] | 0 Speed IVs on Trick Room setters and members (rule P2 says which members) and on Gyro Ball users (RR 7.2, quoting the sheet's Main tab: "Generally, if a Pokemon has Gyro Ball in its moveset or is part of a Trick Room team, you can safely assume 0 speed IVs."; EI 6). This matters only with Minimal Grinding off (D3), so N2 is the rule that always works. |
| V3 | [V] | A Hidden Power user has the IVs of the type it is meant to be. Hidden Power types follow the stored IVs even under Minimal Grinding (D3: "Stored IVs/EVs are untouched, so Hidden Power types still vary"). With 31s it is Dark (Bret's Magnezone in 0.15.2). |
| V4 | [V] | EVs. None at stages 0 and 1. At stage 2, at most one Pokémon on a team, the ace, may have EVs, up to 252 in one stat (EI 6: "an 80-EV boost on the rival's and Wally's ace"; RR 7.3: "Misty: Frogadier '100 HP', '40 Atk', '40 Sp. Atk'"). From stage 3 through J, every Pokémon on a designed team has a full spread: 252/252/4 by its role, or a split bulk spread (RR 7.3: "Erika (cap 44) onward: 252/252/4 spreads"; EI 6: "From the cap-34 segment on, designed teams have full spreads"). At K, no EVs except Red's (D27, D47: "the postgame teams at 100 have none ... so Red stays the only one with EVs"). Ordinary trainers have none (RR 7.1, EI 6). EVs count only with Minimal Grinding off (D3). Decided after the standard was written: the owner approved full spreads from stage 3 through J on designed teams, and none at K. |
| V5 | [W] | 0 Attack IVs on a special attacker that fears Foul Play or confusion (RR 7.2: "0 Attack on special attackers against Foul Play and confusion"). |

## 8. Abilities

| Rule | Check | Rule text |
|---|---|---|
| A1 | [V] exists | The ability is one the species has in this build (`validate.py`). With none set, the battle uses slot 0 (`#define B_TRAINER_MON_RANDOM_ABILITY FALSE`). |
| A2 | [V] | The ability does something in its set. Refused: Chlorophyll, Solar Power, Flower Gift or Leaf Guard without sun on the team or the map; Swift Swim, Rain Dish or Hydration without rain; Sand Rush, Sand Force or Sand Veil without sand; Slush Rush, Ice Body or Snow Cloak without snow; Technician without a move of 60 power or less; Rock Head or Reckless without a recoil move; Iron Fist, Strong Jaw, Mega Launcher, Sharpness, Skill Link or Punk Rock without their moves; Serene Grace without a secondary effect; Harvest without a Berry; Unburden without a consumable item; Aerilate, Pixilate, Refrigerate or Galvanize without a Normal attack; Pickup, Run Away, Honey Gather, Ball Fetch or Illuminate. Mega Stone holders are judged by their Mega's ability. Decided after the standard was written: a Mega battles with the ability in the slot of its base form's ability. The party data's ability sets the slot and Mega Evolving keeps it; an empty slot falls back to another hidden one, then to the first that isn't empty. A Sableye with Frisk becomes a Mega Sableye with Prankster, one with Prankster a Mega Sableye with Magic Bounce. The 0.15.2 audit found 35 Pokémon with a dead ability (26 distinct sets), 18 of them Chlorophyll with no sun on the team or the map. |
| A3 | [W] | A hidden ability, or another slot, fits the set clearly better (the 0.15.2 audit found Guts where No Guard fits a Dynamic Punch). [C] target: 25% to 35% hidden abilities per stage from stage 3 (EI 7: "23–37% of designed Pokémon in each band from the 3rd badge on"; RR 8.1: "about a third"). 0.15.2's were 15% to 22% at stages 0 to 3. |
| A4 | [V] | Ordinary trainers get an ability chosen like a designed team's, never one on A2's list. Heart & Soul's slot 0 Run Away or Pickup does nothing. |

## 9. Movesets

A "support set" has at most one attack, or two attacks plus at least two of hazards, screens, a
status move, recovery, a pivot move, Trick Room, Tailwind and phazing. Every other set is an
"attacker".

| Rule | Check | Rule text |
|---|---|---|
| M1 | [V] | Every Pokémon has four moves its species or a pre-evolution can learn (exists for reworked teams, `validate.py`). Ordinary trainers too. The battle code's default ("`GiveMonInitialMoveset(mon); // TODO: Figure out a default strategy when moves are not set`") gives the last four level-up moves, which at the cap are incoherent (the 0.15.2 audit found "Xatu at 66 with Future Sight, Power Swap, Guard Swap and Me First"). |
| M2 | [V] | No filler move. Refused: Confuse Ray, Supersonic, Sweet Kiss, Smokescreen, Sand Attack, Flash, Kinesis, Scary Face, Charm, Growl, Leer, Tail Whip, Baby-Doll Eyes, Harden, Withdraw, Attract, Captivate, Metronome, Me First, Power Swap, Guard Swap and Mist. Also refused: Focus Energy without Sniper or Super Luck; Mind Reader or Lock-On without an inaccurate move; Defense Curl without Rollout or Ice Ball; Dream Eater without a sleep move; Rest without Sleep Talk, Shed Skin, Natural Cure or a Chesto or Lum Berry. Ditto is the one exemption from M1 and M4: Transform alone, with Imposter or a Choice Scarf as its stated set (the 0.15.2 audit found "a lone Transform Ditto at 90" with neither). The audit found filler on 23 of 0.15.2's designed Pokémon (Confuse Ray on every Golbat). |
| M3 | [W] | An attacker has at least one attack of its own type. Exempt: a known set that replaces STAB with priority and coverage (Dragon Dance Dragonite with Extreme Speed); the critic decides. |
| M4 | [V] | An attacker has at least two attacks of different types (RR 9.1: "3-4 of them attack ... mean distinct attacking types per Pokemon 2.8 (phase A) to 3.1"). |
| M5 | [V] | From stage 2, an attacker has an attack of at least 70 power, counted with what the set does for it (Technician, multi-hit counts, Facade with an Orb, Acrobatics without an item). EI 8's median strongest attack is 80 at caps 30–34. On 0.15.2's teams this refused Whitney's Clefairy (45), the rival's Golbat and Sneasel (60) and his second Croconaw (65). [W] if a stage's median strongest attack falls below EI's for the matching segment: 65, 70, 80, 90, 100, 95, 100, 100 and 110 at stages 0 to 8. 0.15.2's were 65, 80, 90, 90, 100, 90, 100, 110 and 110. |
| M6 | [V] | An attack at 50% accuracy or less (Dynamic Punch, Zap Cannon, Inferno) needs its enabler: No Guard or Compound Eyes, or Mind Reader or Lock-On (the 0.15.2 audit found "Eugene's Machoke's 50% Dynamic Punch"). Decided after the standard was written: the bound is 50%, as the 0.15.2 count assumed, so Focus Blast, Hurricane, Thunder and Blizzard need no enabler (at the first bound, under 75%, the rule flagged them on 74 teams). |
| M7 | [W] | A weak setup move: Growth without sun, Work Up on a single-attacking-stat set, Howl or Hone Claws past stage 2. |
| M8 | [V] | Team roles from stage 3, for bosses and side battles: at least one setup move and one priority move on the team; at least one pivot or hazard; at most one hazard setter per kind of hazard. Mini-bosses and Aces from stage 5: setup or priority, and a pivot or hazard. Decided after the standard was written: an attack that raises its user's stats counts as setup (Power-Up Punch, Charge Beam, Flame Charge, Trailblaze, Aqua Step, Esper Wing, Torch Song, Scale Shot, Rapid Spin, Meteor Beam, Electro Shot); a Flying attack from a Pokémon with Gale Wings counts as priority, and so does Grassy Glide; Toxic Debris counts as a hazard. The rule does not apply to a battle with fewer than three Pokémon (the Kimono Girls fight with one each). RR 9.2's late teams: "Setup 37/40, Priority 30/40, Pivot 24/40, Hazards 12/40" (phase D); EI 8: "A setup sweeper: ... 21/25 (84–85)"; RR 9.3: "Hazards: one setter, usually the lead". |
| M9 | [C] | Coverage for the player's likely answers, early too (RR 9.4: "Even at cap 15-27 bosses carry coverage that hits the counters of their type"). Speed control and utility early (RR 9.5: "Rock Tomb, Icy Wind, Bulldoze, Electroweb, Mud Shot on early bosses"). |
| M10 | [V] | An ordinary trainer's moveset has at least two attacks, one of its own type, and at most one status move, unless it is a support set with a stated job. Both games' ordinary trainers average "2.2 attacking types, 1.25 status moves per Pokemon" (RR 9.1). 0.15.2's averaged 2.15 and 1.20, but without sense at the cap: the audit found "61 of the 795 Pokémon at stages 3 to J (8%) have one attack or none". |

## 10. Plans, Megas and legendaries

| Rule | Check | Rule text |
|---|---|---|
| P1 | [C] | Every designed team has one plan, named in a comment above it in the data module: weather, terrain, Trick Room, hazards and pivots, screens and setup, Tailwind, a Mega ace, doubles synergy, or a gimmick. Its lead starts the plan (D47: "a lead with a plan"; RR 10.1: "A boss team has one plan"; EI 9). |
| P2 | [V] | **Trick Room is a whole team** (RR 10.2: "Trick Room is a full team, not one move"). A team with Trick Room has two setters, or one setter and at least three members of base Speed 60 or less. Every member passes N2 and V2, and no member has a Speed-raising nature. A lone Trick Room on a fast team is refused: the 0.15.2 audit found Blue, Will, Fantina and Tulip. Decided after the standard was written: on a whole Trick Room team the members are the setters, the Pokémon of base Speed 60 or less and those with a Speed-lowering nature. A fast Pokémon with another nature is support outside Trick Room (Will's Xatu sets screens, then U-turns out) and is not held to N2, V2 or P2; at base Speed 61 to 70 it gets only a V2 warning. |
| P3 | [V] | **Mega Evolution.** One Mega per team at most (the engine allows one per trainer per battle, D9), usually on the ace in the last slot (RR 5.4: "in the last slot in 24 of them"). Required on every boss and side battle from stage 3, except the Kimono Girls, and Geeta and N (D41: "whose teams have none"). That means Morty, the rival from his 3rd battle, every Rocket executive from the Hideout, Eusine and Fantina. In Ariana's tag battle the Mega must be among her three. RR 5.4: "none before the third Gym" and "First Mega: Lt. Surge's Manectric-Mega (cap 34)"; EI 5: "From Wattson on, every gym leader has exactly one". Our Mega Ring comes after the 3rd badge (D9), so stage 3 is the first boss after it. This changes D21's "Morty has none". Mini-bosses and Aces: [V] at least one in three teams from stage 5, and two in three from stage 8 and in Kanto (EI 5: "Route mini-bosses carry them from Route 111 (cap 44)", "At caps 84–85, all 25 designed teams have a Mega or a Primal Orb"; RR 15: phase D, Megas on 35 of 40 teams). This changes D47's "no Mega Stones" for Aces. The stones are D9's classic ones and, since 0.16.0, Emerald Imperium's (D58). A Mega battles with the ability of its base form's slot (rule A2). Decided after the standard was written: the owner approved these Megas, on bosses and side battles from stage 3 (Morty included), and on a third of mini-boss and Ace teams from stage 5 and two thirds from stage 8 and in Kanto. |
| P4 | [V] | **Legendary-tier Pokémon** (Paradox, Ultra Beast, sub-legendary, mythical; `isParadox` and the other flags). None before stage 5. From stage 5 a boss may have one Paradox Pokémon or Ultra Beast. From stage 7 a boss may have one sub-legendary or mythical instead. Each Elite Four member has one, and Lance up to two. After the Johto League, rematch and postgame teams have at most three (D47). No restricted legendary on any team (D47: "no restricted legendary"; Red stays the hardest battle, D27). The one exception is N's Zekrom, his signature in D41's postgame side battle and the only restricted legendary on a 0.15.2 team (a count of the designed teams). Mini-bosses and Aces: none in Johto, at most one in Kanto (D47). RR 5.5: "cap 59-68: one or two **Paradox** Pokemon"; "cap 80-82 (story): sub-legendaries, Mythicals and Ultra Beasts"; "Elite Four Members each have a Legendary Pokemon". EI 1.9: "sub-legendaries, Paradox Pokémon and Ultra Beasts appear from the 4th-badge segment". Both games put restricted legendaries at their Elite Four (RR 5.5: "cap 85: box legendaries"; EI 13). This standard does not, because Red stays the hardest battle (D27). Decided after the standard was written: the owner approved a legendary-tier Pokémon for each Elite Four member, and no restricted legendary but N's Zekrom. |
| P5 | [V] | A legendary-tier species the player meets as a wild or static Pokémon does not appear on a trainer team on the same map or the map before it (D47: "Articuno and Zapdos left the Aces at their own catch spots"). Type: Null and Poipole count as legendary-tier for P4 even with an Eviolite. |
| P6 | [V] | **Map weather.** Overworld rain, sandstorm, drought and snow start the same weather in battle (`FIELD_EFFECT_OVERWORLD_WEATHER`; `#define B_OVERWORLD_SNOW GEN_LATEST`). In this build: rain on Routes 40 and 17, Cianwood City, Olivine City and Olivine's port; thunderstorm (rain) on Route 41 and the Lake of Rage; snow on Mt. Silver, Routes 49 and 50, New Sinjoh and the Sinjoh Ruins (each map's `map.json` `"weather"`). Fog on Seafoam's secret cave does nothing (`#define B_OVERWORLD_FOG GEN_3`). Every designed team on such a map uses the weather, or carries its own setter of another weather. No Pokémon there depends on a weather the map cancels. The 0.15.2 audit found Kaia, Ryker, Aaron, Lois, Maylene and Byron. EI 9: "Route weather sets the mini-bosses' plans ... The teams are built for it." |
| P7 | [C] | **Battle effects.** A permanent terrain or Trick Room from the trainer's `Starting Status` (supported by `tools/trainerproc/main.c`; `STARTING_STATUS_*_TERRAIN`, `STARTING_STATUS_TRICK_ROOM` in `include/constants/battle.h`) only on rematch and postgame bosses, and named in the trainer document (G1). RR 10.1, from its v4.0 changelog: "Surge has auto electric terrain for rematch", "Erika has auto grassy terrain for rematch". The engine has no pre-status field (trainerproc's per-Pokémon keys stop at "'Tera Type'"), so EI's pre-burned Guts users become Flame Orb users. |
| P8 | [C] | **Alternative teams.** The Elite Four and late bosses may have alternative teams through a trainer party pool (`Party Size`, `Pool Rules`, `Tags` in trainerproc; `DoTrainerPartyPool`, `src/trainer_pools.c`). RR 10.4: "every Elite Four member two"; EI 9: "Each of three members has two teams, picked at random". Optional. Every possible pick must pass the rules. |

## 11. Class themes

| Rule | Check | Rule text |
|---|---|---|
| C1 | [V] | Each Pokémon of an ordinary trainer, mini-boss or Ace shares at least one type with its class's theme (table 11.1), apart from one off-theme partner per team from 3 Pokémon up. [W] if a class's share over the whole game falls below 75%. RR 12.1's table: Swimmer "Water 96%", Bug Catcher "Bug 86%", Bird Keeper "Flying 80%"; EI 1.8: "Swimmers and Fishermen are 82–90% Water, Black Belts 88% Fighting, Bird Keepers 80% Flying". |
| C2 | [C] | Species come from all nine generations (RR 12.1: "The species are drawn from all nine generations"; EI 9: "The species come from every generation") and fit the class and the level (EI 4: "Filler species are picked to suit the level"). See S3. |
| C3 | [C] | Gym trainers share their Gym's type. Team Rocket uses Poison, Dark and Normal, with one partner of another type. Mini-bosses keep the class theme and add a plan (RR 12.2: "Mini-bosses keep the theme and add a plan"; D30: "themed by the trainer's class"). |
| C4 | [C] | A trainer's names, places and lines stay Heart & Soul's (D30: "Their names, places and lines are Heart & Soul's; only the teams changed"). A team that contradicts its trainer's own line is changed. An example is a Fisherman who talks of his Qwilfish: the Qwilfish stays, though it may be the evolved form or a regional one. |

### 11.1 Theme types for Heart & Soul's classes

Counts are the trainers placed on the maps, counted for this standard. The last column gives
0.15.2's shares, of the Pokémon as the battle code fields them at the NORMAL cap.

| Class (trainers) | Theme types | Main types in 0.15.2 |
|---|---|---|
| Team Rocket (31) | Poison, Dark; Normal | Poison 46%, Flying 19%, Normal 18% |
| Picnicker (29), Lass (18), Pokéfan (13), Beauty (5), Parasol Lady (7) | Normal, Fairy, Grass; cute Pokémon of any type | Grass 38%, Poison 35%; Grass 33%, Normal 19%; Electric 35%, Fire 31% |
| School Kid (26) | Psychic, Electric, Grass, Steel (studied Pokémon) | Grass 26%, Psychic 21%, Electric 20% |
| Fisherman (26), Swimmer F (19), Swimmer M (13), Tuber (1) | Water | Water 100% |
| Sailor (12) | Water, Fighting | Water 68%, Fighting 60% |
| Hiker (25) | Rock, Ground; Fighting, Steel | Ground 72%, Rock 52% |
| Bug Catcher (23) | Bug | Bug 98% |
| Camper (18) | Ground, Bug, Grass, Fire, Water (the outdoors) | Ground 32%, Water 28% |
| Bird Keeper (15) | Flying | Flying 100% |
| Youngster (14) | Normal and early-route Pokémon of any type | Normal 50% |
| Pokémaniac (14), Collector (5) | Dragon, Ghost, Ground and rare or odd species | Ground 43%, Poison 30% |
| Biker (14) | Poison, Dark, Fire, Steel | Poison 44%, Flying 20%, Fire 20% |
| Juggler (10) | Psychic, Electric, Ghost | Electric 52%, Bug 30% |
| Super Nerd (9) | Steel, Electric, Poison, Psychic | Steel 50%, Electric 25% |
| Sage (9) | Grass in the Sprout Tower (the Bellsprout line), Ghost and Psychic elsewhere | Grass 67%, Poison 57% |
| Psychic M (9), Psychic (1) | Psychic | Psychic 100% |
| Hex Maniac (3) | Ghost, Dark, Psychic | Psychic 43%, Ghost 29% |
| Black Belt (8), Battle Girl (3) | Fighting | Fighting 80%; Water 67% |
| Firebreather (7), Burglar (3) | Fire; Fire and Poison | Fire 64%; Fire 50% |
| Skier (6) | Ice | Ice 64% |
| Dragon Tamer (4) | Dragon | Dragon 80% |
| Gentleman (4), Officer (3) | Normal, Fire (pedigree and police dogs) | Fire, Normal, Electric 33% each; Normal 67% |
| Guitarist (2) | Electric, Poison (punk) | Electric 100% |
| Twins (5), Young Couple (2) | a pair's theme, built for doubles (section 12) | Flying 42%; mixed |
| Kimono Girl (3, New Sinjoh) | Eevee's line and the dance's types | mixed |
| Single trainers: Rocket Admin, Professor, Pkmn Trainer, Expert, Cooltrainer, Camper (HnS) | their own story's types | mixed |

## 12. Doubles

| Rule | Check | Rule text |
|---|---|---|
| DB1 | [V] | Each of Heart & Soul's nine double-battle trainers is built for doubles: Amy & May, Ann & Anne, Jo & Zoe, Meg & Peg, Lea & Pia, Thom & Kae, Duff & Eda, Finley and Mualani (`Double Battle: Yes` in `trainers_hns.party`). Each team has Fake Out or redirection (Follow Me, Rage Powder, Lightning Rod, Storm Drain), a spread move, and speed control (Tailwind, Trick Room, Icy Wind, Electroweb). [C] The pair has a synergy: an ability that helps the partner, Pledge pairs, Plus and Minus, weather or terrain with its abusers. RR 11.2: "Lass Ali ... all with Round", "Youngster Timmy: Plusle (Plus) and Electrike (Minus)", "Spread moves ... Fake Out, Tailwind and Follow Me are common in these teams"; EI 10. |
| DB2 | [V] | Two-opponent battles. A trainer fought in a tag battle, or one whose line of sight meets another trainer's on a walkable tile, battles with its first three Pokémon only (Z2). Those three must stand on their own and pass P3 where a Mega is required. The 0.15.2 audit, on Ariana: "her designed Vileplume, Gyarados and Honchkrow never battle" (`RocketHideout_B2F_hns/scripts.inc`: `multi_2_vs_2 TRAINER_ARIANA_1_HNS, ..., TRAINER_GRUNT_23_HNS, ..., PARTNER_LANCE_HNS`). D47 found the same for Aces: "two trainers who see the player at once battle together with three Pokémon each". |
| DB3 | [C] | New doubles for key battles are allowed (RR 11.1: 27 of the boss sheet's 166 teams are doubles; EI holds its rival, Maxie, Archie, Tate and Liza and the Champions as doubles). They need a script change and the owner's decision, because D30 chose mini-bosses "without double battles". |

## 13. Rematches

| Rule | Check | Rule text |
|---|---|---|
| R1 | [V] | Each phone rematch tier is a team made for its own stage. Tier 2's stage is at least the later of stage 3 and the first battle's stage: rematches need three badges (`HasEnoughBadgesForRematch`, `#define OW_REMATCH_BADGE_COUNT 3 // After Whitney`). Each tier's stage is at least the stage of the tier before. The rematch gate offers a tier only from its stage, tier 2 included (`GetMaxRematchStageForBadges`, for every tier made for a stage; Heart & Soul's own tiers keep its level ceiling). |
| R2 | [V] | A tier is a new team, not a copy of the one before. It keeps the trainer's theme and ace, and adds a Pokémon (Z3), evolves its line or upgrades its sets. RR 13.1: "The teams are not the first teams leveled up"; D47: "three Cooltrainers' rematches (Gaven, Beth, Reena) have their first battle's teams". EI copies its tiers (EI 11), which we do not follow. |
| R3 | [V] | Boss rematches (`_2` at J, `_POSTOBC` at K) are new teams (D47). |
| R4 | [V] | A tier list that repeats an ID in `gRematchTable` keeps the repeated ID's team. Examples: `TRAINER_KENNY_3_HNS` three times, `TRAINER_KENJI_2_HNS` four times. The validator reads the table and checks each distinct ID once. |

## 14. Variety and no copying

| Rule | Check | Rule text |
|---|---|---|
| S1 | [V] | No species twice on a team (RR 5.3: "Species repeat in only 2 teams"). Twins and couples may mirror one species as their stated theme. The 0.15.2 audit found "17 trainers with three to six of one species (Darin's and Paul's four Dragonite with the same moves)". |
| S2 | [W] | No species on more than two ordinary trainers of the same map. No species on more than 12 ordinary trainers in the game; EI's most common filler species, Manectric, appears 8 times (a count of Emerald Imperium's trainer data). 0.15.2's most common: "Seaking (30), Golem (30), Weezing (23)". |
| S3 | [W] | At least 35% of each designer packet's Pokémon (section 0.3) come from Gens 3 to 9. At least 350 distinct species across the ordinary trainers. Counts of both games' trainer data: RR's ordinary trainers are 61% Gen 1 and 9% Gen 2, so 30% are later generations, with 476 species over 1,251 Pokémon. EI's filler is 23% Gen 1 and 10% Gen 2, so 67% later, with 368 species over 583. 0.15.2's: "92% of the species are Gen 1 or 2", 210 species over 1,015 Pokémon. Johto and Kanto Pokémon stay the core, as Kanto's do in RR. |
| S4 | [V] | No exact set (species, item, ability and four moves) repeats on two designed teams, except across the versions of one battle: the rival's three, the Gym versions, rematch tiers and Red's two. No designed team shares more than three species with a boss of the same or the next stage (D47's critic found "Hayate was Janine's and Koga's team one route from Fuchsia"). Decided after the standard was written: the species rule is about another trainer's boss, so one trainer's own battles may share species (Blue and his postgame rematch). |
| S5 | [C] | Signposting. A route mini-boss or a promoted trainer is recognisable, and is listed in the trainer document (G1). RR signposts its mini-bosses with "a pre-battle transition" (RR 1, from its v2.3 changelog); EI lists them in its sheet "in route order, '(Optional)' marked" (EI 12). |
| S6 | [V] | **No copying (D2).** A review script compares every designed set and team with both games' parsed data: RR's boss sheet and trainer dumps, and EI's trainer parties. It refuses an exact set (species, item, ability and the same four moves) and a team sharing four or more species with one of theirs. The parsed data is not committed (D2). Decided after the standard was written: Red keeps Heart & Soul's canonical six species (Pikachu, Espeon, Snorlax, Venusaur, Blastoise and Charizard), an accepted exception to the shared-species test; his sets are ours. |
| G1 | [V] | **Trainer document.** The generators write `docs/crystal_imperium/TRAINERS.md`: every designed team by stage and map, with its plan, sets, window and Bag items. RR's community keeps "the community's official boss doc" and EI publishes its "Boss Battles" sheet; ours is generated so it never drifts. |

## 15. The difficulty curve from the first route to the postgame

Every Pokémon is at the player's cap (L2), so the curve is carried by the teams themselves. The
table gives what a stage's teams must have, with rule numbers. "Bosses" includes side battles. The
columns for both games restate RR 15 and EI 13.

| Stage (cap N/H) | Ordinary trainers | Mini-bosses, Aces | Bosses | Both games at this point |
|---|---|---|---|---|
| 0 (15/12): Falkner, Li, Candice | 1 to 2 Pokémon; no items; chosen moves; early middle stages allowed | 3; berries, Eviolite (at most two), Muscle Band; no EVs; neutral natures allowed; no Mega | Falkner 6, Li 3, Candice 6, the rival 1; no EVs, Mega or legendary; unevolved item evolvers allowed (E2); strongest attack around 65 (M5) | RR phase A: "2-4 Pokemon teams with berries and Eviolite", no EVs, no Mega; EI cap 15: 83% not fully evolved, 65 power |
| 1 (24/21): Bugsy, Proton in the Slowpoke Well | 1 to 3 | 4; Silk Scarf, Charcoal, Light Ball, Orbs | Bugsy and Proton 6; no EVs; about 70 to 80 power | EI caps 20–25: no EVs, "about 70 BP, pivots" |
| 2 (33/30): Whitney, the rival in Azalea, Gardenia | 2 to 3 | 4 (mini-bosses), 5 (Aces) | 6; item evolvers evolved except the named Eviolite species (E2, E3); the ace may have EVs (V4); Focus Sash, Leftovers, Expert Belt; attackers at 70 power or more (M5) | EI caps 30–34: first Megas (Wattson, Fantina), full EVs at 34; RR's 3rd Gym: first Mega |
| 3 (42/39): Morty, the Burned Tower rival, Fantina | 2 to 3 | 5; EVs on Aces and mini-bosses from here (V4) | 6; one Mega each (P3); full EVs (V4); setup and priority on the team (M8); fully evolved except named Eviolite species and middle stages below their level | EI's jump, cap 44: "fully evolved teams, full EVs, Life Orb and Choice items, a Mega on most teams" |
| 4 (50/47): Chuck, Jasmine or Pryce first, the Rocket Hideout, Eusine, Maylene | 2 to 4 | 5 to 6 | 6; Assault Vest, Booster Energy, Weakness Policy | RR phase B: "first Mega, first full EVs"; EI cap 47: 6 from Flannery |
| 5 (58/55): the second of Chuck, Jasmine and Pryce, Wake | 2 to 4 | 6; a Mega on one in three (P3) | 6; Paradox or Ultra Beast allowed, one (P4) | RR cap 59: "one or two Paradox Pokemon" |
| 6 (66/63): the third of them, Byron | 2 to 4 | 6 | 6 | RR phase C: "themed weather routes"; EI 64–68: Megas on 13 of 15 |
| 7 (75/72): Clair, the Radio Tower, the Goldenrod Underground rival, Roark | 2 to 4 | 6 | 6; a sub-legendary or mythical allowed, one (P4) | RR caps 80–82: "sub-legendaries, Mythicals and Ultra Beasts" |
| 8 (85): Victory Road, the Elite Four, Lance, the Kimono Girls, Volkner | 2 to 4 | 6; a Mega on two in three (P3) | 6; every Elite Four member one legendary-tier Pokémon, Lance up to two (P4) | RR cap 85: box legendaries; EI 84–85: "Mega on every team; restricted legendaries allowed" |
| J (90): Kanto, the Kanto leaders, Blue, the `_2` rematches, Paldea's side battles | 2 to 4 | 6; at most one sub-legendary (D47) | 6; EVs (V4); up to three legendary-tier on rematches (D47) | no direct match (both games end their story at 85); RR phase D, caps 73–85: Megas on 35 of 40 teams, legendary-tier Pokémon on 26 of 40 |
| K (100): Red, `_POSTOBC`, the postgame side battles, the bonus areas | postgame tier: 4 to 6, boss rules (Z4) | 6 | 6; no EVs except Red (V4); Red the hardest (D27) | RR 13.4: "Postgame: everyone becomes a boss"; EI: Elite Four at 100 |

Where we stay above both games on purpose: every Pokémon at the cap; six-Pokémon Gym Leaders from
the first Gym (D30); Bag items on bosses (I8); designed movesets for ordinary trainers (M1, M10).
Where we stay below on purpose: no restricted legendaries but N's Zekrom (P4), and no EVs at K
except Red's (V4). Both are owner decisions, approved after the standard was written.

## 16. The rules in one table

The last column is what each rule found on 0.15.2's teams, the teams the standard was written
against: the audit's counts and counts made for this standard.

| Rule | Check | What it refuses or warns | On 0.15.2's teams |
|---|---|---|---|
| L1 | V (exists) | a Pokémon not at its stage's NORMAL cap | 0 |
| L3 | V | a team's stage later than the stage tool's earliest | not measured (needs the stage tool) |
| E1 | V | past a level evolution at a stage of its window | 26 Pokémon at their own stage |
| E2, E3 | V | an unevolved non-level evolver from stage 2 without a named Eviolite use | 8 without an Eviolite, 26 with a non-named Eviolite |
| E5 | V | more than 6 levels ahead of its line | 0 |
| E6 | V | below its stage when fought later (blocking item) | 28 more Pokémon on 19 teams |
| E7 | V | an Everstone | 0 |
| Z1, Z2 | V | a size outside table 4.1; a team cut by a two-opponent battle | Ariana's tag battle |
| I3 | V | an item three times; Eviolite twice from stage 2 | 21 teams with one item 3 to 5 times |
| I4, I5 | V, W | an item that does nothing; a weak item | 6 and 5 |
| N2, V2 | V | Speed on a Trick Room or Gyro Ball set | 31 Pokémon with 31 Speed IVs; natures already pass |
| V3 | V | Hidden Power of the wrong type | 1 (Bret's Magnezone) |
| V4 | V | no EVs on a designed team from stage 3 to J | 89 teams |
| A2 | V | a dead ability | 35 Pokémon |
| M2, M5, M6, M7 | V, W | filler, weak power, inaccurate moves (50% or less), weak setup | 23, 10, 1, 3 |
| P2 | V | Trick Room on one Pokémon of a fast team | 4 teams |
| P3 | V | no Mega on a boss from stage 3; too few on mini-bosses and Aces from stage 5 | 14 bosses and side battles (Geeta and N are exempt by D41); 0 of 71 optional teams from stage 5 |
| P4 | V | an Elite Four member without a legendary-tier Pokémon | 5 (Will, Koga, Bruno, Karen, Lance) |
| P6 | V | a team that ignores its map's weather | 6 |
| DB1, DB2 | V | a double without doubles tools; three lost in a tag battle | 9 Heart & Soul doubles to design; Ariana |
| R1, R2 | V | a rematch tier offered before its stage, or a copy | Gaven, Beth and Reena (D47 copies); the rematch gate |
| S1, S2, S3 | V, W | species repeats; a packet under 35% newer generations | 17 trainers with 3 to 6 of one species; 92% Gen 1 and 2 |
| S6 | V | a copied RR or EI set or team | run in review |
