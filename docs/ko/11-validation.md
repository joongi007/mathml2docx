# 수식 검증과 남은 한계

2026-11-10에 검사하고 2026-11-11과 2026-11-12에 보강했습니다. 이 문서는 지원 범위 안에서 확인한 증거를 기록합니다.
모든 MathML·LaTeX·HTML 조합이나 모든 Word 버전의 결과를 보증하지 않습니다.

## 서로 다른 검증 기준

| 검사 | 확인하는 것 | 확인하지 못하는 것 |
| --- | --- | --- |
| 수학적 역할 비교 | 분자·분모, 밑·첨자, 피제곱수·차수, 행렬 셀의 내용과 위치 | 글꼴·줄바꿈·실제 수식 편집 UX |
| ECMA-376 XSD | OMML 구조, 필수 속성, Word 본문의 요소 순서 | 원래 수식과의 의미 일치·화면 배치 |
| DOCX 저장·재오픈 | 수식·표·서식·이미지·링크가 파일에 보존되는지 | Microsoft Word 자체의 표시 |
| LibreOffice PDF | 독립적인 문서 프로그램에서 실제로 표시되는지 | Word와 픽셀 단위 일치 |
| 고의 오류 주입 | 테스트가 대표적인 수식 손상을 잡는지 | 가능한 모든 결함의 검출 |

수학적 역할·내용 비교의 정답은 변환기 출력에서 생성하지 않습니다.
직접 작성한 수학적 역할 모델을 MathML로 인코딩한 뒤, 별도 OMML 해석기가 읽은 역할과
비교합니다. 구조 검증에는 변환기와 독립적인 공식 스키마를 사용합니다.

## DOCX를 저장한 뒤 정답과 비교하기

생성된 DOCX나 정답 DOCX 바이너리를 저장소에 추가하지 않습니다.
수동 수식 44개는 `examples/assets/math-corpus/`의 HTML·LaTeX 입력 파일과
`catalog.json`으로 관리합니다. 기존 Python 예제도 이 입력 파일을 읽습니다.
독립적으로 작성한 정답은 `tests/fixtures/math_expectations.json`에 있습니다.

`tests/test_docx_oracles.py`는 MathML·HTML·LaTeX로 임시 DOCX를 만들고,
`tests/docx_oracle.py`가 ZIP 안의 실제 XML을 읽은 결과와 정답을 비교합니다.
갤러리 44개와 보고서 120개 수식의 파일도 같은 정답으로 검사합니다.
기존 저장 전후 XML 비교는 보존 여부 검사이고, 정답 비교는 원래 의도한 결과인지
확인하는 별도의 검사입니다.

`examples/assets/mixed_math.html`과 `tests/fixtures/mixed_math_expectation.json`은
내용 순서·굵기·기울임·밑줄·색상·정렬·표 병합·중첩 표·번호 시작값·링크 대상·
이미지 바이트 해시와 크기·줄바꿈을 함께 검사합니다.
분자·서식·관계·번호·병합을 일부러 바꾼 파일과 행·열이 달라진 행렬도 검출합니다.

```sh
uv run --no-sync python -m unittest tests.test_docx_oracles -v
```

세부 표현과 비교에서 제외하는 항목은 저장소의 `tests/fixtures/README.md`에 설명했습니다.
이 검사는 저장된 내용과 선택한 구조·속성의 검사이며, Word의 시각적 표시를 대신하지 않습니다.

2026-11-11 추가 검사에서 구형 latex2mathml 3.64의 `\nolimits` 오해석과
다른 연산자까지 영향을 주던 한계 위치 처리, 조각함수의 왼쪽 괄호 구조를 보완했습니다.
각 연산자의 `\limits`·`\nolimits`를 따로 처리하며 일반 텍스트 안의 명령은 유지합니다.
latex2mathml 2.16은 악센트·간격·일반 텍스트 등 여러 정답에 불일치하므로 지원 대상에서
제외했습니다. HTML·MathML은 Python 3.6.0 이상을 유지하고, 선택 LaTeX 기능만
Python 3.6.2 이상과 latex2mathml 3.64 이상을 요구합니다.

