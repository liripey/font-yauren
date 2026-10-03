"""Gera provas (PNG) a partir dos OTF: texto em vários corpos e glifos ampliados.

uso: python tools/proof.py fonte.otf saida.png "texto" [--sizes 12,16,24,48] [--outline glifos]
"""
import argparse

import freetype
import numpy as np
import uharfbuzz as hb
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont


def shape(font_path, text, features=None):
    blob = hb.Blob.from_file_path(font_path)
    face = hb.Face(blob)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, features or {})
    return buf.glyph_infos, buf.glyph_positions, face.upem


def render_line(font_path, text, px, features=None, color=0, hinting=False):
    infos, poss, upem = shape(font_path, text, features)
    face = freetype.Face(font_path)
    face.set_char_size(int(px * 64))
    scale = px / upem
    flags = freetype.FT_LOAD_RENDER | (0 if hinting else freetype.FT_LOAD_NO_HINTING)
    asc = int(px * 1.0)
    h = int(px * 1.35) + 4
    width = int(sum(p.x_advance for p in poss) * scale) + int(px) + 4
    img = np.zeros((h, max(width, 4)), dtype=np.float32)
    pen_x = 2.0
    base = asc
    for info, pos in zip(infos, poss):
        face.load_glyph(info.codepoint, flags)
        bm = face.glyph.bitmap
        if bm.width and bm.rows:
            arr = np.array(bm.buffer, dtype=np.float32).reshape(bm.rows, bm.pitch)[:, :bm.width] / 255.0
            x = int(round(pen_x + pos.x_offset * scale)) + face.glyph.bitmap_left
            y = base - int(round(pos.y_offset * scale)) - face.glyph.bitmap_top
            x0, y0 = max(x, 0), max(y, 0)
            x1, y1 = min(x + bm.width, img.shape[1]), min(y + bm.rows, img.shape[0])
            if x1 > x0 and y1 > y0:
                img[y0:y1, x0:x1] = np.maximum(img[y0:y1, x0:x1], arr[y0 - y:y1 - y, x0 - x:x1 - x])
        pen_x += pos.x_advance * scale
    out = (255 * (1 - img)).astype(np.uint8)
    return Image.fromarray(out[:, : int(pen_x) + 4])


def text_proof(fonts, lines, sizes, out, features=None, label=True, width=None):
    rows = []
    lab_font = ImageFont.load_default()
    for fp in fonts:
        for px in sizes:
            for t in lines:
                im = render_line(fp, t, px, features)
                rows.append((f"{fp.split('/')[-1]}  {px}px", im))
    W = width or max(r[1].width for r in rows) + 20
    H = sum(r[1].height + (14 if label else 2) for r in rows) + 20
    page = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(page)
    y = 10
    for lab, im in rows:
        if label:
            d.text((10, y), lab, fill=150, font=lab_font)
            y += 12
        page.paste(im, (10, y))
        y += im.height + 2
    page.save(out)
    return out


def outline_proof(font_path, names, out, px=420, cols=4, show_points=True):
    """Glifos ampliados com contorno, nós (on-curve) e alças (off-curve)."""
    f = TTFont(font_path)
    gs = f.getGlyphSet()
    upem = f["head"].unitsPerEm
    scale = px / upem
    margin = 30
    cell_w = 0
    widths = [gs[n].width for n in names]
    cell_w = int(max(widths) * scale) + 2 * margin
    cell_h = int(1300 * scale) + 2 * margin
    rows = (len(names) + cols - 1) // cols
    page = Image.new("RGB", (cell_w * cols, cell_h * rows), "white")
    d = ImageDraw.Draw(page)
    face = freetype.Face(font_path)
    face.set_char_size(int(px * 64))
    order = f.getGlyphOrder()
    for i, n in enumerate(names):
        cx = (i % cols) * cell_w + margin
        cy = (i // cols) * cell_h + margin
        base = cy + int(1000 * scale)

        def T(p):
            return (cx + p[0] * scale, base - p[1] * scale)
        # métricas
        for yv, col in ((0, (200, 120, 120)), (500, (120, 160, 220)), (680, (120, 200, 120)),
                        (740, (200, 180, 90)), (-235, (200, 180, 90))):
            d.line([T((0, yv)), T((gs[n].width, yv))], fill=col, width=1)
        d.line([T((0, -300)), T((0, 950))], fill=(180, 180, 180))
        d.line([T((gs[n].width, -300)), T((gs[n].width, 950))], fill=(180, 180, 180))
        # preenchimento via freetype
        gid = order.index(n)
        face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        bm = face.glyph.bitmap
        if bm.width:
            arr = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)[:, :bm.width]
            x = int(cx) + face.glyph.bitmap_left
            y = base - face.glyph.bitmap_top
            tint = Image.new("RGB", (bm.width, bm.rows), (225, 225, 232))
            mask = Image.fromarray(arr)
            page.paste(tint, (x, y), mask)
        if show_points:
            rp = RecordingPen()
            gs[n].draw(rp)
            cur = None
            for op, args in rp.value:
                if op == "moveTo":
                    cur = args[0]
                    d.ellipse([T(cur)[0] - 3, T(cur)[1] - 3, T(cur)[0] + 3, T(cur)[1] + 3], fill=(200, 40, 40))
                elif op == "lineTo":
                    d.line([T(cur), T(args[0])], fill=(20, 20, 20), width=1)
                    cur = args[0]
                    d.rectangle([T(cur)[0] - 2, T(cur)[1] - 2, T(cur)[0] + 2, T(cur)[1] + 2], fill=(30, 30, 200))
                elif op == "curveTo":
                    p1, p2, p3 = args
                    pts = []
                    for t in np.linspace(0, 1, 30):
                        mt = 1 - t
                        pts.append(tuple(mt ** 3 * np.array(cur) + 3 * mt * mt * t * np.array(p1) +
                                         3 * mt * t * t * np.array(p2) + t ** 3 * np.array(p3)))
                    d.line([T(p) for p in pts], fill=(20, 20, 20), width=1)
                    d.line([T(cur), T(p1)], fill=(150, 150, 220))
                    d.line([T(p3), T(p2)], fill=(150, 150, 220))
                    for q in (p1, p2):
                        d.ellipse([T(q)[0] - 2, T(q)[1] - 2, T(q)[0] + 2, T(q)[1] + 2], outline=(90, 90, 200))
                    cur = p3
                    d.ellipse([T(cur)[0] - 2.5, T(cur)[1] - 2.5, T(cur)[0] + 2.5, T(cur)[1] + 2.5], fill=(30, 30, 200))
        d.text((cx, cy - 20), f"{n}  w={gs[n].width}", fill=(80, 80, 80))
    page.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonts", nargs="+")
    ap.add_argument("--out", default="proof.png")
    ap.add_argument("--text", action="append")
    ap.add_argument("--sizes", default="14,24,48")
    ap.add_argument("--outline")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--px", type=int, default=420)
    a = ap.parse_args()
    if a.outline:
        outline_proof(a.fonts[0], a.outline.split(","), a.out, px=a.px, cols=a.cols)
    else:
        text_proof(a.fonts, a.text or ["Hamburgefonstiv"], [int(s) for s in a.sizes.split(",")], a.out)
