"""Independent Presentation MathML to OMML conversion; no Office stylesheets."""

from docx.oxml import OxmlElement
from lxml import etree


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


def text(value):
    node = element("t")
    node.text = value
    node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return element("r", node)


def mathml_to_omml(source):
    """Return an oMath element. Unsupported structures raise instead of losing data."""
    if not isinstance(source, str):
        raise TypeError("MathML must be a string")
    if "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("DTD and entity declarations are not allowed")
    parser = etree.XMLParser(resolve_entities=False, no_network=True, load_dtd=False)
    root = etree.fromstring(source.encode("utf-8"), parser)
    if etree.QName(root).localname != "math":
        raise ValueError("MathML root must be math")
    return element("oMath", *convert(root))


def convert(node):
    tag = etree.QName(node).localname
    children = list(node)

    def group(index, name):
        return element(name, *convert(children[index]))

    def arity(count):
        if len(children) != count:
            raise ValueError(f"{tag} expects {count} children")

    if tag in {"math", "mrow", "mstyle", "mpadded"}:
        return [part for child in children for part in convert(child)]
    if tag == "semantics":
        if not children:
            return []
        return convert(children[0])
    if tag in {"annotation", "annotation-xml"}:
        return []
    if tag in {"mi", "mn", "mo", "mtext", "ms"}:
        return [text("".join(node.itertext()))]
    if tag == "mspace":
        return [text(" ")]
    if tag == "mfrac":
        arity(2)
        return [element("f", group(0, "num"), group(1, "den"))]
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
                element("e", *[part for child in children for part in convert(child)]),
            )
        ]
    if tag == "mfenced":
        separators = "".join(node.get("separators", ",").split())
        parts = []
        for index, child in enumerate(children):
            if index and separators:
                parts.append(text(separators[min(index - 1, len(separators) - 1)]))
            parts.extend(convert(child))
        return [
            element(
                "d",
                element(
                    "dPr",
                    element("begChr", val=node.get("open", "(")),
                    element("endChr", val=node.get("close", ")")),
                ),
                element("e", *parts),
            )
        ]
    if tag in {"munder", "mover", "munderover"}:
        arity(3 if tag == "munderover" else 2)
        base = group(0, "e")
        if tag == "mover" and node.get("accent") == "true":
            accent = "".join(children[1].itertext())
            return [element("acc", element("accPr", element("chr", val=accent)), base)]
        lower = element("limLow", base, group(1, "lim"))
        if tag == "munder":
            return [lower]
        if tag == "mover":
            return [element("limUpp", base, group(1, "lim"))]
        return [element("limUpp", element("e", lower), group(2, "lim"))]
    if tag == "mtable":
        rows = []
        for row in children:
            if etree.QName(row).localname != "mtr":
                raise UnsupportedMathMLError("Only mtr rows are supported in mtable")
            rows.append(element("mr", *[element("e", *convert(cell)) for cell in row]))
        widths = {len(row) for row in children}
        if len(widths) > 1:
            raise ValueError("MathML matrix rows must have equal widths")
        return [element("m", *rows)]
    if tag == "mtd":
        return [part for child in children for part in convert(child)]
    if tag == "mphantom":
        return [
            element(
                "phant",
                element("phantPr", element("show", val="0")),
                element("e", *[part for child in children for part in convert(child)]),
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
