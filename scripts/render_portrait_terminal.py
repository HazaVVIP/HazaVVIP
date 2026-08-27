#!/usr/bin/env python3
"""Render a personal per-pixel formation portrait as an animated SVG."""
from __future__ import annotations

import json
import random
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
POINTS = ROOT / "data" / "portrait_points.json"
OUT = ROOT / "assets" / "portrait"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 820
PORTRAIT_X, PORTRAIT_Y, PORTRAIT_W, PORTRAIT_H = 44, 134, 440, 636

PALETTES = {
    "dark": {
        "bg": "#03050D", "window": "#07101F", "panel": "#040912", "ink": "#F6F8FF",
        "muted": "#6D86A7", "line": "#153457", "cyan": "#258BFF", "violet": "#605DFF",
        "magenta": "#FF3158", "green": "#2DE2E6", "amber": "#FFB74A"
    },
    "light": {
        "bg": "#F4F7FC", "window": "#FBFDFF", "panel": "#EFF4FA", "ink": "#0D1A2B",
        "muted": "#54708D", "line": "#A5B9D2", "cyan": "#005CFF", "violet": "#4D37DA",
        "magenta": "#D51F4A", "green": "#007E8A", "amber": "#AA5A00"
    },
}
COLOR_MAP = {"violet": "violet", "cyan": "cyan", "rose": "magenta"}


def esc(value: object) -> str:
    return escape(str(value))


def f(value: float) -> str:
    return f"{value:.2f}"


def choose_points(raw: list[dict]) -> list[dict]:
    """Keep a strong silhouette while making a manageable per-pixel SVG."""
    core = [p for p in raw if not p.get("edge")]
    edge = [p for p in raw if p.get("edge")]
    # Core samples are spatially regular and edge samples are sparse by design.
    selected: list[dict] = []
    for index, point in enumerate(core):
        if index % 2 == 0 or float(point["ink"]) > 0.62:
            selected.append(point)
    selected.extend(point for index, point in enumerate(edge) if index % 2 == 0)
    return selected


def defs(theme: str, p: dict) -> str:
    prefix = f"px-{theme}"
    return f'''<defs>
  <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['bg']}"/><stop offset="1" stop-color="{p['panel']}"/>
  </linearGradient>
  <linearGradient id="{prefix}-edge" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['cyan']}"/><stop offset="0.52" stop-color="{p['violet']}"/><stop offset="1" stop-color="{p['cyan']}"/>
    <animate attributeName="x1" values="0;0.85;0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="{prefix}-signal" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{p['cyan']}"/><stop offset="0.42" stop-color="{p['violet']}"/><stop offset="0.72" stop-color="{p['magenta']}"/><stop offset="1" stop-color="{p['green']}"/>
    <animate attributeName="x1" values="0;1;0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <pattern id="{prefix}-grid" width="26" height="26" patternUnits="userSpaceOnUse">
    <path d="M26 0H0V26" fill="none" stroke="{p['line']}" stroke-opacity="0.20"/>
  </pattern>
  <filter id="{prefix}-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="{prefix}-portrait-clip"><rect x="{PORTRAIT_X+8}" y="{PORTRAIT_Y+8}" width="{PORTRAIT_W-16}" height="{PORTRAIT_H-16}" rx="4"/></clipPath>
</defs>'''


def chrome(p: dict, prefix: str) -> str:
    return f'''
    <rect x="22" y="22" width="{W-44}" height="{H-44}" rx="24" fill="url(#{prefix}-bg)" stroke="url(#{prefix}-edge)" stroke-width="2"/>
    <rect x="23" y="23" width="{W-46}" height="{H-46}" rx="23" fill="url(#{prefix}-grid)" opacity="0.36"/>
    <rect x="42" y="44" width="{W-84}" height="50" rx="13" fill="{p['window']}" stroke="{p['line']}" stroke-opacity="0.72"/>
    <circle cx="68" cy="69" r="6" fill="#FF6B85"/><circle cx="89" cy="69" r="6" fill="#FFC76A"/><circle cx="110" cy="69" r="6" fill="{p['green']}"/>
    <path d="M140 69h108 M270 69h42 M334 69h130" stroke="{p['line']}" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 10" opacity="0.8">
      <animate attributeName="stroke-dashoffset" from="0" to="-72" dur="3s" repeatCount="indefinite"/>
    </path>
    <circle cx="1180" cy="69" r="5" fill="{p['green']}" filter="url(#{prefix}-glow)">
      <animate attributeName="r" values="3;7;3" dur="2.2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.55;1;0.55" dur="2.2s" repeatCount="indefinite"/>
    </circle>
    <path d="M52 112H1228" stroke="{p['line']}" stroke-opacity="0.64"/>
    <path d="M52 112h56 M1216 112h12" stroke="{p['cyan']}" stroke-width="2"/>
    '''


