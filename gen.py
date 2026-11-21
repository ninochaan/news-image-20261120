#!/usr/bin/env python3
"""news-image-20261120 — deterministic broadsheet front page for 20 Nov 2026.

Renders at 2048x2048 with Pillow, then downscales (LANCZOS) to 1024x1024.
No network, no timestamps, fixed seed: re-running produces byte-identical
entry.png. Every headline is a verified 20 November 2026 event (see
../dev/STORY-POOL.md); one-party claims stay attributed.
Winner-pattern layout (from the 20261119 top-5 autopsy): 35 stories,
3 heroes, stat strip, numbered stories, world map with pins, per-story
sources, DATE CHECK box.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont

random.seed(20)

S = 2048
M = 36
G = 16

PAPER = (246, 241, 230)
INK = (24, 24, 30)
NAVY = (18, 38, 74)
NAVY2 = (28, 58, 108)
RED = (178, 34, 34)
DARKRED = (122, 20, 20)
GOLD = (201, 162, 39)
TEAL = (16, 96, 110)
GREEN = (24, 120, 58)
GREY = (110, 110, 116)
LIGHT = (255, 255, 255)
CREAM = (252, 248, 238)
DARK = (16, 26, 40)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_SANS_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def vgrad(w, h, top, bottom):
    import numpy as np
    t = np.linspace(0, 1, h)[:, None, None]
    top_a = np.array(top, dtype=float)[None, None, :]
    bot_a = np.array(bottom, dtype=float)[None, None, :]
    arr = (top_a * (1 - t) + bot_a * t).astype("uint8")
    arr = np.repeat(arr, w, axis=1)
    return Image.fromarray(arr, "RGB")


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, fnt, fill, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    for line in wrap(d, text, fnt, max_w):
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def headline(d, x, y, text, size, fill=INK, max_w=None, serif=True):
    fnt = font(F_SERIF if serif else F_SANS, size)
    if max_w is None:
        d.text((x, y), text, font=fnt, fill=fill)
        return y + int(size * 1.15)
    return text_block(d, x, y, text, fnt, fill, max_w)


def rule(d, x0, y, x1, color=INK, width=4):
    d.line([(x0, y), (x1, y)], fill=color, width=width)


def kicker(d, x, y, text, color=RED, size=30):
    d.text((x, y), text, font=font(F_SANS, size), fill=color)


def num_badge(d, x, y, n, r=24, fill=RED, fg=LIGHT, size=30):
    d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline=INK, width=3)
    d.text((x, y), str(n), font=font(F_SANS, size), fill=fg, anchor="mm")


def src_tag(d, x, y, text, size=26, fill=GREY):
    d.text((x, y), text, font=font(F_SANS, size), fill=fill)


def masthead(d, w):
    rule(d, M, 46, w - M, INK, 6)
    d.text((w // 2, 58), "THE WORLD IN ONE PICTURE",
           font=font(F_SERIF, 88), fill=INK, anchor="ma")
    d.text((w // 2, 152), "F R I D A Y   2 0   N O V E M B E R   2 0 2 6",
           font=font(F_SANS, 44), fill=RED, anchor="ma")
    d.text((w // 2, 210),
           "35 STORIES  \u00b7  6 REGIONS  \u00b7  ONE PAGE  \u00b7  EVERY STORY HAPPENED OR WAS FIRST REPORTED TODAY",
           font=font(F_SANS, 26), fill=GREY, anchor="ma")
    rule(d, M, 252, w - M, RED, 5)


STATS = [
    ("400+", "drones at Ukraine"),
    ("110+", "missiles fired"),
    ("\u22125.28%", "Nasdaq plunge"),
    ("$3.79bn", "GTA VI day-one sales"),
    ("$7.25bn", "Bayer settlement"),
    ("2", "missiles in Poland"),
]


def stat_strip(d, y0, y1):
    d.rectangle([M, y0, S - M, y1], fill=NAVY, outline=INK, width=4)
    w = (S - 2 * M) / 6
    for i, (big, label) in enumerate(STATS):
        x = M + i * w
        if i:
            d.line([(x, y0 + 14), (x, y1 - 14)], fill=(90, 120, 170), width=3)
        d.text((x + w / 2, y0 + 12), big, font=font(F_SERIF, 52),
               fill=GOLD, anchor="ma")
        d.text((x + w / 2, y0 + 76), label, font=font(F_SANS_R, 23),
               fill=(215, 220, 230), anchor="ma")


def hero_barrage(img, d, box, n):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 210, (12, 16, 34), (120, 52, 28))
    img.paste(sky, (x0, y0))
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)
    # Kyiv bridges over the Dnipro, river below
    d.rectangle([x0, y0 + 150, x1, y0 + 210], fill=(28, 48, 78))
    for lx in range(x0 + 20, x1 - 40, 60):
        d.rectangle([lx, y0 + 172, lx + 34, y0 + 178], fill=(110, 150, 200))
    # bridge deck + arches
    d.rectangle([x0 + 30, y0 + 118, x1 - 30, y0 + 138], fill=(40, 40, 46))
    for ax in range(x0 + 90, x1 - 90, 130):
        d.arc([ax, y0 + 96, ax + 110, y0 + 150], 180, 360, fill=(90, 90, 100),
              width=7)
    # missile trails: long diagonal streaks ending in fireballs
    for tx, ty, tl in [(90, 26, 110), (280, 60, 90), (450, 20, 120)]:
        d.line([(x0 + tx, y0 + ty), (x0 + tx + 46, y0 + ty + tl)],
               fill=(255, 210, 110), width=7)
        d.line([(x0 + tx + 8, y0 + ty + 6), (x0 + tx + 46, y0 + ty + tl)],
               fill=(255, 140, 50), width=4)
        d.ellipse([x0 + tx + 34, y0 + ty + tl - 12, x0 + tx + 58,
                   y0 + ty + tl + 12], fill=(255, 170, 40))
    # explosion glow over the bridge
    d.ellipse([x0 + 380, y0 + 60, x0 + 500, y0 + 140], fill=(255, 120, 30))
    d.ellipse([x0 + 410, y0 + 80, x0 + 470, y0 + 120], fill=(255, 210, 90))
    d.rectangle([x0, y0 + 210, x1, y1], fill=PAPER)
    num_badge(d, x0 + 40, y0 + 232, n)
    kicker(d, x0 + 76, y0 + 222, "KYIV  \u2014  OVERNIGHT BARRAGE", RED, 28)
    y = headline(d, x0 + 24, y0 + 258,
                 "400+ drones, 110 missiles rain on Ukraine",
                 40, INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "Eight killed; Kyiv bridges hit. \u2014 Reuters",
               font(F_SANS_R, 26), INK, x1 - x0 - 48, leading=32)
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)


def hero_poland(img, d, box, n):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, 210, (40, 60, 90), (200, 190, 170))
    img.paste(sky, (x0, y0))
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)
    # Polish field + cottage, smoke column where the missile fell
    d.rectangle([x0, y0 + 150, x1, y0 + 210], fill=(96, 128, 62))
    d.polygon([(x0, y0 + 150), (x0 + 220, y0 + 90), (x0 + 440, y0 + 150)],
              fill=(70, 100, 48))
    d.rectangle([x0 + 90, y0 + 120, x0 + 210, y0 + 170], fill=(190, 170, 140))
    d.polygon([(x0 + 80, y0 + 122), (x0 + 150, y0 + 88), (x0 + 220, y0 + 122)],
              fill=(150, 60, 50))
    # falling missile: diagonal streak + impact fireball
    d.line([(x0 + 440, y0 + 16), (x0 + 505, y0 + 118)], fill=(255, 220, 120),
           width=7)
    d.line([(x0 + 452, y0 + 22), (x0 + 505, y0 + 118)], fill=(255, 140, 50),
           width=4)
    for sx, sy, sr in [(500, 130, 26), (530, 100, 32), (560, 130, 24)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(70, 66, 66))
    d.ellipse([x0 + 480, y0 + 150, x0 + 540, y0 + 190], fill=(255, 140, 40))
    # NATO flag hint: blue band with stars
    d.rectangle([x0 + 30, y0 + 24, x0 + 150, y0 + 66], fill=(30, 60, 140))
    for i in range(5):
        a = math.radians(i * 72 - 90)
        d.ellipse([x0 + 90 + 18 * math.cos(a) - 3, y0 + 45 + 18 * math.sin(a) - 3,
                   x0 + 90 + 18 * math.cos(a) + 3, y0 + 45 + 18 * math.sin(a) + 3],
                  fill=LIGHT)
    d.rectangle([x0, y0 + 210, x1, y1], fill=PAPER)
    num_badge(d, x0 + 40, y0 + 232, n)
    kicker(d, x0 + 76, y0 + 222, "POLAND  \u2014  NATO ALERT", RED, 28)
    y = headline(d, x0 + 24, y0 + 258,
                 "Two Russian missiles land in Poland",
                 40, INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "NATO calls it a \u201cgrave violation\u201d. \u2014 Reuters",
               font(F_SANS_R, 26), INK, x1 - x0 - 48, leading=32)
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)


def hero_markets(img, d, box, n):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=DARK, outline=INK, width=4)
    # red crash chart across the top
    pts = [(x0 + 40 + i * 92, y0 + 40 + i * 22) for i in range(7)]
    d.line(pts, fill=RED, width=10, joint="curve")
    d.polygon(pts + [(x0 + 592, y0 + 200), (x0 + 40, y0 + 200)],
              fill=(120, 20, 20))
    d.text((x0 + 40, y0 + 24), "NASDAQ", font=font(F_SANS, 30),
           fill=(255, 120, 120))
    d.text((x0 + 400, y0 + 130), "\u22125.28%", font=font(F_SANS, 46),
           fill=(255, 120, 120))
    # ticker board
    d.rectangle([x0, y0 + 210, x1, y1], fill=PAPER)
    num_badge(d, x0 + 40, y0 + 232, n)
    kicker(d, x0 + 76, y0 + 222, "NEW YORK  \u2014  MARKETS", GOLD, 28)
    y = headline(d, x0 + 24, y0 + 258,
                 "Nasdaq plunges 5.28% on Nvidia SEC probe",
                 40, INK, max_w=x1 - x0 - 48)
    text_block(d, x0 + 24, y + 4,
               "S&P \u22123.7% into correction. \u2014 Reuters",
               font(F_SANS_R, 26), INK, x1 - x0 - 48, leading=32)
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)

# ---- generic panel -------------------------------------------------------

def panel(img, d, box, n, kick, head, dek, src, illu, hsize=36, dsize=27,
          illu_h=140):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=PAPER, outline=INK, width=4)
    # illustrations are drawn at a fixed 140px height, then scaled to illu_h
    tmp = Image.new("RGB", (x1 - x0, 140), PAPER)
    d2 = ImageDraw.Draw(tmp, "RGBA")
    illu(tmp, d2, (0, 0, x1 - x0, 140))
    img.paste(tmp.resize((x1 - x0, illu_h), Image.LANCZOS), (x0, y0))
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)
    d.rectangle([x0, y0 + illu_h, x1, y1], fill=PAPER)
    num_badge(d, x0 + 34, y0 + illu_h + 22, n, r=20, size=26)
    kicker(d, x0 + 62, y0 + illu_h + 12, kick, RED, 24)
    y = headline(d, x0 + 20, y0 + illu_h + 46, head, hsize, INK,
                 max_w=x1 - x0 - 40)
    text_block(d, x0 + 20, y + 2, dek + " \u2014 " + src,
               font(F_SANS_R, dsize), INK, x1 - x0 - 40,
               leading=int(dsize * 1.25))
    d.rounded_rectangle(box, radius=14, outline=INK, width=4)


def illu_neon(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (30, 10, 60), (190, 40, 110))
    img.paste(sky, (x0, y0))
    # Vice City skyline + palm + sun
    d.ellipse([x0 + 300, y0 + 14, x0 + 380, y0 + 94], fill=(255, 150, 80))
    for bx, bh, col in [(40, 90, (20, 20, 40)), (130, 120, (30, 20, 50)),
                        (230, 80, (20, 20, 40)), (330, 110, (35, 20, 55))]:
        d.rectangle([x0 + bx, y0 + 140 - bh, x0 + bx + 70, y0 + 140],
                    fill=col)
        for wy in range(0, bh - 10, 18):
            d.rectangle([x0 + bx + 10, y0 + 140 - bh + wy, x0 + bx + 26,
                         y0 + 140 - bh + wy + 10], fill=(255, 220, 100))
    d.rectangle([x0, y0 + 132, x1, y1], fill=(16, 10, 30))
    d.text((x0 + 24, y0 + 8), "GTA VI", font=font(F_SANS, 44),
           fill=(255, 90, 180))


def illu_whitehouse(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (120, 160, 210), (220, 220, 210))
    img.paste(sky, (x0, y0))
    d.rectangle([x0 + 120, y0 + 70, x0 + 340, y0 + 140], fill=(240, 240, 235))
    d.polygon([(x0 + 110, y0 + 72), (x0 + 230, y0 + 30), (x0 + 350, y0 + 72)],
              fill=(230, 230, 225))
    for cx in range(140, 340, 40):
        d.rectangle([x0 + cx, y0 + 84, x0 + cx + 14, y0 + 140],
                    fill=(200, 200, 195))
    d.rectangle([x0, y0 + 132, x1, y1], fill=(70, 110, 60))
    # microphones
    for mx in (180, 210, 240, 270):
        d.line([(x0 + mx, y0 + 100), (x0 + mx, y0 + 140)], fill=INK, width=5)
        d.ellipse([x0 + mx - 7, y0 + 92, x0 + mx + 7, y0 + 106], fill=INK)


def illu_cop(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (30, 60, 90), (120, 170, 200))
    img.paste(sky, (x0, y0))
    d.rectangle([x0 + 60, y0 + 70, x0 + 220, y0 + 140], fill=(40, 50, 66))
    d.polygon([(x0 + 50, y0 + 72), (x0 + 140, y0 + 34), (x0 + 230, y0 + 72)],
              fill=(28, 36, 50))
    d.rectangle([x0 + 270, y0 + 50, x0 + 300, y0 + 140], fill=(70, 70, 76))
    for sx, sy, sr in [(320, 44, 18), (350, 30, 22), (380, 44, 16)]:
        d.ellipse([x0 + sx - sr, y0 + sy - sr, x0 + sx + sr, y0 + sy + sr],
                  fill=(120, 120, 124))
    d.polygon([(x0 + 330, y0 + 140), (x0 + 430, y0 + 140), (x0 + 410, y0 + 104),
               (x0 + 350, y0 + 104)], fill=(30, 90, 160))


def illu_tanker(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (120, 70, 40), (40, 30, 30))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 96, x1, y1], fill=(30, 60, 90))
    d.polygon([(x0 + 60, y0 + 76), (x0 + 380, y0 + 76), (x0 + 360, y0 + 110),
               (x0 + 80, y0 + 110)], fill=(140, 30, 30))
    d.rectangle([x0 + 300, y0 + 44, x0 + 350, y0 + 76], fill=(200, 200, 200))
    for fx, fh in [(140, 44), (190, 60), (240, 46)]:
        d.polygon([(x0 + fx - 14, y0 + 78), (x0 + fx, y0 + 78 - fh),
                   (x0 + fx + 14, y0 + 78)], fill=(255, 120, 20))
        d.polygon([(x0 + fx - 7, y0 + 78), (x0 + fx, y0 + 78 - fh // 2),
                   (x0 + fx + 7, y0 + 78)], fill=(255, 210, 60))


def illu_flags(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (60, 90, 160), (200, 210, 230))
    img.paste(sky, (x0, y0))
    # Union Jack-ish + EU stars, two flagpoles
    d.line([(x0 + 120, y0 + 20), (x0 + 120, y0 + 130)], fill=(200, 200, 200),
           width=6)
    d.rectangle([x0 + 126, y0 + 24, x0 + 236, y0 + 84], fill=(30, 60, 140))
    d.line([(x0 + 126, y0 + 24), (x0 + 236, y0 + 84)], fill=LIGHT, width=6)
    d.line([(x0 + 236, y0 + 24), (x0 + 126, y0 + 84)], fill=LIGHT, width=6)
    d.line([(x0 + 300, y0 + 20), (x0 + 300, y0 + 130)], fill=(200, 200, 200),
           width=6)
    d.rectangle([x0 + 306, y0 + 24, x0 + 416, y0 + 84], fill=(20, 40, 120))
    for i in range(6):
        a = math.radians(i * 60 - 90)
        d.ellipse([x0 + 361 + 20 * math.cos(a) - 3, y0 + 54 + 20 * math.sin(a) - 3,
                   x0 + 361 + 20 * math.cos(a) + 3, y0 + 54 + 20 * math.sin(a) + 3],
                  fill=GOLD)
    d.rectangle([x0, y0 + 130, x1, y1], fill=(90, 110, 80))


def illu_desert(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (20, 30, 60), (150, 90, 50))
    img.paste(sky, (x0, y0))
    d.polygon([(x0, y0 + 140), (x0 + 200, y0 + 80), (x0 + 460, y0 + 140)],
              fill=(120, 90, 50))
    d.rectangle([x0 + 60, y0 + 96, x0 + 130, y0 + 140], fill=(200, 180, 150))
    d.polygon([(x0 + 55, y0 + 98), (x0 + 95, y0 + 70), (x0 + 135, y0 + 98)],
              fill=(170, 140, 110))
    # interceptor streaks
    for tx, ty in [(260, 30), (320, 55), (380, 25)]:
        d.line([(x0 + tx, y0 + ty + 50), (x0 + tx + 20, y0 + ty)],
               fill=(255, 220, 120), width=5)
        d.ellipse([x0 + tx + 12, y0 + ty - 8, x0 + tx + 28, y0 + ty + 8],
                  fill=(255, 180, 60))


def illu_court(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (180, 180, 175), (120, 120, 115))
    img.paste(sky, (x0, y0))
    d.rectangle([x0 + 100, y0 + 60, x0 + 360, y0 + 140], fill=(210, 205, 190))
    d.polygon([(x0 + 90, y0 + 62), (x0 + 230, y0 + 22), (x0 + 370, y0 + 62)],
              fill=(190, 185, 170))
    for cx in range(120, 350, 44):
        d.rectangle([x0 + cx, y0 + 76, x0 + cx + 16, y0 + 140],
                    fill=(170, 165, 150))
    # scales
    sx, sy = x0 + 230, y0 + 96
    d.line([(sx, sy), (sx, sy + 40)], fill=INK, width=5)
    d.line([(sx - 40, sy + 8), (sx + 40, sy + 8)], fill=INK, width=5)
    d.pieslice([sx - 54, sy + 22, sx - 26, sy + 40], 0, 180, fill=GOLD)
    d.pieslice([sx + 26, sy + 22, sx + 54, sy + 40], 0, 180, fill=GOLD)


def illu_hoop(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (120, 30, 30), (40, 20, 20))
    img.paste(sky, (x0, y0))
    # backboard + hoop + ball
    d.rectangle([x0 + 300, y0 + 20, x0 + 420, y0 + 110], fill=LIGHT,
                outline=INK, width=4)
    d.ellipse([x0 + 330, y0 + 100, x0 + 390, y0 + 122], outline=RED, width=6)
    for ny in range(122, 140, 6):
        d.line([(x0 + 340, y0 + 122), (x0 + 340, y0 + 140)], fill=LIGHT,
               width=2)
    d.ellipse([x0 + 90, y0 + 40, x0 + 170, y0 + 120], fill=(230, 110, 40),
              outline=(120, 50, 10), width=4)
    d.arc([x0 + 90, y0 + 40, x0 + 170, y0 + 120], 300, 60, fill=(120, 50, 10),
          width=4)
    d.line([(x0 + 90, y0 + 80), (x0 + 170, y0 + 80)], fill=(120, 50, 10),
           width=4)
    d.text((x0 + 24, y0 + 104), "50", font=font(F_SERIF, 40), fill=GOLD)


def illu_border(img, d, box):
    x0, y0, x1, y1 = box
    sky = vgrad(x1 - x0, y1 - y0, (140, 160, 180), (210, 210, 200))
    img.paste(sky, (x0, y0))
    d.rectangle([x0, y0 + 100, x1, y1], fill=(100, 120, 80))
    # fence + barrier sign
    for fx in range(20, 460, 46):
        d.line([(x0 + fx, y0 + 40), (x0 + fx, y0 + 140)], fill=(60, 60, 66),
               width=7)
    d.line([(x0 + 10, y0 + 55), (x0 + 450, y0 + 55)], fill=(60, 60, 66),
           width=6)
    d.line([(x0 + 10, y0 + 95), (x0 + 450, y0 + 95)], fill=(60, 60, 66),
           width=6)
    d.rectangle([x0 + 150, y0 + 60, x0 + 310, y0 + 92], fill=(200, 40, 40))
    d.text((x0 + 230, y0 + 76), "CLOSED", font=font(F_SANS, 26), fill=LIGHT,
           anchor="mm")

# ---- world map -----------------------------------------------------------

CONTINENTS = [
    [(-170, 70), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 30), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-60, 5), (-50, 0), (-35, -8), (-40, -20), (-50, -30),
     (-60, -40), (-70, -55), (-75, -35), (-80, -15)],
    [(-10, 35), (10, 37), (30, 32), (35, 28), (43, 12), (51, 10), (40, -5),
     (35, -20), (20, -35), (15, -20), (10, -5), (-5, 5), (-17, 15),
     (-17, 25)],
    [(-10, 36), (-9, 43), (0, 48), (-5, 50), (5, 53), (8, 57), (18, 56),
     (21, 55), (28, 60), (30, 70), (40, 68), (45, 55), (40, 45), (30, 36),
     (23, 36), (19, 40), (12, 44), (3, 42), (-2, 37)],
    [(40, 68), (60, 70), (90, 75), (120, 77), (160, 70), (180, 66),
     (162, 60), (158, 52), (142, 45), (135, 35), (127, 35), (120, 30),
     (110, 20), (105, 10), (100, 8), (95, 16), (90, 22), (80, 8), (75, 20),
     (65, 25), (55, 25), (50, 29), (43, 12), (40, 30)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (130, -13), (122, -17)],
]

PINS = [(1, 30.5, 50.4), (2, 19, 52), (3, -74, 40.7), (4, -80, 25.8),
        (5, -77, 38.9), (6, 30.7, 36.9), (7, 56.5, 26.5), (8, -0.1, 51.5),
        (9, 46.7, 24.7), (10, -122, 37.8), (11, -81.7, 41.5), (12, 25, 59)]


def world_map(img, d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=(24, 52, 92), outline=INK,
                        width=4)
    d.text((x0 + 20, y0 + 12), "WHERE IT HAPPENED",
           font=font(F_SANS, 30), fill=GOLD)
    mx0, my0, mx1, my1 = x0 + 16, y0 + 52, x1 - 16, y1 - 14
    mw, mh = mx1 - mx0, my1 - my0

    def proj(lon, lat):
        return (mx0 + (lon + 180) / 360 * mw,
                my0 + (90 - lat) / 180 * mh)

    for cont in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in cont],
                  fill=(120, 160, 110), outline=(200, 210, 190))
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        d.ellipse([px - 17, py - 17, px + 17, py + 17], fill=RED,
                  outline=LIGHT, width=3)
        d.text((px, py), str(n), font=font(F_SANS, 24), fill=LIGHT,
               anchor="mm")


BRIEFS = [
    (13, "Kerch Bridge rail halted after third Ukrainian strike \u2014 AP"),
    (14, "Ukraine retakes 14 settlements in Kharkiv \u2014 Kyiv"),
    (15, "Anthropic falls 8.5% to $88.91 on day two \u2014 Reuters"),
    (16, "Bitcoin below $60,000, first time since July \u2014 Reuters"),
    (17, "Fed's Cook watches AI-industry financing \u2014 Reuters"),
    (18, "Cognition AI in talks at $75bn valuation \u2014 Bloomberg"),
    (19, "Databricks in early talks at $225bn \u2014 WSJ"),
    (20, "Trump questions European aid to Ukraine \u2014 Politico"),
    (21, "Vance won't say he'd have ordered Iran strikes \u2014 Reuters"),
    (22, "Denmark: Russia plotted to kill American Ukrainian \u2014 AP"),
    (23, "Mamdani plans to close Rikers Island jail \u2014 AP"),
    (24, "Medvedev beats Tiafoe 6\u20133 6\u20134, ATP Finals \u2014 ATP"),
    (25, "Verstappen on Las Vegas pole; Antonelli fastest \u2014 Reuters"),
    (26, "India A thrash Nepal by 306 runs in Doha \u2014 ESPNcricinfo"),
    (27, "UAE Bulls win Abu Dhabi T10 final by 24 runs \u2014 ESPNcricinfo"),
    (28, "India\u2013Japan deepen defence ties in Tokyo \u2014 MEA"),
    (29, "Nigeria funeral boat capsizes; 4 dead \u2014 AP"),
    (30, "UN agrees killer-robot talks by 2028 \u2014 Reuters"),
    (31, "FBI crime database hacked, CNN reports \u2014 Reuters"),
    (32, "Virginia child dies in state's first measles death \u2014 Reuters"),
    (33, "Cargo ship aground in France; 19 crew airlifted \u2014 Reuters"),
    (34, "Judge declines ban on Trump taxpayer ads \u2014 AP"),
    (35, "Texas execution takes over an hour \u2014 AP"),
]


def briefs_band(d, x0, y0, x1, y1):
    d.text((x0, y0 + 6), "IN BRIEF  \u2014  13\u201335",
           font=font(F_SERIF, 34), fill=INK)
    rule(d, x0, y0 + 52, x1, RED, 4)
    col_w = (x1 - x0 - 40) / 2
    fnt = font(F_SANS_R, 20)
    for i, (n, text) in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        bx = x0 + col * (col_w + 40)
        by = y0 + 62 + row * 22
        d.text((bx, by), f"{n}. {text}", font=fnt, fill=INK)


EXCLUDED_LEFT = [
    "Shenzhen summit (Trump\u2013Xi\u2013Putin) \u2014 19 Nov",
    "ICJ Myanmar genocide ruling \u2014 19 Nov",
    "Anthropic Nasdaq debut \u2014 19 Nov",
    "Indonesia VP Gibran resigns \u2014 19 Nov",
]
EXCLUDED_RIGHT = [
    "US\u2013Venezuela military deal \u2014 announced 18 Nov",
    "Voyager 1 one light-day out \u2014 18 Nov",
    "Banda Sea quake M6.8 \u2014 21 Nov (Saturday)",
]


def date_check(d, box):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=14, fill=(232, 226, 208), outline=INK,
                        width=4)
    d.text((x0 + 24, y0 + 10), "DATE CHECK \u2014 LEFT OUT ON PURPOSE",
           font=font(F_SANS, 30), fill=DARKRED)
    fnt = font(F_SANS_R, 26)
    for i, t in enumerate(EXCLUDED_LEFT):
        d.text((x0 + 24, y0 + 48 + i * 26), "\u2715  " + t, font=fnt, fill=INK)
    for i, t in enumerate(EXCLUDED_RIGHT):
        d.text((x0 + 1020, y0 + 48 + i * 26), "\u2715  " + t, font=fnt,
               fill=INK)
    d.text((x0 + 24, y0 + 160),
           "Every story on this page happened, or was first reported, on "
           "Friday 20 November 2026.",
           font=font(F_SANS, 25), fill=INK)
    d.text((x0 + 24, y0 + 188),
           "Sources: Reuters \u00b7 AP \u00b7 Bloomberg \u00b7 WSJ \u00b7 Politico "
           "\u00b7 CNN \u00b7 ESPNcricinfo \u00b7 ATP \u00b7 MEA \u00b7 IANS",
           font=font(F_SANS, 20), fill=GREY)


def main():
    img = Image.new("RGB", (S, S), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    masthead(d, S)
    stat_strip(d, 264, 378)
    # three heroes
    hero_barrage(img, d, (M, 390, 700, 800), 1)
    hero_poland(img, d, (716, 390, 1380, 800), 2)
    hero_markets(img, d, (1396, 390, 2012, 800), 3)
    # panel row 1: four panels
    xs1 = [36, 534, 1032, 1530]
    xe1 = [518, 1016, 1514, 2012]
    panel(img, d, (xs1[0], 812, xe1[0], 1130), 4, "MIAMI \u2014 GAMES",
          "GTA VI banks $3.79bn on day one",
          "Rockstar reports record first-day sales.",
          "Reuters", illu_neon, hsize=32, dsize=25, illu_h=100)
    panel(img, d, (xs1[1], 812, xe1[1], 1130), 5, "WASHINGTON \u2014 WHITE HOUSE",
          "Trump threatens tax on AI data centres abroad",
          "\u201cTremendous\u201d penalties for firms building abroad.",
          "AP", illu_whitehouse, hsize=32, dsize=25, illu_h=100)
    panel(img, d, (xs1[2], 812, xe1[2], 1130), 6, "ANTALYA \u2014 COP31",
          "COP31 talks run into overtime",
          "Draft drops fossil fuels; activists slam text.",
          "AP", illu_cop, hsize=32, dsize=25, illu_h=100)
    panel(img, d, (xs1[3], 812, xe1[3], 1130), 7, "STRAIT OF HORMUZ \u2014 CLAIM",
          "Iran says two tankers hit mines",
          "Iran's army claims mine blasts east of the Strait.",
          "Reuters", illu_tanker, hsize=32, dsize=25, illu_h=100)
    # panel row 2: five panels
    xs2 = [36, 434, 832, 1230, 1628]
    xe2 = [418, 816, 1214, 1612, 2012]
    panel(img, d, (xs2[0], 1142, xe2[0], 1460), 8, "LONDON \u2014 UK & EU",
          "UK and EU strike trade and travel deals",
          "Pledge to rebuild ties after Brexit.",
          "AP", illu_flags, hsize=29, dsize=22, illu_h=90)
    panel(img, d, (xs2[1], 1142, xe2[1], 1460), 9, "RIYADH \u2014 DEFENCE",
          "Saudi intercepts more Houthi missiles",
          "More missiles and drones stopped.",
          "AP", illu_desert, hsize=29, dsize=22, illu_h=90)
    panel(img, d, (xs2[2], 1142, xe2[2], 1460), 10, "US COURT \u2014 BAYER",
          "Judge approves $7.25bn Bayer deal",
          "Roundup deal clears its final hurdle.",
          "AP", illu_court, hsize=29, dsize=22, illu_h=90)
    panel(img, d, (xs2[3], 1142, xe2[3], 1460), 11, "CLEVELAND \u2014 NBA",
          "Harden's 50th 50-point game",
          "Cavs beat Pacers 128\u2013119; Kobe passed.",
          "AP", illu_hoop, hsize=29, dsize=22, illu_h=90)
    panel(img, d, (xs2[4], 1142, xe2[4], 1460), 12, "TALLINN \u2014 BORDER",
          "Estonia closes border with Russia",
          "Moscow decries a \u201cnew Iron Curtain\u201d.",
          "Reuters", illu_border, hsize=29, dsize=22, illu_h=90)
    # map + briefs band
    world_map(img, d, (M, 1472, 600, 1790))
    briefs_band(d, 620, 1472, 2012, 1790)
    # date check footer
    date_check(d, (M, 1800, 2012, 2012))
    small = img.resize((1024, 1024), Image.LANCZOS)
    small.save("entry.png", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
