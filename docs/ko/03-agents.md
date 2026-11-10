# AI와 스킬

## 배포용 스킬

[mathml2docx 스킬 ZIP](downloads/mathml2docx-skill.zip)을 내려받아 압축을 풀면
`mathml2docx/SKILL.md`와 변환 스크립트가 들어 있습니다. 사용하는 에이전트가 지원하는
스킬 디렉터리에 `mathml2docx` 폴더를 넣으세요. 라이브러리는 별도로 설치해야 합니다.

저장소에서는 `skills/mathml2docx/`가 스킬 원본입니다. 사용자 요청 예시:

> mathml2docx 스킬로 input.html의 수식을 유지해서 output.docx로 변환해 줘.

스크립트를 직접 사용할 수도 있습니다. 출력 파일이 이미 있으면 덮어쓰지 않습니다.
`--images`를 지정한 경우에만 이미지 처리가 켜집니다.

```sh
python skills/mathml2docx/scripts/convert.py input.html output.docx
```

## 기계가 읽는 문서

- [llms.txt](llms.txt): 문서 목록과 진입점
- [llms-full.txt](llms-full.txt): 현재 빌드의 문서 본문 모음

두 파일과 스킬 ZIP은 문서 빌드마다 원본에서 생성합니다.
문서 내용을 AI 도구의 참고 자료로 전달하거나, 문서 수집기가 읽도록 사용할 수 있습니다.

## MCP와의 관계

이 배포에는 MCP 서버가 포함되지 않습니다. 정적 GitHub Pages는 문서와 다운로드 파일을
제공하며 MCP의 초기화, 도구 호출, 리소스 조회 요청을 처리하지 않습니다.
문서를 MCP로 제공하려면 별도 MCP 서버에서 문서를 리소스로 노출해야 합니다.
실제 파일 변환은 Python 실행 환경에서 라이브러리나 스킬 스크립트가 담당합니다.
