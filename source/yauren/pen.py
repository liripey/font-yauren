"""Esqueletos (caminhos) e expansão por pena elíptica.

Um Path descreve a linha central de um traço com nós (x, y, direção,
largura). A expansão usa o modelo de Minkowski de uma pena elíptica:
semi-eixo A na horizontal (metade da haste vertical) e B na vertical
(metade do traço fino). Isto produz contraste de eixo vertical natural
(traços horizontais finos, verticais grossos), como em Georgia, com
possibilidade de girar a pena para eixo humanista (Garamond).
"""
import math

import numpy as np

from .geom import (EPS, bez_pt, bez_tangent, dir_vec, fit_function,
                   hobby_controls, line_intersect, unit, vec)


class Knot:
    __slots__ = ("p", "din", "dout", "w", "a", "b")

    def __init__(self, x, y, din=None, dout=None, w=None, a=None, b=None):
        self.p = vec(x, y)
        self.din = din
        self.dout = dout
        self.w = w
        self.a = a
        self.b = b


class Seg:
    __slots__ = ("kind", "bez", "k0", "k1", "t0", "t1", "explicit")

    def __init__(self, kind, k0, k1, t0=1.0, t1=1.0, explicit=None):
        self.kind = kind  # 'c' curva de Hobby, 'l' reta, 'x' cúbica explícita
        self.k0 = k0
        self.k1 = k1
        self.t0 = t0
        self.t1 = t1
        self.explicit = explicit
        self.bez = None


def _ang(d):
    return None if d is None else math.radians(d)


class Path:
    """Construtor de esqueleto.

    p = Path(x, y, d=90).c(x, y, d=0).l(x, y)
    d: direção (graus) do traçado no nó; din/dout para cantos.
    w: fator de largura da pena no nó; a/b: semi-eixos absolutos.
    t: tensão do segmento (>1 mais tenso; <1 mais "cheio").
    """

    def __init__(self, x, y, d=None, din=None, dout=None, w=None, a=None, b=None):
        if din is None:
            din = d
        if dout is None:
            dout = d
        self.knots = [Knot(x, y, _ang(din), _ang(dout), w, a, b)]
        self.segs = []
        self.closed = False

    # -- construção
    def _add(self, kind, x, y, d, din, dout, w, a, b, t, t0, t1, explicit=None):
        if din is None:
            din = d
        if dout is None:
            dout = d
        k = Knot(x, y, _ang(din), _ang(dout), w, a, b)
        k0 = self.knots[-1]
        self.knots.append(k)
        t0 = t if t0 is None else t0
        t1 = t if t1 is None else t1
        self.segs.append(Seg(kind, k0, k, t0, t1, explicit))
        return self

    def c(self, x, y, d=None, din=None, dout=None, w=None, a=None, b=None, t=1.0, t0=None, t1=None):
        return self._add("c", x, y, d, din, dout, w, a, b, t, t0, t1)

    def l(self, x, y, w=None, a=None, b=None, d=None, din=None, dout=None):
        return self._add("l", x, y, d, din, dout, w, a, b, 1.0, None, None)

    def cc(self, x1, y1, x2, y2, x, y, w=None, a=None, b=None):
        return self._add("x", x, y, None, None, None, w, a, b, 1.0, None, None,
                         explicit=(vec(x1, y1), vec(x2, y2)))

    def close(self, kind="c", t=1.0, t0=None, t1=None):
        k0 = self.knots[-1]
        k1 = self.knots[0]
        t0 = t if t0 is None else t0
        t1 = t if t1 is None else t1
        self.segs.append(Seg(kind, k0, k1, t0, t1))
        self.closed = True
        return self

    # -- resolução das Bézier
    def resolve(self):
        n = len(self.segs)
        # propaga larguras/eixos
        last_w, last_a, last_b = 1.0, None, None
        for k in self.knots:
            if k.w is None:
                k.w = last_w
            last_w = k.w
            if k.a is None:
                k.a = last_a
            last_a = k.a
            if k.b is None:
                k.b = last_b
            last_b = k.b
        for i, s in enumerate(self.segs):
            p0, p1 = s.k0.p, s.k1.p
            if s.kind == "l":
                s.bez = np.array([p0, p0 + (p1 - p0) / 3, p0 + 2 * (p1 - p0) / 3, p1])
            elif s.kind == "x":
                s.bez = np.array([p0, s.explicit[0], s.explicit[1], p1])
            else:
                a0 = s.k0.dout
                if a0 is None:
                    prev = self.segs[i - 1] if (i > 0 or self.closed) else None
                    if prev is not None and prev.kind == "l":
                        v = prev.k1.p - prev.k0.p
                        a0 = math.atan2(v[1], v[0])
                    else:
                        v = p1 - p0
                        a0 = math.atan2(v[1], v[0])
                a1 = s.k1.din
                if a1 is None:
                    nxt = self.segs[i + 1] if i + 1 < n else (self.segs[0] if self.closed else None)
                    if nxt is not None and nxt.kind == "l":
                        v = nxt.k1.p - nxt.k0.p
                        a1 = math.atan2(v[1], v[0])
                    else:
                        v = p1 - p0
                        a1 = math.atan2(v[1], v[0])
                c1, c2 = hobby_controls(p0, a0, p1, a1, s.t0, s.t1)
                c1, c2 = _clamp_extrema(p0, c1, c2, p1, a0, a1)
                s.bez = np.array([p0, c1, c2, p1])
        return self

    # -- contorno preenchido (sem pena)
    def fill(self):
        """Interpreta o esqueleto como contorno fechado preenchido."""
        if not self.closed:
            self.close("l")
        self.resolve()
        segs = []
        for s in self.segs:
            if s.kind == "l":
                segs.append(("l", s.bez[0], s.bez[3]))
            else:
                segs.append(("c",) + tuple(s.bez))
        return [segs]


