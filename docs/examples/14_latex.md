# LaTeX equations

Use the optional frontend for sums, fractions, roots, and matrices.

## Run

```sh
python -m examples.14_latex
```

[Generated DOCX](../downloads/examples/14_latex.docx)

[Reference PDF](../assets/previews/14_latex.pdf)

## Complete source

```python
"""14 latex example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install '.[latex]'
parser = MathmlToDocx()
document = parser.parse_latex(
    r"\sum_{i=1}^{n} \frac{i^2}{\sqrt{x}} + \begin{pmatrix}a&b\\c&d\end{pmatrix}"
)
save(document, "14_latex.docx")
```
