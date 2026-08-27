#!/usr/bin/env python3
"""Validate generated profile assets before committing them."""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "profile.config.json",
    ROOT / "data" / "profile.json",
    ROOT / "data" / "repository_genome.json",
    ROOT / "data" / "portrait_points.json",
    ROOT / "assets" / "portrait" / "portrait-terminal-dark.svg",
    ROOT / "assets" / "portrait" / "portrait-terminal-light.svg",
    ROOT / "assets" / "fallback" / "portrait-terminal-dark.svg",
    ROOT / "assets" / "fallback" / "portrait-terminal-light.svg",
    ROOT / "assets" / "genome" / "repository-genome-dark.svg",
    ROOT / "assets" / "genome" / "repository-genome-light.svg",
    ROOT / "assets" / "genome" / "repository-genome-mobile-dark.svg",
    ROOT / "assets" / "genome" / "repository-genome-mobile-light.svg",
    ROOT / "assets" / "fallback" / "repository-genome-dark.svg",
    ROOT / "assets" / "fallback" / "repository-genome-light.svg",
    ROOT / "assets" / "fallback" / "repository-genome-mobile-dark.svg",
    ROOT / "assets" / "fallback" / "repository-genome-mobile-light.svg",
    ROOT / "assets" / "generated" / "lab-dark.svg",
    ROOT / "assets" / "generated" / "lab-light.svg",
    ROOT / "assets" / "generated" / "signal-array-dark.svg",
    ROOT / "assets" / "generated" / "signal-array-light.svg",
    ROOT / "assets" / "fallback" / "lab-dark.svg",
    ROOT / "assets" / "fallback" / "lab-light.svg",
    ROOT / "assets" / "fallback" / "signal-array-dark.svg",
    ROOT / "assets" / "fallback" / "signal-array-light.svg",
]
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"gh[ousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"-----BEGIN .* PRIVATE KEY-----"),
]


def same(folder: str, name: str) -> bool:
    generated = ROOT / folder / name
    fallback = ROOT / "assets" / "fallback" / name
    return generated.read_bytes() == fallback.read_bytes()


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")

    json_files = (
        ROOT / "profile.config.json",
        ROOT / "data" / "profile.json",
        ROOT / "data" / "repository_genome.json",
        ROOT / "data" / "portrait_points.json",
    )
    for json_path in json_files:
        if json_path.exists():
            try:
                json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON: {json_path.relative_to(ROOT)} ({exc})")

    points_path = ROOT / "data" / "portrait_points.json"
    if points_path.exists():
        points = json.loads(points_path.read_text(encoding="utf-8"))
        if len(points.get("points", [])) < 1000:
            errors.append("portrait point cloud must contain at least 1000 points")
        if not points.get("stats", {}).get("total"):
            errors.append("portrait point cloud is missing stats.total")

    genome_path = ROOT / "data" / "repository_genome.json"
    if genome_path.exists():
        model = json.loads(genome_path.read_text(encoding="utf-8"))
        featured = model.get("featured_artifact", {})
        if featured.get("name") != "GitRecon":
            errors.append("genome featured artifact must be GitRecon")
        if not featured.get("url", "").startswith("https://github.com/HazaVVIP/"):
            errors.append("genome featured artifact URL must target HazaVVIP")
        if len(model.get("genome", [])) < 4:
            errors.append("genome must contain at least four related repositories")

    for path in sorted((ROOT / "assets").rglob("*.svg")):
        try:
            ET.parse(path)
        except ET.ParseError as exc:
            errors.append(f"invalid XML: {path.relative_to(ROOT)} ({exc})")
        if path.stat().st_size > 250_000:
            errors.append(f"too large: {path.relative_to(ROOT)}")
        text = path.read_text(encoding="utf-8")
        if "<script" in text.lower():
            errors.append(f"script tag found: {path.relative_to(ROOT)}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"secret pattern found: {path.relative_to(ROOT)}")

    for path in sorted((ROOT / "assets" / "portrait").glob("portrait-terminal-*.svg")):
        text = path.read_text(encoding="utf-8")
        if text.count("<animate") < 100:
            errors.append(f"portrait animation too sparse: {path.relative_to(ROOT)}")
        if "HALFTONE / SCANLINE / GLITCH / IDENTITY SIGNAL" not in text:
            errors.append(f"portrait marker missing: {path.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required_text in (
        "PORTRAIT SIGNAL",
        "portrait-terminal-dark.svg",
        "portrait-terminal-light.svg",
        "GitRecon",
        "RECON",
        "PACKET",
        "AUTOMATION",
    ):
        if required_text not in readme:
            errors.append(f"README missing marker: {required_text}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(readme):
            errors.append("secret pattern found: README.md")

    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    if "assets/portrait/source-stylized.png" not in ignore:
        errors.append("source portrait must remain ignored")

    for name in (
        "portrait-terminal-dark.svg",
        "portrait-terminal-light.svg",
    ):
        if (ROOT / "assets" / "portrait" / name).exists() and (ROOT / "assets" / "fallback" / name).exists() and not same("assets/portrait", name):
            errors.append(f"{name} fallback differs from portrait asset")

    for name in (
        "repository-genome-dark.svg",
        "repository-genome-light.svg",
        "repository-genome-mobile-dark.svg",
        "repository-genome-mobile-light.svg",
    ):
        if (ROOT / "assets" / "genome" / name).exists() and (ROOT / "assets" / "fallback" / name).exists() and not same("assets/genome", name):
            errors.append(f"{name} fallback differs from generated genome asset")

    for theme in ("dark", "light"):
        generated = (ROOT / "assets" / "generated" / f"signal-array-{theme}.svg").read_bytes()
        fallback = (ROOT / "assets" / "fallback" / f"signal-array-{theme}.svg").read_bytes()
        if generated != fallback:
            errors.append(f"{theme} signal-array fallback differs from generated asset")
        generated = (ROOT / "assets" / "generated" / f"lab-{theme}.svg").read_bytes()
        fallback = (ROOT / "assets" / "fallback" / f"lab-{theme}.svg").read_bytes()
        if generated != fallback:
            errors.append(f"{theme} lab fallback differs from generated asset")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Profile assets validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
