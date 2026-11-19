# 2026-11-19 (late evening): the main menu's layout, title, font and the start-up picture

Lane: /lm, Developer PC, flat screen (`rung-05 interface flat`), with Tefa at the monitor answering picture by picture.
Follows `2026-11-19c-main-menu-picture-and-silent-title-music.md`. Tefa's yes to the result: 2026-11-19, "yes".

## What is installed

- **`Bridge - Atomic Fork main menu layout`** (our second menu mod, built by `tools/menu_layout.py` straight into the
  list's mods folder; not kept in the repo because two of its files are changed copies of the list's own):
  - a one-row title "FALLOUT: TALE OF TWO WASTELANDS", top centre, drawn by `tools/menu_title.py` from Alfa Slab One:
    the menu's yellow, worn (chipped rim, scratches, a few rust spots), 1,600 menu units wide so it fits 16:9;
  - the menu words on the left of the picture, between the flag and the radiation sign, left-aligned;
  - the game's big caps font (number 8) replaced by one made from Alfa Slab One (`tools/game_font.py`): capitals 36
    units in the 50-unit rows; it also shows in the pause menu and wherever else the game uses that font;
  - a highlight box fitted to the chosen word (each row draws its own; the list's wide box is off on the main menu);
  - Load and Settings open on the left: the list stands at x 1010 while a sub-page is open, and MAPMO's script puts
    the page to the left of the list; the title row hides meanwhile;
  - MAPMO's own logo is not drawn on the main menu; its picture is written again with solid letters (pause menu).
- On in the 53 rung profiles that have both Vanilla UI Plus and MAPMO (rung 5 and up); listed but off in the 16
  without them; `ladder_groups.py` keeps that rule on a rebuild.
- **Mod Organizer's start-up picture** (`Splash.png` in the list's folder) is the ATOMIC FORK VR logo cut out of
  Tefa's picture (source `bridge-mods/mo2-splash/`); Begin Again's is kept beside it as
  `Splash.png.bak-2026-11-19-begin-again`. Seen on screen at a start `[verified-live 2026-11-19, n=1]`.

## What was learned

- **The game's font files.** `.fnt`: a float (line height), two ints (1, 1), the picture's name in 284 bytes, then
  256 letters of 14 floats: 0, four corners in the picture, width, height, space before, space after, and the box
  top's height above the writing line. `.Tex`: two ints (width, height) and plain RGBA; white is tinted to the menu
  colour, dark stays dark `[verified-live: our font draws in the game]`. Raising the line height and the 'top'
  number lifts a line of text; the pair 54.2 / 49.2 seats 36-unit capitals in a 50-unit row `[measured by picture]`.
- **Lists clip** what hangs outside them (`clipwindow`): it cut the first word's top and the last word's bottom until
  switched off for the main menu's list.
- **MAPMO's logo is see-through by its own picture** (alpha about 190 of 255), not by a setting.
- **MAPMO's script lays the menu rows out itself** (row height 50, each row's height and place, the list's width =
  the widest word + 30) once at the start. Our own row height in the layout file did not take, even tied to the
  list's fade `[verified-live, n=1]`. Taller rows need a script of our own running after MAPMO's.
- **Sub-pages follow the list:** MAPMO places Load and Settings to the LEFT of the main list, wherever it stands.
- **Esc and Tab do not go back on the Load page with the stock layout either** `[verified-live, n=1 each]`. Enter
  worked on every fresh start and failed several times after the game's window had lost the front and got it back
  `[hypothesis: the focus change]`. With the first layout (list under MAPMO's logo) Enter failed three times running;
  cause not isolated.

## NOT established

- The headset: none of this was looked at in VR.
- Whether Enter's failures come from the focus change (no clean test).
- The logo cut-out is automatic (GrabCut inside a hand-set outline): a faint glow is left on a few edges.

## A slip, for the record

On the Load page I pressed Enter after an Esc without looking; Esc had not gone back, and the lit save loaded. The
game was closed at once (polite close); no save file was written (checked by date).
