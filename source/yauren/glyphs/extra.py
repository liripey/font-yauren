"""Letras latinas especiais: Æ æ Œ œ Ø ø Ð ð Đ đ Þ þ ß ẞ Ħ ħ Ł ł Ŀ ŀ Ŧ ŧ
Ŋ ŋ ĸ ŉ Ĳ ĳ Ə ə ƒ ſ."""
from ..glyph import Glyph, clip, contours_bounds, transform_contours
from ..parts import ellipse, foot_serif, halfplane, head_serif, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import borrow, glyph
from . import lower as LC
from . import upper as UC
from .punct import comma_shape, qright, rdot


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def shift(c, dx=0, dy=0):
    return transform_contours(c, dx=dx, dy=dy)


def run(fn, P, **kw):
    t = Glyph("tmp")
    fn(t, P, **kw)
    t.solve()
    return t.contours, t


# ------------------------------------------------------------- Æ æ Œ œ

@glyph("AE", 0x00C6)
def AE(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    thin = H * 1.3
    xe = cn * 0.82 + S * 0.7
    diag = quad((0, 0), (thin, 0), (xe + thin * 0.5, cap), (xe - thin * 0.5, cap))
    g.add(clip(diag, rect(-1000, cap, 3000, cap + 500)))
    g.add(rect(xe, 0, xe + S, cap))
    tt = UC.arm_t(P)
    g.add(rect(xe - thin * 0.8, cap - tt, xe + S, cap))
    UC.e_arms(g, P, xe + S, xe + S + cn * 0.80, xe + S + cn * 0.66, xe + S + cn * 0.88)
    yb = cap * 0.30
    bt = UC.arm_t(P, 0.95)
    xl = (xe - thin * 0.5) * yb / cap
    g.add(rect(xl + thin * 0.5, yb - bt / 2, xe + 1, yb + bt / 2))
    sl = (xe - thin * 0.5) / cap
    g.add(foot_serif(P, 0, thin, 0, el=P.sfxC, er=P.sfxC * 0.6, sl=sl, sr=sl, caps=True))
    g.add(foot_serif(P, xe, xe + S, 0, el=P.sfxC * 0.8, er=0, caps=True))
    UC.anchors_uc(g, P, (xe + S + cn * 0.4))
    g.space(P.sbC * 0.3, P.sbC * 0.55)


@glyph("ae", 0x00E6)
def ae(g, P):
    S = P.stem
    A, _ = run(LC.a, P, foot=False)
    E, _ = borrow("e", P)
    Wa = P.cn * 0.86 + S + P.curve * 0.95
    xs = Wa - S
    g.add(A)
    g.add(shift(E, xs + S / 2 - P.curve / 2))
    LC.anchors_lc(g, xs + S / 2, P=P)
    g.space(P.rnd * 0.8, P.rnd * 0.72)


@glyph("OE", 0x0152)
def OE(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    _, pc = UC.pens(P)
    xe = cn * 0.86 + P.curveC
    t = 0.97
    p = Path(xe + 4, cap + P.osC - pc.hv, d=180, w=0.9)
    p.c(pc.hh, cap / 2, d=270, t=t, w=1.0)
    p.c(xe + 4, -P.osC + pc.hv, d=0, t=t, w=0.9)
    g.add(stk(p, pc))
    g.add(rect(xe, 0, xe + S, cap))
    UC.e_arms(g, P, xe + S, xe + S + cn * 0.80, xe + S + cn * 0.66, xe + S + cn * 0.88)
    UC.anchors_uc(g, P, (xe + S) * 0.62)
    g.space(P.sbC * 1.05, P.sbC * 0.55)


@glyph("oe", 0x0153)
def oe(g, P):
    O, _ = borrow("o", P)
    E, _ = borrow("e", P)
    g.add(O)
    g.add(shift(E, LC.o_width(P) - P.curve * 1.02))
    LC.anchors_lc(g, LC.o_width(P), P=P)
    g.space(P.rnd, P.rnd * 0.72)


# ------------------------------------------------------------- Ø ø

def slash_over(P, contours, k=1.0):
    b = contours_bounds(contours)
    W = b[2] - b[0]
    Hh = b[3] - b[1]
    pen = Pen(P.hair * 0.72 * k + P.stem * 0.06, P.hair * 0.5)
    p = Path(b[0] - W * 0.03, b[1] - Hh * 0.06).l(b[2] + W * 0.03, b[3] + Hh * 0.06)
    return stk(p, pen)


@glyph("Oslash", 0x00D8)
def Oslash(g, P):
    O, _ = borrow("O", P)
    g.add(O)
    g.add(slash_over(P, O, 1.1))
    W = UC.o_width_uc(P)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 1.05, P.sbC * 1.05)


@glyph("oslash", 0x00F8)
def oslash(g, P):
    O, _ = borrow("o", P)
    g.add(O)
    g.add(slash_over(P, O))
    LC.anchors_lc(g, LC.o_width(P) / 2, P=P)
    g.space(P.rnd, P.rnd)


# ------------------------------------------------------------- Ð ð Đ đ Þ þ

def eth_cap(g, P):
    D, _ = borrow("D", P)
    g.add(D)
    S, cn = P.stemC, P.cn
    t = UC.arm_t(P, 0.95)
    yb = P.cap * 0.49
    g.add(rect(-S * 0.42, yb - t / 2, S + cn * 0.36, yb + t / 2))
    UC.anchors_uc(g, P, (S + cn * 1.3) / 2)
    g.space(P.sbC * 0.6, P.sbC * 1.1)


glyph("Eth", 0x00D0)(eth_cap)
glyph("Dcroat", 0x0110)(eth_cap)


@glyph("dcroat", 0x0111)
def dcroat(g, P):
    D, _ = borrow("d", P)
    g.add(D)
    S = P.stem
    xs = LC.bowl_width(P) - S
    t = P.hair * 1.15
    yb = P.xh + (P.asc - P.xh) * 0.45
    g.add(rect(xs - S * 0.95, yb - t / 2, xs + S + S * 0.40, yb + t / 2))
    LC.anchors_lc(g, xs / 2 + S * 0.2, P=P)
    g.space(P.rnd, P.sb * 0.8)


@glyph("eth", 0x00F0)
def eth(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    _, pc = LC.pens(P)
    W = LC.o_width(P) * 0.96
    t = 0.96
    top = xh * 0.98 + P.os - pc.hv
    bot = -P.os + pc.hv
    cy = (top + bot) / 2
    p = Path(W - pc.hh, cy, d=90).c(W / 2, top, d=180, t=t).c(pc.hh, cy, d=270, t=t)
    p.c(W / 2, bot, d=0, t=t).close("c", t=t)
    g.add(stk(p, pc))
    q = Path(W - pc.hh, cy, d=90, w=1.0)
    q.c(W * 0.70, asc * 0.86, d=128, w=0.9)
    q.c(W * 0.20, asc + P.os * 0.3, d=162, w=0.35)
    g.add(stk(q, pc))
    g.add(stk(Path(W * 0.26, asc * 0.73).l(W * 0.82, asc * 0.92), Pen(S * 0.22, H * 0.55)))
    LC.anchors_lc(g, W / 2, P=P)
    g.space(P.rnd, P.rnd)


@glyph("Thorn", 0x00DE)
def Thorn(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    UC.serifs(g, P, 0, S)
    g.add(UC.p_bowl(P, S, S + cn * 0.72 + P.curveC, cap * 0.20, top=cap * 0.80))
    UC.anchors_uc(g, P, S / 2 + 20)
    g.space(P.sbC, P.sbC * 0.7)


@glyph("thorn", 0x00FE)
def thorn(g, P):
    S = P.stem
    W = LC.bowl_width(P)
    LC.stem(g, P, 0, P.desc, P.asc, foot="both")
    g.add(LC.bowl_right(P, S, W, top_join=0.64, bot_join=0.10))
    LC.anchors_lc(g, (S + W) / 2, top=P.asc, P=P)
    g.space(P.sb, P.rnd)


# ------------------------------------------------------------- ß ẞ

@glyph("germandbls", 0x00DF)
def germandbls(g, P):
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    pl, pc = LC.pens(P)
    W = S + P.cn * 0.84 + P.curve * 0.92
    g.add(rect(0, 0, S, asc * 0.62))
    g.add(foot_serif(P, 0, S, 0))
    top = asc + P.os * 0.5
    p = Path(S / 2, asc * 0.60, d=90)
    p.c(S + (W - S) * 0.30, top - pl.hv, d=0, w=1.0)
    p.c(W * 0.86 - pc.hh * 0.9, asc * 0.79, d=270, w=0.9)
    p.c(W * 0.50, xh * 1.0, d=196, w=0.55)
    g.add(stk(p, pl))
    q = Path(W * 0.50, xh * 1.0, d=-8, w=0.55)
    q.c(W - pc.hh, xh * 0.38, d=270, w=1.0)
    q.c(W * 0.55, -P.os + pc.hv, d=180, w=1.0)
    q.c(S + 18, xh * 0.08, d=158, w=0.5)
    g.add(stk(q, pc))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.sb, P.rnd * 0.8)


@glyph("Germandbls", 0x1E9E)
def Germandbls(g, P):
    S, H, cap, cn = P.stemC, P.hairC, P.cap, P.cn
    pl, pc = UC.pens(P)
    W = S + cn * 0.95 + P.curveC
    g.add(rect(0, 0, S, cap))
    UC.serifs(g, P, 0, S, tr=0)
    tt = UC.arm_t(P)
    g.add(rect(S - 1, cap - tt, W * 0.84, cap))
    d = Path(W * 0.84, cap - tt * 0.5).l(W * 0.44, cap * 0.56)
    g.add(clip(stk(d, Pen(S * 0.46, H * 0.5)), rect(-100, cap, 3000, cap + 400)))
    q = Path(W * 0.42, cap * 0.57, d=0, w=0.7)
    q.c(W - pc.hh, cap * 0.28, d=270, w=1.0)
    q.c(W * 0.55, -P.osC + pc.hv, d=180, w=1.0)
    q.c(S + 20, cap * 0.06, d=165, w=0.5)
    g.add(stk(q, pc))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC * 0.9)


# ------------------------------------------------------------- Ħ ħ Ł ł Ŀ ŀ Ŧ ŧ

@glyph("Hbar", 0x0126)
def Hbar(g, P):
    Hc, _ = borrow("H", P)
    g.add(Hc)
    S = P.stemC
    W = 2 * S + P.cn * 1.40
    t = UC.arm_t(P, 0.95)
    yb = P.cap * 0.77
    g.add(rect(-S * 0.30, yb - t / 2, W + S * 0.30, yb + t / 2))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC)


