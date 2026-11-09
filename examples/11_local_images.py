"""11 local images example."""

from mathml2docx import MathmlToDocx

from .support import ROOT, save

parser = MathmlToDocx(img_src_base_path=ROOT / "assets")
document = parser.parse_html_string(
    '<h1>Local assets</h1><p><img src="swatch.png" width="120"></p>'
)
save(document, "11_local_images.docx")
