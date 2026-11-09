# mathml2docx

HTML과 MathML을 **편집 가능한 Word 문서(`.docx`)**로 변환하는 Python 라이브러리입니다.
LaTeX와 Markdown도 선택 기능으로 지원합니다.

Python **3.6 이상**에서 사용할 수 있습니다. Microsoft Office 설치나 `MML2OMML.XSL`은
필요하지 않습니다. MathML을 Python에서 직접 OMML 수식으로 변환합니다.

현재 저장소는 **1.0.0 배포 준비 코드**입니다. 이 버전은 아직 PyPI에 게시하지 않았으므로,
아래 저장소 설치 명령으로 사용하세요. `pip install mathml2docx`는 PyPI에 게시된 버전을 설치합니다.

## 설치

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .

# 필요한 선택 기능만 설치
python -m pip install '.[latex]'
python -m pip install '.[markdown]'
python -m pip install '.[latex,markdown]'
```

라이브러리 사용에는 uv가 필요하지 않습니다. Python 버전에 맞는 호환 의존성이 설치됩니다.
개발·문서 빌드는 최신 Python과 uv를 사용합니다.

## 빠른 시작

```python
from mathml2docx import convert, TableStyle

html = '''<h1>분석 결과</h1>
<p>편집 가능한 수식입니다.</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>
<table><tr><th>항목</th><th>결과</th></tr>
<tr><td>표본 수</td><td>24</td></tr></table>'''

document = convert(html, 'report.docx', table_style=TableStyle.GRID)
```

`convert()`는 python-docx의 `Document`를 반환합니다. 출력 경로를 생략하면 저장하지 않고
반환만 하므로 문서를 더 수정한 뒤 `document.save('report.docx')`로 저장할 수 있습니다.

## 파일·기존 문서·표 셀

```python
from docx import Document
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_html_file('input.html', 'output.docx', encoding='utf-8')

document = Document()  # 기존 템플릿은 Document('template.docx')
parser.add_html_to_document('<h2>추가 내용</h2><p>본문</p>', document)
cell = document.add_table(1, 1).cell(0, 0)
parser.add_html_to_cell('<b>셀 안의 HTML</b><br>다음 줄', cell)
document.save('combined.docx')
```

파일 변환은 `.docx` 확장자를 중복으로 붙이지 않습니다. 출력 이름을 생략하면 입력 파일의
확장자를 `.docx`로 바꾸며, 생성한 경로를 반환합니다.

## LaTeX·Markdown

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_latex(r'\sum_{i=1}^{n} \frac{i^2}{\sqrt{x}}').save('equation.docx')
parser.parse_markdown('# 제목\n\n~~삭제한 내용~~과 `코드`').save('article.docx')
```

각각 `latex`·`markdown` extra가 필요합니다. Markdown은 표·fenced code·취소선을 지원합니다.
HTML 안의 `$...$`는 자동으로 LaTeX로 해석하지 않습니다.

## 스타일·CSS·템플릿

```python
from docx import Document
from mathml2docx import MathmlToDocx, ParagraphStyle, TableStyle

parser = MathmlToDocx(
    table_style=TableStyle.GRID,
    paragraph_style=ParagraphStyle.NORMAL,
    style_map={'p': {'quotation': 'Quote'}},
    stylesheet='.notice {color:navy; background-color:#e0f2fe}',
)

document = Document()
parser.add_html_to_document('<p class="notice">스타일을 적용한 내용</p>', document)
document.add_paragraph('고객: {{name}}')
parser.replace_html(document, '{{name}}', '<b>홍길동</b>')
document.save('styled.docx')
```

`<style>` 선택자·상속·우선순위·`!important`, 인라인 CSS, Word 문단·문자 스타일 매핑을
지원합니다. 여러 run에 걸친 마커, 표 셀의 마커, 기존 북마크 범위도 교체할 수 있습니다.
외부 CSS는 명시적인 `stylesheet_loader`로 제공하며 자동으로 다운로드하지 않습니다.

## 지원 기능

| 분야 | 주요 기능 |
| --- | --- |
| HTML | 제목, 문단, 블록 요소, 줄바꿈, 코드, 링크·앵커, 글자 서식 |
| 표 | 헤더·본문, `rowspan`·`colspan`, 빈 병합 셀, 중첩 표, 폭·테두리·색상 |
| 목록 | 번호 재시작, 중첩, 시작 번호와 항목 번호 지정 |
| 이미지 | data URL, 지정 디렉터리의 로컬 파일, 자산 로더, 인라인 배치·크기 |
| CSS | 정적 선택자·상속·우선순위, 글꼴·색상·여백·정렬·페이지 나누기 |
| MathML | 토큰·그룹, 분수, 위아래 첨자, 근호, 울타리, 한계식·악센트, 행렬·phantom |
| 템플릿 | 기존 Document, docxtpl, 마커·북마크 교체 |
| 선택 기능 | LaTeX, Markdown, CLI, 에이전트용 변환 스킬 |

