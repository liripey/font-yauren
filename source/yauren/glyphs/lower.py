"""Minúsculas latinas da Yauren.

Convenções: a haste esquerda começa em x=0; o espaçamento final é aplicado
pelo construtor a partir da caixa do desenho (lsb/rsb).
"""
import math

from ..parts import (beak, ellipse, foot_serif, halfplane, head_serif, poly,
                     quad, rect)
from ..glyph import clip
from ..pen import Path, Pen, stroke
from ..registry import glyph


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


# ------------------------------------------------------------- auxiliares

def pens(P):
    return Pen(P.stem / 2, P.hair / 2), Pen(P.curve / 2, P.hair / 2, P.ang)


def XT(P):
    """Topo da serifa de cabeça na altura-x."""
    return P.xh + round(P.os * 0.6)


def stem(g, P, x, y0, y1, head=True, foot="both", el=None, er=None):
    S = P.stem
    g.add(rect(x, y0 if foot else y0, x + S, y1 - (P.hdd + 8 if head else 0)))
    if head:
        g.add(head_serif(P, x, x + S, y1))
    if foot == "both":
        g.add(foot_serif(P, x, x + S, y0, el=el, er=er))
    elif foot == "right":
        g.add(foot_serif(P, x, x + S, y0, el=0, er=P.sfx if er is None else er))
    elif foot == "left":
        g.add(foot_serif(P, x, x + S, y0, el=P.sfx if el is None else el, er=0))


def arch(P, xs, xr, bottom, join=0.60, peak=0.50, top=None, wj=0.30):
    """Arco do n/h/m: sai da haste (borda direita xs) e desce na haste
    cuja borda esquerda é xr, até y=bottom."""
    S, xh = P.stem, P.xh
    pl = Pen(S / 2, P.hair / 2)
    top = xh + P.os if top is None else top
    cnt = xr - xs
    p = Path(xs - S * 0.32, xh * join, d=66, w=wj)
    p.c(xs + cnt * peak, top - pl.hv, d=0, w=1.0)
    p.c(xr + S / 2, xh * 0.50, d=270)
    p.l(xr + S / 2, bottom)
    return stk(p, pl)


def bowl_right(P, xs, W, top_join=0.66, bot_join=0.12, peak=0.46, wj=0.32, wb=0.42,
               top=None, bot=None):
    """Bojo à direita de uma haste (b, p, þ). xs = borda direita da haste."""
    S, xh = P.stem, P.xh
    _, pc = pens(P)
    top = xh + P.os if top is None else top
    bot = -P.os if bot is None else bot
    mid = xs + (W - xs) * peak
    p = Path(xs - S * 0.30, (bot + (top - bot) * top_join), d=60, w=wj)
    p.c(mid, top - pc.hv, d=0, w=1.0)
    p.c(W - pc.hh, (top + bot) / 2 - 4, d=270)
    p.c(mid - 6, bot + pc.hv, d=180)
    p.c(xs - S * 0.2, bot + (top - bot) * bot_join, d=155, w=wb)
    return stk(p, pc)


def bowl_left(P, xs, top_join=0.66, bot_join=0.14, peak=0.54, wj=0.32, wb=0.40,
              top=None, bot=None, x0=0):
    """Bojo à esquerda de uma haste (d, q, a). xs = borda esquerda da haste."""
    S, xh = P.stem, P.xh
    _, pc = pens(P)
    top = xh + P.os if top is None else top
    bot = -P.os if bot is None else bot
    mid = x0 + (xs - x0) * peak
    p = Path(xs + S * 0.30, bot + (top - bot) * top_join, d=120, w=wj)
    p.c(mid, top - pc.hv, d=180, w=1.0)
    p.c(x0 + pc.hh, (top + bot) / 2 + 4, d=270)
    p.c(mid + 4, bot + pc.hv, d=0)
    p.c(xs + S * 0.22, bot + (top - bot) * bot_join, d=28, w=wb)
    return stk(p, pc)


def drop(P, cx, cy, r=None, ry=None):
    """Terminal em gota/bola."""
    r = P.stem * 0.56 + 4 if r is None else r
    return ellipse(cx, cy, r, r * 1.04 if ry is None else ry)


def anchors_lc(g, x, top=None, P=None, bottom_x=None):
    g.anchor("top", x, P.xh if top is None else top)
    g.anchor("bottom", x if bottom_x is None else bottom_x, 0)


