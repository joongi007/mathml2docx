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
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Unicode Mathematical Alphanumeric Symbols includes mapped symbol bases too:
# ∂ and ∇ have mathematical alphabet glyphs, unlike +, =, ⊃, or ∈.
# https://www.unicode.org/charts/PDF/U1D400.pdf
_MATH_ALPHABET_BASES = {
    unicodedata.normalize("NFKC", chr(code))
    for code in range(0x1D400, 0x1D800)
    if unicodedata.name(chr(code), "").startswith("MATHEMATICAL ")
}
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


def _font_aliases(documents):
    """Use declared alternate names plus one documented localized Office font."""
    from xml.etree import ElementTree as ET

    from tests.docx_oracle import NS

    # Microsoft's Korean Style Guide names Malgun Gothic (맑은고딕):
    # https://download.microsoft.com/download/5/b/6/5b62389f-4e3b-4c77-bc18-94efba2fa7bb/kor-kor-StyleGuide.pdf
    groups = [{"malgun gothic", "맑은 고딕", "맑은고딕"}]
    for document in documents:
        if "word/fontTable.xml" not in document.files:
            continue
        for font in ET.fromstring(document.files["word/fontTable.xml"]):
            names = {font.get("{" + NS["w"] + "}name", "").casefold()}
            names.update(
                node.get("{" + NS["w"] + "}val", "").casefold()
                for node in font.findall("w:altName", NS)
            )
            names.discard("")
            if names:
                groups.append(names)
    merged = []
    for group in groups:
        for previous in list(merged):
            if group & previous:
                group |= previous
                merged.remove(previous)
        merged.append(group)
    return {name: min(group) for group in merged for name in group}


class _MathFormatting:
    """Resolve properties Word may move from runs into document/style context."""

    def __init__(self, document, aliases):
        from xml.etree import ElementTree as ET

        from tests.docx_oracle import NS, value

        self.ns = NS
        self.aliases = aliases
        self.parents = {
            child: node for node in document.document.iter() for child in node
        }
        root = ET.fromstring(document.files["word/styles.xml"])
        self.styles = {
            node.get("{" + NS["w"] + "}styleId"): node
            for node in root.findall("w:style", NS)
        }
        self.normal = next(
            (
                key
                for key, node in self.styles.items()
                if node.get("{" + NS["w"] + "}type") == "paragraph"
                and node.get("{" + NS["w"] + "}default") == "1"
            ),
            "Normal",
        )
        settings = ET.fromstring(document.files["word/settings.xml"])
        math_font = value(settings, "m:mathPr/m:mathFont", "Cambria Math", "m")
        self.defaults = {
            "font_" + slot: math_font for slot in ("ascii", "hAnsi", "eastAsia", "cs")
        }
        self.defaults.update(color="auto", size_half_points="22")
        self.defaults.update(
            self.properties(root.find("w:docDefaults/w:rPrDefault/w:rPr", NS))
        )
        self.default_underline = self.underline(
            root.find("w:docDefaults/w:rPrDefault/w:rPr", NS)
        )

    def underline(self, properties):
        if properties is None:
            return None
        element = properties.find("w:u", self.ns)
        return (
            None
            if element is None
            else element.get("{" + self.ns["w"] + "}val", "single")
        )

    def style_underline(self, identifier, seen=None):
        from tests.docx_oracle import value

        seen = set() if seen is None else seen
        if identifier in seen:
            raise ValueError("Circular Word style inheritance: " + identifier)
        node = self.styles.get(identifier)
        if node is None:
            return None
        seen.add(identifier)
        parent = value(node, "w:basedOn")
        inherited = self.style_underline(parent, seen) if parent else None
        local = self.underline(node.find("w:rPr", self.ns))
        return inherited if local is None else local

    def text_underline(self, run):
        from tests.docx_oracle import value

        parent = self.parents.get(run)
        while parent is not None and parent.tag != "{" + self.ns["w"] + "}p":
            parent = self.parents.get(parent)
        result = self.default_underline or "none"
        if parent is not None:
            inherited = self.style_underline(
                value(parent, "w:pPr/w:pStyle", self.normal)
            )
            if inherited is not None:
                result = inherited
        character = value(run, "w:rPr/w:rStyle")
        if character:
            inherited = self.style_underline(character)
            if inherited is not None:
                result = inherited
        local = self.underline(run.find("w:rPr", self.ns))
        return result if local is None else local

    def properties(self, props):
        from tests.docx_oracle import enabled, value

        if props is None:
            return {}
        result = {}
        for name, tag in (("color", "color"), ("size_half_points", "sz")):
            setting = value(props, "w:" + tag)
            if setting is not None:
                result[name] = setting
        fonts = props.find("w:rFonts", self.ns)
        if fonts is not None:
            for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
                font = fonts.get("{" + self.ns["w"] + "}" + slot)
                if font:
                    result["font_" + slot] = font
        for name, tag in (("bold", "b"), ("italic", "i")):
            if props.find("w:" + tag, self.ns) is not None:
                result[name] = enabled(props, "w:" + tag)
        return result

    def style(self, identifier, seen=None):
        from tests.docx_oracle import value

        seen = set() if seen is None else seen
        if identifier in seen:
            raise ValueError("Circular Word style inheritance: " + identifier)
        node = self.styles.get(identifier)
        if node is None:
            return {}
        seen.add(identifier)
        parent = value(node, "w:basedOn")
        result = self.style(parent, seen) if parent else {}
        result.update(self.properties(node.find("w:rPr", self.ns)))
        return result

    def run(self, run):
        from tests.docx_oracle import value

        ancestors = []
        parent = self.parents.get(run)
        while parent is not None:
            ancestors.append(parent)
            parent = self.parents.get(parent)
        paragraph = next(
            (node for node in ancestors if node.tag == "{" + self.ns["w"] + "}p"), None
        )
        result = dict(self.defaults)
        if paragraph is not None:
            result.update(self.style(value(paragraph, "w:pPr/w:pStyle", self.normal)))
        for node in reversed(ancestors):
            if node.tag.startswith("{" + self.ns["m"] + "}"):
                name = node.tag.rsplit("}", 1)[-1]
                result.update(
                    self.properties(
                        node.find("m:" + name + "Pr/m:ctrlPr/w:rPr", self.ns)
                    )
                )
        character = value(run, "w:rPr/w:rStyle")
        if character:
            result.update(self.style(character))
        result.update(self.properties(run.find("w:rPr", self.ns)))
        for name, setting in list(result.items()):
            if name.startswith("font_"):
                result[name] = self.aliases.get(setting.casefold(), setting.casefold())
        return result

    def declared(self, run):
        """Properties explicitly attached to original math, not ambient text."""
        from tests.docx_oracle import value

        result = {}
        ancestors = []
        parent = self.parents.get(run)
        while parent is not None:
            ancestors.append(parent)
            parent = self.parents.get(parent)
        for node in reversed(ancestors):
            if node.tag.startswith("{" + self.ns["m"] + "}"):
                name = node.tag.rsplit("}", 1)[-1]
                result.update(
                    self.properties(
                        node.find("m:" + name + "Pr/m:ctrlPr/w:rPr", self.ns)
                    )
                )
        character = value(run, "w:rPr/w:rStyle")
        if character:
            result.update(self.style(character))
        result.update(self.properties(run.find("w:rPr", self.ns)))
        return set(result)


