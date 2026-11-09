# 기존 XSL 출처 조사

조사일: 2026-11-09. 대상은 이전 버전에 포함된 `mathml2docx/MML2OMML.XSL`입니다.

- 도입 커밋: `0c85e595475bc181be8512dbf398dc02d0e13511` (2024-01-23).
- 커밋 메시지와 파일에는 내려받은 URL, 저작권자, 재배포 허락이 기록되어 있지 않습니다.
- 파일 크기: 155,527바이트.
- SHA-256: `5558e69d8bd6534927c4176bd5d5032d0d4bdc17bdaab7de580ca41e996a609b`.
- 조사 시점 [AbiWord의 동명 파일](https://github.com/AbiWord/abiword/blob/master/plugins/openxml/omml_xslt/mml2omml.xsl)과 바이트 단위로 동일했습니다.

이 일치는 동일한 사본이 공개되어 있다는 증거입니다. 사용자가 실제로 복사한 사이트나
최초 저작자를 특정하는 증거, 재배포 허락의 증거는 아닙니다. 저장소의 MIT 고지만으로
제삼자 파일의 권한까지 확보했다고 판단하지 않습니다.
[Microsoft의 일반 재배포 정책](https://www.microsoft.com/en-us/legal/intellectualproperty/copyright/permissions)은
함께 제공되는 약관의 명시적 허용을 요구하지만, 그 일반 정책만으로 이 사본에 적용되는
개별 라이선스나 법적 위반 여부를 확정하지는 않습니다.

1.0.0에서는 이 파일과 로딩 코드를 제거했습니다. 새 `mathml2docx/math.py`는 Python에서
직접 OMML 노드를 구성하며 XSL 코드나 템플릿을 옮겨 쓰지 않았습니다.
LaTeX의 선택 의존성 [latex2mathml](https://github.com/roniemartinez/latex2mathml)은
자체 MIT 라이선스로 배포되며 소스를 이 패키지에 복사하지 않습니다.

이 변경은 기존 Git 이력과 이미 배포된 0.x 패키지를 변경하지 않습니다.
과거 배포본의 처리나 재배포 허락 여부에 대한 최종 판단은 별도 과제입니다.
