"""Algarismos: alinhados proporcionais (padrão), tabulares (.tf),
estilo antigo (.osf), zero cortado (.zero), sobrescritos e subscritos."""
from ..glyph import transform_contours
from ..parts import beak, ellipse, foot_serif, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import glyph

NAMES = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


class F:
    """Contexto de desenho de um algarismo."""

    def __init__(self, P, FH, y0=0.0, wk=1.0):
        self.P = P
        self.S = P.stem * 1.04
        self.H = P.hair * 1.04
        self.C = P.curve * 1.04
        self.FH = FH
        self.y0 = y0
        self.os = P.os
        self.bw = (P.cn * 1.12 + 1.9 * self.S) * wk
        self.pl = Pen(self.S / 2, self.H / 2)
        self.pc = Pen(self.C / 2, self.H / 2, P.ang)
        self.rb = self.S * 0.50 + 4

    def Y(self, k):
        return self.y0 + self.FH * k


def tab_width(P):
    return round(P.cn * 1.30 + 2 * P.stem)


def drop(f, cx, cy, r=None):
    r = f.rb if r is None else r
    return ellipse(cx, cy, r, r * 1.04)


# ------------------------------------------------------------- desenhos

def d_zero(g, f, slash=False):
    bw, pc = f.bw * 0.90, f.pc
    top = f.Y(1) + f.os - pc.hv
    bot = f.y0 - f.os + pc.hv
    cy = f.Y(0.5)
    t = 0.98
    p = Path(bw - pc.hh, cy, d=90).c(bw / 2, top, d=180, t=t).c(pc.hh, cy, d=270, t=t)
    p.c(bw / 2, bot, d=0, t=t).close("c", t=t)
    g.add(stk(p, pc))
    if slash:
        g.add(stk(Path(bw * 0.70, f.Y(0.80)).l(bw * 0.30, f.Y(0.20)), Pen(f.S * 0.36, f.H * 0.6)))
    return bw


def d_one(g, f):
    S, H, P = f.S, f.H, f.P
    x0 = f.bw * 0.40
    top = f.Y(1) + f.os * 0.5
    g.add(rect(x0, f.y0, x0 + S, top))
    # bandeira
    g.add(quad((x0 + S, top), (x0 - S * 1.25, f.Y(0.80)), (x0 - S * 1.25, f.Y(0.80) - H * 0.9),
               (x0 + 2, f.Y(0.86) - H * 0.6)))
    g.add(foot_serif(P, x0, x0 + S, f.y0, el=P.sfx * 1.6, er=P.sfx * 1.6))
    return x0 + S + P.sfx * 1.6


def d_two(g, f):
    bw, S, H, pc, pl = f.bw * 0.92, f.S, f.H, f.pc, f.pl
    top = f.Y(1) + f.os
    bt = H * 1.35
    p = Path(f.rb * 1.05 + 6, f.Y(0.80), d=80, w=0.7)
    p.c(bw * 0.50, top - pc.hv, d=0, w=1.0)
    p.c(bw - pc.hh, f.Y(0.70), d=270, w=1.0)
    p.c(bw * 0.42, f.Y(0.30), d=228, w=1.02)
    p.c(S * 0.42, f.y0 + bt - 2, d=238, w=1.0)
    g.add(stk(p, pc))
    g.add(drop(f, f.rb + 4, f.Y(0.78)))
    g.add(rect(0, f.y0, bw, f.y0 + bt))
    g.add(beak(f.P, bw, f.y0, bt, f.FH * 0.11, S * 0.42, side="right", vert="up"))
    return bw


def d_three(g, f):
    bw, S, H, pc = f.bw * 0.90, f.S, f.H, f.pc
    top = f.Y(1) + f.os
    bot = f.y0 - f.os
    p = Path(f.rb * 1.1 + 6, f.Y(0.82), d=75, w=0.7)
    p.c(bw * 0.48, top - pc.hv, d=0, w=1.0)
    p.c(bw * 0.92 - pc.hh * 0.92, f.Y(0.77), d=270, w=0.92)
    p.c(bw * 0.38, f.Y(0.535), d=180, w=0.75)
    g.add(stk(p, pc))
    q = Path(bw * 0.38, f.Y(0.535), d=0, w=0.75)
    q.c(bw - pc.hh, f.Y(0.27), d=270, w=1.0)
    q.c(bw * 0.47, bot + pc.hv, d=180, w=1.0)
    q.c(f.rb * 1.2 + 2, f.Y(0.14), d=135, w=0.7)
    g.add(stk(q, pc))
    g.add(drop(f, f.rb + 4, f.Y(0.80)))
    g.add(drop(f, f.rb + 2, f.Y(0.16)))
    return bw