브라우저 전체 CSS, JavaScript 실행, 모든 MathML·LaTeX 표현을 지원하지는 않습니다.
`menclose`, `mmultiscripts`, Content MathML 등 미지원 수식 요소는
`UnsupportedMathMLError`로 알려 주며 조용히 누락시키지 않습니다. 지원 태그의 표현 속성도
전체를 재현하지는 않습니다. 상세 범위는 [마이그레이션 문서](https://github.com/joongi007/mathml2docx/blob/master/docs/05-migration.md)와 [수식 검증 기록](https://github.com/joongi007/mathml2docx/blob/master/docs/11-validation.md)을 참고하세요.

URL 이미지는 자동으로 가져오지 않습니다. 로컬 이미지는 `img_src_base_path` 아래 파일만
읽으며, 다른 자산은 `image_loader` 콜백으로 제공합니다. 사용자가 제공하는 HTML·로더에
대한 자원 제한과 접근 정책은 사용하는 애플리케이션에 맞게 설정하세요.

## CLI

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx article.md article.docx --format markdown
python -m mathml2docx input.html output.docx --encoding utf-8
```

기존 출력은 기본적으로 거절하며, 명시적인 `--force`로 덮어쓸 수 있습니다.

## 문서와 실행 예제

- [시작하기](https://github.com/joongi007/mathml2docx/blob/master/docs/01-getting-started.md) · [API와 옵션](https://github.com/joongi007/mathml2docx/blob/master/docs/02-api.md)
- [수식 검증과 한계](https://github.com/joongi007/mathml2docx/blob/master/docs/11-validation.md), [다른 도구와 비교](https://github.com/joongi007/mathml2docx/blob/master/docs/12-choosing.md)
- [실행 예제 24개](https://github.com/joongi007/mathml2docx/blob/master/docs/examples/00-index.md): 전체 코드·실행 명령·생성 DOCX·참조 PDF
- [작업별 사용법과 전체 기능 표](https://github.com/joongi007/mathml2docx/blob/master/docs/08-recipes.md)
- [복합 보고서 코드](https://github.com/joongi007/mathml2docx/blob/master/examples/21_report.py) · [참조 PDF](https://github.com/joongi007/mathml2docx/blob/master/docs/assets/previews/21_report.pdf)
- [원본 이슈 49건 대응표](https://github.com/joongi007/mathml2docx/blob/master/docs/07-upstream-audit.md)
- [변환 스킬과 AI 문서](https://github.com/joongi007/mathml2docx/blob/master/docs/03-agents.md): 스킬 ZIP, `llms.txt`, `llms-full.txt`
- [웹 문서 배포 안내](https://github.com/joongi007/mathml2docx/blob/master/docs/04-publishing.md)

웹 문서 배포 주소는 <https://joongi007.github.io/mathml2docx/>입니다.
실제 공개에는 저장소의 GitHub Pages 설정이 필요합니다.

## 개발·검증·배포

uv 0.13.7 이상과 최신 개발용 Python을 사용합니다. `.python-version`은 개발용이며
배포 패키지의 최소 Python 버전을 올리지 않습니다.

```sh
uv sync --locked --extra latex --extra markdown --extra test --group docs --group examples
uv run --no-sync python -m pytest -q
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/build_docs.py
uv build
uv run --no-sync twine check dist/*

# 실제 Python 3.6에서 소스·wheel 설치와 기능 검증: Docker 필요
bash scripts/test_legacy.sh
```

CI는 Python 3.6~3.14의 각 minor 버전과 Windows·macOS의 변환을 검사합니다.
PyPI 업로드는 정식 GitHub Release 게시와 검증을 거치며, 최초 Trusted Publisher 및
`pypi` 환경 승인자 설정이 필요합니다. 일반 푸시로는 업로드하지 않습니다.
[개발·호환성·PyPI 안내](https://github.com/joongi007/mathml2docx/blob/master/docs/09-development-release.md)를 참고하세요.

## 라이선스·출처

이 프로젝트의 코드는 [MIT 라이선스](https://github.com/joongi007/mathml2docx/blob/master/LICENSE)로 제공하며,
[html2docx](https://github.com/pqzx/html2docx)의 저작권 고지를 유지합니다.
의존성에는 각각의 라이선스가 적용됩니다. [제삼자 고지](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md)를 참고하세요.

1.0.0 배포물에는 Office의 `MML2OMML.XSL`이나 이를 로딩하는 코드가 포함되지 않습니다.
현재 수식 변환기는 XSL을 실행하지 않고 OMML 노드를 직접 구성합니다. 과거 Git 이력·
보존 태그·0.x 배포본의 XSL 권한 문제까지 소급해 해결한 것은 아닙니다.
[XSL 출처 조사](https://github.com/joongi007/mathml2docx/blob/master/docs/06-xsl-provenance.md)와 [라이선스 설명](https://github.com/joongi007/mathml2docx/blob/master/docs/10-licensing.md)에
확인한 사실과 남은 불확실성을 기록했습니다.
