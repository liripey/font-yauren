"""Símbolos: moedas, matemática, sinais diversos, frações, setas."""
import math

from ..glyph import Glyph, clip, contours_bounds, transform_contours
from ..parts import ellipse, foot_serif, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import borrow, glyph
from . import lower as LC
from . import upper as UC
from .figures import tab_width
from .punct import rdot


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def shift(c, dx=0, dy=0):
    return transform_contours(c, dx=dx, dy=dy)


def scale(c, s, sy=None, dx=0, dy=0):
    return transform_contours(c, s, 0, 0, s if sy is None else sy, dx, dy)


def bounds(c):
    return contours_bounds(c)


# ------------------------------------------------------------- matemática

def mt(P):
    """Espessura de traço dos sinais matemáticos."""
    return P.hair * 0.62 + P.stem * 0.27


def axis(P):
    return round(P.cap * 0.45)


def span(P):
    return P.cn * 1.20 + P.stem * 0.2


def mpen(P):
    t = mt(P)
    return Pen(t / 2, t / 2)


def math_glyph(name, *unis):
    def deco(fn):
        def g_fn(g, P):
            W = tab_width(P)
            fn(g, P, W / 2, axis(P), span(P) / 2, mt(P))
            g.space(width=W, center=True)
        glyph(name, *unis)(g_fn)
        return fn
    return deco


@math_glyph("plus", 0x002B)
def plus(g, P, cx, ya, a, t):
    g.add(rect(cx - a, ya - t / 2, cx + a, ya + t / 2))
    g.add(rect(cx - t / 2, ya - a, cx + t / 2, ya + a))


@math_glyph("minus", 0x2212)
def minus(g, P, cx, ya, a, t):
    g.add(rect(cx - a, ya - t / 2, cx + a, ya + t / 2))


@math_glyph("multiply", 0x00D7)
def multiply(g, P, cx, ya, a, t):
    d = a * 0.74
    pen = mpen(P)
    g.add(stk(Path(cx - d, ya - d).l(cx + d, ya + d), pen))
    g.add(stk(Path(cx - d, ya + d).l(cx + d, ya - d), pen))


@math_glyph("divide", 0x00F7)
def divide(g, P, cx, ya, a, t):
    g.add(rect(cx - a, ya - t / 2, cx + a, ya + t / 2))
    r = t * 0.62 + rdot(P) * 0.30
    g.add(ellipse(cx, ya + a * 0.66, r, r))
    g.add(ellipse(cx, ya - a * 0.66, r, r))


def eq_gap(P, a):
    return a * 0.36 + mt(P) * 0.3


@math_glyph("equal", 0x003D)
def equal(g, P, cx, ya, a, t):
    e = eq_gap(P, a)
    g.add(rect(cx - a, ya + e - t / 2, cx + a, ya + e + t / 2))
    g.add(rect(cx - a, ya - e - t / 2, cx + a, ya - e + t / 2))


@math_glyph("notequal", 0x2260)
def notequal(g, P, cx, ya, a, t):
    equal(g, P, cx, ya, a, t)
    g.add(stk(Path(cx - a * 0.42, ya - a * 0.95).l(cx + a * 0.42, ya + a * 0.95), mpen(P)))


def chev(P, cx, ya, a, left=True, dy=0.0, k=0.78):
    pen = mpen(P)
    h = a * k
    if left:
        p = Path(cx + a, ya + h + dy).l(cx - a, ya + dy).l(cx + a, ya - h + dy)
    else:
        p = Path(cx - a, ya + h + dy).l(cx + a, ya + dy).l(cx - a, ya - h + dy)
    return stk(p, pen)


@math_glyph("less", 0x003C)
def less(g, P, cx, ya, a, t):
    g.add(chev(P, cx, ya, a * 0.92, True))


@math_glyph("greater", 0x003E)
def greater(g, P, cx, ya, a, t):
    g.add(chev(P, cx, ya, a * 0.92, False))


@math_glyph("lessequal", 0x2264)
def lessequal(g, P, cx, ya, a, t):
    g.add(chev(P, cx, ya, a * 0.92, True, dy=a * 0.30, k=0.62))
    g.add(rect(cx - a * 0.92, ya - a * 0.80 - t / 2, cx + a * 0.92, ya - a * 0.80 + t / 2))


