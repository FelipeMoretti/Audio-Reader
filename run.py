import logging
import os
import signal

_log_dir = os.path.join(os.environ.get("APPDATA", "."), "AudioReader")
os.makedirs(_log_dir, exist_ok=True)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%H:%M:%S")

_console = logging.StreamHandler()
_console.setFormatter(_fmt)

_session = logging.FileHandler(os.path.join(_log_dir, "session.log"), mode="w", encoding="utf-8")
_session.setFormatter(_fmt)

_errors = logging.FileHandler(os.path.join(_log_dir, "error.log"), mode="a", encoding="utf-8")
_errors.setLevel(logging.ERROR)
_errors.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_console, _session, _errors])

from audio_reader.app import AppOrchestrator
from audio_reader.ui.tray import SystemTray
from audio_reader.ui.overlay import StatusOverlay


def main():
    app = AppOrchestrator()

    overlay = StatusOverlay()
    overlay.start()
    app.add_state_callback(overlay.update_state)

    tray = SystemTray(app)

    def _shutdown(sig, frame):
        app.stop()
        overlay.stop()
        tray.stop()

    signal.signal(signal.SIGINT, _shutdown)

    try:
        tray.run()  # Blocks - pystray runs on main thread
    finally:
        app.stop()
        overlay.stop()
        os._exit(0)


if __name__ == "__main__":
    main()
