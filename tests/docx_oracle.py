"""Read generated DOCX semantics without importing the converter or python-docx.

The representation deliberately ignores ZIP timestamps, relationship IDs and run
partitioning. It retains mathematical roles, delimiters, fraction type, matrix
dimensions, phantom dimensions and selected document formatting/relationships.
It is a structural oracle, not a Word layout renderer.
"""

import hashlib
import posixpath
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


def math_sequence(nodes):
    result = []
    for node in nodes:
        tag = node.tag.rsplit("}", 1)[-1]
        if tag == "r":
            # Unicode mathematical alphabets and character+mathvariant are
            # equivalent for this role comparison; explicit font checks are
            # separate so normalization cannot conceal lost mathematical style.
            text = unicodedata.normalize(
                "NFKC", "".join(n.text or "" for n in node.findall("m:t", NS))
            )
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
        elif tag in {"sSup", "sSub", "sSubSup", "limLow", "limUpp", "func"}:
            role, args = {
                "sSup": ("sup", ["e", "sup"]),
                "sSub": ("sub", ["e", "sub"]),
                "sSubSup": ("subsup", ["e", "sub", "sup"]),
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
        return [
            {
                "text": "".join(n.text or "" for n in run.findall("m:t", NS)),
                "script": value(run, "m:rPr/m:scr", prefix="m"),
                "style": value(run, "m:rPr/m:sty", prefix="m"),
                "normal": enabled(run, "m:rPr/m:nor", prefix="m"),
            }
            for run in math.findall(".//m:r", NS)
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
            elif node.tag not in {"{" + NS["w"] + "}sectPr", "{" + NS["w"] + "}tcPr"}:
                raise AssertionError("Unrecognized document block: " + node.tag)
        return result

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
                result.append({"math": math_sequence(node)})
            elif node.tag == "{" + NS["w"] + "}hyperlink":
                rid = node.get("{" + NS["r"] + "}id")
                target = (
                    self.relationships[rid]["Target"]
                    if rid
                    else "#" + node.get("{" + NS["w"] + "}anchor")
                )
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
                    elif content.tag != "{" + NS["w"] + "}rPr":
                        raise AssertionError("Unrecognized run content: " + content.tag)
            elif node.tag not in {
                "{" + NS["w"] + "}pPr",
                "{" + NS["w"] + "}bookmarkStart",
                "{" + NS["w"] + "}bookmarkEnd",
            }:
                raise AssertionError("Unrecognized inline content: " + node.tag)
        return result
