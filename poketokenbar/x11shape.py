"""Cut a Tk window to an arbitrary silhouette, on X11.

Windows carves a transparent hole out of a window with the `-transparentcolor`
attribute: pixels matching one key colour become click-through and see-through.
X11 has no such attribute; the equivalent is the Shape extension, which clips
the whole window to a 1-bit mask instead of keying a colour. Wayland
compositors don't speak Shape themselves, but every desktop environment still
runs an XWayland server for ordinary X11 clients -- and Tk is one -- so this
same code path covers an X11 session and a Wayland one alike. It is a no-op
(returns False) on Windows, and degrades the same way if Xlib or the extension
turns out to be unavailable, so callers always have a plain rectangular window
to fall back to.
"""

from __future__ import annotations

import sys

from PIL import Image

_display = None
_unavailable = sys.platform == "win32"


def available() -> bool:
    """Whether `apply_mask` can actually do anything in this session.

    A failed connection attempt is not cached as permanent: at startup the
    tray icon's own GTK/Xlib connection is opening around the same time, and a
    transient hiccup there should not wrongly condemn the floating pet to a
    plain rectangle for the rest of the run. Only platform (win32) and a
    missing `python-xlib` are structural enough to cache.
    """
    global _display, _unavailable
    if _unavailable:
        return False
    if _display is not None:
        return True
    try:
        from Xlib import display
    except ImportError:
        _unavailable = True
        return False
    try:
        d = display.Display()
        if not d.has_extension("SHAPE"):
            return False
    except Exception:
        # No X server reachable right now -- a Wayland session with no
        # XWayland, a headless one, or just not up yet. Try again next time.
        return False
    _display = d
    return True


def _pack_bitmap(alpha: Image.Image, threshold: int = 128) -> bytes:
    """Pack an 'L' image into X11's XYBitmap layout: LSB-first bytes, each
    scanline padded to a 32-bit boundary (the server's bitmap-scanline-pad).
    """
    w, h = alpha.size
    stride = ((w + 31) // 32) * 4
    out = bytearray(stride * h)
    px = alpha.load()
    for y in range(h):
        row = y * stride
        for x in range(w):
            if px[x, y] >= threshold:
                out[row + x // 8] |= 1 << (x % 8)
    return bytes(out)


def apply_mask(window, mask: Image.Image) -> bool:
    """Clip `window` (any Tk widget with a real X window) to `mask`'s alpha.

    `mask` is an 'L' or 'RGBA' image the exact size of the window; pixels at or
    above the mid grey/alpha threshold stay visible, the rest become a hole
    clear through to the desktop. Returns False (window unchanged) if shaping
    is not available here.
    """
    if not available():
        return False
    from Xlib import X
    from Xlib.ext import shape

    alpha = mask.getchannel("A") if mask.mode == "RGBA" else mask.convert("L")
    w, h = alpha.size
    try:
        xwin = _display.create_resource_object("window", window.winfo_id())
        pixmap = xwin.create_pixmap(w, h, 1)
        gc = pixmap.create_gc(foreground=1, background=0)
        pixmap.put_image(gc, 0, 0, w, h, X.XYBitmap, 1, 0, _pack_bitmap(alpha))
        xwin.shape_mask(shape.SO.Set, shape.SK.Bounding, 0, 0, pixmap)
        gc.free()
        pixmap.free()
        _display.sync()
    except Exception:
        # A dead window (closed mid-render) or a transient server hiccup --
        # the caller already has a plain rectangular window either way.
        return False
    return True
