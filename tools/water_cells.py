#!/usr/bin/env python3
"""water_cells.py -- which water type every Capital Wasteland cell names for itself, in a profile's winning plugins.

    python water_cells.py [--mo2 <list folder>] [--game <New Vegas folder>] [--name <profile>]

A cell may name its own water (XCWT); the far water beyond the loaded cells always uses the worldspace's "LOD water"
instead. Where the two differ, a lake shows a straight line where the loaded cells end. 2026-11-20: the Save 4 lake's
98 cells name PotomacNRShallow (olive), the far water is Potomac (green-blue): board row FO-002. Read-only.
"""
import argparse, os, struct, sys, zlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import water_types as W
H = W.HEADER
ap = argparse.ArgumentParser(description=__doc__.split(chr(10) * 2)[0])
ap.add_argument("--mo2", default="C:/Modlists/Atomic Fork VR")
ap.add_argument("--game", default="C:/Steam/steamapps/common/Fallout New Vegas")
ap.add_argument("--name", default="rung-05 interface flat")
a = ap.parse_args()
mo2, game, prof = a.mo2, a.game, a.name
plugins = W.plugin_paths(mo2, game, prof)

def walk(buf, name, mast, out_cells, out_waters, world_of):
    off = 0
    stack = []   # (end, label, gtype)
    while off + H <= len(buf):
        while stack and off >= stack[-1][0]:
            stack.pop()
        typ, size = buf[off:off+4], struct.unpack_from("<I", buf, off+4)[0]
        if typ == b"GRUP":
            label, gtype = buf[off+8:off+12], struct.unpack_from("<I", buf, off+12)[0]
            if gtype == 0 and label not in (b"WRLD", b"WATR"):
                off += size; continue
            if gtype in (6, 8, 9, 10):        # cell children (refs): skip
                off += size; continue
            stack.append((off+size, label, gtype)); off += H; continue
        flags, formid = struct.unpack_from("<II", buf, off+8)
        body = buf[off+H:off+H+size]
        t = typ.decode("latin-1")
        if t in ("CELL", "WATR", "WRLD"):
            if flags & 0x40000:
                try: body = zlib.decompress(body[4:])
                except zlib.error: body = b""
            subs = dict(W.subrecords(body))
            gid = gidf(formid, name, mast)
            if t == "WATR":
                out_waters[gid] = (name, subs)
            elif t == "WRLD":
                world_of[gid] = subs.get("EDID", b"").split(b"\0")[0].decode("latin-1")
            else:
                w = [s for s in stack if s[2] == 1]
                if w:
                    wid = gidf(struct.unpack("<I", w[-1][1])[0], name, mast)
                    out_cells[gid] = (name, wid, subs)
        off += H + size

def gidf(local, name, mast):
    top = local >> 24
    return ((mast[top] if top < len(mast) else name).lower(), local & 0xFFFFFF)

cells, waters, worlds = {}, {}, {}
for name, path in plugins:
    buf = open(path, "rb").read()
    walk(buf, name, W.masters(buf), cells, waters, worlds)
wl = [k for k, v in worlds.items() if v.lower() == "wasteland"]
print("Wasteland ids:", wl)
by = collections.defaultdict(list)
for gid, (name, wid, subs) in cells.items():
    if wid not in wl: continue
    if "XCLC" in subs:
        x, y = struct.unpack_from("<ii", subs["XCLC"])
    else:
        continue
    wt = gidf(struct.unpack("<I", subs["XCWT"])[0], name, W.masters(open(dict(plugins)[name], "rb").read()[:200000])) if "XCWT" in subs else None
    wh = struct.unpack("<f", subs["XCLW"])[0] if "XCLW" in subs and len(subs["XCLW"]) == 4 else None
    by[wt].append((x, y, wh, name))
for wt, lst in sorted(by.items(), key=lambda kv: -len(kv[1])):
    edid = waters.get(wt, ("?", {}))[1].get("EDID", b"?").split(b"\0")[0].decode("latin-1") if wt else "-"
    print(wt, edid, len(lst), "last by", collections.Counter(n for *_, n in lst).most_common(3), "e.g.", lst[:6])
