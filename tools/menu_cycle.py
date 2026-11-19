#!/usr/bin/env python3
"""menu_cycle.py -- one try of the main-menu layout: (the caller has LOOKED and Quit is lit) press Enter, wait for
everything to close, rebuild the layout mod, start the rung, light the first word, save pictures.

    python menu_cycle.py --mo2 <list folder> --rung "rung-05 interface flat" --shots <folder> --name v6

Saves <name>.png (the whole game window) and <name>-menu.png (the menu words at full size). If Enter did not close
the game it asks politely (never by force).
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = "Bridge - Atomic Fork main menu layout"


def running(name):
    return name.lower() in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def tool(name, *args):
    return subprocess.run([sys.executable, os.path.join(HERE, name), *args]).returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--mo2", required=True); ap.add_argument("--rung", required=True)
    ap.add_argument("--shots", required=True); ap.add_argument("--name", required=True)
    a = ap.parse_args()
    if running("FalloutNV.exe"):
        tool("menu_keys.py", "enter")
        t = time.time()
        while time.time() - t < 30 and running("FalloutNV.exe"):
            time.sleep(2)
        if running("FalloutNV.exe"):
            print("Enter did not quit it: polite close request")
            subprocess.run(["taskkill", "/IM", "FalloutNV.exe"], capture_output=True)
    t = time.time()
    while time.time() - t < 150 and (running("FalloutNV.exe") or running("ModOrganizer.exe")):
        time.sleep(2)
    if running("FalloutNV.exe") or running("ModOrganizer.exe"):
        sys.exit("the game or Mod Organizer did not close")
    out = os.path.join(a.mo2, "mods", MOD)
    if tool("menu_layout.py", "--mo2", a.mo2, "--out", out):
        sys.exit("the build failed")
    full = os.path.join(a.shots, a.name + ".png")
    if tool("menu_start.py", "--mo2", a.mo2, "--rung", a.rung, "--shot", os.path.join(a.shots, a.name + "-screen.png")):
        sys.exit(1)
    tool("menu_keys.py", "down")
    tool("menu_shot.py", full)
    tool("menu_shot.py", os.path.join(a.shots, a.name + "-menu.png"), "--crop", "60,440,760,560")


if __name__ == "__main__":
    main()
