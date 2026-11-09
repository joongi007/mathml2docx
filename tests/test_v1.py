import base64
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from docx import Document

from mathml2docx import (
    MathmlToDocx,
    ParagraphStyle,
    TableStyle,
    UnsupportedMathMLError,
    convert,
    mathml_to_omml,
)

NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}


class MathTests(unittest.TestCase):
    def check(self, source, structure):
        root = mathml_to_omml(
            '<math xmlns="http://www.w3.org/1998/Math/MathML">' + source + "</math>"
        )
        self.assertEqual(len(root.xpath(structure, namespaces=NS)), 1)
        return root

    def test_fraction(self):
        root = self.check("<mfrac><mn>1</mn><mn>2</mn></mfrac>", "./m:f/m:den/m:r/m:t")
        self.assertEqual(root.xpath("string(m:f/m:den/m:r/m:t)", namespaces=NS), "2")

    def test_scripts_roots(self):
        for source, path in [
            ("<msup><mi>x</mi><mn>2</mn></msup>", "./m:sSup/m:sup"),
            ("<msub><mi>x</mi><mn>2</mn></msub>", "./m:sSub/m:sub"),
            ("<msubsup><mi>x</mi><mn>1</mn><mn>2</mn></msubsup>", "./m:sSubSup/m:sup"),
            ("<msqrt><mi>x</mi></msqrt>", "./m:rad/m:e"),
            ("<mroot><mi>x</mi><mn>3</mn></mroot>", "./m:rad/m:deg"),
        ]:
            with self.subTest(source=source):
                self.check(source, path)

    def test_fences_and_matrix(self):
        root = self.check("<mfenced><mi>x</mi><mi>y</mi><mi>z</mi></mfenced>", "./m:d")
        self.assertEqual("".join(root.itertext()), "x,y,z")
        self.check(
            "<mtable><mtr><mtd><mn>1</mn></mtd></mtr></mtable>", "./m:m/m:mr/m:e"
        )

    def test_limits_accents(self):
        self.check('<mover accent="true"><mi>x</mi><mo>^</mo></mover>', "./m:acc/m:e")
        self.check(
            "<munderover><mo>∑</mo><mn>0</mn><mi>n</mi></munderover>",
            "./m:limUpp/m:e/m:limLow",
        )

    def test_semantics(self):
        root = self.check(
            '<semantics><mi>x</mi><annotation encoding="application/x-tex">ignored</annotation></semantics>',
            "./m:r",
        )
        self.assertEqual("".join(root.itertext()), "x")

    def test_reject_unsupported(self):
        with self.assertRaises(UnsupportedMathMLError):
            mathml_to_omml("<math><menclose><mi>x</mi></menclose></math>")
        with self.assertRaises(ValueError):
            mathml_to_omml("<math><mfrac><mi>x</mi></mfrac></math>")
        with self.assertRaises(ValueError):
            mathml_to_omml(
                '<!DOCTYPE math [<!ENTITY x SYSTEM "file:///etc/passwd">]><math>&x;</math>'
            )

    def test_latex(self):
        for formula, tag in [
            (r"\frac{1}{2}", "f"),
            (r"x_1^2", "sSubSup"),
            (r"\sqrt{x}", "rad"),
            (r"\sum_{i=0}^{n}i", "limUpp"),
            (r"\begin{pmatrix}a&b\\c&d\end{pmatrix}", "m"),
        ]:
            with self.subTest(formula=formula):
                doc = MathmlToDocx().parse_latex(formula)
                self.assertTrue(doc._element.xpath("//m:" + tag))


