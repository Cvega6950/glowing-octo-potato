"""Crystal Imperium Ace Trainers (DECISIONS.md D47): the tables tools/crystal_imperium/ace_trainers.py
writes from. ACES are new trainers on the routes; UPGRADES give Heart & Soul's own Ace Trainers
(Cooltrainers) competitive teams. A team is a list of Pokemon as boss_teams.py's mon() makes them;
a stage is the badge count when the route is reached (9: after the Johto League), which sets the
party data's levels (ace_trainers.party_levels)."""


def mon(species, item, ability, nature, moves, evs=None):
    return {"species": species, "item": item, "ability": ability, "nature": nature, "moves": moves, "evs": evs}


ACES = [
]

UPGRADES = {}
