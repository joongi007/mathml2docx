# Links and anchors

Use external/internal links, id/name anchors, and links without href.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/20_links.html">Open HTML preview</a></div><iframe src="../assets/inputs/20_links.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/20_links.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/20_links.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.20_links
```

[Generated DOCX](../downloads/examples/20_links.docx)

[Reference PDF](../assets/previews/20_links.pdf)

## Complete source

```python
"""20 links example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1 id="intro">Introduction</h1><p><a href="https://example.com">External link</a> <a href="#intro">Back to introduction</a> <a name="legacy">Named anchor</a> <a>Link without href</a></p>'
)
save(document, "20_links.docx")
```
