from __future__ import annotations

import re
from collections.abc import Iterable

import numpy as np
from paddleocr import PaddleOCR

from .config import OcrConfig

HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class ChineseOcr:
    def __init__(self, config: OcrConfig) -> None:
        self._minimum_confidence = config.minimum_confidence
        self._han_only = config.han_characters_only
        # PaddleOCR 3.x enables the oneDNN/MKLDNN CPU engine by default. Some
        # Windows PaddlePaddle builds fail internally while converting PIR
        # attributes in that engine, so use the standard CPU engine instead.
        # The document pre-processing models are unnecessary for a small,
        # fixed game-text crop and add a substantial startup cost.
        self._engine = PaddleOCR(
            lang=config.language,
            enable_mkldnn=False,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )

    def read(self, image: np.ndarray) -> str:
        """Read text, supporting PaddleOCR's current and legacy result APIs."""
        if hasattr(self._engine, "predict"):
            try:
                return self._from_predict(self._engine.predict(image))
            except (AttributeError, KeyError, TypeError):
                # Some installed PaddleOCR versions expose predict but retain
                # legacy result structures; use the compatible fallback.
                pass
        return self._from_legacy(self._engine.ocr(image, cls=True))

    def _from_predict(self, results: Iterable[object]) -> str:
        pieces: list[str] = []
        for result in results:
            payload = getattr(result, "json", result)
            if callable(payload):
                payload = payload()
            if isinstance(payload, str):
                import json

                payload = json.loads(payload)
            if isinstance(payload, dict) and "res" in payload:
                payload = payload["res"]
            if not isinstance(payload, dict):
                continue
            texts = payload.get("rec_texts", [])
            scores = payload.get("rec_scores", [])
            for text, score in zip(texts, scores):
                if float(score) >= self._minimum_confidence:
                    pieces.append(str(text))
        return self._normalise("".join(pieces))

    def _from_legacy(self, result: object) -> str:
        pieces: list[str] = []
        for block in result or []:
            for line in block or []:
                try:
                    text, score = line[1]
                except (IndexError, TypeError, ValueError):
                    continue
                if float(score) >= self._minimum_confidence:
                    pieces.append(str(text))
        return self._normalise("".join(pieces))

    def _normalise(self, text: str) -> str:
        text = "".join(text.split())
        return "".join(HAN.findall(text)) if self._han_only else text
