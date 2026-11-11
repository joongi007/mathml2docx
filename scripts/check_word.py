"""Read, render, and resave generated examples with locally installed Windows Word.

Requires Windows PowerShell and desktop Microsoft Word (also usable from WSL).
The source documents are opened read-only. All new files go to --output, and
existing review files are refused. No Office installation is bundled or required
by the converter itself.
"""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORD_COMMAND = r"""
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$jobs = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('JOBS_BASE64')) | ConvertFrom-Json
$word = $null
$reports = @()
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    foreach ($job in $jobs) {
        $document = $null
        try {
            $document = $word.Documents.Open($job.source, $false, $true, $false)
            $equations = $document.OMaths.Count
            $pages = $document.ComputeStatistics(2)
            $document.ExportAsFixedFormat($job.pdf, 17)
            $document.SaveAs2($job.roundtrip, 16)
            $reports += [PSCustomObject]@{
                file = $job.name
                word_version = $word.Version
                editable_equations = $equations
                pages = $pages
            }
        } finally {
            if ($null -ne $document) {
                $document.Close(0)
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
            }
        }
    }
} finally {
    if ($null -ne $word) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
}
ConvertTo-Json -InputObject $reports -Depth 5
"""


def windows_path(path):
    value = str(path.resolve())
    if os.name == "nt":
        return value
    match = re.fullmatch(r"/mnt/([a-zA-Z])/(.*)", value)
    if match:
        return match[1].upper() + ":\\" + match[2].replace("/", "\\")
    raise ValueError("Word checks require Windows paths or a WSL /mnt/<drive>/ path")


def word_math_roles(value):
    """Word rewrites U+2212 minus to ASCII '-' in math text when saving.

    Limit this equivalence to text inside mathematical sequences. Delimiter,
    accent, and formatting properties remain exact; document text is untouched.
    Converter-to-answer tests continue to compare their original Unicode text.
    """
    if isinstance(value, list):
        return [
            item.replace("−", "-") if isinstance(item, str) else word_math_roles(item)
            for item in value
        ]
    if isinstance(value, dict):
        return {key: word_math_roles(item) for key, item in value.items()}
    return value


def word_document_blocks(document):
    """Resolve locale-dependent style IDs and normalize only mathematical minus."""
    from xml.etree import ElementTree as ET

    from tests.docx_oracle import NS

    root = ET.fromstring(document.files["word/styles.xml"])
    styles = {
        node.get("{" + NS["w"] + "}styleId"): node.find("w:name", NS)
        .get("{" + NS["w"] + "}val")
        .casefold()
        for node in root.findall("w:style", NS)
        if node.find("w:name", NS) is not None
    }

    def normalize(value):
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, dict):
            return {
                key: word_math_roles(item)
                if key == "math"
                else styles.get(item, item.casefold())
                if key == "style"
                else normalize(item)
                for key, item in value.items()
            }
        return value

    return normalize(document.blocks())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "examples/output")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--examples", nargs="+")
    parser.add_argument("--powershell", default="powershell.exe")
    parser.add_argument("--check-blocks", action="store_true")
    args = parser.parse_args()
    files = sorted(args.input.glob("[0-9][0-9]_*.docx"))
    if args.examples:
        files = [p for p in files if p.stem in args.examples]
        if {p.stem for p in files} != set(args.examples):
            raise ValueError("Some requested examples are missing")
    if not files:
        raise ValueError("Generate examples before running the Word check")
    args.output.mkdir(parents=True, exist_ok=True)
    jobs = []
    for source in files:
        pdf = args.output / (source.stem + ".pdf")
        roundtrip = args.output / source.name
        if pdf.exists() or roundtrip.exists():
            raise FileExistsError("Use a fresh output directory: " + str(args.output))
        jobs.append(
            {
                "name": source.name,
                "source": windows_path(source),
                "pdf": windows_path(pdf),
                "roundtrip": windows_path(roundtrip),
            }
        )
    data = base64.b64encode(json.dumps(jobs).encode("utf-8")).decode("ascii")
    result = subprocess.run(
        [
            args.powershell,
            "-NoProfile",
            "-NonInteractive",
            "-Command",
            WORD_COMMAND.replace("JOBS_BASE64", data),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    if result.returncode:
        raise RuntimeError("Word check failed:\n" + result.stdout + result.stderr)
    reports = json.loads(result.stdout)
    sys.path.insert(0, str(ROOT))
    from tests.docx_oracle import DocxOracle

    for source in files:
        original_document = DocxOracle(source)
        saved_document = DocxOracle(args.output / source.name)
        original = original_document.equations()
        saved = saved_document.equations()
        if word_math_roles(original) != word_math_roles(saved):
            raise AssertionError(
                "Word resave changed mathematical roles: " + source.name
            )
        report = next(r for r in reports if r["file"] == source.name)
        if report["editable_equations"] != len(original):
            raise AssertionError("Word equation count mismatch: " + source.name)
        report["saved_equation_roles_match"] = True
        if args.check_blocks:
            if word_document_blocks(original_document) != word_document_blocks(
                saved_document
            ):
                raise AssertionError(
                    "Word resave changed selected document properties: " + source.name
                )
            report["saved_document_blocks_match"] = True
        report["raw_equations_identical"] = original == saved
        report["minus_spelling_equivalence"] = (
            "U+2212 and ASCII hyphen-minus in math sequences only"
        )
    (args.output / "word-report.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
