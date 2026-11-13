# Options and settings copies

Disable images, tables, math, or styles and independently copy settings.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/18_options.html">Open HTML preview</a></div><iframe src="../assets/inputs/18_options.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/18_options.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/18_options.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.18_options
```

[Generated DOCX](../downloads/examples/18_options.docx)

[Reference PDF](../assets/previews/18_options.pdf)

## Complete source

```python
"""18 options example."""

from mathml2docx import MathmlToDocx

from .support import save

source = MathmlToDocx(images=False, tables=False, mathml=False)
parser = MathmlToDocx()
parser.copy_settings_from(source)
parser.options.styles = False
assert parser.get_origin() is parser
html = '<h1>Options</h1><p><b>Plain</b><img src="missing"></p><table><tr><td>Skipped</td></tr></table><math><mi>x</mi></math>'
save(parser.parse_html_string(html), "18_options.docx")
```
