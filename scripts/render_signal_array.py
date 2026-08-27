#!/usr/bin/env python3
"""Render a cinematic, data-driven Signal Array profile visual."""
from __future__ import annotations

import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile.config.json"
DATA_PATH = ROOT / "data" / "profile.json"
OUT_DIR = ROOT / "assets" / "generated"
FALLBACK_DIR = ROOT / "assets" / "fallback"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x: float, y: float, value: object, size: int, fill: str, weight: int = 400, anchor: str = "start", mono: bool = False, opacity: float = 1.0) -> str:
    family = "monospace" if mono else "sans-serif"
    return f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" font-family="{family}" font-size="{size}px" font-weight="{weight}" fill="{fill}" opacity="{opacity}">{esc(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, width: float = 1, opacity: float = 1.0, dash: str = "") -> str:
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{width:g}" opacity="{opacity:g}" stroke-dasharray="{dash}"/>'


def render(theme: str, config: dict, data: dict) -> str:
    p = config["palette"][theme]
    repos = [repo for repo in data.get("repositories", []) if repo.get("name") != data.get("username")]
    total_stars = sum(int(repo.get("stars", 0)) for repo in repos)
    updated = str(data.get("updated_at", "public signal"))[:10]
    out: list[str] = []

    # A fixed star field keeps previews deterministic and avoids noisy random output.
    stars = [(74, 132, 1), (126, 84, 2), (194, 174, 1), (267, 112, 1), (332, 64, 2), (396, 154, 1), (478, 92, 1), (548, 174, 2), (628, 86, 1), (711, 138, 1), (790, 72, 2), (874, 158, 1), (952, 98, 1), (1040, 150, 2), (1112, 82, 1), (90, 500, 1), (178, 565, 2), (256, 523, 1), (344, 592, 1), (502, 552, 2), (580, 612, 1), (672, 535, 1), (766, 594, 2), (862, 528, 1), (968, 580, 1), (1096, 540, 2)]

    out.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="720" viewBox="0 0 1180 720" role="img" aria-labelledby="title desc">
  <title id="title">{esc(data.get("name", "Aditya"))} — HazaVVIP Signal Array</title>
  <desc id="desc">A cinematic systems intelligence profile visual mapping HazaVVIP repositories into recon, packet, and automation signals.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{p["background"]}"/>
      <stop offset="0.52" stop-color="{p["panel"]}"/>
      <stop offset="1" stop-color="{p["panel_alt"]}"/>
    </linearGradient>
    <radialGradient id="core" cx="48%" cy="44%" r="66%">
      <stop offset="0" stop-color="{p["cyan"]}" stop-opacity=".95"/>
      <stop offset=".18" stop-color="{p["purple"]}" stop-opacity=".68"/>
      <stop offset=".52" stop-color="{p["panel_alt"]}" stop-opacity=".88"/>
      <stop offset="1" stop-color="{p["background"]}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{p["cyan"]}" stop-opacity="0"/>
      <stop offset=".45" stop-color="{p["cyan"]}" stop-opacity=".8"/>
      <stop offset="1" stop-color="{p["purple"]}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="signal" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{p["cyan"]}"/>
      <stop offset=".5" stop-color="{p["purple"]}"/>
      <stop offset="1" stop-color="{p["green"]}"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M 32 0 L 0 0 0 32" fill="none" stroke="{p["border"]}" stroke-width="1" opacity=".28"/>
    </pattern>
    <pattern id="fineGrid" width="8" height="8" patternUnits="userSpaceOnUse">
      <path d="M 8 0 L 0 0 0 8" fill="none" stroke="{p["cyan"]}" stroke-width=".5" opacity=".14"/>
    </pattern>
    <filter id="glow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="smallGlow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .breathe {{ animation: breathe 4s ease-in-out infinite; transform-origin: 440px 340px; }}
      .orbit {{ animation: orbit 18s linear infinite; transform-origin: 440px 340px; }}
      .scan {{ animation: scan 6s linear infinite; }}
      .blink {{ animation: blink 2.6s ease-in-out infinite; }}
      @keyframes breathe {{ 0%,100% {{ opacity:.55; }} 50% {{ opacity:1; }} }}
      @keyframes orbit {{ to {{ transform: rotate(360deg); }} }}
      @keyframes scan {{ 0% {{ transform: translateX(-500px); opacity:0; }} 20% {{ opacity:.5; }} 80% {{ opacity:.5; }} 100% {{ transform: translateX(920px); opacity:0; }} }}
      @keyframes blink {{ 0%,100% {{ opacity:.3; }} 50% {{ opacity:1; }} }}
    </style>
  </defs>
  <rect x="8" y="8" width="1164" height="704" rx="30" fill="url(#bg)" stroke="{p["border"]}" stroke-width="2"/>
  <rect x="9" y="9" width="1162" height="702" rx="29" fill="url(#grid)" opacity=".52"/>
  <rect x="9" y="9" width="1162" height="702" rx="29" fill="url(#fineGrid)" opacity=".28"/>
