import logging
import threading
import numpy as np
import sounddevice as sd

log = logging.getLogger(__name__)

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"


class AudioRecorder:
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def _callback(self, indata: np.ndarray, frames: int,
                  time_info, status) -> None:
        if status:
            log.warning("Audio status: %s", status)
        with self._lock:
            self._chunks.append(indata.copy())

    def start(self) -> None:
        with self._lock:
            self._chunks.clear()
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
        self._stream.start()
        log.info("Recording started.")

    def stop(self) -> np.ndarray:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._chunks:
                log.warning("No audio captured.")
                return np.zeros(0, dtype=DTYPE)
            audio = np.concatenate(self._chunks, axis=0).flatten()
            self._chunks.clear()
        log.info("Recording stopped. Captured %.1fs of audio.",
                 len(audio) / self.sample_rate)
        return audio
