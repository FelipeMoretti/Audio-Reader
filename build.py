"""Build script: PyInstaller exe + Inno Setup installer."""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
INIT_FILE = ROOT / "audio_reader" / "__init__.py"
ISS_FILE = ROOT / "installer.iss"
SPEC_FILE = ROOT / "AudioReader.spec"

ISCC_PATHS = [
    Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
    Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    Path(os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe")),
    Path(r"C:\ProgramData\chocolatey\bin\ISCC.exe"),
]


def get_version() -> str:
    text = INIT_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"(.+?)"', text)
    if not match:
        print("ERROR: Could not read __version__ from", INIT_FILE)
        sys.exit(1)
    return match.group(1)


def update_iss_version(version: str) -> None:
    text = ISS_FILE.read_text(encoding="utf-8")
    text = re.sub(
        r'#define MyAppVersion ".*?"',
        f'#define MyAppVersion "{version}"',
        text,
    )
    text = re.sub(
        r"OutputBaseFilename=AudioReader_v.*?_Setup",
        f"OutputBaseFilename=AudioReader_v{version}_Setup",
        text,
    )
    ISS_FILE.write_text(text, encoding="utf-8")


def find_iscc() -> Path | None:
    for p in ISCC_PATHS:
        if p.exists():
            return p
    return None


def run(cmd: list[str], label: str) -> None:
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}\n")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"\nERROR: {label} failed (exit code {result.returncode})")
        sys.exit(1)


def main():
    version = get_version()
    print(f"Version: {version}")

    # Step 1: PyInstaller
    run(
        [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm"],
        "PyInstaller Build",
    )

    # Step 2: Inno Setup
    iscc = find_iscc()
    if not iscc:
        print("\nWARNING: Inno Setup (ISCC.exe) not found. Skipping installer.")
        print("Install from: https://jrsoftware.org/isdl.php")
        return

    update_iss_version(version)
    run([str(iscc), str(ISS_FILE)], "Inno Setup Installer")

    print(f"\nDone! Installer: dist/AudioReader_v{version}_Setup.exe")


if __name__ == "__main__":
    main()
