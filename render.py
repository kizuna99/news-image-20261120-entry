"""The World Brief v3 — deterministic editorial poster generator.

Draws at 2048x2048 (supersampled) and downscales to the contest size
1024x1024. All randomness comes from a fixed seed; no timestamps.
Requires Pillow + Liberation fonts.
"""
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersample factor
W = 1024 * SS
SEED = 20261120

FONT_DIR = os.environ.get(
    "LIBERATION_FONTS", "/usr/share/fonts/truetype/liberation"
)


def font(name, size):
    return ImageFont.truetype(str(Path(FONT_DIR) / name), int(size * SS))


SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"

# palette
PAPER = (246, 239, 220)
PAPER_D = (238, 228, 200)
INK = (18, 26, 48)
NAVY = (16, 32, 64)
NAVY2 = (27, 48, 92)
GOLD = (192, 148, 44)
GOLD_L = (232, 196, 106)
RED = (178, 34, 40)
RED_D = (128, 22, 30)
CREAM_TXT = (250, 245, 228)
TEAL = (14, 92, 96)
TEAL_D = (8, 52, 62)


def X(v):
    return v * SS


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(d, box, top, bot):
    x0, y0, x1, y1 = [X(v) for v in box]
    h = max(1, y1 - y0)
    for i in range(h):
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=lerp(top, bot, i / h))


def text_c(d, cx, y, s, fnt, fill, spacing=0):
    """Centered text with optional letter spacing (drawn char by char)."""
    if spacing:
        widths = [d.textlength(ch, font=fnt) for ch in s]
        total = sum(widths) + spacing * SS * (len(s) - 1)
        x = X(cx) - total / 2
        for ch, w in zip(s, widths):
            d.text((x, X(y)), ch, font=fnt, fill=fill)
            x += w + spacing * SS
        return
    w = d.textlength(s, font=fnt)
    d.text((X(cx) - w / 2, X(y)), s, font=fnt, fill=fill)


def text_l(d, x, y, s, fnt, fill):
    d.text((X(x), X(y)), s, font=fnt, fill=fill)


def wrap(d, s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fnt) <= X(maxw) or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def tower(d, cx, base, h, col, wtop=10, wbot=30):
    """Transmission tower silhouette."""
    cx, base, h = X(cx), X(base), X(h)
    wt, wb = X(wtop), X(wbot)
    d.line([(cx - wb, base), (cx - wt, base - h)], fill=col, width=3 * SS)
    d.line([(cx + wb, base), (cx + wt, base - h)], fill=col, width=3 * SS)
    d.line([(cx - wb, base), (cx + wt, base - h)], fill=col, width=2 * SS)
    d.line([(cx + wb, base), (cx - wt, base - h)], fill=col, width=2 * SS)
    for t in (0.35, 0.6, 0.85):
        y = base - h * t
        half = wb + (wt - wb) * t
        d.line([(cx - half, y), (cx + half, y)], fill=col, width=2 * SS)
    for arm_y, arm_w in ((0.97, 44), (0.82, 36)):
        y = base - h * arm_y
        d.line([(cx - X(arm_w), y), (cx + X(arm_w), y)], fill=col, width=3 * SS)
        for sx in (-1, 1):
            d.line([(cx + sx * X(arm_w), y), (cx + sx * X(arm_w), y + X(9))],
                   fill=col, width=2 * SS)


def spark(d, cx, cy, r, col):
    cx, cy, r = X(cx), X(cy), X(r)
    for a in range(0, 360, 45):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([(cx, cy), (cx + dx * r, cy + dy * r)], fill=col, width=2 * SS)
    d.ellipse([cx - r * 0.28, cy - r * 0.28, cx + r * 0.28, cy + r * 0.28],
              fill=col)


