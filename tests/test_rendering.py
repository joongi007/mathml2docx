"""A successful process exit must not hide absent LibreOffice formula objects."""

import tempfile
import unittest
from pathlib import Path

from scripts.render_examples import verify_fodt


class LibreOfficeImportTests(unittest.TestCase):
    def test_missing_and_empty_formula_objects_are_rejected(self):
        prefix = '<document xmlns:m="http://www.w3.org/1998/Math/MathML">'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "output.fodt"
            for body in (
                "",
                "<m:math/>",
                "<m:math><m:annotation>hidden source</m:annotation></m:math>",
            ):
                with self.subTest(body=body), self.assertRaises(RuntimeError):
                    path.write_text(prefix + body + "</document>")
                    verify_fodt(path, [True])
            path.write_text(prefix + "<m:math><m:mi>x</m:mi></m:math></document>")
            self.assertEqual(verify_fodt(path, [True]), 1)
            with self.assertRaises(RuntimeError):
                verify_fodt(path, [True, True])
