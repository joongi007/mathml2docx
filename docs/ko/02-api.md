# API와 옵션

`python -m pip install mathml2docx`로 설치하세요. LaTeX·Markdown 선택 의존성은
[시작하기](01-getting-started.md)에서 설명합니다.

## 공개 API

```python
from mathml2docx import convert, MathmlToDocx, TableStyle, ParagraphStyle

convert('<p>내용</p>', 'output.docx', paragraph_style=ParagraphStyle.NORMAL)
parser = MathmlToDocx(table_style=TableStyle.GRID)
```

`HtmlToDocx`도 기존 이름으로 제공하며, 새 코드에는 `MathmlToDocx`를 권장합니다.

| 메서드 | 결과 |
| --- | --- |
| `convert(html, output=None, **options)` | Document 반환, 출력 경로가 있으면 저장 |
| `parser.convert(html, output=None)` | 현재 설정으로 변환 |
| `parse_html_string(html)` | 새 Document 반환 |
| `parse_html_file(input, output=None, encoding='utf-8')` | 저장한 Path 반환. 확장자는 한 번만 추가 |
| `parse_mathml(source)` | 네이티브 OMML 수식이 든 Document 반환 |
| `parse_markdown(source)` | 선택 의존성 Markdown으로 제목·표·코드·취소선 변환 |
| `parse_latex(source)` | 선택 의존성 `latex2mathml`로 변환한 Document 반환. Python 3.6.2 이상 필요 |
| `add_html_to_document(html, document)` | Document·표 셀·DocxTemplate에 추가 |
| `add_html_to_cell(html, cell)` | 표 셀에 추가 |
| `add_image_to_cell(cell, image)` | BytesIO 이미지를 문서·셀에 추가 |
| `copy_settings_from(other)` | 모든 옵션·스타일 매핑 독립 복사 |
| `replace_html(document, marker, html)` | 여러 run에 걸친 고유 마커를 인라인·블록 HTML로 교체 |
| `replace_bookmark(document, name, html)` | 북마크 범위를 HTML로 교체 |
| `get_origin()` | 현재 변환기 반환 |

## 생성자 옵션

| 인자 | 기본값 | 동작 |
| --- | --- | --- |
| `fix_html` | `True` | 호환용 인자. 트리 파싱은 항상 수행 |
| `images` | `True` | 이미지 처리 여부 |
| `tables` | `True` | 표 처리 여부 |
| `mathml` | `True` | MathML 처리 여부 |
| `styles` | `True` | 인라인 서식 처리 여부 |
| `img_src_base_path` | `None` | 이 경로 아래의 로컬 이미지만 허용 |
| `image_loader` | `None` | 자산 출처를 받아 bytes·파일 객체를 반환하는 명시적 콜백 |
| `table_style` | `None` | Word 표 스타일 이름 또는 TableStyle 값 |
| `paragraph_style` | `None` | Word 문단 스타일 이름 또는 ParagraphStyle 값 |
| `stylesheet` | `""` | 추가 CSS 스타일시트 문자열 |
| `stylesheet_loader` | `None` | 외부 CSS 경로를 받아 CSS 문자열을 반환하는 명시적 콜백 |
| `style_map` | `None` | 태그 → class → Word 스타일 이름 매핑 |
| `default_math_display` | `'inline'` | MathML의 display를 생략했을 때 배치. `'block'`으로 이전 배치 선택 |
| `unsupported_math` | `'error'` | `'error'`는 예외 발생, `'text'`는 미지원 수식의 전체 XML 표시 |
| `mathml_preprocessor` | `None` | 완전한 MathML 문자열을 받아 반환하는 콜백 |
| `mathml_fallback` | `None` | `(source, error)`를 받아 텍스트·이미지 바이트·`BytesIO`를 반환하는 콜백 |
| `math_target` | `'word'` | `'libreoffice'`는 정체 식별자를 명시하고 표시 손실이 알려진 표기를 대체 처리 |

생성 후 `parser.options.images = False`로 설정을 변경할 수 있습니다.
표·문단 스타일과 매핑은 `parser.table_style`, `parser.paragraph_style`, `parser.style_map`에
설정합니다. 사용하는 Word 템플릿에 해당 스타일이 있어야 합니다.

기본 이미지 로더는 data URL과 명시한 로컬 기준 경로만 처리합니다. URL 다운로드는
자동으로 하지 않습니다. `image_loader`에서 네트워크를 사용한다면 호출자가 대상·크기·
시간 제한을 적용해야 합니다.

수식·CSS 지원 범위와 호환성 변경은 [마이그레이션 문서](05-migration.md)를 참고하세요.

전체 실행 코드는 [예제 모음](examples/00-index.md), 기능별 조합은 [작업별 사용법](08-recipes.md)을 참고하세요.

[수식 배치·테두리·화학 표기·미지원 입력 처리](03-mathematics.md)를 참고하세요.
