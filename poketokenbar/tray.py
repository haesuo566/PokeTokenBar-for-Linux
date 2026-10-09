"""System-tray icon: the animated companion, plus a right-click menu.

The Windows tray shows an icon and a tooltip but no adjacent text, so the
compact "200.7M" readout the macOS menu bar carries lives in the tooltip here
(and in the floating pet, if enabled).

pystray picks its backend per platform at import time: Win32 on Windows, and
on Linux whichever of AppIndicator/GTK/Xorg is available -- this app needs
nothing special for that beyond having `libayatana-appindicator` (or GTK)
installed. One real behaviour gap survives the swap, though: the
AppIndicator/StatusNotifierItem protocol Linux desktops use has no concept of
a plain left click separate from opening the menu, so `default=True` below
(Windows' double-click-to-open) has no effect there -- opening is always one
extra click, through "Open" in the menu. Nothing in this file can paper over
that; it is a difference between the two tray protocols.
"""

from __future__ import annotations

import sys
import threading

import pystray
from PIL import Image

from .i18n import t

ICON_SIZE = 64
# Every animated frame on Linux costs a PNG encode plus a temp-file
# write+unlink (AppIndicator has no in-memory icon update, unlike Win32's
# HICON swap), so a slower cadence keeps that off the hot path without the
# animation looking stuttery.
FRAME_MS = 200 if sys.platform == "win32" else 400


class Tray:
    def __init__(self, app, on_open, on_toggle_pet, on_quit) -> None:
        self.app = app
        self.on_open = on_open
        self._frames: list[Image.Image] = []
        self._index = 0
        self._key = None
        self._stop = threading.Event()

        # Labels are callables so switching language relabels the menu without
        # rebuilding the icon.
        menu = pystray.Menu(
            pystray.MenuItem(lambda _: t("tray.open"), lambda *_: on_open(),
                             default=True),
            pystray.MenuItem(lambda _: t("tray.refresh"),
                             lambda *_: app.request_refresh()),
            pystray.MenuItem(lambda _: t("tray.pet"), lambda *_: on_toggle_pet(),
                             checked=lambda _: app.config.floating_pet),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda _: t("tray.quit"), lambda *_: on_quit()),
        )
        self.icon = pystray.Icon(
            "poketokenbar", self._placeholder(), t("app.title"), menu
        )

    @staticmethod
    def _placeholder() -> Image.Image:
        return Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))

    def start(self) -> None:
        threading.Thread(target=self.icon.run, name="poke-tray", daemon=True).start()
        threading.Thread(target=self._animate, name="poke-tray-anim", daemon=True).start()

    def stop(self) -> None:
        self._stop.set()
        try:
            self.icon.stop()
        except Exception:
            pass

    def refresh(self) -> None:
        """Pull the current companion and usage into the icon and tooltip."""
        app = self.app
        if app.error:
            self.icon.title = t("tray.error", err=app.error)
            return
        if not app.ready:
            return

        species_id, shiny = app.display_sprite()
        key = (species_id, shiny)
        if key != self._key:
            self._key = key
            frames = (
                app.frames(species_id, shiny, ICON_SIZE)
                if species_id is not None
                else app.egg_frames(ICON_SIZE)
            )
            self._frames = frames or [self._placeholder()]
            self._index = 0
            self.icon.icon = self._frames[0]

        snap = app.snapshot
        name = t("egg.name")
        if species_id is not None:
            species = app.dex.species.get(species_id)
            if species:
                name = species.name(app.config.language) + (" ✨" if shiny else "")
        self.icon.title = f"{name}\n{snap.menu_text(app.config)}"

    def _animate(self) -> None:
        while not self._stop.wait(FRAME_MS / 1000):
            if not self.app.config.animate_tray or len(self._frames) < 2:
                continue
            self._index = (self._index + 1) % len(self._frames)
            try:
                self.icon.icon = self._frames[self._index]
            except Exception:
                pass
