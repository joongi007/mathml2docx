"""Independent Presentation MathML to OMML conversion; no Office stylesheets."""

import re
import sys
import unicodedata
from collections import defaultdict, deque

from docx.oxml import OxmlElement
from lxml import etree

from .math_styles import apply_math_style, math_style

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


def unicode_mathvariant(character):
    """Decode an already styled math character before applying token defaults.

    LaTeX backends commonly emit these characters without mathvariant. A plain
    mi italic default must not contradict their encoded mathematical meaning.
    Explicit/inherited mathvariant handling remains a separate input policy.
    """
    for variant, alphabet in LETTERLIKE.items():
        if character in alphabet.values():
            return variant
    name = unicodedata.name(character, "")
    for variant, prefix in sorted(
        UNICODE_VARIANTS.items(), key=lambda item: len(item[1]), reverse=True
    ):
        if name.startswith("MATHEMATICAL " + prefix + " "):
            return variant
    return None


class UnsupportedMathMLError(ValueError):
    """The input uses a MathML construct this converter cannot preserve."""


class MathMLFallbackWarning(UserWarning):
    """A formula was replaced with visible text or an external image."""


XML_WHITESPACE = " \t\n\r"
XML_SPACE_RUN = re.compile(r"[ \t\n\r]+")
STYLE_DEFAULTS = frozenset(
    {
        "linethickness",
        "bevelled",
        "numalign",
        "denomalign",
        "open",
        "close",
        "separators",
        "lquote",
        "rquote",
        "accent",
        "accentunder",
        "movablelimits",
        "stretchy",
        "form",
        "fence",
        "linebreak",
        "notation",
        "width",
        "height",
        "depth",
        "rowspan",
        "columnspan",
    }
)
# MathML 3 Appendix C: only dictionary entries carrying movablelimits.
MOVABLE_OPERATORS = frozenset("∑∏∐⋀⋁⋂⋃⨀⨁⨂⨃⨄⨅⨆⨇⨈⨉⨊⨐⨑⨒⨓⨔⫼⫿")
# MathML 3 Appendix C accents and legacy accepted bar/vector spellings.
ACCENT_OPERATORS = frozenset(
    "\"'^_`~¨ª¯²³´¸¹ºˆˇˉˊˋˍ˘˙˚˜˝˷̂̑‚‛„‟″‴‵‶‷‾⁗⃛⃜←→↔↚↛↜↝↞↟↠↢↣↤↦↩↪↫↬↭↮↶↷↹"
    "↼↽⇀⇁⇄⇆⇇⇉⇋⇌⇍⇎⇏⇐⇒⇔⇚⇛⇜⇝⇠⇢⇤⇥⇦⇨⇰⇴⇶⇷⇸⇹⇺⇻⇼⇽⇾⇿⎴⎵⏜⏝⏞⏟⏠⏡⟵⟶⟷⟸⟹⟺⟻⟼⟽⟾⟿⤀⤁⤂⤃⤄⤅⤆⤇"
    "⤌⤍⤎⤏⤐⤑⤔⤕⤖⤗⤘⤙⤚⤛⤜⤝⤞⤟⤠⤳⤺⤻⤼⤽⥂⥃⥄⥅⥆⥇⥈⥊⥋⥎⥐⥒⥓⥚⥛⥞⥟⥢⥤⥦⥧⥨⥩⥪⥫⥬⥭⥰⥱⥲⥳⥴⥵⥶⥷⥸⥹⥺⥻⥼⥽"
    "―⃗"
)
BAR_ACCENTS = frozenset("_¯‾―ˉˍ")
FIXED_ARITIES = {
    "mfrac": 2,
    "mroot": 2,
    "msub": 2,
    "msup": 2,
    "msubsup": 3,
    "munder": 2,
    "mover": 2,
    "munderover": 3,
    "mspace": 0,
    "none": 0,
    "mprescripts": 0,
    "mglyph": 0,
    "maligngroup": 0,
    "malignmark": 0,
}
MINIMUM_ARITIES = {"semantics": 1, "maction": 1, "mlabeledtr": 1, "mlongdiv": 3}


def normalize_token(value):
    """MathML collapses XML whitespace, preserving NBSP and mathematical spaces."""
    return XML_SPACE_RUN.sub(" ", value.strip(XML_WHITESPACE))


