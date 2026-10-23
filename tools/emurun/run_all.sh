#!/bin/sh
# Run every Crystal Imperium emulator play test against the current build.
# Usage: tools/emurun/run_all.sh   (after `make hns`)
set -u
cd "$(dirname "$0")/../.."
fail=0
for t in tools/emurun/tests/*.emu; do
    name=$(basename "$t" .emu)
    out=build/emurun/$name
    mkdir -p "$out"
    echo "== $name"
    if python3 tools/emurun/emu.py "$t" --out "$out" --save "$out/test.sav" > "$out/log.txt" 2>&1; then
        status=0
    else
        status=1
        fail=1
    fi
    grep -v "] shot " "$out/log.txt"
    [ $status -eq 0 ] || echo "FAILED: $name (screenshots in $out)"
done
exit $fail
