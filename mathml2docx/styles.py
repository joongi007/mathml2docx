"""Public Word style names and the supported inline CSS subset."""

import re
from enum import Enum

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, RGBColor
from PIL import ImageColor


class TableStyle(str, Enum):
    GRID = "Table Grid"
    LIGHT_SHADING_ACCENT_1 = "Light Shading Accent 1"
    LIGHT_SHADING_ACCENT_4 = "Light Shading Accent 4"


class ParagraphStyle(str, Enum):
    NORMAL = "Normal"
    QUOTE = "Quote"
    TITLE = "Title"
    HEADING_1 = "Heading 1"
    HEADING_2 = "Heading 2"
    LIST_BULLET = "List Bullet"
    LIST_NUMBER = "List Number"


def style_name(value):
    if isinstance(value, Enum):
        return value.value
    return "Table Grid" if value == "TableGrid" else value


def css(source):
    # tinycss2 preserves URLs, quoted semicolons and whitespace in font names.
    import tinycss2

    return {
        item.lower_name: tinycss2.serialize(item.value).strip()
        for item in tinycss2.parse_declaration_list(
            source, skip_comments=True, skip_whitespace=True
        )
        if item.type == "declaration"
    }


def color(value, background="FFFFFF"):
    if not value or value.lower() in {
        "transparent",
        "inherit",
        "initial",
        "currentcolor",
    }:
        return None
    value = value.strip()
    match = re.fullmatch(r"rgba?\(([^)]+)\)", value, re.I)
    try:
        if match:
            fields = match[1].split(",")
            if len(fields) not in {3, 4}:
                return None
            alpha = (
                max(
                    0,
                    min(
                        1,
                        float(fields[3].strip("%")) / (100 if "%" in fields[3] else 1),
                    ),
                )
                if len(fields) == 4
                else 1
            )
            if alpha == 0:
                return None
            channels = [
                round(float(v.strip("%")) * 2.55) if "%" in v else round(float(v))
                for v in fields[:3]
            ]
            base = [int(background[i : i + 2], 16) for i in (0, 2, 4)]
            channels = [
                round(max(0, min(255, c)) * alpha + bg * (1 - alpha))
                for c, bg in zip(channels, base)
            ]
            return "".join(f"{c:02X}" for c in channels)
        return "".join(f"{c:02X}" for c in ImageColor.getrgb(value)[:3])
    except (ValueError, TypeError):
        return None


def length(value, available=6.5):
    match = re.fullmatch(r"\s*(-?\d+(?:\.\d+)?)\s*(px|pt|in|cm|mm|%)?\s*", str(value))
    if not match:
        return None
    number = float(match[1])
    unit = match[2] or "px"
    factor = {
        "px": 1 / 96,
        "pt": 1 / 72,
        "in": 1,
        "cm": 1 / 2.54,
        "mm": 1 / 25.4,
        "%": available / 100,
    }[unit]
    return Emu(round(number * factor * 914400))


def run_style(run, properties):
    rgb = color(properties.get("color"), properties.get("_background", "FFFFFF"))
    if rgb:
        run.font.color.rgb = RGBColor.from_string(rgb)
    background = properties.get("_background") or color(
        properties.get("background-color")
    )
    if background:
        shading = OxmlElement("w:shd")
        shading.set(qn("w:val"), "clear")
        shading.set(qn("w:fill"), background)
        run._r.get_or_add_rPr().append(shading)
    if "font-weight" in properties:
        weight = properties["font-weight"]
        run.bold = weight in {"bold", "bolder"} or (
            weight.isdigit() and int(weight) >= 600
        )
    if "font-style" in properties:
        run.italic = properties["font-style"] in {"italic", "oblique"}
    decoration = properties.get(
        "text-decoration", properties.get("text-decoration-line", "")
    )
    if decoration:
        run.underline = "underline" in decoration
        run.font.strike = "line-through" in decoration
    size = length(properties.get("font-size", ""))
    if size is not None:
        run.font.size = size
    if "font-family" in properties:
        family = properties["font-family"].split(",")[0].strip("\"' ")
        run.font.name = family
        # python-docx's name setter covers ASCII/high ANSI only. CSS font-family
        # also applies to East Asian and complex-script text in the same run.
        fonts = run._r.get_or_add_rPr().get_or_add_rFonts()
        fonts.set(qn("w:eastAsia"), family)
        fonts.set(qn("w:cs"), family)
    if properties.get("vertical-align") in {"super", "sub"}:
        run.font.superscript = properties["vertical-align"] == "super"
        run.font.subscript = properties["vertical-align"] == "sub"


def paragraph_style(paragraph, properties, available=6.5):
    fmt = paragraph.paragraph_format
    align = properties.get("text-align")
    if align in {"left", "right", "center", "justify"}:
        fmt.alignment = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        }[align]
    for key, attr in [
        ("margin-left", "left_indent"),
        ("margin-right", "right_indent"),
        ("text-indent", "first_line_indent"),
        ("margin-top", "space_before"),
        ("margin-bottom", "space_after"),
    ]:
        value = length(properties.get(key, ""), available)
        if value is not None:
            setattr(fmt, attr, value)
    if properties.get("page-break-before", properties.get("break-before")) in {
        "always",
        "page",
    }:
        fmt.page_break_before = True
    if properties.get("line-height", "").endswith("%"):
        try:
            fmt.line_spacing = float(properties["line-height"][:-1]) / 100
        except ValueError:
            pass