def _clamp_extrema(p0, c1, c2, p1, a0, a1, tol=1e-6):
    """Nós com tangente horizontal/vertical são extremos verdadeiros: as
    alças não podem ultrapassar a coordenada do nó (evita "corcundas")."""
    c1 = c1.copy()
    c2 = c2.copy()
    for axis, trig in ((1, math.sin), (0, math.cos)):
        # tangente paralela ao outro eixo => extremo neste eixo
        if abs(trig(a1)) < tol:
            lo, hi = sorted((p0[axis], p1[axis]))
            c1[axis] = min(max(c1[axis], lo), hi)
        if abs(trig(a0)) < tol:
            lo, hi = sorted((p0[axis], p1[axis]))
            c2[axis] = min(max(c2[axis], lo), hi)
    return c1, c2


# ------------------------------------------------------------------ pena

class Pen:
    """Pena elíptica: A semi-eixo horizontal, B vertical, ang rotação (graus)."""

    def __init__(self, A, B, ang=0.0):
        self.A = A
        self.B = B
        self.ang = math.radians(ang)

    @property
    def hv(self):
        """Meia-espessura vertical ao traçar na horizontal."""
        return float(self.support(np.array([0.0, 1.0]), self.A, self.B)[1])

    @property
    def hh(self):
        """Meia-espessura horizontal ao traçar na vertical."""
        return float(self.support(np.array([1.0, 0.0]), self.A, self.B)[0])

    def scaled(self, w):
        return Pen(self.A * w, self.B * w, math.degrees(self.ang))

    def support(self, n, A, B):
        ca, sa = math.cos(self.ang), math.sin(self.ang)
        # leva n para o referencial da elipse
        nx = ca * n[0] + sa * n[1]
        ny = -sa * n[0] + ca * n[1]
        den = math.sqrt(A * A * nx * nx + B * B * ny * ny)
        if den < EPS:
            return np.array([0.0, 0.0])
        sx = A * A * nx / den
        sy = B * B * ny / den
        return np.array([ca * sx - sa * sy, sa * sx + ca * sy])


def _smooth(t):
    return t * t * (3 - 2 * t)


def _seg_offset_fn(seg, pen, sign):
    k0, k1 = seg.k0, seg.k1
    A0 = k0.a if k0.a is not None else pen.A
    A1 = k1.a if k1.a is not None else pen.A
    B0 = k0.b if k0.b is not None else pen.B
    B1 = k1.b if k1.b is not None else pen.B
    w0, w1 = k0.w, k1.w
    lin = seg.kind == "l"
    b = seg.bez

    def f(t):
        s = t if lin else _smooth(t)
        w = w0 + (w1 - w0) * s
        A = (A0 + (A1 - A0) * s) * w
        B = (B0 + (B1 - B0) * s) * w
        p = bez_pt(b, t)
        tg = bez_tangent(b, t)
        n = np.array([-tg[1], tg[0]])
        return p + sign * pen.support(n, A, B)

    return f


def _offset_side(seg, pen, sign, err):
    f = _seg_offset_fn(seg, pen, sign)
    if seg.kind == "l":
        return [("l", f(0.0), f(1.0))]
    out = []
    for bz in fit_function(f, 0.0, 1.0, err=err):
        out.append(("c", bz[0], bz[1], bz[2], bz[3]))
    return out


def _seg_dirs(seg):
    return bez_tangent(seg.bez, 0.0), bez_tangent(seg.bez, 1.0)


def _is_corner(sa, sb, tol_deg=2.0):
    ta = _seg_dirs(sa)[1]
    tb = _seg_dirs(sb)[0]
    c = max(-1.0, min(1.0, float(np.dot(ta, tb))))
    return math.degrees(math.acos(c)) > tol_deg


def _rev(segs):
    out = []
    for s in reversed(segs):
        if s[0] == "l":
            out.append(("l", s[2], s[1]))
        else:
            out.append(("c", s[4], s[3], s[2], s[1]))
    return out


def _chain(segs):
    """Liga segmentos consecutivos fechando pequenos vãos com retas."""
    out = []
    for s in segs:
        if out:
            prev_end = out[-1][-1]
            start = s[1]
            if np.linalg.norm(prev_end - start) > 0.01:
                out.append(("l", prev_end, start))
        out.append(s)
    return out


