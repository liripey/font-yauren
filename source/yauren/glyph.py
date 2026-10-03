"""Contêiner de glifo: soma/subtração de formas, limpeza do contorno."""
import math

import numpy as np
import pathops

from .geom import bez_extrema_t, bez_pt, bez_split


# ------------------------------------------------------------ utilidades

def seg_end(s):
    return s[-1]


def seg_start(s):
    return s[1]


def contours_to_skpath(contours):
    path = pathops.Path()
    pen = path.getPen()
    for c in contours:
        if not c:
            continue
        pen.moveTo(tuple(map(float, c[0][1])))
        for s in c:
            if s[0] == "l":
                pen.lineTo(tuple(map(float, s[2])))
            else:
                pen.curveTo(tuple(map(float, s[2])), tuple(map(float, s[3])), tuple(map(float, s[4])))
        pen.closePath()
    return path


class _SegPen:
    def __init__(self):
        self.contours = []
        self.cur = None
        self.pt = None
        self.start = None

    def moveTo(self, p):
        self.cur = []
        self.pt = np.array(p, dtype=float)
        self.start = self.pt

    def lineTo(self, p):
        p = np.array(p, dtype=float)
        self.cur.append(("l", self.pt, p))
        self.pt = p

    def curveTo(self, *pts):
        pts = [np.array(p, dtype=float) for p in pts]
        if len(pts) == 3:
            self.cur.append(("c", self.pt, pts[0], pts[1], pts[2]))
            self.pt = pts[2]
        else:
            raise ValueError("curveTo com número inesperado de pontos")

    def qCurveTo(self, *pts):
        pts = [np.array(p, dtype=float) for p in pts]
        # converte quadráticas (raras) em cúbicas
        on = self.pt
        offs = pts[:-1]
        last = pts[-1]
        for i, q in enumerate(offs):
            nxt = last if i == len(offs) - 1 else 0.5 * (q + offs[i + 1])
            c1 = on + 2.0 / 3.0 * (q - on)
            c2 = nxt + 2.0 / 3.0 * (q - nxt)
            self.cur.append(("c", on, c1, c2, nxt))
            on = nxt
        self.pt = on

    def closePath(self):
        if self.cur:
            if np.linalg.norm(self.pt - self.start) > 1e-6:
                self.cur.append(("l", self.pt, self.start))
            self.contours.append(self.cur)
        self.cur = None

    def endPath(self):
        self.closePath()


def skpath_to_contours(path):
    pen = _SegPen()
    path.draw(pen)
    return pen.contours


def transform_contours(contours, a=1, b=0, c=0, d=1, dx=0, dy=0):
    M = np.array([[a, c], [b, d]], dtype=float)
    off = np.array([dx, dy], dtype=float)
    out = []
    flip = (a * d - b * c) < 0
    for cnt in contours:
        nc = []
        for s in cnt:
            pts = [M @ p + off for p in s[1:]]
            nc.append((s[0],) + tuple(pts))
        if flip:
            nc = reverse_contour(nc)
        out.append(nc)
    return out


def reverse_contour(c):
    out = []
    for s in reversed(c):
        if s[0] == "l":
            out.append(("l", s[2], s[1]))
        else:
            out.append(("c", s[4], s[3], s[2], s[1]))
    return out


def contour_area(c):
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


def contours_bounds(contours):
    xs, ys = [], []
    for c in contours:
        for s in c:
            if s[0] == "l":
                xs += [s[1][0], s[2][0]]
                ys += [s[1][1], s[2][1]]
            else:
                b = np.array(s[1:])
                pts = bez_pt(b, np.linspace(0, 1, 33))
                xs += list(pts[:, 0])
                ys += list(pts[:, 1])
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------ limpeza

def _seg_len(s):
    if s[0] == "l":
        return float(np.linalg.norm(s[2] - s[1]))
    b = np.array(s[1:])
    pts = bez_pt(b, np.linspace(0, 1, 9))
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))


def _split_extrema(c):
    out = []
    for s in c:
        if s[0] != "c":
            out.append(s)
            continue
        b = np.array(s[1:])
        ts = bez_extrema_t(b)
        # só divide quando o extremo realmente ultrapassa as pontas
        keep = []
        for t in ts:
            p = bez_pt(b, t)
            lo = np.minimum(b[0], b[3])
            hi = np.maximum(b[0], b[3])
            over = max(lo[0] - p[0], p[0] - hi[0], lo[1] - p[1], p[1] - hi[1])
            if over > 0.35:
                keep.append(t)
        if not keep:
            out.append(s)
            continue
        rest = b
        prev_t = 0.0
        for t in keep:
            tt = (t - prev_t) / (1 - prev_t)
            left, rest = bez_split(rest, tt)
            out.append(("c",) + tuple(left))
            prev_t = t
        out.append(("c",) + tuple(rest))
    return out


def _round_contour(c):
    out = []
    for s in c:
        out.append((s[0],) + tuple(np.round(p) for p in s[1:]))
    return out


def _is_flat_curve(s, tol=0.6):
    b = np.array(s[1:])
    p0, p3 = b[0], b[3]
    d = p3 - p0
    L = np.linalg.norm(d)
    if L < 1e-6:
        return np.linalg.norm(b[1] - p0) < tol and np.linalg.norm(b[2] - p0) < tol
    n = np.array([-d[1], d[0]]) / L
    return abs(np.dot(b[1] - p0, n)) < tol and abs(np.dot(b[2] - p0, n)) < tol


