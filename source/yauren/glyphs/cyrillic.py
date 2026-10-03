"""Cirílico (russo, ucraniano, bielorrusso, búlgaro, sérvio, macedônio).

As maiúsculas são funções paramétricas; boa parte das minúsculas cirílicas
segue a tradição de "versaletes" (forma de maiúscula na altura-x), obtidas
chamando a mesma função com parâmetros de minúscula (smallcap)."""
from ..glyph import Glyph, clip, contours_bounds, transform_contours
from ..parts import beak, ellipse, foot_serif, halfplane, head_serif, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import ALIASES, GLYPHS, borrow, composite, glyph
from . import lower as LC
from . import upper as UC


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def shift(c, dx=0, dy=0):
    return transform_contours(c, dx=dx, dy=dy)


def mirror(c, W):
    return transform_contours(c, -1, 0, 0, 1, W, 0)


def smallcap(P, k=0.84):
    """Parâmetros para desenhar formas de maiúscula na altura-x."""
    Q = P.copy()
    Q.cap = P.xh
    Q.osC = P.os
    Q.stemC = P.stem
    Q.hairC = P.hair
    Q.curveC = P.curve
    Q.sfxC = P.sfx
    Q.sftC = P.sft
    Q.sfbC = P.sfb
    Q.cn = P.cn * k
    Q.sbC = P.sb
    Q.rndC = P.rnd
    Q.small = True
    return Q


def is_small(P):
    return getattr(P, "small", False)


def tail_depth(P):
    return (P.desc * 0.62) if is_small(P) else (-P.cap * 0.17)


def desc_tab(g, P, x0, x1):
    """Rabicho descendente (Д Ц Щ Џ)."""
    y = tail_depth(P)
    g.add(quad((x0, 1), (x1, 1), (x1 - (x1 - x0) * 0.12, y), (x0 + (x1 - x0) * 0.08, y)))


# ------------------------------------------------------------- cópias

def _copy(src, cap_src=None):
    def fn(g, P):
        GLYPHS[src][1](g, P)
    return fn


COPIES = [
    ("uni0410", 0x0410, "A"), ("uni0412", 0x0412, "B"), ("uni0415", 0x0415, "E"),
    ("uni041A", 0x041A, "K"), ("uni041C", 0x041C, "M"), ("uni041D", 0x041D, "H"),
    ("uni041E", 0x041E, "O"), ("uni0420", 0x0420, "P"), ("uni0421", 0x0421, "C"),
    ("uni0422", 0x0422, "T"), ("uni0425", 0x0425, "X"), ("uni0405", 0x0405, "S"),
    ("uni0406", 0x0406, "I"), ("uni0408", 0x0408, "J"),
    ("uni0430", 0x0430, "a"), ("uni0435", 0x0435, "e"), ("uni043E", 0x043E, "o"),
    ("uni0440", 0x0440, "p"), ("uni0441", 0x0441, "c"), ("uni0443", 0x0443, "y"),
    ("uni0445", 0x0445, "x"), ("uni0455", 0x0455, "s"), ("uni0456", 0x0456, "i"),
    ("uni0458", 0x0458, "j"), ("uni043A", 0x043A, "kgreenlandic"),
    ("uni0413", 0x0413, "Gamma"), ("uni041F", 0x041F, "Pi"), ("uni0424", 0x0424, "Phi"),
]
for _n, _u, _s in COPIES:
    glyph(_n, _u)(_copy(_s))
    ALIASES[_n] = _s


def both(upper_name, upper_uni, lower_name, lower_uni, k=0.84):
    """Registra maiúscula e minúscula (versalete) a partir da mesma função."""
    def deco(fn):
        glyph(upper_name, upper_uni)(fn)
        if lower_uni is None:
            return fn

        def low(g, P):
            fn(g, smallcap(P, k))
        glyph(lower_name, lower_uni)(low)
        return fn
    return deco


# ------------------------------------------------------------- formas

