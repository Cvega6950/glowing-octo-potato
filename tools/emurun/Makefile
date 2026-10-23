# Headless mGBA driver used by Crystal Imperium play tests.
# Needs libmgba-dev and libpng-dev (Debian/Ubuntu package names).
emurun: emurun.c
	$(CC) -O2 -Wall -o $@ $< -lmgba -lpng

clean:
	rm -f emurun
