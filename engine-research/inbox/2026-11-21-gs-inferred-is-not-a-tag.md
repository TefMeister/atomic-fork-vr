# `[inferred]` is not one of the eight tags (GitHub sweep, Keeper full scan 2026-11-21)

The weekly sweep (check 3b) found **14 lines in this repo, and one on its board, tagged `[inferred]`**, a name that
is not in the vocabulary. A tag the vocabulary does not know counts as nothing: the claim reads as tagged but carries
no confidence at all, and no date.

Where:
- `docs/rung-00-plan.md:17`, `docs/rungs-02-to-08-plan.md:35`;
- `engine-research/2026-11-13-reader/2026-11-13-reader-camera1st-complaint-what-ttwvr-does.md`: lines 17, 55, 57, 76;
- `engine-research/2026-11-13-reader/2026-11-13-reader-skyline-spot-console-route.md`: lines 19, 23, 27, 53, 54, 64, 66;
- `claude-memory/status/it-never-gets-old-vr.md:26` (the board; the modding lane's own file).

Suggested change: each one becomes `[inferred-static YYYY-MM-DD]` when it was read from the files or the code without
running the game, or `[hypothesis]` when it is a guess still to be tested. Read each line first; do not replace them
all blindly. The reader notes of 2026-11-13 were written by the `/lm` reader, so its prompt may be where the word
comes from: worth one line there too.

Valid names: verified-live, verified-numerically, compile-verified, measured, inferred-static, reported, hypothesis,
disproved (`CONVENTIONS.md` → claim hygiene).
