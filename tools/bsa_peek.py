#!/usr/bin/env python3
"""bsa_peek.py -- list, or pull one file out of, a Fallout 3 / New Vegas .bsa (version 104), to LOOK at it.

    python bsa_peek.py <archive.bsa> [--find TEXT]            list the files (those whose path contains TEXT)
    python bsa_peek.py <archive.bsa> --get <path> --out FILE  write that one file to FILE (outside the repo)

Reading only. What comes out is somebody else's file: for measuring, never for the repo.
"""
import struct
import sys
import zlib

COMPRESSED_BY_DEFAULT = 0x4      # archive flag: files are zlib-packed unless their own size bit says otherwise
NAME_BEFORE_DATA = 0x100         # archive flag: each file's data starts with its full path
SIZE_FLIP_BIT = 0x40000000       # a file's size bit that flips the archive's packing default


def read(path):
    d = open(path, "rb").read()
    magic, ver, off, flags, nfold, nfile, lfold, lfile, _ = struct.unpack_from("<4sIIIIIIII", d, 0)
    if magic != b"BSA\0" or ver != 104:
        sys.exit("not a version-104 .bsa")
    p, folders = off, []
    for _ in range(nfold):
        _, count, _ = struct.unpack_from("<QII", d, p); p += 16
        folders.append(count)
    files = []
    for count in folders:
        n = d[p]; name = d[p + 1:p + n].decode("latin-1"); p += 1 + n
        for _ in range(count):
            _, size, offset = struct.unpack_from("<QII", d, p); p += 16
            files.append([name, size, offset])
    for f in files:
        e = d.index(b"\0", p); f.append(d[p:e].decode("latin-1")); p = e + 1
    return d, flags, [(fo + "\\" + fn, size, offset) for fo, size, offset, fn in files]


def get(d, flags, size, offset):
    packed = bool(flags & COMPRESSED_BY_DEFAULT) != bool(size & SIZE_FLIP_BIT)
    size &= ~0xC0000000
    if flags & NAME_BEFORE_DATA:
        n = d[offset]; offset += 1 + n; size -= 1 + n
    blob = d[offset:offset + size]
    return zlib.decompress(blob[4:]) if packed else blob


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    d, flags, files = read(a[0])
    if "--get" in a:
        want = a[a.index("--get") + 1].lower().replace("/", "\\")
        for path, size, offset in files:
            if path.lower() == want:
                open(a[a.index("--out") + 1], "wb").write(get(d, flags, size, offset))
                return
        sys.exit("not in the archive: " + want)
    find = a[a.index("--find") + 1].lower() if "--find" in a else ""
    for path, size, _ in files:
        if find in path.lower():
            print(f"{size & ~0xC0000000:>9}  {path}")


if __name__ == "__main__":
    main()
