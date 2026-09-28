#!/usr/bin/env python3
"""
Renders a "star map" of the last year of GitHub contributions.
Each day is a star; busier days are bigger and brighter.

Usage:
    python generate_activity.py calendar.json out.svg

calendar.json is the raw output of the GitHub GraphQL query used in
.github/workflows/activity.yml (contributionCalendar).
Standard library only.
"""

import base64
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "fonts")

VOID = "#000000"
LINE = "#262626"
TEXT = "#ededed"
MUTED = "#a1a1a1"
BLUE = "#0070f3"
FONT_STACK = "Geist, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def font_css():
    faces = []
    for weight, fname in ((400, "Geist-Regular.subset.woff2"), (600, "Geist-SemiBold.subset.woff2")):
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            return ""
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        faces.append(
            "@font-face{font-family:'Geist';font-weight:%d;font-style:normal;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, b64)
        )
    return "".join(faces)


def load_calendar(path):
    raw = json.load(open(path, encoding="utf-8"))
    return raw["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level_thresholds(counts):
    """Quartiles over the non-zero days, so a few huge days don't flatten everything."""
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return (1, 2, 3)
    pick = lambda q: nz[min(len(nz) - 1, int(len(nz) * q))]
    return (pick(0.25), pick(0.5), pick(0.75))


def level_of(c, t):
    if c <= 0:
        return 0
    if c <= t[0]:
        return 1
    if c <= t[1]:
        return 2
    if c <= t[2]:
        return 3
    return 4


# star look per level: (radius, fill)
STAR = {
    0: (1.2, "#2a2a2a"),
    1: (2.0, "#6b6b6b"),
    2: (2.8, "#a1a1a1"),
    3: (3.4, "#ededed"),
    4: (3.8, "#ffffff"),
}


def build(cal):
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    n = len(weeks)

    W, H = 1000, 236
    x0, x1 = 40, 960
    y0 = 92
    pitch = (x1 - x0) / n

    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    th = level_thresholds(counts)

    stars, labels = [], []

    # month labels: one per month change; drop a label if the next one is under 3 columns away
    cands, last_month = [], None
    for wi, week in enumerate(weeks):
        if not week["contributionDays"]:
            continue
        month = int(week["contributionDays"][0]["date"][5:7]) - 1
        if month != last_month:
            cands.append((wi, month))
            last_month = month
    for i, (wi, month) in enumerate(cands):
        nxt = cands[i + 1][0] if i + 1 < len(cands) else None
        if (nxt is not None and nxt - wi < 3) or wi >= n - 2:
            continue
        labels.append(
            f'<text x="{x0 + wi * pitch:.1f}" y="76" font-size="11" fill="{MUTED}">{MONTHS[month]}</text>'
        )

    for wi, week in enumerate(weeks):
        days = week["contributionDays"]
        if not days:
            continue

        for d in days:
            lv = level_of(d["contributionCount"], th)
            r, fill = STAR[lv]
            cx = x0 + wi * pitch + pitch / 2
            cy = y0 + d["weekday"] * pitch + pitch / 2
            rnd = random.Random(d["date"])
            tw = ""
            if lv >= 3:
                dur, delay = rnd.uniform(3.5, 7), rnd.uniform(0, 6)
                tw = f' class="tw" style="animation-duration:{dur:.1f}s;animation-delay:{delay:.1f}s"'

            if lv == 4:
                stars.append(
                    f'<g{tw}>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="15" fill="url(#glow4)"/>'
                    f'<path d="M{cx-9:.1f} {cy:.1f}H{cx+9:.1f}M{cx:.1f} {cy-9:.1f}V{cy+9:.1f}" stroke="#fff" stroke-opacity=".55" stroke-width="1" stroke-linecap="round"/>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>'
                    f'</g>'
                )
            elif lv == 3:
                stars.append(
                    f'<g{tw}>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="10" fill="url(#glow3)"/>'
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>'
                    f'</g>'
                )
            else:
                stars.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>')

    # legend (right aligned)
    ly = 46
    legend = [f'<text x="{x1}" y="{ly}" text-anchor="end" font-size="12" fill="{MUTED}">More</text>']
    cx = x1 - 38
    for lv in (4, 3, 2, 1, 0):
        r, fill = STAR[lv]
        legend.append(f'<circle cx="{cx}" cy="{ly-4}" r="{max(r, 1.6)}" fill="{fill}"/>')
        cx -= 16
    legend.append(f'<text x="{cx - 2}" y="{ly}" text-anchor="end" font-size="12" fill="{MUTED}">Less</text>')

    total_txt = f"{total:,}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{total_txt} public contributions in the last year">
  <style>
    {font_css()}
    text {{ font-family: {FONT_STACK}; }}
    .tw {{ animation: tw ease-in-out infinite; }}
    @keyframes tw {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .45; }} }}
    @media (prefers-reduced-motion: reduce) {{ .tw {{ animation: none; }} }}
  </style>
  <defs>
    <radialGradient id="glow3"><stop offset="0" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
    <radialGradient id="glow4"><stop offset="0" stop-color="{BLUE}" stop-opacity=".65"/><stop offset=".5" stop-color="{BLUE}" stop-opacity=".18"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  </defs>
  <rect width="{W}" height="{H}" rx="12" fill="{VOID}"/>
  <rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="11.5" fill="none" stroke="{LINE}"/>
  <text x="{x0}" y="46" font-size="16"><tspan font-weight="600" fill="{TEXT}">{total_txt}</tspan><tspan fill="{MUTED}"> public contributions in the last year</tspan></text>
  {''.join(legend)}
  {''.join(labels)}
  {''.join(stars)}
</svg>
"""


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: generate_activity.py calendar.json out.svg")
    cal = load_calendar(sys.argv[1])
    svg = build(cal)
    os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
    open(sys.argv[2], "w", encoding="utf-8").write(svg)
    print(f"Wrote {sys.argv[2]} ({cal['totalContributions']} contributions)")


if __name__ == "__main__":
    main()
