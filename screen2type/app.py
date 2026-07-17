from __future__ import annotations

import argparse
import threading
from pathlib import Path
from time import sleep

from pynput import keyboard

from .capture import RegionCapture
from .config import Settings, load_settings
from .ocr import ChineseOcr
from .typing import TextTyper


class App:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._capture = RegionCapture(settings.capture)
        self._ocr = ChineseOcr(settings.ocr)
        self._typer = TextTyper(settings.typing)
        self._enabled = threading.Event()
        self._quit = threading.Event()
        self._last_sent: str | None = None
        self._empty_reads = 0

    def run(self) -> None:
        print("Ready. Ctrl+Shift+S toggles typing; Ctrl+Shift+Q quits.")
        with keyboard.GlobalHotKeys(
            {
                "<ctrl>+<shift>+s": self._toggle,
                "<ctrl>+<shift>+q": self._stop,
            }
        ):
            try:
                while not self._quit.is_set():
                    if not self._enabled.is_set():
                        sleep(0.05)
                        continue
                    self._tick()
                    sleep(self._settings.runtime.poll_interval_seconds)
            finally:
                self._capture.close()

    def _toggle(self) -> None:
        if self._enabled.is_set():
            self._enabled.clear()
            self._last_sent = None
            self._empty_reads = 0
            print("Paused.")
        else:
            self._enabled.set()
            print("Capture and typing enabled.")

    def _stop(self) -> None:
        print("Stopping.")
        self._quit.set()

    def _tick(self) -> None:
        text = self._ocr.read(self._capture.grab())
        if not text:
            self._empty_reads += 1
            if self._empty_reads >= self._settings.runtime.empty_reads_to_reset:
                self._last_sent = None
            return

        self._empty_reads = 0
        if len(text) > self._settings.runtime.maximum_characters:
            print(f"Skipping suspicious OCR result ({len(text)} chars): {text!r}")
            return
        if text == self._last_sent:
            return

        output = self._typer.send(text)
        self._last_sent = text
        print(f"Sent {text!r} as {output!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR Chinese game text and type it.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    args = parser.parse_args()
    if not args.config.is_file():
        parser.error(
            f"config file not found: {args.config}. Copy config.example.toml first."
        )
    try:
        App(load_settings(args.config)).run()
    except KeyboardInterrupt:
        print("Stopped.")
    return 0
