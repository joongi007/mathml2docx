"""Document layout and explicit recovery for diverse mathematical input."""

import tempfile
import unittest
import warnings
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from docx import Document
from lxml import etree
from PIL import Image

from mathml2docx import MathmlToDocx, UnsupportedMathMLError, convert, mathml_to_omml

NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}


class MathPolicyTests(unittest.TestCase):
    def test_default_inline_keeps_sentence_and_punctuation(self):
        doc = convert("<p><b>Before </b><math><mi>x</mi></math>, after.</p>")
        self.assertEqual(len(doc.paragraphs), 1)
        self.assertEqual(doc.paragraphs[0].text, "Before , after.")
        self.assertEqual(len(doc._element.xpath("//m:oMath")), 1)
        self.assertFalse(doc._element.xpath("//m:oMathPara"))

    def test_block_default_explicit_override_and_css(self):
        p = MathmlToDocx(default_math_display="block")
        self.assertEqual(
            len(p.convert("<p>A<math><mi>x</mi></math>B</p>").paragraphs), 3
        )
        self.assertEqual(
            len(
                p.convert(
                    '<p>A<math display="inline"><mi>x</mi></math>B</p>'
                ).paragraphs
            ),
            1,
        )
        doc = p.convert(
            '<style>math { display: inline; }</style><p>A<math display="block"><mi>x</mi></math>B</p>'
        )
        self.assertEqual(len(doc.paragraphs), 1)
        doc = convert('<p>A<math display="block"><mi>x</mi></math>B</p>')
        self.assertEqual(len(doc._element.xpath("//m:oMathPara/m:oMath")), 1)

    def test_preprocessing_applies_to_html_and_standalone_once(self):
        calls = []

        def normalize(source):
            calls.append(source)
            return source.replace("<unsupported>", "<mrow>").replace(
                "</unsupported>", "</mrow>"
            )

        p = MathmlToDocx(mathml_preprocessor=normalize)
        for parse in (p.parse_mathml, p.parse_html_string):
            doc = parse("<math><unsupported><mi>x</mi></unsupported></math>")
            self.assertEqual(len(doc._element.xpath("//m:oMath")), 1)
        self.assertEqual(len(calls), 2)
        q = MathmlToDocx()
        q.copy_settings_from(p)
        self.assertIs(q.options.mathml_preprocessor, normalize)

    def test_text_fallback_is_visible_warns_and_preserves_source(self):
        source = '<math><menclose notation="circle"><mi>x</mi></menclose></math>'
        p = MathmlToDocx(unsupported_math="text")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            doc = p.parse_mathml(source)
        self.assertTrue(caught)
        self.assertIn(source, doc.paragraphs[0].text)
        self.assertFalse(doc._element.xpath("//m:oMath"))
        with self.assertRaises(UnsupportedMathMLError):
            MathmlToDocx().parse_mathml(source)

    def test_callback_recovers_as_text_or_image_and_survives_save(self):
        seen = []
        image = BytesIO()
        Image.new("RGB", (48, 24), "blue").save(image, format="PNG")

        def fallback(source, error):
            seen.append((source, error))
            return BytesIO(image.getvalue())

        p = MathmlToDocx(mathml_fallback=fallback)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            doc = p.convert(
                '<p>Before <math alttext="chemical structure"><unknown/></math> after.</p>'
            )
        self.assertEqual(len(doc.paragraphs), 1)
        self.assertEqual(doc.paragraphs[0].text, "Before  after.")
        self.assertEqual(len(doc.inline_shapes), 1)
        self.assertEqual(
            doc.inline_shapes[0]._inline.docPr.get("descr"), "chemical structure"
        )
        self.assertIsInstance(seen[0][1], UnsupportedMathMLError)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fallback.docx"
            doc.save(str(path))
            self.assertEqual(len(Document(str(path)).inline_shapes), 1)
            with ZipFile(path) as z:
                self.assertTrue(any(n.startswith("word/media/") for n in z.namelist()))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            doc = MathmlToDocx(
                mathml_fallback=lambda s, e: "unrendered: " + s
            ).parse_mathml("<math><unknown/></math>")
        self.assertIn("unrendered:", doc.paragraphs[0].text)

    def test_invalid_xml_and_wrong_arity_are_never_recovered(self):
        calls = []
        p = MathmlToDocx(
            unsupported_math="text", mathml_fallback=lambda s, e: calls.append(s)
        )
        for source in (
            "<math><mi></math>",
            "<math><mfrac><mi>x</mi></mfrac></math>",
            '<!DOCTYPE math [<!ENTITY x SYSTEM "file:///etc/passwd">]><math><mi>&x;</mi></math>',
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                p.parse_mathml(source)
        self.assertFalse(calls)
        for value in ("", b"", None):
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                MathmlToDocx(
                    mathml_fallback=lambda s, e, value=value: value
                ).parse_mathml("<math><unknown/></math>")

    def test_options_validate_at_construction_and_after_mutation(self):
        for name, value in [
            ("default_math_display", "auto"),
            ("unsupported_math", "ignore"),
            ("mathml_fallback", True),
            ("mathml_preprocessor", 42),
        ]:
            with self.subTest(name=name), self.assertRaises((ValueError, TypeError)):
                MathmlToDocx(**{name: value})
            p = MathmlToDocx()
            with self.assertRaises((ValueError, TypeError)):
                setattr(p.options, name, value)
            with self.assertRaises((ValueError, TypeError)):
                p.options[name] = value

    def test_menclose_keeps_border_sides_strikes_and_content(self):
        root = mathml_to_omml(
            '<math><menclose notation="top bottom updiagonalstrike"><mfrac><mi>a</mi><mi>b</mi></mfrac></menclose></math>'
        )
        self.assertEqual(root.xpath("count(m:borderBox/m:e/m:f)", namespaces=NS), 1)
        props = root.find("m:borderBox/m:borderBoxPr", NS)
        self.assertEqual(
            {etree.QName(n).localname: n.get("{" + NS["m"] + "}val") for n in props},
            {
                "hideTop": "0",
                "hideBot": "0",
                "hideLeft": "1",
                "hideRight": "1",
                "strikeBLTR": "1",
            },
        )
        self.assertTrue(
            mathml_to_omml(
                '<math><menclose notation="radical"><mi>x</mi></menclose></math>'
            ).find("m:rad", NS)
            is not None
        )
        for notation in ("circle", "roundedbox", "box circle", "longdiv"):
            with self.subTest(notation=notation), self.assertRaises(
                UnsupportedMathMLError
            ):
                mathml_to_omml(
                    '<math><menclose notation="'
                    + notation
                    + '"><mi>x</mi></menclose></math>'
                )

    def test_isotope_prescripts_and_ionic_postscripts(self):
        root = mathml_to_omml(
            '<math><mmultiscripts><mi mathvariant="normal">C</mi><none/><mn>2</mn><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts></math>'
        )
        self.assertEqual(root.xpath("string(m:sPre/m:sub//m:t)", namespaces=NS), "6")
        self.assertEqual(root.xpath("string(m:sPre/m:sup//m:t)", namespaces=NS), "14")
        self.assertEqual(
            root.xpath("string(m:sPre/m:e/m:sSup/m:sup//m:t)", namespaces=NS), "2"
        )
        self.assertEqual(
            root.xpath("string(m:sPre/m:e/m:sSup/m:e//m:t)", namespaces=NS), "C"
        )
        for body in (
            "<mi>C</mi><mn>1</mn>",
            "<mprescripts/>",
            "<mi>C</mi><mprescripts/><mn>1</mn>",
            "<mi>C</mi><mprescripts/><mprescripts/>",
        ):
            with self.subTest(body=body), self.assertRaises(ValueError):
                mathml_to_omml(
                    "<math><mmultiscripts>" + body + "</mmultiscripts></math>"
                )

    def test_template_replacement_retains_display_boundaries(self):
        for mode, expected in [("inline", 1), ("block", 3)]:
            with self.subTest(mode=mode):
                doc = Document()
                doc.add_paragraph("before {{equation}} after")
                MathmlToDocx(default_math_display=mode).replace_html(
                    doc, "{{equation}}", "<math><mi>x</mi></math>"
                )
                self.assertEqual(len(doc.paragraphs), expected)
                self.assertEqual(len(doc._element.xpath("//m:oMath")), 1)
                self.assertEqual(
                    len(doc._element.xpath("//m:oMathPara")), int(mode == "block")
                )

    def test_independent_saved_roles_for_chemistry_and_enclosures(self):
        from tests.docx_oracle import DocxOracle

        source = '<math><mmultiscripts><mi>C</mi><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts><mo>+</mo><menclose notation="box"><mi>x</mi></menclose></math>'
        expected = [
            {"prescript": [["C"], ["6"], ["14"]]},
            "+",
            {
                "enclosure": {
                    "body": ["x"],
                    "sides": ["top", "bottom", "left", "right"],
                    "strikes": [],
                }
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "chemical.docx"
            MathmlToDocx().parse_mathml(source).save(str(path))
            self.assertEqual(DocxOracle(path).equations(), [expected])
            # The oracle must distinguish an atomic number from a mass number.
            changed = source.replace("<mn>6</mn><mn>14</mn>", "<mn>14</mn><mn>6</mn>")
            MathmlToDocx().parse_mathml(changed).save(str(path))
            self.assertNotEqual(DocxOracle(path).equations(), [expected])

    def test_libreoffice_target_preserves_upright_and_recovers_lost_enclosures(self):
        root = mathml_to_omml(
            '<math><mi mathvariant="normal">H</mi></math>', target="libreoffice"
        )
        self.assertEqual(root.xpath("count(m:r/m:rPr/m:nor)", namespaces=NS), 1)
        source = '<math><menclose notation="box"><mi>x</mi></menclose></math>'
        self.assertTrue(mathml_to_omml(source).find("m:borderBox", NS) is not None)
        with self.assertRaises(UnsupportedMathMLError):
            MathmlToDocx(math_target="libreoffice").parse_mathml(source)
        with warnings.catch_warnings(record=True) as caught:
            doc = MathmlToDocx(
                math_target="libreoffice", unsupported_math="text"
            ).parse_mathml(source)
        self.assertTrue(caught)
        self.assertIn(source, doc.paragraphs[0].text)
        root = mathml_to_omml(
            "<math><mmultiscripts><mi>C</mi><none/><none/><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts></math>"
        )
        self.assertFalse(root.xpath(".//m:sSubSup", namespaces=NS))

    def test_latex_uses_shared_target_and_recovery(self):
        with warnings.catch_warnings(record=True) as caught:
            doc = MathmlToDocx(
                math_target="libreoffice", unsupported_math="text"
            ).parse_latex(r"\boxed{x}")
        self.assertTrue(caught)
        self.assertIn("menclose", doc.paragraphs[0].text)
        self.assertFalse(doc._element.xpath("//m:oMath"))
        root = mathml_to_omml(
            '<math><semantics><mi>x</mi><annotation-xml><html xmlns="http://www.w3.org/1999/xhtml"><p>ignored</p></html></annotation-xml></semantics></math>',
            target="libreoffice",
        )
        self.assertEqual(root.xpath("string(m:r/m:t)", namespaces=NS), "x")

    def test_libreoffice_recovery_for_known_visual_differences(self):
        for body in [
            "<mphantom><mi>x</mi></mphantom>",
            "<ms>quoted</ms>",
            '<mfrac bevelled="true"><mi>x</mi><mi>y</mi></mfrac>',
        ]:
            source = "<math>" + body + "</math>"
            with self.subTest(body=body):
                self.assertIsNotNone(mathml_to_omml(source))
                with self.assertRaises(UnsupportedMathMLError):
                    mathml_to_omml(source, target="libreoffice")