''')

    # Stars and edge coordinates
    for sx, sy, radius in stars:
        out.append(f'  <circle class="blink" cx="{sx}" cy="{sy}" r="{radius}" fill="{p["text"]}" opacity=".34"/>\n')
    out.append(f'''  {text(42, 44, "SIGNAL ARRAY / 001", 11, p["cyan"], 700, mono=True)}
  {text(1138, 44, "LAT 06.20 · LONG 106.82 · UTC+7", 10, p["muted"], 600, "end", mono=True)}
  {line(42, 61, 1138, 61, p["border"], 1, .7)}
  {text(42, 94, "HazaVVIP", 34, p["text"], 800)}
  {text(42, 118, "SYSTEMS INTELLIGENCE LAB", 12, p["purple"], 700, mono=True)}
  {text(1138, 96, "PUBLIC SIGNAL / LIVE", 11, p["green"], 700, "end", mono=True)}
  <circle class="blink" cx="1114" cy="92" r="5" fill="{p["green"]}" filter="url(#smallGlow)"/>
''')

    # Left vertical mission rail
    out.append(f'''  <path d="M 42 155 V 634" stroke="{p["border"]}" stroke-width="1"/>
  <path d="M 42 155 V 242" stroke="{p["cyan"]}" stroke-width="3"/>
  {text(27, 634, "M I S S I O N", 10, p["muted"], 700, "middle", mono=True)}
  <g transform="translate(18 300) rotate(-90)">
    {text(0, 0, "DISCOVER · INSPECT · CONNECT · SHIP", 10, p["muted"], 600, mono=True)}
  </g>
''')

    # Central orb and orbit system
    cx, cy = 440, 348
    out.append(f'''  <circle cx="{cx}" cy="{cy}" r="206" fill="url(#core)" opacity=".42"/>
  <circle class="breathe" cx="{cx}" cy="{cy}" r="156" fill="none" stroke="{p["cyan"]}" stroke-width="1" stroke-opacity=".28"/>
  <circle cx="{cx}" cy="{cy}" r="122" fill="none" stroke="{p["purple"]}" stroke-width="1" stroke-opacity=".35" stroke-dasharray="2 10"/>
  <ellipse class="orbit" cx="{cx}" cy="{cy}" rx="196" ry="72" fill="none" stroke="{p["cyan"]}" stroke-width="1" stroke-opacity=".42" stroke-dasharray="8 13"/>
  <ellipse class="orbit" cx="{cx}" cy="{cy}" rx="72" ry="196" fill="none" stroke="{p["purple"]}" stroke-width="1" stroke-opacity=".28" stroke-dasharray="4 16"/>
  <circle cx="{cx}" cy="{cy}" r="92" fill="url(#core)" stroke="{p["cyan"]}" stroke-opacity=".8" stroke-width="2" filter="url(#glow)"/>
  <circle cx="{cx}" cy="{cy}" r="76" fill="none" stroke="{p["text"]}" stroke-opacity=".2" stroke-width="1"/>
  <path class="scan" d="M 314 348 H 566" stroke="url(#beam)" stroke-width="2"/>
  {text(cx, cy - 12, "HAZA", 25, p["text"], 800, "middle", mono=True)}
  {text(cx, cy + 16, "CORE / ONLINE", 11, p["cyan"], 700, "middle", mono=True)}
  {text(cx, cy + 40, "signal acquired", 9, p["muted"], 600, "middle", mono=True)}
''')

    # Ray lines and nodes
    nodes = [
        (242, 228, "RECON", "discover / map", p["cyan"], "01"),
        (644, 214, "PACKET", "inspect / craft", p["purple"], "02"),
        (704, 458, "AUTOMATION", "connect / ship", p["green"], "03"),
        (236, 488, "EXPERIMENTS", "test / learn", p["amber"], "04"),
    ]
    for nx, ny, label, sub, color, index in nodes:
        out.append(f'''  <path d="M {cx} {cy} L {nx} {ny}" fill="none" stroke="{color}" stroke-width="1" stroke-opacity=".46" stroke-dasharray="4 9"/>
  <circle class="breathe" cx="{nx}" cy="{ny}" r="24" fill="{p["panel"]}" stroke="{color}" stroke-width="2"/>
  <circle cx="{nx}" cy="{ny}" r="8" fill="{color}" opacity=".16" filter="url(#smallGlow)"/>
  {text(nx, ny + 4, index, 9, color, 800, "middle", mono=True)}
  {text(nx, ny + 44, label, 11, color, 800, "middle", mono=True)}
  {text(nx, ny + 59, sub, 9, p["muted"], 500, "middle", mono=True)}
