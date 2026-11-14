# 2026-11-14: DLSS off at 150% changes nothing: the far skyline still swims and the picture is still soft

Developer PC, /ms, Opus, Tefa in the headset (Quest 3 through Virtual Desktop, 72 Hz). Tefa's question: do the
smudging and the swimming far skyline go away with DLSS off and about 1.5x supersampling?

## The test

- Our test mod `Bridge - picture test DLSS off 150` (`bridge-mods/`): its own `TTWVR.ini` at TTWVR's path with
  `Resolution=150%`, `Upscaler=Off`, every other line as TTWVR's (165%, DLSS, Quality, Sharpness 65%). On in
  `rung-05 interface` only, on the top line of `modlist.txt` (= highest priority, above `TTWVR 1.0.0`); backup
  `modlist.txt.bak-2026-11-14-picture-test`. TTWVR's own file untouched.
- Run 17:05-17:08, Save 4, rung 5. Logs kept: `runs/2026-11-14 1705 rung-05 interface headset picture test DLSS off 150/`
  (with Virtual Desktop's `OpenXR.log`). An 11.6 s main-loop stop during the load (TTWVR's hang watcher, dump written,
  then turning again); no crash.
- Switched off again afterwards (Tefa did not ask to keep it); `ladder.py check` clean.

## What Tefa saw

*"still the same in fallout, game is low resolution"* `[reported, n=1]`: the far skyline still swims with the head
sway, the near grass and shrubs the same, the picture still low resolution.

## The sizes `[measured 2026-11-14]`