## 수식과 혼합 문서

[코퍼스 원본](https://github.com/joongi007/mathml2docx/blob/master/examples/math_corpus.py)은 저장소와 예제 ZIP에 포함됩니다.

- 직접 작성한 수식 20개: 근의 공식, 연분수, 이항계수, 중첩 근호, 텐서 첨자, 급수,
  이상적분, 편미분, 행렬, 조각함수, 악센트, 극한, 확률, 수학 글꼴, annotation·phantom 등.
- LaTeX 24개: 같은 계열에 큰 괄호, 일반 텍스트, 명시적 간격과 `\nolimits`를 추가했습니다.
- 시드 `376`의 조합 수식 240개를 네임스페이스 유무 두 경우로 검사합니다.
  분수·근호·첨자·행렬·울타리·한계식·phantom을 최대 네 단계로 조합합니다.
  서로 다른 입력 문자열은 210개이며 단독 토큰 사례 38개를 포함합니다.
  서로 다른 복잡한 문서 240개를 검사했다는 뜻은 아닙니다.
- 자동 혼합 문서: 수식 280개, 표 20개와 중첩 표 20개, 이미지·링크 각 20개,
  병합 셀, 번호 목록, 굵게·기울임을 저장 후 다시 열어 개수·순서·역할까지 검사합니다.
- 깊이 32의 근호와 1,025개 토큰의 긴 수식, 필수 인자 수, 잘못된 행렬,
  알 수 없는 요소·네임스페이스, DTD·외부 엔티티와 미지원 배치를 별도로 검사합니다.
- [복잡한 수식 갤러리](examples/23_complex_equations.md): MathML 20개와 LaTeX 24개의 DOCX·PDF.
- [수식이 많은 보고서](examples/24_dense_report.md): 수식 배치 120회에 표·목록·이미지·다국어·페이지 나누기를 함께 사용한 DOCX·PDF.
  직접 작성한 수식을 반복 배치하며 새로운 수학 사례 120개를 뜻하지 않습니다.

공식 스키마로 코퍼스 수식 302개(20 + 24 + 240 + 18), 실행 예제 27개 본문과 그 안의 수식 198개를
검사했습니다. 잘못된 분수 구조를 반드시 거절하는 음성 대조군도 확인합니다.
본문 검사에서는 사용되지 않는 `mc:Ignorable` 메타데이터만 제거합니다.
알 수 없는 확장 요소를 지워서 통과시키지 않으며, DOCX 패키지 전체의 인증을 뜻하지 않습니다.

대표적인 고의 오류 9종도 검출했습니다. 분자·분모, 근호의 차수·내용, 위아래 첨자 교환과
이항계수의 분수선 복원, mathvariant·괄호·악센트 손실, 연속 괄호를 하나로 묶는 오류와
LaTeX 괄호 전체의 지수를 닫는 괄호에만 붙이는 오류입니다.
저장 파일을 손상하는 검사로 이미지 바이트·링크·서식·목록·병합의 변경과, 평탄화한 셀 순서는
같지만 2×2 행렬이 1×4로 바뀌는 오류도 검출합니다.

## 이번 검사에서 고친 문제

- 이항계수의 불필요한 분수선, bevelled 분수 유형, 기본·상속 mathvariant와 문자열 따옴표.
- 자식 연산자의 악센트 지정, 위·아래 선, 명시적 울타리 연산자의 OMML delimiter 변환.
- LaTeX 극한 함수의 한계 위치와 다음 인자 묶음, 일반 텍스트와 지원 간격의 표시.
- 주석·처리 명령 파싱, 빈 행렬·잘못된 셀과 네임스페이스 검사, 직접 텍스트의 누락 방지.
- 인라인 수식 뒤 공백 보존, 배경색의 필수 `w:val`, 표 테두리 요소의 표준 순서.

## 재현

개발 환경은 [uv 안내](09-development-release.md)에 따라 준비합니다.

```sh
uv run --no-sync python -m pytest -q
uv run --no-sync python scripts/check_math_mutations.py
uv run --no-sync python -m examples.run_all

# 스키마는 임시 경로로만 받습니다. 다운로드 해시가 달라지면 중단합니다.
uv run --no-sync python scripts/prepare_ecma_schema.py /tmp/mathml2docx-ecma376
uv run --no-sync python scripts/validate_math_schema.py --schemas /tmp/mathml2docx-ecma376

# LibreOffice가 설치된 환경에서 실행
uv run --no-sync python scripts/render_examples.py
```

검증 스키마는 [ECMA-376 Part 4 공식 배포](https://ecma-international.org/publications-and-standards/standards/ecma-376/)의
`OfficeOpenXML-XMLSchema-Transitional.zip`과 [W3C xml.xsd](https://www.w3.org/2001/xml.xsd)입니다.
원본 바이트를 수정하거나 패키지에 포함하지 않습니다. 다운로드 URL·SHA-256은 준비 스크립트에,
검사한 개별 스키마의 SHA-256은 스키마 검사 결과에 출력합니다.
CI에서도 예제 생성 뒤 같은 스키마 검사를 수행합니다.

## 고급 입력과 실제 Word 검사 (2026-11-12)

[연구 보고서](examples/25_research_report.md), [템플릿 워크북](examples/26_template_workbook.md),
[고급 LaTeX 보고서](examples/27_advanced_latex.md)에 서로 다른 입력 18개를 추가했습니다.
MathML 10개와 LaTeX 8개이며, 3×3 헤시안·행렬 셀 안의 행렬·Schur 보완·6단 연분수·
조각함수·이중 합·정규화 편미분·괄호 전체의 지수를 포함합니다.
입력은 `examples/assets/advanced-math/`, 별도로 작성한 정답은
`tests/fixtures/advanced_math_expectations.json`에 있습니다.
워크북은 같은 MathML 10개를 다른 배치에서 검사하며 새로운 수식 10개로 세지 않습니다.

이 검사로 연속 행렬의 괄호를 식 전체에 씌우던 문제, 괄호 전체가 아닌 닫는 괄호에만
지수가 붙던 문제, latex2mathml 3.64가 만든 함수 이름 뒤의 조각함수에서 왼쪽 괄호를
별도 구조로 묶지 못하던 문제를 수정했습니다. 실제 Python 3.6에서도 확장 검사를 통과했습니다.

로컬 Windows의 Microsoft Word **16.0**으로 예제 **27개**를 읽기 전용으로 열고,
PDF로 출력한 뒤 별도 DOCX로 저장했습니다. 수식 **198개**의 수학적 역할은 유지됐습니다.
Word 저장 과정에서 Unicode 마이너스 U+2212가 ASCII 하이픈 마이너스로 바뀌므로,
Word 재저장 비교에서만 수식 텍스트의 이 표기 차이를 정규화합니다.
변환기와 독립 정답의 비교는 Unicode까지 엄격하게 유지합니다.
그 밖의 역할·행렬 크기·괄호·지수의 밑은 그대로 비교합니다.

24~27번은 재저장한 파일의 본문 순서·강조·색상·번호 시작·표 병합/중첩·이미지 해시와
크기·링크 대상도 비교했습니다. Word가 바꾸는 스타일 ID는 실제 스타일 이름으로 비교합니다.
표시 수식의 바깥 레이아웃 요소, 맞춤법 표시, Word가 계산한 `lastRenderedPageBreak`는
본문 내용으로 세지 않으며, 명시적인 줄바꿈·페이지 나누기는 유지해서 검사합니다.
이는 저장 구조의 검사이며 대화형 편집·화면 충실도 인증은 아닙니다.
일부 PDF 페이지를 직접 살폈고, 24~27번의 추출된 텍스트 상자는 페이지 범위를 벗어나지
않았습니다. 모든 글자와 페이지를 검토했다는 뜻은 아닙니다.

Word가 설치된 Windows·WSL에서 재현할 수 있습니다. 입력은 읽기 전용으로 열고,
기존 검토 파일은 덮어쓰지 않으므로 새 출력 폴더를 지정하세요.

```sh
python scripts/check_word.py --input examples/output --output examples/output/word-review
python scripts/check_word.py --input examples/output --output examples/output/word-mixed-review --examples 24_dense_report 25_research_report 26_template_workbook 27_advanced_latex --check-blocks
```

Word는 선택 검증 도구이며 라이브러리 실행이나 CI의 필수 조건이 아닙니다.
엄격한 `--check-blocks`는 다른 문서에서 의미가 같은 직렬화 차이도 알릴 수 있습니다.
예를 들어 Word가 명시적인 밑줄 `none`을 생략하는 차이는 별도로 검토해야 합니다.

## 한글과 동아시아 글꼴

예제 24~27번은 **Malgun Gothic(맑은 고딕)**을 명시합니다. CSS `font-family`를 지정하면
라틴 문자뿐 아니라 동아시아·복합 문자 글꼴 슬롯에도 적용합니다.
글꼴을 지정하지 않은 입력은 기존처럼 템플릿 기본값을 사용합니다.
글꼴 파일을 포함하거나 내장하지는 않습니다. 다른 시스템·뷰어에서는 해당 글자가 있는
글꼴을 설치하거나 예제에서 사용 가능한 CJK 글꼴을 선택해야 합니다.

보고된 한글 네모 현상은 원래 24번을 로컬 Word 16에서 열었을 때 재현되지 않았고,
DOCX에 저장된 한글도 정상이었습니다. 명시적인 글꼴 지정은 저장된 DOCX에서 검사하며,
수정본의 Word 출력에서 한글 표시를 확인했습니다. 네모가 계속되면 해당 프로그램의
글꼴 대체 동작을 추가 확인해야 합니다.

## 남은 범위

위 자동화는 Windows의 Word 16 한 설치 환경에서 열기·PDF 출력·재저장을 검사했습니다.
대화형 편집·접근성·Word 웹/macOS·다른 Word 버전은 아직 확인하지 않았습니다.
LibreOffice 검증으로 대체했다고 주장하지 않습니다.
글꼴과 문서 프로그램에 따라 행 높이·줄바꿈·페이지 수가 달라질 수 있습니다.
이번 LibreOffice 7.3 렌더링에서 `m:fPr/m:type="skw"`의 bevelled 분수는 일반
분수처럼 표시됐습니다. 출력 XML은 skewed 유형으로 스키마를 통과하지만 해당 화면의
동등성은 확인되지 않았으며, Word 직접 확인 항목으로 남깁니다.
같은 렌더러에서 phantom의 예약 폭과 `ms`의 ASCII 따옴표도 기대와 달랐습니다.
숨김·치수 속성과 따옴표 문자는 출력 XML에 보존되지만, 해당 기능의 화면 동등성은
검증 완료로 분류하지 않습니다. 갤러리 M17·M19·M20에서 의도한 수식과 직접 비교하세요.
해당 참조 PDF의 표시를 올바른 정답으로 취급하지 마세요.

`menclose`, `mmultiscripts`, Content MathML, 임의의 음수 간격·강제 수식 줄바꿈·
mpadded 치수는 지원하지 않습니다. 이들은 오류로 알립니다.
`mspace`는 지원하는 양수 간격을 Unicode 공백으로 근사하므로 정밀한 조판 치수를 보증하지 않습니다.
행렬 정렬·연산자 사전·수식 CSS·모든 MathML 표현 속성을 완전하게 재현하지는 않습니다.
일부 표현 속성은 근사하거나 적용하지 않으므로 [수식 지원 범위](05-migration.md)를 확인하세요.
매우 넓은 수식은 응용 프로그램에서 줄바꿈·페이지 폭을 조정해야 합니다.

LaTeX 처리 범위는 설치된 latex2mathml 버전에도 영향을 받습니다. Python 3.6의 구버전
백엔드까지 검사하지만 모든 LaTeX 환경·패키지·매크로의 동등성을 보증하지는 않습니다.
실제 업무 문서를 추가할 때에는 기대하는 수학적 역할과 Word 화면을 함께 확인하고,
발견한 사례를 이 코퍼스에 회귀 테스트로 추가하는 것이 다음 검증 단계입니다.