def attribute(node, inherited, name, default=None):
    """Local attributes override scoped math/mstyle defaults without leaking."""
    return node.get(name, inherited.get("_defaults", {}).get(name, default))


def math_context(node, inherited=None):
    tag = math_name(node)
    result = dict(inherited or {})
    defaults = dict(result.get("_defaults", {}))
    if tag in {"math", "mstyle"}:
        defaults.update(
            {k: node.get(k) for k in STYLE_DEFAULTS if node.get(k) is not None}
        )
    result["_defaults"] = defaults
    if node.get("mathvariant") is not None:
        result["mathvariant"] = node.get("mathvariant")
    if tag == "math":
        result["_displaystyle"] = node.get("display") == "block"
    elif tag == "mtable":
        result["_displaystyle"] = False
    if node.get("displaystyle") is not None:
        result["_displaystyle"] = node.get("displaystyle") == "true"
    if node.get("dir") == "rtl":
        raise UnsupportedMathMLError(
            "Right-to-left mathematical layout requires a fallback renderer"
        )
    result["_css"] = math_style(node, result.get("_css", {}))
    return result


def validate_structure(root):
    """Validate known arities everywhere before any unsupported branch can recover.

    Annotation payloads are deliberately opaque; foreign or unsupported wrappers
    do not conceal malformed supported MathML in their descendants.
    """
    for node in root.iter():
        if any(
            etree.QName(parent).namespace in {None, MATHML_NS}
            and etree.QName(parent).localname in {"annotation", "annotation-xml"}
            for parent in node.iterancestors()
        ):
            continue
        name = etree.QName(node)
        if name.namespace not in {None, MATHML_NS}:
            continue
        tag = name.localname
        if tag in {"annotation", "annotation-xml"}:
            continue
        if tag in FIXED_ARITIES and len(node) != FIXED_ARITIES[tag]:
            raise ValueError(f"{tag} expects {FIXED_ARITIES[tag]} children")
        if tag in MINIMUM_ARITIES and len(node) < MINIMUM_ARITIES[tag]:
            raise ValueError(f"{tag} expects at least {MINIMUM_ARITIES[tag]} children")
        if tag in {"none", "mprescripts", "mspace"} and normalize_token(
            node.text or ""
        ):
            raise ValueError(f"MathML {tag} must be empty")
        if tag == "math" and node is not root:
            raise ValueError("MathML math elements cannot be nested")
        if tag == "mmultiscripts":
            _multiscripts(node)


def _multiscripts(node):
    """Parse script columns independently of conversion and support limits."""
    children = list(node)
    names = [
        etree.QName(child).localname
        if etree.QName(child).namespace in {None, MATHML_NS}
        else ""
        for child in children
    ]
    if not children or names[0] in {"none", "mprescripts"}:
        raise ValueError("mmultiscripts requires a base expression")
    post, pre = [], []
    current = post
    for child, name in zip(children[1:], names[1:]):
        if name == "mprescripts" and etree.QName(child).namespace in {None, MATHML_NS}:
            if current is pre or len(child) or normalize_token(child.text or ""):
                raise ValueError("mmultiscripts allows one empty mprescripts marker")
            current = pre
        else:
            current.append(child)
    if len(post) % 2 or len(pre) % 2:
        raise ValueError("mmultiscripts requires subscript/superscript pairs")
    return children[0], post, pre


def escape_string(value, left, right):
    """Escape delimiters simultaneously, including multi-character custom quotes."""
    delimiters = sorted({q for q in (left, right, "\\") if q}, key=len, reverse=True)
    pattern = re.compile("|".join(re.escape(q) for q in delimiters))
    return left + pattern.sub(lambda match: "\\" + match.group(), value) + right


def element(name, *children, **attributes):
    node = OxmlElement("m:" + name)
    for key, value in attributes.items():
        node.set(
            "{http://schemas.openxmlformats.org/officeDocument/2006/math}" + key,
            str(value),
        )
    node.extend(children)
    return node


def text(value, variant=None, normal_text=False, literal=False):
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
    properties = element("rPr", element("scr", val=script), element("sty", val=style))
    if literal:
        # Unlike nor, lit suppresses mathematical spacing without erasing the
        # encoded character's alphabet/style when Word imports the equation.
        properties.insert(0, element("lit", val="1"))
    return element("r", properties, node)


