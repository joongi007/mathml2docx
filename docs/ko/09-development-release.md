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

GitHub Release 설명 게시는 패키지 업로드와 별개입니다. develop 푸시는 업로드하지 않고,
master 푸시는 TestPyPI 후보를, 검증한 정식 버전 태그는 PyPI 배포를 시작합니다.

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

## 브랜치 작업 흐름

현재 `master`가 main·릴리스 역할을 합니다. 이름을 `main`으로 바꾸지는 않았습니다.
일상적인 개발은 `develop`에서 시작합니다.

```sh
git switch develop
git pull --ff-only
git switch -c feature/table-layout
# 커밋·검증 후 develop 대상 PR을 만듭니다.
```

안정화 기간이 필요하면 develop에서 `release/1.0.0`을 만드세요. 준비되면 master에
병합해 TestPyPI를 검증하고, 최종 수정은 develop에도 반영합니다. 작은 릴리스는
release 브랜치 없이 develop에서 master로 병합해도 됩니다.
develop·feature의 PR이나 푸시로는 패키지를 업로드하지 않습니다.

| 이벤트 | 검사·빌드 | 업로드 |
| --- | --- | --- |
| develop 푸시, develop/master 대상 PR | Python 3.6~3.14·품질·문서·배포물 검사 | 없음 |
| master 푸시·병합 | 같은 전체 검사, 고유 후보 버전 빌드, 깨끗한 wheel 설치 | TestPyPI 업로드 후 해당 인덱스의 실제 파일 설치 검사 |
| 검증한 master 커밋의 정식 태그 `v1.0.0` 푸시 | 버전·소스·같은 커밋의 TestPyPI 성공, 전체 검사, 정식 배포물·설치 검사 | `pypi` 환경을 거쳐 PyPI |
| 기존 태그의 GitHub Release 설명 게시 | 추가 패키지 업로드 없음 | 없음 |
| master에서 `TestPyPI candidate` 수동 실행 | 동일한 후보 파이프라인 | TestPyPI 업로드·설치 검사 |
| `Publish to PyPI` 수동 실행 | 검사·빌드 | 없음 |

master의 패키지 검사는 `TestPyPI candidate`에서 재사용 Python 워크플로를 호출합니다.
같은 푸시에 독립적인 Python 워크플로를 한 번 더 실행하지 않습니다.
별도의 Documentation 워크플로는 한·영 문서를 빌드하고 master만 배포합니다.

## TestPyPI 설치 자동 검증

master에는 `1.0.0`처럼 배포할 정식 버전을 기록합니다. CI의 임시 체크아웃에서만 두 버전을
`1.0.0.dev<run_id><세 자리 attempt>`로 바꾸고 lockfile을 갱신합니다.
버전 변경을 저장소에 커밋하지 않습니다. 실행·전체 재실행마다 고유 후보 버전이 생기므로
같은 버전 재업로드 충돌을 피합니다. 정확한 버전은 워크플로 요약에 표시합니다.

업로드 후 Python 3.8·3.14 job이 TestPyPI의 해당 버전 JSON을 조회합니다.
파일 이름·SHA-256이 빌드한 wheel과 같아야 하며, 공식 TestPyPI 다운로드 URL의 파일을
새 venv에 설치합니다. 의존성은 PyPI에서만 설치하고 `--extra-index-url`로 두 인덱스를
섞지 않습니다. 저장소 밖에서 CSS·MathML·LaTeX·Markdown·마커 교체·저장·재열기를
검사합니다. 앞선 Docker job은 Python 3.6·3.7 소스·wheel 설치도 검사합니다.

로컬 wheel 검사만 통과해서는 후보 워크플로가 성공하지 않습니다. 업로드와 두 원격 설치
검사까지 성공해야 합니다. 인덱스 반영 지연에는 짧게 재시도합니다.
일부 파일 업로드 후 실패했다면 같은 버전을 반복 업로드하기보다 **Re-run all jobs**로
새 후보 버전을 만드세요.

## Trusted Publisher 최초 설정

저장소 파일은 계정 소유권·GitHub 보호 규칙·Trusted Publisher를 설정하지 않습니다.
각 인덱스의 기존 프로젝트에 다음을 등록하세요.

| 인덱스 | Owner | Repository | Workflow filename | Environment |
| --- | --- | --- | --- | --- |
| TestPyPI | `joongi007` | `mathml2docx` | `testpypi.yml` | `testpypi` |
| PyPI | `joongi007` | `mathml2docx` | `publish.yml` | `pypi` |

1. 각 프로젝트의 **Manage → Publishing → Add a new publisher**에서 위 값을 등록합니다.
   TestPyPI의 계정·프로젝트 권한은 별도입니다.
