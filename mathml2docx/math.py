"""Independent Presentation MathML to OMML conversion; no Office stylesheets."""

import re
import sys
import unicodedata
from collections import defaultdict, deque

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


def matching_fences(children):
    """Match sibling fence operators in one pass, including adjacent matrices."""
    pairs = {"(": ")", "[": "]", "{": "}", "⟨": "⟩", "|": "|", "‖": "‖"}
    stack = []
    matches = {}
    for index, child in enumerate(children):
        if math_name(child) != "mo":
            continue
        token = (child.text or "").strip()
        form = child.get("form")
        explicit = child.get("fence") == "true"
        if form == "postfix" or token in {")", "]", "}", "⟩"}:
            # A lone conditional bar in (A|B) is not an unmatched absolute-value
            # fence. Do not let it consume the enclosing delimiter's close.
            while stack and stack[-1][1] in {"|", "‖"} and token != stack[-1][1]:
                stack.pop()
        if stack and (
            (token == stack[-1][1] and form != "prefix")
            or (stack[-1][1] is None and explicit and form == "postfix")
        ):
            start, _ = stack.pop()
            matches[start] = index
        elif (explicit and form == "prefix") or (token in pairs and form != "postfix"):
            stack.append(
                (index, None if explicit and form == "prefix" else pairs.get(token))
            )
        elif form == "postfix" or token in pairs.values():
            stack.clear()
    return matches


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
        if (
            tag == "mrow"
            and len(children) == 2
            and math_name(children[0]) == "mo"
            and (children[0].text or "").strip() == "{"
            and children[0].get("stretchy") != "false"
            and math_name(children[1]) == "mtable"
        ):
            return [fenced("{", "", parts(children[1]))]

        def row_parts(items):
            ends = matching_fences(items)
            result = []
            index = 0
            while index < len(items):
                child = items[index]
                end = ends.get(index)
                if end is not None and (
                    child.get("stretchy") != "false"
                    or (tag == "mrow" and index == 0 and end == len(items) - 1)
                ):
                    result.append(
                        fenced(
                            (child.text or "").strip(),
                            (items[end].text or "").strip(),
                            row_parts(items[index + 1 : end]),
                        )
                    )
                    index = end + 1
                elif (
                    math_name(child) == "mo"
                    and (child.text or "").strip() == "{"
                    and child.get("stretchy") != "false"
                    and index + 1 < len(items)
                    and math_name(items[index + 1]) == "mtable"
                ):
                    # Older latex2mathml emits f(x)={ followed by a table in
                    # the same row instead of giving the cases its own mrow.
                    result.append(fenced("{", "", parts(items[index + 1])))
                    index += 2
                elif (
                    math_name(child) in {"munder", "mover", "munderover"}
                    and len(child)
                    and "".join(child[0].itertext()).strip()
                    in {"lim", "liminf", "limsup"}
                    and index + 1 < len(items)
                ):
                    result.append(
                        element(
                            "func",
                            element("fName", *parts(child)),
                            element("e", *parts(items[index + 1])),
                        )
                    )
                    index += 2
                else:
                    result.extend(parts(child))
                    index += 1
            return result

        return row_parts(children)
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


LATEX_OPERATORS = {
    "sum": "∑",
    "prod": "∏",
    "coprod": "∐",
    "bigcup": "⋃",
    "bigcap": "⋂",
    "bigvee": "⋁",
    "bigwedge": "⋀",
    "lim": "lim",
    "liminf": "liminf",
    "limsup": "limsup",
    "int": "∫",
    "iint": "∬",
    "iiint": "∭",
    "oint": "∮",
}
INTEGRALS = {"∫", "∬", "∭", "∮"}
OPERATOR_SYMBOLS = frozenset(LATEX_OPERATORS.values())
LATEX_COMMAND = re.compile(r"\\([A-Za-z]+|.)")
LATEX_LIMITS = re.compile(r"\s*\\(nolimits|limits)(?![A-Za-z])")


