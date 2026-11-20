#!/usr/bin/env python3
"""water_blend.py -- fade the NEAR water into the FAR water's look before the border between them, so the straight
line across a lake goes.

    python water_blend.py <folder with the game's WATERnnn.pso> <out folder> [--from 5120] [--to 8192]
    python water_blend.py --unpack <shaderpackage.sdp> <folder>      pull the WATER shaders out of the game's package
                                                                      (for reading; never commit them)

What is wrong: the game draws water twice. Near the player (the loaded area, 5 x 5 cells) one of about 30 shaders
with waves, a real mirror picture, see-through shallows and depth haze. Beyond it a plain far-water shader
(WATER034: no waves, one fixed mirror colour). The near shaders already fade their WAVES out between 4096 and 8192
units so the two should meet, but the mirror picture, the see-through part and the haze do not fade: at the border
(8192 to 12288 units away, a straight cell edge) bright mirroring water meets a flat darker band.

What this does: to the end of every near shader it adds the far shader's own sum (a port of WATER034, with that
shader's own colours and fog) and mixes: all near water up to --from units, all far-water look from --to units, a
smooth change between. The border then joins two equal pictures.

How: Windows' own shader library takes each shader apart and puts it together again (as dither_pso.py). The
constants are found by NAME in each shader's own table, so each variant keeps its own register numbers. Variants
that lack a constant the far sum needs are left alone and listed. The game's files are only read.
Built 2026-11-19 (Tefa: "blend that line instead of it being sharp and straight"), board row FO-002.
2026-11-20 (fourth try, the one that works): the far sum is fed the FAR water's own numbers, measured in the game
with water_probe.py / water_bits.py (SETTINGS far_*), not the near water's; and only near water of the Capital
Wasteland's own types fades (SETTINGS fade_types, matched by ShallowColor), so any other water draws exactly as before.
Save 4, flat: the step at the line 14.5 -> 1 colour level (evening and noon); VR on the simulator: 11 -> about 1.
"""
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dither_pso import asm, dis

SETTINGS = {
    "fade_from": 5120.0,    # units from the eye where the near water starts to turn into the far look
    "fade_to": 8192.0,      # ... and where it IS the far look (the nearest the border can ever be with 5 x 5 cells)
    "need": ("EyePos", "ShallowColor", "DeepColor", "ReflectionColor", "FresnelRI", "VarAmounts", "FogParam", "FogColor"),
    "far_shaders": ("WATER033.pso", "WATER034.pso", "WATER035.pso"),   # the far water itself and the empty one
    # 2026-11-20: what the game REALLY feeds the far water in the Capital Wasteland, read off the screen with
    # water_bits.py (Save 4, flat, n=1): shallow and mirror colour are the Potomac record's bytes, but the deep colour
    # and two mixing amounts are the engine's own, not in any water record. Bytes / 255.
    "far_shallow": (52, 75, 52),
    "far_deep": (0, 16, 28),
    "far_reflection": (19, 37, 16),
    "far_varamounts_yz": (0.47, 0.7),      # near water: 0.6, 0.5 (the record's reflectivity, and ?)
    # only the near water of these types fades (their ShallowColor, bytes): the Capital Wasteland's own waters, whose
    # far water is the Potomac look above. Any other water (the Mojave's) is left exactly as it was.
    "fade_types": {"Potomac / DLC03TBPotomacWater": (52, 75, 52), "PotomacNRShallow": (95, 101, 48), "CreekWater01": (107, 92, 33)},
    "type_match": 0.01,    # sum of the three colour differences that still counts as the same water type
}

