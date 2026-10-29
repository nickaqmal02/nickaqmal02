"""Prepare the profile photo for embedding in the SVG card.

Photos can't be vector-traced without looking like a posterised mess, so we
embed a small raster as a base64 data URI inside the SVG instead. That keeps
the card a single self-contained file (external refs are blocked when an SVG
is loaded through an <img> tag, which is exactly how GitHub serves it).

Run once locally, commit avatar.b64 + avatar.jpg, then build_svg.py needs no
Pillow at all (so CI stays light).
"""

from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

from PIL import Image

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/apple/diary/latest_resume/nick_personal_profile.jpeg"
)
SIZE = 240  # rendered at ~104px; 240px covers 2x displays


def main() -> None:
    img = Image.open(SRC).convert("RGB")

    # centre square crop
    w, h = img.size
    side = min(w, h)
    left, top = (w - side) // 2, (h - side) // 2
    img = img.crop((left, top, left + side, top + side)).resize((SIZE, SIZE), Image.LANCZOS)

    img.save("avatar.jpg", "JPEG", quality=86, optimize=True, progressive=True)

    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    raw = buf.getvalue()
    Path("avatar.b64").write_text(base64.b64encode(raw).decode())

    print(f"source  : {SRC}")
    print(f"avatar  : {SIZE}x{SIZE} jpeg, {len(raw) / 1024:.1f} KB -> base64 "
          f"{Path('avatar.b64').stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
