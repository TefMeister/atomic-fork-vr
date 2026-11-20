#!/usr/bin/env python3
"""sky_dome_dither.py -- add fine grain where the SKY DOME is drawn (SKY.pso), not only at the tonemapper.

    python sky_dome_dither.py --lff <LOD Flicker Fix's Shaders/Loose folder> <out folder> [--levels 1.0]
    python sky_dome_dither.py --vanilla <the game's SKY.pso (ps_3_0)> <out folder> [--levels 1.0]

Why: the grain at the tonemapper (dither_pso.py, the mod `Bridge - smooth sky`) made the rings much softer but
they still show (Tefa 2026-11-20, 24 h timelapse). Inside each ring there are thin lines one level off (2026-11-19):
two roundings one after the other. The sky dome's colour is rounded once when it is written into the game's
picture; grain added only after that cannot hide that first step. Here the grain goes in where the dome is drawn.

Two shapes, because the sky shader must match the step before it:
  --lff      LOD Flicker Fix replaces SKY.vso / SKY.pso with an older kind (vs_2_0 / ps_2_x) that has no screen
             position in the pixel step. Its SKY.vso is changed to hand the screen position over (oT0), and its
             SKY.pso adds grain from it. Both go into our mod, which must win over LOD Flicker Fix.
  --vanilla  the game's own SKY.pso (ps_3_0, used when LOD Flicker Fix is off, as in the VR rungs): grain from vPos.
The grain: interleaved gradient noise (as dither_pso.py), +- half of --levels steps of 1/255. Built 2026-11-20, FO-012.
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dither_pso import asm, dis

SETTINGS = {"noise_a": (0.06711056, 0.00583715), "noise_b": 52.9829189,
            "screen": (3440.0, 1440.0)}   # only scales the noise's grid; any size still gives per-pixel noise


def keep_ctab(orig, code):
    _, tok = struct.unpack_from("<II", orig, 0)
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    return code


def body(text):
    return [ln.rstrip("\r") for ln in text.replace("\x00", "").split("\n") if ln.strip() and not ln.strip().startswith("//")]


def lff(src, out, levels):
    a, b = SETTINGS["noise_a"], SETTINGS["noise_b"]
    # the vertex step: also hand over the clip position (x, y, w) in oT0
    vo = open(os.path.join(src, "SKY.vso"), "rb").read()
    v = body(dis(vo))
    assert v[0].strip() == "vs_2_0" and any("oPos.zw, r0.x" in ln for ln in v), "LOD Flicker Fix's SKY.vso is not the known shape"
    v += ["    dp4 r1.x, c0, v0", "    dp4 r1.y, c1, v0", "    mov r1.z, c2.z", "    mov r1.w, r0.x", "    mov oT0, r1"]
    open(os.path.join(out, "SKY.vso"), "wb").write(keep_ctab(vo, asm("\n".join(v) + "\n")))
    po = open(os.path.join(src, "SKY.pso"), "rb").read()
    p = body(dis(po))
    assert p[0].strip() == "ps_2_x" and p[-1].strip() == "mov oC0, r0", "LOD Flicker Fix's SKY.pso is not the known shape"
    sx, sy = SETTINGS["screen"]
    p = ["    ps_2_x",
         f"    def c10, {a[0]}, {a[1]}, {b}, -0.5",
         f"    def c11, 0.5, {sx}, {sy}, {levels / 255.0:.9f}",
         "    def c12, 0, 0, 0, 0",
         "    dcl v0",
         "    dcl t0"] + [ln for ln in p[1:-1] if not ln.strip().startswith("dcl")] + [
         "    rcp r1.w, t0.w",
         "    mul r1.xy, t0, r1.w",
         "    mad r1.xy, r1, c11.x, c11.x",
         "    mul r1.x, r1.x, c11.y",
         "    mul r1.y, r1.y, c11.z",
         "    mov r2.x, c12.x",
         "    dp2add r1.z, r1, c10, r2.x",
         "    frc r1.z, r1.z",
         "    mul r1.z, r1.z, c10.z",
         "    frc r1.z, r1.z",
         "    add r1.z, r1.z, c10.w",
         "    mad r0.xyz, r1.z, c11.w, r0",
         "    mov oC0, r0"]
    open(os.path.join(out, "SKY.pso"), "wb").write(keep_ctab(po, asm("\n".join(p) + "\n")))


def vanilla(src, out, levels):
    a, b = SETTINGS["noise_a"], SETTINGS["noise_b"]
    po = open(src, "rb").read()
    p = body(dis(po))
    assert p[0].strip() == "ps_3_0" and "mul oC0.xyz, c4.y, v0" in [ln.strip() for ln in p], "the game's SKY.pso is not the known shape"
    p = [ln.replace("mul oC0.xyz, c4.y, v0", "mul r0.xyz, c4.y, v0") for ln in p]
    i = next(k for k, ln in enumerate(p) if "mul r0.xyz, c4.y, v0" in ln)
    p[i + 1:i + 1] = ["    mov r2.x, c12.x",
                      "    dp2add r1.x, vPos, c10, r2.x",
                      "    frc r1.x, r1.x",
                      "    mul r1.x, r1.x, c10.z",
                      "    frc r1.x, r1.x",
                      "    add r1.x, r1.x, c10.w",
                      "    mul r1.x, r1.x, c11.w",
                      "    add oC0.xyz, r0, r1.x"]
    p[1:1] = [f"    def c10, {a[0]}, {a[1]}, {b}, -0.5", f"    def c11, 0, 0, 0, {levels / 255.0:.9f}", "    def c12, 0, 0, 0, 0",
              "    dcl vPos.xy"]
    open(os.path.join(out, "SKY.pso"), "wb").write(keep_ctab(po, asm("\n".join(p) + "\n")))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--lff"); g.add_argument("--vanilla")
    ap.add_argument("out"); ap.add_argument("--levels", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    (lff if a.lff else vanilla)(a.lff or a.vanilla, a.out, a.levels)
    for f in sorted(os.listdir(a.out)):
        print(f"{a.out}/{f}:", "  ".join(ln.strip() for ln in body(dis(open(os.path.join(a.out, f), "rb").read()))[-4:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
