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
    sentence = parser.convert("<p>A<math><mi>x</mi></math>B</p>")
    assert len(sentence.paragraphs) == 1
    block = MathmlToDocx(default_math_display="block").convert(
        "<math><mi>x</mi></math>"
    )
    assert block._element.xpath("//m:oMathPara/m:oMath")
    isotope = parser.parse_mathml(
        "<math><mmultiscripts><mi>C</mi><none/><none/><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts></math>"
    )
    assert isotope._element.xpath("//m:sPre/m:sub//m:t/text()") == ["6"]
    assert not isotope._element.xpath("//m:sSubSup")
    korean = parser.parse_html_string(
        '<p style="font-family:Malgun Gothic">한글 and English</p>'
    )
    assert korean._element.xpath("//w:rFonts/@w:eastAsia") == ["Malgun Gothic"]
    matrices = parser.parse_latex(
        r"\begin{pmatrix}a\end{pmatrix}\begin{pmatrix}b\end{pmatrix}"
    )
    assert len(matrices._element.xpath("//m:oMath/m:d")) == 2
    power = parser.parse_latex(r"(a+b)^2")
    assert power._element.xpath("//m:sSup/m:e/m:d/m:e/m:r/m:t/text()") == [
        "a",
        "+",
        "b",
    ]
    cases = parser.parse_latex(r"f(x)=\begin{cases}x&x>0\\0&x\leq0\end{cases}")
    assert cases._element.xpath("//m:d/m:dPr/m:begChr/@m:val") == ["{"]
    assert cases._element.xpath("//m:d/m:dPr/m:endChr/@m:val") == [""]
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
