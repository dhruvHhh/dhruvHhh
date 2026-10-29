#!/usr/bin/env python3
"""
Renders the last year of public GitHub contributions as a doodled calendar,
in the same sketchbook style as the rest of the profile (see doodle.py).
Each day is a hand-drawn mark; busier days get bigger marks and the busiest get a star.

Usage:
    python generate_activity.py calendar.json out.svg

calendar.json is the raw output of the GitHub GraphQL query used in
.github/workflows/activity.yml (contributionCalendar).
Standard library only.
"""

import json
import os
import sys

from doodle import BORDER, INK, MINT, MUTED, YELLOW, Pen, paper, path, style_block

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_calendar(path_):
    raw = json.load(open(path_, encoding="utf-8"))
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


def mark(lv, cx, cy, seed):
    """One day's doodle. Seeded by date, so a day keeps its shape between runs."""
    pen = Pen(seed)
    if lv == 0:
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.3" fill="{BORDER}"/>'
    if lv == 1:
        return path(pen.circle(cx, cy, 3.4, wob=0.08, n=6), fill="none", stroke=MINT, stroke_opacity=".75",
                    stroke_width="1.5", stroke_linecap="round")
    if lv == 2:
        return path(pen.blob(cx, cy, 4.4, var=0.14, n=6), fill=MINT, fill_opacity=".7")
    if lv == 3:
        return path(pen.blob(cx, cy, 6, var=0.12, n=7), fill=MINT)
    return (
        f'<g class="tw" style="animation-delay:{pen.r.uniform(0, 3.6):.1f}s">'
        + path(pen.star(cx, cy, 8.2), fill=YELLOW, stroke=YELLOW, stroke_width="1.4", stroke_linejoin="round")
        + "</g>"
    )


def build(cal):
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    n = len(weeks)

    W, H = 1000, 262
    x0, x1 = 44, 956
    y0 = 108
    pitch = (x1 - x0) / n
    pen = Pen("activity")

    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    th = level_thresholds(counts)

    # month labels: one per month change; drop a label if the next one is under 3 columns away
    labels, cands, last_month = [], [], None
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
            f'<text x="{x0 + wi * pitch:.1f}" y="94" font-size="12" fill="{MUTED}">{MONTHS[month]}</text>'
        )

    marks = []
    for wi, week in enumerate(weeks):
        for d in week["contributionDays"]:
            cx = x0 + wi * pitch + pitch / 2
            cy = y0 + d["weekday"] * pitch + pitch / 2
            marks.append(mark(level_of(d["contributionCount"], th), cx, cy, d["date"]))

    # legend (right aligned): less . o ● ● ★ more
    ly = 50
    legend = [f'<text x="{x1}" y="{ly + 4}" text-anchor="end" font-size="12" fill="{MUTED}">more</text>']
    cx = x1 - 50
    for lv in (4, 3, 2, 1, 0):
        legend.append(mark(lv, cx, ly, f"legend-{lv}"))
        cx -= 22
    legend.append(f'<text x="{cx + 6}" y="{ly + 4}" text-anchor="end" font-size="12" fill="{MUTED}">less</text>')

    total_txt = f"{total:,}"
    num_w = len(total_txt) * 20
    title = (
        f'<text x="{x0}" y="60" font-size="34" font-weight="600" fill="{INK}">{total_txt}</text>'
        + path(pen.squiggle(x0 + 1, x0 + num_w, 72, amp=2.2, step=8), fill="none", stroke=MINT,
               stroke_width="2.6", stroke_linecap="round")
        + f'<text x="{x0 + num_w + 14}" y="58" font-size="16" fill="{MUTED}">public contributions in the last year</text>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-label="{total_txt} public contributions in the last year">'
        + style_block() + paper(W, H, "activity-page")
        + '<g clip-path="url(#page)">' + title + "".join(legend) + "".join(labels) + "".join(marks)
        + "</g></svg>\n"
    )


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
