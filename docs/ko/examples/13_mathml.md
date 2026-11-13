# MathML 수식

분수·위아래 첨자·n제곱근·울타리·행렬 및 문장 안의 편집 가능한 수식을 생성합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/13_mathml.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/13_mathml.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/13_mathml.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/13_mathml.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.13_mathml
```

[생성된 DOCX](../downloads/examples/13_mathml.docx)

[참조 PDF](../assets/previews/13_mathml.pdf)

## 전체 코드

```python
"""13 mathml example."""

from mathml2docx import MathmlToDocx

from .support import save

parser = MathmlToDocx()
document = parser.parse_mathml("<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>")
parser.add_html_to_document(
    """<h2>Inline and block math</h2><p>Area:
<math display="inline"><mi>A</mi><mo>=</mo><mi>π</mi><msup><mi>r</mi><mn>2</mn></msup></math>.</p>
<math><mroot><mi>x</mi><mn>3</mn></mroot><mo>+</mo><msubsup><mi>x</mi><mn>1</mn><mn>2</mn></msubsup></math>
<math><mfenced open="[" close="]"><mtable><mtr><mtd><mn>1</mn></mtd><mtd><mn>2</mn></mtd></mtr><mtr><mtd><mn>3</mn></mtd><mtd><mn>4</mn></mtd></mtr></mtable></mfenced></math>""",
    document,
)
save(document, "13_mathml.docx")
```
