# 파일·인코딩·다국어

UTF-8 입력, 한글·일본어·악센트 문자와 정확한 출력 확장자를 다룹니다.

## 실행

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
