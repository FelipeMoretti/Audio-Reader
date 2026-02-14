import logging
import os
import sys
import threading
import customtkinter as ctk
from pathlib import Path

import keyboard

from audio_reader.config import load_config, save_config, CONFIG_DIR
from audio_reader.i18n import t

log = logging.getLogger(__name__)

LANGUAGES = {
    "Auto-detect": None,
    "Português": "pt",
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "Japanese": "ja",
    "Chinese": "zh",
    "Korean": "ko",
    "Russian": "ru",
}
_CODE_TO_LABEL = {v: k for k, v in LANGUAGES.items()}

# Colors
_HEADER_BLUE = "#4A8FD4"
_ACCENT_GOLD = "#D4A838"
_DROPDOWN_BG = "#2b2b2b"
_DROPDOWN_BTN = "#333333"
_DROPDOWN_HOVER = "#3a3a3a"
_SAVE_BLUE = "#3B82F6"
_SAVE_HOVER = "#2563EB"
_SAVE_BORDER = "#2D6FD4"
_BTN_BG = "#3a3a3a"
_BTN_HOVER = "#4a4a4a"
_BTN_BORDER = "#555555"
_SEPARATOR = "#555555"
_NOTE_COLOR = "#7A8A9A"


def _quality_options() -> dict[str, str]:
    return {
        t("quality_fastest"): "tiny",
        t("quality_balanced"): "base",
        t("quality_accurate"): "small",
        t("quality_very_accurate"): "medium",
    }


def _device_options() -> dict[str, str]:
    return {
        t("cpu"): "cpu",
        t("gpu_nvidia"): "cuda",
    }


def _get_icon_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS) / "audio_reader"
    else:
        base = Path(__file__).parent.parent
    return base / "assets" / "icon.ico"


def _section_header(parent, text: str) -> None:
    container = ctk.CTkFrame(parent, fg_color=_HEADER_BLUE, corner_radius=6, height=38)
    container.pack(fill="x", pady=(12, 5))
    container.pack_propagate(False)
    accent = ctk.CTkFrame(container, fg_color=_HEADER_BLUE, width=4, corner_radius=0)
    accent.pack(side="left", fill="y")
    ctk.CTkLabel(
        container, text=text, text_color="white",
        font=("Segoe UI", 15, "bold"), fg_color="transparent",
    ).pack(side="left", padx=(10, 0))


def _dropdown(parent, variable, values) -> None:
    ctk.CTkOptionMenu(
        parent, variable=variable, values=values,
        fg_color=_DROPDOWN_BG, button_color=_DROPDOWN_BTN,
        button_hover_color=_DROPDOWN_HOVER,
        corner_radius=6, height=40,
        font=("Segoe UI", 13),
        dropdown_font=("Segoe UI", 13),
    ).pack(fill="x", pady=(0, 2))


_MODIFIERS = {"ctrl", "alt", "shift", "left ctrl", "right ctrl", "left alt", "right alt", "left shift", "right shift"}


def _format_hotkey(hotkey: str) -> str:
    return " + ".join(k.strip().capitalize() for k in hotkey.split("+"))


def _validate_hotkey(hotkey: str) -> bool:
    keys = [k.strip().lower() for k in hotkey.split("+")]
    if len(keys) < 2:
        return False
    return any(k in _MODIFIERS for k in keys)