@both("uni0411", 0x0411, "uni0431.sc", None)
def Be(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    UC.serifs(g, P, 0, S, tr=0, br=0)
    UC.e_arms(g, P, S, S + cn * 0.98, None, None)
    g.add(UC.p_bowl(P, S, S + cn * 0.72 + P.curveC, 0, top=cap * 0.56))
    UC.anchors_uc(g, P, (S + cn) / 2)
    g.space(P.sbC, P.rndC * 0.85)


@both("uni0414", 0x0414, "uni0434", 0x0434)
def De(g, P):
    S, H, cn, cap = P.stemC, P.hairC, P.cn, P.cap
    W = cn * 1.30 + S * 1.6
    bt = UC.arm_t(P, 1.12)
    tt = UC.arm_t(P, 1.0)
    xr = W - S * 0.35
    g.add(rect(xr - S, 0, xr, cap))
    g.add(rect(W * 0.20, cap - tt, xr, cap))
    pl = Pen(S * 0.42, H / 2)
    p = Path(W * 0.20 + S * 0.42, cap - tt * 0.5, d=262, w=1.0)
    p.c(W * 0.12, bt + cap * 0.10, d=240, w=0.9)
    p.c(S * 0.2, bt * 0.6, d=225, w=0.7)
    g.add(stk(p, pl))
    g.add(rect(0, 0, W, bt))
    g.add(foot_serif(P, W * 0.20, W * 0.20 + S * 0.84, cap, el=P.sfxC, er=0, caps=True, flip=True))
    g.add(foot_serif(P, xr - S, xr, cap, el=0, er=P.sfxC * 0.9, caps=True, flip=True))
    desc_tab(g, P, 0, S * 0.42)
    desc_tab(g, P, W - S * 0.42, W)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.6, P.sbC * 0.6)


def zhe_arm(P, cx, W, side):
    """Braço + perna do Ж (lado direito; espelha para o esquerdo)."""
    S, H, cap = P.stemC, P.hairC, P.cap
    thin, thick = H * 1.35, S * 1.0
    yj = cap * 0.48
    x0 = cx + S * 0.5 - 2
    ax = cx + W
    arm = quad((x0, yj), (x0, yj + thin * 1.4), (ax, cap), (ax - thin * 1.15, cap))
    sa = (ax - thin * 1.15 - x0) / (cap - yj)
    out = [arm, foot_serif(P, ax - thin * 1.15, ax, cap, el=P.sfxC * 0.5, er=P.sfxC * 0.85,
                           flip=True, sl=-sa, sr=-sa, caps=True)]
    lx = cx + W + S * 0.12
    leg = quad((x0 - 4, yj + 8), (x0 + thick * 0.6, yj + 8), (lx, 0), (lx - thick, 0))
    out.append(clip(leg, rect(-3000, yj + 8, 5000, 3000)))
    sl = (lx - thick - (x0 - 4)) / (yj + 8)
    out.append(foot_serif(P, lx - thick, lx, 0, el=P.sfxC * 0.5, er=P.sfxC * 0.9, sl=-sl, sr=-sl,
                          caps=True))
    res = []
    for sh in out:
        res += sh
    if side == "left":
        res = transform_contours(res, -1, 0, 0, 1, 2 * cx, 0)
    return res


@both("uni0416", 0x0416, "uni0436", 0x0436)
def Zhe(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    Wa = cn * 0.88 + S * 0.55
    cx = Wa + S * 0.6
    g.add(rect(cx - S / 2, 0, cx + S / 2, cap))
    UC.serifs(g, P, cx - S / 2, cx + S / 2)
    g.add(zhe_arm(P, cx, Wa, "right"))
    g.add(zhe_arm(P, cx, Wa, "left"))
    UC.anchors_uc(g, P, cx)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@both("uni0417", 0x0417, "uni0437", 0x0437)
def Ze(g, P):
    S, H, cap = P.stemC, P.hairC, P.cap
    pen = Pen(P.curveC / 2, H / 2, P.ang)
    W = P.cn * 0.95 + P.curveC * 1.2
    top, bot = cap + P.osC, -P.osC
    we = 0.62
    p = Path(pen.hh * we, cap * 0.70, d=90, w=we)
    p.c(W * 0.46, top - pen.hv, d=0, w=1.0)
    p.c(W * 0.92 - pen.hh * 0.92, cap * 0.76, d=270, w=0.92)
    p.c(W * 0.40, cap * 0.535, d=180, w=0.72)
    g.add(stk(p, pen))
    q = Path(W * 0.40, cap * 0.535, d=0, w=0.72)
    q.c(W - pen.hh, cap * 0.27, d=270, w=1.0)
    q.c(W * 0.48, bot + pen.hv, d=180, w=1.0)
    q.c(pen.hh * we, cap * 0.26, d=90, w=we)
    g.add(stk(q, pen))
    hs = cap * 0.06 * (1 - 0.55 * P.wf)
    ts = pen.hh * we * 2
    g.add(quad((0, cap * 0.70), (ts, cap * 0.70), (ts * 0.7, cap * 0.70 - hs), (0, cap * 0.70 - hs)))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.rndC * 0.75, P.rndC * 0.9)


