#!/usr/bin/env python3
"""sim_smudge.py -- a smudge meter for a rung that is ALREADY running on the OpenXR Simulator
(started with `rung_simcheck.py ... --stay`). Nobody in the headset.

    python sim_smudge.py --vrbench <lanes tools/vrbench folder> --out <folder> [--label "test G"]

What it does: takes the left-eye picture the VR mod hands to the headset (the simulator's own capture, as
rung_simcheck does) a number of times with the head STILL, then the same number while the head SWAYS slowly from side
to side (the way a person's head does: a few centimetres, a couple of degrees), and says how much fine detail each set
holds. A picture that smears when the head moves loses fine detail in the moving set; one that stays clean keeps it.

It prints, for the whole picture and for three bands (far = the skyline band, middle, near):
    detail still / detail moving / the ratio moving:still (1.00 = no loss; lower = smeared)
and "frame-to-frame jump": how much two moving pictures in a row differ beyond the sway itself is NOT judged here.
It keeps `still.jpg` and `moving.jpg` (the middle picture of each set) in --out. It closes nothing and presses nothing.

Built 2026-11-19 for the rung-5 smudge (test copies A to G): Tefa sees it in the headset; this asks whether the desk
can see it too. Whether it can is itself the first result: read the note of that day before trusting a number.
"""
import argparse
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SETTINGS = {
    "shots": 14,             # pictures per set
    "head_height_m": 1.7,    # the simulator's default standing head
    "sway_m": 0.06,          # side to side, each way
    "sway_yaw_deg": 3.0,     # the small turn that goes with it
    "sway_period_s": 2.4,    # one full left-right-left
    "step_s": 0.03,          # how often the head is moved while swaying
    "settle_s": 1.5,         # head back to the middle before the still set
    "bands": (("far", 0.30, 0.50), ("middle", 0.50, 0.70), ("near", 0.70, 0.95)),   # rows of the eye, top = 0
}


def detail(im, top=0.0, bottom=1.0):
    """mean strength of the finest detail (a 3x3 edge filter) in a band of rows of the picture"""
    from PIL import ImageFilter, ImageStat
    g = im.convert("L")
    g = g.crop((0, int(g.height * top), g.width, int(g.height * bottom)))
    return ImageStat.Stat(g.filter(ImageFilter.FIND_EDGES)).mean[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--vrbench", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    sys.path.insert(0, a.vrbench)
    import vb_sim
    import rung_simcheck as rs
    s = SETTINGS
    os.makedirs(a.out, exist_ok=True)

    vb_sim.head(0, s["head_height_m"], 0, 0, 0)
    time.sleep(s["settle_s"])
    still = [im for im in (rs.sim_picture() for _ in range(s["shots"])) if im is not None]

    moving, t0 = [], time.time()
    while len(moving) < s["shots"] and time.time() - t0 < 120:
        # sway for a short while, then ask for a picture while still swaying (the request is taken mid-move)
        t1 = time.time()
        while time.time() - t1 < 0.35:
            ph = 2 * math.pi * (time.time() - t0) / s["sway_period_s"]
            vb_sim.head(s["sway_m"] * math.sin(ph), s["head_height_m"], 0, s["sway_yaw_deg"] * math.sin(ph), 0)
            time.sleep(s["step_s"])
        im = rs.sim_picture(timeout=3.0)
        if im is not None:
            moving.append(im)
    vb_sim.head(0, s["head_height_m"], 0, 0, 0)

    if not still or not moving:
        sys.exit(f"no pictures from the simulator (still {len(still)}, moving {len(moving)}): is the rung running?")
    print(f"smudge meter {a.label}: {len(still)} still, {len(moving)} moving pictures, {still[0].size[0]}x{still[0].size[1]}")
    for name, top, bottom in (("whole", 0.0, 1.0),) + s["bands"]:
        ds = sum(detail(im, top, bottom) for im in still) / len(still)
        dm = sum(detail(im, top, bottom) for im in moving) / len(moving)
        print(f"  {name:6s} detail still {ds:6.2f}  moving {dm:6.2f}  moving:still {dm / ds if ds else 0:4.2f}")
    still[len(still) // 2].save(os.path.join(a.out, "still.jpg"), quality=90)
    moving[len(moving) // 2].save(os.path.join(a.out, "moving.jpg"), quality=90)
    return 0


if __name__ == "__main__":
    sys.exit(main())