def open_settings(app) -> None:
    config = load_config()

    quality_opts = _quality_options()
    model_to_label = {v: k for k, v in quality_opts.items()}

    device_opts = _device_options()
    device_to_label = {v: k for k, v in device_opts.items()}

    window = ctk.CTk()
    window.title("Audio Reader")
    window.geometry("550x640")
    window.resizable(False, False)
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    try:
        icon_path = _get_icon_path()
        if icon_path.exists():
            window.after(10, lambda: window.iconbitmap(str(icon_path)))
    except Exception as e:
        log.warning("Could not set window icon: %s", e)

    frame = ctk.CTkFrame(window, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=25, pady=20)

    # ── Top buttons ──
    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.pack(fill="x", pady=(0, 10))

    ctk.CTkButton(
        btn_frame, text=t("view_log"),
        fg_color=_BTN_BG, hover_color=_BTN_HOVER,
        border_width=1, border_color=_BTN_BORDER,
        corner_radius=20, width=120, height=36,
        command=lambda: _open_log(window),
    ).pack(side="left")

    ctk.CTkButton(
        btn_frame, text=t("quit_app"),
        fg_color=_BTN_BG, hover_color=_BTN_HOVER,
        border_width=1, border_color=_BTN_BORDER,
        corner_radius=20, width=120, height=36,
        command=lambda: _quit(app, window),
    ).pack(side="right")

    # ── Separator ──
    ctk.CTkFrame(frame, height=2, fg_color=_SEPARATOR).pack(fill="x", pady=(5, 10))

    # ── Transcription quality ──
    _section_header(frame, t("transcription_quality"))
    current_quality = model_to_label.get(config["model_size"], t("quality_balanced"))
    quality_var = ctk.StringVar(value=current_quality)
    _dropdown(frame, quality_var, list(quality_opts.keys()))

    # ── Processing ──
    _section_header(frame, t("processing"))
    current_device = device_to_label.get(config["device"], t("cpu"))
    device_var = ctk.StringVar(value=current_device)
    _dropdown(frame, device_var, list(device_opts.keys()))

    # ── Language ──
    _section_header(frame, t("language"))
    current_lang_label = _CODE_TO_LABEL.get(config["language"], "Auto-detect")
    lang_var = ctk.StringVar(value=current_lang_label)
    _dropdown(frame, lang_var, list(LANGUAGES.keys()))

    # ── Hotkey ──
    _section_header(frame, t("hotkey"))
    hotkey_var = ctk.StringVar(value=config.get("hotkey", "ctrl+alt"))

    hotkey_btn = ctk.CTkButton(
        frame, text=_format_hotkey(hotkey_var.get()),
        fg_color=_DROPDOWN_BG, hover_color=_DROPDOWN_HOVER,
        border_width=1, border_color=_BTN_BORDER,
        corner_radius=6, height=40,
        font=("Segoe UI", 13),
    )
    hotkey_btn.pack(fill="x", pady=(0, 2))

    def _capture_hotkey():
        hotkey_btn.configure(text=t("press_hotkey"), state="disabled")
        app.hotkey.stop()

        def _do_capture():
            try:
                combo = keyboard.read_hotkey(suppress=False)
            except Exception:
                combo = ""
            finally:
                app.hotkey.start()
            if combo and combo.lower().strip() == "esc":
                window.after(0, lambda: hotkey_btn.configure(
                    text=_format_hotkey(hotkey_var.get()), state="normal"))
            elif combo and _validate_hotkey(combo):
                hotkey_var.set(combo)
                window.after(0, lambda: hotkey_btn.configure(
                    text=_format_hotkey(combo), state="normal"))
            else:
                window.after(0, lambda: hotkey_btn.configure(
                    text=_format_hotkey(hotkey_var.get()), state="normal"))

        threading.Thread(target=_do_capture, daemon=True).start()

    hotkey_btn.configure(command=_capture_hotkey)

    # ── Restore clipboard ──
    clipboard_var = ctk.BooleanVar(value=config["restore_clipboard"])
    ctk.CTkCheckBox(
        frame, text=t("restore_clipboard"),
        variable=clipboard_var,
        font=("Segoe UI", 14),
        checkbox_width=24, checkbox_height=24,
    ).pack(anchor="w", pady=(20, 4))

    # ── Start with Windows ──
    startup_var = ctk.BooleanVar(value=config.get("start_with_windows", False))
    ctk.CTkCheckBox(
        frame, text=t("start_with_windows"),
        variable=startup_var,
        font=("Segoe UI", 14),
        checkbox_width=24, checkbox_height=24,
    ).pack(anchor="w", pady=(4, 12))

    # ── Save button ──
    def on_save():
        device = device_opts[device_var.get()]
        compute_type = "float16" if device == "cuda" else "int8"
        new_config = {
            "model_size": quality_opts[quality_var.get()],
            "device": device,
            "compute_type": compute_type,
            "language": LANGUAGES[lang_var.get()],
            "restore_clipboard": clipboard_var.get(),
            "hotkey": hotkey_var.get(),
            "start_with_windows": startup_var.get(),
        }
        save_config(new_config)
        app.update_config(new_config)
        log.info("Settings saved.")
        window.destroy()

    ctk.CTkButton(
        frame, text=t("save"),
        fg_color=_SAVE_BLUE, hover_color=_SAVE_HOVER,
        border_width=2, border_color=_SAVE_BORDER,
        corner_radius=20, height=40, width=160,
        font=("Segoe UI", 14, "bold"),
        command=on_save,
    ).pack(pady=(10, 15))

    # ── Note ──
    ctk.CTkLabel(
        frame, text=t("note_restart"),
        text_color=_NOTE_COLOR, font=("Segoe UI", 11),
    ).pack(anchor="w")

    window.mainloop()


def _open_log(parent_window):
    log_file = CONFIG_DIR / "session.log"
    log_window = ctk.CTkToplevel(parent_window)
    log_window.title(t("log_title"))
    log_window.geometry("700x400")
    log_window.attributes("-topmost", True)

    try:
        icon_path = _get_icon_path()
        if icon_path.exists():
            log_window.after(10, lambda: log_window.iconbitmap(str(icon_path)))
    except Exception as e:
        log.warning("Could not set log window icon: %s", e)

    text_box = ctk.CTkTextbox(log_window, font=("Consolas", 11), state="disabled")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)

    last_pos = [0]

    def refresh():
        if not log_window.winfo_exists():
            return
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                f.seek(last_pos[0])
                new_text = f.read()
                last_pos[0] = f.tell()
            if new_text:
                text_box.configure(state="normal")
                text_box.insert("end", new_text)
                text_box.see("end")
                text_box.configure(state="disabled")
        except Exception:
            pass
        log_window.after(500, refresh)

    refresh()


def _quit(app, window):
    log.info("Quit requested from settings.")
    window.destroy()
    app.stop()
    os._exit(0)
