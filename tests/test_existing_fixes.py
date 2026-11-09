"""Verify fixes already present before the 1.0 migration using the legacy API."""

import base64
import tempfile
import unittest
from pathlib import Path

from mathml2docx import MathmlToDocx


class ExistingFixTests(unittest.TestCase):
    def test_base64_and_inline_image(self):
        data = base64.b64encode(Path("tests/dataset/testimg.png").read_bytes()).decode()
        doc = MathmlToDocx().parse_html_string(
            '<p>before<img src="data:image/png;base64,' + data + '">after</p>'
        )
        self.assertEqual(len(doc.inline_shapes), 1)
        self.assertEqual(len(doc.paragraphs), 1)

    def test_img_without_src(self):
        doc = MathmlToDocx().parse_html_string("<p>before<img>after</p>")
        self.assertIn("after", doc.paragraphs[0].text)

    def test_cell_leading_break(self):
        doc = MathmlToDocx().parse_html_string(
            "<table><tr><td><br>testing</td></tr></table>"
        )
        self.assertIn("testing", doc.tables[0].cell(0, 0).text)

    def test_encoding_and_paragraph_style(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.html"
            output = Path(tmp) / "output"
            source.write_text("<p>Índice 한글</p>", encoding="utf-8")
            parser = MathmlToDocx(paragraph_style="Quote")
            parser.parse_html_file(str(source), str(output), encoding="utf-8")
            from docx import Document

            doc = Document(str(output) + ".docx")
            self.assertEqual(doc.paragraphs[0].text, "Índice 한글")
            self.assertEqual(doc.paragraphs[0].style.name, "Quote")

    def test_nonempty_rowspan(self):
        html = '<table><tr><th>Name</th><td>Jill</td></tr><tr><th rowspan="2">Phone</th><td>555-1234</td></tr><tr><td>555-8745</td></tr></table>'
        table = MathmlToDocx().parse_html_string(html).tables[0]
        self.assertEqual(table.cell(2, 0).text, "Phone")
        self.assertEqual(table.cell(2, 1).text, "555-8745")

    def test_bold_italic_scripts(self):
        runs = (
            MathmlToDocx()
            .parse_html_string("<p><b>b</b><i>i</i><sup>s</sup><sub>s</sub></p>")
            .paragraphs[0]
            .runs
        )
        runs = [run for run in runs if run.text]
        self.assertTrue(runs[0].bold)
        self.assertTrue(runs[1].italic)
        self.assertTrue(runs[2].font.superscript)
        self.assertTrue(runs[3].font.subscript)