def _cap(kind, p_from, p_to, center, tangent, pen, A, B):
    """Segmentos do terminal do traço, de p_from até p_to."""
    if kind == "butt" or np.linalg.norm(p_from - p_to) < 0.01:
        return [("l", p_from, p_to)]
    if kind == "round":
        h = np.linalg.norm(p_to - p_from) / 2
        u = unit(p_to - p_from)
        r = abs(float(np.dot(pen.support(tangent, A, B), tangent)))
        mid = 0.5 * (p_from + p_to) + tangent * r
        k = 0.5523
        return [("c", p_from, p_from + tangent * k * r, mid - u * k * h, mid),
                ("c", mid, mid + u * k * h, p_to + tangent * k * r, p_to)]
    return [("l", p_from, p_to)]


def stroke(path, pen, cap0="butt", cap1="butt", err=0.9):
    """Expande o esqueleto. Retorna lista de contornos (listas de segmentos)."""
    path.resolve()
    segs = path.segs
    if not segs:
        return []
    # divide em trechos lisos nos cantos
    runs = [[segs[0]]]
    corners = []
    for i in range(1, len(segs)):
        if _is_corner(segs[i - 1], segs[i]):
            corners.append((segs[i - 1], segs[i]))
            runs.append([segs[i]])
        else:
            runs[-1].append(segs[i])
    closed_smooth = False
    if path.closed:
        if _is_corner(segs[-1], segs[0]):
            corners.append((segs[-1], segs[0]))
        else:
            if len(runs) == 1:
                closed_smooth = True
            else:
                runs[0] = runs[-1] + runs[0]
                runs.pop()

    contours = []
    if closed_smooth:
        left, right = [], []
        for s in runs[0]:
            left += _offset_side(s, pen, +1, err)
            right += _offset_side(s, pen, -1, err)
        left = _chain(left)
        right = _chain(right)
        if np.linalg.norm(left[-1][-1] - left[0][1]) > 0.01:
            left.append(("l", left[-1][-1], left[0][1]))
        if np.linalg.norm(right[-1][-1] - right[0][1]) > 0.01:
            right.append(("l", right[-1][-1], right[0][1]))
        contours.append(left)
        contours.append(_rev(right))
        return contours

    nruns = len(runs)
    for ri, run in enumerate(runs):
        left, right = [], []
        for s in run:
            left += _offset_side(s, pen, +1, err)
            right += _offset_side(s, pen, -1, err)
        left = _chain(left)
        right = _chain(right)
        c = list(left)
        first = run[0]
        last = run[-1]
        is_first = ri == 0 and not path.closed
        is_last = ri == nruns - 1 and not path.closed
        ck1 = cap1 if is_last else "butt"
        ck0 = cap0 if is_first else "butt"
        t_end = bez_tangent(last.bez, 1.0)
        A1 = (last.k1.a if last.k1.a is not None else pen.A) * last.k1.w
        B1 = (last.k1.b if last.k1.b is not None else pen.B) * last.k1.w
        c += _cap(ck1, left[-1][-1], right[-1][-1], last.bez[3], t_end, pen, A1, B1)
        c += _rev(right)
        t_st = -bez_tangent(first.bez, 0.0)
        A0 = (first.k0.a if first.k0.a is not None else pen.A) * first.k0.w
        B0 = (first.k0.b if first.k0.b is not None else pen.B) * first.k0.w
        c += _cap(ck0, right[0][1], left[0][1], first.bez[0], t_st, pen, A0, B0)
        contours.append(_chain(c))

    # remendos de junção (mitra) nos cantos
    for sa, sb in corners:
        contours += _miter_patch(sa, sb, pen, err)
    # todas as peças são sólidas: orientação anti-horária uniforme
    return [c if _area(c) > 0 else _rev(c) for c in contours]


def _area(c):
    pts = []
    for s in c:
        if s[0] == "l":
            pts.append(s[1])
        else:
            b = np.array(s[1:])
            for t in np.linspace(0, 1, 9)[:-1]:
                pts.append(bez_pt(b, t))
    pts = np.array(pts)
    x, y = pts[:, 0], pts[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def _miter_patch(sa, sb, pen, err, limit=4.0):
    out = []
    center = sa.bez[3]
    ta = bez_tangent(sa.bez, 1.0)
    tb = bez_tangent(sb.bez, 0.0)
    for sign in (+1, -1):
        fa = _seg_offset_fn(sa, pen, sign)
        fb = _seg_offset_fn(sb, pen, sign)
        pa = fa(1.0)
        pb = fb(0.0)
        m = line_intersect(pa, ta, pb, tb)
        width = max(np.linalg.norm(pa - center), 1.0)
        if m is None or np.linalg.norm(m - center) > limit * width:
            poly = [center, pa, pb]
        else:
            poly = [center, pa, m, pb]
        segs = []
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            if np.linalg.norm(p - q) > 0.01:
                segs.append(("l", p, q))
        if len(segs) >= 3:
            out.append(segs)
    return out
