#!/usr/bin/env python3
"""
Generates the banner, project cards and section headers for a GitHub profile README.
The banner artwork is a finished image (assets/hero.png); hero.svg wraps it and adds
animated steam over the mug. GitHub only animates SVGs, and an SVG shown as an image
cannot load other files, so the PNG is embedded.
Theme: a dark sketchbook with hand-drawn doodles and pastel marker blobs, set in Poppins.
The shared drawing helpers live in scripts/doodle.py.

Usage:
    1. Edit the CONFIG block below.
    2. python build_assets.py
    3. Commit assets/ and README.md.

Standard library only.
"""

import base64
import os
import sys
import textwrap

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from doodle import (  # noqa: E402
    BORDER, CORAL, INK, LAVENDER, MINT, MUTED, PEACH, PILL, SKY, YELLOW,
    Pen, esc, inked, paper, path, sparkle, style_block, text_width,
)

# ----------------------------------------------------------------------------
# CONFIG - edit this part
# ----------------------------------------------------------------------------

# One pastel per project card, in PROJECTS order.
ACCENTS = [MINT, CORAL, LAVENDER, YELLOW, PEACH, SKY]

# Each project's "slug" also picks its doodle (see DOODLES below).
PROJECTS = [
    {
        "slug": "regtree",
        "kind": "RAG system",
        "title": "RegTree",
        "desc": "Vectorless RAG over regulatory and financial PDFs. 96% retrieval accuracy (24/25) with cited sources.",
        "tags": ["Python", "FastAPI", "PySpark", "React", "MCP"],
        "url": "https://github.com/dhruvHhh/RegTree",
        "live": False,
    },
    {
        "slug": "tripwire",
        "kind": "Chrome extension",
        "title": "Tripwire",
        "desc": "Flags risky links on any page and warns before a dangerous one opens. Every check runs locally.",
        "tags": ["JavaScript", "Manifest V3", "HTML", "CSS"],
        "url": "https://github.com/dhruvHhh/tripwire",
        "live": False,
    },
    {
        "slug": "starfall-race",
        "kind": "Multiplayer game",
        "title": "starfall",
        "desc": "Real-time typing race. Join a room, race friends on one paragraph, and watch live progress and WPM.",
        "tags": ["Next.js", "TypeScript", "Colyseus", "Tailwind"],
        "url": "https://github.com/dhruvHhh/starfall-race",
        "live": True,
    },
    {
        "slug": "sunskip",
        "kind": "Heat-aware navigation",
        "title": "SunSkip",
        "desc": "Finds routes with the least time in direct sun, guides walkers in AR, and shows cities where to add shade.",
        "tags": ["React", "FastAPI", "PostGIS", "three.js", "AWS"],
        "url": "https://github.com/suryansh04/sunskip",
        "live": True,
    },
    {
        "slug": "rehabit",
        "kind": "Stroke rehab",
        "title": "Rehabit",
        "desc": "An ESP32 touch board turns daily hand rehab for stroke survivors into games, with an AI voice companion.",
        "tags": ["ESP32", "C++", "FastAPI", "React", "Sarvam"],
        "url": "https://github.com/suryansh04/rehabit",
        "live": False,
    },
    {
        # No public repo yet. Set "url" to link it, or leave None for an unlinked card.
        "slug": "now-ai",
        "kind": "Amazon HackOn",
        "title": "Now AI",
        "desc": "Quick-commerce assistant. XGBoost predicts reorders (1.1-day MAE) and an Alexa skill takes voice orders.",
        "tags": ["Python", "SageMaker", "XGBoost", "Lambda", "Alexa"],
        "url": None,
        "live": False,
    },
]

# Section headers drawn in the same style: (file name, text, pastel).
HEADERS = [
    ("built", "Things I've built", MINT),
    ("toolbox", "My toolbox", YELLOW),
    ("activity", "What I've been up to", LAVENDER),
]

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "assets")


def svg_open(w, h, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label)}">'
    )


# ----------------------------------------------------------------------------
# Doodles: each draws into a 150 x 150 box and returns (art, blobs)
# ----------------------------------------------------------------------------

