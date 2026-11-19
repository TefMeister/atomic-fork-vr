#!/usr/bin/env python3
"""save_rename.py -- carry a New Vegas save over the plugin rename (list_rename.py): the save names its plugins, so
after the rename the game says "This save relies on content that is no longer present" and drops what came from them.

    python save_rename.py --save "Save 4" [--go] [--backup <folder>]

Rewrites the old plugin names to the new ones (list_rename.PAIRS) in the save (.fos) and its xNVSE co-save (.nvse),
fixing every length that holds them. Without --go it only says what it would change. Both files are copied to
--backup first (default: the saves folder's "pre-rename" folder) and never overwritten there. Afterwards it reads
both files back and checks every length adds up; on any doubt it stops before writing.

Where the names are (measured 2026-11-20 on Save 4):
  .fos   the plugin list: uint32 size, a one-byte count, then per plugin "|" uint16 length "|" name "|"
         (the size counts the count byte, every entry and one more byte);
  .nvse  "NVSE" header (format, versions, runtime, plugin count), then per xNVSE plugin: opcode base, chunk count,
         length; per chunk: type, version, length, data. The MODS chunk is a one-byte count and uint16-length names;
         array variables (ARVR) hold strings as the byte 3, a uint16 length and the text.
"""
import argparse
import os
import shutil
import struct
import sys

import list_rename
from save_needs import pick_save, saves_dir

PAIRS = [(o.encode("latin-1"), n.encode("latin-1")) for o, n in list_rename.PAIRS if not o.endswith("_separator")]


def new_plugin(name):
    for o, n in PAIRS:
        if name.startswith(o):
            return n + name[len(o):]
    return name


def fos_fix(d):
    i = d.find(b"|FalloutNV.esm|")
    if i < 8:
        sys.exit("STOP: the plugin list was not found in the .fos")
    size_at, count = i - 8, d[i - 4]
    size = struct.unpack_from("<I", d, size_at)[0]
    pos, out, changed = i - 2, [], []
    for _ in range(count):
        n = struct.unpack_from("<H", d, pos)[0]
        if d[pos + 2:pos + 3] != b"|" or d[pos + 3 + n:pos + 4 + n] != b"|":
            sys.exit("STOP: the .fos plugin list is not laid out as expected")
        name = d[pos + 3:pos + 3 + n]
        nn = new_plugin(name)
        if nn != name:
            changed.append((name, nn))
        out.append(struct.pack("<H", len(nn)) + b"|" + nn + b"|")
        pos += 4 + n
    old_len = pos - (i - 2)
    if size != old_len + 2:                      # measured: the size is the entries + the count byte + 1
        sys.exit(f"STOP: the .fos list size {size} does not match its entries ({old_len} + 2)")
    body = b"".join(out)
    delta = len(body) - old_len
    # right after the list: the file's location table, five uint32 positions further on in the file (measured on
    # Save 4: two near the end, three just after the list). They move by delta; each must land on the same bytes.
    table = list(struct.unpack_from("<5I", d, pos))
    if not all(pos < v <= len(d) for v in table):
        sys.exit(f"STOP: the location table after the plugin list is not five positions further on: {table}")
    moved = struct.pack("<5I", *(v + delta for v in table))
    new = d[:size_at] + struct.pack("<I", len(body) + 2) + d[size_at + 4:i - 2] + body + moved + d[pos + 20:]
    for v in table:
        if d[v:v + 64] != new[v + delta:v + delta + 64]:
            sys.exit("STOP: a moved position does not land on the same bytes")
    return new, changed


def nvse_fix(d):
    sig, fmt, v1, v2, rt, nplug = struct.unpack_from("<4sIHHII", d, 0)
    if sig != b"NVSE":
        sys.exit("STOP: not an xNVSE co-save")
    out, p, changed = [d[:20]], 20, []
    for _ in range(nplug):
        ob, nch, ln = struct.unpack_from("<III", d, p)
        p += 12
        end, chunks = p + ln, []
        for _ in range(nch):
            t, ver, cl = struct.unpack_from("<4sII", d, p)
            data = d[p + 12:p + 12 + cl]
            p += 12 + cl
            if t == b"SDOM":                     # MODS
                cnt, q, parts = data[0], 1, [data[:1]]
                for _ in range(cnt):
                    n = struct.unpack_from("<H", data, q)[0]
                    name = data[q + 2:q + 2 + n]
                    nn = new_plugin(name)
                    if nn != name:
                        changed.append(("MODS", name, nn))
                    parts.append(struct.pack("<H", len(nn)) + nn)
                    q += 2 + n
                if q != len(data):
                    sys.exit("STOP: the MODS chunk is not laid out as expected")
                data = b"".join(parts)
            else:
                for o, n in PAIRS:
                    j = 0
                    while True:
                        j = data.find(o, j)
                        if j < 0:
                            break
                        k = data.find(b".esp", j)
                        if j < 3 or data[j - 3] != 3 or k < 0:
                            sys.exit(f"STOP: an old name in chunk {t[::-1]} that is not a plain string")
                        old = data[j:k + 4]
                        if struct.unpack_from("<H", data, j - 2)[0] != len(old):
                            sys.exit(f"STOP: a string in chunk {t[::-1]} whose length does not match")
                        nn = new_plugin(old)
                        data = data[:j - 2] + struct.pack("<H", len(nn)) + nn + data[k + 4:]
                        changed.append((t[::-1].decode(), old, nn))
                        j = j - 2 + 2 + len(nn)
            chunks.append(struct.pack("<4sII", t, ver, len(data)) + data)
        if p != end:
            sys.exit("STOP: an xNVSE plugin's length does not match its chunks")
        body = b"".join(chunks)
        out.append(struct.pack("<III", ob, nch, len(body)) + body)
    if p != len(d):
        sys.exit("STOP: bytes left over at the end of the co-save")
    return b"".join(out), changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--save", required=True)
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--backup", default=os.path.join(saves_dir(), "pre-rename"))
    a = ap.parse_args()
    fos = pick_save(a.save)
    nvse = fos[:-4] + ".nvse"
    new_fos, c1 = fos_fix(open(fos, "rb").read())
    new_nvse, c2 = nvse_fix(open(nvse, "rb").read()) if os.path.exists(nvse) else (None, [])
    # read back: a second pass over the new bytes must find nothing left and every length must add up
    if fos_fix(new_fos)[1] or (new_nvse and nvse_fix(new_nvse)[1]):
        sys.exit("STOP: the rewritten save still holds old names")
    print(os.path.basename(fos))
    for c in c1:
        print("  .fos  ", c[0].decode(), "->", c[1].decode())
    for c in c2:
        print("  .nvse ", c[0], c[1].decode(), "->", c[2].decode())
    if not (c1 or c2):
        print("  nothing to change")
        return
    if not a.go:
        print("dry run: add --go")
        return
    os.makedirs(a.backup, exist_ok=True)
    for f in (fos, nvse):
        if os.path.exists(f):
            dst = os.path.join(a.backup, os.path.basename(f))
            if not os.path.exists(dst):
                shutil.copy2(f, dst)
    for f, data in ((fos, new_fos), (nvse, new_nvse)):
        if data is not None:
            st = os.stat(f)
            with open(f, "wb") as h:
                h.write(data)
            os.utime(f, (st.st_atime, st.st_mtime))   # keep its date, so Continue still picks the same save
    print("written; the originals are in", a.backup)


if __name__ == "__main__":
    main()
