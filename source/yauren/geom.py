"""Geometria base: Bézier cúbicas, curvas de Hobby e ajuste de curvas.

Todas as funções trabalham com numpy (float64). Uma Bézier cúbica é um
array 4x2: [p0, p1, p2, p3].
"""
import math

import numpy as np

EPS = 1e-9


def vec(x, y):
    return np.array([float(x), float(y)])


def unit(v):
    n = math.hypot(v[0], v[1])
    if n < EPS:
        return np.array([0.0, 0.0])
    return v / n


def dir_vec(deg):
    r = math.radians(deg)
    return np.array([math.cos(r), math.sin(r)])


def angle_of(v):
    return math.atan2(v[1], v[0])


def norm_angle(a):
    while a <= -math.pi:
        a += 2 * math.pi
    while a > math.pi:
        a -= 2 * math.pi
    return a


# ---------------------------------------------------------------- Bézier

def bez_pt(b, t):
    t = np.asarray(t, dtype=float)
    mt = 1.0 - t
    if t.ndim == 0:
        return (mt ** 3) * b[0] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * b[2] + t ** 3 * b[3]
    t = t[:, None]
    mt = mt[:, None]
    return (mt ** 3) * b[0] + 3 * mt * mt * t * b[1] + 3 * mt * t * t * b[2] + t ** 3 * b[3]


def bez_d1(b, t):
    t = float(t)
    mt = 1.0 - t
    return 3 * mt * mt * (b[1] - b[0]) + 6 * mt * t * (b[2] - b[1]) + 3 * t * t * (b[3] - b[2])


def bez_d2(b, t):
    t = float(t)
    return 6 * (1 - t) * (b[2] - 2 * b[1] + b[0]) + 6 * t * (b[3] - 2 * b[2] + b[1])


def bez_tangent(b, t):
    """Tangente unitária robusta (trata alças degeneradas)."""
    d = bez_d1(b, t)
    if math.hypot(d[0], d[1]) > 1e-7:
        return unit(d)
    # alça colapsada: usa a segunda derivada / corda
    if t < 0.5:
        d = b[2] - b[0] if np.linalg.norm(b[2] - b[0]) > EPS else b[3] - b[0]
    else:
        d = b[3] - b[1] if np.linalg.norm(b[3] - b[1]) > EPS else b[3] - b[0]
    return unit(d)


def bez_split(b, t):
    p01 = b[0] + (b[1] - b[0]) * t
    p12 = b[1] + (b[2] - b[1]) * t
    p23 = b[2] + (b[3] - b[2]) * t
    p012 = p01 + (p12 - p01) * t
    p123 = p12 + (p23 - p12) * t
    m = p012 + (p123 - p012) * t
    return np.array([b[0], p01, p012, m]), np.array([m, p123, p23, b[3]])


def bez_extrema_t(b):
    """Valores de t (0<t<1) onde x'(t)=0 ou y'(t)=0."""
    ts = []
    for k in (0, 1):
        p0, p1, p2, p3 = b[0][k], b[1][k], b[2][k], b[3][k]
        a = -p0 + 3 * p1 - 3 * p2 + p3
        bb = 2 * (p0 - 2 * p1 + p2)
        c = p1 - p0
        if abs(a) < 1e-12:
            if abs(bb) > 1e-12:
                ts.append(-c / bb)
        else:
            disc = bb * bb - 4 * a * c
            if disc >= 0:
                sq = math.sqrt(disc)
                ts.append((-bb + sq) / (2 * a))
                ts.append((-bb - sq) / (2 * a))
    return sorted(t for t in ts if 0.0 < t < 1.0)


def bez_length(b, n=24):
    pts = bez_pt(b, np.linspace(0, 1, n + 1))
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))


# ---------------------------------------------------------------- Hobby

def _hobby_f(theta, phi):
    st, ct = math.sin(theta), math.cos(theta)
    sp, cp = math.sin(phi), math.cos(phi)
    num = 2 + math.sqrt(2) * (st - sp / 16) * (sp - st / 16) * (ct - cp)
    den = 3 * (1 + 0.5 * (math.sqrt(5) - 1) * ct + 0.5 * (3 - math.sqrt(5)) * cp)
    return num / den


def hobby_controls(z0, a0, z1, a1, t0=1.0, t1=1.0):
    """Pontos de controle (algoritmo de Hobby/MetaPost) para um segmento
    de z0 (direção a0, rad) até z1 (direção a1, rad), com tensões t0, t1."""
    c = z1 - z0
    L = math.hypot(c[0], c[1])
    if L < EPS:
        return z0.copy(), z1.copy()
    ca = math.atan2(c[1], c[0])
    theta = norm_angle(a0 - ca)
    phi = norm_angle(ca - a1)
    ra = L * _hobby_f(theta, phi) / t0
    rb = L * _hobby_f(phi, theta) / t1
    p1 = z0 + ra * np.array([math.cos(a0), math.sin(a0)])
    p2 = z1 - rb * np.array([math.cos(a1), math.sin(a1)])
    return p1, p2


