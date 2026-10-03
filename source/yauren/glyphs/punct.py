"""Pontuação, aspas, traços, parênteses, espaços."""
import math

from ..glyph import contours_bounds, transform_contours
from ..parts import ellipse, poly, quad, rect
from ..pen import Path, Pen, stroke
from ..registry import borrow, glyph


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def rdot(P):
    return P.stem * 0.60 + 5


def dot(cx, cy, r):
    return ellipse(cx, cy, r, r * 1.02)


def rot180(contours, cx, cy):
    return transform_contours(contours, -1, 0, 0, -1, 2 * cx, 2 * cy)


def comma_shape(P, dx=0, dy=0):
    """Vírgula com o centro do ponto em (rd + dx, rd + dy)."""
    r = rdot(P)
    out = dot(r, r, r)
    pen = Pen(r * 0.70, P.hair * 0.5)
    p = Path(2 * r - r * 0.70, r, d=270, w=1.0)
    p.c(r * 0.95, -r * 1.35, d=232, w=0.55)
    p.c(-r * 0.05, -r * 2.25, d=212, w=0.12)
    out = out + stk(p, pen)
    return transform_contours(out, dx=dx, dy=dy)


# ------------------------------------------------------------- pontos

@glyph("period", 0x002E)
def period(g, P):
    r = rdot(P)
    g.add(dot(r, r - 1, r))
    g.space(P.sb * 1.5, P.sb * 1.5)


@glyph("comma", 0x002C)
def comma(g, P):
    g.add(comma_shape(P))
    g.space(P.sb * 1.5, P.sb * 1.3)


@glyph("colon", 0x003A)
def colon(g, P):
    r = rdot(P)
    g.add(dot(r, r - 1, r))
    g.add(dot(r, P.xh - r + 2, r))
    g.space(P.sb * 1.6, P.sb * 1.6)


@glyph("semicolon", 0x003B)
def semicolon(g, P):
    r = rdot(P)
    g.add(comma_shape(P))
    g.add(dot(r, P.xh - r + 2, r))
    g.space(P.sb * 1.6, P.sb * 1.4)


@glyph("ellipsis", 0x2026)
def ellipsis(g, P):
    r = rdot(P)
    step = 2 * r + max(64, r * 1.5)
    for i in range(3):
        g.add(dot(r + i * step, r - 1, r))
    g.space(P.sb * 1.5, P.sb * 1.5)


@glyph("periodcentered", 0x00B7)
def periodcentered(g, P):
    r = rdot(P) * 0.95
    g.add(dot(r, P.xh * 0.52, r))
    g.space(P.sb * 1.5, P.sb * 1.5)


@glyph("bullet", 0x2022)
def bullet(g, P):
    r = rdot(P) * 1.45
    g.add(dot(r, P.xh * 0.50, r))
    g.space(P.sb * 1.8, P.sb * 1.8)


def exclam_shapes(P):
    r = rdot(P)
    x = r
    pen = Pen(P.stem * 0.56, P.hair * 0.5)
    p = Path(x, P.cap - P.stem * 0.45, d=270, w=1.0).l(x, P.cap * 0.30, w=0.40)
    return stk(p, pen, cap0="round") + dot(x, r - 1, r)


@glyph("exclam", 0x0021)
def exclam(g, P):
    g.add(exclam_shapes(P))
    g.space(P.sb * 1.7, P.sb * 1.7)


@glyph("exclamdown", 0x00A1)
def exclamdown(g, P):
    r = rdot(P)
    g.add(rot180(exclam_shapes(P), r, (P.xh + P.os) / 2))
    g.space(P.sb * 1.7, P.sb * 1.7)


def question_shapes(P):
    S, H, cap = P.stem, P.hair, P.cap
    pl = Pen(S / 2, H / 2)
    W = P.cn * 0.80 + S * 1.1
    rb = S * 0.52 + 5
    p = Path(rb * 1.05 + 4, cap * 0.80, d=80, w=0.72)
    p.c(W * 0.50, cap + P.os - pl.hv, d=0, w=1.0)
    p.c(W - pl.hh, cap * 0.75, d=270, w=1.0)
    p.c(W * 0.52, cap * 0.47, d=225, w=0.9)
    p.c(W * 0.44, cap * 0.30, d=270, w=0.55)
    sh = stk(p, pl)
    sh += ellipse(rb + 4, cap * 0.79, rb, rb * 1.04)
    r = rdot(P)
    sh += dot(W * 0.44, r - 1, r)
    return sh, W


