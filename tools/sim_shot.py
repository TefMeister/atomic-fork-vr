#!/usr/bin/env python3
"""sim_shot.py -- keep one left-eye picture of a rung that is ALREADY running on the OpenXR Simulator
(started with `rung_simcheck.py ... --stay`), optionally with a part of it enlarged.

    python sim_shot.py <out.png> [--crop x0 y0 x1 y1] [--zoom 3]

The picture is the one the VR mod hands to the headset (the simulator's own capture, as rung_simcheck takes it);
nothing of the desktop is photographed, nothing is pressed. --crop is in the eye picture's own pixels.
Built 2026-11-19 for the water line at the "Save 4" spot (the water is at about 150 280 510 360 with the head straight).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("out")
    ap.add_argument("--crop", nargs=4, type=int)
    ap.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    import rung_simcheck as rs
    from PIL import Image
    im = rs.sim_picture()
    if im is None:
        sys.exit("no picture from the simulator: is the rung running?")
    if a.crop:
        im = im.crop(tuple(a.crop))
        im = im.resize((im.width * a.zoom, im.height * a.zoom), Image.LANCZOS)
    im.save(a.out)
    print(f"kept {a.out} {im.size[0]}x{im.size[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
