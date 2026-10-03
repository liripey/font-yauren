"""Gera imagens de espécime da família Yauren (docs/img)."""
import os
import sys

import freetype
import numpy as np
import uharfbuzz as hb
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OTF = os.path.join(ROOT, "fonts", "otf")
OUT = os.path.join(ROOT, "docs", "img")
WEIGHTS = ["Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"]
INK = (24, 28, 38)
PAPER = (250, 248, 243)
ACCENT = (120, 86, 40)
GREY = (130, 130, 130)


def fpath(w):
    return os.path.join(OTF, f"Yauren-{w}.otf")


class Font:
    _cache = {}

    def __init__(self, w):
        self.path = fpath(w)
        blob = hb.Blob.from_file_path(self.path)
        self.hbface = hb.Face(blob)
        self.hbfont = hb.Font(self.hbface)
        self.ft = freetype.Face(self.path)
        self.upem = self.hbface.upem

    @classmethod
    def get(cls, w):
        if w not in cls._cache:
            cls._cache[w] = Font(w)
        return cls._cache[w]

    def shape(self, text, features=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hbfont, buf, features or {})
        return buf.glyph_infos, buf.glyph_positions

    def width(self, text, px, features=None):
        _, pos = self.shape(text, features)
        return sum(p.x_advance for p in pos) * px / self.upem

    def draw(self, img, x, y, text, px, color=INK, features=None, tracking=0):
        """Desenha texto com a linha de base em y."""
        infos, poss = self.shape(text, features)
        self.ft.set_char_size(int(px * 64))
        scale = px / self.upem
        pen = float(x)
        arr = np.asarray(img).copy()
        for info, pos in zip(infos, poss):
            self.ft.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            bm = self.ft.glyph.bitmap
            if bm.width and bm.rows:
                a = np.array(bm.buffer, dtype=np.float32).reshape(bm.rows, bm.pitch)[:, :bm.width] / 255.0
                gx = int(round(pen + pos.x_offset * scale)) + self.ft.glyph.bitmap_left
                gy = int(round(y - pos.y_offset * scale)) - self.ft.glyph.bitmap_top
                x0, y0 = max(gx, 0), max(gy, 0)
                x1, y1 = min(gx + bm.width, arr.shape[1]), min(gy + bm.rows, arr.shape[0])
                if x1 > x0 and y1 > y0:
                    sub = a[y0 - gy:y1 - gy, x0 - gx:x1 - gx][..., None]
                    region = arr[y0:y1, x0:x1].astype(np.float32)
                    col = np.array(color, dtype=np.float32)
                    arr[y0:y1, x0:x1] = (region * (1 - sub) + col * sub).astype(np.uint8)
            pen += pos.x_advance * scale + tracking
        img.paste(Image.fromarray(arr))
        return pen


def wrap(font, text, px, maxw, features=None):
    lines, cur = [], ""
    for word in text.split(" "):
        t = (cur + " " + word).strip()
        if font.width(t, px, features) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(img, font, x, y, text, px, maxw, leading=1.45, color=INK, features=None):
    for line in wrap(font, text, px, maxw, features):
        font.draw(img, x, y, line, px, color, features)
        y += px * leading
    return y


def canvas(w, h):
    return Image.new("RGB", (w, h), PAPER)


def label(img, x, y, text, px=15, color=GREY):
    Font.get("Regular").draw(img, x, y, text, px, color)


# ----------------------------------------------------------------- páginas

def page_cover():
    img = canvas(1800, 1000)
    R = Font.get("Regular")
    Font.get("Light").draw(img, 110, 400, "Yauren", 300, INK)
    label(img, 116, 140, "FAMÍLIA TIPOGRÁFICA EXCLUSIVA · 7 PESOS · OTF", 22, ACCENT)
    Font.get("Regular").draw(img, 116, 560,
                             "Serifada humanista para ciência, leitura e precisão.", 46, INK)
    Font.get("Light").draw(img, 116, 640,
                           "Garamond na elegância, Georgia na robustez, Lexend Deca na clareza.", 30, GREY)
    y = 760
    x = 116
    for w in WEIGHTS:
        f = Font.get(w)
        x = f.draw(img, x, y, "Aa", 64, INK) + 34
    label(img, 116, 860, "Light · Regular · Medium · SemiBold · Bold · ExtraBold · Black", 22)
    img.save(os.path.join(OUT, "01-capa.png"))


