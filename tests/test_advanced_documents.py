"""Independent mathematical answers and mixed-layout checks for advanced inputs."""

import json
import tempfile
import unittest
from pathlib import Path

from examples.advanced_math import CATALOG, DIRECTORY, source
from mathml2docx import MathmlToDocx, convert
from tests.docx_oracle import DocxOracle

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = json.loads(
    (ROOT / "tests/fixtures/advanced_math_expectations.json").read_text(
        encoding="utf-8"
    )
)


class AdvancedDocumentTests(unittest.TestCase):
    def test_advanced_saved_equations_match_independently_authored_answers(self):
        self.assertEqual({entry["id"] for entry in CATALOG}, set(ANSWERS))
        self.assertEqual(
            {entry["file"] for entry in CATALOG},
            {
                path.name
                for path in DIRECTORY.iterdir()
                if path.suffix in {".html", ".tex"}
            },
        )
        parser = MathmlToDocx()
        with tempfile.TemporaryDirectory() as tmp:
            for entry in CATALOG:
                paths = (
                    ("mathml", "html") if entry["format"] == "mathml" else ("latex",)
                )
                for frontend in paths:
                    with self.subTest(case=entry["id"], frontend=frontend):
                        text = source(entry)
                        document = (
                            convert(text)
                            if frontend == "html"
                            else getattr(parser, "parse_" + frontend)(text)
                        )
                        path = Path(tmp) / (entry["id"] + ".docx")
                        document.save(str(path))
                        self.assertEqual(
                            DocxOracle(path).equations(), [ANSWERS[entry["id"]]["math"]]
                        )

    def test_mixed_report_workbook_and_latex_saved_equations(self):
        import os
        import subprocess
        import sys
        from xml.etree import ElementTree as ET

        from tests.docx_oracle import NS

        cases = [
            ("25_research_report", "mathml", 5, 5, "가정과 해석"),
            ("26_template_workbook", "mathml", 10, 10, "검토 대상"),
            ("27_advanced_latex", "latex", 8, 0, "검토:"),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for name, frontend, tables, images, korean in cases:
                with self.subTest(example=name):
                    subprocess.run(
                        [sys.executable, "-m", "examples." + name],
                        cwd=str(ROOT),
                        env=dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=tmp),
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    actual = DocxOracle(Path(tmp) / (name + ".docx"))
                    expected = [
                        ANSWERS[e["id"]]["math"]
                        for e in CATALOG
                        if e["format"] == frontend
                    ]
                    self.assertEqual(actual.equations(), expected)
                    body = actual.document.find("w:body", NS)
                    self.assertEqual(len(body.findall("w:tbl", NS)), tables)
                    self.assertEqual(len(body.findall(".//w:drawing", NS)), images)
                    self.assertTrue(body.findall(".//w:numPr", NS))
                    self.assertTrue(body.findall(".//w:b", NS))
                    self.assertTrue(body.findall(".//w:i", NS))
                    matches = [
                        r
                        for r in body.findall(".//w:r", NS)
                        if korean in "".join(t.text or "" for t in r.findall("w:t", NS))
                    ]
                    self.assertTrue(matches)
                    for run in matches:
                        self.assertEqual(
                            run.find("w:rPr/w:rFonts", NS).get(
                                "{" + NS["w"] + "}eastAsia"
                            ),
                            "Malgun Gothic",
                        )
                    if name == "26_template_workbook":
                        self.assertTrue(body.findall(".//w:tbl/w:tr/w:tc/w:tbl", NS))
                        text = "".join(t.text or "" for t in body.findall(".//w:t", NS))
                        self.assertIn("연구 검토자 / Reviewer", text)
                        self.assertNotIn("{{reader}}", text)
                        header = next(
                            content
                            for path, content in actual.files.items()
                            if path.startswith("word/header") and path.endswith(".xml")
                        )
                        self.assertIn(
                            "수식 검토 기록", "".join(ET.fromstring(header).itertext())
                        )

    def test_dense_report_korean_font_is_present_in_the_saved_file(self):
        import os
        import subprocess
        import sys

        from tests.docx_oracle import NS

        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, "-m", "examples.24_dense_report"],
                cwd=str(ROOT),
                env=dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=tmp),
                check=True,
                stdout=subprocess.PIPE,
            )
            actual = DocxOracle(Path(tmp) / "24_dense_report.docx")
        runs = [
            run
            for run in actual.document.findall(".//w:r", NS)
            if "한글 설명과" in "".join(t.text or "" for t in run.findall("w:t", NS))
        ]
        self.assertEqual(len(runs), 5)
        for run in runs:
            fonts = run.find("w:rPr/w:rFonts", NS)
            self.assertIsNotNone(fonts)
            self.assertEqual(fonts.get("{" + NS["w"] + "}eastAsia"), "Malgun Gothic")

    def test_word_comparison_keeps_structure_and_nontext_properties_exact(self):
        from scripts.check_word import word_math_roles

        before = [{"fraction": [["−x"], ["y"]], "type": "bar"}]
        after = [{"fraction": [["-x"], ["y"]], "type": "bar"}]
        self.assertEqual(word_math_roles(before), after)
        swapped = [{"fraction": [["y"], ["-x"]], "type": "bar"}]
        self.assertNotEqual(word_math_roles(before), word_math_roles(swapped))
        delimiter = [{"fence": {"open": "−", "close": "", "body": ["−x"]}}]
        self.assertEqual(
            word_math_roles(delimiter),
            [{"fence": {"open": "−", "close": "", "body": ["-x"]}}],
        )

    def test_word_layout_wrappers_do_not_hide_explicit_breaks_or_equations(self):
        from xml.etree import ElementTree as ET
        from zipfile import ZIP_DEFLATED, ZipFile

        from tests.docx_oracle import NS

        expected = [
            {
                "paragraph": {
                    "style": "Normal",
                    "content": [
                        {"text": "Before"},
                        {"math": [{"fraction": [["a"], ["b"]], "type": "bar"}]},
                        {"break": "textWrapping"},
                        {"text": "After"},
                    ],
                }
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.docx"
            convert(
                '<p>Before<math display="inline"><mfrac><mi>a</mi><mi>b</mi></mfrac></math><br>After</p>',
                path,
            )
            original = DocxOracle(path)
            self.assertEqual(original.blocks(), expected)
            root = original.document
            paragraph = root.find("w:body/w:p", NS)
            math = paragraph.find("m:oMath", NS)
            index = list(paragraph).index(math)
            paragraph.remove(math)
            wrapper = ET.Element("{" + NS["m"] + "}oMathPara")
            wrapper.append(math)
            paragraph.insert(index, wrapper)
            run = paragraph.find("w:r", NS)
            run.insert(0, ET.Element("{" + NS["w"] + "}lastRenderedPageBreak"))
            original.files["word/document.xml"] = ET.tostring(root, encoding="utf-8")
            saved = Path(tmp) / "word-style.docx"
            with ZipFile(saved, "w", ZIP_DEFLATED) as archive:
                for name, data in original.files.items():
                    archive.writestr(name, data)
            self.assertEqual(DocxOracle(saved).blocks(), expected)

    def test_explicit_asymmetric_fences_and_conditional_bars_keep_their_scope(self):
        fence = {"fence": {"open": "(", "close": "]", "body": ["a,b"]}}
        cases = [
            (
                "mathml",
                '<math><mrow><mo fence="true" form="prefix">(</mo><mi>a</mi><mo>,</mo><mi>b</mi><mo fence="true" form="postfix">]</mo></mrow></math>',
                [fence],
            ),
            ("latex", r"\left(a,b\right]_i", [{"sub": [[fence], ["i"]]}]),
            (
                "latex",
                r"\left(A|B\right)",
                [{"fence": {"open": "(", "close": ")", "body": ["A|B"]}}],
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            for frontend, source_text, expected in cases:
                with self.subTest(frontend=frontend, source=source_text):
                    path = Path(tmp) / "fence.docx"
                    getattr(MathmlToDocx(), "parse_" + frontend)(source_text).save(
                        str(path)
                    )
                    self.assertEqual(DocxOracle(path).equations(), [expected])
