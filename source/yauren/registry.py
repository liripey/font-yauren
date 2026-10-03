"""Registro de glifos desenhados e compostos."""
from collections import OrderedDict

GLYPHS = OrderedDict()      # nome -> (unicodes, função)
COMPOSITES = OrderedDict()  # nome -> (unicodes, base, [marcas], opções)


def glyph(name, *unicodes):
    def deco(f):
        GLYPHS[name] = (list(unicodes), f)
        return f
    return deco


def composite(name, unicodes, base, marks, **opts):
    if isinstance(unicodes, int):
        unicodes = [unicodes]
    COMPOSITES[name] = (list(unicodes), base, list(marks), opts)


def borrow(name, P, a=1, b=0, c=0, d=1, dx=0, dy=0):
    """Desenha outro glifo (coordenadas de desenho, sem espaçamento) e
    devolve (contornos transformados, glifo temporário)."""
    from .glyph import Glyph, transform_contours
    unis, f = GLYPHS[name]
    t = Glyph(name)
    f(t, P)
    t.solve()
    return transform_contours(t.contours, a, b, c, d, dx, dy), t
