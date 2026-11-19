# 2026-11-19: what test A does differently, the line in the water, the rings in the sky

Developer PC, `/lm`, the full-auto run (game 6 of 6), Tefa away for the first part and at the keyboard for the
second. Rung 5 and its test copies on the OpenXR Simulator, the "Save 4" spot. Nothing was worn today.

## 1. Tefa's observation

Tefa, 2026-11-19: *"the rung 5 D,E and F tests all had smudging, A is the only one with a clean picture"* `[reported]`.

## 2. What A switches off that D, E and F leave on

Read from the six profiles' mod lists against plain rung 5 `[measured]`:

| copy | switched off | Tefa in the headset |
| --- | --- | --- |
| A | LOD Flicker Fix, Depth Resolve, Vanilla Plus AO / Particles / Skin / Terrain | clean, no blinking, skyline still |
| C | Vanilla Plus AO | smudge |
| D | Depth Resolve, Vanilla Plus AO, Vanilla Plus Particles | smudge |
| E | Vanilla Plus Skin, Vanilla Plus Terrain | smudge |
| F | High Resolution Water Fog | smudge |
| B | Depth of Field Fix, Alpha Rendering Tweaks, Fog-based Object Culling, High Resolution Water Fog, Real Time Reflections | smudge, puddle correct |

D and E together cover all five add-ons, and both smudge. **The only thing A alone switches off is LOD Flicker Fix
itself.**

Why that add-on: it turns the game's depth picture back to front (near = 1, far = 0), by its own page and its public
source `[measured, the reader]`. It has no setting. TTWVR 1.0.0 reads depth the old way round in every place that
could be read: the upscaler helper's motion shader (sky = depth at 1, the old distance formula, and "anything below
0.0002 is your own hands and gun"), the culling grid shader, the blood shaders `[measured, the reader, from the
helper's plain-text shaders]`. With the picture reversed, most of the world gets the wrong distance, so the upscaler
gets the wrong motion when the head moves (the smudge), the culling grid is built from the misread depth (the
one-frame blinking) and a hard distance border appears past which the world is treated as a held object (the skyline
that slides) `[hypothesis for each symptom; the mechanism is inferred-static]`.

One caveat, the reader's: on 2026-11-14 the smudge was said to stay with the upscaler off. If that holds, LOD Flicker
Fix's own replacement shaders for grass, far objects and trees are the second suspect. The practical answer is the
same either way.

**The test that settles it: `rung-05 test G LOD flicker fix alone on`** (built today): LOD Flicker Fix on, its five
add-ons off. Smudge = LOD Flicker Fix itself, and A's set stays off in VR. Clean = the add-ons, and LOD Flicker Fix
can stay. G passes `ladder.py check` and `needs_check.py`, starts and loads Save 4 on the simulator
`[verified-live 2026-11-19, n=1]`.

What is lost in VR with A's set off: far objects may flicker against each other again; the soft contact shadows; the
soft edge where smoke meets the ground; the nicer skin; the ground shine at low sun. Flat keeps all of them.

Teaching TTWVR the reversed depth is possible but is a rewrite in five places (two helper shaders, two blood
shaders, the grid's user, the near-pass slice): not planned.

## 3. Can the desk see the smudge? Not yet

`tools/sim_smudge.py` (new) takes eye pictures with the head still and with the head swaying and compares the fine
detail. Test G: moving:still 0.95 to 0.98 `[measured, n=1]`. A and plain rung 5 were not measured, and the
simulator's eye picture is only 569 pixels wide, so this number says nothing yet.

## 4. The line through the water

Tefa: *"the water having a clear line going through it, one side is brighter green than the other"*.

On the simulator at Save 4 the water shows a brighter near sheet and a darker far band with a straight border
(pictures in `2026-11-19-pictures/`):

- the same in tests A, B, F and G `[verified-live, n=1 each]`: no Begin Again drawing add-on makes it;
- console `tll` (far land and far water off): the darker far side is gone, the near sheet ends in one straight edge
  with sky behind it; `tws` (water off): both gone `[verified-live, n=1]`.

**So the line is the border between the near water (the loaded area, the full water shader) and the far water.**

TTWVR forces 33 game settings every frame from a built-in list (file offset 0x9067B0, 16 bytes a row, the value a
float at +8) `[measured]`. For water: refractions on; reflections off; reflection size 256; ripples off; **depth haze
off** (its own label: "off - fps144 T2", a speed choice). That is why typing the setting in the console never
changed anything. The far water is not in the list.

Two tries in our own copy of TTWVR.dll (the mod `Bridge desk test - water as the game asks`, profile
`rung-05 test W water depth haze on`; the original DLL untouched):

1. depth haze on (0x9068C8 = 1.0): the near water is see-through at the shore again and darkens with depth; the
   line to the far water is still there `[verified-live, n=1]`;
2. depth haze and reflections on (0x906858 = 1.0 as well): the near water mirrors the sky and the rocks; now it is
   the BRIGHTER side and the far band the darker one: still a line `[verified-live, n=1]`.

Not established: what either costs in frame time; whether flat shows the same border at this spot and hour (the
flat twin of rung 5 was not run today; on 2026-11-13 flat showed one grey-blue lake); whether the far water gets a
reflection at all in VR. Next: a flat still at the same spot and game hour, then the far water's side of it (which
shader draws it, what it takes its colour from).

