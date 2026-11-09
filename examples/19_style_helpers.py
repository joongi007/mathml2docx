"""19 style helpers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
paragraph = document.add_paragraph()
run = paragraph.add_run("Explicit targets")
parser = MathmlToDocx()
parser.add_styles_to_run(
    "color:navy;font-weight:bold;text-decoration:underline", run=run
)
parser.add_styles_to_paragraph("margin-left:1cm;text-align:right", paragraph=paragraph)
save(document, "19_style_helpers.docx")