2. GitHub **Settings → Environments → testpypi / pypi**를 설정합니다.
3. master 후보 배포를 중단 없이 자동화하려면 `testpypi`의 필수 승인자를 두지 않고 master를
   허용합니다. `pypi`에는 필수 승인자와 정식 태그 배포 제한을 설정하세요. YAML의 환경
   이름만으로 승인 규칙이 생기지는 않습니다. 개인 프로젝트에서 본인이 승인해야 한다면
   self-review를 막지 마세요.
4. 필요에 맞게 master·develop의 PR 검토·필수 CI 검사를 설정합니다.
   `v*` 태그 생성·삭제 권한은 저장소 ruleset으로 제한할 수 있습니다.

Trusted Publishing은 OIDC `id-token: write`를 사용하므로 장기 API 키를 Secrets에 넣을
필요가 없습니다. [Publisher 등록](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)과
[배포 안내](https://docs.pypi.org/trusted-publishers/using-a-publisher/)를 참고하세요.
이 설정이 성공하기 전에는 실제 업로드·설치 검증이 완료됐다고 볼 수 없습니다.

## 정식 릴리스 태그 만들기

1. Word 직접 검사와 [마이그레이션](05-migration.md)·[검증 한계](11-validation.md)·
   라이선스·변경 기록 검토를 마칩니다.
2. 두 버전을 배포할 정식 버전으로 맞추고 `uv.lock`을 갱신합니다. 검증 후 master에 병합합니다.
3. 해당 master 커밋의 **TestPyPI candidate**에서 업로드·두 설치 job까지 모두 성공할 때까지
   기다립니다. 다른 커밋·PR·develop의 성공이나 로컬 wheel 검사만으로 대체하지 않습니다.
4. 검증한 커밋에 태그를 만들고 푸시합니다.

```sh
git switch master
git pull --ff-only
# 먼저 이 HEAD의 전체 TestPyPI candidate 실행이 성공했는지 확인하세요.
git tag -a v1.0.0 -m 'Release 1.0.0'
git push origin v1.0.0
```

`Publish to PyPI`는 태그·pyproject·`__version__`의 일치, 태그 커밋의 origin/master 포함,
정확히 같은 SHA의 이 저장소 `testpypi.yml` 실행 성공을 요구합니다.
전체 검사와 정식 wheel 설치를 다시 확인한 뒤 환경 승인을 거쳐 업로드합니다.
이후 GitHub Release 설명을 게시해도 다시 업로드하지 않습니다.

워크플로는 검증하지 않은 태그의 배포를 막습니다. 로컬 Git 태그 생성 자체를 막는 것은
아닙니다. 태그 푸시 권한은 저장소 규칙으로 관리합니다. TestPyPI 성공 전에 태그를 만들면
배포 검사가 실패하므로 검증 완료 후 재실행하세요. 이미 게시한 버전의 수정에는 새 버전을
사용합니다. TestPyPI 후보와 정식 PyPI 배포물은 같은 소스 커밋에서 서로 다른 버전
메타데이터로 빌드하며, 동일 바이너리를 그대로 승격하는 방식은 아닙니다.

## 핫픽스

master는 릴리스 계열로 유지하고 미완료 기능은 develop·release 브랜치에 둡니다.
핫픽스는 현재 master 릴리스 계열에서 분기합니다.

```sh
git switch master
git pull --ff-only
git switch -c hotfix/1.0.1
# 수정·회귀 사례를 추가하고 두 버전과 uv.lock을 1.0.1로 갱신합니다.
# master 대상 PR을 만들고 검사를 거쳐 병합합니다.
```

병합한 master 커밋의 TestPyPI 업로드·설치 검사 후 해당 커밋에 `v1.0.1`을 만듭니다.
master를 develop에 다시 병합하거나 back-merge PR을 만들어 수정이 다음 릴리스에도
남도록 하세요. develop이 이미 `1.1.0`을 목표로 한다면 버전·lock 충돌을 해결하면서
개발 중인 버전을 유지합니다. 이 흐름으로 미출시 기능과 핫픽스를 분리할 수 있습니다.

## 배포 전 남은 확인

로컬 테스트·독립 DOCX 정답·스키마·한영 문서·배포물 검사·워크플로 조건은 지원 범위를
검사합니다. 첫 정식 업로드 전에는 다음이 남습니다.

- Word 표시·편집·재저장. M17·M19·M20의 알려진 차이 포함
- 각 인덱스 소유권·Trusted Publisher·GitHub 환경 설정
- 실제 TestPyPI 업로드 및 해당 파일 설치 검사 성공
- 최종 버전·변경 기록과 과거 XSL 포함 사본의 처리
- 문서 호스팅을 위한 **Settings → Pages → Source: GitHub Actions** 활성화

Pages와 패키지 배포는 별개입니다. 워크플로 정의만으로 계정 설정이나 실제 원격 설치가
검증되지는 않습니다. 정식 릴리스 태그는 자동으로 생성하지 않습니다.

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
