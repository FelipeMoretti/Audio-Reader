import logging
import numpy as np
from faster_whisper import WhisperModel

log = logging.getLogger(__name__)


class TranscriptionEngine:
    def __init__(self, model_size: str = "base", device: str = "cpu",
                 compute_type: str = "int8", language: str | None = None,
                 vad_filter: bool = True):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.vad_filter = vad_filter
        self.model: WhisperModel | None = None

    def load_model(self) -> None:
        log.info("Loading Whisper model '%s' (%s/%s)...",
                 self.model_size, self.device, self.compute_type)
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        log.info("Model loaded successfully.")

    def transcribe(self, audio: np.ndarray) -> str:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=self.vad_filter,
            beam_size=5,
        )

        text = " ".join(seg.text.strip() for seg in segments)
        log.info("Transcribed (%s, %.1fs): %s",
                 info.language, info.duration, text)
        return text
