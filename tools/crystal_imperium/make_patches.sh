#!/bin/sh
# Build the Crystal Imperium release patches into DIR (default build/release):
#   CrystalImperium-from-HnS-2.0.6.bps   BPS patch: Heart & Soul 2.0.6 ROM -> CrystalImperium.gba
#   source-patches/                       git format-patch series on top of HnS tag 2.0.6
#   SHA1SUMS                              hashes of both ROMs (the BPS only applies to that exact
#                                         HnS 2.0.6 ROM: built from tag 2.0.6 with the same tool chain)
# Needs the tool chain from the README, git and a C++ compiler (Flips is built from source).
# The ROMs themselves contain Nintendo's assets and are not written to DIR.
set -eu
cd "$(dirname "$0")/../.."
DIR=${1:-build/release}
BASE_TAG=167aa6d537b109bb229c231ddce4616974c4da71 # Heart & Soul 2.0.6
WORK=build/release-work
mkdir -p "$DIR" "$WORK"

# Crystal Imperium ROM
make -j"$(nproc)" hns
cp pokehns.gba "$WORK/CrystalImperium.gba"

# Heart & Soul 2.0.6 ROM, from a worktree of the base tag
if [ ! -d "$WORK/hns-2.0.6" ]; then
    git worktree add -f "$WORK/hns-2.0.6" "$BASE_TAG"
fi
make -C "$WORK/hns-2.0.6" -j"$(nproc)" hns

# Flips (Floating IPS) for the BPS patch
if [ ! -x "$WORK/flips/flips" ]; then
    rm -rf "$WORK/flips"
    git clone -q --depth 1 https://github.com/Alcaro/Flips.git "$WORK/flips"
    (cd "$WORK/flips" && c++ -O2 -DFLIPS_CLI -o flips flips.cpp flips-cli.cpp crc32.cpp divsufsort.c \
        libbps.cpp libbps-suf.cpp libips.cpp libups.cpp -I.)
fi
"$WORK/flips/flips" --create --bps "$WORK/hns-2.0.6/pokehns.gba" "$WORK/CrystalImperium.gba" \
    "$DIR/CrystalImperium-from-HnS-2.0.6.bps"
# Check the patch reproduces the ROM exactly
"$WORK/flips/flips" --apply "$DIR/CrystalImperium-from-HnS-2.0.6.bps" "$WORK/hns-2.0.6/pokehns.gba" "$WORK/check.gba"
cmp "$WORK/check.gba" "$WORK/CrystalImperium.gba"
rm "$WORK/check.gba"

# Source patches
rm -rf "$DIR/source-patches"
git format-patch -q -o "$DIR/source-patches" "$BASE_TAG..HEAD"

(cd "$WORK" && sha1sum hns-2.0.6/pokehns.gba CrystalImperium.gba) > "$DIR/SHA1SUMS"
echo "Wrote $DIR:"
ls "$DIR"
cat "$DIR/SHA1SUMS"
