"""Independent Presentation MathML to OMML conversion; no Office stylesheets."""

import unicodedata

from docx.oxml import OxmlElement
from lxml import etree

MATHML_NS = "http://www.w3.org/1998/Math/MathML"
# OMML script families and styles are separate properties (ECMA-376 §22.1).
VARIANTS = {
    "normal": ("roman", "p"),
    "bold": ("roman", "b"),
    "italic": ("roman", "i"),
    "bold-italic": ("roman", "bi"),
    "double-struck": ("double-struck", "p"),
    "fraktur": ("fraktur", "p"),
    "bold-fraktur": ("fraktur", "b"),
    "script": ("script", "p"),
    "bold-script": ("script", "b"),
    "sans-serif": ("sans-serif", "p"),
    "bold-sans-serif": ("sans-serif", "b"),
    "sans-serif-italic": ("sans-serif", "i"),
    "sans-serif-bold-italic": ("sans-serif", "bi"),
    "monospace": ("monospace", "p"),
}
UNICODE_VARIANTS = {
    "bold": "BOLD",
    "italic": "ITALIC",
    "bold-italic": "BOLD ITALIC",
    "double-struck": "DOUBLE-STRUCK",
    "fraktur": "FRAKTUR",
    "bold-fraktur": "BOLD FRAKTUR",
    "script": "SCRIPT",
    "bold-script": "BOLD SCRIPT",
    "sans-serif": "SANS-SERIF",
    "bold-sans-serif": "SANS-SERIF BOLD",
    "sans-serif-italic": "SANS-SERIF ITALIC",
    "sans-serif-bold-italic": "SANS-SERIF BOLD ITALIC",
    "monospace": "MONOSPACE",
}
# Unicode's mathematical alphabet has legacy characters in Letterlike Symbols.
LETTERLIKE = {
    "double-struck": dict(zip("CHNPQRZ", "ℂℍℕℙℚℝℤ")),
    "fraktur": dict(zip("CHIRZ", "ℭℌℑℜℨ")),
    "script": dict(zip("BEFHILMRego", "ℬℰℱℋℐℒℳℛℯℊℴ")),
    "italic": {"h": "ℎ"},
}


def variant_characters(value, variant):
    """Use equivalent Unicode math alphabets for explicit MathML variants.

    W3C MathML §3.2.2 defines these as equivalent to character+mathvariant.
    Keep OMML style properties, too; leave already styled characters unchanged.
    """
    prefix = UNICODE_VARIANTS.get(variant)
    if prefix is None:
        return value
    result = []
    for char in value:
        replacement = LETTERLIKE.get(variant, {}).get(char)
        if replacement is None:
            name = unicodedata.name(char, "")
            if "A" <= char <= "Z":
                suffix = "CAPITAL " + char
            elif "a" <= char <= "z":
                suffix = "SMALL " + char.upper()
            elif "0" <= char <= "9":
                suffix = name
            elif name.startswith("GREEK ") and " LETTER " in name:
                suffix = name[6:].replace(" LETTER ", " ")
            else:
                result.append(char)
                continue
            try:
                replacement = unicodedata.lookup(
                    "MATHEMATICAL " + prefix + " " + suffix
                )
            except KeyError:
                replacement = char
        result.append(replacement)
    return "".join(result)


class UnsupportedMathMLError(ValueError):
    """The input uses a MathML construct this converter cannot preserve."""


def element(name, *children, **attributes):
    node = OxmlElement("m:" + name)
    for key, value in attributes.items():
        node.set(
            "{http://schemas.openxmlformats.org/officeDocument/2006/math}" + key,
            str(value),
        )
    node.extend(children)
    return node


def text(value, variant=None, normal_text=False):
    node = element("t")
    node.text = value
    node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    if normal_text:
        return element("r", element("rPr", element("nor", val="1")), node)
    if variant is None:
        return element("r", node)
    if variant not in VARIANTS:
        raise UnsupportedMathMLError("Unsupported mathvariant: " + variant)
    script, style = VARIANTS[variant]
    return element(
        "r", element("rPr", element("scr", val=script), element("sty", val=style)), node
    )


