# 파일·인코딩·다국어

UTF-8 입력, 한글·일본어·악센트 문자와 정확한 출력 확장자를 다룹니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/02_files_unicode.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/02_files_unicode.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/02_files_unicode.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/02_files_unicode.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.02_files_unicode
```

[생성된 DOCX](../downloads/examples/02_files_unicode.docx)

[참조 PDF](../assets/previews/02_files_unicode.pdf)

## 전체 코드

```python
"""02 files unicode example."""

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "unicode.html"
source.write_text(
    "<h1>안녕하세요</h1><p>Índice — 日本語 — Ελληνικά</p>", encoding="utf-8"
)
output = MathmlToDocx().parse_html_file(
    source, OUTPUT / "02_files_unicode.docx", encoding="utf-8"
)
print(output)
```
