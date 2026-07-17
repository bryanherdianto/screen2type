from __future__ import annotations

from time import sleep

from pynput.keyboard import Controller, Key
from pypinyin import Style, lazy_pinyin

from .config import TypingConfig


class TextTyper:
    def __init__(self, config: TypingConfig) -> None:
        self._config = config
        self._keyboard = Controller()

    def send(self, text: str) -> str:
        if self._config.mode == "pinyin":
            output = self._config.pinyin_separator.join(
                lazy_pinyin(text, style=Style.NORMAL, errors=lambda value: list(value))
            )
        else:
            output = text

        for character in output:
            self._keyboard.press(character)
            self._keyboard.release(character)
            if self._config.seconds_between_keys:
                sleep(self._config.seconds_between_keys)

        submit_key = self._config.submit_key
        if submit_key != "none":
            key = {"enter": Key.enter, "space": Key.space, "tab": Key.tab}[submit_key]
            self._keyboard.press(key)
            self._keyboard.release(key)
        return output