def fenced(begin, end, content):
    if len(begin) > 1 or len(end) > 1:
        raise UnsupportedMathMLError("OMML fences require zero or one character")
    return element(
        "d",
        element("dPr", element("begChr", val=begin), element("endChr", val=end)),
        element("e", *content),
    )


def mathml_to_omml(source):
    """Return an oMath element. Unsupported structures raise instead of losing data."""
    if not isinstance(source, str):
        raise TypeError("MathML must be a string")
    if "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("DTD and entity declarations are not allowed")
    parser = etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        remove_comments=True,
        remove_pis=True,
    )
    try:
        root = etree.fromstring(source.encode("utf-8"), parser)
    except etree.XMLSyntaxError as exc:
        raise ValueError("Invalid MathML XML: " + str(exc)) from exc
    if etree.QName(root).localname != "math":
        raise ValueError("MathML root must be math")
    return element("oMath", *convert(root))


def math_name(node):
    qualified = etree.QName(node)
    if qualified.namespace not in {None, MATHML_NS}:
        raise UnsupportedMathMLError(
            "Unsupported MathML namespace: " + qualified.namespace
        )
    return qualified.localname


def convert(node, inherited=None):
    tag = math_name(node)
    inherited = dict(inherited or {})
    for name in (
        ("mathvariant", "linethickness") if tag == "mstyle" else ("mathvariant",)
    ):
        if node.get(name) is not None:
            inherited[name] = node.get(name)
    children = list(node)

    def parts(child):
        return convert(child, inherited)

    def group(index, name):
        return element(name, *parts(children[index]))

    def arity(count):
        if len(children) != count:
            raise ValueError(f"{tag} expects {count} children")

    if tag not in {"mi", "mn", "mo", "mtext", "ms", "annotation", "annotation-xml"}:
        if (node.text or "").strip() or any((c.tail or "").strip() for c in children):
            raise ValueError("Text must be inside a MathML token element")
    if tag == "mpadded" and any(
        node.get(k) is not None
        for k in ("width", "height", "depth", "lspace", "voffset")
    ):
        raise UnsupportedMathMLError("mpadded dimensions cannot be preserved")
    if tag in {"math", "mrow", "mstyle", "mpadded"}:
        # Explicit fence operators (including latex2mathml's \left/\right)
        # need a delimiter object, rather than isolated operator runs.
        if tag == "mrow" and len(children) >= 2:
            first, last = children[0], children[-1]
            begin, end = (first.text or "").strip(), (last.text or "").strip()
            paired = (begin, end) in {
                ("(", ")"),
                ("[", "]"),
                ("{", "}"),
                ("⟨", "⟩"),
                ("|", "|"),
                ("‖", "‖"),
            }
            explicit = (
                first.get("fence") == "true"
                and first.get("form") == "prefix"
                and last.get("fence") == "true"
                and last.get("form") == "postfix"
            )
            if math_name(first) == math_name(last) == "mo" and (explicit or paired):
                return [
                    fenced(
                        begin,
                        end,
                        [part for child in children[1:-1] for part in parts(child)],
                    )
                ]
        result = []
        index = 0
        while index < len(children):
            child = children[index]
            # Encode a limit function and its next explicit argument together.
            # Otherwise some readers absorb lim into the following fraction's
            # numerator when translating the independent OMML objects.
            if (
                etree.QName(child).localname in {"munder", "mover", "munderover"}
                and len(child)
                and "".join(child[0].itertext()).strip() in {"lim", "liminf", "limsup"}
                and index + 1 < len(children)
            ):
                result.append(
                    element(
                        "func",
                        element("fName", *parts(child)),
                        element("e", *parts(children[index + 1])),
                    )
                )
                index += 2
            else:
                result.extend(parts(child))
                index += 1
        return result
    if tag == "semantics":
        if not children:
            return []
        return parts(children[0])
    if tag in {"annotation", "annotation-xml"}:
        return []
    if tag in {"mi", "mn", "mo", "mtext", "ms"}:
        if children:
            raise UnsupportedMathMLError(
                "Nested elements in MathML tokens are unsupported"
            )
        value = node.text or ""
        if tag != "mtext":
            value = " ".join(value.split())
        if tag == "ms":
            value = node.get("lquote", '"') + value + node.get("rquote", '"')
        variant = inherited.get(
            "mathvariant", "italic" if tag == "mi" and len(value) == 1 else "normal"
        )
        if "mathvariant" in inherited:
            value = variant_characters(value, variant)
        return [
            text(
                value,
                variant,
                normal_text=tag in {"mtext", "ms"} and variant == "normal",
            )
        ]
    if tag == "mspace":
        if node.get("linebreak", "auto") not in {"auto", "nobreak"}:
            raise UnsupportedMathMLError("MathML line breaks are unsupported")
        for name in ("height", "depth"):
            if node.get(name, "0") not in {"0", "0em", "0px", "0pt"}:
                raise UnsupportedMathMLError("mspace height/depth are unsupported")
        spaces = {
            "0": "",
            "0em": "",
            "0px": "",
            "0pt": "",
            "0.167em": "\u2009",
            "thinmathspace": "\u2009",
            "0.222em": "\u2005",
            "mediummathspace": "\u2005",
            "0.278em": "\u2004",
            "thickmathspace": "\u2004",
            "0.5em": "\u2002",
            "1em": "\u2003",
            "2em": "\u2003\u2003",
        }
        width = node.get("width", "0")
        if width not in spaces:
            raise UnsupportedMathMLError("Unsupported mspace width: " + width)
        return (
            [text(spaces[width], "normal", normal_text=True)] if spaces[width] else []
        )
    if tag == "mfrac":
        arity(2)
        thickness = node.get("linethickness", inherited.get("linethickness", "medium"))
        if thickness not in {"medium", "0", "0px", "0pt", "0em"}:
            raise UnsupportedMathMLError(
                "Custom fraction line thickness is unsupported"
            )
        fraction_type = (
            "noBar"
            if thickness != "medium"
            else "skw"
            if node.get("bevelled") == "true"
            else "bar"
        )
        return [
            element(
                "f",
                element("fPr", element("type", val=fraction_type)),
                group(0, "num"),
                group(1, "den"),
            )
        ]
    if tag in {"msup", "msub", "msubsup"}:
        arity(3 if tag == "msubsup" else 2)
        if tag == "msubsup":
            return [element("sSubSup", group(0, "e"), group(1, "sub"), group(2, "sup"))]
        return [
            element(
                "sSup" if tag == "msup" else "sSub",
                group(0, "e"),
                group(1, "sup" if tag == "msup" else "sub"),
            )
        ]
    if tag in {"msqrt", "mroot"}:
        if tag == "mroot":
            arity(2)
            return [element("rad", group(1, "deg"), group(0, "e"))]
        return [
            element(
                "rad",
                element("radPr", element("degHide", val="1")),
                element("deg"),
                element("e", *[part for child in children for part in parts(child)]),
            )
        ]
    if tag == "mfenced":
        separators = "".join(node.get("separators", ",").split())
        fence_parts = []
        for index, child in enumerate(children):
            if index and separators:
                fence_parts.append(
                    text(
                        separators[min(index - 1, len(separators) - 1)],
                        normal_text=True,
                    )
                )
            fence_parts.extend(convert(child, inherited))
        return [fenced(node.get("open", "("), node.get("close", ")"), fence_parts)]
    if tag in {"munder", "mover", "munderover"}:
        arity(3 if tag == "munderover" else 2)
        base = group(0, "e")
        accent = "".join(children[1].itertext()).strip()
        is_accent = (
            node.get(
                "accent" if tag == "mover" else "accentunder",
                children[1].get(
                    "accent",
                    "true"
                    if accent in {"^", "~", "¯", "‾", "―", "→", "⃗", "ˆ", "˜"}
                    else "false",
                ),
            )
            == "true"
        )
        if tag in {"mover", "munder"} and is_accent and accent in {"_", "¯", "‾", "―"}:
            return [
                element(
                    "bar",
                    element(
                        "barPr", element("pos", val="top" if tag == "mover" else "bot")
                    ),
                    base,
                )
            ]
        if tag == "munder" and is_accent:
            raise UnsupportedMathMLError(
                "Only line accents below expressions are supported"
            )
        if tag == "mover" and is_accent:
            if len(accent) != 1:
                raise UnsupportedMathMLError("OMML accents require one character")
            return [element("acc", element("accPr", element("chr", val=accent)), base)]
        lower = element("limLow", base, group(1, "lim"))
        if tag == "munder":
            return [lower]
        if tag == "mover":
            return [element("limUpp", base, group(1, "lim"))]
        return [element("limUpp", element("e", lower), group(2, "lim"))]
    if tag == "mtable":
        if not children:
            raise ValueError("MathML matrices must have at least one row")
        rows = []
        for row in children:
            if math_name(row) != "mtr":
                raise UnsupportedMathMLError("Only mtr rows are supported in mtable")
            if (row.text or "").strip() or any(
                (cell.tail or "").strip() for cell in row
            ):
                raise ValueError("Text must be inside a MathML token element")
            if not len(row) or any(math_name(cell) != "mtd" for cell in row):
                raise ValueError("MathML matrix rows require mtd cells")
            rows.append(element("mr", *[element("e", *parts(cell)) for cell in row]))
        widths = {len(row) for row in children}
        if len(widths) > 1:
            raise ValueError("MathML matrix rows must have equal widths")
        return [element("m", *rows)]
    if tag == "mtd":
        return [part for child in children for part in parts(child)]
    if tag == "mphantom":
        return [
            element(
                "phant",
                element(
                    "phantPr",
                    element("show", val="0"),
                    element("zeroWid", val="0"),
                    element("zeroAsc", val="0"),
                    element("zeroDesc", val="0"),
                ),
                element("e", *[part for child in children for part in parts(child)]),
            )
        ]
    raise UnsupportedMathMLError("Unsupported MathML element: " + tag)


