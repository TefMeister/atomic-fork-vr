#!/usr/bin/env python3
"""water_bits.py -- make every water shader write chosen settings as BINARY stripes, so their exact values can be
read off a screenshot (black / grey survives the tonemapper, a colour does not).

    python water_bits.py <folder with WATERnnn.pso> <out folder> --set A|B [--x0 2110]
    python water_bits.py --read <picture.png> --set A|B [--x0 2110] [--rows y0,y1]

Each setting gets a block of 52 pixels: 4 magenta (the block's start), then 12 bits, 4 pixels each, highest bit
first; grey = 1, black = 0. The number is floor(value x scale), so value = number / scale. A setting the shader does
not have paints cyan. The blocks repeat every 13 x 52 pixels from --x0 (put x0 where the far water starts on the
screen, so one full row of blocks crosses it). Alpha is written as 1. Built 2026-11-20, board row FO-002, after
water_probe.py showed the near and far water get different colours.
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dither_pso import asm, dis

BLOCK, MARK, BITW, NBITS = 52, 4, 4, 12
FINE, COARSE = 2040.0, 16.0          # FINE: a colour byte b/255 reads as 8*b; COARSE: 0..256 in 1/16 steps
SETS = {
    "A": [("ShallowColor", c, FINE) for c in "xyz"] + [("DeepColor", c, FINE) for c in "xyz"] +
         [("ReflectionColor", c, FINE) for c in "xyz"] + [("FresnelRI", c, FINE) for c in "xyzw"],
    "B": [("VarAmounts", c, FINE) for c in "xyzw"] + [("FresnelRI", c, COARSE) for c in "xyzw"] +
         [("VarAmounts", c, COARSE) for c in "xyzw"] + [("SunDir", "w", FINE)],
}


def build(src, dst, qs, x0):
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
    period = BLOCK * len(qs)
    cA, cB, cMag, cCyan, cG = (f"c{c + i}" for i in range(5))
    idx_regs = [f"c{c + 5 + i}" for i in range((len(qs) + 3) // 4)]
    defs = [f"    def {cA}, {1.0 / period:.9f}, {period:.1f}, {1.0 / BLOCK:.9f}, {BLOCK:.1f}",
            f"    def {cB}, {-MARK:.1f}, {1.0 / BITW:.9f}, {-NBITS:.1f}, -0.5",
            f"    def {cMag}, 0.5, 0, 0.5, 1",
            f"    def {cCyan}, 0, 0.5, 0.5, 1",
            f"    def {cG}, 0.5, 0, {4095.0:.1f}, {period * 20 - x0:.1f}"]
    for g in range(0, len(qs), 4):
        vals = [float(i) for i in range(g, min(g + 4, len(qs)))] + [0.0] * (4 - min(4, len(qs) - g))
        defs.append(f"    def {idx_regs[g // 4]}, " + ", ".join(f"{v:.1f}" for v in vals))
    out = [ln.replace("oC0", N) for ln in lines]
    tail = [f"    add {T}.x, vPos.x, {cG}.w",                 # x - x0 (+ many periods, to stay positive)
            f"    mul {T}.x, {T}.x, {cA}.x",
            f"    frc {T}.x, {T}.x",
            f"    mul {T}.x, {T}.x, {cA}.y",                  # position in the pattern, 0..period
            f"    mul {T}.y, {T}.x, {cA}.z",
            f"    frc {T}.z, {T}.y",
            f"    add {T}.y, {T}.y, -{T}.z",                  # q = which setting
            f"    mul {T}.z, {T}.z, {cA}.w"]                  # xb = place in the block, 0..52
    # value of setting q into R.x (cyan flag in R.y: 1 = missing); one constant register per scale
    scale_regs, sc_defs = {}, []
    for name, comp, scale in qs:
        if scale not in scale_regs:
            scale_regs[scale] = f"c{c + 5 + len(idx_regs) + len(scale_regs)}"
            sc_defs.append(f"    def {scale_regs[scale]}, {scale:.4f}, 1, 0, 0")
    tail += [f"    mov {R}, {cMag}.y"]
    for i, (name, comp, scale) in enumerate(qs):
        tail += [f"    add {T}.w, {T}.y, -{idx_regs[i // 4]}.{'xyzw'[i % 4]}"]
        if name in reg:
            tail += [f"    mov {V}.x, {reg[name]}.{comp}",
                     f"    mul {V}.x, {V}.x, {scale_regs[scale]}.x",
                     f"    mov {V}.y, {cMag}.y"]
        else:
            tail += [f"    mov {V}.x, {cMag}.y", f"    mov {V}.y, {cMag}.x"]
        tail += [f"    cmp {R}.xy, {T}.w, {V}.xy, {R}.xy"]
    tail += [f"    frc {V}.z, {R}.x",
             f"    add {R}.x, {R}.x, -{V}.z",                  # n = floor(value * scale)
             f"    max {R}.x, {R}.x, {cMag}.y",
             f"    min {R}.x, {R}.x, {cG}.z",
             f"    add {T}.w, {T}.z, {cB}.x",                  # xb - 4
             f"    mul {V}.w, {T}.w, {cB}.y",
             f"    frc {V}.z, {V}.w",
             f"    add {V}.w, {V}.w, -{V}.z",                  # k = 0..11, highest bit first
             f"    add {V}.w, {V}.w, {cB}.z",                  # k - 12
             f"    exp {V}.w, {V}.w",                          # 2^(k-12) = 1 / 2^(j+1)
             f"    mul {V}.w, {R}.x, {V}.w",
             f"    frc {V}.w, {V}.w",
             f"    add {V}.w, {V}.w, {cB}.w",                  # >= 0 means the bit is 1
             f"    mov {T}.x, {cG}.x",
             f"    cmp {V}.xyz, {V}.w, {T}.x, {cMag}.y",
             f"    mov {V}.w, {R}.y",
             f"    add {V}.w, -{V}.w, {cMag}.y",               # -missing
             f"    cmp {V}.xyz, {V}.w, {V}, {cCyan}",
             f"    cmp {V}.xyz, {T}.w, {V}, {cMag}",           # the 4 magenta marker pixels
             f"    mov oC0.xyz, {V}",
             f"    mov oC0.w, {cMag}.w"]
    out += tail
    ver = next(i for i, ln in enumerate(out) if ln.strip() == "ps_3_0")
    out[ver + 1:ver + 1] = defs + sc_defs
    if not any(re.match(r"\s*dcl vPos", ln) for ln in out):
        first = next((i for i, ln in enumerate(out) if ln.strip().startswith(("dcl", "mov", "add", "mul", "mad", "texld"))), len(out))
        out.insert(first, "    dcl vPos.xy")
    code = asm("\n".join(out) + "\n")
    _, tok = struct.unpack_from("<II", orig, 0)
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    open(dst, "wb").write(code)
    return ""


def read(png, qs, x0, rows):
    """for every block start found in the rows, the number in each pixel row-run, grouped: what each setting reads"""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    px = im.load()
    W, H = im.size
    period = BLOCK * len(qs)
    y0, y1 = rows
    found = {}
    for x in range(W):
        p = (x - x0) % period
        if p % BLOCK != 0:
            continue
        q = p // BLOCK
        if x + BLOCK > W:
            continue
        for y in range(y0, y1):
            mark = [px[x + d, y] for d in range(1, 3)]
            if not all(m[0] > 35 and m[2] > 35 and m[1] < 20 for m in mark):
                continue
            bits = []
            ok = True
            for j in range(NBITS):
                cx = x + MARK + j * BITW + BITW // 2
                r, g, b = px[cx, y]
                if r < 25 and g < 25 and b < 25:
                    bits.append(0)
                elif r > 45 and g > 45 and b > 35 and abs(r - g) < 30:
                    bits.append(1)
                elif g > 35 and b > 35 and r < 20:
                    bits.append("C")
                else:
                    ok = False
                    break
            if not ok:
                continue
            if "C" in bits:
                val = "missing"
            else:
                n = int("".join(map(str, bits)), 2)
                val = n
            found.setdefault(q, {}).setdefault(val, []).append(y)
    for q, (name, comp, scale) in enumerate(qs):
        d = found.get(q, {})
        parts = []
        for val, ys in sorted(d.items(), key=lambda kv: min(kv[1])):
            if val == "missing":
                parts.append(f"missing (rows {min(ys)}-{max(ys)}, {len(ys)})")
            else:
                parts.append(f"{val}={val / scale:.5g} (rows {min(ys)}-{max(ys)}, {len(ys)})")
        print(f"  {name}.{comp} x{scale:g}: " + ("; ".join(parts) if parts else "not seen"))


def main(argv):
    s = argv[argv.index("--set") + 1] if "--set" in argv else "A"
    x0 = float(argv[argv.index("--x0") + 1]) if "--x0" in argv else 2110.0
    qs = SETS[s]
    if argv and argv[0] == "--read":
        rows = tuple(int(v) for v in argv[argv.index("--rows") + 1].split(",")) if "--rows" in argv else (900, 1300)
        read(argv[1], qs, int(x0), rows)
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 1
    os.makedirs(argv[1], exist_ok=True)
    done, left = [], []
    for name in sorted(os.listdir(argv[0])):
        if re.fullmatch(r"WATER\d+\.pso", name, re.I):
            why = build(os.path.join(argv[0], name), os.path.join(argv[1], name), qs, x0)
            (left if why else done).append(name + (f" ({why})" if why else ""))
    print(f"{len(done)} bit shaders (set {s}) written to {argv[1]}" + ("; left alone: " + "; ".join(left) if left else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
