#!/usr/bin/env python3
"""Render the HazaVVIP Repository Genome scene.

This is a deterministic, data-driven SVG renderer. It treats repositories as
signals in one organism instead of rendering them as equal-sized cards.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "data" / "repository_genome.json"
LIVE = ROOT / "data" / "profile.json"
OUT = ROOT / "assets" / "genome"
OUT.mkdir(parents=True, exist_ok=True)

PALETTES = {
    "dark": {
        "bg": "#030711", "bg2": "#0A1630", "field": "#07162A", "ink": "#EAFBFF",
        "muted": "#7395AD", "grid": "#77A6BD", "cyan": "#62EEFF", "violet": "#A88BFF",
        "mint": "#66F2BE", "amber": "#FFC46D", "rose": "#FF7B9B", "black": "#02040B",
        "accent": "#C5FAFF", "edge": "#6EA1BA"
    },
    "light": {
        "bg": "#F4FBFC", "bg2": "#DCEEF4", "field": "#E9F6F8", "ink": "#092032",
        "muted": "#4E7182", "grid": "#4D94A8", "cyan": "#007F9D", "violet": "#6946C6",
        "mint": "#008C70", "amber": "#A85C00", "rose": "#B52D55", "black": "#F7FEFF",
        "accent": "#12364B", "edge": "#80BACA"
    },
}

DOMAIN_COLOR = {"RECON": "cyan", "PACKET": "violet", "AUTOMATION": "mint", "EXPERIMENTS": "amber"}
WIDE = (1480, 860)
MOBILE = (900, 1160)


def esc(value: object) -> str:
    return escape(str(value))


def polar_path(cx: float, cy: float, rx: float, ry: float, points: int, phase: float, wobble: float, close=True) -> str:
    out = []
    for i in range(points):
        a = math.tau * i / points
        wave = math.sin(a * 3 + phase) * wobble + math.sin(a * 7 - phase * 0.7) * wobble * 0.45
        x = cx + math.cos(a) * (rx + wave)
        y = cy + math.sin(a) * (ry + wave * 0.72)
        out.append((x, y))
    start = out[0]
    d = f"M {start[0]:.1f} {start[1]:.1f}"
    for i in range(1, len(out)):
        p = out[i]
        prev = out[i - 1]
        # Smooth-ish polygonal contour: many short segments creates organic precision.
        d += f" L {p[0]:.1f} {p[1]:.1f}"
    if close:
        d += " Z"
    return d


def curve(p0, p1, p2, p3) -> str:
    return f"M {p0[0]:.1f} {p0[1]:.1f} C {p1[0]:.1f} {p1[1]:.1f}, {p2[0]:.1f} {p2[1]:.1f}, {p3[0]:.1f} {p3[1]:.1f}"


def defs(theme: str, p: dict, prefix: str) -> str:
    return f"""<defs>
  <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['bg2']}"/>
    <stop offset="0.50" stop-color="{p['bg']}"/>
    <stop offset="1" stop-color="{p['field']}"/>
  </linearGradient>
  <radialGradient id="{prefix}-core" cx="45%" cy="42%" r="68%">
    <stop offset="0" stop-color="{p['cyan']}" stop-opacity="0.18"/>
    <stop offset="0.42" stop-color="{p['violet']}" stop-opacity="0.10"/>
    <stop offset="1" stop-color="{p['black']}" stop-opacity="0.96"/>
  </radialGradient>
  <linearGradient id="{prefix}-coreline" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['accent']}"/>
    <stop offset="0.32" stop-color="{p['cyan']}"/>
    <stop offset="0.70" stop-color="{p['violet']}"/>
    <stop offset="1" stop-color="{p['mint']}"/>
  </linearGradient>
  <linearGradient id="{prefix}-plate" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['field']}" stop-opacity="0.92"/>
    <stop offset="1" stop-color="{p['bg']}" stop-opacity="0.66"/>
  </linearGradient>
  <pattern id="{prefix}-grid" width="52" height="52" patternUnits="userSpaceOnUse">
    <path d="M 52 0 H 0 V 52" fill="none" stroke="{p['grid']}" stroke-opacity="0.12" stroke-width="1"/>
    <circle cx="0" cy="0" r="1.2" fill="{p['grid']}" fill-opacity="0.20"/>
  </pattern>
  <filter id="{prefix}-glow" x="-120%" y="-120%" width="340%" height="340%">
    <feGaussianBlur stdDeviation="8" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="{prefix}-wide-glow" x="-80%" y="-80%" width="260%" height="260%">
    <feGaussianBlur stdDeviation="28"/>
  </filter>
  <clipPath id="{prefix}-clip"><rect x="24" y="24" width="{WIDE[0]-48}" height="{WIDE[1]-48}" rx="34"/></clipPath>
