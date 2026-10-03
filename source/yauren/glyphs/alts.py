"""Alternativos: formas para caixa-alta (.case) e ligaduras."""
from ..glyph import contours_bounds, transform_contours
from ..parts import rect
from ..registry import borrow, glyph
from . import lower as LC

# glifos de pontuação elevados para texto em maiúsculas
CASE = ["hyphen", "endash", "emdash", "parenleft", "parenright", "bracketleft",
        "bracketright", "braceleft", "braceright", "guilsinglleft", "guilsinglright",
        "guillemotleft", "guillemotright", "periodcentered", "bullet", "exclamdown",
        "questiondown", "at"]


def case_shift(P, name):
    if name in ("parenleft", "parenright", "bracketleft", "bracketright", "braceleft",
                "braceright"):
        return round((P.cap - P.xh) * 0.42)
    if name in ("exclamdown", "questiondown"):
        return round(P.cap - P.xh - P.os)
    if name == "at":
        return round((P.cap - P.xh) * 0.55)
    return round((P.cap - P.xh) * 0.5)


def _make_case(name):
    def fn(g, P):
        from ..registry import GLYPHS
        c, t = borrow(name, P)
        g.add(transform_contours(c, dy=case_shift(P, name)))
        g.space(t.lsb, t.rsb, width=None)
    return fn


for _n in CASE:
    glyph(_n + ".case")(_make_case(_n))


# ------------------------------------------------------------- ligaduras

@glyph("fi", 0xFB01)
def fi(g, P):
    f, _ = borrow("f", P)
    i, _ = borrow("dotlessi", P)
    S = P.stem
    fb = contours_bounds(f)
    # barra do f se estende até a haste do i
    xi = fb[2] - S * 0.15
    g.add(f)
    g.add(transform_contours(i, dx=xi))
    bt = P.hair * 1.12
    g.add(rect(S * 0.6 + S, P.xh - bt, xi + S * 0.5, P.xh))
    LC.anchors_lc(g, xi + S / 2, P=P)
    g.space(P.sb * 0.6, P.sb)


@glyph("fl", 0xFB02)
def fl(g, P):
    f, _ = borrow("f", P)
    l, _ = borrow("l", P)
    S = P.stem
    fb = contours_bounds(f)
    xl = fb[2] - S * 0.15
    g.add(f)
    g.add(transform_contours(l, dx=xl))
    bt = P.hair * 1.12
    g.add(rect(S * 0.6 + S, P.xh - bt, xl + S * 0.5, P.xh))
    LC.anchors_lc(g, xl + S / 2, P=P)
    g.space(P.sb * 0.6, P.sb)
