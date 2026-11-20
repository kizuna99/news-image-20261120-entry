"""Render a compact, high-contrast world-news front page."""
from functools import lru_cache
from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont


S = 2
W = H = 1024
PAPER = '#f6f1e7'
INK = '#102b39'
SLATE = '#536673'
GOLD = '#f0b84d'
RED = '#b44939'
FONT_DIR = Path(os.environ.get('LIBERATION_FONTS', '/usr/share/fonts/truetype/liberation'))

canvas = Image.new('RGB', (W * S, H * S), PAPER)
draw = ImageDraw.Draw(canvas)


def xy(value):
    return int(round(value * S))


def rect(x, y, w, h, fill, radius=0, outline=None, width=1):
    coords = (xy(x), xy(y), xy(x + w), xy(y + h))
    if radius:
        draw.rounded_rectangle(coords, radius=xy(radius), fill=fill, outline=outline,
                               width=xy(width) if outline else 1)
    else:
        draw.rectangle(coords, fill=fill, outline=outline,
                       width=xy(width) if outline else 1)


def segment(points, fill, width=2):
    draw.line([(xy(x), xy(y)) for x, y in points], fill=fill, width=xy(width), joint='curve')


def polygon(points, fill):
    draw.polygon([(xy(x), xy(y)) for x, y in points], fill=fill)


def circle(x, y, r, fill, outline=None, width=1):
    draw.ellipse((xy(x - r), xy(y - r), xy(x + r), xy(y + r)), fill=fill,
                 outline=outline, width=xy(width) if outline else 1)


@lru_cache(maxsize=None)
def face(size, serif=False, bold=True):
    family = 'Serif' if serif else 'Sans'
    weight = 'Bold' if bold else 'Regular'
    return ImageFont.truetype(str(FONT_DIR / f'Liberation{family}-{weight}.ttf'), xy(size))


def write(x, y, value, size, fill=INK, *, serif=False, bold=True, anchor='lt'):
    draw.text((xy(x), xy(y)), value, font=face(size, serif, bold), fill=fill, anchor=anchor)


def lead_art():
    """A literal power-grid scene: towers, a dark city, and incoming strike marks."""
    x, y, w, h = 638, 164, 350, 334
    rect(x, y, w, h, '#1d5068')
    rect(x, y, 7, h, GOLD)
    # Dawn disk and distant horizon.
    circle(848, 248, 80, '#f4bd58')
    polygon([(638, 405), (691, 365), (729, 379), (775, 345), (816, 373),
             (858, 352), (905, 374), (948, 346), (988, 370), (988, 498), (638, 498)], '#123748')
    for bx, by, bw, bh in [(660, 396, 31, 102), (700, 371, 25, 127),
                           (742, 412, 36, 86), (900, 390, 30, 108), (946, 369, 24, 129)]:
        rect(bx, by, bw, bh, '#0c2b3a')
        for yy in range(by + 16, by + bh - 8, 18):
            rect(bx + 7, yy, 5, 7, '#f0b84d')
            if bw > 27:
                rect(bx + 20, yy, 5, 7, '#f0b84d')
    # Transmission towers and cables.
    for tx, scale in [(792, 1.0), (949, 0.62)]:
        base = 489
        top = base - 185 * scale
        segment([(tx, top), (tx - 54 * scale, base)], '#071f2c', 5)
        segment([(tx, top), (tx + 54 * scale, base)], '#071f2c', 5)
        segment([(tx - 38 * scale, base - 66 * scale), (tx + 38 * scale, base - 66 * scale)], '#071f2c', 4)
        segment([(tx - 48 * scale, base - 113 * scale), (tx + 48 * scale, base - 113 * scale)], '#071f2c', 4)
        segment([(tx - 22 * scale, base - 66 * scale), (tx + 22 * scale, base - 113 * scale)], '#071f2c', 3)
        segment([(tx + 22 * scale, base - 66 * scale), (tx - 22 * scale, base - 113 * scale)], '#071f2c', 3)
    segment([(638, 323), (723, 348), (792, 329), (949, 355), (988, 346)], '#4e8295', 3)
    segment([(638, 345), (712, 370), (792, 351), (949, 377), (988, 368)], '#4e8295', 2)
    # Three small descending strike markers make the event unmistakable.
    for px, py in [(690, 196), (744, 181), (935, 214)]:
        segment([(px, py), (px - 18, py + 29)], '#f7d98b', 4)
        polygon([(px - 18, py + 29), (px - 29, py + 30), (px - 19, py + 40)], '#f7d98b')
    rect(638, 458, w, 40, '#0a2836')
    write(661, 468, 'UKRAINE  /  POWER GRID', 20, '#f8d88c')