def i_shape(g, P):
    S, H, cn, cap = P.stemC, P.hairC, P.cn, P.cap
    W = cn * 1.30 + S * 2
    thin = H * 1.4
    g.add(rect(0, 0, S, cap))
    g.add(rect(W - S, 0, W, cap))
    d = quad((S - thin, 0), (S + 2, 0), (W - S + thin, cap), (W - S - 2, cap))
    g.add(clip(d, rect(-100, cap, 3000, cap + 300), rect(-100, -300, 3000, 0)))
    UC.serifs(g, P, 0, S)
    UC.serifs(g, P, W - S, W)
    UC.anchors_uc(g, P, W / 2)
    return W


@both("uni0418", 0x0418, "uni0438", 0x0438)
def I_(g, P):
    i_shape(g, P)
    g.space(P.sbC, P.sbC)


@both("uni041B", 0x041B, "uni043B", 0x043B)
def El(g, P):
    S, H, cn, cap = P.stemC, P.hairC, P.cn, P.cap
    W = cn * 1.24 + S * 1.7
    tt = UC.arm_t(P, 1.0)
    xr = W - S
    g.add(rect(xr, 0, W, cap))
    UC.serifs(g, P, xr, W, tl=0)
    xl = W * 0.24
    g.add(rect(xl, cap - tt, xr + 2, cap))
    g.add(foot_serif(P, xl, xl + S * 0.85, cap, el=P.sfxC, er=0, caps=True, flip=True))
    pl = Pen(S * 0.44, H / 2)
    rb = (S * 0.42 + 5) * (1 - 0.15 * P.wf)
    p = Path(xl + S * 0.44, cap - tt * 0.6, d=268, w=1.0)
    p.c(xl * 0.62, cap * 0.22, d=245, w=0.9)
    p.c(rb * 1.4, rb * 0.9, d=210, w=0.6)
    g.add(stk(p, pl))
    g.add(ellipse(rb * 1.05, rb * 1.0, rb, rb))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.4, P.sbC)


@both("uni0423", 0x0423, "uni0443.sc", None)
def U_(g, P):
    S, H, cn, cap = P.stemC, P.hairC, P.cn, P.cap
    W = cn * 1.38 + S * 1.5
    thick, thin = S * 1.04, H * 1.3
    yj = cap * 0.30
    xj = W * 0.50
    a1 = quad((0, cap), (thick, cap), (xj + thick * 0.5, yj - 30), (xj - thick * 0.5, yj - 30))
    g.add(clip(a1, halfplane((0, cap), (xj - thick * 0.5, yj - 30), "right"),
               rect(-2000, -2000, 4000, yj - 5)))
    sl = (xj - thick * 0.5) / (cap - yj + 30)
    g.add(foot_serif(P, 0, thick, cap, el=P.sfxC, er=P.sfxC * 0.55, flip=True, sl=sl, sr=sl, caps=True))
    pt = Pen(thin * 0.62, H / 2)
    rb = (S * 0.48 + 5) * (1 - 0.15 * P.wf)
    dx = (W - thin / 2 - W * 0.30) / (cap - cap * 0.18)
    p = Path(W - thin / 2, cap + 20)
    p.l(W * 0.30 + dx * 0, cap * 0.18)
    p.c(W * 0.12, -P.osC + H * 0.55, d=200, w=1.0, a=S * 0.38, b=H * 0.55)
    p.c(rb * 0.9, rb * 0.6, d=160, w=1.0, a=S * 0.30, b=H * 0.5)
    g.add(clip(stk(p, pt), rect(-2000, cap, 4000, cap + 400)))
    g.add(ellipse(rb * 0.9, rb * 1.0, rb, rb))
    g.add(foot_serif(P, W - thin, W, cap, el=P.sfxC * 0.55, er=P.sfxC, flip=True,
                     sl=-dx, sr=-dx, caps=True))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.3, P.sbC * 0.3)


