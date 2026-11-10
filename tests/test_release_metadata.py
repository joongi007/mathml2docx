"""Release gates are development checks, separate from Python 3.6 runtime APIs."""

import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_release import release_version


@unittest.skipIf(
    sys.version_info < (3, 11), "Release tooling uses Python 3.11+; CI invokes 3.14"
)
class ReleaseMetadataTests(unittest.TestCase):
    def prepare(self, root, project, module=None):
        (root / "pyproject.toml").write_text(
            '[project]\nversion = "' + project + '"\n', encoding="utf-8"
        )
        (root / "mathml2docx").mkdir(exist_ok=True)
        (root / "mathml2docx/__init__.py").write_text(
            '__version__ = "' + (project if module is None else module) + '"\n',
            encoding="utf-8",
        )

    def test_stable_and_candidate_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for version, prerelease in [
                ("1.0.0", False),
                ("1.0.0rc1", True),
                ("1.0.0.dev1", True),
            ]:
                with self.subTest(version=version):
                    self.prepare(root, version)
                    self.assertEqual(
                        release_version(root, "v" + version, prerelease), version
                    )

    def test_mismatched_versions_tags_and_release_types_are_rejected(self):
        cases = [
            ("1.0.0", "0.1.3", "v1.0.0", False),
            ("1.0.0", None, "v1.0.1", False),
            ("1.0.0", None, "v1.0.0", True),
            ("1.0.0rc1", None, "v1.0.0rc1", False),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for project, module, tag, prerelease in cases:
                with self.subTest(
                    project=project, module=module, tag=tag, prerelease=prerelease
                ):
                    self.prepare(root, project, module)
                    with self.assertRaises(ValueError):
                        release_version(root, tag, prerelease)
