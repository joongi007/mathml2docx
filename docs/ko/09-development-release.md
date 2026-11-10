# 개발 환경·Python 호환성·배포

## 보존한 버전

기존 master 이력은 되돌리거나 강제 푸시하지 않았습니다. 다음 태그를 로컬과 원격에 보관합니다.

| 태그 | 커밋 | 내용 |
| --- | --- | --- |
| `v0.1.3-legacy` | `89205f4` | 원래 0.1.3 소스 |
| `snapshot/pre-python36-compat` | `a8ef2ec` | Python 3.6 지원 복구 전의 1.0 후보 |

호환성·검증 작업은 `compat/python36-uv`에서 검토한 뒤 master에 병합했습니다.
보존 태그에는 과거 XSL이 남아 있을 수 있습니다. 보존이 재배포 권한을 해결하지는 않습니다.
[XSL 출처 조사](06-xsl-provenance.md)를 참고하세요.

GitHub Release 게시는 병합·푸시와 별개의 작업입니다. 일반 푸시나 태그 생성으로는
패키지를 업로드하지 않습니다.

## 개발 환경

설치 사용자는 uv가 없어도 됩니다. core는 Python 3.6 이상을 지원하며,
개발·문서는 `.python-version`에 지정한 최신 Python을 사용합니다.

```sh
uv sync --locked --extra latex --extra markdown --extra test --group docs --group examples
uv run --no-sync python -m pytest -q
uv run --no-sync python -m unittest tests.test_docx_oracles -v
uv run --no-sync python -m examples.run_all
uv run --no-sync python scripts/build_docs.py
uv build
uv run --no-sync python scripts/check_dist.py
uv run --no-sync twine check dist/*
uv run --no-sync python scripts/check_wheel_install.py
```

uv 0.13.7 이상이 필요합니다. 의존성은 `pyproject.toml`에서 관리하며,
`uv.lock`은 Python 버전별 의존성 해석 결과를 고정합니다. 의존성이나 버전을 바꾸면
`uv lock`을 실행하세요. 중복된 requirements.txt 설정은 없습니다.

- `[project.dependencies]`: 실행 의존성
- `[project.optional-dependencies]`: LaTeX·Markdown·테스트 extra
- `[dependency-groups]`: 개발·문서·예제 도구. 설치 사용자에게 강제하지 않음
- `[tool.uv.dependency-groups]`: 개발 도구 그룹만 Python 3.10 이상 요구

릴리스 메타데이터 도구는 Python 3.11 이상이 필요하며 워크플로에서는 3.14로 실행합니다.
구형 Python에서는 해당 도구의 테스트만 건너뛰고 문서 변환 테스트는 유지합니다.

## Python 3.6 호환성

의존성 범위는 구형 Python에서 동작하는 릴리스를 허용합니다. Python 3.6에서는
python-docx 0.8.11과 구형 CSS·LaTeX 의존성을 선택하고, 최신 Python에서는 더 최신의
호환 버전을 선택합니다. HTML·MathML은 Python 3.6.0 이상, 선택 LaTeX 기능은
Python 3.6.2 이상과 latex2mathml 3.64 이상을 요구합니다.
3.6.0·3.6.1에서 LaTeX를 요청하면 필요한 버전을 알려 줍니다.

빌드 백엔드는 `flit_core>=3.11,<4`입니다. 3.12 계열은 Python 3.6·3.7과 현재의
메타데이터·라이선스 필드를 지원하므로 wheel·소스 설치가 가능합니다.
구형 python-docx는 링크 텍스트를 `paragraph.text`에 포함하지 않지만 실제 XML에는
링크와 텍스트가 보존됩니다. 테스트는 XML과 다시 연 문서를 확인합니다.

```sh
bash scripts/test_legacy.sh
bash scripts/test_legacy.sh python:3.7.17-slim-bullseye
```