''')

    # Right transmission log with depth and artifact strips
    out.append(f'''  <path d="M 808 148 H 1138" stroke="{p["border"]}" stroke-width="1"/>
  {text(808, 142, "TRANSMISSION LOG", 11, p["amber"], 800, mono=True)}
  {text(1138, 142, "3 ARTIFACTS", 9, p["muted"], 600, "end", mono=True)}
''')
    artifact_repos = repos[:3]
    artifact_colors = [p["cyan"], p["purple"], p["green"]]
    for idx in range(3):
        y = 178 + idx * 112
        repo = artifact_repos[idx] if idx < len(artifact_repos) else {"name": "awaiting-signal", "description": "next artifact", "language": "Other", "stars": 0}
        color = artifact_colors[idx]
        name = str(repo.get("name", "artifact"))[:18]
        desc = str(repo.get("description", "public artifact"))[:27]
        language = str(repo.get("language", "Other"))[:10]
        stars = int(repo.get("stars", 0))
        out.append(f'''  <g transform="translate({idx * 9} {idx * 3})">
    <rect x="808" y="{y}" width="330" height="86" rx="14" fill="{p["panel"]}" fill-opacity=".86" stroke="{color}" stroke-opacity=".48"/>
    <rect x="808" y="{y}" width="6" height="86" rx="3" fill="{color}"/>
    {text(830, y + 23, f"ARTIFACT / 0{idx + 1}", 9, color, 700, mono=True)}
    {text(830, y + 48, name, 17, p["text"], 800, mono=True)}
    {text(830, y + 67, desc, 10, p["muted"], 500, mono=True)}
    {text(1114, y + 23, language, 9, p["muted"], 700, "end", mono=True)}
    {text(1114, y + 68, f"★ {stars}", 10, color, 700, "end", mono=True)}
    <path d="M 830 {y + 76} H 920" stroke="{color}" stroke-width="2" stroke-opacity=".34"/>
    <path d="M 930 {y + 76} H 1000" stroke="{p["border"]}" stroke-width="2"/>
  </g>
''')

    # Lower signal strip
    out.append(f'''  <path d="M 92 606 H 1088" stroke="{p["border"]}" stroke-width="1"/>
  {text(92, 596, "ACTIVITY / SIGNAL DENSITY", 10, p["green"], 700, mono=True)}
  {text(1088, 596, f"SNAPSHOT {updated}", 9, p["muted"], 600, "end", mono=True)}
  <path d="M 92 640 C 140 612 160 666 205 640 S 274 616 315 642 S 384 676 427 633 S 500 604 544 640 S 613 675 659 634 S 736 608 780 640 S 852 670 896 630 S 970 610 1018 641 S 1060 657 1088 632" fill="none" stroke="url(#signal)" stroke-width="3" stroke-linecap="round" filter="url(#smallGlow)"/>
  <path d="M 92 640 C 140 612 160 666 205 640 S 274 616 315 642 S 384 676 427 633 S 500 604 544 640 S 613 675 659 634 S 736 608 780 640 S 852 670 896 630 S 970 610 1018 641 S 1060 657 1088 632" fill="none" stroke="{p["text"]}" stroke-opacity=".22" stroke-width="1"/>
  {text(92, 675, f"REPOSITORIES {len(repos):02d}", 10, p["muted"], 700, mono=True)}
  {text(268, 675, f"STARS {total_stars:02d}", 10, p["muted"], 700, mono=True)}
  {text(408, 675, f"FOLLOWERS {int(data.get('followers', 0)):02d}", 10, p["muted"], 700, mono=True)}
  {text(1088, 675, "END OF TRANSMISSION // BUILD IN PUBLIC", 10, p["cyan"], 700, "end", mono=True)}
</svg>
''')
    return "".join(out)


def main() -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FALLBACK_DIR.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        rendered = render(theme, config, data)
        (OUT_DIR / f"signal-array-{theme}.svg").write_text(rendered, encoding="utf-8")
        (FALLBACK_DIR / f"signal-array-{theme}.svg").write_text(rendered, encoding="utf-8")
    print("Rendered Signal Array light/dark assets")


if __name__ == "__main__":
    main()
