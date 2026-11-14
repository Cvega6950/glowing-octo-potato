"""Python driver for libdsrun.so, the headless DS runner on Delta's melonDS core.

    from dsrun import DS
    ds = DS("build/pokeplatinum.us.nds")
    ds.run(600)
    ds.press("A", frames=4)
    ds.screenshot("out.png")
    ds.read32(0x02101D2C)

Keys: A B SELECT START RIGHT LEFT UP DOWN R L X Y. Run with TZ=UTC (DS() sets it) so the
emulated clock is the same everywhere.
"""
import ctypes
import os
import time as _time

KEYS = {"A": 0, "B": 1, "SELECT": 2, "START": 3, "RIGHT": 4, "LEFT": 5, "UP": 6, "DOWN": 7,
        "R": 8, "L": 9, "X": 10, "Y": 11}

# 2026-10-24 01:30 UTC, as in Crystal Imperium's play tests (night in the game).
DEFAULT_EPOCH = 1792805400

_LIB = None


def _lib(path=None):
    global _LIB
    if _LIB is None:
        os.environ["TZ"] = "UTC"
        _time.tzset()
        path = path or os.environ.get("DSRUN_LIB") or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "build", "dsrun", "libdsrun.so")
        lib = ctypes.CDLL(path)
        lib.dsrun_open.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_longlong]
        lib.dsrun_open.restype = ctypes.c_int
        lib.dsrun_set_keys.argtypes = [ctypes.c_uint]
        lib.dsrun_touch.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.dsrun_run.argtypes = [ctypes.c_int]
        lib.dsrun_frame_count.restype = ctypes.c_ulonglong
        lib.dsrun_main_ram.restype = ctypes.POINTER(ctypes.c_ubyte)
        for n in ("8", "16", "32"):
            getattr(lib, "dsrun_read" + n).argtypes = [ctypes.c_uint]
            getattr(lib, "dsrun_read" + n).restype = ctypes.c_uint
            getattr(lib, "dsrun_write" + n).argtypes = [ctypes.c_uint, ctypes.c_uint]
        lib.dsrun_framebuffer_rgb.argtypes = [ctypes.c_void_p]
        lib.dsrun_screenshot.argtypes = [ctypes.c_char_p]
        lib.dsrun_screenshot.restype = ctypes.c_int
        lib.dsrun_save_size.restype = ctypes.c_uint
        lib.dsrun_save_data.restype = ctypes.POINTER(ctypes.c_ubyte)
        lib.dsrun_write_save.argtypes = [ctypes.c_char_p]
        lib.dsrun_write_save.restype = ctypes.c_int
        lib.dsrun_save_dirty.restype = ctypes.c_int
        lib.dsrun_external_bios.restype = ctypes.c_int
        _LIB = lib
    return _LIB


class DS:
    """One emulated DS. libdsrun.so holds a single machine, so use one DS per process."""

    def __init__(self, rom, save=None, bios_dir=None, epoch=DEFAULT_EPOCH, lib=None):
        self.lib = _lib(lib)
        rc = self.lib.dsrun_open(os.fsencode(rom), os.fsencode(save) if save else None,
                                 os.fsencode(bios_dir) if bios_dir else None, epoch)
        if rc:
            raise RuntimeError(f"dsrun_open failed ({rc}) for {rom}")
        self.held = 0

    # --- time and input ---
    @property
    def frame(self):
        return self.lib.dsrun_frame_count()

    def run(self, frames=1):
        self.lib.dsrun_run(int(frames))

    def hold(self, *keys):
        self.held = 0
        for k in keys:
            self.held |= 1 << KEYS[k]
        self.lib.dsrun_set_keys(self.held)

    def release(self):
        self.hold()

    def press(self, *keys, frames=4, after=8):
        """Press keys together for `frames` frames, then release them for `after` frames."""
        self.hold(*keys)
        self.run(frames)
        self.release()
        self.run(after)

    def touch(self, x, y, frames=4, after=8):
        self.lib.dsrun_touch(x, y)
        self.run(frames)
        self.lib.dsrun_release()
        self.run(after)

    # --- memory ---
    def read8(self, a): return self.lib.dsrun_read8(a)
    def read16(self, a): return self.lib.dsrun_read16(a)
    def read32(self, a): return self.lib.dsrun_read32(a)
    def write8(self, a, v): self.lib.dsrun_write8(a, v)
    def write16(self, a, v): self.lib.dsrun_write16(a, v)
    def write32(self, a, v): self.lib.dsrun_write32(a, v)

    def ram(self, addr, length):
        """`length` bytes of main RAM from `addr` (0x02000000-0x023FFFFF)."""
        base = self.lib.dsrun_main_ram()
        off = addr - 0x02000000
        assert 0 <= off and off + length <= 0x400000, hex(addr)
        return bytes(ctypes.cast(ctypes.byref(base.contents, off), ctypes.POINTER(ctypes.c_ubyte * length)).contents)

    # --- screen ---
    def framebuffer(self):
        """Both screens as RGB bytes, 256x384, top screen first."""
        buf = (ctypes.c_ubyte * (256 * 384 * 3))()
        self.lib.dsrun_framebuffer_rgb(buf)
        return bytes(buf)

    def screenshot(self, path):
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        if self.lib.dsrun_screenshot(os.fsencode(path)):
            raise RuntimeError("screenshot failed: " + path)

    def screen_hash(self, screen=None):
        """A short hash of the top (0), bottom (1) or both (None) screens, to wait for changes."""
        import hashlib
        fb = self.framebuffer()
        half = 256 * 192 * 3
        part = fb if screen is None else fb[screen * half:(screen + 1) * half]
        return hashlib.sha1(part).hexdigest()[:12]

    # --- save ---
    @property
    def save_data(self):
        n = self.lib.dsrun_save_size()
        if not n:
            return b""
        return bytes(ctypes.cast(self.lib.dsrun_save_data(), ctypes.POINTER(ctypes.c_ubyte * n)).contents)

    def write_save(self, path):
        if self.lib.dsrun_write_save(os.fsencode(path)):
            raise RuntimeError("write_save failed: " + path)

    @property
    def external_bios(self):
        return bool(self.lib.dsrun_external_bios())
