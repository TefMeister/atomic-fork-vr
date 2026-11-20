# Main menu row: why every word is equally bright, and how Left/Right can move the choice

Reader note, 2026-11-21 (static reading only; nothing launched, nothing replaced).
Paths below are relative to the Mod Organizer `mods\` folder unless said otherwise.

## 1. What sets `_VUI+Highlighted`

`Vanilla UI Plus (New Vegas)\Menus\Prefabs\list_box_template.xml:39-43`:

```xml
<_VUI+Highlighted>
	<copy src="me" trait="y" />
	<eq src="parent" trait="_highlight_y" />
	<and src="parent" trait="_VUI+Focus" />
</_VUI+Highlighted>
```

- It is true when the item's **y equals the list's `_highlight_y`**, and the list has `_VUI+Focus`. [measured]
- `_highlight_y` is "Y-value of highlight box ... Automatically set in code", default `-1`
  (`...\Prefabs\list_box.xml:56-58`); the highlight box itself copies it (`list_box.xml:103`). [measured]
  The game exe carries `_highlight_y`, `_selected_height`, `lb_highlight_box`, `_scroll_delta` as code-set
  trait names (FalloutNV.exe strings). [measured] So the engine writes the selected item's y into it. [inferred]
- It does not read `mouseover` at all: it follows whatever item the list itself has selected, whether
  chosen by mouse, keyboard or pad. [inferred: the engine's list code chooses which item is selected]
- `_VUI+Focus` on our list = "Back button not visible" (our `start_menu.xml:251`), so it is 1 on the top level. [measured]
- Our dimming reads it: `ListItemText` brightness minus 110 when the item's `_VUI+Highlighted` is false
  and the list's `_NeverGetsOldPitch` is 1 (our `start_menu.xml:1006-1017`). [measured]
- Load order: our bridge mod is above VUI+ and MCM in every rung-05+ profile (e.g. the
  `It Never Gets Old VR` profile has the bridge at lines 2-3, VUI+ at 558, MCM at 625), so our start_menu.xml
  and VUI+'s list_box_template.xml are the ones in use (MCM ships an older list_box_template.xml that loses). [measured]

## 2. Why all six words lit up at once (and all dimmed when the window was behind)

Our script puts **every row item at y = 0** on the top level (`tools/menu_row/MenuRow.gek:41`,
`SetUIFloatAlt (sNGORowP + "\y") 0`). [measured] So:

- When the list has any item selected, `_highlight_y` = that item's y = **0**, which equals **every** item's y,
  so all six are "highlighted", none gets the minus 110, and all six are equally bright. [inferred, fits the observation exactly]
- When nothing is selected (window not in front, cursor elsewhere), `_highlight_y` stays at -1 (or another non-0 value),
  no item matches, and all six are dimmed. [inferred, fits the observation exactly]
- Down, Left/Right or the mouse then change which item is selected, but every item still sits at y 0, so the
  brightness cannot show it. **The capture was not stale: the test itself cannot show the selection.** [inferred]
  It also means we have NOT yet seen whether Down or our Left/Right actually moved the selection.

## 3. How the menu moves its selection

Navigation traits that exist in the game: `xdefault`, `xup`, `xdown`, `xleft`, `xright`, `xbuttona/b/x/y/lb/rb/lt/rt/
start`, `repeatvertical`, `repeathorizontal` (all present as trait names in FalloutNV.exe). **`xlist`, `xitem`, `xscroll`
do not exist** (0 hits in the exe and 0 in every mod's menus). [measured]

Real uses in this list's mods:

- `xdefault 1` on every list item, comment "necessary for keyboard navigation" (`VUI+ ...\list_box_template.xml:23`);
  `repeatvertical 1` "necessary for controller navigation" (`:24`). [measured]
- `xup` → `MCM_Trigger` mouseover on our `main_container` (our `start_menu.xml:250`; VUI+ original `:204`). VUI+ moved it
  there from every list item; MCM's own copy still has it on each item (`MCM\menus\prefabs\list_box_template.xml:46`). [measured]
  Since Up still moves inside lists with that on every item, the list's own Up/Down must win and `xup` only fires when
  the list cannot move (top edge). [inferred] So list Up/Down is the list's own code, by list order, not by screen position. [inferred]
- Left/Right turned into clicks, on the menu root: `quantity_menu.xml:18-19` (`xleft`/`xright` → decrease/increase arrow
  `clicked`), `sleep_wait_menu.xml:13-14` (→ horizontal scrollbar arrows). [measured]
- All four directions turned into clicks on hidden hotrects that a script reads: `Prefabs\MCM\MCM.xml:994-997`
  (`xdown/xleft/xright/xup` → `child(InputDown/Left/Right/Up)` `clicked`), read back as `_left`/`_right` at `:1003`, `:1006`. [measured]
- `repeathorizontal` (Left/Right change a value on the selected item, held key repeats): level-up skills
  (`levelup_menu.xml:381`), settings meters (our `start_menu.xml:1129`), chargen (`char_gen_menu.xml:354`), race/sex sliders
  (`race_sex_menu.xml:285`), quantity (`:96`), sleep/wait (`:77`), hacking (`:289`), caravan (`caravan_builddeck_menu.xml:192`),
  Stewie's menu (`stew_menu.xml:474`). [measured]
- **No horizontal list navigated with Left/Right** exists in any loose menu file here (no Pip-Boy, barter or tab XML
  in the loose files; the vanilla ones are packed in `Fallout - Misc.bsa`, compressed, not read). [measured / not checked]

## 4. Recommendation

**First, make the brightness able to show the choice** (nothing else can be judged until then). Either:

- A (keeps VUI+'s logic): in MenuRow.gek give each item a different, invisible y, e.g. `y = index * 0.01` instead of 0, so only
  the selected one equals `_highlight_y`. Risk: if the engine fills `_highlight_y` from something other than the item's
  y trait, it will not match. [inferred]
- B (vanilla pattern): base the dimming on the item's `mouseover` instead of `_VUI+Highlighted` (vanilla race/sex items
  light up on `mouseover`, `race_sex_menu.xml:176-182`; VUI+ meters treat `mouseover` as the pad's selection,
  our `start_menu.xml:1153-1154`). Risk: the mouse cursor may override a key choice. [inferred]

Before choosing, one cheap logging run: each frame write `main_container\_highlight_y` and, per item, `y`, `mouseover`
and `_VUI+Highlighted` (GetUIFloatAlt) to the log while pressing Down, Left, Right and moving the mouse. That replaces
the screenshot and shows which of A or B the engine supports.

**Then Left/Right.** The list's own Up/Down are the reliable mover (list order, edges handled by the game). Two ways to reach them:

1. Keep the TapKey 200/208 bridge (keyboard). Check in the log that one Left/Right press moves exactly one step
   (if the game also moves on native Left/Right, ours doubles it). `IsKeyPressed 203/205` does not see the pad's
   D-pad. [inferred]
2. Better, one route for keyboard AND pad: copy MCM's pattern. Put `<xleft> <ref src="child(NGOLeft)" trait="clicked"/> </xleft>`
   and the same `xright` on `main_container` (where `xup` already sits), add two hidden hotrects `NGOLeft`/`NGORight`,
   and have MenuRow.gek read their `clicked` and answer with TapKey 200/208. This uses the game's own direction handling,
   so the D-pad comes for free. Unproven here: whether `xleft`/`xright` on the list fire while a list item is selected
   (`xup` on the same tile does, at the top edge). [inferred] Test it with the same logging run.

Fallback for the pad only: `Controller Support NVSE` can map `DPAD_LEFT`/`DPAD_RIGHT` to keys, but it is set
`GameModeOnly = 1` (menus ignored) and would affect every menu if opened up (`Controller Support.ini`). [measured]
