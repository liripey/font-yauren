"""Vietnamita: gancho (hỏi), chifre (horn), marcas combinadas e compostos."""
import unicodedata

from ..glyph import Glyph, contours_bounds, transform_contours
from ..parts import ellipse, rect
from ..pen import Path, Pen, stroke
from ..registry import COMPOSITES, GLYPHS, borrow, composite, glyph
from . import lower as LC
from . import upper as UC
from .marks import M, MC, TOP_MARKS, f_acute, f_breve, f_circumflex, f_tilde


def stk(path, pen, cap0="butt", cap1="butt"):
    return stroke(path, pen, cap0, cap1)


def f_hook(m, dx=0.0, k=1.0):
    S, H = m.S, m.H
    h = m.hu * (0.78 if m.case else 0.88) * k * (1 + 0.10 * m.P.wf)
    w = h * (0.70 + 0.12 * m.P.wf)
    cx = m.cx + dx
    y0 = m.y0
    pen = Pen((S * 0.30 + 3) * (1 - 0.35 * m.P.wf), H * 0.52)
    p = Path(cx - w * 0.42, y0 + h * 0.70, d=90, w=0.55)
    p.c(cx + w * 0.02, y0 + h - pen.hv, d=0, w=1.0)
    p.c(cx + w * 0.42, y0 + h * 0.66, d=270, w=1.0)
    p.c(cx + w * 0.02, y0 + h * 0.36, d=225, w=0.7)
    p.c(cx, y0, d=270, w=0.5)
    return stk(p, pen), y0 + h


TOP_MARKS["hookabovecomb"] = (0x0309, f_hook)


def _mk_top(fn, case):
    def g_fn(g, P):
        m = M(P, case)
        sh, top = fn(m)
        g.add(sh)
        g.anchor("_top", m.cx, m.base)
        b = contours_bounds(sh)
        g.anchor("top", m.cx, b[3] - (m.y0 - m.base) + 30)
        g.space(width=0)
    return g_fn


glyph("hookabovecomb", 0x0309)(_mk_top(f_hook, False))
glyph("hookabovecomb.case")(_mk_top(f_hook, True))


# marcas combinadas (circunflexo/breve + tom)
TONES = {
    "acute": lambda m, dx, dy, k: _shift(f_acute(m, k=k)[0], dx, dy),
    "grave": lambda m, dx, dy, k: _shift(f_acute(m, flip=True, k=k)[0], dx, dy),
    "hook": lambda m, dx, dy, k: _shift(f_hook(m, k=k)[0], dx, dy),
    "tilde": lambda m, dx, dy, k: _shift(_scale_tilde(m, k), dx, dy),
}


def _shift(c, dx, dy):
    return transform_contours(c, dx=dx, dy=dy)


def _scale_tilde(m, k):
    sh, _ = f_tilde(m)
    b = contours_bounds(sh)
    cx = (b[0] + b[2]) / 2
    return transform_contours(sh, k, 0, 0, k, cx * (1 - k), b[1] * (1 - k))


def _combo(first, tone, case):
    def g_fn(g, P):
        m = M(P, case)
        if first == "circumflex":
            base, top = f_circumflex(m)
        else:
            base, top = f_breve(m)
        g.add(base)
        b = contours_bounds(base)
        w = b[2] - b[0]
        h = b[3] - b[1]
        if first == "circumflex" and tone in ("acute", "grave", "hook"):
            # tom à direita do circunflexo (convenção vietnamita)
            k = 0.82
            sh = TONES[tone](m, 0, 0, k)
            sb = contours_bounds(sh)
            dx = b[2] + 12 - sb[0] - w * 0.18
            dy = b[1] + h * 0.42 - sb[1]
            sh = _shift(sh, dx, dy)
        else:
            k = 0.80 if tone != "tilde" else 0.78
            sh = TONES[tone](m, 0, 0, k)
            sb = contours_bounds(sh)
            dx = (b[0] + b[2]) / 2 - (sb[0] + sb[2]) / 2
            dy = b[3] + (22 if case else 30) - sb[1]
            sh = _shift(sh, dx, dy)
        g.add(sh)
        g.anchor("_top", m.cx, m.base)
        bb = contours_bounds(base + sh)
        g.anchor("top", m.cx, bb[3] - (m.y0 - m.base) + 30)
        g.space(width=0)
    return g_fn


