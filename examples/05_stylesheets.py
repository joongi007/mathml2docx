"""05 stylesheets example."""

from mathml2docx import MathmlToDocx

from .support import save

assets = {
    "theme.css": ".notice {color:teal;font-size:16pt} .notice strong {color:purple}"
}
parser = MathmlToDocx(
    stylesheet_loader=assets.__getitem__, stylesheet="h1 {color:navy}"
)
document = parser.parse_html_string("""<link rel="stylesheet" href="theme.css">
<style>#main {color:red} .notice {color:green !important}</style>
<h1>CSS cascade</h1><p id="main" class="notice" style="color:orange">Important wins. <strong>Nested selector</strong></p>""")
save(document, "05_stylesheets.docx")
