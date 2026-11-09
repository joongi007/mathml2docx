# 개발 환경·Python 호환성·PyPI 배포

## 버전 보존과 현재 작업 위치

기존 master는 되돌리거나 강제 푸시하지 않습니다. 다음 태그를 로컬과 원격에 보관해 변경 전 상태를 보존합니다.

| 태그 | 커밋 | 내용 |
| --- | --- | --- |
| `v0.1.3-legacy` | `89205f4` | 원래 0.1.3 소스 |
| `snapshot/pre-python36-compat` | `a8ef2ec` | Python 3.6 호환성 복구 전의 1.0 후보 |

호환성·uv·배포 구성과 수식 검증 변경은 `compat/python36-uv`에서 검사한 뒤 master에 반영합니다.
GitHub Release·PyPI 배포는 별도 검토 후 진행합니다. 보존 태그를 만들거나 푸시하는 것만으로
PyPI 배포가 시작되지는 않습니다. 자동 업로드는 아래의 GitHub Release 게시 이벤트가 기준입니다.

## 개발 환경

설치 사용자는 uv가 없어도 됩니다. 배포 라이브러리는 Python 3.6 이상을 지원하고,
개발·문서 도구는 `.python-version`에 고정한 최신 Python에서 실행합니다.

```sh
uv sync --locked --extra latex --extra markdown --extra test --group docs --group examples
uv run --no-sync python -m pytest -q
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/build_docs.py
uv build
uv run --no-sync twine check dist/*
```

uv 0.13.7 이상이 필요합니다. `pyproject.toml`이 실행·선택·개발 의존성의 단일 원천이며,
`uv.lock`이 Python 버전별 해석 결과와 개발 환경을 고정합니다. 의존성을 바꾸면 `uv lock`을
실행해 lockfile도 함께 검토하세요. `requirements*.txt`는 중복 관리하지 않습니다.

- `[project.dependencies]`: 실제 사용자가 설치하는 실행 의존성
- `[project.optional-dependencies]`: `latex`, `markdown`, 테스트용 `test` extra
- `[dependency-groups]`: 개발·문서·예제 도구. 배포 사용자에게 강제 설치하지 않음
- `[tool.uv.dependency-groups]`: 개발 도구만 Python 3.10 이상으로 제한

## Python 3.6 호환성

의존성의 최소 버전은 3.6에서 동작하는 릴리스를 허용하며, 패키지 관리자는 해당 인터프리터와
호환되는 버전을 선택합니다. 예를 들어 Python 3.6에서는 python-docx 0.8.11과 구버전
CSS·LaTeX 의존성을 사용합니다. 최신 Python에서는 최신 호환 버전을 사용합니다.

빌드 백엔드는 `flit_core>=3.11,<4`입니다. 3.12 계열은 Python 3.6에서도 동작하고
현재 메타데이터·라이선스 필드를 처리하므로, wheel뿐 아니라 sdist 소스 설치도 가능합니다.
구버전 python-docx는 링크 텍스트를 `paragraph.text`에 포함하지 않지만 실제 DOCX XML에는
링크와 텍스트가 보존됩니다. 라이브러리의 문서 변환 결과는 XML·재열기 검증으로 확인합니다.

```sh
# Docker를 사용해 호스트 Python이나 작업 폴더를 바꾸지 않고 검증합니다.
bash scripts/test_legacy.sh
bash scripts/test_legacy.sh python:3.7.17-slim-bullseye
```

이 검사는 컨테이너의 임시 폴더에 소스를 복사하고, 실제 설치·전체 unittest·docstring 예제를
실행합니다. 이어 wheel을 만들고 깨끗한 venv에 설치한 뒤 저장소 밖에서 CSS·템플릿·수식·
Markdown 변환을 확인합니다. Python 3.6/3.7의 pip는 `>=21.3,<22`를 사용합니다.

Python 3.8 이상에서는 다음처럼 lockfile로 구버전 환경을 선택할 수 있습니다.

```sh
uv sync --locked --no-default-groups --python 3.8 --extra latex --extra markdown --extra test
uv run --no-sync --no-default-groups --python 3.8 python -m unittest discover -v
```

