# 북마크 교체

Word 북마크의 범위를 HTML로 교체하고 앞뒤 내용과 북마크를 보존합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다. 이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/16_bookmarks.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/16_bookmarks.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/16_bookmarks.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/16_bookmarks.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.16_bookmarks
```

[생성된 DOCX](../downloads/examples/16_bookmarks.docx)

[참조 PDF](../assets/previews/16_bookmarks.pdf)

## 전체 코드

```python
"""16 bookmarks example."""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph("Before ")
start = OxmlElement("w:bookmarkStart")
start.set(qn("w:id"), "1")
start.set(qn("w:name"), "result")
p._p.append(start)
p.add_run("replace this")
end = OxmlElement("w:bookmarkEnd")
end.set(qn("w:id"), "1")
p._p.append(end)
p.add_run(" after.")
MathmlToDocx().replace_bookmark(document, "result", "<b>new result</b>")
save(document, "16_bookmarks.docx")
```