def d_regtree(pen, c):
    a = [
        path(pen.curve([(75, 142), (74, 122), (76, 100), (75, 78)])),
        path(pen.curve([(75, 114), (58, 102), (44, 90)])),
        path(pen.curve([(75, 100), (93, 89), (106, 76)])),
        path(pen.line(75, 78, 75, 60)),
        path(pen.curve([(42, 143), (75, 141), (110, 144)])),
    ]
    for x, y, rot in ((23, 57, -8), (99, 43, 7), (62, 22, -2)):
        w, h, f = 26, 32, 8
        a.append(
            f'<g transform="rotate({rot} {x + w / 2} {y + h / 2})">'
            + path(pen.poly([(x, y), (x + w - f, y), (x + w, y + f), (x + w, y + h), (x, y + h)]))
            + path(pen.poly([(x + w - f, y), (x + w - f, y + f), (x + w, y + f)], closed=False))
            + path(pen.line(x + 6, y + 15, x + w - 6, y + 15, 0.4))
            + path(pen.line(x + 6, y + 22, x + w - 10, y + 22, 0.4))
            + "</g>"
        )
    a.append(path(sparkle(132, 22, 7), stroke_width="2"))
    a.append(path(sparkle(18, 30, 4.5), stroke_width="1.8"))
    return "".join(a), [(pen.blob(80, 46, 33), c), (pen.blob(26, 116, 12), c)]


def d_tripwire(pen, c):
    a = [
        path(pen.line(22, 62, 22, 140)), path(pen.line(128, 62, 128, 140)),
        path(pen.line(14, 140, 30, 140)), path(pen.line(120, 140, 136, 140)),
        path(pen.curve([(22, 74), (50, 86), (75, 90), (100, 86), (128, 74)])),
        path(pen.line(75, 90, 75, 97, 0.3)),
        path("M62 117Q62 98 75 97Q88 98 88 117Z"),
        path(pen.line(58, 117, 92, 117, 0.5)),
        f'<circle cx="75" cy="122" r="3.2" fill="currentColor" stroke="none"/>',
        path(pen.curve([(96, 100), (100, 107), (96, 114)])),
        path(pen.curve([(103, 96), (109, 107), (103, 118)])),
        path(pen.circle(112, 32, 14)),
        path(pen.line(112, 24, 112, 33, 0.3)),
        f'<circle cx="112" cy="39.5" r="2.2" fill="currentColor" stroke="none"/>',
    ]
    tx, ty = 38, 80
    ptr = [(0, 0), (0, 25), (6, 19), (11, 30), (15, 28), (10, 17), (18, 17)]
    a.append(path(pen.poly([(tx + x, ty + y) for x, y in ptr], wob=0.3)))
    return "".join(a), [(pen.blob(77, 110, 21), c), (pen.blob(112, 32, 17, var=0.08), c)]


def d_starfall(pen, c):
    a = []
    for x, ch in ((10, "W"), (52, "P"), (94, "M")):
        y = 98
        a.append(path(pen.rrect(x, y, 36, 36, 8)))
        a.append(path(pen.rrect(x + 5, y + 4, 26, 22, 5, wob=0.5), stroke_width="1.6"))
        a.append(f'<text x="{x + 18}" y="{y + 20.5}" text-anchor="middle" font-size="12" font-weight="600" '
                 f'fill="currentColor" stroke="none">{ch}</text>')
    a.append(path(pen.star(114, 36, 16)))
    for (x1, y1, x2, y2) in ((99, 47, 56, 70), (96, 38, 64, 54), (104, 55, 76, 78)):
        a.append(path(pen.line(x1, y1, x2, y2)))
    a.append(path(sparkle(26, 34, 6), stroke_width="2"))
    a.append(f'<circle cx="52" cy="22" r="2.4" fill="currentColor" stroke="none"/>')
    return "".join(a), [(pen.blob(114, 37, 21), c), (pen.blob(70, 120, 15), c)]


def d_sunskip(pen, c):
    import math
    a = [path(pen.circle(38, 40, 15))]
    for i in range(8):
        ang = math.radians(i * 45 + 10)
        a.append(path(pen.line(38 + 21 * math.cos(ang), 40 + 21 * math.sin(ang),
                               38 + 28 * math.cos(ang), 40 + 28 * math.sin(ang), 0.3)))
    a += [
        path(pen.curve([(105, 141), (104, 124), (106, 106)])),
        path(pen.curve([(105, 118), (96, 110)])),
        path(pen.cloud(106, 78, 26)),
        path(pen.curve([(8, 142), (75, 140), (146, 143)])),
    ]
    for x in range(80, 136, 8):
        a.append(path(pen.line(x, 147, x + 6, 141, 0.2), stroke_width="1.6"))
    a.append(path(pen.curve([(14, 126), (40, 116), (62, 124), (84, 136)]), stroke_dasharray="2 7"))
    return "".join(a), [(pen.blob(38, 40, 24), c), (pen.blob(106, 79, 20, var=0.1), MINT)]


