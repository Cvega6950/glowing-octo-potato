#!/usr/bin/env python3
"""Crystal Imperium trainer AI measurement (DECISIONS.md D60).

A measurement build (include/imperium_ai_measure.h with IMPERIUM_AI_MEASURE 1) lets a play test
hand the player's side to a fixed AI. This script turns the designed battles of the play tests
(the bosses, Ace Trainers, Cooltrainers, rematches, side battles...) into AI-vs-AI runs: the same
player team at the same level cap as in the test, each battle played RUNS times from frame
offsets 1, 38, 75... A trainer AI that plays better wins more of them, and by more.

  ai_measure.py gen OUTDIR [--runs K] [--per-shard N] [--tests a,b,...] [--trainers T1,T2,...]
      write OUTDIR/shard_NNN.emu: each starts its own new game and plays about N battles
  ai_measure.py run ROM ELF OUTDIR [--jobs J] [--emulator mgba|vbam]
      play every shard in OUTDIR, J at a time; each shard's log is OUTDIR/shard_NN/log.txt
  ai_measure.py summary OUTDIR [BASEDIR]
      per-trainer results; with BASEDIR, the change from it (a variant against a baseline)

A battle's result is the player's win (1) or loss (0) and a margin: the player's remaining HP
share minus the trainer's, both as fractions of their teams' total HP (+1 a flawless player win,
-1 a flawless trainer win). Lower is a stronger trainer AI.
"""
import argparse
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

# The play tests whose battles are measured: every designed trainer battle
DEFAULT_TESTS = ["falkner", "bugsy", "whitney", "gym_trainers_m2", "bosses_m3", "bosses_m4", "bosses_m5",
                 "bosses_e4", "red", "route_bosses", "side_battles", "boss_rematches", "ace_trainers_johto",
                 "ace_trainers_kanto", "cooltrainers"]

BATTLE_RE = re.compile(r'^!battle\(\s*"(TRAINER_\w+)"\s*(,\s*double\s*=\s*True\s*)?\)\s*$')
SAMPLE_RE = re.compile(r'^!sample_battle\(\s*"(TRAINER_\w+)"(.*)\)\s*$')
STATE_ARG_RE = re.compile(r'"(\w+\.ss)"')


def parse_test(path):
    """The test's preamble (everything up to its first savestate) and its battles, each as
    (trainer constant, double, setup lines from the preamble's state). A battle's setup is the
    chain of lines that built the state it was fought from."""
    lines = [l.rstrip("\n") for l in open(path)]
    preamble, i = [], 0
    while i < len(lines) and not lines[i].startswith("savestate "):
        preamble.append(lines[i])
        i += 1
    if i == len(lines):
        return preamble, []
    first_state = lines[i].split()[1]
    states = {first_state: []}       # state name -> setup lines after the preamble
    current = []                     # setup lines of the state being built or fought from
    battles = []
    for line in lines[i + 1:]:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("loadstate "):
            name = s.split()[1]
            current = list(states.get(name, []))
            continue
        if s.startswith("savestate "):
            states[s.split()[1]] = list(current)
            continue
        m = BATTLE_RE.match(s)
        if m:
            battles.append((m.group(1), bool(m.group(2)), list(current)))
            current = None  # the battle changes the state; the test loads another before the next
            continue
        m = SAMPLE_RE.match(s)
        if m:
            st = STATE_ARG_RE.search(m.group(2))
            setup = states.get(st.group(1), []) if st else (current or [])
            battles.append((m.group(1), False, list(setup)))
            continue
        if current is None:
            continue  # after a battle: checks of its result
        # Setup: a team, items, flags, pokes. Checks of the game's state (expect..., waituntil...)
        # aren't needed to rebuild it.
        if s.startswith(("expect", "waituntil", "within", "shot ", "tally", "peek")):
            continue
        current.append(s)
    return preamble, battles


