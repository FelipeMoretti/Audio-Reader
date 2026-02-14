import logging
import sys
import threading
from pathlib import Path
from PIL import Image
import pystray

from audio_reader import __version__
from audio_reader.app import AppState
from audio_reader.i18n import t

log = logging.getLogger(__name__)

ICON_SIZE = 64


def _get_icon_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) / "audio_reader"
    else:
        base = Path(__file__).parent.parent
    return base / "assets" / "icon.png"


def _load_icon() -> Image.Image:
    icon_path = _get_icon_path()
    if icon_path.exists():
        return Image.open(icon_path).resize((ICON_SIZE, ICON_SIZE))
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (33, 150, 243, 255))
    return img


class SystemTray:
    def __init__(self, app):
        self.app = app
        self._icon: pystray.Icon | None = None
        self._settings_open = False

    def _build_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(f"{t('tray_title')} v{__version__}", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(t("tray_settings"), self._on_settings, default=True),
            pystray.MenuItem(t("tray_quit"), self._on_quit),
        )

    def _on_settings(self, icon, item) -> None:
        if self._settings_open:
            return
        self._settings_open = True

        from audio_reader.ui.settings import open_settings

        def _run():
            try:
                open_settings(self.app)
            except Exception as e:
                log.error("Settings window error: %s", e, exc_info=True)
            finally:
                self._settings_open = False

        threading.Thread(target=_run, daemon=True).start()

    def _on_quit(self, icon, item) -> None:
        log.info("Quit requested from tray.")
        self.app.stop()
        if self._icon:
            self._icon.stop()

    def update_state(self, state: AppState) -> None:
        if self._icon is None:
            return
        self._icon.title = f"Audio Reader - {state.value}"

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()

    def run(self) -> None:
        image = _load_icon()
        self._icon = pystray.Icon(
            name="audio_reader",
            icon=image,
            title="Audio Reader - Loading...",
            menu=self._build_menu(),
        )
        self.app.add_state_callback(self.update_state)
        self.app.start()
        self._on_settings(None, None)
        self._icon.run()
