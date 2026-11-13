# 인라인 base64 이미지

data URL 이미지를 글자 사이에 삽입하고 표시 폭을 지정합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/10_data_images.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/10_data_images.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/10_data_images.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/10_data_images.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.10_data_images
```

[생성된 DOCX](../downloads/examples/10_data_images.docx)

[참조 PDF](../assets/previews/10_data_images.pdf)

## 전체 코드

```python
"""10 data images example."""

import base64

from mathml2docx import convert

from .support import ROOT, save

encoded = base64.b64encode((ROOT / "assets/swatch.png").read_bytes()).decode()
document = convert(
    '<p>Before <img alt="color swatch" src="data:image/png;base64,'
    + encoded
    + '" style="width:96px"> after</p>'
)
save(document, "10_data_images.docx")
```
