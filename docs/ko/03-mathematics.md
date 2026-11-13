# 수식 배치와 입력 처리

구조가 있는 수식에는 MathML을 사용하고, LaTeX 입력에는 `latex` 선택 의존성을 설치하세요.
지원하는 수식은 편집 가능한 Word 수식이 됩니다. 미지원 시각 표기는 원문을 표시하거나
프로그램이 제공하는 콜백으로 렌더링할 수 있습니다.

HTML·MathML에는 `python -m pip install mathml2docx`를 사용하세요. LaTeX도 사용하려면
`python -m pip install "mathml2docx[latex]"`로 설치합니다(Python 3.6.2 이상).

## 인라인 수식과 표시 수식

[MathML 표준](https://www.w3.org/TR/MathML3/chapter2.html#interf.toplevel)에 따라
`<math>`의 기본값은 `inline`입니다. 앞뒤 문장과 문장부호를 같은 문단에 유지합니다.

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx()
parser.convert('''<p>값 <math><mi>x</mi></math>의 단위는 미터입니다.</p>
<math display="block"><mfrac><mn>1</mn><mn>2</mn></mfrac></math>''', 'layout.docx')
```

인라인 수식에서 `movablelimits`를 사용하는 `munder`·`mover`·`munderover` 연산자는 compact 스타일의 옆 첨자로 배치합니다. display 스타일에서는 위아래 한계 위치를 유지합니다. 분수·첨자·표 셀은 각각의 수식 스타일을 설정하며 `displaystyle`로 재정의할 수 있습니다.

표시 수식은 별도 문단과 OMML의 `oMathPara` 요소를 사용합니다.
`display`를 생략하면 block이 되던 입력의 배치를 유지하려면
`MathmlToDocx(default_math_display='block')`을 사용하세요.

배치는 지원하는 CSS `display` → MathML의 `display` 속성 → `default_math_display`
순서로 결정합니다. CSS 값은 `inline`, `block`, `inline math`, `block math`,
`inline-block`을 인식하며 `inline-block`은 인라인으로 배치합니다.
`styles=False`이면 CSS를 적용하지 않습니다. `displaystyle`은 수식 내부 스타일에 관한
속성이므로 문단 배치를 정하는 `display` 대신 사용하지 마세요.
`mathml_to_omml()`은 수식 요소만 반환하며 문서 배치는 호출자가 정합니다.

## 기본 변환이 지원하는 표기

| MathML | 지원 범위 |
| --- | --- |
| 토큰·행·분수·근호·일반 첨자 | 기본 OMML 수식 |
| 악센트·위아래 선·극한·직사각 행렬 | 문서화된 범위의 OMML 수식. 복합·숨김 악센트와 행렬 셀 병합은 명시적인 대체 처리 필요 |
| `mmultiscripts` | 뒤 첨자 한 쌍·앞 첨자 한 쌍, 없는 첨자는 `none` |
| `menclose` | `box`, `top`, `bottom`, `left`, `right`, `actuarial`, `radical`, 가로·세로·대각 취소선 |
| `menclose`의 원·둥근 상자·나눗셈·화살표 테두리 | 명시적인 대체 처리 필요 |
| 여러 열의 앞뒤 첨자·Content MathML·화학 구조도 | 대체 처리 또는 입력 전처리 필요 |

화학식의 원소 기호에는 `mathvariant="normal"`로 정체를 지정하고, 원자 수는 아래 첨자,
전하는 위 첨자로 표현하세요. `mmultiscripts`로 원자 번호·질량수를 원소 앞에 놓을 수 있습니다.
반응 화살표와 주석에는 `mo`·`mover`·`munder`를 사용할 수 있습니다.
[화학식 예제](examples/28_chemistry_enclosures.md)를 참고하세요.
이 기능은 표기 변환이며 화학식 파서나 LaTeX `mhchem` 구현은 아닙니다.

## LibreOffice 대상 문서

Writer에서 열 문서에는 `MathmlToDocx(math_target='libreoffice')`를 사용하세요.
정체 식별자에 명시적인 글꼴 속성을 추가하고, 표시 손실이 확인된 OMML 표기는 같은
대체 처리 정책으로 넘깁니다. Writer 24.2는 phantom 공간·기울어진 분수·문자열 따옴표를
다르게 표시하고, 근호 외 테두리를 생략하거나 비어 있는 앞 첨자를 자리표시자로 표시할 수
있으므로 이 경우에는 대체 처리가 필요합니다.

```python
parser = MathmlToDocx(math_target='libreoffice', unsupported_math='text')
```

테두리를 이미지로 유지하려면 원문 표시 대신 `mathml_fallback`을 제공하세요.
기본값 `math_target='word'`는 편집 가능한 Word 테두리를 유지합니다.
대상 프로그램은 명시적으로 선택합니다. 변환기는 나중에 DOCX를 열 프로그램을 감지할 수
없습니다. 이 옵션은 알려진 호환성 차이의 처리 정책이며 Writer 버전 전체의 배치 동등성을
보증하지 않습니다. `parse_latex()`에도 같은 대상·대체 설정을 적용합니다.
저수준 함수에는 `target='libreoffice'`를 지정할 수 있으며 이미지 렌더러가 필요한 경우
계속 예외를 발생시킵니다.

## 미지원 입력을 원문으로 남기기

```python
from mathml2docx import MathmlToDocx

parser = MathmlToDocx(unsupported_math='text')
parser.parse_mathml('<math><menclose notation="circle"><mi>x</mi></menclose></math>').save('source.docx')
```

문서에 `[Unconverted MathML]`과 전체 XML을 표시합니다. 원문 표현이므로 렌더링한 수식과
같지는 않습니다. 수식을 조용히 삭제하지 않으며, 대체 시 `MathMLFallbackWarning`을 남깁니다.
기본값인 `unsupported_math='error'`는 엄격한 변환을 유지합니다.

## 외부 렌더러 연결하기

콜백은 정규화된 MathML 원문과 `UnsupportedMathMLError`를 받습니다.
문자열을 반환하면 그대로 표시하고, PNG·JPEG 이미지 바이트나 `BytesIO`를 반환하면
문서에 이미지를 내장합니다. 이미지는 사용 가능한 페이지 너비 안으로 제한합니다.
대체 텍스트는 `alttext`를 사용하며, 없으면 MathML 원문을 사용합니다.
이미지는 편집 가능한 수식이 아닙니다.

```python
from mathml2docx import MathmlToDocx

def fallback(source, error):
    # 신뢰할 수 있는 MathML 렌더러를 연결하세요. 이 예제는 원문을 보존합니다.
    return 'Unsupported equation: ' + source

parser = MathmlToDocx(mathml_fallback=fallback)
parser.parse_mathml('<math><unknown/></math>').save('recovered.docx')
```

콜백은 `unsupported_math`보다 우선합니다. 미지원 MathML 변환에만 호출하며,
잘못된 XML·잘못된 인자 수·콜백 자체의 오류는 그대로 전달합니다.
빈 결과나 잘못된 타입을 반환하면 오류가 됩니다. 외부 렌더링 서비스에는 자동으로 접속하지 않습니다.
[이미지 대체 전체 예제](examples/29_math_fallbacks.md)를 참고하세요.

## 변환 전 입력 정규화

`mathml_preprocessor(source)`는 HTML·독립 MathML의 각 수식마다 한 번 호출됩니다.
완전한 MathML 문자열을 반환하세요. 입력과 반환값 모두 DTD·엔티티 확장·네트워크 접근 없이 검사합니다.

```python
from lxml import etree
from mathml2docx import MathmlToDocx

def normalize(source):
    root = etree.fromstring(source.encode('utf-8'))
    if root.get('data-display') == 'separate':
        root.set('display', 'block')
    return etree.tostring(root, encoding='unicode')

parser = MathmlToDocx(mathml_preprocessor=normalize)
parser.convert('<math data-display="separate"><mi>x</mi></math>', 'normalized.docx')
```

정규화할 때는 수식의 의미를 보존하세요. 알 수 없는 태그를 제거하면 표기가 사라질 수 있습니다.
화면 표현을 유지해야 한다면 이미지 렌더러를 연결하세요.

## 속성 기본값·토큰·구조 검사

`math`·`mstyle`의 지원하는 표시 속성 기본값은 하위 요소에 적용하고, 해당 요소의 직접
지정을 우선합니다. 분수선 생략(`linethickness="0"`), 괄호·구분자, 문자열 따옴표,
악센트와 movable limits 등이 포함됩니다. 중첩 스타일은 그 컨테이너 안에만 적용합니다.

토큰 공백은 MathML의 XML 공백 규칙을 따릅니다. `mtext`를 포함해 코드의 들여쓰기는
정규화하고, NBSP·narrow NBSP는 보존합니다. `ms` 안의 따옴표는 눈에 보이도록 이스케이프합니다.
Unicode 문자열 입력은 이미 디코딩된 문자를 기준으로 처리하므로, XML 선언의 과거 인코딩
이름 때문에 문자를 다시 인코딩하거나 깨뜨리지 않습니다.

미지원 입력을 대체하기 전에 표시 트리 전체의 알려진 인자 수를 검사합니다. annotation의
내용은 불투명한 메타데이터로 다룹니다. 잘못된 구조는 형제 순서와 관계없이 `ValueError`가
되고, 기본 변환으로 표현할 수 없는 유효한 구조는 `UnsupportedMathMLError`로 대체 처리할 수
있습니다. 병합·비정형 MathML 표, `mo`·`mspace` 강제 줄바꿈, RTL 배치, 복합·숨김 악센트도
배치를 버리는 대신 이 정책을 사용합니다.

## 서식·링크·템플릿

지원하는 MathML CSS 색상·크기·글꼴은 HTML에서 상속하며 수식의 글자와 복합 기호에 적용합니다.
하위 요소의 스타일을 우선하고, Word의 수학 글꼴 변형과 CSS 글꼴은 구분해 유지합니다.
Unicode 수학 알파벳은 토큰과 `mtext`·`ms` 문자열에서 원래 서체를 보존하며
일반 텍스트·공백·수학 문자를 섞을 수 있습니다.
상대 크기, MathML의 `mathsize`·`mathcolor`, `currentColor`, RGBA도 지원 범위에서 계산합니다.
`styles=False`이면 CSS 변환을 적용하지 않습니다.

수식 ID는 내부 링크를 위한 Word 북마크가 됩니다. 표시 수식을 포함한 링크는 여러 문단에
걸쳐 범위를 유지합니다. 링크가 있는 표시 수식도 Word 재저장 후 편집 가능한 구조,
혼합 수학 서체와 표시 배치를 보존합니다. 표 셀의 표시 수식도 문단 경계를 유지합니다. 마커를 치환할 때 주변
수식을 보존하며, 북마크는 수식만 있는 경우도 선택한 XML 범위를 교체합니다.
[수식·템플릿 전체 예제](examples/30_mathml_fidelity.md)를 참고하세요.

HTML 입력에는 접두사가 없는 `math`와 표시 태그를 사용합니다. 접두사가 있는 XML은
`parse_mathml()`로 전달하세요. HTML 경로에 넣으면 일반 텍스트로 평탄화하는 대신 입력
형식 오류를 발생시킵니다.
