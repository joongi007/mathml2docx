# List numbering and nesting

Use start values, li values, independent restarts, and nested numbered/bulleted lists.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/09_lists.html">Open HTML preview</a></div><iframe src="../assets/inputs/09_lists.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/09_lists.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/09_lists.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.09_lists
```

[Generated DOCX](../downloads/examples/09_lists.docx)

[Reference PDF](../assets/previews/09_lists.pdf)

## Complete source

```python
"""09 lists example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1>Lists</h1><ol start="3"><li>Third<ol><li>Nested first</li><li>Nested second</li></ol></li><li value="8">Eighth</li></ol><ol><li>Restart at one</li></ol><ul><li>Bullet<ul><li>Nested bullet</li></ul></li></ul>'
)
save(document, "09_lists.docx")
```
