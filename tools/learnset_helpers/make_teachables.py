#!/usr/bin/env python3

"""
Usage: python3 make_teachable.py SOURCE_DIR

Build a C-header defining the set of teachable moves for each configured-on
species-family based on the learnable moves defined in SOURCE_DIR/all_learnables.json.

A move is "teachable" if it is:
    1. Can be taught by some Move Tutor in the overworld, which is identified by
       using the ChooseMonForMoveTutor special in a script and setting VAR_0x8005
       to the offered MOVE constant. (e.g., MOVE_SWAGGER)
    2. Assigned to some TM or HM in include/constants/tms_hms.h using the
       FOREACH_TM macro.
    3. A universal move, as defined by universalMoves in
       src/data/pokemon/special_movesets.json

For a given species, a move is considered teachable to that species if:
    1. The species can learn the move via *any* method within any Expansion-
       supported game.
    2. The species rule defined by their teachingType in the species_info folder

Crystal Imperium (DECISIONS.md D39): with P_IMPERIUM_SPECIES_DATA, Radical Red decides instead for
the moves it teaches by TM or tutor (src/data/pokemon/imperium_teachables.json, written by
tools/crystal_imperium/imperium_species.py): a species that has Radical Red data learns one of them
if it does there. An HM move also stays teachable to a species that learns it in an official
game: Radical Red's HM lists leave out many newer forms (Alolan Geodude's Rock Smash). Radical
Red's TM and tutor moves that are neither TMs nor tutor moves here become tutor moves (the move
relearner teaches them).
"""

from itertools import chain
from textwrap import dedent

import json
import pathlib
import re
import sys
import typing


CONFIG_ENABLED_PAT = re.compile(r"^#define P_LEARNSET_HELPER_TEACHABLE\s+(?P<cfg_val>[^ ]*)", flags=re.MULTILINE)
IMPERIUM_ENABLED_PAT = re.compile(r"^#define P_IMPERIUM_SPECIES_DATA\s+(?P<cfg_val>[^ ]*)", flags=re.MULTILINE)
IMPERIUM_TEACHABLES_JSON = pathlib.Path("./src/data/pokemon/imperium_teachables.json")
ALPHABETICAL_ORDER_ENABLED_PAT = re.compile(r"^#define HGSS_SORT_TMS_BY_NUM\s+(?P<cfg_val>[^ ]*)", flags=re.MULTILINE)
TM_LITERACY_PAT = re.compile(r"^#define P_TM_LITERACY\s+GEN_(?P<cfg_val>[^ ]*)", flags=re.MULTILINE)
TMHM_MACRO_PAT = re.compile(r"F\((\w+)\)")
SNAKIFY_PAT = re.compile(r"(?!^)([A-Z]+)")

def enabled() -> bool:
    """
    Check if the user has explicitly enabled this opt-in helper.
    """
    with open("./include/config/pokemon.h", "r") as cfg_pokemon_fp:
        cfg_pokemon = cfg_pokemon_fp.read()
        cfg_defined = CONFIG_ENABLED_PAT.search(cfg_pokemon)
        return cfg_defined is not None and cfg_defined.group("cfg_val") in ("TRUE", "1")

def extract_repo_tms(build: str = "") -> typing.Generator[str, None, None]:
    """
    Yield MOVE constants assigned to a TM or HM in the user's repo.
    When `build` is set (e.g. "POKEMON_HNS", "FIRERED"), only yield
    TMs from the matching #if block; otherwise yield all.
    """
    with open("./include/constants/tms_hms.h", "r") as tmshms_fp:
        text = tmshms_fp.read()

    if not build:
        for m in TMHM_MACRO_PAT.finditer(text):
            yield f"MOVE_{m.group(1)}"
        return

    BUILD_GUARD_MAP = {
        "POKEMON_HNS": "IS_HNS",
        "FIRERED": "IS_FRLG",
        "LEAFGREEN": "IS_FRLG",
    }
    target_guard = BUILD_GUARD_MAP.get(build, "")

    # Simple state machine for top-level #if IS_X / #else / #endif
    active = True
    depth = 0
    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#if ") or stripped.startswith("#ifdef"):
            depth += 1
            if depth == 1:
                active = bool(target_guard and target_guard in stripped)
            continue
        if stripped.startswith("#else") and depth == 1:
            active = not active
            continue
        if stripped.startswith("#endif"):
            if depth == 1:
                active = True
            depth = max(0, depth - 1)
            continue

        if active:
            m = TMHM_MACRO_PAT.search(line)
            if m:
                yield f"MOVE_{m.group(1)}"

def extract_repo_hms(build: str = "") -> typing.Generator[str, None, None]:
    """
    Yield the MOVE constants of extract_repo_tms(build) that are HMs (FOREACH_HM).
    """
    with open("./include/constants/tms_hms.h", "r") as tmshms_fp:
        text = tmshms_fp.read()
    hms = set()
    for m in re.finditer(r"#define FOREACH_HM\(F\)((?:[^\n]*\\\n)*[^\n]*)", text):
        hms.update(f"MOVE_{name}" for name in TMHM_MACRO_PAT.findall(m.group(1)))
    for move in extract_repo_tms(build):
        if move in hms:
            yield move

