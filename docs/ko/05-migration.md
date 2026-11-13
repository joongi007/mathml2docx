# 0.x에서 1.x로 옮기기

1.0.0은 XSL 파일 없이 MathML을 Word 수식(OMML)으로 변환합니다.

PyPI 배포 패키지를 업그레이드하세요.

```sh
python -m pip install --upgrade "mathml2docx[latex,markdown]"
```

앱에서 사용하는 선택 기능만 설치하면 됩니다. HTML·MathML에는 `mathml2docx`만 필요합니다.

```python
from mathml2docx import convert, MathmlToDocx, TableStyle, ParagraphStyle

convert('<h1>보고서</h1><p>내용</p>', 'report.docx',
        table_style=TableStyle.GRID, paragraph_style=ParagraphStyle.NORMAL)

parser = MathmlToDocx()
parser.parse_mathml('<math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>').save('fraction.docx')
# python -m pip install "mathml2docx[latex]"
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
- Office XSL은 제거했습니다. 과거 릴리스와 Git 기록에는 남아 있으므로 이전이
  과거 배포본의 라이선스 상태까지 해결하지는 않습니다.
- 미지원 MathML은 `UnsupportedMathMLError`로 알려 줍니다. 전체 MathML 규격이나
  모든 LaTeX 패키지를 지원한다고 보장하지 않습니다.

## 지원하는 수식

기본 토큰(`mi`, `mn`, `mo`, `mtext`, `ms`), 그룹, 분수, 위·아래 첨자, 제곱근과 n제곱근,
울타리, 위·아래 한계, 악센트, 직사각 행렬, phantom을 지원합니다. `semantics`는 첫
표현식을 변환하고 주석은 제외합니다. 일부 `menclose` 표기와 `mmultiscripts`의 앞뒤 첨자 한 쌍을 지원합니다.
Content MathML은 전처리 또는 대체 처리가 필요합니다. 글꼴·간격·악센트 등 MathML 표현 속성 전체를 재현하지는 않습니다.
LaTeX는 `latex2mathml`이 생성한 MathML에 이 지원 범위가 적용됩니다.
독립 정답 비교에서 구형 latex2mathml 2.16의 문자·악센트·명령 손실이 확인되어
선택 LaTeX 기능은 Python 3.6.2 이상과 latex2mathml 3.64 이상으로 제한합니다.
Python 3.6.0·3.6.1에서도 HTML·MathML 변환은 유지되며, LaTeX를 요청하면 요구 버전을 알려 줍니다.
HTML 안의 `$...$`는 자동으로 LaTeX로 해석하지 않습니다.

추가 검증에서 `mathvariant`, `ms`의 따옴표, 선 없는 이항계수와 bevelled 분수,
명시적인 괄호, 위·아래 선과 악센트, 극한 함수의 인자 묶음을 보완했습니다.
`mpadded`의 치수, 강제 수식 줄바꿈, 임의의 음수 간격과 사용자 지정 분수선 두께는
명시적인 오류를 냅니다. 일부 행렬 정렬·CSS·연산자 속성은 적용하지 않습니다.
`mspace`의 지원 간격은 Unicode 공백 근사입니다.
[수식 코퍼스·독립 스키마·렌더링 검증](11-validation.md)에서 확인한 범위와 남은 한계를 볼 수 있습니다.

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
document = Document()
document.add_paragraph('{{content}}')
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

## 수식 배치와 대체 처리

`display`를 생략한 MathML은 표준에 맞춰 인라인으로 배치합니다. 이전의 블록 배치를
유지하려면 `MathmlToDocx(default_math_display='block')`을 사용하세요. 명시적인
`display="block"`과 지원하는 CSS display 값도 적용합니다. 미지원 수식은 기본적으로
예외를 발생시키며 `unsupported_math='text'`, `mathml_fallback`, `mathml_preprocessor`로
명시적인 대체 처리를 선택할 수 있습니다. [수식 처리](03-mathematics.md)를 참고하세요.

## 수식 정확성과 입력 복구

`math`·`mstyle`의 속성 기본값을 일관되게 적용합니다. compact 스타일의 movable limits는
분수·첨자 내부를 포함해 옆 첨자로 배치하므로 이전의 위아래 배치에 의존하던 입력은
모양이 달라질 수 있습니다. 의도에 맞는 `display="block"` 또는 `displaystyle`를 지정하세요.

복합 악센트·병합/비정형 수식 표·RTL 배치를 기본 변환으로 보존할 수 없으면 명시적인
대체 처리를 사용합니다. `mo`의 강제 줄바꿈도 `mspace`와 같은 정책을 따릅니다.
미지원 형제가 먼저 나오더라도 잘못된 인자 수는 대체 전에 검출합니다.

LaTeX 백엔드 등이 이미 출력한 Unicode 수학 알파벳에도 대응하는 OMML 서체를 지정합니다.
Word가 해당 문자를 일반 문자로 풀어 저장할 때 이중 획·굵은 글꼴 등이 사라지지 않도록 합니다.

토큰 공백과 문자열 이스케이프는 MathML 규칙을 따르며, XML 인코딩 선언이 이미 디코딩한
Unicode를 바꾸지 않습니다. 수식 CSS와 XML 경계를 따르는 템플릿 치환으로 수식·서식·주변
내용을 함께 보존합니다.

### 1.0.1 보정

Unicode 수학 알파벳은 명시적·상속 `mathvariant`가 있어도 원래 서체를 유지하며,
스타일을 지정한 문자열도 텍스트 간격을 보존합니다. 해석되지 않은 LaTeX 명령 토큰은
식별자로 저장하지 않고 `UnsupportedMathMLError`로 알립니다. 사용자 정의 매크로는
변환 전에 펼치세요. 이 백엔드 검증은 MathML 대체 처리보다 먼저 실행하며,
명시적인 `\text{...}` 내용은 문자열로 유지합니다.
