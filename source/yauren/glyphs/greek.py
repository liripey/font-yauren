"""Grego monotônico (maiúsculas, minúsculas, tonos e dialítica).

Letras idênticas às latinas reutilizam o mesmo desenho (glifos próprios,
para kerning e recursos por script)."""
import math

from ..glyph import Glyph, clip, contours_bounds, transform_contours
from ..parts import ellipse, foot_serif, halfplane, head_serif, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import ALIASES, borrow, composite, glyph
from . import lower as LC
from . import upper as UC


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def shift(c, dx=0, dy=0):
    return transform_contours(c, dx=dx, dy=dy)


def ring(cx, cy, rx, ry, pen, t=0.97):
    p = Path(cx + rx - pen.hh, cy, d=90).c(cx, cy + ry - pen.hv, d=180, t=t)
    p.c(cx - rx + pen.hh, cy, d=270, t=t).c(cx, cy - ry + pen.hv, d=0, t=t).close("c", t=t)
    return stk(p, pen)


# ------------------------------------------------------------- cópias latinas

def _copy(src):
    from ..registry import ALIASES

    def fn(g, P):
        from ..registry import GLYPHS
        GLYPHS[src][1](g, P)
    return fn


for _name, _uni, _src in [
        ("Alpha", 0x0391, "A"), ("Beta", 0x0392, "B"), ("Epsilon", 0x0395, "E"),
        ("Zeta", 0x0396, "Z"), ("Eta", 0x0397, "H"), ("Iota", 0x0399, "I"),
        ("Kappa", 0x039A, "K"), ("Mu", 0x039C, "M"), ("Nu", 0x039D, "N"),
        ("Omicron", 0x039F, "O"), ("Rho", 0x03A1, "P"), ("Tau", 0x03A4, "T"),
        ("Upsilon", 0x03A5, "Y"), ("Chi", 0x03A7, "X"),
        ("omicron", 0x03BF, "o"), ("nu", 0x03BD, "v")]:
    glyph(_name, _uni)(_copy(_src))
    ALIASES[_name] = _src


# ------------------------------------------------------------- maiúsculas

@glyph("Gamma", 0x0393)
def Gamma(g, P):
    S, cn = P.stemC, P.cn
    g.add(rect(0, 0, S, P.cap))
    UC.serifs(g, P, 0, S, tr=0)
    UC.e_arms(g, P, S, S + cn * 1.0, None, None)
    UC.anchors_uc(g, P, S / 2 + 20)
    g.space(P.sbC, P.sbC * 0.55)


@glyph("Delta", 0x0394)
def Delta(g, P):
    from .symbols import increment
    increment(g, P)


@glyph("Theta", 0x0398)
def Theta(g, P):
    W = UC.o_width_uc(P)
    g.add(UC.o_ring(P, 0, W))
    t = UC.arm_t(P, 1.0)
    C = P.curveC
    g.add(rect(W * 0.28, P.cap * 0.5 - t / 2, W * 0.72, P.cap * 0.5 + t / 2))
    from ..parts import beak
    for x, side in ((W * 0.28, "left"), (W * 0.72, "right")):
        g.add(beak(P, x, P.cap * 0.5 + t / 2, t, P.cap * 0.05, P.stemC * 0.30, side=side, taper=0.7))
        g.add(beak(P, x, P.cap * 0.5 - t / 2, t, P.cap * 0.05, P.stemC * 0.30, side=side, vert="up",
                   taper=0.7))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.rndC, P.rndC)


@glyph("Lambda", 0x039B)
def Lambda(g, P):
    UC.A(g, P, bar=False)


