"""
Shared look for every SVG in this profile: a dark dotted sketchbook page,
chalk-white hand-drawn lines, and pastel marker blobs. Where a line crosses a
blob it switches to dark ink, like a doodle drawn over a highlighter mark.

Used by build_assets.py and scripts/generate_activity.py. Standard library only.
"""

import base64
import html
import math
import os
import random

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------

PAPER = "#16161a"    # card and banner background
DOTS = "#ffffff"     # notebook dot grid, drawn very faint
BORDER = "#3a3a43"
INK = "#f3efe6"      # chalk lines and main text
MUTED = "#a9a59c"
DARK = "#141417"     # ink on top of a pastel blob
PILL = "#1f1f25"

YELLOW = "#ffd36e"
MINT = "#86e3b9"
CORAL = "#ff8f80"
LAVENDER = "#b7a5ff"
SKY = "#86c8ff"
PEACH = "#ffb98a"

FONT_STACK = "Poppins, 'Segoe UI', Helvetica, Arial, sans-serif"
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts")


def esc(s):
    return html.escape(s, quote=True)


def font_css():
    """Embed Poppins so the SVG renders the same everywhere (GitHub blocks web fonts in images)."""
    faces = []
    for weight, fname in ((400, "Poppins-Regular.latin.woff2"), (600, "Poppins-SemiBold.latin.woff2")):
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            return ""  # falls back to system fonts
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        faces.append(
            "@font-face{font-family:'Poppins';font-weight:%d;font-style:normal;"
            "src:url(data:font/woff2;base64,%s) format('woff2');}" % (weight, b64)
        )
    return "".join(faces)


# Rough Poppins advance widths in em, good enough to size highlights and pills.
_NARROW = set("iIjl.,'!|:;")
_SEMI = set("frt()-/ ")
_WIDE = set("mwMW")


def text_width(s, size, bold=False):
    em = 0.0
    for ch in s:
        if ch in _NARROW:
            em += 0.27
        elif ch in _SEMI:
            em += 0.36
        elif ch in _WIDE:
            em += 0.9
        elif ch.isupper() or ch.isdigit():
            em += 0.66
        else:
            em += 0.58
    return em * size * (1.04 if bold else 1.0)


# ----------------------------------------------------------------------------
# Hand-drawn shapes
# ----------------------------------------------------------------------------

def _f(v):
    return f"{v:.1f}"


def smooth_path(pts, closed=False):
    """Catmull-Rom spline through pts, as cubic Beziers."""
    n = len(pts)
    P = (pts[-1:] + pts + pts[:2]) if closed else ([pts[0]] + pts + [pts[-1]])
    d = [f"M{_f(P[1][0])} {_f(P[1][1])}"]
    for i in range(1, (n if closed else n - 1) + 1):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}")
    if closed:
        d.append("Z")
    return "".join(d)


