"""Insert rendered HTML at markers and bookmark ranges without flattening runs."""

from copy import deepcopy

from bs4 import BeautifulSoup
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .h2d import BLOCKS

_PROPERTIES = {
    qn(name)
    for name in (
        "w:pPr",
        "w:rPr",
        "w:sdtPr",
        "w:sdtEndPr",
        "w:customXmlPr",
        "w:smartTagPr",
    )
}


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
        if child.tag in _PROPERTIES:
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


def _split_at(node, boundary):
    """Copy the content before and after an actual XML boundary node.

    Text offsets cannot distinguish a bookmark from adjacent equations, pictures,
    or breaks. Keep the ancestors on either side so their formatting and hyperlink
    attributes survive, even when the boundary is nested inside a wrapper.
    """
    left, right = deepcopy(node), deepcopy(node)
    for part in (left, right):
        for child in list(part):
            part.remove(child)
    found = False
    for child in node:
        if child.tag in _PROPERTIES:
            left.append(deepcopy(child))
            right.append(deepcopy(child))
        elif child is boundary:
            found = True
        elif not found and any(value is boundary for value in child.iter()):
            before, after = _split_at(child, boundary)
            left.append(before)
            right.append(after)
            found = True
        elif found:
            right.append(deepcopy(child))
        else:
            left.append(deepcopy(child))
    if not found:
        raise ValueError("Bookmark endpoint not found")
    return left, right


def _has_content(node):
    """Whether a split subtree contains content beyond formatting scaffolding."""
    if node.tag in _PROPERTIES:
        return False
    if node.tag == qn("w:t"):
        return bool(node.text)
    if node.tag in {qn("m:oMath"), qn("m:oMathPara")}:
        return True
    if len(node):
        return any(_has_content(child) for child in node)
    # Empty wrappers result from splitting styled runs and hyperlinks. Other
    # leaves include visible breaks/tabs and positional objects such as bookmarks.
    return node.tag not in {qn("w:p"), qn("w:r"), qn("w:hyperlink")}


def _inline_blocks(blocks):
    return all(
        block.tag == qn("w:p") and not any(True for _ in block.iter(qn("m:oMathPara")))
        for block in blocks
    )


def _append_content(target, paragraph):
    for child in list(paragraph):
        if child.tag != qn("w:pPr"):
            target.append(child)


def _replace_nodes(first, originals, replacements):
    parent = first.getparent()
    for node in replacements:
        first.addprevious(node)
    for node in originals:
        parent.remove(node)
    if parent.tag == qn("w:tc") and (not len(parent) or parent[-1].tag != qn("w:p")):
        parent.append(OxmlElement("w:p"))


def _render(converter, document, html):
    body = document._element.body
    original = list(body)
    part = document.part
    relationships = dict(part.rels)
    related_parts = dict(part.related_parts)
    numbering = next(
        (rel.target_part for rel in part.rels.values() if rel.reltype == RT.NUMBERING),
        None,
    )
    numbering_xml = deepcopy(numbering.element) if numbering is not None else None
    cached = set(part.__dict__)
    try:
        converter.add_html_to_document(html, document)
        result = [node for node in body if node not in original]
        for node in result:
            body.remove(node)
        return result
    except Exception:
        # Partial rendering can allocate list definitions and image/hyperlink
        # relationships before a later equation fails. Roll those allocations
        # back along with the temporary body nodes, leaving a reusable template.
        part.rels.clear()
        part.rels.update(relationships)
        part.related_parts.clear()
        part.related_parts.update(related_parts)
        if numbering_xml is not None:
            numbering.element.clear()
            numbering.element.attrib.update(numbering_xml.attrib)
            numbering.element.text = numbering_xml.text
            numbering.element.tail = numbering_xml.tail
            numbering.element.extend(deepcopy(list(numbering_xml)))
        elif numbering is None:
            # python-docx versions use either name for their lazy property cache.
            for key in ("numbering_part", "_numbering_part"):
                if key not in cached:
                    part.__dict__.pop(key, None)
        raise
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
    # A text marker can span equations, pictures, breaks, or bookmarks. Remove
    # only its text, retaining those objects in their original relative order.
    for value in list(removed.iter(qn("w:t"))):
        value.getparent().remove(value)
    for child in list(removed):
        if _has_content(child):
            left.append(child)
    if inline and _inline_blocks(blocks):
        for block in blocks:
            _append_content(left, block)
        _append_content(left, right)
        replacement = [left]
    else:
        replacement = ([left] if _has_content(left) else []) + blocks
        if _has_content(right):
            replacement.append(right)
        if not replacement:
            replacement = [left]
    _replace_nodes(paragraph, [paragraph], replacement)


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
    if nodes.index(first) > nodes.index(last) or (
        first is last
        and list(first.iter()).index(start) > list(first.iter()).index(end)
    ):
        raise ValueError("Bookmark end precedes start")
    blocks = _render(converter, document, html)
    # Keep the bookmark around the inserted material, including multi-block HTML.
    left, _ = _split_at(first, start)
    _, right = _split_at(last, end)
    if first is last and _inline(html) and _inline_blocks(blocks):
        left.append(deepcopy(start))
        for block in blocks:
            _append_content(left, block)
        left.append(deepcopy(end))
        _append_content(left, right)
        replacements = [left]
    else:
        left.append(deepcopy(start))
        right.insert(1 if right.find(qn("w:pPr")) is not None else 0, deepcopy(end))
        replacements = [left] + blocks + [right]
    _replace_nodes(
        first, nodes[nodes.index(first) : nodes.index(last) + 1], replacements
    )
