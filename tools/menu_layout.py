#!/usr/bin/env python3
"""menu_layout.py -- build our main-menu layout mod (title row, menu on the left, our menu font).

    python menu_layout.py --mo2 <list folder> --out <mod folder>

Part of the mod is changed copies of two of the list's own layout files (so the repo keeps this builder, not the
copies); the rest is drawn here from our font:

  1. Vanilla UI Plus's start_menu.xml: on the MAIN MENU's top level (title showing, no Back button) the list of menu
     words sits on the LEFT of the picture, between the flag and the radiation sign, left-aligned. In a sub-menu
     (Load, Settings) and in the pause menu it is where it always was: MAPMO's script puts the sub-menus to the
     LEFT of the list, so they need the list on the right. Our own title row is added at the top, centred.
  2. MAPMO's pause_title.xml: its logo is no longer drawn on the main menu (ours is); the pause menu keeps it.
  3. MAPMO's TTW logo picture (see-through by its own making), written again with solid letters, for the pause menu.
  4. The title row picture (menu_title.py) and the menu font (game_font.py --worn, replacing the game's big caps font,
     number 8: main menu, pause menu and wherever else the game writes in it), both from tools/fonts, worn alike.

Fails loudly when a piece of text it changes is not found (a new version of either mod): nothing is written then.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "fonts", "AlfaSlabOne-Regular.ttf")

# Everything below is in menu units: the screen is 960 high whatever its real size (1,707 wide at 16:9).
MENU_X_SHARE = 0.041      # the menu words start this share of the screen's width from the left (the same spot of
                          # the picture on any screen shape, as the game stretches the picture to the screen)
MENU_X_INSET = 30         # ... less the list box's own inset before its words
SUBMENU_LIST_X = 1010     # where the list stands while Load or Settings is open (the Load panel is 750 wide)
ROW_PITCH = 1             # only a flag now: 1 = on the main menu (the rows keep the list's own 50)
DIM_OTHERS = 110          # on the main menu the words NOT chosen are this much darker (of 255): the chosen one stands out without a box
MENU_Y = 325              # top of the first menu word (in Load and Settings: the list's place on the right)
ROW_Y = 885              # 2026-11-21 (Tefa): on the main menu's top level the words stand in ONE ROW along the bottom,
                          # centred, so the title in the picture stays clear; the menu's own Up/Down walk it (Left/Right: see menu_row/)
ROW_GAP = 60              # space between two words in the row
ROW_SCRIPTS = os.path.join(HERE, "menu_row")   # our script that lays the row out after MAPMO (copied into the mod)
MENU_CAP = 36             # height of the menu font's capitals: 36 of the 50-high row leaves a clear gap (Tefa: rows too close at 43)
FONT_LINE, FONT_TOP = 54.2, 49.2   # the font file's two placing numbers, tuned by picture so words sit in their rows
TITLE_SHOWN_WIDTH = 1600  # the title row's width on screen (16:9 is 1,707 wide)
TITLE_Y = 26
TITLE_ROW_ON = 0           # 2026-11-21: off, the main menu picture has "A Tale of Two Wastelands" painted in it
TITLE_FILE = os.path.join("textures", "interface", "nevergetsold", "title_row.dds")
TITLE_GAME_PATH = "Interface" + chr(92) + "NeverGetsOld" + chr(92) + "title_row.dds"
LOGO_SOLID_FROM = 190     # MAPMO's logo letters are this see-through at their most solid (of 255): made 255

VUI = os.path.join("mods", "Vanilla UI Plus (New Vegas)", "Menus", "Options", "start_menu.xml")
TITLE = os.path.join("mods", "MAPMO - Main and Pause Menus Overhaul", "menus", "prefabs", "mapmo", "startmenu", "pause_title.xml")
LOGO = os.path.join("mods", "MAPMO - Main and Pause Menus Overhaul", "textures", "MAPMO", "Logos", "ba_ttw_futura.dds")

LIST_OLD = """			<x>
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
LIST_NEW = f"""			<!-- It Never Gets Old: 1 on the main menu's top level (title showing, no Back button) -->
			<_NeverGetsOldLeft>
				<not src="sibling(main_back_button)" trait="visible"/>
				<and src="sibling(main_title)" trait="visible"/>
			</_NeverGetsOldLeft>
			<!-- It Never Gets Old: 1 on the main menu inside a sub-menu (Load, Settings): the list stands right of the panel,
			     which MAPMO's script puts to the LEFT of the list, so both end up on the left of the screen -->
			<_NeverGetsOldSub>
				<copy src="sibling(main_back_button)" trait="visible"/>
				<and src="sibling(main_title)" trait="visible"/>
			</_NeverGetsOldSub>
			<_leftjustify> <copy src="me" trait="_NeverGetsOldLeft"/> </_leftjustify>
			<!-- our row height on the main menu (0 = the list's own, in the pause menu) -->
			<_NeverGetsOldPitch>
				<copy> {ROW_PITCH} </copy>
				<onlyif src="sibling(main_title)" trait="visible"/>
			</_NeverGetsOldPitch>
			<clipwindow> <not src="sibling(main_title)" trait="visible"/> </clipwindow> <!-- nothing scrolls here; clipping cut letter tops -->
			<_line_alpha> <copy> 255 </copy> <onlyifnot src="sibling(main_title)" trait="visible"/> </_line_alpha> <!-- each row draws its own box -->
			<_fill_alpha>
				<copy src="globals" trait="_VUI+Highlighting" />
				<mul> 2.5 </mul>
				<onlyifnot src="sibling(main_title)" trait="visible"/>
			</_fill_alpha>
			<x>
				<copy src="parent" trait="width"/>
				<sub src="me" trait="width"/>
				<sub src="parent" trait="_x_buffer"/>
				<onlyifnot src="sibling(main_title)" trait="visible"/>
				<add> <!-- It Never Gets Old: the row, centred (its width is set by our script, menu_row/MenuRow.gek) -->
					<copy src="screen" trait="width"/>
					<sub src="me" trait="width"/>
					<div> 2 </div>
					<onlyif src="me" trait="_NeverGetsOldLeft"/>
				</add>
				<add>
					<copy> {SUBMENU_LIST_X} </copy>
					<onlyif src="me" trait="_NeverGetsOldSub"/>
				</add>
			</x>
			<y>
				<copy src="parent" trait="height"/>
				<sub src="me" trait="height"/>
				<div> 2 </div>
				<onlyifnot src="sibling(main_title)" trait="visible"/>
				<add>
					<copy> {MENU_Y} </copy>
					<onlyif src="me" trait="_NeverGetsOldSub"/>
				</add>
				<add>
					<copy> {ROW_Y} </copy>
					<onlyif src="me" trait="_NeverGetsOldLeft"/>
				</add>
			</y>
			<_NGORowGap> {ROW_GAP} </_NGORowGap>

			<width> 300 </width>"""

