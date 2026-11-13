# docxtpl 연동

Jinja 템플릿을 렌더링한 뒤 HTML 문단을 추가합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다. 이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/17_docxtpl.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/17_docxtpl.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/17_docxtpl.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/17_docxtpl.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.17_docxtpl
```

[생성된 DOCX](../downloads/examples/17_docxtpl.docx)

[참조 PDF](../assets/previews/17_docxtpl.pdf)

## 전체 코드

```python
"""17 docxtpl example."""

from docx import Document
from docxtpl import DocxTemplate

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "jinja_template.docx"
document = Document()
document.add_paragraph("Hello {{ name }}")
document.save(source)
template = DocxTemplate(source)
template.render({"name": "Alex"})
MathmlToDocx().add_html_to_document(
    "<h2>Added HTML section</h2><p>After Jinja rendering.</p>", template
)
output = OUTPUT / "17_docxtpl.docx"
template.save(output)
print(output)
```
