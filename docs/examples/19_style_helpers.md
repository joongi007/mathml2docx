# Style helpers

Explicitly apply CSS text to a target run or paragraph.

## Run

```sh
python -m examples.19_style_helpers
```

[Generated DOCX](../downloads/examples/19_style_helpers.docx)

[Reference PDF](../assets/previews/19_style_helpers.pdf)

## Complete source

```python
"""19 style helpers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
paragraph = document.add_paragraph()
run = paragraph.add_run("Explicit targets")
parser = MathmlToDocx()
parser.add_styles_to_run(
    "color:navy;font-weight:bold;text-decoration:underline", run=run
)
parser.add_styles_to_paragraph("margin-left:1cm;text-align:right", paragraph=paragraph)
save(document, "19_style_helpers.docx")
```