def load_imperium_teachables():
    """
    Crystal Imperium (DECISIONS.md D39): Radical Red's TM and tutor moves and, for each species it
    has, the ones it learns there. None unless P_IMPERIUM_SPECIES_DATA is on.
    """
    with open("./include/config/pokemon.h", "r") as cfg_pokemon_fp:
        cfg_defined = IMPERIUM_ENABLED_PAT.search(cfg_pokemon_fp.read())
    if cfg_defined is None or cfg_defined.group("cfg_val") not in ("TRUE", "1"):
        return None
    with open(IMPERIUM_TEACHABLES_JSON, "r") as fp:
        data = json.load(fp)
    return {"moves": set(data["moves"]), "species": {sp: set(moves) for sp, moves in data["species"].items()}}

def imperium_extra_tutors(imperium, repo_tms: list[str], repo_tutors: list[str]) -> list[str]:
    """
    Radical Red's TM and tutor moves that are neither TMs nor tutor moves here.
    """
    if imperium is None:
        return []
    return sorted(imperium["moves"] - set(repo_tms) - set(repo_tutors))

def official_learnables(all_learnables: dict[str, set[str]], species_upper: str):
    """
    Crystal Imperium (DECISIONS.md D39): the official learnables of a list's species. A form without
    data of its own (BASCULEGION_F, given a list to follow Radical Red's) has its base species'.
    """
    name = species_upper
    while name not in all_learnables and "_" in name:
        name = name.rsplit("_", 1)[0]
    return all_learnables[name]

def extract_tm_litteracy_config() -> bool:
    config = False
    with open("./include/config/pokemon.h", "r") as cfg_pokemon_fp:
        cfg_pokemon = cfg_pokemon_fp.read()
        cfg_defined = TM_LITERACY_PAT.search(cfg_pokemon)
        if cfg_defined:
            cfg_val = cfg_defined.group("cfg_val")
            if ((cfg_val == "LATEST") or (int(cfg_val) > 6)):
                config = True
    return config

def prepare_output(all_learnables: dict[str, set[str]], tms: list[str], tutors: list[str], special_movesets, repo_teaching_types, header: str, imperium=None, hms=()) -> str:
    """
    Build the file content for teachable_learnsets.h.
    """

    tm_litteracy_config = extract_tm_litteracy_config()

    cursor = 0
    new = header + dedent("""
    static const u16 sNoneTeachableLearnset[] = {
        MOVE_UNAVAILABLE,
    };
    """)

    joinpat = ",\n    "
    for species_data in repo_teaching_types:
        if isinstance(species_data, str):
            new += (species_data)
            continue
        species = species_data["name"]
        teaching_type = species_data["teaching_type"]
        new += f"static const u16 s{species}TeachableLearnset[] = "
        new += "{\n"
        species_upper =  SNAKIFY_PAT.sub(r"_\1", species).upper()
        if teaching_type == "ALL_TEACHABLES":
            part1 = list(filter(lambda m: m not in special_movesets["signatureTeachables"], tms))
            part2 = list(filter(lambda m: m not in special_movesets["signatureTeachables"], tutors))
        else:
            if teaching_type == "TM_ILLITERATE":
                learnables = official_learnables(all_learnables, species_upper)
                if not tm_litteracy_config:
                    learnables = filter(lambda m: m not in special_movesets["universalMoves"], learnables)
            else:
                learnables = official_learnables(all_learnables, species_upper) + special_movesets["universalMoves"]
            part1 = list(filter(lambda m: m in learnables, tms))
            part2 = list(filter(lambda m: m in learnables, tutors))


        repo_species_teachables = part1 + part2
        rr_moves = imperium["species"].get(f"SPECIES_{species_upper}") if imperium else None
        if rr_moves is not None:
            # Crystal Imperium (DECISIONS.md D39): Radical Red's lists decide for its TM and tutor moves
            official = set(repo_species_teachables)
            repo_species_teachables = [m for m in tms + tutors
                                       if m in rr_moves or (m in official and (m not in imperium["moves"] or m in hms))]
        if species_upper == "TERAPAGOS":
             repo_species_teachables = filter(lambda m: m != "MOVE_TERA_BLAST", repo_species_teachables)

        repo_species_teachables = list(dict.fromkeys(repo_species_teachables))
        new += "\n".join([
            f"    {joinpat.join(chain(repo_species_teachables, ('MOVE_UNAVAILABLE',)))},",
            "};\n",
        ])

    return new

