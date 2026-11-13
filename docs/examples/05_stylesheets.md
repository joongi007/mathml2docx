# CSS stylesheets

Combine style tags, explicit external CSS loading, selectors, inheritance, and important precedence.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.05_stylesheets
```

[Generated DOCX](../downloads/examples/05_stylesheets.docx)

[Reference PDF](../assets/previews/05_stylesheets.pdf)

## Complete source

```python
"""05 stylesheets example."""

from mathml2docx import MathmlToDocx

from .support import save

assets = {
    "theme.css": ".notice {color:teal;font-size:16pt} .notice strong {color:purple}"
}
parser = MathmlToDocx(
    stylesheet_loader=assets.__getitem__, stylesheet="h1 {color:navy}"
)
document = parser.parse_html_string("""<link rel="stylesheet" href="theme.css">
<style>#main {color:red} .notice {color:green !important}</style>
<h1>CSS cascade</h1><p id="main" class="notice" style="color:orange">Important wins. <strong>Nested selector</strong></p>""")
save(document, "05_stylesheets.docx")
```