def _collinear(a, b, c, tol=0.6):
    d = c - a
    L = np.linalg.norm(d)
    if L < 1e-6:
        return True
    n = np.array([-d[1], d[0]]) / L
    # b deve estar entre a e c
    t = np.dot(b - a, d) / (L * L)
    return abs(np.dot(b - a, n)) < tol and -0.01 < t < 1.01


def cleanup_contour(c, min_len=1.0):
    c = _split_extrema(c)
    c = _round_contour(c)
    # curvas planas viram retas
    c = [("l", s[1], s[4]) if s[0] == "c" and _is_flat_curve(s, 0.45) else s for s in c]
    # remove segmentos minúsculos (funde pontos)
    changed = True
    while changed and len(c) > 2:
        changed = False
        for i, s in enumerate(c):
            if _seg_len(s) < min_len:
                prev = c[i - 1]
                nxt = c[(i + 1) % len(c)]
                # conecta o fim do anterior ao início do próximo
                p_new = s[1] if s[0] == "l" else s[1]
                nxt = (nxt[0], p_new) + tuple(nxt[2:])
                c[(i + 1) % len(c)] = nxt
                del c[i]
                changed = True
                break
    # funde retas colineares
    changed = True
    while changed and len(c) > 2:
        changed = False
        for i in range(len(c)):
            a = c[i]
            b = c[(i + 1) % len(c)]
            if a[0] == "l" and b[0] == "l" and _collinear(a[1], a[2], b[2]):
                j = (i + 1) % len(c)
                c[i] = ("l", a[1], b[2])
                del c[j]
                changed = True
                break
    # garante continuidade exata
    for i in range(len(c)):
        nxt = c[(i + 1) % len(c)]
        end = c[i][-1]
        if not np.array_equal(nxt[1], end):
            c[(i + 1) % len(c)] = (nxt[0], end) + tuple(nxt[2:])
    return c


def _harmonize(c, tol_deg=4.0):
    """Força alças horizontais/verticais em nós de extremo quase alinhados."""
    n = len(c)
    out = [list(s) for s in c]
    for i in range(n):
        a = out[i]
        b = out[(i + 1) % n]
        if a[0] != "c" or b[0] != "c":
            continue
        node = a[4]
        hin = a[3]
        hout = b[2]
        vin = node - hin
        vout = hout - node
        if np.linalg.norm(vin) < 1 or np.linalg.norm(vout) < 1:
            continue
        for axis in (0, 1):
            other = 1 - axis
            ang_in = math.degrees(math.atan2(abs(vin[other]), abs(vin[axis]) + 1e-9))
            ang_out = math.degrees(math.atan2(abs(vout[other]), abs(vout[axis]) + 1e-9))
            if ang_in < tol_deg and ang_out < tol_deg and np.sign(vin[axis]) == np.sign(vout[axis]):
                hin = hin.copy()
                hout = hout.copy()
                hin[other] = node[other]
                hout[other] = node[other]
                a[3] = hin
                b[2] = hout
    return [tuple(s) for s in out]


def cleanup(contours):
    out = []
    for c in contours:
        if not c:
            continue
        c = cleanup_contour(list(c))
        if len(c) < 2:
            continue
        c = _harmonize(c)
        if abs(contour_area(c)) < 4:
            continue
        out.append(c)
    return out


def clip(shape, *cutters):
    """Subtrai os cortadores de UMA forma (corte local)."""
    p = contours_to_skpath(shape)
    p.simplify(fix_winding=True, keep_starting_points=False)
    for c in cutters:
        q = contours_to_skpath(c)
        q.simplify(fix_winding=True, keep_starting_points=False)
        p = pathops.op(p, q, pathops.PathOp.DIFFERENCE, fix_winding=True,
                       keep_starting_points=False)
    return skpath_to_contours(p)


def intersect(shape, *masks):
    """Interseção de UMA forma com máscaras."""
    p = contours_to_skpath(shape)
    p.simplify(fix_winding=True, keep_starting_points=False)
    for c in masks:
        q = contours_to_skpath(c)
        q.simplify(fix_winding=True, keep_starting_points=False)
        p = pathops.op(p, q, pathops.PathOp.INTERSECTION, fix_winding=True,
                       keep_starting_points=False)
    return skpath_to_contours(p)


# ------------------------------------------------------------ Glyph

class Glyph:
    def __init__(self, name, unicodes=()):
        self.name = name
        self.unicodes = list(unicodes)
        self.adds = []
        self.cuts = []
        self.anchors = {}
        self.lsb = None
        self.rsb = None
        self.width = None
        self.contours = None
        self.center = False

    def add(self, contours):
        if contours:
            self.adds.append(contours)
        return self

    def cut(self, contours):
        if contours:
            self.cuts.append(contours)
        return self

    def anchor(self, name, x, y):
        self.anchors[name] = (float(x), float(y))

    def space(self, lsb=None, rsb=None, width=None, center=False):
        self.lsb = lsb
        self.rsb = rsb
        self.width = width
        self.center = center

    def solve(self):
        builder = pathops.OpBuilder(fix_winding=True, keep_starting_points=False)
        any_add = False
        for shape in self.adds:
            p = contours_to_skpath(shape)
            p.simplify(fix_winding=True, keep_starting_points=False)
            builder.add(p, pathops.PathOp.UNION)
            any_add = True
        for shape in self.cuts:
            p = contours_to_skpath(shape)
            p.simplify(fix_winding=True, keep_starting_points=False)
            builder.add(p, pathops.PathOp.DIFFERENCE)
        if not any_add:
            self.contours = []
            return self
        res = builder.resolve()
        self.contours = skpath_to_contours(res)
        return self
