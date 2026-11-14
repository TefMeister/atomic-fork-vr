"""clip_flickers.py -- find one-frame blinks in a Virtual Desktop clip of Tefa's, with Flickers BeG0nE's reader.

    python clip_flickers.py <clip.mp4> <work folder> [--width 1200]

The reader (BeG0nE flickers/tools/flicker_read.py) reads a catcher dump: numbered pictures per eye plus a frames.txt
of head poses. A Virtual Desktop clip is one view with no poses, so this writes every frame as a picture of one "eye"
with blank poses (the reader lines up head motion itself, by phase correlation), runs the reader, then draws each odd
frame between its neighbours with the pixels that only that frame has marked pink (odd.jpg), since the reader's own
sheet does not mark them. Built 2026-11-14 for Tefa's rung-5 clip (`...212457-0.mp4`): the blinking was small rocks
next to the big rock's edge missing for one frame.

Frames go to <work folder> (about 2 MB each at 1200 wide: a 10 s clip at 60 fps is ~1.3 GB): use a scratch folder.
"""
import argparse, os, subprocess, sys

import cv2
import numpy as np

READER_DIR = os.path.expanduser("~/github-backups/BeG0nE/flickers/tools")
SHOWN = 6   # odd frames drawn in odd.jpg, highest share first


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clip")
    ap.add_argument("work")
    ap.add_argument("--width", type=int, default=1200)
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    if any(n.endswith(".ppm") for n in os.listdir(a.work)):
        sys.exit("the work folder already has pictures: use an empty one")
    subprocess.run(["ffmpeg", "-v", "error", "-i", a.clip, "-vf", "scale=%d:-2" % a.width, "-start_number", "0",
                    os.path.join(a.work, "frame-0-%02d.ppm")], check=True)
    n = sum(1 for x in os.listdir(a.work) if x.endswith(".ppm"))
    h, w = cv2.imread(os.path.join(a.work, "frame-0-00.ppm")).shape[:2]
    with open(os.path.join(a.work, "frames.txt"), "w") as f:
        f.write("# from a Virtual Desktop clip: one view, no pose data (poses blank)\n")
        for k in range(n):
            f.write("%d 0 0 0 0 0 0 0 1 0 0 0 0 %d 0 0 %d %d 0 0\n" % (k, k, w, h))
    subprocess.run([sys.executable, "-I", os.path.join(READER_DIR, "flicker_read.py"), a.work], check=True)
    sys.path.insert(0, READER_DIR)
    import flicker_read as fr
    rep = fr.read_dump(a.work)
    rows = []
    for o in sorted(rep["odd"], key=lambda o: -o["share"])[:SHOWN]:
        k = o["index"]
        p, c, nx = (fr.read_rgb(os.path.join(a.work, "frame-0-%02d.ppm" % i)) for i in (k - 1, k, k + 1))
        m = fr.odd_mask(p, c, nx)
        ov = c.copy()
        ov[m > 0] = (255, 0, 255)
        row = np.hstack([p, ov, nx])
        cv2.putText(row, "frame %d (clip %.2f s) share %.2f" % (k, k / 60.0, o["share"]), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        rows.append(row)
    if rows:
        sheet = np.vstack(rows)
        sheet = cv2.resize(sheet, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imwrite(os.path.join(a.work, "odd.jpg"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("odd.jpg: each odd frame between its neighbours, its own changes in pink")
    return 0


if __name__ == "__main__":
    sys.exit(main())
