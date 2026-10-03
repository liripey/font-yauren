"""Tabela de letras acentuadas (decompostas no OTF final)."""
from ..registry import composite

# marcas por nome curto
T = {
    "grave": "gravecomb", "acute": "acutecomb", "circ": "circumflexcomb",
    "tilde": "tildecomb", "macron": "macroncomb", "breve": "brevecomb",
    "dot": "dotaccentcomb", "dier": "dieresiscomb", "ring": "ringcomb",
    "hung": "hungarumlautcomb", "caron": "caroncomb", "ctab": "commaturnedabovecomb",
    "dotb": "dotbelowcomb", "comma": "commaaccentcomb", "ced": "cedillacomb",
    "ogon": "ogonekcomb", "caronalt": "caroncomb.alt",
}
TOPS = {"grave", "acute", "circ", "tilde", "macron", "breve", "dot", "dier", "ring", "hung",
        "caron"}

SUFFIX = {
    "grave": "grave", "acute": "acute", "circ": "circumflex", "tilde": "tilde",
    "macron": "macron", "breve": "breve", "dot": "dotaccent", "dier": "dieresis",
    "ring": "ring", "hung": "hungarumlaut", "caron": "caron", "comma": "commaaccent",
    "ced": "cedilla", "ogon": "ogonek", "dotb": "dotbelow", "ctab": "commaaccent",
    "caronalt": "caron",
}


def comp(name, uni, base, *marks):
    upper = base[0].isupper()
    ms = []
    for mk in marks:
        mname = T[mk]
        if upper and mk in TOPS:
            mname += ".case"
        ms.append(mname)
    composite(name, uni, base, ms)


def series(letter, pairs, upper_base=None, lower_base=None):
    """pairs: [(marca, cp_maiúscula, cp_minúscula)]"""
    U = upper_base or letter.upper()
    L = lower_base or letter
    for mk, cu, cl in pairs:
        if cu:
            comp(letter.upper() + SUFFIX[mk], cu, U, mk)
        if cl:
            comp(letter + SUFFIX[mk], cl, L, mk)


series("a", [("grave", 0xC0, 0xE0), ("acute", 0xC1, 0xE1), ("circ", 0xC2, 0xE2),
             ("tilde", 0xC3, 0xE3), ("dier", 0xC4, 0xE4), ("ring", 0xC5, 0xE5),
             ("macron", 0x100, 0x101), ("breve", 0x102, 0x103), ("ogon", 0x104, 0x105)])
series("c", [("ced", 0xC7, 0xE7), ("acute", 0x106, 0x107), ("circ", 0x108, 0x109),
             ("dot", 0x10A, 0x10B), ("caron", 0x10C, 0x10D)])
series("d", [("caron", 0x10E, None)])
comp("dcaron", 0x10F, "d", "caronalt")
series("e", [("grave", 0xC8, 0xE8), ("acute", 0xC9, 0xE9), ("circ", 0xCA, 0xEA),
             ("dier", 0xCB, 0xEB), ("macron", 0x112, 0x113), ("breve", 0x114, 0x115),
             ("dot", 0x116, 0x117), ("ogon", 0x118, 0x119), ("caron", 0x11A, 0x11B),
             ("tilde", 0x1EBC, 0x1EBD)])
series("g", [("circ", 0x11C, 0x11D), ("breve", 0x11E, 0x11F), ("dot", 0x120, 0x121),
             ("caron", 0x1E6, 0x1E7)])
comp("Gcommaaccent", 0x122, "G", "comma")
comp("gcommaaccent", 0x123, "g", "ctab")
series("h", [("circ", 0x124, 0x125)])
series("i", [("grave", 0xCC, 0xEC), ("acute", 0xCD, 0xED), ("circ", 0xCE, 0xEE),
             ("dier", 0xCF, 0xEF), ("tilde", 0x128, 0x129), ("macron", 0x12A, 0x12B),
             ("breve", 0x12C, 0x12D)], lower_base="dotlessi")
comp("Iogonek", 0x12E, "I", "ogon")
comp("iogonek", 0x12F, "i", "ogon")
comp("Idotaccent", 0x130, "I", "dot")
comp("Jcircumflex", 0x134, "J", "circ")
comp("jcircumflex", 0x135, "dotlessj", "circ")
comp("Kcommaaccent", 0x136, "K", "comma")
comp("kcommaaccent", 0x137, "k", "comma")
comp("Lacute", 0x139, "L", "acute")
comp("lacute", 0x13A, "l", "acute")
comp("Lcommaaccent", 0x13B, "L", "comma")
comp("lcommaaccent", 0x13C, "l", "comma")
comp("Lcaron", 0x13D, "L", "caronalt")
comp("lcaron", 0x13E, "l", "caronalt")
series("n", [("tilde", 0xD1, 0xF1), ("acute", 0x143, 0x144), ("caron", 0x147, 0x148),
             ("grave", 0x1F8, 0x1F9)])
comp("Ncommaaccent", 0x145, "N", "comma")
comp("ncommaaccent", 0x146, "n", "comma")
series("o", [("grave", 0xD2, 0xF2), ("acute", 0xD3, 0xF3), ("circ", 0xD4, 0xF4),
             ("tilde", 0xD5, 0xF5), ("dier", 0xD6, 0xF6), ("macron", 0x14C, 0x14D),
             ("breve", 0x14E, 0x14F), ("hung", 0x150, 0x151), ("ogon", 0x1EA, 0x1EB)])
series("r", [("acute", 0x154, 0x155), ("caron", 0x158, 0x159)])
comp("Rcommaaccent", 0x156, "R", "comma")
comp("rcommaaccent", 0x157, "r", "comma")
series("s", [("acute", 0x15A, 0x15B), ("circ", 0x15C, 0x15D), ("ced", 0x15E, 0x15F),
             ("caron", 0x160, 0x161)])
comp("Scommaaccent", 0x218, "S", "comma")
comp("scommaaccent", 0x219, "s", "comma")
comp("Tcedilla", 0x162, "T", "ced")
comp("tcedilla", 0x163, "t", "ced")
comp("Tcaron", 0x164, "T", "caron")
comp("tcaron", 0x165, "t", "caronalt")
comp("Tcommaaccent", 0x21A, "T", "comma")
comp("tcommaaccent", 0x21B, "t", "comma")
series("u", [("grave", 0xD9, 0xF9), ("acute", 0xDA, 0xFA), ("circ", 0xDB, 0xFB),
             ("dier", 0xDC, 0xFC), ("tilde", 0x168, 0x169), ("macron", 0x16A, 0x16B),
             ("breve", 0x16C, 0x16D), ("ring", 0x16E, 0x16F), ("hung", 0x170, 0x171),
             ("ogon", 0x172, 0x173)])
series("w", [("circ", 0x174, 0x175), ("grave", 0x1E80, 0x1E81), ("acute", 0x1E82, 0x1E83),
             ("dier", 0x1E84, 0x1E85)])
series("y", [("acute", 0xDD, 0xFD), ("dier", 0x178, 0xFF), ("circ", 0x176, 0x177),
             ("grave", 0x1EF2, 0x1EF3), ("tilde", 0x1EF8, 0x1EF9)])
series("z", [("acute", 0x179, 0x17A), ("dot", 0x17B, 0x17C), ("caron", 0x17D, 0x17E)])
