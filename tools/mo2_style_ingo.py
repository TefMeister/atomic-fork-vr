#!/usr/bin/env python3
"""mo2_style_ingo.py -- Mod Organizer 2's look for IT NEVER GETS OLD WHEN SOMETHING BLOWS UP IN VR!: Tefa's poster
behind the whole window, the poster's amber and cream for the writing, an American poster font on the big labels.

    python mo2_style_ingo.py --mo2 <list folder> --picture <poster.png> [--font <font.ttf>] [--install-font] [--select]

Built on the see-through style that ships with Mod Organizer (Trosski's Transparent-Style, Fallout 3 edition): every
panel there is already see-through over one picture. This copies it as stylesheets/It Never Gets Old VR.qss, with
  - the picture: the poster, darkened so the lists stay readable (BACKDROP_DIM), plus a darker, blurred copy for the
    dialogs (SETTINGS_DIM) and a small one for the toolbar strip;
  - the Fallout 3 green swapped for the poster's amber, everywhere: in the style and in its small pictures (arrows,
    tick boxes, radio buttons), which are recoloured copies, so the original style is untouched;
  - the font on tabs, buttons, headings, the menu bar and drop-down boxes; the lists keep a plain font (poster fonts
    are hard to read small). Mod Organizer cannot load a font file itself: --install-font installs it in Windows for
    this user only (undone by deleting the file and the one registry value it prints).
Run it again after the poster changes: everything it writes is rebuilt. --select sets it in ModOrganizer.ini (MO2
closed). Fails loudly when a colour it swaps is not found.
"""
import argparse
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join("stylesheets", "Transparent-Style-FO3-Trosski.qss")
SOURCE_PICS = os.path.join("stylesheets", "Transparent-Style", "Fallout3")
NAME = "It Never Gets Old VR"
OUT_QSS = NAME + ".qss"
OUT_PICS = os.path.join("stylesheets", NAME)

BACKDROP_SIZE = (1920, 1080)
BACKDROP_DIM = 0.55          # the main window's picture at 55 % brightness
SETTINGS_DIM = 0.30          # dialogs: darker and blurred, they are mostly text
SETTINGS_BLUR = 6
AMBER = (242, 169, 59)       # the poster's lettering rim
CREAM = "#f3e2b5"            # the poster's lettering face

COLOURS = {                  # the source style's -> ours
    "#1AFF80": "#f2a93b",
    "rgba(26, 255, 128,": "rgba(242, 169, 59,",
    "rgba(0, 0, 0, 10)": "rgba(10, 8, 5, 120)",       # lists: dark enough to read over the poster
    "rgba(113, 113, 113, 50)": "rgba(60, 40, 20, 110)",
    "#ffffff": CREAM,
}


def swap(text):
    for old, new in COLOURS.items():
        n = text.count(old)
        if not n:
            sys.exit(f"NOT FOUND: {old} in the source style (a new version?). Nothing written.")
        text = text.replace(old, new)
    return text.replace("Transparent-Style/Fallout3/Fallout3", NAME + "/poster").replace("Transparent-Style/Fallout3/", NAME + "/")


def tint(src, dst):
    """A small green picture -> the same in amber (brightness and see-through kept)."""
    im = np.asarray(Image.open(src).convert("RGBA")).astype(np.float32)
    lum = (im[..., :3] @ np.array([0.299, 0.587, 0.114], dtype=np.float32)) / 255
    g = im[..., 1] / 255                                        # the green channel carries the shape
    v = np.maximum(lum, g)[..., None]
    out = np.concatenate([v * np.array(AMBER, dtype=np.float32), im[..., 3:]], -1)
    Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").save(dst)


