# news-image-01 entry (Python 3.13, standard library only).
#
# Draws one 1024x1024 PNG that sums up the world news of Friday
# 13 November 2026: a newspaper front page with a hero panel and four
# illustrated tiles, plus a footer ticker with two more stories.
# Everything is drawn in code -- flat vector shapes and a built-in
# 5x7 bitmap font -- so the program is deterministic and needs no
# network, no assets and no installed packages.
#
# Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# Writes: $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png)

import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024

# --- palette (newsprint) ---
CREAM = (246, 241, 227)
PAPER = (250, 247, 236)
NAVY = (22, 35, 58)
INK = (26, 34, 48)
RED = (179, 39, 30)
BLUE = (43, 93, 138)
GOLD = (201, 162, 39)
SKY = (223, 230, 238)
SEA = (96, 122, 148)
DARKSEA = (58, 82, 108)
WOOD = (122, 84, 52)
WOOD_L = (150, 108, 70)
GREEN = (46, 125, 70)
GREEN_L = (92, 168, 110)
GREY = (140, 148, 158)
DARKGREY = (74, 82, 94)
WHITE = (255, 255, 255)
BLACK = (20, 20, 24)
UA_BLUE = (0, 91, 172)
UA_YELLOW = (255, 213, 0)
EU_BLUE = (0, 51, 153)
ORANGE = (214, 110, 30)
SMOKE = (120, 124, 130)


class Canvas:
    """An RGB pixel buffer with simple flat drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5) if abs(yy - cy) <= r else -1
            if dx >= 0:
                self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            d = 1 - ((yy - cy) / ry) ** 2
            if d < 0:
                continue
            dx = int(rx * (d ** 0.5))
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Filled polygon, scanline fill."""
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)