@both("uni0426", 0x0426, "uni0446", 0x0446)
def Tse(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    W = cn * 1.30 + S * 2
    bt = UC.arm_t(P, 1.12)
    g.add(rect(0, 0, S, cap))
    g.add(rect(W - S, 0, W, cap))
    UC.serifs(g, P, 0, S, bottom=False)
    UC.serifs(g, P, W - S, W, bottom=False)
    g.add(rect(0, 0, W + S * 0.45, bt))
    desc_tab(g, P, W + S * 0.45 - S * 0.45, W + S * 0.45)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC * 0.4)


@both("uni0427", 0x0427, "uni0447", 0x0447)
def Che(g, P):
    S, H, cn, cap = P.stemC, P.hairC, P.cn, P.cap
    W = cn * 1.15 + S * 2
    pl = Pen(S / 2, H / 2)
    g.add(rect(W - S, 0, W, cap))
    UC.serifs(g, P, W - S, W)
    p = Path(S / 2, cap - 20, d=270)
    p.l(S / 2, cap * 0.62)
    p.c(W * 0.45, cap * 0.38 + pl.hv, d=0, w=1.0)
    p.c(W - S * 0.7, cap * 0.44, d=40, w=0.4)
    g.add(stk(p, pl))
    UC.serifs(g, P, 0, S, bottom=False)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC)


def sha(g, P, tail=False):
    S, cn, cap = P.stemC, P.cn, P.cap
    c2 = cn * 0.86
    W = 3 * S + 2 * c2
    bt = UC.arm_t(P, 1.12)
    for x in (0, S + c2, 2 * S + 2 * c2):
        g.add(rect(x, 0, x + S, cap))
        UC.serifs(g, P, x, x + S, bottom=False)
    Wb = W + (S * 0.45 if tail else 0)
    g.add(rect(0, 0, Wb, bt))
    if tail:
        desc_tab(g, P, Wb - S * 0.45, Wb)
    UC.anchors_uc(g, P, W / 2)
    return W


@both("uni0428", 0x0428, "uni0448", 0x0448)
def Sha(g, P):
    sha(g, P)
    g.space(P.sbC, P.sbC)


@both("uni0429", 0x0429, "uni0449", 0x0449)
def Shcha(g, P):
    sha(g, P, tail=True)
    g.space(P.sbC, P.sbC * 0.4)


def soft(g, P, x0=0):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(x0, 0, x0 + S, cap))
    UC.serifs(g, P, x0, x0 + S, br=0)
    g.add(UC.p_bowl(P, x0 + S, x0 + S + cn * 0.70 + P.curveC, 0, top=cap * 0.56))
    return x0 + S + cn * 0.70 + P.curveC


@both("uni042C", 0x042C, "uni044C", 0x044C)
def Soft(g, P):
    W = soft(g, P)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.rndC * 0.85)


@both("uni042A", 0x042A, "uni044A", 0x044A)
def Hard(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    x0 = cn * 0.36
    W = soft(g, P, x0)
    tt = UC.arm_t(P, 1.0)
    g.add(rect(0, cap - tt, x0 + 2, cap))
    g.add(beak(P, 0, cap, tt, cap * 0.13, S * 0.40, side="left"))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.45, P.rndC * 0.85)


