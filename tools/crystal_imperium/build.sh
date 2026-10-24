#!/bin/sh
# Build Pokemon Crystal Imperium and run its checks.
#   tools/crystal_imperium/build.sh          build + validate data
#   tools/crystal_imperium/build.sh --test   also run the emulator play tests (needs libmgba-dev)
set -eu
cd "$(dirname "$0")/../.."
python3 tools/crystal_imperium/validate.py --check
python3 tools/crystal_imperium/boss_teams.py --check
python3 tools/crystal_imperium/care_packages.py --check
make -j"$(nproc)" hns
cp pokehns.gba CrystalImperium.gba
echo "Built CrystalImperium.gba ($(sha1sum CrystalImperium.gba | cut -d' ' -f1))"
if [ "${1:-}" = "--test" ]; then
    tools/emurun/run_all.sh
fi