## 5. The rings in the sky

Tefa: *"it has these visible rings forming as the sky gets brighter or dimmer"*.

`tools/sky_bands.py` (new): head tilted up 35 degrees, `set gamehour to 4`, `set timescale to 120`, 40 pictures 4 s
apart (about 04:00 to 09:00), the sky reduced to one brightness per row (the median, so stars do not count).
Table: `2026-11-19-pictures/sky_bands.csv` `[measured]`.

- From the top of the picture to the horizon (52 degrees) the sky uses **2 to 13 brightness values**.
- Each flat band is **5 to 35 degrees** wide; the bands are concentric round the top of the sky
  (`sky at dawn, contrast stretched.png`).
- Every step between bands is **1 level of 256**, the least a screen can show.
- Inside the bands neighbouring pixels differ by 0.03 to 0.2 of a level: **no grain at all**.

So the rings are the rounding of a very gentle fade to 256 levels, with nothing to hide the steps. They are in the
picture before the headset and before Virtual Desktop. As the light changes, the steps move, which is why they
"form". Fewer than 256 levels is not the fault; the perfectly clean fade is.

The cure is dithering: fine noise about half a level strong, added before the rounding, so a band's edge becomes a
soft speckle the eye averages out. Where to add it is the open question: the game's tonemap shader (Begin Again
replaces it with Vanilla Plus Tonemapper) rounds first, but TTWVR's upscaler works after it and would average an
early dither away and round again; the safe place is TTWVR's last copy to the headset. Proof on the desk when it is
tried: `sky_bands.py` shows grain near 0.5 and no flat bands. Virtual Desktop's 10-bit stream setting cannot remove
these rings but stops the video stream adding its own.

## 5b. The rings, second round (afternoon; Tefa: carry on alone)

Tefa also answered the puddle question: *"the small pool with the tyre has so far been green with no reflection
looking at it from one side, going around it makes the water transparent but a layer of something is clearly missing
that makes it actually look like water"* `[reported]`. Not looked at yet on the desk; board row `[ID FO-002]`.

**A measuring mistake first.** The 569-pixel eye picture of section 5 is a shrunken 8-bit copy, and ANY gentle fade
photographed that way shows flat bands one level apart. So "bands of one level" alone proves nothing; what tells a
visible ring from an invisible one is whether the band's edge is a clean line or a speckle, at full size. The
simulator's capture is a photo of its preview window: with `window_width` 3400, `window_height` 1400 and `zoom_scale`
2.6 in its settings the eye picture is 1468 x 1209 (still not 1:1, but the edges can be judged). Settings put back
afterwards (backup `settings.json.bak-2026-11-19-before-full-size`).

At full size, plain rung 5, dawn (`set gamehour to 5.3`): the ring edges are clean lines, and inside a band there
are thin lines one level darker or brighter that follow the ring: the rings are real `[measured, n=4 pictures]`.

Two cures tried, both in our own desk-only mods, both WITHOUT effect:

1. **Noise at the very last step** (`Bridge desk test - sky dither`: our copy of `ttwvr_dlss_host.exe`, whose two
   final shaders are plain text; half a level of noise added to what they write, same file length). The helper
   started and drew; grain 0.059 -> 0.117; the ring edges are as clean as before `[verified-live, n=1]`. So the
   picture is already rounded when it reaches the helper.
