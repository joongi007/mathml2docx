# 문서 사이트 빌드

문서 사이트는 Python 빌더가 Markdown을 HTML로 변환하는 정적 사이트입니다.
Jinja2 템플릿과 Pygments 코드 강조를 사용하며 MkDocs나 JavaScript 빌드 도구는 필요하지 않습니다.

이 문서는 문서 사이트를 빌드하는 기여자를 위한 안내입니다.
패키지 설치는 [시작하기](01-getting-started.md)에서 다룹니다.

## 로컬 빌드와 미리보기

Python 3.10 이상과 uv 0.13.7 이상을 사용해 저장소 루트에서 실행하세요.

```sh
uv sync --locked --all-extras --group docs --group examples
uv run --no-sync python scripts/build_docs.py
python -m http.server 8000 --directory site
```

영어는 `http://localhost:8000/`, 한국어는 `http://localhost:8000/ko/`에서 확인합니다.
빌드는 Python 예제를 실행해 DOCX와 소스 ZIP을 생성하고 두 언어를 HTML로 변환합니다.
로컬 링크·앵커·번역 쌍·검색 인덱스·다운로드를 검사한 뒤에만 출력 폴더를 교체합니다.
다른 생성 폴더에 빌드하려면 `--output PATH`를 지정하세요.

## 내용과 레이아웃 수정

| 내용 | 원본 |
| --- | --- |
| 영어·한국어 안내 | `docs/*.md` / `docs/ko/*.md` |
| 두 언어 목차 | `docs_site/navigation.json` |
| 페이지 템플릿·디자인 토큰·동작 | `docs_site/page.html`, `site.css`, `site.js` |
| 예제 제목·설명 | `examples/catalog.json`, `catalog.ko.json` |
| 실행 예제 코드 | `examples/` |
| Markdown 변환·링크 검사 | `scripts/site_builder.py` |

새 페이지는 두 언어로 추가하고 각각의 목차에 등록하세요. 렌더링·레이아웃을 바꿀 때도
기존 URL을 유지합니다. 자동 생성되는 예제 페이지는 카탈로그와 Python 코드를 수정하면
다음 빌드에 반영됩니다.

검색은 브라우저에서 언어별 JSON 인덱스를 조회하며 영어·한국어·API 이름의 부분 문자열을
찾습니다. 결과는 HTML이 아닌 텍스트로 삽입합니다. JavaScript 없이도 본문과 목차를
읽을 수 있으며, 검색과 코드 복사 기능은 JavaScript가 필요합니다.

## 배포

GitHub의 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로
지정하세요. `Documentation` 워크플로우는 PR과 develop 푸시에서 빌드하고,
master 빌드만 `github-pages` 환경으로 배포합니다.

생성된 `site/`·DOCX·예제 출력 폴더는 커밋하지 않습니다. 참조 PDF를 갱신하려면
LibreOffice Writer·Math·글꼴·Poppler를 설치한 뒤 [렌더링 검사](11-validation.md#libreoffice)를
실행하세요. PDF 미리보기와 편집 가능한 DOCX는 별도 파일입니다.
