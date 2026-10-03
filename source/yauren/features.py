"""Geração do código de recursos OpenType (sintaxe AFDKO .fea)."""
from .glyph import contours_bounds
from .kerning import compute_kerning
from .registry import COMPOSITES

FIG = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def _cls(names):
    return "[" + " ".join(names) + "]"


def _cname(n):
    return n.replace(".", "_")


def _has(gl, *names):
    return all(n in gl for n in names)


def build_features(gl, P, kern=True):
    names = set(gl)
    out = []
    scripts = ["DFLT", "latn"]
    if "Alpha" in names:
        scripts.append("grek")
    if "afii10017" in names or "A-cy" in names:
        scripts.append("cyrl")
    out.append("languagesystem DFLT dflt;")
    out.append("languagesystem latn dflt;")
    out.append("languagesystem latn ROM;")
    out.append("languagesystem latn MOL;")
    out.append("languagesystem latn CAT;")
    for sc in scripts[2:]:
        out.append(f"languagesystem {sc} dflt;")
    out.append("")

    top_marks = [n for n in gl if n.endswith("comb") and "_top" in gl[n].anchors]
    top_case = [n + ".case" for n in top_marks if n + ".case" in names]
    top_marks_c = [n for n in top_marks if n + ".case" in names]
    uppers = sorted(n for n in names if n[:1].isupper() and gl[n].unicodes
                    and not n.endswith(".case"))

    # ---------------------------------------------------------------- ccmp
    out.append("feature ccmp {")
    if top_marks:
        out.append(f"  @CombTop = {_cls(top_marks)};")
        out.append("  lookup ccmp_dotless {")
        out.append("    sub i' @CombTop by dotlessi;")
        out.append("    sub j' @CombTop by dotlessj;")
        out.append("  } ccmp_dotless;")
    if "caroncomb.alt" in names:
        out.append("  lookup ccmp_caron {")
        out.append("    sub [d l L t] caroncomb' by caroncomb.alt;")
        out.append("  } ccmp_caron;")
    if top_case:
        out.append(f"  @CombTopLC = {_cls(top_marks_c)};")
        out.append(f"  @CombTopUC = {_cls(top_case)};")
        out.append(f"  @UCBase = {_cls(uppers)};")
        out.append("  lookup ccmp_case {")
        out.append("    sub @UCBase @CombTopLC' by @CombTopUC;")
        out.append("    sub @UCBase @CombTopUC @CombTopLC' by @CombTopUC;")
        out.append("  } ccmp_case;")
    out.append("} ccmp;\n")

    # ---------------------------------------------------------------- locl
    out.append("feature locl {")
    for lang in ("ROM", "MOL"):
        out.append(f"  script latn; language {lang} exclude_dflt;")
        pairs = [("Scedilla", "Scommaaccent"), ("scedilla", "scommaaccent"),
                 ("Tcedilla", "Tcommaaccent"), ("tcedilla", "tcommaaccent")]
        for a, b in pairs:
            if _has(gl, a, b):
                out.append(f"    sub {a} by {b};")
    if "periodcentered" in names and "ldot" in names:
        out.append("  script latn; language CAT exclude_dflt;")
        out.append("    sub l periodcentered' l by periodcentered;")
    out.append("} locl;\n")

    # ---------------------------------------------------------------- figuras
    tf = [f + ".tf" for f in FIG]
    osf = [f + ".osf" for f in FIG]
    if _has(gl, *tf):
        out.append("feature tnum {")
        out.append(f"  sub {_cls(FIG)} by {_cls(tf)};")
        out.append("} tnum;\n")
        out.append("feature pnum {")
        out.append(f"  sub {_cls(tf)} by {_cls(FIG)};")
        out.append("} pnum;\n")
    if _has(gl, *osf):
        out.append("feature onum {")
        out.append(f"  sub {_cls(FIG + tf)} by {_cls(osf + osf)};")
        out.append("} onum;\n")
        out.append("feature lnum {")
        out.append(f"  sub {_cls(osf)} by {_cls(FIG)};")
        out.append("} lnum;\n")
    if "zero.zero" in names:
        out.append("feature zero {")
        out.append("  sub [zero zero.tf] by zero.zero;")
        out.append("} zero;\n")
    for feat, suf in (("sups", "sups"), ("subs", "subs"), ("sinf", "subs"),
                      ("numr", "numr"), ("dnom", "dnom")):
        src = [f for f in FIG if f + "." + suf in names]
        if src:
            out.append(f"feature {feat} {{")
            out.append(f"  sub {_cls(src + [s + '.tf' for s in src])} by "
                       f"{_cls([s + '.' + suf for s in src] * 2)};")
            out.append(f"}} {feat};\n")
    if _has(gl, "fraction", *[f + ".numr" for f in FIG]):
        out.append("feature frac {")
        out.append("  lookup frac_num {")
        out.append(f"    sub {_cls(FIG)} by {_cls([f + '.numr' for f in FIG])};")
        out.append("    sub slash by fraction;")
        out.append("  } frac_num;")
        out.append("  lookup frac_den {")
        out.append(f"    sub [fraction {' '.join(f + '.dnom' for f in FIG)}] "
                   f"{_cls([f + '.numr' for f in FIG])}' by {_cls([f + '.dnom' for f in FIG])};")
        out.append("  } frac_den;")
        out.append("} frac;\n")
    if _has(gl, "ordfeminine", "ordmasculine"):
        out.append("feature ordn {")
        out.append(f"  sub {_cls(FIG)} [a A]' by ordfeminine;")
        out.append(f"  sub {_cls(FIG)} [o O]' by ordmasculine;")
        out.append("} ordn;\n")

    # ---------------------------------------------------------------- case
    case = [n[:-5] for n in names if n.endswith(".case") and n[:-5] in names
            and not n[:-5].endswith("comb")]
    if case:
        case.sort()
        out.append("feature case {")
        out.append(f"  sub {_cls(case)} by {_cls([c + '.case' for c in case])};")
        out.append("} case;\n")

    # ---------------------------------------------------------------- liga
    if _has(gl, "fi", "fl"):
        out.append("feature liga {")
        out.append("  sub f i by fi;")
        out.append("  sub f l by fl;")
        out.append("} liga;\n")

    # ---------------------------------------------------------------- ss01
    ss = sorted(n for n in names if n.endswith(".ss01") and n[:-5] in names)
    if ss:
        out.append("feature ss01 {")
        out.append('  featureNames { name "Alternativas de legibilidade"; };')
        out.append(f"  sub {_cls([s[:-5] for s in ss])} by {_cls(ss)};")
        out.append("} ss01;\n")

    # ---------------------------------------------------------------- kern
    if kern:
        fam, pairs, exc = compute_kerning(gl, P)
        used_l = sorted({a for a, b in pairs})
        used_r = sorted({b for a, b in pairs})
        out.append("feature kern {")
        for a in used_l:
            out.append(f"  @kL_{_cname(a)} = [{' '.join(fam[a])}];")
        for b in used_r:
            out.append(f"  @kR_{_cname(b)} = [{' '.join(fam[b])}];")
        out.append("  lookup kern_pairs {")
        for (a, b), v in sorted(exc.items()):
            out.append(f"    pos {a} {b} {v};")
        for (a, b), v in sorted(pairs.items()):
            out.append(f"    pos @kL_{_cname(a)} @kR_{_cname(b)} {v};")
        out.append("  } kern_pairs;")
        out.append("} kern;\n")

    # ---------------------------------------------------------------- mark
    out.append(mark_features(gl, P))
    return "\n".join(l for l in out if l is not None)


