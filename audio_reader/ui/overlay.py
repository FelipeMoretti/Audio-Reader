import logging
import tkinter as tk
import threading

from PIL import Image, ImageDraw, ImageTk

from audio_reader.app import AppState
from audio_reader.i18n import t

log = logging.getLogger(__name__)

BAR_W = 180
BAR_H = 36
RADIUS = 18
BOTTOM_MARGIN = 48
_BAR_COLOR = "#2b2b2b"
_TRANSPARENT = "#010101"
_CIRCLE_SIZE = 16
_CIRCLE_X = 10
_CIRCLE_Y = 9
_SS = 4

PULSE_MIN = 0.35
PULSE_MAX = 1.0
PULSE_STEP = 0.03
PULSE_MS = 30

_STATE_COLORS = {
    AppState.RECORDING: "#F44336",
    AppState.TRANSCRIBING: "#FF9800",
    AppState.INJECTING: "#4CAF50",
}

_STATE_KEYS = {
    AppState.RECORDING: "recording",
    AppState.TRANSCRIBING: "transcribing",
    AppState.INJECTING: "injecting",
}


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _create_pill(w, h, r, fill, bg):
    sw, sh = w * _SS, h * _SS
    img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=r * _SS, fill=fill)
    img = img.resize((w, h), Image.LANCZOS)
    alpha = img.split()[3]
    mask = alpha.point(lambda a: 255 if a > 128 else 0)
    result = Image.new("RGB", (w, h), bg)
    result.paste(Image.new("RGB", (w, h), fill), mask=mask)
    return result


def _create_circle(size, fill, bg):
    ss = size * _SS
    img = Image.new("RGB", (ss, ss), bg)
    draw = ImageDraw.Draw(img)
    draw.ellipse([0, 0, ss - 1, ss - 1], fill=fill)
    return img.resize((size, size), Image.LANCZOS)


class StatusOverlay:
    def __init__(self):
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._circle_item = None
        self._label = None
        self._thread: threading.Thread | None = None
        self._pill_photo = None
        self._circle_photo = None
        self._visible = False
        self._pulsing = False
        self._pulse_alpha = PULSE_MAX
        self._pulse_dir = -1
        self._pulse_rgb = (255, 255, 255)

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()

    def _run_tk(self) -> None:
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.attributes("-transparentcolor", _TRANSPARENT)
        self._root.configure(bg=_TRANSPARENT)

        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - BAR_W) // 2
        y = screen_h - BAR_H - BOTTOM_MARGIN
        self._root.geometry(f"{BAR_W}x{BAR_H}+{x}+{y}")

        self._canvas = tk.Canvas(
            self._root, width=BAR_W, height=BAR_H,
            bg=_TRANSPARENT, highlightthickness=0,
        )
        self._canvas.pack()

        pill_img = _create_pill(BAR_W, BAR_H, RADIUS, _BAR_COLOR, _TRANSPARENT)
        self._pill_photo = ImageTk.PhotoImage(pill_img)
        self._canvas.create_image(0, 0, anchor="nw", image=self._pill_photo)

        circle_img = _create_circle(_CIRCLE_SIZE, "white", _BAR_COLOR)
        self._circle_photo = ImageTk.PhotoImage(circle_img)
        self._circle_item = self._canvas.create_image(
            _CIRCLE_X, _CIRCLE_Y, anchor="nw", image=self._circle_photo,
        )

        self._label = self._canvas.create_text(
            (BAR_W + 26) // 2, BAR_H // 2,
            text="", fill="white",
            font=("Segoe UI", 11, "bold"),
        )

        self._root.withdraw()
        self._root.mainloop()

    def _update_circle(self, color: str) -> None:
        if not self._canvas:
            return
        circle_img = _create_circle(_CIRCLE_SIZE, color, _BAR_COLOR)
        self._circle_photo = ImageTk.PhotoImage(circle_img)
        self._canvas.itemconfig(self._circle_item, image=self._circle_photo)

    def update_state(self, state: AppState) -> None:
        if self._root is None:
            return
        color = _STATE_COLORS.get(state)
        key = _STATE_KEYS.get(state)
        if color and key:
            self._root.after(0, self._show, color, t(key))
        else:
            self._root.after(0, self._hide)

    def _show(self, circle_color: str, text: str) -> None:
        if not self._canvas:
            return
        self._update_circle(circle_color)
        self._canvas.itemconfig(self._label, text=text)
        if self._root:
            self._root.deiconify()
        self._visible = True

        is_recording = (circle_color == _STATE_COLORS[AppState.RECORDING])
        if is_recording and not self._pulsing:
            self._pulse_rgb = _hex_to_rgb(circle_color)
            self._pulsing = True
            self._pulse_alpha = PULSE_MAX
            self._pulse_dir = -1
            self._pulse()
        elif not is_recording:
            self._pulsing = False

    def _pulse(self) -> None:
        if not self._pulsing or not self._canvas:
            return
        self._pulse_alpha += self._pulse_dir * PULSE_STEP
        if self._pulse_alpha <= PULSE_MIN:
            self._pulse_alpha = PULSE_MIN
            self._pulse_dir = 1
        elif self._pulse_alpha >= PULSE_MAX:
            self._pulse_alpha = PULSE_MAX
            self._pulse_dir = -1

        r, g, b = self._pulse_rgb
        v = self._pulse_alpha
        color = f"#{int(r * v):02x}{int(g * v):02x}{int(b * v):02x}"
        self._update_circle(color)

        if self._root:
            self._root.after(PULSE_MS, self._pulse)

    def _hide(self) -> None:
        self._pulsing = False
        if self._root:
            self._root.withdraw()
        self._visible = False

    def stop(self) -> None:
        self._pulsing = False
        if self._root:
            self._root.after(0, self._root.destroy)
