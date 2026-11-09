# 실행 예제 모음

Python 실행 예제 22개를 문서 빌드에서 실제 실행해 DOCX로 만듭니다.

```sh
python -m pip install '.[latex,test]' -r requirements-examples.txt
python -m examples.run_all
```

모든 결과는 `examples/output/`에 저장됩니다. 개별 실행은 `python -m examples.01_quickstart`처럼 합니다.

[전체 예제 코드·자산 ZIP](../downloads/mathml2docx-examples.zip)

아래 PDF는 LibreOffice 7.3.7로 렌더링한 참조 결과입니다. Word 버전·글꼴에 따라 화면은 달라질 수 있습니다.

- [빠른 시작](01_quickstart.md): convert() 한 번으로 HTML을 저장하고 Document를 반환받습니다.
- [파일·인코딩·다국어](02_files_unicode.md): UTF-8 입력, 한글·일본어·악센트 문자와 정확한 출력 확장자를 다룹니다.
- [기존 문서와 표 셀](03_existing_document.md): 기존 Document에 내용을 추가하고 셀 안에 HTML을 삽입합니다.
- [글자 서식과 색상](04_inline_formatting.md): 굵기·기울임·밑줄·취소선·위아래 첨자·코드·반투명 색상 합성을 보여 줍니다.
- [CSS 스타일시트](05_stylesheets.md): style 태그, 외부 CSS 로더, 선택자·상속·important 우선순위를 함께 사용합니다.
- [Word 스타일과 클래스 매핑](06_word_styles.md): 공개 스타일 Enum과 사용자 정의 character style을 HTML class에 연결합니다.
- [문단 배치와 페이지 나누기](07_page_layout.md): 정렬·여백·들여쓰기·줄 간격과 페이지 나누기를 지정합니다.
- [표 병합과 중첩](08_tables.md): thead·tbody, rowspan·colspan, 셀 배경, 표 폭·테두리와 중첩 표를 조합합니다.
- [목록 번호와 중첩](09_lists.md): 시작 번호, li의 value, 독립 목록 재시작, 중첩 번호·글머리를 보여 줍니다.
- [인라인 base64 이미지](10_data_images.md): data URL 이미지를 글자 사이에 삽입하고 표시 폭을 지정합니다.
- [로컬 이미지](11_local_images.md): 명시한 기준 경로 아래의 이미지를 읽습니다. 기준 밖 경로는 허용하지 않습니다.
- [자산 로더와 이미지 직접 삽입](12_asset_loader.md): 논리 자산 ID를 bytes로 해석하고 BytesIO 이미지를 셀에 직접 추가합니다.
- [MathML 수식](13_mathml.md): 분수·위아래 첨자·n제곱근·울타리·행렬 및 문장 안의 편집 가능한 수식을 생성합니다.
- [LaTeX 수식](14_latex.md): 선택 의존성으로 합계·분수·제곱근·행렬을 Word 수식으로 변환합니다.
- [인라인 마커와 블록 교체](15_markers.md): 서식 run에 걸친 마커를 바꾸고 표 셀에 여러 블록을 삽입합니다.
- [북마크 교체](16_bookmarks.md): Word 북마크의 범위를 HTML로 교체하고 앞뒤 내용과 북마크를 보존합니다.
- [docxtpl 연동](17_docxtpl.md): Jinja 템플릿을 렌더링한 뒤 HTML 문단을 추가합니다.
- [옵션과 설정 복사](18_options.md): 이미지·표·수식·서식을 끄고 설정을 독립적으로 복사합니다.
- [서식 헬퍼](19_style_helpers.md): 대상 run과 paragraph에 CSS 문자열을 명시적으로 적용합니다.
- [링크와 앵커](20_links.md): 외부 링크, 문서 내부 링크, id·name 앵커와 href 없는 링크를 다룹니다.
- [복합 보고서](21_report.md): 스타일시트·이미지·병합 표·중첩 목록·수식·페이지 나누기를 한 문서에 조합합니다.
- [Markdown 연동](22_markdown.md): 제목·표·목록·코드와 ~~취소선~~을 선택 Markdown 프런트엔드로 변환합니다.
