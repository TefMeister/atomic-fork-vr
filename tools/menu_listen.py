#!/usr/bin/env python3
"""menu_listen.py -- how loud is what this PC is playing right now? For "is the menu music off".

    python menu_listen.py [--seconds 12] [--label "main menu"]

Listens to the default sound output (loopback, nothing is recorded to disk) and prints one line: the loudest moment
and the average, in dB below full scale, and how much of the time anything was sounding at all. Digital silence
reads as SILENT. It hears EVERYTHING the PC plays, so take a reading with the game closed first.
"""
import argparse
import math
import warnings

import numpy as np
import soundcard as sc

RATE = 48000
SOUNDING_ABOVE_DB = -70.0   # a 50 ms slice louder than this counts as "something is sounding"


def db(x):
    return -120.0 if x <= 1e-6 else 20 * math.log10(x)


def listen(seconds):
    warnings.simplefilter("ignore")
    mic = sc.get_microphone(sc.default_speaker().id, include_loopback=True)
    with mic.recorder(samplerate=RATE) as r:
        data = r.record(numframes=int(RATE * seconds))
    mono = np.abs(data).max(axis=1)
    step = RATE // 20
    slices = [float(np.sqrt(np.mean(mono[i:i + step] ** 2))) for i in range(0, len(mono) - step + 1, step)]
    sounding = sum(1 for s in slices if db(s) > SOUNDING_ABOVE_DB) / max(1, len(slices))
    return db(float(mono.max())), db(float(np.sqrt(np.mean(mono ** 2)))), sounding


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--seconds", type=float, default=12.0)
    ap.add_argument("--label", default="now")
    a = ap.parse_args()
    peak, avg, sounding = listen(a.seconds)
    word = "SILENT" if sounding == 0 else ("SOUND all the time" if sounding > 0.9 else "SOUND part of the time")
    print(f"{a.label}: {word}; loudest {peak:.0f} dB, average {avg:.0f} dB, sounding {sounding * 100:.0f} % of {a.seconds:.0f} s")


if __name__ == "__main__":
    main()
