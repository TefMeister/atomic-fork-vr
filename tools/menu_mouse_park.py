#!/usr/bin/env python3
"""menu_mouse_park.py -- push the flat game's own mouse arrow into the bottom-right corner, out of a menu picture.

    python menu_mouse_park.py

The game draws its own arrow in the middle of the main menu and reads the mouse as relative moves, so the arrow is
pushed with relative moves (SendInput) while the game's window is in front. Presses nothing. Then: menu_shot.py.
"""
import ctypes
import sys
import time

import menu_keys as m

STEPS, STEP_PX, GAP_S = 40, 120, 0.02
MOUSEEVENTF_MOVE = 0x0001


def main():
    hwnd = m.game_window()
    if not hwnd:
        sys.exit("the game's window is not there")
    m.to_front(hwnd)
    time.sleep(0.5)
    if m.exe_of(m.u.GetForegroundWindow()) != m.GAME_EXE:
        sys.exit("the game is not in front: nothing moved")
    for _ in range(STEPS):
        i = m.INPUT(0, m.U(mi=m.MI(STEP_PX, STEP_PX, 0, MOUSEEVENTF_MOVE, 0, None)))
        m.u.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))
        time.sleep(GAP_S)
    print("arrow parked in the bottom-right corner")


if __name__ == "__main__":
    main()