@math_glyph("greaterequal", 0x2265)
def greaterequal(g, P, cx, ya, a, t):
    g.add(chev(P, cx, ya, a * 0.92, False, dy=a * 0.30, k=0.62))
    g.add(rect(cx - a * 0.92, ya - a * 0.80 - t / 2, cx + a * 0.92, ya - a * 0.80 + t / 2))


@math_glyph("plusminus", 0x00B1)
def plusminus(g, P, cx, ya, a, t):
    y = ya + a * 0.22
    b = a * 0.78
    g.add(rect(cx - a, y - t / 2, cx + a, y + t / 2))
    g.add(rect(cx - t / 2, y - b, cx + t / 2, y + b))
    g.add(rect(cx - a, y - b - a * 0.42 - t / 2, cx + a, y - b - a * 0.42 + t / 2))


def tilde_wave(P, cx, y, a, amp=None):
    t = mt(P)
    amp = a * 0.20 if amp is None else amp
    pen = Pen(t / 2 * 1.08, t / 2 * 0.92)
    p = Path(cx - a, y - amp * 0.75, d=55)
    p.c(cx - a * 0.45, y + amp, d=0)
    p.c(cx + a * 0.45, y - amp, d=0)
    p.c(cx + a, y + amp * 0.75, d=55)
    return stk(p, pen)


@math_glyph("asciitilde", 0x007E)
def asciitilde(g, P, cx, ya, a, t):
    g.add(tilde_wave(P, cx, ya, a))


@math_glyph("approxequal", 0x2248)
def approxequal(g, P, cx, ya, a, t):
    e = eq_gap(P, a) * 1.1
    g.add(tilde_wave(P, cx, ya + e, a))
    g.add(tilde_wave(P, cx, ya - e, a))


@math_glyph("logicalnot", 0x00AC)
def logicalnot(g, P, cx, ya, a, t):
    g.add(rect(cx - a, ya - t / 2 + a * 0.2, cx + a, ya + t / 2 + a * 0.2))
    g.add(rect(cx + a - t, ya - a * 0.45, cx + a, ya + a * 0.2))


@math_glyph("asciicircum", 0x005E)
def asciicircum(g, P, cx, ya, a, t):
    pen = mpen(P)
    b = a * 0.80
    top = P.cap
    p = Path(cx - b, top - b * 1.05).l(cx, top - t * 0.4).l(cx + b, top - b * 1.05)
    g.add(clip(stk(p, pen), rect(-1000, top, 3000, top + 300)))


@math_glyph("infinity", 0x221E)
def infinity(g, P, cx, ya, a, t):
    pen = Pen(t / 2 * 1.12, t / 2 * 0.85)
    h = a * 0.50
    w = a * 1.02
    for s in (1, -1):
        p = Path(cx, ya, d=(42 if s > 0 else 138))
        p.c(cx + s * w * 0.50, ya + h, d=(0 if s > 0 else 180))
        p.c(cx + s * w, ya, d=270)
        p.c(cx + s * w * 0.50, ya - h, d=(180 if s > 0 else 0))
        p.c(cx, ya, d=(138 if s > 0 else 42))
        g.add(stk(p, pen))


def pct_ovals(P, n):
    """Sinais de porcentagem/permilagem: n ovais + barra."""
    S, H, cap = P.stem, P.hair, P.cap
    pc = Pen((H * 0.95 + S * 0.20) / 2, H * 0.48, P.ang)
    ry = cap * 0.205 + S * 0.05
    rx = P.cn * 0.19 + S * 0.42
    gap = P.cn * 0.12 + S * 0.15
    out = []
    xs = [rx, 3 * rx + gap] + ([5 * rx + gap + max(24, S * 0.35)] if n == 3 else [])
    ys = [cap - ry, ry] + ([ry] if n == 3 else [])
    for ox, oy in zip(xs, ys):
        p = Path(ox + rx - pc.hh, oy, d=90).c(ox, oy + ry - pc.hv, d=180)
        p.c(ox - rx + pc.hh, oy, d=270).c(ox, oy - ry + pc.hv, d=0).close("c")
        out += stk(p, pc)
    x0, x1 = rx * 0.6, 3 * rx + gap - rx * 0.6
    out += stk(Path(x0, -6).l(x1 + rx * 0.2, cap + 6), Pen(H * 0.78 + S * 0.10, H * 0.5))
    return out


