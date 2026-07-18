from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path

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
        print(
            "Ready. Press Enter in this terminal to start or pause typing; "
            "press Ctrl+C to quit.",
            flush=True,
        )
        threading.Thread(target=self._watch_stdin, daemon=True).start()
        try:
            while not self._quit.is_set():
                if not self._enabled.is_set():
                    self._quit.wait(0.05)
                    continue
                self._tick()
                self._quit.wait(self._settings.runtime.poll_interval_seconds)
        finally:
            self._capture.close()

    def _watch_stdin(self) -> None:
        for _ in sys.stdin:
            if self._quit.is_set():
                return
            if self._enabled.is_set():
                self._enabled.clear()
                self._last_sent = None
                self._empty_reads = 0
                print("Paused. Press Enter to start again.", flush=True)
                continue
            delay = int(self._settings.runtime.start_delay_seconds)
            for remaining in range(delay, 0, -1):
                print(
                    f"Starting in {remaining}... switch to the game window.",
                    flush=True,
                )
                if self._quit.wait(1):
                    return
            self._enabled.set()
            print("Capture and typing enabled. Press Enter to pause.", flush=True)
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
        if self._quit.is_set() or not self._enabled.is_set():
            return

        output = self._typer.send(text, cancel=self._quit)
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