def pictures(mo2, poster):
    out = os.path.join(mo2, OUT_PICS)
    os.makedirs(out, exist_ok=True)
    src = os.path.join(mo2, SOURCE_PICS)
    for f in os.listdir(src):
        if f.lower().startswith("fallout3"):
            continue
        tint(os.path.join(src, f), os.path.join(out, f))
    p = Image.open(poster).convert("RGB")
    big = ImageEnhance.Brightness(p.resize(BACKDROP_SIZE, Image.LANCZOS)).enhance(BACKDROP_DIM)
    big.save(os.path.join(out, "poster.png"))
    dlg = ImageEnhance.Brightness(p.resize(BACKDROP_SIZE, Image.LANCZOS).filter(ImageFilter.GaussianBlur(SETTINGS_BLUR))).enhance(SETTINGS_DIM)
    dlg.save(os.path.join(out, "poster-settings.png"))
    big.resize((BACKDROP_SIZE[0] // 4, BACKDROP_SIZE[1] // 4), Image.LANCZOS).save(os.path.join(out, "poster-small.png"))
    icon = Image.open(os.path.join(src, "Fallout3_icon.png"))
    Image.new("RGBA", icon.size, (0, 0, 0, 0)).save(os.path.join(out, "poster_icon.png"))   # the toolbar divider: plain
    for f in ("Fallout3-itemB-open.png", "Fallout3-itemB-close.png"):   # tree open/close arrows (Windows ignores case)
        tint(os.path.join(src, f), os.path.join(out, "poster" + f[len("Fallout3"):]))


def font_name(path):
    from PIL import ImageFont
    return ImageFont.truetype(path, 12).getname()[0]


def install_font(path):
    import winreg
    name = font_name(path)
    folder = os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Windows", "Fonts")
    os.makedirs(folder, exist_ok=True)
    dst = os.path.join(folder, os.path.basename(path))
    shutil.copyfile(path, dst)
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts") as k:
        winreg.SetValueEx(k, f"{name} (TrueType)", 0, winreg.REG_SZ, dst)
    print(f"font installed for this user: {name} (registry value '{name} (TrueType)')")


def select(mo2):
    p = os.path.join(mo2, "ModOrganizer.ini")
    with open(p, encoding="utf-8", newline="") as f:
        text = f.read()
    new, n = re.subn(r"(?m)^style=.*?(\r?)$", lambda m: "style=" + OUT_QSS + m.group(1), text)
    if n != 1:
        sys.exit("NOT FOUND: one style= line in ModOrganizer.ini")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    print("selected in ModOrganizer.ini:", OUT_QSS)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--picture", required=True)
    ap.add_argument("--font", default=os.path.join(HERE, "fonts", "RacingSansOne-Regular.ttf"))
    ap.add_argument("--install-font", action="store_true")
    ap.add_argument("--select", action="store_true")
    a = ap.parse_args()
    with open(os.path.join(a.mo2, SOURCE), encoding="utf-8") as f:
        text = swap(f.read())
    fname = font_name(a.font)
    extra = f"""

/* ---- {NAME}: the poster font on the big labels (tools/mo2_style_ingo.py) ---- */
QTabBar::tab, QPushButton, QToolButton, QHeaderView::section, QGroupBox::title, QMenuBar::item, QComboBox {{
  font-family: '{fname}';
  font-weight: normal;
  font-size: 15px;
  letter-spacing: 1px;
}}
QTabBar::tab:selected, QHeaderView::section {{
  color: #f2a93b;
}}
QTabBar::tab:selected {{
  border-bottom: 2px solid #c8321e;
}}
QAbstractItemView::item:selected {{
  background: rgba(200, 50, 30, 150);
  color: #fff4d6;
}}
QProgressBar::chunk {{
  background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c8321e, stop:1 #f2a93b);
}}
"""
    text = f"/* {NAME}: Trosski's Transparent-Style (Fallout 3) over Tefa's poster, in the poster's colours */\n" + text + extra
    pictures(a.mo2, a.picture)
    with open(os.path.join(a.mo2, "stylesheets", OUT_QSS), "w", encoding="utf-8") as f:
        f.write(text)
    print("written: stylesheets/" + OUT_QSS, "and", OUT_PICS, "| font:", fname)
    if a.install_font:
        install_font(a.font)
    if a.select:
        select(a.mo2)


if __name__ == "__main__":
    main()