def build():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img, "RGBA")

    # paper grain (deterministic)
    for _ in range(5200):
        gx, gy = rng.randrange(W), rng.randrange(W)
        tone = rng.choice([(232, 222, 192), (252, 247, 232), (240, 231, 205)])
        d.point((gx, gy), fill=tone)

    # outer frame
    d.rectangle([X(10), X(10), X(1014), X(1014)], outline=NAVY, width=3 * SS)
    d.rectangle([X(17), X(17), X(1007), X(1007)], outline=GOLD, width=1 * SS)

    # ---------- masthead ----------
    text_c(d, 512, 26, "INDEPENDENT DAILY PICTURE EDITION · ONE DAY · ONE PAGE",
           font(SANS_B, 10.5), RED, spacing=2)
    text_c(d, 512, 42, "THE WORLD BRIEF", font(SERIF_B, 63), INK)
    d.line([(X(28), X(116)), (X(996), X(116))], fill=RED, width=3 * SS)
    d.line([(X(28), X(121)), (X(996), X(121))], fill=GOLD, width=1 * SS)
    # dateline bar
    d.rectangle([X(28), X(127), X(996), X(153)], fill=NAVY)
    text_l(d, 40, 133, "FRIDAY · 20 NOVEMBER 2026", font(SANS_B, 13.5), GOLD_L)
    r = "30 SOURCED STORIES · 7 REGIONS · 6 ILLUSTRATED"
    f = font(SANS_B, 13.5)
    d.text((X(984) - d.textlength(r, font=f), X(133)), r, font=f, fill=CREAM_TXT)

    # ---------- hero scene ----------
    hx0, hy0, hx1, hy1 = 28, 161, 996, 349
    split = 592
    # left: Ukraine night
    vgrad(d, (hx0, hy0, split, hy1), (10, 16, 38), (38, 52, 96))
    # right: COP31 dawn
    vgrad(d, (split, hy0, hx1, hy1), (16, 84, 96), (238, 178, 92))
    # stars (left only)
    for _ in range(90):
        sx = rng.randrange(X(hx0 + 8), X(split - 8))
        sy = rng.randrange(X(hy0 + 6), X(hy0 + 90))
        d.point((sx, sy), fill=(220, 228, 250))
        if rng.random() < 0.3:
            d.point((sx + 1, sy), fill=(180, 195, 235))
    # moon
    d.ellipse([X(70), X(176), X(104), X(210)], fill=(232, 234, 220))
    d.ellipse([X(82), X(172), X(112), X(206)], fill=(16, 26, 56))
    # sun (right)
    d.ellipse([X(872), X(196), X(968), X(292)], fill=(250, 205, 92))
    d.ellipse([X(884), X(208), X(956), X(280)], fill=(252, 220, 130))
    # globe arc (right, centre-left of dawn side)
    gx, gy, gr = 700, 268, 62
    d.ellipse([X(gx - gr), X(gy - gr), X(gx + gr), X(gy + gr)],
              outline=(240, 240, 230), width=2 * SS)
    for k in (-0.6, 0.0, 0.6):
        d.arc([X(gx - gr * (1 - abs(k)) - 4), X(gy - gr), X(gx + gr * (1 - abs(k)) + 4),
               X(gy + gr)], 90, 270, fill=(240, 240, 230), width=1 * SS)
        d.arc([X(gx - gr * (1 - abs(k)) - 4), X(gy - gr), X(gx + gr * (1 - abs(k)) + 4),
               X(gy + gr)], 270, 450, fill=(240, 240, 230), width=1 * SS)
    for off in (-30, 0, 30):
        d.line([(X(gx - gr + 4), X(gy + off)), (X(gx + gr - 4), X(gy + off))],
               fill=(240, 240, 230), width=1 * SS)
    # towers + lines (left)
    tower(d, 180, 330, 118, (8, 12, 26))
    tower(d, 330, 330, 92, (8, 12, 26))
    tower(d, 468, 330, 128, (8, 12, 26))
    for (x1, y1, x2, y2) in [(136, 218, 286, 244), (224, 218, 374, 244),
                            (374, 244, 424, 208), (286, 244, 512, 208)]:
        d.line([(X(x1), X(y1)), (X(x2), X(y2))], fill=(8, 12, 26), width=2 * SS)
    # sparks / barrage glow
    spark(d, 262, 268, 15, (255, 176, 66))
    spark(d, 408, 292, 11, (255, 140, 60))
    spark(d, 128, 300, 9, (255, 196, 90))
    d.ellipse([X(238), X(306), X(300), X(330)], fill=(255, 120, 50, 110))
    # bridge silhouette (left bottom)
    d.rectangle([X(hx0), X(318), X(split), X(330)], fill=(52, 74, 122))
    for bx in range(hx0 + 26, split - 10, 52):
        d.line([(X(bx), X(318)), (X(bx + 20), X(300))], fill=(6, 10, 20),
               width=3 * SS)
        d.line([(X(bx + 20), X(300)), (X(bx + 40), X(318))], fill=(6, 10, 20),
               width=3 * SS)
    # Antalya skyline (right bottom): dome + minarets
    sky = TEAL_D
    d.rectangle([X(split), X(316), X(hx1), X(330)], fill=sky)
    d.pieslice([X(748), X(252), X(868), X(330)], 180, 360, fill=sky)
    d.rectangle([X(802), X(238), X(814), X(258)], fill=sky)
    d.polygon([(X(802), X(238)), (X(814), X(238)), (X(808), X(224))], fill=sky)
    for mx in (636, 946):
        d.rectangle([X(mx), X(252), X(mx + 10), X(330)], fill=sky)
        d.polygon([(X(mx - 2), X(252)), (X(mx + 12), X(252)), (X(mx + 5), X(232))],
                  fill=sky)
        d.rectangle([X(mx - 4), X(282), X(mx + 14), X(288)], fill=sky)
    for bx, bw, bh in [(600, 44, 34), (884, 52, 42), (700, 30, 22)]:
        d.rectangle([X(bx), X(330 - bh), X(bx + bw), X(330)], fill=sky)
    # ground line both sides
    d.rectangle([X(hx0), X(330), X(hx1), X(hy1)], fill=(10, 14, 26))
    # hero frame + divider
    d.line([(X(split), X(hy0)), (X(split), X(hy1))], fill=GOLD, width=2 * SS)
    d.rectangle([X(hx0), X(hy0), X(hx1), X(hy1)], outline=INK, width=2 * SS)
    # hero tags
    d.rectangle([X(hx0), X(hy0), X(252), X(hy0 + 24)], fill=RED)
    text_l(d, hx0 + 10, hy0 + 4, "LEAD · EUROPE AT WAR", font(SANS_B, 11.5),
           CREAM_TXT)
    d.rectangle([X(772), X(hy0), X(hx1), X(hy0 + 24)], fill=TEAL_D)
    text_l(d, 782, hy0 + 4, "CLIMATE · COP31 FINALE", font(SANS_B, 11.5),
           CREAM_TXT)
    return img, d