@both("uni042B", 0x042B, "uni044B", 0x044B)
def Yeru(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    W = soft(g, P)
    x = W + P.sbC * 0.9 + P.sfxC * 2 + S * 0.2
    g.add(rect(x, 0, x + S, cap))
    UC.serifs(g, P, x, x + S)
    UC.anchors_uc(g, P, (x + S) / 2)
    g.space(P.sbC, P.sbC)


@both("uni042D", 0x042D, "uni044D", 0x044D)
def Ereversed(g, P):
    c, t = borrow("C", P)
    b = contours_bounds(c)
    W = b[2] + b[0]
    g.add(mirror(c, W))
    t_ = UC.arm_t(P, 1.0)
    g.add(rect(W * 0.38, P.cap * 0.5 - t_ / 2, W - P.curveC * 0.5, P.cap * 0.5 + t_ / 2))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.rndC * 0.6, P.rndC)


@both("uni042E", 0x042E, "uni044E", 0x044E)
def Yu(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    UC.serifs(g, P, 0, S)
    W = cn * 1.10 + 2 * P.curveC
    x0 = S + cn * 0.30
    g.add(UC.o_ring(P, x0, W))
    t_ = UC.arm_t(P, 1.0)
    g.add(rect(S - 1, cap * 0.5 - t_ / 2, x0 + P.curveC * 0.5, cap * 0.5 + t_ / 2))
    UC.anchors_uc(g, P, x0 / 2 + W / 2)
    g.space(P.sbC, P.rndC)


@both("uni042F", 0x042F, "uni044F", 0x044F)
def Ya(g, P):
    c, t = borrow("R", P)
    b = contours_bounds(c)
    W = b[2] + b[0]
    g.add(mirror(c, W))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC * 0.4, P.sbC)


@both("uni0404", 0x0404, "uni0454", 0x0454)
def Eukr(g, P):
    c, t = borrow("C", P)
    b = contours_bounds(c)
    g.add(c)
    t_ = UC.arm_t(P, 1.0)
    W = b[2] - b[0]
    g.add(rect(P.curveC * 0.5, P.cap * 0.5 - t_ / 2, W * 0.62, P.cap * 0.5 + t_ / 2))
    UC.anchors_uc(g, P, W / 2)
    g.space(P.rndC, P.rndC * 0.6)