def d_rehabit(pen, c):
    a = [
        path(pen.curve([(95, 98), (94, 82), (96, 64)])),
        path("M95 80Q80 60 70 66Q76 82 95 80Z"),
        path("M96 70Q110 50 122 54Q118 72 96 70Z"),
        path(pen.poly([(69, 108), (121, 108), (114, 142), (76, 142)])),
        path(pen.rrect(63, 97, 64, 12, 4)),
        f'<circle cx="86" cy="122" r="2.6" fill="currentColor" stroke="none"/>',
        f'<circle cx="104" cy="122" r="2.6" fill="currentColor" stroke="none"/>',
        path(pen.curve([(89, 129), (95, 134), (101, 129)])),
    ]
    for cx, cy, r in ((24, 120, 9), (38, 92, 8), (22, 66, 7)):
        a.append(path(pen.circle(cx, cy, r)))
    for x1, y1, x2, y2 in ((50, 84, 56, 80), (51, 93, 58, 93), (50, 102, 56, 106)):
        a.append(path(pen.line(x1, y1, x2, y2, 0.2), stroke_width="2"))
    return "".join(a), [(pen.blob(95, 124, 26), c), (pen.blob(38, 92, 11, var=0.08), c)]


def d_now_ai(pen, c):
    a = [
        path(pen.curve([(56, 74), (57, 50), (74, 44), (91, 50), (92, 74)])),
        path(pen.poly([(34, 72), (114, 72), (120, 142), (28, 142)])),
        path(sparkle(74, 106, 12)),
        path(sparkle(96, 88, 5), stroke_width="1.8"),
        path(pen.rrect(96, 8, 48, 34, 11)),
        path(pen.poly([(106, 41), (102, 54), (117, 41)], closed=False)),
    ]
    for x, hh in ((109, 6), (116, 12), (123, 8), (130, 4)):
        a.append(path(pen.line(x, 25 - hh, x, 25 + hh, 0.2)))
    return "".join(a), [(pen.blob(74, 108, 30), c), (pen.blob(120, 25, 15, var=0.08), c)]


DOODLES = {
    "regtree": d_regtree,
    "tripwire": d_tripwire,
    "starfall-race": d_starfall,
    "sunskip": d_sunskip,
    "rehabit": d_rehabit,
    "now-ai": d_now_ai,
}


# ----------------------------------------------------------------------------
# Banner
# ----------------------------------------------------------------------------

def build_hero():
    png = os.path.join(OUT_DIR, "hero.png")
    w, h = 2019, 779  # hero.png's size
    b64 = base64.b64encode(open(png, "rb").read()).decode()
    # two steam wisps above the mug; each rises and fades, the second half a cycle later
    wisps = "".join(
        f'<g transform="translate({x} 520)"><path class="steam" style="animation-delay:{d}s" '
        f'd="M0 0C-6 -6 6 -12 0 -18C-6 -24 6 -30 0 -36"/></g>'
        for x, d in ((1834, 0), (1861, 1.5))
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="Dhruv Honwad, Full Stack AI Engineer">'
        "<style>"
        ".steam{fill:none;stroke:#f9f8f9;stroke-width:3.6;stroke-linecap:round;opacity:0;"
        "animation:rise 3s ease-in-out infinite;}"
        "@keyframes rise{0%{opacity:0;transform:translateY(8px);}30%{opacity:.95;}"
        "100%{opacity:0;transform:translateY(-18px);}}"
        "@media (prefers-reduced-motion:reduce){.steam{animation:none;opacity:.9;}}"
        "</style>"
        f'<image href="data:image/png;base64,{b64}" width="{w}" height="{h}"/>'
        f"{wisps}</svg>\n"
    )


# ----------------------------------------------------------------------------
# Cards
# ----------------------------------------------------------------------------