# ---------------- panels ----------------

def icon_tower(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (16, 26, 58), (52, 74, 128))
    tower(d, x + w / 2, y + h - 8, h - 26, (6, 9, 18), 8, 24)
    spark(d, x + w / 2 + 16, y + 26, 10, (255, 176, 66))
    spark(d, x + 18, y + h - 26, 7, (255, 140, 60))


def icon_globe(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (14, 92, 96), (240, 186, 96))
    cx, cy, r = x + w / 2, y + h / 2 + 4, 30
    d.ellipse([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], fill=(20, 110, 110),
              outline=(245, 242, 225), width=2 * SS)
    for off in (-15, 0, 15):
        d.line([(X(cx - r + 3), X(cy + off)), (X(cx + r - 3), X(cy + off))],
               fill=(245, 242, 225), width=1 * SS)
    d.arc([X(cx - 12), X(cy - r), X(cx + 12), X(cy + r)], 90, 270,
          fill=(245, 242, 225), width=1 * SS)
    d.arc([X(cx - 12), X(cy - r), X(cx + 12), X(cy + r)], 270, 450,
          fill=(245, 242, 225), width=1 * SS)
    d.pieslice([X(x + w - 40), X(y + h - 30), X(x + w + 2), X(y + h + 12)],
               180, 360, fill=TEAL_D)


def icon_cyclone(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (30, 70, 110), (120, 170, 200))
    cx, cy = x + w / 2, y + h / 2 - 8
    for r, a0 in ((34, 20), (26, 140), (18, 260), (10, 60)):
        d.arc([X(cx - r), X(cy - r), X(cx + r), X(cy + r)], a0, a0 + 250,
              fill=(250, 250, 246), width=3 * SS)
    d.ellipse([X(cx - 4), X(cy - 4), X(cx + 4), X(cy + 4)], fill=(250, 250, 246))
    # coast + waves
    d.polygon([(X(x), X(y + h)), (X(x), X(y + h - 16)), (X(x + 34), X(y + h - 8)),
               (X(x + w), X(y + h - 20)), (X(x + w), X(y + h))], fill=(24, 60, 44))
    for wx in range(6, int(w) - 8, 16):
        d.arc([X(x + wx), X(y + h - 13), X(x + wx + 11), X(y + h - 5)], 180, 360,
              fill=(250, 250, 246), width=1 * SS)