@glyph("question", 0x003F)
def question(g, P):
    sh, W = question_shapes(P)
    g.add(sh)
    g.space(P.sb * 1.2, P.sb * 1.1)


@glyph("questiondown", 0x00BF)
def questiondown(g, P):
    sh, W = question_shapes(P)
    g.add(rot180(sh, W / 2, (P.xh + P.os) / 2))
    g.space(P.sb * 1.1, P.sb * 1.2)


# ------------------------------------------------------------- aspas

def quote_band(P):
    r = rdot(P) * 0.92
    top = P.cap + 12
    return r, top


def qright(P, dx=0):
    """Aspa simples direita (forma de vírgula) com ponto no alto."""
    r, top = quote_band(P)
    sc = 0.92
    c = transform_contours(comma_shape(P), sc, 0, 0, sc, 0, 0)
    # centro do ponto em (r, r) após escala; leva o topo para 'top'
    return transform_contours(c, dx=dx, dy=top - 2 * r)


def qleft(P, dx=0):
    r, top = quote_band(P)
    c = qright(P)
    b = contours_bounds(c)
    # gira 180° dentro da mesma faixa vertical
    return rot180(c, (b[0] + b[2]) / 2 + dx / 2, (b[1] + b[3]) / 2) if dx == 0 else \
        transform_contours(rot180(c, (b[0] + b[2]) / 2, (b[1] + b[3]) / 2), dx=dx)


def qgap(P):
    return rdot(P) * 2 * 0.92 + max(46, P.stem * 0.55)


@glyph("quoteright", 0x2019)
def quoteright(g, P):
    g.add(qright(P))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("quoteleft", 0x2018)
def quoteleft(g, P):
    g.add(qleft(P))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("quotedblright", 0x201D)
def quotedblright(g, P):
    g.add(qright(P))
    g.add(qright(P, dx=qgap(P)))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("quotedblleft", 0x201C)
def quotedblleft(g, P):
    g.add(qleft(P))
    g.add(qleft(P, dx=qgap(P)))
    g.space(P.sb * 1.4, P.sb * 1.4)


@glyph("quotesinglbase", 0x201A)
def quotesinglbase(g, P):
    g.add(comma_shape(P))
    g.space(P.sb * 1.5, P.sb * 1.3)


@glyph("quotedblbase", 0x201E)
def quotedblbase(g, P):
    g.add(comma_shape(P))
    g.add(comma_shape(P, dx=qgap(P) * 1.05))
    g.space(P.sb * 1.5, P.sb * 1.3)


def straight_quote(P, x):
    w = P.stem * 0.80
    top = P.cap + 12
    return quad((x - w / 2, top), (x + w / 2, top), (x + w * 0.22, top - P.cap * 0.32),
                (x - w * 0.22, top - P.cap * 0.32))


@glyph("quotesingle", 0x0027)
def quotesingle(g, P):
    g.add(straight_quote(P, 0))
    g.space(P.sb * 1.7, P.sb * 1.7)


@glyph("quotedbl", 0x0022)
def quotedbl(g, P):
    g.add(straight_quote(P, 0))
    g.add(straight_quote(P, P.stem * 0.8 + max(60, P.stem * 0.7)))
    g.space(P.sb * 1.7, P.sb * 1.7)


def chevron(P, x0, left=True, k=1.0):
    S, H, xh = P.stem, P.hair, P.xh
    h = xh * 0.25 * k
    w = h * 0.92
    yc = xh * 0.48
    pen = Pen(S * 0.36, H * 0.6)
    if left:
        p = Path(x0 + w, yc + h).l(x0, yc).l(x0 + w, yc - h)
    else:
        p = Path(x0, yc + h).l(x0 + w, yc).l(x0, yc - h)
    return stk(p, pen), w


@glyph("guilsinglleft", 0x2039)
def guilsinglleft(g, P):
    c, w = chevron(P, 0, True)
    g.add(c)
    g.space(P.sb * 1.3, P.sb * 1.3)


