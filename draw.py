#!/usr/bin/env python3
"""Render the news-image-20261123 r3 entry: a newspaper front page.

Broadsheet layout, light mode, lead-dominant: one big lead story
(COP31 collapse) on top, three columns of secondary stories below.
Run: python3 draw.py  -> writes entry.png (1024x1024) next to this file.
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
W, H = 1024, 1024
PAPER = (253, 251, 245)   # off-white newsprint
INK = (17, 17, 17)        # near-black
RED = (192, 57, 43)       # accent, breaking tags only
GRAY = (90, 90, 90)
LIGHT_RULE = (200, 196, 186)
GLOBE_BLUE = (216, 230, 240)
LAND = (143, 169, 143)

MX = 36                   # side margin
CW = W - 2 * MX           # content width


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_h(draw, lines, fnt, leading):
    """Pixel height of wrapped lines at the given leading."""
    total = 0
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        total += (box[3] - box[1]) + leading
    return total - leading if lines else 0


def draw_lines(draw, x, y, lines, fnt, fill, leading):
    """Draw wrapped lines; return y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        box = draw.textbbox((0, 0), line, font=fnt)
        y += (box[3] - box[1]) + leading
    return y


def fit_size(draw, text, fnt_name, start, max_w):
    """Largest font size <= start whose text fits max_w."""
    size = start
    while size > 10:
        fnt = font(fnt_name, size)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        size -= 2
    return font(fnt_name, 10)


def tag(draw, x, y, text, fill=RED, fg=(255, 255, 255), size=19):
    """Solid tag chip; returns width used."""
    fnt = font("DejaVuSans-Bold.ttf", size)
    tw = draw.textlength(text, font=fnt)
    pad_x, pad_y = 10, 5
    box = draw.textbbox((0, 0), text, font=fnt)
    th = box[3] - box[1]
    draw.rectangle([x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y], fill=fill)
    draw.text((x + pad_x, y + pad_y - 1), text, font=fnt, fill=fg)
    return tw + 2 * pad_x


def story(draw, x, y, w, tag_text, headline, summary,
          head_size=25, sum_size=18, tag_fill=RED):
    """One secondary story block; returns y below the block."""
    tag_w = tag(draw, x, y, tag_text, fill=tag_fill, size=17)
    y += 26
    hf = font("DejaVuSans-Bold.ttf", head_size)
    lines = wrap(draw, headline, hf, w)
    y = draw_lines(draw, x, y, lines, hf, INK, 3)
    y += 4
    sf = font("DejaVuSans.ttf", sum_size)
    slines = wrap(draw, summary, sf, w)
    y = draw_lines(draw, x, y, slines, sf, (60, 60, 60), 2)
    return y


