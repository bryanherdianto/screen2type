from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class CaptureConfig:
    monitor: int
    region: tuple[int, int, int, int]


@dataclass(frozen=True)
class OcrConfig:
    language: str
    minimum_confidence: float
    han_characters_only: bool


@dataclass(frozen=True)
class TypingConfig:
    mode: str
    pinyin_separator: str
    seconds_between_keys: float
    submit_key: str


@dataclass(frozen=True)
class RuntimeConfig:
    poll_interval_seconds: float
    empty_reads_to_reset: int
    maximum_characters: int
    start_delay_seconds: float


@dataclass(frozen=True)
class Settings:
    capture: CaptureConfig
    ocr: OcrConfig
    typing: TypingConfig
    runtime: RuntimeConfig


def load_settings(path: Path) -> Settings:
    with path.open("rb") as file:
        data = tomllib.load(file)

    capture = data["capture"]
    region = tuple(int(value) for value in capture["region"])
    if len(region) != 4 or region[2] <= 0 or region[3] <= 0:
        raise ValueError("capture.region must be [left, top, width, height]")

    typing = data["typing"]
    mode = typing["mode"].lower()
    if mode not in {"pinyin", "characters"}:
        raise ValueError("typing.mode must be 'pinyin' or 'characters'")
    submit_key = typing["submit_key"].lower()
    if submit_key not in {"none", "enter", "space", "tab"}:
        raise ValueError("typing.submit_key must be none, enter, space, or tab")

    ocr = data["ocr"]
    runtime = data["runtime"]
    return Settings(
        capture=CaptureConfig(int(capture["monitor"]), region),
        ocr=OcrConfig(
            str(ocr["language"]),
            float(ocr["minimum_confidence"]),
            bool(ocr["han_characters_only"]),
        ),
        typing=TypingConfig(
            mode,
            str(typing["pinyin_separator"]),
            float(typing["seconds_between_keys"]),
            submit_key,
        ),
        runtime=RuntimeConfig(
            float(runtime["poll_interval_seconds"]),
            int(runtime["empty_reads_to_reset"]),
            int(runtime["maximum_characters"]),
            float(runtime.get("start_delay_seconds", 5.0)),
        ),
    )