def latex_to_omml(source):
    """Convert LaTeX math via the optional MIT-licensed latex2mathml package."""
    try:
        from latex2mathml.converter import convert as latex_to_mathml
    except ImportError as exc:
        raise ImportError("Install mathml2docx[latex] to convert LaTeX") from exc
    converted = latex_to_mathml(source, display="block")
    # Older latex2mathml versions used side scripts for block sums/products.
    # Keep the public block-equation output consistent on legacy Python too.
    root = etree.fromstring(
        converted.encode("utf-8"),
        etree.XMLParser(resolve_entities=False, no_network=True),
    )
    if r"\nolimits" not in source:
        for node in root.iter():
            name = etree.QName(node).localname
            if name not in {"msub", "msup", "msubsup"} or not len(node):
                continue
            base = node[0]
            if etree.QName(base).localname == "mo" and base.text in {
                "∑",
                "∏",
                "∐",
                "⋃",
                "⋂",
                "⋁",
                "⋀",
                "lim",
                "liminf",
                "limsup",
            }:
                namespace = etree.QName(node).namespace
                replacement = {
                    "msub": "munder",
                    "msup": "mover",
                    "msubsup": "munderover",
                }[name]
                node.tag = (
                    "{" + namespace + "}" + replacement if namespace else replacement
                )
    return mathml_to_omml(etree.tostring(root, encoding="unicode"))
