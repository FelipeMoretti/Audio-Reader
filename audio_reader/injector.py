import logging
import time
import ctypes

import pyperclip

log = logging.getLogger(__name__)

user32 = ctypes.windll.user32

VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_ALT = 0x12
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002

SCAN_CTRL = 0x1D
SCAN_V = 0x2F


class TextInjector:
    def __init__(self, restore_clipboard: bool = True):
        self.restore_clipboard = restore_clipboard

    def inject(self, text: str) -> None:
        if not text:
            log.warning("Empty text, nothing to inject.")
            return

        old_clipboard = None
        if self.restore_clipboard:
            try:
                old_clipboard = pyperclip.paste()
            except Exception:
                old_clipboard = None

        pyperclip.copy(text)
        log.info("Clipboard set (%d chars).", len(text))

        # Release any stuck modifier keys
        user32.keybd_event(VK_CONTROL, SCAN_CTRL, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_ALT, 0x38, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_SHIFT, 0x2A, KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        # Ctrl+V via keybd_event (with scan codes)
        user32.keybd_event(VK_CONTROL, SCAN_CTRL, 0, 0)
        user32.keybd_event(VK_V, SCAN_V, 0, 0)
        time.sleep(0.05)
        user32.keybd_event(VK_V, SCAN_V, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, SCAN_CTRL, KEYEVENTF_KEYUP, 0)
        log.info("Sent Ctrl+V via keybd_event.")

        time.sleep(0.5)

        if self.restore_clipboard and old_clipboard is not None:
            try:
                pyperclip.copy(old_clipboard)
            except Exception:
                log.warning("Failed to restore clipboard.")

        log.info("Injected %d characters.", len(text))
