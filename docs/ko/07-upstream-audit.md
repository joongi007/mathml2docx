# 원본 프로젝트 이슈 호환성

mathml2docx는 `pqzx/html2docx`에서 파생됐습니다. 이 기록은 원본 프로젝트의 이슈
49건(PR 제외, 열린 이슈와 닫힌 이슈)을 1.0 변환기의 동작과 연결합니다.
검토 스냅샷은 2026-11-09 기준이며 아래 표에서 재현 근거·수정 내용·입력별 한계를
확인할 수 있습니다. 사용 질문과 관리 요청은 변환기 결함과 구분합니다.
구조 검사와 문서 프로그램 표시 검사의 차이는 [검증 안내](11-validation.md)를 참고하세요.

## 기존 수정 검증

변경 전 HEAD(`89205f4`)의 패키지를 임시 경로로 복원해 `tests/test_existing_fixes.py`의 6개 테스트를 실행했습니다. base64/인라인 이미지, src 누락, 선행 br, UTF-8/문단 스타일, 내용이 있는 rowspan, 기본 글자 서식은 모두 통과했습니다. 동일 테스트를 새 엔진에서도 실행합니다.

## 기존 동작과 회귀 검사

`tests/test_regressions.py`의 9개 테스트 중 기존 코드에서 오류 4개와 실패 1개를 먼저 확인했습니다. 새 엔진에서는 통과합니다. 추가 공개 API·수식·보안·병합·목록·템플릿 검증은 `tests/test_v1.py`에 있습니다. XML 및 관계 검증이며 Word 화면의 시각적 검증은 아닙니다.

