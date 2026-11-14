#!/usr/bin/env python3
"""Run Platinum Imperium's play tests on the headless Delta-core runner.

    tools/dsrun/run_tests.py                 every test in tests/playtests/
    tools/dsrun/run_tests.py boot autorun    only these tests
    ROM=path/to.nds tools/dsrun/run_tests.py  another ROM (default build/pokeplatinum.us.nds)

Each test is tests/playtests/<name>.py with a function run(t), where t is a Test (see
playtest.py). Every test runs in its own process (libdsrun holds one machine). Screenshots go to
build/playtests/<name>/. Exit status 1 if any test fails.
"""
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TESTS = os.path.join(ROOT, "tests", "playtests")


def main(argv):
    names = argv or sorted(f[:-3] for f in os.listdir(TESTS) if f.endswith(".py") and not f.startswith("_"))
    results = []
    for name in names:
        t0 = time.time()
        p = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "playtest.py"), name],
                           capture_output=True, text=True)
        ok = p.returncode == 0
        last = [l for l in p.stdout.splitlines() if l.startswith("RESULT")]
        detail = last[-1][7:] if last else ""
        results.append((name, ok, time.time() - t0, detail))
        print(f"{'PASS' if ok else 'FAIL'}  {name}  ({time.time() - t0:.0f} s)  {detail}", flush=True)
        if not ok:
            sys.stdout.write("\n".join(l for l in (p.stdout + p.stderr).splitlines()
                                       if not l.startswith(("PU", "15111011", "FW:", "MAC:")))[-4000:] + "\n")
    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} play tests pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
