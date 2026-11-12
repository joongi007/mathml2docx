"""Verify actual LibreOffice math rendering and export DOCX examples to PDF."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

from docx import Document

from mathml2docx import mathml_to_omml

MATHML = "http://www.w3.org/1998/Math/MathML"
OMML = "http://schemas.openxmlformats.org/officeDocument/2006/math"
PROBE = "2718281828459045235"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPECTATIONS = ROOT / "tests/fixtures/example_equation_counts.json"


def source_equations(path):
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return [
        any((t.text or "").strip() for t in node.iter("{" + OMML + "}t"))
        for node in root.iter("{" + OMML + "}oMath")
    ]


def expected_source_equations(path, expected_counts):
    """Catch conversion-time deletion/duplication before viewer round-tripping."""
    if path.stem not in expected_counts:
        raise ValueError("No independently authored equation count for " + path.name)
    equations = source_equations(path)
    expected = expected_counts[path.stem]
    if len(equations) != expected:
        raise AssertionError(
            "Expected "
            + str(expected)
            + " equations from input in "
            + path.name
            + "; found "
            + str(len(equations))
        )
    if not all(equations):
        raise AssertionError("Empty equation in generated source: " + path.name)
    return equations


def verify_fodt(path, expected):
    root = ET.parse(str(path)).getroot()
    equations = list(root.iter("{" + MATHML + "}math"))
    if len(equations) != len(expected):
        raise RuntimeError(
            "LibreOffice imported "
            + str(len(equations))
            + " of "
            + str(len(expected))
            + " equations in "
            + path.name
            + ". Install libreoffice-writer AND libreoffice-math."
        )
    tokens = {"{" + MATHML + "}" + name for name in ("mi", "mn", "mo", "mtext", "ms")}
    for number, (node, nonempty) in enumerate(zip(equations, expected), 1):
        if nonempty and not any(
            t.tag in tokens and (t.text or "").strip() for t in node.iter()
        ):
            raise RuntimeError(
                "LibreOffice imported an empty equation "
                + str(number)
                + " in "
                + path.name
            )
    return len(equations)


def office_export(soffice, profile, kind, output, files):
    subprocess.run(
        [
            soffice,
            "-env:UserInstallation=" + profile.as_uri(),
            "--headless",
            "--convert-to",
            kind,
            "--outdir",
            str(output),
            *[str(p.resolve()) for p in files],
        ],
        check=True,
        timeout=max(120, 15 * len(files)),
    )
    suffix = kind.split(":", 1)[0]
    missing = [
        p.stem for p in files if not (output / (p.stem + "." + suffix)).is_file()
    ]
    if missing:
        raise RuntimeError(
            "LibreOffice did not produce " + suffix + ": " + ", ".join(missing)
        )


def render(
    soffice, pdftotext, files, output, force=False, expectations=DEFAULT_EXPECTATIONS
):
    manifest = json.loads(expectations.read_text(encoding="utf-8"))
    expected_counts = {
        name: entry["equations"] for name, entry in manifest["documents"].items()
    }
    expected_inputs = {
        path: expected_source_equations(path, expected_counts) for path in files
    }
    output.mkdir(parents=True, exist_ok=True)
    for path in files:
        if (output / (path.stem + ".pdf")).exists() and not force:
            raise FileExistsError(
                "Preview already exists: " + path.stem + "; use --force to replace"
            )
    version = subprocess.check_output(
        [soffice, "--version"], universal_newlines=True
    ).strip()
    with tempfile.TemporaryDirectory(prefix="mathml2docx-render-") as tmp:
        stage = Path(tmp)
        profile = stage / "profile"
        document = Document()
        document.add_paragraph("Math rendering probe")
        document.add_paragraph()._p.append(
            mathml_to_omml("<math><mn>" + PROBE + "</mn></math>")
        )
        probe = stage / "mathml2docx-probe.docx"
        document.save(str(probe))
        office_export(soffice, profile, "pdf", stage, [probe])
        office_export(soffice, profile, "fodt", stage, [probe])
        verify_fodt(stage / "mathml2docx-probe.fodt", [True])
        text = subprocess.check_output(
            [pdftotext, str(stage / "mathml2docx-probe.pdf"), "-"],
            universal_newlines=True,
        )
        if PROBE not in re.sub(r"\s+", "", text):
            raise RuntimeError(
                "LibreOffice PDF math probe is blank. Install libreoffice-math and math fonts; PDF export success alone is insufficient."
            )
        office_export(soffice, profile, "pdf", stage, files)
        office_export(soffice, profile, "fodt", stage, files)
        report = []
        for source in files:
            count = verify_fodt(
                stage / (source.stem + ".fodt"), expected_inputs[source]
            )
            report.append(
                dict(file=source.name, equations=count, pdf=(source.stem + ".pdf"))
            )
        # Publish only after all checks pass, so stale PDFs cannot satisfy checks.
        for source in files:
            shutil.copy2(
                stage / (source.stem + ".pdf"), output / (source.stem + ".pdf")
            )
        (output / "libreoffice-report.json").write_text(
            json.dumps(
                dict(version=version, pdf_math_probe=True, documents=report), indent=2
            )
            + "\n",
            encoding="utf-8",
        )
    print(
        "Verified LibreOffice PDF math probe and",
        sum(p["equations"] for p in report),
        "equations in",
        len(files),
        "documents:",
        output,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--soffice", default=shutil.which("soffice") or shutil.which("libreoffice")
    )
    parser.add_argument("--pdftotext", default=shutil.which("pdftotext"))
    parser.add_argument("--input", type=Path, default=Path("examples/output"))
    parser.add_argument(
        "--output", type=Path, default=Path("examples/output/libreoffice-review")
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--expectations",
        type=Path,
        default=DEFAULT_EXPECTATIONS,
        help="Independent input equation-count manifest",
    )
    args = parser.parse_args()
    if not args.soffice or not args.pdftotext:
        parser.error(
            "Install LibreOffice Writer + Math and Poppler (pdftotext), or supply executable paths"
        )
    files = sorted(args.input.glob("[0-9][0-9]_*.docx"))
    if not files:
        parser.error("No examples found; run python -m examples.run_all first")
    render(
        args.soffice,
        args.pdftotext,
        files,
        args.output.resolve(),
        args.force,
        args.expectations,
    )


if __name__ == "__main__":
    main()