# ---------------------------------------------------------------- ajuste

def _bernstein(u):
    mt = 1 - u
    return mt ** 3, 3 * mt * mt * u, 3 * mt * u * u, u ** 3


def _gen_bezier(pts, u, tl, tr):
    p0, p3 = pts[0], pts[-1]
    b0, b1, b2, b3 = _bernstein(u)
    A1 = b1[:, None] * tl
    A2 = b2[:, None] * tr
    c00 = np.sum(A1 * A1)
    c01 = np.sum(A1 * A2)
    c11 = np.sum(A2 * A2)
    tmp = pts - (b0 + b1)[:, None] * p0 - (b2 + b3)[:, None] * p3
    x0 = np.sum(A1 * tmp)
    x1 = np.sum(A2 * tmp)
    det = c00 * c11 - c01 * c01
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        al = (x0 * c11 - x1 * c01) / det
        ar = (c00 * x1 - c01 * x0) / det
    else:
        al = ar = seg / 3
    eps = 1e-6 * seg
    if al < eps or ar < eps:
        al = ar = seg / 3
    return np.array([p0, p0 + tl * al, p3 + tr * ar, p3])


def _max_err(pts, bez, u):
    q = bez_pt(bez, u)
    d = np.sum((q - pts) ** 2, axis=1)
    i = int(np.argmax(d))
    return math.sqrt(d[i]), i


def _reparam(bez, pts, u):
    out = np.empty_like(u)
    for i, (p, t) in enumerate(zip(pts, u)):
        q = bez_pt(bez, t)
        q1 = bez_d1(bez, t)
        q2 = bez_d2(bez, t)
        num = np.dot(q - p, q1)
        den = np.dot(q1, q1) + np.dot(q - p, q2)
        out[i] = t if abs(den) < 1e-12 else t - num / den
    return np.clip(out, 0.0, 1.0)


def fit_points(pts, tl, tr, err=0.35):
    """Ajusta UMA cúbica aos pontos com tangentes fixas nas pontas.
    tl aponta para frente no início; tr aponta para trás no fim.
    Retorna (bezier, erro_max)."""
    d = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    if d[-1] < EPS:
        return np.array([pts[0], pts[0], pts[-1], pts[-1]]), 0.0
    u = d / d[-1]
    bez = _gen_bezier(pts, u, tl, tr)
    e, _ = _max_err(pts, bez, u)
    best = (e, bez)
    for _ in range(12):
        if e < err:
            break
        u = _reparam(bez, pts, u)
        bez = _gen_bezier(pts, u, tl, tr)
        e, _ = _max_err(pts, bez, u)
        if e < best[0]:
            best = (e, bez)
    return best[1], best[0]


def fit_function(f, t0, t1, err=0.35, n=28, depth=0, maxdepth=6):
    """Aproxima a curva paramétrica f(t), t em [t0,t1], por cúbicas.
    Tangentes nas pontas são obtidas numericamente."""
    ts = np.linspace(t0, t1, n)
    pts = np.array([f(t) for t in ts])
    tl = _num_tangent(f, t0, t0, t1, +1)
    tr = -_num_tangent(f, t1, t0, t1, -1)
    if np.linalg.norm(pts[-1] - pts[0]) < 0.05:
        return []
    bez, e = fit_points(pts, tl, tr, err)
    if e <= err or depth >= maxdepth:
        return [bez]
    tm = 0.5 * (t0 + t1)
    return (fit_function(f, t0, tm, err, n, depth + 1, maxdepth) +
            fit_function(f, tm, t1, err, n, depth + 1, maxdepth))


def _num_tangent(f, t, lo, hi, side):
    span = hi - lo
    for h in (1e-4, 1e-3, 1e-2):
        dh = h * span
        if side > 0:
            a, b = f(t), f(min(hi, t + dh))
        else:
            a, b = f(max(lo, t - dh)), f(t)
        v = b - a
        if np.linalg.norm(v) > 1e-9:
            return unit(v)
    a, b = f(lo), f(hi)
    return unit(b - a)


def line_intersect(p, d, q, e):
    """Interseção das retas p + s*d e q + t*e. Retorna ponto ou None."""
    den = d[0] * e[1] - d[1] * e[0]
    if abs(den) < 1e-9:
        return None
    w = q - p
    s = (w[0] * e[1] - w[1] * e[0]) / den
    return p + s * d
