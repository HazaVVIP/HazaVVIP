#!/usr/bin/env python3
"""Validate generated profile assets before committing them."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "README.md",
    ROOT / "profile.config.json",
    ROOT / "data" / "profile.json",
    ROOT / "assets" / "generated" / "lab-dark.svg",
    ROOT / "assets" / "generated" / "lab-light.svg",
    ROOT / "assets" / "fallback" / "lab-dark.svg",
    ROOT / "assets" / "fallback" / "lab-light.svg",
]
SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"ghu_[A-Za-z0-9_]+"),
    re.compile(r"-----BEGIN .* PRIVATE KEY-----"),
]


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.exists():
            errors.append(f"missing: {path.relative_to(ROOT)}")

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
    for required_text in ("Systems Intelligence Lab", "RECON", "PACKET", "AUTOMATION", "lab-dark.svg", "lab-light.svg"):
        if required_text not in readme:
            errors.append(f"README missing marker: {required_text}")
    for pattern in SECRET_PATTERNS:
        if pattern.search(readme):
            errors.append("secret pattern found: README.md")

    generated_dark = (ROOT / "assets" / "generated" / "lab-dark.svg").read_bytes()
    fallback_dark = (ROOT / "assets" / "fallback" / "lab-dark.svg").read_bytes()
    if generated_dark != fallback_dark:
        errors.append("dark fallback differs from generated asset")
    generated_light = (ROOT / "assets" / "generated" / "lab-light.svg").read_bytes()
    fallback_light = (ROOT / "assets" / "fallback" / "lab-light.svg").read_bytes()
    if generated_light != fallback_light:
        errors.append("light fallback differs from generated asset")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print("Profile assets validated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