# ------------------------------------------------------------- n m h r u

@glyph("n", 0x006E)
def n(g, P):
    S = P.stem
    xr = S + P.cn
    stem(g, P, 0, 0, XT(P))
    g.add(arch(P, S, xr, P.sft))
    g.add(foot_serif(P, xr, xr + S, 0))
    anchors_lc(g, (xr + S) / 2, P=P)
    g.anchor("ogonek", xr + S * 0.7, 0)
    g.space(P.sb, P.sb)


@glyph("h", 0x0068)
def h(g, P):
    S = P.stem
    xr = S + P.cn
    stem(g, P, 0, 0, P.asc)
    g.add(arch(P, S, xr, P.sft))
    g.add(foot_serif(P, xr, xr + S, 0))
    anchors_lc(g, (xr + S) / 2, top=P.asc, P=P)
    g.space(P.sb, P.sb)


@glyph("m", 0x006D)
def m(g, P):
    S = P.stem
    cm = P.cn * 0.84
    x1 = S + cm
    x2 = x1 + S + cm
    stem(g, P, 0, 0, XT(P))
    g.add(arch(P, S, x1, P.sft, join=0.60))
    g.add(foot_serif(P, x1, x1 + S, 0))
    g.add(arch(P, x1 + S, x2, P.sft, join=0.60))
    g.add(foot_serif(P, x2, x2 + S, 0))
    anchors_lc(g, (x2 + S) / 2, P=P)
    g.space(P.sb, P.sb)


@glyph("r", 0x0072)
def r(g, P):
    S, xh = P.stem, P.xh
    pl, _ = pens(P)
    stem(g, P, 0, 0, XT(P), foot="both", er=P.sfx * 1.7)
    top = xh + P.os
    rb = S * 0.56 + 6
    ex = S + P.cn * 0.62
    p = Path(S - S * 0.32, xh * 0.58, d=66, w=0.30)
    p.c(S + P.cn * 0.26, top - pl.hv, d=0, w=1.0)
    p.c(ex - rb * 0.9, top - pl.hv * 1.4, d=-12, w=1.0)
    g.add(stk(p, pl))
    g.add(drop(P, ex - rb, top - rb * 1.05, rb))
    anchors_lc(g, S * 0.9, P=P, bottom_x=S / 2)
    g.space(P.sb, P.sb * 0.6)


@glyph("u", 0x0075)
def u(g, P):
    S, xh = P.stem, P.xh
    pl, _ = pens(P)
    xr = S + P.cn * 0.98
    # haste esquerda + bojo inferior
    g.add(head_serif(P, 0, S, XT(P)))
    bot = -P.os
    p = Path(S / 2, XT(P) - P.hdd - 10, d=270)
    p.l(S / 2, xh * 0.50)
    p.c(S + (xr - S) * 0.48, bot + pl.hv, d=0, w=1.0)
    p.c(xr + S * 0.32, xh * 0.40, d=66, w=0.30)
    g.add(stk(p, pl))
    stem(g, P, xr, 0, XT(P), foot="right")
    anchors_lc(g, (xr + S) / 2, P=P)
    g.anchor("ogonek", xr + S * 0.8, 0)
    g.space(P.sb, P.sb * 0.9)


# ------------------------------------------------------------- i j l

def i_dot(P, cx):
    r = P.stem * 0.62 + 6
    cy = P.xh + (P.asc - P.xh) * 0.62
    return ellipse(cx, cy, r, r)


@glyph("dotlessi", 0x0131)
def dotlessi(g, P):
    S = P.stem
    stem(g, P, 0, 0, XT(P))
    anchors_lc(g, S / 2, P=P)
    g.anchor("ogonek", S * 0.6, 0)
    g.space(P.sb, P.sb)


@glyph("i", 0x0069)
def i(g, P):
    S = P.stem
    stem(g, P, 0, 0, XT(P))
    g.add(i_dot(P, S * 0.5 + 2))
    anchors_lc(g, S / 2, P=P)
    g.anchor("ogonek", S * 0.6, 0)
    g.space(P.sb, P.sb)


