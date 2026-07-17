from __future__ import annotations

import numpy as np
from mss import mss

from .config import CaptureConfig


class RegionCapture:
    def __init__(self, config: CaptureConfig) -> None:
        self._sct = mss()
        if config.monitor < 1 or config.monitor >= len(self._sct.monitors):
            raise ValueError(
                f"monitor {config.monitor} is unavailable; "
                f"choose 1 through {len(self._sct.monitors) - 1}"
            )
        monitor = self._sct.monitors[config.monitor]
        left, top, width, height = config.region
        self._region = {
            "left": monitor["left"] + left,
            "top": monitor["top"] + top,
            "width": width,
            "height": height,
        }

    def grab(self) -> np.ndarray:
        """Return a BGR OpenCV image from the configured region."""
        image = np.asarray(self._sct.grab(self._region))
        return image[:, :, :3]

    def close(self) -> None:
        self._sct.close()
