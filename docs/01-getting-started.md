# 시작하기

## 설치

이 문서는 저장소의 1.0.0 코드 기준입니다. 아직 PyPI에 새 버전을 게시하지 않았으므로
현재 코드를 사용하려면 저장소에서 설치하세요.

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .
# LaTeX도 사용하려면:
python -m pip install '.[latex]'
```

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

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_html_file('input.html', 'output.docx')
parser.parse_latex(r'\frac{1}{2}').save('latex.docx')
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
