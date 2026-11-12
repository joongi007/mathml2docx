"""Read generated DOCX semantics without importing the converter or python-docx.

The representation deliberately ignores ZIP timestamps, relationship IDs and run
partitioning. It retains mathematical roles, delimiters, fraction type, matrix
dimensions, phantom dimensions and selected document formatting/relationships.
It is a structural oracle, not a Word layout renderer.
"""

import hashlib
import posixpath
import re
import unicodedata
from xml.etree import ElementTree as ET
from zipfile import ZipFile

NS = {
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}


def value(node, path, default=None, prefix="w"):
    prop = node.find(path, NS)
    return default if prop is None else prop.get("{" + NS[prefix] + "}val", default)


def enabled(node, path, default=False, prefix="w"):
    prop = node.find(path, NS)
    if prop is None:
        return default
    return prop.get("{" + NS[prefix] + "}val", "1") not in {"0", "false", "off"}


def math_alphabet(value):
    """Normalize only equivalent math alphabets, never spacing or other symbols."""
    letterlike = "ℂℍℕℙℚℝℤℭℌℑℜℨℬℰℱℋℐℒℳℛℯℊℴℎ"
    return "".join(
        unicodedata.normalize("NFKC", char)
        if 0x1D400 <= ord(char) <= 0x1D7FF or char in letterlike
        else char
        for char in value
    )


def math_run_format(run):
    properties = {}
    for name, tag in [("color", "color"), ("size_half_points", "sz")]:
        setting = value(run, "w:rPr/w:" + tag)
        if setting is not None:
            properties[name] = setting
    fonts = run.find("w:rPr/w:rFonts", NS)
    if fonts is not None:
        for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
            setting = fonts.get("{" + NS["w"] + "}" + slot)
            if setting is not None:
                properties["font_" + slot] = setting
    for name, tag in [("bold", "b"), ("italic", "i")]:
        if run.find("w:rPr/w:" + tag, NS) is not None:
            properties[name] = enabled(run, "w:rPr/w:" + tag)
    return properties


def effective_math_variant(run, char):
    """Read equivalent Unicode/OMML math styles without discarding distinctions."""
    normal = enabled(run, "m:rPr/m:nor", prefix="m")
    script = value(run, "m:rPr/m:scr", "roman", "m")
    style = value(run, "m:rPr/m:sty", "p" if normal else "i", "m")
    for characters, family, variant in [
        ("ℂℍℕℙℚℝℤ", "double-struck", "p"),
        ("ℭℌℑℜℨ", "fraktur", "p"),
        ("ℬℰℱℋℐℒℳℛℯℊℴ", "script", "p"),
        ("ℎ", "roman", "i"),
    ]:
        if char in characters:
            return {"script": family, "style": variant, "normal": normal}
    name = unicodedata.name(char, "")
    if name.startswith("MATHEMATICAL "):
        for prefix, family, variant in [
            ("SANS-SERIF BOLD ITALIC", "sans-serif", "bi"),
            ("SANS-SERIF BOLD", "sans-serif", "b"),
            ("SANS-SERIF ITALIC", "sans-serif", "i"),
            ("BOLD SCRIPT", "script", "b"),
            ("BOLD FRAKTUR", "fraktur", "b"),
            ("BOLD ITALIC", "roman", "bi"),
            ("DOUBLE-STRUCK", "double-struck", "p"),
            ("SANS-SERIF", "sans-serif", "p"),
            ("MONOSPACE", "monospace", "p"),
            ("FRAKTUR", "fraktur", "p"),
            ("SCRIPT", "script", "p"),
            ("BOLD", "roman", "b"),
            ("ITALIC", "roman", "i"),
        ]:
            if name.startswith("MATHEMATICAL " + prefix + " "):
                script, style = family, variant
                break
    return {"script": script, "style": style, "normal": normal}


