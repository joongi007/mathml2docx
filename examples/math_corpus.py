"""Original mathematical examples and deterministic composition corpus.

The small expression model describes mathematical roles, independently of OMML.
Its encoder emits only MathML. Tests interpret the resulting OMML separately.
No third-party equation datasets or Office stylesheets are copied here.
"""

import json
import random
from html import escape
from pathlib import Path

# Input files are text so reviewers can inspect them without Word.
CORPUS = Path(__file__).resolve().parent / "assets/math-corpus"
CATALOG = json.loads((CORPUS / "catalog.json").read_text(encoding="utf-8"))
SHOWCASE = []
LATEX = []
for entry in CATALOG:
    source = (CORPUS / entry["file"]).read_text(encoding="utf-8").strip()
    if entry["format"] == "mathml":
        if not source.startswith("<math>") or not source.endswith("</math>"):
            raise ValueError("Expected an explicit math root: " + entry["file"])
        SHOWCASE.append(
            (entry["title"], source[len("<math>") : -len("</math>")].strip())
        )
    else:
        LATEX.append(source)


def generated_cases(count=240):
    """Yield (id, MathML, expected role tree), with a reproducible seed."""
    rng = random.Random(376)

    def expression(depth):
        if depth == 0 or rng.randrange(5) == 0:
            return rng.choice(["x", "y", "α", "β", "0", "1", "2", "∞", "𝛼"])
        kind = rng.choice(
            [
                "fraction",
                "sup",
                "sub",
                "subsup",
                "sqrt",
                "root",
                "row",
                "fence",
                "matrix",
                "lower",
                "upper",
                "phantom",
            ]
        )
        n = {
            "subsup": 3,
            "sqrt": 1,
            "phantom": 1,
            "fence": 1,
            "row": 3,
            "matrix": 4,
        }.get(kind, 2)
        return (kind,) + tuple(expression(depth - 1) for _ in range(n))

    for index in range(count):
        model = expression(4)
        yield f"generated-{index:03d}", encode_mathml(model), model


def encode_mathml(model):
    if isinstance(model, str):
        return "<mi>" + escape(model) + "</mi>"
    kind, children = model[0], model[1:]
    body = "".join(encode_mathml(child) for child in children)
    if kind == "matrix":
        cells = ["<mtd>" + encode_mathml(c) + "</mtd>" for c in children]
        return (
            "<mtable><mtr>"
            + "".join(cells[:2])
            + "</mtr><mtr>"
            + "".join(cells[2:])
            + "</mtr></mtable>"
        )
    tags = {
        "fraction": "mfrac",
        "sup": "msup",
        "sub": "msub",
        "subsup": "msubsup",
        "sqrt": "msqrt",
        "root": "mroot",
        "row": "mrow",
        "fence": "mfenced",
        "lower": "munder",
        "upper": "mover",
        "phantom": "mphantom",
    }
    return "<" + tags[kind] + ">" + body + "</" + tags[kind] + ">"
