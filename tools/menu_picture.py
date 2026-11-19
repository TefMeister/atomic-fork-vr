#!/usr/bin/env python3
"""menu_picture.py -- turn a picture into the main menu's background file (main_background.dds).

    python menu_picture.py <picture.png> <out main_background.dds> [--size 1920x1080]

The game's file is 1920 x 1080. The picture is resized to exactly that when its shape differs by less than
SHAPE_TOLERANCE; otherwise it is fitted inside and padded with black (it is never cropped), and the tool says which.
Written uncompressed (32-bit, no mip levels) so soft fades keep every level.
"""
import struct
import sys
from PIL import Image

SHAPE_TOLERANCE = 0.005   # up to half a percent of stretch counts as "the same shape"


def dds_header(w, h):
    DDSD = 0x1 | 0x2 | 0x4 | 0x8 | 0x1000            # caps, height, width, pitch, pixel format
    pf = struct.pack("<II4sIIIII", 32, 0x40, b"\0\0\0\0", 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0)   # X8R8G8B8
    return b"DDS " + struct.pack("<IIIIIII", 124, DDSD, h, w, w * 4, 0, 0) + b"\0" * 44 + pf + struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit(__doc__)
    W, H = 1920, 1080
    if "--size" in sys.argv:
        W, H = (int(x) for x in sys.argv[sys.argv.index("--size") + 1].lower().split("x"))
    im = Image.open(args[0]).convert("RGB")
    stretch = (im.width / im.height) / (W / H) - 1
    if abs(stretch) <= SHAPE_TOLERANCE:
        out = im.resize((W, H), Image.LANCZOS)
        print(f"{im.width} x {im.height} -> {W} x {H}: resized whole, no crop, no padding (shape differs by {abs(stretch) * 100:.2f} %)")
    else:
        k = min(W / im.width, H / im.height)
        small = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        out = Image.new("RGB", (W, H))
        out.paste(small, ((W - small.width) // 2, (H - small.height) // 2))
        print(f"{im.width} x {im.height} -> {small.width} x {small.height} inside {W} x {H}: PADDED with black, not cropped")
    with open(args[1], "wb") as f:
        f.write(dds_header(W, H) + out.convert("RGBA").tobytes("raw", "BGRA"))


if __name__ == "__main__":
    main()
