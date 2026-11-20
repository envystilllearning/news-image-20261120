#!/usr/bin/env python3
"""Sum up Friday 20 November 2026's world news in one image.

Composes a broadsheet front page (1024x1024 PNG) from illustrated scene
assets held in this repository plus typeset headlines, summaries and
sources. Deterministic: fixed assets, fixed fonts, no network, no clock.
Writes the image to /output/entry.png (or $ENTRY_OUTPUT_DIR/entry.png,
falling back to ./entry.png when /output does not exist).
"""
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT

W = H = 1024
PAPER = (247, 242, 231)
INK = (26, 23, 20)
RED = (179, 35, 27)
NAVY = (22, 50, 79)
GRAY = (90, 83, 89)
HAIR = (210, 202, 188)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def cover(img, w, h):
    """Center-crop img to exactly w x h."""
    iw, ih = img.size
    scale = max(w / iw, h / ih)
    img = img.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    x = (img.size[0] - w) // 2
    y = (img.size[1] - h) // 2
    return img.crop((x, y, x + w, y + h))


def load_asset(name, w, h, hue):
    p = ASSETS / name
    if p.exists():
        return cover(Image.open(p).convert("RGB"), w, h)
    # Fallback panel: flat colour with a simple sun/disc motif, never a crash.
    img = Image.new("RGB", (w, h), hue)
    d = ImageDraw.Draw(img)
    d.ellipse([w * 0.62, h * 0.14, w * 0.62 + h * 0.34, h * 0.14 + h * 0.34],
              fill=(255, 214, 120))
    d.rectangle([0, h * 0.78, w, h], fill=(0, 0, 0))
    return img