Docker 검사는 소스를 임시 폴더로 복사하고 설치·전체 런타임 테스트·유틸리티 doctest
11개를 실행합니다. 이어 wheel을 만들어 깨끗한 venv에 설치하고 저장소 밖에서
CSS·템플릿·수식·Markdown·저장·재열기를 확인합니다. 구형 pip는 `>=21.3,<22`입니다.

```sh
uv sync --locked --no-default-groups --python 3.8 --extra latex --extra markdown --extra test
uv run --no-sync --no-default-groups --python 3.8 python -m unittest discover -v
```

기본 개발 인터프리터는 3.14입니다. 버전을 바꿀 때는 별도 환경이나 `--python`을 사용하세요.
CI는 3.6~3.14의 각 minor 버전을 검사합니다. 3.6·3.7은 Docker, 최신 버전은 uv를
사용합니다. Windows 3.8·3.14와 macOS 3.14의 변환도 검사합니다.
uv의 구형 인터프리터 지원이 Python 3.6 바이너리 자동 다운로드를 뜻하지는 않으므로
명시한 컨테이너 이미지를 사용합니다.

## CI와 CD 규칙

| 이벤트 | 검사·빌드 | 업로드 |
| --- | --- | --- |
| master 대상 PR | 런타임·품질·문서 검사 | 없음 |
| master 푸시·병합 | 런타임·품질·문서 검사, Pages 배포 시도 | 패키지 업로드 없음 |
| 태그만 푸시 | 릴리스 게시 이벤트 없음 | 없음 |
| 후보 GitHub Release 게시: `v1.0.0rc1`, prerelease 표시 | 전체 검사·버전/소스 조건·배포물 검사·깨끗한 wheel 설치 | `testpypi` 환경을 거쳐 TestPyPI |
| 정식 GitHub Release 게시: `v1.0.0` | 같은 검사 | `pypi` 환경을 거쳐 PyPI |
| `Publish to PyPI` 수동 실행 | 검사·빌드 | 없음 |

`check_release.py`는 태그·pyproject 버전·모듈 `__version__`·GitHub prerelease 표시의
일치를 요구합니다. 릴리스 소스는 `origin/master`에 포함되어야 합니다.
GitHub 체크박스만 바꿔 RC를 정식 버전으로 게시하거나 정식 버전을 RC로 사용할 수 없습니다.

업로드 전에 wheel·sdist 내용과 메타데이터, Twine 검사, 깨끗한 환경의 실제 wheel 설치와
API smoke test를 수행합니다. 업로드 job에는 검증한 배포물과 OIDC 권한만 전달하고
소스 체크아웃은 전달하지 않습니다. TestPyPI와 PyPI는 별도 인덱스이며 자동 승격하지 않습니다.

## Trusted Publisher 최초 설정

저장소 파일은 PyPI 계정이나 GitHub 승인 규칙을 설정하지 않습니다.
두 인덱스를 쓸 계획이라면 각각의 기존 프로젝트에 설정하세요.

1. PyPI의 `mathml2docx`에서 **Manage → Publishing → Add a new publisher**를 엽니다.
2. GitHub publisher에 다음 값을 등록합니다.

| 인덱스 | Owner | Repository | Workflow filename | Environment |
| --- | --- | --- | --- | --- |
| PyPI | `joongi007` | `mathml2docx` | `publish.yml` | `pypi` |
| TestPyPI | `joongi007` | `mathml2docx` | `publish.yml` | `testpypi` |

3. 별도 계정·프로젝트인 TestPyPI에도 등록합니다. 같은 이름의 프로젝트가 있다는 사실만으로
   업로드 권한이 확인되지는 않으므로 소유권을 확인하세요.
4. GitHub **Settings → Environments**에서 `pypi`와 `testpypi`를 설정합니다.
5. **Required reviewers**와 배포 가능한 태그를 설정합니다. 개인 프로젝트에서 직접
   릴리스를 만들고 승인한다면 **Prevent self-review**를 켜지 마세요.
6. 실제 게시 전에 보호 규칙을 확인하세요. YAML에 환경 이름을 쓰는 것만으로 승인 규칙이
   생기지는 않습니다.