INSET_OLD = """					<add>
						<copy> 20 </copy>
						<onlyif>
							<copy src="me" trait="justify"/>
							<eq> &left; </eq>
						</onlyif>
					</add>
				</x>
				<y>
					<copy src="parent" trait="height" />
					<sub src="me" trait="height" />
					<div> 2 </div>
					<add>
						<copy src="me" trait="font" />
						<copy src="globals" trait="_VUI+FontY_"/>
					</add>
				</y>
			</text>

			<text name="lb_item_button_text">"""
INSET_NEW = INSET_OLD.replace("<copy> 20 </copy>", """<copy> 20 </copy>
						<sub> <!-- It Never Gets Old: the box sits evenly round the words -->
							<copy src="grandparent" trait="_NeverGetsOldLeft"/>
							<mult> 5 </mult>
						</sub>""")

ITEM_OLD = """			<brightness> <copy src="io" trait="brightness"/> </brightness>
			<height> <copy src="io" trait="_item_height"/> </height>
			<user0> 0 </user0> <!-- action mapping visibility: 0=none 1=button text 2=button icon -->"""
ITEM_NEW = f"""			<brightness> <copy src="io" trait="brightness"/> </brightness>
			<height> <copy src="io" trait="_item_height"/> </height>
			<!-- It Never Gets Old: on the main menu no highlight box at all (Tefa 2026-11-19: it was too small for the word); the
			     chosen word stays bright and the others are dimmed. (Tried 2026-11-19 and dropped: our own row height and
			     stacking here. MAPMO's script sets every row's height and place itself at the start, so the rows stay 50 apart.) -->
			<clips> <not src="parent" trait="_NeverGetsOldPitch"/> </clips>
			<xleft> <ref src="sibling" trait="mouseover"/> </xleft> <!-- Left = the word before (proven 2026-11-21, flat); no "next" source exists for Right: Right = Down -->
			<user0> 0 </user0> <!-- action mapping visibility: 0=none 1=button text 2=button icon -->"""

BRIGHT_OLD = """				<brightness>
					<copy src="me" trait="alpha"/>
					<add> <!--VUI+ target highlighting -->
						<copy src="globals" trait="_VUI+Highlighting" />
						<onlyif src="parent" trait="_VUI+Highlighted" />
					</add>
				</brightness>"""
BRIGHT_NEW = BRIGHT_OLD.replace("""				</brightness>""", f"""					<sub> <!-- It Never Gets Old: the words not chosen are dimmer on the main menu (there is no box) -->
						<copy> {DIM_OTHERS} </copy>
						<onlyifnot src="parent" trait="_VUI+Highlighted" />
						<onlyif src="grandparent" trait="_NeverGetsOldPitch" />
					</sub>
				</brightness>""")

