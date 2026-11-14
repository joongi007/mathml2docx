# 시작하기

## 설치

기본 패키지는 Python 3.6 이상, 선택 기능인 LaTeX는 3.6.2 이상을 지원합니다.
아래 방법 중 하나로 PyPI 패키지를 설치하세요. HTML·MathML은 기본 패키지로,
LaTeX·Markdown 입력은 선택 의존성을 추가해 사용합니다. Git이나 저장소 복제는 필요하지 않습니다.

### pip

프로젝트의 Python 환경에서 설치하세요. 환경이 없다면 `python -m venv .venv`로 만들고,
운영체제에 맞는 명령으로 [활성화](https://docs.python.org/3/library/venv.html#how-venvs-work)하세요.

```sh
python -m pip install mathml2docx
```

선택 입력은 필요한 기능에 맞춰 설치합니다.

```sh
python -m pip install "mathml2docx[latex]"
python -m pip install "mathml2docx[markdown]"
# 두 기능을 함께 설치:
python -m pip install "mathml2docx[latex,markdown]"
```

설치된 버전은 다음 명령으로 확인합니다.

```sh
python -m pip show mathml2docx
```

기존 설치는 `python -m pip install --upgrade mathml2docx`로 갱신합니다.
두 선택 기능을 사용한다면 `python -m pip install --upgrade "mathml2docx[latex,markdown]"`을
사용하세요. 저장한 Python 스크립트는 `python report.py`로 실행합니다.

### uv

[uv](https://docs.astral.sh/uv/getting-started/installation/)를 별도로 설치하세요.
새 프로젝트는 `uv init --bare report-project`로 만든 뒤 `cd report-project`로 이동합니다.
기존 uv 프로젝트라면 해당 디렉터리에서 바로 실행하세요.

```sh
uv add mathml2docx
# 두 선택 입력도 함께 사용하려면:
uv add "mathml2docx[latex,markdown]"
uv run python -c "import mathml2docx; print(mathml2docx.__version__)"
```

하나만 필요하면 `uv add "mathml2docx[latex]"` 또는
`uv add "mathml2docx[markdown]"`을 사용하세요. uv는 환경을 관리하고
`pyproject.toml`과 `uv.lock`에 의존성을 기록합니다. 저장한 스크립트는
`uv run python report.py`로 실행합니다.

선언된 버전 범위 안에서 업데이트하려면 다음 명령을 실행하세요.

```sh
uv lock --upgrade-package mathml2docx
uv sync
```

### Poetry

[Poetry](https://python-poetry.org/docs/#installation)를 별도로 설치하세요.
현재 Poetry 도구는 Python 3.10 이상이 필요합니다. 새 프로젝트 디렉터리에서는
`poetry init`을 실행하고 지원할 인터프리터에 맞춰 Python 버전 범위를 지정하세요.
기존 Poetry 프로젝트라면 해당 디렉터리에서 바로 실행합니다.

```sh
poetry add mathml2docx
# 두 선택 입력도 함께 사용하려면:
poetry add "mathml2docx[latex,markdown]"
poetry run python -c "import mathml2docx; print(mathml2docx.__version__)"
```

하나만 필요하면 `poetry add "mathml2docx[latex]"` 또는
`poetry add "mathml2docx[markdown]"`을 사용하세요. Poetry는 `pyproject.toml`과
`poetry.lock`에 의존성을 기록합니다. 저장한 스크립트는 `poetry run python report.py`로
실행하고, 선언된 버전 범위 안에서 업데이트하려면 `poetry update mathml2docx`를 사용하세요.

### 버전 호환성

패키지 관리 도구의 Python 요구사항은 라이브러리와 별개입니다. Python 3.6에서 라이브러리를
사용하기 위해 최신 도구까지 Python 3.6에 설치할 필요는 없습니다. 반복 설치에는 프로젝트의
requirements나 lockfile을 보관하세요. 0.x에서 이전한다면 [마이그레이션](05-migration.md)을,
라이브러리 소스 수정과 기여를 위한 설정은 [개발과 릴리스](09-development-release.md)를 참고하세요.

### Python 3.6

Python 3.6과 호환되는 의존성 wheel을 설치할 수 있도록 pip 버전을 맞추세요.

```sh
python -m pip install --upgrade "pip>=21.3,<22"
python -m pip install mathml2docx
```

pip가 현재 Python에 맞는 의존성 버전을 선택합니다. 선택 기능인 LaTeX에는
Python 3.6.2 이상이 필요합니다.

## HTML·수식 변환

```python
from mathml2docx import convert

html = '''<h1>수식 예제</h1>
<p>다음은 분수입니다.</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>'''
convert(html, 'example.docx')
```

`convert()`는 python-docx의 Document를 반환합니다. 출력 경로를 생략하면 저장하지
않습니다. XSL 파일이나 Microsoft Office 설치는 필요하지 않습니다.

기존 HTML 파일을 변환하려면 `input.html` 파일을 준비한 뒤 실행하세요.

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_html_file('input.html', 'output.docx')
```

`latex` 선택 의존성을 설치한 뒤에는 다음과 같이 변환합니다.

```python
from mathml2docx import MathmlToDocx

MathmlToDocx().parse_latex(r'\frac{1}{2}').save('latex.docx')
```

## 기존 문서에 추가

```python
from docx import Document
from mathml2docx import MathmlToDocx

document = Document()
document.add_paragraph('기존 내용')
MathmlToDocx().add_html_to_document('<p>추가할 내용</p>', document)
document.save('combined.docx')
```

표 셀에는 `add_html_to_cell(html, cell)`을 사용합니다.
0.x에서 업그레이드한다면 [마이그레이션 안내](05-migration.md)를 먼저 읽으세요.