def fenced(begin, end, content, grow=True):
    if len(begin) > 1 or len(end) > 1:
        raise UnsupportedMathMLError("OMML fences require zero or one character")
    properties = [element("begChr", val=begin), element("endChr", val=end)]
    if not grow:
        properties.append(element("grow", val="0"))
    return element(
        "d",
        element("dPr", *properties),
        element("e", *content),
    )


def parse_mathml(source):
    """Parse one MathML root without DTDs, entities, or network access."""
    if not isinstance(source, str):
        raise TypeError("MathML must be a string")
    if "<!DOCTYPE" in source.upper() or "<!ENTITY" in source.upper():
        raise ValueError("DTD and entity declarations are not allowed")
    parser = etree.XMLParser(
        encoding="utf-8",
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
    return root


def mathml_to_omml(source, *, target="word"):
    """Return an oMath element. Unsupported structures raise instead of losing data."""
    root = parse_mathml(source)
    if target not in {"word", "libreoffice"}:
        raise ValueError("Math target must be word or libreoffice")
    validate_structure(root)
    result = element("oMath", *convert(root, {"_target": target}))
    if target == "libreoffice":
        for node in root.iter():
            if any(
                etree.QName(p).localname in {"annotation", "annotation-xml"}
                for p in node.iterancestors()
            ):
                continue
            if etree.QName(node).localname in {"annotation", "annotation-xml"}:
                continue
            tag = math_name(node)
            if tag in {"mphantom", "ms"} or (
                tag == "mfrac" and node.get("bevelled") == "true"
            ):
                raise UnsupportedMathMLError(
                    "LibreOffice may change phantom spacing, bevelled fractions or string quotes; use an image fallback"
                )
            if tag == "menclose" and set(node.get("notation", "longdiv").split()) - {
                "radical"
            }:
                raise UnsupportedMathMLError(
                    "LibreOffice does not reliably display OMML enclosures; use an image fallback"
                )
            if tag == "mmultiscripts":
                children = list(node)
                markers = [
                    i
                    for i, child in enumerate(children)
                    if math_name(child) == "mprescripts"
                ]
                if markers and any(
                    math_name(child) == "none" for child in children[markers[0] + 1 :]
                ):
                    raise UnsupportedMathMLError(
                        "LibreOffice displays empty prescripts as placeholders; use an image fallback"
                    )
    if target == "libreoffice":
        # Writer's importer ignores sty=p on identifiers in some versions.
        # nor expresses the same upright intent in the supported ODF importer.
        namespace = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}
        for properties in result.xpath(
            './/m:rPr[m:scr[@m:val="roman"] and m:sty[@m:val="p"] and not(m:nor)]',
            namespaces=namespace,
        ):
            properties.insert(0, element("nor", val="1"))
    return result


def math_name(node):
    qualified = etree.QName(node)
    if qualified.namespace not in {None, MATHML_NS}:
        raise UnsupportedMathMLError(
            "Unsupported MathML namespace: " + qualified.namespace
        )
    return qualified.localname


def space_like(node):
    tag = math_name(node)
    return tag in {"mtext", "mspace", "maligngroup", "malignmark"} or (
        tag in {"mrow", "mstyle", "mphantom", "mpadded"}
        and all(space_like(child) for child in node)
    )


def operator_core(node, inherited):
    """Return an embellished operator's actual mo and scoped defaults, if any."""
    context = math_context(node, inherited)
    tag = math_name(node)
    if tag == "mo":
        return node, context
    if tag in {
        "msub",
        "msup",
        "msubsup",
        "munder",
        "mover",
        "munderover",
        "mmultiscripts",
        "mfrac",
        "semantics",
    } and len(node):
        return operator_core(node[0], context)
    if tag in {"mrow", "mstyle", "mphantom", "mpadded"}:
        operators = [child for child in node if not space_like(child)]
        if len(operators) == 1:
            return operator_core(operators[0], context)
    return None


