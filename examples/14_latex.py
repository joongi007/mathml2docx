"""14 latex example."""

from mathml2docx import MathmlToDocx

from .support import save

# Install: python -m pip install '.[latex]'
parser = MathmlToDocx()
document = parser.parse_latex(
    r"\sum_{i=1}^{n} \frac{i^2}{\sqrt{x}} + \begin{pmatrix}a&b\\c&d\end{pmatrix}"
)
save(document, "14_latex.docx")
