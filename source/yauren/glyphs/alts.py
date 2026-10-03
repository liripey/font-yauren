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
    """fl clássico: o arco do f desce como haste do l."""
    from ..pen import Path, Pen, stroke
    from ..parts import foot_serif
    S, H, xh, asc = P.stem, P.hair, P.xh, P.asc
    pl = Pen(S / 2, H / 2)
    x0 = S * 0.60
    LC.stem(g, P, x0, 0, xh, head=False, foot="both", er=P.sfx * 1.0)
    xl = x0 + S + P.cn * 0.66
    top = asc + P.os * 0.5
    p = Path(x0 + S / 2, xh - 10, d=90)
    p.l(x0 + S / 2, asc - (asc - xh) * 0.55)
    p.c((x0 + S / 2 + xl + S / 2) / 2, top - pl.hv, d=0, w=1.0)
    p.c(xl + S / 2, asc - (asc - xh) * 0.55, d=270, w=1.0)
    p.l(xl + S / 2, P.sft)
    g.add(stroke(p, pl))
    g.add(foot_serif(P, xl, xl + S, 0))
    bt = P.hair * 1.12
    g.add(rect(0, xh - bt, x0 + S + P.cn * 0.40, xh))
    LC.anchors_lc(g, xl + S / 2, P=P)
    g.space(P.sb * 0.6, P.sb)
