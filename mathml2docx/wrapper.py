"""Public converter. Options reference the engine directly, without duplicate state."""

from docx import Document

from .h2d import HtmlToDocx
from .math import latex_to_mathml


class MathmlToDocx(HtmlToDocx):
    def __init__(
        self,
        fix_html=True,
        images=True,
        tables=True,
        mathml=True,
        styles=True,
        img_src_base_path=None,
        table_style=None,
        paragraph_style=None,
        *,
        image_loader=None,
        style_map=None,
        stylesheet="",
        stylesheet_loader=None,
        default_math_display="inline",
        unsupported_math="error",
        mathml_preprocessor=None,
        mathml_fallback=None,
        math_target="word",
    ):
        super().__init__()
        for name, value in {
            "fix_html": fix_html,
            "images": images,
            "tables": tables,
            "mathml": mathml,
            "styles": styles,
            "img_src_base_path": img_src_base_path,
            "image_loader": image_loader,
            "default_math_display": default_math_display,
            "unsupported_math": unsupported_math,
            "mathml_preprocessor": mathml_preprocessor,
            "mathml_fallback": mathml_fallback,
            "math_target": math_target,
        }.items():
            setattr(self.options, name, value)
        self.table_style = table_style
        self.paragraph_style = paragraph_style
        self.style_map = style_map or {}
        self.stylesheet = stylesheet
        self.stylesheet_loader = stylesheet_loader

    @property
    def options(self):
        # During base initialization the engine uses a dictionary. Keep the public
        # object compatible with both legacy keys and typed property access.
        return self._engine_options

    @options.setter
    def options(self, value):
        self._engine_options = _OptionsDict(value)

    def get_origin(self):
        return self

    def copy_settings_from(self, other):
        if not isinstance(other, HtmlToDocx):
            raise TypeError("other must be an HtmlToDocx or MathmlToDocx")
        super().copy_settings_from(other)

    def convert(self, html, output=None):
        document = self.parse_html_string(html)
        if output is not None:
            document.save(output)
        return document

    def parse_mathml(self, source):
        document = Document()
        self._add_mathml_to_document(source, document)
        return document

    def parse_latex(self, source):
        return self.parse_mathml(latex_to_mathml(source))

    def parse_markdown(self, source):
        """Convert Markdown with tables, fenced code and ~~strikethrough~~."""
        from .markdown import markdown_to_html

        return self.parse_html_string(markdown_to_html(source))

    def replace_html(self, document, marker, html):
        """Replace a unique marker, including markers split across styled runs."""
        from .templates import replace_html

        replace_html(self, document, marker, html)

    def replace_bookmark(self, document, name, html):
        """Replace a named bookmark range while preserving surrounding content."""
        from .templates import replace_bookmark

        replace_bookmark(self, document, name, html)


class _OptionsDict(dict):
    _keys = {
        "fix_html": "fix-html",
        "images": "images",
        "tables": "tables",
        "mathml": "mathml",
        "styles": "styles",
        "img_src_base_path": "img_src_base_path",
        "image_loader": "image_loader",
        "default_math_display": "default_math_display",
        "unsupported_math": "unsupported_math",
        "mathml_preprocessor": "mathml_preprocessor",
        "mathml_fallback": "mathml_fallback",
        "math_target": "math_target",
    }

    def __getattr__(self, name):
        key = self._keys.get(name)
        if key is None:
            raise AttributeError(name)
        return self[key]

    def __setattr__(self, name, value):
        key = self._keys.get(name)
        if key is None:
            raise AttributeError(name)
        self[key] = value

    def __setitem__(self, key, value):
        name = "fix_html" if key == "fix-html" else key
        if name in {
            "fix_html",
            "images",
            "tables",
            "mathml",
            "styles",
        } and not isinstance(value, bool):
            raise TypeError(f"{name} must be bool")
        if (
            name in {"image_loader", "mathml_preprocessor", "mathml_fallback"}
            and value is not None
            and not callable(value)
        ):
            raise TypeError(name + " must be callable or None")
        if name == "default_math_display" and value not in {"inline", "block"}:
            raise ValueError("default_math_display must be inline or block")
        if name == "unsupported_math" and value not in {"error", "text"}:
            raise ValueError("unsupported_math must be error or text")
        if name == "math_target" and value not in {"word", "libreoffice"}:
            raise ValueError("math_target must be word or libreoffice")
        super().__setitem__(key, value)
