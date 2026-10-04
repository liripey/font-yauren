"""Diacríticos: marcas combinantes (minúsculas e .case), acentos isolados."""
import math

from ..glyph import contours_bounds, transform_contours
from ..parts import ellipse, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import glyph
from .punct import comma_shape, rdot


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def MC(P):
    """Centro horizontal das marcas combinantes (à esquerda da origem)."""
    return -round((P.cn * 1.10 + 2 * P.curve) / 2 + P.sb * 1.15)


class M:
    def __init__(self, P, case):
        self.P = P
        self.case = case
        self.S, self.H = P.stem, P.hair
        self.base = P.cap if case else P.xh
        self.y0 = self.base + (64 if case else 92)
        self.hu = 126 if case else 165
        self.cx = MC(P)


# ------------------------------------------------------------- formas

def f_acute(m, flip=False, k=1.0, dx=0.0):
    S, H, hu = m.S, m.H, m.hu * k
    w = hu * (0.98 if m.case else 0.72)
    x0, x1 = m.cx - w * 0.42 + dx, m.cx + w * 0.42 + dx
    if flip:
        x0, x1 = m.cx + w * 0.42 + dx, m.cx - w * 0.42 + dx
    pen = Pen(S * 0.38 + 4, H * 0.45)
    p = Path(x0, m.y0, w=0.32).l(x1, m.y0 + hu - S * 0.25, w=1.0)
    return stk(p, pen, cap1="round"), m.y0 + hu


def f_circumflex(m, invert=False):
    S, H = m.S, m.H
    h = m.hu * (0.70 if m.case else 0.78)
    w = m.hu * (1.70 if m.case else 1.52)
    pen = Pen(S * 0.36, H * 0.55)
    y0, y1 = m.y0, m.y0 + h
    if invert:
        y0, y1 = y1, y0
    p = Path(m.cx - w / 2, y0).l(m.cx, y1).l(m.cx + w / 2, y0)
    sh = stk(p, pen)
    # corta pontas abaixo/acima da faixa
    from ..glyph import clip
    sh = clip(sh, rect(-3000, m.y0 - 400, 3000, m.y0), rect(-3000, m.y0 + h, 3000, m.y0 + h + 400))
    return sh, m.y0 + h


def f_tilde(m):
    S, H = m.S, m.H
    h = m.hu * (0.60 if m.case else 0.58)
    w = m.hu * (1.78 if m.case else 1.62)
    pen = Pen(S * 0.37, H * 0.55)
    cx, y0 = m.cx, m.y0
    p = Path(cx - w / 2, y0 + h * 0.10, d=64, w=0.62)
    p.c(cx - w * 0.21, y0 + h * 0.90, d=0, w=1.0)
    p.c(cx + w * 0.21, y0 + h * 0.12, d=0, w=1.0)
    p.c(cx + w / 2, y0 + h * 0.92, d=64, w=0.62)
    sh = stk(p, pen)
    b = contours_bounds(sh)
    sh = transform_contours(sh, dy=y0 - b[1])
    b = contours_bounds(sh)
    return sh, b[3]


def f_macron(m):
    w = m.hu * (1.65 if m.case else 1.48)
    t = m.H * 1.28
    y = m.y0 + (8 if m.case else 18)
    return rect(m.cx - w / 2, y, m.cx + w / 2, y + t), y + t


def f_breve(m):
    S, H = m.S, m.H
    h = m.hu * (0.52 if m.case else 0.62)
    w = m.hu * (1.50 if m.case else 1.36)
    pen = Pen(S * 0.36, H * 0.55)
    p = Path(m.cx - w / 2, m.y0 + h, d=270, w=0.4)
    p.c(m.cx, m.y0 + pen.hv, d=0, w=1.0)
    p.c(m.cx + w / 2, m.y0 + h, d=90, w=0.4)
    return stk(p, pen), m.y0 + h


def f_dot(m, dx=0.0):
    r = rdot(m.P) * 0.92
    return ellipse(m.cx + dx, m.y0 + r, r, r * 1.02), m.y0 + 2 * r


def f_dieresis(m):
    r = rdot(m.P) * 0.92
    d = r * 1.42 + (26 if not m.case else 34)
    a, _ = f_dot(m, -d)
    b, top = f_dot(m, d)
    return a + b, top


def f_ring(m):
    H, S = m.H, m.S
    pen = Pen(S * 0.25, H * 0.52, m.P.ang)
    rr = 2 * pen.A + (24 if m.case else 30)
    rry = rr * (0.92 if m.case else 1.0)
    cy = m.y0 + rry - (4 if m.case else 0)
    p = Path(m.cx + rr - pen.hh, cy, d=90).c(m.cx, cy + rry - pen.hv, d=180)
    p.c(m.cx - rr + pen.hh, cy, d=270).c(m.cx, cy - rry + pen.hv, d=0).close("c")
    return stk(p, pen), cy + rry


