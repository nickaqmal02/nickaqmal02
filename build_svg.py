"""Generate the light/dark profile cards (neofetch layout + Neovim logo art).

Single source of truth: edit CONTENT / ROWS / palette here, run
`python build_svg.py`, commit both SVGs. Live values are element ids that
today.py rewrites, so this file is only for design changes.

Left: Neovim logo as block glyphs (brand blue/green kept per cell).
Right: dot-leader key/value rows, dashed section rules.
Footer: quote in comment syntax.
"""

from __future__ import annotations

import json
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1200, 660

PALETTES = {
    "dark": {
        "bg": "#0b0f14",
        "border": "#1e2a36",
        "text": "#dbe6f0",
        "muted": "#6b7d8f",
        "label": "#8b6fd4",
        "accent": "#58a6ff",
        "accent2": "#2ea043",
        "warn": "#d94f4f",
        # logo: blue-light, blue-deep, green-light, green-deep
        "logo": ("#4aa3e0", "#1f6f9c", "#7dc35a", "#3f7a2f"),
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d8dee6",
        "text": "#1b222c",
        "muted": "#6b7785",
        "label": "#7c5cbf",
        "accent": "#0969da",
        "accent2": "#16794a",
        "warn": "#c93c37",
        "logo": ("#1f6f9c", "#10394f", "#3f7a2f", "#204d18"),
    },
}
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"
GLYPHS = " ░▒▓█"

HEADER_USER = "nik@sentiri"
HEADER_TAIL = "final-year · AI engineering"

ROWS = [
    ("Status", "running", "dot"),
    ("Uptime", "—", "account_age"),
    ("Host", "UPNM · Malaysia", None),
    ("Kernel", "B.Sc. Computer Science (Hons)", None),
    ("Shell", "zsh · LazyVim", None),
    ("Focus", "NLP · RAG · backend", None),
]
BUILDING = [
    ("Sentiri", "NLP for autism therapy centres"),
    ("ApexAgent", "macOS voice agent in Swift"),
    ("Model eval", "XLM-R vs mBERT, losses too"),
]
STATS = [
    ("Repos", "repo_data"),
    ("Stars", "star_data"),
    ("Commits", "commit_data"),
    ("Followers", "follower_data"),
    ("Lines", "loc_data"),
]
QUOTE = "// measure it, or it didn't happen."

# ── geometry ──────────────────────────────────────────────────────────────
PORT_X, PORT_TOP = 60, 108
PORT_SIZE, PORT_LH = 11, 13.2
PORT_ADV = PORT_SIZE * 0.6
DIVIDER_X = 500
LEFT_CENTER = (PORT_X + DIVIDER_X) / 2
RIGHT_X, RIGHT_EDGE = 550, 1140
VALUE_X = RIGHT_EDGE
ROW_TOP, ROW_STEP = 120, 24
DOT_RESERVE = 128
FOOTER_RULE_Y = H - 88
FOOTER_TEXT_Y = H - 56


def load_logo() -> dict:
    p = Path("ascii_logo.json")
    return json.loads(p.read_text()) if p.exists() else {"cols": 0, "rows": 0, "cells": []}


def tw(s: str, size: float = 13) -> float:
    return len(s) * size * 0.6


