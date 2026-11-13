# 시작하기

## 설치

배포 패키지는 Python 3.6 이상을 지원합니다. 프로젝트의 Python 환경에
PyPI 패키지를 설치하세요.

```sh
python -m pip install mathml2docx
```

HTML·MathML 변환은 기본 패키지로 사용할 수 있습니다. LaTeX·Markdown 입력에는
선택 의존성을 설치하세요.

```sh
python -m pip install "mathml2docx[latex]"
python -m pip install "mathml2docx[markdown]"
# 두 기능을 함께 설치:
python -m pip install "mathml2docx[latex,markdown]"
```

LaTeX 변환에는 Python 3.6.2 이상이 필요합니다. 설치된 버전은 다음 명령으로 확인합니다.

```sh
python -c "import mathml2docx; print(mathml2docx.__version__)"
```

uv를 사용하는 프로젝트에서는 `uv add mathml2docx`로 배포 패키지를 추가할 수 있습니다.
두 선택 기능을 함께 추가하려면 `uv add "mathml2docx[latex,markdown]"`을 사용하세요.
패키지 사용에는 Git이나 저장소 복제가 필요하지 않습니다. 소스 수정과 기여를 위한 설정은
[개발과 릴리스](09-development-release.md)에서 다룹니다.

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
기존 사용자라면 [1.0.0 마이그레이션](05-migration.md)을 먼저 읽으세요.