def page_weights():
    img = canvas(1800, 1220)
    y = 120
    for w in WEIGHTS:
        f = Font.get(w)
        label(img, 110, y - 74, w.upper(), 16, ACCENT)
        f.draw(img, 110, y, "Pesquisa & Precisão — Ciência que transforma 2026", 62)
        y += 160
    img.save(os.path.join(OUT, "02-pesos.png"))


TEXT_PT = ("A Yauren nasceu para dar voz a um laboratório de pesquisa: relatórios, artigos, "
           "rótulos de amostras e apresentações precisam ser lidos com rapidez e sem ambiguidade. "
           "Por isso a família combina a elegância das garaldes com uma altura-x generosa, "
           "aberturas amplas e espaçamento confortável. Ação, função, coração e informação: "
           "os acentos do português foram desenhados com o mesmo cuidado que as letras, e o "
           "kerning é calculado também para cada caractere acentuado.")


def page_text():
    img = canvas(1800, 1300)
    R, B, L = Font.get("Regular"), Font.get("Bold"), Font.get("Light")
    label(img, 110, 90, "TEXTO CORRIDO · 17 / 24 px · Regular, Bold e Light", 16, ACCENT)
    y = 150
    B.draw(img, 110, y, "Legibilidade em primeiro lugar", 40)
    y += 70
    y = paragraph(img, R, 110, y, TEXT_PT, 24, 760)
    y2 = paragraph(img, R, 930, 220, TEXT_PT, 17, 760, leading=1.55)
    y = max(y, y2) + 50
    label(img, 110, y, "CORPOS PEQUENOS (renderização com hinting)", 16, ACCENT)
    y += 40
    for px in (11, 12, 13, 14, 16):
        R.draw(img, 110, y, f"{px} px — Resultados preliminares indicam redução de 12,5% na variância (p < 0,05; n = 48).", px)
        y += px * 1.9
    y += 30
    label(img, 110, y, "TÍTULOS", 16, ACCENT)
    y += 90
    Font.get("Black").draw(img, 110, y, "Relatório Anual", 84)
    Font.get("SemiBold").draw(img, 900, y, "Métodos e Materiais", 52)
    y += 80
    L.draw(img, 110, y, "Uma nova geração de instrumentos analíticos", 40)
    img.save(os.path.join(OUT, "03-texto.png"))


def page_scripts():
    img = canvas(1800, 1150)
    R = Font.get("Regular")
    rows = [
        ("PORTUGUÊS", "Ação, coração, órgão, pôr, vovô, à luz, Çé — ª 1º 2ª"),
        ("ESPAÑOL · FRANÇAIS · DEUTSCH", "¿Qué año? Où êtes-vous? Größe, Fußgänger, Ærø, Ørsted"),
        ("POLSKI · ČEŠTINA · TÜRKÇE · ROMÂNĂ", "Łódź, żółć · Příliš žluťoučký · Iğdır, ışık · Țară, știință"),
        ("TIẾNG VIỆT", "Tiếng Việt có dấu: Người ấy ở đâu? Nghiên cứu khoa học."),
        ("ΕΛΛΗΝΙΚΆ", "Επιστήμη και έρευνα · αβγδεζηθικλμνξοπρστυφχψω · ΑΒΓΔΩ"),
        ("РУССКИЙ · УКРАЇНСЬКА · ҚАЗАҚША", "Научное исследование · Наукове дослідження · Ғылым"),
        ("GUARANI · HAWAIʻI · AZƏRBAYCAN", "Ñandeʼa ñeʼẽ, g̃uarã · Hawaiʻi · Əlifba, şəhər, ğ"),
        ("CIÊNCIA", "α = 0,05 · β-caroteno · Δt = 3 µs · Ω · π ≈ 3,1416 · ∑ ∫ √ ∞ ≤ ≥ ± ×"),
    ]
    y = 120
    for lab, txt in rows:
        label(img, 110, y - 44, lab, 15, ACCENT)
        R.draw(img, 110, y, txt, 46)
        y += 132
    img.save(os.path.join(OUT, "04-idiomas.png"))


