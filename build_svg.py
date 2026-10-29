"""Generate the light/dark profile cards (neofetch layout + ASCII portrait).

Single source of truth: edit CONTENT / ROWS / palette here, run
`python build_svg.py`, commit both SVGs. Live values are element ids that
today.py rewrites, so this file is only for design changes.

Layout: block-art portrait left (with a vertical rule separating it from the
data), dot-leader key/value rows right, dashed section rules, quote footer.
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
        "portrait": ("#182533", "#2b4459", "#3f6484", "#5e8cb5", "#8fbde2", "#d3e9fb"),
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
        "portrait": ("#e8eef4", "#c6d4e2", "#9ab0c6", "#6a89a7", "#41608a", "#22395c"),
    },
}
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"

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
PORT_X, PORT_TOP = 60, 110
PORT_SIZE, PORT_LH = 10, 12.5
PORT_ADV = PORT_SIZE * 0.6
RIGHT_X, RIGHT_EDGE = 540, 1140
VALUE_X = RIGHT_EDGE
DIVIDER_X = 490
ROW_TOP, ROW_STEP = 120, 24
DOT_RESERVE = 128
FOOTER_RULE_Y = H - 88
FOOTER_TEXT_Y = H - 56


def load_portrait() -> dict:
    p = Path("ascii_portrait.json")
    return json.loads(p.read_text()) if p.exists() else {"cols": 0, "rows": 0, "shades": []}


def tw(s: str, size: float = 13) -> float:
    """Approximate monospace text width."""
    return len(s) * size * 0.6


def build(theme: str, values: dict[str, str]) -> str:
    p = PALETTES[theme]
    port = load_portrait()
    invert = True                      # both: ink mapping (dark pixels = dense glyphs)
    ramp = " .:oO@"
    shades = p["portrait"]
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
        6%   {{ opacity: .22; }}
        58%  {{ opacity: .22; }}
        66%  {{ transform: translateY({port["rows"] * PORT_LH if port["rows"] else 360}px); opacity: 0; }}
        100% {{ transform: translateY({port["rows"] * PORT_LH if port["rows"] else 360}px); opacity: 0; }}
      }}
      @media (prefers-reduced-motion: reduce) {{ .blink, .pulse, .scan {{ animation: none; }} }}
    """)
    add("</style></defs>")

    # card
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

    # ── portrait ──────────────────────────────────────────────────────────
    if port["shades"]:
        add('<g id="portrait">')
        add(f'<rect class="scan" x="{PORT_X - 6}" y="{PORT_TOP - 4}" '
            f'width="{port["cols"] * PORT_ADV + 12:.0f}" height="2" '
            f'fill="{p["accent"]}" opacity="0"/>')
        for i, row in enumerate(port["shades"]):
            y = PORT_TOP + i * PORT_LH
            if all(v >= len(ramp) for v in row):
                continue
            add(f'<text x="{PORT_X}" y="{y:.1f}" font-size="{PORT_SIZE}" xml:space="preserve">')
            run_char, run_glyph, run_start = None, None, 0
            for x_idx, lum in enumerate(row):
                if lum >= len(ramp):          # paper sentinel -> blank, both themes
                    glyph, char = 0, " "
                else:
                    glyph = (len(ramp) - 1) - lum
                    char = ramp[glyph]
                if run_char is None:
                    run_char, run_glyph, run_start = char, glyph, x_idx
                elif glyph != run_glyph:
                    add(f'<tspan fill="{shades[run_glyph]}">'
                        f'{escape(run_char * (x_idx - run_start))}</tspan>')
                    run_char, run_glyph, run_start = char, glyph, x_idx
            if run_char is not None:
                add(f'<tspan fill="{shades[run_glyph]}">'
                    f'{escape(run_char * (len(row) - run_start))}</tspan>')
            add("</text>")
        add("</g>")

    # vertical rule between portrait and data
    add(f'<line x1="{DIVIDER_X}" y1="104" x2="{DIVIDER_X}" y2="{PORT_TOP + (port["rows"] * PORT_LH if port["rows"] else 360) + 6:.0f}" '
        f'stroke="{p["border"]}" stroke-width="1"/>')

    # caption under portrait
    cap_y = PORT_TOP + (port["rows"] * PORT_LH if port["rows"] else 360) + 26
    add(f'<text x="{PORT_X}" y="{cap_y:.0f}" font-size="11" fill="{p["muted"]}">'
        f'nikabdulaqmal@gmail.com</text>')
    add(f'<text x="{PORT_X}" y="{cap_y + 18:.0f}" font-size="11" fill="{p["muted"]}">'
        f'github.com/nickaqmal02</text>')

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

    # added / deleted sub-line, right aligned under LINES
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
