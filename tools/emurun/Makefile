# Headless emulator drivers used by Platinum Imperium play tests.
#   emurun           mGBA backend; needs libmgba-dev and libpng-dev (Debian/Ubuntu package names)
#   emurun-libretro  loads a libretro GBA core at run time (EMURUN_CORE=path/to/core.so);
#                    tools/emurun/build_vbam_core.sh builds VBA-M's core at Delta's pinned commit
all: emurun emurun-libretro

emurun: emurun.c backend_mgba.c backend.h
	$(CC) -O2 -Wall -o $@ emurun.c backend_mgba.c -lmgba -lpng

emurun-libretro: emurun.c backend_libretro.c backend.h libretro.h
	$(CC) -O2 -Wall -Wl,--export-dynamic-symbol=time -o $@ emurun.c backend_libretro.c -ldl -lpng

clean:
	rm -f emurun emurun-libretro
