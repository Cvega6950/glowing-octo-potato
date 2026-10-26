#!/bin/sh
# Build VBA-M's libretro core at the commit Delta's GBA core (GBADeltaCore) pins, so the play
# tests can run on the same emulator code as Delta on iOS:
#   tools/emurun/build_vbam_core.sh [DIR]      # default DIR: build/vbam
#   EMURUN_CORE=build/vbam/src/libretro/vbam_libretro.so tools/emurun/run_all.sh vbam
# GBADeltaCore's visualboyadvance-m submodule: https://github.com/rileytestut/GBADeltaCore
set -eu
COMMIT=453fa0decf179360926fb417725a794aa496d6e3
DIR=${1:-build/vbam}
if [ ! -d "$DIR/.git" ]; then
    git init -q "$DIR"
    git -C "$DIR" remote add origin https://github.com/visualboyadvance-m/visualboyadvance-m.git
fi
git -C "$DIR" fetch -q --depth 1 origin "$COMMIT"
git -C "$DIR" checkout -q "$COMMIT"
make -C "$DIR/src/libretro" -j"$(nproc)" >/dev/null
echo "$DIR/src/libretro/vbam_libretro.so"
