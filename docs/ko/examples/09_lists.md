# 목록 번호와 중첩

시작 번호, li의 value, 독립 목록 재시작, 중첩 번호·글머리를 보여 줍니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/09_lists.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/09_lists.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/09_lists.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/09_lists.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.09_lists
```

[생성된 DOCX](../downloads/examples/09_lists.docx)

[참조 PDF](../assets/previews/09_lists.pdf)

## 전체 코드

```python
"""09 lists example."""

from mathml2docx import convert

from .support import save

document = convert(
    '<h1>Lists</h1><ol start="3"><li>Third<ol><li>Nested first</li><li>Nested second</li></ol></li><li value="8">Eighth</li></ol><ol><li>Restart at one</li></ol><ul><li>Bullet<ul><li>Nested bullet</li></ul></li></ul>'
)
save(document, "09_lists.docx")
```
