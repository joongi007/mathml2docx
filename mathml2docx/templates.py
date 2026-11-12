"""Insert rendered HTML at markers and bookmark ranges without flattening runs."""

from copy import deepcopy

from bs4 import BeautifulSoup
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .h2d import BLOCKS


def _text(node):
    return "".join(t.text or "" for t in node.iter(qn("w:t")))


def _split(node, offset):
    """Copy an XML subtree on either side of a visible-text offset."""
    left, right = deepcopy(node), deepcopy(node)
    if node.tag == qn("w:t"):
        left.text = (node.text or "")[:offset]
        right.text = (node.text or "")[offset:]
        for part in (left, right):
            part.set(qn("xml:space"), "preserve")
        return left, right
    for part in (left, right):
        for child in list(part):
            part.remove(child)
    for child in node:
        if child.tag in {qn("w:pPr"), qn("w:rPr")}:
            left.append(deepcopy(child))
            right.append(deepcopy(child))
            continue
        size = len(_text(child))
        if offset == 0:
            right.append(deepcopy(child))
        elif offset >= size:
            left.append(deepcopy(child))
            offset -= size
        else:
            a, b = _split(child, offset)
            left.append(a)
            right.append(b)
            offset = 0
    return left, right


def _render(converter, document, html):
    body = document._element.body
    original = list(body)
    try:
        converter.add_html_to_document(html, document)
        result = [node for node in body if node not in original]
        for node in result:
            body.remove(node)
        return result
    finally:
        for node in list(body):
            if node not in original:
                body.remove(node)


def _inline(html):
    soup = BeautifulSoup(html, "html.parser")
    return not soup.find(
        list(
            BLOCKS
            | {
                "table",
                "ol",
                "ul",
                "li",
                "hr",
                "title",
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            }
        )
    )


def _splice(paragraph, start, end, blocks, inline):
    left, rest = _split(paragraph, start)
    removed, right = _split(rest, end - start)
    # A marker can span runs interleaved with pictures or equations. Text
    # replacement must not silently delete those zero-width XML objects.
    for child in list(removed):
        if child.tag == qn("w:pPr"):
            continue
        if child.xpath(".//w:drawing|.//w:object") or child.tag in {
            qn("m:oMath"),
            qn("m:oMathPara"),
        }:
            preserved = deepcopy(child)
            for value in list(preserved.iter(qn("w:t"))):
                value.getparent().remove(value)
            left.append(preserved)
    if inline and all(
        b.tag == qn("w:p") and not b.xpath("./m:oMathPara") for b in blocks
    ):
        for block in blocks:
            for child in list(block):
                if child.tag != qn("w:pPr"):
                    left.append(child)
        for child in list(right):
            if child.tag != qn("w:pPr"):
                left.append(child)
        replacement = [left]
    else:
        replacement = (
            [left]
            if _text(left) or left.xpath(".//w:drawing|.//w:bookmarkStart")
            else []
        ) + blocks
        if _text(right) or right.xpath(".//w:drawing|.//w:bookmarkEnd"):
            replacement.append(right)
        if not replacement:
            replacement = [left]
    for node in replacement:
        paragraph.addprevious(node)
    parent = paragraph.getparent()
    parent.remove(paragraph)
    if parent.tag == qn("w:tc") and parent[-1].tag != qn("w:p"):
        parent.append(OxmlElement("w:p"))


def replace_html(converter, document, marker, html):
    if not isinstance(marker, str) or not marker:
        raise ValueError("marker must be a nonempty string")
    matches = [
        (p, _text(p).find(marker))
        for p in document._element.body.iter(qn("w:p"))
        if marker in _text(p)
    ]
    if len(matches) != 1 or _text(matches[0][0]).count(marker) != 1:
        raise ValueError("Expected exactly one marker occurrence")
    paragraph, start = matches[0]
    blocks = _render(converter, document, html)
    _splice(paragraph, start, start + len(marker), blocks, _inline(html))


def replace_bookmark(converter, document, name, html):
    starts = [
        node
        for node in document._element.body.iter(qn("w:bookmarkStart"))
        if node.get(qn("w:name")) == name
    ]
    if len(starts) != 1:
        raise ValueError("Expected exactly one bookmark named " + name)
    start = starts[0]
    ends = [
        node
        for node in document._element.body.iter(qn("w:bookmarkEnd"))
        if node.get(qn("w:id")) == start.get(qn("w:id"))
    ]
    if len(ends) != 1:
        raise ValueError("Bookmark end is missing or ambiguous")
    end = ends[0]

    def paragraph(node):
        while node is not None and node.tag != qn("w:p"):
            node = node.getparent()
        if node is None:
            raise ValueError("Bookmark must be inside a paragraph")
        return node

    first, last = paragraph(start), paragraph(end)
    if first.getparent() is not last.getparent():
        raise ValueError(
            "Bookmark endpoints must belong to the same document container"
        )
    nodes = list(first.getparent())
    if nodes.index(first) > nodes.index(last):
        raise ValueError("Bookmark end precedes start")

    def offset(p, target):
        total = 0
        for node in p.iter():
            if node is target:
                return total
            if node.tag == qn("w:t"):
                total += len(node.text or "")
        raise ValueError("Bookmark endpoint not found")

    a, b = offset(first, start), offset(last, end)
    blocks = _render(converter, document, html)
    # Keep the bookmark around the inserted material, including multi-block HTML.
    left, _ = _split(first, a)
    _, right = _split(last, b)
    for tree in (left, right):
        for node in list(tree.iter()):
            if node.tag in {qn("w:bookmarkStart"), qn("w:bookmarkEnd")} and node.get(
                qn("w:id")
            ) == start.get(qn("w:id")):
                node.getparent().remove(node)
    if (
        first is last
        and _inline(html)
        and all(x.tag == qn("w:p") and not x.xpath("./m:oMathPara") for x in blocks)
    ):
        left.append(deepcopy(start))
        for block in blocks:
            for child in list(block):
                if child.tag != qn("w:pPr"):
                    left.append(child)
        left.append(deepcopy(end))
        for child in list(right):
            if child.tag != qn("w:pPr"):
                left.append(child)
        replacements = [left]
    else:
        left.append(deepcopy(start))
        right.insert(1 if right.find(qn("w:pPr")) is not None else 0, deepcopy(end))
        replacements = [left] + blocks + [right]
    for node in replacements:
        first.addprevious(node)
    parent = first.getparent()
    for node in nodes[nodes.index(first) : nodes.index(last) + 1]:
        parent.remove(node)