class PublicApiTests(unittest.TestCase):
    def test_simple_api_and_styles(self):
        doc = convert("<table><tr><td>x</td></tr></table>", table_style=TableStyle.GRID)
        self.assertEqual(doc.tables[0].style.name, "Table Grid")
        doc = convert("<p>x</p>", paragraph_style=ParagraphStyle.QUOTE)
        self.assertEqual(doc.paragraphs[0].style.name, "Quote")

    def test_file_paths_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.html"
            source.write_text("<p>Índice 한글</p>", encoding="utf-8")
            parser = MathmlToDocx()
            for name in ["output.docx", "output"]:
                result = parser.parse_html_file(source, Path(tmp) / name)
                self.assertEqual(result.name, "output.docx")
                self.assertEqual(Document(result).paragraphs[0].text, "Índice 한글")
            self.assertEqual(
                parser.parse_html_file(source), source.with_suffix(".docx")
            )

    def test_explicit_style_targets(self):
        doc = Document()
        paragraph = doc.add_paragraph()
        run = paragraph.add_run("x")
        parser = MathmlToDocx()
        parser.add_styles_to_run("color:red;text-decoration:underline", run=run)
        parser.add_styles_to_paragraph("margin-left:96px", paragraph=paragraph)
        self.assertEqual(str(run.font.color.rgb), "FF0000")
        self.assertTrue(run.underline)
        self.assertEqual(paragraph.paragraph_format.left_indent.inches, 1)
        with self.assertRaises(ValueError):
            parser.add_styles_to_run("color:red")

    def test_copy_options(self):
        source = MathmlToDocx(
            images=False, mathml=False, style_map={"p": {"x": "Quote"}}
        )
        target = MathmlToDocx()
        target.copy_settings_from(source)
        source.options.images = True
        source.style_map["p"]["x"] = "Normal"
        self.assertFalse(target.options.images)
        self.assertFalse(target.options["mathml"])
        self.assertEqual(target.style_map["p"]["x"], "Quote")
        with self.assertRaises(TypeError):
            target.options.images = "false"

    def test_nested_disabled_options(self):
        doc = MathmlToDocx(images=False, mathml=False).parse_html_string(
            "<table><tr><td><img><math><mi>x</mi></math></td></tr></table>"
        )
        self.assertFalse(doc._element.xpath("//m:oMath"))
        self.assertNotIn("image", doc.tables[0].cell(0, 0).text)

    def test_template_placeholder(self):
        doc = Document()
        doc.add_paragraph("before")
        doc.add_paragraph("{{content}}")
        doc.add_paragraph("after")
        MathmlToDocx().replace_html(
            doc,
            "{{content}}",
            '<p>middle</p><p><a href="https://example.com">link</a></p>',
        )
        self.assertEqual(
            ["".join(p._p.xpath(".//w:t/text()")) for p in doc.paragraphs],
            ["before", "middle", "link", "after"],
        )
        with BytesIO() as out:
            doc.save(out)
            out.seek(0)
            reopened = Document(out)
            self.assertTrue(reopened.paragraphs[2]._p.xpath("./w:hyperlink"))

    def test_docxtpl(self):
        from docxtpl import DocxTemplate

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "template.docx"
            Document().save(path)
            template = DocxTemplate(path)
            MathmlToDocx().add_html_to_document("<p>added</p>", template)
            self.assertEqual(template.get_docx().paragraphs[0].text, "added")


