# ruff: noqa: F401
from .h2d import HtmlToDocx
from .math import (
    MathMLFallbackWarning,
    UnsupportedMathMLError,
    latex_to_omml,
    mathml_to_omml,
)
from .styles import ParagraphStyle, TableStyle
from .wrapper import MathmlToDocx

__version__ = "1.0.2"


def convert(html, output=None, **options):
    """Convert HTML to a Document, optionally saving it to an exact output path."""
    return MathmlToDocx(**options).convert(html, output)
