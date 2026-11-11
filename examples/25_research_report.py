"""Distinct advanced MathML formulas inside a bilingual research-style report."""

from pathlib import Path

from mathml2docx import TableStyle, convert

from .advanced_math import CATALOG, source
from .support import save

sections = [
    """<style>
body {font-family:'Malgun Gothic';font-size:10pt;color:#1e293b}
h1,h2 {color:#17365d} h1 {font-size:20pt} h2 {font-size:14pt} .equation {text-align:center;margin-top:12pt;margin-bottom:12pt}
.note {background-color:#eef2ff} th {background-color:#dbeafe}
</style><h1>Advanced numerical methods / 고급 수치 해석</h1>
<p class="note">한글 설명과 mathematical notation in one report. Each numbered
formula is a different authored problem, rather than another placement of the same expression.</p>
<p><b>Review:</b> inspect nested fractions, complete matrix boundaries, derivative
roles, and line wrapping. <a href="https://example.com/methods">Method reference</a>.</p>"""
]
for index, entry in enumerate(e for e in CATALOG if e["format"] == "mathml"):
    sections.extend(
        [
            f"<h2>{entry['id']}. {entry['title']}</h2>",
            "<p><strong>가정과 해석:</strong> the expression below keeps each numerator, "
            "denominator, matrix cell and script editable. <em>Check the grouped arguments.</em></p>",
            '<p class="equation">' + source(entry) + "</p>",
            '<ol start="3"><li>분자·분모와 첨자의 역할을 확인합니다.</li>'
            "<li>Compare the expression with the original text input.</li></ol>",
        ]
    )
    if index % 2 == 0:
        sections.append(
            '<table><tr><th colspan="2">검토 기록 / Review record</th></tr>'
            '<tr><td rowspan="2">Assumptions</td><td><b>Finite dimensions</b> and positive parameters.</td></tr>'
            "<tr><td><table><tr><td>Nested note</td><td><i>Preserve the original cell order.</i></td></tr></table></td></tr>"
            '</table><p><img src="swatch.png" width="48"> <u>Reference swatch</u> and a caption.</p>'
        )
    if index in {2, 5, 8}:
        sections.append(
            '<p style="page-break-after:always">Section review complete.</p>'
        )
document = convert(
    "<html><body>" + "".join(sections) + "</body></html>",
    table_style=TableStyle.GRID,
    img_src_base_path=str(Path(__file__).resolve().parent / "assets"),
)
save(document, "25_research_report.docx")
