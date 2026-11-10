"""Compare saved DOCX files against checked-in, independently written answers."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from examples.math_corpus import CATALOG, CORPUS
from mathml2docx import MathmlToDocx, convert
from mathml2docx.math import latex_to_omml
from tests.docx_oracle import NS, DocxOracle

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = json.loads(
    (ROOT / "tests/fixtures/math_expectations.json").read_text(encoding="utf-8")
)


class SavedDocumentOracleTests(unittest.TestCase):
    def assert_run_properties(self, document, index, expected):
        runs = document.math_runs(index)
        self.assertTrue(
            any(
                all(run[key] == value for key, value in expected.items())
                for run in runs
            ),
            "Missing mathematical run properties: " + repr(expected),
        )

    def test_early_python_patch_reports_latex_requirement(self):
        with patch(
            "mathml2docx.math.sys.version_info", (3, 6, 1)
        ), self.assertRaisesRegex(ImportError, "Python >=3.6.2"):
            latex_to_omml(r"\frac{1}{2}")

    def test_latex_operator_layout_and_literal_text_are_preserved(self):
        cases = [
            (
                r"\sum\nolimits_{i=1}^{n}i+\sum_{j=1}^{m}j",
                [
                    {"subsup": [["∑"], ["i=1"], ["n"]]},
                    "i+",
                    {"upper": [[{"lower": [["∑"], ["j=1"]]}], ["m"]]},
                    "j",
                ],
            ),
            (
                r"\int\limits_0^1 x\,dx",
                [
                    {"upper": [[{"lower": [["∫"], ["0"]]}], ["1"]]},
                    "xdx",
                ],
            ),
            (
                r"\text{\sum\nolimits}+\sum_{i=1}^n i",
                [
                    r"\sum\nolimits+",
                    {"upper": [[{"lower": [["∑"], ["i=1"]]}], ["n"]]},
                    "i",
                ],
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for source, expected in cases:
                with self.subTest(latex=source):
                    path = Path(tmp) / "operator.docx"
                    MathmlToDocx().parse_latex(source).save(str(path))
                    self.assertEqual(DocxOracle(path).equations(), [expected])

    def test_saved_document_changes_do_not_match_answer(self):
        source = (ROOT / "examples/assets/mixed_math.html").read_text(encoding="utf-8")
        expected = json.loads(
            (ROOT / "tests/fixtures/mixed_math_expectation.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "original.docx"
            convert(source, original, img_src_base_path=str(ROOT / "examples/assets"))
            good = DocxOracle(original)
            self.assertEqual(good.blocks(), expected)
            for change in [
                "numerator",
                "bold",
                "hyperlink",
                "image",
                "numbering",
                "merge",
                "heading",
            ]:
                with self.subTest(change=change):
                    files = dict(good.files)
                    root = ET.fromstring(files["word/document.xml"])
                    part = "word/document.xml"
                    if change == "numerator":
                        root.find(".//m:f/m:num//m:t", NS).text = "WRONG"
                    elif change == "bold":
                        props = next(
                            p
                            for p in root.findall(".//w:rPr", NS)
                            if p.find("w:b", NS) is not None
                        )
                        props.remove(props.find("w:b", NS))
                    elif change == "hyperlink":
                        part = "word/_rels/document.xml.rels"
                        root = ET.fromstring(files[part])
                        for rel in root:
                            if rel.get("Target") == "https://example.com/reference":
                                rel.set("Target", "https://example.com/wrong")
                    elif change == "image":
                        image = next(
                            name for name in files if name.startswith("word/media/")
                        )
                        files[image] = b"changed image content"
                    elif change == "numbering":
                        part = "word/numbering.xml"
                        root = ET.fromstring(files[part])
                        for start in root.findall(".//w:start", NS):
                            if start.get("{" + NS["w"] + "}val") == "3":
                                start.set("{" + NS["w"] + "}val", "7")
                    elif change == "merge":
                        props = next(
                            p
                            for p in root.findall(".//w:tcPr", NS)
                            if p.find("w:vMerge", NS) is not None
                        )
                        props.remove(props.find("w:vMerge", NS))
                    elif change == "heading":
                        root.find(".//w:pStyle", NS).set(
                            "{" + NS["w"] + "}val", "Normal"
                        )
                    files[part] = ET.tostring(root, encoding="utf-8")
                    changed = Path(tmp) / (change + ".docx")
                    with ZipFile(changed, "w", ZIP_DEFLATED) as archive:
                        for name, content in files.items():
                            archive.writestr(name, content)
                    self.assertNotEqual(DocxOracle(changed).blocks(), expected)

    def test_matrix_shape_is_checked_in_addition_to_flat_cell_content(self):
        source = (CORPUS / "M09.html").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            original = Path(tmp) / "matrix.docx"
            MathmlToDocx().parse_mathml(source).save(str(original))
            good = DocxOracle(original)
            self.assertEqual(good.equations(), [ANSWERS["M09"]["math"]])
            root = ET.fromstring(good.files["word/document.xml"])
            matrix = root.find(".//m:m", NS)
            rows = matrix.findall("m:mr", NS)
            for cell in list(rows[1]):
                rows[1].remove(cell)
                rows[0].append(cell)
            matrix.remove(rows[1])
            good.files["word/document.xml"] = ET.tostring(root, encoding="utf-8")
            changed = Path(tmp) / "wrong-shape.docx"
            with ZipFile(changed, "w", ZIP_DEFLATED) as archive:
                for name, content in good.files.items():
                    archive.writestr(name, content)
            self.assertNotEqual(
                DocxOracle(changed).equations(), [ANSWERS["M09"]["math"]]
            )

    def test_mixed_html_matches_document_answer(self):
        source = (ROOT / "examples/assets/mixed_math.html").read_text(encoding="utf-8")
        expected = json.loads(
            (ROOT / "tests/fixtures/mixed_math_expectation.json").read_text(
                encoding="utf-8"
            )
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "mixed.docx"
            convert(source, path, img_src_base_path=str(ROOT / "examples/assets"))
            actual = DocxOracle(path)
        self.assertEqual(actual.blocks(), expected)

    def test_all_inputs_have_independent_answers(self):
        self.assertEqual({entry["id"] for entry in CATALOG}, set(ANSWERS))
        self.assertEqual(len(CATALOG), len(ANSWERS))
        self.assertEqual(
            {entry["file"] for entry in CATALOG},
            {
                path.name
                for path in CORPUS.iterdir()
                if path.suffix in {".html", ".tex"}
            },
        )

    def test_saved_mathml_html_and_latex_match_answers(self):
        parser = MathmlToDocx()
        with tempfile.TemporaryDirectory() as tmp:
            for entry in CATALOG:
                source = (CORPUS / entry["file"]).read_text(encoding="utf-8")
                paths = ["mathml", "html"] if entry["format"] == "mathml" else ["latex"]
                for frontend in paths:
                    with self.subTest(case=entry["id"], frontend=frontend):
                        document = (
                            convert(source)
                            if frontend == "html"
                            else getattr(parser, "parse_" + frontend)(source)
                        )
                        path = Path(tmp) / (entry["id"] + ".docx")
                        document.save(str(path))
                        actual = DocxOracle(path)
                        self.assertEqual(
                            actual.equations(), [ANSWERS[entry["id"]]["math"]]
                        )
                        for expected in ANSWERS[entry["id"]].get("run_properties", []):
                            self.assert_run_properties(actual, 0, expected)

    def generate_example(self, name, directory):
        subprocess.run(
            [sys.executable, "-m", "examples." + name],
            cwd=str(ROOT),
            env=dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=directory),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        return DocxOracle(Path(directory) / (name + ".docx"))

    def test_gallery_file_matches_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = self.generate_example("23_complex_equations", tmp)
        order = [f"M{i:02d}" for i in range(1, 21)] + [
            f"L{i:02d}" for i in range(1, 25)
        ]
        self.assertEqual(actual.equations(), [ANSWERS[key]["math"] for key in order])
        for index, key in enumerate(order):
            for expected in ANSWERS[key].get("run_properties", []):
                with self.subTest(case=key):
                    self.assert_run_properties(actual, index, expected)

    def test_dense_report_file_matches_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = self.generate_example("24_dense_report", tmp)
        expected = []
        for _section in range(5):
            for index in range(20):
                expected.append(ANSWERS[f"M{index + 1:02d}"]["math"])
                if index in {0, 5, 10, 15}:
                    expected.append([{"fraction": [["a"], ["b"]], "type": "bar"}])
        self.assertEqual(actual.equations(), expected)


if __name__ == "__main__":
    unittest.main()