def matching_fences(children, inherited=None):
    """Match sibling fence operators in one pass, including adjacent matrices."""
    pairs = {"(": ")", "[": "]", "{": "}", "⟨": "⟩", "|": "|", "‖": "‖"}
    stack = []
    matches = {}
    for index, child in enumerate(children):
        if math_name(child) != "mo":
            continue
        if attribute(child, inherited or {}, "fence") == "false":
            continue
        token = normalize_token(child.text or "")
        form = attribute(child, inherited or {}, "form")
        explicit = attribute(child, inherited or {}, "fence") == "true"
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
    """Resolve scoped defaults and CSS once, then emit the node's own notation."""
    inherited = math_context(node, inherited)
    tag = math_name(node)
    if tag not in {
        "math",
        "mrow",
        "mstyle",
        "mpadded",
        "semantics",
        "annotation",
        "annotation-xml",
        "mi",
        "mn",
        "mo",
        "mtext",
        "ms",
        "mspace",
        "mfrac",
        "msup",
        "msub",
        "msubsup",
        "mmultiscripts",
        "menclose",
        "msqrt",
        "mroot",
        "mfenced",
        "munder",
        "mover",
        "munderover",
        "mtable",
        "mtd",
        "mphantom",
    }:
        raise UnsupportedMathMLError("Unsupported MathML element: " + tag)
    if tag in {"mo", "mspace"} and attribute(
        node, inherited, "linebreak", "auto"
    ) not in {"auto", "nobreak"}:
        raise UnsupportedMathMLError("MathML line breaks are unsupported")
    if inherited.get("_target") == "libreoffice":
        if tag in {"mphantom", "ms"} or (
            tag == "mfrac" and attribute(node, inherited, "bevelled") == "true"
        ):
            raise UnsupportedMathMLError(
                "LibreOffice may change phantom spacing, bevelled fractions or string quotes; use an image fallback"
            )
        if tag == "menclose" and set(
            attribute(node, inherited, "notation", "longdiv").split()
        ) - {"radical"}:
            raise UnsupportedMathMLError(
                "LibreOffice does not reliably display OMML enclosures; use an image fallback"
            )
    result = _convert(node, inherited)
    # Transparent containers must not overwrite explicit descendant CSS. A
    # compound's control properties style its own glyphs, not its child runs.
    if tag not in {
        "math",
        "mrow",
        "mstyle",
        "mpadded",
        "semantics",
        "annotation",
        "annotation-xml",
        "mtd",
        "munder",
        "mover",
        "munderover",
    }:
        for part in result:
            if tag == "mmultiscripts" and etree.QName(part).localname not in {
                "sPre",
                "sSub",
                "sSup",
                "sSubSup",
            }:
                continue
            if (
                tag == "menclose"
                and not attribute(node, inherited, "notation", "longdiv").split()
            ):
                continue
            apply_math_style(part, inherited["_css"])
    return result


