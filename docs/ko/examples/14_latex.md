# LaTeX 수식

선택 의존성으로 합계·분수·제곱근·행렬을 Word 수식으로 변환합니다.

## 실행

```sh
python -m examples.14_latex
```

[생성된 DOCX](../downloads/examples/14_latex.docx)

[참조 PDF](../assets/previews/14_latex.pdf)

## 전체 코드

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
