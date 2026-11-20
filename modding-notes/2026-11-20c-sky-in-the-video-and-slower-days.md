# 2026-11-20 afternoon: the sky rings live against in the video; slower days

Lane: plain session on the Developer PC, Tefa at the desk. Follows `2026-11-20b-the-water-line-cured.md`.

## The sky rings (FO-012)

Tefa, after the two 24 h timelapses: *"the sky rings really did make a massive difference with the fix on, but are
still noticable ... is there a way to smooth this transition out even more"*.

- Tried: grain where the SKY DOME is drawn too (`tools/sky_dome_dither.py`, new; `--lff` changes LOD Flicker Fix's
  SKY.vso / SKY.pso pair, which is the old shader kind with no screen position, so the vertex step hands it over;
  `--vanilla` for the game's own ps_3_0 SKY.pso). Flat, Save 4, 05:36, looking 35 degrees up, full size: today's fix
  alone leaves a row-to-row ring residual of 0.015 levels, with the dome grain 0.013 `[measured, n=1 each]`: no
  visible rings in either, no real gain. Not kept (the tool is).
- **The rings Tefa saw are in the VIDEO**: the recorder writes 1280 x 720 with ordinary compression, which averages
  the grain away and paints its own bands. A frame from each video at the same moment, contrast stretched: fixes OFF =
  long clean rings, fixes ON = blocky compression bands `[measured, n=1]`. The game itself is to be judged live, not
  from the recording; for YouTube, full size and a higher bitrate keep the grain.

## Slower days (FO-019): `Bridge - slower days` (source in `bridge-mods/`)

Tefa: clock 30 % slower overall, and the dawn / dusk stretch 50 % slower again ("if these can be separately tuned").
Dawn and dusk 4x longer was dropped: the Capital Wasteland's own sunrise and sunset already last 4 game hours each
(TNAM 5:00-9:00 and 16:00-20:00; the Mojave's 6:00-8:00 and 18:00-20:00).

- No plugin, no record changed: a JIP script-runner file `NVSE/Plugins/Scripts/ln_AtomicForkSlowerDays.txt`
  registers `NVSE/user_defined_functions/AtomicFork/SlowerDays.gek` on the main loop (every 30 frames). It sets the
  TimeScale global to fDayScale (21) or, while the current climate's sunrise or sunset is on, fTwilightScale (10.5).
  Settings: `config/AtomicFork/SlowerDays.ini`. Clashes with nothing in this list (no other mod sets TimeScale);
  weather mods are untouched because the climates are only read.
- `[verified-live 2026-11-20, flat, n=1]`: at 05:00.03 the clock went 21 -> 10.5; the climate read dawn 5, dusk end 20.
- Learned on the way: script variables must not share a name with any form (`rC` exists: "Form with that Editor ID
  already exists", the whole file then never runs); a function passed inline in brackets is capped at 512 characters
  (use a file in user_defined_functions); JIP's GetClimateTraitNumeric gives the times in MINUTES (5:00 = 300).
  Compile errors go to `nvse.log` ("Error on line N").
- It overrides a console `set timescale`: keep it OFF for timelapse recordings (the timelapse profiles do not carry it).

## Other

- `set timescale to 1` crashes this list a few seconds later (Stewie's Tweaks' low-actor update, the same call trace
  twice) `[verified-live, n=2]`; 240 and 30 are fine.
- `console_type.py`: the game crashed between two lines and the remaining keys went into Tefa's Claude window. Every
  key now checks the game is still in front (Shift let go first); it stopped cleanly on the next crash.
- Idle third-person camera off in every profile (`bDisableAutoVanityMode=1`, [General]).

## For the standalone package (Tefa: Discord and SpringHeelJon, if he wants them)

Three mods, same files flat and VR: water fade (needs Shader Loader; tuned to TTW's Capital Wasteland waters), smooth
sky (an altered copy of Vanilla Plus Tonemapper's three shaders: needs that mod, and **sharing it needs its author's
permission, or a small patcher that makes the change on the user's own copy**), slower days (xNVSE + JIP).