@glyph("Xi", 0x039E)
def Xi(g, P):
    from ..parts import beak
    S, cn, cap = P.stemC, P.cn, P.cap
    W = cn * 1.30 + S
    tt, bt = UC.arm_t(P, 1.05), UC.arm_t(P, 1.12)
    mt = UC.arm_t(P, 1.0)
    g.add(rect(0, cap - tt, W, cap))
    g.add(beak(P, 0, cap, tt, cap * 0.12, S * 0.40, side="left"))
    g.add(beak(P, W, cap, tt, cap * 0.12, S * 0.40, side="right"))
    g.add(rect(0, 0, W, bt))
    g.add(beak(P, 0, 0, bt, cap * 0.13, S * 0.42, side="left", vert="up"))
    g.add(beak(P, W, 0, bt, cap * 0.13, S * 0.42, side="right", vert="up"))
    ym = cap * 0.51
    x0, x1 = W * 0.17, W * 0.83
    g.add(rect(x0, ym - mt / 2, x1, ym + mt / 2))
    for x, side in ((x0, "left"), (x1, "right")):
        g.add(beak(P, x, ym + mt / 2, mt, cap * 0.05, S * 0.32, side=side, taper=0.7))
        g.add(beak(P, x, ym - mt / 2, mt, cap * 0.05, S * 0.32, side=side, vert="up", taper=0.7))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.6, P.sbC * 0.6)