def math_inline(node, display=False, alignment=None):
    result = {"math": math_sequence(node)}
    if display:
        result.update(display=True, math_alignment=alignment)
    formatted = []
    for run in node.findall(".//m:r", NS):
        properties = math_run_format(run)
        for char in "".join(t.text or "" for t in run.findall("m:t", NS)):
            variant = effective_math_variant(run, char)
            token = math_alphabet(char)
            if (
                formatted
                and formatted[-1]["format"] == properties
                and formatted[-1]["variant"] == variant
            ):
                formatted[-1]["text"] += token
            else:
                formatted.append(
                    {"text": token, "format": properties, "variant": variant}
                )
    result["math_runs"] = formatted
    return result


def math_content(node):
    """Read a whole-equation hyperlink without losing its mathematical result.

    Word can replace a HYPERLINK field inside oMath with a hyperlink element
    inside that same oMath. Both express a link over the entire equation. Fields
    spanning partial results or containing other/nested instructions are rejected.
    """
    children = list(node)
    hyperlinks = [
        child for child in children if child.tag == "{" + NS["w"] + "}hyperlink"
    ]
    field_tags = {"{" + NS["w"] + "}fldChar", "{" + NS["w"] + "}instrText"}
    fields = [child for child in node.iter() if child.tag in field_tags]
    if hyperlinks:
        if len(children) != 1 or len(hyperlinks) != 1 or fields:
            raise AssertionError(
                "Oracle requires a whole-equation, unnested math hyperlink"
            )
        link = hyperlinks[0]
        if any(
            child.tag == "{" + NS["w"] + "}hyperlink" for child in list(link.iter())[1:]
        ):
            raise AssertionError("Nested math hyperlinks are unsupported")
        return list(link), link
    if not fields:
        return children, None

    def event(run):
        if run.tag != "{" + NS["m"] + "}r":
            return None
        content = [
            child
            for child in run
            if child.tag not in {"{" + NS["m"] + "}rPr", "{" + NS["w"] + "}rPr"}
        ]
        if content and all(
            child.tag == "{" + NS["w"] + "}instrText" for child in content
        ):
            return "instruction", "".join(child.text or "" for child in content)
        if len(content) == 1 and content[0].tag == "{" + NS["w"] + "}fldChar":
            return content[0].get("{" + NS["w"] + "}fldCharType"), None
        if any(child.tag in field_tags for child in content):
            raise AssertionError("Mixed field instructions and mathematical result")
        return None

    events = [event(child) for child in children]
    if not events or events[0] != ("begin", None) or events[-1] != ("end", None):
        raise AssertionError("Malformed mathematical HYPERLINK field boundaries")
    separators = [
        index for index, item in enumerate(events) if item == ("separate", None)
    ]
    if len(separators) != 1:
        raise AssertionError("Mathematical HYPERLINK field requires one separator")
    separator = separators[0]
    instructions = events[1:separator]
    if not instructions or any(
        item is None or item[0] != "instruction" for item in instructions
    ):
        raise AssertionError("Malformed mathematical HYPERLINK field instructions")
    body = children[separator + 1 : -1]
    if any(
        child.tag in field_tags or child.tag == "{" + NS["w"] + "}hyperlink"
        for item in body
        for child in item.iter()
    ):
        raise AssertionError("Nested mathematical hyperlink fields are unsupported")
    code = "".join(item[1] for item in instructions)
    match = re.fullmatch(
        r'\s*HYPERLINK\s+(?:(\\l)\s+)?"((?:[^"\\]|\\["\\])*)"\s*', code, re.I
    )
    if match is None or not match.group(2):
        raise AssertionError(
            "Unsupported or malformed mathematical field code: " + code
        )
    target = re.sub(r'\\(["\\])', r"\1", match.group(2))
    return body, ("#" if match.group(1) else "") + target


