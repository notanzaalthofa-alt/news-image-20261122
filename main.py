"""news-image-20261122: sum up 22 November 2026 world news in one image.

Pure-stdlib Python. Renders a 1024x1024 PNG of 54 verified stories from
22 November 2026 (UTC): 3 lead stories, a UTC timeline strip, and a
two-column grid of 51 more. Writes ONLY to MAKEFUN_OUTPUT_DIR.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# --- palette (original: deep slate blue + gold) ---
BG = (11, 27, 43)
PANEL = (18, 42, 60)
PANEL2 = (23, 52, 72)
GOLD = (233, 196, 106)
WHITE = (245, 244, 238)
MUTED = (150, 175, 190)
FAINT = (105, 128, 145)
LINE = (52, 84, 106)

CAT_COLORS = {
    "WAR": (224, 82, 82),
    "POL": (120, 150, 240),
    "CLIM": (96, 200, 130),
    "ECON": (230, 200, 90),
    "TECH": (80, 190, 220),
    "SCI": (170, 140, 230),
    "SPORT": (240, 150, 60),
    "CULT": (230, 130, 180),
    "WORLD": (110, 200, 190),
    "US": (200, 170, 240),
    "HEALTH": (90, 210, 160),
}

# --- original 5x7 bitmap font: each glyph is 7 rows of 5 bits ---
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x0E, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "~": (0, 0, 0x0A, 0x15, 0, 0, 0),
    "^": (0x04, 0x0A, 0x11, 0, 0, 0, 0),
    "•": (0, 0, 0x0E, 0x0E, 0x0E, 0, 0),
}

# --- pixel buffer ---
PIX = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i] = color[0]
        PIX[i + 1] = color[1]
        PIX[i + 2] = color[2]


def fill(x, y, w, h, color):
    for yy in range(y, y + h):
        if yy < 0 or yy >= H:
            continue
        base = (yy * W + x) * 3
        for xx in range(max(0, x), min(W, x + w)):
            i = base + (xx - x) * 3 if x >= 0 else (yy * W + xx) * 3
            PIX[i] = color[0]
            PIX[i + 1] = color[1]
            PIX[i + 2] = color[2]


def hline(x0, x1, y, color):
    for xx in range(x0, x1 + 1):
        put(xx, y, color)


def vline(x, y0, y1, color):
    for yy in range(y0, y1 + 1):
        put(x, yy, color)


def adv(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * adv(scale)


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT["?"]
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    for dy in range(scale):
                        for dx in range(scale):
                            put(cx + col * scale + dx, y + row * scale + dy, color)
        cx += adv(scale)


def draw_centered(cx, y, s, scale, color):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, width_chars):
    words = s.split(" ")
    lines = []
    cur = ""
    for w in words:
        if cur == "":
            cur = w
        elif len(cur) + 1 + len(w) <= width_chars:
            cur = cur + " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def trunc(s, n):
    if len(s) <= n:
        return s
    return s[: n - 1] + ">"


# --- PNG encoder ---
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += PIX[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# --- stories: all verified 22 November 2026 (UTC) ---
# 3 leads, then 51 more in the grid. Total 54.
LEADS = [
    ("CLIM", "COP31 COLLAPSES: NO DEAL",
     "EU objects to a text with no fossil fuels; talks end with no pact."),
    ("POL", "DEMOCRATS WIN RECORD HOUSE MAJORITY",
     "258 seats after flipping North Carolina; largest majority in 34 years."),
    ("WAR", "RUSSIAN SHIP ABLAZE OFF FINLAND",
     "Cargo vessel burns in the Baltic; 14 missing near Kyiv."),
]

GRID = [
    ("WAR", "Settler arson in West Bank"),
    ("WAR", "Blast on Russian ship in Libya"),
    ("WAR", "Boy, 7, pulled from Ukraine rubble"),
    ("POL", "Korea minister quits over exam row"),
    ("WORLD", "Indonesia factory fire: 36 missing"),
    ("POL", "Schumer faces leadership challenge"),
    ("ECON", "China eases margin trading rules"),
    ("US", "Trump hosts meme-coin gala"),
    ("ECON", "Anthropic IPO chafes bankers"),
    ("POL", "US-Libya aviation, minerals deals"),
    ("WORLD", "S. Africa deputy president dies"),
    ("HEALTH", "Ethiopia polio drive for 11m kids"),
    ("WORLD", "Gambia intercepts 491 migrants"),
    ("WORLD", "ECOWAS backs women in green shift"),
    ("CULT", "Miley Cyrus marries Maxx Morando"),
    ("CULT", "Paolo Bulgari dies aged 89"),
    ("SPORT", "FIFA set to confirm UK for 2035"),
    ("SPORT", "Alcaraz wins ATP Finals title"),
    ("SPORT", "Verstappen wins Las Vegas GP"),
    ("SPORT", "Liverpool thrash Man Utd 4-0"),
    ("SPORT", "Tottenham beat Man City 3-1 in WSL"),
    ("SPORT", "McBurnie double stuns Brighton 2-0"),
    ("SPORT", "Price wins Grand Slam of Darts"),
    ("SPORT", "Bristol rout Harlequins 48-21"),
    ("SPORT", "Pakistan beat Scotland by 9 wkts"),
    ("SPORT", "Will Jacks out with broken hand"),
    ("SPORT", "Eagles end 7-game skid vs Steelers"),
    ("SPORT", "Lions win sixth straight over Bucs"),
    ("SPORT", "Panthers edge Ravens 35-33"),
    ("SPORT", "Cowboys rout Titans 51-30"),
    ("SPORT", "Bridges buzzer-beater lifts Knicks"),
    ("SPORT", "Antonsen wins Hong Kong Open"),
    ("SPORT", "Mohun Bagan go top of ISL"),
    ("SPORT", "India U19 B Women win tri-series"),
    ("US", "Army to detonate explosives"),
    ("US", "Alabama gas pipeline fire"),
    ("US", "Ohio baby-shower shooting kills 3"),
    ("POL", "Hubbard defeats Rep. Virginia Foxx"),
    ("POL", "Jeffries open to impeachment push"),
    ("POL", "Ossoff Senate win fuels 2028 talk"),
    ("WORLD", "Turkey protests media closures"),
    ("SPORT", "Fernandes pauses Man Utd talks"),
    ("SPORT", "Paredes collapses in TV interview"),
    ("SCI", "Gordon Bell Prize for exascale sim"),
    ("SCI", "New pulsar found 1m times faster"),
    ("SCI", "JWST replays stellar merger"),
    ("SCI", "BepiColombo MIXS sees first X-rays"),
    ("ECON", "New York unveils 5 GW nuclear plan"),
    ("ECON", "Brava takes Brazil oil cluster"),
    ("POL", "Burnham hails landmark EU deal"),
    ("SPORT", "Cote d'Ivoire snatch late draw"),
]

# (UTC time, short label) for the timeline strip
TIMELINE = [
    ("09:49", "VERSTAPPEN WINS", "LAS VEGAS GP"),
    ("11:57", "SEARCH FOR MISSING", "AFTER KYIV STRIKE"),
    ("12:57", "COP31: NO DEAL", "WHAT NEXT?"),
    ("14:28", "BLAST ON RUSSIAN", "SHIP AT LIBYA PORT"),
    ("15:22", "MILEY CYRUS", "MARRIES IN CALIFORNIA"),
    ("16:44", "FIFA SET TO CONFIRM", "UK FOR 2035 WWC"),
    ("19:37", "PRICE WINS", "GRAND SLAM OF DARTS"),
    ("20:26", "DEMOCRATS FLIP NC", "258-SEAT MAJORITY"),
]


def draw():
    fill(0, 0, W, H, BG)
    # gold top rule + header
    fill(0, 0, W, 4, GOLD)
    draw_centered(W // 2, 16, "22 NOVEMBER 2026", 4, GOLD)
    draw_centered(W // 2, 52, "THE WORLD IN ONE IMAGE  -  SUNDAY", 2, WHITE)
    draw_centered(W // 2, 70, "54 STORIES VERIFIED  -  ALL FROM 22 NOVEMBER 2026 (UTC)", 1, MUTED)

    # --- 3 lead cards ---
    card_w = 320
    card_h = 158
    y0 = 92
    for i, (cat, head, detail) in enumerate(LEADS):
        x0 = 12 + i * (card_w + 12)
        fill(x0, y0, card_w, card_h, PANEL)
        fill(x0, y0, card_w, 3, CAT_COLORS[cat])
        draw_text(x0 + 12, y0 + 12, "LEAD " + str(i + 1) + "  -  " + cat, 1, CAT_COLORS[cat])
        lines = wrap(head, 16)
        yy = y0 + 32
        for ln in lines[:3]:
            draw_text(x0 + 12, yy, ln, 3, WHITE)
            yy += 22
        dlines = wrap(detail, 24)
        yy += 2
        for ln in dlines[:3]:
            draw_text(x0 + 12, yy, ln, 2, MUTED)
            yy += 16

    # --- UTC timeline strip ---
    ty = 262
    fill(12, ty, 1000, 72, PANEL2)
    draw_text(24, ty + 8, "UTC TIMELINE", 1, GOLD)
    hline(40, 984, ty + 44, LINE)
    n = len(TIMELINE)
    for i, (t, a, b) in enumerate(TIMELINE):
        cx = 80 + i * 124
        fill(cx - 4, ty + 40, 8, 8, GOLD)
        draw_centered(cx, ty + 24, t, 1, WHITE)
        draw_centered(cx, ty + 54, a, 1, WHITE)
        draw_centered(cx, ty + 63, b, 1, MUTED)

    # --- grid section header ---
    draw_text(12, 348, "THE DAY IN BRIEF  -  51 MORE STORIES", 2, GOLD)
    hline(12, 1012, 366, LINE)

    # --- two-column grid ---
    col_w = 493
    row_h = 23
    gy = 378
    left = GRID[:26]
    right = GRID[26:]
    for col_i, col in enumerate((left, right)):
        x0 = 12 + col_i * (col_w + 14)
        for r, (cat, txt) in enumerate(col):
            yy = gy + r * row_h
            fill(x0, yy + 3, 8, 8, CAT_COLORS[cat])
            draw_text(x0 + 14, yy, cat, 1, CAT_COLORS[cat])
            draw_text(x0 + 14 + 5 * 6 + 6, yy, trunc(txt, 34), 2, WHITE)

    # --- footer ---
    hline(12, 1012, 984, LINE)
    draw_centered(
        W // 2, 996,
        "SOURCES: REUTERS - BBC - AP - AFP - PANA - STORIES FIRST REPORTED 22 NOV 2026 (UTC)",
        1, FAINT,
    )


def main():
    out_dir = os.environ["MAKEFUN_OUTPUT_DIR"]
    draw()
    path = os.path.join(out_dir, "news.png")
    with open(path, "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