def j_body(g, P):
    S, xh, d = P.stem, P.xh, P.desc
    pl, _ = pens(P)
    g.add(head_serif(P, 0, S, XT(P)))
    rb = S * 0.54 + 5
    p = Path(S / 2, XT(P) - P.hdd - 10, d=270)
    p.l(S / 2, d * 0.30)
    p.c(-S * 0.40, d - P.os + pl.hv, d=180, w=1.0)
    p.c(-S * 1.45 + rb * 0.6, d + rb * 0.9, d=145, w=0.75)
    g.add(stk(p, pl))
    g.add(drop(P, -S * 1.45 + rb * 0.85, d - P.os + rb * 1.08, rb))


@glyph("dotlessj", 0x0237)
def dotlessj(g, P):
    j_body(g, P)
    anchors_lc(g, P.stem / 2, P=P)
    g.space(P.sb * 0.6, P.sb)


@glyph("j", 0x006A)
def j(g, P):
    j_body(g, P)
    g.add(i_dot(P, P.stem * 0.5 + 2))
    anchors_lc(g, P.stem / 2, P=P)
    g.space(P.sb * 0.6, P.sb)


@glyph("l", 0x006C)
def l(g, P):
    S = P.stem
    stem(g, P, 0, 0, P.asc)
    anchors_lc(g, S / 2, top=P.asc, P=P)
    g.anchor("center", S / 2, (P.asc - P.hdd) / 2)
    g.space(P.sb, P.sb)


# ------------------------------------------------------------- o c e

def o_width(P):
    return P.cn * 1.10 + 2 * P.curve


@glyph("o", 0x006F)
def o(g, P):
    xh = P.xh
    _, pc = pens(P)
    W = o_width(P)
    t = 0.96
    top = xh + P.os - pc.hv
    bot = -P.os + pc.hv
    p = Path(W - pc.hh, xh / 2, d=90).c(W / 2, top, d=180, t=t).c(pc.hh, xh / 2, d=270, t=t)
    p.c(W / 2, bot, d=0, t=t).close("c", t=t)
    g.add(stk(p, pc))
    anchors_lc(g, W / 2, P=P)
    g.anchor("ogonek", W * 0.55, 0)
    g.space(P.sb * 1.15, P.sb * 1.15)


@glyph("c", 0x0063)
def c(g, P):
    S, xh = P.stem, P.xh
    _, pc = pens(P)
    W = o_width(P) * 0.90
    t = 0.96
    top = xh + P.os
    bot = -P.os
    rb = S * 0.54 + 5
    bx = W - rb
    by = xh - rb * 1.35
    p = Path(bx + rb * 0.15, by + rb * 0.2, d=88, w=0.62)
    p.c(W * 0.52, top - pc.hv, d=180, w=1.0, t=t)
    p.c(pc.hh, xh / 2, d=270, t=t)
    p.c(W * 0.54, bot + pc.hv, d=0, t=t)
    p.c(W + 4, xh * 0.20, d=40, w=0.72)
    g.add(stk(p, pc))
    g.add(drop(P, bx, by, rb))
    anchors_lc(g, W * 0.55, P=P)
    g.anchor("cedilla", W * 0.52, 0)
    g.space(P.sb * 1.15, P.sb * 0.75)