def _is_letter(b):
    import unicodedata
    if not b.unicodes:
        return False
    return unicodedata.category(chr(b.unicodes[0])).startswith("L")


def mark_features(gl, P):
    from .build import default_anchor
    keys = ["top", "bottom", "ogonek", "cedilla"]
    marks = {k: [] for k in keys}
    for n, b in gl.items():
        for k in keys:
            if "_" + k in b.anchors and n.endswith(("comb", "comb.case")):
                marks[k].append(n)
    lines = []
    for k in keys:
        for m in marks[k]:
            x, y = gl[m].anchors["_" + k]
            lines.append(f"markClass {m} <anchor {round(x)} {round(y)}> @MC_{k};")
    lines.append("")
    lines.append("feature mark {")
    is_mark = {m for k in keys for m in marks[k]}
    for k in keys:
        if not marks[k]:
            continue
        lines.append(f"  lookup mark_{k} {{")
        for n, b in gl.items():
            if n in is_mark or n.startswith(".") or not b.contours:
                continue
            if not _is_letter(b):
                continue
            a = b.anchors.get(k) or default_anchor(b, k, P)
            lines.append(f"    pos base {n} <anchor {round(a[0])} {round(a[1])}> mark @MC_{k};")
        lines.append(f"  }} mark_{k};")
    lines.append("} mark;\n")
    bases = sorted(n for n, b in gl.items() if n not in is_mark and b.contours and n not in ("fi", "fl"))
    ligs = [n for n in ("fi", "fl") if n in gl]
    lines.append("table GDEF {")
    marks_all = sorted(is_mark | ({"caroncomb.alt"} & set(gl)))
    bases = [b for b in bases if b not in marks_all]
    lines.append(f"  GlyphClassDef [{' '.join(bases)}], [{' '.join(ligs)}], [{' '.join(marks_all)}], ;")
    for lg in ligs:
        lines.append(f"  LigatureCaretByPos {lg} {round(gl[lg].width * 0.5)};")
    lines.append("} GDEF;\n")
    if "caroncomb.alt" in gl:
        x, y = gl["caroncomb.alt"].anchors["_topright"]
        lines.append(f"markClass caroncomb.alt <anchor {round(x)} {round(y)}> @MC_topright;")
        lines.append("feature mark {")
        lines.append("  lookup mark_topright {")
        for n in ("d", "l", "L", "t"):
            a = gl[n].anchors.get("topright") or default_anchor(gl[n], "topright", P)
            lines.append(f"    pos base {n} <anchor {round(a[0])} {round(a[1])}> mark @MC_topright;")
        lines.append("  } mark_topright;")
        lines.append("} mark;\n")
    lines.append("feature mkmk {")
    for k in ("top", "bottom"):
        ms = [m for m in marks[k] if k in gl[m].anchors]
        if not ms:
            continue
        lines.append(f"  lookup mkmk_{k} {{")
        for m in ms:
            x, y = gl[m].anchors[k]
            lines.append(f"    pos mark {m} <anchor {round(x)} {round(y)}> mark @MC_{k};")
        lines.append(f"  }} mkmk_{k};")
    lines.append("} mkmk;\n")
    return "\n".join(lines)
