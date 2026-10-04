"""Auditoria geométrica: desalinhamentos, traços "quase" retos e assimetrias.

uso: python tools/audit.py fonte.otf [--sym]
"""
import sys

import numpy as np
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

ZONES = {"base": 0, "xh": 500, "cap": 680, "asc": 740, "desc": -235, "fig": 660}

# glifos cujo desenho deve ser espelhado (simetria esquerda/direita)
SYMMETRIC = ["o", "O", "zero", "zero.tf", "eight", "H", "I", "T", "X", "A", "V", "W", "Y", "M",
             "v", "w", "x", "i", "l", "dotlessi", "n", "u", "Theta", "Phi", "Omega", "Pi",
             "uni0416", "uni0428", "uni0436", "uni0448", "period", "colon", "exclam", "quotedbl",
             "quotesingle", "bullet", "periodcentered", "plus", "minus", "multiply", "divide",
             "equal", "asterisk", "bar", "degree", "circumflexcomb", "caroncomb", "brevecomb",
             "dieresiscomb", "macroncomb", "ringcomb", "dotaccentcomb", "circumflexcomb.case",
             "caroncomb.case", "brevecomb.case", "dieresiscomb.case", "macroncomb.case",
             "ringcomb.case", "dotaccentcomb.case", "notequal", "infinity", "lozenge",
             "product", "dagger", "daggerdbl", "uni041F", "uni0418"]


def segments(gs, name):
    rp = DecomposingRecordingPen(gs)
    gs[name].draw(rp)
    out = []
    cur = start = None
    for op, args in rp.value:
        if op == "moveTo":
            cur = start = args[0]
        elif op == "lineTo":
            out.append(("l", cur, args[0]))
            cur = args[0]
        elif op == "curveTo":
            out.append(("c", cur) + tuple(args))
            cur = args[-1]
        elif op == "closePath":
            if cur != start:
                out.append(("l", cur, start))
    return out


def check_lines(gs, name):
    """Linhas quase verticais/horizontais e alças quase alinhadas."""
    issues = []
    for s in segments(gs, name):
        if s[0] == "l":
            (x0, y0), (x1, y1) = s[1], s[2]
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            if 0 < dx <= 3 and dy > 25:
                issues.append(f"quase-vertical dx={dx:.0f} em ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
            if 0 < dy <= 3 and dx > 25:
                issues.append(f"quase-horizontal dy={dy:.0f} em ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})")
        else:
            p0, c1, c2, p3 = s[1:]
            for a, b in ((p0, c1), (p3, c2)):
                dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
                if 0 < dy <= 2 and dx > 20:
                    issues.append(f"alça quase-horizontal dy={dy:.0f} em ({a[0]:.0f},{a[1]:.0f})")
                if 0 < dx <= 2 and dy > 20:
                    issues.append(f"alça quase-vertical dx={dx:.0f} em ({a[0]:.0f},{a[1]:.0f})")
    return issues


def check_zones(gs, name, os_lc=12, os_uc=14):
    """Nós a 1–3 unidades das linhas de referência (ou dos overshoots)."""
    targets = set()
    for v in ZONES.values():
        targets.add(v)
    for v in (-os_lc, 500 + os_lc, -os_uc, 680 + os_uc):
        targets.add(v)
    issues = []
    pts = set()
    for s in segments(gs, name):
        pts.add(tuple(s[1]))
        pts.add(tuple(s[-1]))
    for (x, y) in pts:
        if y in targets:
            continue
        for t in targets:
            if 0 < abs(y - t) <= 2:
                issues.append(f"y={y:.0f} perto de {t}")
    return sorted(set(issues))


def _edges(gs, name):
    edges = []
    for s in segments(gs, name):
        if s[0] == "l":
            pts = [s[1], s[2]]
        else:
            p0, c1, c2, p3 = [np.array(p, float) for p in s[1:]]
            ts = np.linspace(0, 1, 24)
            pts = [tuple(((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * c1 + 3 * (1 - t) * t * t * c2
                         + t ** 3 * p3) for t in ts]
        edges += list(zip(pts[:-1], pts[1:]))
    return edges


def coverage(edges, xs, y):
    """Cobertura par-ímpar nos pontos xs da linha y."""
    cuts = []
    for (ax, ay), (bx, by) in edges:
        if (ay <= y < by) or (by <= y < ay):
            cuts.append(ax + (y - ay) * (bx - ax) / (by - ay))
    cuts.sort()
    inside = np.zeros(len(xs), dtype=bool)
    for k in range(0, len(cuts) - 1, 2):
        inside |= (xs >= cuts[k]) & (xs < cuts[k + 1])
    return inside


def symmetry_error(gs, name, step=2.0, axis=None):
    """Fração da tinta que não coincide com o espelho em torno do eixo
    (centro da caixa, ou 'axis' dado)."""
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    if not bp.bounds:
        return None
    x0, y0, x1, y1 = bp.bounds
    cx = (x0 + x1) / 2 if axis is None else axis
    half = max(cx - x0, x1 - cx) + 4
    off = np.arange(step / 2 + 0.37, half, step)  # evita amostrar exatamente sobre arestas inteiras
    xs_r = cx + off
    xs_l = cx - off
    edges = _edges(gs, name)
    diff = ink = 0
    for y in np.arange(y0 + step / 2 + 0.37, y1, step):
        a = coverage(edges, xs_l, y)
        b = coverage(edges, xs_r, y)
        diff += np.logical_xor(a, b).sum()
        ink += a.sum() + b.sum()
    return diff / max(ink, 1)


def main():
    path = sys.argv[1]
    f = TTFont(path)
    gs = f.getGlyphSet()
    order = f.getGlyphOrder()
    n_line = n_zone = 0
    print(f"== {path}")
    for name in order:
        li = check_lines(gs, name)
        zi = check_zones(gs, name)
        if li or zi:
            n_line += len(li)
            n_zone += len(zi)
            print(f"{name}: " + "; ".join(li + zi))
    print(f"-- {n_line} problemas de retidão, {n_zone} de alinhamento")
    if "--sym" in sys.argv:
        hmtx = f["hmtx"].metrics
        print("== simetria (xor espelhado / tinta) e lsb/rsb")
        from fontTools.pens.boundsPen import BoundsPen
        for name in SYMMETRIC:
            if name not in gs:
                continue
            e = symmetry_error(gs, name)
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            adv = hmtx[name][0]
            lsb = bp.bounds[0] if bp.bounds else 0
            rsb = adv - bp.bounds[2] if bp.bounds else 0
            flag = " <<" if e is not None and e > 0.02 else ""
            print(f"{name:22s} assim={e:.3f} lsb={lsb:.0f} rsb={rsb:.0f}{flag}")


if __name__ == "__main__":
    main()
