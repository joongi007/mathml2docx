"""Check an installed wheel from outside the source tree; compatible with 3.6."""

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from docx import Document

import mathml2docx
from mathml2docx import MathmlToDocx


def main():
    source = Path(__file__).resolve().parents[1] / "mathml2docx"
    package = Path(mathml2docx.__file__).resolve()
    if source == package.parent:
        raise RuntimeError("Smoke check must use an installed distribution, not source")
    parser = MathmlToDocx()
    doc = parser.parse_html_string(
        "<style>p {color:navy}</style><p>Wheel</p><math><mfrac><mn>1</mn><mn>2</mn></mfrac></math>"
    )
    assert str(doc.paragraphs[0].runs[0].font.color.rgb) == "000080"
    with BytesIO() as output:
        doc.save(output)
        output.seek(0)
        with ZipFile(output) as archive:
            assert b"oMath" in archive.read("word/document.xml")
    doc = Document()
    p = doc.add_paragraph()
    p.add_run("A {{co")
    p.add_run("ntent}} B")
    parser.replace_html(doc, "{{content}}", "<b>new</b>")
    assert doc.paragraphs[0].text == "A new B"
    assert parser.parse_latex(r"\sum_{i=1}^{n}i")._element.xpath("//m:limUpp")
    markdown = parser.parse_markdown("# Heading\n\n~~deleted~~")
    assert markdown.paragraphs[1].runs[0].font.strike
    with TemporaryDirectory() as tmp:
        target = Path(tmp) / "saved.docx"
        doc.save(str(target))
        assert Document(str(target)).paragraphs[0].text == "A new B"
    print("Installed wheel passed:", mathml2docx.__version__, package)


if __name__ == "__main__":
    main()
