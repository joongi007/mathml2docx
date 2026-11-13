# 복합 보고서

스타일시트·이미지·병합 표·중첩 목록·수식·페이지 나누기를 한 문서에 조합합니다.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/21_report.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/21_report.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/21_report.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/21_report.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.21_report
```

[생성된 DOCX](../downloads/examples/21_report.docx)

[참조 PDF](../assets/previews/21_report.pdf)

## 전체 코드

```python
"""21 report example."""

from mathml2docx import MathmlToDocx, TableStyle

from .support import ROOT, save

parser = MathmlToDocx(table_style=TableStyle.GRID, img_src_base_path=ROOT / "assets")
document = parser.parse_html_string(
    (ROOT / "assets/report.html").read_text(encoding="utf-8")
)
save(document, "21_report.docx")
```

## 입력 HTML

```html
<!doctype html>
<html><head><title>Research report</title><style>
body {font-family:DejaVu Sans;font-size:11pt;color:#1e293b}
h1,h2 {color:#164e63} .summary {background-color:#e0f2fe;padding:8px}
th {background-color:#164e63;color:white} .number {text-align:right}
table {width:100%;border:1px solid #164e63} .page {page-break-before:always}
</style></head><body>
<h1 id="overview">Experiment overview</h1><p class="summary">A mixed document with <strong>HTML formatting</strong>, a local image, tables, lists and editable equations.</p>
<p>Color key: <img src="swatch.png" width="120"> inline with text.</p>
<h2>Method</h2><ol><li>Collect samples<ul><li>Control group</li><li>Test group</li></ul></li><li>Measure results</li></ol>
<table><thead><tr><th rowspan="2">Group</th><th colspan="2">Measurements</th></tr><tr><th>Initial</th><th>Final</th></tr></thead><tbody><tr><td>Control</td><td class="number">12</td><td class="number">15</td></tr><tr><td>Test</td><td class="number">12</td><td class="number">24</td></tr></tbody></table>
<p>Formula: <math display="inline"><mi>r</mi><mo>=</mo><mfrac><mrow><mi>final</mi><mo>−</mo><mi>initial</mi></mrow><mi>initial</mi></mfrac></math>.</p>
<h2 class="page">Discussion</h2><p style="margin-left:5%;line-height:150%">The test group improved more than the control group.</p>
<blockquote><span style="background-color:rgba(245,158,11,.25)">Interpretation requires more samples.</span></blockquote>
<p><a href="#overview">Return to overview</a> · <a href="https://example.com">Reference</a></p>
<pre>rate = (final - initial) / initial</pre><hr><p>End of report.</p>
</body></html>

```
