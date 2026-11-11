"""Validate equations using externally supplied ECMA-376 Transitional schemas.

No schema is bundled or fetched by this script. See docs/11-validation.md for
the official sources, preparation, scope, and why XSD success is insufficient.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.advanced_math import CATALOG as ADVANCED  # noqa: E402
from examples.advanced_math import source as advanced_source  # noqa: E402
from examples.math_corpus import LATEX, SHOWCASE, generated_cases  # noqa: E402
from mathml2docx import mathml_to_omml  # noqa: E402
from mathml2docx.math import latex_to_omml  # noqa: E402

MATH = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WORD = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def load_schema(directory, namespace, filename):
    # The published ECMA schemas import XML's namespace without schemaLocation.
    # Preload its official declaration in a wrapper; keep originals unmodified.
    wrapper = etree.Element("{http://www.w3.org/2001/XMLSchema}schema")
    for ns, name in [(XML, "xml.xsd"), (namespace, filename)]:
        etree.SubElement(
            wrapper,
            "{http://www.w3.org/2001/XMLSchema}import",
            namespace=ns,
            schemaLocation=(directory / name).as_uri(),
        )
    return etree.XMLSchema(wrapper)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schemas", type=Path, required=True)
    parser.add_argument("--docx-dir", type=Path, default=ROOT / "examples/output")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    schemas = args.schemas.resolve()
    math_schema = load_schema(schemas, MATH, "shared-math.xsd")
    word_schema = load_schema(schemas, WORD, "wml.xsd")
    count = 0
    for name, body in SHOWCASE + [(n, b) for n, b, _ in generated_cases()]:
        try:
            math_schema.assertValid(mathml_to_omml("<math>" + body + "</math>"))
        except etree.DocumentInvalid as exc:
            raise RuntimeError("Invalid equation: " + name) from exc
        count += 1
    for source in LATEX:
        math_schema.assertValid(latex_to_omml(source))
        count += 1
    for entry in ADVANCED:
        convert = mathml_to_omml if entry["format"] == "mathml" else latex_to_omml
        math_schema.assertValid(convert(advanced_source(entry)))
        count += 1
    # Negative control: a schema validator must reject denominator before numerator.
    invalid = etree.fromstring(
        (
            '<m:oMath xmlns:m="' + MATH + '"><m:f><m:den/><m:num/></m:f></m:oMath>'
        ).encode()
    )
    if math_schema.validate(invalid):
        raise RuntimeError("Schema negative control unexpectedly accepted invalid OMML")
    documents = 0
    document_equations = 0
    for path in sorted(args.docx_dir.glob("[0-9][0-9]_*.docx")):
        with ZipFile(path) as archive:
            root = etree.fromstring(archive.read("word/document.xml"))
        for math in root.iter("{" + MATH + "}oMath"):
            math_schema.assertValid(math)
            document_equations += 1
        # Current examples use no extension content. Remove only unused MC metadata;
        # reject any remaining undeclared extensions rather than silently filtering.
        for node in root.iter():
            node.attrib.pop("{" + MC + "}Ignorable", None)
        try:
            word_schema.assertValid(root)
        except etree.DocumentInvalid as exc:
            raise RuntimeError("Invalid main document: " + str(path)) from exc
        documents += 1
    if not documents:
        raise RuntimeError("No example documents found; run python -m examples.run_all")
    report = {
        "corpus_equations": count,
        "example_documents": documents,
        "document_equations": document_equations,
        "negative_control_rejected": True,
        "schema_sha256": {
            name: hashlib.sha256((schemas / name).read_bytes()).hexdigest()
            for name in ["shared-math.xsd", "wml.xsd", "xml.xsd"]
        },
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
