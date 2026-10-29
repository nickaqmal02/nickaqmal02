"""Generate light_mode.svg + dark_mode.svg from one layout definition.

Single source of truth for the profile card: edit the CONTENT dict or the
layout numbers here, run `python build_svg.py`, and both themes regenerate.
Dynamic values (stats) are left as placeholder text with element ids that
today.py fills in.
"""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1180, 660
PAD = 64
LEFT_X = PAD
LEFT_W = 616
RIGHT_X = 712
RIGHT_W = W - PAD - RIGHT_X

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

PALETTES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#58a6ff",
        "accent2": "#3fb950",
        "zebra": "#ffffff08",
        "chip": "#1f2937",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "text": "#1f2328",
        "muted": "#57606a",
        "accent": "#0969da",
        "accent2": "#1a7f37",
        "zebra": "#00000006",
        "chip": "#eaeef2",
    },
}

NAME = "NIK ABDUL AQMAL"
SUBTITLE = "Computer Science (Hons) @ UPNM  ·  Applied NLP & ML  ·  Malaysia"

BUILDING = [
    ("Sentiri", "NLP platform for autism therapy centres"),
    ("ApexAgent", "macOS voice agent, pure Swift"),
    ("Model eval", "XLM-R vs mBERT, losses reported too"),
]

CHIPS = [
    "Python", "Django", "PyTorch", "Hugging Face", "BERTopic",
    "LangChain", "ChromaDB", "PostgreSQL", "Redis", "Celery",
    "Swift", "Tailwind",
]

# (label, element id) — id is filled at build/refresh time
STATS = [
    ("account age", "account_age"),
    ("commits", "commit_data"),
    ("repositories", "repo_data"),
    ("stars earned", "star_data"),
    ("contributed to", "contrib_data"),
    ("followers", "follower_data"),
    ("lines written", "loc_data"),
    ("added / deleted", "loc_delta"),
]

CHIP_FONT = 13
CHIP_H = 30
CHIP_GAP = 10
ROW_GAP = 10
CHIP_COLS = 4
COL_W = (LEFT_W - CHIP_GAP * (CHIP_COLS - 1)) / CHIP_COLS

# vertical rhythm
HEADER_DIVIDER_Y = 176
BUILDING_LABEL_Y = 212
BUILDING_ROWS_Y = (246, 278, 310)
STACK_LABEL_Y = 350
CHIPS_TOP = 368
CHIPS_STEP = CHIP_H + ROW_GAP
PANEL_TOP = 196
PANEL_ROW_TOP = 248
PANEL_ROW_STEP = 34
PANEL_ROW_H = 30
PANEL_BOTTOM = PANEL_ROW_TOP + len(STATS) * PANEL_ROW_STEP - (PANEL_ROW_STEP - PANEL_ROW_H) + 12

# avatar (photo embedded as base64 — SVG loaded via <img> cannot fetch external files)
AVATAR_R = 52
AVATAR_CX = W - PAD - AVATAR_R
AVATAR_CY = 118
AVATAR_B64 = Path("avatar.b64")


