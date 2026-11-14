#!/bin/sh
# Build libdsrun.so: the headless DS runner on the melonDS core Delta uses.
#   tools/dsrun/build.sh            -> build/dsrun/libdsrun.so
# Needs cmake, a C++17 compiler and libpng-dev. Fetches rileytestut/melonDS at a53f9ba.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${DSRUN_BUILD:-$HERE/../../build/dsrun}"
MELONDS_REV=a53f9bab7b5c06efcbc6ecdf30ac0367555995aa
mkdir -p "$OUT"
if [ ! -d "$OUT/melonDS/.git" ]; then
    git clone -q https://github.com/rileytestut/melonDS "$OUT/melonDS"
fi
git -C "$OUT/melonDS" checkout -q "$MELONDS_REV"
cmake -S "$HERE" -B "$OUT/cmake" -DCMAKE_BUILD_TYPE=Release -DMELONDS_DIR="$OUT/melonDS" >/dev/null
cmake --build "$OUT/cmake" -j"$(nproc)"
cp "$OUT/cmake/libdsrun.so" "$OUT/libdsrun.so"
echo "Built $OUT/libdsrun.so (melonDS $MELONDS_REV)"
