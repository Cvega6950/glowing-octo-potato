"""Crystal Imperium's team kit (docs/crystal_imperium/DECISIONS.md D47, D56, D59): the
mon() every designed team is written with, and the party file renderer the generators share
(boss_teams.py for the bosses, ace_trainers.py for the Ace Trainers and the upgraded Cooltrainers).

  mon(species, item, ability, nature, moves, evs=None, ivs=None, raised_item=None)

  species, item, ability, nature, moves  as the party file spells them ("Marowak Alola", "Sitrus Berry",
                         "Lightning Rod", "Adamant", four moves)
  evs                    a Showdown-style spread, "252 Atk / 4 SpD / 252 Spe" (at most 252 a stat, 510 in all)
  ivs                    a Showdown-style spread for the stats that are not 31, "0 Spe" or "0 Atk / 30 SpA"
                         (the party file gets all six); without it every IV is 31. The battle keeps an
                         uneven spread as it is (CreateNPCTrainerPartyFromTrainer, src/battle_main.c)
  raised_item            the item the Pokemon holds instead when its battle is fought after the stage
                         its team is made for and it has evolved there (sRaisedItems, src/battle_main.c):
                         an Eviolite holder's Sitrus Berry once it is a Tyranitar

A team made for a stage keeps its Pokemon as made at its stage's cap. Raised to a later cap it evolves as
any trainer's does, and only a named Eviolite species holding an Eviolite (NAMED_EVIOLITE) or a Pikachu
holding a Light Ball stays as it is (GetTrainerMonEvolvedSpecies).
"""
import re

STATS = ("HP", "Atk", "Def", "SpA", "SpD", "Spe")
MAX_IV = 31
MAX_EV = 252
MAX_EVS = 510

# Moves whose power comes from friendship. A trainer's Pokemon has its party entry's Happiness,
# 0 when it has none (CreateNPCTrainerPartyFromTrainer), which would leave Return at power 1.
FRIENDSHIP_MOVES = {"Return", "Pika Papow", "Veevee Volley"}
FULL_FRIENDSHIP = 255

# The named Eviolite species (the trainer standard's table 3.2, rule E3): the only ones a designed team
# may keep unevolved with an Eviolite from stage 2 on, and the only ones the battle code keeps as made
# when the team is raised to a later stage's cap (boss_teams.py writes them to sKeptUnevolvedSpecies in
# src/data/level_cap_bosses.h). Each is "tier A": with the Eviolite, its HP x Defense and HP x Sp. Def
# are at least 1.10 times those of every most-evolved form it could be, at every cap from 33 to 100
# (31 IVs, no EVs, a neutral nature). validate.py recomputes the tiers from the build's base stats and
# evolutions and fails if this list differs (Porygon is tier A too, but left out: its own evolution,
# Porygon2, is on the list and far bulkier with the same Eviolite).
NAMED_EVIOLITE = ("Porygon2", "Dusclops", "Charjabug", "Swadloon", "Shelmet", "Golbat", "Pikachu", "Electabuzz",
                  "Magmar", "Rhydon", "Gligar", "Chansey", "Scyther", "Eelektrik", "Misdreavus", "Sneasel", "Aipom",
                  "Togetic", "Type: Null", "Poipole")
# The tier A species the list leaves out, and why
NOT_NAMED = {"Porygon": "its evolution Porygon2 is named and far bulkier with the same Eviolite"}


def parse_stats(text, what="IVs"):
    """{stat: value} from a Showdown-style spread ("252 Atk / 4 SpD"); ValueError for anything else."""
    top = MAX_IV if what == "IVs" else MAX_EV
    out = {}
    for part in text.split("/"):
        m = re.fullmatch(r"\s*(\d+)\s+(HP|Atk|Def|SpA|SpD|Spe)\s*", part)
        if not m:
            raise ValueError(f"{what} {text!r}: each part is a number and one of {', '.join(STATS)}")
        value, stat = int(m.group(1)), m.group(2)
        if stat in out:
            raise ValueError(f"{what} {text!r}: {stat} twice")
        if value > top:
            raise ValueError(f"{what} {text!r}: {stat} {value} is above {top}")
        out[stat] = value
    if what == "EVs" and sum(out.values()) > MAX_EVS:
        raise ValueError(f"EVs {text!r}: {sum(out.values())} in all, above {MAX_EVS}")
    return out


def ivs_of(m):
    """A Pokemon's six IVs, {stat: value}: 31 except where its ivs say otherwise."""
    ivs = dict.fromkeys(STATS, MAX_IV)
    if m.get("ivs"):
        ivs.update(parse_stats(m["ivs"], "IVs"))
    return ivs


def evs_of(m):
    """A Pokemon's EVs, {stat: value} (0 for a stat its evs leave out)."""
    evs = dict.fromkeys(STATS, 0)
    if m.get("evs"):
        evs.update(parse_stats(m["evs"], "EVs"))
    return evs


def iv_line(m):
    """The party file's IVs line for a Pokemon: all six stats."""
    ivs = ivs_of(m)
    return " / ".join(f"{ivs[s]} {s}" for s in STATS)


def mon(species, item, ability, nature, moves, evs=None, ivs=None, raised_item=None):
    m = {"species": species, "item": item, "ability": ability, "nature": nature, "moves": moves, "evs": evs,
         "ivs": ivs, "raised_item": raised_item}
    # A malformed spread fails here, at the designer's line, not in the party file
    try:
        ivs_of(m)
        evs_of(m)
    except ValueError as e:
        raise ValueError(f"{species}: {e}") from None
    if raised_item is not None and not (isinstance(raised_item, str) and raised_item.strip()):
        raise ValueError(f"{species}: raised_item is an item's name, such as \"Sitrus Berry\"")
    return m


def render_mon(m, level):
    """One Pokemon of a party block in src/data/trainers_hns.party, at the given level."""
    out = f"\n{m['species']}" + (f" @ {m['item']}" if m.get("item") else "") + f"\nLevel: {level}\n"
    out += f"IVs: {iv_line(m)}\n"
    if m.get("evs"):
        out += f"EVs: {m['evs']}\n"
    if m.get("ability"):
        out += f"Ability: {m['ability']}\n"
    if m.get("nature"):
        out += f"Nature: {m['nature']}\n"
    if FRIENDSHIP_MOVES & set(m["moves"]):
        out += f"Happiness: {FULL_FRIENDSHIP}\n"
    out += "".join(f"- {mv}\n" for mv in m["moves"])
    return out


def render_mons(mons, level):
    return "".join(render_mon(m, level) for m in mons)


def constant(prefix, name):
    """A party file name as trainerproc writes its constant (fprint_constant: items, moves, abilities,
    natures): letters and digits upper-cased, apostrophes dropped, anything else an underscore."""
    out = []
    for c in name.strip():
        if c.isascii() and c.isalnum():
            out.append(c.upper())
        elif c not in "'’":
            out.append("_")
    return f"{prefix}_{''.join(out)}"


def species_constant(name):
    """A party file species as trainerproc writes its constant (fprint_species): runs of other characters
    are one underscore, apostrophes and % are dropped, the gender signs are _M and _F."""
    out, underscore = [], False
    for c in name.strip():
        if c.isascii() and c.isalnum():
            out.append(("_" if underscore and out else "") + c.upper())
            underscore = False
        elif c in "'%’":
            continue
        elif c in "♂♀":
            out.append("_M" if c == "♂" else "_F")
            underscore = False
        elif c == "é":
            out.append(("_" if underscore and out else "") + "E")
            underscore = False
        else:
            underscore = True
    return "SPECIES_" + "".join(out)
