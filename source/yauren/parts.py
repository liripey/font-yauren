"""Peças reutilizáveis: hastes, serifas, terminais, formas básicas."""
import math

import numpy as np

from .pen import Path, Pen, stroke


def poly(*pts):
    segs = []
    n = len(pts)
    for i in range(n):
        p = np.array(pts[i], dtype=float)
        q = np.array(pts[(i + 1) % n], dtype=float)
        if np.linalg.norm(p - q) > 1e-6:
            segs.append(("l", p, q))
    return [segs]


def rect(x0, y0, x1, y1):
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    return poly((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def ellipse(cx, cy, rx, ry, t=1.0):
    p = Path(cx + rx, cy, d=90).c(cx, cy + ry, d=180, t=t).c(cx - rx, cy, d=270, t=t)
    p.c(cx, cy - ry, d=0, t=t).close("c", t=t)
    return p.fill()


def pen_lc(P, ang=None):
    return Pen(P.stem / 2, P.hair / 2, P.ang if ang is None else ang)


def pen_uc(P, ang=None):
    return Pen(P.stemC / 2, P.hairC / 2, P.ang if ang is None else ang)


def pen_curve(P, ang=None):
    return Pen(P.curve / 2, P.hair / 2, P.ang if ang is None else ang)


def pen_curveC(P, ang=None):
    return Pen(P.curveC / 2, P.hairC / 2, P.ang if ang is None else ang)


def S(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def mirror_y(contours, y0):
    from .glyph import transform_contours
    return transform_contours(contours, 1, 0, 0, -1, 0, 2 * y0)


def mirror_x(contours, x0):
    from .glyph import transform_contours
    return transform_contours(contours, -1, 0, 0, 1, 2 * x0, 0)


def shift(contours, dx=0, dy=0):
    from .glyph import transform_contours
    return transform_contours(contours, 1, 0, 0, 1, dx, dy)


# ------------------------------------------------------------------ serifas

def foot_serif(P, xl, xr, y0=0, el=None, er=None, tip=None, br=None,
               slope=4.0, flip=False, caps=False, sl=0.0, sr=0.0):
    """Serifa de pé com colchete (bracket), apoiada em y0.
    xl/xr: bordas da haste na linha y0. el/er: extensões esquerda/direita.
    sl/sr: inclinação das bordas da haste (dx por unidade de altura, a
    partir da base da serifa) para hastes diagonais.
    flip=True espelha (serifa de topo)."""
    ext = P.sfxC if caps else P.sfx
    el = ext if el is None else el
    er = ext if er is None else er
    tip = (P.sftC if caps else P.sft) if tip is None else tip
    br = (P.sfbC if caps else P.sfb) if br is None else br
    hgt = tip + br + 40

    def XL(h):
        return xl + sl * h

    def XR(h):
        return xr + sr * h

    p = Path(XL(0) - el, y0) if el > 0 else Path(XL(0), y0)
    if er > 0:
        p.l(XR(0) + er, y0).l(XR(0) + er, y0 + tip, dout=180 - slope)
        p.c(XR(tip + br), y0 + tip + br, d=math.degrees(math.atan2(1, sr)))
    else:
        p.l(XR(0), y0)
    p.l(XR(hgt), y0 + hgt).l(XL(hgt), y0 + hgt)
    if el > 0:
        p.l(XL(tip + br), y0 + tip + br, dout=math.degrees(math.atan2(-1, -sl)))
        p.c(XL(0) - el, y0 + tip, d=180 + slope)
    c = p.fill()
    if flip:
        c = mirror_y(c, y0)
    return c


def head_serif(P, xl, xr, top, ext=None, drop=None, tipf=0.55, br=None):
    """Serifa de cabeça em cunha (minúsculas), estilo garalde.
    O topo da haste inclina-se da direita para a ponta à esquerda."""
    ext = P.hdx if ext is None else ext
    drop = P.hdd if drop is None else drop
    tip = P.hair * tipf
    br = P.sfb * 1.1 if br is None else br
    tx = xl - ext
    p = Path(xr, top)
    p.l(tx, top - drop)
    p.l(tx, top - drop - tip, dout=-4)
    p.c(xl, top - drop - tip - br, d=270)
    p.l(xl, top - drop - tip - br - 40)
    p.l(xr, top - drop - tip - br - 40)
    return p.fill()


def spur_serif(P, xl, xr, y0, side="right", ext=None, flip=False):
    """Esporão: serifa unilateral (ex.: pé do d, a; topo do q)."""
    ext = P.sfx * 0.9 if ext is None else ext
    if side == "right":
        return foot_serif(P, xl, xr, y0, el=0, er=ext, flip=flip)
    return foot_serif(P, xl, xr, y0, el=ext, er=0, flip=flip)


def beak(P, x, y, t, L, w, side="left", vert="down", br=None, taper=0.55):
    """Serifa vertical (bico) na ponta de um braço horizontal.
    x: borda externa do braço; y: aresta externa do braço (topo p/ 'down');
    t: espessura do braço; L: quanto o bico ultrapassa o braço;
    w: largura do bico junto ao braço."""
    br = P.sfbC * 1.2 if br is None else br
    yb = y - t           # face interna do braço
    p = Path(x, y)
    p.l(x, yb - L)
    p.l(x + w * taper, yb - L + 2, dout=88)
    p.c(x + w + br, yb, d=0, t=1.1)
    p.l(x + w + br + 40, yb)
    p.l(x + w + br + 40, y)
    c = p.fill()
    if side == "right":
        c = mirror_x(c, x)
    if vert == "up":
        c = mirror_y(c, y)
    return c


def halfplane(p, q, side="left", R=4000):
    """Semiplano à esquerda (ou direita) da reta orientada p->q."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    d = q - p
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    if side == "right":
        n = -n
    a = p - d * R
    b = q + d * R
    return poly(a, b, b + n * R, a + n * R)


def quad(*pts):
    return poly(*pts)


def ball(P, cx, cy, r, ry=None):
    return ellipse(cx, cy, r, r if ry is None else ry)
