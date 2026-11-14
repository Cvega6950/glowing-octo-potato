#!/bin/sh
# Prepare a git worktree of Platinum Imperium for building and play testing, by copying the
# downloaded build dependencies (ignored by git) and the Delta-core runner from a main checkout.
#   tools/imperium/worktree_setup.sh [MAIN_CHECKOUT]   (default /home/user/glowing-octo-potato)
# Then: make -j"$(nproc)" release && python3 tools/dsrun/run_tests.py
set -eu
cd "$(dirname "$0")/../.."
MAIN="${1:-/home/user/glowing-octo-potato}"
[ "$(pwd -P)" = "$(cd "$MAIN" && pwd -P)" ] && { echo "This is the main checkout; nothing to do."; exit 0; }
for d in subprojects/libvct-1.3.1 subprojects/NitroDWC-2.2.30008 subprojects/NitroSDK-4.2.30001 \
         subprojects/NitroSystem-071126.1 subprojects/NitroWiFi-2.1.30003 subprojects/packagecache \
         subprojects/metang subprojects/meson-1.12.0 subprojects/yyjson-0.12.0 tools/metroskrew; do
    if [ ! -e "$d" ] && [ -e "$MAIN/$d" ]; then
        cp -a "$MAIN/$d" "$d"
    fi
done
mkdir -p build/dsrun
[ -f build/dsrun/libdsrun.so ] || cp "$MAIN/build/dsrun/libdsrun.so" build/dsrun/libdsrun.so
echo "Worktree ready: run make -j\$(nproc) release"
