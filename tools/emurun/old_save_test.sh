#!/bin/sh
# Save compatibility: make a save with Heart & Soul 2.0.6, then Continue it in Crystal Imperium
# (party kept, the key items and DexNav handed out, the L menu complete, DexNav search levels at 0).
# Usage: tools/emurun/old_save_test.sh [HNS_DIR]   HNS_DIR holds pokehns.gba/.elf built from
#        HnS tag 2.0.6 (tools/crystal_imperium/make_patches.sh builds it in build/release-work).
#        EMURUN_EMULATOR=vbam (with EMURUN_CORE) runs it on VBA-M.
set -eu
cd "$(dirname "$0")/../.."
HNS=${1:-build/release-work/hns-2.0.6}
OUT=build/emurun/old_save-${EMURUN_EMULATOR:-mgba}
mkdir -p "$OUT"
python3 tools/emurun/emu.py tools/emurun/tests_oldsave/1_make_hns_save.emu \
    --rom "$HNS/pokehns.gba" --elf "$HNS/pokehns.elf" --out "$OUT/hns" --save "$OUT/old.sav"
python3 tools/emurun/emu.py tools/emurun/tests_oldsave/2_continue_on_ci.emu \
    --out "$OUT/ci" --save "$OUT/old.sav" --keep-save
