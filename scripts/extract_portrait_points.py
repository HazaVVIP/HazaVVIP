#!/usr/bin/env python3
"""Extract a compact halftone point cloud from the stylized portrait master."""
from __future__ import annotations

import json
import random
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "portrait" / "source-stylized.png"
OUTPUT = ROOT / "data" / "portrait_points.json"

# The source portrait is intentionally kept local and ignored by git. The
# public artifact contains only abstract point/color data and the rendered SVG.
GRID_W, GRID_H = 92, 122


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def main() -> None:
    image = Image.open(SOURCE).convert("RGB")
    image = ImageOps.fit(image, (GRID_W, GRID_H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.50))
    pixels = image.load()
    points: list[dict[str, float | str]] = []
    rng = random.Random(8181)

    for y in range(GRID_H):
        for x in range(GRID_W):
            r, g, b = pixels[x, y]
            lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            sat = (max(r, g, b) - min(r, g, b)) / 255.0
            # White background disappears; darker portrait pixels become dense.
            ink = clamp((1.0 - lum) * 1.18 + sat * 0.10)
            if ink < 0.145:
                continue
            # A slight deterministic dropout gives the point cloud air and grain.
            dropout = 0.025 if ink > 0.45 else 0.11
            if rng.random() < dropout:
                continue
            if b >= r * 0.92 and b >= g * 0.98:
                color = "cyan"
            elif r > b * 1.08:
                color = "rose"
            else:
                color = "violet"
            points.append({
                "x": x / (GRID_W - 1),
                "y": y / (GRID_H - 1),
                "ink": round(ink, 3),
                "color": color,
                "size": round(0.75 + ink * 2.15, 2),
            })

    # Sparse edge particles are derived from the same source, not invented as
    # a second portrait. They create the disintegration halo used by the scene.
    edge = []
    for point in points:
        ink = float(point["ink"])
        if ink < 0.28 and rng.random() > 0.28:
            continue
        if rng.random() > 0.12:
            continue
        dx = (rng.random() - 0.5) * 0.055
        dy = (rng.random() - 0.5) * 0.04
        edge.append({
            "x": round(clamp(float(point["x"]) + dx), 4),
            "y": round(clamp(float(point["y"]) + dy), 4),
            "ink": round(max(0.18, ink * 0.66), 3),
            "color": point["color"],
            "size": round(0.55 + ink * 1.4, 2),
            "edge": True,
        })

    payload = {
        "source": "stylized portrait master; original photo not published",
        "grid": [GRID_W, GRID_H],
        "points": points + edge,
        "stats": {"core_points": len(points), "edge_points": len(edge), "total": len(points) + len(edge)},
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    print(f"wrote {OUTPUT} with {len(points) + len(edge)} points")


if __name__ == "__main__":
    main()
