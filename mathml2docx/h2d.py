"""HTML tree traversal with per-conversion state and explicit resource loading."""

import base64
import re
import warnings
from copy import deepcopy
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString
from docx import Document
from docx.document import Document as DocumentType
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.image.exceptions import UnrecognizedImageError
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches
from docx.table import _Cell

from .config import DEFAULT_PARAGRAPH_STYLE, DEFAULT_TABLE_STYLE
from .css import INHERITED, computed_styles
from .math import (
    MathMLFallbackWarning,
    UnsupportedMathMLError,
    element,
    mathml_to_omml,
    parse_mathml,
)
from .styles import css, length, paragraph_style, run_style, style_name

BLOCKS = {
    "p",
    "div",
    "section",
    "main",
    "article",
    "header",
    "footer",
    "aside",
    "blockquote",
    "pre",
    "address",
    "figure",
    "figcaption",
}
FORMATS = {
    "b": "font-weight:bold",
    "strong": "font-weight:bold",
    "i": "font-style:italic",
    "em": "font-style:italic",
    "u": "text-decoration:underline",
    "s": "text-decoration:line-through",
    "strike": "text-decoration:line-through",
    "del": "text-decoration:line-through",
    "sup": "vertical-align:super",
    "sub": "vertical-align:sub",
    "code": "font-family:Courier New",
    "pre": "font-family:Courier New",
}


class HtmlToDocx:
    def __init__(self):
        self.options = {
            "fix-html": True,
            "images": True,
            "tables": True,
            "mathml": True,
            "styles": True,
            "img_src_base_path": None,
            "image_loader": None,
            "default_math_display": "inline",
            "unsupported_math": "error",
            "mathml_preprocessor": None,
            "mathml_fallback": None,
            "math_target": "word",
        }
        self.table_style = DEFAULT_TABLE_STYLE
        self.paragraph_style = DEFAULT_PARAGRAPH_STYLE
        self.style_map = {}
        self.stylesheet = ""
        self.stylesheet_loader = None

    def copy_settings_from(self, other):
        self.options = other.options.copy()
        self.table_style = other.table_style
        self.paragraph_style = other.paragraph_style
        self.style_map = deepcopy(other.style_map)
        self.stylesheet = other.stylesheet
        self.stylesheet_loader = other.stylesheet_loader

    @staticmethod
    def parse_dict_string(value, separator=";"):
        return css(value)

    def parse_html_string(self, html):
        document = Document()
        self.add_html_to_document(html, document)
        return document

    def parse_html_file(self, filename_html, filename_docx=None, encoding="utf-8"):
        source = Path(filename_html)
        target = (
            Path(filename_docx)
            if filename_docx is not None
            else source.with_suffix(".docx")
        )
        if target.suffix.lower() != ".docx":
            target = target.with_name(target.name + ".docx")
        if target.resolve() == source.resolve():
            raise ValueError("Input and output paths must differ")
        document = self.parse_html_string(source.read_text(encoding=encoding))
        document.save(target)
        return target

    def add_html_to_document(self, html, document):
        if not isinstance(html, str):
            raise TypeError("html must be a string")
        if not isinstance(document, (DocumentType, _Cell)):
            # docxtpl exposes its underlying python-docx document through get_docx().
            if callable(getattr(document, "get_docx", None)):
                current = getattr(document, "docx", None)
                document = (
                    current
                    if isinstance(current, DocumentType)
                    else document.get_docx()
                )
            if not isinstance(document, (DocumentType, _Cell)):
                raise TypeError("document must be a python-docx Document or cell")
        soup = BeautifulSoup(html, "html.parser")
        computed = (
            computed_styles(soup, self.stylesheet, self.stylesheet_loader)
            if self.options["styles"]
            else {}
        )
        _Renderer(self, document, computed).render(soup)

    def add_html_to_cell(self, html, cell):
        if not isinstance(cell, _Cell):
            raise TypeError("cell must be a python-docx table cell")
        self.add_html_to_document(html, cell)

    def _add_mathml_to_document(self, source, document):
        _Renderer(self, document).math(source, {})

    @staticmethod
    def add_image_to_cell(cell, image):
        if not isinstance(cell, (DocumentType, _Cell)) or not isinstance(
            image, BytesIO
        ):
            raise TypeError("Expected Document/cell and BytesIO image")
        cell.add_paragraph().add_run().add_picture(image)

    def add_styles_to_paragraph(self, style, paragraph=None):
        if paragraph is None:
            raise ValueError("Pass paragraph= with the target python-docx paragraph")
        paragraph_style(paragraph, css(style) if isinstance(style, str) else style)

    def add_styles_to_run(self, style, run=None):
        if run is None:
            raise ValueError("Pass run= with the target python-docx run")
        run_style(run, css(style) if isinstance(style, str) else style)


