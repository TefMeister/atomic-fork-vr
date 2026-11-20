# 2026-11-20 morning: the water line is cured (flat and VR simulator), and why it was there

Lane: plain session on the Developer PC, Tefa at the desk (*"please grind the water line problem on opus however much
you can. if possible, maybe bring the further line forward by blending it in, instead of trying to push the closer one
further"*). Board row FO-002. Follows `2026-11-19-what-test-a-does-differently-the-water-line-the-sky-rings.md` §5d.

## 1. Why the line is there `[measured]`

- **The lake's own cells name their own water.** `tools/water_cells.py` (new): 98 Capital Wasteland cells name
  `PotomacNRShallow` (the Save 4 lake among them, water height 10750); most others name none (= the worldspace's
  Potomac). The far water beyond the loaded cells always uses the worldspace's LOD water, Potomac.
- The two records differ only in three colours and one fog distance: shallow 95,101,48 vs 52,75,52; deep 17,17,4
  vs 27,39,24; mirror colour 53,49,0 vs 19,37,16; DNAM +36 580 vs 460.
- **What the shaders really get**, read off the screen: `tools/water_probe.py` (every water shader paints its inputs
  as stripes) and `tools/water_bits.py` (chosen inputs as binary stripes, exact). Far water = WATER033 (mirror, no
  waves), near = WATER000. Far: shallow and mirror colour = Potomac's bytes exactly, but **deep colour 0,16,28** and
  **VarAmounts.y 0.47 / .z 0.7** come from the engine, not any record (near: the record's 17,17,4 and 0.6 / 0.5).
  Fresnel, sun, fog: the same for both. Evening (the save's hour) and noon (`set gamehour to 12`): identical
  `[measured, n=1 each]`, so the numbers do not follow the time of day.
- So the three fades of 2026-11-19 had the right idea but the wrong target: they fed the far look the NEAR water's
  numbers.

## 2. The cure: `Bridge - water fades into the far look` (Tefa's direction: the far look comes forward)

`tools/water_blend.py` rebuilt: every near-water shader works out the far water's own picture with the measured far
numbers and turns into it between 5120 and 8192 units from the eye (the border is never nearer than 8192). Only the
Capital Wasteland's own water types fade (Potomac, PotomacNRShallow, CreekWater01, matched by their shallow
colour); any other water (the Mojave's) is drawn exactly as before.

| | step at the line before | after |
|---|---|---|
| flat, Save 4, evening | 14.5 colour levels | 1.0 `[measured, n=1]` |
| flat, Save 4, noon | 14.7 | 1.0 `[measured, n=1]` |
| VR simulator, Save 4 | about 11 | about 1 (a smooth change instead) `[measured, n=1]` |

The step is measured at 52 points along the border found by the stripe probe (median of near minus far, 5 rows each
side). Pictures: `2026-11-20-pictures/water line - A/B/C ... before-after.png`, `water line - test stripes.png`.

The price: from mid-distance the lake takes the river's greener far look instead of staying olive (Tefa to judge).
Left: a 1-pixel hairline, in some columns only, about 10 levels darker, exactly on the old border; it was there
before too, under the colour step. It looks like a hairline gap where the near and far water meet (nothing drawn
there), which a colour change cannot fill `[hypothesis]`.

Profiles: `rung-05 test Y flat water fade` (flat rung 5 + the mod) and `rung-05 test Y water fade` (VR: test V + the
mod). Desk only: `rung-05 test P flat water probe` with `Bridge desk test - water probe`.

## 3. Tools and settings changed

- `rung_flatcheck.py`: DPI-aware (at 200 % scaling the picture was the window's top-left quarter); `--console
  "line;line"` typed once the save has loaded (e.g. the game hour).
- Screenshots (Tefa's ask): every profile's `SScreenShotBaseName` (fallout.ini and falloutprefs.ini, backups
  `*.bak-2026-11-20-screenshots`) points at the Desktop folder `Atomic Fork water line`, named after the profile, so
  two profiles' counters can never overwrite each other. `[verified-live, n=1]`. The older ones (in MO2's
  overwrite\Root) were copied there into `your screenshots`.
- Camera: two runs went off-view because Tefa moved the mouse to look at the lake (he wants a picture of every run
  instead: done, Desktop folder).
- After a `--stay` simulator run, the game shows "The Xbox 360 Controller has been disconnected" once VR Bench's hands
  go, and does not close behind it; Enter (its only button, Ok) and it closes in seconds.

## 4. The black hairline (afternoon; Tefa from the Keeper PC: *"the water line is still there, like a black line going through it"*)

The 1-pixel line of section 2 is what Tefa saw in the timelapse. Cause `[measured]`: a gap where the near water's tiles
meet the far water's; nothing is drawn there, so the lake bed shows.

Found on the way (probes in the water shaders, Save 4, flat):
- near-water tiles are one cell each, measured from their own corner (local 0..4096);
- the near water is placed by WATER001.vso, the far water by WATER000.vso (each placement shader tagged the water
  with its own number);
- the placement step's depth is in game units for both, but it is depth straight ahead: about 0.57 of the true
  distance at the edge of an ultrawide view, so the border can show at a depth well under 8192.

Tries (`tools/water_seam.py`, pictures in the Desktop folder `Atomic Fork water line/hairline runs/` and the transfer
folder): every tile grown 16 units on its far sides: the line mostly gone, but light lines appear where see-through
near tiles overlap (drawn twice); grown only beyond a depth: no effect (the gate cut the border too); far tiles on one
side only: no effect (here the far tiles meet the near ones on their start side); **far tiles (WATER000.vso only) on
all four sides**: 16 units mostly, **64 units: gone**. Along the border, 30 of 52 points dipped before, 3 small ones
(4-6 levels) after `[measured, n=1]`. WATER000.vso (grown 64) is now part of `Bridge - water fades into the far look`.

The timelapse fixes-ON clip was made again without slower days (Tefa: both at the original speed): the dashed black
line of the old clip 2 is not in the new one at the start or 200 s in `[measured, n=1 each]`.
