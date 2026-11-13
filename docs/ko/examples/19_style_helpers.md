# 서식 헬퍼

대상 run과 paragraph에 CSS 문자열을 명시적으로 적용합니다.

## 입력과 출력 비교

이 예제는 Word 객체에 직접 스타일을 적용하므로 HTML 입력이 없습니다. PDF에서 결과를 확인하세요.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/19_style_helpers.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/19_style_helpers.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.19_style_helpers
```

[생성된 DOCX](../downloads/examples/19_style_helpers.docx)

[참조 PDF](../assets/previews/19_style_helpers.pdf)

## 전체 코드

```python
"""19 style helpers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
paragraph = document.add_paragraph()
run = paragraph.add_run("Explicit targets")
parser = MathmlToDocx()
parser.add_styles_to_run(
    "color:navy;font-weight:bold;text-decoration:underline", run=run
)
parser.add_styles_to_paragraph("margin-left:1cm;text-align:right", paragraph=paragraph)
save(document, "19_style_helpers.docx")
```
