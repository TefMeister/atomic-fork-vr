# 2026-11-19: the reader's report (depth, the water list, the board, ideas, code shape)

The one read-only helper of the `/lm` session of 2026-11-19. Nothing launched, nothing written. Board line numbers
are those of the board BEFORE the re-cut of the same day. The session's own findings are in
`2026-11-19-what-test-a-does-differently-the-water-line-the-sky-rings.md`.

## 1. The static question: does TTWVR cope with LOD Flicker Fix's reversed depth?

**Answer:** no. LOD Flicker Fix must stay off in the VR rungs for now. TTWVR reads the depth picture the old way
round in every place that could be read, has no detection of a reversed depth, and LOD Flicker Fix has no setting to
limit what it does. Telling TTWVR is possible but is a rewrite in several places, not a flag.

**What LOD Flicker Fix changes** `[measured]` (its public source, one 100-line file, matches the 10 KB DLL; installed
1.2.1): the game's projection maths so near = 1 and far = 0; the depth clear value 1 to 0; every depth comparison
swapped inside the game's render-state routine; a fixed depth bias (0.00002); about 80 replacement vertex shaders
(far LOD, far trees, grass, no-light, parallax) whose fog distance is recomputed for the reversed depth
`[measured, 4 disassembled]`. It does not change the depth format or the viewport range. No INI, no setting.

**How TTWVR reads the depth**
- The upscaler helper (`ttwvr_dlss_host.exe`) carries its shaders as plain text `[measured]`. Its motion shader: sky
  is `d >= 0.9999995`, distance is `n*f / (f - d*(f-n))`: the old direction, hard-coded. Reversed, nearly the whole
  world comes out at about the near-plane distance `[inferred-static]`.
- The same shader treats anything with depth below 0.0002 as "your own hands, gun and body" (TTWVR's near pass;
  `fNearPassDepth = 0.0002`) `[measured]`. Reversed, that catches everything farther than roughly 5,000 near-plane
  lengths: a hard distance border past which the world is handled as a held object `[inferred-static]`; the exact
  distance `[hypothesis]`.
- DLSS and FSR are not handed the game's depth but one TTWVR re-makes from that wrong distance `[measured]`; the
  "depth inverted" flag is not the lever. FSR is created with flags 0x40 (no inverted bit), at 0x10491B65.
- The culling grid shader (same helper, 128 x 96 tiles, min and max depth per tile) uses 1.0 as "nothing here / far"
  and the same near-pass mask `[measured]`: both backwards on a reversed picture. The code that USES the grid was
  not read.
- The blood shaders inside TTWVR.dll use the same old-direction formula and sky test `[measured]`.
- One part adapts: the per-draw shader-constant code (the "depth row c%d is not a perspective depth of the w row"
  message, 0x104F4630) fits the depth row to the game's own numbers `[inferred-static]`.
- No text about LOD Flicker Fix, Shader Loader or reversed depth in the DLL `[measured]`.
- The switches: `TTWVR.ini` is read for 13 `[VR]` keys only (look-up 0x10091FC0, key table 0x10744C08 to
  0x10744CD8) `[measured]`. Everything else is a built-in table at 0x10743BB8 to 0x10744C08 (section / key / default
  text). Defaults: `bOcclusionCull 1`, `bFogCull 1`, `bSolidDepth 1`, `iSolidDepthAt 2`, `bFirstPersonOwnDepth 1`,
  `bFastInvert 1`, `bNearPass 1` `[measured]`.
- A small patch can flip any of them: re-point the row's default from the shared "1" text (0x10745064) to the "0"
  text (0x10745118). File offsets of the pointers: `bOcclusionCull` 0x74286C, `bFogCull` 0x742890, `bSolidDepth`
  0x7428B4, `iSolidDepthAt` 0x7428C0, `bFastInvert` 0x74277C `[inferred-static, not tried]`. Never edit the "1" text
  itself: every row shares it.

**Symptoms against mechanisms:** smudge on bushes and far things = wrong motion for most of the world when the head
moves sideways `[hypothesis]`; the skyline sliding = the hard distance border `[hypothesis]`; the one-frame blinking
of small rocks = the culling grid built from the misread depth `[hypothesis]`, not provable until the grid's user is
read; the puddle = not LOD Flicker Fix (wrong in A too), it belongs to the water.

**Caveat:** the board said the smudge stayed with the upscaler off (one remark, in a run with no anti-aliasing, where
thin grass shimmers anyway). If it really stays with the upscaler off and LOD Flicker Fix on, the second candidate
is LOD Flicker Fix's replacement grass / far LOD / tree shaders `[hypothesis]`.

**What is lost with them off in VR:** LOD Flicker Fix: far objects and decals may flicker against each other again.
Depth Resolve: a faster depth for depth of field, which TTWVR switches off anyway. Vanilla Plus AO: soft contact
shadows. Particles: smoke and dust get a hard line where they meet the ground. Skin: plainer skin. Terrain: no
ground shine at low sun, blockier fog on terrain, fewer lights on the ground.

