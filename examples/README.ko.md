# 실행 예제

[English](README.md) · [한국어](README.ko.md) · [예제 목록](https://joongi007.github.io/mathml2docx/ko/examples/00-index/)

예제 목록에서 ZIP을 내려받아 압축을 푸세요. `examples/` 패키지와 공통 모듈, 필요한
자산이 들어 있습니다. `examples/` 폴더가 들어 있는 위치에서 아래 명령을 실행합니다.

```sh
python -m pip install "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
python -m examples.01_quickstart
# 예제 30개를 모두 생성:
python -m examples.run_all
```

PyPI 배포 패키지를 설치해 사용합니다. 일부 예제가 LaTeX를 사용하므로 전체 실행에는
Python 3.6.2 이상이 필요합니다. 라이브러리 core는 Python 3.6.0 이상을 지원합니다.
docxtpl은 17번 예제에서 사용합니다. 개별 선택 기능과 Python 3.6의 pip 설정은
[설치 안내](https://joongi007.github.io/mathml2docx/ko/01-getting-started/)를 참고하세요.

결과는 `examples/output/`에 저장됩니다. 패키지 내부의 상대 import가 동작하도록
`python -m`으로 실행하세요. 코드를 자신의 앱으로 옮길 때는 `.support`의 공통 함수를
자신의 경로와 `document.save(...)` 호출로 바꾸면 됩니다.

영한 문서는 같은 코드와 자산을 공유합니다. Word와 LibreOffice는 수식을 다르게
표시할 수 있습니다. [호환성과 검증](https://joongi007.github.io/mathml2docx/ko/11-validation/)을 참고하세요.
