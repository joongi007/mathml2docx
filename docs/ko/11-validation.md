# 호환성과 검증

생성 문서는 WordprocessingML과 OMML을 사용합니다. 저장된 내용은 독립적으로 작성한
정답과 공식 XML 스키마로 검사합니다. 문서 프로그램에 따라 글꼴·수식 배치·페이지 구성이
달라질 수 있으므로 사용할 환경에서도 결과를 확인하세요.

## 검사하는 항목

| 검사 | 목적 | 한계 |
| --- | --- | --- |
| 독립 수식 정답 | 분수·첨자·근호·행렬·괄호의 역할과 내용 | 화면·대화형 편집 검사가 아님 |
| 저장 문서 비교 | 본문 순서·강조·표·병합·번호·이미지·링크 | 선택한 속성을 검사 |
| 공식 ECMA-376 스키마 | OMML과 본문 요소 순서의 유효성 | 의도한 의미까지 보증하지 않음 |
| 고의 오류 주입 | 대표적인 수식 손상을 검출하는지 확인 | 모든 결함의 검출을 보증하지 않음 |
| Word 자동화 | Word 16에서 예제 열기·출력·재저장 | 한 설치 환경에서 확인 |
| LibreOffice 검사 | 가져온 수식 객체 수와 실제 PDF 수식 출력 | Word와 배치가 다를 수 있음 |

수식 코퍼스에는 직접 작성한 기본 수식 44개, 시드로 조합한 수식 240개, 고급 입력 18개가
있습니다. 조합 수식은 단순 토큰을 포함하며 서로 다른 입력 문자열은 210개입니다.
복잡한 보고서 240종을 뜻하지 않습니다. 고급 예제에는 중첩 블록 행렬·6단 연분수·적분·
편미분과 본문·표·이미지를 섞은 문서가 있습니다.

입력은 `examples/assets/math-corpus/`·`examples/assets/advanced-math/`,
독립 정답은 `tests/fixtures/`에서 관리합니다. 생성한 DOCX는 Git에 보관하지 않습니다.
[실행 예제](examples/00-index.md)에서 직접 확인할 문서를 내려받을 수 있습니다.

## 글꼴

변환기는 글꼴 이름을 지정하며 글꼴 파일을 내장하지 않습니다. 문서의 문자를 포함하는
글꼴을 설치하세요. 지정한 글꼴이 없거나 대체 글꼴에 문자가 없으면 한글·수학 문자 등이
네모로 표시될 수 있습니다.

CSS `font-family`는 라틴·동아시아·복합 문자 글꼴 슬롯에 적용합니다.
글꼴을 지정하지 않으면 Word 템플릿 기본값을 사용합니다. 예제 24~28은 Malgun Gothic을
사용합니다. 다른 시스템에서는 Noto Sans CJK 등 설치된 CJK 글꼴을 선택하세요.
Python 패키지는 이 글꼴 파일을 포함하지 않습니다.

## LibreOffice

**Writer와 Math를 함께 설치하세요.** Writer만 설치한 최소 환경에서는 PDF 출력이
성공해도 수식 전체가 빈칸으로 나올 수 있습니다. LibreOffice 24.2.7.2에서 이를 재현했고,
같은 파일에 Math를 추가하자 수식 표시가 복원됐습니다. 한글·수식 글꼴도 필요합니다.

Debian·Ubuntu 설치 예시:

```sh
sudo apt-get install libreoffice-writer libreoffice-math poppler-utils fonts-noto-cjk fonts-stix
```

미리보기 생성과 검사:

```sh
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/render_examples.py --output examples/output/libreoffice-review
```

검사는 새 임시 출력으로 실행하며, LibreOffice의 flat XML에서 수식 객체 수를 비교하고
PDF의 수식 텍스트를 읽어 실제 렌더링도 확인합니다. 누락·빈 수식은 실패로 처리합니다.
`pdftotext`가 필요하며 PATH에 없으면 `--soffice`·`--pdftotext`를 지정하세요.
기존 출력 파일을 교체하려면 `--force`가 필요합니다.

Writer 24.2는 기본 OMML 테두리와 취소선도 생략할 수 있습니다.
`math_target='libreoffice'`를 선택하면 이 표기를 명시적인 대체 처리로 넘기고 화학식 원소의
정체를 유지합니다. 불필요한 빈 뒤 첨자 쌍은 생성하지 않아 자리표시자 네모를 방지합니다.
기본 Word 대상 화학식 미리보기에서는 테두리 차이를 확인할 수 있습니다. 필요하면 이미지
대체를 사용하세요.

특정 뷰어를 위해 기본 수식을 자동으로 이미지로 바꾸지는 않습니다. 미지원 입력에는
[원문·이미지 대체 처리](03-mathematics.md)를 선택하세요. 이미지가 편집 가능성보다 고정된
모양이 중요할 때 유용하지만, 편집 가능한 수식은 아닙니다.

### 알려진 표시 차이

phantom의 예약 공간·기울어진 분수·문자열 따옴표·악센트·줄바꿈은 프로그램마다 다를 수
있습니다. phantom의 본문은 의도적으로 숨기며 예약 크기는 다르게 처리될 수 있습니다.
LibreOffice에서는 기울어진 분수가 일반 분수처럼 나올 수 있습니다. 이 기능이 중요하면
수식 갤러리의 입력과 출력을 함께 비교하세요. 구조 검증은 화면 동등성 인증이 아닙니다.

## 자동 검사 재현

```sh
uv run --no-sync python -m pytest -q
uv run --no-sync python scripts/check_math_mutations.py
uv run --no-sync python scripts/prepare_ecma_schema.py /tmp/mathml2docx-ecma376
uv run --no-sync python scripts/validate_math_schema.py --schemas /tmp/mathml2docx-ecma376
```

스키마는 [ECMA-376](https://ecma-international.org/publications-and-standards/standards/ecma-376/)과
[W3C xml.xsd](https://www.w3.org/2001/xml.xsd)에서 받으며 준비 스크립트가 해시를 검사합니다.
스키마 원본은 패키지에 포함하지 않습니다.

Word가 설치된 Windows·WSL에서는:

```sh
python scripts/check_word.py --input examples/output --output examples/output/word-review
python scripts/check_word.py --input examples/output --output examples/output/word-mixed-review --examples 24_dense_report 25_research_report 26_template_workbook 27_advanced_latex --check-blocks
```

입력은 읽기 전용으로 열고 별도 파일로 저장합니다. Word가 Unicode 마이너스 U+2212를
ASCII 하이픈 마이너스로 바꿀 수 있어 Word 재저장 비교에서만 수식 문자열의 이 차이를
허용합니다. 변환기와 독립 정답의 비교는 Unicode까지 정확하게 유지합니다.
Word 웹·macOS Word·접근성·대화형 수식 편집은 사용할 환경에서 별도로 확인해야 합니다.