class Pen:
    """Draws slightly wobbly shapes. A fixed seed keeps every rebuild identical."""

    def __init__(self, seed):
        self.r = random.Random(seed)

    def j(self, a):
        return self.r.uniform(-a, a)

    def line(self, x1, y1, x2, y2, wob=1.2):
        mx, my = (x1 + x2) / 2 + self.j(wob), (y1 + y2) / 2 + self.j(wob)
        return f"M{_f(x1)} {_f(y1)}Q{_f(mx)} {_f(my)} {_f(x2)} {_f(y2)}"

    def curve(self, pts, wob=0.8):
        pts = [pts[0]] + [(x + self.j(wob), y + self.j(wob)) for x, y in pts[1:-1]] + [pts[-1]]
        return smooth_path(pts)

    def poly(self, pts, closed=True, wob=0.7):
        pts = [(x + self.j(wob), y + self.j(wob)) for x, y in pts]
        d = f"M{_f(pts[0][0])} {_f(pts[0][1])}" + "".join(f"L{_f(x)} {_f(y)}" for x, y in pts[1:])
        return d + ("Z" if closed else "")

    def circle(self, cx, cy, r, wob=0.04, n=9):
        """A circle drawn in one stroke that overshoots its start a little."""
        a0 = self.r.uniform(0, 2 * math.pi)
        pts = []
        for i in range(n + 2):
            a = a0 + 2 * math.pi * i / n
            rr = r * (1 + self.j(wob))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        a = a0 + 2 * math.pi * (n + 1.35) / n
        pts.append((cx + r * 0.97 * math.cos(a), cy + r * 0.97 * math.sin(a)))
        return smooth_path(pts)

    def blob(self, cx, cy, r, var=0.16, n=8):
        a0 = self.r.uniform(0, 2 * math.pi)
        pts = []
        for i in range(n):
            a = a0 + 2 * math.pi * i / n
            rr = r * (1 + self.j(var))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return smooth_path(pts, closed=True)

    def cloud(self, cx, cy, r, bumps=7):
        """Bumpy cloud or tree-canopy outline: small outward arcs between points on a circle."""
        a0 = self.r.uniform(0, 2 * math.pi)
        pts = []
        for i in range(bumps):
            a = a0 + 2 * math.pi * (i + self.j(0.12)) / bumps
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d = f"M{_f(pts[0][0])} {_f(pts[0][1])}"
        for i in range(bumps):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % bumps]
            rb = math.hypot(x2 - x1, y2 - y1) * 0.6
            d += f"A{_f(rb)} {_f(rb)} 0 0 1 {_f(x2)} {_f(y2)}"
        return d + "Z"

    def rrect(self, x, y, w, h, rad, wob=0.9):
        j = self.j
        e = lambda x1, y1, x2, y2: f"Q{_f((x1 + x2) / 2 + j(wob))} {_f((y1 + y2) / 2 + j(wob))} {_f(x2)} {_f(y2)}"
        return (
            f"M{_f(x + rad)} {_f(y)}"
            + e(x + rad, y, x + w - rad, y) + f"Q{_f(x + w)} {_f(y)} {_f(x + w)} {_f(y + rad)}"
            + e(x + w, y + rad, x + w, y + h - rad) + f"Q{_f(x + w)} {_f(y + h)} {_f(x + w - rad)} {_f(y + h)}"
            + e(x + w - rad, y + h, x + rad, y + h) + f"Q{_f(x)} {_f(y + h)} {_f(x)} {_f(y + h - rad)}"
            + e(x, y + h - rad, x, y + rad) + f"Q{_f(x)} {_f(y)} {_f(x + rad + 2 + j(1))} {_f(y + j(0.8))}"
        )

    def squiggle(self, x1, x2, y, amp=3.0, step=9.0):
        pts, x, k = [], x1, 0
        while x < x2:
            pts.append((x, y + (amp if k % 2 else -amp) + self.j(0.6)))
            x += step
            k += 1
        pts.append((x2, y))
        return smooth_path(pts)

    def star(self, cx, cy, r, points=5, inner=0.47, rot=-90):
        pts = []
        for i in range(points * 2):
            a = math.radians(rot + 180 * i / points)
            rr = (r if i % 2 == 0 else r * inner) * (1 + self.j(0.05))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return self.poly(pts, wob=0.3)

    def arrow(self, pts, head=9):
        d = self.curve(pts, wob=1.5)
        (ax, ay), (bx, by) = pts[-2], pts[-1]
        ang = math.atan2(by - ay, bx - ax)
        h1 = (bx - head * math.cos(ang - 0.5), by - head * math.sin(ang - 0.5))
        h2 = (bx - head * math.cos(ang + 0.5), by - head * math.sin(ang + 0.5))
        return d + f"M{_f(h1[0])} {_f(h1[1])}L{_f(bx)} {_f(by)}L{_f(h2[0])} {_f(h2[1])}"


def sparkle(cx, cy, r):
    """Four-point twinkle shape."""
    return (
        f"M{_f(cx)} {_f(cy - r)}Q{_f(cx)} {_f(cy)} {_f(cx + r)} {_f(cy)}"
        f"Q{_f(cx)} {_f(cy)} {_f(cx)} {_f(cy + r)}Q{_f(cx)} {_f(cy)} {_f(cx - r)} {_f(cy)}"
        f"Q{_f(cx)} {_f(cy)} {_f(cx)} {_f(cy - r)}Z"
    )


def path(d, **attrs):
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}"{extra}/>'


# ----------------------------------------------------------------------------
# Page pieces
# ----------------------------------------------------------------------------

def style_block(extra=""):
    return (
        "<style>"
        f"{font_css()}"
        f"text{{font-family:{FONT_STACK};}}"
        ".tw{animation:tw 3.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}"
        "@keyframes tw{0%,100%{opacity:1;transform:scale(1);}50%{opacity:.35;transform:scale(.7);}}"
        "@media (prefers-reduced-motion:reduce){.tw{animation:none;}}"
        f"{extra}"
        "</style>"
    )


def paper(w, h, seed, rx=16):
    """Background page with a faint dot grid and a hand-drawn border."""
    pen = Pen(seed)
    return (
        f'<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="11" cy="11" r="1.1" fill="{DOTS}" fill-opacity=".07"/></pattern>'
        f'<clipPath id="page"><rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{rx}"/></clipPath></defs>'
        f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{rx}" fill="{PAPER}"/>'
        f'<rect x="2" y="2" width="{w - 4}" height="{h - 4}" rx="{rx}" fill="url(#dots)"/>'
        + path(pen.rrect(3, 3, w - 6, h - 6, rx, wob=1.4), fill="none", stroke=BORDER, stroke_width="2",
               stroke_linecap="round")
    )


def inked(uid, art, blobs, transform=""):
    """
    Draws `art` (strokes in currentColor) over pastel `blobs` [(path, colour)].
    The art is drawn twice: chalk everywhere, then dark ink clipped to the blobs.
    """
    fills = "".join(path(d, fill=c) for d, c in blobs)
    clip = "".join(path(d) for d, _ in blobs)
    t = f' transform="{transform}"' if transform else ""
    return (
        f'<defs><g id="{uid}" fill="none" stroke="currentColor" stroke-width="2.4" '
        f'stroke-linecap="round" stroke-linejoin="round">{art}</g>'
        f'<clipPath id="{uid}-c">{clip}</clipPath></defs>'
        f'<g{t}>{fills}<use href="#{uid}" color="{INK}"/>'
        f'<g clip-path="url(#{uid}-c)"><use href="#{uid}" color="{DARK}"/></g></g>'
    )
