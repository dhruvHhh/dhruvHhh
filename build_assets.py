#!/usr/bin/env python3
"""
Generates the hero banner and project cards for a GitHub profile README.
Theme: deep space in Vercel's neutral palette, with Geist embedded in each SVG.

Usage:
    1. Edit the CONFIG block below.
    2. python build_assets.py
    3. Commit assets/ and README.md.

Standard library only.
"""

import base64
import html
import os
import random
import textwrap

# ----------------------------------------------------------------------------
# CONFIG - edit this part
# ----------------------------------------------------------------------------

NAME = "Dhruv Honwad"
TITLE = "Full Stack AI Engineer"
TAGLINE = "React, FastAPI and RAG systems. SIH 2025 Grand Finalist."

# Accent colours cycle across project cards (Vercel's brand set).
ACCENTS = ["#0070f3", "#ff0080", "#50e3c2", "#7928ca", "#f5a623"]

# If the number of projects is odd, the last card is drawn full width.
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
        "slug": "prepview",
        "kind": "AI platform",
        "title": "PrepView",
        "desc": "Proctored mock interviews with video answers and AI scoring, a coding round, and an ATS resume analyzer.",
        "tags": ["React", "TypeScript", "Node.js", "Gemini", "Deepgram"],
        "url": "https://github.com/dhruvHhh/PrepView",
        "live": False,
    },
    {
        "slug": "news",
        "kind": "SIH 2025 mobile app",
        "title": "N.E.W.S",
        "desc": "Offline-first health reports with live maps, a Gemini medical assistant and 12 regional languages.",
        "tags": ["React Native", "Expo", "Node.js", "Firebase"],
        "url": "https://github.com/dhruvHhh/sih2025",
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
        # No public repo yet. Set "url" to link it, or leave None for an unlinked card.
        "slug": "now-ai",
        "kind": "Amazon HackOn",
        "title": "Now AI",
        "desc": "AI-native quick-commerce assistant. XGBoost predicts 30-day reorders (1.1-day MAE), and an Alexa skill on AWS Lambda takes voice orders into a Bedrock-powered cart.",
        "tags": ["Python", "SageMaker", "XGBoost", "Lambda", "Alexa"],
        "url": None,
        "live": False,
    },
]

# ----------------------------------------------------------------------------
# Tokens (Vercel neutrals)
# ----------------------------------------------------------------------------

VOID = "#000000"
LINE = "#262626"
LINE_SOFT = "#1a1a1a"
TEXT = "#ededed"
MUTED = "#a1a1a1"
GREEN = "#50e3c2"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "assets")
FONT_DIR = os.path.join(HERE, "fonts")

FONT_STACK = "Geist, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def esc(s):
    return html.escape(s, quote=True)


def font_css():
    """Embed the subset Geist files so the SVG renders the same everywhere."""
    faces = []
    for weight, fname in ((400, "Geist-Regular.subset.woff2"), (600, "Geist-SemiBold.subset.woff2")):
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            return ""  # falls back to system fonts
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        faces.append(
            "@font-face{font-family:'Geist';font-weight:%d;font-style:normal;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, b64)
        )
    return "".join(faces)


FONTS = font_css()


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------

def ellipse_path(rx, ry):
    return f"M{rx},0 A{rx},{ry} 0 1,1 {-rx},0 A{rx},{ry} 0 1,1 {rx},0 Z"