def build_card(p, accent):
    w, h = 490, 290
    pad = 26
    pen = Pen(p["slug"])

    lines = textwrap.wrap(p["desc"], width=37)
    if len(lines) > 3:
        print(f"Warning: description for '{p['title']}' wraps to {len(lines)} lines; shorten it so it fits.")
    desc = "".join(
        f'<text x="{pad}" y="{136 + i * 21}" font-size="14" fill="{MUTED}">{esc(l)}</text>'
        for i, l in enumerate(lines[:3])
    )

    # "kind" sticker, plus an optional live badge
    kw = text_width(p["kind"], 12, bold=True) + 24
    sticker = (
        path(pen.rrect(pad, 24, kw, 26, 13, wob=0.6), fill=accent, fill_opacity=".14", stroke=accent,
             stroke_width="1.6")
        + f'<text x="{pad + kw / 2:.1f}" y="41.5" text-anchor="middle" font-size="12" font-weight="600" '
          f'fill="{accent}">{esc(p["kind"])}</text>'
    )
    if p.get("live"):
        lx = pad + kw + 10
        sticker += (
            f'<circle class="tw" cx="{lx + 8:.1f}" cy="37" r="4" fill="{MINT}"/>'
            f'<text x="{lx + 18:.1f}" y="41.5" font-size="12" font-weight="600" fill="{MINT}">live</text>'
        )

    title = (
        f'<text x="{pad}" y="94" font-size="30" font-weight="600" letter-spacing="-.5" fill="{INK}">'
        f'{esc(p["title"])}</text>'
        + path(pen.squiggle(pad + 1, pad + 64, 108, amp=2.4, step=8), fill="none", stroke=accent,
               stroke_width="2.4", stroke_linecap="round")
    )

    x, y = pad, h - 56
    pills = []
    for tag in p["tags"][:5]:
        pw = text_width(tag, 12) + 24
        pills.append(
            path(pen.rrect(x, y, pw, 28, 14, wob=0.6), fill=PILL, stroke=BORDER, stroke_width="1.6")
            + f'<text x="{x + pw / 2:.1f}" y="{y + 18.5}" text-anchor="middle" font-size="12" fill="{INK}">'
              f'{esc(tag)}</text>'
        )
        x += pw + 8
    if x > w - pad + 8:
        print(f"Warning: tags for '{p['title']}' overflow the card; drop one.")

    art, blobs = DOODLES[p["slug"]](pen, accent)
    doodle = inked("art", art, blobs, transform="translate(326 44) scale(.96)")

    return (
        svg_open(w, h, f"{p['title']}: {p['desc']}") + style_block() + paper(w, h, p["slug"] + "-page")
        + '<g clip-path="url(#page)">' + doodle + sticker + title + desc + "".join(pills) + "</g></svg>\n"
    )


# ----------------------------------------------------------------------------
# Section headers and the README grid
# ----------------------------------------------------------------------------

def build_header(text, accent):
    w, h = 1000, 72
    pen = Pen(text)
    tw = text_width(text, 28, bold=True)
    return (
        svg_open(w, h, text) + style_block()
        + path(sparkle(20, 34, 11), fill=accent)
        + f'<text x="44" y="45" font-size="28" font-weight="600" letter-spacing="-.3" fill="{INK}">{esc(text)}</text>'
        + path(pen.squiggle(46, 46 + min(tw, 260) * 0.55, 61, amp=2.6, step=9), fill="none", stroke=accent,
               stroke_width="3", stroke_linecap="round")
        + "</svg>\n"
    )


def build_grid():
    rows = []
    for i in range(0, len(PROJECTS), 2):
        cells = []
        for p in PROJECTS[i:i + 2]:
            img = f'<img src="assets/cards/{p["slug"]}.svg" alt="{esc(p["title"])}" width="100%"/>'
            body = f'<a href="{p["url"]}">{img}</a>' if p.get("url") else img
            cells.append(f'    <td width="50%">\n      {body}\n    </td>')
        rows.append("  <tr>\n" + "\n".join(cells) + "\n  </tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>\n"


def write(rel, text):
    full = os.path.join(OUT_DIR, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    if len(PROJECTS) % 2:
        print("Note: an odd number of projects leaves the last grid row half empty.")
    write("hero.svg", build_hero())
    for i, p in enumerate(PROJECTS):
        write(f'cards/{p["slug"]}.svg', build_card(p, ACCENTS[i % len(ACCENTS)]))
    for slug, text, accent in HEADERS:
        write(f"headers/{slug}.svg", build_header(text, accent))
    write("projects-grid.md", build_grid())
    print(f"Wrote hero.svg, {len(PROJECTS)} cards and {len(HEADERS)} headers to {OUT_DIR}")


if __name__ == "__main__":
    main()
