"""Independent mathematical-role expectations and mixed-document regressions."""

import unittest
from io import BytesIO
from pathlib import Path

from docx import Document
from lxml import etree

from examples.math_corpus import LATEX, SHOWCASE, generated_cases
from mathml2docx import UnsupportedMathMLError, convert, mathml_to_omml
from mathml2docx.math import latex_to_omml

NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}


def expected_roles(model):
    """Normalize only grouping in the source expression model, not XML output."""
    if isinstance(model, str):
        return (model,)
    if model[0] == "row":
        return tuple(item for child in model[1:] for item in expected_roles(child))
    return ((model[0],) + tuple(expected_roles(c) for c in model[1:]),)


def read_roles(nodes):
    """Interpret OMML independently into mathematical roles; reject unknown output."""
    result = []
    for node in nodes:
        tag = etree.QName(node).localname
        if tag == "r":
            result.append("".join(node.xpath("./m:t/text()", namespaces=NS)))
            continue
        if tag == "rad":
            hidden = node.xpath("./m:radPr/m:degHide/@m:val", namespaces=NS)
            role, args = ("sqrt", ["e"]) if hidden == ["1"] else ("root", ["e", "deg"])
        elif tag == "m":
            result.append(
                ("matrix",)
                + tuple(read_roles(c) for c in node.xpath("./m:mr/m:e", namespaces=NS))
            )
            continue
        else:
            role, args = {
                "f": ("fraction", ["num", "den"]),
                "sSup": ("sup", ["e", "sup"]),
                "sSub": ("sub", ["e", "sub"]),
                "sSubSup": ("subsup", ["e", "sub", "sup"]),
                "limLow": ("lower", ["e", "lim"]),
                "limUpp": ("upper", ["e", "lim"]),
                "d": ("fence", ["e"]),
                "phant": ("phantom", ["e"]),
            }[tag]
        result.append(
            (role,) + tuple(read_roles(node.find("m:" + arg, NS)) for arg in args)
        )
    return tuple(result)