def build_hero():
    w, h = 1000, 360
    cx, cy, tilt = 780, 190, -18
    ratio = 0.36
    rings = [110, 200, 300, 410]

    rnd = random.Random(11)
    stars = []
    for _ in range(46):
        x, y = rnd.uniform(12, w - 12), rnd.uniform(12, h - 12)
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        o = rnd.uniform(0.25, 0.75)
        dur, delay = rnd.uniform(3, 8), rnd.uniform(0, 6)
        stars.append(
            f'<circle class="tw" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#fff" opacity="{o:.2f}" '
            f'style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"/>'
        )

    ring_svg = "".join(
        f'<ellipse rx="{r}" ry="{r*ratio:.1f}" fill="none" stroke="{LINE}" stroke-width="1"/>'
        for r in rings
    )

    # (ring index, colour, radius, seconds per orbit, phase 0..1)
    planets = [
        (0, "#ededed", 2.6, 26, 0.10),
        (1, "#0070f3", 5.0, 48, 0.62),
        (2, "#ff0080", 4.0, 80, 0.30),
        (2, "#50e3c2", 2.4, 80, 0.86),
        (3, "#7928ca", 5.5, 130, 0.05),
    ]
    planet_svg = []
    for ri, col, pr, dur, phase in planets:
        r = rings[ri]
        d = ellipse_path(r, r * ratio)
        planet_svg.append(
            f'<g><circle r="{pr*3.4:.1f}" fill="url(#g-{col[1:]})"/><circle r="{pr}" fill="{col}"/>'
            f'<animateMotion dur="{dur}s" begin="{-dur*phase:.1f}s" repeatCount="indefinite" path="{d}"/></g>'
        )

    glow_defs = "".join(
        f'<radialGradient id="g-{c[1:]}"><stop offset="0" stop-color="{c}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>'
        for c in ("#ededed", "#0070f3", "#ff0080", "#50e3c2", "#7928ca")
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(NAME)}, {esc(TITLE)}">
  <style>
    {FONTS}
    text {{ font-family: {FONT_STACK}; }}
    .tw {{ animation: tw ease-in-out infinite; }}
    @keyframes tw {{ 0%,100% {{ opacity: .12; }} 50% {{ opacity: .9; }} }}
    @media (prefers-reduced-motion: reduce) {{ .tw {{ animation: none; }} }}
  </style>
  <defs>
    {glow_defs}
    <radialGradient id="neb-b"><stop offset="0" stop-color="#0070f3" stop-opacity=".20"/><stop offset="1" stop-color="#0070f3" stop-opacity="0"/></radialGradient>
    <radialGradient id="neb-v"><stop offset="0" stop-color="#7928ca" stop-opacity=".22"/><stop offset="1" stop-color="#7928ca" stop-opacity="0"/></radialGradient>
    <radialGradient id="neb-p"><stop offset="0" stop-color="#ff0080" stop-opacity=".14"/><stop offset="1" stop-color="#ff0080" stop-opacity="0"/></radialGradient>
    <radialGradient id="sun"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset=".08" stop-color="#fff" stop-opacity=".9"/><stop offset=".22" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{VOID}" stop-opacity="1"/>
      <stop offset=".42" stop-color="{VOID}" stop-opacity=".92"/>
      <stop offset=".66" stop-color="{VOID}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="clip"><rect width="{w}" height="{h}" rx="12"/></clipPath>
  </defs>

  <g clip-path="url(#clip)">
    <rect width="{w}" height="{h}" fill="{VOID}"/>
    <ellipse cx="{cx-70}" cy="{cy+30}" rx="330" ry="210" fill="url(#neb-v)"/>
    <ellipse cx="{cx+60}" cy="{cy-40}" rx="300" ry="170" fill="url(#neb-b)"/>
    <ellipse cx="{cx+20}" cy="{cy+90}" rx="220" ry="120" fill="url(#neb-p)"/>
    {''.join(stars)}
    <g transform="translate({cx} {cy}) rotate({tilt})">
      {ring_svg}
      <circle r="64" fill="url(#sun)"/>
      {''.join(planet_svg)}
    </g>
    <rect width="{w}" height="{h}" fill="url(#fade)"/>
  </g>
  <rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="11.5" fill="none" stroke="{LINE}"/>

  <text x="56" y="168" font-size="64" font-weight="600" letter-spacing="-2.6" fill="{TEXT}">{esc(NAME)}</text>
  <text x="58" y="214" font-size="22" font-weight="400" fill="{TEXT}">{esc(TITLE)}</text>
  <text x="58" y="250" font-size="16" font-weight="400" fill="{MUTED}">{esc(TAGLINE)}</text>
