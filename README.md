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

- `Ctrl+Shift+S` — toggle capture and typing
- `Ctrl+Shift+Q` — quit

`tools/select_region.py` opens one captured monitor image. Drag a rectangle tightly around the changing Chinese prompt and press Enter; it updates `config.toml`.

## Configuration

The important settings are in `config.toml`:

- `capture.region`: screen coordinates of the game prompt.
- `typing.mode`: use `pinyin` for games that expect pinyin; use `characters` only when the target accepts direct Chinese characters.
- `typing.pinyin_separator`: normally empty; change it to a space if the game needs individual syllables separated.
- `typing.submit_key`: add `enter`, `space`, or `tab` only if the game requires it.

PaddleOCR downloads its language models on first use. The app disables PaddleOCR's optional oneDNN/MKLDNN CPU acceleration because some Windows PaddlePaddle builds crash inside that backend; this trades a little speed for reliable OCR. On Windows, global hotkeys or injected input can be blocked when the game is running as administrator; run this program at the same privilege level if necessary.

## Notes

The program intentionally sends each unchanged recognised prompt only once. If a prompt is missed, toggle capture off and on after adjusting the region or OCR confidence. Verify the behaviour with a non-competitive practice screen before using it anywhere important.