@glyph("guilsinglright", 0x203A)
def guilsinglright(g, P):
    c, w = chevron(P, 0, False)
    g.add(c)
    g.space(P.sb * 1.3, P.sb * 1.3)


@glyph("guillemotleft", 0x00AB)
def guillemotleft(g, P):
    c, w = chevron(P, 0, True)
    g.add(c)
    c2, _ = chevron(P, w * 0.62 + P.stem * 0.55, True)
    g.add(c2)
    g.space(P.sb * 1.3, P.sb * 1.3)


@glyph("guillemotright", 0x00BB)
def guillemotright(g, P):
    c, w = chevron(P, 0, False)
    g.add(c)
    c2, _ = chevron(P, w * 0.62 + P.stem * 0.55, False)
    g.add(c2)
    g.space(P.sb * 1.3, P.sb * 1.3)


# ------------------------------------------------------------- traços

def hyphen_t(P):
    return P.stem * 0.52 + 4


@glyph("hyphen", 0x002D, 0x2010)
def hyphen(g, P):
    t = hyphen_t(P)
    yc = P.xh * 0.50
    g.add(rect(0, yc - t / 2, P.cn * 0.62 + P.stem * 0.3, yc + t / 2))
    g.space(P.sb * 1.2, P.sb * 1.2)


@glyph("endash", 0x2013)
def endash(g, P):
    t = P.hair * 1.25
    yc = P.xh * 0.50
    g.add(rect(0, yc - t / 2, 500 - 2 * 24, yc + t / 2))
    g.space(24, 24)


@glyph("emdash", 0x2014)
def emdash(g, P):
    t = P.hair * 1.25
    yc = P.xh * 0.50
    g.add(rect(0, yc - t / 2, 1000 - 2 * 30, yc + t / 2))
    g.space(30, 30)


@glyph("figuredash", 0x2012)
def figuredash(g, P):
    from .figures import tab_width
    t = P.hair * 1.25
    yc = P.xh * 0.50
    W = tab_width(P)
    g.add(rect(0, yc - t / 2, W - 50, yc + t / 2))
    g.space(width=W, center=True)


@glyph("underscore", 0x005F)
def underscore(g, P):
    t = P.hair * 1.25
    g.add(rect(0, -120 - t, 500, -120))
    g.space(0, 0)


# ------------------------------------------------------------- delimitadores

def paren_geom(P):
    top = P.cap + 92
    bot = P.desc + 28
    return top, bot


def paren_shape(P):
    S, H = P.stem, P.hair
    top, bot = paren_geom(P)
    W = 118 + S * 0.62
    pen = Pen(S * 0.47, H * 0.5)
    mid = (top + bot) / 2
    p = Path(W, top, d=228, w=0.36)
    p.c(pen.hh, mid, d=270, w=1.0)
    p.c(W, bot, d=312, w=0.36)
    return stk(p, pen), W


@glyph("parenleft", 0x0028)
def parenleft(g, P):
    sh, W = paren_shape(P)
    g.add(sh)
    g.space(P.sb * 1.5, P.sb * 0.8)


@glyph("parenright", 0x0029)
def parenright(g, P):
    sh, W = paren_shape(P)
    g.add(transform_contours(sh, -1, 0, 0, 1, W, 0))
    g.space(P.sb * 0.8, P.sb * 1.5)


def bracket_shape(P):
    S, H = P.stem, P.hair
    top, bot = paren_geom(P)
    sw = S * 0.80
    W = sw + 120
    at = H * 1.3
    sh = rect(0, bot, sw, top) + rect(0, top - at, W, top) + rect(0, bot, W, bot + at)
    return sh, W


@glyph("bracketleft", 0x005B)
def bracketleft(g, P):
    sh, W = bracket_shape(P)
    g.add(sh)
    g.space(P.sb * 1.7, P.sb * 0.6)


@glyph("bracketright", 0x005D)
def bracketright(g, P):
    sh, W = bracket_shape(P)
    g.add(transform_contours(sh, -1, 0, 0, 1, W, 0))
    g.space(P.sb * 0.6, P.sb * 1.7)


