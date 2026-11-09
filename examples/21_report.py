"""21 report example."""

from mathml2docx import MathmlToDocx, TableStyle

from .support import ROOT, save

parser = MathmlToDocx(table_style=TableStyle.GRID, img_src_base_path=ROOT / "assets")
document = parser.parse_html_string(
    (ROOT / "assets/report.html").read_text(encoding="utf-8")
)
save(document, "21_report.docx")
