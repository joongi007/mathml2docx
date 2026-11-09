"""15 markers example."""

from docx import Document

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph()
p.add_run("Dear {{na").bold = True
p.add_run("me}}, welcome.").italic = True
cell = document.add_table(1, 1).cell(0, 0)
cell.text = "{{table_content}}"
parser = MathmlToDocx()
parser.replace_html(document, "{{name}}", '<span style="color:teal">Alex</span>')
parser.replace_html(
    document,
    "{{table_content}}",
    "<h2>Inserted blocks</h2><ul><li>First</li><li>Second</li></ul>",
)
save(document, "15_markers.docx")
