import sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D, OUT = sys.argv[1], sys.argv[2]
FONTS = [("Teko[wght].ttf", b"Bold", "1 Teko"), ("Oswald[wght].ttf", b"Bold", "2 Oswald"),
         ("SairaExtraCondensed-Bold.ttf", None, "3 Saira Extra Condensed"), ("Antonio[wght].ttf", b"Bold", "4 Antonio"),
         ("PathwayGothicOne-Regular.ttf", None, "5 Pathway Gothic"), ("ShareTech-Regular.ttf", None, "6 Share Tech")]
WORDS = ["CONTINUE", "NEW", "LOAD", "SETTINGS", "CREDITS", "QUIT"]
YELLOW, PW, PH = (255, 221, 103), 300, 46
def plate(font, word, picked, angle):
    im = Image.new("RGBA", (PW + 40, PH + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0 = 20, 20
    d.rounded_rectangle((x0, y0, x0 + PW, y0 + PH), 4, fill=(12, 12, 12, 255), outline=(70, 60, 40, 255), width=2)
    cx, cy, r = x0 + 26, y0 + PH // 2, 13                      # the round red button
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=(40, 36, 30, 255))
    if picked:   # pressed in: darker, smaller, shadow on top
        d.ellipse((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), fill=(120, 18, 12, 255))
        d.arc((cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2), 200, 340, fill=(30, 5, 3, 255), width=3)
    else:        # raised: bright, highlight
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(205, 40, 28, 255))
        d.ellipse((cx - 7, cy - 9, cx + 1, cy - 3), fill=(255, 150, 130, 255))
    d.text((x0 + 56, cy + (2 if picked else 0)), word, font=font, fill=YELLOW, anchor="lm")
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)
rng = random.Random(3)
cols = []
for f, var, name in FONTS:
    font = ImageFont.truetype(f"{D}/{f}", 34)
    if var:
        try: font.set_variation_by_name(var)
        except Exception: pass
    col = Image.new("RGBA", (380, 60 + 64 * len(WORDS)), (0, 0, 0, 0))
    ImageDraw.Draw(col).text((190, 22), name, font=ImageFont.truetype(f"{D}/Oswald[wght].ttf", 22), fill=(230, 230, 230), anchor="mm")
    for i, w in enumerate(WORDS):
        p = plate(font, w, i == 1, rng.uniform(-2.5, 2.5))
        col.alpha_composite(p, (190 - p.width // 2, 50 + 64 * i + (64 - p.height) // 2 + 10))
    cols.append(col)
sheet = Image.new("RGBA", (3 * 380 + 40, 2 * cols[0].height + 40), (58, 52, 44, 255))
for k, c in enumerate(cols):
    sheet.alpha_composite(c, (20 + (k % 3) * 380, 20 + (k // 3) * cols[0].height))
sheet.convert("RGB").save(OUT)
