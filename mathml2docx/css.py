"""Static CSS cascade for document conversion (never fetches resources)."""

import warnings
from xml.etree.ElementTree import Element

import cssselect2
import tinycss2
from bs4 import Tag

INHERITED = {
    "color",
    "font-family",
    "font-size",
    "font-weight",
    "font-style",
    "text-align",
    "white-space",
    "line-height",
    "visibility",
    "text-decoration",
    "text-decoration-line",
    "list-style-type",
}


def declarations(source):
    for item in tinycss2.parse_declaration_list(
        source, skip_comments=True, skip_whitespace=True
    ):
        if item.type != "declaration":
            continue
        value = tinycss2.serialize(item.value).strip()
        name = item.lower_name
        if name in {"margin", "padding"}:
            fields = value.split()
            if 1 <= len(fields) <= 4:
                sides = (
                    fields * 4
                    if len(fields) == 1
                    else [fields[0], fields[1], fields[0], fields[1]]
                    if len(fields) == 2
                    else [fields[0], fields[1], fields[2], fields[1]]
                    if len(fields) == 3
                    else fields
                )
                for side, field in zip(["top", "right", "bottom", "left"], sides):
                    yield name + "-" + side, field, item.important
                continue
        yield name, value, item.important


def computed_styles(soup, stylesheet="", loader=None):
    matcher = cssselect2.Matcher()
    order = 0

    def add_sheet(source, depth=0):
        nonlocal order
        if depth > 8:
            raise ValueError("CSS import nesting exceeds 8")
        for rule in tinycss2.parse_stylesheet(
            source, skip_comments=True, skip_whitespace=True
        ):
            if rule.type == "at-rule":
                condition = tinycss2.serialize(rule.prelude).strip()
                if (
                    rule.lower_at_keyword == "media"
                    and condition in {"all", "print"}
                    and rule.content
                ):
                    add_sheet(tinycss2.serialize(rule.content), depth + 1)
                elif rule.lower_at_keyword == "import" and loader:
                    tokens = [t for t in rule.prelude if t.type != "whitespace"]
                    if tokens:
                        token = tokens[0]
                        href = getattr(token, "value", None)
                        if token.type == "function" and token.lower_name == "url":
                            href = (
                                tinycss2.serialize(token.arguments).strip().strip("\"'")
                            )
                        if href:
                            add_sheet(loader(href), depth + 1)
                continue
            if rule.type != "qualified-rule":
                continue
            try:
                selectors = cssselect2.compile_selector_list(rule.prelude)
            except cssselect2.SelectorError:
                warnings.warn(
                    "Unsupported CSS selector: " + tinycss2.serialize(rule.prelude),
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue
            order += 1
            payload = (order, list(declarations(tinycss2.serialize(rule.content))))
            for selector in selectors:
                if selector.pseudo_element is None:
                    matcher.add_selector(selector, payload)

    for tag in soup.find_all(["style", "link"]):
        if tag.name == "style" and tag.get("media", "all") in {"all", "print"}:
            add_sheet(tag.get_text())
        elif tag.name == "link" and "stylesheet" in tag.get("rel", []) and loader:
            add_sheet(loader(tag.get("href", "")))
    add_sheet(stylesheet)
    pairs = {}

    def tree(tag):
        attrs = {
            k: " ".join(v) if isinstance(v, list) else str(v)
            for k, v in tag.attrs.items()
            if v is not None
        }
        element = Element(tag.name or "html", attrs)
        pairs[id(element)] = tag
        for child in tag.children:
            if isinstance(child, Tag):
                element.append(tree(child))
        return element

    html = soup.find("html", recursive=False)
    root = tree(html) if html is not None else Element("html")
    if html is None:
        for child in soup.children:
            if isinstance(child, Tag):
                root.append(tree(child))
    computed = {}
    for wrapper in cssselect2.ElementWrapper.from_html_root(root).iter_subtree():
        tag = pairs.get(id(wrapper.etree_element))
        if tag is None:
            continue
        winners = {}
        for specificity, _, _, (source_order, entries) in matcher.match(wrapper):
            for name, value, important in entries:
                priority = (important, 0, *specificity, source_order)
                if name not in winners or priority >= winners[name][0]:
                    winners[name] = (priority, value)
        for name, value, important in declarations(tag.get("style", "")):
            priority = (important, 1, 0, 0, 0, 0)
            if name not in winners or priority >= winners[name][0]:
                winners[name] = (priority, value)
        computed[id(tag)] = {name: value for name, (_, value) in winners.items()}
    return computed