# WATER034's own sum, register names as placeholders. T0..T3 temps, TL the far result, TG the mix, N the near result.
FAR_SUM = """
    add {T0}.xyz, {EyePos}, -{vpos}
    dp3 {T0}.w, {T0}, {T0}
    rsq {T0}.w, {T0}.w
    mul {T1}.xyz, {T0}, {T0}.w
    rcp {T0}.z, {T0}.w
    add {T0}.z, -{T0}.z, {FogParam}.x
    dp2add {T0}.x, {T0}, {T0}, {K0}.x
    rsq {T0}.x, {T0}.x
    rcp {T0}.x, {T0}.x
    mad_sat {TG}.x, {T0}.x, {KB}.x, {KB}.y
    add {T0}.x, {T0}.x, {K0}.y
    mad_sat {T0}.x, {T0}.x, {K0}.z, {K0}.w
    add {T0}.x, {T0}.x, -{K0}.w
    mov_sat {T0}.y, {T1}.z
    mad {T1}.xyz, {T1}.z, {K1}.xxyw, -{T1}
SUN
    add {T0}.y, -{T0}.y, {K0}.w
    mul {T0}.w, {T0}.y, {T0}.y
    mul {T0}.w, {T0}.w, {T0}.w
    mul {T0}.y, {T0}.y, {T0}.w
    mov {T0}.w, {K0}.w
    lrp {T1}.w, {T0}.y, {T0}.w, {FresnelRI}.x
    lrp_sat {T2}.x, -{T0}.x, {T0}.w, {FV}.z
    mov {T3}.xyz, {FS}
    add {T0}.xyw, -{T3}.xyzz, {FD}.xyzz
    mad {T0}.xyw, {T2}.x, {T0}, {FS}.xyzz
    mul {TL}.w, {T2}.x, {valpha}.w
    lrp_sat {T2}.xyz, {T1}.w, {FR}, {T0}.xyww
SUNADD
    add {T1}.xyz, -{T0}.xyww, {FogColor}
    rcp {T1}.w, {FogParam}.y
    mul_sat {T0}.z, {T0}.z, {T1}.w
    add {T0}.z, -{T0}.z, {K0}.w
    pow {T1}.w, {T0}.z, {FresnelRI}.y
    mad {TL}.xyz, {T1}.w, {T1}, {T0}.xyww
GATE
    lrp oC0, {TG}.x, {N}, {TL}
"""
SUN_LINES = """    dp3_sat {T0}.w, {T1}, {SunDir}
    pow {T3}.x, {T0}.w, {VarAmounts}.x
    add {T0}.w, {T3}.x, {K1}.z
    mul {T1}.xyz, {T0}.w, {SunColor}"""
SUNADD_SUN = "    mad_sat {T0}.xyw, {T1}.xyzz, {SunDir}.w, {T2}.xyzz"
SUNADD_NONE = "    mov_sat {T0}.xyw, {T2}.xyzz"


# WATER033's own sum: the far water WITH the mirror picture (the same projected look-up the near shaders use).
FAR_SUM_MIRROR = """
    mad {T0}, {vobj}.xyzx, {K0}.wwwx, {K0}.xxxw
    dp4 {T1}.x, {vm2}, {T0}
    dp4 {T1}.y, {vm3}, {T0}
    dp4 {T1}.z, {vm4}, {T0}
    dp4 {T1}.w, {vm5}, {T0}
    texldp {T0}, {T1}, {ReflectionMap}
    mov {T1}.yz, {FV}
    lrp {T2}.xyz, {T1}.y, {T0}, {FR}
    add {T0}.xyz, {EyePos}, -{vpos}
    dp2add {T0}.w, {T0}, {T0}, {K0}.x
    rsq {T0}.w, {T0}.w
    rcp {T0}.w, {T0}.w
    mad_sat {TG}.x, {T0}.w, {KB}.x, {KB}.y
    add {T0}.w, {T0}.w, {K0}.y
    mad_sat {T0}.w, {T0}.w, {K0}.z, {K0}.w
    add {T0}.w, {T0}.w, -{K0}.w
    add {T1}.x, -{T1}.z, {K0}.w
    mad_sat {T0}.w, -{T0}.w, {T1}.x, {FV}.z
    mov {T1}.xyz, {FS}
    add {T1}.xyz, -{T1}, {FD}
    mad {T1}.xyz, {T0}.w, {T1}, {FS}
    mul {TL}.w, {T0}.w, {valpha}.w
    mad {T2}.xyz, {T2}, {FresnelRI}.w, -{T1}
    dp3 {T0}.w, {T0}, {T0}
    rsq {T0}.w, {T0}.w
    mul {T0}.xyz, {T0}, {T0}.w
    rcp {T0}.w, {T0}.w
    add {T0}.w, -{T0}.w, {FogParam}.x
    mov_sat {T1}.w, {T0}.z
    mad {T0}.xyz, {T0}.z, {K1}.xxyw, -{T0}
SUN
    add {T1}.w, -{T1}.w, {K0}.w
    mul {T2}.w, {T1}.w, {T1}.w
    mul {T2}.w, {T2}.w, {T2}.w
    mul {T1}.w, {T1}.w, {T2}.w
    mov {T2}.w, {K0}.w
    lrp {T3}.x, {T1}.w, {T2}.w, {FresnelRI}.x
    mad {T1}.xyz, {T3}.x, {T2}, {T1}
SUNADD
    add {T1}.xyz, -{T0}, {FogColor}
    rcp {T1}.w, {FogParam}.y
    mul_sat {T0}.w, {T0}.w, {T1}.w
    add {T0}.w, -{T0}.w, {K0}.w
    pow {T1}.w, {T0}.w, {FresnelRI}.y
    mad {TL}.xyz, {T1}.w, {T1}, {T0}
GATE
    lrp oC0, {TG}.x, {N}, {TL}
"""
MIRROR_SUN_LINES = """    dp3_sat {T0}.x, {T0}, {SunDir}
    pow {T2}.w, {T0}.x, {VarAmounts}.x
    add {T0}.x, {T2}.w, {K1}.z
    mul {T0}.xyz, {T0}.x, {SunColor}"""
