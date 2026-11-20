"""Render the original editorial poster with Pillow and Liberation fonts."""
from functools import lru_cache
from pathlib import Path
import os

from PIL import Image, ImageDraw, ImageFont

SCALE = 2
INK, PAPER, MUTED = '#112b38', '#f7f4e9', '#435765'
FONT_DIR = Path(os.environ.get('LIBERATION_FONTS', '/usr/share/fonts/truetype/liberation'))
canvas = Image.new('RGB', (1024 * SCALE, 1024 * SCALE), PAPER)
draw = ImageDraw.Draw(canvas)


def pixels(values):
    return tuple(round(value * SCALE) for value in values)


@lru_cache
def font(size, serif=False, bold=True):
    family = 'Serif' if serif else 'Sans'
    style = 'Bold' if bold else 'Regular'
    return ImageFont.truetype(str(FONT_DIR / f'Liberation{family}-{style}.ttf'), size * SCALE)


def text(x, y, words, size, color=INK, *, serif=False, bold=True, end=1000):
    face = font(size, serif, bold)
    width = draw.textlength(words, font=face) / SCALE
    if x + width > end:
        raise ValueError(f'Text overflows by {x + width - end:.1f}px: {words}')
    draw.text(pixels((x, y)), words, font=face, fill=color, anchor='lt')


def box(x, y, w, h, color):
    draw.rectangle(pixels((x, y, x + w - 0.5, y + h - 0.5)), fill=color)


def line(points, color, width=2):
    draw.line([pixels(point) for point in points], fill=color, width=width * SCALE, joint='curve')


def poly(points, color):
    draw.polygon([pixels(point) for point in points], fill=color)


def ellipse(x, y, w, h, color):
    draw.ellipse(pixels((x, y, x + w, y + h)), fill=color)


def lead_art():
    box(662, 154, 326, 280, '#204559')
    # A narrow dateline rail gives the lead illustration a clear editorial frame.
    box(662, 154, 5, 240, '#ecb559')
    box(670, 154, 318, 4, '#5c9ed0')
    ellipse(742, 184, 156, 156, '#ecb559')
    for points in [[(662, 266), (714, 292), (768, 304), (825, 288), (888, 314), (943, 301), (988, 318)],
                   [(662, 282), (714, 308), (768, 320), (825, 306), (888, 331), (943, 317), (988, 331)]]:
        line(points, '#366276', 2)
    poly([(662, 344), (728, 315), (756, 334), (809, 295), (876, 327), (928, 309), (988, 341),
          (988, 434), (662, 434)], '#163849')
    for x, y, height in [(679, 351, 43), (717, 331, 63), (760, 361, 33), (864, 347, 47), (934, 331, 63)]:
        box(x, y, 26, height, '#0e2b3a')
        for offset in range(8, height - 8, 12):
            if (offset + x) % 3:
                box(x + 7, y + offset, 4, 5, '#cfaa65')
                box(x + 16, y + offset, 4, 5, '#cfaa65')
    for x, y, scale in [(837, 222, 1), (943, 260, .62)]:
        def point(dx, dy):
            return x + dx * scale, y + dy * scale
        for a, b in [((-47, 171), (0, 0)), ((47, 171), (0, 0)), ((-42, 115), (42, 115)),
                     ((-31, 66), (31, 66)), ((-35, 115), (25, 66)), ((35, 115), (-25, 66)),
                     ((-46, 170), (35, 115)), ((46, 170), (-35, 115))]:
            line([point(*a), point(*b)], '#0b2835', 4)
    box(662, 394, 326, 40, '#0e2b3a')
    box(662, 394, 5, 40, '#ecb559')
    box(682, 403, 27, 10, '#5c9ed0')
    box(682, 413, 27, 10, '#ecb559')
    text(724, 405, 'UKRAINE / POWER GRID', 20, '#fcdb93', end=982)


