# 2026-11-19 (evening): Tefa's picture on the main menu, and no music there

Lane: /lm, Developer PC, flat screen (profile `rung-05 interface flat`). Job raised by the Keeper PC from Tefa the same
day: *"use as the Fallout main menu background and ... remove the music from it please"*.

## What the main menu uses in this setup

- **Background:** `textures/interface/main/main_background.dds`. Two mods carry it: `Begin Again Main Menu`
  (1920 x 1080, DXT1, no mip levels) and `Vanilla Loading Screens HD` (2048 x 1024); Begin Again Main Menu sits higher
  in the list and won `[measured: the mod list; verified-live 2026-11-19, n=1: the before-picture shows its art]`.
- **Music:** `Music/Special/MainTitle.mp3` (the game's setting `SMainMenuMusicTrack=special\maintitle.mp3`), supplied
  by `Begin Again - Menu Music Replacer` `[measured]`. No game master or plugin in the list names that file
  (a text search of every .esm / .esp; only MAPMO's settings mention "MainTitle", for its logo and volume)
  `[inferred-static]`, so replacing it touches the main menu alone.
- **Why the menu still had music with our "music off" setting:** `MAPMO - Main and Pause Menus Overhaul` sets the
  game's `fMainMenuMusicVolume` itself, from its own `fMainTitleMusicSound` (25 in Begin Again's config)
  `[measured: the setting and the plugin's strings]`. Our `fMainMenuMusicVolume=0.0` in every rung's
  `falloutcustom.ini` (since 2026-11-10) is overwritten where MAPMO is on. Before the mod the menu measured
  sounding 100 % of 12 s, loudest -23 dB `[verified-live 2026-11-19, n=1]`. This answers FO-011 for the menu: no, it
  did not stay off. In-game music (`fDefaultMusicVolume=0`) is a different setting and was not looked at here.

## The mod: `Bridge - Atomic Fork main menu` (source in `bridge-mods/`)

| file | what | made with |
| --- | --- | --- |
| `textures/interface/main/main_background.dds` | Tefa's picture, 1920 x 1080, uncompressed 32-bit, no mip levels | `tools/menu_picture.py` |
| `Music/Special/MainTitle.mp3` | 60 s of digital silence (44.1 kHz stereo, 64 kbit/s) | ffmpeg (`anullsrc`) |

- The picture is 1672 x 941; the file needs 1920 x 1080. The shapes differ by 0.05 % (half a pixel), so it was resized
  whole: **no crop, no padding**. Uncompressed on purpose: the DXT1 of the file it replaces would put blocks in the
  sky's fade.
- On at the very top of the list in all 69 `rung-*` profiles (the top wins); `tools/ladder_groups.py` `BRIDGE_MODS`
  keeps it on when a rung is rebuilt. The list's own profiles (`Begin Again`, `Debug Mode`) are not changed, and no
  Begin Again or TTWVR file is. The mod lists as they were: `modlists.bak-2026-11-19-before-menu-mod.tgz` beside the
  profiles folder.

## Proof (flat, `rung-05 interface flat`, the monitor, 3440 x 1440)

| | before the mod | with the mod |
| --- | --- | --- |
| picture | Begin Again's two helmets | the Atomic Fork VR picture `[verified-live 2026-11-19, n=1]` |
| sound at the menu, nothing pressed | sounding 100 % of 12 s, loudest -23 dB | **silent**: 0 % of 20 s `[verified-live 2026-11-19, n=1]` |
| sound while Down is pressed twice | (not measured) | two short clicks (loudest -18 dB, 2 % of 6 s): effects still play `[verified-live, n=1]` |

State-o-matiC both times: "still" (a menu), not hung. Sound measured with `tools/menu_listen.py` (what the PC's sound
output plays; silent with the game closed before each run). Pictures:
`2026-11-19-pictures/flat - main menu before (Begin Again picture).jpg` and
`flat - main menu with the Atomic Fork picture.jpg`.

## NOT established

- **The headset.** Only the flat game was started. The file and the music are the same in VR, but how the picture
  sits in TTWVR's menu view was not looked at.
- **The look on other screen shapes.** On this 21:9 monitor the game stretches the 16:9 picture sideways to fill the
  screen (it did the same to Begin Again's). On a 16:9 view it is undistorted `[inferred-static]`.
- **The words on top.** MAPMO's "FALLOUT: TALE OF TWO WASTELANDS" logo (left) and the menu items (right, over the
  word FORK) are drawn over the picture. Both are MAPMO settings (logo choice, position); nothing was changed.
- Speech: the main menu has none, so "speech stays" could not be shown there; nothing but the one music file changed.

## Driving the menu (new)

Enter HELD about 0.12 s (SendInput, scancode) selects the highlighted item; the short tap of 2026-11-09 did not. Down
moves the highlight (the first Down lights Continue). Quit closes the game at once, no question, and Mod Organizer
with it within 3 s `[verified-live 2026-11-19, n=2]`.
