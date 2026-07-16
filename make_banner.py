from PIL import Image, ImageDraw, ImageFont
import math

W, H = 1200, 300
BG = (13, 17, 23)          # GitHub dark background
GRID = (30, 38, 48)        # subtle grid lines
ACCENT_GREEN = (63, 185, 80)
ACCENT_RED = (248, 81, 73)
TEXT_WHITE = (230, 237, 243)
TEXT_MUTED = (139, 148, 158)

img = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# --- subtle grid background (terminal / SOC dashboard feel) ---
step = 30
for x in range(0, W, step):
    draw.line([(x, 0), (x, H)], fill=GRID, width=1)
for y in range(0, H, step):
    draw.line([(0, y), (W, y)], fill=GRID, width=1)

# --- corner bracket accents (like a targeting / terminal frame) ---
bracket_len = 40
bracket_color = ACCENT_GREEN
lw = 3
margin = 20
# top-left
draw.line([(margin, margin), (margin + bracket_len, margin)], fill=bracket_color, width=lw)
draw.line([(margin, margin), (margin, margin + bracket_len)], fill=bracket_color, width=lw)
# top-right
draw.line([(W - margin, margin), (W - margin - bracket_len, margin)], fill=bracket_color, width=lw)
draw.line([(W - margin, margin), (W - margin, margin + bracket_len)], fill=bracket_color, width=lw)
# bottom-left
draw.line([(margin, H - margin), (margin + bracket_len, H - margin)], fill=bracket_color, width=lw)
draw.line([(margin, H - margin), (margin, H - margin - bracket_len)], fill=bracket_color, width=lw)
# bottom-right
draw.line([(W - margin, H - margin), (W - margin - bracket_len, H - margin)], fill=bracket_color, width=lw)
draw.line([(W - margin, H - margin), (W - margin, H - margin - bracket_len)], fill=bracket_color, width=lw)

# --- small red "alert" dots scattered (representing flagged events) ---
alert_points = [(150, 60), (1040, 240), (980, 55), (110, 235), (1090, 140)]
for (x, y) in alert_points:
    r = 4
    draw.ellipse([x-r, y-r, x+r, y+r], fill=ACCENT_RED)

# --- fonts ---
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
mono_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
mono_bold_path = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

title_font = ImageFont.truetype(bold_path, 54)
subtitle_font = ImageFont.truetype(mono_path, 22)
tag_font = ImageFont.truetype(mono_bold_path, 17)
stack_font = ImageFont.truetype(mono_path, 18)

def center_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (W - w) / 2
    draw.text((x, y), text, font=font, fill=fill)
    return w

# --- title ---
center_text(draw, "PASSWORD STRENGTH ANALYZER", 68, title_font, TEXT_WHITE)

# --- subtitle line with a terminal-style prompt ---
subtitle = "> Weak / Moderate / Strong   //   Instant Feedback"
center_text(draw, subtitle, 140, subtitle_font, ACCENT_GREEN)

# --- tech stack pills ---
stack_items = ["Python", "Regex", "CLI", "Cyber Security"]
gap = 22
paddings = 18
# measure total width first
widths = []
for item in stack_items:
    bbox = draw.textbbox((0, 0), item, font=stack_font)
    widths.append(bbox[2] - bbox[0] + paddings * 2)
total_w = sum(widths) + gap * (len(stack_items) - 1)
start_x = (W - total_w) / 2
y_pill = 205
pill_h = 34

x = start_x
colors = [ACCENT_GREEN, ACCENT_RED, ACCENT_GREEN, ACCENT_RED]
for item, w, c in zip(stack_items, widths, colors):
    draw.rounded_rectangle([x, y_pill, x + w, y_pill + pill_h], radius=17, outline=c, width=2)
    bbox = draw.textbbox((0, 0), item, font=stack_font)
    text_w = bbox[2] - bbox[0]
    draw.text((x + (w - text_w) / 2, y_pill + 6), item, font=stack_font, fill=TEXT_WHITE)
    x += w + gap

# --- footer tagline ---
center_text(draw, "Password Auditing  •  Common-Password Detection  •  Security Awareness", 262, ImageFont.truetype(mono_path, 15), TEXT_MUTED)

img.save("/home/claude/password-strength-analyzer/screenshots/banner.png")
print("Banner saved.")
