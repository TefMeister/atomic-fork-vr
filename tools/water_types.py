#!/usr/bin/env python3
"""water_types.py -- which water does a worldspace use NEAR the player and which FAR away, in a profile's winning
plugins, and how do the two water records differ?

    python water_types.py --mo2 <mod list folder> --game <New Vegas folder> --name <profile> [--world Wasteland]

A worldspace record names two waters: its ordinary water (NAM2, used by every cell that names none of its own) and
its "LOD water type" (NAM3), used for the far water beyond the loaded cells. When the two are different records, or
one mod changed one and not the other, the lake shows a straight line where they meet.
It reads the plugins in the profile's load order (later wins), prints every plugin that carries the worldspace and
what it names, then the two water records as the LAST plugin that carries each defines them, field by field.
Read-only. Built 2026-11-19 for the water line (board row FO-002).
"""
import argparse
import os
import struct
import sys
import zlib

HEADER = 24


def plugin_paths(mo2, game, profile):
    """load order -> full path (a mod's copy wins over the game's Data folder; among mods the modlist's top wins)"""
    prof = os.path.join(mo2, "profiles", profile)
    with open(os.path.join(prof, "modlist.txt"), encoding="utf-8") as f:
        mods = [ln[1:].strip() for ln in f if ln.startswith("+")]
    with open(os.path.join(prof, "loadorder.txt"), encoding="utf-8", errors="replace") as f:
        order = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    with open(os.path.join(prof, "plugins.txt"), encoding="utf-8", errors="replace") as f:
        active = {ln.strip().lstrip("*").lower() for ln in f if ln.strip() and not ln.startswith("#")}
    out = []
    for name in order:
        if name.lower() not in active and not name.lower().endswith(".esm"):
            continue
        for m in mods:
            p = os.path.join(mo2, "mods", m, name)
            if os.path.isfile(p):
                out.append((name, p))
                break
        else:
            p = os.path.join(game, "Data", name)
            if os.path.isfile(p):
                out.append((name, p))
    return out


def subrecords(data):
    off, out = 0, []
    while off + 6 <= len(data):
        tag, size = data[off:off + 4], struct.unpack_from("<H", data, off + 4)[0]
        out.append((tag.decode("latin-1"), data[off + 6:off + 6 + size]))
        off += 6 + size
    return out


def records(buf, want):
    """every top-level-group record whose type is in want: (type, formid, subrecords)"""
    off = 0
    while off + HEADER <= len(buf):
        typ, size = buf[off:off + 4], struct.unpack_from("<I", buf, off + 4)[0]
        if typ == b"GRUP":
            label, gtype = buf[off + 8:off + 12], struct.unpack_from("<I", buf, off + 12)[0]
            if gtype == 0 and label.decode("latin-1") not in want:
                off += size                      # a whole top group of another kind: skip it
            else:
                off += HEADER                    # step inside
            continue
        flags, formid = struct.unpack_from("<II", buf, off + 8)
        body = buf[off + HEADER:off + HEADER + size]
        if typ.decode("latin-1") in want:
            if flags & 0x00040000:
                try:
                    body = zlib.decompress(body[4:])
                except zlib.error:
                    body = b""
            yield typ.decode("latin-1"), formid, subrecords(body)
        off += HEADER + size


def masters(buf):
    size = struct.unpack_from("<I", buf, 4)[0]
    return [d.split(b"\0")[0].decode("latin-1") for t, d in subrecords(buf[HEADER:HEADER + size]) if t == "MAST"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--game", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--world", default="Wasteland")
    a = ap.parse_args()
    plugins = plugin_paths(a.mo2, a.game, a.name)
    index = {n.lower(): i for i, (n, _) in enumerate(plugins)}

    def glob_id(local, name, mast):
        """a plugin's own form number -> (owning plugin, 24-bit number)"""
        top = local >> 24
        owner = mast[top] if top < len(mast) else name
        return owner.lower(), local & 0xFFFFFF

    world, waters = None, {}
    for name, path in plugins:
        with open(path, "rb") as f:
            buf = f.read()
        mast = masters(buf)
        for typ, formid, subs in records(buf, {"WRLD", "WATR"}):
            d = dict(subs)                       # the first of each tag is enough here
            gid = glob_id(formid, name, mast)
            if typ == "WATR":
                waters[gid] = (name, subs)
            elif d.get("EDID", b"").split(b"\0")[0].decode("latin-1").lower() == a.world.lower():
                nam2 = glob_id(struct.unpack("<I", d["NAM2"])[0], name, mast) if "NAM2" in d else None
                nam3 = glob_id(struct.unpack("<I", d["NAM3"])[0], name, mast) if "NAM3" in d else None
                world = (name, nam2, nam3)
                print(f"{name}: {a.world} names water {nam2}, far water {nam3}")
    if not world:
        sys.exit(f"no worldspace '{a.world}' in the profile's plugins")
    print(f"\nwinning: {world[0]}")
    recs = {}
    for label, gid in (("near (NAM2)", world[1]), ("far (NAM3)", world[2])):
        if gid not in waters:
            print(f"{label}: {gid} not found")
            continue
        name, subs = waters[gid]
        d = dict(subs)
        print(f"{label}: {d.get('EDID', b'?').split(b'\\0')[0].decode('latin-1')} {gid[0]}:{gid[1]:06X}, last defined by {name}")
        recs[label] = d
    if len(recs) == 2:
        (la, da), (lb, db) = recs.items()
        if world[1] == world[2]:
            print("\nthe same record for near and far: the difference is not here")
        for tag in sorted(set(da) | set(db)):
            if tag in ("EDID", "FULL") or da.get(tag) == db.get(tag):
                continue
            xa, xb = da.get(tag, b""), db.get(tag, b"")
            print(f"  {tag}: differs ({len(xa)} / {len(xb)} bytes)")
            if tag in ("DNAM", "DATA") and len(xa) == len(xb) and len(xa) >= 60:
                for off in range(0, len(xa) - 3, 4):
                    if xa[off:off + 4] != xb[off:off + 4]:
                        fa, fb = struct.unpack_from("<f", xa, off)[0], struct.unpack_from("<f", xb, off)[0]
                        print(f"      +{off:3d}: {xa[off:off+4].hex()} / {xb[off:off+4].hex()}   as numbers {fa:.4g} / {fb:.4g}   as colours {tuple(xa[off:off+4])} / {tuple(xb[off:off+4])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
