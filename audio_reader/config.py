import json
import logging
import os
import subprocess
import sys
from pathlib import Path

log = logging.getLogger(__name__)


def _detect_gpu() -> tuple[str, str]:
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=5,
            creationflags=0x08000000,  # CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            log.info("NVIDIA GPU detected — using CUDA with float16.")
            return "cuda", "float16"
    except Exception:
        pass
    log.info("No NVIDIA GPU detected — using CPU with int8.")
    return "cpu", "int8"


_device, _compute_type = _detect_gpu()

DEFAULT_CONFIG = {
    "model_size": "base",
    "device": _device,
    "compute_type": _compute_type,
    "language": None,
    "restore_clipboard": True,
    "vad_filter": True,
    "hotkey": "ctrl+alt",
    "start_with_windows": False,
}

CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home())) / "AudioReader"
CONFIG_FILE = CONFIG_DIR / "config.json"


_MODIFIERS = {"ctrl", "alt", "shift", "left ctrl", "right ctrl", "left alt", "right alt", "left shift", "right shift"}


def _valid_hotkey(hotkey: str) -> bool:
    keys = [k.strip().lower() for k in hotkey.split("+")]
    return len(keys) >= 2 and any(k in _MODIFIERS for k in keys)


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        merged = {**DEFAULT_CONFIG, **user_config}
    else:
        merged = dict(DEFAULT_CONFIG)
    if not _valid_hotkey(merged.get("hotkey", "")):
        merged["hotkey"] = DEFAULT_CONFIG["hotkey"]
    return merged


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def set_startup(enabled: bool) -> None:
    import winreg
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    app_name = "AudioReader"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        if enabled:
            if getattr(sys, "frozen", False):
                exe_path = sys.executable
            else:
                exe_path = f'"{sys.executable}" "{Path(__file__).resolve().parent.parent / "run.py"}"'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            log.info("Startup registry entry added: %s", exe_path)
        else:
            try:
                winreg.DeleteValue(key, app_name)
                log.info("Startup registry entry removed.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        log.exception("Failed to update startup registry")
