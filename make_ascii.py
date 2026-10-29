"""Photo -> ascii_portrait.json for the profile card.

Why segmentation: the headshot has a dark suit on a dark backdrop, so plain
luminance ASCII turns the whole frame into noise. rembg cuts the subject out;
the composite then reads as a clean silhouette with legible facial features.

Local-only tool (needs Pillow + rembg, ~1GB model on first run). The output
JSON is committed, so CI never needs these dependencies.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

SRC = Path("/Users/apple/diary/latest_resume/nick_personal_profile.jpeg")
CUTOUT = Path("/tmp/cutout.png")
COLS = 62
CHAR_ASPECT = 2.05
CONTRAST = 1.25
LEVELS = 6


def cutout() -> Image.Image:
    if not CUTOUT.exists():
        from rembg import remove  # imported lazily so the tool runs without it once cached

        img = Image.open(SRC).convert("RGBA")
        res = remove(img)
        bbox = res.getbbox()
        if bbox:
            res = res.crop(bbox)
        res.save(CUTOUT)
    return Image.open(CUTOUT).convert("RGBA")


def build() -> dict:
    subject = cutout()
    canvas = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    canvas.alpha_composite(subject)

    g = canvas.convert("L")
    g = ImageOps.autocontrast(g, cutoff=1)
    g = ImageEnhance.Contrast(g).enhance(CONTRAST)

    rows = max(8, round(COLS * (g.size[1] / g.size[0]) / CHAR_ASPECT))
    g = g.resize((COLS, rows), Image.LANCZOS)

    shades = []
    for y in range(rows):
        row = []
        for x in range(COLS):
            v = int(g.getpixel((x, y)))
            # 0..5 = luminance steps, 6 = paper/background sentinel (always blank)
            row.append(LEVELS if v > 250 else min(LEVELS - 1, v * LEVELS // 256))
        shades.append(row)
    return {"cols": COLS, "rows": rows, "shades": shades}


if __name__ == "__main__":
    data = build()
    Path("ascii_portrait.json").write_text(json.dumps(data, separators=(",", ":")))
    ramp = " .:oO@"
    print("\n".join("".join(ramp[v] if v < len(ramp) else " " for v in row) for row in data["shades"]))
    print(f"\n{data['cols']}x{data['rows']} -> ascii_portrait.json "
          f"({Path('ascii_portrait.json').stat().st_size:,} B)")
