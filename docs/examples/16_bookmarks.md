# Bookmark replacement

Replace Word bookmark ranges while preserving surrounding content and bookmarks.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.16_bookmarks
```

[Generated DOCX](../downloads/examples/16_bookmarks.docx)

[Reference PDF](../assets/previews/16_bookmarks.pdf)

## Complete source

```python
"""16 bookmarks example."""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph("Before ")
start = OxmlElement("w:bookmarkStart")
start.set(qn("w:id"), "1")
start.set(qn("w:name"), "result")
p._p.append(start)
p.add_run("replace this")
end = OxmlElement("w:bookmarkEnd")
end.set(qn("w:id"), "1")
p._p.append(end)
p.add_run(" after.")
MathmlToDocx().replace_bookmark(document, "result", "<b>new result</b>")
save(document, "16_bookmarks.docx")
```
