# mathml2docx

[English](https://github.com/joongi007/mathml2docx/blob/master/README.md) · [한국어](https://github.com/joongi007/mathml2docx/blob/master/README.ko.md) · [사용 문서](https://joongi007.github.io/mathml2docx/ko/)

Python에서 HTML과 MathML을 Word 문서로 변환합니다. **편집 가능한 수식**, 서식 있는
본문, 표와 이미지를 보고서·학습지·문서 템플릿에 넣을 수 있습니다.
문서를 생성할 때 Microsoft Office는 필요하지 않습니다.

Python 3.6 이상 · 선택 기능으로 LaTeX·Markdown 지원 · MIT 라이선스

## 설치

[PyPI](https://pypi.org/project/mathml2docx/)에 배포된 패키지를 설치하세요.

```sh
python -m pip install mathml2docx
# LaTeX·Markdown 기능도 설치:
python -m pip install "mathml2docx[latex,markdown]"
```

선택 기능인 LaTeX 변환은 Python 3.6.2 이상이 필요합니다. 라이브러리 사용에는 uv가
필요하지 않습니다. 재현 가능한 설치를 원하면 프로젝트의 requirements나 lockfile에
패키지 버전을 고정하세요. 라이브러리 소스를 수정하려면
[개발 환경 설정](https://joongi007.github.io/mathml2docx/ko/09-development-release/)을 참고하세요.

## 첫 Word 문서 만들기

```python
from mathml2docx import convert

convert('''
<h1>학습 노트</h1>
<p>값 <math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>은 이분의 일입니다.</p>
<math display="block"><msup><mi>x</mi><mn>2</mn></msup></math>
''', 'lesson.docx')
```

`lesson.docx`를 Word에서 열면 본문과 수식을 편집할 수 있습니다. `convert()`는
python-docx의 `Document`도 반환합니다. 출력 경로를 생략하면 Python에서 계속 수정할 수 있습니다.

## 지원 기능

| 입력·작업 | 기능 |
| --- | --- |
| HTML | 제목, 문단, 링크, 중첩 목록, 글자 서식 |
| 표 | 셀 병합, 중첩 표, Word 표 스타일 |
| 이미지 | 데이터 URL, 허용한 로컬 파일, 직접 제공하는 로더 |
| CSS | 지원하는 선택자, 글꼴, 색상, 정렬, 페이지 나누기 |
| MathML | 분수, 근호, 첨자, 극한, 악센트, 행렬, 일부 테두리 표기와 동위원소 첨자 |
| LaTeX·Markdown | latex2mathml과 Python-Markdown을 사용하는 선택 기능 |
| 템플릿 | 기존 문서·셀에 추가하고 마커·북마크 내용 교체 |

HTML·CSS·Presentation MathML의 문서화된 일부 기능을 지원합니다.
브라우저의 전체 화면 배치를 그대로 재현하는 도구는 아닙니다.

## 수식 배치와 미지원 입력

MathML 표준에 따라 `<math>`의 **기본 배치는 inline**입니다. 별도 표시 수식에는
`display="block"`을 지정하세요. `display`가 없는 입력을 기존처럼 block으로 처리하려면:

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(default_math_display='block')
```

지원하지 않는 수식 구조는 기본적으로 `UnsupportedMathMLError`를 발생시킵니다.
다양한 입력을 받는 프로그램에서는 `unsupported_math='text'`로 XML 원문을 문서에 표시하거나,
`mathml_fallback(source, error)`로 텍스트·이미지를 제공하거나,
`mathml_preprocessor(source)`로 입력을 정규화할 수 있습니다.
대체 시에는 `MathMLFallbackWarning`을 남기며, 잘못된 XML은 계속 오류로 처리합니다.
지원 표기와 전체 예제는 [수식 처리 안내](https://joongi007.github.io/mathml2docx/ko/03-mathematics/)를 참고하세요.

## LaTeX·Markdown·명령줄

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_latex(r'\frac{1}{2} + x_1^2').save('equation.docx')
parser.parse_markdown('# 노트\n\n**강조**와 ~~삭제~~ 표시.').save('notes.docx')
```

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx input.html output.docx --default-math-display block --unsupported-math text
```

기존 출력 파일을 교체하려면 `--force`를 사용하세요. HTML의 달러 기호는 LaTeX 구분자로
해석하지 않습니다. 네트워크 이미지와 외부 스타일시트는 명시적인 로더가 필요합니다.

## 사용 문서와 예제

- [시작하기](https://joongi007.github.io/mathml2docx/ko/01-getting-started/) · [API와 옵션](https://joongi007.github.io/mathml2docx/ko/02-api/) · [활용법](https://joongi007.github.io/mathml2docx/ko/08-recipes/)
- [실행 예제와 DOCX 다운로드](https://joongi007.github.io/mathml2docx/ko/examples/00-index/): 서식, 템플릿, 과학 보고서, 화학식과 대체 렌더링.
- [MathML 보존 예제](https://joongi007.github.io/mathml2docx/ko/examples/30_mathml_fidelity/): 상속 기본값, 악센트, 수식 서식, 링크와 템플릿 치환.
- [0.x에서 이전하기](https://joongi007.github.io/mathml2docx/ko/05-migration/) · [호환성과 검증](https://joongi007.github.io/mathml2docx/ko/11-validation/)
- [English documentation](https://joongi007.github.io/mathml2docx/)

LibreOffice로 PDF를 생성하려면 **Writer와 Math**, 사용할 글꼴을 설치하세요.
Writer만 설치하면 수식이 빈칸으로 나올 수 있습니다.
[렌더링 안내](https://joongi007.github.io/mathml2docx/ko/11-validation/#libreoffice)에 설치·검사 명령이 있습니다. 테두리 등 알려진 차이에는
`math_target='libreoffice'`와 명시적인 대체 처리를 사용하세요.

## 기여와 라이선스

개발은 `develop`에서 시작합니다. 환경 구성·테스트·배포는
[개발과 릴리스](https://joongi007.github.io/mathml2docx/ko/09-development-release/)를,
변경 사항은 [CHANGELOG.md](https://github.com/joongi007/mathml2docx/blob/master/CHANGELOG.md)를 참고하세요.

[MIT](https://github.com/joongi007/mathml2docx/blob/master/LICENSE) 라이선스이며 [html2docx](https://github.com/pqzx/html2docx)에서 파생됐습니다.
의존성의 라이선스는 [THIRD_PARTY_NOTICES.md](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md)에 정리돼 있습니다.
1.0 변환기는 OMML을 직접 생성하며 Office XSL을 포함하지 않습니다.
과거 0.x 배포물은 별도의 [출처 기록](https://joongi007.github.io/mathml2docx/ko/06-xsl-provenance/)을 참고하세요.