def prepare_header(h_align: int, tmshms: list[str], tutors: list[str], universals: list[str]) -> str:
    universals_title = "Near-universal moves found in data/special_movesets.json:"
    tmhm_title = "TM/HM moves found in \"include/constants/tms_hms.h\":"
    tutor_title = "Tutor moves found from map scripts:"
    h_align = max(h_align, len(universals_title), len(tmhm_title), len(tutor_title))

    lines = [
         "//",
         "// DO NOT MODIFY THIS FILE! It is auto-generated by tools/learnset_helpers/make_teachables.py",
         "//",
         "",
        f"// {'*' * h_align} //",
        f"// {tmhm_title: >{h_align}} //",
    ]
    lines.extend([f"// - {move: <{h_align - 2}} //" for move in tmshms])
    lines.extend([
        f"// {'*' * h_align} //",
        f"// {tutor_title: <{h_align}} //",
    ])
    lines.extend([f"// - {move: <{h_align - 2}} //" for move in sorted(tutors)])
    lines.extend([
        f"// {'*' * h_align} //",
        f"// {universals_title: <{h_align}} //",
    ])
    lines.extend([f"// - {move: <{h_align - 2}} //" for move in universals])
    lines.extend([
        f"// {'*' * h_align} //",
         "",
    ])

    return "\n".join(lines)

def create_tutor_moves_array(tutors):
    """
    Generate gTutorMoves[].
    """
    header = dedent("""\
        // DO NOT MODIFY THIS FILE! It is auto-generated by tools/learnset_helpers/make_teachables.py
        // Needed by tutor moves relearner!

        const u16 gTutorMoves[] = {
    """)

    lines = [f"    {move}," for move in tutors]
    lines.append("    MOVE_UNAVAILABLE\n};\n")
    with open("./src/data/tutor_moves.h", "w") as f:
        f.write(header + "\n".join(lines))

def make_move_tutors(build_dir, special_movesets, imperium=None, repo_tms=()):
    SOURCE_TUTORS_JSON = build_dir / "all_tutors.json"

    assert SOURCE_TUTORS_JSON.exists(), f"{SOURCE_TUTORS_JSON=} does not exist"
    assert SOURCE_TUTORS_JSON.is_file(), f"{SOURCE_TUTORS_JSON=} is not a file"

    with open(SOURCE_TUTORS_JSON, "r") as fp:
        repo_tutors = json.load(fp)

    repo_tutors = sorted(list(set(repo_tutors + special_movesets["extraTutors"])))
    repo_tutors = sorted(set(repo_tutors + imperium_extra_tutors(imperium, list(repo_tms), repo_tutors)))
    create_tutor_moves_array(repo_tutors)

    return repo_tutors

def main():
    if not enabled():
        quit()

    tutor_mode = False
    build_target = ""
    args = sys.argv[1:]

    while args and args[0].startswith("--"):
        if args[0] == "--tutors":
            tutor_mode = True
            args.pop(0)
        elif args[0] == "--build" and len(args) > 1:
            args.pop(0)
            build_target = args.pop(0)
        else:
            print(f"Unknown option: {args[0]}", file=sys.stderr)
            quit(1)

    if len(args) != 1:
        print("Invalid number of arguments", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        quit(1)

    SOURCE_DIR = pathlib.Path(args[0])

    with open("src/data/pokemon/special_movesets.json", "r") as file:
        special_movesets = json.load(file)

    imperium = load_imperium_teachables()
    repo_tutors = make_move_tutors(SOURCE_DIR, special_movesets, imperium, extract_repo_tms(build_target))
    if tutor_mode:
        quit(0)

    SOURCE_LEARNSETS_JSON = pathlib.Path("./src/data/pokemon/all_learnables.json")
    SOURCE_TEACHING_TYPES_JSON = SOURCE_DIR / "all_teaching_types.json"

    assert SOURCE_LEARNSETS_JSON.exists(), f"{SOURCE_LEARNSETS_JSON=} does not exist"
    assert SOURCE_LEARNSETS_JSON.is_file(), f"{SOURCE_LEARNSETS_JSON=} is not a file"

    assert SOURCE_TEACHING_TYPES_JSON.exists(), f"{SOURCE_TEACHING_TYPES_JSON=} does not exist"
    assert SOURCE_TEACHING_TYPES_JSON.is_file(), f"{SOURCE_TEACHING_TYPES_JSON=} is not a file"

    repo_tms = list(extract_repo_tms(build_target))

    with open("./include/config/pokedex_plus_hgss.h", "r") as cfg_pokemon_fp:
        cfg_pokemon = cfg_pokemon_fp.read()
        cfg_defined = ALPHABETICAL_ORDER_ENABLED_PAT.search(cfg_pokemon)
        if cfg_defined is None or cfg_defined.group("cfg_val") in ("FALSE", "0"):
            repo_tms = sorted(repo_tms)

    h_align = max(map(lambda move: len(move), chain(special_movesets["universalMoves"], repo_tms, repo_tutors))) + 2
    header = prepare_header(h_align, repo_tms, repo_tutors, special_movesets["universalMoves"])

    with open(SOURCE_LEARNSETS_JSON, "r") as source_fp:
        all_learnables = json.load(source_fp)

    with open(SOURCE_TEACHING_TYPES_JSON, "r") as source_fp:
        repo_teaching_types = json.load(source_fp)

    hms = set(extract_repo_hms(build_target))
    content = prepare_output(all_learnables, repo_tms, repo_tutors, special_movesets, repo_teaching_types, header, imperium, hms)
    with open("./src/data/pokemon/teachable_learnsets.h", "w") as teachables_fp:
        teachables_fp.write(content)

if __name__ == "__main__":
    main()
