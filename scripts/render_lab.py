#!/usr/bin/env python3
"""Render the HazaVVIP Systems Intelligence Lab profile dashboard."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "profile.config.json"
DATA_PATH = ROOT / "data" / "profile.json"
OUT_DIR = ROOT / "assets" / "generated"
FALLBACK_DIR = ROOT / "assets" / "fallback"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_text(x: int, y: int, text: str, size: int, fill: str, weight: int = 400, anchor: str = "start", family: str = "system") -> str:
    resolved_family = "monospace" if family == "mono" else "sans-serif"
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{resolved_family}" font-size="{size}px" font-weight="{weight}" fill="{fill}">{esc(text)}</text>'


def pill(x: int, y: int, label: str, color: str, text_color: str) -> str:
    width = max(72, len(label) * 8 + 28)
    return (
        f'<rect x="{x}" y="{y - 19}" width="{width}" height="28" rx="14" fill="{color}" opacity=".16" stroke="{color}" stroke-opacity=".5"/>'
        + svg_text(x + width / 2, y, label, 12, color, 700, "middle", "mono")
    )


def render(theme: str, config: dict, data: dict) -> str:
    p = config["palette"][theme]
    repos = data.get("repositories", [])
    domains = config["domains"]
    total_stars = sum(int(repo.get("stars", 0)) for repo in repos)
    language_counts: dict[str, int] = {}
    for repo in repos:
        language = repo.get("language") or "Other"
        language_counts[language] = language_counts.get(language, 0) + 1
    top_languages = sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
    max_lang = max((count for _, count in top_languages), default=1)

    out: list[str] = []
    out.append(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="790" viewBox="0 0 1180 790" role="img" aria-labelledby="title desc">
  <title id="title">{esc(config["display_name"])} — {esc(config["lab_name"])}</title>
  <desc id="desc">A data-driven systems intelligence dashboard showing repository domains, telemetry, and project topology.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{p["background"]}"/>
      <stop offset="1" stop-color="{p["panel_alt"]}"/>
    </linearGradient>
    <linearGradient id="cyanLine" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{p["cyan"]}"/>
      <stop offset="1" stop-color="{p["purple"]}"/>
    </linearGradient>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="microGrid" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="{p["border"]}" stroke-width="1" opacity=".22"/>
    </pattern>
    <style>
      .pulse {{ animation: pulse 3s ease-in-out infinite; transform-origin: center; }}
      .scan {{ animation: scan 5s linear infinite; }}
      @keyframes pulse {{ 0%,100% {{ opacity: .38; }} 50% {{ opacity: 1; }} }}
      @keyframes scan {{ 0% {{ transform: translateX(-400px); opacity: 0; }} 20% {{ opacity: .6; }} 80% {{ opacity: .6; }} 100% {{ transform: translateX(700px); opacity: 0; }} }}
    </style>
  </defs>
  <rect x="8" y="8" width="1164" height="774" rx="28" fill="url(#bg)" stroke="{p["border"]}" stroke-width="2"/>
  <rect x="9" y="9" width="1162" height="772" rx="27" fill="url(#microGrid)" opacity=".55"/>
  <rect class="scan" x="50" y="80" width="420" height="2" fill="url(#cyanLine)" opacity=".45"/>
''')

    # Header / chrome
    out.append(f'''  <rect x="32" y="28" width="1116" height="62" rx="16" fill="{p["panel"]}" stroke="{p["border"]}"/>
  <circle cx="59" cy="59" r="7" fill="{p["red"]}"/>
  <circle cx="82" cy="59" r="7" fill="{p["amber"]}"/>
  <circle cx="105" cy="59" r="7" fill="{p["green"]}"/>
  {svg_text(135, 64, "HazaVVIP // systems-intelligence-lab", 17, p["text"], 700, family="mono")}
  {svg_text(1070, 57, "STATUS", 10, p["muted"], 700, "end", "mono")}
  <circle class="pulse" cx="1094" cy="58" r="6" fill="{p["green"]}" filter="url(#softGlow)"/>
  {svg_text(1118, 64, "ONLINE", 13, p["green"], 700, "end", "mono")}
''')

    # Left domain panel
    out.append(f'''  <rect x="32" y="112" width="525" height="380" rx="20" fill="{p["panel"]}" stroke="{p["border"]}"/>
  {svg_text(58, 148, "01 / OPERATIONAL DOMAINS", 13, p["cyan"], 700, family="mono")}
  {svg_text(58, 174, "repository topology", 25, p["text"], 800)}
  {svg_text(58, 199, "three signals · one engineering system", 13, p["muted"], family="mono")}
''')

    domain_y = 235
    color_map = {"cyan": p["cyan"], "purple": p["purple"], "green": p["green"], "amber": p["amber"]}
    for index, domain in enumerate(domains):
        y = domain_y + index * 78
        color = color_map.get(domain["color"], p["cyan"])
        repo_names = " · ".join(domain.get("repositories", []))
        out.append(f'''  <rect x="58" y="{y}" width="473" height="61" rx="13" fill="{p["panel_alt"]}" stroke="{color}" stroke-opacity=".45"/>
  <circle class="pulse" cx="80" cy="{y + 30}" r="6" fill="{color}" filter="url(#softGlow)"/>
  {svg_text(100, y + 26, domain["label"], 14, color, 800, family="mono")}
  {svg_text(100, y + 47, domain["description"], 12, p["muted"], family="mono")}
  {svg_text(505, y + 36, repo_names, 11, p["text"], 600, "end", "mono")}
''')

    # Right topology panel
    out.append(f'''  <rect x="575" y="112" width="573" height="380" rx="20" fill="{p["panel"]}" stroke="{p["border"]}"/>
  {svg_text(602, 148, "02 / REPOSITORY TOPOLOGY", 13, p["purple"], 700, family="mono")}
  {svg_text(602, 174, "signal map", 25, p["text"], 800)}
  {svg_text(602, 199, "public artifacts connected by domain", 13, p["muted"], family="mono")}
''')

    # Topology graph
    cx, cy = 855, 320
    out.append(f'''  <circle cx="{cx}" cy="{cy}" r="74" fill="{p["panel_alt"]}" stroke="{p["cyan"]}" stroke-opacity=".55" stroke-width="2"/>
  <circle class="pulse" cx="{cx}" cy="{cy}" r="55" fill="none" stroke="{p["cyan"]}" stroke-opacity=".24" stroke-width="2"/>
  {svg_text(cx, cy - 8, "HAZA", 19, p["text"], 800, "middle", "mono")}
  {svg_text(cx, cy + 16, "CORE", 12, p["cyan"], 700, "middle", "mono")}
''')
    nodes = [
        (670, 260, "RECON", p["cyan"]),
        (1040, 260, "PACKET", p["purple"]),
        (670, 410, "AUTOMATION", p["green"]),
        (1040, 410, "EXPERIMENTS", p["amber"]),
    ]
    for nx, ny, label, color in nodes:
        out.append(f'''  <path d="M {cx} {cy} L {nx} {ny}" fill="none" stroke="{color}" stroke-opacity=".5" stroke-width="2" stroke-dasharray="5 8"/>
  <circle class="pulse" cx="{nx}" cy="{ny}" r="29" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-width="2"/>
  {svg_text(nx, ny + 4, label, 10, color, 800, "middle", "mono")}
''')

    # Telemetry panel
    out.append(f'''  <rect x="32" y="515" width="1116" height="222" rx="20" fill="{p["panel"]}" stroke="{p["border"]}"/>
  {svg_text(58, 551, "03 / LIVE TELEMETRY", 13, p["green"], 700, family="mono")}
  {svg_text(58, 578, "engineering signal", 25, p["text"], 800)}
  {svg_text(1120, 552, "snapshot: " + str(data.get("updated_at", "public data"))[:10], 11, p["muted"], 600, "end", "mono")}
''')

    metrics = [
        ("PUBLIC REPOS", data.get("public_repos", len(repos)), p["cyan"]),
        ("FOLLOWERS", data.get("followers", 0), p["purple"]),
        ("STARS", total_stars, p["green"]),
        ("DOMAINS", len(domains), p["amber"]),
    ]
    metric_x = [58, 290, 522, 754]
    for (label, value, color), x in zip(metrics, metric_x):
        out.append(f'''  <rect x="{x}" y="602" width="198" height="96" rx="14" fill="{p["panel_alt"]}" stroke="{color}" stroke-opacity=".35"/>
  {svg_text(x + 18, 628, label, 10, p["muted"], 700, family="mono")}
  {svg_text(x + 18, 670, str(value), 33, color, 800, family="mono")}
  <circle class="pulse" cx="{x + 174}" cy="{650}" r="5" fill="{color}"/>
''')

    # Languages bar
    out.append(f'''  <rect x="986" y="602" width="134" height="96" rx="14" fill="{p["panel_alt"]}" stroke="{p["border"]}"/>
  {svg_text(1002, 628, "STACK MIX", 10, p["muted"], 700, family="mono")}
''')
    bar_y = 644
    for idx, (language, count) in enumerate(top_languages):
        width = int(82 * count / max_lang)
        color = [p["cyan"], p["purple"], p["green"], p["amber"], p["red"]][idx % 5]
        out.append(f'''  {svg_text(1002, bar_y + idx * 10 + 7, language[:10], 8, p["muted"], family="mono")}
  <rect x="1054" y="{bar_y + idx * 10}" width="52" height="6" rx="3" fill="{p["border"]}"/>
  <rect x="1054" y="{bar_y + idx * 10}" width="{max(5, min(52, int(width * 52 / 82)))}" height="6" rx="3" fill="{color}"/>
''')

    out.append(f'''  {svg_text(58, 725, "$ observe --public-signal --continuous", 12, p["muted"], family="mono")}
  {svg_text(1120, 725, "RECON · PACKET · AUTOMATION", 12, p["cyan"], 700, "end", "mono")}
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
        (OUT_DIR / f"lab-{theme}.svg").write_text(rendered, encoding="utf-8")
        (FALLBACK_DIR / f"lab-{theme}.svg").write_text(rendered, encoding="utf-8")
    print(f"Rendered {OUT_DIR / 'lab-dark.svg'} and {OUT_DIR / 'lab-light.svg'}")


if __name__ == "__main__":
    main()
