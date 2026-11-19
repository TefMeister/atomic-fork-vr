#!/usr/bin/env python3
"""game_font.py -- make a Fallout 3 / New Vegas menu font (.fnt + .Tex) from an ordinary font file.

    python game_font.py <font.ttf> <out folder> --fnt glow_futura_caps_large --tex AtomicFork_Menu_0_Lod_A
                        [--cap 46] [--line 60] [--caps-only] [--worn]

Writes <out>/textures/fonts/<fnt>.fnt and <out>/textures/fonts/<tex>.Tex. The .fnt name decides which of the game's
fonts it replaces (the game's font list is in fallout.ini, sFontFile_1..9); the .Tex name is our own, so nobody
else's picture is overwritten. Letters are white with a dark edge and a soft dark shadow: the game tints white to
the menu colour and leaves dark dark. --caps-only draws capitals for small letters too (the game's caps fonts have
no small letters at all). --worn gives the letters the title's worn look (menu_title.py's wear: rust, chips, scratches),
coloured so that once the game tints white to the menu yellow they match the title's colours.

The .fnt layout (read off the game's own files, 14,632 bytes): float line height, two ints (1, 1), the picture's
name in 284 bytes, then 256 letters of 14 floats each: 0, the four corners in the picture (left-top, right-top,
left-bottom, right-bottom, as fractions), width, height, space before, space after (advance = before + width +
after), and how far the box's top is above the writing line. The .Tex is two ints (width, height) and plain RGBA.
"""
import argparse
import os
import struct
import zlib

import numpy as np

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

import menu_title

ATLAS = 1024          # the picture is ATLAS x ATLAS
PAD = 8               # room round each letter for the edge and the shadow
EDGE = 3              # width of the dark edge
TRACKING = EDGE + 1       # extra room after each letter, or one letter's dark edge lies on the next letter's face
SHADOW_BLUR = 3
ACCENT_ROOM = 3       # rows kept above the capitals (more pushes every line of text down)
SHADOW_ALPHA = 0.75
EDGE_RGB = (22, 16, 10)
NAME_BYTES = 284
WEAR_SCALE = 0.5      # the menu capitals are about half the title's height on screen: every worn feature half as big
WEAR_SCRATCHES = (0, 0, 1)   # scratches per letter, picked at random from these


def font_for_cap(path, cap):
    size = 10
    while True:
        f = ImageFont.truetype(path, size)
        box = f.getbbox("H")
        if box[3] - box[1] >= cap:
            return f
        size += 1


def worn_colours():
    """The title's colours divided by the menu yellow: the game multiplies our white by that yellow, so these come out
    as the title's own rust and dark rust."""
    return tuple(tuple(min(255, round(255 * c / f)) for c, f in zip(rgb, menu_title.FACE))
                 for rgb in (menu_title.RUST, menu_title.DARK_RUST))


def letter(font, ch, ascent, descent, worn=False):
    """One letter in its box: (RGBA picture, advance). The box is the letter's own width plus PAD each side."""
    left, _, right, _ = font.getbbox(ch, anchor="ls")
    w = max(1, right - left) + 2 * PAD
    h = ascent + descent + 2 * PAD
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).text((PAD - left, PAD + ascent), ch, font=font, fill=255, anchor="ls")
    face = Image.new("RGB", (w, h), (255, 255, 255))
    if worn:
        rng = np.random.default_rng(zlib.crc32(ch.encode("utf-8")))    # the same letter wears the same way on every build
        rust, dark = worn_colours()
        f, mask = menu_title.wear(mask, rng, (255, 255, 255), rust, dark, WEAR_SCALE, int(rng.choice(WEAR_SCRATCHES)))
        face = Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))
    edge = mask.filter(ImageFilter.MaxFilter(2 * EDGE + 1))
    shadow = edge.filter(ImageFilter.GaussianBlur(SHADOW_BLUR)).point(lambda v: int(v * SHADOW_ALPHA))
    alpha = ImageChops.lighter(edge, shadow)                         # solid inside the edge, soft outside it
    rgb = Image.composite(face, Image.new("RGB", (w, h), EDGE_RGB), mask)
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out, font.getlength(ch), left


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("ttf"); ap.add_argument("out")
    ap.add_argument("--fnt", required=True); ap.add_argument("--tex", required=True)
    ap.add_argument("--cap", type=int, default=46, help="height of a capital letter, in menu units")
    ap.add_argument("--line", type=float, default=52.0, help="line height written in the file's first number (the game's big caps font: 52)")
    ap.add_argument("--top", type=float, default=47.0, help="the 'box top above the writing line' number written for every letter (the game's big caps "
                    "font: 47). The game places a line of text by it: a bigger number lifts the text. Seen 2026-11-19: with the true value "
                    "(57) and line 60 the menu words sat half a row above their boxes")
    ap.add_argument("--caps-only", action="store_true")
    ap.add_argument("--worn", action="store_true", help="the title's worn look on every letter")
    a = ap.parse_args()
    font = font_for_cap(a.ttf, a.cap)
    ascent = a.cap + ACCENT_ROOM
    descent = max(4, a.cap // 4)
    atlas = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    glyphs = [(0.0,) * 14] * 256
    x = y = 0
    row_h = ascent + descent + 2 * PAD
    made = {}
    for code in range(32, 256):
        try:
            ch = bytes([code]).decode("cp1252")
        except UnicodeDecodeError:
            continue
        if a.caps_only:
            ch = ch.upper() if len(ch.upper()) == 1 else ch
        if not ch.strip():
            if code == 32:
                glyphs[code] = (0.0,) * 12 + (float(round(font.getlength(" "))), 0.0)
            continue
        if ch not in made:
            img, adv, left = letter(font, ch, ascent, descent, a.worn)
            if x + img.width > ATLAS:
                x, y = 0, y + row_h
            if y + row_h > ATLAS:
                raise SystemExit("the letters do not fit the picture: smaller --cap, or a bigger ATLAS")
            atlas.paste(img, (x, y))
            made[ch] = (x, y, img.width, img.height, adv, left)
            x += img.width
        gx, gy, w, h, adv, left = made[ch]
        u0, v0, u1, v1 = gx / ATLAS, gy / ATLAS, (gx + w) / ATLAS, (gy + h) / ATLAS
        before = 0.0                               # as the game's own fonts: the box starts at the pen
        after = float(round(adv) - w + TRACKING)
        glyphs[code] = (0.0, u0, v0, u1, v0, u0, v1, u1, v1, float(w), float(h), before, after, a.top)
    folder = os.path.join(a.out, "textures", "fonts")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, a.fnt + ".fnt"), "wb") as f:
        f.write(struct.pack("<fII", a.line, 1, 1) + a.tex.encode("ascii").ljust(NAME_BYTES, bytes(1)))
        for g in glyphs:
            f.write(struct.pack("<14f", *g))
    with open(os.path.join(folder, a.tex + ".Tex"), "wb") as f:
        f.write(struct.pack("<II", ATLAS, ATLAS) + atlas.tobytes())
    print(f"{len(made)} letters, capital height {a.cap}, used {y + row_h} of {ATLAS} rows")


if __name__ == "__main__":
    main()