class _Renderer:
    def __init__(self, config, target, computed=None):
        self.computed = computed or {}
        self.config = config
        self.target = target
        self.paragraph = None
        self.lists = []
        self.pre = False
        self.document = (
            target if isinstance(target, DocumentType) else target.part.document
        )

    def paragraph_for(self):
        if self.paragraph is None:
            if (
                isinstance(self.target, _Cell)
                and len(self.target.paragraphs) == 1
                and not self.target.paragraphs[0]._p.xpath(
                    "./w:r|./w:hyperlink|./m:oMath"
                )
                and not self.target.paragraphs[0].text
            ):
                self.paragraph = self.target.paragraphs[0]
            else:
                self.paragraph = self.target.add_paragraph()
            if self.config.paragraph_style:
                self.paragraph.style = style_name(self.config.paragraph_style)
        return self.paragraph

    def available(self):
        section = self.document.sections[-1]
        return (
            section.page_width - section.left_margin - section.right_margin
        ) / 914400

    def properties(self, node, inherited):
        tag = node.name
        properties = {
            key: value
            for key, value in inherited.items()
            if key in INHERITED or key.startswith("_")
        }
        if self.config.options["styles"]:
            properties.update(css(FORMATS.get(tag, "")))
            properties.update(self.computed.get(id(node), css(node.get("style", ""))))
            for key, value in list(properties.items()):
                if value == "inherit":
                    properties[key] = inherited.get(key, "")
            if "background-color" not in properties and "_background" in inherited:
                properties["_background"] = inherited["_background"]
            if properties.get("background-color"):
                from .styles import color

                properties["_background"] = color(
                    properties["background-color"],
                    inherited.get("_background", "FFFFFF"),
                ) or inherited.get("_background", "FFFFFF")
        size = properties.get("font-size", "")
        if size.endswith(("em", "%")):
            base = length(inherited.get("font-size", "12pt"))
            factor = float(size[:-2]) if size.endswith("em") else float(size[:-1]) / 100
            properties["font-size"] = (
                str((base.pt if base is not None else 12) * factor) + "pt"
            )
        return properties

    def render(self, node, inherited=None):
        inherited = inherited or {}
        if isinstance(node, (Comment, Doctype)):
            return
        if isinstance(node, NavigableString):
            value = str(node) if self.pre else re.sub(r"[\t\r\n ]+", " ", str(node))
            if self.paragraph is None:
                value = value.lstrip(" ")
            elif (
                not self.pre
                and len(self.paragraph._p)
                and self.paragraph._p[-1].tag != qn("m:oMath")
                and "".join(
                    t.text or "" for t in self.paragraph._p[-1].iter(qn("w:t"))
                ).endswith(" ")
            ):
                value = value.lstrip(" ")
            if value:
                fresh = self.paragraph is None
                run = self.paragraph_for().add_run(value)
                if fresh and self.config.options["styles"]:
                    paragraph_style(self.paragraph, inherited, self.available())
                if self.config.options["styles"]:
                    run_style(run, inherited)
                    if inherited.get("_word_style"):
                        run.style = inherited["_word_style"]
            return
        tag = node.name
        if tag == "head":
            title = node.find("title")
            if title is not None:
                self.render(title, inherited)
            return
        if tag in {"script", "style", "meta", "link"}:
            return
        properties = self.properties(node, inherited)
        if (
            properties.get("display") == "none"
            or properties.get("visibility") == "hidden"
        ):
            return
        if tag == "table":
            if self.config.options["tables"]:
                self.table(node, properties)
            self.paragraph = None
            return
        if tag == "math":
            if self.config.options["mathml"]:
                self.math(str(node), properties)
            return
        if tag == "img":
            if self.config.options["images"]:
                self.image(node)
            return
        if tag == "br":
            self.paragraph_for().add_run().add_break()
            return
        if tag == "hr":
            self.paragraph = None
            p = self.paragraph_for()
            borders = OxmlElement("w:pBdr")
            bottom = OxmlElement("w:bottom")
            for attr, value in {"val": "single", "sz": "6", "color": "auto"}.items():
                bottom.set(qn("w:" + attr), value)
            borders.append(bottom)
            p._p.get_or_add_pPr().append(borders)
            self.paragraph = None
            return
        if tag in {"ol", "ul"}:
            self.paragraph = None
            self.lists.append(self.numbering(tag, node.get("start", "1")))
            for child in node.children:
                self.render(child, properties)
            self.lists.pop()
            self.paragraph = None
            return
        is_block = (
            tag in BLOCKS
            or tag == "li"
            or bool(re.fullmatch(r"h[1-6]", tag or ""))
            or tag == "title"
        )
        if is_block:
            self.paragraph = None
            paragraph = self.paragraph_for()
            if tag and re.fullmatch(r"h[1-6]", tag):
                paragraph.style = "Heading " + tag[1]
            elif tag == "title":
                paragraph.style = "Title"
            elif tag == "blockquote" and not self.config.paragraph_style:
                paragraph.style = "Quote"
            if tag == "li" and self.lists:
                self.apply_number(
                    paragraph, self.lists[-1], len(self.lists) - 1, node.get("value")
                )
            if self.config.options["styles"]:
                paragraph_style(paragraph, properties, self.available())
        mapped = self.config.style_map.get(tag, {})
        for class_name in node.get("class", []):
            if class_name in mapped:
                chosen = self.document.styles[style_name(mapped[class_name])]
                if chosen.type == WD_STYLE_TYPE.PARAGRAPH:
                    self.paragraph_for().style = chosen
                else:
                    properties["_word_style"] = chosen.name
        anchor = node.get("id") or (node.get("name") if tag == "a" else None)
        if anchor:
            ids = self.document._element.xpath("//w:bookmarkStart/@w:id")
            number = str(max([int(value) for value in ids], default=-1) + 1)
            start = OxmlElement("w:bookmarkStart")
            start.set(qn("w:id"), number)
            start.set(qn("w:name"), anchor)
            end = OxmlElement("w:bookmarkEnd")
            end.set(qn("w:id"), number)
            self.paragraph_for()._p.extend([start, end])
        if tag == "a" and node.get("href"):
            self.link(node, properties)
            return
        old_pre = self.pre
        self.pre = (
            self.pre
            or tag == "pre"
            or properties.get("white-space") in {"pre", "pre-wrap"}
        )
        for child in node.children:
            self.render(child, properties)
        self.pre = old_pre
        if is_block:
            if (
                tag
                in {
                    "p",
                    "div",
                    "section",
                    "main",
                    "article",
                    "header",
                    "footer",
                    "aside",
                    "figure",
                }
                and any(
                    getattr(child, "name", None) in BLOCKS | {"table", "ol", "ul"}
                    for child in node.children
                )
                and len(paragraph._p) == (1 if paragraph._p.pPr is not None else 0)
            ):
                paragraph._p.getparent().remove(paragraph._p)
            if properties.get("page-break-after", properties.get("break-after")) in {
                "always",
                "page",
            }:
                self.paragraph_for().add_run().add_break(WD_BREAK.PAGE)
            self.paragraph = None

    def numbering(self, tag, start):
        numbering = self.document.part.numbering_part.element
        ids = [int(v) for v in numbering.xpath("./w:abstractNum/@w:abstractNumId")]
        abstract_id = max(ids, default=-1) + 1
        abstract = OxmlElement("w:abstractNum")
        abstract.set(qn("w:abstractNumId"), str(abstract_id))
        for depth in range(9):
            level = OxmlElement("w:lvl")
            level.set(qn("w:ilvl"), str(depth))
            for name, value in [
                ("start", str(int(start))),
                ("numFmt", "decimal" if tag == "ol" else "bullet"),
                ("suff", "space"),
                ("lvlText", f"%{depth + 1}." if tag == "ol" else "•"),
            ]:
                prop = OxmlElement("w:" + name)
                prop.set(qn("w:val"), value)
                level.append(prop)
            abstract.append(level)
        numbering.insert_element_before(abstract, "w:num", "w:numIdMac")
        number = numbering.add_num(abstract_id)
        return number.numId

    def apply_number(self, paragraph, number, depth, value=None):
        if value is not None:
            number = self.numbering("ol", value)
            self.lists[-1] = number
        props = paragraph._p.get_or_add_pPr().get_or_add_numPr()
        props.get_or_add_ilvl().val = min(depth, 8)
        props.get_or_add_numId().val = number
        paragraph.paragraph_format.left_indent = Inches(0.25 * (depth + 1))
        paragraph.paragraph_format.first_line_indent = Inches(-0.15)

    def link(self, node, properties):
        paragraph = self.paragraph_for()
        href = node["href"]
        if urlsplit(href).scheme.lower() not in {"", "http", "https", "mailto"}:
            for child in node.children:
                self.render(child, properties)
            return
        link = OxmlElement("w:hyperlink")
        if href.startswith("#"):
            link.set(qn("w:anchor"), href[1:])
        else:
            link.set(
                qn("r:id"),
                paragraph.part.relate_to(href, RT.HYPERLINK, is_external=True),
            )
        # Render children through the regular path, then move their runs into the hyperlink.
        start = len(paragraph._p)
        for child in node.children:
            self.render(child, properties)
        for child in list(paragraph._p)[start:]:
            link.append(child)
        paragraph._p.append(link)

    def math(self, source, properties):
        # Validate both sides of preprocessing. Recovery must not hide malformed
        # XML, DTDs, wrong arity, or exceptions raised by application callbacks.
        root = parse_mathml(source)
        preprocessor = self.config.options.get("mathml_preprocessor")
        if preprocessor is not None:
            source = preprocessor(source)
            root = parse_mathml(source)
        display = properties.get(
            "display",
            root.get(
                "display", self.config.options.get("default_math_display", "inline")
            ),
        )
        if display not in {
            "inline",
            "block",
            "inline math",
            "block math",
            "inline-block",
        }:
            raise ValueError("Math display must be inline or block")
        block = display in {"block", "block math"}
        replacement = None
        try:
            equation = mathml_to_omml(
                source, target=self.config.options.get("math_target", "word")
            )
        except UnsupportedMathMLError as exc:
            fallback = self.config.options.get("mathml_fallback")
            if fallback is not None:
                replacement = fallback(source, exc)
            elif self.config.options.get("unsupported_math", "error") == "text":
                replacement = "[Unconverted MathML] " + source
            else:
                raise
            if isinstance(replacement, bytes):
                replacement = BytesIO(replacement)
            if not isinstance(replacement, (str, BytesIO)):
                raise TypeError(
                    "mathml_fallback must return text, image bytes, or BytesIO"
                ) from exc
            if (isinstance(replacement, str) and not replacement.strip()) or (
                isinstance(replacement, BytesIO) and not replacement.getbuffer().nbytes
            ):
                raise ValueError("MathML fallback must not be empty") from exc
            warnings.warn(
                "MathML fallback used: " + str(exc), MathMLFallbackWarning, stacklevel=3
            )
        if block:
            self.paragraph = None
        paragraph = self.paragraph_for()
        if self.config.options["styles"]:
            paragraph_style(paragraph, properties, self.available())
        if replacement is None:
            if block:
                alignment = {"left": "left", "right": "right", "center": "center"}.get(
                    properties.get("text-align"), "center"
                )
                equation = element(
                    "oMathPara",
                    element("oMathParaPr", element("jc", val=alignment)),
                    equation,
                )
            paragraph._p.append(equation)
        elif isinstance(replacement, str):
            run = paragraph.add_run(replacement)
            if self.config.options["styles"]:
                run_style(run, properties)
        else:
            replacement.seek(0)
            shape = paragraph.add_run().add_picture(replacement)
            limit = Inches(self.available())
            if shape.width > limit:
                shape.height = round(shape.height * limit / shape.width)
                shape.width = limit
            shape._inline.docPr.set(
                "descr", root.get("alttext") or "MathML image: " + source
            )
        if block:
            self.paragraph = None

    def image(self, node):
        source = node.get("src", "")
        image = None
        try:
            if source.startswith("data:image/") and ";base64," in source:
                image = BytesIO(
                    base64.b64decode(source.split(",", 1)[1], validate=True)
                )
            elif self.config.options.get("image_loader"):
                image = self.config.options["image_loader"](source)
                if isinstance(image, bytes):
                    image = BytesIO(image)
            elif (
                self.config.options.get("img_src_base_path")
                and not urlsplit(source).scheme
            ):
                base = Path(self.config.options["img_src_base_path"]).resolve()
                path = (base / source).resolve()
                if (path == base or base in path.parents) and path.is_file():
                    image = BytesIO(path.read_bytes())
            if image is not None:
                dimensions = self.computed.get(id(node), css(node.get("style", "")))
                width = length(dimensions.get("width", node.get("width", "")))
                height = length(dimensions.get("height", node.get("height", "")))
                self.paragraph_for().add_run().add_picture(
                    image, width=width, height=height
                )
                return
        except (ValueError, OSError, UnrecognizedImageError) as exc:
            warnings.warn(
                f"Image could not be loaded: {type(exc).__name__}",
                RuntimeWarning,
                stacklevel=2,
            )
        self.paragraph_for().add_run(node.get("alt") or "<image: unavailable>")

    def table(self, node, properties=None):
        properties = properties or {}
        rows = [row for row in node.find_all("tr") if row.find_parent("table") is node]
        occupied = set()
        placements = []
        width = 0
        for r, row in enumerate(rows):
            col = 0
            for cell in row.find_all(["td", "th"], recursive=False):
                while (r, col) in occupied:
                    col += 1
                colspan = max(1, int(cell.get("colspan", 1)))
                raw_span = int(cell.get("rowspan", 1))
                rowspan = (
                    len(rows) - r
                    if raw_span == 0
                    else max(1, min(raw_span, len(rows) - r))
                )
                if colspan > 1000:
                    raise ValueError("colspan exceeds 1000")
                for rr in range(r, r + rowspan):
                    for cc in range(col, col + colspan):
                        if (rr, cc) in occupied:
                            raise ValueError("Overlapping table spans")
                        occupied.add((rr, cc))
                placements.append((r, col, rowspan, colspan, cell))
                col += colspan
                width = max(width, col)
        if not rows or not width:
            return
        if len(rows) * width > 100000:
            raise ValueError("Table exceeds 100000 cells")
        table = self.target.add_table(len(rows), width)
        if self.config.table_style:
            table.style = style_name(self.config.table_style)
        align = properties.get("text-align")
        if align in {"left", "center", "right"}:
            table.alignment = {
                "left": WD_TABLE_ALIGNMENT.LEFT,
                "center": WD_TABLE_ALIGNMENT.CENTER,
                "right": WD_TABLE_ALIGNMENT.RIGHT,
            }[align]
        table_width = length(
            properties.get("width", node.get("width", "")), self.available()
        )
        if table_width is not None:
            table.autofit = False
            width_node = table._tbl.tblPr.find(qn("w:tblW"))
            width_node.set(qn("w:type"), "dxa")
            width_node.set(qn("w:w"), str(round(table_width / 635)))
        if properties.get("border") or node.get("border"):
            borders = OxmlElement("w:tblBorders")
            from .styles import color

            border_color = next(
                (
                    color(part)
                    for part in properties.get("border", "").split()
                    if color(part)
                ),
                "000000",
            )
            for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
                edge = OxmlElement("w:" + side)
                for key, value in {
                    "val": "single",
                    "sz": "6",
                    "color": border_color,
                }.items():
                    edge.set(qn("w:" + key), value)
                borders.append(edge)
            table._tbl.tblPr.insert_element_before(
                borders,
                "w:shd",
                "w:tblLayout",
                "w:tblCellMar",
                "w:tblLook",
                "w:tblCaption",
                "w:tblDescription",
                "w:tblPrChange",
            )
        # Cache cells before merging; repeated Table.cell() would reconstruct the entire grid.
        cells = table._cells
        for r, c, rs, cs, source in placements:
            target = cells[r * width + c]
            if rs > 1 or cs > 1:
                target.merge(cells[(r + rs - 1) * width + c + cs - 1])
            child = _Renderer(self.config, target, self.computed)
            cell_properties = dict(properties)
            ancestors = []
            ancestor = source.parent
            while ancestor is not node:
                ancestors.append(ancestor)
                ancestor = ancestor.parent
            for ancestor in reversed(ancestors):
                cell_properties = self.properties(ancestor, cell_properties)
            cell_properties = self.properties(source, cell_properties)
            from .styles import color

            shading = color(
                cell_properties.get("background-color"),
                cell_properties.get("_background", "FFFFFF"),
            )
            if shading:
                fill = OxmlElement("w:shd")
                fill.set(qn("w:val"), "clear")
                fill.set(qn("w:fill"), cell_properties.get("_background", shading))
                target._tc.get_or_add_tcPr().append(fill)
            cell_width = length(
                cell_properties.get("width", source.get("width", "")), self.available()
            )
            if cell_width is not None:
                target.width = cell_width
            if source.name == "th":
                cell_properties["font-weight"] = "bold"
            for content in source.children:
                child.render(content, cell_properties)
            if target._tc[-1].tag != qn("w:p"):
                target.add_paragraph()