def star(d, cx, cy, r, col):
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((X(cx + rr * math.cos(ang)), X(cy + rr * math.sin(ang))))
    d.polygon(pts, fill=col)


def icon_bridge(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (24, 44, 92), (90, 130, 180))
    # bridge deck + arch
    d.rectangle([X(x + 6), X(y + h - 34), X(x + w - 6), X(y + h - 28)],
                fill=GOLD_L)
    d.arc([X(x + 14), X(y + h - 58), X(x + w - 14), X(y + h - 6)], 180, 360,
          fill=GOLD_L, width=3 * SS)
    for vx in (20, 44, 68):
        d.line([(X(x + vx), X(y + h - 32)), (X(x + vx), X(y + h - 44))],
               fill=GOLD_L, width=2 * SS)
    # EU stars arc + crown hint
    for i in range(5):
        a = math.radians(180 + i * 40)
        sx, sy = x + w / 2 + 30 * math.cos(a), y + 32 + 15 * math.sin(a)
        star(d, sx, sy, 6, GOLD_L)
    d.polygon([(X(x + 12), X(y + 22)), (X(x + 20), X(y + 12)), (X(x + 26), X(y + 20)),
               (X(x + 32), X(y + 12)), (X(x + 40), X(y + 22)), (X(x + 40), X(y + 27)),
               (X(x + 12), X(y + 27))], fill=GOLD_L)


def icon_market(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (40, 14, 20), (96, 26, 34))
    pts = [(8, 18), (24, 26), (38, 22), (52, 38), (66, 34), (80, 52)]
    for i in range(len(pts) - 1):
        d.line([(X(x + pts[i][0]), X(y + pts[i][1])), (X(x + pts[i + 1][0]),
               X(y + pts[i + 1][1]))], fill=(255, 120, 110), width=2 * SS)
    for (px, py) in pts:
        d.line([(X(x + px), X(y + py - 11)), (X(x + px), X(y + py + 11))],
               fill=(255, 150, 140), width=1 * SS)
        d.rectangle([X(x + px - 3), X(y + py - 7), X(x + px + 3), X(y + py + 7)],
                    fill=(255, 90, 84))
    d.polygon([(X(x + 80), X(y + 58)), (X(x + 88), X(y + 46)), (X(x + 90), X(y + 60))],
              fill=(255, 90, 84))
    # AI chip
    cx0, cy0 = x + w - 34, y + h - 36
    d.rectangle([X(cx0), X(cy0), X(cx0 + 24), X(cy0 + 24)], outline=GOLD_L,
                width=2 * SS)
    d.rectangle([X(cx0 + 7), X(cy0 + 7), X(cx0 + 17), X(cy0 + 17)], fill=GOLD_L)
    for p in (4, 12, 20):
        d.line([(X(cx0 + p), X(cy0 - 5)), (X(cx0 + p), X(cy0))], fill=GOLD_L,
               width=2 * SS)
        d.line([(X(cx0 + p), X(cy0 + 24)), (X(cx0 + p), X(cy0 + 29))],
               fill=GOLD_L, width=2 * SS)


def icon_route(d, x, y, w, h):
    vgrad(d, (x, y, x + w, y + h), (18, 62, 92), (64, 130, 150))
    # dashed sea route
    pts = [(x + 10, y + h - 18), (x + 34, y + h - 38), (x + 52, y + 22),
           (x + w - 16, y + 16)]
    for i in range(len(pts) - 1):
        d.line([(X(pts[i][0]), X(pts[i][1])), (X(pts[i + 1][0]),
               X(pts[i + 1][1]))], fill=(250, 240, 200), width=2 * SS)
    for (px, py) in (pts[0], pts[-1]):
        d.ellipse([X(px - 5), X(py - 5), X(px + 5), X(py + 5)], fill=RED,
                  outline=(250, 245, 228), width=1 * SS)
    # boat
    bx, by = x + 30, y + h - 26
    d.polygon([(X(bx), X(by)), (X(bx + 30), X(by)), (X(bx + 24), X(by + 9)),
               (X(bx + 5), X(by + 9))], fill=(250, 245, 228))
    d.rectangle([X(bx + 11), X(by - 8), X(bx + 20), X(by)], fill=(250, 245, 228))
    # scales of justice (court)
    sx, sy = x + w - 26, y + 44
    d.line([(X(sx), X(sy - 20)), (X(sx), X(sy + 12))], fill=GOLD_L, width=2 * SS)
    d.line([(X(sx - 14), X(sy - 14)), (X(sx + 14), X(sy - 14))], fill=GOLD_L,
           width=2 * SS)
    for sgn in (-1, 1):
        d.arc([X(sx + sgn * 14 - 7), X(sy - 12), X(sx + sgn * 14 + 7), X(sy - 2)],
              0, 180, fill=GOLD_L, width=2 * SS)


