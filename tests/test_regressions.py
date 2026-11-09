"""Public behavior regressions from pqzx/html2docx issues."""

import unittest

from mathml2docx import MathmlToDocx


class RegressionTests(unittest.TestCase):
    def parse(self, html):
        return MathmlToDocx(images=False).parse_html_string(html)

    def test_link_without_href(self):
        self.assertEqual(
            self.parse('<p>a <a name="x">anchor</a> b</p>').paragraphs[0].text,
            "a anchor b",
        )

    def test_background_rgba(self):
        doc = self.parse('<span style="background-color:rgba(255,0,0,0.88)">x</span>')
        self.assertIn("FF1F1F", doc._element.xml)

    def test_css_on_bold(self):
        run = (
            self.parse('<b style="color:#ff0000;text-decoration:underline">x</b>')
            .paragraphs[0]
            .runs[0]
        )
        self.assertTrue(run.bold)
        self.assertTrue(run.underline)
        self.assertEqual(str(run.font.color.rgb), "FF0000")

    def test_whitespace(self):
        self.assertEqual(
            self.parse("<p>Hello <b>bold</b> world</p>").paragraphs[0].text,
            "Hello bold world",
        )

    def test_spans(self):
        doc = self.parse(
            '<table><tr><td colspan="2"></td></tr><tr><td>A</td><td>B</td></tr></table>'
        )
        self.assertEqual(len(doc.tables[0].columns), 2)
        self.assertEqual(doc.tables[0].cell(1, 1).text, "B")

    def test_percent_margin(self):
        self.assertEqual(
            self.parse('<p style="margin-left:4%">x</p>').paragraphs[0].text, "x"
        )

    def test_missing_image(self):
        doc = MathmlToDocx().parse_html_string("<p>A<img>B</p>")
        self.assertIn("B", doc.paragraphs[0].text)

    def test_first_break(self):
        self.assertIn(
            "testing",
            self.parse("<table><tr><td><br>testing</td></tr></table>")
            .tables[0]
            .cell(0, 0)
            .text,
        )

    def test_css_url(self):
        self.assertEqual(
            self.parse('<p style="background-image:url(https://example.com/a)">x</p>')
            .paragraphs[0]
            .text,
            "x",
        )


if __name__ == "__main__":
    unittest.main()