def d_four(g, f):
    bw, S, H, P = f.bw * 0.96, f.S, f.H, f.P
    xs = bw * 0.62
    yb = f.Y(0.27)
    bt = H * 1.25
    top = f.Y(1) + f.os * 0.3
    g.add(rect(xs, f.y0, xs + S, top))
    g.add(rect(0, yb - bt / 2, bw, yb + bt / 2))
    th = H * 1.45
    g.add(quad((xs + S * 0.2, top), (xs + S, top), (th, yb - bt / 2 + 2), (0, yb - bt / 2 + 2)))
    g.add(foot_serif(P, xs, xs + S, f.y0, el=P.sfx * 1.2, er=P.sfx * 1.2))
    return bw


def d_five(g, f):
    bw, S, H, pc, P = f.bw * 0.90, f.S, f.H, f.pc, f.P
    bot = f.y0 - f.os
    bt = H * 1.3
    x1 = bw * 0.14
    g.add(rect(x1, f.Y(1) - bt, bw * 0.92, f.Y(1)))
    g.add(beak(P, bw * 0.92, f.Y(1), bt, f.FH * 0.08, S * 0.36, side="right", taper=0.7))
    g.add(quad((x1, f.Y(1)), (x1 + S * 0.82, f.Y(1)), (x1 + S * 0.72, f.Y(0.56)), (x1 - 4, f.Y(0.58))))
    p = Path(x1 + S * 0.3, f.Y(0.57), d=40, w=0.55)
    p.c(bw * 0.50, f.Y(0.64) - pc.hv, d=0, w=1.0)
    p.c(bw - pc.hh, f.Y(0.32), d=270, w=1.0)
    p.c(bw * 0.47, bot + pc.hv, d=180, w=1.0)
    p.c(f.rb * 1.2 + 2, f.Y(0.14), d=135, w=0.7)
    g.add(stk(p, pc))
    g.add(drop(f, f.rb + 2, f.Y(0.16)))
    return bw


def d_six(g, f):
    bw, S, H, pc = f.bw * 0.92, f.S, f.H, f.pc
    top = f.Y(1) + f.os
    bot = f.y0 - f.os
    t = 0.98
    p = Path(bw - f.rb * 1.1 - 4, f.Y(0.86), d=100, w=0.7)
    p.c(bw * 0.56, top - pc.hv, d=180, w=1.0)
    p.c(pc.hh, f.Y(0.42), d=270, w=1.0, t=t)
    p.c(bw * 0.52, bot + pc.hv, d=0, t=t)
    p.c(bw - pc.hh, f.Y(0.31), d=90, t=t)
    p.c(bw * 0.53, f.Y(0.62) - pc.hv, d=180, t=t)
    p.c(pc.hh * 1.3 + 2, f.Y(0.35), d=245, w=0.45)
    g.add(stk(p, pc))
    g.add(drop(f, bw - f.rb - 4, f.Y(0.84)))
    return bw


def d_seven(g, f):
    bw, S, H, P = f.bw * 0.92, f.S, f.H, f.P
    bt = H * 1.3
    g.add(rect(0, f.Y(1) - bt, bw, f.Y(1)))
    g.add(beak(P, 0, f.Y(1), bt, f.FH * 0.11, S * 0.40, side="left"))
    p = Path(bw - S * 0.32, f.Y(1) - bt * 0.5, d=245, w=0.7)
    p.c(bw * 0.52, f.Y(0.45), d=250, w=1.0)
    p.c(bw * 0.40, f.y0, d=264, w=1.04)
    g.add(stk(p, f.pl))
    return bw


