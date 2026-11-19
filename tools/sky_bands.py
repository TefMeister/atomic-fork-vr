#!/usr/bin/env python3
"""sky_bands.py -- photograph the sky of a rung that is ALREADY running on the OpenXR Simulator while the light
changes, and measure the "rings" (colour banding) in it. Nobody in the headset.

    python sky_bands.py --out <folder> [--shots 36] [--every 4] [--label "rung 5"]

Before it: tilt the pretend head up (vb_sim.head(0, 1.7, 0, 0, 35)) and set the game's clock going from its console
(`set gamehour to 4`, `set timescale to 120`: one game hour every 30 s), then start this. It only takes pictures.

A ring is a place where the sky's brightness, which should rise smoothly from the top of the sky to the horizon,
jumps by a whole step and then stays flat for a while. For every picture the sky part of the left eye is reduced to
one brightness per row (the MEDIAN of the row, so stars and cloud specks do not count) and per colour channel, and
these are printed:
    levels      how many different brightness values the sky uses from top to bottom (few = coarse steps)
    widest      the widest flat band, in rows of the picture and in degrees of the view
    jump        the biggest single step between two neighbouring bands, in 8-bit levels (1 = the least a screen can show)
    grain       how much neighbouring pixels differ inside the bands (0 = perfectly flat bands, nothing hides the steps)
It keeps every picture (`sky NN.png`) and a table (`sky_bands.csv`) in --out.

Built 2026-11-19 on Tefa's ask: "it has these visible rings forming as the sky gets brighter or dimmer".
"""
import argparse
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SETTINGS = {
    "sky_box": (60, 15, 500, 330),   # the sky in the eye picture with the head tilted up 35 degrees (left, top, right, bottom)
    "eye_rows": 604,                 # rows of the eye picture
    "eye_deg": 100.0,                # about what the eye picture covers top to bottom (TTWVR's 52.5 up + 47.5 down)
}


def measure(im):
    """the four numbers for one picture; im is the whole left eye (RGB)"""
    l, t, r, b = SETTINGS["sky_box"]
    sky = im.crop((l, t, r, b))
    w, h = sky.size
    px = sky.load()
    out = {}
    worst = None
    for ci, cname in enumerate("RGB"):
        prof = []
        for y in range(h):
            row = sorted(px[x, y][ci] for x in range(w))
            prof.append(row[w // 2])
        bands, start = [], 0                       # (value, rows)
        for y in range(1, h + 1):
            if y == h or prof[y] != prof[start]:
                bands.append((prof[start], y - start))
                start = y
        levels = len(set(prof))
        widest = max(n for _, n in bands)
        jump = max((abs(bands[i + 1][0] - bands[i][0]) for i in range(len(bands) - 1)), default=0)
        out[cname] = (levels, widest, jump)
        if worst is None or widest > worst[1]:
            worst = (cname, widest, jump, levels)
    grain, n = 0.0, 0                              # mean difference between side-by-side pixels (green)
    for y in range(0, h, 3):
        for x in range(0, w - 1, 3):
            grain += abs(px[x, y][1] - px[x + 1, y][1])
            n += 1
    mid = px[w // 2, h // 2]
    return {"channel": worst[0], "levels": worst[3], "widest_rows": worst[1],
            "widest_deg": round(worst[1] * SETTINGS["eye_deg"] / SETTINGS["eye_rows"], 2), "jump": worst[2],
            "grain": round(grain / max(n, 1), 3), "sky_mid": "%d %d %d" % mid}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots", type=int, default=36)
    ap.add_argument("--every", type=float, default=4.0)
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    import rung_simcheck as rs
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for i in range(a.shots):
        t = time.time()
        im = rs.sim_picture()
        if im is None:
            print(f"{i:02d}: no picture", flush=True)
        else:
            im.save(os.path.join(a.out, f"sky {i:02d}.png"))
            m = measure(im)
            m["shot"] = i
            rows.append(m)
            print(f"{i:02d}: sky {m['sky_mid']:>11s}  levels {m['levels']:3d}  widest band {m['widest_rows']:3d} rows "
                  f"({m['widest_deg']:4.1f} deg, {m['channel']})  jump {m['jump']}  grain {m['grain']}", flush=True)
        time.sleep(max(0.0, a.every - (time.time() - t)))
    if rows:
        with open(os.path.join(a.out, "sky_bands.csv"), "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=["shot", "sky_mid", "channel", "levels", "widest_rows", "widest_deg", "jump", "grain"])
            wr.writeheader()
            wr.writerows(rows)
    return 0 if rows else 1


if __name__ == "__main__":
    sys.exit(main())
