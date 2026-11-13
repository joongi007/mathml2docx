# LaTeX 수식

선택 의존성으로 합계·분수·제곱근·행렬을 Word 수식으로 변환합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/14_latex.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/14_latex.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/14_latex.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/14_latex.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

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