def math_sequence(nodes):
    if getattr(nodes, "tag", None) == "{" + NS["m"] + "}oMath":
        nodes, _ = math_content(nodes)
    result = []
    for node in nodes:
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "r":
            # Unicode mathematical alphabets and character+mathvariant are
            # equivalent for this role comparison; explicit font checks are
            # separate so normalization cannot conceal lost mathematical style.
            text = math_alphabet("".join(n.text or "" for n in node.findall("m:t", NS)))
            if not text.strip():
                continue
            if result and isinstance(result[-1], str):
                result[-1] += text
            else:
                result.append(text)
            continue
        if tag == "f":
            result.append(
                {
                    "fraction": [
                        math_sequence(node.find("m:num", NS)),
                        math_sequence(node.find("m:den", NS)),
                    ],
                    "type": value(node, "m:fPr/m:type", "bar", "m"),
                }
            )
        elif tag in {"sSup", "sSub", "sSubSup", "sPre", "limLow", "limUpp", "func"}:
            role, args = {
                "sSup": ("sup", ["e", "sup"]),
                "sSub": ("sub", ["e", "sub"]),
                "sSubSup": ("subsup", ["e", "sub", "sup"]),
                "sPre": ("prescript", ["e", "sub", "sup"]),
                "limLow": ("lower", ["e", "lim"]),
                "limUpp": ("upper", ["e", "lim"]),
                "func": ("function", ["fName", "e"]),
            }[tag]
            result.append(
                {role: [math_sequence(node.find("m:" + arg, NS)) for arg in args]}
            )
        elif tag == "rad":
            base = math_sequence(node.find("m:e", NS))
            result.append(
                {"sqrt": base}
                if enabled(node, "m:radPr/m:degHide", prefix="m")
                else {"root": [math_sequence(node.find("m:deg", NS)), base]}
            )
        elif tag == "d":
            args = node.findall("m:e", NS)
            if len(args) != 1:
                raise AssertionError("Oracle expects a single delimiter argument")
            result.append(
                {
                    "fence": {
                        "open": value(node, "m:dPr/m:begChr", "(", "m"),
                        "close": value(node, "m:dPr/m:endChr", ")", "m"),
                        "body": math_sequence(args[0]),
                    }
                }
            )
        elif tag == "m":
            result.append(
                {
                    "matrix": [
                        [math_sequence(cell) for cell in row.findall("m:e", NS)]
                        for row in node.findall("m:mr", NS)
                    ]
                }
            )
        elif tag == "acc":
            result.append(
                {
                    "accent": {
                        "char": value(node, "m:accPr/m:chr", prefix="m"),
                        "body": math_sequence(node.find("m:e", NS)),
                    }
                }
            )
        elif tag == "bar":
            result.append(
                {
                    "bar": {
                        "position": value(node, "m:barPr/m:pos", "bot", "m"),
                        "body": math_sequence(node.find("m:e", NS)),
                    }
                }
            )
        elif tag == "borderBox":
            result.append(
                {
                    "enclosure": {
                        "body": math_sequence(node.find("m:e", NS)),
                        "sides": [
                            side
                            for side, prop in [
                                ("top", "hideTop"),
                                ("bottom", "hideBot"),
                                ("left", "hideLeft"),
                                ("right", "hideRight"),
                            ]
                            if not enabled(node, "m:borderBoxPr/m:" + prop, prefix="m")
                        ],
                        "strikes": [
                            kind
                            for kind, prop in [
                                ("horizontal", "strikeH"),
                                ("vertical", "strikeV"),
                                ("up", "strikeBLTR"),
                                ("down", "strikeTLBR"),
                            ]
                            if enabled(node, "m:borderBoxPr/m:" + prop, prefix="m")
                        ],
                    }
                }
            )
        elif tag == "phant":
            result.append(
                {
                    "phantom": math_sequence(node.find("m:e", NS)),
                    "hidden": not enabled(node, "m:phantPr/m:show", True, "m"),
                    "zero_width": enabled(node, "m:phantPr/m:zeroWid", prefix="m"),
                    "zero_ascent": enabled(node, "m:phantPr/m:zeroAsc", prefix="m"),
                    "zero_descent": enabled(node, "m:phantPr/m:zeroDesc", prefix="m"),
                }
            )
        else:
            raise AssertionError("Unrecognized math content in saved DOCX: " + tag)
    return result