2. **Sharpening off** (`Bridge desk test - sharpness 0`: `Sharpness=0%` in an own TTWVR.ini; Tefa's is 65%): the
   rings and the thin lines are the same `[verified-live, n=1]`. Sharpening does not draw them.

**So the rings are made in the game's own picture, before the VR mod touches it**: in the sky's drawing or in the
step that brings the game's bright picture down to 256 levels (Begin Again's Vanilla Plus Tonemapper replaces that
shader: `ISHDRBLENDINSHADER*.pso`, three variants). The thin lines inside the bands suggest two roundings one after
the other, or the sky dome's own rings of points `[hypothesis]`.

NEXT: (1) one flat still of the same sky (the flat twin of rung 5): rings in flat too = the game / Begin Again, not
VR at all, and Begin Again's flat players have them as well; (2) a dither in our own copy of the tonemapper shader
(needs the shader taken apart and rebuilt: ps_3_0, screen position from `vPos`), loaded after Begin Again's by
Shader Loader, in the VR rungs only; (3) check at full size that the upscaler does not smooth it away; if it does,
the noise has to move with the frame or be added at both ends.

## 5c. The rings, third round: the cure works on the desk

Tefa, 2026-11-19: *"the rings also appear in the flat version of the game and possibly the water line too"*
`[reported]`. So the rings are the game's / the list's own, not VR's; the flat still was not needed.

`tools/dither_pso.py` (new) takes a ps_3_0 shader apart with Windows' own shader library, adds half a level of
fine noise (made from the pixel's place on the screen) to the final colour write, and puts it together again. Run on
Vanilla Plus Tonemapper's three `ISHDRBLENDINSHADER*.pso` (the step that brings the game's bright picture down to
256 levels); the three results live in our own mod `Bridge - smooth sky`, which wins over Begin Again's files without
touching them.

Rung 5 with that mod, same sky, same hour, full size `[verified-live, simulator, n=1 run, 4 pictures]`:
- the hard ring edges are gone: each edge is a speckle that fades from one level to the next
  (`2026-11-19-pictures/sky full size - plain left, tonemapper dither right, stretched.png`; the contrast is
  stretched about 60 times, the soft waves left in it are far below what an eye sees);
- grain 0.066 -> 0.356 of a level; the 2%-98% spread of the crop 96-97 -> 95-98;
- the upscaler (DLSS Quality) did NOT smooth the noise away: it is in the picture the headset gets.

Not established: how it looks in the headset (noise of half a level should be invisible; through Virtual Desktop's
video stream it could show as faint grain in dark scenes or be smoothed back into rings); whether the noise standing
still on the screen is noticed when the head turns (if so: make it move with the frame). Strength 1.0 (half a level
each way) is the textbook value; the tool takes another.

To wear: profile `rung-05 test V clean picture and smooth sky` = test A (LOD Flicker Fix and its five add-ons off)
+ `Bridge - smooth sky`. `ladder.py check` and `needs_check.py` clean; V itself not started on the desk (A and the
mod each were).

## 6. Tools made or mended

- `tools/sim_shot.py`: one eye picture of a running rung, a part enlarged.
- `tools/sim_smudge.py`, `tools/sky_bands.py`: above.
- `tools/console_type.py`: no longer stops when a window of the game has an arrow in its title.
- Found: `rung_simcheck.py --stay` leaves the test save's date bumped to today (the non-stay run puts it back);
  today it was put back by hand from the file's creation date. And `ghidrust` hung 30 minutes on TTWVR.dll (15 MB);
  the reader used a plain Python + capstone scan. Both on the fault list.

## 7. Left as it was found

No game running; VR Bench off; Mod Organizer on `rung-05 test A LOD flicker fix off`; the simulator's keyboard
setting back on "app"; Save 4's date back to 2026-11-13; no new save files. New in the mod list's folder: profiles
`rung-05 test G ...` and `rung-05 test W ...`, `rung-05 test S sky dither`, `rung-05 test T sharpness 0`, and the mods `Bridge desk test - water as
the game asks`, `Bridge desk test - sky dither`, `Bridge desk test - sharpness 0` (desk only, never for a played profile).
