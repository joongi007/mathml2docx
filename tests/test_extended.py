"""Remaining upstream issues: CSS, transparency, exact template insertion."""

import unittest
from io import BytesIO

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from mathml2docx import MathmlToDocx, convert


def bookmark(p, name, first, selected, last):
    p.add_run(first).bold = True
    a = OxmlElement("w:bookmarkStart")
    a.set(qn("w:id"), "42")
    a.set(qn("w:name"), name)
    p._p.append(a)
    p.add_run(selected)
    b = OxmlElement("w:bookmarkEnd")
    b.set(qn("w:id"), "42")
    p._p.append(b)
    p.add_run(last).italic = True


class StylesheetTests(unittest.TestCase):
    def test_specificity_important_inheritance(self):
        doc = convert("""<style>p {color:blue} .notice {color:green !important}
        #message {color:black} p > strong {text-decoration:underline}</style>
        <p id="message" class="notice" style="color:red">A<strong>B</strong></p>""")
        runs = doc.paragraphs[0].runs
        self.assertEqual(str(runs[0].font.color.rgb), "008000")
        self.assertEqual(str(runs[1].font.color.rgb), "008000")
        self.assertTrue(runs[1].underline)
        self.assertTrue(runs[1].bold)

    def test_inline_important_and_external_explicit(self):
        calls = []

        def loader(path):
            calls.append(path)
            return ".item { color:red !important; font-size:18pt }"

        doc = convert(
            '<link rel="stylesheet" href="theme.css"><p class="item" style="color:blue !important">x</p>',
            stylesheet_loader=loader,
        )
        self.assertEqual(calls, ["theme.css"])
        run = doc.paragraphs[0].runs[0]
        self.assertEqual(str(run.font.color.rgb), "0000FF")
        self.assertEqual(run.font.size.pt, 18)

    def test_selector_combinators_and_order(self):
        doc = convert(
            "<style>section p:first-child {color:red} section p + p {color:blue} p {font-weight:bold}</style><section><p>A</p><p>B</p></section>"
        )
        runs = [p.runs[0] for p in doc.paragraphs if p.runs]
        self.assertEqual([str(r.font.color.rgb) for r in runs], ["FF0000", "0000FF"])

    def test_alpha_composite(self):
        doc = convert(
            '<div style="background-color:blue"><span style="background-color:rgba(255,0,0,0.5)"><b>x</b></span></div>'
        )
        self.assertIn("800080", doc._element.xml)

    def test_margin_shorthand_not_inherited(self):
        doc = convert('<section style="margin:1in"><p>x</p></section>')
        p = [p for p in doc.paragraphs if p.text][0]
        self.assertIsNone(p.paragraph_format.left_indent)

    def test_no_implicit_css_loading(self):
        from unittest.mock import patch

        with patch(
            "urllib.request.urlopen", side_effect=AssertionError("unexpected fetch")
        ):
            self.assertEqual(
                convert('<link rel="stylesheet" href="http://127.0.0.1"><p>x</p>')
                .paragraphs[0]
                .text,
                "x",
            )