| 이슈 | 판정 | 근거·제약 |
| --- | --- | --- |
| [#1 failed to convert html table to docx](https://github.com/pqzx/html2docx/issues/1) | 검증 | tbody 및 중첩 표를 포함한 기존 데이터셋 통과. |
| [#2 Conversion of <ol><li>: No style with name 'List Number'](https://github.com/pqzx/html2docx/issues/2) | 수정 | 목록 번호 XML 직접 생성으로 List Number 스타일 존재 여부와 무관하게 동작. |
| [#3 Errno 36] File name too long: 'data:image/png;base64,iVBOR](https://github.com/pqzx/html2docx/issues/3) | 기존 수정 검증 | base64 이미지 처리. |
| [#4 Does it support css styles?](https://github.com/pqzx/html2docx/issues/4) | 지원 구현 | style 태그·정적 CSS 선택자·specificity·상속·important 및 명시적 외부 CSS 로더 구현. 대응 Word 속성 범위는 사용법 표에 명시. |
| [#6 IndexError: list index out of range](https://github.com/pqzx/html2docx/issues/6) | 원본 입력 검증 | 원문 FILE.txt를 변환·저장하고 LibreOffice PDF 렌더링 완료. 표 데이터는 병합 회귀 테스트와 함께 검증. |
| [#10 Issue with float margins and named (vs RGB) colors](https://github.com/pqzx/html2docx/issues/10) | 수정·검증 | 실수 길이와 named color 처리. |
| [#12 <img src="data:image/png;base64,xxxx==>](https://github.com/pqzx/html2docx/issues/12) | 기존 수정 검증 | base64 PNG 이미지 처리. |
| [#13 ValueError: invalid literal for int() with base 10: 'r'](https://github.com/pqzx/html2docx/issues/13) | 검증 | hr과 제목 태그를 별도로 처리. 기존 hr 테스트도 통과. |
| [#14 Renders as more or less plain text](https://github.com/pqzx/html2docx/issues/14) | 원본 입력 검증 | 이슈 본문의 Qt HTML 5,660자를 변환·렌더링. 글꼴·크기·색상·굵기 보존. p를 글꼴 크기만 보고 Heading으로 추측하지는 않음. |
| [#15 HTML Tag <a href=...](https://github.com/pqzx/html2docx/issues/15) | 검증 | 링크 텍스트와 관계를 DOCX 저장 후 재오픈해 검증. 구버전 python-docx의 paragraph.text 표시는 별개. |
| [#21 Color conversion not done when a text is in bold or italic](https://github.com/pqzx/html2docx/issues/21) | 수정 | bold/italic 태그에도 CSS 색상 상속·적용. |
| [#22 Tweak to handle links without href](https://github.com/pqzx/html2docx/issues/22) | 수정 | href 없는 링크의 텍스트 유지. |
| [#25 Create document from Word template](https://github.com/pqzx/html2docx/issues/25) | 기능 구현·검증 | 기존 Word 템플릿, 여러 run의 인라인 마커, 문단 간 북마크 범위 교체 지원. 앞뒤 run 서식과 북마크 보존 테스트. |
| [#27 UnicodeDecodeError:   how to convert html documents with accented characters?](https://github.com/pqzx/html2docx/issues/27) | 기존 수정 검증 | 비ASCII UTF-8 파일 읽기. |
| [#28 Code breaks for base64 image source, saying OSError: [Errno 36] File name too long](https://github.com/pqzx/html2docx/issues/28) | 기존 수정 검증 | base64 이미지 처리. |
| [#30 <title> attribute should be rendered with the MS Word "Title" style](https://github.com/pqzx/html2docx/issues/30) | 기능 추가 | title을 Word Title 문단으로 처리. |
| [#31 Addin page breaks?](https://github.com/pqzx/html2docx/issues/31) | 기능 추가 | page-break-before/after 및 break-before/after. |
| [#32 parse_dict_string raising excemptions in edge cases](https://github.com/pqzx/html2docx/issues/32) | 수정 | tinycss2 파서로 URL의 콜론·따옴표·공백 보존. |
| [#33 Tab_stops](https://github.com/pqzx/html2docx/issues/33) | 지원·예제 | pre 탭 보존 검증. Word 스타일에서 탭 정지·점선 리더를 설정하는 실행 코드를 작업별 사용법에 제공. |
| [#35 Suggestion for HTML class to Word style mapping](https://github.com/pqzx/html2docx/issues/35) | 기능 추가 | p class -> Quote 매핑 검증; 인라인 class는 character style 이름 사용. |
| [#36 Add support for DocxTemplate fom docxtpl package](https://github.com/pqzx/html2docx/issues/36) | 기능 구현·검증 | 실제 docxtpl Jinja 치환 후 HTML 추가·저장·재오픈 검증. 렌더링한 내용을 get_docx 재초기화로 잃던 추가 결함도 수정. |
| [#37 'HtmlToDocx' object has no attribute 'run'](https://github.com/pqzx/html2docx/issues/37) | 구조 수정·검증 | 파서의 공유 run 상태 의존을 제거. 선행 br, 이미지, 링크, 빈 입력·셀 경로를 회귀 테스트. 원문 입력은 공개되지 않아 동일 입력 비교는 불가. |
| [#38 Getting IndexError: list index out of range when parsing wikipedia page](https://github.com/pqzx/html2docx/issues/38) | 현재 실제 입력 검증 | 동일 Wikipedia URL의 현재 HTML 2,481,297바이트에서 표 28개·문단 626개 생성 및 PDF 렌더링. 2022년 스냅샷 자체는 없음. |
| [#40 Nested Ordered list not working correctly](https://github.com/pqzx/html2docx/issues/40) | 원본 입력 검증 | 원문 첨부 HTML로 PDF 렌더링 완료. 시작 번호·재시작·중첩 깊이·li value 및 번호 뒤 간격을 예제로 검증. |
| [#41 Add the ability to make bold, italics and Underline. Also, can you look into adding superscripts and subscripts?](https://github.com/pqzx/html2docx/issues/41) | 기존 수정 검증 | b/i/sup/sub 서식 검증. |
| [#42 Background Color is Not working](https://github.com/pqzx/html2docx/issues/42) | 수정 | 실제 RGB 배경색을 w:shd fill로 기록. |
| [#43 table_style = 'TableGrid'](https://github.com/pqzx/html2docx/issues/43) | 수정 | TableGrid 별칭 및 공개 TableStyle.GRID 제공. |
| [#44 Converting block level elements like <div> into paragraphs](https://github.com/pqzx/html2docx/issues/44) | 수정 | div/section 등 블록을 문단으로 처리. |
| [#46 Add classes with specific styles](https://github.com/pqzx/html2docx/issues/46) | 기능 추가 | 태그·class별 Word style_map. |
| [#47 Release Latest Version, so we can use paragraph_style support](https://github.com/pqzx/html2docx/issues/47) | 배포 준비 완료 | 1.0.0 wheel·sdist 생성 및 설치 검증, 문단 스타일 지원. upstream PyPI 프로젝트 게시 권한은 이 저장소 변경으로 확보되지 않으며 실제 게시는 별도 작업. |
| [#48 Unable to convert html with rowspan to docx correctly](https://github.com/pqzx/html2docx/issues/48) | 기존 수정 검증·보강 | Phone 행 병합은 기존 코드 통과. 새 코드는 빈 셀 병합까지 검증. |
| [#49 margin handler cannot handle percentages](https://github.com/pqzx/html2docx/issues/49) | 수정 | %와 실수 길이 처리; %는 문서 본문 가용 폭 기준. |
| [#50 Including tables](https://github.com/pqzx/html2docx/issues/50) | 검토 | 보고자가 잘못된 HTML로 철회. 추가 재현 요구 없음. |
| [#51 "IndexError: list index out of range" when using colspan attribute](https://github.com/pqzx/html2docx/issues/51) | 수정 | colspan을 반영해 열 수 계산; 빈 병합 셀도 위치 추적. |
| [#52 How can I render HTML-file content to specific tag/word into a template.docx file (word replacement)?](https://github.com/pqzx/html2docx/issues/52) | 기능 구현·검증 | 문장 중간·여러 run·표 셀의 마커, 단일·다중 문단 북마크를 HTML로 교체. 삽입 링크·이미지·수식의 문서 관계와 앞뒤 내용 보존. |
| [#54 "IndexError: list index out of range" when using rowspan attribute](https://github.com/pqzx/html2docx/issues/54) | 수정 | 본문의 Country/Dhaka/Sylhet 예제로 병합 위치와 텍스트 검증. |
| [#55 'gbk' codec can't decode byte 0xac in position 1024: illegal multibyte sequence](https://github.com/pqzx/html2docx/issues/55) | 기존 수정 검증 | 명시적 UTF-8 파일 읽기 및 encoding 인자. |
| [#57 Poor Performance for Large Tables](https://github.com/pqzx/html2docx/issues/57) | 수정·측정 | 표 셀 배열을 한 번 생성; 반복 Table.cell 호출 제거. 아래 측정 참고. |
| [#60 img without src will crash](https://github.com/pqzx/html2docx/issues/60) | 기존 수정 검증 | src 없는 img가 예외 없이 처리됨. |
| [#61 ImportError: cannot import name 'OxmlElement' from 'docx.oxml'](https://github.com/pqzx/html2docx/issues/61) | 검증 | 지원 의존성 범위에서 import 및 문서 생성 검증; 모든 과거 버전 조합을 보장하지 않음. |
| [#62 parser crash with a tag  without href](https://github.com/pqzx/html2docx/issues/62) | 수정 | href 없는 a의 텍스트 보존. |
| [#66 [bug] tables containing a <td> whose first child is <br> results in a crash](https://github.com/pqzx/html2docx/issues/66) | 기존 수정 검증 | 셀 첫 자식 br 뒤 텍스트 유지. |
| [#67 handling base64 image](https://github.com/pqzx/html2docx/issues/67) | 기존 수정 검증 | data URL PNG를 실제 DOCX 이미지로 변환. |
| [#68 Underline not converting into docx](https://github.com/pqzx/html2docx/issues/68) | 수정 | CSS text-decoration:underline 지원. |
| [#70 ValueError: invalid literal for int() with base 10: '0.88'](https://github.com/pqzx/html2docx/issues/70) | 수정·검증 | RGBA 소수 알파 예외 제거 및 상위 배경색과 실제 RGB 합성. 빨강 50%와 파랑 배경의 보라색 결과를 검증. |
| [#71 Images are not positioned correctly in the resulting DOCX file](https://github.com/pqzx/html2docx/issues/71) | 원본 이미지 포함 검증 | 원문 HTML의 공개 이미지 6개를 명시적 로더로 읽어 DOCX에 삽입하고 PDF 렌더링. 인라인 배치·CSS 크기와 앞뒤 텍스트 보존을 별도 회귀 테스트. |
| [#74 Issue with Ordered List Numbering and Strikethrough Rendering in DOCX](https://github.com/pqzx/html2docx/issues/74) | 수정·프런트엔드 추가 | 목록별 번호 재시작. parse_markdown()에서 표·코드·~~취소선~~ 기본 지원. 코드 안의 ~~ 보존과 실제 Word 취소선 속성을 검증. |
| [#75 I continued this project on other repo](https://github.com/pqzx/html2docx/issues/75) | 안내 | 후속 프로젝트 소개로 제품 결함 아님. |
| [#78 Security: please enable private vulnerability reporting](https://github.com/pqzx/html2docx/issues/78) | 코드 수정·외부 조치 구분 | 변환기의 암묵적 HTTP·CSS 로딩 제거 및 로컬 기준 경로 제한 검증. 명시적 로더만 허용. upstream Private Vulnerability Reporting 설정 변경은 소유자 권한 필요. |

## 표 성능 측정

같은 Python 3.14 환경에서 300행×3열의 단순 텍스트 표를 1회씩 변환했습니다.
변경 전 10.128초, 변경 후 0.057초였습니다. HTML 구성·환경에 따라 결과는 달라집니다.
이 수치는 단일 측정이며 성능 보장이나 모든 종류의 병합 표에 대한 결과는 아닙니다.

## 추가 검증과 실행 예제

- `tests/test_extended.py`: CSS 선택자·우선순위·상속, 상대 글자 크기, RGBA 합성, 인라인 마커·북마크, 이미지 보존, DOCTYPE 및 중첩 p 처리.
- `tests/test_examples.py`: 예제 30개를 별도 프로세스로 실행하고 DOCX를 다시 열어 실제 표·수식·링크·마커·템플릿 결과를 검증.
- [실행 예제 30개](examples/00-index.md): 전체 코드·입력 HTML·생성 DOCX·LibreOffice PDF.
- LibreOffice 24.2.7.2에서 예제 30개의 수식 224개 가져오기와 PDF 출력을 검사했습니다. 앞선 검사에서는 확보한 원본 이슈 입력도 렌더링했습니다. 보고서·목록·수식 등 주요 화면을 별도로 확인했습니다.
- Qt HTML의 글꼴 크기만으로 제목 의미를 자동 추정하지는 않습니다. CSS 서식 보존과 명시적인 제목으로 처리하며, Markdown은 선택 프런트엔드로 지원합니다.

추가 CSS 지원 후 같은 300행×3열 입력의 재측정값은 0.089초였습니다(1회 측정).
