# Complex equation gallery

Compare 20 authored MathML and 24 LaTeX examples covering nested fractions, matrices, calculus, accents, and math alphabets.

## Run

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

In the LibreOffice 7.3 reference PDF, M17 phantom width, M19 bevelled fractions, and M20 string quotes differ from the intended display. Their structures, properties, and characters are retained in XML, but visual equivalence has not been established. Direct Microsoft Word checks also remain outstanding.

[Validation scope and limitations](../11-validation.md)