@glyph("percent", 0x0025)
def percent(g, P):
    g.add(pct_ovals(P, 2))
    g.space(P.sb * 1.1, P.sb * 1.1)


@glyph("perthousand", 0x2030)
def perthousand(g, P):
    g.add(pct_ovals(P, 3))
    g.space(P.sb * 1.1, P.sb * 1.1)


# ------------------------------------------------------------- operadores grandes

@glyph("partialdiff", 0x2202)
def partialdiff(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    _, pc = LC.pens(P)
    W = P.cn * 1.0 + P.curve * 1.6
    rb = S * 0.5 + 4
    t = 0.97
    p = Path(rb * 1.0 + 4, cap * 0.84, d=60, w=0.7)
    p.c(W * 0.50, cap + P.os - pc.hv, d=0, w=1.0)
    p.c(W - pc.hh, cap * 0.50, d=270, w=1.0)
    p.c(W * 0.48, -P.os + pc.hv, d=180, t=t)
    p.c(pc.hh, cap * 0.27, d=90, t=t)
    p.c(W * 0.50, cap * 0.55 - pc.hv, d=0, t=t)
    p.c(W - pc.hh * 1.2, cap * 0.38, d=-60, w=0.45)
    g.add(stk(p, pc))
    g.add(ellipse(rb + 4, cap * 0.82, rb, rb * 1.04))
    g.space(P.sb * 1.1, P.sb * 1.1)


@glyph("increment", 0x2206)
def increment(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.40 + S * 1.2
    thin, thick = H * 1.25, S * 0.92
    top = cap + P.osC * 0.6
    xa = W / 2
    bt = UC.arm_t(P, 1.2)
    arms = (quad((0, 0), (thin, 0), (xa + thin / 2, top), (xa - thin / 2, top)) +
            quad((W - thick, 0), (W, 0), (xa + thin / 2, top), (xa + thin / 2 - thick, top)))
    from ..parts import halfplane
    g.add(clip(arms, halfplane((0, 0), (xa - thin / 2, top), "left"),
               halfplane((W, 0), (xa + thin / 2, top), "right"), rect(-1000, top, 3000, top + 500)))
    g.add(rect(0, 0, W, bt))
    g.space(P.sb * 0.5, P.sb * 0.5)


@glyph("product", 0x220F)
def product(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.36
    top = cap
    bot = P.desc * 0.55
    tt = UC.arm_t(P, 1.1)
    g.add(rect(0, top - tt, 2 * S + W, top))
    g.add(rect(0, bot, S, top))
    g.add(rect(S + W, bot, 2 * S + W, top))
    g.add(foot_serif(P, 0, S, bot, caps=True))
    g.add(foot_serif(P, S + W, 2 * S + W, bot, caps=True))
    g.space(P.sb, P.sb)


@glyph("summation", 0x2211)
def summation(g, P, base=False):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.22 + S
    top, bot = (cap, 0) if base else (cap, P.desc * 0.55)
    tt, bt = UC.arm_t(P, 1.0), UC.arm_t(P, 1.12)
    from ..parts import beak
    g.add(rect(0, top - tt, W, top))
    g.add(beak(P, W, top, tt, cap * 0.13, S * 0.42, side="right"))
    g.add(rect(0, bot, W, bot + bt))
    g.add(beak(P, W, bot, bt, cap * 0.15, S * 0.44, side="right", vert="up"))
    ym = (top + bot) / 2
    d1 = quad((0, top - tt), (S * 1.05, top - tt), (W * 0.52 + S * 0.5, ym), (W * 0.52 - S * 0.5, ym))
    g.add(d1)
    pen = Pen(H * 0.7, H * 0.5)
    g.add(stk(Path(W * 0.52, ym + 10).l(H * 0.4, bot + bt - 2), pen))
    g.space(P.sb * 0.7, P.sb * 0.5)


@glyph("radical", 0x221A)
def radical(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = P.cn * 1.40
    pen_t = Pen(H * 0.72, H * 0.5)
    pen_k = Pen(S * 0.42, H * 0.5)
    g.add(stk(Path(0, cap * 0.40).l(W * 0.13, cap * 0.47), pen_t))
    g.add(stk(Path(W * 0.12, cap * 0.47).l(W * 0.36, -P.os), pen_k))
    g.add(stk(Path(W * 0.35, -P.os + 8).l(W, cap + 60), pen_t))
    g.space(P.sb * 0.5, P.sb * 0.3)


@glyph("integral", 0x222B)
def integral(g, P):
    S, H = P.stem, P.hair
    pl = Pen(S * 0.46, H / 2)
    top, bot = P.asc + 40, P.desc - 10
    W = P.cn * 0.75
    rb = S * 0.45 + 4
    p = Path(W - rb * 0.6, top - rb * 1.0, d=110, w=0.6)
    p.c(W * 0.66, top - pl.hv, d=180, w=1.0)
    p.c(W * 0.50, (top + bot) / 2 + 120, d=262, w=1.0)
    p.c(W * 0.50, (top + bot) / 2 - 120, d=278, w=1.0)
    p.c(W * 0.34, bot + pl.hv, d=180, w=1.0)
    p.c(rb * 0.6, bot + rb * 1.0, d=110, w=0.6)
    g.add(stk(p, pl))
    g.add(ellipse(W - rb, top - rb * 1.1, rb, rb))
    g.add(ellipse(rb, bot + rb * 1.1, rb, rb))
    g.space(P.sb * 0.6, P.sb * 0.6)


@glyph("lozenge", 0x25CA)
def lozenge(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = P.cn * 1.1
    pen = Pen(S * 0.30, H * 0.55)
    p = Path(W / 2, -4).l(W, cap * 0.47).l(W / 2, cap + 4).l(0, cap * 0.47).close("l")
    g.add(stk(p, pen))
    g.space(P.sb, P.sb)


# ------------------------------------------------------------- micro, pi, Ohm

def mu_shape(g, P):
    u, _ = borrow("u", P)
    g.add(u)
    S = P.stem
    g.add(rect(0, P.desc, S, P.xh * 0.5))


@glyph("mu", 0x00B5, 0x03BC)
def mu(g, P):
    mu_shape(g, P)
    LC.anchors_lc(g, (P.stem + P.cn) / 2, P=P)
    g.space(P.sb, P.sb * 0.9)


@glyph("pi", 0x03C0)
def pi(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 1.10 + S * 1.5
    t = H * 1.3
    g.add(rect(0, xh - t, W, xh))
    g.add(rect(W * 0.20, 0, W * 0.20 + S * 0.92, xh - 2))
    g.add(foot_serif(P, W * 0.20, W * 0.20 + S * 0.92, 0, el=P.sfx * 0.8, er=P.sfx * 0.8))
    pl = Pen(S / 2, H / 2)
    xr = W * 0.70
    p = Path(xr + S / 2, xh - 4, d=270).l(xr + S / 2, xh * 0.25)
    p.c(xr + S * 1.3, -P.os + pl.hv, d=0, w=1.0)
    p.c(W, xh * 0.10, d=60, w=0.5)
    g.add(stk(p, pl))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.sb * 0.6, P.sb * 0.5)


# ------------------------------------------------------------- moedas

@glyph("dollar", 0x0024)
def dollar(g, P):
    Sg, _ = borrow("S", P)
    b = bounds(Sg)
    g.add(Sg)
    w = P.hair * 1.1 + P.stem * 0.12
    cx = (b[0] + b[2]) / 2
    g.add(rect(cx - w / 2, b[1] - 80, cx + w / 2, b[3] + 80))
    g.space(P.sb * 1.0, P.sb * 1.0)


@glyph("cent", 0x00A2)
def cent(g, P):
    c, _ = borrow("c", P)
    b = bounds(c)
    g.add(c)
    w = P.hair * 1.1 + P.stem * 0.12
    cx = (b[0] + b[2]) / 2 - 10
    g.add(rect(cx - w / 2, b[1] - 95, cx + w / 2, b[3] + 95))
    g.space(P.sb * 1.15, P.sb * 0.75)


@glyph("sterling", 0x00A3)
def sterling(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    pl = Pen(S / 2, H / 2)
    W = P.cn * 1.05 + S * 1.3
    rb = S * 0.52 + 5
    xs = W * 0.28
    p = Path(W - rb * 1.0, cap * 0.78, d=95, w=0.7)
    p.c(xs + W * 0.30, cap + P.os - pl.hv, d=180, w=1.0)
    p.c(xs + S / 2, cap * 0.62, d=270, w=1.0)
    p.l(xs + S / 2, cap * 0.22)
    p.c(xs - S * 0.2, H * 1.4, d=225, w=0.9)
    g.add(stk(p, pl))
    g.add(ellipse(W - rb - 2, cap * 0.76, rb, rb * 1.04))
    bt = H * 1.35
    g.add(rect(0, 0, W, bt))
    from ..parts import beak
    g.add(beak(P, W, 0, bt, cap * 0.12, S * 0.42, side="right", vert="up"))
    t = H * 1.2
    g.add(rect(xs - S * 0.95, cap * 0.42 - t / 2, xs + S + S * 0.95, cap * 0.42 + t / 2))
    g.space(P.sb * 0.8, P.sb * 0.6)


@glyph("yen", 0x00A5)
def yen(g, P):
    Y, _ = borrow("Y", P)
    b = bounds(Y)
    g.add(Y)
    cx = (b[0] + b[2]) / 2
    t = UC.arm_t(P, 0.95)
    a = P.stemC * 1.6
    for y in (P.cap * 0.38, P.cap * 0.22):
        g.add(rect(cx - a, y - t / 2, cx + a, y + t / 2))
    g.space(P.sb * 0.3, P.sb * 0.3)


@glyph("Euro", 0x20AC)
def Euro(g, P):
    C, _ = borrow("C", P)
    b = bounds(C)
    dx = P.stemC * 0.55
    g.add(shift(C, dx))
    t = UC.arm_t(P, 0.95)
    for y in (P.cap * 0.58, P.cap * 0.40):
        g.add(rect(0, y - t / 2, dx + (b[2] - b[0]) * 0.62, y + t / 2))
    g.space(P.sb * 0.6, P.sb * 0.6)


@glyph("currency", 0x00A4)
def currency(g, P):
    S, H = P.stem, P.hair
    r = P.cap * 0.25
    cx, cy = r * 1.45, P.cap * 0.42
    pc = Pen(S * 0.33, H * 0.55, P.ang)
    p = Path(cx + r - pc.hh, cy, d=90).c(cx, cy + r - pc.hv, d=180)
    p.c(cx - r + pc.hh, cy, d=270).c(cx, cy - r + pc.hv, d=0).close("c")
    g.add(stk(p, pc))
    pen = mpen(P)
    for sx in (1, -1):
        for sy in (1, -1):
            a0 = r * 0.82
            a1 = r * 1.40
            g.add(stk(Path(cx + sx * a0 * 0.707, cy + sy * a0 * 0.707).l(cx + sx * a1 * 0.707, cy + sy * a1 * 0.707), pen))
    g.space(P.sb * 0.8, P.sb * 0.8)


# ------------------------------------------------------------- sinais diversos

def ring_shape(P, cx, cy, r, t):
    pen = Pen(t / 2 * 1.15, t / 2 * 0.85)
    p = Path(cx + r - pen.hh, cy, d=90).c(cx, cy + r - pen.hv, d=180)
    p.c(cx - r + pen.hh, cy, d=270).c(cx, cy - r + pen.hv, d=0).close("c")
    return stk(p, pen)


def small_letter(name, P, k, cx, cy):
    """Desenha um glifo reduzido (k) centrado em (cx, cy)."""
    Q = P.scaled(k, weight_comp=1.0 + (1 - k) * 0.55)
    c, _ = borrow(name, Q)
    b = bounds(c)
    return shift(c, cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2)


@glyph("copyright", 0x00A9)
def copyright(g, P):
    R = P.cap * 0.5 + 20
    cx, cy = R, P.cap / 2
    g.add(ring_shape(P, cx, cy, R, P.hair * 1.45))
    g.add(small_letter("C", P, 0.56, cx + 4, cy))
    g.space(P.sb * 1.1, P.sb * 1.1)


@glyph("registered", 0x00AE)
def registered(g, P):
    R = P.cap * 0.5 + 20
    cx, cy = R, P.cap / 2
    g.add(ring_shape(P, cx, cy, R, P.hair * 1.45))
    g.add(small_letter("R", P, 0.52, cx + 6, cy))
    g.space(P.sb * 1.1, P.sb * 1.1)


@glyph("trademark", 0x2122)
def trademark(g, P):
    k = 0.42
    T = small_letter("T", P, k, 0, 0)
    M = small_letter("M", P, k, 0, 0)
    bt, bm = bounds(T), bounds(M)
    top = P.cap
    g.add(shift(T, -bt[0], top - bt[3]))
    g.add(shift(M, (bt[2] - bt[0]) + P.sb * 0.6 - bm[0], top - bm[3]))
    g.space(P.sb * 0.8, P.sb * 0.8)


@glyph("degree", 0x00B0)
def degree(g, P):
    r = P.cap * 0.135 + P.stem * 0.1
    g.add(ring_shape(P, r, P.cap - r, r, P.hair * 1.1 + P.stem * 0.15))
    g.space(P.sb * 1.3, P.sb * 1.3)


def ordinal(g, P, name):
    Q = P.scaled(0.62, weight_comp=1.22)
    c, _ = borrow(name, Q)
    b = bounds(c)
    top = P.cap + 4
    c = shift(c, -b[0], top - (Q.xh + Q.os))
    g.add(c)
    t = P.hair * 1.25
    yb = top - (Q.xh + Q.os) - 55
    g.add(rect(0, yb - t, b[2] - b[0], yb))


@glyph("ordfeminine", 0x00AA)
def ordfeminine(g, P):
    ordinal(g, P, "a")
    g.space(P.sb * 1.3, P.sb * 1.3)


@glyph("ordmasculine", 0x00BA)
def ordmasculine(g, P):
    ordinal(g, P, "o")
    g.space(P.sb * 1.3, P.sb * 1.3)


@glyph("numero", 0x2116)
def numero(g, P):
    N, _ = borrow("N", P)
    bn = bounds(N)
    g.add(N)
    Q = P.scaled(0.62, weight_comp=1.22)
    o, _ = borrow("o", Q)
    b = bounds(o)
    x0 = bn[2] + P.sb * 1.2
    top = P.cap + 4
    g.add(shift(o, x0 - b[0], top - (Q.xh + Q.os)))
    t = P.hair * 1.25
    yb = top - (Q.xh + Q.os) - 55
    g.add(rect(x0, yb - t, x0 + (b[2] - b[0]), yb))
    g.space(P.sb, P.sb * 1.2)


@glyph("section", 0x00A7)
def section(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    pen = Pen(P.curve / 2 * (0.84 - 0.18 * P.wf), H / 2, P.ang)
    W = P.cn * 0.82 + P.curve * 1.15
    top, bot = cap + P.os, -P.os - 110
    hgt = top - bot
    we = 0.6
    # S superior
    p = Path(W - pen.hh * we, top - hgt * 0.16, d=90, w=we)
    p.c(W * 0.50, top - pen.hv, d=180, w=1.0)
    p.c(pen.hh, top - hgt * 0.17, d=270, w=1.0)
    p.c(W * 0.50, top - hgt * 0.40, d=-14, w=1.1)
    p.c(W - pen.hh, top - hgt * 0.60, d=270, w=1.0)
    p.c(W * 0.62, bot + hgt * 0.36, d=200, w=0.5)
    g.add(stk(p, pen))
    q = Path(pen.hh * we, bot + hgt * 0.16, d=270, w=we)
    q.c(W * 0.50, bot + pen.hv, d=0, w=1.0)
    q.c(W - pen.hh, bot + hgt * 0.17, d=90, w=1.0)
    q.c(W * 0.50, bot + hgt * 0.40, d=166, w=1.1)
    q.c(pen.hh, bot + hgt * 0.60, d=90, w=1.0)
    q.c(W * 0.38, top - hgt * 0.36, d=20, w=0.5)
    g.add(stk(q, pen))
    g.space(P.sb * 1.1, P.sb * 1.1)


@glyph("paragraph", 0x00B6)
def paragraph(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = P.cn * 0.95 + S * 1.4
    s1 = W * 0.52
    s2 = W - S * 0.70
    bot = P.desc * 0.6
    g.add(rect(s1, bot, s1 + S * 0.70, cap))
    g.add(rect(s2, bot, s2 + S * 0.70, cap))
    g.add(rect(s1, cap - H * 1.3, W, cap))
    p = Path(s1 + 2, cap, d=180).c(0, cap * 0.72, d=270).c(s1 + 2, cap * 0.42, d=0).close("l")
    g.add(p.fill())
    g.space(P.sb * 0.9, P.sb * 0.9)


@glyph("at", 0x0040)
def at(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    R = cap * 0.56 + S * 0.15
    cx, cy = R, cap * 0.40
    pen = Pen(P.curve * 0.30 * (1 - 0.30 * P.wf), H * 0.55, P.ang)
    # anel externo aberto
    p = Path(cx + R * 0.62, cy - R * 0.62, d=-30, w=0.8)
    p.c(cx + R - pen.hh, cy + R * 0.05, d=90, w=1.0)
    p.c(cx, cy + R - pen.hv, d=180, w=1.0)
    p.c(cx - R + pen.hh, cy, d=270, w=1.0)
    p.c(cx + R * 0.05, cy - R + pen.hv, d=0, w=1.0)
    p.c(cx + R * 0.66, cy - R * 0.78, d=35, w=0.6)
    g.add(stk(p, pen))
    # 'a' interno (bojo + haste)
    ri = R * 0.42
    pi_ = Pen(P.curve * 0.36 * (1 - 0.25 * P.wf), H * 0.5, P.ang)
    xi = cx - R * 0.04
    q = Path(xi + ri - pi_.hh, cy + 6, d=90).c(xi, cy + ri - pi_.hv, d=180)
    q.c(xi - ri + pi_.hh, cy, d=270).c(xi, cy - ri + pi_.hv, d=0).close("c")
    g.add(stk(q, pi_))
    xs = xi + ri - S * 0.36
    sp = Pen(S * 0.38 * (1 - 0.25 * P.wf), H * 0.5)
    r = Path(xs + S * 0.36, cy + ri, d=270).l(xs + S * 0.36, cy - ri * 0.55)
    r.c(xs + S * 0.36 + R * 0.25, cy - ri * 0.95, d=0, w=1.0)
    r.c(cx + R * 0.66, cy - R * 0.05, d=80, w=0.7)
    g.add(stk(r, sp))
    g.space(P.sb * 0.9, P.sb * 0.9)


@glyph("ampersand", 0x0026)
def ampersand(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    pl = Pen(S / 2, H / 2)
    pc = Pen(P.curve / 2, H / 2, P.ang)
    W = P.cn * 1.30 + S * 1.5
    top = cap + P.os
    # laço superior + diagonal até a cauda
    p = Path(W * 0.30, cap * 0.56, d=110, w=0.8)
    p.c(W * 0.20, cap * 0.80, d=90, w=0.9)
    p.c(W * 0.38, top - pl.hv, d=0, w=1.0)
    p.c(W * 0.54, cap * 0.80, d=270, w=0.75)
    p.c(W * 0.30, cap * 0.52, d=220, w=0.6)
    g.add(stk(p, Pen(S * 0.46, H / 2)))
    q = Path(W * 0.30, cap * 0.58, d=315, w=0.9)
    q.c(W * 0.78, cap * 0.10, d=315, w=1.05)
    q.c(W * 0.96, -P.os + pl.hv, d=0, w=1.0)
    q.c(W + 6, cap * 0.08, d=60, w=0.5)
    g.add(stk(q, pl))
    # bojo inferior
    r = Path(W * 0.32, cap * 0.53, d=200, w=0.7)
    r.c(pc.hh, cap * 0.22, d=270, w=1.0)
    r.c(W * 0.38, -P.os + pc.hv, d=0, w=1.0)
    r.c(W * 0.80, cap * 0.30, d=55, w=0.55)
    g.add(stk(r, pc))
    # braço com serifa
    t = H * 1.2
    g.add(rect(W * 0.66, cap * 0.40 - t, W + P.sfx * 0.5, cap * 0.40))
    g.space(P.sb * 0.9, P.sb * 0.5)


@glyph("numbersign", 0x0023)
def numbersign(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = tab_width(P)
    a = span(P) / 2
    cx = W / 2
    t = mt(P)
    h = cap * 0.86
    y0 = (cap - h) / 2 - 10
    for y in (y0 + h * 0.32, y0 + h * 0.68):
        g.add(rect(cx - a, y - t / 2, cx + a, y + t / 2))
    pen = Pen(t / 2 * 1.2, t / 2)
    for x in (cx - a * 0.36, cx + a * 0.36):
        g.add(stk(Path(x - h * 0.08, y0).l(x + h * 0.08, y0 + h), pen))
    g.space(width=W, center=True)


@glyph("asterisk", 0x002A)
def asterisk(g, P):
    S = P.stem
    L = P.cap * 0.20
    cx, cy = L * 1.05, P.cap - L * 1.05
    for k in range(5):
        ang = math.radians(90 + k * 72)
        pen = Pen(S * 0.30, S * 0.30)
        p = Path(cx, cy, w=0.35).l(cx + L * math.cos(ang), cy + L * math.sin(ang), w=1.0)
        g.add(stk(p, pen, cap1="round"))
    g.space(P.sb * 1.2, P.sb * 1.2)


@glyph("dagger", 0x2020)
def dagger(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = P.cn * 0.95
    cx = W / 2
    g.add(quad((cx - S * 0.36, cap + 20), (cx + S * 0.36, cap + 20), (cx + S * 0.16, P.desc * 0.7),
               (cx - S * 0.16, P.desc * 0.7)))
    y = cap * 0.70
    g.add(poly((0, y - H * 0.55), (cx, y - H * 0.9), (W, y - H * 0.55),
               (W, y + H * 0.55), (cx, y + H * 0.9), (0, y + H * 0.55)))
    g.space(P.sb * 0.9, P.sb * 0.9)


@glyph("daggerdbl", 0x2021)
def daggerdbl(g, P):
    S, H, cap = P.stem, P.hair, P.cap
    W = P.cn * 0.95
    cx = W / 2
    g.add(quad((cx - S * 0.30, cap + 20), (cx + S * 0.30, cap + 20), (cx + S * 0.30, P.desc * 0.7),
               (cx - S * 0.30, P.desc * 0.7)))
    for y in (cap * 0.70, P.desc * 0.7 + (cap - P.desc * 0.7) * 0.18):
        g.add(poly((0, y - H * 0.55), (cx, y - H * 0.9), (W, y - H * 0.55),
                   (W, y + H * 0.55), (cx, y + H * 0.9), (0, y + H * 0.55)))
    g.space(P.sb * 0.9, P.sb * 0.9)


# ------------------------------------------------------------- frações

def frac(g, P, num, den):
    n, _ = borrow(num + ".numr", P)
    d, _ = borrow(den + ".dnom", P)
    s, _ = borrow("fraction", P)
    bn, bd, bs = bounds(n), bounds(d), bounds(s)
    x = 0
    g.add(shift(n, x - bn[0]))
    x += bn[2] - bn[0]
    xs = x - (bs[2] - bs[0]) * 0.40
    g.add(shift(s, xs - bs[0]))
    xd = xs + (bs[2] - bs[0]) * 0.60
    g.add(shift(d, xd - bd[0]))
    g.space(P.sb * 0.8, P.sb * 0.8)


for _nm, _u, _n, _d in (("onehalf", 0x00BD, "one", "two"), ("onequarter", 0x00BC, "one", "four"),
                        ("threequarters", 0x00BE, "three", "four")):
    def _f(g, P, n=_n, d=_d):
        frac(g, P, n, d)
    glyph(_nm, _u)(_f)


# ------------------------------------------------------------- setas

def arrow(P, x0, y0, x1, y1):
    t = mt(P)
    L = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    hl = t * 2.6 + 70
    hw = t * 1.5 + 52
    bx, by = x1 - ux * hl, y1 - uy * hl
    shaft = stk(Path(x0, y0).l(bx + ux * 10, by + uy * 10), Pen(t / 2, t / 2))
    head = poly((x1, y1), (bx + nx * hw, by + ny * hw), (bx + ux * hl * 0.22, by + uy * hl * 0.22),
                (bx - nx * hw, by - ny * hw))
    return shaft + head


@glyph("arrowleft", 0x2190)
def arrowleft(g, P):
    ya = axis(P)
    g.add(arrow(P, 760, ya, 0, ya))
    g.space(P.sb, P.sb)


@glyph("arrowright", 0x2192)
def arrowright(g, P):
    ya = axis(P)
    g.add(arrow(P, 0, ya, 760, ya))
    g.space(P.sb, P.sb)


@glyph("arrowup", 0x2191)
def arrowup(g, P):
    W = tab_width(P)
    g.add(arrow(P, W / 2, -20, W / 2, P.cap + 20))
    g.space(width=W, center=True)


@glyph("arrowdown", 0x2193)
def arrowdown(g, P):
    W = tab_width(P)
    g.add(arrow(P, W / 2, P.cap + 20, W / 2, -20))
    g.space(width=W, center=True)


@glyph("arrowboth", 0x2194)
def arrowboth(g, P):
    ya = axis(P)
    g.add(arrow(P, 380, ya, 0, ya))
    g.add(arrow(P, 370, ya, 820, ya))
    g.space(P.sb, P.sb)