def f_hungarumlaut(m):
    d = m.hu * (0.36 if m.case else 0.30)
    a, top = f_acute(m, k=0.92, dx=-d)
    b, _ = f_acute(m, k=0.92, dx=d)
    return a + b, top


def f_dotbelow(m):
    r = rdot(m.P) * 0.92
    cy = -86 - r
    return ellipse(m.cx, cy, r, r * 1.02), cy - r


def f_commabelow(m):
    sc = 0.78 * (1 - 0.32 * m.P.wf)
    c = transform_contours(comma_shape(m.P), sc, 0, 0, sc, 0, 0)
    b = contours_bounds(c)
    return transform_contours(c, dx=m.cx - (b[0] + b[2]) / 2 + 6, dy=-62 - b[3]), None


def f_commaabove(m):
    sc = 0.78 * (1 - 0.32 * m.P.wf) * (0.85 if m.case else 1.0)
    c = transform_contours(comma_shape(m.P), -sc, 0, 0, -sc, 0, 0)
    b = contours_bounds(c)
    return transform_contours(c, dx=m.cx - (b[0] + b[2]) / 2, dy=m.y0 - b[1]), None


def f_cedilla(m):
    S, H = m.S, m.H
    cx = m.cx
    pen = Pen(S * 0.30 + 2, H * 0.5)
    sh = rect(cx - S * 0.22, -56, cx + S * 0.18, 16)
    p = Path(cx - S * 0.22, -50, d=8, w=0.55)
    p.c(cx + 60 + S * 0.25, -120, d=270, w=1.0)
    p.c(cx - 56, -206, d=192, w=0.3)
    return sh + stk(p, pen), None


def f_ogonek(m):
    S, H = m.S, m.H
    cx = m.cx
    pen = Pen(S * 0.40, H * 0.5)
    p = Path(cx + 12, 6, d=236, w=0.80)
    p.c(cx - 52, -112, d=270, w=1.0)
    p.c(cx + 36, -212, d=8, w=0.26)
    return stk(p, pen), None


def f_caronalt(m):
    """Caron em forma de apóstrofo (ď ľ ť Ľ)."""
    sc = 0.86 * (1 - 0.25 * m.P.wf)
    c = transform_contours(comma_shape(m.P), sc, 0, 0, sc, 0, 0)
    b = contours_bounds(c)
    return transform_contours(c, dx=m.cx - b[0] + 22 + m.S * 0.1, dy=(m.P.asc + 8) - b[3]), None


TOP_MARKS = {
    "gravecomb": (0x0300, lambda m: f_acute(m, flip=True)),
    "acutecomb": (0x0301, lambda m: f_acute(m)),
    "circumflexcomb": (0x0302, lambda m: f_circumflex(m)),
    "tildecomb": (0x0303, f_tilde),
    "macroncomb": (0x0304, f_macron),
    "brevecomb": (0x0306, f_breve),
    "dotaccentcomb": (0x0307, lambda m: f_dot(m)),
    "dieresiscomb": (0x0308, f_dieresis),
    "ringcomb": (0x030A, f_ring),
    "hungarumlautcomb": (0x030B, f_hungarumlaut),
    "caroncomb": (0x030C, lambda m: f_circumflex(m, invert=True)),
    "commaturnedabovecomb": (0x0312, f_commaabove),
}
BOTTOM_MARKS = {
    "dotbelowcomb": (0x0323, f_dotbelow),
    "commaaccentcomb": (0x0326, f_commabelow),
    "cedillacomb": (0x0327, f_cedilla),
    "ogonekcomb": (0x0328, f_ogonek),
}


def _make_mark(fn, case, kind):
    def g_fn(g, P):
        m = M(P, case)
        sh, top = fn(m)
        g.add(sh)
        if kind == "top":
            g.anchor("_top", m.cx, m.base)
            b = contours_bounds(sh)
            g.anchor("top", m.cx, (b[3] if top is None else top) - (m.y0 - m.base) + 30)
        elif kind == "bottom":
            g.anchor("_bottom", m.cx, 0)
            g.anchor("bottom", m.cx, -190)
        g.space(width=0)
    return g_fn


for name, (uni, fn) in TOP_MARKS.items():
    glyph(name, uni)(_make_mark(fn, False, "top"))
    glyph(name + ".case")(_make_mark(fn, True, "top"))
