#!/usr/bin/env python3
"""water_probe.py -- make every water shader paint its own settings on the screen as vertical stripes, so the near
water and the far water can be compared in ONE picture (same light, same tonemapper, same frame).

    python water_probe.py <folder with the game's WATERnnn.pso> <out folder> [--reps 3]
    python water_probe.py --read <picture.png> [--reps 3]          say what each stripe shows, near against far

Why: three fades (water_blend.py, 2026-11-19) failed because the far water is drawn with numbers we had never seen.
Here each shader still works out its normal colour, then writes a stripe pattern instead. The screen is cut into
--reps repeats of 12 stripes (the pattern repeats so that every stripe crosses the line somewhere on the lake):

    0  which shader drew this pixel: six thin columns, the shader's number in binary (white = 1, left = lowest bit)
    1  ShallowColor     2  DeepColor     3  ReflectionColor     4  FogColor
    5  FresnelRI.xyz    6  VarAmounts.xyz      7  FogParam.xyz / 65536      8  SunColor
    9  the vertex alpha (grey)     10  the shader's own colour     11  the shader's own alpha (grey)

A setting the shader does not have paints magenta. Alpha is written as 1, so the stripes are not mixed with what lies
under the water. The tonemapper still changes the colours, so the picture answers "same or different, and which
way", not exact numbers. Where a stripe has the same colour on both sides of the line, that setting is the same for
the near and the far water. Our own output only; the game's files are only read. Built 2026-11-20, board row FO-002.
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dither_pso import asm, dis

SETTINGS = {
    "width": 3440,          # the flat window (OneTweak, borderless, the whole screen)
    "reps": 3,
    "bits": 6,
    "fog_scale": 1.0 / 65536,
}
BANDS = ["ID", "ShallowColor", "DeepColor", "ReflectionColor", "FogColor", "FresnelRI", "VarAmounts", "FogParam",
         "SunColor", "valpha", "own colour", "own alpha"]


def shader_number(name):
    return int(re.search(r"(\d+)", name).group(1))


def probe(src, dst, reps):
    orig = open(src, "rb").read()
    text = dis(orig)
    reg = dict(re.findall(r"//\s+(\w+)\s+(c\d+)\s+\d+\s*$", text, re.M))
    lines = [ln.rstrip("\r") for ln in text.replace("\x00", "").split("\n") if ln.strip() and not ln.strip().startswith("//")]
    if not any("oC0" in ln for ln in lines):
        return "writes no colour"
    body = " ".join(lines)
    t = max((int(x) for x in re.findall(r"\br(\d+)(?:_abs)?\b", body)), default=-1) + 1
    if t + 4 > 31:
        return "no spare registers"
    N, T, R, V = (f"r{t + i}" for i in range(4))
    c = max((int(x) for x in re.findall(r"\bc(\d+)\b", text)), default=-1) + 1
    va = None
    for ln in lines:
        m = re.match(r"\s*dcl_texcoord6(?:_centroid)? (v\d+)", ln)
        if m:
            va = m.group(1)
    num = shader_number(os.path.basename(src))
    period = SETTINGS["width"] / reps
    # constants: cZ zero, cO one, cM magenta, cS (1/period*12, fog scale), then the stripe starts, 4 to a register
    cZ, cO, cM, cS = (f"c{c + i}" for i in range(4))
    starts = []                                     # (start in stripe units 0..12, value source)
    sub = 1.0 / SETTINGS["bits"]
    for j in range(SETTINGS["bits"]):
        starts.append((j * sub, cO if (num >> j) & 1 else cZ))
    for i in range(1, 12):
        starts.append((float(i), i))
    k0 = c + 4
    start_regs = []
    defs = [f"    def {cZ}, 0, 0, 0, 1", f"    def {cO}, 1, 1, 1, 1", f"    def {cM}, 1, 0, 1, 1",
            f"    def {cS}, {12.0 / period:.9f}, {SETTINGS['fog_scale']:.9f}, {1 / 12.0:.9f}, 12"]
    for g in range(0, len(starts), 4):
        chunk = [s for s, _ in starts[g:g + 4]] + [0.0] * (4 - len(starts[g:g + 4]))
        defs.append(f"    def c{k0 + g // 4}, " + ", ".join(f"{x:.6f}" for x in chunk))
        start_regs.append(f"c{k0 + g // 4}")
    if k0 + len(start_regs) > 223:
        return "no spare constants"

    def value(i):
        """lines that put stripe i's value into V"""
        if isinstance(i, str):
            return [f"    mov {V}, {i}"]
        name = BANDS[i]
        if name in ("ShallowColor", "DeepColor", "ReflectionColor", "FogColor", "FresnelRI", "VarAmounts", "SunColor"):
            return [f"    mov {V}, {reg[name]}"] if name in reg else [f"    mov {V}, {cM}"]
        if name == "FogParam":
            return [f"    mov {V}, {reg[name]}", f"    mul {V}, {V}, {cS}.y"] if name in reg else [f"    mov {V}, {cM}"]
        if name == "valpha":
            return [f"    mov {V}, {va}.w"] if va else [f"    mov {V}, {cM}"]
        if name == "own colour":
            return [f"    mov {V}, {N}"]
        if name == "own alpha":
            return [f"    mov {V}, {N}.w"]
        raise ValueError(name)

    out = [ln.replace("oC0", N) for ln in lines]
    # f = frac(x / period) * 12: which stripe this pixel is in
    tail = [f"    mul {T}.x, vPos.x, {cS}.x",           # x * 12 / period
            f"    mul {T}.y, {T}.x, {cS}.z",            # / 12
            f"    frc {T}.y, {T}.y",
            f"    mul {T}.x, {T}.y, {cS}.w"]            # * 12
    tail += value(starts[0][1])
    tail += [f"    mov {R}, {V}"]
    for idx, (s, src_) in enumerate(starts[1:], start=1):
        comp = "xyzw"[idx % 4]
        tail += value(src_)
        tail += [f"    add {T}.z, {T}.x, -{start_regs[idx // 4]}.{comp}",
                 f"    cmp {R}, {T}.z, {V}, {R}"]
    tail += [f"    mov oC0.xyz, {R}", f"    mov oC0.w, {cO}.x"]
    out += tail
    ver = next(i for i, ln in enumerate(out) if ln.strip() == "ps_3_0")
    out[ver + 1:ver + 1] = defs
    if not any(re.match(r"\s*dcl vPos", ln) for ln in out):
        first_dcl = next((i for i, ln in enumerate(out) if ln.strip().startswith(("dcl", "mov", "add", "mul", "mad", "texld"))), len(out))
        out.insert(first_dcl, "    dcl vPos.xy")
    code = asm("\n".join(out) + "\n")
    _, tok = struct.unpack_from("<II", orig, 0)
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    open(dst, "wb").write(code)
    return ""


