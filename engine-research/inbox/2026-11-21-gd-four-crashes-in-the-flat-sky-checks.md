# Four crashes in a row in the 2026-11-20 flat sky checks (Gold Digger, Keeper full scan 2026-11-21)

Gold Digger's shelves hold four crash dumps from 2026-11-20 between 12:21 and 12:25, one for each launch of the
rung-05 flat sky checks with test V and test S:
`crashes/2026-11-20_12-21-34_PC1_FalloutNV.exe.9624.dmp`, `12-22-51 ... .12132.dmp`, `12-24-44 ... .12156.dmp` and
`12-25-51 ... .11948.dmp`. Windows recorded each one as an APPCRASH of FalloutNV.exe 1.4.0.525, `0xC0000005`, and
Gold Digger reads the crash spot as `FalloutNV.exe+0x477C6D` [measured 2026-11-20, from the crash shelf]. The runs
are in `runs/2026-11-20 1221 ...` to `1226 ... test S flat sky check`.

The crash logger did not catch the cause: its call trace stops at ntdll with "Exception occurred while logging"
(`overwrite__Root__Crash Logs__CrashLogger.2026-11-20-12-21-25.log`). One more crash log of the same morning,
10:55:15, is empty apart from its heading.

The notes of 2026-11-20 do not name these four crashes. `2026-11-20c-sky-in-the-video-and-slower-days.md` does
record that `set timescale to 1` crashes this list a few seconds later, through Stewie's Tweaks' low-actor update.
`[hypothesis]` If the sky checks change the time scale, these are that same crash. If they do not, it is a second
crash.

Proposed board row: check whether the sky-check route sets the time scale. If it does not, compare the four dumps'
crash spot with the timescale crash's.