def _math_items(value):
    if isinstance(value, list):
        for child in value:
            for item in _math_items(child):
                yield item
    elif isinstance(value, dict):
        if "math" in value:
            yield value
        else:
            for child in value.values():
                for item in _math_items(child):
                    yield item


def word_document_blocks(document, aliases=None):
    """Resolve Word formatting context without weakening the raw DOCX oracle."""
    from xml.etree import ElementTree as ET

    from tests.docx_oracle import NS, effective_math_variant, math_alphabet

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
                else [dict(run, text=run["text"].replace("−", "-")) for run in item]
                if key == "math_runs"
                else styles.get(item, item.casefold())
                if key == "style"
                else normalize(item)
                for key, item in value.items()
            }
        return value

    blocks = normalize(document.blocks())
    context = _MathFormatting(
        document, _font_aliases([document]) if aliases is None else aliases
    )
    blocks = _ordinary_text_underlines(document, blocks, context)
    items = list(_math_items(blocks))
    equations = document.document.findall(".//m:oMath", NS)
    if len(items) != len(equations):
        raise AssertionError(
            "Word comparison could not align mathematical XML with document blocks"
        )
    for item, equation in zip(items, equations):
        formatted = []
        for run in equation.findall(".//m:r", NS):
            properties = context.run(run)
            for char in "".join(t.text or "" for t in run.findall("m:t", NS)):
                variant = effective_math_variant(run, char)
                # scr maps characters into mathematical alphabets (ISO/IEC
                # 29500-1 22.1.2.94). Canonicalize only symbols without a mapped
                # alphabet glyph; keep weight/style, nor, and mapped ∂/∇ exact.
                if (
                    not char.isalnum()
                    and math_alphabet(char) not in _MATH_ALPHABET_BASES
                ):
                    variant["script"] = "roman"
                character_properties = dict(properties)
                # Word removes duplicate field font flags when native math sty
                # expresses the same value. Contradictory flags remain visible.
                for name, marker in (("bold", "b"), ("italic", "i")):
                    if name in character_properties and character_properties[name] == (
                        marker in variant["style"]
                    ):
                        character_properties.pop(name)
                token = math_alphabet(char).replace("−", "-")
                if (
                    formatted
                    and formatted[-1]["format"] == character_properties
                    and formatted[-1]["variant"] == variant
                ):
                    formatted[-1]["text"] += token
                else:
                    formatted.append(
                        {
                            "text": token,
                            "format": character_properties,
                            "variant": variant,
                        }
                    )
        item["math_runs"] = formatted
    return blocks


