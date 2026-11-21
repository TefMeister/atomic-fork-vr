# FNVVR Reborn v0.18.0 to v0.20.0: laser pointing in a game menu, distant water fixed again, effects that ran two or three times a frame; TTWVR's public release reported

**Status:** 🆕 new · **Priority:** medium. Follows the topic of 2026-11-14 (FNVVR Reborn up to v0.17.0). Three board
rows touch it: `[ID FO-017]` (menus with the VR controllers: point and press), `[ID FO-002]` (the water) and
`[ID FO-004]` (the picture "shifting around ever so slightly").

## What is public

Read online on 2026-11-21 from the repository's release viewer (four new release notes). Nothing was downloaded,
nothing copied. All `[reported 2026-11-21]`.

**FNVVR Reborn** by **df4l** (a New Vegas VR mod inside a DXVK `d3d9.dll`, OpenVR, not built on TTW; we do not use it,
it is a reference for what New Vegas does in stereo):

- **v0.20.0 (2026-11-18):**
  - **Lasers in a game menu:** the companion wheel now works with the controller lasers: the laser hovers the slice it
    points at, trigger / A / X choose, the stick still works. A second fix: closing a dialogue, the inventory or a
    container with the left stick held no longer unequips the weapon or swaps hotkey items.
  - **Distant water:** it reflected the hazy sky instead of the shore, turned grey past a fixed distance and moved
    with the head; reflections now match what is above the water. And the water **animated twice as fast as on a flat
    screen and differed between the eyes**, because its timing ran once per eye; it now updates once per frame.
  - **Effects that ran two or three times a frame:** object fades, light / shadow fades, eye adaptation, the loading
    fader and the water timing each ran once per drawn eye pass; now once per frame. The foveation map is rebuilt
    far less often (43,772 rebuilds in 20 minutes down to 2, on a Steam Frame).
  - **Pip-Boy angle setting** (Normal, or 15 to 90 degrees) turning the Pip-Boy towards the eyes, aimed at
    controllers without tracking rings such as the Quest 3. Known issues: name entry uses SteamVR's keyboard; a fire
    effect missing parts in one eye; a scope reticle issue.
- **v0.19.0 / v0.19.1 (2026-11-15):** eye-tracked foveated rendering (off by default); scope lenses placed on the
  weapon model's eyepiece for unknown modded guns; a calling-convention crash fix for the Steam Frame.
- **v0.18.0 (2026-11-14):** the world drawn at the eye's own size instead of a wider picture cropped afterwards
  (about 28 % fewer pixels a world pass); a mod-owned allocator for small game memory blocks "to reduce stutter";
  the right grip grabs objects with empty hands or a melee weapon.
- Nothing in these four notes on LOD popping, the weather or Tale of Two Wastelands.

**TTWVR / Tale of Two Realities** (KUPOkinz, the VR mod our list runs on): KeenGamer reported on 2026-11-18 that it
was released on 2026-11-17 (motion controls rebuilt, over 500 weapons set up for two hands, an experimental
multiplayer mode) `[reported 2026-11-18, one outlet]`. The article names no version or download page. Our copy is
1.0.0 from the Discord pins of 2026-11-12. A Nexus Mods page that may be its home refused an automated fetch
(could not read); nothing here says whether a newer build than 1.0.0 exists.

## What it means for us

- **`[ID FO-017]`:** a game menu driven by a laser on New Vegas is shown to be doable: hit-test the laser against the
  menu's own elements and send the choice as the game's own input `[reported]`. TTWVR feeds menus a fake pad, no
  pointer (the reader's note of 2026-11-21); if laser pointing is wanted, this is the shape to write fresh in our own
  Bridge plugin, starting with one simple menu `[hypothesis]`. The "left stick held while closing a menu unequips
  the weapon" bug is worth a quick look on our side too, since TTWVR also turns stick input into pad input in menus
  `[hypothesis]`.
- **`[ID FO-002]` and `[ID FO-004]`:** a VR mod that draws New Vegas once per eye can run the game's per-pass timers
  once per eye: water moving at double speed and differing between the eyes, and fades / eye adaptation stepping
  twice a frame `[reported for FNVVR]`. Whether TTWVR has the same fault is not known `[hypothesis]`. Cheap check on
  the simulator at Save 4: compare the water's ripple speed flat against VR, and grab both eyes in one frame to see
  whether the water differs. A "yes" would also be a candidate for the slight shifting Tefa saw on rung 3.
- **The TTWVR release:** when Tefa next opens the Flat2VR Discord or the mod's page, check whether there is a build
  newer than 1.0.0 and its changelog before the next ladder rung is built `[hypothesis]`: a newer TTWVR can move the
  ground under every rung test.

## Sources

- df4l, FNVVR Reborn, releases v0.18.0 to v0.20.0 (2026-11-14 to 11-18): https://github.com/df4l/FNVVR/releases
- KeenGamer, Matthew Adams, "The Fallout: A Tale of Two Realities VR mod ... is out now" (2026-11-18): https://www.keengamer.com/articles/news/the-fallout-a-tale-of-two-realities-vr-mod-for-the-fallout-game-is-out-now/