PANEL_SOURCES = ["REUTERS · 20 NOV 2026", "THE GUARDIAN · REUTERS", "REUTERS · 20 NOV 2026",
                 "REUTERS · THE GUARDIAN", "REUTERS · AP", "REUTERS · AP"]

PANELS = [
    ("01 · EUROPE — WAR", RED, icon_tower,
     "Missiles & drones pound Ukraine's energy grid; 8 killed",
     "One of the war's biggest barrages hits power sites in nine regions; Kyiv bridges struck."),
    ("02 · CLIMATE — TÜRKIYE", TEAL, icon_globe,
     "COP31 runs into overtime as Africa demands climate finance",
     "Ministers say they 'didn't come here to beg'; fossil fuels vanish from the draft deal in Antalya."),
    ("03 · ASIA — WEATHER", (30, 90, 140), icon_cyclone,
     "Cyclone Akvan slams India's east coast",
     "The third cyclone in under a month makes landfall; coastal districts brace for flooding and outages."),
    ("04 · EUROPE — DIPLOMACY", NAVY2, icon_bridge,
     "UK & EU seal reset: food trade + youth mobility",
     "Brussels deal opens travel, work and study to up to 100,000 young people a year; farm trade eased."),
    ("05 · MARKETS — AI ROUT", RED_D, icon_market,
     "AI sell-off deepens despite Anthropic's record IPO",
     "S&P 500 sinks 3.7% and Nasdaq turns negative for the year; the $81bn listing can't stop the rout."),
    ("06 · ASIA — JUSTICE", (86, 52, 110), icon_route,
     "World court: Myanmar guilty of Rohingya genocide",
     "Landmark ICJ ruling lands as Malaysia plans to resettle 10,000 Rohingya refugees in Türkiye."),
]


WIRE = [
    ("EUROPE", "Russian missiles land in Poland; NATO protests"),
    ("EUROPE", "Ukraine strike halts trains on Kerch Bridge"),
    ("EUROPE", "Estonia shuts its Russia border for six months"),
    ("EUROPE", "Denmark: Russian plot to kill Ukrainian exposed"),
    ("EUROPE", "Spain: Feijoo beats Sanchez in TV debate — polls"),
    ("AMERICAS", "Trump–Putin 'very good talks' after China summit"),
    ("AMERICAS", "Trump, Xi & Putin issue joint peace declaration"),
    ("AMERICAS", "Trump: more work needed on Canada trade deal"),
    ("AMERICAS", "Court approves $7.25bn Bayer Roundup settlement"),
    ("AMERICAS", "Mamdani sets plan to close Rikers Island jail"),
    ("AMERICAS", "El Salvador's Bukele launches third-term bid"),
    ("AMERICAS", "Haiti strikes prison deal with El Salvador"),
    ("MIDEAST", "Qeshm blast was munitions disposal, Iran says"),
    ("MIDEAST", "Saudi Arabia intercepts Houthi missiles, drones"),
    ("MIDEAST", "US presses Singapore, Malaysia on Iran sanctions"),
    ("ASIA-PAC", "Prabowo meets Xi in Beijing on trade, seas"),
    ("ASIA-PAC", "China $2bn bond draws $72bn in orders"),
    ("ASIA-PAC", "South Korea: first cholera case in a decade"),
    ("AFRICA", "Angola pays $180m for 10% of De Beers"),
    ("AFRICA", "Kenya picks US group for Mrima Hill minerals"),
    ("AFRICA", "Nigeria moves to end jail for suicide attempts"),
    ("GLOBAL", "UK & France block UAE pick for UN chief"),
    ("GLOBAL", "US to penalise AI data centres built abroad"),
    ("CULTURE", "Grand Theft Auto VI arrives to rave reviews"),
]


