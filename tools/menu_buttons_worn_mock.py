"""A worn terminal-style menu button, drawn from scratch (our own art in that style, not copied)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D, OUT = sys.argv[1], sys.argv[2]
W, H = 132, 26                      # drawn small, like the old game's pixel art, then enlarged with hard pixels
rng = np.random.default_rng(5)

def noise(w, h, blur):
    a = Image.fromarray((rng.random((h, w)) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(a, np.float32) / 255

def button(word, picked, font, label=(62, 88, 112), text=(196, 206, 214)):
    im = np.zeros((H, W, 3), np.float32)
    # the metal plate: grey-brown, grainy, darker grime in blotches
    base = np.array([92, 86, 76], np.float32)
    im[:] = base * (0.80 + 0.35 * noise(W, H, 0.6)[..., None]) * (0.85 + 0.25 * noise(W, H, 3)[..., None])
    im[0, :] *= 1.35; im[:, 0] *= 1.3; im[-1, :] *= 0.55; im[:, -1] *= 0.6          # bevel: lit top-left
    out = Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(out)
    # the socket and the round red button
    cx, cy = 11, H // 2
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(34, 30, 26)); d.arc((cx - 7, cy - 7, cx + 7, cy + 7), 20, 200, fill=(140, 132, 118))
    if picked:
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill=(110, 16, 10)); d.arc((cx - 4, cy - 4, cx + 4, cy + 4), 180, 360, fill=(40, 6, 4))
    else:
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(214, 44, 30)); d.point([(cx - 2, cy - 3), (cx - 1, cy - 3), (cx - 2, cy - 2)], fill=(255, 170, 150))
    # the label: a slate-blue panel with a thin light rim, set into the plate
    x0, y0, x1, y1 = 22, 4, W - 5, H - 5
    d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), fill=(30, 28, 24))
    lab = np.zeros((y1 - y0 + 1, x1 - x0 + 1, 3), np.float32); lab[:] = label
    lab *= (0.88 + 0.22 * noise(lab.shape[1], lab.shape[0], 0.8))[..., None]
    out.paste(Image.fromarray(np.clip(lab, 0, 255).astype(np.uint8)), (x0, y0))
    d.rectangle((x0, y0, x1, y1), outline=(150, 170, 186))
    d.text(((x0 + x1) // 2 + (1 if picked else 0), (y0 + y1) // 2 + 1 + (1 if picked else 0)), word, font=font, fill=text, anchor="mm")
    # wear: scratches across the plate and label, chipped specks, rub-off at the rim
    a = np.asarray(out, np.float32)
    for _ in range(4):
        x, y, ln = rng.integers(0, W), rng.integers(0, H), rng.integers(6, 30)
        for t in range(ln):
            xx, yy = x + t, int(y + t * rng.uniform(-0.2, 0.2))
            if 0 <= xx < W and 0 <= yy < H: a[yy, xx] = a[yy, xx] * 0.6 + 70
    spk = noise(W, H, 0.4) > 0.93
    a[spk] *= 0.55
    rub = (noise(W, H, 1.0) > 0.86)
    a[y0, x0:x1][rub[y0, x0:x1]] = label; a[y1, x0:x1][rub[y1, x0:x1]] = label
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

rows = []
for fname, size, name in (("Silkscreen-Regular.ttf", 8, "A"), ("VT323-Regular.ttf", 16, "B"), ("PixelifySans[wght].ttf", 11, "C")):
    f = ImageFont.truetype(f"{D}/{fname}", size)
    col = [button(w, w == "NEW", f) for w in ("CONTINUE", "NEW", "LOAD", "SETTINGS", "QUIT")]
    rows.append((name, col))
    rows.append((name + " yellow on black", [button(w, w == "NEW", f, label=(18, 18, 16), text=(255, 221, 103)) for w in ("CONTINUE", "NEW", "LOAD", "SETTINGS", "QUIT")]))
S2 = 3
sheet = Image.new("RGB", (len(rows) * (W * S2 + 30) + 30, 5 * (H * S2 + 10) + 70), (40, 36, 30)); dd = ImageDraw.Draw(sheet)
for k, (name, col) in enumerate(rows):
    x = 30 + k * (W * S2 + 30); dd.text((x, 20), name, fill=(230, 230, 230), font=ImageFont.truetype(f"{D}/Oswald[wght].ttf", 22))
    for i, b in enumerate(col):
        sheet.paste(b.resize((W * S2, H * S2), Image.NEAREST), (x, 60 + i * (H * S2 + 10)))
sheet.save(OUT)
