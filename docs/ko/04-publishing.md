# 문서 운영

## 로컬 빌드

저장소 루트에서 Python 3.10 이상으로 실행합니다.

```sh
uv sync --locked --extra latex --extra markdown --group docs --group examples
uv run --no-sync python scripts/build_docs.py
python -m http.server 8000 --directory site
```

`http://localhost:8000`은 영문 기본 문서, `http://localhost:8000/ko/`는 한국어 문서입니다.
언어 선택은 현재 보고 있는 페이지의 다른 언어판으로 이동합니다. 언어마다 탐색 메뉴·
검색 색인을 생성합니다. 두 언어에서 예제 코드와 DOCX 다운로드를 제공하며,
실행 코드와 바이너리 원본은 공유합니다.

두 언어 모두 MkDocs `--strict`로 빌드하므로 경고가 있으면 실패합니다. 빌드 후 37쌍의
페이지가 갖춰졌는지, 실제 HTML의 언어·같은 페이지 전환 링크·검색·다운로드도 확인합니다.
번역 페이지를 추가하면 두 언어의 페이지 수에 맞춰 검사 범위가 늘어납니다.

## GitHub Pages

**Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 설정합니다.
master에 변경이 반영되면 `Documentation` 워크플로가 두 언어를 하나의 사이트로 빌드해
`github-pages` 환경으로 배포합니다. PR은 빌드만 합니다. Actions에서 수동 실행도 가능합니다.

주소는 영문 `https://joongi007.github.io/mathml2docx/`,
한국어 `https://joongi007.github.io/mathml2docx/ko/`입니다.
워크플로 파일이 있다는 사실만으로 Pages가 활성화되지는 않습니다. 저장소 설정과
실제 배포 결과를 확인하세요.

## 원본과 번역 관리

| 대상 | 영어 | 한국어 |
| --- | --- | --- |
| README | `README.md` | `README.ko.md` |
| 안내 문서 | `docs/*.md` | `docs/ko/*.md` |
| 탐색·검색 설정 | `mkdocs.yml` | `mkdocs.ko.yml` |
| 예제 설명 | `examples/catalog.json` | `examples/catalog.ko.json` |
| 생성되는 예제 문서 | `docs/examples/` | `docs/ko/examples/` |

기능이나 API가 바뀌면 양쪽 문서를 함께 수정하세요. 새 페이지는 양쪽 탐색 메뉴에 추가합니다.
예제 설명은 카탈로그에서 수정합니다. 생성된 문서를 직접 고치면 다음 빌드에서 덮어씁니다.
예제 코드의 원본은 `examples/`에 있습니다.

`site/`, 생성 DOCX, `docs/ko/assets/`·`downloads/`의 빌드용 사본은 커밋하지 않습니다.
참조 PDF 원본은 `docs/assets/previews/` 한 곳에서 관리합니다. 별도 LibreOffice를 설치해
`python scripts/render_examples.py`를 실행한 뒤 검토한 PDF를 복사할 수 있습니다.
기존 PDF는 과거 미리보기이므로 문서 빌드 때 자동 갱신하지 않습니다.

## MkDocs가 필요한가요?

필수는 아닙니다. GitHub Pages는 정적 HTML·CSS·JavaScript를 호스팅하므로 자체 사이트도
가능합니다. 현재는 Markdown 원본과 기존 주소를 유지하면서 목차·검색·링크 검사·테마를
활용하려고 MkDocs를 사용합니다. 별도 다국어 플러그인 없이 두 설정을 빌드하고,
작은 공통 템플릿과 hook으로 언어 전환을 제공합니다.

전용 레이아웃이나 인터랙티브 변환기가 필요하면 테마를 확장하거나 자체 사이트로
이전할 수 있습니다. Markdown·예제 카탈로그·Python 예제는 변환 엔진과 분리되어 있습니다.
이전할 때는 기존 주소, 다국어 페이지 대응, 검색, 다운로드와 접근성을 함께 유지하세요.

공식 안내: [GitHub Pages 사용자 지정 워크플로](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages),
[MkDocs 테마 사용자 지정](https://www.mkdocs.org/user-guide/customizing-your-theme/).