for _first in ("circumflex", "breve"):
    for _tone in ("acute", "grave", "hook", "tilde"):
        _n = f"{_first}comb_{_tone}comb"
        glyph(_n)(_combo(_first, _tone, False))
        glyph(_n + ".case")(_combo(_first, _tone, True))


# ------------------------------------------------------------- chifre

def horn_shape(P, x, y, size):
    S, H = P.stem, P.hair
    pen = Pen(S * 0.36, H * 0.55)
    r = LC.rbf(P, 0.36)
    p = Path(x - S * 0.3, y - size * 0.30, d=28, w=1.0)
    p.c(x + size * 0.42, y + size * 0.22, d=62, w=0.75)
    p.c(x + size * 0.52, y + size * 0.62, d=95, w=0.6)
    return stk(p, pen) + ellipse(x + size * 0.50 - r * 0.3, y + size * 0.62, r, r * 1.05)


@glyph("horncomb", 0x031B)
def horncomb(g, P):
    cx = MC(P) + LC.o_width(P) * 0.40
    g.add(horn_shape(P, cx, P.xh * 0.86, P.xh * 0.30))
    g.space(width=0)


def _horn(base, caps):
    def fn(g, P):
        c, t = borrow(base, P)
        b = contours_bounds(c)
        g.add(c)
        top = P.cap if caps else P.xh
        size = top * (0.24 if caps else 0.30)
        if base in ("O", "o"):
            x = b[2] - (P.curveC if caps else P.curve) * 0.30
            y = top * 0.86
        else:
            x = b[2] - (P.sfxC * 0.6 if caps else 0)
            y = top * 0.90
        g.add(horn_shape(P, x, y, size))
        for k, v in t.anchors.items():
            g.anchor(k, *v)
        g.space(t.lsb, (t.rsb or 0) * 0.6)
    return fn


glyph("Ohorn", 0x01A0)(_horn("O", True))
glyph("ohorn", 0x01A1)(_horn("o", False))
glyph("Uhorn", 0x01AF)(_horn("U", True))
glyph("uhorn", 0x01B0)(_horn("u", False))


# ------------------------------------------------------------- compostos

def _existing_unicodes():
    s = set()
    for n, (unis, f) in GLYPHS.items():
        s.update(unis)
    for n, (unis, b, m, o) in COMPOSITES.items():
        s.update(unis)
    return s


TONE_CH = {"grave": "̀", "acute": "́", "hook": "̉", "tilde": "̃",
           "dotb": "̣"}


def register():
    have = _existing_unicodes()
    bases = {"a": "a", "e": "e", "i": "dotlessi", "o": "o", "u": "u", "y": "y",
             "A": "A", "E": "E", "I": "I", "O": "O", "U": "U", "Y": "Y"}
    for v, gbase in bases.items():
        upper = v.isupper()
        suf = ".case" if upper else ""
        tops = [(None, "")]
        if v in "aAeEoO":
            tops.append(("circumflex", "̂"))
        if v in "aA":
            tops.append(("breve", "̆"))
        if v in "oOuU":
            tops.append(("horn", "̛"))
        for top, tch in tops:
            for tone, toch in [(None, "")] + list(TONE_CH.items()):
                seq = v + tch + toch
                nfc = unicodedata.normalize("NFC", seq)
                if len(nfc) != 1 or (top is None and tone is None):
                    continue
                cp = ord(nfc)
                if cp in have:
                    continue
                base = gbase
                marks = []
                if top == "horn":
                    base = v + "horn" if v.islower() else v + "horn"
                    base = {"o": "ohorn", "u": "uhorn", "O": "Ohorn", "U": "Uhorn"}[v]
                if top in ("circumflex", "breve"):
                    if tone in ("grave", "acute", "hook", "tilde"):
                        marks.append(f"{top}comb_{tone}comb{suf}")
                    else:
                        marks.append(f"{top}comb{suf}")
                if tone in ("grave", "acute", "hook", "tilde") and top not in ("circumflex", "breve"):
                    marks.append({"grave": "gravecomb", "acute": "acutecomb",
                                  "hook": "hookabovecomb", "tilde": "tildecomb"}[tone] + suf)
                if tone == "dotb":
                    marks.append("dotbelowcomb")
                name = "uni%04X" % cp
                composite(name, cp, base, marks)
                have.add(cp)


register()
