# Inline formatting and colors

Apply emphasis, underline, strike, scripts, code, and alpha-composited colors.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/04_inline_formatting.html">Open HTML preview</a></div><iframe src="../assets/inputs/04_inline_formatting.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/04_inline_formatting.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/04_inline_formatting.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.04_inline_formatting
```

[Generated DOCX](../downloads/examples/04_inline_formatting.docx)

[Reference PDF](../assets/previews/04_inline_formatting.pdf)

## Complete source

```python
"""04 inline formatting example."""

from mathml2docx import convert

from .support import save

document = convert("""<h1>Inline formatting</h1><p><b>Bold</b> <i>italic</i> <u>underline</u>
<del>removed</del> H<sub>2</sub>O x<sup>2</sup> <code>code()</code></p>
<p style="font-family:DejaVu Sans;font-size:14pt;color:navy">Named color and font</p>
<p style="background-color:blue"><span style="background-color:rgba(255,0,0,.5)">Purple blend</span></p>
<pre>first\tsecond\n  indented code</pre>""")
save(document, "04_inline_formatting.docx")
```