class CompositionCorpusTests(unittest.TestCase):
    def test_generated_roles_with_and_without_namespace(self):
        for name, body, model in generated_cases():
            for namespace in ["", ' xmlns="http://www.w3.org/1998/Math/MathML"']:
                with self.subTest(case=name, namespace=namespace):
                    root = mathml_to_omml("<math" + namespace + ">" + body + "</math>")
                    self.assertEqual(read_roles(root), expected_roles(model))

    def test_nested_fraction_root_and_scripts_have_correct_roles(self):
        root = mathml_to_omml(
            "<math><mfrac><msubsup><mi>x</mi><mn>1</mn><mn>2</mn></msubsup><mroot><mi>y</mi><mn>3</mn></mroot></mfrac></math>"
        )
        self.assertEqual(
            read_roles(root),
            (
                (
                    "fraction",
                    (("subsup", ("x",), ("1",), ("2",)),),
                    (("root", ("y",), ("3",)),),
                ),
            ),
        )

    def test_showcase_and_latex_survive_save_and_reopen(self):
        document = Document()
        expected = []
        for name, body in SHOWCASE:
            with self.subTest(mathml=name):
                math = mathml_to_omml("<math>" + body + "</math>")
                document.add_paragraph()._p.append(math)
                expected.append(etree.tostring(math, method="c14n"))
        for source in LATEX:
            with self.subTest(latex=source):
                math = latex_to_omml(source)
                document.add_paragraph()._p.append(math)
                expected.append(etree.tostring(math, method="c14n"))
        with BytesIO() as stream:
            document.save(stream)
            stream.seek(0)
            reopened = Document(stream)
        self.assertEqual(
            [
                etree.tostring(m, method="c14n")
                for m in reopened._element.xpath("//m:oMath")
            ],
            expected,
        )

    def test_large_mixed_document_preserves_counts_order_and_relationships(self):
        blocks = [
            "<style>td {background-color:#eef2ff} strong {color:navy}</style><h1>Corpus report</h1>"
        ]
        for index, (_, body, _) in enumerate(generated_cases()):
            blocks.append(
                f'<p><strong>before-{index}</strong> <math display="inline">{body}</math> <em>after-{index}</em></p>'
            )
            if index % 12 == 0:
                blocks.append(
                    '<table><tr><td rowspan="2">merged</td><td><math display="inline"><mfrac><mi>a</mi><mi>b</mi></mfrac></math></td></tr><tr><td><table><tr><td>nested</td></tr></table></td></tr></table><ol start="3"><li>First <math display="inline"><mi>x</mi></math></li><li>Second</li></ol><p><a href="https://example.com">reference</a><img src="swatch.png" width="24"></p>'
                )
        doc = convert(
            "".join(blocks),
            img_src_base_path=str(
                Path(__file__).resolve().parents[1] / "examples/assets"
            ),
        )
        with BytesIO() as stream:
            doc.save(stream)
            stream.seek(0)
            doc = Document(stream)
        self.assertEqual(len(doc._element.xpath("//m:oMath")), 280)
        self.assertEqual(len(doc.tables), 20)
        self.assertEqual(len(doc.inline_shapes), 20)
        self.assertEqual(len(doc._element.xpath("//w:hyperlink")), 20)
        paragraphs = [p for p in doc.paragraphs if p.text.startswith("before-")]
        self.assertEqual(len(paragraphs), 240)
        for index, (paragraph, (_, _, model)) in enumerate(
            zip(paragraphs, generated_cases())
        ):
            with self.subTest(index=index):
                self.assertEqual(paragraph.text, f"before-{index}  after-{index}")
                self.assertTrue(paragraph.runs[0].bold)
                self.assertTrue(paragraph.runs[-1].italic)
                self.assertEqual(
                    read_roles(paragraph._p.xpath("./m:oMath")[0]),
                    expected_roles(model),
                )
        for table in doc.tables:
            self.assertIs(table.cell(0, 0)._tc, table.cell(1, 0)._tc)
            self.assertEqual(table.cell(1, 1).tables[0].cell(0, 0).text, "nested")


