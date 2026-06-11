#!/usr/bin/env python3
"""
Generate the "Story Night" Bildwelten for Performance Culture.
Pure standard library — no external dependencies.

A starlit night and a long philosophers' walk: deep midnight sky, stars,
moonlight, moonlit hills, a winding path, two figures in conversation,
constellations, and dawn breaking at the end of the journey.

Run:  python3 scripts/generate-imagery.py
Out:  assets/img/{hero,m1,m2,m3,m4,interlude}.svg
"""
import math
import os
import random

W, H = 1600, 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")

VIOLET = "#9D6BFF"
VIOLET2 = "#B99BFF"
STAR = "#eef0ff"
WARM = "#fff0c8"
GOLD = "#ffd98a"
DARK = "#05040c"


# ---------------------------------------------------------------- defs / base
def head(seed, glow_cx=50, glow_cy=66, glow_op=0.4, dawn=False):
    top, mid, bot = "#080616", "#0b0820", "#120c28"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
   <stop offset="0" stop-color="{top}"/>
   <stop offset="0.55" stop-color="{mid}"/>
   <stop offset="1" stop-color="{bot}"/>
 </linearGradient>
 <radialGradient id="glow" cx="{glow_cx}%" cy="{glow_cy}%" r="60%">
   <stop offset="0" stop-color="{VIOLET}" stop-opacity="{glow_op}"/>
   <stop offset="0.4" stop-color="#5a2ea8" stop-opacity="0.16"/>
   <stop offset="1" stop-color="#0a0714" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="moon" cx="50%" cy="50%" r="50%">
   <stop offset="0" stop-color="#fdfcff"/>
   <stop offset="0.7" stop-color="#e7ddff"/>
   <stop offset="1" stop-color="#c9b8ff"/>
 </radialGradient>
 <radialGradient id="moonglow" cx="50%" cy="50%" r="50%">
   <stop offset="0" stop-color="#e8deff" stop-opacity="0.5"/>
   <stop offset="1" stop-color="#e8deff" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="dawn" cx="50%" cy="100%" r="80%">
   <stop offset="0" stop-color="#ffd49a" stop-opacity="0.55"/>
   <stop offset="0.32" stop-color="#c77dff" stop-opacity="0.3"/>
   <stop offset="0.7" stop-color="#5a2ea8" stop-opacity="0.12"/>
   <stop offset="1" stop-color="#0a0714" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="vig" cx="50%" cy="46%" r="78%">
   <stop offset="0.5" stop-color="#07050e" stop-opacity="0"/>
   <stop offset="1" stop-color="#040308" stop-opacity="0.92"/>
 </radialGradient>
 <filter id="soft"><feGaussianBlur stdDeviation="3"/></filter>
 <filter id="soft9"><feGaussianBlur stdDeviation="9"/></filter>
 <filter id="haze" x="-20%" y="-20%" width="140%" height="140%">
   <feTurbulence type="fractalNoise" baseFrequency="0.012 0.016" numOctaves="2" seed="{seed}" stitchTiles="stitch"/>
   <feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.4  0 0 0 0 0.95  0 0 0 0.5 0"/>
   <feGaussianBlur stdDeviation="8"/>
   <feComponentTransfer><feFuncA type="linear" slope="0.4"/></feComponentTransfer>
 </filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#haze)" opacity="0.4"/>
