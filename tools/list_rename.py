#!/usr/bin/env python3
"""list_rename.py -- take the source list's name out of our fork of it, everywhere Mod Organizer and the game read it.

    python list_rename.py --mo2 <list folder> [--downloads <downloads folder>] [--go]

Without --go it only prints what it would change. The rule (Tefa 2026-11-19, the source list's author's condition
for a fork): the fork must not carry the source list's name anywhere. What it changes, with Mod Organizer closed:
  1. mod folders and the files inside them that carry the name (plugins, archives and their .override marks, the
     per-plugin CellOffsets copy, the menu-mod preset): OLD -> NEW by the table below;
  2. every text file in profiles/ (mod lists, plugin lists, load orders, settings), and the profile folder itself;
  3. ModOrganizer.ini, nxmhandler.ini, the Wabbajack compiler settings (renamed too);
  4. each mod's meta.ini: install-file names; a Nexus description that names the list is emptied (it is the mod
     page's own text, shown only in Mod Organizer's info box);
  5. download archives and their .meta files in the downloads folder.
Game content that merely contains the words (the Fallout 3 song "Begin Again" on the radio, its credits) is not the
list's name and is left alone. Folders of the list itself and of the downloads are renamed separately, last.
Safe to run twice: a second run finds nothing to do.
"""
import argparse
import os
import re
import sys

OLD = "Begin" + " Again"      # split so a search of our own files for the name finds only this line's purpose
PAIRS = [                     # longest first
    ("BEGIN AGAIN V6.1.0_separator", "ATOMIC FORK VR_separator"),
    ("BEGIN AGAIN V6.1.0", "ATOMIC FORK VR"),
    ("BA Weathers", "Atomic Fork VR Weathers"),
    (OLD, "Atomic Fork VR"),
]
GAME_SONG = re.compile(r'song Begin Again|Begin Again\?" by', re.I)   # the radio song, never renamed (a bare '"Begin Again"'
                                                                   # also matched the Wabbajack settings' list name: too broad)
TEXT_EXT = {".txt", ".ini", ".json", ".compiler_settings", ".meta", ""}
DATED_BACKUP = re.compile(r"\.txt\.(\d{4}_\d\d_\d\d_|bak)")   # load-order backups (Mod Organizer's dated ones and ours):
                                                            # renamed inside too, so restoring one still works


def new_name(s):
    for o, n in PAIRS:
        s = s.replace(o, n)
    return s


def rename(path, go, log):
    d, b = os.path.split(path)
    nb = new_name(b)
    if nb == b:
        return path
    dst = os.path.join(d, nb)
    if os.path.exists(dst):
        sys.exit(f"STOP: both exist: {path} and {dst}")
    log.append(f"rename  {path}  ->  {nb}")
    if go:
        os.rename(path, dst)
    return dst


def edit_text(path, go, log, meta=False):
    try:
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        enc = "utf-8"
    except UnicodeDecodeError:
        with open(path, encoding="latin-1", newline="") as f:
            text = f.read()
        enc = "latin-1"
    if not any(o.lower() in text.lower() for o, _ in PAIRS):
        return
    out = []
    for line in text.splitlines(keepends=True):
        if meta and line.startswith("nexusDescription=") and OLD.lower() in line.lower():
            out.append('nexusDescription=""' + ("\r\n" if line.endswith("\r\n") else "\n"))
            continue
        if meta and line.startswith("nexusDescription="):
            out.append(line)
            continue
        out.append(new_name(line) if not GAME_SONG.search(line) else line)
    new = "".join(out)
    if new != text:
        log.append(f"edit    {path}")
        if go:
            with open(path, "w", encoding=enc, newline="") as f:
                f.write(new)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--downloads")
    ap.add_argument("--go", action="store_true")
    a = ap.parse_args()
    log = []
    mods = os.path.join(a.mo2, "mods")
    # 1 + 4: mods (files inside first, then the folder)
    for m in sorted(os.listdir(mods)):
        p = os.path.join(mods, m)
        if not os.path.isdir(p):
            continue
        for root, dirs, files in os.walk(p, topdown=False):
            for f in files:
                fp = os.path.join(root, f)
                if f == "meta.ini" and root == p:
                    edit_text(fp, a.go, log, meta=True)
                elif new_name(f) != f:
                    rename(fp, a.go, log)
            for d in dirs:                         # folders named after a plugin (CellOffsets keeps one per plugin)
                rename(os.path.join(root, d), a.go, log)
        rename(p, a.go, log)
    # 2: profiles
    prof = os.path.join(a.mo2, "profiles")
    for pr in sorted(os.listdir(prof)):
        pp = os.path.join(prof, pr)
        for f in os.listdir(pp):
            fp = os.path.join(pp, f)
            if os.path.isfile(fp) and (os.path.splitext(f)[1].lower() in TEXT_EXT or DATED_BACKUP.search(f)):
                edit_text(fp, a.go, log)
        rename(pp, a.go, log)
    # 3: the list's own settings
    for f in ("ModOrganizer.ini", "nxmhandler.ini"):
        edit_text(os.path.join(a.mo2, f), a.go, log)
    for f in os.listdir(a.mo2):
        if f.endswith(".compiler_settings"):
            fp = os.path.join(a.mo2, f)
            edit_text(fp, a.go, log)
            rename(fp, a.go, log)
    # 5: downloads
    if a.downloads:
        for f in sorted(os.listdir(a.downloads)):
            fp = os.path.join(a.downloads, f)
            if os.path.isfile(fp):
                if f.endswith(".meta"):
                    edit_text(fp, a.go, log)
                rename(fp, a.go, log)
    print("\n".join(log))
    print(f"\n{len(log)} change(s) {'made' if a.go else 'to make (dry run: add --go)'}")


if __name__ == "__main__":
    main()
