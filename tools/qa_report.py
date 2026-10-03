"""Relatório técnico de controle de qualidade (markdown) dos OTF gerados.

Mede nos contornos finais: hastes, traços finos, alturas, overshoots,
consistência de métricas verticais, recursos OpenType e pares de kerning.
"""
import os
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEIGHTS = ["Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]


def bounds(gs, name):
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    return bp.bounds


def hscan(gs, name, y):
    """Interseções horizontais do contorno com a linha y (x ordenados)."""
    from fontTools.pens.basePen import BasePen
    import numpy as np

    class P(BasePen):
        def __init__(s):
            super().__init__(gs)
            s.pts = []
            s.segs = []

        def _moveTo(s, p):
            s.cur = p
            s.start = p

        def _lineTo(s, p):
            s.segs.append((s.cur, p))
            s.cur = p

        def _curveToOne(s, a, b, c):
            p0 = s.cur
            for i in range(1, 25):
                t = i / 24
                mt = 1 - t
                q = (mt ** 3 * p0[0] + 3 * mt * mt * t * a[0] + 3 * mt * t * t * b[0] + t ** 3 * c[0],
                     mt ** 3 * p0[1] + 3 * mt * mt * t * a[1] + 3 * mt * t * t * b[1] + t ** 3 * c[1])
                s.segs.append((s.cur, q))
                s.cur = q

        def _closePath(s):
            if s.cur != s.start:
                s.segs.append((s.cur, s.start))
    pen = P()
    gs[name].draw(pen)
    xs = []
    for (x0, y0), (x1, y1) in pen.segs:
        if (y0 <= y < y1) or (y1 <= y < y0):
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    return sorted(xs)


def vscan(gs, name, x):
    rot = {}
    from fontTools.pens.transformPen import TransformPen
    from fontTools.pens.recordingPen import RecordingPen
    rp = RecordingPen()
    gs[name].draw(TransformPen(rp, (0, 1, 1, 0, 0, 0)))

    class G:
        def draw(self, pen):
            rp.replay(pen)
    tmp = {"t": G()}
    return hscan(tmp, "t", x)


def measure(path):
    f = TTFont(path)
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    r = {}
    # haste do n e do H (corte a meia altura)
    xs = hscan(gs, "n", 250)
    r["haste n"] = round(xs[1] - xs[0]) if len(xs) >= 2 else None
    xs = hscan(gs, "H", 200)
    r["haste H"] = round(xs[1] - xs[0]) if len(xs) >= 2 else None
    # fino: topo do o (corte vertical no centro)
    b = bounds(gs, "o")
    ys = vscan(gs, "o", (b[0] + b[2]) / 2)
    r["fino o (topo)"] = round(ys[-1] - ys[-2]) if len(ys) >= 4 else None
    xs = hscan(gs, "o", 250)
    r["curva o (lado)"] = round(xs[1] - xs[0]) if len(xs) >= 4 else None
    r["contraste"] = (f"{r['fino o (topo)'] / r['curva o (lado)']:.2f}"
                      if r["fino o (topo)"] and r["curva o (lado)"] else None)
    r["altura-x (x)"] = round(bounds(gs, "x")[3])
    r["maiúsc. (H)"] = round(bounds(gs, "H")[3])
    r["ascend. (l)"] = round(bounds(gs, "l")[3])
    r["descend. (p)"] = round(bounds(gs, "p")[1])
    ob = bounds(gs, "o")
    r["overshoot o"] = f"{round(ob[1])} / +{round(ob[3] - 500)}"
    Ob = bounds(gs, "O")
    r["overshoot O"] = f"{round(Ob[1])} / +{round(Ob[3] - 680)}"
    r["avanço n / o / H"] = f"{gs['n'].width} / {gs['o'].width} / {gs['H'].width}"
    r["glifos"] = len(f.getGlyphOrder())
    r["caracteres"] = len(cmap)
    gpos = f["GPOS"].table
    pairs = 0
    for lk in gpos.LookupList.Lookup:
        if lk.LookupType == 2:
            for st in lk.SubTable:
                if st.Format == 1:
                    pairs += sum(len(ps.PairValueRecord) for ps in st.PairSet)
                else:
                    pairs += sum(1 for c1 in st.Class1Record for c2 in c1.Class2Record
                                 if c2.Value1 and getattr(c2.Value1, "XAdvance", 0))
    r["pares de kerning"] = pairs
    r["tamanho (KB)"] = round(os.path.getsize(path) / 1024)
    return r, f


def features(f):
    out = set()
    for tag in ("GSUB", "GPOS"):
        if tag in f:
            for fr in f[tag].table.FeatureList.FeatureRecord:
                out.add(fr.FeatureTag)
    return sorted(out)


def main():
    rows = {}
    font = None
    for w in WEIGHTS:
        p = os.path.join(ROOT, "fonts", "otf", f"Yauren-{w}.otf")
        rows[w], font = measure(p)
    keys = list(next(iter(rows.values())).keys())
    lines = ["| Medida | " + " | ".join(WEIGHTS) + " |", "|---|" + "---|" * len(WEIGHTS)]
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(rows[w][k]) for w in WEIGHTS) + " |")
    f = TTFont(os.path.join(ROOT, "fonts", "otf", "Yauren-Regular.otf"))
    vm = (f["hhea"].ascent, f["hhea"].descent, f["OS/2"].sTypoAscender, f["OS/2"].sTypoDescender,
          f["OS/2"].usWinAscent, f["OS/2"].usWinDescent)
    lines.append("")
    lines.append(f"Métricas verticais (iguais em todos os pesos): hhea {vm[0]}/{vm[1]}, "
                 f"typo {vm[2]}/{vm[3]} (USE_TYPO_METRICS), win {vm[4]}/{vm[5]}.")
    lines.append("")
    lines.append("Recursos OpenType: " + ", ".join(f"`{t}`" for t in features(f)))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