ROW_OLD = """		<image name="main_title">"""
ROW_NEW = """		<!-- It Never Gets Old: our own title row, top centre, on the main menu -->
		<image name="NeverGetsOldTitle">
			<visible> <!-- not while Load or Settings is open: their panel reaches the top -->
				<not src="sibling(main_back_button)" trait="visible"/>
				<and src="sibling(main_title)" trait="visible"/>
				<and> {title_on} </and> <!-- 0 since 2026-11-21: Tefa's new picture carries the title itself -->
			</visible>
			<alpha> <copy src="sibling(main_title)" trait="alpha"/> </alpha>
			<depth> 2 </depth>
			<systemcolor> &nosystemcolor; </systemcolor>
			<filename> {path} </filename>
			<zoom> {zoom} </zoom>
			<width> <copy src="me" trait="filewidth"/> </width>
			<height> <copy src="me" trait="fileheight"/> </height>
			<x>
				<copy src="screen" trait="width"/>
				<sub> {shown} </sub>
				<div> 2 </div>
			</x>
			<y> {y} </y>
		</image>

		<image name="main_title">"""

HIDE_OLD = """  <visible>
    <copy src="main_title" trait="visible"/>
    <add src="io" trait="_MAPMOShowLogoInPauseMenu"/>
  </visible>"""
HIDE_NEW = """  <visible> <!-- It Never Gets Old: not on the main menu (our title row is there) -->
    <copy>0</copy>
    <add src="io" trait="_MAPMOShowLogoInPauseMenu"/>
  </visible>"""


def change(text, old, new, what):
    for o, n in ((old.replace("\n", "\r\n"), new.replace("\n", "\r\n")), (old, new)):
        if text.count(o) == 1:
            return text.replace(o, n)
    sys.exit(f"NOT FOUND (or found twice): {what}. Nothing written.")


def write_dds(im, path):
    w, h = im.size
    pf = struct.pack("<II4sIIIII", 32, 0x41, bytes(4), 32, 0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000)
    head = b"DDS " + struct.pack("<IIIIIII", 124, 0x100F, h, w, w * 4, 0, 0) + bytes(44) + pf + struct.pack("<IIIII", 0x1000, 0, 0, 0, 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(head + im.tobytes("raw", "BGRA"))


def solid_logo(src, dst):
    """MAPMO's logo with its letters made solid: same size, same colours, the see-through value scaled up."""
    r, g, b, a = Image.open(src).convert("RGBA").split()
    a = a.point(lambda v: min(255, round(v * 255 / LOGO_SOLID_FROM)))
    write_dds(Image.merge("RGBA", (r, g, b, a)), dst)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font", default=FONT, help="the menu font and title row's font (default: Alfa Slab One)")
    a = ap.parse_args()
    # read and change the two layout files first: if either has moved on, nothing at all is written
    with open(os.path.join(a.mo2, VUI), encoding="latin-1", newline="") as f:
        menu = change(f.read(), LIST_OLD, LIST_NEW, "the menu list's place in start_menu.xml")
        menu = change(menu, INSET_OLD, INSET_NEW, "the words' inset in start_menu.xml's list item")
        menu = change(menu, ITEM_OLD, ITEM_NEW, "the list row's height in start_menu.xml")
        menu = change(menu, BRIGHT_OLD, BRIGHT_NEW, "the list words' brightness in start_menu.xml")
    with open(os.path.join(a.mo2, TITLE), encoding="latin-1", newline="") as f:
        logo = change(f.read(), HIDE_OLD, HIDE_NEW, "the logo's 'visible' in pause_title.xml")
    title_out = os.path.join(a.out, TITLE_FILE)
    os.makedirs(os.path.dirname(title_out), exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, "menu_title.py"), a.font, title_out], check=True)
    with open(title_out, "rb") as f:
        title_w = struct.unpack_from("<I", f.read(20), 16)[0]
    row = ROW_NEW.format(title_on=TITLE_ROW_ON, path=TITLE_GAME_PATH, zoom=round(TITLE_SHOWN_WIDTH * 100 / title_w, 2), shown=TITLE_SHOWN_WIDTH, y=TITLE_Y)
    menu = change(menu, ROW_OLD, row, "main_title in start_menu.xml")
    for dst, text in ((os.path.join("Menus", "Options", "start_menu.xml"), menu),
                      (os.path.join("menus", "prefabs", "mapmo", "startmenu", "pause_title.xml"), logo)):
        p = os.path.join(a.out, dst)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="latin-1", newline="") as f:
            f.write(text)
        print("written:", dst)
    solid_logo(os.path.join(a.mo2, LOGO), os.path.join(a.out, "textures", "MAPMO", "Logos", "ba_ttw_futura.dds"))
    print("written: the solid pause logo")
    subprocess.run([sys.executable, os.path.join(HERE, "game_font.py"), a.font, a.out, "--fnt", "glow_futura_caps_large",
                    "--tex", "NeverGetsOld_Menu_0_Lod_A", "--cap", str(MENU_CAP), "--line", str(FONT_LINE), "--top", str(FONT_TOP), "--caps-only", "--worn"], check=True)
    for rel in (os.path.join("NVSE", "Plugins", "Scripts", "gr_NeverGetsOldMenuRow.txt"),
                os.path.join("NVSE", "user_defined_functions", "NeverGetsOld", "MenuRow.gek")):
        dst = os.path.join(a.out, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(ROW_SCRIPTS, os.path.basename(rel)), dst)
        print("written:", rel)


if __name__ == "__main__":
    main()