# --- 5x7 bitmap font (uppercase, digits, punctuation) ---
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    '$': ("00100", "01111", "10101", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "00100", "11111", "00100", "10101", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    s = s.upper()
    for ci, ch in enumerate(s):
        g = FONT.get(ch, FONT[' '])
        ox = x + ci * 6 * scale
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == '1':
                    cv.rect(ox + c * scale, y + r * scale, scale, scale, color)


def draw_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    """Greedy word wrap into lines that fit max_w pixels."""
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if text_w(t, scale) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# --- scene drawing ---

def panel(cv, x, y, w, h, border=NAVY, bw=3):
    cv.rect(x, y, w, h, border)
    cv.rect(x + bw, y + bw, w - 2 * bw, h - 2 * bw, PAPER)


def caption_bar(cv, x, y, w, h, title, sub, tscale=3, sscale=2):
    cv.rect(x, y, w, h, NAVY)
    ty = y + 12
    for i, ln in enumerate(wrap(title, tscale, w - 24)):
        draw_text(cv, x + 12, ty + i * (7 * tscale + 4), ln, tscale, CREAM)
    sy = ty + len(wrap(title, tscale, w - 24)) * (7 * tscale + 4) + 4
    for i, ln in enumerate(wrap(sub, sscale, w - 24)):
        draw_text(cv, x + 12, sy + i * (7 * sscale + 3), ln, sscale, (200, 208, 220))


def draw_header(cv):
    cv.rect(0, 0, W, 116, NAVY)
    draw_centered(cv, W // 2, 16, "FRIDAY 13 NOVEMBER 2026", 6, CREAM)
    cv.rect(48, 76, W - 96, 4, RED)
    draw_centered(cv, W // 2, 88, "SEVEN STORIES THAT DEFINED THE DAY", 2, (200, 208, 220))


def draw_hero(cv):
    # Senate hearing: two empty witness chairs, jacket, nameplates.
    x, y, w, h = 16, 132, 992, 272
    panel(cv, x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    cv.rect(ix, iy, iw, ih, SKY)
    # back wall columns
    for cx in range(ix + 40, ix + iw, 160):
        cv.rect(cx, iy, 26, ih - 96, (178, 190, 206))
        cv.rect(cx, iy, 26, 10, (150, 164, 184))
    # US flag, left
    fx, fy, fw, fh = ix + 28, iy + 18, 120, 64
    for i in range(7):
        cv.rect(fx, fy + i * 9, fw, 9, RED if i % 2 == 0 else WHITE)
    cv.rect(fx, fy, 52, 36, BLUE)
    for r in range(3):
        for c in range(4):
            cv.circle(fx + 8 + c * 12, fy + 7 + r * 11, 2, WHITE)
    # flag pole
    cv.rect(fx + fw + 4, fy - 8, 4, fh + 16, WOOD)
    # witness desk: its bottom edge is the top of the caption bar
    dy = iy + ih - 78 - 96
    cv.rect(ix, dy, iw, 96, WOOD)
    cv.rect(ix, dy, iw, 10, WOOD_L)
    cv.rect(ix, dy + 40, iw, 4, (90, 60, 36))
    # two empty chairs behind the desk
    for cx in (ix + 300, ix + 560):
        cv.rect(cx, dy - 84, 130, 84, DARKGREY)          # chair back
        cv.rect(cx + 8, dy - 76, 114, 68, GREY)
        cv.rect(cx - 12, dy - 84, 14, 84, DARKGREY)      # arm
        cv.rect(cx + 128, dy - 84, 14, 84, DARKGREY)
    # leather jacket draped over the left chair
    cv.poly([(ix + 300, dy - 84), (ix + 430, dy - 84), (ix + 420, dy - 12),
             (ix + 380, dy - 30), (ix + 340, dy - 12), (ix + 310, dy - 24)], BLACK)
    cv.line(ix + 330, dy - 78, ix + 330, dy - 18, (60, 60, 66), 2)
    # microphones on the desk
    for mx in (ix + 330, ix + 360, ix + 620, ix + 650):
        cv.line(mx, dy + 8, mx, dy - 26, BLACK, 3)
        cv.circle(mx, dy - 30, 7, BLACK)
    # nameplates on the desk front, clear of the caption bar
    for nx, nm in ((ix + 296, "HUANG"), (ix + 556, "LUTNICK")):
        cv.rect(nx, dy + 14, 138, 34, WHITE)
        cv.rect(nx, dy + 14, 138, 3, NAVY)
        cv.rect(nx, dy + 45, 138, 3, NAVY)
        draw_centered(cv, nx + 69, dy + 22, nm, 2, NAVY)
    # gavel block, right
    cv.rect(ix + iw - 120, dy + 52, 84, 30, WOOD_L)
    cv.rect(ix + iw - 104, dy + 20, 52, 22, WOOD)
    caption_bar(cv, x, y + h - 78, w, 78,
                "SENATE SUMMONS HUANG & LUTNICK",
                "EX-NVIDIA CHIEF AND COMMERCE SECRETARY ORDERED TO TESTIFY",
                tscale=4, sscale=2)


def draw_ukraine(cv, x, y, w, h):
    # Round table with Ukrainian, US and EU flags; three chairs.
    panel(cv, x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    cv.rect(ix, iy, iw, 148, (214, 226, 238))
    # wall + window
    cv.rect(ix + 30, iy + 14, 90, 60, (168, 196, 222))
    cv.rect(ix + 30, iy + 14, 90, 60, SKY)
    cv.line(ix + 75, iy + 14, ix + 75, iy + 74, WHITE, 3)
    cv.line(ix + 30, iy + 44, ix + 120, iy + 44, WHITE, 3)
    # flags on poles behind the table
    def flag(fx, fy, kind):
        cv.rect(fx, fy, 64, 40, WHITE)
        if kind == 'ua':
            cv.rect(fx, fy, 64, 20, UA_BLUE)
            cv.rect(fx, fy + 20, 64, 20, UA_YELLOW)
        elif kind == 'us':
            for i in range(5):
                cv.rect(fx, fy + i * 8, 64, 8, RED if i % 2 == 0 else WHITE)
            cv.rect(fx, fy, 28, 20, BLUE)
        else:
            cv.rect(fx, fy, 64, 40, EU_BLUE)
            for a in range(8):
                import math
                cv.circle(int(fx + 32 + 12 * math.cos(a * 0.785)),
                          int(fy + 20 + 12 * math.sin(a * 0.785)), 2, GOLD)
        cv.rect(fx + 30, fy + 40, 4, 34, WOOD)
    flag(ix + 60, iy + 20, 'ua')
    flag(ix + iw // 2 - 32, iy + 12, 'us')
    flag(ix + iw - 124, iy + 20, 'eu')
    # round table
    cv.ellipse(ix + iw // 2, iy + 128, 190, 34, WOOD)
    cv.ellipse(ix + iw // 2, iy + 122, 190, 34, WOOD_L)
    cv.rect(ix + iw // 2 - 70, iy + 128, 140, 20, WOOD)
    # papers on the table
    cv.rect(ix + iw // 2 - 90, iy + 112, 54, 18, WHITE)
    cv.rect(ix + iw // 2 + 40, iy + 112, 54, 18, WHITE)
    # chairs
    for cx in (ix + 40, ix + iw - 110):
        cv.rect(cx, iy + 96, 70, 52, DARKGREY)
    caption_bar(cv, x, y + 148, w, h - 148,
                "EUROPE JOINS UKRAINE TALKS",
                "US ENVOYS BRING EUROPE INTO TALKS AFTER PUTIN MEETING")


def draw_warship(cv, x, y, w, h):
    # Grey sea, warship with smoke, drone above.
    panel(cv, x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    cv.rect(ix, iy, iw, 148, (196, 206, 216))
    cv.circle(ix + 64, iy + 34, 26, (240, 236, 214))  # cold sun, left of the drone
    # sea
    cv.rect(ix, iy + 92, iw, 56, SEA)
    cv.rect(ix, iy + 92, iw, 4, DARKSEA)
    for sx in range(ix + 20, ix + iw - 40, 70):
        cv.line(sx, iy + 118, sx + 34, iy + 118, (180, 200, 218), 3)
        cv.line(sx + 10, iy + 136, sx + 44, iy + 136, (180, 200, 218), 3)
    # warship
    hx, hy = ix + 120, iy + 78
    cv.poly([(hx, hy + 22), (hx + 240, hy + 22), (hx + 210, hy + 44),
             (hx + 20, hy + 44)], DARKGREY)
    cv.rect(hx + 60, hy - 6, 90, 28, GREY)
    cv.rect(hx + 170, hy - 6, 26, 28, GREY)
    cv.line(hx + 90, hy - 6, hx + 90, hy - 34, DARKGREY, 4)
    cv.line(hx + 200, hy - 6, hx + 200, hy - 26, DARKGREY, 4)
    # smoke
    for i, (sx, sy, r) in enumerate([(hx + 96, hy - 48, 16), (hx + 112, hy - 66, 20),
                                     (hx + 132, hy - 84, 24), (hx + 156, hy - 100, 18)]):
        cv.circle(sx, sy, r, SMOKE)
    # fire flash on the deck
    cv.poly([(hx + 190, hy + 22), (hx + 206, hy - 2), (hx + 216, hy + 22)], ORANGE)
    cv.poly([(hx + 198, hy + 22), (hx + 206, hy + 6), (hx + 212, hy + 22)], GOLD)
    # drone
    cv.circle(ix + iw - 70, iy + 26, 5, BLACK)
    cv.line(ix + iw - 84, iy + 26, ix + iw - 56, iy + 26, BLACK, 2)
    cv.line(ix + iw - 70, iy + 40, ix + iw - 58, iy + 52, BLACK, 2)
    caption_bar(cv, x, y + 148, w, h - 148,
                "DRONE HITS RUSSIAN WARSHIP",
                "UKRAINIAN DRONE STRIKES WARSHIP IN THE GULF OF FINLAND")


def draw_iran(cv, x, y, w, h):
    # Desert coast, radar dome, missile streak, tanker on the sea.
    panel(cv, x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    cv.rect(ix, iy, iw, 148, (238, 214, 170))  # desert sky
    cv.circle(ix + 70, iy + 30, 22, (244, 226, 170))
    # sea band
    cv.rect(ix, iy + 96, iw, 52, SEA)
    cv.rect(ix, iy + 96, iw, 4, DARKSEA)
    # tanker
    cv.rect(ix + 300, iy + 108, 130, 22, DARKGREY)
    cv.rect(ix + 330, iy + 92, 34, 16, GREY)
    cv.line(ix + 340, iy + 92, ix + 340, iy + 74, DARKGREY, 3)
    # radar dome on the coast
    bx, by = ix + 70, iy + 96
    cv.rect(bx, by - 34, 90, 34, (120, 128, 138))
    cv.ellipse(bx + 45, by - 34, 45, 34, (200, 206, 212))
    cv.line(bx + 45, by - 68, bx + 45, by - 34, DARKGREY, 3)
    cv.circle(bx + 45, by - 70, 4, RED)
    # missile streak across the sky
    cv.line(ix + iw - 40, iy + 8, ix + 200, iy + 78, ORANGE, 5)
    cv.line(ix + iw - 40, iy + 8, ix + 240, iy + 66, GOLD, 3)
    cv.circle(ix + iw - 40, iy + 8, 7, RED)
    caption_bar(cv, x, y + 148, w, h - 148,
                "IRAN SAYS IT HIT US RADAR",
                "TEHRAN CLAIMS BAHRAIN STRIKE; TANKERS HIT IN HORMUZ")


def draw_fbi(cv, x, y, w, h):
    # Laptop with a fake video call: masked face, falling coins.
    panel(cv, x, y, w, h)
    ix, iy, iw, ih = x + 3, y + 3, w - 6, h - 6
    cv.rect(ix, iy, iw, 148, (30, 42, 66))
    # laptop screen
    sx, sy, sw, sh = ix + 90, iy + 14, 300, 108
    cv.rect(sx - 8, sy - 8, sw + 16, sh + 16, DARKGREY)
    cv.rect(sx, sy, sw, sh, (16, 28, 48))
    # video-call face: head + mask
    cv.circle(sx + 150, sy + 46, 30, (222, 184, 150))
    cv.rect(sx + 120, sy + 40, 60, 16, BLACK)  # mask band
    cv.circle(sx + 138, sy + 48, 3, WHITE)
    cv.circle(sx + 162, sy + 48, 3, WHITE)
    cv.rect(sx + 128, sy + 78, 44, 22, (70, 90, 120))  # shoulders
    # call UI
    cv.rect(sx + 10, sy + 8, 54, 14, RED)
    draw_text(cv, sx + 14, sy + 10, "LIVE", 1, WHITE)
    cv.rect(sx + sw - 64, sy + 8, 54, 14, (40, 60, 40))
    draw_text(cv, sx + sw - 60, sy + 10, "REC", 1, WHITE)
    # laptop base
    cv.poly([(sx - 26, sy + sh + 8), (sx + sw + 26, sy + sh + 8),
             (sx + sw + 8, sy + sh + 26), (sx - 8, sy + sh + 26)], GREY)
    # coins spilling out
    for cx, cy, r in [(sx + sw + 30, sy + 30, 12), (sx + sw + 52, sy + 58, 10),
                      (sx + sw + 18, sy + 84, 11), (sx + sw + 66, sy + 96, 9),
                      (sx + sw - 40, sy + 118, 10)]:
        cv.circle(cx, cy, r, GOLD)
        draw_text(cv, cx - 4, cy - 4, "$", 1, (120, 90, 0))
    caption_bar(cv, x, y + 148, w, h - 148,
                "FBI: N. KOREA $400M HACK",
                "FAKE VIDEO CALLS STOLE CRYPTO IN 'FACESTEALER' SCHEME")


def draw_footer(cv):
    cv.rect(16, 932, 992, 76, RED)
    draw_centered(cv, W // 2, 942,
                  "ALSO: MICROSOFT 365 DOWN WORLDWIDE - OUTLOOK AND TEAMS OUT SINCE THURSDAY",
                  2, WHITE)
    draw_centered(cv, W // 2, 972,
                  "KANE: RECORD 126th CAP, ENGLAND 2-1 CROATIA - US: RECORD 483,200 DEPORTATIONS",
                  2, WHITE)


# --- PNG writer (stdlib only) ---

def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 6)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    cv = Canvas(W, H, CREAM)
    draw_header(cv)
    draw_hero(cv)
    draw_ukraine(cv, 16, 420, 488, 244)
    draw_warship(cv, 520, 420, 488, 244)
    draw_iran(cv, 16, 676, 488, 244)
    draw_fbi(cv, 520, 676, 488, 244)
    draw_footer(cv)
    out = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    n = write_png(cv, out)
    print(f"wrote {out} ({n} bytes)")


if __name__ == "__main__":
    main()
