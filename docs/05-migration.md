# 1.0.0으로 옮기기

1.0.0은 XSL 파일 없이 MathML을 Word 수식(OMML)으로 변환합니다.
패키지 버전은 변경했지만 PyPI 배포는 별도로 진행해야 합니다.

```python
from mathml2docx import convert, MathmlToDocx, TableStyle, ParagraphStyle

convert('<h1>보고서</h1><p>내용</p>', 'report.docx',
        table_style=TableStyle.GRID, paragraph_style=ParagraphStyle.NORMAL)

parser = MathmlToDocx()
parser.parse_mathml('<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>').save('fraction.docx')
# python -m pip install 'mathml2docx[latex]'
parser.parse_latex(r'\frac{1}{2} + x^2').save('equation.docx')
```

## 달라지는 동작

- 배포 패키지는 Python 3.6 이상을 지원합니다. 개발·문서 도구는 Python 3.10 이상에서 uv로 관리합니다.
- `parse_html_file(input, output)`은 `.docx`를 중복해서 붙이지 않습니다.
  출력 이름 생략 시 입력 파일의 확장자를 `.docx`로 바꿉니다. 생성 경로를 반환합니다.
- HTML은 항상 BeautifulSoup 트리로 처리합니다. `fix_html` 옵션은 기존 호출 호환용이며
  `False`여도 트리 파싱을 생략하지 않습니다.
- `get_origin()`은 동일한 변환기 객체를 반환합니다. 옵션은 한 곳에 저장하고
  `parser.options.images`와 `parser.options['images']`를 모두 지원합니다.
- `copy_settings_from()`은 모든 옵션과 스타일 매핑을 독립적으로 복사합니다.
- 서식 헬퍼는 숨은 파서 상태 대신 대상을 명시합니다.
  `add_styles_to_run(css, run=run)`, `add_styles_to_paragraph(css, paragraph=paragraph)`를 사용하세요.
- URL 이미지는 자동으로 다운로드하지 않습니다. 기본적으로 data URL만 처리합니다.
  로컬 이미지는 `img_src_base_path` 아래 파일만 읽습니다. URL·사용자 자산 처리는
  `image_loader(source)` 콜백으로 직접 제공하며, 콜백이 `bytes`나 파일 객체를 반환해야 합니다.
- Office XSL은 제거했습니다. 과거 릴리스와 Git 기록에는 남아 있으므로 이번 변경이
  과거 배포본의 라이선스 상태까지 해결하지는 않습니다.
- 미지원 MathML은 `UnsupportedMathMLError`로 알려 줍니다. 전체 MathML 규격이나
  모든 LaTeX 패키지를 지원한다고 보장하지 않습니다.

## 지원하는 수식

기본 토큰(`mi`, `mn`, `mo`, `mtext`, `ms`), 그룹, 분수, 위·아래 첨자, 제곱근과 n제곱근,
울타리, 위·아래 한계, 악센트, 직사각 행렬, phantom을 지원합니다. `semantics`는 첫
표현식을 변환하고 주석은 제외합니다. `menclose`, `mmultiscripts`, Content MathML 등은
현재 지원하지 않습니다. 글꼴·간격·악센트 등 MathML 표현 속성 전체를 재현하지는 않습니다.
LaTeX는 `latex2mathml`이 생성한 MathML에 이 지원 범위가 적용됩니다.
HTML 안의 `$...$`는 자동으로 LaTeX로 해석하지 않습니다.

## 스타일·템플릿

인라인 CSS의 색상, 배경색, 글꼴, 크기, 굵기, 기울임, 밑줄, 취소선, 정렬, 여백,
들여쓰기, 페이지 나누기를 처리합니다. RGBA 알파는 0일 때 투명 처리하고 그 외에는 상위 배경색과 합성합니다.
`<style>` 선택자 규칙과 명시적 로더로 제공한 외부 CSS를 적용합니다.
Markdown 입력은 `markdown` extra를 설치한 뒤 `parse_markdown()`으로 변환합니다.
표·코드 블록·`~~text~~` 취소선을 기본 지원합니다. 별도 Markdown 파서의 HTML도 전달할 수 있습니다. 글꼴 크기만으로 제목을 추측하지 않습니다.

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(style_map={'p': {'quotation': 'Quote'}})
document = Document('template.docx')
parser.add_html_to_document('<p class="quotation">인용</p>', document)
# 고유 마커를 HTML로 교체합니다. 여러 run에 걸친 마커도 지원합니다.
parser.replace_html(document, '{{content}}', '<p>삽입할 내용</p>')
# 문장 안의 마커나 기존 북마크에도 삽입할 수 있습니다.
# parser.replace_bookmark(document, 'result', '<b>결과</b>')
document.save('output.docx')
```

기존 Document의 스타일과 목록 정의를 사용합니다. 새 목록은 매번 새 번호 정의를
생성하므로 번호가 재시작하고, 중첩 목록은 깊이에 맞는 번호 수준을 사용합니다.
`DocxTemplate` 객체는 `get_docx()`를 통해 내용 추가를 지원합니다.

## CLI

```sh
mathml2docx input.html output.docx
python -m mathml2docx input.tex equation.docx --format latex
```

기존 출력 파일은 거절하며 `--force`로 덮어쓸 수 있습니다.
