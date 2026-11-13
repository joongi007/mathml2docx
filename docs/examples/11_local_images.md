# Local images

Read files below an explicit base directory; paths outside it are refused.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/11_local_images.html">Open HTML preview</a></div><iframe src="../assets/inputs/11_local_images.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/11_local_images.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/11_local_images.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.11_local_images
```

[Generated DOCX](../downloads/examples/11_local_images.docx)

[Reference PDF](../assets/previews/11_local_images.pdf)

## Complete source

```python
"""11 local images example."""

from mathml2docx import MathmlToDocx

from .support import ROOT, save

parser = MathmlToDocx(img_src_base_path=ROOT / "assets")
document = parser.parse_html_string(
    '<h1>Local assets</h1><p><img src="swatch.png" width="120"></p>'
)
save(document, "11_local_images.docx")
```
