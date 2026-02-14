import logging
import threading
from typing import Callable

import keyboard

log = logging.getLogger(__name__)


class HotkeyListener:
    def __init__(self, on_hotkey: Callable[[], None], hotkey: str = "ctrl+alt"):
        self.on_hotkey = on_hotkey
        self._running = False
        self._held = False
        self._hotkey = hotkey
        self._keys = [k.strip() for k in hotkey.split("+")]

    def _on_press(self) -> None:
        if self._running and not self._held:
            self._held = True
            log.debug("%s held — start", self._hotkey)
            threading.Thread(target=self.on_hotkey, daemon=True).start()

    def _on_release(self, event: keyboard.KeyboardEvent) -> None:
        if self._running and self._held:
            if not all(keyboard.is_pressed(k) for k in self._keys):
                self._held = False
                log.debug("%s released — stop", self._hotkey)
                threading.Thread(target=self.on_hotkey, daemon=True).start()

    def start(self) -> None:
        self._running = True
        keyboard.add_hotkey(self._hotkey, self._on_press, suppress=False)
        for key in self._keys:
            keyboard.on_release_key(key, self._on_release)
        log.info("Hotkey listener started (hold %s).", self._hotkey)

    def stop(self) -> None:
        self._running = False
        self._held = False
        keyboard.unhook_all()
        log.info("Hotkey listener stopped.")

    def update_hotkey(self, new_hotkey: str) -> None:
        self.stop()
        self._hotkey = new_hotkey
        self._keys = [k.strip() for k in new_hotkey.split("+")]
        self.start()
        log.info("Hotkey updated to: %s", new_hotkey)