@glyph("hbar", 0x0127)
def hbar(g, P):
    h, _ = borrow("h", P)
    g.add(h)
    S = P.stem
    t = P.hair * 1.15
    yb = P.xh + (P.asc - P.xh) * 0.45
    g.add(rect(-S * 0.55, yb - t / 2, S + S * 0.85, yb + t / 2))
    LC.anchors_lc(g, (2 * S + P.cn) / 2, top=P.asc, P=P)
    g.space(P.sb, P.sb)


def lslash_bar(P, xc, yc, d):
    pen = Pen(P.stem * 0.30, P.hair * 0.58)
    return stk(Path(xc - d, yc - d * 0.55).l(xc + d, yc + d * 0.55), pen)


@glyph("Lslash", 0x0141)
def Lslash(g, P):
    Lc, _ = borrow("L", P)
    g.add(Lc)
    S = P.stemC
    g.add(lslash_bar(P, S / 2, P.cap * 0.47, S * 1.05))
    UC.anchors_uc(g, P, S / 2 + 10, bottom_x=(S + P.cn) / 2)
    g.space(P.sbC * 0.5, P.sbC * 0.4)


@glyph("lslash", 0x0142)
def lslash(g, P):
    l, _ = borrow("l", P)
    g.add(l)
    S = P.stem
    g.add(lslash_bar(P, S / 2, P.asc * 0.50, S * 1.15))
    LC.anchors_lc(g, S / 2, top=P.asc, P=P)
    g.space(P.sb * 0.7, P.sb * 0.7)