class TemplateTests(unittest.TestCase):
    def test_marker_across_runs(self):
        doc = Document()
        p = doc.add_paragraph()
        p.add_run("before {{co").bold = True
        p.add_run("ntent}} after").italic = True
        MathmlToDocx().replace_html(doc, "{{content}}", "<u>inserted</u>")
        self.assertEqual(doc.paragraphs[0].text, "before inserted after")
        runs = [r for r in doc.paragraphs[0].runs if r.text]
        self.assertTrue(runs[0].bold)
        self.assertTrue(runs[1].underline)
        self.assertTrue(runs[2].italic)

    def test_marker_in_cell_with_table(self):
        doc = Document()
        cell = doc.add_table(1, 1).cell(0, 0)
        cell.text = "before {{x}} after"
        MathmlToDocx().replace_html(
            doc, "{{x}}", "<table><tr><td>inner</td></tr></table>"
        )
        self.assertEqual(cell.tables[0].cell(0, 0).text, "inner")
        self.assertEqual([p.text for p in cell.paragraphs], ["before ", " after"])

    def test_bookmark_inline(self):
        doc = Document()
        bookmark(doc.add_paragraph(), "content", "before ", "old", " after")
        MathmlToDocx().replace_bookmark(doc, "content", "<b>new</b>")
        self.assertEqual(doc.paragraphs[0].text, "before new after")
        self.assertEqual(len(doc._element.xpath("//w:bookmarkStart")), 1)
        self.assertEqual(len(doc._element.xpath("//w:bookmarkEnd")), 1)
        with BytesIO() as out:
            doc.save(out)
            out.seek(0)
            self.assertEqual(Document(out).paragraphs[0].text, "before new after")
        MathmlToDocx().replace_bookmark(doc, "content", "<i>again</i>")
        self.assertEqual(doc.paragraphs[0].text, "before again after")

    def test_bookmark_across_paragraphs(self):
        doc = Document()
        first = doc.add_paragraph("before ")
        a = OxmlElement("w:bookmarkStart")
        a.set(qn("w:id"), "1")
        a.set(qn("w:name"), "range")
        first._p.append(a)
        first.add_run("old")
        last = doc.add_paragraph("discard")
        b = OxmlElement("w:bookmarkEnd")
        b.set(qn("w:id"), "1")
        last._p.append(b)
        last.add_run(" after")
        MathmlToDocx().replace_bookmark(doc, "range", "<h2>new</h2><p>body</p>")
        self.assertEqual(
            [p.text for p in doc.paragraphs], ["before ", "new", "body", " after"]
        )
        self.assertEqual(doc.paragraphs[1].style.name, "Heading 2")

    def test_invalid_html_does_not_remove_marker(self):
        doc = Document()
        doc.add_paragraph("{{x}}")
        with self.assertRaises(ValueError):
            MathmlToDocx().replace_html(doc, "{{x}}", "<math><unknown/></math>")
        self.assertEqual([p.text for p in doc.paragraphs], ["{{x}}"])


class FullDocumentTests(unittest.TestCase):
    def test_doctype_is_not_rendered(self):
        doc = convert("<!doctype html><html><body><p>Only content</p></body></html>")
        self.assertEqual([p.text for p in doc.paragraphs], ["Only content"])

    def test_stylesheet_cell_alignment_and_fill(self):
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = convert(
            "<style>td {text-align:right;background-color:navy}</style><table><tr><td>12</td></tr></table>"
        )
        cell = doc.tables[0].cell(0, 0)
        self.assertEqual(cell.paragraphs[0].alignment, WD_ALIGN_PARAGRAPH.RIGHT)
        self.assertIn("000080", cell._tc.xml)

    def test_font_relative_size(self):
        doc = convert(
            '<p style="font-size:10pt"><span style="font-size:150%">large</span></p>'
        )
        self.assertEqual(doc.paragraphs[0].runs[0].font.size.pt, 15)


class PreservationTests(unittest.TestCase):
    def test_inline_marker_preserves_pictures(self):
        from pathlib import Path

        doc = Document()
        p = doc.add_paragraph("before ")
        p.add_run().add_picture(str(Path("examples/assets/swatch.png")))
        p.add_run("{{name}}")
        p.add_run().add_picture(str(Path("examples/assets/swatch.png")))
        p.add_run(" after")
        MathmlToDocx().replace_html(doc, "{{name}}", "<b>new</b>")
        self.assertEqual(len(doc.inline_shapes), 2)
        self.assertEqual(doc.paragraphs[0].text, "before new after")

    def test_nested_paragraph_repair(self):
        doc = convert('<p><p>before<img src="missing">after</p></p>')
        self.assertEqual(len(doc.paragraphs), 1)
        self.assertIn("before", doc.paragraphs[0].text)


class MarkdownTests(unittest.TestCase):
    def test_markdown_strike_tables_and_code(self):
        doc = MathmlToDocx().parse_markdown(
            "# Title\n\n~~deleted~~ and `~~literal~~`\n\n|A|B|\n|-|-|\n|1|2|"
        )
        self.assertEqual(doc.paragraphs[0].style.name, "Heading 1")
        runs = [r for r in doc.paragraphs[1].runs if r.text]
        self.assertTrue(runs[0].font.strike)
        self.assertIn("~~literal~~", doc.paragraphs[1].text)
        self.assertFalse(runs[-1].font.strike)
        self.assertEqual(doc.tables[0].cell(1, 1).text, "2")