MIRROR_SUNADD_SUN = "    mad {T0}.xyz, {T0}, {SunDir}.w, {T1}"
MIRROR_SUNADD_NONE = "    mov {T0}.xyz, {T1}"


def unpack(sdp, out):
    b = open(sdp, "rb").read()
    os.makedirs(out, exist_ok=True)
    off, n = 12, 0
    while off < len(b):
        name = b[off:off + 256].split(b"\0")[0].decode("latin-1")
        size = struct.unpack_from("<I", b, off + 256)[0]
        if name.upper().startswith("WATER"):
            open(os.path.join(out, name), "wb").write(b[off + 260:off + 260 + size])
            n += 1
        off += 260 + size
    print(f"{n} WATER shaders written to {out}")


def blend(src, dst, fade_from, fade_to):
    """returns '' when written, else why the shader was left alone"""
    orig = open(src, "rb").read()
    text = dis(orig)
    reg = dict(re.findall(r"//\s+(\w+)\s+(c\d+)\s+\d+\s*$", text, re.M))
    missing = [k for k in SETTINGS["need"] if k not in reg]
    if missing:
        return "lacks " + ", ".join(missing)
    # no NUL and no CR: the disassembly ends in a NUL line, and the assembler stops reading at it (2026-11-19: the
    # far sum added after it was silently dropped and the near water drew nothing)
    lines = [ln.rstrip("\r") for ln in text.replace("\x00", "").split("\n") if ln.strip() and not ln.strip().startswith("//")]
    if not any("oC0" in ln for ln in lines):
        return "writes no colour"
    body = " ".join(lines)
    temps = [int(x) for x in re.findall(r"\br(\d+)(?:_abs)?\b", body)]
    consts = [int(x) for x in re.findall(r"\bc(\d+)\b", text)]
    ins = [int(x) for x in re.findall(r"\bv(\d+)\b", body)]
    t = max(temps) + 1
    names = {"N": f"r{t}", "T0": f"r{t+1}", "T1": f"r{t+2}", "T2": f"r{t+3}", "T3": f"r{t+4}", "TL": f"r{t+5}", "TG": f"r{t+6}"}
    if t + 6 > 31:
        return "no spare registers"
    c = max(consts) + 1
    types = list(SETTINGS["fade_types"].values())
    names.update(K0=f"c{c}", K1=f"c{c+1}", KB=f"c{c+2}", FS=f"c{c+3}", FD=f"c{c+4}", FR=f"c{c+5}", FV=f"c{c+6}", KM=f"c{c+7}")
    names.update({f"KT{i}": f"c{c+8+i}" for i in range(len(types))})
    names.update(reg)
    dcl = [i for i, ln in enumerate(lines) if ln.strip().startswith("dcl")]
    extra_dcl = []

    def input_reg(pattern, decl):
        for i in dcl:
            m = re.match(pattern, lines[i].strip())
            if m:
                want = set(decl.split(".")[1])
                have = set((m.group(2) or "xyzw"))
                if not want <= have:                      # widen the mask the shader declared
                    lines[i] = re.sub(r"\.\w+$", "", lines[i]) + "." + "".join(ch for ch in "xyzw" if ch in want | have)
                return m.group(1)
        nonlocal ins
        v = f"v{max(ins) + 1}"
        ins.append(max(ins) + 1)
        extra_dcl.append(f"    {decl.split('.')[0].replace('V', v)}.{decl.split('.')[1]}")
        return v

    names["vpos"] = input_reg(r"dcl_texcoord(?:_centroid)? (v\d+)(?:\.(\w+))?$", "dcl_texcoord_centroid V.xyz")
    names["valpha"] = input_reg(r"dcl_texcoord6(?:_centroid)? (v\d+)(?:\.(\w+))?$", "dcl_texcoord6 V.w")
    sun = "SunDir" in reg and "SunColor" in reg
    samplers = dict(re.findall(r"//\s+(\w+)\s+(s\d+)\s+\d+\s*$", text, re.M))
    if "ReflectionMap" in samplers:
        # the game pairs a near shader that has the mirror picture with the far shader that has it too (WATER033):
        # 2026-11-19, Tefa's picture: fading to the plain one (WATER034) gave an olive band in front of a grey far water
        names["ReflectionMap"] = samplers["ReflectionMap"]
        names["vobj"] = input_reg(r"dcl_texcoord1(?:_centroid)? (v\d+)(?:\.(\w+))?$", "dcl_texcoord1_centroid V.xyz")
        for n in (2, 3, 4, 5):
            names[f"vm{n}"] = input_reg(r"dcl_texcoord%d(?:_centroid)? (v\d+)(?:\.(\w+))?$" % n, f"dcl_texcoord{n}_centroid V.xyzw")
        far = FAR_SUM_MIRROR.replace("SUNADD", MIRROR_SUNADD_SUN if sun else MIRROR_SUNADD_NONE)
        far = far.replace("SUN", MIRROR_SUN_LINES if sun else "    mov {T0}.xyz, {K0}.x")
    else:
        far = FAR_SUM.replace("SUNADD", SUNADD_SUN if sun else SUNADD_NONE).replace("SUN", SUN_LINES if sun else "")
    # the gate: TG.y = 1 when this near water is one of the fade types, else 0 (then the shader draws as before)
    gate = ["    mov {TG}.y, {K0}.x"]
    for i in range(len(SETTINGS["fade_types"])):
        gate += [f"    mov {{T3}}.xyz, {{ShallowColor}}",
                 f"    add {{T3}}.xyz, {{T3}}, -{{KT{i}}}",
                 f"    dp3 {{T3}}.w, {{T3}}_abs, {{KM}}.y",
                 f"    add {{T3}}.w, {{T3}}.w, -{{KM}}.x",
                 f"    cmp {{T3}}.w, {{T3}}.w, {{K0}}.x, {{K0}}.w",
                 f"    max {{TG}}.y, {{TG}}.y, {{T3}}.w"]
    gate += ["    mul {TG}.x, {TG}.x, {TG}.y"]
    far = far.replace("GATE", chr(10).join(gate))
    far = far.format(**names)
    lines = [ln.replace("oC0", names["N"]) for ln in lines]
    lines += [ln for ln in far.split("\n") if ln.strip()]
    ver = next(i for i, ln in enumerate(lines) if ln.strip() == "ps_3_0")
    span = fade_to - fade_from
    lines[ver + 1:ver + 1] = [f"    def {names['K0']}, 0, -4096, -0.000244140625, 1",
                              f"    def {names['K1']}, 0, 2, 2.40649434e-009, 0",
                              f"    def {names['KB']}, {-1.0 / span:.9f}, {fade_to / span:.9f}, 0, 0"]
    rgb = lambda b: ", ".join(f"{v / 255.0:.9f}" for v in b) + ", 1"
    vy, vz = SETTINGS["far_varamounts_yz"]
    lines[ver + 1:ver + 1] = [f"    def {names['FS']}, {rgb(SETTINGS['far_shallow'])}",
                              f"    def {names['FD']}, {rgb(SETTINGS['far_deep'])}",
                              f"    def {names['FR']}, {rgb(SETTINGS['far_reflection'])}",
                              f"    def {names['FV']}, 0, {vy}, {vz}, 0",
                              f"    def {names['KM']}, {SETTINGS['type_match']}, 1, 0, 0"] +                              [f"    def {names[f'KT{i}']}, {rgb(t)}" for i, t in enumerate(types)]
    first_dcl = next(i for i, ln in enumerate(lines) if ln.strip().startswith("dcl"))
    lines[first_dcl:first_dcl] = extra_dcl
    code = asm("\n".join(lines) + "\n")
    _, tok = struct.unpack_from("<II", orig, 0)
    if tok & 0xFFFF == 0xFFFE:
        n = (tok >> 16) & 0x7FFF
        code = code[:4] + orig[4:8 + 4 * n] + code[4:]
    open(dst, "wb").write(code)
    return ""


def main(argv):
    if len(argv) == 3 and argv[0] == "--unpack":
        unpack(argv[1], argv[2])
        return 0
    if len(argv) < 2:
        print(__doc__)
        return 1
    src, out = argv[0], argv[1]
    fade_from = float(argv[argv.index("--from") + 1]) if "--from" in argv else SETTINGS["fade_from"]
    fade_to = float(argv[argv.index("--to") + 1]) if "--to" in argv else SETTINGS["fade_to"]
    os.makedirs(out, exist_ok=True)
    done, left = [], []
    for name in sorted(os.listdir(src)):
        if not re.fullmatch(r"WATER\d+\.pso", name, re.I) or name.upper() in [x.upper() for x in SETTINGS["far_shaders"]]:
            continue
        why = blend(os.path.join(src, name), os.path.join(out, name), fade_from, fade_to)
        (left if why else done).append(name + (f" ({why})" if why else ""))
    print(f"{len(done)} near-water shaders written to {out} (fade {fade_from:.0f} to {fade_to:.0f} units)")
    if left:
        print("left alone: " + "; ".join(left))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
