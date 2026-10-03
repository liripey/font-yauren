"""Maiúsculas latinas da Yauren."""
import math

from ..glyph import clip
from ..parts import (beak, ellipse, foot_serif, halfplane, poly, quad, rect)
from ..pen import Path, Pen, stroke
from ..registry import glyph


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def pens(P):
    return Pen(P.stemC / 2, P.hairC / 2), Pen(P.curveC / 2, P.hairC / 2, P.ang)


def anchors_uc(g, P, x, bottom_x=None):
    g.anchor("top", x, P.cap)
    g.anchor("bottom", x if bottom_x is None else bottom_x, 0)


def serifs(g, P, xl, xr, top=True, bottom=True, tl=None, tr=None, bl=None, br=None):
    """Serifas de topo/pé de uma haste vertical de maiúscula."""
    if bottom:
        g.add(foot_serif(P, xl, xr, 0, el=bl, er=br, caps=True))
    if top:
        g.add(foot_serif(P, xl, xr, P.cap, el=tl, er=tr, caps=True, flip=True))


def ustem(g, P, x, top=True, bottom=True, w=None, **kw):
    S = P.stemC if w is None else w
    g.add(rect(x, 0, x + S, P.cap))
    serifs(g, P, x, x + S, top, bottom, **kw)


def arm_t(P, k=1.0):
    return P.hairC * 1.18 * k


# ------------------------------------------------------------- H I E F L T

@glyph("H", 0x0048)
def H(g, P):
    S, cap = P.stemC, P.cap
    W = P.cn * 1.40
    x2 = S + W
    ustem(g, P, 0)
    ustem(g, P, x2)
    bar = arm_t(P, 1.0)
    yc = cap * 0.515
    g.add(rect(S - 1, yc - bar / 2, x2 + 1, yc + bar / 2))
    anchors_uc(g, P, (x2 + S) / 2)
    g.anchor("ogonek", x2 + S * 0.6, 0)
    g.space(P.sbC, P.sbC)


@glyph("I", 0x0049)
def I(g, P):
    S = P.stemC
    ustem(g, P, 0)
    anchors_uc(g, P, S / 2)
    g.anchor("ogonek", S * 0.55, 0)
    g.space(P.sbC, P.sbC)


def e_arms(g, P, S, top_r, mid_r, bot_r, mid_y=0.515, beaks=True):
    cap = P.cap
    tt, mt, bt = arm_t(P, 1.0), arm_t(P, 0.95), arm_t(P, 1.12)
    if top_r:
        g.add(rect(S - 1, cap - tt, top_r, cap))
        g.add(beak(P, top_r, cap, tt, cap * 0.13, S * 0.40, side="right"))
    if mid_r:
        ym = cap * mid_y
        g.add(rect(S - 1, ym - mt / 2, mid_r, ym + mt / 2))
        g.add(beak(P, mid_r, ym + mt / 2, mt, cap * 0.055, S * 0.34, side="right", taper=0.7))
        g.add(beak(P, mid_r, ym - mt / 2, mt, cap * 0.055, S * 0.34, side="right", vert="up", taper=0.7))
    if bot_r:
        g.add(rect(S - 1, 0, bot_r, bt))
        g.add(beak(P, bot_r, 0, bt, cap * 0.15, S * 0.44, side="right", vert="up"))


@glyph("E", 0x0045)
def E(g, P):
    S, cn = P.stemC, P.cn
    g.add(rect(0, 0, S, P.cap))
    serifs(g, P, 0, S, tr=0, br=0)
    e_arms(g, P, S, S + cn * 1.02, S + cn * 0.86, S + cn * 1.12)
    anchors_uc(g, P, (S + cn * 1.0) / 2)
    g.anchor("ogonek", S + cn * 0.9, 0)
    g.space(P.sbC, P.sbC * 0.55)


