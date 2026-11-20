#!/usr/bin/env python3
"""mo2_style.py -- Mod Organizer 2's look in the IT NEVER GETS OLD WHEN SOMETHING BLOWS UP IN VR! colours: night navy, cream writing, the logo's red and gold.

    python mo2_style.py --mo2 <list folder> [--install-font] [--select]

Reads the list's own dark style (stylesheets/Fluency Dark It Never Gets Old VR Edition.qss: every widget is already
styled there, and its icons stay where they are), swaps its colours for the logo's, puts Alfa Slab One (the font of
our main menu) on tabs, buttons, headings, the menu bar and drop-down boxes, and writes stylesheets/It Never Gets Old VR.qss
beside it. The lists keep a plain font: Alfa Slab One is a poster font and hard to read small. Mod Organizer cannot
load a font file itself, so the font must be installed in Windows: --install-font does that for this user only (no
administrator; undone by deleting the file and the one registry value it prints). --select makes it the style in
ModOrganizer.ini (Mod Organizer closed; or pick it under Settings > General > Style).
Fails loudly when a colour it swaps is not found.
"""
import argparse
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_FILE = os.path.join(HERE, "fonts", "AlfaSlabOne-Regular.ttf")
FONT_NAME = "Alfa Slab One"
SOURCE = os.path.join("stylesheets", "Fluency Dark It Never Gets Old VR Edition.qss")
OUT_NAME = "It Never Gets Old VR plain.qss"   # superseded by mo2_style_ingo.py (the poster look), which owns "It Never Gets Old VR.qss"

# the source style's colour -> ours (its own palette notes: main, text/button, disabled, hover, select, text, text disabled)
COLOURS = {
    "#191919": "#10161e",   # main background: night navy
    "#2d2d2d": "#1b2633",   # text boxes and buttons
    "#3d3d3d": "#243243",   # disabled
    "#4d4d4d": "#6e2418",   # hover: dark rust red
    "#444":    "#9e2f1c",   # the picked row: the logo's red
    "#fff":    "#efdcb2",   # writing: the logo's cream
    "#323232": "#4a5566",   # disabled writing
    "#ffdd67": "#e9b14a",   # accents (progress bars, tab buttons): the logo's gold rim
    "#5C5C5C": "#8a3a24",
    "#1d1d1d": "#0b1016",
    "#141414": "#0b1016",
    "#373d49": "#1e4e6e",   # the logo's blue
    "#add":    "#6fa3c4",
}

EXTRA = f"""

/* ---- It Never Gets Old VR: the poster font on the big labels (added by tools/mo2_style.py) ---- */
QTabBar::tab, QPushButton, QToolButton, QHeaderView::section, QGroupBox::title, QMenuBar::item, QComboBox {{
  font-family: '{FONT_NAME}';
  font-weight: normal;
  letter-spacing: 1px;
}}
QTabBar::tab:selected {{
  color: #e9b14a;
  border-bottom: 2px solid #9e2f1c;
}}
QHeaderView::section {{
  color: #e9b14a;
}}
QProgressBar::chunk {{
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9e2f1c, stop:1 #e9b14a);
}}
"""


def swap(text):
    for old, new in COLOURS.items():
        pat = re.compile(re.escape(old) + r"(?![0-9a-fA-F])", re.IGNORECASE)
        text, n = pat.subn(new, text)
        if not n:
            sys.exit(f"NOT FOUND: the colour {old} in the source style (a new version?). Nothing written.")
    return text


def install_font():
    import winreg
    folder = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, os.path.basename(FONT_FILE))
    shutil.copyfile(FONT_FILE, dst)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts") as k:
        winreg.SetValueEx(k, f"{FONT_NAME} (TrueType)", 0, winreg.REG_SZ, dst)
    print(f"font installed for this user: {FONT_NAME} (registry value '{FONT_NAME} (TrueType)')")


def select(mo2):
    p = os.path.join(mo2, "ModOrganizer.ini")
    with open(p, encoding="utf-8", newline="") as f:
        text = f.read()
    new, n = re.subn(r"(?m)^style=.*?(\r?)$", lambda m: "style=" + OUT_NAME + m.group(1), text)
    if n != 1:
        sys.exit("NOT FOUND: one style= line in ModOrganizer.ini")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print("selected in ModOrganizer.ini:", OUT_NAME)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--install-font", action="store_true")
    ap.add_argument("--select", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(a.mo2, SOURCE), encoding="utf-8") as f:
        text = swap(f.read())
    text = "/* It Never Gets Old VR: the dark Fluency style in the IT NEVER GETS OLD WHEN SOMETHING BLOWS UP IN VR! colours (tools/mo2_style.py) */\n" + text + EXTRA
    with open(os.path.join(a.mo2, "stylesheets", OUT_NAME), "w", encoding="utf-8") as f:
        f.write(text)
    print("written: stylesheets/" + OUT_NAME)
    if a.install_font:
        install_font()
    if a.select:
        select(a.mo2)


if __name__ == "__main__":
    main()