def gen(args):
    tests = args.tests.split(",") if args.tests else DEFAULT_TESTS
    os.makedirs(args.outdir, exist_ok=True)
    total = trainers = n = 0
    for t in tests:
        preamble, battles = parse_test(os.path.join(HERE, "tests", t + ".emu"))
        groups = {}
        only = set(args.trainers.split(",")) if args.trainers else None
        for trainer, double, setup in battles:
            if only is not None and trainer not in only:
                continue
            key = tuple(setup)
            if key not in groups:
                groups[key] = []
            if (trainer, double) not in groups[key]:
                groups[key].append((trainer, double))
        # A shard starts the game from power-on (its own emulator run), so it holds one test's
        # battles; a big test is split into shards of about --per-shard battles
        chunks, cur, size = [], [], 0
        for setup, tr in groups.items():
            for i in range(0, len(tr), max(1, args.per_shard // args.runs)):
                part = tr[i:i + max(1, args.per_shard // args.runs)]
                if cur and size + len(part) * args.runs > args.per_shard:
                    chunks.append(cur)
                    cur, size = [], 0
                cur.append((list(setup), part))
                size += len(part) * args.runs
        if cur:
            chunks.append(cur)
        chunks = [c for c in chunks if c]
        for chunk in chunks:
            out = ["# Crystal Imperium AI measurement shard (tools/emurun/ai_measure.py): AI-vs-AI runs",
                   f"# from tests/{t}.emu"]
            out += [l for l in preamble if l.strip() and not l.strip().startswith("#")]
            out.append("savestate base.ss")
            for gi, (setup, part) in enumerate(chunk):
                state = f"g{gi}.ss"
                out += ["loadstate base.ss"] + setup + [f"savestate {state}"]
                for trainer, double in part:
                    trainers += 1
                    for k in range(args.runs):
                        out += [f"loadstate {state}", f"wait {1 + 37 * k}", "poke8 {gImperiumAiVsAi} 1",
                                f'!battle("{trainer}"{", double=True" if double else ""})',
                                f'!autobattle("0,0,0,0,0,0", {args.max_frames})',
                                f"peek8 {{gBattleOutcome}} aim_{trainer}"]
                        total += 1
            open(os.path.join(args.outdir, f"shard_{n:03d}.emu"), "w").write("\n".join(out) + "\n")
            n += 1
    print(f"{total} battles ({trainers} trainer battles x {args.runs}) in {n} shards")


def run(args):
    shards = sorted(f for f in os.listdir(args.outdir) if re.match(r"shard_\d+\.emu$", f))
    # The biggest shards first, so the last ones to finish are short
    env = dict(os.environ)
    if args.emulator == "vbam":
        env.setdefault("EMURUN_CORE", os.path.join(ROOT, "build", "vbam", "src", "libretro", "vbam_libretro.so"))
    procs = []
    pending = list(shards)
    while pending or procs:
        while pending and len(procs) < args.jobs:
            s = pending.pop(0)
            out = os.path.join(args.outdir, s[:-4])
            os.makedirs(out, exist_ok=True)
            log = open(os.path.join(out, "log.txt"), "w")
            p = subprocess.Popen([sys.executable, os.path.join(HERE, "emu.py"), os.path.join(args.outdir, s),
                                  "--rom", args.rom, "--elf", args.elf, "--emulator", args.emulator,
                                  "--out", out, "--save", os.path.join(out, "test.sav")],
                                 stdout=log, stderr=subprocess.STDOUT, cwd=ROOT, env=env)
            procs.append((p, s, log))
        for p, s, log in list(procs):
            if p.poll() is not None:
                log.close()
                procs.remove((p, s, log))
                print(f"{s}: exit {p.returncode}", flush=True)
        if procs:
            try:
                procs[0][0].wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass


OUTCOME_RE = re.compile(r"autobattle: outcome=(\d+) .*?party_hp=(\S+)(?: enemy_hp=(\S+) party_max=(\S+))?")
TALLY_RE = re.compile(r"\] aim_(TRAINER_\w+) @")


def results(outdir):
    """trainer -> list of (win, margin); a battle without a result (timeout) counts as neither"""
    res = {}
    for d in sorted(os.listdir(outdir)):
        log = os.path.join(outdir, d, "log.txt")
        if not os.path.exists(log):
            continue
        pending = None
        for line in open(log):
            m = OUTCOME_RE.search(line)
            if m:
                pending = m
                continue
            t = TALLY_RE.search(line)
            if t and pending:
                outcome = int(pending.group(1))
                trainer = t.group(1)
                if outcome in (1, 2) and pending.group(3):
                    php = [int(x) for x in pending.group(2).split("/")]
                    pmax = [int(x) for x in pending.group(4).split("/")]
                    ehp = [tuple(int(y) for y in x.split(":")) for x in pending.group(3).split("/")]
                    pf = sum(php) / max(1, sum(pmax))
                    ef = sum(h for h, _ in ehp) / max(1, sum(m for _, m in ehp))
                    res.setdefault(trainer, []).append((1 if outcome == 1 else 0, pf - ef))
                else:
                    res.setdefault(trainer, []).append((None, None))
                pending = None
    return res


def stats(rows):
    done = [r for r in rows if r[0] is not None]
    n = len(done)
    wins = sum(r[0] for r in done)
    margin = sum(r[1] for r in done) / n if n else 0.0
    return n, wins, margin, len(rows) - n


def summary(args):
    res = results(args.outdir)
    base = results(args.basedir) if args.basedir else None
    tot = [0, 0, 0.0, 0]
    btot = [0, 0, 0.0, 0]
    print(f"{'trainer':40s} {'wins':>9s} {'margin':>7s}" + ("   base wins  margin   delta" if base else ""))
    for trainer in sorted(res):
        n, w, m, to = stats(res[trainer])
        tot[0] += n; tot[1] += w; tot[2] += m * n; tot[3] += to
        line = f"{trainer:40s} {w:4d}/{n:<4d} {m:+7.3f}"
        if base and trainer in base:
            bn, bw, bm, bto = stats(base[trainer])
            btot[0] += bn; btot[1] += bw; btot[2] += bm * bn; btot[3] += bto
            line += f"   {bw:4d}/{bn:<4d} {bm:+7.3f} {m - bm:+7.3f}"
        if to:
            line += f"  ({to} without a result)"
        print(line)
    n, w = tot[0], tot[1]
    p = w / n if n else 0
    se = math.sqrt(p * (1 - p) / n) if n else 0
    print(f"\nALL: player wins {w}/{n} = {100 * p:.1f}% (+-{196 * se:.1f}), mean margin {tot[2] / max(1, n):+.3f}, "
          f"{tot[3]} without a result")
    if base:
        bn, bw = btot[0], btot[1]
        bp = bw / bn if bn else 0
        bse = math.sqrt(bp * (1 - bp) / bn) if bn else 0
        print(f"BASE (same trainers): player wins {bw}/{bn} = {100 * bp:.1f}% (+-{196 * bse:.1f}), "
              f"mean margin {btot[2] / max(1, bn):+.3f}")
        dse = math.sqrt(se * se + bse * bse)
        z = (p - bp) / dse if dse else 0
        print(f"DELTA: win rate {100 * (p - bp):+.1f} points (z={z:+.2f}; below -1.96 means the variant's trainers "
              f"are significantly stronger), margin {tot[2] / max(1, n) - btot[2] / max(1, bn):+.3f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("outdir")
    g.add_argument("--runs", type=int, default=3)
    g.add_argument("--per-shard", type=int, default=40)
    g.add_argument("--tests", default="")
    g.add_argument("--trainers", default="", help="only these TRAINER_ constants (comma-separated)")
    g.add_argument("--max-frames", type=int, default=40000)
    r = sub.add_parser("run")
    r.add_argument("rom")
    r.add_argument("elf")
    r.add_argument("outdir")
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--emulator", default="mgba", choices=["mgba", "vbam"])
    s = sub.add_parser("summary")
    s.add_argument("outdir")
    s.add_argument("basedir", nargs="?")
    args = ap.parse_args()
    {"gen": gen, "run": run, "summary": summary}[args.cmd](args)


if __name__ == "__main__":
    main()