- Virtual Desktop's own log, this run: `Application: NVVR (FalloutNV.exe)`, `Recommended resolution: 2688x2880 (1.000
  supersampling, 1.000 upscaling)`. TTWVR's log: `Meta Quest 3 (swapchains up to 16384x16384)`.
- **The 4096-per-eye cap is the OpenXR Simulator's** (`swapchains up to 4096x4096` in its runs), not the headset's: on
  the Quest nothing is capped at 165% or at 150%.
- TTWVR's percentage is per side (simulator: 2944 wide at 100%, 4864 at 165%) `[measured 2026-11-12]`. So on the Quest:
  now (165% + DLSS Quality) about 4435x4752 out, drawn at about 2957x3168; the test (150%, no upscaler) drawn at
  4032x4320, about 1.9 times the pixels `[inferred-static]`.
- TTWVR's log never prints the eye size it chose, nor which settings file won; the test file's win is
  `[inferred-static]` (MO2 priority). Tefa was asked whether the VR menu showed 150% / Off.
- The 2026-11-11 note "Upscaler=Off froze the picture" was a simulator-only finding: in the headset the picture with the
  upscaler off was live `[verified-live 2026-11-14, n=1]`.

## What it means

- **The swimming far skyline is not DLSS** `[verified-live 2026-11-14, n=1]`. It stays with the board's suspect, TTWVR's
  far (LOD) pass in stereo (`MODEL: FABLE`).
- **The softness is not the size the game draws at**: about twice the pixels without any upscaler looked the same
  `[reported, n=1]`. Downstream suspects `[hypothesis]`: Virtual Desktop's stream (codec H.264+ on this PC; bitrate and
  quality are set on the headset), or the way TTWVR hands the eye picture over. The cheap decider: does another VR game
  look sharp through Virtual Desktop on the same settings? (asked of Tefa).
- Frame rate at 150% without DLSS: not yet reported.

## Then: the same rung with the test mod off (17:52, Tefa)

Rung 5 again with TTWVR's own settings (165%, DLSS Quality, Sharpness 65%), logs in
`runs/2026-11-14 1752 rung-05 interface headset short run/`. Tefa: *"picture was clear now, but the far away thing and
bushes still smudge"* `[reported, n=1]`. The two runs differ only by the test mod, so DLSS Quality at 165% looks
clearer than no upscaler at 150% (DLSS also anti-aliases and sharpens) `[hypothesis]`; it stays. The soft look Tefa
remembered from rung 3 (2026-11-13) was most likely DLSS Performance, set then `[hypothesis]`. The smudging of far
things and bushes is there with and without DLSS, so it is not the upscaler `[reported, n=2 runs]`.

## Next: two test copies of rung 5 for the swim and the smudge (built 2026-11-14 evening, Opus, no game)

First two leads, both already handled by TTWVR, so dropped: depth of field and transparency multisampling. TTWVR's DLL
forces `bDoDepthOfField` off, `bTransparencyMultisampling` off and `iMultiSample` 0 (its strings: "Depth of Field: off",
"Antialiasing: Off", "iMultiSample is forced 0 ... MSAA must be off with DLSS") and hooks the game's depth-of-field
setter `[inferred-static]`; the profile INIs' `bDoDepthOfField=1` does not reach the VR picture.

What rungs 2 and 3 add that hooks the drawing (NVSE plugins; rung 1 has none): LOD Flicker Fix (patches the far (LOD)
shaders' depth), LOD Fixes and Improvements, Depth Resolve (logs an INTZ depth texture of 2944x2208 even on the Quest,
whose eye is 2688x2880), Depth of Field Fix, Fallout Alpha Rendering Tweaks, Fog-based Object Culling, Shader Loader
(rung 2), Real Time Reflections (rung 3) `[measured]` (profile diff). None was written for two eyes `[hypothesis]`.

Two new MO2 profiles, copies of `rung-05 interface` (left untouched), shared saves (Save 4 works):
- `rung-05 test A LOD flicker fix off`: only LOD Flicker Fix off. For the swimming far skyline.
- `rung-05 test B drawing plugins off`: Fog-based Object Culling, Alpha Rendering Tweaks, Depth Resolve, Depth of Field
  Fix, Real Time Reflections off. For the smudging bushes and far things, and the blinking.
Kept ON in both: LOD Fixes and Improvements (Begin Again's big far meshes may need its vertex limit fix) and Shader
Loader. `ladder.py check` clean on both. Not in `ladder_groups.py`: a rebuild leaves them alone.

## The blinking, read from Tefa's clip (rung 5, 2026-11-13 21:24, `VirtualDesktop.Android-20261113-212457-0.mp4`)

Read with Flickers BeG0nE's reader through the new `tools/clip_flickers.py` (every one of the 605 frames, head motion
lined up; the clip is one view at 60 fps). One repeated frame in 10 s (not Virtual Desktop filling in) `[measured]`.
- **The clearest blink, frame 371 (6.2 s): two small rocks just below the big rock's edge are missing for that one frame**,
  there before and after `[measured, n=1 clip]`. Whole objects gone for a frame is culling (the engine deciding an
  object is hidden), not shimmer.
- Frames 282 and 531: the ground and grass texture in the lower right flickers over a wide patch (smaller, many
  pixels): the shimmer kind, likely fine ground detail under head motion `[hypothesis]`.

Candidates for the culled rocks `[hypothesis]`: TTWVR's own occlusion culling (`bOcclusionCull`, from a coarse grid of
the eye's depth, decided on a worker thread for both eyes: an object right next to an occluder's edge can be judged
hidden from a depth one frame old while the head moves); Begin Again's `Fog-based Object Culling` (rung 2, in test B).
The game's own `bEnableBoundingVolumeOcclusion=1` is the same in every rung, the debug one included, so it alone does
not explain "sharp at first". Test B says whether Begin Again's culling plays a part; TTWVR's own switch is not in
TTWVR.ini (a DLL table, as with `bFogCull`).

## The water: underwater parts drawn shifted (Tefa's screenshot of 2026-11-13 21:23)

Tefa: *"things underwater are shifted wrong, like the tyre and the rocks that should just be the tips above
waterline"*. In the picture each submerged object has a darker copy of its outline shifted up and to the left of the
part above the water (the tyre by about 40 px, the stones less), on the olive sheet, with the flat bright green beside it
`[measured, one still]`. A copy shifted by an amount that changes across the picture fits the water reading a depth or
refraction picture made at a DIFFERENT SIZE from the eye it is drawn into `[hypothesis]`. Two Begin Again rung-2 plugins
make such pictures: Depth Resolve (logs a 2944x2208 depth texture on the Quest, whose eye is not that size) and High
Resolution Water Fog (`HighResWaterDepth.dll`, the water's own depth). The 2026-11-13 flat-vs-VR comparison showed the
fault is VR-only, which does not clear these two: a plugin written for one flat screen can go wrong only in VR.
High Resolution Water Fog is now OFF in `rung-05 test B drawing plugins off` too (with Depth Resolve); `ladder.py check`
clean. Test B therefore also asks: is the water right there?

## Test A stopped at a box; the tests rebuilt by what needs what (2026-11-14 19:48)

Tefa's start of test A stopped at "LOD Flicker Fix not found. Depth Resolve cannot be used without it", and came back
after OK: the game did not start (closed by Tefa). My miss: the add-ons' needs were not checked. Read from the DLLs
(`tools/needs_check.py`, new; run it before any start of a changed profile) `[measured]`:
- LOD Flicker Fix is needed by Depth Resolve, Vanilla Plus AO, Vanilla Plus Particles, Vanilla Plus Skin, Vanilla Plus
  Terrain; Depth Resolve by Vanilla Plus AO and Particles; all of them need Shader Loader.
- **Vanilla Plus AO arrives at rung 3** (off in rung 2), when Tefa's picture went soft: screen-space ambient occlusion
  worked out from Depth Resolve's depth, which on the Quest is 2944x2208, not the eye's size. Shadows computed at the
  wrong size would smudge bushes and draw dark outlines beside objects (the tyre) `[hypothesis]`: the top suspect now.

The three tests, all copies of rung 5, `needs_check.py` and `ladder.py check` clean on each:
- `rung-05 test A LOD flicker fix off`: LOD Flicker Fix, Depth Resolve and the four Vanilla Plus add-ons off (skyline).
- `rung-05 test B drawing plugins off`: Fog-based Object Culling, Alpha Rendering Tweaks, Depth of Field Fix, Real Time
  Reflections, High Resolution Water Fog off; Depth Resolve back on (blinking, water).
- `rung-05 test C ambient occlusion off` (new): only Vanilla Plus AO off (smudge, dark outlines). Wear first.

## Test A worn (2026-11-14 20:07-20:14, Tefa, Quest 3): "looks beautiful, no smudge, no blinking"

Tefa: *"ran just A, looks beautiful, no smudge, no blinking, things still wrong in the puddle"* `[verified-live
2026-11-14, n=1]`. Logs: `runs/2026-11-14 1955 test A headset/`; clean exit, no Windows errors.
- **The smudge and the blinking come from the LOD Flicker Fix group**: LOD Flicker Fix, Depth Resolve, Vanilla Plus AO,
  Particles, Skin, Terrain (Begin Again's drawing add-ons, written for one flat screen). Which one(s): test C (AO alone
  off) next; then the others one at a time if C does not do it.
- **The puddle is NOT that group**: the underwater parts are still drawn shifted. Test B (High Resolution Water Fog,
  Fog-based Object Culling and three more off) is the next for it; TTWVR's own water drawing stays the other suspect.
- **The far skyline did not swim either** (Tefa, asked "did the far skyline still swim": *"no"*) `[verified-live 2026-11-14, n=1]`: the swim is the same group, most likely LOD Flicker Fix itself (it changes how the far view is drawn).
