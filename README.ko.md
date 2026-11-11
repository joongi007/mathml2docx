# mathml2docx

[English](https://github.com/joongi007/mathml2docx/blob/master/README.md) · [한국어](https://github.com/joongi007/mathml2docx/blob/master/README.ko.md)

Python으로 HTML과 MathML을 Word 문서로 변환합니다. 수식은 Word에서 편집할 수 있어
보고서·학습지·문서 템플릿에 활용할 수 있습니다. 문서를 생성하는 컴퓨터에 Microsoft
Office가 설치되어 있을 필요는 없습니다.

**Python 3.6 이상** · LaTeX·Markdown 선택 지원 · MIT 라이선스

## 설치

아래 예제는 **이 저장소의 1.0 코드**를 기준으로 합니다. 그대로 실행하려면 저장소를
설치하세요. 기존 PyPI 배포 버전은 API가 다릅니다.

```sh
git clone https://github.com/joongi007/mathml2docx.git
cd mathml2docx
python -m pip install .
```

LaTeX와 Markdown도 사용하려면 선택 의존성을 설치합니다.

```sh
python -m pip install '.[latex,markdown]'
```

LaTeX 기능에는 Python **3.6.2 이상**이 필요합니다. 라이브러리 사용에 uv는 필요하지 않습니다.

## 첫 문서 만들기

```python
from mathml2docx import convert

html = '''
<h1>학습 노트</h1>
<p>아래 분수는 Word에서도 편집할 수 있습니다.</p>
<math xmlns="http://www.w3.org/1998/Math/MathML">
  <mfrac><mn>1</mn><mn>2</mn></mfrac>
</math>
'''

convert(html, 'lesson.docx')
```

실행 후 `lesson.docx`를 열어보세요. Python에서 더 수정하려면 출력 경로를 생략한
`document = convert(html)`로 문서를 받은 뒤, 준비됐을 때
`document.save('lesson.docx')`로 저장하세요.

## 어떤 내용을 변환할 수 있나요?

- **HTML:** 제목·문단·링크·글자 서식·목록
- **표:** 셀 병합·중첩 표·Word 표 스타일
- **이미지:** data URL·명시한 로컬 파일·사용자 정의 로더
- **스타일:** 지원하는 CSS 선택자·글꼴·색상·정렬·페이지 나누기
- **수식:** 지원하는 MathML 분수·근호·첨자·한계식·악센트·행렬
- **기존 문서:** 문서나 셀에 내용 추가, 마커·북마크의 내용 교체

HTML·CSS·MathML의 일부 기능을 지원하며, 브라우저 화면 전체를 재현하지는 않습니다.
미지원 MathML 요소는 `UnsupportedMathMLError`로 알립니다.
자세한 범위는 [지원 기능과 마이그레이션](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/05-migration.md),
[검증 결과와 알려진 한계](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/11-validation.md)를 참고하세요.
Word에서 직접 확인해야 하는 항목도 검증 문서에 기록했습니다.

## 다른 사용 방법

| 하고 싶은 작업 | 예제 |
| --- | --- |
| HTML 파일 변환·다국어 처리 | [파일과 인코딩](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/02_files_unicode.md) |
| 기존 문서나 표 셀에 HTML 추가 | [기존 문서](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/03_existing_document.md) |
| Word 스타일 적용·HTML 클래스 매핑 | [Word 스타일](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/06_word_styles.md) |
| 템플릿의 내용 교체 | [마커](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/15_markers.md) · [북마크](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/16_bookmarks.md) |
| 수식·표·이미지를 함께 사용 | [복잡한 수식](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/23_complex_equations.md) · [혼합 보고서](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/24_dense_report.md) |

## LaTeX와 Markdown

위의 선택 의존성을 설치한 뒤 실행하세요.

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.parse_latex(r'\frac{1}{2} + x_1^2').save('equation.docx')
parser.parse_markdown('# 노트\n\n**굵게**와 ~~삭제한~~ 내용.').save('notes.docx')
```

LaTeX는 입력 형식으로 직접 지정합니다. HTML 안의 `$...$`를 자동으로 수식 변환하지는 않습니다.

## 명령줄 사용

```sh
mathml2docx input.html output.docx
mathml2docx equation.tex equation.docx --format latex
mathml2docx notes.md notes.docx --format markdown
```

기존 출력 파일을 교체하려면 `--force`를 사용하세요. URL 이미지와 외부 스타일시트는
자동으로 내려받지 않습니다. Python에서 명시적인 로더를 제공할 수 있습니다.

## 사용법 문서

- [시작하기](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/01-getting-started.md) · [API 참고](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/02-api.md) · [작업별 사용법](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/08-recipes.md)
- [실행 예제 24개](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/examples/00-index.md): 전체 코드와 로컬 DOCX 생성 명령
- 웹 문서: [English](https://joongi007.github.io/mathml2docx/) · [한국어](https://joongi007.github.io/mathml2docx/ko/). Pages 활성화와 배포 성공 후 공개되며, 배포된 문서에서 예제 파일도 내려받을 수 있습니다.

## 개발 참여

변경 작업은 `develop`에서 시작합니다. uv 개발 환경·테스트·브랜치·배포 방법은
[개발·릴리스 안내](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/09-development-release.md)에,
1.0 변경 사항은 [변경 기록](https://github.com/joongi007/mathml2docx/blob/master/CHANGELOG.md)에 정리했습니다.

## 라이선스

[MIT](https://github.com/joongi007/mathml2docx/blob/master/LICENSE) 라이선스이며, 원본
[html2docx](https://github.com/pqzx/html2docx)의 저작권 고지를 유지합니다.
의존성에는 각자의 라이선스가 적용됩니다. [제삼자 고지](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md)를 참고하세요.
1.0 변환기는 기존 Office XSL 없이 Word 수식을 직접 생성합니다. 과거 XSL 사본의 권한은
별도 미해결 사항으로 [라이선스 범위](https://github.com/joongi007/mathml2docx/blob/master/docs/ko/10-licensing.md)에 설명했습니다.
