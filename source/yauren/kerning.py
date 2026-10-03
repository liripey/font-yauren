"""Kerning automático por perfis ópticos.

Para cada glifo calculam-se os perfis esquerdo/direito em linhas de
varredura. O valor de um par combina:
  1. área de branco média entre os perfis (limitada em profundidade),
     comparada com a referência 'nn' / 'HH' (equal-area spacing);
  2. uma restrição de distância mínima (evita colisões e aproximações
     excessivas, inclusive com acentos).
Só são kernados pares em que ao menos um lado é "aberto" (diagonais,
braços, pontuação), preservando o espaçamento desenhado das formas retas
e redondas.
"""
import unicodedata

import numpy as np

from .geom import bez_pt
from .registry import COMPOSITES

STEP = 10
YS = np.arange(-320, 1000, STEP) + STEP / 2

OPEN_UC = set("AFJKLPRTVWXYZ")
OPEN_LC = set("fkrtvwxyzj")
OPEN_PUNCT = {"period", "comma", "quoteleft", "quoteright", "quotedblleft", "quotedblright",
              "quotesingle", "quotedbl", "hyphen", "endash", "emdash", "guilsinglleft",
              "guilsinglright", "guillemotleft", "guillemotright", "parenleft", "parenright",
              "bracketleft", "bracketright", "braceleft", "braceright", "slash", "ellipsis",
              "quotesinglbase", "quotedblbase", "one", "four", "seven", "colon", "semicolon",
              "asterisk", "question", "exclam", "periodcentered"}

