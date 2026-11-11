# mathml2docx

HTML과 MathML 수식을 Word 문서(`.docx`)로 변환하는 Python 라이브러리입니다.
MathML은 Python에서 직접 Word의 OMML 수식으로 변환합니다. XSL이나 Office 설치가 필요하지 않습니다.
LaTeX와 Markdown은 선택 의존성을 설치해 사용할 수 있습니다.

- [시작하기](01-getting-started.md): 설치, 문자열·파일 변환, 기존 문서에 추가
- [API와 옵션](02-api.md): 공개 메서드, 스타일, 이미지와 변환 제약
- [문서 운영](04-publishing.md): 로컬 빌드와 GitHub Pages 배포

이 프로젝트는 [html2docx](https://github.com/pqzx/html2docx)에서 파생되었습니다.
브라우저의 렌더링 결과를 그대로 복제하는 도구는 아닙니다. 필요한 HTML·수식·스타일이
변환되는지 실제 출력 문서에서 확인하세요.

- [1.0.0 마이그레이션](05-migration.md)
- [기존 XSL 출처 조사](06-xsl-provenance.md)
- [원본 이슈 49건 검토](07-upstream-audit.md)

- [실행 예제 27개와 DOCX·PDF](examples/00-index.md)
- [작업별 사용법과 전체 기능 표](08-recipes.md)

- [uv 개발 환경·Python 호환성·PyPI 배포](09-development-release.md)

- [라이선스와 XSL 대체 범위](10-licensing.md)

- [수식 검증과 남은 한계](11-validation.md)
- [다른 도구와 비교해 선택하기](12-choosing.md)
