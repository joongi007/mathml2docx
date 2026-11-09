# 문서 운영

## 로컬 빌드

Python 3.10 이상에서 저장소 루트를 기준으로 실행합니다.

```sh
python -m pip install -r requirements-docs.txt -r requirements-examples.txt '.[latex,test]'
python scripts/build_docs.py
python -m http.server 8000 --directory site
```

`http://localhost:8000`에서 문서를 확인합니다. `site/`에는 HTML, 검색 인덱스,
`llms.txt`, `llms-full.txt`, `downloads/mathml2docx-skill.zip`이 생성됩니다.
빌드 스크립트는 MkDocs의 `--strict` 옵션으로 문서 경고를 실패로 처리합니다.

## GitHub Pages

저장소의 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로
설정하세요. 이후 `master`에 변경 사항이 반영되면 `Documentation` 워크플로가 빌드하고
`github-pages` 환경으로 배포합니다. PR에서는 빌드만 검사합니다.
Actions 화면에서 수동 실행할 수도 있습니다.

기본 배포 주소는 `https://joongi007.github.io/mathml2docx/`입니다.
이 설정 파일을 추가한 것만으로 사이트가 공개되지는 않습니다. GitHub의 Pages 설정과
워크플로 성공 여부를 확인하세요.

문서는 `docs/`, 탐색 메뉴는 `mkdocs.yml`, 스킬은 `skills/mathml2docx/`에서 수정합니다.
문서 추가 시 `mkdocs.yml`의 메뉴에도 등록하세요. API 설명과 예제는 실제 구현과 함께
갱신하고 빌드 산출물은 커밋하지 않습니다.

배포 구성은 [GitHub Pages 공식 문서](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)와
[MkDocs 배포 문서](https://www.mkdocs.org/user-guide/deploying-your-docs/)를 참고합니다.

예제 코드는 `examples/`와 `examples/catalog.json`을 함께 수정하세요. 문서 빌드는 모든 예제를
실행하고 `docs/examples/`에 전체 코드와 다운로드 링크를 생성합니다. 이 폴더의 문구를
직접 수정하면 다음 빌드에서 덮어쓰므로 설명은 catalog에서 수정합니다.
PDF 참조 결과는 `python scripts/render_examples.py`로 다시 생성한 뒤
`docs/assets/previews/`로 복사합니다. 이 과정에는 별도 LibreOffice 설치가 필요합니다.
