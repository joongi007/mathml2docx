# LaTeX 수식

선택 의존성으로 합계·분수·제곱근·행렬을 Word 수식으로 변환합니다.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

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

# Install: python -m pip install "mathml2docx[latex]"
parser = MathmlToDocx()
document = parser.parse_latex(
    r"\sum_{i=1}^{n} \frac{i^2}{\sqrt{x}} + \begin{pmatrix}a&b\\c&d\end{pmatrix}"
)
save(document, "14_latex.docx")
```