@glyph("Ldot", 0x013F)
def Ldot(g, P):
    Lc, _ = borrow("L", P)
    g.add(Lc)
    S = P.stemC
    r = rdot(P) * 0.95
    g.add(ellipse(S + P.cn * 0.38, P.cap * 0.47, r, r))
    UC.anchors_uc(g, P, S / 2 + 10, bottom_x=(S + P.cn) / 2)
    g.space(P.sbC, P.sbC * 0.4)


@glyph("ldot", 0x0140)
def ldot(g, P):
    l, _ = borrow("l", P)
    g.add(l)
    S = P.stem
    r = rdot(P) * 0.95
    g.add(ellipse(S + P.sfx + r + 18, P.xh * 0.52, r, r))
    LC.anchors_lc(g, S / 2, top=P.asc, P=P)
    g.space(P.sb, P.sb * 1.4)


@glyph("Tbar", 0x0166)
def Tbar(g, P):
    T, _ = borrow("T", P)
    g.add(T)
    S, cn = P.stemC, P.cn
    W = cn * 1.42 + S
    x0 = (W - S) / 2
    t = UC.arm_t(P, 0.95)
    yb = P.cap * 0.47
    g.add(rect(x0 - S * 0.75, yb - t / 2, x0 + S * 1.75, yb + t / 2))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.5, P.sbC * 0.5)


@glyph("tbar", 0x0167)
def tbar(g, P):
    T, _ = borrow("t", P)
    g.add(T)
    S = P.stem
    x0 = S * 0.62
    t = P.hair * 1.1
    yb = P.xh * 0.42
    g.add(rect(x0 - S * 0.45, yb - t / 2, x0 + S * 1.55, yb + t / 2))
    LC.anchors_lc(g, x0 + S / 2, P=P)
    g.space(P.sb * 0.6, P.sb * 0.5)


# ------------------------------------------------------------- Ŋ ŋ ĸ ŉ

def P0stem(P):
    return getattr(P, "lc_stem", P.stem)