def _ordinary_text_underlines(document, blocks, context):
    """Distinguish an omitted default from an inherited character underline."""
    from tests.docx_oracle import NS

    characters = []
    for run in document.document.findall(".//w:r", NS):
        underline = context.text_underline(run)
        for node in run.findall("w:t", NS):
            characters.extend((char, underline) for char in (node.text or ""))
    states = iter(characters)

    def visit(value):
        if isinstance(value, dict):
            if "math" in value:
                return value
            return {key: visit(item) for key, item in value.items()}
        if not isinstance(value, list):
            return value
        result = []
        for item in value:
            if not isinstance(item, dict) or "text" not in item:
                result.append(visit(item))
                continue
            for char in item["text"]:
                state = next(states, None)
                if state is None or state[0] != char:
                    raise AssertionError(
                        "Word comparison could not align ordinary text with its formatting"
                    )
                character = dict(item, text=char)
                if state[1] == "none":
                    character.pop("underline", None)
                else:
                    character["underline"] = state[1]
                if (
                    result
                    and isinstance(result[-1], dict)
                    and "text" in result[-1]
                    and {key: item for key, item in result[-1].items() if key != "text"}
                    == {key: item for key, item in character.items() if key != "text"}
                ):
                    result[-1]["text"] += char
                else:
                    result.append(character)
        return result

    result = visit(blocks)
    if next(states, None) is not None:
        raise AssertionError("Word comparison did not account for all ordinary text")
    return result


def _math_only_serializations(original, saved, differences, path="blocks"):
    if isinstance(original, list) and isinstance(saved, list):
        for index, (left, right) in enumerate(zip(original, saved)):
            _math_only_serializations(left, right, differences, path + "/" + str(index))
    elif isinstance(original, dict) and isinstance(saved, dict):
        if "paragraph" in original and "paragraph" in saved:
            a = original["paragraph"].get("content", [])
            b = saved["paragraph"].get("content", [])
            if len(a) == len(b) == 1 and "math" in a[0] and "math" in b[0]:
                if (
                    not a[0].get("display")
                    and b[0].get("display")
                    and b[0].get("math_alignment") == "centerGroup"
                ):
                    differences.append(
                        {
                            "path": path,
                            "change": "math-only inline paragraph serialized as oMathPara",
                            "saved_alignment": "centerGroup",
                        }
                    )
                    b[0].pop("display")
                    b[0].pop("math_alignment")
        for key in original.keys() & saved.keys():
            _math_only_serializations(
                original[key], saved[key], differences, path + "/" + key
            )


def compare_word_documents(original, saved):
    """Report exact differences separately from narrowly defined Word equivalences."""
    aliases = _font_aliases([original, saved])
    before = word_document_blocks(original, aliases)
    after = word_document_blocks(saved, aliases)
    projection = _project_math_formats(original, before, after, aliases)
    serializations = []
    _math_only_serializations(before, after, serializations)
    return {
        "raw_blocks_match": original.blocks() == saved.blocks(),
        "effective_blocks_match": before == after,
        "serialization_differences": serializations,
        "effective_mismatches": list(_comparison_differences(before, after))[:20],
        "source_declaration_projection": projection,
        "raw_math_metadata_differences": [
            change
            for change in _comparison_differences(original.blocks(), saved.blocks())
            if "/math_runs/" in change["path"]
        ][:20],
        "effective_formatting_resolution": [
            "docDefaults and paragraph/character style inheritance",
            "ordinary-text underline inheritance, including character hyperlink styles",
            "nearest mathematical control properties",
            "document mathFont default",
            "fontTable alternate names and documented Malgun Gothic localization",
            "U+2212 and ASCII hyphen-minus in math text only",
            "script-family applicability for symbols with no Unicode mathematical alphabet glyph mapping",
        ],
    }