def pixel_groups(points: list[dict], p: dict, prefix: str) -> tuple[str, int]:
    rng = random.Random(2727)
    groups: list[str] = []
    portrait_inner_x = PORTRAIT_X + 14
    portrait_inner_y = PORTRAIT_Y + 14
    portrait_inner_w = PORTRAIT_W - 28
    portrait_inner_h = PORTRAIT_H - 28
    for index, point in enumerate(points):
        x = portrait_inner_x + float(point["x"]) * portrait_inner_w
        y = portrait_inner_y + float(point["y"]) * portrait_inner_h
        size = float(point["size"])
        color = p[COLOR_MAP[str(point["color"])]]
        # Each pixel begins displaced, then converges into the portrait and drifts.
        dx = rng.randrange(-42, 43)
        dy = rng.randrange(-34, 35)
        drift_x = rng.choice((-1, 1)) * rng.randrange(2, 11)
        drift_y = rng.choice((-1, 1)) * rng.randrange(1, 7)
        start = 0.08 + (index % 58) * 0.025
        dur = 10.8 + (index % 9) * 0.34
        key_times = "0;.13;.24;.56;.78;1"
        values = f"translate({dx} {dy});translate({dx} {dy});translate(0 0);translate({drift_x} {drift_y});translate(0 0);translate({dx} {dy})"
        opacity = 0.42 + min(0.50, float(point["ink"]) * 0.62)
        extra = ""
        if index % 3 == 0:
            extra = f'<animate attributeName="opacity" values="0;{opacity:.2f};{opacity:.2f};0.25;{opacity:.2f}" dur="{7.0+(index%7)*0.31:.2f}s" begin="{start+1.8:.2f}s" repeatCount="indefinite"/>'
        groups.append(f'''<g opacity="{opacity:.2f}">
          <animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{key_times}" dur="{dur:.2f}s" begin="{start:.2f}s" repeatCount="indefinite"/>
          {extra}
          <path d="M{f(x)} {f(y)}h{f(size)}v{f(size)}h-{f(size)}z" fill="{color}"/>
        </g>''')
    return "".join(groups), len(points)


def portrait_scene(points: list[dict], p: dict, prefix: str) -> tuple[str, int]:
    pixels, count = pixel_groups(points, p, prefix)
    return f'''
    <rect x="{PORTRAIT_X}" y="{PORTRAIT_Y}" width="{PORTRAIT_W}" height="{PORTRAIT_H}" rx="8" fill="{p['panel']}" stroke="{p['cyan']}" stroke-opacity="0.86" stroke-width="2"/>
    <path d="M{PORTRAIT_X} {PORTRAIT_Y+26}h30 M{PORTRAIT_X} {PORTRAIT_Y+26}v30 M{PORTRAIT_X+PORTRAIT_W} {PORTRAIT_Y+PORTRAIT_H-26}h-30 M{PORTRAIT_X+PORTRAIT_W} {PORTRAIT_Y+PORTRAIT_H-26}v-30" fill="none" stroke="{p['cyan']}" stroke-width="2"/>
    <g clip-path="url(#{prefix}-portrait-clip)">
      <rect x="{PORTRAIT_X+8}" y="{PORTRAIT_Y+8}" width="{PORTRAIT_W-16}" height="{PORTRAIT_H-16}" fill="{p['panel']}"/>
      {pixels}
      <g opacity="0.22">
        <path d="M{PORTRAIT_X+10} {PORTRAIT_Y+120}H{PORTRAIT_X+PORTRAIT_W-10} M{PORTRAIT_X+10} {PORTRAIT_Y+292}H{PORTRAIT_X+PORTRAIT_W-10} M{PORTRAIT_X+10} {PORTRAIT_Y+464}H{PORTRAIT_X+PORTRAIT_W-10}" stroke="{p['cyan']}" stroke-width="1" stroke-dasharray="1 12">
          <animate attributeName="stroke-dashoffset" from="0" to="-80" dur="3.8s" repeatCount="indefinite"/>
        </path>
      </g>
    </g>
    <path d="M{PORTRAIT_X+PORTRAIT_W+26} {PORTRAIT_Y+58}h64 M{PORTRAIT_X+PORTRAIT_W+26} {PORTRAIT_Y+70}h38 M{PORTRAIT_X+PORTRAIT_W+26} {PORTRAIT_Y+82}h82" stroke="{p['line']}" stroke-width="2" stroke-linecap="round" stroke-dasharray="2 7"/>
    ''', count


