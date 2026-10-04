"""Parâmetros de desenho da Yauren por peso.

Unidades em 1/1000 em. Os valores-chave são definidos para os sete pesos e
interpolados linearmente quando necessário (ex.: sobrescritos).
"""
import copy

WEIGHTS = [
    # (classe, nome do estilo)
    (300, "Light"),
    (400, "Regular"),
    (500, "Medium"),
    (600, "SemiBold"),
    (700, "Bold"),
    (800, "ExtraBold"),
    (900, "Black"),
]

# tabela mestre: peso -> valores
_T = {
    300: dict(stem=58, hair=27, cn=300, sfx=40, sft=26, sfb=28, hdx=42, hdd=34, sb=33),
    400: dict(stem=84, hair=35, cn=296, sfx=44, sft=33, sfb=34, hdx=46, hdd=38, sb=32),
    500: dict(stem=100, hair=40, cn=292, sfx=45, sft=37, sfb=37, hdx=47, hdd=40, sb=30),
    600: dict(stem=119, hair=45, cn=286, sfx=46, sft=41, sfb=40, hdx=48, hdd=42, sb=28),
    700: dict(stem=139, hair=50, cn=278, sfx=47, sft=45, sfb=43, hdx=49, hdd=44, sb=26),
    800: dict(stem=160, hair=56, cn=268, sfx=48, sft=50, sfb=46, hdx=50, hdd=46, sb=23),
    900: dict(stem=182, hair=62, cn=256, sfx=49, sft=55, sfb=49, hdx=51, hdd=48, sb=20),
}


def _interp(w):
    ks = sorted(_T)
    if w <= ks[0]:
        return dict(_T[ks[0]])
    if w >= ks[-1]:
        return dict(_T[ks[-1]])
    for a, b in zip(ks, ks[1:]):
        if a <= w <= b:
            f = (w - a) / (b - a)
            return {k: _T[a][k] + (_T[b][k] - _T[a][k]) * f for k in _T[a]}


class Params:
    def __init__(self, weight=400):
        v = _interp(weight)
        self.weight = weight
        self.wf = (weight - 300) / 600.0  # 0..1 fator de peso
        # métricas verticais (fixas em todos os pesos)
        self.xh = 500
        self.cap = 680
        self.asc = 740
        self.desc = -235
        self.fig = 660
        self.os = 12          # overshoot minúsculas
        self.osC = 14         # overshoot maiúsculas
        # hastes
        # dimensões inteiras (hastes pares) => desenhos simétricos após o
        # arredondamento das coordenadas
        ev = lambda x: 2 * round(x / 2)  # noqa: E731
        self.stem = ev(v["stem"])
        self.hair = ev(v["hair"])
        self.stemC = ev(v["stem"] * 1.09 + 2)
        self.hairC = ev(v["hair"] * 1.06)
        self.curve = ev(self.stem * 1.07)     # espessura máxima das curvas
        self.curveC = ev(self.stemC * 1.07)
        # contra-forma do n (largura entre hastes)
        self.cn = ev(v["cn"])
        # serifas
        self.sfx = round(v["sfx"])          # extensão da serifa de pé (minúsc.)
        self.sft = round(v["sft"])          # espessura na ponta
        self.sfb = round(v["sfb"])          # altura do colchete (bracket)
        self.sfxC = round(v["sfx"] * 1.22)  # maiúsculas
        self.sftC = round(v["sft"] * 1.05)
        self.sfbC = round(v["sfb"] * 1.1)
        self.hdx = v["hdx"]          # serifa de cabeça (cunha)
        self.hdd = v["hdd"]          # queda da cunha
        # espaçamento base (a partir da ponta da serifa)
        self.sb = v["sb"]
        # lados redondos medem-se do extremo da curva; retos, da ponta da serifa
        self.rnd = (self.sb + self.sfx) * 0.68
        self.sbC = self.sb * 1.4
        self.rndC = (self.sbC + self.sfxC) * 0.70
        # eixo de contraste (graus) para bojos: vertical, para formas redondas
        # simétricas e cortes de terminais retos
        self.ang = 0.0
        # escala horizontal (para variantes reduzidas)
        self.u = 1.0

    def copy(self):
        return copy.copy(self)

    def scaled(self, s, weight_comp=1.0):
        """Versão reduzida (sobrescritos/inferiores). weight_comp > 1
        engrossa os traços relativamente para manter a cor tipográfica."""
        q = self.copy()
        for k in ("xh", "cap", "asc", "desc", "fig", "os", "osC", "cn", "sfx", "sfb",
                  "sfxC", "sfbC", "hdx", "hdd", "sb", "u", "rnd", "sbC", "rndC"):
            setattr(q, k, getattr(self, k) * s)
        for k in ("stem", "hair", "stemC", "hairC", "curve", "curveC", "sft", "sftC"):
            setattr(q, k, getattr(self, k) * s * weight_comp)
        return q
