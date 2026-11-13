# Inline base64 images

Place data URL images inside a paragraph and set their display width.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/10_data_images.html">Open HTML preview</a></div><iframe src="../assets/inputs/10_data_images.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/10_data_images.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/10_data_images.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.10_data_images
```

[Generated DOCX](../downloads/examples/10_data_images.docx)

[Reference PDF](../assets/previews/10_data_images.pdf)

## Complete source

```python
"""10 data images example."""

import base64

from mathml2docx import convert

from .support import ROOT, save

encoded = base64.b64encode((ROOT / "assets/swatch.png").read_bytes()).decode()
document = convert(
    '<p>Before <img alt="color swatch" src="data:image/png;base64,'
    + encoded
    + '" style="width:96px"> after</p>'
)
save(document, "10_data_images.docx")
```