Trusted Publishing은 `id-token: write`를 사용하므로 장기 PyPI API 키나 비밀번호를
GitHub Secrets에 넣을 필요가 없습니다.
공식 안내: [Publisher 등록](https://docs.pypi.org/trusted-publishers/adding-a-publisher/),
[OIDC 배포와 TestPyPI](https://docs.pypi.org/trusted-publishers/using-a-publisher/).

## 후보·정식 릴리스 준비

1. Word 직접 검사를 마치고 [마이그레이션](05-migration.md), [검증 한계](11-validation.md),
   라이선스와 변경 기록을 검토합니다.
2. 후보 버전은 두 패키지 버전을 `1.0.0rc1`로 맞추고 `uv.lock`을 갱신한 뒤 검증한 커밋을
   master에 병합합니다. `v1.0.0rc1` GitHub Release를 **Set as a pre-release**로 게시합니다.
3. 검사를 통과하고 환경 승인을 받으면 TestPyPI에 업로드합니다. 해당 후보 버전을
   TestPyPI에서 설치하고 동작을 확인합니다.
4. 정식 버전은 두 버전을 `1.0.0`으로 맞추고 lock·변경 기록을 갱신해 검증 후 병합합니다.
   `v1.0.0`을 정식 GitHub Release로 게시하고 PyPI 환경을 승인합니다.
5. 잘못 게시한 버전은 새 버전으로 고칩니다. 같은 버전을 덮어쓰는 방식으로 계획하지 마세요.

릴리스 전에 수동 워크플로로 검사·빌드를 수행할 수 있습니다. 수동 실행은 업로드나
계정 설정의 정상 여부를 검증하지 않습니다.
Pages는 별도입니다. 문서 게시에는 **Settings → Pages → Source: GitHub Actions**가
필요하며, PyPI 업로드 자체에 Pages가 필요한 것은 아닙니다.

## 배포 전 남은 확인

코드에는 테스트·독립 DOCX 정답·스키마 검사·버전/이벤트 조건·배포물 검사·설치한 wheel
검사가 준비되어 있습니다. 첫 실제 업로드 전에는 다음을 확인하세요.

- Word 표시·편집·재저장. M17·M19·M20의 알려진 차이 포함
- 사용할 인덱스의 소유권과 Trusted Publisher
- GitHub 환경 승인자·배포 제한
- 의도적으로 게시한 후보 버전의 TestPyPI 설치
- 최종 버전·변경 기록과 과거 XSL 포함 사본의 처리 방침
- 문서·다운로드를 호스팅하려면 Pages 활성화

2026-11-11 공개 조회에서는 PyPI 0.1.3, TestPyPI 0.1.10이 표시됐으며 1.0.0은 없었습니다.
이는 계정 권한을 확인한 결과가 아닙니다. 이번 유지보수 작업은 Release 게시·패키지 업로드·
계정 설정 변경·과거 사본 삭제를 수행하지 않습니다.

## 검증 기록

2026-11-10에는 Python 3.6에서 기본 및 2.16.5 LaTeX 백엔드로 108개 테스트와
11개 doctest·설치 smoke test를 통과했습니다. 이때 검사는 구조·보존 중심이었으며 모든
수식의 의미를 확인하지는 못했습니다. Python 3.7·3.8에서도 검사했고 3.14에서는
108개 테스트와 860개 추가 사례를 보고했습니다.

2026-11-11 독립 정답 비교에서 2.16의 텍스트·악센트·간격 불일치를 발견해 지원에서
제외했습니다. 별도의 릴리스 조건 테스트를 추가하기 전, 3.14에서 런타임 테스트 117개와
추가 사례 941개를 통과했고 실제 Python 3.6.15·3.8에서도 통과했습니다.
입력과 JSON 정답은 보관하고 생성 DOCX는 Git·sdist에서 제외합니다.
[검증 문서](11-validation.md)는 이 검사와 Word 직접 확인의 차이를 설명합니다.
