"""needs_check.py -- before a start: does every switched-on NVSE add-on have the add-ons it says it needs?

    python needs_check.py --mo2 <Begin Again folder> --name <profile>     exit 1 when something is missing

Many of Begin Again's drawing add-ons refuse to load without another one and say so in a box at the start that stops
the game ("LOD Flicker Fix not found. Depth Resolve cannot be used without it, please install it."). Each such add-on
carries those sentences inside its DLL, so they are read from the DLL: every "<Name> not found." whose next sentence
is "... cannot be used without it". <Name> is matched to a mod of the list by its words (ignoring "Fallout", "NVSE",
"-"). Built 2026-11-14 after test A (LOD Flicker Fix off) stopped at exactly that box on Tefa's start.
"""
import argparse, glob, os, re, sys

NOISE = {"fallout", "nvse", "-", "the"}


def words(s):
    return {w for w in re.split(r"[^a-z0-9]+", s.lower()) if w and w not in NOISE}


def needs_of(dll):
    """the add-on names the DLL says it cannot run without"""
    data = open(dll, "rb").read()
    text = [t.decode("latin-1") for t in re.findall(rb"[\x20-\x7e]{6,}", data)]
    out = []
    for i, t in enumerate(text):
        m = re.fullmatch(r"([^%]+) not found\.", t)   # no "%s.ini not found." format strings (NVTF)
        if m and i + 1 < len(text) and "cannot be used without it" in text[i + 1]:
            out.append(m.group(1))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True)
    ap.add_argument("--name", required=True)
    a = ap.parse_args()
    with open(os.path.join(a.mo2, "profiles", a.name, "modlist.txt"), encoding="utf-8") as f:
        on = [ln[1:].strip() for ln in f if ln.startswith("+")]
    on_words = {m: words(m) for m in on}
    missing = []
    for mod in on:
        for dll in glob.glob(os.path.join(a.mo2, "mods", glob.escape(mod), "[nN][vV][sS][eE]", "[pP]lugins", "*.dll")):
            for need in needs_of(dll):
                w = words(need)
                if not any(w <= mw for mw in on_words.values()):
                    missing.append((mod, need))
    for mod, need in sorted(set(missing)):
        print("MISSING: %s needs %s, which is off in this profile (the game would stop at a box)" % (mod, need))
    print("needs check '%s': %s" % (a.name, "%d missing" % len(set(missing)) if missing else "every add-on has what it needs"))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