</defs>"""


def mobile_defs(theme: str, p: dict, prefix: str) -> str:
    return f"""<defs>
  <linearGradient id="{prefix}-bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{p['bg2']}"/><stop offset="0.55" stop-color="{p['bg']}"/><stop offset="1" stop-color="{p['field']}"/>
  </linearGradient>
  <radialGradient id="{prefix}-core" cx="48%" cy="42%" r="65%">
    <stop offset="0" stop-color="{p['cyan']}" stop-opacity="0.20"/><stop offset="0.48" stop-color="{p['violet']}" stop-opacity="0.08"/><stop offset="1" stop-color="{p['black']}" stop-opacity="0.96"/>
  </radialGradient>
  <linearGradient id="{prefix}-coreline" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p['accent']}"/><stop offset="0.34" stop-color="{p['cyan']}"/><stop offset="0.68" stop-color="{p['violet']}"/><stop offset="1" stop-color="{p['mint']}"/></linearGradient>
  <pattern id="{prefix}-grid" width="44" height="44" patternUnits="userSpaceOnUse"><path d="M 44 0 H 0 V 44" fill="none" stroke="{p['grid']}" stroke-opacity="0.12" stroke-width="1"/><circle cx="0" cy="0" r="1.1" fill="{p['grid']}" fill-opacity="0.20"/></pattern>
  <filter id="{prefix}-glow" x="-120%" y="-120%" width="340%" height="340%"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <filter id="{prefix}-wide-glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="28"/></filter>
