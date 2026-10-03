"""Montagem dos arquivos OTF (CFF) da família Yauren."""
import importlib
import math
import os
import sys

import numpy as np
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen

from .glyph import Glyph, cleanup, contours_bounds, transform_contours
from .params import WEIGHTS, Params
from .registry import COMPOSITES, GLYPHS

FAMILY = "Yauren"
VERSION = "1.000"
VENDOR = "YAUR"
GLYPH_MODULES = ["lower", "upper", "figures", "punct", "marks", "extra", "symbols", "alts",
                 "greek", "cyrillic", "composites", "vietnamese"]


def load_modules():
    for m in GLYPH_MODULES:
        importlib.import_module(f".glyphs.{m}", __package__)


# --------------------------------------------------------------- glifos

class Built:
    __slots__ = ("name", "unicodes", "contours", "width", "anchors", "lsb_x")

    def __init__(self, name, unicodes, contours, width, anchors):
        self.name = name
        self.unicodes = unicodes
        self.contours = contours
        self.width = width
        self.anchors = anchors


def _place(g):
    """Aplica o espaçamento: desloca contornos e âncoras, define avanço."""
    b = contours_bounds(g.contours) if g.contours else None
    dx = 0.0
    if g.width is not None and g.lsb is None and g.rsb is None and not g.center:
        width = g.width          # posição fixa (marcas combinantes)
    elif g.width is not None and (g.center or b is None):
        width = g.width
        if b is not None:
            dx = round((width - (b[2] - b[0])) / 2 - b[0])
    elif b is not None:
        lsb = g.lsb if g.lsb is not None else 0
        rsb = g.rsb if g.rsb is not None else 0
        dx = round(lsb - b[0])
        width = round(b[2] + dx + rsb)
        if g.width is not None:
            width = g.width
    else:
        width = g.width or 0
    contours = transform_contours(g.contours, dx=dx) if dx else g.contours
    anchors = {k: (v[0] + dx, v[1]) for k, v in g.anchors.items()}
    return contours, int(round(width)), anchors


def build_glyph(name, P):
    unis, f = GLYPHS[name]
    g = Glyph(name, unis)
    f(g, P)
    g.solve()
    g.contours = cleanup(g.contours)
    contours, width, anchors = _place(g)
    # arredonda novamente após deslocamento (dx inteiro mantém inteiros)
    return Built(name, unis, contours, width, anchors)


def default_anchor(b, key, P):
    bb = contours_bounds(b.contours) if b.contours else (0, 0, b.width, 0)
    cx = (bb[0] + bb[2]) / 2
    upper = b.name[:1].isupper()
    if key == "top":
        return (cx, P.cap if upper else (P.asc if bb[3] > P.xh + 150 else P.xh))
    if key in ("bottom", "cedilla"):
        if key == "cedilla" and "bottom" in b.anchors:
            return b.anchors["bottom"]
        return (cx, 0)
    if key == "ogonek":
        return (bb[2] - P.stem * 0.45, 0)
    if key == "topright":
        return (bb[2], P.asc)
    return (cx, 0)


MARK_KEYS = ["top", "bottom", "ogonek", "cedilla", "topright"]


def build_composite(name, built, P):
    from .glyph import clip, contours_to_skpath, skpath_to_contours
    import pathops
    unis, base, marks, opts = COMPOSITES[name]
    B = built[base]
    shapes = [B.contours]
    anchors = dict(B.anchors)
    for mk in marks:
        M = built[mk]
        key = next(k for k in MARK_KEYS if "_" + k in M.anchors)
        ba = anchors.get(key) or default_anchor(B, key, P)
        ma = M.anchors["_" + key]
        dx, dy = round(ba[0] - ma[0]), round(ba[1] - ma[1])
        shapes.append(transform_contours(M.contours, dx=dx, dy=dy))
        if key in M.anchors:
            anchors[key] = (M.anchors[key][0] + dx, M.anchors[key][1] + dy)
    from .glyph import union_all
    res = union_all(shapes)
    return Built(name, unis, cleanup(res), B.width, anchors)


def build_all(P, only=None):
    load_modules()
    out = {}
    names = list(GLYPHS) if only is None else [n for n in GLYPHS if n in only]
    for name in names:
        try:
            out[name] = build_glyph(name, P)
        except Exception as e:  # pragma: no cover - diagnóstico
            raise RuntimeError(f"falha no glifo {name}: {e}") from e
    for name in COMPOSITES:
        if only is not None and name not in only:
            continue
        try:
            out[name] = build_composite(name, out, P)
        except Exception as e:  # pragma: no cover
            raise RuntimeError(f"falha no composto {name}: {e}") from e
    return out


