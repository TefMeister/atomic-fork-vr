# 2026-11-19 late to 2026-11-20 00:40: the source list's name out of the fork; menu and Mod Organizer look; the water line in flat

Lane: plain session on the Developer PC, Tefa at the desk. Follows `2026-11-19d-main-menu-layout-title-font-splash.md`.

## The name (Tefa 2026-11-19: "we cannot have Begin Again written down anywhere", the source author's condition for a fork)

- `tools/list_rename.py` (dry run first, `--go` to do it; a second run finds nothing): every mod folder, plugin, archive,
  `.override` mark, the per-plugin CellOffsets folder and the menu-mod preset that carried the name now say
  "Atomic Fork VR" (`BA Weathers` too); all 71 profiles (and the load-order backups inside them), ModOrganizer.ini,
  nxmhandler.ini, the Wabbajack compiler settings and the download archives with their .meta files follow. Nexus
  descriptions that named the list are emptied (only shown in MO2's info box). The divider is `ATOMIC FORK VR`, the
  start entry `Atomic Fork VR`, the base profile `Atomic Fork VR`. Then the list folder and the downloads folder were
  renamed to `Atomic Fork VR`, with the nxm link handler (registry) and a new desktop shortcut.
  `[verified-live 2026-11-20, n=2]`: the flat game starts on the renamed list and loads Save 4.
- No plugin had a renamed plugin as a master (read from every plugin's header), so nothing else needed changing.
- Left alone on purpose: the Fallout 3 radio song "Begin Again" (inside the game's own .esm files and TTW's credits).
- Old backups and logs that still hold the name moved out of the list to the backups folder beside it (nothing deleted).
- **Saves name their plugins.** Save 4 then said "This save relies on content that is no longer present" (the four
  renamed plugins). `tools/save_rename.py` rewrites the names in the .fos (plugin list + the five location numbers right
  after it, all shifted by the growth and checked to land on the same bytes) and the .nvse co-save (MODS chunk and string
  elements of array variables, every chunk length redone); originals in the saves folder's `pre-rename`. After it:
  `save_needs.py` says it opens clean, and it loads `[verified-live, n=2]`. Any other save made before the rename needs
  the same run.
- Our tools follow the new names (`moshortcut://:Atomic Fork VR`, profile `Atomic Fork VR`, the LOD mod names).

## The look

- Title: "FALLOUT : TALE OF TWO WASTELANDS" (space before the colon, Tefa).
- The menu font has the title's wear (`menu_title.wear`, used by `game_font.py --worn`; colours divided by the menu
  yellow so they come out as the title's after the game's tint). Checked on a picture made from the built files.
- No highlight box on the main menu; the words not chosen are 110 darker. `[not seen in the game yet]`
- MO2's start-up picture: only the flat fronts of the logo (cut by brightness, holes filled, the 3D sides and glow
  trimmed); the 3D one kept as `Splash-3d-2026-11-19.png`.
- MO2 style `Atomic Fork VR.qss` (`tools/mo2_style.py`): the list's dark Fluency style in the logo's colours, Alfa Slab
  One on tabs, buttons, headings (installed for this user only); all dividers the logo's red. `[not seen by Tefa yet]`

## The water line, flat, Save 4 (`rung-05 interface flat`), 2026-11-20 00:30

Still there `[measured, n=1, one full-size picture]`: the lake is two flat colours, the far part RGB 71,71,56 and
the near part 85,83,62, changing over about 20 px; neither has surface detail (spread 0-1). Board row FO-002.

## Slips

- The first launch pressed Enter four times at the box without State-o-matiC and only said "save loaded: NO" at the
  end; the later launches had State-o-matiC watching.
- A message to another session quoted "take over atomic-fork-vr"; the project guard read it as Tefa's words and gave
  the project to that session (fault list).

## 2026-11-20 morning: the main menu photographed in 16:9 (Tefa asked for a good picture with everything showing)

- Two full-size pictures of the game's own window, 1920 x 1080, `rung-05 interface flat`, in `2026-11-20-pictures/`:
  `flat - main menu 1920x1080, nothing picked.png` and `... Continue picked.png`. Title, the six words, the Vault Boy
  mark bottom left and the TTW mark bottom right are all in.
- **The menu without the box is now seen in the game** `[verified-live 2026-11-20, n=2]`: no highlight box, the picked
  word bright yellow, the others dimmer.
- How: the flat profiles ask for 1280 x 720, but OneTweak (borderless, sizes on "autodetect") stretches the window over
  the whole 3440 x 1440 screen whatever the game's own size says, so a 16:9 picture came out stretched sideways. For
  this one run OneTweak's window and render size were set to 1920 x 1080 (and the profile's iSize the same); both files
  were put back from their backups afterwards, and MO2's last profile too.
- The game's own mouse arrow sits in the middle of the menu: `tools/menu_mouse_park.py` pushes it into the bottom-right
  corner (relative mouse moves) before `menu_shot.py`.
