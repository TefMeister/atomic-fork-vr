#!/usr/bin/env python3
"""ingo_saves.py -- give IT NEVER GETS OLD WHEN SOMETHING BLOWS UP IN VR! its own saves, carried over the plugin rename.

    python ingo_saves.py --mo2 <the new list's folder> [--go]

The saves folder (Documents/My Games/FalloutNV/Saves) is shared by every list on the PC, and a save names its plugins:
after ingo_rename.py the new list's plugins are called "It Never Gets Old VR ...", so an old save shows "This save
relies on content that is no longer present" (seen 2026-11-21). Renaming inside the shared saves would break them for
the Atomic Fork VR list, which is kept as it was. So:
  1. every save (.fos with its .nvse co-save, never the .bak files) is COPIED into the subfolder SUBDIR, dates kept;
  2. the copies get the new plugin names (save_rename.py's checked rewrite, with this table);
  3. every profile of the new list reads and writes its saves there: SLocalSavePath in its Fallout.ini and
     FalloutPrefs.ini ([General]), a .bak-2026-11-21-saves copy beside each file first.
The originals in the shared folder are not touched. Without --go it only says what it would do. Safe to run again: a
save already in the subfolder is not copied again, and a copy already renamed has nothing left to change.
"""
import argparse
import glob
import os
import re
import shutil
import sys

import save_rename
from save_needs import saves_dir

SUBDIR = "It Never Gets Old VR"
INI_VALUE = "Saves\\" + SUBDIR + "\\"
NEW = "It Never Gets Old VR"
TABLE = [                       # longest first; the first match from the start of a plugin's name wins
    ("Atomic Fork VR Conflict reolution patch", NEW + " Conflict Resolution Patch"),
    ("Begin Again Conflict reolution patch", NEW + " Conflict Resolution Patch"),
    ("Atomic Fork VR", NEW),
    ("Begin" + " Again", NEW),
    ("BA Weathers", NEW + " Weathers"),
]
save_rename.PAIRS = [(o.encode("latin-1"), n.encode("latin-1")) for o, n in TABLE]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()
    root = saves_dir()
    if os.path.basename(os.path.normpath(root)) == SUBDIR:
        root = os.path.dirname(os.path.normpath(root))
    dst_dir = os.path.join(root, SUBDIR)
    if a.go:
        os.makedirs(dst_dir, exist_ok=True)
    for fos in sorted(glob.glob(os.path.join(root, "*.fos"))):
        name = os.path.basename(fos)
        dst = os.path.join(dst_dir, name)
        if not os.path.exists(dst):
            print("copy ", name)
            if a.go:
                shutil.copy2(fos, dst)
                if os.path.exists(fos[:-4] + ".nvse"):
                    shutil.copy2(fos[:-4] + ".nvse", dst[:-4] + ".nvse")
        src = dst if a.go else fos
        new_fos, c1 = save_rename.fos_fix(open(src, "rb").read())
        nv = src[:-4] + ".nvse"
        new_nv, c2 = save_rename.nvse_fix(open(nv, "rb").read()) if os.path.exists(nv) else (None, [])
        if save_rename.fos_fix(new_fos)[1] or (new_nv and save_rename.nvse_fix(new_nv)[1]):
            sys.exit("STOP: a rewritten save still holds old names: " + name)
        print("      %d plugin name(s) in the save, %d in the co-save to change" % (len(c1), len(c2)))
        if a.go and (c1 or c2):
            for f, data in ((dst, new_fos), (dst[:-4] + ".nvse", new_nv)):
                if data is not None:
                    st = os.stat(f)
                    with open(f, "wb") as h:
                        h.write(data)
                    os.utime(f, (st.st_atime, st.st_mtime))
    for prof in sorted(glob.glob(os.path.join(a.mo2, "profiles", "*"))):
        for ini in ("fallout.ini", "falloutprefs.ini"):
            p = os.path.join(prof, ini)
            if not os.path.exists(p):
                continue
            text = open(p, encoding="latin-1", newline="").read()
            new, n = re.subn(r"(?im)^(SLocalSavePath=).*?(\r?)$", lambda m: m.group(1) + INI_VALUE + m.group(2), text)
            if n == 0:
                new, n = re.subn(r"(?im)^(\[General\]\r?\n)", lambda m: m.group(1) + "SLocalSavePath=" + INI_VALUE + "\r\n", text, count=1)
            if new != text:
                print("ini  ", os.path.basename(prof), ini)
                if a.go:
                    bak = p + ".bak-2026-11-21-saves"
                    if not os.path.exists(bak):
                        shutil.copy2(p, bak)
                    with open(p, "w", encoding="latin-1", newline="") as f:
                        f.write(new)
    print("done" if a.go else "dry run: add --go")


if __name__ == "__main__":
    main()
