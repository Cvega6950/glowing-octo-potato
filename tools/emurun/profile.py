#!/usr/bin/env python3
"""Name the functions in an emurun `profile` file (see emurun.c).

Usage: tools/emurun/profile.py PROFILE [--elf pokehns.elf] [--frames FIRST LAST] [--top N]

Prints, for the samples of frames FIRST..LAST of the profile (all by default):
- self time: the function each sample's pc was in (BIOS calls and the sound mixer's code in IWRAM
  are named as such);
- inclusive time, roughly: the functions found on the stack (a return address left behind by an
  earlier call can count a function that has returned: read it as a hint, not a measurement).
Each sample is INTERVAL CPU cycles (280,896 cycles are a frame).
"""
import argparse
import bisect
import collections
import subprocess


def load_symbols(elf):
    syms = []
    out = subprocess.run(["arm-none-eabi-nm", "-n", elf], check=True, capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] in "tTwW" and not parts[2].startswith("$"):
            syms.append((int(parts[0], 16), parts[2]))
    return sorted(syms)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("profile")
    ap.add_argument("--elf", default="pokehns.elf")
    ap.add_argument("--frames", nargs=2, type=int, metavar=("FIRST", "LAST"))
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()

    syms = load_symbols(args.elf)
    addrs = [a for a, _ in syms]
    # The sound mixer runs from a copy in IWRAM (SoundMainRAM_Buffer, a data symbol)
    nm = subprocess.run(["arm-none-eabi-nm", "-n", "-S", args.elf], check=True, capture_output=True, text=True).stdout
    mixer = next(((int(p[0], 16), int(p[0], 16) + int(p[1], 16)) for p in (l.split() for l in nm.splitlines())
                  if len(p) == 4 and p[3] == "SoundMainRAM_Buffer"), (0, 0))

    def name(v):
        v &= ~1
        if v < 0x4000:
            return "(BIOS)"
        if mixer[0] <= v < mixer[1]:
            return "(sound mixer, IWRAM)"
        i = bisect.bisect_right(addrs, v) - 1
        return syms[i][1] if i >= 0 else "%08X" % v

    self_time, inclusive, frames = collections.Counter(), collections.Counter(), set()
    n = 0
    for line in open(args.profile):
        parts = line.split()
        frame = int(parts[0])
        if args.frames and not args.frames[0] <= frame <= args.frames[1]:
            continue
        n += 1
        frames.add(frame)
        here = name(int(parts[1], 16))
        self_time[here] += 1
        for fn in {here} | {name(int(x, 16)) for x in parts[3:]}:
            inclusive[fn] += 1
    if not n:
        print("no samples")
        return
    print(f"{n} samples, frames {min(frames)}-{max(frames)} ({n / len(frames):.0f} per frame)")
    print("self time:")
    for fn, c in self_time.most_common(args.top):
        print(f"  {100.0 * c / n:5.1f}%  {fn}")
    print("inclusive time (approximate, from the stack):")
    for fn, c in inclusive.most_common(args.top):
        print(f"  {100.0 * c / n:5.1f}%  {fn}")


if __name__ == "__main__":
    main()
