# 라이선스와 XSL 대체 범위

## 프로젝트와 의존성

프로젝트 코드는 [MIT 라이선스](https://github.com/joongi007/mathml2docx/blob/master/LICENSE)로
제공합니다. 원본 html2docx의 `Copyright (c) 2019 pqzx` 고지를 유지하고,
프로젝트 작성자 고지는 `Copyright (c) 2024-2026 joongi007`로 정리했습니다.

의존성을 전부 MIT로 다시 배포하는 뜻은 아닙니다. 실행 의존성에는 MIT·BSD-3-Clause·
MIT-CMU 등이 적용되며, lxml·Pillow의 바이너리 배포본에는 추가 구성 요소의 고지가 있습니다.
docxtpl 테스트·예제 연동에는 해당 패키지의 LGPL 조건이 적용됩니다. 정확한 버전과 배포
형태에 따라 각 패키지의 고지를 확인해야 합니다.
[제삼자 고지](https://github.com/joongi007/mathml2docx/blob/master/THIRD_PARTY_NOTICES.md)는
직접 의존성의 출처와 조사 범위를 설명하며, wheel·sdist에도 LICENSE와 함께 포함됩니다.

## XSL은 어떻게 대체했나

기존 `MML2OMML.XSL` 파일과 그 파일을 여는 경로·XSLT 호출을 제거했습니다.
새 코드는 MathML을 XML로 파싱하고 태그에 맞는 OMML 노드를 직접 만듭니다.
LaTeX는 선택 의존성 latex2mathml에서 MathML로 변환한 뒤 같은 네이티브 변환기를 사용합니다.
기존 XSL 템플릿을 Python으로 옮겨 쓰는 방식은 사용하지 않았습니다.

회귀 테스트는 `etree.XSLT`와 파일 기반 `etree.parse` 사용을 막은 상태에서도 분수·첨자·
근호가 변환되는지 확인합니다. 빌드 검사는 wheel과 sdist에서 XSL 파일이 제외됐고,
프로젝트 및 제삼자 고지가 포함됐는지 확인합니다.

이것이 Office XSL의 모든 기능과 결과를 동일하게 재현한다는 뜻은 아닙니다.
지원 범위는 [수식 안내](05-migration.md)에 명시했습니다. 미지원 태그는
`UnsupportedMathMLError`를 내며, 지원 태그의 모든 시각적 속성까지 재현하지는 않습니다.

## 아직 확정할 수 없는 부분

기존 XSL은 AbiWord 공개 사본과 바이트 단위로 같지만, 실제 복사한 사이트와 재배포
허락은 확인되지 않았습니다. MIT 고지를 추가하는 것으로 이 권한이 생기지는 않습니다.
[출처 조사](06-xsl-provenance.md)에 확인한 사실과 증거를 보관했습니다.

새 배포물의 XSL 의존 제거와 과거 배포물의 법적 상태는 별개입니다. Git 이력·보존 태그·
기존 PyPI 배포본은 이번 코드 변경으로 사라지거나 권한 문제가 소급 해결되지 않습니다.
현재 고지는 확인한 범위의 정리이며, 모든 과거 자료의 권리 관계를 확정하는 보증은 아닙니다.
