# Complex equation gallery

Compare 20 authored MathML and 24 LaTeX examples covering nested fractions, matrices, calculus, accents, and math alphabets.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.23_complex_equations
```

[Generated DOCX](../downloads/examples/23_complex_equations.docx)

[Reference PDF](../assets/previews/23_complex_equations.pdf)

## Complete source

```python
"""Complex equations for inspection in Word and independent renderers."""

from docx import Document

from mathml2docx import mathml_to_omml
from mathml2docx.math import latex_to_omml

from .math_corpus import LATEX, SHOWCASE
from .support import save

document = Document()
document.add_heading("Complex equation gallery", 0)
document.add_paragraph(
    "Original examples: inspect fraction bars, script roles, radicals, accents, matrices and mathematical alphabets."
)
for index, (name, body) in enumerate(SHOWCASE, 1):
    document.add_heading(f"M{index:02d}: {name}", 2)
    document.add_paragraph()._p.append(mathml_to_omml("<math>" + body + "</math>"))
document.add_page_break()
document.add_heading("LaTeX frontend", 1)
for index, source in enumerate(LATEX, 1):
    document.add_heading(f"L{index:02d}", 2)
    document.add_paragraph(source).paragraph_format.keep_with_next = True
    document.add_paragraph()._p.append(latex_to_omml(source))
save(document, "23_complex_equations.docx")
```

## Visual comparison notes

Some equation properties vary between Word and LibreOffice, particularly phantom spacing, bevelled fractions and string quotes. Compare the input with the generated document when those details matter.

[Validation scope and limitations](../11-validation.md)
