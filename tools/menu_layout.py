#!/usr/bin/env python3
"""menu_layout.py -- build our main-menu layout mod from the list's own two layout files.

    python menu_layout.py --mo2 <Begin Again folder> --out <mod folder>

Takes Vanilla UI Plus's start_menu.xml, MAPMO's pause_title.xml and MAPMO's logo picture as they are in the list, makes the few changes
below, and writes the changed copies into <mod folder> (same paths, so a mod placed above both wins):

  1. On the MAIN MENU's top level (title showing, no Back button) the list of menu words sits on the LEFT, under
     MAPMO's logo, its words ending where the logo's letters end. In a sub-menu (Load, Settings) and in the pause menu it is where it always was:
     MAPMO's script places the sub-menus to the LEFT of the list, so they need the list on the right.
  2. On the main menu the logo is drawn a little higher (MAPMO's pause_title.xml), so the words sit clear below it.
  3. The logo (MAPMO's ba_ttw_futura.dds, see-through by its own picture) is written again with solid letters.

Fails loudly when a piece of text it changes is not found (a new version of either mod): nothing is written then.
"""
import argparse
import os
import sys

UNDER_LOGO_Y = 205      # menu words start this far below the logo's top (the logo's own Y setting), in menu units
LIST_X_FROM_LOGO = 372  # the list's box starts this far right of the logo's X, so the words END where its letters end
LOGO_UP = 18            # the logo is drawn this far above its own Y setting on the main menu (Tefa: logo up, menu stays)
LOGO_SOLID_FROM = 190   # the logo picture's letters are this see-through at their most solid (of 255): made 255

VUI = os.path.join("mods", "Vanilla UI Plus (New Vegas)", "Menus", "Options", "start_menu.xml")
TITLE = os.path.join("mods", "MAPMO - Main and Pause Menus Overhaul", "menus", "prefabs", "mapmo", "startmenu", "pause_title.xml")
TITLE_OLD = """    <add><copy src="io" trait="_MAPMOMainTitleYPos"/><onlyif src="main_title" trait="visible"/></add>"""
TITLE_NEW = f"""    <add><copy src="io" trait="_MAPMOMainTitleYPos"/><sub>{LOGO_UP}</sub><onlyif src="main_title" trait="visible"/></add> <!-- Atomic Fork: logo up -->"""
LOGO = os.path.join("mods", "MAPMO - Main and Pause Menus Overhaul", "textures", "MAPMO", "Logos", "ba_ttw_futura.dds")

LIST_OLD_X = """			<x>
				<copy src="parent" trait="width"/>
				<sub src="me" trait="width"/>
				<sub src="parent" trait="_x_buffer"/>
			</x>
			<y>
				<copy src="parent" trait="height"/>
				<sub src="me" trait="height"/>
				<div> 2 </div>
			</y>
			<width> 300 </width>"""
LIST_NEW_X = f"""			<!-- Atomic Fork: 1 on the main menu's top level (title showing, no Back button) -->
			<_AtomicForkLeft>
				<not src="sibling(main_back_button)" trait="visible"/>
				<and src="sibling(main_title)" trait="visible"/>
			</_AtomicForkLeft>
			<x>
				<copy src="parent" trait="width"/>
				<sub src="me" trait="width"/>
				<sub src="parent" trait="_x_buffer"/>
				<onlyifnot src="me" trait="_AtomicForkLeft"/>
				<add>
					<copy src="io" trait="_MAPMOMainTitleXPos"/>
					<add> {LIST_X_FROM_LOGO} </add>
					<onlyif src="me" trait="_AtomicForkLeft"/>
				</add>
			</x>
			<y>
				<copy src="parent" trait="height"/>
				<sub src="me" trait="height"/>
				<div> 2 </div>
				<onlyifnot src="me" trait="_AtomicForkLeft"/>
				<add>
					<copy src="io" trait="_MAPMOMainTitleYPos"/>
					<add> {UNDER_LOGO_Y} </add>
					<onlyif src="me" trait="_AtomicForkLeft"/>
				</add>
			</y>
			<width> 300 </width>"""

def solid_logo(src, dst):
    """The logo with its letters made solid: same size, same colours, the see-through value scaled up."""
    import struct
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    r, g, b, a = im.split()
    a = a.point(lambda v: min(255, round(v * 255 / LOGO_SOLID_FROM)))
    out = Image.merge("RGBA", (r, g, b, a))
    w, h = out.size
    pf = struct.pack("<II4sIIIII", 32, 0x41, b"\0\0\0\0", 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    head = b"DDS " + struct.pack("<IIIIIII", 124, 0x100F, h, w, w * 4, 0, 0) + b"\0" * 44 + pf + struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(head + out.tobytes("raw", "BGRA"))


def change(text, old, new, what):
    old_n, new_n = old.replace("\n", "\r\n"), new.replace("\n", "\r\n")
    for o, n in ((old_n, new_n), (old, new)):
        if text.count(o) == 1:
            return text.replace(o, n)
    sys.exit(f"NOT FOUND (or found twice): {what}. Nothing written.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    jobs = [(VUI, os.path.join("Menus", "Options", "start_menu.xml"), LIST_OLD_X, LIST_NEW_X, "the menu list's place in start_menu.xml"),
            (TITLE, os.path.join("menus", "prefabs", "mapmo", "startmenu", "pause_title.xml"), TITLE_OLD, TITLE_NEW, "the logo's height in pause_title.xml")]
    done = []
    for src, dst, old, new, what in jobs:
        with open(os.path.join(a.mo2, src), encoding="latin-1", newline="") as f:
            done.append((dst, change(f.read(), old, new, what)))
    for dst, text in done:
        p = os.path.join(a.out, dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="latin-1", newline="") as f:
            f.write(text)
        print("written:", dst)
    logo_out = os.path.join("textures", "MAPMO", "Logos", "ba_ttw_futura.dds")
    solid_logo(os.path.join(a.mo2, LOGO), os.path.join(a.out, logo_out))
    print("written:", logo_out)


if __name__ == "__main__":
    main()
