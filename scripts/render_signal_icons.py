#!/usr/bin/env python3
"""Render a text-free animated icon rail for the visual-only README."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "portrait"
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = {
    "dark": {"bg": "#03050D", "panel": "#07101F", "line": "#153457", "cyan": "#258BFF", "violet": "#605DFF", "magenta": "#FF3158", "green": "#2DE2E6"},
    "light": {"bg": "#F4F7FC", "panel": "#FBFDFF", "line": "#A5B9D2", "cyan": "#005CFF", "violet": "#4D37DA", "magenta": "#D51F4A", "green": "#007E8A"},
}


def render(theme: str) -> str:
    p = PALETTES[theme]
    symbols = []
    for index in range(8):
        x = 30 + index * 146
        accent = (p["cyan"], p["violet"], p["magenta"], p["green"])[index % 4]
        # Each icon is a compact geometry glyph, not text.
        if index == 0:  # radar / recon
            glyph = f'<circle cx="{x+45}" cy="84" r="22" fill="none" stroke="{accent}" stroke-width="2"/><path d="M{x+45} 84L{x+64} 64M{x+45} 52V116M{x+13} 84H{x+77}" stroke="{accent}" stroke-width="2"/><circle cx="{x+64}" cy="64" r="5" fill="{accent}"/>'
        elif index == 1:  # route
            glyph = f'<path d="M{x+14} 102C{x+28} 102 {x+25} 66 {x+43} 66S{x+57} 102 {x+75} 102" fill="none" stroke="{accent}" stroke-width="4"/><circle cx="{x+14}" cy="102" r="7" fill="{accent}"/><circle cx="{x+43}" cy="66" r="7" fill="{accent}"/><circle cx="{x+75}" cy="102" r="7" fill="{accent}"/>'
        elif index == 2:  # packet
            glyph = f'<path d="M{x+17} 63h28l15 15-15 15H17z" fill="none" stroke="{accent}" stroke-width="2" transform="translate({x} 0)"/><path d="M{x+29} 78h22M{x+40} 67v22" stroke="{accent}" stroke-width="2"/>'
        elif index == 3:  # automation
            glyph = f'<circle cx="{x+45}" cy="84" r="26" fill="none" stroke="{accent}" stroke-width="2" stroke-dasharray="3 8"/><circle cx="{x+45}" cy="84" r="8" fill="{accent}"/><path d="M{x+45} 46v18M{x+45} 104v18M{x+7} 84h18M{x+65} 84h18" stroke="{accent}" stroke-width="3"/>'
        elif index == 4:  # shield
            glyph = f'<path d="M{x+45} 48l28 12v23c0 20-13 30-28 37-15-7-28-17-28-37V60z" fill="none" stroke="{accent}" stroke-width="3"/><path d="M{x+30} 83l10 10 20-22" fill="none" stroke="{accent}" stroke-width="4"/>'
        elif index == 5:  # waveform
            glyph = f'<path d="M{x+10} 86h12l8-22 10 42 10-38 8 18h18" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        elif index == 6:  # terminal cursor
            glyph = f'<rect x="{x+17}" y="55" width="56" height="58" rx="7" fill="none" stroke="{accent}" stroke-width="2"/><path d="M{x+30} 75l12 10-12 10M{x+50} 98h14" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>'
        else:  # star / experiment
            glyph = f'<path d="M{x+45} 47l9 25 26 1-20 16 7 25-22-14-22 14 7-25-20-16 26-1z" fill="none" stroke="{accent}" stroke-width="2"/>'
        symbols.append(f'''<g>
          <rect x="{x}" y="22" width="116" height="124" rx="18" fill="{p['panel']}" stroke="{p['line']}" stroke-width="2"/>
          <path d="M{x+18} 22h80" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
          {glyph}
          <circle cx="{x+96}" cy="42" r="3" fill="{accent}"><animate attributeName="opacity" values="0.15;1;0.15" dur="{2.2+(index%4)*0.37:.2f}s" begin="{index*0.13:.2f}s" repeatCount="indefinite"/></circle>
          <animateTransform attributeName="transform" type="translate" values="0 0;0 -3;0 0" dur="{4.8+(index%5)*0.31:.2f}s" begin="{index*0.12:.2f}s" repeatCount="indefinite"/>
        </g>''')
    raw = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="170" viewBox="0 0 1200 170" role="img" aria-label="Animated HazaVVIP signal icon rail, {theme} theme">
  <rect width="1200" height="170" rx="24" fill="{p['bg']}"/>
  <path d="M20 155H1180" stroke="{p['line']}" stroke-opacity="0.52" stroke-dasharray="2 12"><animate attributeName="stroke-dashoffset" from="0" to="-84" dur="3.5s" repeatCount="indefinite"/></path>
  {''.join(symbols)}
</svg>
'''
    return "\n".join(line.rstrip() for line in raw.splitlines()) + "\n"


for theme in ("dark", "light"):
    path = OUT / f"signal-icons-{theme}.svg"
    path.write_text(render(theme))
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