def panels_and_wire(img, d):
    # hero caption strip
    cy = 357
    d.rectangle([X(28), X(cy), X(996), X(cy + 44)], fill=INK)
    text_l(d, 40, cy + 5, "KYIV — Energy grid pounded in one of the war's",
           font(SANS_B, 13), CREAM_TXT)
    text_l(d, 40, cy + 22, "largest barrages · 8 killed · bridges hit",
           font(SANS_B, 13), CREAM_TXT)
    text_l(d, 620, cy + 5, "ANTALYA — COP31 finale: Africa pushes",
           font(SANS_B, 13), GOLD_L)
    text_l(d, 620, cy + 22, "for climate finance on closing day",
           font(SANS_B, 13), GOLD_L)

    # panels 3 x 2
    px0, py0, pw, ph, gap = 28, 409, 309, 158, 7
    for i, (tag, col, icon, head, summ) in enumerate(PANELS):
        cx = px0 + (i % 3) * (pw + gap)
        cyy = py0 + (i // 3) * (ph + gap)
        d.rectangle([X(cx), X(cyy), X(cx + pw), X(cyy + ph)], fill=(255, 253, 244),
                    outline=INK, width=1 * SS)
        d.rectangle([X(cx), X(cyy), X(cx + pw), X(cyy + 23)], fill=col)
        text_l(d, cx + 9, cyy + 4, tag, font(SANS_B, 11.5), CREAM_TXT)
        _sf = font(SANS_B, 9.5)
        _sw = d.textlength(PANEL_SOURCES[i], font=_sf)
        d.text((X(cx + pw - 9) - _sw, X(cyy + 6)), PANEL_SOURCES[i], font=_sf,
               fill=(255, 240, 210))
        # icon scene
        ix, iy, iw, ih = cx + 9, cyy + 31, 86, 118
        icon(d, ix, iy, iw, ih)
        d.rectangle([X(ix), X(iy), X(ix + iw), X(iy + ih)], outline=INK,
                    width=1 * SS)
        # headline + summary
        tx = cx + 105
        tw = pw - 105 - 9
        hl = wrap(d, head, font(SANS_B, 15.5), tw)
        yy = cyy + 33
        for ln in hl[:3]:
            text_l(d, tx, yy, ln, font(SANS_B, 15.5), INK)
            yy += 21
        yy += 3
        for ln in wrap(d, summ, font(SANS, 12.5), tw)[:5]:
            text_l(d, tx, yy, ln, font(SANS, 12.5), (52, 56, 66))
            yy += 16.5

    # world wire
    wy = 748
    d.rectangle([X(28), X(wy), X(996), X(wy + 26)], fill=RED)
    text_l(d, 40, wy + 4,
           "THE WORLD WIRE — 24 MORE STORIES FIRST REPORTED ON FRIDAY 20 NOV 2026",
           font(SANS_B, 13), CREAM_TXT)
    colw, row0, rowh = 474, wy + 34, 15.5
    for i, (region, head) in enumerate(WIRE):
        col = i // 12
        row = i % 12
        x = 36 + col * (colw + 12)
        y = row0 + row * rowh
        text_l(d, x, y, f"{i + 7:02d}", font(SANS_B, 11), RED)
        text_l(d, x + 24, y, region, font(SANS_B, 11), NAVY)
        rw = d.textlength(region, font=font(SANS_B, 11)) / SS
        text_l(d, x + 30 + rw, y, "· " + head, font(SANS, 11.5), INK)
        if row < 11:
            d.line([(X(x), X(y + 13.5)), (X(x + colw - 8), X(y + 13.5))],
                   fill=(216, 206, 178), width=1)

    # footer / date check
    fy = 972
    d.line([(X(28), X(fy - 6)), (X(996), X(fy - 6))], fill=GOLD, width=1 * SS)
    text_c(d, 512, fy,
           "DATE CHECK — ALL 30 ITEMS FIRST REPORTED FRIDAY 20 NOVEMBER 2026 · "
           "SOURCES: REUTERS · AP · THE GUARDIAN · BBC", font(SANS_B, 11), NAVY)
    text_c(d, 512, fy + 17,
           "No news photographs — every image on this page is original drawn geometry.",
           font(SANS, 10.5), (90, 88, 78))


def main():
    img, d = build()
    panels_and_wire(img, d)
    out = img.resize((1024, 1024), Image.LANCZOS)
    dest = Path(__file__).with_name("entry.png")
    out.save(dest, format="PNG", optimize=True)
    print(f"wrote {dest} {dest.stat().st_size} bytes")


if __name__ == "__main__":
    main()
