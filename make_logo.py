"""Neovim logo -> ascii_logo.json (block glyphs, brand colours preserved).

The logo is solid shapes on transparency, so coverage (alpha) drives glyph
density while hue decides which brand colour a cell belongs to. Colours are
stored as indices; build_svg.py maps them per theme.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

SRC = Path("/tmp/nvim_logo.png")
OUT = Path("ascii_logo.json")
COLS = 46
CHAR_ASPECT = 2.0
GLYPHS = " ░▒▓█"      # index 0..4 by coverage


def build() -> dict:
    img = Image.open(SRC).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    w, h = img.size
    rows = max(6, round(COLS * (h / w) / CHAR_ASPECT))
    img = img.resize((COLS, rows), Image.LANCZOS)

    cells = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            r, g, b, a = img.getpixel((x, y))
            if a < 40:
                line.append([0, 0])
                continue
            glyph = min(4, max(1, round(a / 255 * 4)))
            # blue vs green family, then light/dark within the family
            lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            if b > g:
                colour = 0 if lum >= 0.55 else 1          # blue / deep blue
            else:
                colour = 2 if lum >= 0.55 else 3          # green / deep green
            line.append([glyph, colour])
        cells.append(line)
    return {"cols": COLS, "rows": rows, "cells": cells}


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    for row in data["cells"]:
        print("".join(GLYPHS[g] for g, _ in row))
    print(f"\n{data['cols']}x{data['rows']} -> {OUT} ({OUT.stat().st_size:,} B)")