개발용 `.python-version`은 3.14이므로, 버전을 오가며 작업할 때는 별도 환경 경로를 지정하거나
`--python`을 명시하세요. CI는 Python 3.6·3.7을 Docker에서, 3.8~3.14의 각 minor 버전을 uv로 검사합니다. Windows 3.8·3.14와 macOS 3.14의 변환 검사도 실행합니다.
최신 uv가 구버전 인터프리터를 지원하더라도 Python 3.6 바이너리를 자동 다운로드할 수 있다는
뜻은 아닙니다. 그래서 3.6 검증에는 명시한 컨테이너를 사용합니다.

## PyPI Trusted Publishing 최초 설정

이 파일과 워크플로를 추가하는 것만으로 PyPI 계정 설정이 바뀌지는 않습니다.
최초 한 번은 프로젝트 소유자가 다음을 설정해야 합니다.

1. PyPI에서 `mathml2docx`의 **Manage → Publishing → Add a new publisher**를 엽니다.
2. GitHub publisher에 다음 값을 등록합니다.

| 필드 | 값 |
| --- | --- |
| Owner | `joongi007` |
| Repository | `mathml2docx` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

3. GitHub 저장소 **Settings → Environments**에서 `pypi` 환경을 만듭니다.
4. **Required reviewers**에 검토자를 등록하고, 배포 가능한 태그를 제한합니다. 개인 저장소에서
   본인이 릴리스를 만들고 승인한다면 self-review를 막는 옵션은 켜지 마세요.
5. 실제 배포 전 환경 승인 설정이 적용됐는지 확인합니다. YAML의 `environment: pypi`만으로
   승인자가 자동 등록되지는 않습니다.

비밀번호나 장기 PyPI 토큰을 GitHub Secrets에 저장할 필요가 없습니다. publish job의
`id-token: write`로 GitHub OIDC 신원을 PyPI가 검증합니다.
공식 절차: [PyPI publisher 등록](https://docs.pypi.org/trusted-publishers/adding-a-publisher/),
[PyPI 업로드 작업](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## 검토 후 배포

1. 호환성 브랜치의 변경을 검토하고 master에 반영합니다.
2. 버전과 변경 내용을 확정합니다. 예: `1.0.0`.
3. GitHub에서 그 버전에 해당하는 태그 `v1.0.0`의 Release를 작성하고, 검토 후 게시합니다.
4. `Publish to PyPI`가 전체 호환성 검사·문서 빌드·패키지 검사를 실행합니다.
5. release tag가 `pyproject.toml`의 버전과 같은지, 소스가 master에 포함됐는지 검사합니다.
6. 모든 검사를 통과하면 `pypi` 환경의 승인을 기다립니다. 승인 후에만 PyPI에 업로드합니다.

`workflow_dispatch`로 수동 실행하면 검사와 빌드까지만 수행하며 업로드하지 않습니다.
일반 master 푸시·PR·태그 푸시·prerelease 게시로는 PyPI 업로드를 하지 않습니다.
PyPI의 같은 버전 파일을 덮어쓰는 방식으로 복구하지 말고, 문제가 있으면 새 버전을 준비하세요.

Pages 배포와 PyPI 배포는 서로 별개입니다. 이 작업에서 원격 Pages 설정이나 PyPI 설정을
대신 변경하지 않았습니다.

## 검증 기록 (2026-11-10)

Python 3.6에서 전체 unittest 108개를 기본 LaTeX 백엔드와 2.16.5 백엔드로 각각
실행했습니다. docstring 예제 11개와 소스·wheel 설치 후 변환도 통과했습니다.
Python 3.7·3.8에서도 전체 변환 검사를 실행했고, 원격 CI가 위 Python·OS 조합을 검사합니다.
Python 3.14에서는 pytest 108개와 추가 사례 860개, 고의 수식 오류 7종 검출,
공식 스키마 검사, 문서 빌드, 배포 메타데이터·라이선스·XSL 미포함 검사를 수행합니다.

[수식 검증 문서](11-validation.md)에 코퍼스·원본 스키마·실행 명령과 화면상의 한계를
기록했습니다. XML 검사·LibreOffice 렌더링은 Microsoft Word 직접 검증과 구분합니다.
작업 브랜치에서는 Pages 배포를 건너뛰며, 일반 푸시로 PyPI 업로드를 수행하지 않습니다.