class DocxOracle:
    def __init__(self, source):
        with ZipFile(source) as archive:
            if archive.testzip() is not None:
                raise AssertionError("Corrupt DOCX archive")
            self.files = {name: archive.read(name) for name in archive.namelist()}
        self.document = ET.fromstring(self.files["word/document.xml"])
        self.relationships = {
            node.get("Id"): node.attrib
            for node in ET.fromstring(self.files["word/_rels/document.xml.rels"])
        }
        self.numbering = ET.fromstring(self.files["word/numbering.xml"])

    def equations(self):
        return [math_sequence(math) for math in self.document.findall(".//m:oMath", NS)]

    def math_runs(self, index):
        math = self.document.findall(".//m:oMath", NS)[index]
        math_content(math)
        return [
            {
                "text": "".join(n.text or "" for n in run.findall("m:t", NS)),
                "script": value(run, "m:rPr/m:scr", prefix="m"),
                "style": value(run, "m:rPr/m:sty", prefix="m"),
                "normal": enabled(run, "m:rPr/m:nor", prefix="m"),
                **({"format": math_run_format(run)} if math_run_format(run) else {}),
            }
            for run in math.findall(".//m:r", NS)
            if run.find("m:t", NS) is not None
        ]

    def blocks(self, container=None):
        if container is None:
            container = self.document.find("w:body", NS)
        result = []
        for node in container:
            if node.tag == "{" + NS["w"] + "}p":
                paragraph = self.paragraph(node)
                if paragraph["content"]:
                    result.append({"paragraph": paragraph})
            elif node.tag == "{" + NS["w"] + "}tbl":
                rows = []
                for row in node.findall("w:tr", NS):
                    cells = []
                    for cell in row.findall("w:tc", NS):
                        cells.append(
                            {
                                "span": int(value(cell, "w:tcPr/w:gridSpan", "1")),
                                "merge": value(cell, "w:tcPr/w:vMerge", "continue")
                                if cell.find("w:tcPr/w:vMerge", NS) is not None
                                else None,
                                "fill": self.cell_fill(cell),
                                "blocks": self.blocks(cell),
                            }
                        )
                    rows.append(cells)
                result.append({"table": rows})
            elif node.tag not in {
                "{" + NS["w"] + "}sectPr",
                "{" + NS["w"] + "}tcPr",
                "{" + NS["w"] + "}bookmarkStart",
                "{" + NS["w"] + "}bookmarkEnd",
            }:
                raise AssertionError("Unrecognized document block: " + node.tag)
        return result

    def assert_internal_links(self):
        names = {
            node.get("{" + NS["w"] + "}name")
            for node in self.document.findall(".//w:bookmarkStart", NS)
        }
        for link in self.document.findall(".//w:hyperlink", NS):
            target = link.get("{" + NS["w"] + "}anchor")
            if target is not None and target not in names:
                raise AssertionError("Internal hyperlink has no bookmark: " + target)
        for equation in self.document.findall(".//m:oMath", NS):
            _, link = math_content(equation)
            if isinstance(link, str) and link.startswith("#") and link[1:] not in names:
                raise AssertionError("Internal hyperlink has no bookmark: " + link[1:])

    @staticmethod
    def cell_fill(cell):
        node = cell.find("w:tcPr/w:shd", NS)
        return None if node is None else node.get("{" + NS["w"] + "}fill")

    def paragraph(self, node):
        result = {
            "style": value(node, "w:pPr/w:pStyle", "Normal"),
            "content": self.inline(node),
        }
        alignment = value(node, "w:pPr/w:jc")
        if alignment is not None:
            result["alignment"] = alignment
        props = node.find("w:pPr/w:numPr", NS)
        if props is not None:
            identifier = value(props, "w:numId")
            number = next(
                n
                for n in self.numbering.findall("w:num", NS)
                if n.get("{" + NS["w"] + "}numId") == identifier
            )
            abstract_id = value(number, "w:abstractNumId")
            level_id = value(props, "w:ilvl", "0")
            abstract = next(
                n
                for n in self.numbering.findall("w:abstractNum", NS)
                if n.get("{" + NS["w"] + "}abstractNumId") == abstract_id
            )
            level = next(
                n
                for n in abstract.findall("w:lvl", NS)
                if n.get("{" + NS["w"] + "}ilvl") == level_id
            )
            result["list"] = {
                "level": int(level_id),
                "start": int(value(level, "w:start", "1")),
                "format": value(level, "w:numFmt"),
                "suffix": value(level, "w:suff", "tab"),
            }
        return result

    def inline(self, container):
        result = []
        for node in container:
            if node.tag == "{" + NS["m"] + "}oMath":
                result.append(self.math_inline(node))
            elif node.tag == "{" + NS["m"] + "}oMathPara":
                alignment = value(node, "m:oMathParaPr/m:jc", "centerGroup", "m")
                for child in node:
                    if child.tag == "{" + NS["m"] + "}oMath":
                        result.append(
                            self.math_inline(child, display=True, alignment=alignment)
                        )
                    elif child.tag != "{" + NS["m"] + "}oMathParaPr":
                        raise AssertionError(
                            "Unrecognized display math content: " + child.tag
                        )
            elif node.tag == "{" + NS["w"] + "}hyperlink":
                target = self.hyperlink_target(node)
                result.append({"link": target, "content": self.inline(node)})
            elif node.tag == "{" + NS["w"] + "}r":
                for content in node:
                    if content.tag == "{" + NS["w"] + "}t":
                        text = content.text or ""
                        if not text:
                            continue
                        item = {"text": text}
                        for name, prop in [
                            ("bold", "b"),
                            ("italic", "i"),
                            ("strike", "strike"),
                        ]:
                            if enabled(node, "w:rPr/w:" + prop):
                                item[name] = True
                        for name, prop in [("color", "color"), ("underline", "u")]:
                            setting = value(node, "w:rPr/w:" + prop)
                            if setting:
                                item[name] = setting
                        if (
                            result
                            and "text" in result[-1]
                            and {k: v for k, v in item.items() if k != "text"}
                            == {k: v for k, v in result[-1].items() if k != "text"}
                        ):
                            result[-1]["text"] += text
                        else:
                            result.append(item)
                    elif content.tag == "{" + NS["w"] + "}br":
                        result.append(
                            {
                                "break": content.get(
                                    "{" + NS["w"] + "}type", "textWrapping"
                                )
                            }
                        )
                    elif content.tag == "{" + NS["w"] + "}tab":
                        result.append({"tab": True})
                    elif content.tag == "{" + NS["w"] + "}drawing":
                        for blip in content.findall(".//a:blip", NS):
                            rel = self.relationships[blip.get("{" + NS["r"] + "}embed")]
                            image = self.files[
                                posixpath.normpath("word/" + rel["Target"])
                            ]
                            extent = content.find(".//wp:extent", NS)
                            result.append(
                                {
                                    "image": {
                                        "sha256": hashlib.sha256(image).hexdigest(),
                                        "width_emu": int(extent.get("cx")),
                                        "height_emu": int(extent.get("cy")),
                                    }
                                }
                            )
                    elif content.tag not in {
                        "{" + NS["w"] + "}rPr",
                        "{" + NS["w"] + "}lastRenderedPageBreak",
                    }:
                        raise AssertionError("Unrecognized run content: " + content.tag)
            elif node.tag not in {
                "{" + NS["w"] + "}pPr",
                "{" + NS["w"] + "}bookmarkStart",
                "{" + NS["w"] + "}bookmarkEnd",
                "{" + NS["w"] + "}proofErr",
            }:
                raise AssertionError("Unrecognized inline content: " + node.tag)
        return result

    def hyperlink_target(self, node):
        rid = node.get("{" + NS["r"] + "}id")
        if rid:
            relationship = self.relationships.get(rid)
            if relationship is None or not relationship.get("Type", "").endswith(
                "/hyperlink"
            ):
                raise AssertionError(
                    "Hyperlink relationship is missing or has the wrong type"
                )
            return relationship["Target"]
        anchor = node.get("{" + NS["w"] + "}anchor")
        if anchor is None:
            raise AssertionError("Hyperlink has no target")
        return "#" + anchor

    def math_inline(self, node, display=False, alignment=None):
        _, link = math_content(node)
        result = math_inline(node, display, alignment)
        if link is not None:
            target = link if isinstance(link, str) else self.hyperlink_target(link)
            return {"link": target, "content": [result]}
        return result