BASE_LETTERS = [chr(c) for c in range(0x41, 0x5B)] + [chr(c) for c in range(0x61, 0x7B)]
BASE_OTHER = ["germandbls", "ae", "oe", "AE", "OE", "eth", "thorn", "Thorn", "dotlessi",
              "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def _flatten(contours, n=12):
    edges = []
    for c in contours:
        for s in c:
            if s[0] == "l":
                edges.append((s[1][0], s[1][1], s[2][0], s[2][1]))
            else:
                b = np.array(s[1:])
                pts = bez_pt(b, np.linspace(0, 1, n + 1))
                for p, q in zip(pts[:-1], pts[1:]):
                    edges.append((p[0], p[1], q[0], q[1]))
    return np.array(edges) if edges else np.zeros((0, 4))


def profile(b):
    E = _flatten(b.contours)
    L = np.full(len(YS), np.nan)
    R = np.full(len(YS), np.nan)
    if len(E) == 0:
        return L, R
    y0 = np.minimum(E[:, 1], E[:, 3])
    y1 = np.maximum(E[:, 1], E[:, 3])
    for i, y in enumerate(YS):
        # amostra três linhas dentro da faixa
        xs_all = []
        for yy in (y - STEP * 0.4, y, y + STEP * 0.4):
            m = (y0 <= yy) & (y1 > yy)
            if m.any():
                e = E[m]
                xs = e[:, 0] + (yy - e[:, 1]) * (e[:, 2] - e[:, 0]) / (e[:, 3] - e[:, 1])
                xs_all.append(xs)
        if xs_all:
            xs = np.concatenate(xs_all)
            L[i] = xs.min()
            R[i] = xs.max()
    return L, R


class Prof:
    def __init__(self, b):
        self.L, self.R = profile(b)
        self.w = b.width


def avg_gap(pa, pb, capd):
    g = (pa.w - pa.R) + pb.L
    m = ~np.isnan(g)
    if not m.any():
        return None
    return float(np.mean(np.minimum(g[m], capd)))


def min_kern(pa, pb, dmin):
    """Menor kern (mais negativo permitido) que mantém distância >= dmin."""
    ia = np.where(~np.isnan(pa.R))[0]
    ib = np.where(~np.isnan(pb.L))[0]
    if len(ia) == 0 or len(ib) == 0:
        return -1e9
    ya, yb = YS[ia], YS[ib]
    dy = yb[None, :] - ya[:, None]
    ok = np.abs(dy) < dmin
    if not ok.any():
        return -1e9
    need = np.sqrt(np.maximum(dmin ** 2 - dy ** 2, 0)) + pa.R[ia][:, None] - pa.w - pb.L[ib][None, :]
    return float(np.max(np.where(ok, need, -1e9)))


def is_open(name):
    base = name.split(".")[0]
    if base in OPEN_PUNCT:
        return True
    if len(base) == 1 and (base in OPEN_UC or base in OPEN_LC):
        return True
    return False


def kind(name):
    ch = name[:1]
    if len(name.split(".")[0]) == 1:
        return "uc" if ch.isupper() else "lc"
    if name in ("AE", "OE", "Thorn"):
        return "uc"
    return "lc"


def side_kind(name):
    base = name.split(".")[0]
    if base in OPEN_PUNCT and base not in ("one", "four", "seven"):
        return "p"
    if base in ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"):
        return "f"
    return kind(name)


ALLOWED = {("uc", "uc"), ("uc", "lc"), ("lc", "lc"), ("f", "f"), ("f", "p"), ("p", "f"),
           ("uc", "p"), ("lc", "p"), ("p", "uc"), ("p", "lc"), ("p", "p")}


def compute_kerning(gl, P, k_area=0.62, thresh=12):
    """Retorna (famílias, pares_base, exceções).
    famílias: base -> lista de membros (base + acentuados)."""
    profs = {}

    def prof(n):
        if n not in profs:
            profs[n] = Prof(gl[n])
        return profs[n]

    ref = {}
    for key, (a, b) in {"lc": ("n", "n"), "uc": ("H", "H"), "mix": ("H", "n")}.items():
        ref[key] = avg_gap(prof(a), prof(b), 1e9)
    capd = ref["lc"] * 2.0
    dmin = P.sb * 2 * 0.56
    kmax = P.cn * 0.42

    bases = [n for n in BASE_LETTERS + BASE_OTHER if n in gl]
    bases += [n for n in sorted(OPEN_PUNCT) if n in gl and n not in bases]
    pairs = {}
    for a in bases:
        for b in bases:
            if not (is_open(a) or is_open(b)):
                continue
            if (side_kind(a), side_kind(b)) not in ALLOWED:
                continue
            pa, pb = prof(a), prof(b)
            g = avg_gap(pa, pb, capd)
            ka, kb = kind(a), kind(b)
            r = ref["uc"] if (ka == "uc" and kb == "uc") else (ref["lc"] if ka == kb == "lc" else ref["mix"])
            kv = 0.0 if g is None else (r - g) * k_area
            kv = max(kv, -kmax)
            kmin = min_kern(pa, pb, dmin)
            if kv > 0 and kmin <= 0:
                kv = 0.0
            kv = max(kv, kmin)
            kv = int(round(kv / 2.0) * 2)
            if abs(kv) >= thresh:
                pairs[(a, b)] = kv

    from .registry import ALIASES
    fam = {b: [b] for b in bases}
    for n, src in ALIASES.items():
        if n in gl and src in fam:
            fam[src].append(n)
    for n, (unis, base, marks, opts) in COMPOSITES.items():
        base = ALIASES.get(base, base)
        root = {"dotlessi": "i", "dotlessj": "j"}.get(base, base)
        if n in gl and root in fam:
            fam[root].append(n)
    exceptions = {}
    for (a, b), kv in pairs.items():
        for A in fam[a]:
            for B in fam[b]:
                if A == a and B == b:
                    continue
                kmin = min_kern(prof(A), prof(B), dmin)
                v = max(kv, kmin)
                v = int(round(v / 2.0) * 2)
                if v != kv:
                    exceptions[(A, B)] = v if abs(v) >= thresh or kv != 0 else 0
    return fam, pairs, exceptions