def right_visual(p: dict, prefix: str) -> str:
    rng = random.Random(9191)
    pieces: list[str] = []
    # Orbiting rings provide a second focal system without static prose.
    pieces.append(f'''<g transform="translate(880 314)">
      <circle r="118" fill="none" stroke="{p['line']}" stroke-opacity="0.55" stroke-dasharray="3 13"/>
      <circle r="82" fill="none" stroke="{p['violet']}" stroke-opacity="0.62" stroke-dasharray="1 9">
        <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/>
      </circle>
      <circle r="45" fill="none" stroke="{p['cyan']}" stroke-opacity="0.72"/>
      <circle r="11" fill="{p['cyan']}" filter="url(#{prefix}-glow)"><animate attributeName="r" values="8;15;8" dur="2.6s" repeatCount="indefinite"/></circle>
      <path d="M-150 0H150 M0 -150V150" stroke="{p['line']}" stroke-opacity="0.42" stroke-dasharray="2 11"/>
      <circle cx="0" cy="-118" r="7" fill="{p['magenta']}"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/></circle>
    </g>''')
    # A moving wave and signal bars make the right side feel instrument-like.
    wave = "M594 535 C 650 495, 686 574, 742 535 S 832 495, 888 535 S 978 574, 1034 535 S 1122 495, 1180 535"
    pieces.append(f'''<path d="{wave}" fill="none" stroke="url(#{prefix}-signal)" stroke-width="4" stroke-linecap="round"/>
      <path d="{wave}" fill="none" stroke="{p['cyan']}" stroke-opacity="0.55" stroke-width="1" stroke-dasharray="2 12"><animate attributeName="stroke-dashoffset" from="0" to="-96" dur="3.2s" repeatCount="indefinite"/></path>''')
    for i in range(14):
        x = 594 + i * 44
        height = 18 + rng.randrange(8, 70)
        y = 690 - height
        color = p["cyan"] if i % 4 == 0 else p["violet"] if i % 4 == 1 else p["magenta"] if i % 4 == 2 else p["green"]
        pieces.append(f'''<rect x="{x}" y="{y}" width="18" height="{height}" rx="3" fill="{color}" opacity="0.52">
          <animate attributeName="height" values="{height};{max(8,height-26)};{height}" dur="{2.8+(i%5)*0.33:.2f}s" begin="{(i%7)*0.18:.2f}s" repeatCount="indefinite"/>
          <animate attributeName="y" values="{y};{y+26};{y}" dur="{2.8+(i%5)*0.33:.2f}s" begin="{(i%7)*0.18:.2f}s" repeatCount="indefinite"/>
        </rect>''')
    # Decorative node rail and corner glyphs.
    for i in range(8):
        x = 584 + i * 86
        pieces.append(f'<circle cx="{x}" cy="612" r="{3+i%3}" fill="{p["cyan"] if i%2==0 else p["violet"]}" opacity="0.72"><animate attributeName="opacity" values="0.25;1;0.25" dur="{2.5+(i%4)*0.3:.2f}s" begin="{(i%6)*0.21:.2f}s" repeatCount="indefinite"/></circle>')
    pieces.append(f'''<path d="M566 178h36v18 M566 178v36 M1194 178h-36v18 M1194 178v36 M566 646h36v-18 M566 646v-36 M1194 646h-36v-18 M1194 646v-36" fill="none" stroke="{p['cyan']}" stroke-width="2" stroke-opacity="0.82"/>''')
    return "".join(pieces)


def render(theme: str, points: list[dict]) -> tuple[str, int]:
    p = PALETTES[theme]
    prefix = f"px-{theme}"
    portrait, count = portrait_scene(points, p, prefix)
    raw = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="HazaVVIP per-pixel animated portrait signal, {theme} theme">
  {defs(theme, p)}
  <rect width="{W}" height="{H}" fill="{p['bg']}"/>
  {chrome(p, prefix)}
  {portrait}
  {right_visual(p, prefix)}
  <path d="M52 774H1228" stroke="{p['line']}" stroke-opacity="0.55"/>
  <circle cx="52" cy="774" r="3" fill="{p['cyan']}"/><circle cx="1228" cy="774" r="3" fill="{p['violet']}"/>
</svg>
'''
    return "\n".join(line.rstrip() for line in raw.splitlines()) + "\n", count


def main() -> None:
    payload = json.loads(POINTS.read_text())
    points = choose_points(payload["points"])
    print(f"selected {len(points)} animated pixels from {len(payload['points'])} source points")
    for theme in ("dark", "light"):
        svg, count = render(theme, points)
        path = OUT / f"portrait-terminal-{theme}.svg"
        path.write_text(svg)
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes, pixels={count})")


if __name__ == "__main__":
    main()
