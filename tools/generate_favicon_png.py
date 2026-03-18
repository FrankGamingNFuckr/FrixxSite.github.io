from __future__ import annotations

import binascii
import struct
import zlib
from pathlib import Path


def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    length = struct.pack(">I", len(data))
    crc = binascii.crc32(chunk_type)
    crc = binascii.crc32(data, crc)
    crc_bytes = struct.pack(">I", crc & 0xFFFFFFFF)
    return length + chunk_type + data + crc_bytes


def _srgb_to_u8(x: float) -> int:
    x = 0.0 if x < 0.0 else 1.0 if x > 1.0 else x
    return int(round(x * 255))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _hex_rgb(hex_color: str) -> tuple[float, float, float]:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return r, g, b


def _blend_over(bg: tuple[int, int, int, int], fg: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    br, bgc, bb, ba = bg
    fr, fgc, fb, fa = fg
    a = fa / 255.0
    inv = 1.0 - a
    r = int(round(fr * a + br * inv))
    g = int(round(fgc * a + bgc * inv))
    b = int(round(fb * a + bb * inv))
    return (r, g, b, 255)


def generate_favicon_png(out_path: Path, size: int = 64) -> None:
    # Palette roughly matches favicon.svg
    c0 = _hex_rgb("#0b2b55")
    c1 = _hex_rgb("#061427")
    c2 = _hex_rgb("#03040a")

    gold0 = _hex_rgb("#ffcb05")
    gold1 = _hex_rgb("#ffd96b")
    red = _hex_rgb("#ff2323")

    # Start with a background radial-ish gradient (approximation)
    pixels: list[list[tuple[int, int, int, int]]] = []
    cx = size * 0.35
    cy = size * 0.30
    max_r = (size * 0.85)

    for y in range(size):
        row: list[tuple[int, int, int, int]] = []
        for x in range(size):
            dx = x - cx
            dy = y - cy
            r = (dx * dx + dy * dy) ** 0.5
            t = min(1.0, r / max_r)
            # Blend c0 -> c1 -> c2
            if t < 0.55:
                tt = t / 0.55
                rr = _lerp(c0[0], c1[0], tt)
                gg = _lerp(c0[1], c1[1], tt)
                bb = _lerp(c0[2], c1[2], tt)
            else:
                tt = (t - 0.55) / 0.45
                rr = _lerp(c1[0], c2[0], tt)
                gg = _lerp(c1[1], c2[1], tt)
                bb = _lerp(c1[2], c2[2], tt)
            row.append((_srgb_to_u8(rr), _srgb_to_u8(gg), _srgb_to_u8(bb), 255))
        pixels.append(row)

    def put(x: int, y: int, rgba: tuple[int, int, int, int]) -> None:
        if 0 <= x < size and 0 <= y < size:
            pixels[y][x] = _blend_over(pixels[y][x], rgba)

    # Stars (fixed positions like SVG)
    stars = [
        (14, 18, 255, 255, 255, 190),
        (50, 16, 255, 255, 255, 175),
        (44, 28, 255, 255, 255, 165),
        (18, 44, 255, 255, 255, 175),
        (52, 46, 255, 255, 255, 190),
        (36, 52, 255, 255, 255, 165),
    ]
    for x, y, r, g, b, a in stars:
        put(x, y, (r, g, b, a))

    # Red accent ring (simple circle stroke)
    ring_cx = ring_cy = size // 2
    ring_r = int(round(size * 0.34375))  # ~22 for 64
    stroke = 3
    rr_u8, rg_u8, rb_u8 = (_srgb_to_u8(red[0]), _srgb_to_u8(red[1]), _srgb_to_u8(red[2]))
    for y in range(size):
        for x in range(size):
            dx = x - ring_cx
            dy = y - ring_cy
            dist = (dx * dx + dy * dy) ** 0.5
            if ring_r - stroke / 2 <= dist <= ring_r + stroke / 2:
                put(x, y, (rr_u8, rg_u8, rb_u8, 56))

    # Gold "F" mark (blocky approximation)
    g0 = (_srgb_to_u8(gold0[0]), _srgb_to_u8(gold0[1]), _srgb_to_u8(gold0[2]))
    g1 = (_srgb_to_u8(gold1[0]), _srgb_to_u8(gold1[1]), _srgb_to_u8(gold1[2]))

    def fill_rect(x0: int, y0: int, w: int, h: int, c: tuple[int, int, int], a: int = 255) -> None:
        for yy in range(y0, y0 + h):
            for xx in range(x0, x0 + w):
                put(xx, yy, (c[0], c[1], c[2], a))

    # Vertical stem
    fill_rect(22, 18, 8, 34, g0, 240)
    # Top bar
    fill_rect(22, 18, 26, 7, g1, 245)
    # Middle bar
    fill_rect(22, 31, 20, 6, g1, 235)

    # Slight outline
    outline = (_srgb_to_u8(0.6), _srgb_to_u8(0.48), _srgb_to_u8(0.05))
    # (Keep it subtle by alpha)
    for yy in range(18, 52):
        for xx in range(22, 48):
            if (xx, yy) in [(22, yy) for yy in range(18, 52)] or (yy in (18, 51) and 22 <= xx < 48):
                put(xx, yy, (outline[0], outline[1], outline[2], 40))

    # Encode PNG
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0
        for x in range(size):
            r, g, b, a = pixels[y][x]
            raw.extend(bytes((r, g, b, a)))

    compressed = zlib.compress(bytes(raw), level=9)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # RGBA

    png = bytearray(signature)
    png.extend(_png_chunk(b"IHDR", ihdr))
    png.extend(_png_chunk(b"IDAT", compressed))
    png.extend(_png_chunk(b"IEND", b""))

    out_path.write_bytes(bytes(png))


def main() -> int:
    out = Path("favicon.png")
    generate_favicon_png(out)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
