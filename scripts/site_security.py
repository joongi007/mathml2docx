"""Allow-list public documentation HTML and confine generated preview frames."""

import re
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

SITE_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data:; frame-src 'self'; connect-src 'self'; "
    "base-uri 'none'; form-action 'none'; object-src 'none'"
)


def sanitize_document(html):
    import nh3

    tags = set(nh3.ALLOWED_TAGS) | {
        "div",
        "span",
        "section",
        "details",
        "summary",
        "iframe",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
    }
    attrs = {
        "*": {"id", "class", "title", "lang", "dir"},
        "a": {"href", "name"},
        "img": {"src", "alt", "width", "height", "loading"},
        "th": {"colspan", "rowspan", "scope"},
        "td": {"colspan", "rowspan"},
        "ol": {"start"},
        "li": {"value"},
        "code": {"class"},
        "details": {"open"},
        "iframe": {"src", "title", "loading", "sandbox", "referrerpolicy"},
    }
    cleaned = nh3.clean(
        html,
        tags=tags,
        attributes=attrs,
        clean_content_tags={"script", "style", "svg", "math", "object", "embed"},
        url_schemes={"https", "http", "mailto"},
    )
    soup = BeautifulSoup(cleaned, "html.parser")
    for frame in soup.find_all("iframe"):
        src = frame.get("src", "")
        # Source-relative paths, before rewrite_links moves documentation pages.
        if not re.fullmatch(
            r"\.\./assets/(?:inputs|pdf-pages)/[0-9]{2}_[a-z_]+\.html", src
        ):
            frame.decompose()
            continue
        frame["sandbox"] = ""
        frame["loading"] = "lazy"
        frame["referrerpolicy"] = "no-referrer"
    for image in soup.find_all("img", src=True):
        parts = urlsplit(image["src"])
        if parts.scheme or parts.netloc:
            # Documentation images are built locally, not fetched from readers.
            del image["src"]
    return str(soup)
