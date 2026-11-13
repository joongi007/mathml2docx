# Inline markers and block replacement

Replace markers spanning formatted runs and insert multiple blocks into cells.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.15_markers
```

[Generated DOCX](../downloads/examples/15_markers.docx)

[Reference PDF](../assets/previews/15_markers.pdf)

## Complete source

```python
"""15 markers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph()
p.add_run("Dear {{na").bold = True
p.add_run("me}}, welcome.").italic = True
cell = document.add_table(1, 1).cell(0, 0)
cell.text = "{{table_content}}"
parser = MathmlToDocx()
parser.replace_html(document, "{{name}}", '<span style="color:teal">Alex</span>')
parser.replace_html(
    document,
    "{{table_content}}",
    "<h2>Inserted blocks</h2><ul><li>First</li><li>Second</li></ul>",
)
save(document, "15_markers.docx")
```
