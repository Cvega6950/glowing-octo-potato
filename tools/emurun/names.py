#!/usr/bin/env python3
"""Annotate emurun output with species and move names: python3 tools/emurun/names.py < log"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
species = {int(v): k[8:] for k, v in re.findall(r"#define (SPECIES_\w+)\s+(\d+)\b", open(os.path.join(ROOT, "include/constants/species.h")).read())}
moves = {}
for name, val in re.findall(r"^\s*(MOVE_\w+)\s*=\s*(\d+)\s*,", open(os.path.join(ROOT, "include/constants/moves.h")).read(), re.M):
    moves[int(val)] = name[5:]
# enum entries without explicit values follow the previous one
cur = -1
for line in open(os.path.join(ROOT, "include/constants/moves.h")):
    m = re.match(r"\s*(MOVE_\w+)\s*(?:=\s*([^,]+))?,", line)
    if not m:
        continue
    if m.group(2):
        try:
            cur = int(m.group(2))
        except ValueError:
            cur = {v: k for k, v in moves.items()}.get(m.group(2).strip()[5:], cur) if m.group(2).strip().startswith("MOVE_") else cur
            continue
    else:
        cur += 1
    moves.setdefault(cur, m.group(1)[5:])
for line in sys.stdin:
    line = re.sub(r"species (\d+)", lambda m: species.get(int(m.group(1)), m.group(0)), line)
    line = re.sub(r"move (\d+)", lambda m: moves.get(int(m.group(1)), m.group(0)), line)
    sys.stdout.write(re.sub(r"\[frame \d+\] autobattle: ", "", line))
