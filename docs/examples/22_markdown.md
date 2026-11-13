# Markdown integration

Convert headings, tables, lists, code, and strikethrough with the optional frontend.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/22_markdown.html">Open HTML preview</a></div><iframe src="../assets/inputs/22_markdown.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/22_markdown.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/22_markdown.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.22_markdown
```

[Generated DOCX](../downloads/examples/22_markdown.docx)

[Reference PDF](../assets/previews/22_markdown.pdf)

## Complete source

```python
"""22 markdown example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install "mathml2docx[markdown]"
source = """# Markdown example

1. First
2. Second

| A | B |
|---|---|
| 1 | 2 |

~~Deleted content~~

```python
print('hello')
```
"""
document = MathmlToDocx().parse_markdown(source)
save(document, "22_markdown.docx")
```
