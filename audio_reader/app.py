import enum
import logging
import threading
from typing import Callable

from audio_reader.config import load_config, save_config, set_startup
from audio_reader.i18n import set_language
from audio_reader.recorder import AudioRecorder
from audio_reader.transcription import TranscriptionEngine
from audio_reader.hotkey import HotkeyListener
from audio_reader.injector import TextInjector

log = logging.getLogger(__name__)


class AppState(enum.Enum):
    LOADING_MODEL = "loading_model"
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    INJECTING = "injecting"


class AppOrchestrator:
    def __init__(self):
        self.config = load_config()
        set_language(self.config.get("language"))
        self.state = AppState.LOADING_MODEL
        self._state_callbacks: list[Callable[[AppState], None]] = []

        self.engine = TranscriptionEngine(
            model_size=self.config["model_size"],
            device=self.config["device"],
            compute_type=self.config["compute_type"],
            language=self.config["language"],
            vad_filter=self.config["vad_filter"],
        )
        self.recorder = AudioRecorder()
        self.injector = TextInjector(
            restore_clipboard=self.config["restore_clipboard"],
        )
        self.hotkey = HotkeyListener(on_hotkey=self._on_hotkey, hotkey=self.config["hotkey"])

    def add_state_callback(self, callback: Callable[[AppState], None]) -> None:
        self._state_callbacks.append(callback)

    def _set_state(self, state: AppState) -> None:
        self.state = state
        log.info("State → %s", state.value)
        for cb in self._state_callbacks:
            try:
                cb(state)
            except Exception:
                log.exception("Error in state change callback")

    def start(self) -> None:
        self._set_state(AppState.LOADING_MODEL)
        thread = threading.Thread(target=self._load_and_listen, daemon=True)
        thread.start()

    def _load_and_listen(self) -> None:
        self.engine.load_model()
        self._set_state(AppState.IDLE)
        self.hotkey.start()

    def _on_hotkey(self) -> None:
        if self.state == AppState.IDLE:
            self._start_recording()
        elif self.state == AppState.RECORDING:
            self._stop_recording_and_process()

    def _start_recording(self) -> None:
        self._set_state(AppState.RECORDING)
        self.recorder.start()

    def _stop_recording_and_process(self) -> None:
        try:
            self._set_state(AppState.TRANSCRIBING)
            audio = self.recorder.stop()

            if len(audio) == 0:
                log.warning("No audio captured, returning to idle.")
                return

            text = self.engine.transcribe(audio)

            if text.strip():
                self._set_state(AppState.INJECTING)
                self.injector.inject(text.strip())
        except Exception:
            log.exception("Error during transcription/injection")
        finally:
            self._set_state(AppState.IDLE)

    def stop(self) -> None:
        self.hotkey.stop()
        if self.state == AppState.RECORDING:
            self.recorder.stop()
        log.info("App stopped.")

    def update_config(self, new_config: dict) -> None:
        old_hotkey = self.config.get("hotkey")
        self.config.update(new_config)
        save_config(self.config)
        self.injector.restore_clipboard = self.config["restore_clipboard"]
        self.engine.language = self.config["language"]
        self.engine.vad_filter = self.config["vad_filter"]
        set_language(self.config.get("language"))
        if self.config.get("hotkey") != old_hotkey:
            self.hotkey.update_hotkey(self.config["hotkey"])
        set_startup(self.config.get("start_with_windows", False))
