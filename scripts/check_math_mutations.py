"""Check that the corpus detects representative mathematical corruption.

Each mutation runs in a temporary copy. The working tree is never modified.
This is a targeted sensitivity check, not an exhaustive mutation score.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUTATIONS = [
    (
        "accept unresolved LaTeX commands as identifiers",
        "    _reject_unresolved_latex(root)",
        "    pass  # deliberate missing backend validation",
    ),
    (
        "lose encoded mathvariant",
        "effective = encoded or variant",
        "effective = variant",
    ),
    (
        "lose root style defaults",
        'if tag in {"math", "mstyle"}:',
        'if tag == "mstyle":',
    ),
    (
        "trim nonbreaking token spaces",
        'return XML_SPACE_RUN.sub(" ", value.strip(XML_WHITESPACE))',
        'return " ".join(value.split())',
    ),
    (
        "skip structural prevalidation",
        "    validate_structure(root)",
        "    pass  # deliberate missing validation",
    ),
    (
        "drop math CSS properties",
        '            apply_math_style(part, inherited["_css"])',
        "            pass  # deliberate missing style",
    ),
    (
        "swap isotope atomic and mass numbers",
        'script(pre[0], "sub"),\n                    script(pre[1], "sup")',
        'script(pre[1], "sub"),\n                    script(pre[0], "sup")',
    ),
    (
        "drop enclosure borders",
        'visible = set(sides) if "box" in notations else set(sides) & notations',
        "visible = set()",
    ),
    (
        "detach grouped LaTeX scripts",
        "    _group_latex_fence_scripts(root)",
        "    pass  # deliberate mutation",
    ),
    (
        "collapse adjacent fence groups",
        "end = ends.get(index)",
        "end = len(items) - 1 if index in ends else None",
    ),
    (
        "swap numerator/denominator",
        'group(0, "num", script=True),\n                group(1, "den", script=True)',
        'group(1, "num", script=True),\n                group(0, "den", script=True)',
    ),
    (
        "swap root degree/radicand",
        'group(1, "deg", script=True), group(0, "e")',
        'group(0, "deg", script=True), group(1, "e")',
    ),
    (
        "swap subscript/superscript",
        'group(1, "sub", script=True),\n                    group(2, "sup", script=True)',
        'group(2, "sub", script=True),\n                    group(1, "sup", script=True)',
    ),
    ("restore unwanted binomial bar", 'if thickness != "medium"', "if False"),
    (
        "lose explicit mathvariant",
        'result["mathvariant"] = node.get("mathvariant")',
        'result["mathvariant"] = "normal"',
    ),
    (
        "lose delimiter character",
        'element("begChr", val=begin)',
        'element("begChr", val="(")',
    ),
    ("lose accent character", 'element("chr", val=accent)', 'element("chr", val="?")'),
]


def main():
    original = (ROOT / "mathml2docx/math.py").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory(prefix="mathml2docx-mutations-") as tmp:
        directory = Path(tmp)
        shutil.copytree(
            str(ROOT / "mathml2docx"),
            str(directory / "mathml2docx"),
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        for name in ["tests", "examples"]:
            (directory / name).mkdir()
            (directory / name / "__init__.py").touch()
        shutil.copy(
            str(ROOT / "tests/test_math_validation.py"),
            str(directory / "tests/test_math_validation.py"),
        )
        shutil.copy(
            str(ROOT / "examples/math_corpus.py"),
            str(directory / "examples/math_corpus.py"),
        )
        shutil.copytree(
            str(ROOT / "examples/assets/math-corpus"),
            str(directory / "examples/assets/math-corpus"),
        )
        for name in [
            "test_advanced_documents.py",
            "test_math_policies.py",
            "test_math_audit_regressions.py",
            "test_math_html_regressions.py",
            "docx_oracle.py",
        ]:
            shutil.copy(str(ROOT / "tests" / name), str(directory / "tests" / name))
        shutil.copy(
            str(ROOT / "examples/advanced_math.py"),
            str(directory / "examples/advanced_math.py"),
        )
        shutil.copytree(
            str(ROOT / "examples/assets/advanced-math"),
            str(directory / "examples/assets/advanced-math"),
        )
        (directory / "tests/fixtures").mkdir()
        shutil.copy(
            str(ROOT / "tests/fixtures/advanced_math_expectations.json"),
            str(directory / "tests/fixtures/advanced_math_expectations.json"),
        )
        # The shading regression is part of MathematicalMeaningTests, too.
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_math_validation.py::CompositionCorpusTests::test_generated_roles_with_and_without_namespace",
            "tests/test_math_validation.py::MathematicalMeaningTests",
            "tests/test_advanced_documents.py::AdvancedDocumentTests::test_advanced_saved_equations_match_independently_authored_answers",
            "tests/test_math_policies.py::MathPolicyTests::test_independent_saved_roles_for_chemistry_and_enclosures",
            "tests/test_math_audit_regressions.py",
            "tests/test_math_html_regressions.py",
        ]
        baseline = subprocess.run(
            command,
            cwd=str(directory),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        if baseline.returncode:
            raise RuntimeError("Unmodified baseline failed:\n" + baseline.stdout)
        for name, before, after in MUTATIONS:
            if original.count(before) != 1:
                raise RuntimeError(
                    "Mutation anchor changed; review sensitivity check: " + name
                )
            (directory / "mathml2docx/math.py").write_text(
                original.replace(before, after), encoding="utf-8"
            )
            result = subprocess.run(
                command,
                cwd=str(directory),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            if result.returncode != 1 or not any(
                marker in result.stdout
                for marker in ("AssertionError", "DID NOT RAISE", "FAIL:")
            ):
                raise RuntimeError(
                    "Mutation was not caught by an assertion: "
                    + name
                    + "\n"
                    + result.stdout
                )
            print("Detected:", name)
    print(f"Detected all {len(MUTATIONS)} targeted mutations")


if __name__ == "__main__":
    main()
