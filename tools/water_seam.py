#!/usr/bin/env python3
"""water_seam.py -- close the hairline gap where the near water meets the far water: every water tile is made a few
units bigger on its far sides, so neighbouring tiles overlap instead of leaving a crack.

    python water_seam.py <folder with the game's WATER00n.vso> <out folder> [--grow 16]

Why (Tefa 2026-11-20, from the 24 h timelapse: "the water line is still there, like a black line going through it"):
once water_blend.py made the near and far water the same colour, a 1-pixel dark line stayed on the old border, in
some columns only. It was there before too. Nothing is drawn on those pixels, so the lake bed shows: a crack between
the near water's tiles and the far water's, which meet edge to edge but not exactly.

What it does: the water's three vertex shaders (WATER000-002.vso, used by near and far water alike) move every corner
of a tile that lies above 0.5 in the tile's own x or y by --grow units, before anything else uses the position. The
tiles are measured from their own corner (2026-11-20: a probe painting the near water by its own position showed the
colour running 0..1 across each cell and jumping at the cell edges), so each tile grows on its two far sides and
overlaps the next tile, near or far. Everything the water draws is worked out from the moved position (waves, the
mirror picture, the distance), so where two tiles overlap they paint the same picture.
Built 2026-11-20, board row FO-002.
"""
import argparse
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dither_pso import asm, dis

SETTINGS = {"grow": 64.0, "from": 0.0, "to": 1.0, "all_sides": True, "only": ("WATER000.vso",),   # 2026-11-20: only the FAR water's tiles (WATER000.vso; the near water uses 001), on all four sides, always   # grow only from these view depths on (clip w = depth straight ahead,
            # about 0.57 of the true distance at the edge of an ultrawide view; the border is at least 8192 away). Nearer, where the water is most see-through,
            "shaders": ("WATER000.vso", "WATER001.vso", "WATER002.vso")}   # overlapping tiles showed as light lines (2026-11-20)


def seam(src, dst, grow):
    orig = open(src, "rb").read()
    lines = [ln.rstrip("\r") for ln in dis(orig).replace("\x00", "").split("\n") if ln.strip() and not ln.strip().startswith("//")]
    assert lines[0].strip() == "vs_1_1", src
    body = " ".join(lines)
    regs = [int(x) for x in re.findall(r"\br(\d+)", body)]
    consts = [int(x) for x in re.findall(r"\bc(\d+)", dis(orig))]
    rf, rp, rd, c, c2 = f"r{max(regs) + 1}", f"r{max(regs) + 2}", f"r{max(regs) + 3}", f"c{max(consts) + 1}", f"c{max(consts) + 2}"
    assert max(regs) + 3 <= 11 and max(consts) + 2 < 96, "no spare registers"
    pos = next(re.match(r"\s*dcl_position (v\d+)", ln).group(1) for ln in lines if re.match(r"\s*dcl_position", ln))
    first = next(i for i, ln in enumerate(lines) if not ln.strip().startswith(("vs_", "def", "dcl")))
    out = lines[:first] + [f"    dp4 {rd}.x, c3, {pos}",                  # the corner's distance from the eye (clip w)
                           f"    mad {rd}.x, {rd}.x, {c}.z, {c}.w",       # 0 at 'from', 1 at 'to'
                           f"    max {rd}.x, {rd}.x, {c2}.x",
                           f"    min {rd}.x, {rd}.x, {c2}.y",
                           f"    mul {rd}.x, {rd}.x, {c}.x",              # how far this corner moves
                           f"    slt {rf}.xy, {c}.y, {pos}.xy",           # 1 where the corner is on the tile's far side
                           ] + ([f"    add {rf}.xy, {rf}, {rf}",                # all sides: -1 on the near side, +1 on the far side
                                 f"    add {rf}.xy, {rf}, -{c2}.y"] if SETTINGS.get("all_sides") else []) + [
                           f"    mad {rp}.xy, {rf}, {rd}.x, {pos}",
                           f"    mov {rp}.zw, {pos}"]
    out += [re.sub(rf"\b{pos}\b", rp, ln) for ln in lines[first:]]
    ver = next(i for i, ln in enumerate(out) if ln.strip() == "vs_1_1")
    span = SETTINGS["to"] - SETTINGS["from"]
    out[ver + 1:ver + 1] = [f"    def {c}, {grow:.4f}, 0.5, {1.0 / span:.9f}, {-SETTINGS['from'] / span:.6f}",
                            f"    def {c2}, 0, 1, 0, 0"]
    code = asm("\n".join(out) + "\n")
    _, tok = struct.unpack_from("<II", orig, 0)
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    open(dst, "wb").write(code)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--grow", type=float, default=SETTINGS["grow"])
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for n in SETTINGS.get("only") or SETTINGS["shaders"]:
        seam(os.path.join(a.src, n), os.path.join(a.out, n), a.grow)
        print(n, "written, tiles grow", a.grow, "units on their far sides")
    return 0


if __name__ == "__main__":
    sys.exit(main())
