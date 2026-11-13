# MathML recovery and image fallbacks

Preserve unsupported source or embed an explicitly supplied rendered expression.

## Compare input and output

Compare the actual HTML/MathML input in your browser with the generated DOCX exported to PDF by LibreOffice. Open the DOCX in Word to inspect editable equations.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>Browser · HTML / MathML</h3><a href="../assets/inputs/29_math_fallbacks.html">Open HTML preview</a></div><iframe src="../assets/inputs/29_math_fallbacks.html" title="Browser · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/29_math_fallbacks.pdf">Open PDF</a></div><iframe src="../assets/pdf-pages/29_math_fallbacks.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

For Markdown and LaTeX examples, the browser shows the generated HTML or MathML. Browser MathML support, Word styles, fonts and page layout can produce different results.

The PDF panel shows page images. Open the original PDF to zoom, search or select text, or download the DOCX to edit it.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.29_math_fallbacks
```

[Generated DOCX](../downloads/examples/29_math_fallbacks.docx)

[Reference PDF](../assets/previews/29_math_fallbacks.pdf)

## Complete source

```python
"""Explicit recovery: preserve MathML source or embed a known rendered image."""

from pathlib import Path

from mathml2docx import MathmlToDocx

from .support import save

# This sample ships two pre-rendered expressions. Replace this lookup with your
# own trusted renderer to handle other notations; do not substitute an unrelated image.
BOXED_X = (
    '<math alttext="boxed x"><menclose notation="box"><mi>x</mi></menclose></math>'
)
CIRCLED_X = (
    '<math alttext="circled x"><menclose notation="circle"><mi>x</mi></menclose></math>'
)


def fallback(source, error):
    if source == CIRCLED_X:
        return (Path(__file__).parent / "assets/circled-x.png").read_bytes()
    if source == BOXED_X:
        return (Path(__file__).parent / "assets/boxed-x.png").read_bytes()
    return "[Unconverted MathML] " + source


parser = MathmlToDocx(math_target="libreoffice", mathml_fallback=fallback)
document = parser.convert(
    "<h1>Recovering unsupported notation</h1><p>The following circled x is an image: "
    + CIRCLED_X
    + ".</p>"
)
parser.add_html_to_document(
    "<p>A boxed x uses the same explicit recovery: " + BOXED_X + ".</p>", document
)
parser.add_html_to_document(
    "<p>Unrecognized input remains visible as source:</p><math><unknown><mi>y</mi></unknown></math>",
    document,
)
save(document, "29_math_fallbacks.docx")
```
