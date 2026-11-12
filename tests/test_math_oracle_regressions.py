"""Independent document checks must detect math layout, styling and count loss."""

import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from docx import Document

from mathml2docx import MathmlToDocx, convert, mathml_to_omml
from tests.docx_oracle import NS, DocxOracle


def write_changed(original, destination, root):
    with ZipFile(destination, "w", ZIP_DEFLATED) as archive:
        for name, data in original.files.items():
            archive.writestr(
                name,
                ET.tostring(root, encoding="utf-8")
                if name == "word/document.xml"
                else data,
            )


class MathOracleRegressionTests(unittest.TestCase):
    def test_inline_and_display_layout_and_justification_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            inline = Path(tmp) / "inline.docx"
            block = Path(tmp) / "block.docx"
            right = Path(tmp) / "right.docx"
            convert('<math display="inline"><mi>x</mi></math>', inline)
            convert('<math display="block"><mi>x</mi></math>', block)
            convert(
                '<math display="block" style="text-align:right"><mi>x</mi></math>',
                right,
            )
            self.assertEqual(
                DocxOracle(inline).equations(), DocxOracle(block).equations()
            )
            self.assertNotEqual(DocxOracle(inline).blocks(), DocxOracle(block).blocks())
            self.assertNotEqual(DocxOracle(block).blocks(), DocxOracle(right).blocks())

    def test_math_color_size_and_each_font_slot_survive_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.docx"
            MathmlToDocx().parse_mathml("<math><mi>x</mi></math>").save(str(path))
            before = DocxOracle(path)
            for prop, attrs in [
                ("color", {"val": "FF0000"}),
                ("sz", {"val": "48"}),
                (
                    "rFonts",
                    {
                        "ascii": "Malgun Gothic",
                        "hAnsi": "Malgun Gothic",
                        "eastAsia": "Malgun Gothic",
                        "cs": "Malgun Gothic",
                    },
                ),
            ]:
                with self.subTest(prop=prop):
                    root = ET.fromstring(before.files["word/document.xml"])
                    run = root.find(".//m:r", NS)
                    props = ET.Element("{" + NS["w"] + "}rPr")
                    item = ET.SubElement(props, "{" + NS["w"] + "}" + prop)
                    for name, value in attrs.items():
                        item.set("{" + NS["w"] + "}" + name, value)
                    run.insert(1, props)
                    changed = Path(tmp) / "changed.docx"
                    write_changed(before, changed, root)
                    after = DocxOracle(changed)
                    self.assertNotEqual(before.math_runs(0), after.math_runs(0))
                    self.assertNotEqual(before.blocks(), after.blocks())

    def test_nonbreaking_characters_are_not_alphabet_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.docx", Path(tmp) / "b.docx"
            MathmlToDocx().parse_mathml("<math><mn>1&#x202F;234</mn></math>").save(
                str(a)
            )
            MathmlToDocx().parse_mathml("<math><mn>1 234</mn></math>").save(str(b))
            self.assertNotEqual(DocxOracle(a).equations(), DocxOracle(b).equations())

    def test_render_input_is_checked_against_independent_counts(self):
        from scripts.render_examples import expected_source_equations

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "13_mathml.docx"
            doc = Document()
            for _ in range(4):
                doc.add_paragraph()._p.append(mathml_to_omml("<math><mi>x</mi></math>"))
            doc.save(str(path))
            self.assertEqual(
                expected_source_equations(path, {"13_mathml": 4}), [True] * 4
            )
            doc._element.body.remove(doc.paragraphs[-1]._p)
            doc.save(str(path))
            with self.assertRaisesRegex(AssertionError, "Expected 4"):
                expected_source_equations(path, {"13_mathml": 4})
            for _ in range(2):
                doc.add_paragraph()._p.append(mathml_to_omml("<math><mi>x</mi></math>"))
            doc.save(str(path))
            with self.assertRaisesRegex(AssertionError, "Expected 4"):
                expected_source_equations(path, {"13_mathml": 4})

    def test_effective_variant_detects_loss_and_accepts_unicode_equivalence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.docx"
            MathmlToDocx().parse_mathml(
                '<math><mi mathvariant="double-struck">R</mi></math>'
            ).save(str(path))
            before = DocxOracle(path)
            root = ET.fromstring(before.files["word/document.xml"])
            root.find(".//m:scr", NS).set("{" + NS["m"] + "}val", "roman")
            equivalent = Path(tmp) / "equivalent.docx"
            write_changed(before, equivalent, root)
            self.assertEqual(before.blocks(), DocxOracle(equivalent).blocks())
            root.find(".//m:t", NS).text = "R"
            lost = Path(tmp) / "lost.docx"
            write_changed(before, lost, root)
            self.assertNotEqual(before.blocks(), DocxOracle(lost).blocks())

    def test_mixed_unicode_variants_inside_one_run_remain_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mixed.docx"
            MathmlToDocx().parse_mathml("<math><mtext>𝑥y</mtext></math>").save(
                str(path)
            )
            before = DocxOracle(path)
            root = ET.fromstring(before.files["word/document.xml"])
            root.find(".//m:t", NS).text = "xy"
            lost = Path(tmp) / "lost.docx"
            write_changed(before, lost, root)
            self.assertNotEqual(before.blocks(), DocxOracle(lost).blocks())

    def test_fidelity_example_matches_independent_equations_and_style(self):
        import json
        import os
        import subprocess
        import sys

        root = Path(__file__).resolve().parents[1]
        expected = json.loads(
            (root / "tests/fixtures/mathml_fidelity_expectations.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, "-m", "examples.30_mathml_fidelity"],
                cwd=str(root),
                env=dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=tmp),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            document = DocxOracle(Path(tmp) / "30_mathml_fidelity.docx")
            self.assertEqual(document.equations(), expected)
            literal_runs = document.math_runs(14)
            self.assertEqual(
                [run["text"] for run in literal_runs], ["café: ", "𝐱", " + ", "ℝ"]
            )
            self.assertEqual(
                [run["normal"] for run in literal_runs], [True, False, True, False]
            )
            linked_runs = document.math_runs(17)
            self.assertEqual(
                [run["style"] for run in linked_runs], ["i", "p", "b", "p", "p", "p"]
            )
            self.assertEqual(linked_runs[-1]["script"], "double-struck")
            self.assertEqual(
                [r["format"] for r in document.math_runs(7)],
                [{"color": "9C2745", "size_half_points": "48"}] * 2,
            )
            self.assertIsNotNone(
                document.document.find('.//w:bookmarkStart[@w:name="ratio_result"]', NS)
            )
            cell = document.document.find(".//w:tbl/w:tr/w:tc", NS)
            self.assertEqual(len(cell.findall("w:p", NS)), 3)

    def test_internal_equation_link_requires_a_saved_bookmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "links.docx"
            convert(
                '<p><a href="#eq">Equation</a></p><math id="eq"><mi>x</mi></math>', path
            )
            before = DocxOracle(path)
            before.assert_internal_links()
            root = ET.fromstring(before.files["word/document.xml"])
            for paragraph in root.findall(".//w:p", NS):
                for node in list(paragraph):
                    if node.tag in {
                        "{" + NS["w"] + "}bookmarkStart",
                        "{" + NS["w"] + "}bookmarkEnd",
                    }:
                        paragraph.remove(node)
            missing = Path(tmp) / "missing.docx"
            write_changed(before, missing, root)
            with self.assertRaisesRegex(AssertionError, "no bookmark"):
                DocxOracle(missing).assert_internal_links()