</defs>"""


def specks(p: dict, seed: int, count: int, cx: float, cy: float, spread_x: float, spread_y: float) -> str:
    items = []
    for i in range(count):
        a = (seed * 0.73 + i * 2.399963) % math.tau
        r = 0.22 + ((seed * 19 + i * 43) % 100) / 100
        x = cx + math.cos(a) * spread_x * r
        y = cy + math.sin(a) * spread_y * r
        if 32 < x < 1448 and 32 < y < 828:
            op = 0.09 + (i % 7) * 0.035
            rad = 0.6 + (i % 4) * 0.35
            items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{p["accent"]}" opacity="{op:.2f}"/>')
    return "".join(items)


def mobile_specks(p: dict, seed: int, count: int) -> str:
    items = []
    for i in range(count):
        a = (seed * 0.73 + i * 2.399963) % math.tau
        r = 0.20 + ((seed * 19 + i * 43) % 100) / 100
        x = 450 + math.cos(a) * 390 * r
        y = 390 + math.sin(a) * 350 * r
        if 28 < x < 872 and 28 < y < 1132:
            op = 0.10 + (i % 7) * 0.035
            items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{0.7 + (i%3)*0.3:.1f}" fill="{p["accent"]}" opacity="{op:.2f}"/>')
    return "".join(items)


def pill(x: float, y: float, text: str, color: str, p: dict, prefix: str, anchor: str = "start") -> str:
    width = 18 + max(28, len(text) * 7.1)
    xx = x if anchor == "start" else x - width
    return f'''<g>
      <rect x="{xx:.1f}" y="{y-17:.1f}" width="{width:.1f}" height="26" rx="13" fill="{p['field']}" fill-opacity="0.88" stroke="{color}" stroke-opacity="0.66"/>
      <circle cx="{xx+13:.1f}" cy="{y-4:.1f}" r="3.2" fill="{color}" filter="url(#{prefix}-glow)"/>
      <text x="{xx+23:.1f}" y="{y:.1f}" fill="{p['ink']}" fill-opacity="0.94" font-family="sans-serif" font-size="13" letter-spacing="1.4">{esc(text)}</text>
    </g>'''


def wide_scene(data: dict, theme: str) -> str:
    p = PALETTES[theme]
    prefix = f"wide-{theme}"
    repos = data["genome"]
    featured = data["featured_artifact"]
    cx, cy = 840, 428
    strands = []
    beads = []
    positions = [(78, 198), (95, 590), (382, 100), (1200, 120), (1380, 318), (1320, 680)]
    for i, repo in enumerate(repos):
        x, y = positions[i]
        dom = repo["domain"]
        color = p[DOMAIN_COLOR.get(dom, "amber")]
        target_angle = -2.65 + i * 1.05
        tx = cx + math.cos(target_angle) * (196 + (i % 3) * 22)
        ty = cy + math.sin(target_angle) * (122 + (i % 2) * 16)
        c1 = (x + (cx - x) * 0.35, y + (cy - y) * 0.12 + math.sin(i) * 80)
        c2 = (x + (cx - x) * 0.78, y + (cy - y) * 0.90 + math.cos(i) * 70)
        d = curve((x, y), c1, c2, (tx, ty))
        weight = 1.8 + min(5.2, repo.get("stars", 0) * 1.3 + (i % 3) * 0.55)
        opacity = 0.38 + (i % 4) * 0.10
        if repo.get("state") == "EXPERIMENT":
            opacity *= 0.72
        strands.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{weight:.1f}" opacity="{opacity:.2f}" stroke-linecap="round"/>')
        strands.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="0.9" opacity="0.62" stroke-dasharray="2 14"><animate attributeName="stroke-dashoffset" from="0" to="-64" dur="{6+i*0.7:.1f}s" repeatCount="indefinite"/></path>')
        beads.append(pill(x, y, repo["name"], color, p, prefix, "start" if x < cx else "end"))
        beads.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{4.0 + (i%3)*1.2:.1f}" fill="{color}" opacity="0.96" filter="url(#{prefix}-glow)"/>')
    contour = []
    for i in range(5):
        contour.append(f'<path d="{polar_path(cx, cy, 255+i*25, 174+i*18, 44, i*0.7, 10+i*2)}" fill="none" stroke="{p["cyan"] if i%2==0 else p["violet"]}" stroke-opacity="{0.12+i*0.035:.2f}" stroke-width="{1+i*0.32:.1f}" stroke-dasharray="2 18"/>')
    core = f'''
      <ellipse cx="{cx}" cy="{cy}" rx="300" ry="220" fill="{p['cyan']}" opacity="0.06" filter="url(#{prefix}-wide-glow)"/>
      <path d="{polar_path(cx, cy, 244, 165, 54, 0.6, 18)}" fill="url(#{prefix}-core)" stroke="url(#{prefix}-coreline)" stroke-opacity="0.78" stroke-width="3"/>
      <path d="{polar_path(cx, cy, 205, 132, 46, 2.1, 13)}" fill="none" stroke="{p['accent']}" stroke-opacity="0.68" stroke-width="1.6"/>
      <path d="{polar_path(cx, cy, 166, 105, 42, -0.4, 10)}" fill="{p['black']}" stroke="{p['cyan']}" stroke-opacity="0.48" stroke-width="1.4"/>
      <ellipse cx="{cx}" cy="{cy}" rx="76" ry="50" fill="{p['black']}" stroke="{p['accent']}" stroke-opacity="0.88" stroke-width="2.5"/>
      <ellipse cx="{cx}" cy="{cy}" rx="51" ry="31" fill="none" stroke="{p['violet']}" stroke-opacity="0.78" stroke-width="2" stroke-dasharray="1 9"/>
      <circle cx="{cx}" cy="{cy}" r="17" fill="{p['violet']}" opacity="0.82" filter="url(#{prefix}-glow)"/>
      <circle cx="{cx}" cy="{cy}" r="6" fill="{p['ink']}"/>
      <text x="{cx}" y="{cy-4}" text-anchor="middle" fill="{p['ink']}" font-family="sans-serif" font-size="14" font-weight="700" letter-spacing="2">GITRECON</text>
      <text x="{cx}" y="{cy+18}" text-anchor="middle" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="2">SURFACE MAPPER / ACTIVE</text>
    '''
    log_lines = []
    for i, repo in enumerate(repos[:4]):
        y = 190 + i * 32
        col = p[DOMAIN_COLOR.get(repo["domain"], "amber")]
        log_lines.append(f'<line x1="1110" y1="{y}" x2="1172" y2="{y}" stroke="{col}" stroke-width="2" opacity="0.76"/><circle cx="1100" cy="{y}" r="3" fill="{col}"/><text x="1192" y="{y+4}" fill="{p["muted"]}" font-family="sans-serif" font-size="11" letter-spacing="1">{esc(repo["domain"])} / {esc(repo["state"])}</text>')
    top = f'''
      <text x="72" y="86" fill="{p['ink']}" font-family="sans-serif" font-size="16" letter-spacing="4">HAZAVVIP / REPOSITORY GENOME</text>
      <text x="72" y="112" fill="{p['muted']}" font-family="sans-serif" font-size="11" letter-spacing="2">AN EVOLVING MAP OF ENGINEERING SIGNALS</text>
      <text x="1408" y="86" text-anchor="end" fill="{p['mint']}" font-family="sans-serif" font-size="12" letter-spacing="2">● SIGNAL ONLINE</text>
      <path d="M 70 138 H 440" stroke="{p['edge']}" stroke-opacity="0.42"/>
      <path d="M 1110 138 H 1410" stroke="{p['edge']}" stroke-opacity="0.42"/>
    '''
    labels = f'''
      <text x="76" y="735" fill="{p['muted']}" font-family="sans-serif" font-size="11" letter-spacing="1.4">ONE ARTIFACT → MANY INSTRUMENTS → ONE LIVING SYSTEM</text>
      <text x="1408" y="735" text-anchor="end" fill="{p['muted']}" font-family="sans-serif" font-size="11" letter-spacing="1.4">RUST / {featured['stars']}★ / {esc(featured['state'])}</text>
      <text x="1110" y="150" fill="{p['ink']}" font-family="sans-serif" font-size="11" letter-spacing="2">TRANSMISSION LOG</text>
      <text x="74" y="166" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="2">REPOSITORY STRANDS</text>
    '''
    inner = f'''<rect x="24" y="24" width="{WIDE[0]-48}" height="{WIDE[1]-48}" rx="34" fill="url(#{prefix}-grid)" stroke="{p['edge']}" stroke-opacity="0.32"/>{specks(p, 31, 105, cx, cy, 720, 360)}{top}{"".join(contour)}{"".join(strands)}{core}{"".join(beads)}{"".join(log_lines)}{labels}
      <path d="M 74 764 H 1406" stroke="{p['edge']}" stroke-opacity="0.30"/>
      <path d="M 74 764 h 44 M 1406 764 h -44" stroke="{p['accent']}" stroke-opacity="0.62" stroke-width="2"/>
    '''
    return svg_document(WIDE, prefix, defs(theme, p, prefix), inner, f"HazaVVIP Repository Genome featuring GitRecon, {theme} theme")


def mobile_scene(data: dict, theme: str) -> str:
    p = PALETTES[theme]
    prefix = f"mobile-{theme}"
    repos = data["genome"]
    featured = data["featured_artifact"]
    cx, cy = 450, 410
    strands = []
    # A vertical composition: the organism is upper, proof rails below.
    for i, repo in enumerate(repos):
        color = p[DOMAIN_COLOR.get(repo["domain"], "amber")]
        side = -1 if i % 2 == 0 else 1
        y0 = 148 + (i % 3) * 52
        x0 = 58 if side < 0 else 842
        tx = cx + side * (120 + (i % 2) * 18)
        ty = cy + (i - 2.5) * 39
        d = curve((x0, y0), (x0 + side * 180, 110 + i * 18), (cx + side * 260, 360 + i * 8), (tx, ty))
        width = 2.2 + min(4.2, repo.get("stars", 0) * 1.4 + (i % 3) * 0.5)
        op = 0.34 + (i % 4) * 0.10
        if repo.get("state") == "EXPERIMENT": op *= 0.72
        strands.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width:.1f}" opacity="{op:.2f}" stroke-linecap="round"/>')
        strands.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="0.8" opacity="0.58" stroke-dasharray="2 13"><animate attributeName="stroke-dashoffset" from="0" to="-60" dur="{5.5+i*0.6:.1f}s" repeatCount="indefinite"/></path>')
        strands.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="{4+(i%2)}" fill="{color}" filter="url(#{prefix}-glow)"/>')
    core = f'''
      <ellipse cx="{cx}" cy="{cy}" rx="322" ry="246" fill="{p['cyan']}" opacity="0.06" filter="url(#{prefix}-wide-glow)"/>
      <path d="{polar_path(cx, cy, 246, 175, 48, 0.5, 17)}" fill="url(#{prefix}-core)" stroke="url(#{prefix}-coreline)" stroke-opacity="0.76" stroke-width="3"/>
      <path d="{polar_path(cx, cy, 204, 140, 42, 1.8, 14)}" fill="none" stroke="{p['accent']}" stroke-opacity="0.66" stroke-width="1.5"/>
      <path d="{polar_path(cx, cy, 160, 105, 40, -0.3, 10)}" fill="{p['black']}" stroke="{p['cyan']}" stroke-opacity="0.54" stroke-width="1.5"/>
      <ellipse cx="{cx}" cy="{cy}" rx="92" ry="58" fill="{p['black']}" stroke="{p['accent']}" stroke-opacity="0.88" stroke-width="2.4"/>
      <circle cx="{cx}" cy="{cy}" r="18" fill="{p['violet']}" opacity="0.82" filter="url(#{prefix}-glow)"/>
      <circle cx="{cx}" cy="{cy}" r="6" fill="{p['ink']}"/>
      <text x="{cx}" y="{cy-2}" text-anchor="middle" fill="{p['ink']}" font-family="sans-serif" font-size="15" font-weight="700" letter-spacing="2">GITRECON</text>
      <text x="{cx}" y="{cy+20}" text-anchor="middle" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.5">SURFACE MAPPER</text>
    '''
    rows = []
    y = 785
    for i, repo in enumerate(repos[:6]):
        col = p[DOMAIN_COLOR.get(repo["domain"], "amber")]
        x = 70 + (i % 2) * 405
        yy = y + (i // 2) * 70
        rows.append(f'<circle cx="{x}" cy="{yy-4}" r="4" fill="{col}"/><text x="{x+14}" y="{yy}" fill="{p["ink"]}" font-family="sans-serif" font-size="12" letter-spacing="1">{esc(repo["name"])}</text><text x="{x+14}" y="{yy+19}" fill="{p["muted"]}" font-family="sans-serif" font-size="9" letter-spacing="1">{esc(repo["domain"])} / {esc(repo["state"])}</text>')
    inner = f'''<rect x="24" y="24" width="{MOBILE[0]-48}" height="{MOBILE[1]-48}" rx="30" fill="url(#{prefix}-grid)" stroke="{p['edge']}" stroke-opacity="0.32"/>{mobile_specks(p, 43, 90)}
      <text x="58" y="82" fill="{p['ink']}" font-family="sans-serif" font-size="15" letter-spacing="3">HAZAVVIP / GENOME</text>
      <text x="58" y="108" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.6">AN EVOLVING MAP OF ENGINEERING SIGNALS</text>
      <text x="842" y="82" text-anchor="end" fill="{p['mint']}" font-family="sans-serif" font-size="11" letter-spacing="1.8">● ONLINE</text>
      {"".join(strands)}{core}
      <path d="M 62 700 H 838" stroke="{p['edge']}" stroke-opacity="0.3"/>
      <text x="62" y="732" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.4">SIGNAL SOURCES / REPOSITORY GENOME</text>
      {"".join(rows)}
      <text x="62" y="1095" fill="{p['muted']}" font-family="sans-serif" font-size="10" letter-spacing="1.2">ONE ARTIFACT → MANY INSTRUMENTS → ONE LIVING SYSTEM</text>
    '''
    return svg_document(MOBILE, prefix, mobile_defs(theme, p, prefix), inner, f"HazaVVIP Repository Genome mobile scene featuring GitRecon, {theme} theme")


def svg_document(size: tuple[int, int], prefix: str, defs_text: str, inner: str, label: str) -> str:
    w, h = size
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
  {defs_text}
  <rect width="{w}" height="{h}" fill="url(#{prefix}-bg)"/>
  {inner}
</svg>
'''


def main():
    data = json.loads(CONFIG.read_text())
    live = json.loads(LIVE.read_text())
    live_index = {item["name"].lower(): item for item in live.get("repositories", [])}
    for item in [data.get("featured_artifact", {}), *data.get("genome", [])]:
        current = live_index.get(item.get("name", "").lower())
        if current:
            for key in ("language", "stars", "updated_at"):
                if key in current:
                    item[key] = current[key]
    outputs = {
        "repository-genome-dark.svg": wide_scene(data, "dark"),
        "repository-genome-light.svg": wide_scene(data, "light"),
        "repository-genome-mobile-dark.svg": mobile_scene(data, "dark"),
        "repository-genome-mobile-light.svg": mobile_scene(data, "light"),
    }
    for name, content in outputs.items():
        path = OUT / name
        path.write_text(content)
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
