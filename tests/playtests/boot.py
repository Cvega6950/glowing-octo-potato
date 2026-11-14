"""Boot: the ROM starts the way Delta starts it (melonDS 0.9.5, no BIOS files, direct boot) and
the screens keep changing through the intro for 30 seconds of emulated time."""


def run(t):
    ds = t.ds
    t.check(not ds.external_bios, "the test must run without BIOS files, as most Delta users do")
    hashes = []
    for i in range(6):
        ds.run(300)
        hashes.append(ds.screen_hash())
        t.shot(f"intro_{i}")
    t.check(len(set(hashes)) >= 4, f"the screens should change through the intro: {hashes}")
    t.result(f"booted, {len(set(hashes))} distinct screens in {ds.frame} frames")
