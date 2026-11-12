# 작업별 사용법

[실행 예제 30개](examples/00-index.md)는 전체 코드와 생성 DOCX, LibreOffice에서 만든 PDF를 제공합니다.
이 페이지는 자주 조합하는 사용법과 저수준 API를 모았습니다.

## 파일 여러 개를 한꺼번에 변환

```python
from pathlib import Path
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
Path('output').mkdir(exist_ok=True)
for source in Path('input').glob('*.html'):
    parser.parse_html_file(source, Path('output') / source.with_suffix('.docx').name)
```

출력 폴더를 먼저 만드세요. 파서를 재사용해도 각 `parse_html_string()`·`parse_html_file()` 호출은
새 문서를 만듭니다. 같은 문서에 여러 HTML을 붙일 때는 `add_html_to_document()`를 사용합니다.

## 스타일시트와 선택자

```python
from mathml2docx import MathmlToDocx

stylesheets = {'theme.css': '.notice {color:navy} p > strong {color:teal}'}
parser = MathmlToDocx(
    stylesheet='h1 {font-size:20pt}',
    stylesheet_loader=stylesheets.__getitem__,
)
document = parser.parse_html_string('''
<link rel="stylesheet" href="theme.css">
<style>.notice {background-color:rgba(255,200,0,.25)}</style>
<h1>안내</h1><p class="notice">중요한 <strong>내용</strong></p>
''')
document.save('styled.docx')
```

`<style>`, 선택자, specificity, 소스 순서, 상속, 인라인 스타일, `!important`를 처리합니다.
`@media print`·`all`을 적용합니다. 외부 `<link>`와 `@import`는 명시한 로더가 있을 때만
읽습니다. CSS를 적용하더라도 Word에 대응시키는 속성은 아래 지원 표의 범위입니다.
Flexbox·Grid·브라우저 JavaScript 실행이나 픽셀 단위 복제는 제공하지 않습니다.

## 문장 중간의 마커·북마크

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
document = Document('template.docx')
parser.replace_html(document, '{{customer}}', '<b>홍길동</b>')
parser.replace_bookmark(document, 'result', '<h2>분석 결과</h2><p>상세 내용</p>')
document.save('filled.docx')
```

마커가 여러 run으로 나뉘어 있어도 찾습니다. 같은 문서 안에 마커가 여러 번 있으면
실수로 여러 곳을 바꾸지 않도록 거절합니다. 인라인 HTML은 같은 문단에 삽입하고, 블록
HTML은 앞뒤 텍스트 사이에 별도 블록으로 삽입합니다. 본문과 표 셀에서 사용할 수 있습니다.
북마크는 한 문단 또는 같은 컨테이너 안의 여러 문단에 걸칠 수 있습니다. 서로 다른 표 셀에
걸친 북마크는 거절합니다. 기존 run의 서식·이미지·링크와 삽입한 HTML의 관계를 보존합니다.
머리글·바닥글의 마커 치환은 현재 본문 검색 대상에 포함하지 않습니다.

## Word 템플릿에서 글꼴·탭 정지 지정

```python
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from mathml2docx import MathmlToDocx

