#!/bin/sh
# Build Platinum Imperium.
#   tools/imperium/build.sh          -> PlatinumImperium.nds
#   tools/imperium/build.sh --test   also build the Delta-core runner and run the play tests
set -eu
cd "$(dirname "$0")/../.."
make -j"$(nproc)" release
cp build/pokeplatinum.us.nds PlatinumImperium.nds
echo "Built PlatinumImperium.nds ($(sha1sum PlatinumImperium.nds | cut -d' ' -f1))"
if [ "${1:-}" = "--test" ]; then
    [ -f build/dsrun/libdsrun.so ] || tools/dsrun/build.sh
    ROM=PlatinumImperium.nds python3 tools/dsrun/run_tests.py
fi