</svg>
"""


# ----------------------------------------------------------------------------
# Cards
# ----------------------------------------------------------------------------

def build_card(p, accent, wide=False):
    w, h = (1000, 224) if wide else (490, 236)
    pad = 28

    # corner orbit motif, centred just outside the top-right corner
    ox, oy = w + 6, -6
    arcs = "".join(
        f'<circle cx="{ox}" cy="{oy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="1"/>'
        for r in (58, 94, 130)
    )
    import math
    ang = math.radians(146)
    px, py = ox + 94 * math.cos(ang), oy + 94 * math.sin(ang)
    ang2 = math.radians(112)
    qx, qy = ox + 58 * math.cos(ang2), oy + 58 * math.sin(ang2)
    ang3 = math.radians(162)
    sx, sy = ox + 130 * math.cos(ang3), oy + 130 * math.sin(ang3)

    lines = textwrap.wrap(p["desc"], width=96 if wide else 54)[:3]
    if len(lines) > 2:
        print(f"Warning: description for '{p['title']}' wraps to {len(lines)} lines; shorten it so it does not crowd the tags.")
    desc = "".join(
        f'<text x="{pad}" y="{124 + i*22}" font-size="15" fill="{MUTED}">{esc(l)}</text>'
        for i, l in enumerate(lines)
    )

    x, y = pad, h - 58
    pills = []
    for tag in p["tags"][:5]:
        pw = len(tag) * 6.9 + 26
        pills.append(
            f'<rect x="{x:.1f}" y="{y}" width="{pw:.1f}" height="28" rx="14" fill="#0a0a0a" stroke="{LINE}"/>'
            f'<text x="{x+pw/2:.1f}" y="{y+18.5}" text-anchor="middle" font-size="12.5" fill="{TEXT}">{esc(tag)}</text>'
        )
        x += pw + 8

    kind_w = len(p["kind"]) * 7.2
    live = ""
    if p.get("live"):
        lx = pad + kind_w + 14
        live = (
            f'<rect x="{lx:.1f}" y="24" width="52" height="22" rx="11" fill="#001a14" stroke="#0b3d31"/>'
            f'<circle cx="{lx+14:.1f}" cy="35" r="3.2" fill="{GREEN}"/>'
            f'<text x="{lx+23:.1f}" y="39.2" font-size="12" fill="{TEXT}">Live</text>'
        )

    acc_id = accent[1:]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(p['title'])}">
  <style>
    {FONTS}
    text {{ font-family: {FONT_STACK}; }}
  </style>
  <defs>
    <radialGradient id="a-{acc_id}"><stop offset="0" stop-color="{accent}" stop-opacity=".6"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
    <clipPath id="c"><rect width="{w}" height="{h}" rx="10"/></clipPath>
  </defs>
  <g clip-path="url(#c)">
    <rect width="{w}" height="{h}" fill="{VOID}"/>
    {arcs}
    <circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.6" fill="{MUTED}"/>
    <circle cx="{qx:.1f}" cy="{qy:.1f}" r="2.2" fill="{TEXT}"/>
    <circle cx="{px:.1f}" cy="{py:.1f}" r="16" fill="url(#a-{acc_id})"/>
    <circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="{accent}"/>
  </g>
  <rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="9.5" fill="none" stroke="{LINE}"/>
  <text x="{pad}" y="40" font-size="13" fill="{MUTED}">{esc(p['kind'])}</text>
  {live}
  <text x="{pad}" y="88" font-size="30" font-weight="600" letter-spacing="-1.1" fill="{TEXT}">{esc(p['title'])}</text>
  {desc}
  {''.join(pills)}
</svg>
"""


def build_grid():
    rows = []
    n = len(PROJECTS)
    for i in range(0, n, 2):
        chunk = PROJECTS[i:i + 2]
        span = ' colspan="2"' if len(chunk) == 1 else ' width="50%"'
        cells = []
        for p in chunk:
            img = f'<img src="assets/cards/{p["slug"]}.svg" alt="{esc(p["title"])}" width="100%"/>'
            body = f'<a href="{p["url"]}">{img}</a>' if p.get("url") else img
            cells.append(
                f'    <td{span}>\n'
                f'      {body}\n'
                f'    </td>'
            )
        rows.append("  <tr>\n" + "\n".join(cells) + "\n  </tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>\n"


def main():
    os.makedirs(os.path.join(OUT_DIR, "cards"), exist_ok=True)
    open(os.path.join(OUT_DIR, "hero.svg"), "w", encoding="utf-8").write(build_hero())
    for i, p in enumerate(PROJECTS):
        wide = (len(PROJECTS) % 2 == 1 and i == len(PROJECTS) - 1)
        svg = build_card(p, ACCENTS[i % len(ACCENTS)], wide)
        open(os.path.join(OUT_DIR, "cards", f'{p["slug"]}.svg'), "w", encoding="utf-8").write(svg)
    open(os.path.join(OUT_DIR, "projects-grid.md"), "w", encoding="utf-8").write(build_grid())
    print(f"Wrote hero.svg and {len(PROJECTS)} cards to {OUT_DIR}")
    if not FONTS:
        print("Note: fonts/ not found, using system fonts instead of Geist.")


if __name__ == "__main__":
    main()