@glyph("F", 0x0046)
def F(g, P):
    S, cn = P.stemC, P.cn
    g.add(rect(0, 0, S, P.cap))
    serifs(g, P, 0, S, tr=0, br=P.sfxC * 1.1)
    e_arms(g, P, S, S + cn * 1.00, S + cn * 0.84, None, mid_y=0.50)
    anchors_uc(g, P, (S + cn * 0.9) / 2, bottom_x=S / 2)
    g.space(P.sbC, P.sbC * 0.55)


@glyph("L", 0x004C)
def L(g, P):
    S, cn = P.stemC, P.cn
    g.add(rect(0, 0, S, P.cap))
    serifs(g, P, 0, S, br=0)
    e_arms(g, P, S, None, None, S + cn * 1.04)
    anchors_uc(g, P, S / 2 + 10, bottom_x=(S + cn) / 2)
    g.anchor("topright", S + P.sfxC, P.cap)
    g.anchor("center", S + cn * 0.35, P.cap * 0.5)
    g.space(P.sbC, P.sbC * 0.4)


@glyph("T", 0x0054)
def T(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    W = cn * 1.42 + S
    x0 = (W - S) / 2
    tt = arm_t(P, 1.05)
    g.add(rect(x0, 0, x0 + S, cap - tt + 1))
    g.add(foot_serif(P, x0, x0 + S, 0, caps=True))
    g.add(rect(0, cap - tt, W, cap))
    g.add(beak(P, 0, cap, tt, cap * 0.14, S * 0.42, side="left"))
    g.add(beak(P, W, cap, tt, cap * 0.14, S * 0.42, side="right"))
    anchors_uc(g, P, W / 2)
    g.anchor("cedilla", W / 2, 0)
    g.space(P.sbC * 0.45, P.sbC * 0.45)


# ------------------------------------------------------------- P R B D

def p_bowl(P, S, xr, yb, top=None, k=0.42):
    """Bojo do P/R/B: de y=top até yb, encostado à haste (borda direita S)."""
    cap = P.cap
    top = cap if top is None else top
    _, pc = pens(P)
    hv = pc.hv
    xm = S + (xr - S) * k
    p = Path(S - 2, top - hv, d=0)
    p.l(xm, top - hv)
    p.c(xr - pc.hh, (top + yb) / 2, d=270)
    p.c(xm, yb + hv, d=180)
    p.l(S - 2, yb + hv)
    return stk(p, pc)


@glyph("P", 0x0050)
def P_(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    serifs(g, P, 0, S, tr=0, br=P.sfxC * 1.05)
    g.add(p_bowl(P, S, S + cn * 0.72 + P.curveC, cap * 0.40))
    anchors_uc(g, P, (S + cn) / 2, bottom_x=S / 2)
    g.space(P.sbC, P.rndC * 0.8)


@glyph("R", 0x0052)
def R(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    _, pc = pens(P)
    g.add(rect(0, 0, S, cap))
    serifs(g, P, 0, S, tr=0)
    yb = cap * 0.45
    g.add(p_bowl(P, S, S + cn * 0.68 + P.curveC, yb))
    # perna
    lx = S + cn * 0.90 + S * 1.02
    th = S * 1.02
    x0 = S + cn * 0.30
    leg = quad((x0 - th * 0.3, yb + pc.hv * 2), (x0 + th * 0.7, yb + pc.hv * 2), (lx, 0), (lx - th, 0))
    g.add(clip(leg, rect(-100, yb + pc.hv * 1.4, 2000, 2000)))
    sl = (lx - th - (x0 - th * 0.3)) / (yb + pc.hv * 2)
    g.add(foot_serif(P, lx - th, lx, 0, el=P.sfxC * 0.5, er=P.sfxC * 0.85, caps=True,
                     sl=-sl, sr=-sl))
    anchors_uc(g, P, (S + cn) / 2, bottom_x=S / 2)
    g.space(P.sbC, P.sbC * 0.4)


@glyph("B", 0x0042)
def B(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    _, pc = pens(P)
    g.add(rect(0, 0, S, cap))
    serifs(g, P, 0, S, tr=0, br=0)
    ym = cap * 0.54
    g.add(p_bowl(P, S, S + cn * 0.58 + P.curveC, ym - pc.hv * 0.6))
    g.add(p_bowl(P, S, S + cn * 0.71 + P.curveC, 0, top=ym + pc.hv * 0.6, k=0.45))
    anchors_uc(g, P, (S + cn) / 2)
    g.space(P.sbC, P.rndC * 0.85)


@glyph("D", 0x0044)
def D(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    serifs(g, P, 0, S, tr=0, br=0)
    g.add(p_bowl(P, S, S + cn * 1.08 + P.curveC, 0, k=0.34))
    anchors_uc(g, P, (S + cn * 1.3) / 2)
    g.space(P.sbC, P.rndC)


# ------------------------------------------------------------- O Q C G

def o_width_uc(P):
    return P.cn * 1.46 + 2 * P.curveC


def o_ring(P, x0, W, t=0.97):
    cap = P.cap
    _, pc = pens(P)
    top = cap + P.osC - pc.hv
    bot = -P.osC + pc.hv
    cy = cap / 2
    p = Path(x0 + W - pc.hh, cy, d=90).c(x0 + W / 2, top, d=180, t=t).c(x0 + pc.hh, cy, d=270, t=t)
    p.c(x0 + W / 2, bot, d=0, t=t).close("c", t=t)
    return stk(p, pc)


@glyph("O", 0x004F)
def O(g, P):
    W = o_width_uc(P)
    g.add(o_ring(P, 0, W))
    anchors_uc(g, P, W / 2)
    g.anchor("ogonek", W * 0.55, 0)
    g.space(P.rndC, P.rndC)


@glyph("Q", 0x0051)
def Q(g, P):
    W = o_width_uc(P)
    S, H = P.stemC, P.hairC
    g.add(o_ring(P, 0, W))
    p = Path(W * 0.42, P.osC * 0.2, d=-28, w=1.0)
    p.c(W * 0.80, -P.cap * 0.14, d=-8, w=0.8)
    p.c(W * 1.06, -P.cap * 0.20, d=-2, w=0.35)
    g.add(stk(p, Pen(S * 0.46, H * 0.62)))
    anchors_uc(g, P, W / 2)
    g.space(P.rndC, P.rndC * 0.6)


@glyph("C", 0x0043)
def C(g, P):
    S, cap = P.stemC, P.cap
    _, pc = pens(P)
    W = P.cn * 1.34 + 2 * P.curveC
    t = 0.97
    top = cap + P.osC
    bot = -P.osC
    we = 0.62
    p = Path(W - pc.hh * we, cap * 0.72, d=90, w=we)
    p.c(W * 0.53, top - pc.hv, d=180, w=1.0, t=t)
    p.c(pc.hh, cap / 2, d=270, t=t)
    p.c(W * 0.54, bot + pc.hv, d=0, t=t)
    p.c(W + 6, cap * 0.17, d=42, w=0.72)
    g.add(stk(p, pc))
    # serifa vertical do terminal superior
    ts = pc.hh * we * 2
    hs = cap * 0.07 * (1 - 0.55 * P.wf)
    g.add(quad((W - ts, cap * 0.72), (W, cap * 0.72), (W, cap * 0.72 - hs),
               (W - ts * 0.3, cap * 0.72 - hs)))
    anchors_uc(g, P, W * 0.55)
    g.anchor("cedilla", W * 0.53, 0)
    g.space(P.rndC, P.rndC * 0.55)


@glyph("G", 0x0047)
def G(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    _, pc = pens(P)
    W = P.cn * 1.38 + 2 * P.curveC
    t = 0.97
    top = cap + P.osC
    bot = -P.osC
    we = 0.62
    p = Path(W - pc.hh * we, cap * 0.72, d=90, w=we)
    p.c(W * 0.53, top - pc.hv, d=180, w=1.0, t=t)
    p.c(pc.hh, cap / 2, d=270, t=t)
    p.c(W * 0.53, bot + pc.hv, d=0, t=t)
    p.c(W - S / 2, cap * 0.22, d=72, w=1.0, a=S / 2, b=H / 2)
    p.l(W - S / 2, cap * 0.42)
    g.add(stk(p, Pen(pc.A, pc.B, P.ang)))
    ts = pc.hh * we * 2
    hs = cap * 0.07 * (1 - 0.55 * P.wf)
    g.add(quad((W - ts, cap * 0.72), (W, cap * 0.72), (W, cap * 0.72 - hs),
               (W - ts * 0.3, cap * 0.72 - hs)))
    # barra/serifa do queixo
    yb = cap * 0.42
    g.add(foot_serif(P, W - S, W, yb, el=P.cn * 0.30, er=P.sfxC * 0.4, caps=True, flip=True))
    anchors_uc(g, P, W * 0.55)
    g.anchor("cedilla", W * 0.52, 0)
    g.space(P.rndC, P.sbC * 0.8)


# ------------------------------------------------------------- S

@glyph("S", 0x0053)
def S_(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 0.98 + P.curveC * 1.15
    top = cap + P.osC
    bot = -P.osC
    pen = Pen(P.curveC / 2 * 0.96, H / 2, P.ang)
    we = 0.62
    p = Path(W - pen.hh * we, cap * 0.70, d=90, w=we)
    p.c(W * 0.52, top - pen.hv, d=180, w=1.0)
    p.c(pen.hh * 0.95 + 2, cap * 0.75, d=270, w=0.96)
    p.c(W * 0.50, cap * 0.51, d=-33, w=1.22, t=1.0)
    p.c(W - pen.hh * 1.0, cap * 0.245, d=270, w=1.0)
    p.c(W * 0.47, bot + pen.hv, d=180, w=1.0)
    p.c(pen.hh * we, cap * 0.28, d=90, w=we)
    g.add(stk(p, pen))
    ts = pen.hh * we * 2
    hs = cap * 0.07 * (1 - 0.55 * P.wf)
    g.add(quad((W - ts, cap * 0.70), (W, cap * 0.70), (W, cap * 0.70 - hs),
               (W - ts * 0.3, cap * 0.70 - hs)))
    g.add(quad((0, cap * 0.28), (ts, cap * 0.28), (ts * 0.3, cap * 0.28 + hs * 1.1),
               (0, cap * 0.28 + hs * 1.1)))
    anchors_uc(g, P, W / 2)
    g.anchor("cedilla", W * 0.48, 0)
    g.space(P.rndC * 0.75, P.rndC * 0.75)


# ------------------------------------------------------------- U J

@glyph("U", 0x0055)
def U(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.36 + S * 1.62
    thin = S * 0.60
    pl = Pen(S / 2, H / 2)
    bot = -P.osC
    p = Path(S / 2, cap - 20, d=270)
    p.l(S / 2, cap * 0.34)
    p.c(W * 0.50, bot + pl.hv * 1.1, d=0, w=1.0)
    p.c(W - thin / 2, cap * 0.32, d=90, w=1.0, a=thin / 2)
    p.l(W - thin / 2, cap - 20)
    g.add(stk(p, pl))
    serifs(g, P, 0, S, bottom=False)
    serifs(g, P, W - thin, W, bottom=False, tl=P.sfxC * 0.85, tr=P.sfxC * 0.85)
    anchors_uc(g, P, W / 2)
    g.anchor("ogonek", W * 0.55, 0)
    g.space(P.sbC, P.sbC)


@glyph("J", 0x004A)
def J(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    pl = Pen(S / 2, H / 2)
    rb = (S * 0.52 + 5) * (1 - 0.15 * P.wf)
    x0 = S * 0.9
    p = Path(x0 + S / 2, cap - 20, d=270)
    p.l(x0 + S / 2, cap * 0.10)
    p.c(x0 - S * 0.35, -P.cap * 0.16 + pl.hv, d=180, w=1.0)
    p.c(x0 - S * 1.35 + rb * 0.5, -P.cap * 0.16 + rb * 0.85, d=150, w=0.75)
    g.add(stk(p, pl))
    g.add(ellipse(x0 - S * 1.35 + rb * 0.8, -P.cap * 0.16 + rb * 1.02, rb, rb * 1.04))
    serifs(g, P, x0, x0 + S, bottom=False)
    anchors_uc(g, P, x0 + S / 2)
    g.space(P.sbC * 0.5, P.sbC)


# ------------------------------------------------------------- V W X Y A

def vee(g, P, x0, W, top, bottom, thick, thin, flat, serif_l=True, serif_r=True,
        ext_out=None, ext_in=None, apex=0.5):
    xa = x0 + W * apex
    ex = P.sfxC if ext_out is None else ext_out
    ei = ex * 0.55 if ext_in is None else ext_in
    L = (x0, top)
    Lb = (xa - flat / 2, bottom)
    R = (x0 + W, top)
    Rb = (xa + flat / 2, bottom)
    arms = (quad(L, (L[0] + thick, top), (Lb[0] + thick, bottom), Lb) +
            quad((R[0] - thin, top), R, Rb, (Rb[0] - thin, bottom)))
    g.add(clip(arms, halfplane(L, Lb, "right"), halfplane(R, Rb, "left"),
               rect(-2000, bottom - 3000, 4000, bottom)))
    sl = (Lb[0] - L[0]) / (top - bottom)
    sr = (Rb[0] - R[0]) / (top - bottom)
    if serif_l:
        g.add(foot_serif(P, L[0], L[0] + thick, top, el=ex, er=ei, flip=True, sl=sl, sr=sl, caps=True))
    if serif_r:
        g.add(foot_serif(P, R[0] - thin, R[0], top, el=ei, er=ex, flip=True, sl=sr, sr=sr, caps=True))
    return xa


@glyph("V", 0x0056)
def V(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.40 + S * 1.5
    xa = vee(g, P, 0, W, cap, -P.osC * 0.8, S * 1.06, H * 1.3, H * 0.6)
    anchors_uc(g, P, xa)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@glyph("W", 0x0057)
def W_(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.08 + S * 1.3
    thick, thin = S * 1.02, H * 1.25
    bottom = -P.osC * 0.8
    xa1 = vee(g, P, 0, W, cap, bottom, thick, thin, H * 0.5, serif_r=False)
    off = W - thin * 0.5 - S * 0.66
    xa2 = vee(g, P, off, W, cap, bottom, thick, thin, H * 0.5, serif_l=False)
    anchors_uc(g, P, (xa1 + xa2) / 2)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@glyph("X", 0x0058)
def X(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.30 + S * 1.45
    thick, thin = S * 1.05, H * 1.3
    ex, ei = P.sfxC, P.sfxC * 0.6
    g.add(quad((0, cap), (thick, cap), (W, 0), (W - thick, 0)))
    g.add(quad((W - thin, cap), (W, cap), (thin, 0), (0, 0)))
    s1 = (W - thick) / cap
    g.add(foot_serif(P, 0, thick, cap, el=ex, er=ei, flip=True, sl=s1, sr=s1, caps=True))
    g.add(foot_serif(P, W - thick, W, 0, el=ei, er=ex, sl=-s1, sr=-s1, caps=True))
    s2 = (W - thin) / cap
    g.add(foot_serif(P, W - thin, W, cap, el=ei, er=ex, flip=True, sl=-s2, sr=-s2, caps=True))
    g.add(foot_serif(P, 0, thin, 0, el=ex, er=ei, sl=s2, sr=s2, caps=True))
    anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@glyph("Y", 0x0059)
def Y(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.40 + S * 1.5
    thick, thin = S * 1.04, H * 1.3
    xc = W / 2
    yj = cap * 0.44
    # haste
    g.add(rect(xc - S / 2, 0, xc + S / 2, yj + 10))
    g.add(foot_serif(P, xc - S / 2, xc + S / 2, 0, caps=True))
    # braços até a junção
    L, Lb = (0, cap), (xc - S / 2, yj)
    R, Rb = (W, cap), (xc + S / 2, yj)
    a1 = quad(L, (thick, cap), (Lb[0] + thick, yj - 40), (Lb[0], yj - 40))
    a2 = quad((W - thin, cap), R, (Rb[0], yj - 40), (Rb[0] - thin, yj - 40))
    g.add(clip(a1 + a2, halfplane(L, Lb, "right"), halfplane(R, Rb, "left"),
               rect(-2000, -2000, 4000, yj - 30)))
    sl = (Lb[0] - L[0]) / (cap - yj + 40)
    sr = (Rb[0] - R[0]) / (cap - yj + 40)
    g.add(foot_serif(P, 0, thick, cap, el=P.sfxC, er=P.sfxC * 0.55, flip=True, sl=sl, sr=sl, caps=True))
    g.add(foot_serif(P, W - thin, W, cap, el=P.sfxC * 0.55, er=P.sfxC, flip=True, sl=sr, sr=sr, caps=True))
    anchors_uc(g, P, xc)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@glyph("A", 0x0041)
def A(g, P, bar=True):
    S, H, cap = P.stemC, P.hairC, P.cap
    W = P.cn * 1.46 + S * 1.45
    thick, thin = S * 1.06, H * 1.3
    top = cap + P.osC * 0.9
    flat = H * 0.5
    xa = W * 0.5
    Lt, Rt = (xa - flat / 2, top), (xa + flat / 2, top)
    Lb, Rb = (0, 0), (W, 0)
    arms = (quad(Lb, (thin, 0), (Lt[0] + thin, top), Lt) +
            quad((W - thick, 0), Rb, Rt, (Rt[0] - thick, top)))
    g.add(clip(arms, halfplane(Lb, Lt, "left"), halfplane(Rb, Rt, "right"),
               rect(-2000, top, 4000, top + 3000)))
    # barra
    yb = cap * 0.30
    bt = arm_t(P, 0.95)
    k1 = yb / top
    xl = Lb[0] + (Lt[0] - Lb[0]) * k1
    xr = Rb[0] + (Rt[0] - Rb[0]) * k1
    if bar:
        g.add(rect(xl + thin * 0.5, yb - bt / 2, xr - thick * 0.5, yb + bt / 2))
    sl = (Lt[0] - Lb[0]) / top
    sr = (Rt[0] - Rb[0]) / top
    g.add(foot_serif(P, 0, thin, 0, el=P.sfxC, er=P.sfxC * 0.6, sl=sl, sr=sl, caps=True))
    g.add(foot_serif(P, W - thick, W, 0, el=P.sfxC * 0.6, er=P.sfxC, sl=sr, sr=sr, caps=True))
    anchors_uc(g, P, xa)
    g.anchor("ogonek", W - S * 0.4, 0)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


# ------------------------------------------------------------- K M N Z

@glyph("K", 0x004B)
def K(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    ustem(g, P, 0)
    W = S * 1.45 + cn * 0.95
    thin = H * 1.4
    thick = S * 1.06
    yj = cap * 0.30
    xs0 = S * 0.4
    ax = W - thin * 0.2
    lo0, lo1 = (xs0, yj), (ax - thin, cap)
    up0, up1 = (xs0 + thin, yj), (ax, cap)
    g.add(quad(lo0, up0, up1, lo1))
    sa = (lo1[0] - lo0[0]) / (cap - yj)
    g.add(foot_serif(P, ax - thin, ax, cap, el=P.sfxC * 0.55, er=P.sfxC * 0.85, flip=True,
                     sl=-sa, sr=-sa, caps=True))
    tj = 0.26
    jx = up0[0] + (up1[0] - up0[0]) * tj
    lx = W + S * 0.25
    leg = quad((jx - thick * 0.62, cap), (jx + thick * 0.38, cap), (lx, 0), (lx - thick, 0))
    g.add(clip(leg, halfplane(up0, up1, "left")))
    sl = (lx - thick - (jx - thick * 0.62)) / cap
    g.add(foot_serif(P, lx - thick, lx, 0, el=P.sfxC * 0.55, er=P.sfxC * 0.95, sl=-sl, sr=-sl,
                     caps=True))
    anchors_uc(g, P, (S + W) / 2 - S * 0.3, bottom_x=W / 2)
    g.space(P.sbC, P.sbC * 0.3)


@glyph("N", 0x004E)
def N(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    thin = H * 1.45
    W = cn * 1.30 + S * 1.6
    # hastes finas
    g.add(rect(0, 0, thin, cap))
    g.add(rect(W - thin, 0, W, cap))
    # diagonal grossa
    diag = quad((0, cap), (S * 1.12, cap), (W, -P.osC * 0.6), (W - S * 1.12, -P.osC * 0.6))
    g.add(clip(diag, rect(-1000, -2000, 0, 2000), rect(W, -2000, 3000, 2000),
               rect(-1000, -2000, 3000, -P.osC * 0.6)))
    g.add(foot_serif(P, 0, thin, 0, caps=True))
    g.add(foot_serif(P, 0, thin, cap, el=P.sfxC, er=0, caps=True, flip=True))
    g.add(foot_serif(P, W - thin, W, cap, caps=True, flip=True))
    anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC)


@glyph("M", 0x004D)
def M(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    thin = H * 1.45
    W = cn * 1.72 + S * 1.9
    xv = W * 0.5
    # hastes externas (esq. fina, dir. grossa)
    g.add(rect(0, 0, thin, cap))
    g.add(rect(W - S, 0, W, cap))
    vb = -P.osC * 0.6
    d1 = quad((0, cap), (S * 1.1, cap), (xv + S * 0.45, vb), (xv - S * 0.65, vb))
    d2 = quad((W - S * 0.5 - thin, cap), (W - S * 0.5, cap), (xv + S * 0.45, vb), (xv + S * 0.45 - thin, vb))
    g.add(clip(d1 + d2, rect(-1000, -2000, 0, 2000), rect(-1000, -2000, 3000, vb)))
    g.add(foot_serif(P, 0, thin, 0, caps=True))
    g.add(foot_serif(P, 0, thin, cap, el=P.sfxC, er=0, caps=True, flip=True))
    g.add(foot_serif(P, W - S, W, 0, caps=True))
    g.add(foot_serif(P, W - S, W, cap, el=0, er=P.sfxC, caps=True, flip=True))
    anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC)


@glyph("Z", 0x005A)
def Z(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    W = cn * 1.18 + S * 1.0
    bt = arm_t(P, 1.0)
    bb = arm_t(P, 1.12)
    g.add(rect(S * 0.12, cap - bt, W, cap))
    g.add(rect(0, 0, W, bb))
    th = S * 1.10
    g.add(clip(quad((W - th, cap), (W, cap), (th, 0), (0, 0)),
               rect(W, -100, 3000, 2000), rect(-1000, -100, 0, 2000)))
    g.add(beak(P, S * 0.12, cap, bt, cap * 0.14, S * 0.40, side="left"))
    g.add(beak(P, W, 0, bb, cap * 0.16, S * 0.44, side="right", vert="up"))
    anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.7, P.sbC * 0.7)