@glyph("e", 0x0065)
def e(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    _, pc = pens(P)
    W = o_width(P) * 0.96
    t = 0.96
    top = xh + P.os
    bot = -P.os
    bar_t = H * 1.05
    yb = xh * 0.56
    g.add(rect(pc.hh, yb - bar_t / 2, W - 1, yb + bar_t / 2))
    p = Path(W - pc.hh * 0.88, yb - bar_t / 2, d=90, w=0.88)
    p.c(W * 0.50, top - pc.hv, d=180, w=1.0, t=t)
    p.c(pc.hh, xh * 0.48, d=270, t=t)
    p.c(W * 0.54, bot + pc.hv, d=0, t=t)
    p.c(W + 6, xh * 0.21, d=42, w=0.70)
    g.add(stk(p, pc))
    anchors_lc(g, W * 0.52, P=P)
    g.anchor("ogonek", W * 0.62, 0)
    g.space(P.sb * 1.15, P.sb * 0.95)


# ------------------------------------------------------------- b d p q

def bowl_width(P):
    return P.stem + P.cn * 1.04 + P.curve


@glyph("b", 0x0062)
def b(g, P):
    S = P.stem
    W = bowl_width(P)
    g.add(rect(0, 0, S, P.asc - P.hdd - 8))
    g.add(head_serif(P, 0, S, P.asc))
    g.add(bowl_right(P, S, W))
    # esporão na base esquerda
    g.add(poly((0, 0), (S, 0), (S, 40), (-S * 0.22, 0)))
    anchors_lc(g, (S + W) / 2, top=P.asc, P=P)
    g.space(P.sb, P.sb * 1.15)


@glyph("p", 0x0070)
def p(g, P):
    S = P.stem
    W = bowl_width(P)
    stem(g, P, 0, P.desc, XT(P), foot="both")
    g.add(bowl_right(P, S, W, top_join=0.64, bot_join=0.10))
    anchors_lc(g, (S + W) / 2, P=P)
    g.space(P.sb, P.sb * 1.15)


@glyph("d", 0x0064)
def d(g, P):
    S = P.stem
    xs = bowl_width(P) - S
    g.add(bowl_left(P, xs))
    stem(g, P, xs, 0, P.asc, foot="right")
    anchors_lc(g, xs / 2 + S * 0.2, P=P)
    g.anchor("topright", xs + S, P.asc)
    g.space(P.sb * 1.15, P.sb)


@glyph("q", 0x0071)
def q(g, P):
    S = P.stem
    xs = bowl_width(P) - S
    g.add(bowl_left(P, xs, top_join=0.64))
    g.add(rect(xs, P.desc, xs + S, P.xh + P.os * 0.6))
    g.add(foot_serif(P, xs, xs + S, P.desc))
    # pequeno esporão no topo à direita
    tp = P.xh + P.os * 0.6
    g.add(poly((xs, tp), (xs + S, tp), (xs + S + S * 0.42, tp - P.hdd * 0.7),
               (xs + S + S * 0.42, tp - P.hdd * 0.7 - P.hair * 0.5), (xs + S, tp - P.hdd - 30),
               (xs, tp - 60)))
    anchors_lc(g, xs / 2 + S * 0.2, P=P)
    g.space(P.sb * 1.15, P.sb)


# ------------------------------------------------------------- a

@glyph("a", 0x0061)
def a(g, P, foot=True):
    S, H, xh = P.stem, P.hair, P.xh
    pl, pc = pens(P)
    W = P.cn * 0.86 + S + P.curve * 0.95
    xs = W - S                  # borda esquerda da haste
    top = xh + P.os
    # haste + gancho superior com gota
    rb = S * 0.56 + 5
    p = Path(xs + S / 2, P.sft + 2, d=90)
    p.l(xs + S / 2, xh * 0.58)
    p.c(xs * 0.52, top - pl.hv, d=180, w=1.0)
    p.c(rb * 1.05 + 4, xh - rb * 1.05, d=242, w=0.82)
    g.add(stk(p, pl))
    g.add(drop(P, rb + 4, xh - rb * 1.22, rb))
    # pé (esporão à direita)
    if foot:
        g.add(foot_serif(P, xs, xs + S, 0, el=0, er=P.sfx * 0.8))
    # bojo
    q = Path(xs + S * 0.32, xh * 0.60, d=198, w=0.55)
    q.c(pc.hh * 0.98, xh * 0.24, d=270, w=1.0)
    q.c(xs * 0.50, -P.os + pc.hv, d=0)
    q.c(xs + S * 0.30, xh * 0.18, d=52, w=0.40)
    g.add(stk(q, pc))
    anchors_lc(g, W * 0.48, P=P)
    g.anchor("ogonek", W - S * 0.3, 0)
    g.space(P.sb * 1.0, P.sb * 0.8)


# ------------------------------------------------------------- s

@glyph("s", 0x0073)
def s(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = o_width(P) * 0.76
    top = xh + P.os
    bot = -P.os
    pen = Pen(P.curve / 2 * 0.96, H / 2, P.ang)
    we = 0.62
    p = Path(W - pen.hh * we, xh * 0.66, d=90, w=we)
    p.c(W * 0.52, top - pen.hv, d=180, w=1.0)
    p.c(pen.hh * 0.95 + 2, xh * 0.745, d=270, w=0.96)
    p.c(W * 0.50, xh * 0.51, d=-31, w=1.25, t=1.0)
    p.c(W - pen.hh * 1.0, xh * 0.25, d=270, w=1.0)
    p.c(W * 0.47, bot + pen.hv, d=180, w=1.0)
    p.c(pen.hh * we, xh * 0.31, d=90, w=we)
    g.add(stk(p, pen))
    # pequenas serifas verticais nos terminais
    ts = pen.hh * we * 2
    g.add(quad((W - ts, xh * 0.66), (W, xh * 0.66), (W, xh * 0.66 - xh * 0.07),
               (W - ts * 0.45, xh * 0.66 - xh * 0.07)))
    g.add(quad((0, xh * 0.31), (ts, xh * 0.31), (ts * 0.55, xh * 0.31 + xh * 0.08),
               (0, xh * 0.31 + xh * 0.08)))
    anchors_lc(g, W / 2, P=P)
    g.anchor("cedilla", W * 0.48, 0)
    g.space(P.sb * 1.0, P.sb * 1.0)


# ------------------------------------------------------------- t f

@glyph("t", 0x0074)
def t(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    pl, _ = pens(P)
    x0 = S * 0.62
    ttop = xh + (P.asc - xh) * 0.42
    # haste com topo inclinado
    g.add(poly((x0, xh - 20), (x0 + S, xh - 20), (x0 + S, ttop), (x0, ttop - P.hdd * 1.4)))
    p = Path(x0 + S / 2, xh, d=270)
    p.l(x0 + S / 2, xh * 0.30)
    p.c(x0 + S + P.cn * 0.22, -P.os + pl.hv, d=0, w=1.0)
    p.c(x0 + S + P.cn * 0.52, xh * 0.17, d=58, w=0.60)
    g.add(stk(p, pl))
    # barra
    bt = H * 1.12
    g.add(rect(0, xh - bt, x0 + S + P.cn * 0.42, xh))
    anchors_lc(g, x0 + S / 2, P=P)
    g.anchor("topright", x0 + S, ttop)
    g.anchor("cedilla", x0 + S * 0.9, 0)
    g.space(P.sb * 0.6, P.sb * 0.5)


@glyph("f", 0x0066)
def f(g, P, bar=True):
    S, H, xh = P.stem, P.hair, P.xh
    pl, _ = pens(P)
    x0 = S * 0.60
    top = P.asc + P.os * 0.5
    rb = S * 0.55 + 6
    stem(g, P, x0, 0, xh, head=False, foot="both", er=P.sfx * 1.4)
    hx = x0 + S + P.cn * 0.56
    p = Path(x0 + S / 2, xh - 10, d=90)
    p.l(x0 + S / 2, P.asc - (P.asc - xh) * 0.50)
    p.c(x0 + S + P.cn * 0.20, top - pl.hv, d=0, w=1.0)
    p.c(hx - rb * 0.9, top - pl.hv * 1.6, d=-16, w=0.95)
    g.add(stk(p, pl))
    g.add(drop(P, hx - rb, top - rb * 1.08, rb))
    bt = H * 1.12
    if bar:
        g.add(rect(0, xh - bt, x0 + S + P.cn * 0.40, xh))
    anchors_lc(g, x0 + S / 2, P=P)
    g.space(P.sb * 0.6, P.sb * 0.2)


# ------------------------------------------------------------- v w x y

def diag_hw(pen_A, pen_B, dx, dy):
    """Largura horizontal de um traço reto (pena elíptica) com direção dx,dy."""
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    s = math.sqrt(pen_A ** 2 * nx ** 2 + pen_B ** 2 * ny ** 2)
    return 2 * s / abs(nx)


def vee(g, P, x0, W, top, bottom, thick, thin, flat, serif_l=True, serif_r=True,
        ext_out=None, ext_in=None, caps=False, apex=0.5):
    """Forma em V: braço grosso à esquerda, fino à direita.
    x0: borda externa esquerda no topo; W: largura externa no topo."""
    xa = x0 + W * apex          # ápice (centro do achatamento)
    ex = (P.sfxC if caps else P.sfx) if ext_out is None else ext_out
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
        g.add(foot_serif(P, L[0], L[0] + thick, top, el=ex, er=ei, flip=True, sl=sl, sr=sl, caps=caps))
    if serif_r:
        g.add(foot_serif(P, R[0] - thin, R[0], top, el=ei, er=ex, flip=True, sl=sr, sr=sr, caps=caps))
    return xa


@glyph("v", 0x0076)
def v(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 1.0 + S * 1.6
    xa = vee(g, P, 0, W, xh, -P.os * 0.7, S * 1.04, H * 1.25, H * 0.7)
    anchors_lc(g, xa, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


@glyph("w", 0x0077)
def w(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 0.80 + S * 1.30
    thick, thin = S * 0.98, H * 1.2
    flat = H * 0.6
    bottom = -P.os * 0.7
    xa1 = vee(g, P, 0, W, xh, bottom, thick, thin, flat, serif_r=False)
    off = W - thin * 0.5 - S * 0.62
    xa2 = vee(g, P, off, W, xh, bottom, thick, thin, flat, serif_l=False)
    anchors_lc(g, (xa1 + xa2) / 2, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


@glyph("x", 0x0078)
def x(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 0.98 + S * 1.5
    thick, thin = S * 1.02, H * 1.25
    ex = P.sfx
    ei = P.sfx * 0.6
    # grosso: topo esquerdo -> base direita
    g.add(quad((0, xh), (thick, xh), (W, 0), (W - thick, 0)))
    g.add(quad((W - thin, xh), (W, xh), (thin, 0), (0, 0)))
    sl = W / xh - thick / xh * 0
    s1 = (W - thick) / xh
    g.add(foot_serif(P, 0, thick, xh, el=ex, er=ei, flip=True, sl=s1, sr=s1))
    g.add(foot_serif(P, W - thick, W, 0, el=ei, er=ex, sl=-s1, sr=-s1))
    s2 = (W - thin) / xh
    g.add(foot_serif(P, W - thin, W, xh, el=ei, er=ex, flip=True, sl=-s2, sr=-s2))
    g.add(foot_serif(P, 0, thin, 0, el=ex, er=ei, sl=s2, sr=s2))
    anchors_lc(g, W / 2, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


@glyph("y", 0x0079)
def y(g, P):
    S, H, xh, d = P.stem, P.hair, P.xh, P.desc
    W = P.cn * 1.0 + S * 1.6
    thick, thin = S * 1.04, H * 1.25
    xa = W * 0.5
    flat = H * 0.7
    bottom = -P.os * 0.4
    L, Lb = (0, xh), (xa - flat / 2, bottom)
    R, Rb = (W, xh), (xa + flat / 2, bottom)
    ex, ei = P.sfx, P.sfx * 0.55
    arm = quad(L, (thick, xh), (Lb[0] + thick, bottom), Lb)
    g.add(clip(arm, halfplane(L, Lb, "right"), halfplane(R, Rb, "left"),
               rect(-2000, bottom - 3000, 4000, bottom)))
    sl = (Lb[0] - L[0]) / (xh - bottom)
    sr = (Rb[0] - R[0]) / (xh - bottom)
    g.add(foot_serif(P, 0, thick, xh, el=ex, er=ei, flip=True, sl=sl, sr=sl))
    # braço fino continua até a cauda
    pt = Pen(thin * 0.62, H / 2)
    dxdy = (Rb[0] - R[0]) / (xh - bottom)
    yk = d * 0.40
    xk = R[0] - thin / 2 + dxdy * (xh - yk)
    rb = S * 0.50 + 5
    p = Path(R[0] - thin / 2, xh + 30)
    p.l(xk, yk)
    p.c(xk - W * 0.36, d - P.os + H * 0.55, d=180, w=1.0, a=S * 0.40, b=H * 0.55)
    p.c(rb * 0.9 - S * 0.4, d + rb * 0.7, d=150, w=1.0, a=S * 0.32, b=H * 0.5)
    g.add(clip(stk(p, pt), rect(-2000, xh, 4000, xh + 400)))
    g.add(drop(P, rb * 0.95 - S * 0.4, d - P.os + rb * 1.06, rb))
    g.add(foot_serif(P, W - thin, W, xh, el=ei, er=ex, flip=True, sl=sr, sr=sr))
    anchors_lc(g, xa, P=P)
    g.space(P.sb * 0.45, P.sb * 0.45)


# ------------------------------------------------------------- k z

@glyph("k", 0x006B)
def k(g, P, short=False):
    S, H, xh = P.stem, P.hair, P.xh
    stem(g, P, 0, 0, XT(P) if short else P.asc)
    W = S + P.cn * 0.86
    thin = H * 1.4
    thick = S * 1.04
    yj = xh * 0.27
    xs0 = S * 0.35
    ax = W - thin * 0.1
    lo0, lo1 = (xs0, yj), (ax - thin, xh)
    up0, up1 = (xs0 + thin, yj), (ax, xh)
    g.add(quad(lo0, up0, up1, lo1))
    sa = (lo1[0] - lo0[0]) / (xh - yj)
    g.add(foot_serif(P, ax - thin, ax, xh, el=P.sfx * 0.55, er=P.sfx * 0.85, flip=True,
                     sl=-sa, sr=-sa))
    # perna: nasce do braço e desce até a base direita
    tj = 0.30
    jx = up0[0] + (up1[0] - up0[0]) * tj
    lx = W + S * 0.22
    leg = quad((jx - thick * 0.62, xh), (jx + thick * 0.38, xh), (lx, 0), (lx - thick, 0))
    g.add(clip(leg, halfplane(up0, up1, "left")))
    jy = up0[1] + (up1[1] - up0[1]) * tj
    sl = (lx - thick - (jx - thick * 0.62)) / xh
    g.add(foot_serif(P, lx - thick, lx, 0, el=P.sfx * 0.55, er=P.sfx * 0.95, sl=-sl, sr=-sl))
    anchors_lc(g, (S + W) / 2 - S * 0.3, top=P.asc, P=P, bottom_x=W / 2)
    g.space(P.sb, P.sb * 0.45)


@glyph("z", 0x007A)
def z(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = P.cn * 0.86 + S * 1.0
    bt = H * 1.12
    bb = H * 1.25
    g.add(rect(0, xh - bt, W - S * 0.2, xh))
    g.add(rect(S * 0.15, 0, W, bb))
    th = diag_hw(S / 2, H / 2, -(W - S * 0.9), -xh)
    g.add(quad((W - th * 1.0, xh - bt + 1), (W, xh - bt + 1), (th, bb - 1), (0, bb - 1)))
    g.add(quad((W - th, xh - bt), (W - S * 0.2, xh), (W, xh), (W, xh - bt)))
    g.add(beak(P, 0, xh, bt, xh * 0.20, S * 0.44, side="left", br=P.sfb * 0.9))
    g.add(beak(P, W, 0, bb, xh * 0.22, S * 0.46, side="right", vert="up", br=P.sfb * 0.9))
    anchors_lc(g, W / 2, P=P)
    g.space(P.sb * 0.7, P.sb * 0.7)


# ------------------------------------------------------------- g

@glyph("g", 0x0067)
def g_(g, P):
    S, H, xh, d = P.stem, P.hair, P.xh, P.desc
    pl, pc = pens(P)
    W = o_width(P) * 0.94
    pen_b = Pen(P.curve / 2 * 0.94, H / 2, P.ang)
    # bojo superior
    bw = W * 0.74
    bx0 = W * 0.03
    btop = xh + P.os
    bbot = xh * 0.22
    cx = bx0 + bw / 2
    cy = (btop + bbot) / 2
    t = 0.97
    q = Path(bx0 + bw - pen_b.hh, cy, d=90).c(cx, btop - pen_b.hv, d=180, t=t)
    q.c(bx0 + pen_b.hh, cy, d=270, t=t).c(cx, bbot + pen_b.hv, d=0, t=t).close("c", t=t)
    g.add(stk(q, pen_b))
    # orelha (cunha horizontal)
    e = Path(cx + bw * 0.18, btop - pen_b.hv * 1.1, d=-2, w=0.85)
    e.c(W + 4, xh + H * 0.25, d=8, w=1.55)
    g.add(stk(e, Pen(S * 0.30, H * 0.55)))
    # elo + laço inferior
    ly = -xh * 0.035
    lb = d - P.os
    pk = Pen(P.curve / 2, H * 0.58, P.ang)
    k = Path(cx - bw * 0.20, bbot + pen_b.hv * 0.8, d=212, w=0.72)
    k.c(W * 0.36, ly + pk.hv * 0.6, d=0, w=1.0, t=0.9)
    k.c(W * 0.82, ly - 4, d=-14, w=1.0)
    k.c(W - pk.hh, (ly + lb) / 2 - 10, d=270, w=1.0)
    k.c(W * 0.47, lb + pk.hv, d=180, w=1.0)
    k.c(pk.hh * 0.9, (ly + lb) / 2 + 8, d=90, w=0.9)
    k.c(W * 0.30, ly - pk.hv * 0.2, d=4, w=0.5)
    g.add(stk(k, pk))
    anchors_lc(g, cx, P=P)
    g.space(P.sb * 0.9, P.sb * 0.5)
