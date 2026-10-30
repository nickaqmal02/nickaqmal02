"""Render nik_resume.pdf into an animated GIF preview for the GitHub README.

Pages -> PNG (PyMuPDF) -> downscale -> looped GIF.
"""
from pathlib import Path
from typing import List

import pymupdf
from PIL import Image

PDF: Path = Path.home() / "nickaqmal02" / "nik_resume.pdf"
OUT: Path = Path.home() / "nickaqmal02" / "nik_resume_preview.gif"
SCALE: float = 1.4          # zoom factor for crisp text at small size
TARGET_WIDTH: int = 560     # README display width (px)
FRAME_MS: int = 6000        # 6 s per page
GIF_WIDTH: int = 720        # stored width before GitHub's display scaling


def main() -> None:
    doc: pymupdf.Document = pymupdf.open(PDF)
    frames: List[Image.Image] = []
    for page in doc:
        pix: pymupdf.Pixmap = page.get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE))
        img: Image.Image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        ratio: float = GIF_WIDTH / img.width
        img = img.resize((GIF_WIDTH, int(img.height * ratio)), Image.LANCZOS)
        frames.append(img)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    print(f"pages={len(frames)} size_kb={OUT.stat().st_size // 1024} out={OUT}")


if __name__ == "__main__":
    main()