def _coalesce_math_characters(characters):
    result = []
    for character in characters:
        if (
            result
            and result[-1]["format"] == character["format"]
            and result[-1]["variant"] == character["variant"]
        ):
            result[-1]["text"] += character["text"]
        else:
            result.append(character)
    return result


def _project_math_formats(original, before, after, aliases):
    """Require all source math declarations; disclose unspecified Word additions.

    A Normal text font does not itself author a font on low-level OMML. Resolve
    saved declarations through their effective context, but compare exactly the
    property keys declared on original mathematical runs or control properties.
    """
    from tests.docx_oracle import NS

    context = _MathFormatting(original, aliases)
    source_items = list(_math_items(before))
    saved_items = list(_math_items(after))
    equations = original.document.findall(".//m:oMath", NS)
    checked = 0
    unspecified = 0
    unaligned = []
    for index, (equation, source, saved) in enumerate(
        zip(equations, source_items, saved_items)
    ):
        masks = []
        for run in equation.findall(".//m:r", NS):
            declared = context.declared(run)
            masks.extend(
                [declared] * len("".join(t.text or "" for t in run.findall("m:t", NS)))
            )
        expanded = []
        for item in (source, saved):
            expanded.append(
                [
                    dict(
                        text=char,
                        format=dict(run["format"]),
                        variant=dict(run["variant"]),
                    )
                    for run in item["math_runs"]
                    for char in run["text"]
                ]
            )
        if len(masks) != len(expanded[0]) or len(masks) != len(expanded[1]):
            unaligned.append(index)
            continue
        for mask, left, right in zip(masks, expanded[0], expanded[1]):
            checked += len(mask)
            unspecified += len((left["format"].keys() | right["format"].keys()) - mask)
            for item in (left, right):
                item["format"] = {
                    key: value for key, value in item["format"].items() if key in mask
                }
        source["math_runs"] = _coalesce_math_characters(expanded[0])
        saved["math_runs"] = _coalesce_math_characters(expanded[1])
    return {
        "policy": "Every original math run/control declaration is checked against saved effective context; unspecified properties are not asserted",
        "checked_character_properties": checked,
        "unspecified_character_properties": unspecified,
        "unaligned_equations": unaligned,
    }


def _comparison_differences(original, saved, path="blocks"):
    if (
        path.endswith("/math_runs")
        and isinstance(original, list)
        and isinstance(saved, list)
    ):
        # Word freely merges runs. Diagnose the actual differing character and
        # property instead of reporting every later run as positionally shifted.
        original, saved = [
            [dict(run, text=char) for run in runs for char in run["text"]]
            for runs in (original, saved)
        ]
        if len(original) != len(saved):
            yield {
                "path": path + "/length",
                "source": len(original),
                "saved": len(saved),
            }
        for index, (left, right) in enumerate(zip(original, saved)):
            for change in _comparison_differences(left, right, path + "/" + str(index)):
                change.update(
                    source_character=left["text"], saved_character=right["text"]
                )
                yield change
        return
    if type(original) is not type(saved):
        yield {"path": path, "source": original, "saved": saved}
    elif isinstance(original, dict):
        for key in sorted(original.keys() | saved.keys()):
            if key not in original or key not in saved:
                yield {
                    "path": path + "/" + key,
                    "source": original.get(key),
                    "saved": saved.get(key),
                }
            else:
                for change in _comparison_differences(
                    original[key], saved[key], path + "/" + key
                ):
                    yield change
    elif isinstance(original, list):
        if len(original) != len(saved):
            yield {
                "path": path + "/length",
                "source": len(original),
                "saved": len(saved),
            }
        for index, (left, right) in enumerate(zip(original, saved)):
            for change in _comparison_differences(left, right, path + "/" + str(index)):
                yield change
    elif original != saved:
        yield {"path": path, "source": original, "saved": saved}


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

    mismatched = []
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
            comparison = compare_word_documents(original_document, saved_document)
            report.update(comparison)
            report["saved_document_blocks_match"] = comparison["raw_blocks_match"]
            report["saved_document_effective_blocks_match"] = comparison[
                "effective_blocks_match"
            ]
            if not comparison["effective_blocks_match"]:
                mismatched.append(source.name)
        report["raw_equations_identical"] = original == saved
        report["minus_spelling_equivalence"] = (
            "U+2212 and ASCII hyphen-minus in math sequences only"
        )
    (args.output / "word-report.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    if mismatched:
        raise AssertionError(
            "Word resave has unresolved effective document differences (see word-report.json): "
            + ", ".join(mismatched)
        )


if __name__ == "__main__":
    main()