def _latex_operator_policies(source):
    """Handle limits per operator, even on backends lacking these directives.

    Only operator layout directives are removed before the backend parses LaTeX.
    Literal text groups and escaped commands are preserved. The backend still
    parses every mathematical argument, script and expression.
    """
    policies = defaultdict(deque)
    output = []
    cursor = copied = 0
    while cursor < len(source):
        if source[cursor] != "\\":
            symbol = source[cursor]
            if symbol in OPERATOR_SYMBOLS:
                policies[symbol].append("scripts" if symbol in INTEGRALS else "limits")
            cursor += 1
            continue
        token = LATEX_COMMAND.match(source, cursor)
        if token is None:
            cursor += 1
            continue
        command = token.group(1)
        end = token.end()
        if command in {"text", "mbox", "operatorname"}:
            brace = end
            while brace < len(source) and source[brace].isspace():
                brace += 1
            if brace < len(source) and source[brace] == "{":
                depth = 1
                cursor = brace + 1
                while cursor < len(source) and depth:
                    if source[cursor] == "\\":
                        cursor += 2
                        continue
                    if source[cursor] == "{":
                        depth += 1
                    elif source[cursor] == "}":
                        depth -= 1
                    cursor += 1
                continue
        if command in LATEX_OPERATORS:
            symbol = LATEX_OPERATORS[command]
            policy = "scripts" if symbol in INTEGRALS else "limits"
            directive = LATEX_LIMITS.match(source, end)
            while directive:
                policy = "scripts" if directive.group(1) == "nolimits" else "limits"
                output.append(source[copied:end])
                copied = directive.end()
                end = copied
                directive = LATEX_LIMITS.match(source, end)
            policies[symbol].append(policy)
        cursor = end
    output.append(source[copied:])
    return "".join(output), policies


def _group_latex_fence_scripts(root):
    """Keep (a+b)^2 editable as a grouped base, rather than a scripted ')' run.

    Some latex2mathml releases attach a script to the closing operator alone.
    This normalization is LaTeX-specific: explicit MathML retains its own bases.
    """
    pairs = {"(": ")", "[": "]", "{": "}", "⟨": "⟩", "|": "|", "‖": "‖"}
    for parent in reversed(list(root.iter())):
        if etree.QName(parent).localname not in {"math", "mrow", "mtd", "mstyle"}:
            continue
        stack = []
        for child in list(parent):
            name = etree.QName(child).localname
            scripted = name in {"msub", "msup", "msubsup"} and len(child)
            operator = child[0] if scripted else child
            if etree.QName(operator).localname != "mo":
                continue
            token = (operator.text or "").strip()
            form = operator.get("form")
            explicit = operator.get("fence") == "true"
            if form == "postfix" or token in {")", "]", "}", "⟩"}:
                while stack and stack[-1][1] in {"|", "‖"} and token != stack[-1][1]:
                    stack.pop()
            if stack and (
                (token == stack[-1][1] and form != "prefix")
                or (stack[-1][1] is None and explicit and form == "postfix")
            ):
                opening, _ = stack.pop()
                if scripted:
                    base = etree.Element("{" + etree.QName(parent).namespace + "}mrow")
                    start, end = parent.index(opening), parent.index(child)
                    for item in list(parent)[start:end]:
                        base.append(item)
                    base.append(operator)
                    child.insert(0, base)
            elif (explicit and form == "prefix") or (
                token in pairs and form != "postfix"
            ):
                stack.append(
                    (child, None if explicit and form == "prefix" else pairs.get(token))
                )
            elif token in pairs.values():
                stack.clear()


def latex_to_omml(source):
    """Convert LaTeX math via the optional MIT-licensed latex2mathml package."""
    # Ruff's oldest target is 3.7; the core package also supports early 3.6.
    if sys.version_info < (3, 6, 2):  # noqa: UP036
        raise ImportError(
            "LaTeX conversion requires Python >=3.6.2; HTML and MathML support Python >=3.6.0"
        )
    try:
        from latex2mathml.converter import convert as latex_to_mathml
    except ImportError as exc:
        raise ImportError("Install mathml2docx[latex] to convert LaTeX") from exc
    prepared, policies = _latex_operator_policies(source)
    converted = latex_to_mathml(prepared, display="block")
    root = etree.fromstring(
        converted.encode("utf-8"),
        etree.XMLParser(resolve_entities=False, no_network=True),
    )
    _group_latex_fence_scripts(root)
    layouts = {
        "msub": ("msub", "munder"),
        "munder": ("msub", "munder"),
        "msup": ("msup", "mover"),
        "mover": ("msup", "mover"),
        "msubsup": ("msubsup", "munderover"),
        "munderover": ("msubsup", "munderover"),
    }
    for base in root.iter():
        symbol = base.text
        if (
            etree.QName(base).localname not in {"mo", "mi"}
            or symbol not in OPERATOR_SYMBOLS
        ):
            continue
        policy = (
            policies[symbol].popleft()
            if policies[symbol]
            else "scripts"
            if symbol in INTEGRALS
            else "limits"
        )
        node = base.getparent()
        name = etree.QName(node).localname
        if name not in layouts or node[0] is not base:
            continue
        replacement = layouts[name][policy == "limits"]
        namespace = etree.QName(node).namespace
        node.tag = "{" + namespace + "}" + replacement if namespace else replacement
    return mathml_to_omml(etree.tostring(root, encoding="unicode"))
