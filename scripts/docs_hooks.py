"""Add links to the equivalent page in each documentation language."""

import json
import posixpath
from pathlib import Path

LANGUAGES = {"en": ("English", ""), "ko": ("한국어", "ko/")}
SITE_URL = "https://joongi007.github.io/mathml2docx/"


def on_env(env, config, **kwargs):
    # The bundled theme has no Korean catalog. Reuse its translation blocks;
    # Jinja provides these without adding Babel or another localization plugin.
    if config.extra["language"] == "ko":
        catalog = json.loads(
            (Path(__file__).resolve().parents[1] / "docs_theme/ko.json").read_text(
                encoding="utf-8"
            )
        )
        env.add_extension("jinja2.ext.i18n")
        env.install_gettext_callables(
            lambda message: catalog.get(message, message),
            lambda singular, plural, count: catalog.get(
                singular if count == 1 else plural, singular if count == 1 else plural
            ),
        )
    return env


def on_page_context(context, page, config, **kwargs):
    language = config.extra["language"]
    current = LANGUAGES[language][1] + page.url
    context["languages"] = [
        {
            "code": code,
            "label": label,
            "current": code == language,
            "href": posixpath.relpath(prefix + page.url or ".", current or ".") + "/",
            "absolute_url": SITE_URL + prefix + page.url,
        }
        for code, (label, prefix) in LANGUAGES.items()
    ]
    return context