def layout_chips() -> list[tuple[str, float, float]]:
    """Uniform 4-column grid inside the left column; returns (text, x, y)."""
    return [
        (text, LEFT_X + (i % CHIP_COLS) * (COL_W + CHIP_GAP),
         CHIPS_TOP + (i // CHIP_COLS) * CHIPS_STEP)
        for i, text in enumerate(CHIPS)
    ]


def build(theme: str, stats: dict[str, str]) -> str:
    p = PALETTES[theme]
    chips = layout_chips()
    chips_bottom = max(y for _, _, y in chips) + CHIP_H

    parts: list[str] = []
    add = parts.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Nik Abdul Aqmal — profile card">')
    add("<defs>")
    add("<style>")
    add(f"""
      text {{ font-family: {FONT}; }}
      .cursor {{ animation: blink 1.1s step-end infinite; }}
      @keyframes blink {{ 0%, 49% {{ opacity: 1; }} 50%, 100% {{ opacity: 0; }} }}
      @media (prefers-reduced-motion: reduce) {{ .cursor {{ animation: none; }} }}
    """)
    add("</style>")
    add(f'<clipPath id="avatarClip"><circle cx="{AVATAR_CX}" cy="{AVATAR_CY}" r="{AVATAR_R}"/></clipPath>')
    add("</defs>")

    # card
    add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" '
        f'fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="1"/>')

    # title bar
    add(f'<path d="M0.5 18.5 A18 18 0 0 1 18.5 0.5 H{W - 18.5} A18 18 0 0 1 {W - 0.5} 18.5 V46 H0.5 Z" '
        f'fill="{p["panel"]}"/>')
    add(f'<line x1="0" y1="46" x2="{W}" y2="46" stroke="{p["border"]}" stroke-width="1"/>')
    for cx, col in ((26, "#ff5f57"), (48, "#febc2e"), (70, "#28c840")):
        add(f'<circle cx="{cx}" cy="23" r="6" fill="{col}"/>')
    add(f'<text x="94" y="28" font-size="13" fill="{p["muted"]}">'
        f'nik@macbook ~ % ./whoami</text>')
    add(f'<text x="{W - PAD}" y="28" font-size="12" fill="{p["muted"]}" '
        f'text-anchor="end">zsh — 1180×660</text>')

    # header
    add(f'<text x="{LEFT_X}" y="118" font-size="40" font-weight="700" '
        f'letter-spacing="1.5" fill="{p["text"]}">{escape(NAME)}</text>')
    add(f'<text x="{LEFT_X}" y="152" font-size="16" fill="{p["muted"]}">{escape(SUBTITLE)}</text>')

    # avatar
    if AVATAR_B64.exists():
        data = AVATAR_B64.read_text().strip()
        add(f'<circle cx="{AVATAR_CX}" cy="{AVATAR_CY}" r="{AVATAR_R + 3}" fill="{p["panel"]}"/>')
        add(f'<image x="{AVATAR_CX - AVATAR_R}" y="{AVATAR_CY - AVATAR_R}" '
            f'width="{AVATAR_R * 2}" height="{AVATAR_R * 2}" '
            f'preserveAspectRatio="xMidYMid slice" clip-path="url(#avatarClip)" '
            f'href="data:image/jpeg;base64,{data}"/>')
        add(f'<circle cx="{AVATAR_CX}" cy="{AVATAR_CY}" r="{AVATAR_R}" fill="none" '
            f'stroke="{p["accent"]}" stroke-width="1.5" opacity="0.55"/>')
    else:
        add(f'<circle cx="{AVATAR_CX}" cy="{AVATAR_CY}" r="{AVATAR_R}" fill="{p["panel"]}" '
            f'stroke="{p["border"]}" stroke-width="1"/>')
    add(f'<line x1="{LEFT_X}" y1="{HEADER_DIVIDER_Y}" x2="{W - PAD}" y2="{HEADER_DIVIDER_Y}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')

    # left: currently building
    add(f'<text x="{LEFT_X}" y="{BUILDING_LABEL_Y}" font-size="12" letter-spacing="2.5" '
        f'font-weight="700" fill="{p["accent"]}">CURRENTLY BUILDING</text>')
    for i, (name, desc) in enumerate(BUILDING):
        y = BUILDING_ROWS_Y[i]
        add(f'<text x="{LEFT_X}" y="{y}" font-size="15" fill="{p["accent2"]}">›</text>')
        add(f'<text x="{LEFT_X + 18}" y="{y}" font-size="15" font-weight="700" '
            f'fill="{p["text"]}">{escape(name)}</text>')
        add(f'<text x="{LEFT_X + 18 + len(name) * 9.1 + 14}" y="{y}" font-size="14" '
            f'fill="{p["muted"]}">— {escape(desc)}</text>')

    # left: stack chips (uniform grid)
    add(f'<text x="{LEFT_X}" y="{STACK_LABEL_Y}" font-size="12" letter-spacing="2.5" '
        f'font-weight="700" fill="{p["accent"]}">STACK</text>')
    for text, x, y in chips:
        add(f'<rect x="{x}" y="{y}" width="{COL_W}" height="{CHIP_H}" rx="{CHIP_H / 2}" '
            f'fill="{p["chip"]}" stroke="{p["border"]}" stroke-width="1"/>')
        add(f'<text x="{x + COL_W / 2}" y="{y + 20}" font-size="{CHIP_FONT}" '
            f'fill="{p["text"]}" text-anchor="middle">{escape(text)}</text>')

    # left: contact
    contact_y = chips_bottom + 46
    add(f'<text x="{LEFT_X}" y="{contact_y}" font-size="14" fill="{p["muted"]}">'
        f'✉  nikabdulaqmal@gmail.com</text>')
    add(f'<text x="{LEFT_X + 250}" y="{contact_y}" font-size="14" fill="{p["muted"]}">'
        f'⌥  github.com/nickaqmal02</text>')

    # right: stats panel
    add(f'<rect x="{RIGHT_X}" y="{PANEL_TOP}" width="{RIGHT_W}" height="{PANEL_BOTTOM - PANEL_TOP}" '
        f'rx="12" fill="{p["panel"]}" stroke="{p["border"]}" stroke-width="1"/>')
    add(f'<text x="{RIGHT_X + 20}" y="{PANEL_TOP + 30}" font-size="12" letter-spacing="2.5" '
        f'font-weight="700" fill="{p["accent"]}">GITHUB</text>')
    add(f'<line x1="{RIGHT_X + 20}" y1="{PANEL_TOP + 42}" x2="{RIGHT_X + RIGHT_W - 20}" '
        f'y2="{PANEL_TOP + 42}" stroke="{p["border"]}" stroke-width="1"/>')

    row_top = PANEL_ROW_TOP
    for i, (label, eid) in enumerate(STATS):
        y = row_top + i * PANEL_ROW_STEP
        if i % 2 == 0:
            add(f'<rect x="{RIGHT_X + 10}" y="{y}" width="{RIGHT_W - 20}" height="{PANEL_ROW_H}" '
                f'rx="6" fill="{p["zebra"]}"/>')
        add(f'<text x="{RIGHT_X + 22}" y="{y + 20}" font-size="13" fill="{p["muted"]}">'
            f'{escape(label)}</text>')
        add(f'<text id="{eid}" x="{RIGHT_X + RIGHT_W - 22}" y="{y + 20}" font-size="13" '
            f'font-weight="600" fill="{p["text"]}" text-anchor="end">'
            f'{escape(stats.get(eid, "—"))}</text>')

    # footer
    footer_y = H - 62
    add(f'<line x1="{PAD}" y1="{footer_y - 30}" x2="{W - PAD}" y2="{footer_y - 30}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')
    add(f'<text x="{PAD}" y="{footer_y}" font-size="14" fill="{p["text"]}">'
        f'<tspan fill="{p["accent2"]}">nik@sentiri</tspan> '
        f'<tspan fill="{p["muted"]}">~ %</tspan> '
        f'<tspan fill="{p["muted"]}">measure it, or it didn\'t happen</tspan></text>')
    add(f'<rect class="cursor" x="{PAD + 402}" y="{footer_y - 12}" width="9" height="15" '
        f'fill="{p["accent"]}"/>')
    add(f'<text x="{W - PAD}" y="{footer_y}" font-size="13" fill="{p["muted"]}" '
        f'text-anchor="end">open to AI engineering conversations</text>')

    add("</svg>")
    return "\n".join(parts) + "\n"


def main() -> None:
    seed = {eid: "—" for _, eid in STATS}
    for theme in ("dark", "light"):
        path = Path(f"{theme}_mode.svg")
        path.write_text(build(theme, seed), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
