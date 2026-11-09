"""Execute the published examples and verify their observable document content."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from docx import Document

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_all_examples(self):
        catalog = json.loads(
            (ROOT / "examples/catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(catalog), {p.stem for p in (ROOT / "examples").glob("[0-9][0-9]_*.py")}
        )
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, MATHML2DOCX_EXAMPLE_OUTPUT=tmp)
            result = subprocess.run(
                [sys.executable, "-m", "examples.run_all"],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in catalog:
                with self.subTest(example=name):
                    path = Path(tmp) / (name + ".docx")
                    with ZipFile(path) as archive:
                        self.assertIsNone(archive.testzip())
                    self.assertTrue(Document(path)._element.body is not None)
            tables = Document(Path(tmp) / "08_tables.docx").tables[0]
            self.assertIs(tables.cell(1, 0)._tc, tables.cell(2, 0)._tc)
            self.assertEqual(tables.cell(3, 0).tables[0].cell(0, 0).text, "Inner cell")
            math = Document(Path(tmp) / "13_mathml.docx")
            self.assertTrue(math._element.xpath("//m:f"))
            self.assertTrue(math._element.xpath("//m:m"))
            self.assertEqual(
                Document(Path(tmp) / "15_markers.docx").paragraphs[0].text,
                "Dear Alex, welcome.",
            )
            self.assertEqual(
                Document(Path(tmp) / "16_bookmarks.docx").paragraphs[0].text,
                "Before new result after.",
            )
            self.assertEqual(
                Document(Path(tmp) / "17_docxtpl.docx").paragraphs[0].text, "Hello Alex"
            )
            disabled = Document(Path(tmp) / "18_options.docx")
            self.assertFalse(disabled.tables)
            self.assertFalse(disabled.inline_shapes)
            self.assertFalse(disabled._element.xpath("//m:oMath"))
            links = Document(Path(tmp) / "20_links.docx")
            self.assertTrue(links._element.xpath("//w:bookmarkStart"))
            self.assertTrue(links._element.xpath("//w:hyperlink[@w:anchor]"))
            report = Document(Path(tmp) / "21_report.docx")
            self.assertEqual(len(report.tables), 1)
            self.assertEqual(len(report.inline_shapes), 1)
            self.assertTrue(report._element.xpath("//m:f"))