for name, (uni, fn) in BOTTOM_MARKS.items():
    kind = {"cedillacomb": "cedilla", "ogonekcomb": "ogonek"}.get(name, "bottom")

    def _mk(fn=fn, kind=kind):
        def g_fn(g, P):
            m = M(P, False)
            sh, _ = fn(m)
            g.add(sh)
            g.anchor("_" + kind, m.cx, 0)
            g.anchor("_bottom", m.cx, 0)
            g.space(width=0)
        return g_fn
    glyph(name, uni)(_mk())


@glyph("caroncomb.alt")
def caroncomb_alt(g, P):
    m = M(P, False)
    sh, _ = f_caronalt(m)
    g.add(sh)
    g.anchor("_topright", m.cx, P.asc)
    g.space(width=0)


# ------------------------------------------------------------- acentos isolados

SPACING = {
    "grave": (0x0060, "gravecomb"), "acute": (0x00B4, "acutecomb"),
    "circumflex": (0x02C6, "circumflexcomb"), "tilde": (0x02DC, "tildecomb"),
    "macron": (0x00AF, "macroncomb"), "breve": (0x02D8, "brevecomb"),
    "dotaccent": (0x02D9, "dotaccentcomb"), "dieresis": (0x00A8, "dieresiscomb"),
    "ring": (0x02DA, "ringcomb"), "hungarumlaut": (0x02DD, "hungarumlautcomb"),
    "caron": (0x02C7, "caroncomb"), "cedilla": (0x00B8, "cedillacomb"),
    "ogonek": (0x02DB, "ogonekcomb"),
}


def _make_spacing(src):
    def g_fn(g, P):
        fn = TOP_MARKS.get(src, BOTTOM_MARKS.get(src))[1]
        m = M(P, False)
        sh, _ = fn(m)
        g.add(sh)
        g.space(P.sb * 1.6, P.sb * 1.6)
    return g_fn


for name, (uni, src) in SPACING.items():
    glyph(name, uni)(_make_spacing(src))


# ------------------------------------------------------------- marcas inferiores extras

def _below(fn_top, case=False, gap=70):
    """Converte uma forma de marca superior em inferior (topo em -gap)."""
    def fn(m):
        sh, _ = fn_top(m)
        b = contours_bounds(sh)
        return transform_contours(sh, dy=-gap - b[3]), None
    return fn


EXTRA_BOTTOM = {
    "dieresisbelowcomb": (0x0324, _below(f_dieresis)),
    "ringbelowcomb": (0x0325, _below(f_ring)),
    "circumflexbelowcomb": (0x032D, _below(lambda m: f_circumflex(m))),
    "brevebelowcomb": (0x032E, _below(f_breve)),
    "brevinvertedbelowcomb": (0x032F, _below(
        lambda m: (transform_contours(f_breve(m)[0], 1, 0, 0, -1, 0, 2 * m.y0 + m.hu * 0.62), None))),
    "tildebelowcomb": (0x0330, _below(f_tilde)),
    "macronbelowcomb": (0x0331, _below(f_macron)),
    "minusbelowcomb": (0x0320, _below(lambda m: (rect(m.cx - m.hu * 0.45, m.y0, m.cx + m.hu * 0.45,
                                                       m.y0 + m.H * 1.28), None))),
}


def _mk_bottom(fn):
    def g_fn(g, P):
        m = M(P, False)
        sh, _ = fn(m)
        g.add(sh)
        g.anchor("_bottom", m.cx, 0)
        g.space(width=0)
    return g_fn


for _name, (_uni, _fn) in EXTRA_BOTTOM.items():
    glyph(_name, _uni)(_mk_bottom(_fn))


# ------------------------------------------------------------- letras modificadoras

@glyph("apostrophemod", 0x02BC)
def apostrophemod(g, P):
    from .punct import qright
    g.add(qright(P))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("commaturnedmod", 0x02BB)
def commaturnedmod(g, P):
    from .punct import qleft
    g.add(qleft(P))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("glottalstop", 0x0294)
def glottalstop(g, P):
    from .punct import question_shapes
    S, H, cap = P.stem, P.hair, P.cap
    pl = Pen(S / 2, H / 2)
    W = P.cn * 0.80 + S * 1.1
    p = Path(S * 0.45, cap * 0.78, d=90, w=0.75)
    p.c(W * 0.50, cap + P.os - pl.hv, d=0, w=1.0)
    p.c(W - pl.hh, cap * 0.74, d=270, w=1.0)
    p.c(W * 0.52, cap * 0.45, d=225, w=0.95)
    p.c(W * 0.46, cap * 0.28, d=270, w=1.0)
    p.l(W * 0.46, 0)
    g.add(stk(p, pl))
    from ..parts import foot_serif
    g.add(foot_serif(P, W * 0.46 - S / 2, W * 0.46 + S / 2, 0))
    g.space(P.sb, P.sb)