def page_features():
    img = canvas(1800, 1250)
    R = Font.get("Regular")
    demos = [
        ("Padrão (alinhados proporcionais)", "Lote 1.234.567 — 0,0168 mg", {}),
        ("tnum — tabulares", "Lote 1.234.567 — 0,0168 mg", {"tnum": True}),
        ("onum — estilo antigo", "Lote 1.234.567 — 0,0168 mg", {"onum": True}),
        ("zero — zero cortado", "ID 0O0-1010-OO8", {"zero": True}),
        ("frac — frações", "1/2 · 3/4 · 15/16 · 7/8", {"frac": True}),
        ("sups / subs", "m2 · x3 · H2O · CO2", None),
        ("ordn — ordinais", "1a 2o 3a 10o", {"ordn": True}),
        ("case — pontuação para caixa-alta", "(ATENÇÃO) — «NOVO» [LAB-01]", {"case": True}),
        ("liga — ligaduras", "fluxo · filtro · fiel · flor", {}),
    ]
    y = 110
    for lab, txt, feat in demos:
        label(img, 110, y - 40, lab, 16, ACCENT)
        if feat is None:
            x = R.draw(img, 110, y, "m", 50)
            x = R.draw(img, x, y, "2", 50, features={"sups": True})
            x = R.draw(img, x, y, " · x", 50)
            x = R.draw(img, x, y, "3", 50, features={"sups": True})
            x = R.draw(img, x, y, " · H", 50)
            x = R.draw(img, x, y, "2", 50, features={"subs": True})
            x = R.draw(img, x, y, "O · CO", 50)
            R.draw(img, x, y, "2", 50, features={"subs": True})
        else:
            R.draw(img, 110, y, txt, 50, features=feat)
        y += 125
    img.save(os.path.join(OUT, "05-recursos.png"))


def page_glyphs():
    img = canvas(1800, 1100)
    R = Font.get("Regular")
    sets = [
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "abcdefghijklmnopqrstuvwxyz",
        "0123456789 ¹²³ ½ ¼ ¾ % ‰ € $ £ ¥ ¢ ₀₁₂",
        "ÁÂÃÀÇÉÊÍÓÔÕÚÜ áâãàçéêíóôõúü ÆŒØßÐÞŁ",
        ".,:;…!¡?¿·•‘’“”‚„«»‹›-–—()[]{}/\\|@&#*†‡§¶©®™°",
        "+−×÷=≠≈<>≤≥±¬∞∂∆∏∑√∫µπΩ ← ↑ → ↓ ↔",
    ]
    y = 150
    for s_ in sets:
        R.draw(img, 110, y, s_, 54)
        y += 140
    label(img, 110, 60, "CONJUNTO DE CARACTERES (amostra) · Yauren Regular", 16, ACCENT)
    img.save(os.path.join(OUT, "06-caracteres.png"))


def page_legibility():
    img = canvas(1800, 820)
    R, B = Font.get("Regular"), Font.get("Bold")
    label(img, 110, 80, "DESAMBIGUAÇÃO — formas distintas para caracteres que costumam se confundir", 16, ACCENT)
    pairs = ["Il1|", "O0Ø", "rn m", "cl d", "vv w", "6b 9q", "a g e", "5S 2Z", "B8"]
    x, y = 110, 260
    for p_ in pairs:
        x = B.draw(img, x, y, p_, 96) + 70
        if x > 1500:
            x, y = 110, y + 190
    R.draw(img, 110, 700, "Zero com recurso 'zero': 0 → 0̸ · Il1 com serifas e bandeira distintas", 30, GREY)
    img.save(os.path.join(OUT, "07-legibilidade.png"))


def main():
    os.makedirs(OUT, exist_ok=True)
    page_cover()
    page_weights()
    page_text()
    page_scripts()
    page_features()
    page_glyphs()
    page_legibility()
    print("espécimes em", OUT)


if __name__ == "__main__":
    main()
