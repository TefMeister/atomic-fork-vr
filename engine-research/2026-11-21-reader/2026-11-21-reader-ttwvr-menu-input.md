# How TTWVR hands the VR controllers to the game's menus (main menu in particular)

Reader note, 2026-11-21. Static only: TTWVR 1.0.0's `NVSE/Plugins/TTWVR.dll` (strings and disassembly), its two
helper exes, `TTWVR.ini` and `TTWVR.dat`. Nothing launched or attached. Addresses are TTWVR.dll VAs (image base 0x10000000).
Supersedes nothing.

## 1. A fake Xbox pad, not keys or a mouse

- **TTWVR hooks `XInputGetState`** (looked up by name and by ordinal 100 in `xinput1_3.dll`): setup at 0x101f07cc,
  detours 0x101f02b0 / 0x101f0320. For pad 0, when its own flag (state+0xBF8) is set, it returns its own 16-byte
  XINPUT_STATE (state+0xBD8); otherwise the real pad; with no xinput1_3, "not connected" (0x48F). [measured]
  String: "xinput1_3.dll not present; analogue movement will not reach the game". [measured]
- It also hooks the game's control read at 0x00A24660 ("keys count with the pad connected") and the controller
  switch, and reads/writes `_Has360Controller` (string 0x108f69ec). [measured]
- **No key or mouse faking:** USER32 imports are only window/monitor calls and MessageBoxA; no SendInput,
  keybd_event, mouse_event, SetCursorPos or GetCursorPos. No dinput import (the "dinput8.dll" string is a name only). [measured]
  The two helper exes import only D3D / ole32 and contain no input or menu strings. [measured]
- **What the pad carries while a menu is open** (pad builder 0x10561f90-0x10562545; XINPUT_GAMEPAD at edi):
  - A (0x1000) from one controller button (0x105620c9 / 0x10562137), B (0x2000) from another (0x10562145), Start (0x10)
    (0x1056214e); Y/X/LB/RB for the Pip-Boy pages (menu ids 0x3EA, 0x3EB, 0x3FF: 0x10562190-0x105622f4). [measured]
    Which physical buttons feed them was not traced. [not checked]
  - **Sticks:** outside the Pip-Boy pages, whichever thumbstick is pushed further (left 0x11c/0x120 vs right 0x124/0x128)
    is written into the pad's LEFT stick, X and Y (0x105623f5-0x10562459, scaled by 32767). [measured]
  - **No D-pad bits for menus.** The only D-pad writes come from an 8-direction table (0x10923724: 5,1,9,4,8,6,2,A =
    the 8 diagonals and sides) used with RB (0x200) for the hotkey wheel (0x10560f8d, 0x10562384). [measured / wheel use inferred]
- **The menus' own up/down/left/right therefore come from the engine reading that left stick** (thumbstick → menu
  direction is the game's own pad navigation). [inferred]
- The menu-input dispatcher hook (game 0x0070F6E0 → 0x10212430, string "pad buttons in menus are left to the engine"):
  for button presses (A/B/X/Y/LB/RB/Start/Back, not the D-pad: mask 0xF3F0 over the game's pad words 0x011D8A58 /
  0x011D8A70) and some special key codes, it briefly swaps the interface's active tile (InterfaceManager+0xBC) with a tile
  of the TOP menu when the current one belongs to another menu, then restores it. It does nothing to directions. [measured code / inferred meaning]
- The "hover check" patch (game call sites 0x0070CD63, 0x00715BC0) wraps the game's visibility test so tiles TTWVR hides
  from the eye pictures still count as visible. [measured code / inferred meaning]

## 2. No pointer, laser or cursor on menus

- No "cursor", "laser" (one shader comment only), "pointer at menu" or "point at" wording for menus; `bPointToActivate`
  (0x107460ec) is for activating things in the world. [measured]
- The StartMenu is in `sFlatMenus` = "Start,Loading,Credits" by default (key 0x10746334, value 0x10746344); our
  TTWVR.ini only has the [VR] section and does not change it. So the main menu is shown flat and driven by the pad
  only. [measured / meaning inferred]
- TTWVR never sets the game's cursor (no cursor API imports, no cursor strings). [measured]

## 3. What would make left/right on the stick move along our row

The stick reaches the menu only as the pad's left stick, and the engine handles the direction. Script keys cannot do it
(coordinator, verified live 2026-11-21). In order of cost:

1. **XML only, try first:** on each row item, `<xleft>` / `<xright>` pointing at the neighbouring item's `mouseover`,
   the way VUI+ points `xup` at `MCM_Trigger`'s `mouseover` (our start_menu.xml:250). The items come from one template,
   so the neighbour has to be named by position (`src="sibling"` = the previous one), and the other direction needs a
   different route. Unproven: whether the engine takes xleft/xright on a list item, and whether setting mouseover moves
   the list's own selection. [inferred] One run with the `_highlight_y` log answers it.
2. **Our own small hook (reliable, no TTWVR change):** patch FalloutNV.exe's import of `XInputGetState` (the import
   table entry, so load order with TTWVR does not matter). Call through (which reaches TTWVR's fake pad), then, only while
   the StartMenu is on its top level, turn the left stick a quarter turn: new Y = minus old X. Stick right = Down = next
   word, stick left = Up = previous word, the same mapping MenuRow.gek uses. The engine moves the selection itself,
   and the edges and key repeat stay the game's. [inferred]
3. **A TTWVR change** (the same axis swap in its pad builder, 0x105623f5) would also do it, but it is KUPOkinz's binary:
   a request, not something we patch.
