"""Settings defaults: a new game starts with every Platinum Imperium setting at its documented
default (docs/platinum_imperium/API.md), the Running Shoes in hand, and auto-run on (Options bit 15
clear)."""

FLAGS_ON = ["FLAG_IMPERIUM_MINIMAL_GRINDING", "FLAG_IMPERIUM_FAST_BATTLES", "FLAG_IMPERIUM_FAST_INTRO",
            "FLAG_IMPERIUM_EXP_SHARE_ALL", "FLAG_IMPERIUM_EXP_BOOST", "FLAG_IMPERIUM_REUSABLE_TMS",
            "FLAG_IMPERIUM_SLEEP_CLAUSE", "FLAG_IMPERIUM_SETTINGS_INITIALIZED"]
FLAGS_OFF = ["FLAG_IMPERIUM_INFINITE_REPEL", "FLAG_IMPERIUM_EASY_CATCH"] + [f"FLAG_IMPERIUM_SPARE_{i}" for i in range(1, 7)]
VARS = {"VAR_IMPERIUM_DIFFICULTY": 0, "VAR_IMPERIUM_LEVEL_CAP_MODE": 0, "VAR_IMPERIUM_CARE_PACKAGES": 0,
        "VAR_IMPERIUM_SETTINGS_VERSION": 1, "VAR_IMPERIUM_SPARE_1": 0, "VAR_IMPERIUM_SPARE_2": 0,
        "VAR_IMPERIUM_SPARE_3": 0, "VAR_IMPERIUM_SPARE_4": 0}


def run(t):
    frames = t.new_game()
    t.shot("new_game")
    for f in FLAGS_ON:
        t.check(t.flag(f), f"{f} should be set in a new game")
    for f in FLAGS_OFF:
        t.check(not t.flag(f), f"{f} should be clear in a new game")
    for v, want in VARS.items():
        t.check(t.var(v) == want, f"{v} = {t.var(v)}, want {want}")
    t.check(t.running_shoes(), "InitNewGame gives the Running Shoes")
    t.check(t.options_word() & 0x8000 == 0, f"Options bit 15 (auto-run off) is clear: {t.options_word():#06x}")
    t.check(t.mb("levelCap") == 15, f"level cap with no badges is 15, got {t.mb('levelCap')}")
    t.result(f"{len(FLAGS_ON) + len(FLAGS_OFF)} flags, {len(VARS)} vars, shoes and auto-run as specified "
             f"(new game in {frames} frames)")
