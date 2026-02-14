# -*- mode: python ; coding: utf-8 -*-
import os
import importlib

# ── Locate packages ──────────────────────────────────────────────
_ctranslate2_dir = os.path.dirname(importlib.import_module("ctranslate2").__file__)
_customtkinter_dir = os.path.dirname(importlib.import_module("customtkinter").__file__)
_sounddevice_data_dir = os.path.dirname(
    importlib.import_module("_sounddevice_data").__file__
)
_faster_whisper_dir = os.path.dirname(importlib.import_module("faster_whisper").__file__)

a = Analysis(
    ["run.py"],
    pathex=[],
    binaries=[],
    datas=[
        (_customtkinter_dir, "customtkinter"),
        (_sounddevice_data_dir, "_sounddevice_data"),
        (_ctranslate2_dir, "ctranslate2"),
        (os.path.join(_faster_whisper_dir, "assets"), os.path.join("faster_whisper", "assets")),
        (os.path.join("audio_reader", "assets"), os.path.join("audio_reader", "assets")),
    ],
    hiddenimports=[
        "faster_whisper",
        "ctranslate2",
        "sounddevice",
        "_sounddevice_data",
        "customtkinter",
        "pyperclip",
        "keyboard",
        "pystray",
        "PIL",
        "PIL._tkinter_finder",
        "numpy",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AudioReader",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # No terminal window
    icon=os.path.join("audio_reader", "assets", "icon.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AudioReader",
)