def read(png, reps):
    """per stripe: the colour on each side of the line, found as the two biggest colour groups in that stripe's water"""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    W, H = im.size
    period = W / reps
    px = im.load()
    print(f"{png}: {W}x{H}")
    for r in range(reps):
        for b in range(12):
            x0, x1 = int(r * period + b * period / 12) + 4, int(r * period + (b + 1) * period / 12) - 4
            if b == 0:
                continue
            counts = {}
            for y in range(0, H, 2):
                for x in range(x0, x1, 3):
                    col = px[x, y]
                    q = (col[0] // 4 * 4, col[1] // 4 * 4, col[2] // 4 * 4)
                    counts[q] = counts.get(q, 0) + 1
            top = sorted(counts.items(), key=lambda kv: -kv[1])[:3]
            print(f"  rep {r} stripe {b:2d} {BANDS[b]:16s} " + "  ".join(f"{k}x{v}" for k, v in top))


def main(argv):
    reps = int(argv[argv.index("--reps") + 1]) if "--reps" in argv else SETTINGS["reps"]
    if argv and argv[0] == "--read":
        read(argv[1], reps)
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 1
    src, out = argv[0], argv[1]
    os.makedirs(out, exist_ok=True)
    done, left = [], []
    for name in sorted(os.listdir(src)):
        if not re.fullmatch(r"WATER\d+\.pso", name, re.I):
            continue
        why = probe(os.path.join(src, name), os.path.join(out, name), reps)
        (left if why else done).append(name + (f" ({why})" if why else ""))
    print(f"{len(done)} probe shaders written to {out}")
    if left:
        print("left alone: " + "; ".join(left))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