## 2. The water list

- One preset, no tiers `[measured]`: 33 rows at 0x10907DB0 (file 0x9067B0), each = game setting address, type,
  value, label. Routine 0x10457410 writes all 33 into the game with no condition, called from the per-frame routine
  (0x1056A3AC) `[inferred-static]`. Not reachable from `TTWVR.ini`.
- Water rows forced: refractions on; reflections off; reflection width and height 256; reflection blur on;
  full-scene reflections off; silhouette reflections off; ripples off; water depth fog off (label "off - fps144 T2").
  `bUseWaterLOD` is not in the table `[measured]`.
- Smallest change in our DLL copy: a row's value from 0 to 1 (`00 00 80 3F`): `bUseWaterDepth` file 0x9068C8,
  `bUseWaterReflections` file 0x906858 `[inferred-static]`.
- The puddle (correct only in B): with reflections and depth fog forced off, Real Time Reflections and High
  Resolution Water Fog are the likely two of B's five `[hypothesis]`.

## 3. The board check (old line numbers)

- Already struck: 28, 31, 37, 38, 39, 41.
- Answered by a newer row: 22 (tests A/B/C ready) by 21, 20 and 17; 21's and 20's NEXT by 17; 23's trail by 21;
  25's NEXT by 21; 26 by 24 ("18 of 18 starts up") and 25 ("RUNG 5 WORN"); 33 item 4 by 21, items 2-3 by 27, item 1
  by 27; 29 item 2 by 23, item 3 (menu text) still unanswered; 34 stale ("NEXT = rung 4").
- Features: smudge / blinking / skyline (17, 20-23, 25, 33.4, 29.2); the water (27, 33.2-3, 25, 22); the start crash
  (24, 26, 39); the crash of 2026-11-16 (19); the ladder (34, 29, 26); the horizon (30, 29.1); rung 8's skeleton (32,
  31, 38); the v1.0 direction (18); controls on the desk (35, 33.1); desk-check tooling (28, 37, 40, 41); the dark
  bands (36); squished menu text (29.3, 26); housekeeping (42, 43).
- Gate tags that look wrong: 17 and 19 are ours first (`[PD]`), then Tefa's; 18 is a decision, not a task; 20-23, 25,
  26 are finished; 33's flat step is done; 36 waits on Tefa in the headset (`[VR USER]`).
- Above the block: line 9 "never edit ... TTWVR's files" is replaced by line 13 but still reads as a rule; line 13
  (1) is softened by row 18 ("if Kupo updates his mod a lot, we might update ours as well"); line 13 (4) "Begin
  Again stays untouched" is true for its files, but the bridge switches Begin Again mods off per VR rung.
- Only Tefa's word closes: 17 (and F's puddle), 19, 24, 29 item 3, 32, 34, 35, 36, 43.

## 4. Ideas

`ideas.py list`: no fresh ideas waiting `[measured]`. The game has no page of its own in mod-ideas; the seven standing
ideas were dropped on 2026-11-10. The one live direction is the 2026-11-16 line (gun out without RG; v1.0 around
Begin Again): NOT STARTED.

## 5. Code shape

`rung_simcheck.py` (507 lines, 51 loose numbers) already has a named settings block. Left loose: the pretend hand
and head positions, repeated waits, two key codes, the 240 s default. A small move-only tidy of the head height, the
hand poses and the 2.5 s "head settled" wait is worth doing; low priority.

## 6. Tool fault

ghidrust hung for 30 minutes on its first call against TTWVR.dll (15 MB) and timed out; the reading was done with a
plain Python + capstone script.

## What the /lm session did with it

- **Depth (1):** taken as the working cause; written on the board's top row `[ID FO-001]` with test G as the one
  wear that settles it. The table offsets were not tried. The grid's user is still unread.
- **The water list (2):** the 33-row table was re-read by the session and matches `[measured]`. Both changes were
  TRIED in our own DLL copy on the simulator: depth haze alone, then with reflections. The near water changes each
  time; the line to the far water stays. So the reader's "smallest change" is not the whole cure. Board row
  `[ID FO-002]`.
- **The board (3):** re-cut the same day: 12 rows moved out of the block word for word, every row given a feature ID
  (FO-001 to FO-014; the session's own numbering, close to the reader's grouping), six new rows on top, the heading
  re-dated. Not done: re-tagging the kept rows' gates one by one (rows 17 and 19 are covered by the new top rows),
  and the clarifying clauses above the block (left for Tefa: they are his decisions).
- **Ideas (4):** nothing to grade. The 2026-11-16 direction keeps its row `[ID FO-008]`.
- **Code shape (5):** not done today; the Inspector's verdict is `fix later: FO-010` (the desk-check tooling row).
- **The tool fault (6):** on the fault list.
- Nothing static was left for the reader when its report arrived.
