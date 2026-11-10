# Paragraph layout and page breaks

Set alignment, spacing, indentation, line height, and page breaks.

## Run

```sh
python -m examples.07_page_layout
```

[Generated DOCX](../downloads/examples/07_page_layout.docx)

[Reference PDF](../assets/previews/07_page_layout.pdf)

## Complete source

```python
"""07 page layout example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Paragraph layout</h1><p style="text-align:center">Centered</p>
<p style="margin-left:10%;text-indent:12pt;line-height:150%;margin-top:8pt">Indented paragraph with line spacing.</p>
<p style="page-break-after:always">End of page one</p><h2>Page two</h2><p>Continued.</p>""")
save(document, "07_page_layout.docx")
```
