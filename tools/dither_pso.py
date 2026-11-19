#!/usr/bin/env python3
"""dither_pso.py -- add fine noise to what a ps_3_0 tonemap shader writes, before the picture is rounded to 8 bits.

    python dither_pso.py <in.pso> <out.pso> [strength in 8-bit levels, default 1.0 = half a level each way]
    python dither_pso.py --show <file.pso>          print the shader taken apart

Why: a very gentle fade (the sky at dawn and dusk) rounded to 256 levels shows as rings. Noise of about half a level,
added BEFORE the rounding, turns each ring's edge into a speckle the eye averages out (dithering).

How: the shader is taken apart with Windows' own d3dcompiler_47.dll (D3DDisassemble), the final colour write is sent
through a spare register, interleaved-gradient noise made from the pixel's place on the screen (vPos) is added, and
it is put together again (D3DAssemble); the original's table of names (the CTAB comment block) is kept.
Works on shaders whose last colour write is either three `exp oC0.x / .y / .z` lines or one line writing `oC0.xyz`
(Vanilla Plus Tonemapper's three ISHDRBLENDINSHADER*.pso). Our own output only: the input file is never changed.
Built 2026-11-19 for the rings in the sky (board row FO-012).
"""
import ctypes
import re
import struct
import sys

SETTINGS = {
    "noise_a": (0.06711056, 0.00583715),   # interleaved gradient noise (Jimenez 2014): frac(52.98 * frac(dot(pos, a)))
    "noise_b": 52.9829189,
}

d3d = ctypes.WinDLL("d3dcompiler_47.dll")


def blob_bytes(b):
    vt = ctypes.cast(ctypes.cast(b, ctypes.POINTER(ctypes.c_void_p))[0], ctypes.POINTER(ctypes.c_void_p))
    get_ptr = ctypes.WINFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(vt[3])
    get_size = ctypes.WINFUNCTYPE(ctypes.c_size_t, ctypes.c_void_p)(vt[4])
    return ctypes.string_at(get_ptr(b), get_size(b))


def dis(data):
    out = ctypes.c_void_p()
    hr = d3d.D3DDisassemble(data, ctypes.c_size_t(len(data)), 0, None, ctypes.byref(out))
    if hr != 0:
        raise SystemExit("could not take the shader apart: " + hex(hr & 0xffffffff))
    return blob_bytes(out).decode("latin-1")


def asm(text):
    code, err, b = ctypes.c_void_p(), ctypes.c_void_p(), text.encode("latin-1")
    hr = d3d.D3DAssemble(b, ctypes.c_size_t(len(b)), None, None, None, 0, ctypes.byref(code), ctypes.byref(err))
    if hr != 0:
        raise SystemExit("could not put the shader together: " + (blob_bytes(err).decode("latin-1") if err else hex(hr & 0xffffffff)))
    return blob_bytes(code)


def dither(src, dst, strength=1.0):
    orig = open(src, "rb").read()
    text = dis(orig)
    lines = [ln for ln in text.split("\n") if ln.strip() and not ln.strip().startswith("//")]
    regs = [int(x) for x in re.findall(r"\br(\d+)(?:_abs)?\b", " ".join(lines))]
    consts = [int(x) for x in re.findall(r"\bc(\d+)\b", text)]
    r_col, r_noise = max(regs) + 1, max(regs) + 2
    c_a, c_b = max(consts) + 1, max(consts) + 2
    outs = [i for i, ln in enumerate(lines) if re.match(r"\s*\w+ oC0\.(x|y|z|xyz), ", ln)]
    if len(outs) not in (1, 3) or outs != list(range(outs[0], outs[0] + len(outs))):
        raise SystemExit(f"{src}: the final colour write is not a shape this tool knows (lines {outs})")
    new = [lines[i].replace("oC0.", f"r{r_col}.", 1) for i in outs]
    new += [f"    dp2add r{r_noise}.x, vPos, c{c_a}, c{c_a}.z",
            f"    frc r{r_noise}.x, r{r_noise}.x",
            f"    mul r{r_noise}.x, r{r_noise}.x, c{c_a}.w",
            f"    frc r{r_noise}.x, r{r_noise}.x",
            f"    add r{r_noise}.x, r{r_noise}.x, c{c_b}.x",
            f"    mad oC0.xyz, r{r_noise}.x, c{c_b}.y, r{r_col}"]
    lines[outs[0]:outs[0] + len(outs)] = new
    ver = next(i for i, ln in enumerate(lines) if ln.strip() == "ps_3_0")
    a = SETTINGS["noise_a"]
    lines[ver + 1:ver + 1] = [f"    def c{c_a}, {a[0]}, {a[1]}, 0, {SETTINGS['noise_b']}",
                              f"    def c{c_b}, -0.5, {strength / 255.0:.9f}, 0, 0"]
    first_dcl = next(i for i, ln in enumerate(lines) if ln.strip().startswith("dcl_"))
    lines.insert(first_dcl, "    dcl vPos.xy")
    code = asm("\n".join(lines) + "\n")
    _, tok = struct.unpack_from("<II", orig, 0)          # keep the names table right after the version token
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    open(dst, "wb").write(code)
    return dis(code)


def main(argv):
    if len(argv) == 2 and argv[0] == "--show":
        print(dis(open(argv[1], "rb").read()))
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 1
    out = dither(argv[0], argv[1], float(argv[2]) if len(argv) > 2 else 1.0)
    tail = [ln for ln in out.split("\n") if ln.strip() and not ln.strip().startswith("//")][-9:]
    print(f"{argv[1]}: written; its last lines:")
    print("\n".join(tail))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
