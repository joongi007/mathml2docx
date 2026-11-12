# 다른 도구와 비교해 선택하기

입력 형식과 문서 작업 흐름에 맞는 변환기를 선택하세요.
아래 표는 공식 문서의 기능 구분이며 같은 입력으로 성능을 비교한 벤치마크는 아닙니다.

| 도구 | 공식적으로 안내하는 기능 | 선택할 때 볼 점 |
| --- | --- | --- |
| [Pandoc](https://pandoc.org/MANUAL.html#math) | 여러 문서 형식과 DOCX의 OMML 수식 출력 | Markdown·LaTeX 등 문서 전체 변환 파이프라인에 검토할 수 있습니다. |
| [html4docx](https://github.com/dfop02/html4docx) | HTML→DOCX, CSS·이미지·표·목록 개선 | 같은 upstream에서 이어진 Python HTML 변환 대안으로, 실제 HTML·API 호환성을 비교하세요. |
| [Microsoft 365](https://learn.microsoft.com/en-us/office/math/mathml) | MathML 가져오기·내보내기와 OMML 저장 | Word 안에서 직접 작업할 때 제품의 수식 기능도 검토할 수 있습니다. |
| mathml2docx | Python API, HTML 안의 지원 MathML, 선택 LaTeX, 기존 문서·셀·마커·북마크 삽입 | 서버나 로컬 코드에서 기존 python-docx 흐름과 결합할 때 사용할 수 있습니다. |

이 프로젝트의 목표는 Python에서 HTML·수식을 기존 Word 문서에 넣는 작업을 짧은 코드로
구현하고, 지원 범위와 검증 사례를 공개하는 것입니다. 외부 업로드 없이 변환할 수 있지만,
명시적으로 제공한 이미지·CSS 로더가 외부에 접근하는지는 사용하는 애플리케이션에 달려 있습니다.