class HtmlTests(unittest.TestCase):
    def test_base64_inline_image(self):
        data = base64.b64encode(Path("tests/dataset/testimg.png").read_bytes()).decode()
        doc = convert(
            '<p>before<img src="data:image/png;base64,'
            + data
            + '" style="width:96px">after</p>'
        )
        self.assertEqual(len(doc.paragraphs), 1)
        self.assertEqual(doc.paragraphs[0].text, "beforeafter")
        self.assertEqual(len(doc.inline_shapes), 1)
        self.assertEqual(doc.inline_shapes[0].width.inches, 1)

    def test_no_implicit_network_or_arbitrary_files(self):
        with patch(
            "urllib.request.urlopen", side_effect=AssertionError("Network forbidden")
        ):
            doc = convert(
                '<p><img src="http://127.0.0.1/private"><img src="/etc/passwd"></p>'
            )
        self.assertEqual(len(doc.inline_shapes), 0)
        with tempfile.TemporaryDirectory() as tmp:
            doc = convert('<img src="../outside.png">', img_src_base_path=tmp)
            self.assertEqual(len(doc.inline_shapes), 0)

    def test_loader(self):
        calls = []

        def loader(src):
            calls.append(src)
            return Path("tests/dataset/testimg.png").read_bytes()

        doc = convert('<img src="asset:1">', image_loader=loader)
        self.assertEqual(calls, ["asset:1"])
        self.assertEqual(len(doc.inline_shapes), 1)

    def test_merged_empty_rowspan(self):
        html = (
            '<table><tr><td rowspan="2"></td><td>A</td></tr><tr><td>B</td></tr></table>'
        )
        doc = convert(html)
        table = doc.tables[0]
        self.assertIs(table.cell(0, 0)._tc, table.cell(1, 0)._tc)
        self.assertEqual(table.cell(1, 1).text, "B")

    def test_upstream_spans(self):
        html = '<table><tr><th colspan="2">Country</th><th></th></tr><tr><td>Dhaka</td><td rowspan="2">Bangladesh</td></tr><tr><td>Sylhet</td></tr></table>'
        table = convert(html).tables[0]
        self.assertEqual(table.cell(2, 0).text, "Sylhet")
        self.assertEqual(table.cell(2, 1).text, "Bangladesh")
        self.assertEqual(len(table.columns), 3)

    def test_nested_table(self):
        table = convert(
            "<table><tr><td>outer<table><tbody><tr><td>inner</td></tr></tbody></table></td></tr></table>"
        ).tables[0]
        self.assertEqual(table.cell(0, 0).tables[0].cell(0, 0).text, "inner")

    def test_lists_restart_and_nest(self):
        doc = convert(
            '<ol><li>A<ol start="3"><li>B</li></ol></li><li>C</li></ol><ol><li>D</li></ol>'
        )
        paragraphs = [p for p in doc.paragraphs if p.text]
        ids = [p._p.pPr.numPr.numId.val for p in paragraphs]
        self.assertEqual(ids[0], ids[2])
        self.assertNotEqual(ids[0], ids[1])
        self.assertNotEqual(ids[0], ids[3])
        self.assertEqual(paragraphs[1]._p.pPr.numPr.ilvl.val, 1)
        self.assertIn('w:val="3"', doc.part.numbering_part.element.xml)

    def test_blocks_title_pagebreak_classmap(self):
        doc = MathmlToDocx(style_map={"p": {"quote": "Quote"}}).parse_html_string(
            '<title>T</title><div>A</div><section>B</section><p class="quote" style="page-break-before:always">C</p>'
        )
        self.assertEqual([p.text for p in doc.paragraphs], ["T", "A", "B", "C"])
        self.assertEqual(doc.paragraphs[0].style.name, "Title")
        self.assertEqual(doc.paragraphs[-1].style.name, "Quote")
        self.assertTrue(doc.paragraphs[-1].paragraph_format.page_break_before)

    def test_inline_formats(self):
        doc = convert(
            "<p><del>gone</del><sub>sub</sub><sup>sup</sup><i>italics</i></p>"
        )
        runs = doc.paragraphs[0].runs
        self.assertTrue(runs[0].font.strike)
        self.assertTrue(runs[1].font.subscript)
        self.assertTrue(runs[2].font.superscript)
        self.assertTrue(runs[3].italic)

    def test_color_forms(self):
        for value in ["red", "#f00", "rgb(255,0,0)", "rgba(255,0,0,0.88)"]:
            with self.subTest(value=value):
                run = (
                    convert('<p style="color:' + value + '">x</p>')
                    .paragraphs[0]
                    .runs[0]
                )
                self.assertEqual(
                    str(run.font.color.rgb),
                    "FF1F1F" if value.startswith("rgba") else "FF0000",
                )

    def test_pre_tabs_and_break(self):
        text = "a\tb\n  c"
        self.assertEqual(convert("<pre>" + text + "</pre>").paragraphs[0].text, text)
        self.assertEqual(convert("<br>text").paragraphs[0].text, "\ntext")

    def test_nested_block_no_empty_paragraph(self):
        doc = convert(
            "<h1>Test file</h1><p>P1</p><p>P2</p><div>D1</div><div><span>D2</span></div><section><div>D3</div></section>"
        )
        self.assertEqual(
            [p.text for p in doc.paragraphs],
            ["Test file", "P1", "P2", "D1", "D2", "D3"],
        )

    def test_styles_false(self):
        run = convert('<b style="color:red">x</b>', styles=False).paragraphs[0].runs[0]
        self.assertIsNone(run.bold)
        self.assertIsNone(run.font.color.rgb)