# --------------------------------------------------------------- fonte

def _charstring(b):
    pen = T2CharStringPen(b.width, None)
    for c in b.contours:
        if not c:
            continue
        pen.moveTo(tuple(int(v) for v in c[0][1]))
        for s in c:
            if s[0] == "l":
                pen.lineTo(tuple(int(v) for v in s[2]))
            else:
                pen.curveTo(tuple(int(v) for v in s[2]), tuple(int(v) for v in s[3]),
                            tuple(int(v) for v in s[4]))
        pen.closePath()
    return pen.getCharString()


def _private(P):
    r = lambda v: int(round(v))
    blues = [-r(P.os), 0, r(P.xh), r(P.xh + P.os), r(P.fig), r(P.fig + 10), r(P.cap),
             r(P.cap + P.osC), r(P.asc), r(P.asc + 12)]
    return {"BlueValues": blues,
            "OtherBlues": [r(P.desc) - 12, r(P.desc)],
            "StdHW": r(P.hair), "StdVW": r(P.stem),
            "StemSnapH": sorted({r(P.hair), r(P.hairC)}),
            "StemSnapV": sorted({r(P.stem), r(P.stemC)}),
            "BlueScale": 0.039625, "BlueShift": 7, "BlueFuzz": 0}


COPYRIGHT = "Copyright 2026 Yauren. Todos os direitos reservados."
LICENSE = ("Fonte proprietária de uso exclusivo da Yauren e de seu laboratório de pesquisa. "
           "Proibida a redistribuição, venda ou sublicenciamento sem autorização por escrito.")
DESCRIPTION = ("Yauren é uma família serifada humanista para leitura contínua e "
               "comunicação científica: altura-x generosa, aberturas amplas, contraste "
               "moderado e espaçamento confortável.")

PANOSE_WEIGHT = {300: 4, 400: 5, 500: 6, 600: 7, 700: 8, 800: 9, 900: 10}


def glyph_order(glyphs):
    enc = sorted((n for n, b in glyphs.items() if b.unicodes and n != ".notdef"),
                 key=lambda n: glyphs[n].unicodes[0])
    unenc = sorted(n for n, b in glyphs.items() if not b.unicodes and n != ".notdef")
    return [".notdef"] + enc + unenc


