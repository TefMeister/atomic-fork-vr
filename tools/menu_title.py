#!/usr/bin/env python3
"""menu_title.py -- draw a one-row, weathered title picture for the main menu.

    python menu_title.py <font.ttf> <out.dds> [--text "FALLOUT: TALE OF TWO WASTELANDS"] [--plain] [--seed 7]

Cream letters with rust blotches, chipped edges and scratches, a dark edge and a soft shadow, on a see-through
background; --plain leaves the wear off. The picture is WIDTH x HEIGHT; the menu layout shows it at a set width.
Uncompressed 32-bit .dds, so the wear stays crisp.
"""
import argparse
import struct

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 2048, 160
TEXT_WIDTH = 1960            # the row of letters is fitted to this many pixels
CREAM, RUST, DARK_RUST, EDGE_RGB = (238, 224, 186), (168, 84, 36), (92, 44, 18), (30, 18, 10)
EDGE = 4
RUST_SHARE = 0.34            # how much of the letters' face is rust
CHIP_AT_EDGE = 0.40          # how much of the letters' rim is chipped away
CHIP_INSIDE = 0.035
SCRATCHES = 34


def noise(rng, size, blur):
    """Smooth random blotches, 0..1, evenly spread (so a threshold of 0.7 covers 30 %)."""
    w, h = size
    im = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, dtype=np.float32)
    ranks = a.argsort(axis=None).argsort().reshape(a.shape)
    return ranks / ranks.max()


def fit_font(path, text):
    size = 20
    while ImageFont.truetype(path, size + 1).getlength(text) <= TEXT_WIDTH:
        size += 1
    return ImageFont.truetype(path, size)


def write_dds(im, path):
    w, h = im.size
    pf = struct.pack("<II4sIIIII", 32, 0x41, bytes(4), 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    head = b"DDS " + struct.pack("<IIIIIII", 124, 0x100F, h, w, w * 4, 0, 0) + bytes(44) + pf + struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(head + im.tobytes("raw", "BGRA"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ttf"); ap.add_argument("out")
    ap.add_argument("--text", default="FALLOUT: TALE OF TWO WASTELANDS")
    ap.add_argument("--plain", action="store_true"); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    font = fit_font(a.ttf, a.text)
    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    ImageDraw.Draw(mask).text((WIDTH // 2, HEIGHT // 2), a.text, font=font, fill=255, anchor="mm")
    face = np.empty((HEIGHT, WIDTH, 3), np.float32)
    face[:] = CREAM
    if not a.plain:
        m = np.asarray(mask, dtype=np.float32) / 255
        rim = m - np.asarray(mask.filter(ImageFilter.MinFilter(9)), dtype=np.float32) / 255      # 1 on the letters' rim
        blot, grain, chip = noise(rng, (WIDTH, HEIGHT), 9), noise(rng, (WIDTH, HEIGHT), 1.2), noise(rng, (WIDTH, HEIGHT), 3.5)
        rust = np.clip((blot - (1 - RUST_SHARE)) / 0.08, 0, 1)[..., None]
        face = face * (1 - rust) + np.array(RUST, np.float32) * rust
        speck = (grain > 0.90)[..., None]
        face = np.where(speck, face * 0.45 + np.array(DARK_RUST, np.float32) * 0.55, face)
        face *= (0.86 + 0.14 * noise(rng, (WIDTH, HEIGHT), 20))[..., None]                        # uneven fading
        face *= np.linspace(1.06, 0.88, HEIGHT, dtype=np.float32)[:, None, None]                 # lighter at the top
        gone = ((chip > 1 - CHIP_AT_EDGE) & (rim > 0.5)) | (chip > 1 - CHIP_INSIDE)
        scratch = Image.new("L", (WIDTH, HEIGHT), 0)
        d = ImageDraw.Draw(scratch)
        for _ in range(SCRATCHES):
            x, y, ln, tilt = rng.integers(0, WIDTH), rng.integers(0, HEIGHT), rng.integers(40, 260), rng.uniform(-0.25, 0.25)
            d.line((x, y, x + ln, y + ln * tilt), fill=255, width=int(rng.integers(1, 3)))
        gone |= np.asarray(scratch) > 0
        mask = Image.fromarray((m * ~gone * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    edge = mask.filter(ImageFilter.MaxFilter(2 * EDGE + 1))
    shadow = ImageChops.offset(edge, 4, 5).filter(ImageFilter.GaussianBlur(4)).point(lambda v: int(v * 0.8))
    rgb = Image.composite(Image.fromarray(np.clip(face, 0, 255).astype(np.uint8)), Image.new("RGB", (WIDTH, HEIGHT), EDGE_RGB), mask)
    out = rgb.convert("RGBA")
    out.putalpha(ImageChops.lighter(edge, shadow))
    write_dds(out, a.out)
    print(f"title row: {WIDTH} x {HEIGHT}, letters {int(font.getlength(a.text))} px wide")


if __name__ == "__main__":
    main()
