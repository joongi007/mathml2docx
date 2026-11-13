# Combined report

Combine stylesheets, images, merged tables, nested lists, equations, and page breaks.

## Run

Extract the [example bundle](../downloads/mathml2docx-examples.zip), install the [example dependencies](00-index.md), and run this command from the folder containing `examples/`:

```sh
python -m examples.21_report
```

[Generated DOCX](../downloads/examples/21_report.docx)

[Reference PDF](../assets/previews/21_report.pdf)

## Complete source

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

## Input HTML

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