def sheet_panel(idx, w, h):
    """Panel idx (0..5) of the 3x2 medium sheet, or an individual file."""
    sheet = ASSETS / "sheet.jpg"
    names = ["med_ukeu.jpg", "med_cop31.jpg", "med_poland.jpg",
             "med_italy.jpg", "med_japan.jpg", "med_cricket.jpg"]
    hues = [(46, 94, 140), (32, 120, 90), (90, 110, 60),
            (170, 60, 40), (190, 120, 40), (40, 130, 70)]
    if sheet.exists():
        img = Image.open(sheet).convert("RGB")
        sw, sh = img.size
        cw, ch = sw // 3, sh // 2
        ix, iy = round(cw * 0.02), round(ch * 0.02)  # inset off the gutters
        x, y = (idx % 3) * cw + ix, (idx // 3) * ch + iy
        return cover(img.crop((x, y, x + cw - 2 * ix, y + ch - 2 * iy)), w, h)
    return load_asset(names[idx], w, h, hues[idx])


# ---------------------------------------------------------------- stories
HEROES = [
    dict(img="hero_kyiv.jpg", hue=(30, 42, 84), kick="1  KYIV, UKRAINE · WAR",
         head="Russian missiles hit three Kyiv bridges",
         body="An overnight barrage of about 110 missiles and 400 drones "
              "killed at least nine people across Ukraine and cut power "
              "and water in the capital.",
         src="(Kyiv Independent, BBC)"),
    dict(img="hero_cyclone.jpg", hue=(14, 110, 110), kick="2  ODISHA, INDIA · CYCLONE",
         head="Cyclone Akvan comes ashore in eastern India",
         body="The storm crossed the coast near Gopalpur from about 8 am "
              "after more than 300,000 people were moved to shelters. "
              "No deaths were reported.",
         src="(IMD, Deccan Herald)"),
    dict(img="hero_markets.jpg", hue=(120, 30, 40), kick="3  TAIPEI · SEOUL · TOKYO · MARKETS",
         head="AI sell-off sinks Asia's stock markets",
         body="Taiwan's index fell 6.2% to end its worst week since 1991. "
              "Seoul lost 5.2% and Tokyo 5.1% as chipmakers led the slide.",
         src="(Al Jazeera, Anadolu)"),
]

MEDIUMS = [
    dict(kick="4  BRUSSELS · DIPLOMACY", head="UK and EU seal a \u201creset\u201d deal",
         body="Food trade, youth visas, carbon link.", src="(Reuters)"),
    dict(kick="5  ANTALYA · CLIMATE", head="COP31 reaches its last day with no deal",
         body="The draft text leaves out fossil fuels.", src="(UN News)"),
    dict(kick="6  EASTERN POLAND · SECURITY", head="Russian cruise missile lands in Poland",
         body="It fell in a field; two airports paused.", src="(Reuters)"),
    dict(kick="7  ITALY · LABOUR", head="General strike over Italy's budget",
         body="Workers and students march.", src="(Reuters)"),
    dict(kick="8  TOKYO · ECONOMY", head="Japan's inflation picks up to 2.3%",
         body="A December rate rise in view.", src="(Reuters)"),
    dict(kick="9  WELLINGTON · CRICKET", head="Phillips hits 118 against India",
         body="Hundreds v India in all three formats.", src="(ICC)"),
]

BRIEFS = [
    ("Lviv", "A strike on a railway station kills two", "BBC"),
    ("Moscow", "Russia decries Estonia's border closure", "Reuters"),
    ("Berlin", "School pupils strike against military service", "Al Jazeera"),
    ("London", "General says UK faces cyber attacks abroad", "Sky News"),
    ("Beijing", "China holds its loan rates for an 18th month", "Xinhua"),
    ("Tokyo", "SoftBank shares fall more than 14% in a day", "Al Jazeera"),
    ("Seoul", "Kospi index ends the week 7.9% lower", "Anadolu"),
    ("Ganjam", "209 mm of rain falls as Akvan crosses", "PTI"),
    ("Lebanon", "Israeli air strikes hit the south and east", "Anadolu"),
    ("Yemen", "Gunmen fire on a cargo ship off the coast", "UKMTO"),
    ("Abuja", "Court bars new evidence on Tinubu", "Channels TV"),
    ("Kampala", "Police told to enforce Ebola ban on rallies", "allAfrica"),
    ("Malawi", "Fuel crisis brings night-long petrol queues", "Al Jazeera"),
    ("Africa", "AfDB says 22 countries are in debt distress", "allAfrica"),
    ("Las Vegas", "Russell fastest in wet Grand Prix practice", "Autosport"),
    ("New York", "Nasdaq futures fall 1.6% before the bell", "24/7 Wall St"),
    ("Washington", "Democrats query Kari Lake's free work", "Al Jazeera"),
    ("Wellington", "Nicholls makes 175 in a stand of 216", "ICC"),
    ("Sydney", "Australian shares fall in the sell-off", "Reuters"),
    ("Antalya", "Panama asks COP31 to cap world oil output", "Al Jazeera"),
    ("Antalya", "EU official calls the climate draft unacceptable", "RTÉ"),
    ("Turin", "ATP backs a plan to lift player pay past $350m", "Anadolu"),
]

STATS = [
    ("3", "bridges over the Dnipro damaged"),
    ("300,000+", "people moved to shelters"),
    ("-6.2%", "Taiwan share index, Friday close"),
    ("100,000", "youth visas a year, UK-EU deal"),
    ("2.3%", "Japan consumer inflation, Oct"),
    ("118", "runs by Glenn Phillips v India"),
]

REGIONS = [  # (label, count, colour)
    ("Europe 8", 8, (46, 94, 140)), ("Asia 8", 8, (192, 57, 43)),
    ("Middle East 3", 3, (176, 141, 32)), ("Africa 5", 5, (39, 130, 80)),
    ("Americas 4", 4, (110, 70, 160)), ("Oceania 3", 3, (14, 110, 110)),
    ("Global 4", 4, (110, 110, 110)),
]


# ---------------------------------------------------------------- layout
M = 28           # page margin
CW = W - 2 * M   # content width


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Kicker row
    d.text((M, 16), "THE WORLD IN ONE DAY", font=F(SANS_B, 17), fill=RED)
    right = "31 STORIES · 7 REGIONS · EVERY ONE DATED FRIDAY 20 NOVEMBER 2026"
    d.text((W - M - d.textlength(right, font=F(SANS_B, 15)), 18),
           right, font=F(SANS_B, 15), fill=INK)
    d.line([M, 44, W - M, 44], fill=INK, width=2)

    # Masthead
    title = "Friday 20 November 2026"
    tf = F(SERIF_B, 63)
    d.text(((W - d.textlength(title, font=tf)) / 2, 52), title, font=tf, fill=INK)
    sub = ("Russian missiles hit Kyiv's bridges · Cyclone Akvan strikes India · "
           "An AI sell-off sinks Asia's markets")
    sf = F(SERIF, 17)
    d.text(((W - d.textlength(sub, font=sf)) / 2, 128), sub, font=sf, fill=(60, 55, 50))
    d.line([M, 158, W - M, 158], fill=INK, width=3)
    d.line([M, 163, W - M, 163], fill=INK, width=1)

    # Stat band
    y = 172
    colw = CW / 6
    for i, (num, lab) in enumerate(STATS):
        x = M + i * colw
        if i:
            d.line([x, y + 2, x, y + 44], fill=HAIR, width=1)
        d.text((x + 8, y), num, font=F(SERIF_B, 27), fill=RED if i in (0, 2, 5) else INK)
        for j, ln in enumerate(wrap(d, lab, F(SANS, 11), colw - 16)[:2]):
            d.text((x + 8, y + 34 + j * 13), ln, font=F(SANS, 11), fill=GRAY)

    # Region bar
    y = 234
    total = sum(c for _, c, _ in REGIONS)
    x = M
    for label, count, colour in REGIONS:
        wseg = CW * count / total
        d.rectangle([x, y, x + wseg - 2, y + 20], fill=colour)
        d.text((x + 7, y + 4), label, font=F(SANS_B, 12), fill=WHITE)
        x += wseg

    # Hero cards
    y = 264
    gap = 13
    cardw = (CW - 2 * gap) / 3
    imgh = 144
    for i, s in enumerate(HEROES):
        x = M + i * (cardw + gap)
        img.paste(load_asset(s["img"], int(cardw), imgh, s["hue"]), (int(x), y))
        ty = y + imgh + 8
        d.text((x, ty), s["kick"], font=F(SANS_B, 12), fill=RED)
        ty += 18
        for ln in wrap(d, s["head"], F(SERIF_B, 24), cardw)[:3]:
            d.text((x, ty), ln, font=F(SERIF_B, 24), fill=INK)
            ty += 29
        ty += 2
        for ln in wrap(d, s["body"] + " " + s["src"], F(SANS, 13), cardw)[:4]:
            d.text((x, ty), ln, font=F(SANS, 13), fill=(50, 46, 42))
            ty += 17

    # Medium cards (2 rows x 3)
    y = 600
    rowh = 96
    for r in range(2):
        for c in range(3):
            idx = r * 3 + c
            s = MEDIUMS[idx]
            x = M + c * (cardw + gap)
            yy = y + r * (rowh + 10)
            img.paste(sheet_panel(idx, 96, rowh), (int(x), yy))
            tx = x + 106
            d.text((tx, yy + 1), s["kick"], font=F(SANS_B, 10), fill=RED)
            ty = yy + 15
            for ln in wrap(d, s["head"], F(SANS_B, 15), cardw - 106)[:2]:
                d.text((tx, ty), ln, font=F(SANS_B, 15), fill=INK)
                ty += 19
            for ln in wrap(d, s["body"] + " " + s["src"], F(SANS, 11), cardw - 106)[:2]:
                d.text((tx, ty + 1), ln, font=F(SANS, 11), fill=(50, 46, 42))
                ty += 14

    # Briefs
    y = 818
    d.line([M, y - 8, W - M, y - 8], fill=INK, width=2)
    d.text((M, y), "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES",
           font=F(SANS_B, 15), fill=RED)
    colw2 = (CW - 24) / 2
    bf = F(SANS, 11)
    bfb = F(SANS_B, 11)
    for i, (place, text, src) in enumerate(BRIEFS):
        col = 0 if i < 11 else 1
        row = i if i < 11 else i - 11
        x = M + col * (colw2 + 24)
        yy = y + 20 + row * 13.5
        num = f"{i + 10} "
        d.text((x, yy), num, font=bfb, fill=RED)
        nx = x + d.textlength(num, font=bfb)
        lead = place + " "
        d.text((nx, yy), lead, font=bfb, fill=INK)
        rest = text + f" ({src})"
        maxw = colw2 - (nx - x)
        lines = wrap(d, rest, bf, maxw)
        d.text((nx + d.textlength(lead, font=bfb), yy),
               lines[0] if lines else "", font=bf, fill=(50, 46, 42))

    # Date check strip
    d.rectangle([M, 990, W - M, 1012], fill=RED)
    msg = ("DATE CHECK — Left out, they broke before Friday: World Court's Myanmar ruling · "
           "Shenzhen declaration · Tonga drought emergency.")
    d.text((M + 8, 995), msg, font=F(SANS_B, 10), fill=WHITE)
    return img


def main():
    img = render()
    out_dir = Path(os.environ.get("ENTRY_OUTPUT_DIR", "/output"))
    if not out_dir.exists():
        out_dir = ROOT
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"
    img.save(out, format="PNG", optimize=True)
    if out.stat().st_size > 1_000_000:  # competition cap: 1 MiB
        img.quantize(colors=256, method=Image.MEDIANCUT).save(
            out, format="PNG", optimize=True)
    print("wrote", out, out.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
