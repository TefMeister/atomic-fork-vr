#!/usr/bin/env python3
"""ingo_rename.py -- the list's second rename (Tefa 2026-11-20): ATOMIC FORK VR -> IT NEVER GETS OLD WHEN SOMETHING
BLOWS UP IN VR!, run on the COPY of the list (the Atomic Fork VR folder stays as it was).

    python ingo_rename.py --mo2 <list folder> [--go]

Uses list_rename.py's walk (mod folders and the files in them, profiles, ModOrganizer.ini, the compiler settings),
with this table instead of its own. Where the name is SHOWN (Mod Organizer's separator, the menu, the splash) it is
the full title. File, folder, plugin and profile names get the short form "It Never Gets Old VR": the full title
would add 34 characters to every path inside the worldspace merge and puts a "!" into names that launchers and
batch files pass around.
Also renames our own words inside our own Bridge files (comments, the menu layout's private trait names, the
slower-days script's file name), so the old name is gone from the list entirely.
Plugins renamed here are checked afterwards by ladder.py check (masters).
"""
import os
import sys

import list_rename as lr

FULL = "IT NEVER GETS OLD WHEN SOMETHING BLOWS UP IN VR!"
SHORT = "It Never Gets Old VR"
lr.OLD = "Atomic Fork VR"
lr.PAIRS = [                                   # longest first
    ("ATOMIC FORK VR_separator", FULL + "_separator"),
    ("Atomic Fork VR Conflict reolution patch", SHORT + " Conflict Resolution Patch"),
    ("Fluency Dark Atomic Fork VR Edition", "Fluency Dark " + SHORT + " Edition"),
    ("ATOMIC FORK VR", FULL),
    ("Atomic Fork VR", SHORT),
    ("Bridge - Atomic Fork", "Bridge - It Never Gets Old"),
    ("ln_AtomicForkSlowerDays", "ln_NeverGetsOldSlowerDays"),
    ("_AtomicFork", "_NeverGetsOld"),
    ("Atomic Fork", "It Never Gets Old"),
]
lr.GAME_SONG = __import__("re").compile(r"(?!x)x")   # nothing to spare this time

OUR_TEXT = (".xml", ".txt", ".ini", ".qss")


def our_files(mo2, go, log):
    """Text inside our own Bridge mods and the style sheets."""
    mods = os.path.join(mo2, "mods")
    for m in os.listdir(mods):
        if not m.startswith("Bridge"):
            continue
        for root, _, files in os.walk(os.path.join(mods, m)):
            for f in files:
                if f.lower().endswith(OUR_TEXT) and f != "meta.ini":
                    lr.edit_text(os.path.join(root, f), go, log)
    st = os.path.join(mo2, "stylesheets")
    for f in os.listdir(st):
        if f.endswith(".qss"):
            lr.edit_text(os.path.join(st, f), go, log)
            lr.rename(os.path.join(st, f), go, log)


if __name__ == "__main__":
    go = "--go" in sys.argv
    mo2 = sys.argv[sys.argv.index("--mo2") + 1]
    if os.path.basename(os.path.normpath(mo2)) == "Atomic Fork VR":
        sys.exit("STOP: this is the original folder; run it on the copy")
    log = []
    our_files(mo2, go, log)        # first, while the folders still have their old names
    print("\n".join(log))
    lr.main()
