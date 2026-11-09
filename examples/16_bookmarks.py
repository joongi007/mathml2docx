"""16 bookmarks example."""

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx

from .support import save

document = Document()
p = document.add_paragraph("Before ")
start = OxmlElement("w:bookmarkStart")
start.set(qn("w:id"), "1")
start.set(qn("w:name"), "result")
p._p.append(start)
p.add_run("replace this")
end = OxmlElement("w:bookmarkEnd")
end.set(qn("w:id"), "1")
p._p.append(end)
p.add_run(" after.")
MathmlToDocx().replace_bookmark(document, "result", "<b>new result</b>")
save(document, "16_bookmarks.docx")
