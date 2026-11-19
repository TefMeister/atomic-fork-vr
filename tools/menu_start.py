#!/usr/bin/env python3
"""menu_start.py -- start one rung through Mod Organizer, wait for the main menu, save a picture of the screen.

    python menu_start.py --mo2 <Begin Again folder> --rung "rung-05 interface flat" --shot OUT.png [--wait 70]

Leaves the game at its menu (close it with menu_keys.py quit, a look, then menu_keys.py enter). Refuses when the
game or Mod Organizer is already up.
"""
import argparse
import os
import subprocess
import sys
import time

from PIL import ImageGrab

START_LIMIT_S = 150


def running(name):
    return name.lower() in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True); ap.add_argument("--rung", required=True); ap.add_argument("--shot", required=True)
    ap.add_argument("--wait", type=float, default=70.0)
    a = ap.parse_args()
    if running("FalloutNV.exe") or running("ModOrganizer.exe"):
        sys.exit("the game or Mod Organizer is already running: close it first")
    subprocess.Popen([os.path.join(a.mo2, "ModOrganizer.exe"), "-p", a.rung, "moshortcut://:Begin Again"], cwd=a.mo2,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = time.time()
    while time.time() - t < START_LIMIT_S and not running("FalloutNV.exe"):
        time.sleep(2)
    if not running("FalloutNV.exe"):
        sys.exit("THE GAME NEVER STARTED")
    time.sleep(a.wait)
    if not running("FalloutNV.exe"):
        sys.exit("THE GAME IS GONE (crashed or quit)")
    ImageGrab.grab().save(a.shot)
    print("at the menu; picture saved")


if __name__ == "__main__":
    main()
