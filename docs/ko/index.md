# HTML과 수식을 Word 문서로

Python 문자열·파일·문서 템플릿으로 Word 문서를 만드세요.
mathml2docx는 지원하는 HTML과 MathML을 서식 있는 본문과 편집 가능한 Word 수식으로 변환합니다.

## 첫 문서 만들기

PyPI에 배포된 패키지를 설치하세요.

```sh
python -m pip install mathml2docx
```

```python
from mathml2docx import convert

convert('<h1>학습 노트</h1><p>값 <math><mi>x</mi></math>을 편집할 수 있습니다.</p>',
        'lesson.docx')
```

[시작하기](01-getting-started.md)에서 설치 방법과 실행 순서를 확인하세요.
문서를 생성할 때 Microsoft Office는 필요하지 않습니다.

## 작업에 맞는 안내 찾기

| 입력·작업 | 시작할 문서 |
| --- | --- |
| 본문·표·이미지가 있는 HTML | [시작하기](01-getting-started.md), [서식 활용법](08-recipes.md) |
| MathML·LaTeX 수식 | [수식 배치와 입력 처리](03-mathematics.md) |
| 기존 Word 템플릿 | [마커](examples/15_markers.md), [북마크](examples/16_bookmarks.md), [docxtpl](examples/17_docxtpl.md) |
| 과학 보고서·학습지 | [연구 보고서](examples/25_research_report.md), [템플릿 워크북](examples/26_template_workbook.md) |
| 화학식·비표준 수식 | [화학 표기](examples/28_chemistry_enclosures.md), [대체 렌더링](examples/29_math_fallbacks.md) |
| mathml2docx 0.x 코드 이전 | [마이그레이션](05-migration.md) |

## 출력 결과 이해하기

지원하는 수식은 Word의 기본 수식 형식인 OMML로 저장돼 편집할 수 있습니다.
HTML·CSS는 일부 기능을 지원하며, 브라우저 배치·모든 MathML 표기·모든 LaTeX 패키지를
재현하지는 않습니다. 미지원 입력에는 명시적인 대체 처리를 적용하고,
글꼴과 LibreOffice 관련 사항은 [프로그램 호환성 안내](11-validation.md)를 확인하세요.

[전체 예제](examples/00-index.md)에서 Python 코드·DOCX·PDF를 살펴보거나,
[API 안내](02-api.md)에서 개별 옵션을 찾아볼 수 있습니다.
