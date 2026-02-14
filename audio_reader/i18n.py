import locale
import logging

log = logging.getLogger(__name__)

_TRANSLATIONS = {
    "en": {
        "settings_title": "Audio Reader",
        "transcription_quality": "Transcription Quality",
        "quality_fastest": "Fastest (lower quality)",
        "quality_balanced": "Balanced",
        "quality_accurate": "Accurate",
        "quality_very_accurate": "Very accurate (slower)",
        "processing": "Processing",
        "cpu": "CPU",
        "gpu_nvidia": "GPU (NVIDIA)",
        "language": "Language",
        "auto_detect": "Auto-detect",
        "restore_clipboard": "Restore Clipboard",
        "save": "SAVE",
        "note_restart": "Note: Changing quality/processing requires app restart.",
        "view_log": "View Logs",
        "log_title": "Audio Reader - Log",
        "quit_app": "Close App",
        "tray_title": "Audio Reader",
        "tray_settings": "Settings",
        "tray_quit": "Quit",
        "hotkey": "Hotkey",
        "press_hotkey": "Press keys...",
        "hotkey_invalid": "Invalid: need 2+ keys with a modifier (Ctrl, Alt, Shift)",
        "recording": "Recording...",
        "transcribing": "Transcribing...",
        "injecting": "Injecting...",
        "start_with_windows": "Start with Windows",
    },
    "pt": {
        "settings_title": "Audio Reader",
        "transcription_quality": "Qualidade da Transcrição",
        "quality_fastest": "Mais rápido (menor qualidade)",
        "quality_balanced": "Equilibrado",
        "quality_accurate": "Preciso",
        "quality_very_accurate": "Muito preciso (Mais Lento)",
        "processing": "Processamento",
        "cpu": "CPU",
        "gpu_nvidia": "GPU (NVIDIA)",
        "language": "Idioma",
        "auto_detect": "Auto-detectar",
        "restore_clipboard": "Restaurar Área de Transferência",
        "save": "SALVAR",
        "note_restart": "Nota: Alterar qualidade/processamento requer reinício do App.",
        "view_log": "Ver Logs",
        "log_title": "Audio Reader - Log",
        "quit_app": "Fechar App",
        "tray_title": "Audio Reader",
        "tray_settings": "Configurações",
        "tray_quit": "Sair",
        "hotkey": "Atalho",
        "press_hotkey": "Pressione as teclas...",
        "hotkey_invalid": "Inválido: precisa de 2+ teclas com modificador (Ctrl, Alt, Shift)",
        "recording": "Gravando...",
        "transcribing": "Transcrevendo...",
        "injecting": "Injetando...",
        "start_with_windows": "Iniciar com o Windows",
    },
}


def _detect_language() -> str:
    try:
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith("pt"):
            return "pt"
    except Exception:
        pass
    return "en"


_current = _detect_language()
log.info("UI language: %s", _current)


def set_language(lang_code: str | None) -> None:
    global _current
    if lang_code in _TRANSLATIONS:
        _current = lang_code
    else:
        _current = _detect_language()
    log.info("UI language set to: %s", _current)


def t(key: str) -> str:
    return _TRANSLATIONS[_current].get(key, key)
