from __future__ import annotations

import argparse
import random
from pathlib import Path


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def generate_starfield_svg(width: int, height: int, stars: int, seed: int) -> str:
    rng = random.Random(seed)

    def star_color() -> str:
        # Mostly white; occasional slight tint.
        palette = [
            "#ffffff",
            "#ffffff",
            "#ffffff",
            "#fff3c0",
            "#c2e9ff",
            "#ffd7ff",
            "#d6ccff",
            "#bfffd0",
            "#ffc0c0",
        ]
        return rng.choice(palette)

    # Background gradient colors (dark space)
    bg0, bg1, bg2 = "#101a3a", "#060a16", "#03040a"

    parts: list[str] = []
    parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">' 
    )
    parts.append("  <defs>")
    parts.append("    <radialGradient id=\"v\" cx=\"50%\" cy=\"40%\" r=\"70%\">")
    parts.append(f"      <stop offset=\"0%\" stop-color=\"{bg0}\" stop-opacity=\"0.75\"/>")
    parts.append(f"      <stop offset=\"55%\" stop-color=\"{bg1}\" stop-opacity=\"0.92\"/>")
    parts.append(f"      <stop offset=\"100%\" stop-color=\"{bg2}\" stop-opacity=\"1\"/>")
    parts.append("    </radialGradient>")
    parts.append("    <filter id=\"blur1\" x=\"-20%\" y=\"-20%\" width=\"140%\" height=\"140%\">")
    parts.append("      <feGaussianBlur stdDeviation=\"0.7\"/>")
    parts.append("    </filter>")
    parts.append("    <filter id=\"blur2\" x=\"-30%\" y=\"-30%\" width=\"160%\" height=\"160%\">")
    parts.append("      <feGaussianBlur stdDeviation=\"1.4\"/>")
    parts.append("    </filter>")
    parts.append("  </defs>")
    parts.append("")

    parts.append(f"  <rect width=\"{width}\" height=\"{height}\" fill=\"url(#v)\"/>")

    # Small stars
    parts.append("  <g fill=\"#ffffff\" fill-opacity=\"0.86\">")
    for _ in range(stars):
        x = rng.random() * width
        y = rng.random() * height
        r = _clamp(rng.gauss(1.0, 0.35), 0.55, 1.65)
        # A little twinkle variance
        a = _clamp(rng.gauss(0.80, 0.12), 0.35, 0.92)
        parts.append(f"    <circle cx=\"{x:.0f}\" cy=\"{y:.0f}\" r=\"{r:.2f}\" fill-opacity=\"{a:.2f}\"/>")
    parts.append("  </g>")

    # A few glow stars
    glow_count = max(6, stars // 18)
    parts.append("  <g filter=\"url(#blur2)\">")
    for _ in range(glow_count):
        x = rng.random() * width
        y = rng.random() * height
        r = _clamp(rng.gauss(2.7, 0.55), 1.8, 4.2)
        a = _clamp(rng.gauss(0.46, 0.10), 0.20, 0.70)
        parts.append(
            f"    <circle cx=\"{x:.0f}\" cy=\"{y:.0f}\" r=\"{r:.2f}\" fill=\"{star_color()}\" fill-opacity=\"{a:.2f}\"/>")
    parts.append("  </g>")

    # Subtle blur dust
    parts.append("  <g filter=\"url(#blur1)\">")
    for _ in range(max(4, stars // 40)):
        x = rng.random() * width
        y = rng.random() * height
        r = _clamp(rng.gauss(1.7, 0.4), 1.0, 2.8)
        a = _clamp(rng.gauss(0.32, 0.08), 0.12, 0.50)
        parts.append(f"    <circle cx=\"{x:.0f}\" cy=\"{y:.0f}\" r=\"{r:.2f}\" fill=\"#ffffff\" fill-opacity=\"{a:.2f}\"/>")
    parts.append("  </g>")

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a lightweight starfield SVG for the site background.")
    parser.add_argument("--out", default="assets/starfield.svg", help="Output path (default: assets/starfield.svg)")
    parser.add_argument("--width", type=int, default=1800)
    parser.add_argument("--height", type=int, default=1000)
    parser.add_argument("--stars", type=int, default=140)
    parser.add_argument("--seed", type=int, default=2026)

    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    svg = generate_starfield_svg(args.width, args.height, args.stars, args.seed)
    out_path.write_text(svg, encoding="utf-8", newline="\n")
    print(f"Wrote {out_path} ({args.width}x{args.height}, stars={args.stars}, seed={args.seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