class MathematicalMeaningTests(unittest.TestCase):
    def test_required_argument_counts(self):
        for tag, count in [
            ("mfrac", 2),
            ("mroot", 2),
            ("msup", 2),
            ("msub", 2),
            ("msubsup", 3),
            ("munder", 2),
            ("mover", 2),
            ("munderover", 3),
        ]:
            for wrong in range(5):
                if wrong != count:
                    with self.subTest(tag=tag, children=wrong), self.assertRaises(
                        ValueError
                    ):
                        self.math(
                            "<" + tag + ">" + "<mi>x</mi>" * wrong + "</" + tag + ">"
                        )

    def test_unsupported_constructs_and_external_entities(self):
        for tag in [
            "menclose",
            "maction",
            "mstack",
            "apply",
        ]:
            with self.subTest(tag=tag), self.assertRaises(UnsupportedMathMLError):
                self.math("<" + tag + "><mi>x</mi></" + tag + ">")
        for body in [
            "<mlongdiv><mn>1</mn><mn>2</mn><mn>3</mn></mlongdiv>",
            '<mglyph src="unused.png" alt="x"/>',
        ]:
            with self.subTest(body=body), self.assertRaises(UnsupportedMathMLError):
                self.math(body)
        for source in [
            '<!DOCTYPE math SYSTEM "https://example.com/math.dtd"><math/>',
            '<!DOCTYPE math [<!ENTITY x SYSTEM "file:///etc/passwd">]><math><mi>&x;</mi></math>',
            "<math><mi>&unknown;</mi></math>",
        ]:
            with self.subTest(source=source), self.assertRaises(ValueError):
                mathml_to_omml(source)

    def test_deep_and_wide_supported_expressions(self):
        root = self.math("<msqrt>" * 32 + "<mi>x</mi>" + "</msqrt>" * 32)
        self.assertEqual(len(root.xpath(".//m:rad", namespaces=NS)), 32)
        root = self.math("<mi>x</mi><mo>+</mo>" * 512 + "<mn>1</mn>")
        self.assertEqual(len(root.xpath("./m:r", namespaces=NS)), 1025)
        self.assertEqual(root.xpath("m:r[last()]/m:t/text()", namespaces=NS), ["1"])

    def test_explicit_operator_fences_are_delimiters(self):
        root = self.math(
            '<mrow><mo fence="true" form="prefix">|</mo><mfrac><mi>a</mi><mi>b</mi></mfrac><mo fence="true" form="postfix">|</mo></mrow>'
        )
        self.assertEqual(root.xpath("m:d/m:dPr/m:begChr/@m:val", namespaces=NS), ["|"])
        self.assertEqual(len(root.xpath("m:d/m:e/m:f", namespaces=NS)), 1)

    def test_latex_limit_uses_lower_limit(self):
        root = latex_to_omml(r"\lim_{x\to0}\frac{\sin x}{x}=1")
        self.assertEqual(
            root.xpath("string(m:func/m:fName/m:limLow/m:e/m:r/m:t)", namespaces=NS),
            "lim",
        )
        self.assertEqual(len(root.xpath("m:func/m:e/m:f", namespaces=NS)), 1)

    def test_text_and_math_spacing_have_normal_text_property(self):
        root = self.math('<mtext>result</mtext><mspace width="1em"/>')
        self.assertEqual(
            root.xpath("m:r/m:rPr/m:nor/@m:val", namespaces=NS), ["1", "1"]
        )

    def test_required_shading_and_table_property_order(self):
        doc = convert(
            '<p><span style="background-color:red">text</span></p><table style="width:90%;border:1px solid blue"><tr><td style="background-color:yellow">cell</td></tr></table>'
        )
        self.assertTrue(doc._element.xpath("//w:shd"))
        self.assertFalse(doc._element.xpath("//w:shd[not(@w:val)]"))
        properties = [etree.QName(n).localname for n in doc.tables[0]._tbl.tblPr]
        self.assertLess(properties.index("tblBorders"), properties.index("tblLayout"))

    def math(self, content):
        return mathml_to_omml("<math>" + content + "</math>")

    def test_binomial_has_no_fraction_bar(self):
        root = self.math('<mfrac linethickness="0"><mi>n</mi><mi>k</mi></mfrac>')
        self.assertEqual(
            root.xpath("string(m:f/m:fPr/m:type/@m:val)", namespaces=NS), "noBar"
        )

    def test_bevelled_fraction(self):
        root = self.math('<mfrac bevelled="true"><mi>x</mi><mi>y</mi></mfrac>')
        self.assertEqual(
            root.xpath("string(m:f/m:fPr/m:type/@m:val)", namespaces=NS), "skw"
        )

    def test_upright_identifiers_and_inherited_variants(self):
        root = self.math(
            '<mi>sin</mi><mi mathvariant="normal">d</mi><mstyle mathvariant="bold"><mi>x</mi></mstyle>'
        )
        self.assertEqual(
            root.xpath("m:r/m:rPr/m:sty/@m:val", namespaces=NS), ["p", "p", "b"]
        )
        self.assertEqual(root.xpath("m:r/m:t/text()", namespaces=NS), ["sin", "d", "𝐱"])

    def test_mathematical_alphabets_preserve_distinctions(self):
        for variant, source, expected in [
            ("double-struck", "RZ", "ℝℤ"),
            ("script", "Fe", "ℱℯ"),
            ("fraktur", "CH", "ℭℌ"),
            ("bold", "vα2", "𝐯𝛂𝟐"),
            ("italic", "hx", "ℎ𝑥"),
            ("bold", "𝑥", "𝑥"),
        ]:
            with self.subTest(variant=variant, source=source):
                root = self.math(
                    '<mi mathvariant="' + variant + '">' + source + "</mi>"
                )
                self.assertEqual(
                    root.xpath("m:r/m:t/text()", namespaces=NS), [expected]
                )

    def test_string_quotes(self):
        root = self.math('<ms>hello</ms><ms lquote="[" rquote="]">x</ms>')
        self.assertEqual(
            root.xpath("m:r/m:t/text()", namespaces=NS), ['"hello"', "[x]"]
        )

    def test_comment_and_processing_instruction_are_not_math(self):
        root = self.math(
            "<mi>x</mi><!-- comment --><?hint ignore?><mo>+</mo><mn>1</mn>"
        )
        self.assertEqual(root.xpath("m:r/m:t/text()", namespaces=NS), ["x", "+", "1"])

    def test_foreign_namespace_is_rejected(self):
        for content in [
            '<mi xmlns="urn:unrelated">x</mi>',
            '<mtable><mtr xmlns="urn:unrelated"><mtd/></mtr></mtable>',
            '<mrow><mo xmlns="urn:unrelated">(</mo><mi>x</mi><mo>)</mo></mrow>',
        ]:
            with self.subTest(content=content), self.assertRaises(
                UnsupportedMathMLError
            ):
                self.math(content)

    def test_invalid_matrix_cells_and_empty_matrix_are_rejected(self):
        for content in [
            "<mtable/>",
            "<mtable><mtr/></mtable>",
            "<mtable><mtr><mi>x</mi></mtr></mtable>",
            "<mtable><mtr>lost<mtd><mi>x</mi></mtd></mtr></mtable>",
        ]:
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.math(content)

    def test_multi_character_fence_is_explicitly_rejected(self):
        with self.assertRaises(UnsupportedMathMLError):
            self.math('<mfenced open="abc"><mi>x</mi></mfenced>')

    def test_operator_accents_and_underbar(self):
        root = self.math(
            '<mover><mi>v</mi><mo accent="true">→</mo></mover><munder><mi>x</mi><mo accent="true">―</mo></munder>'
        )
        self.assertEqual(
            root.xpath("string(m:acc/m:accPr/m:chr/@m:val)", namespaces=NS), "→"
        )
        self.assertEqual(
            root.xpath("string(m:bar/m:barPr/m:pos/@m:val)", namespaces=NS), "bot"
        )

    def test_unsupported_layout_is_rejected(self):
        for content in [
            '<mpadded width="0"><mi>x</mi></mpadded>',
            '<mspace linebreak="newline"/>',
            '<mi mathvariant="initial">x</mi>',
        ]:
            with self.subTest(content=content), self.assertRaises(
                UnsupportedMathMLError
            ):
                self.math(content)

    def test_plain_text_in_structural_math_is_rejected(self):
        with self.assertRaises(ValueError):
            self.math("lost<mi>x</mi>")


class MixedMathTests(unittest.TestCase):
    def test_math_does_not_trim_following_text_space(self):
        doc = convert('<p>before <math display="inline"><mi>x</mi></math> after</p>')
        self.assertEqual(
            doc.paragraphs[0]._p.xpath("./w:r/w:t/text()"), ["before ", " after"]
        )

    def test_math_inside_hyperlink_is_preserved(self):
        doc = convert(
            '<p>before <a href="https://example.com"><math display="inline"><mi>x</mi></math></a> after</p>'
        )
        self.assertEqual(len(doc._element.xpath("//m:oMath")), 1)

    def test_roundtrip_keeps_math_between_styled_runs(self):
        doc = convert(
            '<p><b>Before</b><math display="inline"><mfrac><mn>1</mn><mn>2</mn></mfrac></math><i>After</i></p>'
        )
        with BytesIO() as stream:
            doc.save(stream)
            stream.seek(0)
            doc = Document(stream)
        self.assertEqual(len(doc.paragraphs), 1)
        self.assertEqual(len(doc._element.xpath("//m:f")), 1)
        self.assertTrue(doc.paragraphs[0].runs[0].bold)
        self.assertTrue(doc.paragraphs[0].runs[-1].italic)
