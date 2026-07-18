# screen2type

An OCR-to-pinyin helper for Chinese typing games. It captures a fixed screen region, recognises the Chinese prompt with PaddleOCR, converts it to pinyin, and sends keystrokes after a global hotkey.

## Setup

Requires Python 3.11+.

```powershell
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Copy-Item config.example.toml config.toml
python tools/select_region.py --config config.toml
python main.py
```

Keep the game focused, then use:

- `Ctrl+Alt+S` to toggle capture and typing
- `Ctrl+Alt+Q` to quit

`tools/select_region.py` waits a few seconds (`--delay`, default 5) so you can focus the game window, then opens one captured monitor image. Drag a rectangle tightly around the changing Chinese prompt and press Enter; it updates `config.toml` automatically.

## Configuration

The important settings are in `config.toml`:

- `capture.region`: screen coordinates of the game prompt.
- `typing.mode`: use `pinyin` for games that expect pinyin; use `characters` only when the target accepts direct Chinese characters.
- `typing.pinyin_separator`: normally empty; change it to a space if the game needs individual syllables separated.
- `typing.submit_key`: add `enter`, `space`, or `tab` only if the game requires it.
