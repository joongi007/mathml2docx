# 수식이 많은 혼합 보고서

수식 120개와 병합·중첩 표, 목록, 이미지, 링크, 다국어 문장과 페이지 나누기를 조합합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/24_dense_report.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/24_dense_report.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/24_dense_report.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/24_dense_report.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.24_dense_report
```

[생성된 DOCX](../downloads/examples/24_dense_report.docx)

[참조 PDF](../assets/previews/24_dense_report.pdf)

## 전체 코드

```python
"""A paginated report combining 120 equations and repeated HTML structures."""

from pathlib import Path

from mathml2docx import convert

from .math_corpus import SHOWCASE
from .support import save

blocks = [
    "<style>body {font-family:'Malgun Gothic';font-size:11pt} h1 {color:navy;font-size:20pt} h2 {font-size:14pt} td {background-color:#eef2ff} .label {font-weight:bold;color:#244488}</style><h1>Mixed mathematical report</h1>"
]
for section in range(5):
    blocks.append(
        f"<h2>Section {section + 1}</h2><p>한글 설명과 mathematical notation in one report.</p>"
    )
    for index, (name, body) in enumerate(SHOWCASE):
        blocks.append(
            f'<p><span class="label">{section + 1}.{index + 1} {name}</span> — before <math display="inline">{body}</math> after <i>formatted explanation</i>.</p>'
        )
        if index % 5 == 0:
            blocks.append(
                '<table><tr><th>Context</th><th>Equation and formatting</th></tr><tr><td rowspan="2">Merged cell</td><td><b>Ratio</b>: <math display="inline"><mfrac><mi>a</mi><mi>b</mi></mfrac></math></td></tr><tr><td><table><tr><td>Nested table</td></tr></table></td></tr></table><ol start="3"><li>Check the numerator and denominator.</li><li>Keep <strong>bold</strong> and <em>italic</em> text.</li></ol><p><a href="https://example.com">Reference link</a> <img src="swatch.png" width="32"> Caption.</p>'
            )
    if section < 4:
        blocks.append('<p style="page-break-after:always">End of section.</p>')
document = convert(
    "<html><body>" + "".join(blocks) + "</body></html>",
    img_src_base_path=str(Path(__file__).resolve().parent / "assets"),
)
save(document, "24_dense_report.docx")
```