def make_font(P, style, glyphs, path, features=None, vmetrics=None):
    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    order = glyph_order(glyphs)
    fb = FontBuilder(1000, isTTF=False)
    fb.setupGlyphOrder(order)
    cmap = {}
    for n in order:
        for u in glyphs[n].unicodes:
            cmap[u] = n
    fb.setupCharacterMap(cmap)

    charstrings = {}
    metrics = {}
    for n in order:
        b = glyphs[n]
        charstrings[n] = _charstring(b)
        bb = contours_bounds(b.contours) if b.contours else None
        metrics[n] = (b.width, int(math.floor(bb[0])) if bb else 0)

    ribbi = P.weight in (400, 700)
    fam_name = FAMILY if ribbi else f"{FAMILY} {style}"
    sub_name = style if ribbi else "Regular"
    ps_name = f"{FAMILY}-{style}"
    ul_pos = -125
    ul_thk = 55
    fb.setupCFF(
        ps_name,
        {"FullName": f"{FAMILY} {style}", "FamilyName": FAMILY, "Weight": style,
         "version": VERSION, "Notice": COPYRIGHT, "isFixedPitch": False,
         "ItalicAngle": 0, "UnderlinePosition": ul_pos, "UnderlineThickness": ul_thk},
        charstrings,
        _private(P),
    )
    fb.setupHorizontalMetrics(metrics)
    vm = vmetrics or {"asc": 960, "desc": -300, "winAsc": 1000, "winDesc": 320}
    fb.setupHorizontalHeader(ascent=vm["asc"], descent=vm["desc"], lineGap=0)
    names = {
        "copyright": COPYRIGHT,
        "familyName": fam_name,
        "styleName": sub_name,
        "uniqueFontIdentifier": f"{VERSION};{VENDOR};{ps_name}",
        "fullName": f"{FAMILY} {style}",
        "version": f"Version {VERSION}",
        "psName": ps_name,
        "manufacturer": "Yauren",
        "designer": "Yauren",
        "description": DESCRIPTION,
        "licenseDescription": LICENSE,
    }
    if not ribbi:
        names["typographicFamily"] = FAMILY
        names["typographicSubfamily"] = style
    fb.setupNameTable(names, mac=False)
    fs_sel = (1 << 7)  # USE_TYPO_METRICS
    fs_sel |= (1 << 5) if P.weight == 700 else (1 << 6)
    panose = Panose()
    panose.bFamilyType = 2
    panose.bSerifStyle = 2
    panose.bWeight = PANOSE_WEIGHT.get(P.weight, 5)
    panose.bProportion = 3
    panose.bContrast = 4
    panose.bStrokeVariation = 2
    panose.bArmStyle = 2
    panose.bLetterForm = 2
    panose.bMidline = 2
    panose.bXHeight = 4
    fb.setupOS2(version=4, sTypoAscender=vm["asc"], sTypoDescender=vm["desc"], sTypoLineGap=0,
                usWinAscent=vm["winAsc"], usWinDescent=vm["winDesc"],
                sxHeight=P.xh, sCapHeight=P.cap, usWeightClass=P.weight, usWidthClass=5,
                achVendID=VENDOR, fsType=0, fsSelection=fs_sel, panose=panose,
                ySubscriptXSize=600, ySubscriptYSize=600, ySubscriptYOffset=140,
                ySuperscriptXSize=600, ySuperscriptYSize=600, ySuperscriptYOffset=420,
                yStrikeoutSize=ul_thk, yStrikeoutPosition=int(P.xh * 0.52),
                usDefaultChar=0, usBreakChar=32, usMaxContext=4)
    fb.setupPost(italicAngle=0, underlinePosition=ul_pos, underlineThickness=ul_thk,
                 isFixedPitch=0)
    if features:
        fb.addOpenTypeFeatures(features)
    font = fb.font
    font["head"].fontRevision = float(VERSION)
    font["head"].macStyle = 1 if P.weight == 700 else 0
    font["OS/2"].recalcUnicodeRanges(font)
    font["OS/2"].recalcCodePageRanges(font)
    fb.save(path)
    return path


def _work(w):
    P = Params(w)
    gl = build_all(P)
    from .features import build_features
    fea = build_features(gl, P)
    return w, gl, fea


def family_vmetrics(results):
    ymax, ymin = 0, 0
    for w, gl, fea in results:
        for b in gl.values():
            if b.contours:
                bb = contours_bounds(b.contours)
                ymax = max(ymax, bb[3])
                ymin = min(ymin, bb[1])
    return {"asc": 960, "desc": -300, "winAsc": int(math.ceil(max(ymax, 960))) + 2,
            "winDesc": int(math.ceil(max(-ymin, 300))) + 2}


def main(argv=None):
    from multiprocessing import Pool
    argv = argv if argv is not None else sys.argv[1:]
    weights = [int(a) for a in argv if a.isdigit()] or [w for w, _ in WEIGHTS]
    names = dict(WEIGHTS)
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts", "otf"))
    os.makedirs(out_dir, exist_ok=True)
    if len(weights) > 1:
        with Pool(min(len(weights), os.cpu_count() or 2)) as pool:
            results = pool.map(_work, weights)
    else:
        results = [_work(weights[0])]
    vm = family_vmetrics(results)
    fea_dir = os.path.join(os.path.dirname(__file__), "..", "build")
    os.makedirs(fea_dir, exist_ok=True)
    for w, gl, fea in results:
        with open(os.path.join(fea_dir, f"{names[w]}.fea"), "w") as fh:
            fh.write(fea)
        out = make_font(Params(w), names[w], gl, os.path.join(out_dir, f"{FAMILY}-{names[w]}.otf"),
                        features=fea, vmetrics=vm)
        print("ok", out, len(gl), "glifos")
    # hinting PostScript (afdko otfautohint) + WOFF2 para web
    import shutil
    import subprocess
    web_dir = os.path.join(out_dir, "..", "webfonts")
    os.makedirs(web_dir, exist_ok=True)
    for w, _, _ in results:
        path = os.path.join(out_dir, f"{FAMILY}-{names[w]}.otf")
        if shutil.which("otfautohint") and "--no-hint" not in argv:
            subprocess.run(["otfautohint", path], check=True, capture_output=True)
        from fontTools.ttLib import TTFont
        f = TTFont(path)
        f.flavor = "woff2"
        f.save(os.path.join(web_dir, f"{FAMILY}-{names[w]}.woff2"))


if __name__ == "__main__":
    main()
