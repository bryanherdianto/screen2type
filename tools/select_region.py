"""Interactively save a screen capture rectangle into config.toml."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from time import sleep

import cv2
import numpy as np
from mss import mss


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    parser.add_argument("--monitor", type=int, default=None)
    parser.add_argument(
        "--delay",
        type=float,
        default=5.0,
        help="seconds to wait before the screenshot, so you can focus the game",
    )
    args = parser.parse_args()
    if not args.config.is_file():
        parser.error(
            f"config file not found: {args.config}. Copy config.example.toml first."
        )

    source = args.config.read_text(encoding="utf-8")
    match = re.search(r"(?m)^monitor\s*=\s*(\d+)", source)
    if match is None:
        parser.error("config file has no [capture] monitor setting")
    configured_monitor = int(match.group(1))
    monitor_number = args.monitor or configured_monitor
    for remaining in range(int(args.delay), 0, -1):
        print(f"Capturing in {remaining}... switch to the game window now.")
        sleep(1)
    with mss() as sct:
        if monitor_number < 1 or monitor_number >= len(sct.monitors):
            parser.error(f"monitor must be 1 through {len(sct.monitors) - 1}")
        monitor = sct.monitors[monitor_number]
        image = np.asarray(sct.grab(monitor))[:, :, :3]

    region = cv2.selectROI(
        "Select Chinese prompt, then press Enter", image, False, False
    )
    cv2.destroyAllWindows()
    left, top, width, height = (int(value) for value in region)
    if width == 0 or height == 0:
        print("No region selected; config was not changed.")
        return 1

    replacement = f"region = [{left}, {top}, {width}, {height}]"
    updated = re.sub(r"(?m)^region\s*=\s*\[[^]]+\]", replacement, source, count=1)
    args.config.write_text(updated, encoding="utf-8")
    print(f"Saved {replacement} to {args.config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