def draw_globe(draw, cx, cy, r):
    """Simple drawn globe with a red crack: the lead visual."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOBE_BLUE,
                 outline=INK, width=3)
    # Abstract landmasses (ellipses, clipped by the circle visually).
    blobs = [
        (cx - r * 0.55, cy - r * 0.55, cx - r * 0.05, cy - r * 0.05),
        (cx + r * 0.10, cy - r * 0.70, cx + r * 0.62, cy - r * 0.15),
        (cx - r * 0.30, cy + r * 0.10, cx + r * 0.30, cy + r * 0.55),
        (cx + r * 0.45, cy + r * 0.30, cx + r * 0.70, cy + r * 0.60),
    ]
    for b in blobs:
        draw.ellipse(b, fill=LAND)
    # Red crack across the globe.
    crack = [
        (cx - r * 0.75, cy - r * 0.45), (cx - r * 0.30, cy - r * 0.10),
        (cx - r * 0.45, cy + r * 0.25), (cx + r * 0.05, cy + r * 0.45),
        (cx - r * 0.10, cy + r * 0.75), (cx + r * 0.35, cy + r * 0.90),
    ]
    draw.line(crack, fill=RED, width=6, joint="curve")
    # "NO DEAL" stamp, tilted, at the globe's lower right.
    stamp = Image.new("RGBA", (240, 68), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sf = font("DejaVuSans-Bold.ttf", 24)
    sd.rectangle([4, 4, 236, 64], fill=PAPER, outline=RED, width=4)
    sd.text((120, 34), "NO DEAL", font=sf, fill=RED, anchor="mm")
    stamp = stamp.rotate(-10, expand=True, resample=Image.BICUBIC)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(stamp, (cx + 55 - 120, cy + 45 - 34), stamp)
    return img


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    name_fnt = fit_size(d, "THE WORLD HERALD", "DejaVuSans-Bold.ttf", 64, CW)
    nw = d.textlength("THE WORLD HERALD", font=name_fnt)
    d.text(((W - nw) / 2, 26), "THE WORLD HERALD", font=name_fnt, fill=INK)
    d.line([(MX, 108), (W - MX, 108)], fill=INK, width=3)
    d.line([(MX, 114), (W - MX, 114)], fill=INK, width=1)
    dateline_fnt = font("DejaVuSans-Bold.ttf", 20)
    d.text((MX, 122), "MONDAY, 23 NOVEMBER 2026", font=dateline_fnt, fill=INK)
    right = "ONE PAGE  •  EIGHT STORIES"
    rw = d.textlength(right, font=dateline_fnt)
    d.text((W - MX - rw, 122), right, font=dateline_fnt, fill=GRAY)
    d.line([(MX, 152), (W - MX, 152)], fill=INK, width=1)

    # ---- Lead story ----
    y = 168
    tag(d, MX, y, "BREAKING", size=19)
    tag_fnt = font("DejaVuSans-Bold.ttf", 19)
    tag_label = "CLIMATE  —  ANTALYA, TÜRKIYE"
    d.text((MX + 132, y + 4), tag_label, font=tag_fnt, fill=GRAY)
    y += 46

    head_fnt = fit_size(d, "COP31 COLLAPSES", "DejaVuSans-Bold.ttf", 86, CW)
    d.text((MX, y), "COP31 COLLAPSES", font=head_fnt, fill=INK)
    hb = d.textbbox((0, 0), "COP31 COLLAPSES", font=head_fnt)
    y += (hb[3] - hb[1]) + 6
    sub_fnt = font("DejaVuSans-Bold.ttf", 34)
    d.text((MX, y), "NO DEAL AFTER 48 HOURS OF OVERTIME", font=sub_fnt, fill=RED)
    sb = d.textbbox((0, 0), "NO DEAL AFTER 48 HOURS OF OVERTIME", font=sub_fnt)
    y += (sb[3] - sb[1]) + 18

    # Summary (left) + globe visual (right).
    sum_w = 560
    sum_fnt = font("DejaVuSans.ttf", 22)
    summary = ("After ~48 hours of overtime, ~200 countries leave Antalya "
               "with no overarching agreement — the first full collapse of "
               "a COP's main deal since Copenhagen 2009.")
    slines = wrap(d, summary, sum_fnt, sum_w)
    sy = y
    sy = draw_lines(d, MX, sy, slines, sum_fnt, (40, 40, 40), 6)
    sy += 10
    sum2 = ("The EU refused any deal without fossil-fuel phase-out language.")
    s2lines = wrap(d, sum2, sum_fnt, sum_w)
    sy = draw_lines(d, MX, sy, s2lines, font("DejaVuSans-Bold.ttf", 22),
                    INK, 6)
    # Globe on the right of the summary block.
    globe_cx, globe_cy, globe_r = W - MX - 165, y + 72, 72
    stamp_layer = draw_globe(d, globe_cx, globe_cy, globe_r)
    img.paste(Image.alpha_composite(img.convert("RGBA"), stamp_layer)
              .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    y = max(sy, y + 170) + 14

    # Stat strip: 200 countries / 48h overtime / 0 agreement.
    stats = [("200", "COUNTRIES AT THE TABLE"),
             ("48h", "OVERTIME, NO DEAL"),
             ("0", "AGREEMENT REACHED")]
    col_w = CW // 3
    stat_fnt = font("DejaVuSans-Bold.ttf", 40)
    stat_lab = font("DejaVuSans-Bold.ttf", 16)
    for i, (num, lab) in enumerate(stats):
        cx = MX + i * col_w + col_w // 2
        nw2 = d.textlength(num, font=stat_fnt)
        d.text((cx - nw2 / 2, y), num, font=stat_fnt, fill=RED)
        lw = d.textlength(lab, font=stat_lab)
        d.text((cx - lw / 2, y + 48), lab, font=stat_lab, fill=GRAY)
        if i:
            d.line([(MX + i * col_w, y + 4),
                    (MX + i * col_w, y + 62)], fill=LIGHT_RULE, width=2)
    y += 78

    # Double rule into the secondary zone.
    d.line([(MX, y), (W - MX, y)], fill=INK, width=2)
    d.line([(MX, y + 5), (W - MX, y + 5)], fill=INK, width=1)
    y += 22

    # ---- Secondary zone: 3 columns ----
    col_w = (CW - 2 * 26) // 3
    x0 = MX
    x1 = MX + col_w + 26
    x2 = MX + 2 * (col_w + 26)
    top = y

    # Column 1: Ukraine.
    cy = story(d, x0, top, col_w, "UKRAINE",
               "Drone strike kills 11 in Dymer",
               "Drone hits a five-storey block north of Kyiv; 11 dead, "
               "including a teenager.", head_size=23, sum_size=16)
    cy += 10
    d.line([(x0, cy), (x0 + col_w, cy)], fill=LIGHT_RULE, width=1)
    cy += 10
    cy = story(d, x0, cy, col_w, "BLACK SEA",
               "Ukraine sinks Russian frigate Merkury",
               "Frigate sinks off Benghazi after a suspected naval "
               "drone attack.", head_size=23, sum_size=16)

    # Column 2: USA.
    cy = story(d, x1, top, col_w, "USA",
               "Democrats clinch 258 House seats",
               "AP calls at least 258 seats — largest House majority "
               "since 1992.", head_size=23, sum_size=16)
    cy += 10
    d.line([(x1, cy), (x1 + col_w, cy)], fill=LIGHT_RULE, width=1)
    cy += 10
    cy = story(d, x1, cy, col_w, "WASHINGTON",
               "Trump: strike Iran if no deal",
               "President \"inclined\" to resume military conflict if no "
               "deal by New Year.", head_size=23, sum_size=16)

    # Column 3: sport, markets, Indonesia.
    cy = story(d, x2, top, col_w, "SPORT",
               "Alcaraz wins ATP Finals",
               "Beats Zverev 6-2, 7-6(7); undefeated 5-0 week in Turin.",
               head_size=23, sum_size=16)
    cy += 10
    d.line([(x2, cy), (x2 + col_w, cy)], fill=LIGHT_RULE, width=1)
    cy += 10
    cy = story(d, x2, cy, col_w, "MARKETS",
               "Taiwan stocks swing 1,666 points",
               "Index closes 36,811.89, up 778.60 (+2.16%); TSMC "
               "NT$2,030.", head_size=23, sum_size=16)
    cy += 10
    d.line([(x2, cy), (x2 + col_w, cy)], fill=LIGHT_RULE, width=1)
    cy += 10
    cy = story(d, x2, cy, col_w, "INDONESIA",
               "Factory fire kills 24 in Banten",
               "Blaze at a candy factory; 24 dead, ~30 unaccounted for.",
               head_size=23, sum_size=16)

    # ---- Footer ----
    foot_fnt = font("DejaVuSans.ttf", 15)
    foot = "Sources: Reuters  •  Associated Press  •  Al Jazeera  •  Xinhua  •  World News Wire  —  23 Nov 2026"
    fw = d.textlength(foot, font=foot_fnt)
    d.text(((W - fw) / 2, H - 30), foot, font=foot_fnt, fill=GRAY)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
