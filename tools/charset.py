"""Quadro com todos os glifos de uma fonte (controle visual)."""
import sys

import freetype
import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont


def chart(path, out, cell=72, px=46, cols=24, start=0, count=None):
    f = TTFont(path)
    order = f.getGlyphOrder()
    names = order[start:start + count] if count else order[start:]
    face = freetype.Face(path)
    face.set_char_size(px * 64)
    rows = (len(names) + cols - 1) // cols
    img = Image.new("L", (cols * cell, rows * (cell + 12)), 255)
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()
    base = int(cell * 0.70)
    for i, n in enumerate(names):
        x0 = (i % cols) * cell
        y0 = (i // cols) * (cell + 12)
        d.rectangle([x0, y0, x0 + cell - 1, y0 + cell + 11], outline=225)
        gid = order.index(n)
        face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        bm = face.glyph.bitmap
        adv = face.glyph.advance.x / 64
        ox = x0 + int((cell - adv) / 2)
        d.line([ox, y0 + base, ox + adv, y0 + base], fill=200)
        if bm.width:
            arr = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)[:, :bm.width]
            g = Image.fromarray(255 - arr)
            mask = Image.fromarray(arr)
            img.paste(0, (ox + face.glyph.bitmap_left, y0 + base - face.glyph.bitmap_top), mask)
        d.text((x0 + 2, y0 + cell - 2), n[:12], fill=120, font=fnt)
    img.save(out)


if __name__ == "__main__":
    chart(sys.argv[1], sys.argv[2], start=int(sys.argv[3]) if len(sys.argv) > 3 else 0,
          count=int(sys.argv[4]) if len(sys.argv) > 4 else None)
