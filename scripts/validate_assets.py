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


def same(name: str) -> bool:
    generated = ROOT / "assets" / "genome" / name
    fallback = ROOT / "assets" / "fallback" / name
    return generated.read_bytes() == fallback.read_bytes()


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")

    for json_path in (ROOT / "profile.config.json", ROOT / "data" / "profile.json", ROOT / "data" / "repository_genome.json"):
        if json_path.exists():
            try:
                json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid JSON: {json_path.relative_to(ROOT)} ({exc})")

    genome_config = ROOT / "data" / "repository_genome.json"
    if genome_config.exists():
        model = json.loads(genome_config.read_text(encoding="utf-8"))
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

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required_text in (
        "REPOSITORY GENOME",
        "GitRecon",
        "repository-genome-dark.svg",
        "repository-genome-light.svg",
        "repository-genome-mobile-dark.svg",
        "repository-genome-mobile-light.svg",
        "RECON",
        "PACKET",
        "AUTOMATION",
    ):
        if required_text not in readme:
            errors.append(f"README missing marker: {required_text}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(readme):
            errors.append("secret pattern found: README.md")

    for name in (
        "repository-genome-dark.svg",
        "repository-genome-light.svg",
        "repository-genome-mobile-dark.svg",
        "repository-genome-mobile-light.svg",
    ):
        if (ROOT / "assets" / "genome" / name).exists() and (ROOT / "assets" / "fallback" / name).exists() and not same(name):
            errors.append(f"{name} fallback differs from generated genome asset")

    for theme in ("dark", "light"):
        generated = (ROOT / "assets" / "generated" / f"signal-array-{theme}.svg").read_bytes()
        fallback = (ROOT / "assets" / "fallback" / f"signal-array-{theme}.svg").read_bytes()
        if generated != fallback:
            errors.append(f"{theme} signal-array fallback differs from generated asset")

    for theme in ("dark", "light"):
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
