#!/bin/sh
# Build Pokemon Platinum Imperium and run its checks.
#   tools/platinum_imperium/build.sh          build + check the generated data
#   tools/platinum_imperium/build.sh --test   also run the emulator play tests (needs libmgba-dev)
set -eu
cd "$(dirname "$0")/../.."
python3 tools/platinum_imperium/care_packages.py --check
python3 tools/platinum_imperium/tm_list.py --check
python3 tools/platinum_imperium/validate_teams.py
make -j"$(nproc)"
cp pokeemerald.gba PlatinumImperium.gba
echo "Built PlatinumImperium.gba ($(sha1sum PlatinumImperium.gba | cut -d' ' -f1))"
if [ "${1:-}" = "--test" ]; then
    tools/emurun/run_all.sh
fi