def brace_shape(P):
    S, H = P.stem, P.hair
    top, bot = paren_geom(P)
    mid = (top + bot) / 2
    W = 150 + S * 0.55
    xs = W * 0.40
    pen = Pen(S * 0.42, H * 0.5)
    up = Path(W, top - pen.hv * 0.4, d=180, w=0.55)
    up.c(xs, top - 110, d=270, w=1.0)
    up.l(xs, mid + 95)
    up.c(0, mid, d=225, w=0.4)
    lo = Path(W, bot + pen.hv * 0.4, d=180, w=0.55)
    lo.c(xs, bot + 110, d=90, w=1.0)
    lo.l(xs, mid - 95)
    lo.c(0, mid, d=135, w=0.4)
    return stk(up, pen) + stk(lo, pen) + poly((0, mid), (xs - 10, mid + 40), (xs - 10, mid - 40)), W


@glyph("braceleft", 0x007B)
def braceleft(g, P):
    sh, W = brace_shape(P)
    g.add(sh)
    g.space(P.sb * 1.4, P.sb * 0.8)


@glyph("braceright", 0x007D)
def braceright(g, P):
    sh, W = brace_shape(P)
    g.add(transform_contours(sh, -1, 0, 0, 1, W, 0))
    g.space(P.sb * 0.8, P.sb * 1.4)


def slash_shape(P, flip=False):
    H = P.hair
    top = P.cap + 70
    bot = -150
    W = (top - bot) * 0.36
    pen = Pen(H * 0.9 + P.stem * 0.12, H * 0.5)
    if flip:
        p = Path(0, top).l(W, bot)
    else:
        p = Path(0, bot).l(W, top)
    return stk(p, pen)


@glyph("slash", 0x002F)
def slash(g, P):
    g.add(slash_shape(P))
    g.space(P.sb * 0.5, P.sb * 0.5)


@glyph("backslash", 0x005C)
def backslash(g, P):
    g.add(slash_shape(P, True))
    g.space(P.sb * 0.5, P.sb * 0.5)


@glyph("fraction", 0x2044)
def fraction(g, P):
    H = P.hair
    top = P.cap
    bot = 0
    W = (top - bot) * 0.48
    pen = Pen(H * 0.8 + P.stem * 0.10, H * 0.5)
    g.add(stk(Path(0, bot).l(W, top), pen))
    g.space(-P.sb * 3.2, -P.sb * 3.2)


@glyph("bar", 0x007C)
def bar(g, P):
    w = P.hair * 1.2 + P.stem * 0.25
    g.add(rect(0, P.desc, w, P.asc + 20))
    g.space(P.sb * 2.6, P.sb * 2.6)


@glyph("brokenbar", 0x00A6)
def brokenbar(g, P):
    w = P.hair * 1.2 + P.stem * 0.25
    g.add(rect(0, P.desc, w, P.xh * 0.42))
    g.add(rect(0, P.xh * 0.70, w, P.asc + 20))
    g.space(P.sb * 2.6, P.sb * 2.6)


# ------------------------------------------------------------- espaços

def _space(name, uni, wfn):
    def fn(g, P):
        g.space(width=round(wfn(P)))
    glyph(name, uni)(fn)


def word_space(P):
    return 242 + P.stem * 0.12


def _tab(P):
    from .figures import tab_width
    return tab_width(P)


_space("space", 0x0020, word_space)
_space("nbspace", 0x00A0, word_space)
_space("figurespace", 0x2007, _tab)
_space("punctuationspace", 0x2008, lambda P: rdot(P) * 2 + P.sb * 3)
_space("thinspace", 0x2009, lambda P: 170)
_space("hairspace", 0x200A, lambda P: 80)
_space("narrownbspace", 0x202F, lambda P: 170)
_space("enspace", 0x2002, lambda P: 500)
_space("emspace", 0x2003, lambda P: 1000)
_space("zerowidthspace", 0x200B, lambda P: 0)


@glyph(".notdef")
def notdef(g, P):
    from ..glyph import reverse_contour
    t = 40
    inner = rect(t, t, 500 - t, P.cap - t)
    g.add(rect(0, 0, 500, P.cap) + [reverse_contour(inner[0])])
    g.space(50, 50)
