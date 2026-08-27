#!/usr/bin/env python3
"""Render a personal halftone portrait inside a terminal-style SVG scene."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
POINTS = ROOT / "data" / "portrait_points.json"
OUT = ROOT / "assets" / "portrait"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 820
PORTRAIT_X, PORTRAIT_Y, PORTRAIT_W, PORTRAIT_H = 44, 152, 430, 606

PALETTES = {
    "dark": {
        "bg": "#050816", "window": "#0A1023", "panel": "#070C19", "ink": "#F2F8FF",
        "muted": "#7891A8", "line": "#284766", "cyan": "#47E6F2", "violet": "#9C6CFF",
        "magenta": "#F27DE2", "green": "#56E7AF", "amber": "#FFC76A", "white": "#FFFFFF"
    },
    "light": {
        "bg": "#F4FAFC", "window": "#F9FEFF", "panel": "#F1F8FA", "ink": "#172A3A",
        "muted": "#5B788A", "line": "#9CC5D0", "cyan": "#008EA4", "violet": "#7045D2",
        "magenta": "#BE3DAA", "green": "#00896E", "amber": "#A45F00", "white": "#FFFFFF"
    },
}
COLOR_MAP = {"violet": "violet", "cyan": "cyan", "rose": "magenta"}


def esc(value: object) -> str:
    return escape(str(value))


def fmt(value: float) -> str:
    return f"{value:.2f}"


def path_for_points(points: list[dict], color_key: str, x0: float, y0: float, w: float, h: float) -> str:
    chunks: list[str] = []
    for p in points:
        if p["color"] != color_key or p.get("edge"):
            continue
        x = x0 + float(p["x"]) * w
        y = y0 + float(p["y"]) * h
        s = float(p["size"])
        chunks.append(f"M{fmt(x)} {fmt(y)}h{fmt(s)}v{fmt(s)}h-{fmt(s)}z")
    return "".join(chunks)


def edge_path(points: list[dict], x0: float, y0: float, w: float, h: float) -> str:
    chunks: list[str] = []
    for p in points:
        if not p.get("edge"):
            continue
        x = x0 + float(p["x"]) * w
        y = y0 + float(p["y"]) * h
        s = float(p["size"])
        chunks.append(f"M{fmt(x)} {fmt(y)}h{fmt(s)}v{fmt(s)}h-{fmt(s)}z")
    return "".join(chunks)


def defs(theme: str, p: dict) -> str:
    prefix = f"pt-{theme}"
    return f'''<defs>
  <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['bg']}"/><stop offset="1" stop-color="{p['panel']}"/>
  </linearGradient>
  <linearGradient id="{prefix}-edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['cyan']}"/><stop offset="0.55" stop-color="{p['violet']}"/><stop offset="1" stop-color="{p['cyan']}"/>
    <animate attributeName="x1" values="0;0.8;0" dur="11s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="{prefix}-data" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['cyan']}"/><stop offset="0.45" stop-color="{p['violet']}"/><stop offset="0.72" stop-color="{p['magenta']}"/><stop offset="1" stop-color="{p['green']}"/>
    <animate attributeName="x1" values="0;1;0" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="{prefix}-portrait" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['violet']}"/><stop offset="0.48" stop-color="{p['magenta']}"/><stop offset="1" stop-color="{p['cyan']}"/>
  </linearGradient>
  <pattern id="{prefix}-grid" width="26" height="26" patternUnits="userSpaceOnUse">
    <path d="M26 0H0V26" fill="none" stroke="{p['line']}" stroke-opacity="0.22"/>
  </pattern>
  <filter id="{prefix}-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="{prefix}-portrait-clip"><rect x="{PORTRAIT_X+8}" y="{PORTRAIT_Y+8}" width="{PORTRAIT_W-16}" height="{PORTRAIT_H-16}" rx="4"/></clipPath>
</defs>'''


def header(p: dict, prefix: str, theme: str) -> str:
    return f'''
    <rect x="22" y="22" width="{W-44}" height="{H-44}" rx="24" fill="url(#{prefix}-bg)" stroke="url(#{prefix}-edge)" stroke-width="2"/>
    <rect x="23" y="23" width="{W-46}" height="{H-46}" rx="23" fill="url(#{prefix}-grid)" opacity="0.38"/>
    <rect x="42" y="44" width="{W-84}" height="54" rx="13" fill="{p['window']}" stroke="{p['line']}" stroke-opacity="0.72"/>
    <circle cx="68" cy="71" r="6" fill="#FF6B85"/><circle cx="89" cy="71" r="6" fill="#FFC76A"/><circle cx="110" cy="71" r="6" fill="{p['green']}"/>
    <text x="136" y="76" fill="{p['ink']}" font-family="sans-serif" font-size="15" font-weight="700" letter-spacing="2">hazavvip.profile.sh —live</text>
    <text x="1200" y="76" text-anchor="end" fill="{p['green']}" font-family="sans-serif" font-size="12" font-weight="700" letter-spacing="2">● SIGNAL ONLINE</text>
    <text x="54" y="116" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="3">VISUAL.MAP / PERSONAL IDENTITY LAYER</text>
    <text x="1225" y="116" text-anchor="end" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="2">{theme.upper()} / PORTRAIT ENGINE</text>
    '''


def portrait_scene(points: list[dict], p: dict, prefix: str) -> str:
    paths = []
    for key in ("violet", "rose", "cyan"):
        d = path_for_points(points, key, PORTRAIT_X + 14, PORTRAIT_Y + 14, PORTRAIT_W - 28, PORTRAIT_H - 28)
        color = p[COLOR_MAP[key]]
        paths.append(f'<path d="{d}" fill="{color}" opacity="0.86"/>')
    edge = edge_path(points, PORTRAIT_X + 14, PORTRAIT_Y + 14, PORTRAIT_W - 28, PORTRAIT_H - 28)
    # Deterministic horizontal fragment bands create the living scan/glitch behavior.
    rng = random.Random(1412)
    bands = []
    for i in range(48):
        y = PORTRAIT_Y + 20 + i * 11.6
        width = 250 + rng.randrange(0, 190)
        x = PORTRAIT_X + 15 + rng.randrange(0, 90)
        color = p["cyan"] if i % 3 == 0 else p["violet"] if i % 3 == 1 else p["magenta"]
        delay = (i % 12) * 0.17
        bands.append(f'''<rect x="{x}" y="{y:.1f}" width="{width}" height="{1 + i%3}" fill="{color}" opacity="0.12">
          <animate attributeName="x" values="{x};{x+18+rng.randrange(0,30)};{x}" dur="{4.2 + (i%5)*0.35:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.04;0.28;0.06" dur="{3.0 + (i%4)*0.45:.2f}s" begin="{delay:.2f}s" repeatCount="indefinite"/>
        </rect>''')
    fragments = []
    for i in range(34):
        x = PORTRAIT_X + 22 + rng.randrange(0, PORTRAIT_W - 44)
        y = PORTRAIT_Y + 25 + rng.randrange(0, PORTRAIT_H - 50)
        w = 8 + rng.randrange(2, 32)
        color = p["cyan"] if i % 2 == 0 else p["magenta"]
        fragments.append(f'''<path d="M{x} {y}h{w}v1h-{w}z" fill="{color}" opacity="0.18">
          <animateTransform attributeName="transform" type="translate" values="0 0;{(-1 if i%2 else 1)*(8+i%7)} {(-4+i%5)};0 0" dur="{5.2+(i%6)*0.31:.2f}s" begin="{(i%9)*0.23:.2f}s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.04;0.42;0.08" dur="{4.4+(i%5)*0.4:.2f}s" begin="{(i%9)*0.23:.2f}s" repeatCount="indefinite"/>
        </path>''')
    return f'''
    <rect x="{PORTRAIT_X}" y="{PORTRAIT_Y}" width="{PORTRAIT_W}" height="{PORTRAIT_H}" rx="8" fill="{p['panel']}" stroke="{p['cyan']}" stroke-opacity="0.8" stroke-width="2"/>
    <path d="M{PORTRAIT_X} {PORTRAIT_Y+24}h28 M{PORTRAIT_X} {PORTRAIT_Y+24}v28 M{PORTRAIT_X+PORTRAIT_W} {PORTRAIT_Y+PORTRAIT_H-24}h-28 M{PORTRAIT_X+PORTRAIT_W} {PORTRAIT_Y+PORTRAIT_H-24}v-28" fill="none" stroke="{p['cyan']}" stroke-width="2"/>
    <g clip-path="url(#{prefix}-portrait-clip)">
      <rect x="{PORTRAIT_X+8}" y="{PORTRAIT_Y+8}" width="{PORTRAIT_W-16}" height="{PORTRAIT_H-16}" fill="{p['panel']}"/>
      {''.join(paths)}
      <path d="{edge}" fill="{p['cyan']}" opacity="0.48"/>
      {''.join(bands)}
      {''.join(fragments)}
      <rect x="{PORTRAIT_X+8}" y="{PORTRAIT_Y+8}" width="{PORTRAIT_W-16}" height="{PORTRAIT_H-16}" fill="none" stroke="{p['cyan']}" stroke-opacity="0.25" stroke-width="1"/>
    </g>
    <text x="{PORTRAIT_X+22}" y="{PORTRAIT_Y-16}" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="2">PORTRAIT / HALFTONE FIELD</text>
    <text x="{PORTRAIT_X+PORTRAIT_W-18}" y="{PORTRAIT_Y+PORTRAIT_H+22}" text-anchor="end" fill="{p['muted']}" font-family="sans-serif" font-size="9" letter-spacing="1.5">POINT CLOUD / 3:4 SOURCE</text>
    '''


def info_scene(p: dict) -> str:
    rows = [
        ("Subject", "HazaVVIP", p["cyan"]),
        ("Role", "Builder / open-source explorer", p["ink"]),
        ("Origin", "public work / private curiosity", p["violet"]),
        ("Status", "Building + Learning + Shipping", p["green"]),
        ("ToolChain", "Git · Python · Rust · C++ · PHP", p["ink"]),
        ("Core.Focus", "Recon / Packet / Automation", p["magenta"]),
        ("Core.Artifact", "GitRecon — surface mapper", p["cyan"]),
        ("Core.Signal", "hazler · haquests · MCP-Server", p["ink"]),
        ("Grid.GitHub", "@HazaVVIP", p["violet"]),
    ]
    parts = [f'<text x="526" y="183" fill="{p["cyan"]}" font-family="sans-serif" font-size="12" font-weight="700" letter-spacing="2">SYSTEM.INFO</text>', f'<text x="526" y="212" fill="{p["violet"]}" font-family="sans-serif" font-size="18" font-weight="700">HazaVVIP / REPOSITORY GENOME</text>']
    y = 254
    for i, (label, value, color) in enumerate(rows):
        parts.append(f'<text x="526" y="{y}" fill="{color}" font-family="sans-serif" font-size="12" letter-spacing="1.5">{esc(label)}</text>')
        parts.append(f'<path d="M646 {y-4} H 1182" stroke="{p["line"]}" stroke-opacity="0.34" stroke-dasharray="2 8"/>')
        parts.append(f'<text x="1184" y="{y}" text-anchor="end" fill="{p["ink"]}" font-family="sans-serif" font-size="12">{esc(value)}</text>')
        y += 38
    parts.append(f'<text x="526" y="610" fill="{p["muted"]}" font-family="sans-serif" font-size="11" letter-spacing="1.3">&gt; More about me &amp; projects below in README <tspan fill="{p["cyan"]}">▮</tspan></text>')
    parts.append(f'<rect x="526" y="654" width="670" height="64" rx="9" fill="{p["panel"]}" stroke="{p["line"]}" stroke-opacity="0.72"/>')
    parts.append(f'<text x="548" y="680" fill="{p["muted"]}" font-family="sans-serif" font-size="10" letter-spacing="2">LIVE TRANSMISSION</text>')
    parts.append(f'<path d="M548 697 C 610 675, 630 716, 692 695 S 770 679, 832 698 S 912 712, 970 690 S 1068 674, 1172 696" fill="none" stroke="url(#pt-data)" stroke-width="3"/>')
    parts.append(f'<path d="M548 697 C 610 675, 630 716, 692 695 S 770 679, 832 698 S 912 712, 970 690 S 1068 674, 1172 696" fill="none" stroke="{p["cyan"]}" stroke-opacity="0.42" stroke-width="1" stroke-dasharray="2 12"><animate attributeName="stroke-dashoffset" from="0" to="-84" dur="4s" repeatCount="indefinite"/></path>')
    return f'''<g>{''.join(parts)}
      <path d="M526 148 H1196" stroke="{p['line']}" stroke-opacity="0.62"/>
      <circle cx="1180" cy="179" r="4" fill="{p['green']}" filter="url(#pt-glow)"/>
      <text x="1196" y="183" text-anchor="end" fill="{p['green']}" font-family="sans-serif" font-size="11" letter-spacing="1.5">LIVE</text>
    </g>'''


def render(theme: str, points: list[dict]) -> str:
    p = PALETTES[theme]
    prefix = f"pt-{theme}"
    content = header(p, prefix, theme) + portrait_scene(points, p, prefix) + info_scene(p)
    raw = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="HazaVVIP animated halftone portrait terminal, {theme} theme">
  {defs(theme, p)}
  <rect width="{W}" height="{H}" fill="{p['bg']}"/>
  {content}
  <path d="M52 772 H1228" stroke="{p['line']}" stroke-opacity="0.55"/>
  <text x="54" y="797" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.7">HALFTONE / SCANLINE / GLITCH / IDENTITY SIGNAL</text>
  <text x="1226" y="797" text-anchor="end" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.7">HAZAVVIP.PROFILE.SH</text>
</svg>
'''
    return "\n".join(line.rstrip() for line in raw.splitlines()) + "\n"


def main() -> None:
    payload = json.loads(POINTS.read_text())
    points = payload["points"]
    for theme in ("dark", "light"):
        path = OUT / f"portrait-terminal-{theme}.svg"
        path.write_text(render(theme, points))
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