@both("uni040F", 0x040F, "uni045F", 0x045F)
def Dzhe(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    W = cn * 1.30 + S * 2
    bt = UC.arm_t(P, 1.12)
    g.add(rect(0, 0, S, cap))
    g.add(rect(W - S, 0, W, cap))
    UC.serifs(g, P, 0, S, bottom=False)
    UC.serifs(g, P, W - S, W, bottom=False)
    g.add(rect(0, 0, W, bt))
    desc_tab(g, P, W / 2 - S * 0.25, W / 2 + S * 0.25)
    UC.anchors_uc(g, P, W / 2)
    g.space(P.sbC, P.sbC)


@both("uni0490", 0x0490, "uni0491", 0x0491)
def Gheup(g, P):
    S, cn, cap = P.stemC, P.cn, P.cap
    g.add(rect(0, 0, S, cap))
    UC.serifs(g, P, 0, S, tr=0)
    tt = UC.arm_t(P, 1.0)
    xr = S + cn * 0.92
    g.add(rect(S - 1, cap - tt, xr, cap))
    up = cap * 0.17 if not is_small(P) else P.cap * 0.22
    g.add(quad((xr - S * 0.62, cap - tt), (xr, cap - tt), (xr, cap + up), (xr - S * 0.45, cap + up)))
    UC.anchors_uc(g, P, S / 2 + 20)
    g.space(P.sbC, P.sbC * 0.5)


def lje(g, P, base):
    """Љ Њ: ligadura com o bojo do Ь."""
    S, cn, cap = P.stemC, P.cn, P.cap
    c, t = borrow(base, P)
    b = contours_bounds(c)
    g.add(c)
    # haste direita da base: borda direita = extremo - extensão da serifa
    x0 = b[2] - P.sfxC - S
    g.add(rect(x0, 0, x0 + S, cap))
    g.add(UC.p_bowl(P, x0 + S, x0 + S + cn * 0.66 + P.curveC, 0, top=cap * 0.56))


@glyph("uni0409", 0x0409)
def Lje(g, P):
    lje(g, P, "uni041B")
    g.space(P.sbC * 0.4, P.rndC * 0.85)


@glyph("uni0459", 0x0459)
def lje_lc(g, P):
    lje(g, smallcap(P), "uni043B")
    g.space(P.sb * 0.4, P.rnd * 0.85)


@glyph("uni040A", 0x040A)
def Nje(g, P):
    lje(g, P, "H")
    g.space(P.sbC, P.rndC * 0.85)


@glyph("uni045A", 0x045A)
def nje_lc(g, P):
    lje(g, smallcap(P), "H")
    g.space(P.sb, P.rnd * 0.85)


def tshe(g, P, small, hook):
    """Ћ Ђ (maiúsculas) e ћ ђ (minúsculas: h com barra)."""
    S, H, cn = P.stemC if not small else P.stem, P.hair, P.cn
    if small:
        hgl, _ = borrow("h", P)
        if hook:
            hb = Glyph("t")
            xr = S + P.cn
            LC.stem(hb, P, 0, 0, P.asc)
            hb.add(LC.arch(P, S, xr, 0))
            pl = Pen(S / 2, H / 2)
            rb = LC.rbf(P, 0.54)
            p = Path(xr + S / 2, 2, d=270)
            p.l(xr + S / 2, P.desc * 0.30)
            p.c(xr - S * 0.40, P.desc - P.os + pl.hv, d=180, w=1.0)
            p.c(xr - S * 1.45 + rb * 0.6, P.desc + rb * 0.9, d=145, w=0.75)
            hb.add(stk(p, pl))
            hb.add(LC.drop(P, xr - S * 1.45 + rb * 0.85, P.desc - P.os + rb * 1.08, rb))
            hb.solve()
            hgl = hb.contours
        g.add(hgl)
        t = H * 1.15
        yb = P.xh + (P.asc - P.xh) * 0.45
        g.add(rect(-S * 0.55, yb - t / 2, S + S * 0.85, yb + t / 2))
        return
    cap = P.cap
    W = cn * 1.05 + S * 2.2
    tt = UC.arm_t(P, 1.0)
    xs = W * 0.30
    g.add(rect(xs, 0, xs + S, cap))
    g.add(rect(0, cap - tt, xs + S + cn * 0.55, cap))
    g.add(beak(P, 0, cap, tt, cap * 0.13, S * 0.40, side="left"))
    g.add(beak(P, xs + S + cn * 0.55, cap, tt, cap * 0.13, S * 0.40, side="right"))
    g.add(foot_serif(P, xs, xs + S, 0, caps=True))
    pl = Pen(S / 2, P.hairC / 2)
    xr = W - S
    p = Path(xs + S - S * 0.3, cap * 0.50, d=62, w=0.3)
    p.c(xs + S + (xr - xs - S) * 0.5, cap * 0.66 - pl.hv, d=0, w=1.0)
    p.c(xr + S / 2, cap * 0.40, d=270)
    if hook:
        rb = (S * 0.5 + 5) * (1 - 0.15 * P.wf)
        p.l(xr + S / 2, -cap * 0.05)
        p.c(xr - S * 0.3, -cap * 0.20 + pl.hv, d=180, w=1.0)
        p.c(xr - S * 1.2, -cap * 0.20 + rb * 1.6, d=130, w=0.7)
        g.add(stk(p, pl))
        g.add(ellipse(xr - S * 1.2 + rb * 0.35, -cap * 0.20 + rb * 1.15, rb, rb))
    else:
        p.l(xr + S / 2, P.sftC)
        g.add(stk(p, pl))
        g.add(foot_serif(P, xr, xr + S, 0, caps=True))


@glyph("uni040B", 0x040B)
def Tshe(g, P):
    tshe(g, P, False, False)
    g.space(P.sbC * 0.5, P.sbC)


@glyph("uni0402", 0x0402)
def Dje(g, P):
    tshe(g, P, False, True)
    g.space(P.sbC * 0.5, P.sbC)


@glyph("uni045B", 0x045B)
def tshe_lc(g, P):
    tshe(g, P, True, False)
    g.space(P.sb * 0.7, P.sb)


@glyph("uni0452", 0x0452)
def dje_lc(g, P):
    tshe(g, P, True, True)
    g.space(P.sb * 0.7, P.sb)


@glyph("uni0431", 0x0431)
def be_lc(g, P):
    """б: bojo de o com haste que sobe e se curva para a direita."""
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    pl, pc = LC.pens(P)
    W = LC.o_width(P)
    t = 0.96
    p = Path(W - pc.hh, xh / 2, d=90).c(W / 2, xh + P.os - pc.hv, d=180, t=t)
    p.c(pc.hh, xh / 2, d=270, t=t).c(W / 2, -P.os + pc.hv, d=0, t=t).close("c", t=t)
    g.add(stk(p, pc))
    q = Path(pc.hh, xh * 0.5, d=90, w=1.0)
    q.c(W * 0.30, asc * 0.84, d=60, w=0.85)
    q.c(W * 0.92, asc + P.os * 0.4, d=20, w=0.5)
    g.add(stk(q, pl))
    LC.anchors_lc(g, W / 2, top=asc, P=P)
    g.space(P.rnd, P.rnd)


@glyph("uni0432", 0x0432)
def ve_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["B"][1](g, smallcap(P, 0.86))


@glyph("uni0433", 0x0433)
def ge_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["Gamma"][1](g, smallcap(P, 0.84))


@glyph("uni043C", 0x043C)
def em_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["M"][1](g, smallcap(P, 0.82))


@glyph("uni043D", 0x043D)
def en_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["H"][1](g, smallcap(P, 0.84))


@glyph("uni043F", 0x043F)
def pe_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["Pi"][1](g, smallcap(P, 0.84))


@glyph("uni0442", 0x0442)
def te_lc(g, P):
    from ..registry import GLYPHS
    GLYPHS["T"][1](g, smallcap(P, 0.82))


@glyph("uni0444", 0x0444)
def ef_lc(g, P):
    S, H, xh = P.stem, P.hair, P.xh
    W = LC.o_width(P) * 1.22
    cx = W / 2
    pc = Pen(P.curve / 2 * 0.92, H / 2, P.ang)
    t = 0.96
    p = Path(W - pc.hh, xh / 2, d=90).c(cx, xh + P.os - pc.hv, d=180, t=t)
    p.c(pc.hh, xh / 2, d=270, t=t).c(cx, -P.os + pc.hv, d=0, t=t).close("c", t=t)
    g.add(stk(p, pc))
    g.add(rect(cx - S / 2, P.desc, cx + S / 2, P.asc - P.hdd - 8))
    g.add(head_serif(P, cx - S / 2, cx + S / 2, P.asc))
    g.add(foot_serif(P, cx - S / 2, cx + S / 2, P.desc))
    LC.anchors_lc(g, cx, top=P.asc, P=P)
    g.space(P.rnd, P.rnd)


# compostos cirílicos
for _n, _u, _b, _m in [
        ("uni0401", 0x0401, "uni0415", ["dieresiscomb.case"]),
        ("uni0451", 0x0451, "uni0435", ["dieresiscomb"]),
        ("uni0419", 0x0419, "uni0418", ["brevecomb.case"]),
        ("uni0439", 0x0439, "uni0438", ["brevecomb"]),
        ("uni0403", 0x0403, "uni0413", ["acutecomb.case"]),
        ("uni0453", 0x0453, "uni0433", ["acutecomb"]),
        ("uni040C", 0x040C, "uni041A", ["acutecomb.case"]),
        ("uni045C", 0x045C, "uni043A", ["acutecomb"]),
        ("uni040E", 0x040E, "uni0423", ["brevecomb.case"]),
        ("uni045E", 0x045E, "uni0443", ["brevecomb"]),
        ("uni0407", 0x0407, "uni0406", ["dieresiscomb.case"]),
        ("uni0457", 0x0457, "dotlessi", ["dieresiscomb"]),
        ("uni0400", 0x0400, "uni0415", ["gravecomb.case"]),
        ("uni0450", 0x0450, "uni0435", ["gravecomb"]),
        ("uni040D", 0x040D, "uni0418", ["gravecomb.case"]),
        ("uni045D", 0x045D, "uni0438", ["gravecomb"])]:
    composite(_n, _u, _b, _m)
