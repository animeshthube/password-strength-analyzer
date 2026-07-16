from PIL import Image, ImageDraw, ImageFont
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from password_analyzer import analyze_password

examples = [
    "12345678",
    "Password1",
    "qwerty123",
    "aaaaaaaa1A!",
    "ChangeMe!",
    "Tr0ub4dor&3",
    "MyP@ssphrase99",
    "P@ssw0rd2026!",
]

rows = []
for pw in examples:
    r = analyze_password(pw)
    rows.append((pw, r["score"], r["max_score"], r["strength"]))

W, H = 1100, 90 + 44 * (len(rows) + 1)
BG = (13, 17, 23)
PANEL = (17, 22, 29)
BORDER = (35, 43, 53)
TEXT = (220, 228, 236)
MUTED = (120, 130, 140)
GREEN = (63, 185, 80)
YELLOW = (219, 171, 9)
RED = (248, 81, 73)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

mono_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
mono_bold_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
title_font = ImageFont.truetype(mono_bold_path, 24)
header_font = ImageFont.truetype(mono_bold_path, 16)
row_font = ImageFont.truetype(mono_path, 16)

# window chrome dots
for i, c in enumerate([RED, YELLOW, GREEN]):
    draw.ellipse([24 + i*22, 22, 24 + i*22 + 12, 34], fill=c)

draw.text((30, 46), "$ python password_analyzer.py --demo", font=title_font, fill=(150,160,170))

top = 90
col_x = [30, 430, 560, 700]
headers = ["PASSWORD", "SCORE", "", "STRENGTH"]
for x, h in zip(col_x, headers):
    draw.text((x, top), h, font=header_font, fill=MUTED)

draw.line([(20, top+30), (W-20, top+30)], fill=BORDER, width=1)

color_map = {"Weak": RED, "Moderate": YELLOW, "Strong": GREEN}
y = top + 44
for pw, score, maxs, strength in rows:
    draw.text((col_x[0], y), pw, font=row_font, fill=TEXT)
    draw.text((col_x[1], y), f"{score}/{maxs}", font=row_font, fill=TEXT)
    # mini bar
    bar_x = col_x[2]
    bar_w = 110
    bar_h = 12
    draw.rounded_rectangle([bar_x, y+3, bar_x+bar_w, y+3+bar_h], radius=4, fill=(30,38,48))
    fill_w = int(bar_w * score / maxs)
    if fill_w > 0:
        draw.rounded_rectangle([bar_x, y+3, bar_x+fill_w, y+3+bar_h], radius=4, fill=color_map[strength])
    draw.text((col_x[3], y), strength, font=header_font, fill=color_map[strength])
    y += 44

img.save("/home/claude/password-strength-analyzer/screenshots/demo_output.png")
print("Saved demo_output.png")
