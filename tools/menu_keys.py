#!/usr/bin/env python3
"""menu_keys.py -- press keys in the flat game's main menu (the game's own window is brought to the front first).

    python menu_keys.py down down enter          keys in order: up down left right enter esc
    python menu_keys.py quit                     six Downs (to Quit), then the caller LOOKS, then: menu_keys.py enter

Keys go out as held scancodes (HOLD_S each): this game ignores a quick tap of Enter. Refuses when the window in
front afterwards is not FalloutNV.exe's. Never press Enter without having looked at the highlight: New sits two
rows under Continue.
"""
import ctypes
import os
import sys
import time
from ctypes import wintypes as w

HOLD_S = 0.12
GAP_S = 0.35
GAME_EXE = "falloutnv.exe"
KEYS = {"down": (0x50, True), "up": (0x48, True), "left": (0x4B, True), "right": (0x4D, True), "enter": (0x1C, False), "esc": (0x01, False)}
u, k = ctypes.windll.user32, ctypes.windll.kernel32


class KI(ctypes.Structure):
    _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD), ("time", w.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class MI(ctypes.Structure):
    _fields_ = [("dx", w.LONG), ("dy", w.LONG), ("mouseData", w.DWORD), ("dwFlags", w.DWORD), ("time", w.DWORD), ("dwExtraInfo", ctypes.c_void_p)]


class U(ctypes.Union):
    _fields_ = [("ki", KI), ("mi", MI)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", w.DWORD), ("u", U)]


def exe_of(hwnd):
    pid = w.DWORD(0)
    u.GetWindowThreadProcessId(w.HWND(hwnd), ctypes.byref(pid))
    h = k.OpenProcess(0x1000, False, pid.value)
    if not h:
        return ""
    buf, n = ctypes.create_unicode_buffer(520), w.DWORD(520)
    ok = k.QueryFullProcessImageNameW(w.HANDLE(h), 0, buf, ctypes.byref(n))
    k.CloseHandle(w.HANDLE(h))
    return os.path.basename(buf.value).lower() if ok else ""


def game_window():
    found = []

    @ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    def cb(hwnd, _):
        if u.IsWindowVisible(hwnd) and exe_of(hwnd) == GAME_EXE:
            found.append(hwnd)
        return True
    u.EnumWindows(cb, 0)
    return found[0] if found else None


def send(scan, flags):
    i = INPUT(1, U(ki=KI(0, scan, flags, 0, None)))
    u.SendInput(1, ctypes.byref(i), ctypes.sizeof(i))


def press(name):
    scan, extended = KEYS[name]
    flags = 0x8 | (0x1 if extended else 0)
    send(scan, flags); time.sleep(HOLD_S); send(scan, flags | 0x2); time.sleep(GAP_S)


def to_front(hwnd):
    if u.GetForegroundWindow() != hwnd:
        send(0x38, 0x8); send(0x38, 0x8 | 0x2)          # an Alt tap, or Windows may refuse the switch
        u.SetForegroundWindow(w.HWND(hwnd)); time.sleep(0.8)
        press("left")                                   # the first key after the switch can be swallowed (seen 2026-11-19
                                                        # with Enter); Left does nothing in the main list, so it goes first
    return exe_of(u.GetForegroundWindow()) == GAME_EXE


def main():
    names = sys.argv[1:]
    if names == ["quit"]:
        names = ["down"] * 6
    if not names or any(n not in KEYS for n in names):
        sys.exit(__doc__)
    hwnd = game_window()
    if not hwnd or not to_front(hwnd):
        sys.exit("the game's window is not there, or would not come to the front: nothing pressed")
    for n in names:
        press(n)


if __name__ == "__main__":
    main()