<rect width="{W}" height="{H}" fill="url(#{"dawn" if dawn else "glow"})"/>
'''


def tail():
    return f'<rect width="{W}" height="{H}" fill="url(#vig)"/>\n</svg>\n'


def starfield(rnd, n, ymax=H, bright_every=11):
    out = []
    for _ in range(n):
        x = rnd.uniform(0, W)
        y = rnd.uniform(0, ymax)
        roll = rnd.random()
        col = GOLD if roll < 0.10 else (VIOLET2 if roll < 0.18 else STAR)
        if rnd.random() < 1.0 / bright_every:
            R = rnd.uniform(1.7, 3.0)
            o = rnd.uniform(0.7, 1.0)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R*4.5:.1f}" fill="{col}" opacity="{o*0.10:.2f}" filter="url(#soft)"/>')
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R:.1f}" fill="{col}" opacity="{o:.2f}"/>')
            s = R * 3.4
            out.append(f'<path d="M{x-s:.1f} {y:.1f} H{x+s:.1f} M{x:.1f} {y-s:.1f} V{y+s:.1f}" stroke="{col}" stroke-width="0.7" opacity="{o*0.45:.2f}"/>')
        else:
            r = rnd.uniform(0.4, 1.4)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="{rnd.uniform(0.25,0.85):.2f}"/>')
    return "<g>" + "\n".join(out) + "</g>\n"


def moon(cx, cy, r):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r*3.2:.0f}" fill="url(#moonglow)"/>\n'
        f'<circle cx="{cx}" cy="{cy}" r="{r:.0f}" fill="url(#moon)"/>\n'
        f'<circle cx="{cx+r*0.32:.0f}" cy="{cy-r*0.12:.0f}" r="{r*0.95:.0f}" fill="#0b0820" opacity="0.18"/>\n'
    )


def ridge(rnd, base_y, amp, fill, opacity=1.0, seed_pts=7):
    pts = [(0, base_y + rnd.uniform(-amp * 0.3, amp * 0.3))]
    for i in range(1, seed_pts):
        x = W * i / (seed_pts - 1)
        pts.append((x, base_y - rnd.uniform(0, amp)))
    d = f'M0 {H} L{pts[0][0]:.0f} {pts[0][1]:.0f} '
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]; x1, y1 = pts[i]
        mx = (x0 + x1) / 2
        d += f'Q {x0:.0f} {y0:.0f} {mx:.0f} {(y0+y1)/2:.0f} '
    d += f'L{W} {pts[-1][1]:.0f} L{W} {H} Z'
    return f'<path d="{d}" fill="{fill}" opacity="{opacity}"/>\n'


def trail(x0, y0, x1, y1, sway=140):
    """A winding luminous path from (x0,y0) bottom to (x1,y1) horizon."""
    mx = (x0 + x1) / 2 + sway
    my = (y0 + y1) / 2
    d = f'M{x0:.0f} {y0:.0f} Q {mx:.0f} {my:.0f} {x1:.0f} {y1:.0f}'
    return (
        f'<path d="{d}" fill="none" stroke="{VIOLET2}" stroke-width="7" opacity="0.10" filter="url(#soft)"/>\n'
        f'<path d="{d}" fill="none" stroke="#f3eeff" stroke-width="1.4" opacity="0.5" stroke-dasharray="2 9" stroke-linecap="round"/>\n'
    )


def figures(x, ground_y, h, gap=0.55):
    """Two robed silhouettes walking side by side."""
    def one(cx, hh):
        w = hh * 0.36
        hr = hh * 0.11
        hy = ground_y - hh * 0.86
        body = (f'M{cx-w*0.5:.1f} {ground_y:.1f} '
                f'C {cx-w*0.58:.1f} {ground_y-hh*0.5:.1f} {cx-hr*1.1:.1f} {ground_y-hh*0.72:.1f} {cx:.1f} {ground_y-hh*0.74:.1f} '
                f'C {cx+hr*1.1:.1f} {ground_y-hh*0.72:.1f} {cx+w*0.58:.1f} {ground_y-hh*0.5:.1f} {cx+w*0.5:.1f} {ground_y:.1f} Z')
        return (f'<path d="{body}" fill="{DARK}"/>'
                f'<circle cx="{cx:.1f}" cy="{hy:.1f}" r="{hr:.1f}" fill="{DARK}"/>'
                f'<path d="{body}" fill="none" stroke="{VIOLET2}" stroke-width="0.8" opacity="0.35"/>')
    dx = h * gap
    shadow = f'<ellipse cx="{x:.0f}" cy="{ground_y+3:.0f}" rx="{h*0.7:.0f}" ry="{h*0.06:.0f}" fill="#000" opacity="0.45" filter="url(#soft)"/>'
    return "<g>" + shadow + one(x - dx * 0.5, h) + one(x + dx * 0.5, h * 0.94) + "</g>\n"


def constellation(rnd, pts):
    seg = ['<g fill="none" stroke="%s" stroke-width="1" opacity="0.4">' % VIOLET2]
    for i in range(1, len(pts)):
        seg.append(f'<line x1="{pts[i-1][0]:.0f}" y1="{pts[i-1][1]:.0f}" x2="{pts[i][0]:.0f}" y2="{pts[i][1]:.0f}"/>')
    seg.append("</g>")
    dots = []
    for (px, py) in pts:
        dots.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="2.4" fill="#fff" opacity="0.95"/>')
        dots.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="6" fill="{VIOLET2}" opacity="0.22" filter="url(#soft)"/>')
    return "".join(seg) + "<g>" + "".join(dots) + "</g>\n"


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(body)
    print("wrote", os.path.relpath(path))


# ----------------------------------------------------- HERO  (the walk begins)
def scene_hero():
    rnd = random.Random(11)
    s = head(seed=7, glow_cx=50, glow_cy=84, glow_op=0.34)
    hz = 770
    s += starfield(rnd, 210, ymax=hz - 30)
    s += moon(rnd.uniform(1180, 1320), 250, 66)
    s += constellation(rnd, [(180, 210), (250, 150), (330, 210), (300, 300), (210, 300), (180, 210)])
    s += ridge(rnd, hz + 70, 90, "#0a0818", 1.0, 6)
    s += ridge(rnd, hz + 30, 70, "#070512", 1.0, 7)
    s += trail(W * 0.52, H, W * 0.5, hz + 6, sway=120)
    s += figures(W * 0.52, H - 96, 96)
    s += tail()
    write("hero.svg", s)


# ------------------------------------------------- INTERLUDE (the walk goes on)
def scene_interlude():
    rnd = random.Random(33)
    s = head(seed=14, glow_cx=50, glow_cy=70, glow_op=0.36)
    hz = 720
    # milky-way diagonal band
    s += '<g opacity="0.5" filter="url(#soft9)"><path d="M-50 240 Q 800 120 1660 360" stroke="#b9a6ff" stroke-width="120" fill="none" opacity="0.10"/></g>\n'
    s += starfield(rnd, 240, ymax=hz - 20, bright_every=9)
    s += moon(rnd.uniform(300, 380), 200, 40)
    s += ridge(rnd, hz + 80, 80, "#090717", 1.0, 6)
    s += ridge(rnd, hz + 36, 60, "#060410", 1.0, 7)
    s += trail(W * 0.46, H, W * 0.5, hz + 4, sway=200)
    s += tail()
    write("interlude.svg", s)


# ----------------------------------- M.I  Defining the Work (marking the route)
def scene_m1():
    rnd = random.Random(3)
    s = head(seed=4, glow_cx=64, glow_cy=80, glow_op=0.36)
    hz = 760
    s += starfield(rnd, 190, ymax=hz - 30)
    s += moon(280, 240, 50)
    s += ridge(rnd, hz + 70, 80, "#0a0818", 1.0, 6)
    s += ridge(rnd, hz + 26, 60, "#070512", 1.0, 7)
    s += trail(W * 0.42, H, W * 0.66, hz + 6, sway=150)
    # milestone markers along the path
    for i, t in enumerate([0.18, 0.34, 0.5, 0.66, 0.82]):
        px = W * (0.42 + (0.66 - 0.42) * t) + math.sin(t * math.pi) * 150
        py = H - (H - hz) * t - 10
        s += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="9" fill="{VIOLET}" opacity="0.22" filter="url(#soft)"/><circle cx="{px:.0f}" cy="{py:.0f}" r="3" fill="#fff" opacity="0.9"/>\n'
    s += tail()
    write("m1.svg", s)


# ------------------------------- M.II  Operating Together (two minds, one walk)
def scene_m2():
    rnd = random.Random(8)
    s = head(seed=12, glow_cx=44, glow_cy=72, glow_op=0.42)
    hz = 750
    s += starfield(rnd, 200, ymax=hz - 30, bright_every=9)
    s += moon(1280, 220, 58)
    # constellation arc above the two figures (the conversation)
    s += constellation(rnd, [(560, 330), (650, 250), (760, 230), (870, 270), (960, 350)])
    s += ridge(rnd, hz + 60, 80, "#0a0818", 1.0, 6)
    s += ridge(rnd, hz + 22, 56, "#060410", 1.0, 7)
    s += figures(W * 0.5, hz + 36, 150, gap=0.6)
    s += tail()
    write("m2.svg", s)


# ----------------------------- M.III  Leverage & Clarity (the high vantage)
def scene_m3():
    rnd = random.Random(21)
    s = head(seed=19, glow_cx=50, glow_cy=58, glow_op=0.34)
    hz = 560
    s += starfield(rnd, 240, ymax=hz - 10, bright_every=8)
    s += moon(820, 170, 46)
    # layered receding ridges -> sense of distance / clarity
    s += ridge(rnd, hz + 250, 70, "#0c0a1e", 1.0, 7)
    s += ridge(rnd, hz + 170, 80, "#090717", 1.0, 7)
    s += ridge(rnd, hz + 90, 90, "#070512", 1.0, 6)
    s += ridge(rnd, hz + 24, 70, "#04030c", 1.0, 6)
    # lone figures on the near ridge, looking out
    s += figures(W * 0.7, hz + 250, 84, gap=0.55)
    s += tail()
    write("m3.svg", s)


# ----------------------------------- M.IV  Beyond the Machine (dawn / summit)
def scene_m4():
    rnd = random.Random(5)
    s = head(seed=2, glow_cx=50, glow_cy=100, glow_op=0.4, dawn=True)
    hz = 720
    # stars thin out toward the warm horizon
    s += starfield(rnd, 150, ymax=hz - 120)
    # warm horizon band
    s += f'<rect x="0" y="{hz-4}" width="{W}" height="4" fill="#ffd9a0" opacity="0.35" filter="url(#soft)"/>\n'
    s += ridge(rnd, hz + 90, 110, "#0a0718", 1.0, 6)
    s += ridge(rnd, hz + 36, 80, "#060410", 1.0, 7)
    s += trail(W * 0.46, H, W * 0.52, hz + 6, sway=120)
    s += figures(W * 0.52, hz + 30, 120, gap=0.5)
    s += tail()
    write("m4.svg", s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    scene_hero()
    scene_interlude()
    scene_m1()
    scene_m2()
    scene_m3()
    scene_m4()
    print("done")