def d_eight(g, f):
    bw, S, H, pc = f.bw * 0.92, f.S, f.H, f.pc
    top = f.Y(1) + f.os
    bot = f.y0 - f.os
    ym = f.Y(0.545)
    pu = Pen(pc.A * 0.92, pc.B, f.P.ang)
    x0, x1 = bw * 0.09, bw * 0.91
    t = 0.98
    p = Path(x1 - pu.hh, (top + ym) / 2, d=90).c(bw / 2, top - pu.hv, d=180, t=t)
    p.c(x0 + pu.hh, (top + ym) / 2, d=270, t=t).c(bw / 2, ym - pu.hv * 0.5, d=0, t=t).close("c", t=t)
    g.add(stk(p, pu))
    q = Path(bw - pc.hh, (ym + bot) / 2, d=90).c(bw / 2, ym + pc.hv * 0.5, d=180, t=t)
    q.c(pc.hh, (ym + bot) / 2, d=270, t=t).c(bw / 2, bot + pc.hv, d=0, t=t).close("c", t=t)
    g.add(stk(q, pc))
    return bw


def d_nine(g, f):
    # o 9 é o 6 girado 180° em torno do centro do corpo
    tmp = type(g)("tmp")
    bw = d_six(tmp, f)
    cy = f.y0 + f.FH / 2
    for shape in tmp.adds:
        g.add(transform_contours(shape, -1, 0, 0, -1, bw, 2 * cy))
    return bw


DRAW = [d_zero, d_one, d_two, d_three, d_four, d_five, d_six, d_seven, d_eight, d_nine]

# espaçamento proporcional (múltiplos de P.sb)
PROP_SB = {
    "zero": (1.3, 1.3), "one": (1.0, 1.0), "two": (1.0, 1.0), "three": (1.1, 1.1),
    "four": (0.8, 1.0), "five": (1.1, 1.1), "six": (1.2, 1.1), "seven": (1.0, 0.8),
    "eight": (1.15, 1.15), "nine": (1.1, 1.2),
}

# estilo antigo: (altura relativa, deslocamento vertical relativo à altura-x)
OSF = {
    "zero": "x", "one": "x", "two": "x", "three": "d", "four": "d", "five": "d",
    "six": "a", "seven": "d", "eight": "a", "nine": "d",
}


def osf_geom(P, kind):
    if kind == "x":
        return P.xh * 1.0, 0.0
    if kind == "a":
        return P.fig, 0.0
    h = P.xh * 1.32
    return h, P.xh - h


def _make(name, idx, mode):
    def fn(g, P):
        if mode == "lining" or mode == "tab" or mode == "zero":
            f = F(P, P.fig)
        elif mode == "osf":
            h, y0 = osf_geom(P, OSF[name])
            f = F(P, h, y0, wk=0.92)
        if mode == "zero":
            d_zero(g, f, slash=True)
        else:
            DRAW[idx](g, f)
        if mode == "tab" or mode == "zero":
            g.space(width=tab_width(P), center=True)
        else:
            l, r = PROP_SB[name]
            g.space(P.sb * l, P.sb * r)
    return fn


for i, n in enumerate(NAMES):
    glyph(n, 0x30 + i)(_make(n, i, "lining"))
    glyph(n + ".tf")(_make(n, i, "tab"))
    glyph(n + ".osf")(_make(n, i, "osf"))
glyph("zero.zero")(_make("zero", 0, "zero"))


# ------------------------------------------------------------- sobrescritos

SUP_UNI = {0: 0x2070, 1: 0x00B9, 2: 0x00B2, 3: 0x00B3, 4: 0x2074, 5: 0x2075, 6: 0x2076,
           7: 0x2077, 8: 0x2078, 9: 0x2079}
SUB_UNI = {i: 0x2080 + i for i in range(10)}


def small_params(P):
    return P.scaled(0.60, weight_comp=1.22)


def _make_small(idx, y0_fn, tab=False):
    def fn(g, P):
        Q = small_params(P)
        f = F(Q, Q.fig, y0_fn(P, Q))
        DRAW[idx](g, f)
        n = NAMES[idx]
        l, r = PROP_SB[n]
        g.space(Q.sb * l * 0.9, Q.sb * r * 0.9)
    return fn


def sup_y(P, Q):
    return P.cap - Q.fig


def sub_y(P, Q):
    return -Q.fig * 0.22


def numr_y(P, Q):
    return P.cap - Q.fig


def dnom_y(P, Q):
    return 0.0


for i, n in enumerate(NAMES):
    glyph(n + ".sups", SUP_UNI[i])(_make_small(i, sup_y))
    glyph(n + ".subs", SUB_UNI[i])(_make_small(i, sub_y))
    glyph(n + ".numr")(_make_small(i, numr_y))
    glyph(n + ".dnom")(_make_small(i, dnom_y))