def icon(kind, x, y, size, bg, accent):
    rect(x, y, size, size, bg, radius=4)
    mid = x + size / 2
    if kind == 'climate':
        circle(mid, y + 25, 17, accent)
        for yy in (48, 59, 70):
            segment([(x + 9, y + yy), (x + 28, y + yy - 6), (x + 46, y + yy),
                     (x + 65, y + yy - 6), (x + 75, y + yy)], PAPER, 3)
    elif kind == 'cyclone':
        circle(mid, y + size / 2, 8, accent)
        draw.arc((xy(x + 12), xy(y + 12), xy(x + size - 12), xy(y + size - 12)), 205, 348,
                 fill=PAPER, width=xy(5))
        draw.arc((xy(x + 19), xy(y + 19), xy(x + size - 5), xy(y + size - 5)), 25, 168,
                 fill=PAPER, width=xy(5))
        segment([(x + 18, y + 64), (x + 27, y + 73), (x + 38, y + 73)], PAPER, 4)
    elif kind == 'trade':
        segment([(x + 14, y + 30), (x + 65, y + 30)], PAPER, 5)
        segment([(x + 65, y + 30), (x + 55, y + 21), (x + 65, y + 30), (x + 55, y + 39)], accent, 5)
        segment([(x + 70, y + 58), (x + 19, y + 58)], PAPER, 5)
        segment([(x + 19, y + 58), (x + 29, y + 49), (x + 19, y + 58), (x + 29, y + 67)], accent, 5)
    elif kind == 'markets':
        for i, height in enumerate((41, 31, 22, 13)):
            rect(x + 15 + i * 15, y + 68 - height, 9, height, PAPER)
        segment([(x + 11, y + 17), (x + 32, y + 28), (x + 46, y + 25), (x + 74, y + 48)], accent, 5)
        polygon([(x + 75, y + 48), (x + 60, y + 46), (x + 72, y + 35)], accent)
    else:
        # People / resettlement.
        for px, py, r in [(22, 30, 6), (43, 21, 7), (64, 34, 6)]:
            circle(x + px, y + py, r, accent)
            rect(x + px - 8, y + py + 7, 16, 15, PAPER)
        segment([(x + 12, y + 66), (x + 72, y + 66)], PAPER, 3)


def card(x, y, width, height, number, kind, section, headline, detail, bg, accent):
    rect(x, y, width, 5, bg)
    rect(x, y + 5, 50, 3, accent)
    icon(kind, x, y + 20, 76, bg, accent)
    write(x + 94, y + 21, f'{number}  /  {section}', 18, bg)
    for i, line in enumerate(headline):
        write(x + 94, y + 52 + i * 34, line, 30, INK, serif=True)
    for i, line in enumerate(detail):
        write(x + 94, y + 122 + i * 23, line, 20, SLATE, bold=False)
    rect(x + width - 30, y + height - 8, 30, 2, bg)


def compose():
    # Masthead: the date and edition stay visible even at a small preview size.
    rect(36, 27, 952, 7, INK)
    write(36, 49, 'WORLD', 68, INK, serif=True)
    write(320, 49, 'BRIEF', 68, RED, serif=True)
    write(653, 55, 'FRIDAY  /  GLOBAL EDITION', 20, RED)
    write(653, 83, '20 NOVEMBER 2026', 31, INK)
    rect(36, 130, 952, 3, INK)
    rect(36, 137, 952, 3, GOLD)
    write(36, 148, 'THE DAY IN SIX STORIES', 16, SLATE)
    write(824, 148, 'GLOBAL  /  20.11.26', 16, SLATE)

    # Lead story, deliberately short and literal.
    rect(36, 164, 952, 334, INK)
    write(62, 182, '01  /  EUROPE  ·  WAR', 22, '#f8d88c')
    write(62, 225, 'RUSSIA STRIKES', 54, PAPER, serif=True)
    write(62, 286, "UKRAINE'S POWER GRID", 44, PAPER, serif=True)
    write(62, 357, 'Missiles and drones hit energy infrastructure.', 24, PAPER, bold=False)
    write(62, 388, 'At least eight people were killed.', 24, PAPER, bold=False)
    rect(62, 445, 510, 2, '#4e8295')
    write(62, 456, 'UKRAINE  /  ENERGY INFRASTRUCTURE', 16, '#b8d0d5')
    lead_art()

    # Five highly distinct, region-labelled briefs.
    card(36, 524, 466, 167, '02', 'climate', 'GLOBAL CLIMATE',
         ('Africa presses for', 'climate finance'),
         ('COP31 reaches its scheduled', 'final day in Türkiye.'), '#216052', GOLD)
    card(522, 524, 466, 167, '03', 'cyclone', 'SOUTH ASIA',
         ('Cyclone Akvan', 'hits eastern India'),
         ('Landfall brings heavy rain.', 'Third cyclone in a month.'), '#24617c', '#f4c267')
    card(36, 711, 466, 167, '04', 'trade', 'EUROPE  ·  TRADE',
         ('UK and EU agree', 'new reset deals'),
         ('Food trade and youth', 'mobility are covered.'), '#704d6a', '#f5c763')
    card(522, 711, 466, 167, '05', 'markets', 'GLOBAL MARKETS',
         ('AI sell-off drags', 'world stocks lower'),
         ("Anthropic's listing fails", 'to reverse the tech rout.'), '#a04136', '#f5c763')

    # A wide closing story creates a strong visual footer and preserves the number.
    rect(36, 898, 952, 76, '#eee3ce')
    rect(36, 898, 952, 5, '#704433')
    icon('people', 50, 913, 50, '#704433', GOLD)
    write(150, 909, '06  /  DISPLACEMENT', 18, '#704433')
    write(150, 936, 'Malaysia plans to resettle 10,000 Rohingya in Türkiye.', 26, INK, serif=True)

    rect(36, 993, 952, 3, INK)


if __name__ == '__main__':
    compose()
    poster = canvas.resize((W, H), Image.Resampling.LANCZOS)
    # Indexed colour keeps the poster crisp and well below the 1 MiB gate.
    poster.quantize(192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
        Path(__file__).with_name('entry.png'), optimize=True)