document = Document()
normal = document.styles['Normal']
normal.font.name = 'Noto Sans CJK KR'
normal.font.size = Pt(11)
normal.paragraph_format.tab_stops.add_tab_stop(
    Cm(12), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
MathmlToDocx().add_html_to_document('<pre>항목\t금액</pre>', document)
document.save('tabs.docx')
```

글꼴 이름을 지정해도 폰트를 파일에 포함하지는 않습니다. 문서를 여는 환경에 해당 글꼴이
있어야 합니다. 일반 HTML 공백은 접히며, `pre`·`white-space:pre-wrap`에서는 탭·줄바꿈을 보존합니다.

## 수식 XML 직접 삽입과 미지원 입력 처리

```python
from docx import Document
from mathml2docx import mathml_to_omml, latex_to_omml, UnsupportedMathMLError

document = Document()
paragraph = document.add_paragraph('계산: ')
paragraph._p.append(mathml_to_omml('<math><msup><mi>x</mi><mn>2</mn></msup></math>'))
paragraph._p.append(latex_to_omml(r'\frac{1}{2}'))
try:
    mathml_to_omml('<math><unknown/></math>')
except UnsupportedMathMLError as error:
    print(error)  # 입력을 조용히 삭제하지 않고 미지원 요소를 알려 줍니다.
document.save('equations.docx')
```

저수준 API는 lxml OMML 요소를 반환합니다. 보통은 Document를 반환하는
`parse_mathml()`·`parse_latex()`가 더 간편합니다. LaTeX는 `latex` extra가 필요합니다.
전체 지원 범위는 [마이그레이션 문서](05-migration.md)의 수식 표를 참고하세요.

## HTML 지원 범위

| 분야 | 지원 |
| --- | --- |
| 구조 | p, div, section, main, article, header, footer, aside, blockquote, pre, figure, figcaption, h1~h6, title |
| 글자 | b/strong, i/em, u, del/s/strike, sup/sub, code, span, br, hr |
| 링크 | 외부 URL·메일·문서 내부 링크, id·name 앵커, href 없는 a의 텍스트 |
| 표 | table, thead/tbody/tfoot, th/td, rowspan/colspan, 빈 병합 셀, 중첩 표 |
| 목록 | ol/ul/li, start·value, 중첩 목록, 독립 번호 재시작 |
| 이미지 | base64 data URL, 지정 경로 아래의 로컬 파일, 명시적 자산 로더, 인라인 배치, width/height |
| CSS 선택 | type·class·id·복합 선택자, 자식·형제 선택자, 정적 pseudo-class, 인라인 및 important 우선순위 |
| CSS 서식 | color, background-color, font-family/size/weight/style, text-decoration, vertical-align |
| CSS 문단 | text-align, margin, text-indent, line-height(%), white-space, display:none, visibility:hidden, 페이지 나누기 |
| CSS 표 | width, border, 셀 배경·글자·정렬, 표 정렬 |
| 템플릿 | 기존 Document, docxtpl, class→Word 문단·문자 스타일, 인라인 마커·북마크 치환 |

## CLI

```sh
python -m mathml2docx input.html output.docx
mathml2docx input.html output.docx --encoding utf-8
mathml2docx equation.tex equation.docx --format latex
mathml2docx article.md article.docx --format markdown
mathml2docx equation.mathml equation.docx --format mathml
mathml2docx input.html output.docx --force
```

기본적으로 기존 출력을 덮어쓰지 않습니다. `--force`는 명시적으로 덮어쓰며 입력 파일과
같은 경로는 거절합니다. Python `Document.save()`는 python-docx의 저장 동작을 따릅니다.

## Markdown 바로 변환

```python
from mathml2docx import MathmlToDocx

# python -m pip install ".[markdown]"
MathmlToDocx().parse_markdown("# 제목\n\n~~삭제~~와 `코드`").save("article.docx")
```

표·fenced code·취소선을 포함합니다. 코드 안의 `~~`는 취소선으로 해석하지 않습니다.

## 한글과 글꼴

문서 뷰어에 있는 CJK 글꼴을 지정하세요. 예제 24~27번은 맑은 고딕을 사용합니다.
HTML 조각에는 `p` 등 실제 요소를 선택하거나 컨테이너의 인라인 스타일을 사용하세요.
`body` 선택자를 사용하려면 입력에 `<body>` 요소가 있어야 합니다.

```python
from mathml2docx import convert

convert('<div style="font-family:Malgun Gothic"><p>한글과 English</p></div>', 'korean.docx')
```

CSS 글꼴은 라틴·동아시아·복합 문자 슬롯에 기록하며, 글꼴 파일은 내장하지 않습니다.