def _convert(node, inherited):
    tag = math_name(node)
    children = list(node)

    def parts(child, script=False):
        context = inherited
        if script:
            context = dict(inherited, _displaystyle=False)
        return convert(child, context)

    def group(index, name, script=False):
        return element(name, *parts(children[index], script))

    def styled(part, context=None):
        return apply_math_style(part, (context or inherited)["_css"])

    def attr(name, default=None):
        return attribute(node, inherited, name, default)

    def arity(count):
        if len(children) != count:
            raise ValueError(f"{tag} expects {count} children")

    if tag not in {"mi", "mn", "mo", "mtext", "ms", "annotation", "annotation-xml"}:
        if normalize_token(node.text or "") or any(
            normalize_token(c.tail or "") for c in children
        ):
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
            and attribute(children[0], inherited, "stretchy") != "false"
            and math_name(children[1]) == "mtable"
        ):
            parts(children[0])  # Validate operators even when used as delimiters.
            return [styled(fenced("{", "", parts(children[1])))]

        def row_parts(items):
            ends = matching_fences(items, inherited)
            result = []
            index = 0
            while index < len(items):
                child = items[index]
                end = ends.get(index)
                if end is not None and (
                    attribute(child, inherited, "stretchy") != "false"
                    or (tag == "mrow" and index == 0 and end == len(items) - 1)
                ):
                    parts(child)
                    parts(items[end])
                    result.append(
                        styled(
                            fenced(
                                normalize_token(child.text or ""),
                                normalize_token(items[end].text or ""),
                                row_parts(items[index + 1 : end]),
                                grow=attribute(child, inherited, "stretchy") != "false"
                                and attribute(items[end], inherited, "stretchy")
                                != "false",
                            ),
                            math_context(child, inherited),
                        )
                    )
                    index = end + 1
                elif (
                    math_name(child) == "mo"
                    and (child.text or "").strip() == "{"
                    and attribute(child, inherited, "stretchy") != "false"
                    and index + 1 < len(items)
                    and math_name(items[index + 1]) == "mtable"
                ):
                    # Older latex2mathml emits f(x)={ followed by a table in
                    # the same row instead of giving the cases its own mrow.
                    parts(child)
                    result.append(styled(fenced("{", "", parts(items[index + 1]))))
                    index += 2
                elif (
                    math_name(child) in {"munder", "mover", "munderover"}
                    and len(child)
                    and "".join(child[0].itertext()).strip()
                    in {"lim", "liminf", "limsup"}
                    and index + 1 < len(items)
                ):
                    result.append(
                        styled(
                            element(
                                "func",
                                element("fName", *parts(child)),
                                element("e", *parts(items[index + 1])),
                            )
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
        value = normalize_token(node.text or "")
        if tag == "ms":
            value = escape_string(value, attr("lquote", '"'), attr("rquote", '"'))
        variant = inherited.get(
            "mathvariant", "italic" if tag == "mi" and len(value) == 1 else "normal"
        )
        if value:
            runs = []
            current_properties = None
            for character in value:
                # Encoded mathematical alphabets carry their own semantics:
                # surrounding mathvariant declarations must not restyle them
                # (MathML 3 sections 3.2.2 and 7.5). Apply explicit variants
                # only to ordinary characters, preserving mixed token runs.
                encoded = unicode_mathvariant(character)
                effective = encoded or variant
                rendered = (
                    character
                    if encoded or "mathvariant" not in inherited
                    else variant_characters(character, variant)
                )
                normal = tag in {"mtext", "ms"} and effective == "normal"
                literal = tag in {"mtext", "ms"} and not normal
                properties = (effective, normal, literal)
                if runs and properties == current_properties:
                    runs[-1][-1].text += rendered
                else:
                    runs.append(
                        text(rendered, effective, normal_text=normal, literal=literal)
                    )
                    current_properties = properties
            return runs
        return [
            text(
                value,
                variant,
                normal_text=tag in {"mtext", "ms"} and variant == "normal",
            )
        ]
    if tag == "mspace":
        if attr("linebreak", "auto") not in {"auto", "nobreak"}:
            raise UnsupportedMathMLError("MathML line breaks are unsupported")
        for name in ("height", "depth"):
            if attr(name, "0") not in {"0", "0em", "0px", "0pt"}:
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
        width = attr("width", "0")
        if width not in spaces:
            raise UnsupportedMathMLError("Unsupported mspace width: " + width)
        return (
            [text(spaces[width], "normal", normal_text=True)] if spaces[width] else []
        )
    if tag == "mfrac":
        arity(2)
        thickness = attr("linethickness", "medium")
        if thickness not in {"medium", "0", "0px", "0pt", "0em"}:
            raise UnsupportedMathMLError(
                "Custom fraction line thickness is unsupported"
            )
        fraction_type = (
            "noBar"
            if thickness != "medium"
            else "skw"
            if attr("bevelled") == "true"
            else "bar"
        )
        return [
            element(
                "f",
                element("fPr", element("type", val=fraction_type)),
                group(0, "num", script=True),
                group(1, "den", script=True),
            )
        ]
    if tag in {"msup", "msub", "msubsup"}:
        arity(3 if tag == "msubsup" else 2)
        if tag == "msubsup":
            return [
                element(
                    "sSubSup",
                    group(0, "e"),
                    group(1, "sub", script=True),
                    group(2, "sup", script=True),
                )
            ]
        return [
            element(
                "sSup" if tag == "msup" else "sSub",
                group(0, "e"),
                group(1, "sup" if tag == "msup" else "sub", script=True),
            )
        ]
    if tag == "mmultiscripts":
        base_node, post, pre = _multiscripts(node)
        if len(post) > 2 or len(pre) > 2:
            raise UnsupportedMathMLError(
                "Multiple script columns require a fallback renderer"
            )

        def script(child, name):
            if math_name(child) == "none":
                if len(child) or (child.text or "").strip():
                    raise ValueError("MathML none must be empty")
                return element(name)
            return element(name, *parts(child, script=True))

        base = parts(base_node)
        if post:
            has_sub, has_sup = [math_name(child) != "none" for child in post]
            if has_sub and has_sup:
                base = [
                    styled(
                        element(
                            "sSubSup",
                            element("e", *base),
                            script(post[0], "sub"),
                            script(post[1], "sup"),
                        )
                    )
                ]
            elif has_sub or has_sup:
                base = [
                    styled(
                        element(
                            "sSub" if has_sub else "sSup",
                            element("e", *base),
                            script(
                                post[0] if has_sub else post[1],
                                "sub" if has_sub else "sup",
                            ),
                        )
                    )
                ]
        if pre:
            base = [
                element(
                    "sPre",
                    script(pre[0], "sub"),
                    script(pre[1], "sup"),
                    element("e", *base),
                )
            ]
        return base
    if tag == "menclose":
        notations = set(attr("notation", "longdiv").split())
        sides = {
            "top": "hideTop",
            "bottom": "hideBot",
            "left": "hideLeft",
            "right": "hideRight",
        }
        strikes = {
            "horizontalstrike": "strikeH",
            "verticalstrike": "strikeV",
            "updiagonalstrike": "strikeBLTR",
            "downdiagonalstrike": "strikeTLBR",
        }
        supported = set(sides) | set(strikes) | {"box", "radical", "actuarial"}
        if notations - supported:
            raise UnsupportedMathMLError(
                "Unsupported menclose notation: "
                + " ".join(sorted(notations - supported))
            )
        base = [part for child in children for part in parts(child)]
        if "radical" in notations:
            base = [
                styled(
                    element(
                        "rad",
                        element("radPr", element("degHide", val="1")),
                        element("deg"),
                        element("e", *base),
                    )
                )
            ]
        if notations - {"radical"}:
            visible = set(sides) if "box" in notations else set(sides) & notations
            if "actuarial" in notations:
                visible.update({"top", "right"})
            properties = [
                element(name, val="0" if side in visible else "1")
                for side, name in sides.items()
            ]
            properties.extend(
                element(name, val="1")
                for notation, name in strikes.items()
                if notation in notations
            )
            base = [
                element(
                    "borderBox",
                    element("borderBoxPr", *properties),
                    element("e", *base),
                )
            ]
        return base
    if tag in {"msqrt", "mroot"}:
        if tag == "mroot":
            arity(2)
            return [element("rad", group(1, "deg", script=True), group(0, "e"))]
        return [
            element(
                "rad",
                element("radPr", element("degHide", val="1")),
                element("deg"),
                element("e", *[part for child in children for part in parts(child)]),
            )
        ]
    if tag == "mfenced":
        separators = XML_SPACE_RUN.sub("", attr("separators", ","))
        fence_parts = []
        for index, child in enumerate(children):
            if index and separators:
                fence_parts.append(
                    styled(
                        text(
                            separators[min(index - 1, len(separators) - 1)],
                            normal_text=True,
                        )
                    )
                )
            fence_parts.extend(convert(child, inherited))
        return [
            fenced(
                normalize_token(attr("open", "(")),
                normalize_token(attr("close", ")")),
                fence_parts,
            )
        ]
    if tag in {"munder", "mover", "munderover"}:
        arity(3 if tag == "munderover" else 2)
        base = parts(children[0])
        core = operator_core(children[0], inherited)
        movable = False
        if core is not None:
            operator, context = core
            movable = (
                attribute(
                    operator,
                    context,
                    "movablelimits",
                    "true"
                    if normalize_token(operator.text or "") in MOVABLE_OPERATORS
                    else "false",
                )
                == "true"
            )
        if movable and not inherited.get("_displaystyle", False):
            if tag == "munderover":
                return [
                    styled(
                        element(
                            "sSubSup",
                            element("e", *base),
                            group(1, "sub", script=True),
                            group(2, "sup", script=True),
                        )
                    )
                ]
            return [
                styled(
                    element(
                        "sSup" if tag == "mover" else "sSub",
                        element("e", *base),
                        group(1, "sup" if tag == "mover" else "sub", script=True),
                    )
                )
            ]

        def attach(base_parts, index, above):
            script_node = children[index]
            core = operator_core(script_node, inherited)
            default = "false"
            if core is not None:
                operator, context = core
                default = attribute(
                    operator,
                    context,
                    "accent",
                    "true"
                    if normalize_token(operator.text or "") in ACCENT_OPERATORS
                    else "false",
                )
            is_accent = attr("accent" if above else "accentunder", default) == "true"
            script_parts = parts(script_node, script=not is_accent)
            if not is_accent:
                return styled(
                    element(
                        "limUpp" if above else "limLow",
                        element("e", *base_parts),
                        element("lim", *script_parts),
                    )
                )
            # A single converted token can be represented by OMML's character
            # accent. Never flatten radicals, hidden content, scripts or unknown
            # wrappers into their descendant text.
            if len(script_parts) != 1 or etree.QName(script_parts[0]).localname != "r":
                raise UnsupportedMathMLError(
                    "Structured MathML accents require a fallback renderer"
                )
            token = script_parts[0].find(
                "{http://schemas.openxmlformats.org/officeDocument/2006/math}t"
            )
            accent = token.text or "" if token is not None else ""
            if len(accent) != 1:
                raise UnsupportedMathMLError("OMML accents require one character")
            context = math_context(script_node, inherited)
            if core is not None:
                context = core[1]
            if accent in BAR_ACCENTS:
                if (
                    core is not None
                    and attribute(core[0], core[1], "stretchy") == "false"
                ):
                    raise UnsupportedMathMLError(
                        "Nonstretching line accents require a fallback renderer"
                    )
                return styled(
                    element(
                        "bar",
                        element("barPr", element("pos", val="top" if above else "bot")),
                        element("e", *base_parts),
                    ),
                    context,
                )
            if not above:
                raise UnsupportedMathMLError(
                    "Only line accents below expressions are supported"
                )
            return styled(
                element(
                    "acc",
                    element("accPr", element("chr", val=accent)),
                    element("e", *base_parts),
                ),
                context,
            )

        if tag != "mover":
            base = [attach(base, 1, False)]
        if tag != "munder":
            base = [attach(base, 2 if tag == "munderover" else 1, True)]
        return base
    if tag == "mtable":
        if not children:
            raise UnsupportedMathMLError(
                "Empty MathML tables require a fallback renderer"
            )
        rows = []
        for row in children:
            if math_name(row) != "mtr":
                raise UnsupportedMathMLError("Only mtr rows are supported in mtable")
            if normalize_token(row.text or "") or any(
                normalize_token(cell.tail or "") for cell in row
            ):
                raise ValueError("Text must be inside a MathML token element")
            if any(math_name(cell) != "mtd" for cell in row):
                raise ValueError("MathML matrix rows require mtd cells")
            if not len(row):
                raise UnsupportedMathMLError(
                    "Empty MathML rows require a fallback renderer"
                )
            row_context = math_context(row, inherited)
            rows.append(
                element(
                    "mr", *[element("e", *convert(cell, row_context)) for cell in row]
                )
            )
        widths = {len(row) for row in children}
        if len(widths) > 1:
            raise UnsupportedMathMLError(
                "Ragged MathML tables require a fallback renderer"
            )
        return [element("m", *rows)]
    if tag == "mtd":
        if any(attr(name, "1") != "1" for name in ("rowspan", "columnspan")):
            raise UnsupportedMathMLError(
                "Spanning MathML cells require a fallback renderer"
            )
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


def _reject_unresolved_latex(root):
    """Do not mistake backend passthrough control sequences for identifiers.

    Explicit mtext/ms content and real backslash operators remain literal. This
    validation belongs to the LaTeX adapter, not to user-supplied MathML tokens.
    """
    for node in root.iter():
        if etree.QName(node).localname not in {"mi", "mo"}:
            continue
        token = normalize_token(node.text or "")
        if re.fullmatch(r"\\[A-Za-z]+", token):
            raise UnsupportedMathMLError(
                "Unresolved LaTeX command: "
                + token
                + ". Check the input or backend support."
            )


def latex_to_mathml(source):
    """Normalize optional LaTeX backend output before the shared MathML pipeline."""
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
    _reject_unresolved_latex(root)
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
    return etree.tostring(root, encoding="unicode")


def latex_to_omml(source, *, target="word"):
    """Convert LaTeX math via the optional MIT-licensed latex2mathml package."""
    return mathml_to_omml(latex_to_mathml(source), target=target)