@glyph("Pi", 0x03A0)
def Pi(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    W = cn * 1.40
    tt = UC.arm_t(P, 1.1)
    g.add(rect(0, cap - tt, 2 * S + W, cap))
    g.add(rect(0, 0, S, cap))
    g.add(rect(S + W, 0, 2 * S + W, cap))
    g.add(foot_serif(P, 0, S, 0, caps=True))
    g.add(foot_serif(P, S + W, 2 * S + W, 0, caps=True))
    UC.anchors_uc(g, P, S + W / 2)
    g.space(P.sbC, P.sbC)


@glyph("Sigma", 0x03A3)
def Sigma(g, P):
    from .symbols import summation
    summation(g, P, base=True)
    g.space(P.sbC * 0.7, P.sbC * 0.5)


@glyph("Phi", 0x03A6)
def Phi(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.30 + P.curveC * 2
    cx = W / 2
    g.add(rect(cx - S / 2, 0, cx + S / 2, cap))
    UC.serifs(g, P, cx - S / 2, cx + S / 2)
    pen = Pen(P.curveC / 2 * 0.95, H / 2, P.ang)
    g.add(ring(cx, cap * 0.5, W / 2, cap * 0.33, pen))
    UC.anchors_uc(g, P, cx)
    g.space(P.rndC, P.rndC)


@glyph("Psi", 0x03A8)
def Psi(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.36 + S * 1.6
    cx = W / 2
    g.add(rect(cx - S / 2, 0, cx + S / 2, cap))
    UC.serifs(g, P, cx - S / 2, cx + S / 2)
    pl = Pen(S / 2, H / 2)
    yb = cap * 0.32
    p = Path(S / 2, cap - 20, d=270)
    p.l(S / 2, cap * 0.62)
    p.c(cx, yb + pl.hv, d=0, w=1.0)
    p.c(W - S * 0.30, cap * 0.62, d=90, w=1.0, a=S * 0.30)
    p.l(W - S * 0.30, cap - 20)
    g.add(stk(p, pl))
    g.add(foot_serif(P, 0, S, cap, caps=True, flip=True))
    g.add(foot_serif(P, W - S * 0.6, W, cap, caps=True, flip=True))
    UC.anchors_uc(g, P, cx)
    g.space(P.sbC, P.sbC)


@glyph("Omega", 0x03A9, 0x2126)
def Omega(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    _, pc = UC.pens(P)
    W = cn * 1.46 + 2 * P.curveC
    top = cap + P.osC
    bt = UC.arm_t(P, 1.15)
    p = Path(W * 0.30, bt * 0.5, d=118, w=0.85)
    p.c(pc.hh, cap * 0.50, d=90, w=1.0, t=0.95)
    p.c(W / 2, top - pc.hv, d=0, t=0.95)
    p.c(W - pc.hh, cap * 0.50, d=270, t=0.95)
    p.c(W * 0.70, bt * 0.5, d=242, w=0.85)
    g.add(stk(p, pc))
    g.add(rect(0, 0, W * 0.38, bt))
    g.add(rect(W * 0.62, 0, W, bt))
    from ..parts import beak
    g.add(beak(P, 0, 0, bt, cap * 0.10, S * 0.36, side="left", vert="up"))
    g.add(beak(P, W, 0, bt, cap * 0.10, S * 0.36, side="right", vert="up"))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.6, P.sbC * 0.6)


# ------------------------------------------------------------- minúsculas

def pens(P):
    return LC.pens(P)


@glyph("alpha", 0x03B1)
def alpha(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    pl, pc = pens(P)
    W = LC.o_width(P) * 1.02
    xb = W * 0.80
    t = 0.96
    p = Path(xb - S * 0.1, xh * 0.80, d=128, w=0.55)
    p.c(xb * 0.50, xh + P.os - pc.hv, d=180, w=1.0)
    p.c(pc.hh, xh * 0.5, d=270, t=t)
    p.c(xb * 0.50, -P.os + pc.hv, d=0, t=t)
    p.c(xb - S * 0.1, xh * 0.22, d=52, w=0.55)
    g.add(stk(p, pc))
    q = Path(xb - S * 0.15, xh + P.os * 0.4, d=282, w=1.0)
    q.c(xb + S * 0.10, xh * 0.20, d=290, w=1.0)
    q.c(W, -P.os + pl.hv, d=10, w=0.45)
    g.add(stk(q, pl))
    LC.anchors_lc(g, xb * 0.5, P=P)
    g.space(P.rnd, P.sb * 0.5)


@glyph("beta", 0x03B2)
def beta(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    pl, pc = pens(P)
    W = S + P.cn * 0.84 + P.curve * 0.92
    top = asc + P.os * 0.5
    p = Path(S / 2, P.desc, d=90)
    p.l(S / 2, asc * 0.60)
    p.c(S + (W - S) * 0.30, top - pl.hv, d=0, w=1.0)
    p.c(W * 0.86 - pc.hh * 0.9, asc * 0.79, d=270, w=0.9)
    p.c(W * 0.46, xh * 1.0, d=196, w=0.55)
    g.add(stk(p, pl))
    q = Path(W * 0.46, xh * 1.0, d=-8, w=0.55)
    q.c(W - pc.hh, xh * 0.40, d=270, w=1.0)
    q.c(W * 0.55, -P.os + pc.hv, d=180, w=1.0)
    q.c(S * 0.5, xh * 0.18, d=145, w=0.45)
    g.add(stk(q, pc))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.sb, P.rnd * 0.9)


@glyph("gamma", 0x03B3)
def gamma(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 1.0 + S * 1.5
    bottom = -xh * 0.22
    xa = LC.vee(g, P, 0, W, xh, bottom, S * 1.02, H * 1.25, H * 0.6)
    pen = Pen(S * 0.24 + H * 0.15, H * 0.55)
    r = xh * 0.13 + S * 0.45
    g.add(ring(xa, bottom - r * 0.80, r * 0.80, r, pen))
    LC.anchors_lc(g, xa, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


@glyph("delta", 0x03B4)
def delta(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    pl, pc = pens(P)
    W = LC.o_width(P) * 0.96
    g.add(ring(W / 2, xh * 0.50, W / 2, xh / 2 + P.os, pc))
    rb = LC.rbf(P, 0.48)
    p = Path(W * 0.36, xh * 0.94, d=128, w=0.75)
    p.c(W * 0.16 + pl.hh * 0.8, asc * 0.80, d=90, w=0.9)
    p.c(W * 0.46, asc + P.os - pl.hv, d=0, w=1.0)
    p.c(W * 0.86 - rb * 0.5, asc - rb * 0.6, d=-25, w=0.7)
    g.add(stk(p, pl))
    g.add(LC.drop(P, W * 0.86 - rb * 0.2, asc - rb * 0.95, rb))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.rnd, P.rnd)


@glyph("epsilon", 0x03B5)
def epsilon(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = LC.o_width(P) * 0.78
    pen = Pen(P.curve / 2 * 0.92, H / 2, P.ang)
    p = Path(W * 0.94, xh * 0.80, d=110, w=0.6)
    p.c(W * 0.52, xh + P.os - pen.hv, d=180, w=1.0)
    p.c(pen.hh * 0.9 + W * 0.04, xh * 0.74, d=270, w=0.9)
    p.c(W * 0.58, xh * 0.53, d=0, w=0.6)
    g.add(stk(p, pen))
    q = Path(W * 0.62, xh * 0.53, d=180, w=0.6)
    q.c(pen.hh, xh * 0.25, d=270, w=1.0)
    q.c(W * 0.52, -P.os + pen.hv, d=0, w=1.0)
    q.c(W + 4, xh * 0.18, d=40, w=0.6)
    g.add(stk(q, pen))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.rnd * 0.9, P.rnd * 0.6)


@glyph("zeta", 0x03B6)
def zeta(g, P):
    S, H, xh, asc, d = P.stem, P.hair, P.xh, P.asc, P.desc
    _, pc = pens(P)
    W = LC.o_width(P) * 0.80
    t = H * 1.1
    g.add(rect(W * 0.16, asc - t, W, asc))
    p = Path(W * 0.94, asc - t * 0.5, d=215, w=0.75)
    p.c(pc.hh, xh * 0.45, d=270, w=1.0)
    p.c(W * 0.50, H * 0.6, d=0, w=0.6)
    p.c(W * 0.86, -xh * 0.18, d=280, w=1.0)
    p.c(W * 0.46, d * 0.88, d=200, w=0.4)
    g.add(stk(p, pc))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.rnd * 0.9, P.rnd * 0.6)


@glyph("eta", 0x03B7)
def eta(g, P):
    S = P.stem
    xr = S + P.cn
    g.add(rect(0, 0, S, LC.XT(P) - P.hdd - 8))
    g.add(head_serif(P, 0, S, LC.XT(P)))
    g.add(LC.arch(P, S, xr, P.desc))
    LC.anchors_lc(g, (xr + S) / 2 - S * 0.3, P=P)
    g.space(P.sb, P.sb)


@glyph("theta", 0x03B8)
def theta(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    _, pc = pens(P)
    W = LC.o_width(P) * 0.92
    top, bot = asc + P.os * 0.5, -P.os
    g.add(ring(W / 2, (top + bot) / 2, W / 2, (top - bot) / 2, pc))
    t = H * 1.15
    ym = (top + bot) / 2
    g.add(rect(pc.hh, ym - t / 2, W - pc.hh, ym + t / 2))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.rnd, P.rnd)


def iota_body(g, P):
    S, xh = P.stem, P.xh
    pl, _ = pens(P)
    g.add(head_serif(P, 0, S, LC.XT(P)))
    p = Path(S / 2, LC.XT(P) - P.hdd - 10, d=270)
    p.l(S / 2, xh * 0.28)
    p.c(S + P.cn * 0.16, -P.os + pl.hv, d=0, w=1.0)
    p.c(S + P.cn * 0.38, xh * 0.13, d=60, w=0.5)
    g.add(stk(p, pl))


@glyph("iota", 0x03B9)
def iota(g, P):
    iota_body(g, P)
    LC.anchors_lc(g, P.stem / 2, P=P)
    g.space(P.sb, P.sb * 0.4)


@glyph("kappa", 0x03BA)
def kappa(g, P):
    LC.k(g, P, short=True)


@glyph("lambda", 0x03BB)
def lambda_(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    W = P.cn * 1.0 + S * 1.4
    thick, thin = S * 1.02, H * 1.3
    xt = W * 0.10
    d1 = quad((xt, asc), (xt + thick, asc), (W, 0), (W - thick, 0))
    g.add(clip(d1, rect(-100, -500, 3000, 0)))
    s1 = (W - thick - xt) / asc
    jy = xh * 0.62
    jx = xt + s1 * (asc - jy) + thick * 0.3
    g.add(quad((jx, jy + 20), (jx + thin, jy + 20), (thin, 0), (0, 0)))
    g.add(foot_serif(P, W - thick, W, 0, el=P.sfx * 0.4, er=P.sfx * 0.8, sl=-s1, sr=-s1))
    g.add(foot_serif(P, 0, thin, 0, el=P.sfx * 0.8, er=P.sfx * 0.4,
                     sl=(jx - 0) / (jy + 20), sr=(jx - 0) / (jy + 20)))
    g.add(head_serif(P, xt, xt + thick, asc, ext=P.hdx * 0.8))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.sb * 0.5, P.sb * 0.5)


@glyph("xi", 0x03BE)
def xi(g, P):
    S, H, xh, asc, d = P.stem, P.hair, P.xh, P.asc, P.desc
    _, pc = pens(P)
    W = LC.o_width(P) * 0.80
    t = H * 1.1
    g.add(rect(W * 0.16, asc - t, W, asc))
    pen = Pen(P.curve / 2 * 0.9, H / 2, P.ang)
    p = Path(W * 0.86, asc - t * 0.5, d=200, w=0.6)
    p.c(pen.hh + W * 0.08, asc * 0.80, d=270, w=0.9)
    p.c(W * 0.60, xh * 1.02, d=0, w=0.6)
    g.add(stk(p, pen))
    q = Path(W * 0.66, xh * 1.02, d=180, w=0.6)
    q.c(pen.hh, xh * 0.45, d=270, w=1.0)
    q.c(W * 0.50, H * 0.6, d=0, w=0.6)
    q.c(W * 0.86, -xh * 0.18, d=280, w=1.0)
    q.c(W * 0.46, d * 0.88, d=200, w=0.4)
    g.add(stk(q, pen))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.rnd * 0.9, P.rnd * 0.6)


@glyph("rho", 0x03C1)
def rho(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = LC.o_width(P)
    g.add(ring(W / 2, xh / 2, W / 2, xh / 2 + P.os, pc))
    g.add(rect(0, P.desc, S * 1.02, xh * 0.50))
    g.add(foot_serif(P, 0, S * 1.02, P.desc))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.sb, P.rnd)


@glyph("sigma", 0x03C3)
def sigma(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = LC.o_width(P) * 0.92
    t = H * 1.15
    g.add(ring(W / 2, xh / 2 - P.os * 0.3, W / 2, xh / 2 + P.os * 0.7, pc))
    g.add(rect(W * 0.45, xh - t, W * 1.18, xh))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.rnd, P.sb * 0.4)


@glyph("sigmafinal", 0x03C2)
def sigmafinal(g, P):
    S, H, xh, d = P.stem, P.hair, P.xh, P.desc
    _, pc = pens(P)
    W = LC.o_width(P) * 0.84
    rb = LC.rbf(P, 0.5)
    p = Path(W - rb * 0.9, xh * 0.74, d=95, w=0.6)
    p.c(W * 0.55, xh + P.os - pc.hv, d=180, w=1.0)
    p.c(pc.hh, xh * 0.45, d=270, w=1.0)
    p.c(W * 0.50, H * 0.6, d=0, w=0.6)
    p.c(W * 0.84, -xh * 0.16, d=280, w=1.0)
    p.c(W * 0.44, d * 0.86, d=200, w=0.4)
    g.add(stk(p, pc))
    g.add(LC.drop(P, W - rb, xh * 0.74, rb))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.rnd, P.rnd * 0.5)


@glyph("tau", 0x03C4)
def tau(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    pl, _ = pens(P)
    W = P.cn * 0.95 + S
    t = H * 1.15
    g.add(rect(0, xh - t, W, xh))
    x0 = W * 0.40
    p = Path(x0 + S / 2, xh - 4, d=270)
    p.l(x0 + S / 2, xh * 0.28)
    p.c(x0 + S + P.cn * 0.16, -P.os + pl.hv, d=0, w=1.0)
    p.c(x0 + S + P.cn * 0.36, xh * 0.13, d=60, w=0.5)
    g.add(stk(p, pl))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.sb * 0.5, P.sb * 0.4)


@glyph("upsilon", 0x03C5)
def upsilon(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    pl, _ = pens(P)
    W = P.cn * 1.0 + S * 1.6
    g.add(head_serif(P, 0, S, LC.XT(P)))
    p = Path(S / 2, LC.XT(P) - P.hdd - 10, d=270)
    p.l(S / 2, xh * 0.42)
    p.c(W * 0.52, -P.os + pl.hv, d=0, w=1.0)
    p.c(W - pl.hh, xh * 0.52, d=90, w=1.0)
    p.c(W * 0.88, xh + P.os * 0.4, d=112, w=0.55)
    g.add(stk(p, pl))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.sb, P.rnd * 0.8)


@glyph("phi", 0x03C6)
def phi(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = LC.o_width(P) * 1.18
    cx = W / 2
    g.add(ring(cx, xh / 2, W / 2, xh / 2 + P.os, Pen(P.curve / 2 * 0.95, H / 2, P.ang)))
    g.add(rect(cx - S / 2, P.desc, cx + S / 2, P.asc * 0.86))
    g.add(foot_serif(P, cx - S / 2, cx + S / 2, P.desc))
    LC.anchors_lc(g, cx, P=P)
    g.space(P.rnd, P.rnd)


@glyph("chi", 0x03C7)
def chi(g, P):
    S, H, xh, d = P.stem, P.hair, P.xh, P.desc
    W = P.cn * 1.0 + S * 1.5
    thick, thin = S * 1.02, H * 1.25
    top, bot = xh, d * 0.92
    g.add(quad((0, top), (thick, top), (W, bot), (W - thick, bot)))
    g.add(quad((W - thin, top), (W, top), (thin, bot), (0, bot)))
    s1 = (W - thick) / (top - bot)
    g.add(foot_serif(P, 0, thick, top, el=P.sfx * 0.8, er=P.sfx * 0.5, flip=True, sl=s1, sr=s1))
    g.add(foot_serif(P, W - thick, W, bot, el=P.sfx * 0.5, er=P.sfx * 0.8, sl=-s1, sr=-s1))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


@glyph("psi", 0x03C8)
def psi(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    pl, _ = pens(P)
    W = P.cn * 1.12 + S * 1.8
    cx = W / 2
    g.add(head_serif(P, 0, S, LC.XT(P)))
    p = Path(S / 2, LC.XT(P) - P.hdd - 10, d=270)
    p.l(S / 2, xh * 0.45)
    p.c(cx, -P.os + pl.hv, d=0, w=1.0)
    p.c(W - pl.hh, xh * 0.50, d=90, w=1.0)
    p.c(W * 0.90, xh + P.os * 0.4, d=112, w=0.55)
    g.add(stk(p, pl))
    g.add(rect(cx - S * 0.45, P.desc, cx + S * 0.45, P.asc * 0.86))
    g.add(foot_serif(P, cx - S * 0.45, cx + S * 0.45, P.desc))
    LC.anchors_lc(g, cx, P=P)
    g.space(P.sb, P.rnd * 0.8)


@glyph("omega", 0x03C9)
def omega(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = LC.o_width(P) * 1.40
    cx = W / 2
    pen = Pen(P.curve / 2 * 0.95, H / 2, P.ang)
    for s in (1, -1):
        x = lambda k: cx - s * (cx - k)  # noqa: E731
        p = Path(x(W * 0.22), xh + P.os * 0.4, d=(250 if s > 0 else 290), w=0.6)
        p.c(x(pen.hh), xh * 0.42, d=270, w=1.0)
        p.c(x(W * 0.28), -P.os + pen.hv, d=(0 if s > 0 else 180), w=1.0)
        p.c(x(cx - S * 0.32), xh * 0.28, d=(70 if s > 0 else 110), w=0.8)
        p.c(cx, xh * 0.62, d=90, w=0.6)
        g.add(stk(p, pen))
    LC.anchors_lc(g, cx, P=P)
    g.space(P.rnd, P.rnd)


# ------------------------------------------------------------- tonos

def tonos_shape(P, x, y0, case=False):
    """Tonos: acento agudo mais vertical."""
    S, H = P.stem, P.hair
    hu = 140 if case else 160
    pen = Pen(S * 0.38 + 4, H * 0.45)
    p = Path(x - hu * 0.14, y0, w=0.32).l(x + hu * 0.14, y0 + hu - S * 0.25, w=1.0)
    return stroke(p, pen, "butt", "round")


@glyph("tonoscomb", 0x0341)
def tonoscomb(g, P):
    from .marks import MC
    cx = MC(P)
    g.add(tonos_shape(P, cx, P.xh + 92))
    g.anchor("_top", cx, P.xh)
    g.anchor("top", cx, P.xh + 165 + 30)
    g.space(width=0)


@glyph("tonos", 0x0384)
def tonos(g, P):
    g.add(tonos_shape(P, 0, P.xh + 92))
    g.space(P.sb * 1.6, P.sb * 1.6)


@glyph("dieresistonoscomb", 0x0344)
def dieresistonoscomb(g, P):
    from .marks import MC, M, f_dieresis
    cx = MC(P)
    m = M(P, False)
    sh, top = f_dieresis(m)
    g.add(sh)
    g.add(tonos_shape(P, cx, P.xh + 80))
    g.anchor("_top", cx, P.xh)
    g.anchor("top", cx, P.xh + 220)
    g.space(width=0)


@glyph("dieresistonos", 0x0385)
def dieresistonos(g, P):
    from .marks import M, f_dieresis
    m = M(P, False)
    m.cx = 0
    sh, top = f_dieresis(m)
    g.add(sh)
    g.add(tonos_shape(P, 0, P.xh + 80))
    g.space(P.sb * 1.6, P.sb * 1.6)


# tonos em minúsculas e dialítica: compostos regulares
for _n, _u, _b, _m in [
        ("alphatonos", 0x03AC, "alpha", ["tonoscomb"]),
        ("epsilontonos", 0x03AD, "epsilon", ["tonoscomb"]),
        ("etatonos", 0x03AE, "eta", ["tonoscomb"]),
        ("iotatonos", 0x03AF, "iota", ["tonoscomb"]),
        ("omicrontonos", 0x03CC, "omicron", ["tonoscomb"]),
        ("upsilontonos", 0x03CD, "upsilon", ["tonoscomb"]),
        ("omegatonos", 0x03CE, "omega", ["tonoscomb"]),
        ("iotadieresis", 0x03CA, "iota", ["dieresiscomb"]),
        ("upsilondieresis", 0x03CB, "upsilon", ["dieresiscomb"]),
        ("iotadieresistonos", 0x0390, "iota", ["dieresistonoscomb"]),
        ("upsilondieresistonos", 0x03B0, "upsilon", ["dieresistonoscomb"]),
        ("Iotadieresis", 0x03AA, "Iota", ["dieresiscomb.case"]),
        ("Upsilondieresis", 0x03AB, "Upsilon", ["dieresiscomb.case"])]:
    composite(_n, _u, _b, _m)


def _cap_tonos(base):
    def fn(g, P):
        c, t = borrow(base, P)
        b = contours_bounds(c)
        T = tonos_shape(P, 0, P.cap - 140 + 20, case=True)
        tb = contours_bounds(T)
        g.add(shift(T, -tb[0]))
        gap = P.sbC * 0.8 + 10
        g.add(shift(c, (tb[2] - tb[0]) + gap - b[0] + (t.lsb or 0) * 0))
        g.space(P.sbC * 0.5, t.rsb if t.rsb is not None else P.sbC)
    return fn


for _n, _u, _b in [("Alphatonos", 0x0386, "A"), ("Epsilontonos", 0x0388, "E"),
                   ("Etatonos", 0x0389, "H"), ("Iotatonos", 0x038A, "I"),
                   ("Omicrontonos", 0x038C, "O"), ("Upsilontonos", 0x038E, "Y"),
                   ("Omegatonos", 0x038F, "Omega")]:
    glyph(_n, _u)(_cap_tonos(_b))
