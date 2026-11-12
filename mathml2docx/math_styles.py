"""Supported CSS and MathML run styling without python-docx Run wrappers."""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree

from .styles import color, css, length

MATH_CSS = ("color", "font-size", "font-family")


def math_style(node, parent_properties):
    """Resolve inherited presentation attributes and the supported CSS subset."""
    properties = dict(parent_properties)
    declarations = {}
    for attribute, name in (("mathcolor", "color"), ("mathsize", "font-size")):
        if node.get(attribute) is not None:
            declarations[name] = node.get(attribute)
    declarations.update(css(node.get("style", "")))
    background = declarations.get("background-color", node.get("mathbackground"))
    if background:
        properties["_background"] = color(
            background, parent_properties.get("_background", "FFFFFF")
        ) or parent_properties.get("_background", "FFFFFF")
    for name in MATH_CSS:
        value = declarations.get(name)
        if (
            value is None
            or value == "inherit"
            or (name == "color" and value.lower() == "currentcolor")
        ):
            continue
        if name == "font-size" and value.endswith(("em", "%")):
            base = length(parent_properties.get("font-size", "12pt"))
            try:
                factor = (
                    float(value[:-2])
                    if value.endswith("em")
                    else float(value[:-1]) / 100
                )
            except ValueError:
                continue
            value = str((base.pt if base is not None else 12) * factor) + "pt"
        properties[name] = value
    return properties


def apply_math_style(node, properties):
    """Apply Word run properties to a math run or a compound's control glyphs."""
    run_properties = OxmlElement("w:rPr")
    rgb = color(properties.get("color"), properties.get("_background", "FFFFFF"))
    if rgb:
        node_color = OxmlElement("w:color")
        node_color.set(qn("w:val"), rgb)
        run_properties.append(node_color)
    size = length(properties.get("font-size", ""))
    if size is not None and size > 0:
        for name in ("sz", "szCs"):
            node_size = OxmlElement("w:" + name)
            node_size.set(qn("w:val"), str(max(1, int(size.pt * 2))))
            run_properties.append(node_size)
    if properties.get("font-family"):
        family = properties["font-family"].split(",")[0].strip("\"' ")
        fonts = OxmlElement("w:rFonts")
        for name in ("ascii", "hAnsi", "eastAsia", "cs"):
            fonts.set(qn("w:" + name), family)
        run_properties.insert(0, fonts)
    if not len(run_properties):
        return node
    tag = etree.QName(node).localname
    if tag == "r":
        previous = node.find(qn("w:rPr"))
        if previous is not None:
            for child in run_properties:
                old = previous.find(child.tag)
                if old is not None:
                    previous.remove(old)
                previous.append(child)
        else:
            node.insert(1 if node.find(qn("m:rPr")) is not None else 0, run_properties)
    elif tag in {
        "f",
        "rad",
        "d",
        "acc",
        "bar",
        "limLow",
        "limUpp",
        "sSub",
        "sSup",
        "sSubSup",
        "sPre",
        "m",
        "phant",
        "borderBox",
        "func",
    }:
        container = node.find(qn("m:" + tag + "Pr"))
        if container is None:
            container = OxmlElement("m:" + tag + "Pr")
            node.insert(0, container)
        control = container.find(qn("m:ctrlPr"))
        if control is None:
            control = OxmlElement("m:ctrlPr")
            container.append(control)
        previous = control.find(qn("w:rPr"))
        if previous is not None:
            control.remove(previous)
        control.append(run_properties)
    return node