def eng_body(g, P):
    S, xh, d = P.stem, P.xh, P.desc
    pl = Pen(S / 2, P.hair / 2)
    xr = S + P.cn
    LC.stem(g, P, 0, 0, LC.XT(P))
    g.add(LC.arch(P, S, xr, 0))
    rb = LC.rbf(P, 0.54)
    reach = S * 1.55 + P.cn * 0.12 if S < 1.05 * P0stem(P) else S * 1.25 + P.cn * 0.30
    g.add(LC.hook_tail(P, xr + S / 2, 2, d - P.os, reach, pl, rb))
    return xr


@glyph("eng", 0x014B)
def eng(g, P):
    xr = eng_body(g, P)
    LC.anchors_lc(g, (xr + P.stem) / 2, P=P)
    g.space(P.sb, P.sb)


@glyph("Eng", 0x014A)
def Eng(g, P):
    Q = P.copy()
    Q.xh = P.cap
    Q.os = P.osC
    Q.lc_stem = P.stem
    Q.stem = P.stemC
    Q.hair = P.hairC
    Q.cn = P.cn * 1.30
    Q.hdx = P.sfxC
    xr = eng_body(g, Q)
    UC.anchors_uc(g, P, (xr + Q.stem) / 2)
    g.space(P.sbC, P.sbC)


@glyph("kgreenlandic", 0x0138)
def kgreenlandic(g, P):
    LC.k(g, P, short=True)


@glyph("napostrophe", 0x0149)
def napostrophe(g, P):
    q = qright(P)
    b = contours_bounds(q)
    g.add(shift(q, -b[0]))
    n, _ = borrow("n", P)
    g.add(shift(n, (b[2] - b[0]) + P.sb * 1.4 + P.sfx))
    g.space(P.sb * 1.4, P.sb)


# ------------------------------------------------------------- Ĳ ĳ

@glyph("IJ", 0x0132)
def IJ(g, P):
    I, _ = borrow("I", P)
    J, _ = borrow("J", P)
    S = P.stemC
    g.add(I)
    g.add(shift(J, S + P.sfxC * 2 + P.sb * 0.8 - S * 0.9))
    g.space(P.sbC, P.sbC)


@glyph("ij", 0x0133)
def ij(g, P):
    i, _ = borrow("i", P)
    j, _ = borrow("j", P)
    S = P.stem
    g.add(i)
    g.add(shift(j, S + P.sfx * 2 + P.sb * 0.9))
    g.space(P.sb, P.sb)


# ------------------------------------------------------------- Ə ə ƒ ſ

@glyph("schwa", 0x0259)
def schwa(g, P):
    E, _ = borrow("e", P)
    b = contours_bounds(E)
    g.add(transform_contours(E, -1, 0, 0, -1, b[0] + b[2], P.xh))
    LC.anchors_lc(g, (b[0] + b[2]) / 2, P=P)
    g.space(P.rnd * 0.72, P.rnd)


@glyph("Schwa", 0x018F)
def Schwa(g, P):
    Q = P.copy()
    Q.xh = P.cap
    Q.os = P.osC
    Q.stem = P.stemC
    Q.hair = P.hairC
    Q.curve = P.curveC
    Q.cn = P.cn * 1.30
    E, _ = borrow("e", Q)
    b = contours_bounds(E)
    g.add(transform_contours(E, -1, 0, 0, -1, b[0] + b[2], P.cap))
    UC.anchors_uc(g, P, (b[0] + b[2]) / 2)
    g.space(P.sbC * 0.95, P.sbC * 1.15)


@glyph("florin", 0x0192)
def florin(g, P):
    S, H, xh, asc, d = P.stem, P.hair, P.xh, P.asc, P.desc
    pl = Pen(S / 2, H / 2)
    W = P.cn * 0.95 + S
    rb = LC.rbf(P, 0.5)
    p = Path(rb * 0.9, d + rb * 0.9, d=-30, w=0.75)
    p.c(W * 0.30, d - P.os + pl.hv, d=0, w=1.0)
    p.c(W * 0.46, d * 0.40, d=78, w=1.0)
    p.c(W * 0.56, asc * 0.62, d=82, w=1.0)
    p.c(W * 0.72, asc + P.os - pl.hv, d=0, w=1.0)
    p.c(W - rb * 0.9, asc - rb * 0.9, d=-30, w=0.75)
    g.add(stk(p, pl))
    g.add(LC.drop(P, rb, d - P.os + rb * 1.05, rb))
    g.add(LC.drop(P, W - rb, asc + P.os - rb * 1.05, rb))
    t = H * 1.12
    g.add(rect(W * 0.20, xh - t, W * 0.86, xh))
    g.space(P.sb * 0.6, P.sb * 0.6)


@glyph("longs", 0x017F)
def longs(g, P):
    LC.f(g, P, bar=False)