def icon(kind, x, y, bg, mark):
    box(x, y, 84, 84, bg)

    def p(a, b):
        return x + a, y + b

    if kind == 'climate':
        ellipse(x + 24, y + 13, 38, 38, mark)
        for row in (49, 60, 71):
            line([p(9, row), p(26, row - 5), p(43, row), p(60, row - 5), p(75, row)], PAPER, 3)
    elif kind == 'cyclone':
        for angle in (20, 200):
            draw.arc(pixels((x + 12, y + 12, x + 72, y + 72)), angle, angle + 135, fill=PAPER, width=5 * SCALE)
        ellipse(x + 33, y + 33, 18, 18, mark)
        line([p(13, 49), p(21, 61), p(31, 64)], PAPER, 4)
        line([p(71, 35), p(64, 23), p(53, 20)], PAPER, 4)
    elif kind == 'markets':
        for i, height in enumerate((45, 33, 28, 15)):
            box(x + 16 + i * 15, y + 68 - height, 8, height, PAPER)
        line([p(13, 15), p(35, 27), p(49, 24), p(72, 45)], mark, 5)
        poly([p(71, 47), p(58, 46), p(72, 34)], mark)
    elif kind == 'trade':
        for offset, flip in [(26, False), (52, True)]:
            a, b = (18, 66) if not flip else (66, 18)
            line([p(a, offset), p(b, offset)], PAPER, 5)
            tail = b + (10 if flip else -10)
            line([p(tail, offset - 9), p(b, offset), p(tail, offset + 9)], mark, 5)
    else:
        for a, b in [(20, 42), (38, 32), (56, 42)]:
            ellipse(x + a, y + b - 13, 10, 10, mark)
            box(x + a - 2, y + b, 14, 16, PAPER)
        line([p(14, 66), p(70, 66)], PAPER, 3)


def card(x, y, kind, tag, headline, detail, bg, accent):
    edge = x + 466
    box(x, y, 466, 4, bg)
    box(x, y + 4, 52, 2, accent)
    icon(kind, x, y + 15, bg, accent)
    text(x + 102, y + 16, tag, 21, bg, end=edge)
    for i, words in enumerate(headline):
        text(x + 102, y + 44 + 38 * i, words, 37, serif=True, end=edge)
    for i, words in enumerate(detail):
        text(x + 102, y + 121 + 30 * i, words, 26, MUTED, bold=False, end=edge)
    box(edge - 30, y + 166, 30, 2, bg)


def compose():
    box(36, 27, 952, 6, INK)
    text(36, 47, 'The World Brief', 73, serif=True)
    text(652, 51, 'FRIDAY  ·  EDITION 47', 24, '#9d382a')
    text(652, 83, '20 NOVEMBER 2026', 34, end=989)
    box(36, 130, 952, 3, INK)
    box(36, 137, 952, 2, '#ecb559')
    text(36, 141, 'SIX STORIES  /  ONE WORLD', 17, MUTED, end=300)
    box(36, 154, 626, 280, INK)
    text(60, 174, '01  /  EUROPE · WAR', 25, '#fcdb93')
    text(60, 214, 'Russia strikes', 59, PAPER, serif=True)
    text(60, 273, 'Ukraine’s power grid', 57, PAPER, serif=True, end=646)
    text(60, 350, 'At least eight killed as missiles and', 29, PAPER, bold=False)
    text(60, 383, 'drones hit energy infrastructure.', 29, PAPER, bold=False)
    lead_art()
    card(36, 457, 'climate', '02  /  GLOBAL CLIMATE', ('COP31 talks stall', 'over climate finance'),
         ('African ministers urge', 'funding in Türkiye.'), '#21594f', '#f3bd58')
    card(522, 457, 'cyclone', '03  /  SOUTH ASIA', ('Cyclone Akvan', 'hits eastern India'),
         ('Landfall brings heavy rain.', 'Third storm in a month.'), '#215776', '#f2b558')
    card(36, 641, 'trade', '04  /  EUROPE · TRADE', ('UK and EU agree', 'post-Brexit reset'),
         ('Deals cover food trade', 'and youth mobility.'), '#694963', '#f3bd58')
    card(522, 641, 'markets', '05  /  GLOBAL MARKETS', ('AI selloff drags', 'world stocks lower'),
         ('Anthropic’s IPO fails', 'to stem tech rout.'), '#8b3c35', '#f5bc52')
    box(36, 825, 952, 105, '#f0e8d5')
    box(36, 825, 952, 4, '#633a2e')
    box(36, 829, 6, 101, '#ecb559')
    icon('people', 36, 843, '#633a2e', '#f3bd58')
    text(139, 842, '06  /  DISPLACEMENT', 21, '#633a2e')
    text(139, 872, 'Malaysia plans to resettle 10,000 Rohingya', 39, serif=True)
    text(139, 921, 'The refugees would be relocated to Türkiye.', 26, MUTED, bold=False)
    box(36, 967, 952, 2, INK)
    text(36, 982, 'REPORTING  /  REUTERS · THE GUARDIAN', 20, MUTED)
    text(884, 982, 'WB / 47', 20, MUTED, end=988)


if __name__ == '__main__':
    compose()
    poster = canvas.resize((1024, 1024), Image.Resampling.LANCZOS)
    # Keep edge antialiasing without adding the grain of a dithered palette.
    indexed = poster.quantize(192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    indexed.save(Path(__file__).with_name('entry.png'), optimize=True)
