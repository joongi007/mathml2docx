# 자산 로더와 이미지 직접 삽입

논리 자산 ID를 bytes로 해석하고 BytesIO 이미지를 셀에 직접 추가합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다. 이 예제는 Word 객체로 직접 만든 내용도 포함합니다. 브라우저에는 삽입한 HTML/MathML 조각만 호출 순서대로 표시하며, PDF에는 주변 Word 문서와 해당 스타일도 포함합니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/12_asset_loader.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/12_asset_loader.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/12_asset_loader.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/12_asset_loader.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.12_asset_loader
```

[생성된 DOCX](../downloads/examples/12_asset_loader.docx)

[참조 PDF](../assets/previews/12_asset_loader.pdf)

## 전체 코드

```python
"""12 asset loader example."""

from io import BytesIO

from mathml2docx import MathmlToDocx

from .support import ROOT, save

# Resolve allowed logical asset IDs. No network access or arbitrary file paths.
assets = {"asset:logo": (ROOT / "assets/swatch.png").read_bytes()}
parser = MathmlToDocx(image_loader=assets.__getitem__)
document = parser.parse_html_string(
    '<p>Asset <img src="asset:logo" width="80"> inline</p>'
)
cell = document.add_table(1, 1).cell(0, 0)
parser.add_image_to_cell(cell, BytesIO(assets["asset:logo"]))
save(document, "12_asset_loader.docx")
```
