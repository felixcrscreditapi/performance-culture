#!/usr/bin/env python3
"""
Generate the cinematic SVG "Bildwelten" for Performance Culture.
Pure standard library — no external dependencies.

Each scene shares an atmospheric base (deep violet gradient + turbulence haze +
volumetric violet glow + vignette) and adds a distinct geometric motif per movement.

Run:  python3 scripts/generate-imagery.py
Out:  assets/img/{hero,m1,m2,m3,m4,interlude}.svg
"""
import math
import os
import random

W, H = 1600, 1000
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")

ACC = "#9D6BFF"
ACC2 = "#B99BFF"
ACC3 = "#D6C7FF"


def head(seed, glow_cx=50, glow_cy=58, glow_op=0.55, hue="0.62 0.42 1.0"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
   <stop offset="0" stop-color="#160c2a"/>
   <stop offset="0.5" stop-color="#100a1e"/>
   <stop offset="1" stop-color="#07050e"/>
 </linearGradient>
 <radialGradient id="glow" cx="{glow_cx}%" cy="{glow_cy}%" r="62%">
   <stop offset="0" stop-color="{ACC}" stop-opacity="{glow_op}"/>
   <stop offset="0.38" stop-color="#5a2ea8" stop-opacity="0.20"/>
   <stop offset="1" stop-color="#0a0714" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="vig" cx="50%" cy="44%" r="78%">
   <stop offset="0.5" stop-color="#07050e" stop-opacity="0"/>
   <stop offset="1" stop-color="#050308" stop-opacity="0.92"/>
 </radialGradient>
 <filter id="haze" x="-20%" y="-20%" width="140%" height="140%">
   <feTurbulence type="fractalNoise" baseFrequency="0.011 0.015" numOctaves="2" seed="{seed}" stitchTiles="stitch"/>
   <feColorMatrix values="0 0 0 0 {hue.split()[0]}  0 0 0 0 {hue.split()[1]}  0 0 0 0 {hue.split()[2]}  0 0 0 0.55 0"/>
   <feGaussianBlur stdDeviation="7"/>
   <feComponentTransfer><feFuncA type="linear" slope="0.55"/></feComponentTransfer>
 </filter>
 <filter id="blur1"><feGaussianBlur stdDeviation="1.6"/></filter>
 <filter id="blur6"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<rect width="{W}" height="{H}" fill="url(#haze)" opacity="0.5"/>
<rect width="{W}" height="{H}" fill="url(#glow)"/>
'''


def tail():
    return f'<rect width="{W}" height="{H}" fill="url(#vig)"/>\n</svg>\n'


def particles(rnd, n, ymin=0, ymax=H, bias_top=False):
    out = []
    for _ in range(n):
        x = rnd.uniform(0, W)
        if bias_top:
            y = ymin + (ymax - ymin) * (rnd.random() ** 1.7)
        else:
            y = rnd.uniform(ymin, ymax)
        r = rnd.uniform(0.5, 2.3)
        o = rnd.uniform(0.08, 0.6)
        col = ACC3 if rnd.random() < 0.4 else "#eaf1ff"
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" opacity="{o:.2f}"/>')
    return "\n".join(out)


def write(name, body):
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(body)
    print("wrote", os.path.relpath(path))


# ---------------------------------------------------------------- HERO / vista
def scene_hero():
    rnd = random.Random(11)
    s = head(seed=7, glow_cx=50, glow_cy=70, glow_op=0.5)
    hz = 660  # horizon
    s += f'<ellipse cx="{W/2}" cy="{hz}" rx="780" ry="120" fill="{ACC}" opacity="0.28" filter="url(#blur6)"/>\n'
    s += f'<rect x="0" y="{hz-1}" width="{W}" height="2" fill="{ACC2}" opacity="0.5"/>\n'
    vx, vy = W / 2, hz
    g = ['<g stroke="%s" stroke-width="1" fill="none">' % ACC, ]
    for i in range(-9, 10):
        x = W / 2 + i * 150
        g.append(f'<line x1="{x:.0f}" y1="{H}" x2="{vx:.0f}" y2="{vy:.0f}" opacity="{max(0.04,0.16-abs(i)*0.012):.3f}"/>')
    for j in range(1, 9):
        yy = hz + (H - hz) * (j / 9) ** 2.2
        g.append(f'<line x1="0" y1="{yy:.0f}" x2="{W}" y2="{yy:.0f}" opacity="{0.13-j*0.012:.3f}"/>')
    g.append("</g>")
    s += "\n".join(g) + "\n"
    s += '<g>' + particles(rnd, 70, 40, hz - 40, bias_top=True) + '</g>\n'
    s += tail()
    write("hero.svg", s)


# ----------------------------------------------- M.I  converging trajectories
def scene_m1():
    rnd = random.Random(3)
    s = head(seed=4, glow_cx=70, glow_cy=50, glow_op=0.6)
    fx, fy = W * 0.7, H * 0.48
    g = ['<g fill="none">']
    for i in range(26):
        ang = (i / 26) * math.tau
        rad = rnd.uniform(620, 1050)
        x0 = fx + math.cos(ang) * rad
        y0 = fy + math.sin(ang) * rad * 0.7
        o = rnd.uniform(0.05, 0.22)
        col = ACC2 if i % 4 == 0 else ACC
        g.append(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{fx:.0f}" y2="{fy:.0f}" stroke="{col}" stroke-width="1" opacity="{o:.2f}"/>')
    g.append("</g>")
    s += "\n".join(g) + "\n"
    s += f'<circle cx="{fx}" cy="{fy}" r="120" fill="{ACC}" opacity="0.22" filter="url(#blur6)"/>\n'
    s += f'<circle cx="{fx}" cy="{fy}" r="5" fill="#eaf1ff" opacity="0.95" filter="url(#blur1)"/>\n'
    s += f'<circle cx="{fx}" cy="{fy}" r="34" fill="none" stroke="{ACC2}" stroke-width="1.2" opacity="0.5"/>\n'
    s += '<g>' + particles(rnd, 46) + '</g>\n'
    s += tail()
    write("m1.svg", s)


# ---------------------------------------------------- M.II  network of peers
def scene_m2():
    rnd = random.Random(8)
    s = head(seed=12, glow_cx=42, glow_cy=46, glow_op=0.5)
    nodes = []
    for _ in range(26):
        nodes.append((rnd.uniform(120, W - 120), rnd.uniform(140, H - 160)))
    links = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            d = math.hypot(dx, dy)
            if d < 300:
                o = (1 - d / 300) * 0.28
                links.append(f'<line x1="{nodes[i][0]:.0f}" y1="{nodes[i][1]:.0f}" x2="{nodes[j][0]:.0f}" y2="{nodes[j][1]:.0f}" stroke="{ACC}" stroke-width="1" opacity="{o:.2f}"/>')
    s += '<g fill="none">' + "\n".join(links) + "</g>\n"
    for (x, y) in nodes:
        r = rnd.uniform(2.5, 5.5)
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r+6:.0f}" fill="{ACC}" opacity="0.10" filter="url(#blur1)"/>'
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{ACC3}" opacity="0.9"/>\n'
    s += '<g>' + particles(rnd, 34) + '</g>\n'
    s += tail()
    write("m2.svg", s)


# ----------------------------------------------- M.III  topographic contours
def scene_m3():
    rnd = random.Random(21)
    s = head(seed=19, glow_cx=50, glow_cy=64, glow_op=0.46)
    g = ['<g fill="none" stroke-width="1.1">']
    layers = 16
    for k in range(layers):
        base = 250 + k * 46
        amp = 26 + k * 3
        ph = rnd.uniform(0, math.tau)
        freq = rnd.uniform(2.2, 3.4)
        pts = []
        for px in range(0, W + 1, 24):
            t = px / W
            y = base + math.sin(t * math.pi * freq + ph) * amp + math.sin(t * math.pi * 7 + ph * 2) * (amp * 0.25)
            pts.append(f'{px},{y:.1f}')
        o = 0.06 + (k / layers) * 0.16
        col = ACC2 if k % 5 == 0 else ACC
        g.append(f'<polyline points="{" ".join(pts)}" stroke="{col}" opacity="{o:.2f}"/>')
    g.append("</g>")
    s += "\n".join(g) + "\n"
    s += '<g>' + particles(rnd, 30, 0, 260) + '</g>\n'
    s += tail()
    write("m3.svg", s)


# --------------------------------------------------- M.IV  ascent / 10x burst
def scene_m4():
    rnd = random.Random(5)
    s = head(seed=2, glow_cx=50, glow_cy=92, glow_op=0.7)
    cx, cy = W / 2, H * 1.02
    g = ['<g fill="none">']
    for i in range(30):
        ang = -math.pi / 2 + (i - 15) / 15 * (math.pi * 0.46)
        L = rnd.uniform(700, 1080)
        x1 = cx + math.cos(ang) * L
        y1 = cy + math.sin(ang) * L
        o = rnd.uniform(0.05, 0.20)
        col = ACC2 if i % 3 == 0 else ACC
        g.append(f'<line x1="{cx:.0f}" y1="{cy:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" stroke="{col}" stroke-width="1" opacity="{o:.2f}"/>')
    g.append("</g>")
    s += "\n".join(g) + "\n"
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="620" ry="240" fill="{ACC}" opacity="0.3" filter="url(#blur6)"/>\n'
    s += '<g>' + particles(rnd, 64, 60, H - 120, bias_top=True) + '</g>\n'
    s += tail()
    write("m4.svg", s)


# ------------------------------------------------------- INTERLUDE wide vista
def scene_interlude():
    rnd = random.Random(33)
    s = head(seed=14, glow_cx=50, glow_cy=52, glow_op=0.5)
    cx, cy = W / 2, H * 0.5
    for k in range(7):
        r = 160 + k * 130
        o = 0.18 - k * 0.02
        s += f'<ellipse cx="{cx}" cy="{cy}" rx="{r}" ry="{r*0.6:.0f}" fill="none" stroke="{ACC}" stroke-width="1" opacity="{max(0.03,o):.2f}"/>\n'
    s += f'<circle cx="{cx}" cy="{cy}" r="80" fill="{ACC}" opacity="0.25" filter="url(#blur6)"/>\n'
    s += f'<circle cx="{cx}" cy="{cy}" r="4" fill="#eaf1ff" opacity="0.95"/>\n'
    s += '<g>' + particles(rnd, 60) + '</g>\n'
    s += tail()
    write("interlude.svg", s)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    scene_hero()
    scene_m1()
    scene_m2()
    scene_m3()
    scene_m4()
    scene_interlude()
    print("done")
