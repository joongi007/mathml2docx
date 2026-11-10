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


@unittest.skipIf(sys.version_info < (3, 11), "Release tooling uses Python 3.11+")
class PublishingFlowTests(unittest.TestCase):
    def test_candidates_have_matching_metadata_and_unique_retry_versions(self):
        from scripts.prepare_testpypi import prepare_candidate

        versions = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for attempt in (1, 2):
                ReleaseMetadataTests().prepare(root, "1.0.0")
                candidate = prepare_candidate(root, 42, attempt)
                versions.append(candidate)
                self.assertEqual(release_version(root), candidate)
        self.assertEqual(versions, ["1.0.0.dev42001", "1.0.0.dev42002"])

    def test_candidate_rejects_invalid_base_or_identifiers(self):
        from scripts.prepare_testpypi import prepare_candidate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for base, run_id, attempt in (
                ("1.0.0rc1", 42, 1),
                ("1.0.0.dev1", 42, 1),
                ("1.0.0.post1", 42, 1),
                ("1.0.0+local", 42, 1),
                ("1.0.0", 0, 1),
                ("1.0.0", 42, 0),
                ("1.0.0", 42, 1000),
            ):
                with self.subTest(base=base, run_id=run_id, attempt=attempt):
                    ReleaseMetadataTests().prepare(root, base)
                    with self.assertRaises(ValueError):
                        prepare_candidate(root, run_id, attempt)
                    self.assertEqual(release_version(root), base)

    def test_final_tag_requires_successful_installation_on_the_exact_master_commit(
        self,
    ):
        from copy import deepcopy

        from scripts.check_testpypi_run import verified_run

        sha = "a" * 40
        run = {
            "head_sha": sha,
            "head_branch": "master",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "path": ".github/workflows/testpypi.yml",
            "head_repository": {"full_name": "joongi007/mathml2docx"},
        }
        self.assertEqual(verified_run([run], sha, "joongi007/mathml2docx"), run)
        for key, value in (
            ("head_sha", "b" * 40),
            ("head_branch", "develop"),
            ("event", "pull_request"),
            ("status", "in_progress"),
            ("conclusion", "failure"),
            ("conclusion", "skipped"),
            ("conclusion", "cancelled"),
            ("path", ".github/workflows/python-app.yml"),
            ("head_repository", {"full_name": "another/fork"}),
        ):
            with self.subTest(key=key, value=value):
                changed = deepcopy(run)
                changed[key] = value
                with self.assertRaises(ValueError):
                    verified_run([changed], sha, "joongi007/mathml2docx")
        with self.assertRaises(ValueError):
            verified_run([], sha, "joongi007/mathml2docx")
        run["event"] = "workflow_dispatch"
        self.assertEqual(verified_run([run], sha, "joongi007/mathml2docx"), run)

    def test_testpypi_file_must_match_hash_version_filename_and_official_host(self):
        from copy import deepcopy

        from scripts.check_testpypi_install import distribution_url

        version = "1.0.0.dev42001"
        filename = "mathml2docx-" + version + "-py3-none-any.whl"
        sha256 = "a" * 64
        url = "https://test-files.pythonhosted.org/packages/example.whl"
        metadata = {
            "info": {"version": version},
            "urls": [
                {
                    "filename": filename,
                    "packagetype": "bdist_wheel",
                    "digests": {"sha256": sha256},
                    "yanked": False,
                    "url": url,
                }
            ],
        }
        self.assertEqual(
            distribution_url(metadata, version, filename, sha256),
            url + "#sha256=" + sha256,
        )
        for key, value in (
            ("filename", "another.whl"),
            ("packagetype", "sdist"),
            ("digests", {"sha256": "b" * 64}),
            ("yanked", True),
            ("url", "https://example.com/example.whl"),
            ("url", "http://test-files.pythonhosted.org/example.whl"),
            ("url", "https://user@test-files.pythonhosted.org/example.whl"),
            ("url", url + "#sha256=other"),
        ):
            with self.subTest(key=key, value=value):
                changed = deepcopy(metadata)
                changed["urls"][0][key] = value
                with self.assertRaises(ValueError):
                    distribution_url(changed, version, filename, sha256)
        with self.assertRaises(ValueError):
            distribution_url(metadata, "1.0.0", filename, sha256)

    def test_index_visibility_retry_is_bounded(self):
        import io
        import json
        from unittest.mock import patch
        from urllib.error import HTTPError

        from scripts.check_testpypi_install import published_wheel

        version = "1.0.0.dev42001"
        wheel = Path("candidate.whl")
        metadata = {
            "info": {"version": version},
            "urls": [
                {
                    "filename": wheel.name,
                    "packagetype": "bdist_wheel",
                    "digests": {"sha256": "a" * 64},
                    "url": "https://test-files.pythonhosted.org/candidate.whl",
                }
            ],
        }
        not_found = HTTPError("https://test.pypi.org", 404, "pending", {}, None)
        with patch(
            "scripts.check_testpypi_install.urlopen",
            side_effect=[not_found, io.BytesIO(json.dumps(metadata).encode())],
        ), patch("scripts.check_testpypi_install.time.sleep") as sleep:
            url = published_wheel(version, wheel, "a" * 64)
            self.assertIn("#sha256=", url)
            sleep.assert_called_once_with(5)
        with patch(
            "scripts.check_testpypi_install.urlopen", side_effect=not_found
        ), patch("scripts.check_testpypi_install.time.sleep"):
            with self.assertRaises(RuntimeError):
                published_wheel(version, wheel, "a" * 64)
