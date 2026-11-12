"""Explicit recovery: preserve MathML source or embed a known rendered image."""

from pathlib import Path

from mathml2docx import MathmlToDocx

from .support import save

# This sample ships two pre-rendered expressions. Replace this lookup with your
# own trusted renderer to handle other notations; do not substitute an unrelated image.
BOXED_X = (
    '<math alttext="boxed x"><menclose notation="box"><mi>x</mi></menclose></math>'
)
CIRCLED_X = (
    '<math alttext="circled x"><menclose notation="circle"><mi>x</mi></menclose></math>'
)


def fallback(source, error):
    if source == CIRCLED_X:
        return (Path(__file__).parent / "assets/circled-x.png").read_bytes()
    if source == BOXED_X:
        return (Path(__file__).parent / "assets/boxed-x.png").read_bytes()
    return "[Unconverted MathML] " + source


parser = MathmlToDocx(math_target="libreoffice", mathml_fallback=fallback)
document = parser.convert(
    "<h1>Recovering unsupported notation</h1><p>The following circled x is an image: "
    + CIRCLED_X
    + ".</p>"
)
parser.add_html_to_document(
    "<p>A boxed x uses the same explicit recovery: " + BOXED_X + ".</p>", document
)
parser.add_html_to_document(
    "<p>Unrecognized input remains visible as source:</p><math><unknown><mi>y</mi></unknown></math>",
    document,
)
save(document, "29_math_fallbacks.docx")