def build(theme: str, values: dict[str, str]) -> str:
    p = PALETTES[theme]
    logo = load_logo()
    logo_w = logo["cols"] * PORT_ADV
    logo_h = logo["rows"] * PORT_LH
    logo_x = LEFT_CENTER - logo_w / 2
    out: list[str] = []
    add = out.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Nik Abdul Aqmal — profile card">')
    add("<defs><style>")
    add(f"""
      text {{ font-family: {FONT}; }}
      .blink {{ animation: blink 1.15s step-end infinite; }}
      @keyframes blink {{ 0%,49% {{ opacity:1 }} 50%,100% {{ opacity:0 }} }}
      .pulse {{ animation: pulse 2.4s ease-in-out infinite; }}
      @keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.3 }} }}
      .scan {{ animation: scan 8s linear infinite; }}
      @keyframes scan {{
        0%   {{ transform: translateY(0); opacity: 0; }}
        6%   {{ opacity: .18; }}
        58%  {{ opacity: .18; }}
        66%  {{ transform: translateY({logo_h:.0f}px); opacity: 0; }}
        100% {{ transform: translateY({logo_h:.0f}px); opacity: 0; }}
      }}
      @media (prefers-reduced-motion: reduce) {{ .blink, .pulse, .scan {{ animation: none; }} }}
    """)
    add("</style></defs>")

    add(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" '
        f'fill="{p["bg"]}" stroke="{p["border"]}" stroke-width="1"/>')

    # header
    add(f'<text x="{PORT_X}" y="66" font-size="15">'
        f'<tspan fill="{p["accent"]}">{escape(HEADER_USER)}</tspan>'
        f'<tspan fill="{p["muted"]}"> ~ % neofetch</tspan></text>')
    add(f'<text x="{RIGHT_EDGE}" y="66" font-size="11" fill="{p["muted"]}" '
        f'text-anchor="end">{escape(HEADER_TAIL)}</text>')
    add(f'<line x1="{PORT_X}" y1="82" x2="{RIGHT_EDGE}" y2="82" '
        f'stroke="{p["border"]}" stroke-width="1"/>')

    # ── logo ──────────────────────────────────────────────────────────────
    if logo["cells"]:
        add('<g id="logo">')
        add(f'<rect class="scan" x="{logo_x - 6:.0f}" y="{PORT_TOP - 6}" '
            f'width="{logo_w + 12:.0f}" height="2" fill="{p["accent"]}" opacity="0"/>')
        for i, row in enumerate(logo["cells"]):
            y = PORT_TOP + i * PORT_LH
            if all(cell[0] == 0 for cell in row):
                continue
            add(f'<text x="{LEFT_CENTER:.0f}" y="{y:.1f}" font-size="{PORT_SIZE}" '
                f'text-anchor="middle" xml:space="preserve">')
            run_colour, buf = None, ""
            for glyph_idx, colour_idx in row:
                if run_colour is None:
                    run_colour, buf = colour_idx, GLYPHS[glyph_idx]
                elif colour_idx != run_colour:
                    add(f'<tspan fill="{p["logo"][run_colour]}">{escape(buf)}</tspan>')
                    run_colour, buf = colour_idx, GLYPHS[glyph_idx]
                else:
                    buf += GLYPHS[glyph_idx]
            if buf:
                add(f'<tspan fill="{p["logo"][run_colour]}">{escape(buf)}</tspan>')
            add("</text>")
        add("</g>")

    # vertical rule between logo and data
    rule_bottom = PORT_TOP + (logo_h if logo["rows"] else 360) + 8
    add(f'<line x1="{DIVIDER_X}" y1="104" x2="{DIVIDER_X}" y2="{rule_bottom:.0f}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')

    # centred caption under the logo
    cap_y = PORT_TOP + (logo_h if logo["rows"] else 360) + 34
    add(f'<text x="{LEFT_CENTER:.0f}" y="{cap_y:.0f}" font-size="11" fill="{p["muted"]}" '
        f'text-anchor="middle">nikabdulaqmal@gmail.com</text>')
    add(f'<text x="{LEFT_CENTER:.0f}" y="{cap_y + 18:.0f}" font-size="11" fill="{p["muted"]}" '
        f'text-anchor="middle">github.com/nickaqmal02</text>')

    # ── key/value rows ────────────────────────────────────────────────────
    y = ROW_TOP
    for label, value, eid in ROWS:
        add(f'<text x="{RIGHT_X}" y="{y}" font-size="12" letter-spacing="1.2" '
            f'fill="{p["label"]}">{escape(label.upper())}</text>')
        add(f'<line x1="{RIGHT_X + tw(label.upper(), 12) + 12:.0f}" y1="{y - 4}" '
            f'x2="{VALUE_X - DOT_RESERVE}" y2="{y - 4}" stroke="{p["muted"]}" '
            f'stroke-width="1" stroke-dasharray="1 5" opacity="0.65"/>')
        if eid == "account_age":
            add(f'<text id="account_age" x="{VALUE_X}" y="{y}" font-size="13" '
                f'fill="{p["text"]}" text-anchor="end">{escape(values.get("account_age", "—"))}</text>')
        elif eid == "dot":
            add(f'<circle class="pulse" cx="{VALUE_X - tw(value, 13) - 13:.0f}" cy="{y - 4}" '
                f'r="4" fill="{p["accent2"]}"/>')
            add(f'<text x="{VALUE_X}" y="{y}" font-size="13" fill="{p["text"]}" '
                f'text-anchor="end">{escape(value)}</text>')
        else:
            add(f'<text x="{VALUE_X}" y="{y}" font-size="13" fill="{p["text"]}" '
                f'text-anchor="end">{escape(value)}</text>')
        y += ROW_STEP

    # ── building ──────────────────────────────────────────────────────────
    y += 22
    add(f'<text x="{RIGHT_X}" y="{y}" font-size="11" letter-spacing="2" font-weight="700" '
        f'fill="{p["accent2"]}">- BUILDING</text>')
    add(f'<line x1="{RIGHT_X + 108}" y1="{y - 4}" x2="{RIGHT_EDGE}" y2="{y - 4}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')
    y += 26
    for name, desc in BUILDING:
        add(f'<text x="{RIGHT_X}" y="{y}" font-size="13" fill="{p["accent2"]}">›</text>')
        add(f'<text x="{RIGHT_X + 18}" y="{y}" font-size="13" font-weight="700" '
            f'fill="{p["text"]}">{escape(name)}</text>')
        add(f'<text x="{RIGHT_X + 18 + tw(name, 13) + 14:.0f}" y="{y}" font-size="12.5" '
            f'fill="{p["muted"]}">— {escape(desc)}</text>')
        y += ROW_STEP

    # ── github stats ──────────────────────────────────────────────────────
    y += 22
    add(f'<text x="{RIGHT_X}" y="{y}" font-size="11" letter-spacing="2" font-weight="700" '
        f'fill="{p["accent"]}">- GITHUB</text>')
    add(f'<line x1="{RIGHT_X + 92}" y1="{y - 4}" x2="{RIGHT_EDGE}" y2="{y - 4}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')
    y += 26
    for label, eid in STATS:
        add(f'<text x="{RIGHT_X}" y="{y}" font-size="12" letter-spacing="1.2" '
            f'fill="{p["label"]}">{escape(label.upper())}</text>')
        add(f'<line x1="{RIGHT_X + tw(label.upper(), 12) + 12:.0f}" y1="{y - 4}" '
            f'x2="{VALUE_X - DOT_RESERVE}" y2="{y - 4}" stroke="{p["muted"]}" '
            f'stroke-width="1" stroke-dasharray="1 5" opacity="0.65"/>')
        add(f'<text id="{eid}" x="{VALUE_X}" y="{y}" font-size="13" fill="{p["text"]}" '
            f'text-anchor="end">—</text>')
        y += ROW_STEP

    add(f'<text x="{VALUE_X}" y="{y + 2}" font-size="10.5" text-anchor="end">'
        f'<tspan id="loc_add" fill="{p["accent2"]}">—</tspan>'
        f'<tspan fill="{p["muted"]}"> / </tspan>'
        f'<tspan id="loc_del" fill="{p["warn"]}">—</tspan></text>')

    # ── footer ────────────────────────────────────────────────────────────
    add(f'<line x1="{PORT_X}" y1="{FOOTER_RULE_Y}" x2="{RIGHT_EDGE}" y2="{FOOTER_RULE_Y}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')
    add(f'<text x="{PORT_X}" y="{FOOTER_TEXT_Y}" font-size="13" fill="{p["muted"]}">'
        f'{escape(QUOTE)}</text>')
    add(f'<rect class="blink" x="{PORT_X + tw(QUOTE, 13) + 7:.0f}" y="{FOOTER_TEXT_Y - 12}" '
        f'width="8" height="14" fill="{p["accent"]}"/>')
    add(f'<text x="{RIGHT_EDGE}" y="{FOOTER_TEXT_Y}" font-size="11" fill="{p["muted"]}" '
        f'text-anchor="end">open to AI engineering roles</text>')

    add("</svg>")
    return "\n".join(out) + "\n"


def main() -> None:
    for theme in ("dark", "light"):
        path = Path(f"{theme}_mode.svg")
        path.write_text(build(theme, {"account_age": "—"}), encoding="utf-8")
        print(f"wrote {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
