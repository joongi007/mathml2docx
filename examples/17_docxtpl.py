"""17 docxtpl example."""

from docx import Document
from docxtpl import DocxTemplate

from mathml2docx import MathmlToDocx

from .support import OUTPUT

source = OUTPUT / "jinja_template.docx"
document = Document()
document.add_paragraph("Hello {{ name }}")
document.save(source)
template = DocxTemplate(source)
template.render({"name": "Alex"})
MathmlToDocx().add_html_to_document(
    "<h2>Added HTML section</h2><p>After Jinja rendering.</p>", template
)
output = OUTPUT / "17_docxtpl.docx"
template.save(output)
print(output)
