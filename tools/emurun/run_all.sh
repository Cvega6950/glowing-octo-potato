#!/bin/sh
# Run every Platinum Imperium emulator play test against the current build.
# Usage: tools/emurun/run_all.sh [mgba|vbam]   (after `make`)
#   mgba (default): libmgba.  vbam: VBA-M's libretro core, the emulator Delta's GBA core is built
#   on; set EMURUN_CORE to the core (tools/emurun/build_vbam_core.sh builds it).
set -u
cd "$(dirname "$0")/../.."
emulator=${1:-mgba}
case $emulator in
    mgba) results=build/emurun ;;
    vbam) results=build/emurun-vbam ;;
    *) echo "usage: $0 [mgba|vbam]" >&2; exit 1 ;;
esac
make -s -C tools/emurun
fail=0
for t in tools/emurun/tests/*.emu; do
    name=$(basename "$t" .emu)
    out=$results/$name
    mkdir -p "$out"
    echo "== $name"
    if python3 tools/emurun/emu.py "$t" --emulator "$emulator" --out "$out" --save "$out/test.sav" > "$out/log.txt" 2>&1; then
        status=0
    else
        status=1
        fail=1
    fi
    grep -v "] shot " "$out/log.txt"
    [ $status -eq 0 ] || echo "FAILED: $name (screenshots in $out)"
done
exit $fail
