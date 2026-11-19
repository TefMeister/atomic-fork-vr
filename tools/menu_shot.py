#!/usr/bin/env python3
"""menu_shot.py -- a picture of the game's own window at full size, even when another window covers it.

    python menu_shot.py OUT.png [--crop x,y,w,h]

Asks Windows for the window's contents (PrintWindow, full content); takes no focus and presses nothing. A game that
has stopped drawing gives its last frame, so use it for menus, not to prove the game is alive.
"""
import ctypes
import sys
from ctypes import wintypes as w

from PIL import Image

import menu_keys

ctypes.windll.shcore.SetProcessDpiAwareness(2)
u, g = ctypes.windll.user32, ctypes.windll.gdi32
for f, res, args in ((u.GetDC, w.HDC, [w.HWND]), (g.CreateCompatibleDC, w.HDC, [w.HDC]), (g.CreateCompatibleBitmap, w.HBITMAP, [w.HDC, ctypes.c_int, ctypes.c_int]),
                     (g.SelectObject, w.HGDIOBJ, [w.HDC, w.HGDIOBJ]), (u.PrintWindow, w.BOOL, [w.HWND, w.HDC, w.UINT]),
                     (g.GetDIBits, ctypes.c_int, [w.HDC, w.HBITMAP, w.UINT, w.UINT, ctypes.c_void_p, ctypes.c_void_p, w.UINT]),
                     (g.DeleteObject, w.BOOL, [w.HGDIOBJ]), (g.DeleteDC, w.BOOL, [w.HDC]), (u.ReleaseDC, ctypes.c_int, [w.HWND, w.HDC])):
    f.restype, f.argtypes = res, args


class BMI(ctypes.Structure):
    _fields_ = [("biSize", w.DWORD), ("biWidth", w.LONG), ("biHeight", w.LONG), ("biPlanes", w.WORD), ("biBitCount", w.WORD),
                ("biCompression", w.DWORD), ("biSizeImage", w.DWORD), ("a", w.LONG), ("b", w.LONG), ("c", w.DWORD), ("d", w.DWORD)]


def shot(hwnd):
    r = w.RECT()
    u.GetClientRect(w.HWND(hwnd), ctypes.byref(r))
    W, H = r.right, r.bottom
    dc = u.GetDC(hwnd); mdc = g.CreateCompatibleDC(dc); bmp = g.CreateCompatibleBitmap(dc, W, H)
    g.SelectObject(mdc, bmp)
    u.PrintWindow(hwnd, mdc, 3)          # client area only, full content
    bi = BMI(ctypes.sizeof(BMI), W, -H, 1, 32, 0, 0, 0, 0, 0, 0)
    buf = ctypes.create_string_buffer(W * H * 4)
    g.GetDIBits(mdc, bmp, 0, H, buf, ctypes.byref(bi), 0)
    g.DeleteObject(bmp); g.DeleteDC(mdc); u.ReleaseDC(hwnd, dc)
    return Image.frombuffer("RGBA", (W, H), buf, "raw", "BGRA", 0, 1).convert("RGB")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    hwnd = menu_keys.game_window()
    if not hwnd:
        sys.exit("the game's window is not there")
    im = shot(hwnd)
    if "--crop" in sys.argv:
        x, y, cw, ch = (int(v) for v in sys.argv[sys.argv.index("--crop") + 1].split(","))
        im = im.crop((x, y, x + cw, y + ch))
    im.save(sys.argv[1])
    print(im.size)


if __name__ == "__main__":
    main()
