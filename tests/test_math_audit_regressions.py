"""Independent source-to-OMML contracts from the November MathML audit."""

import warnings

import pytest

from mathml2docx import (
    MathMLFallbackWarning,
    MathmlToDocx,
    UnsupportedMathMLError,
    mathml_to_omml,
)

NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math"}

# MathML 3 sections 3.2.2 and 7.5: encoded mathematical alphabets keep
# their meaning under surrounding mathvariant declarations.
PROTECTED_ALPHABETS = [
    ("𝐱", "roman", "b"),
    ("𝑥", "roman", "i"),
    ("𝒙", "roman", "bi"),
    ("ℝ", "double-struck", "p"),
    ("𝔵", "fraktur", "p"),
    ("𝖝", "fraktur", "b"),
    ("𝓍", "script", "p"),
    ("𝔁", "script", "b"),
    ("𝗑", "sans-serif", "p"),
    ("𝘅", "sans-serif", "b"),
    ("𝘹", "sans-serif", "i"),
    ("𝙭", "sans-serif", "bi"),
    ("𝚡", "monospace", "p"),
    ("ℎ", "roman", "i"),
]


@pytest.mark.parametrize("character,script,style", PROTECTED_ALPHABETS)
@pytest.mark.parametrize("token", ["mi", "mn", "mo", "mtext", "ms"])
@pytest.mark.parametrize("scope", ["math", "mstyle", "token"])
def test_encoded_alphabets_survive_mathvariant_declarations(
    character, script, style, token, scope
):
    body = "<{0}{1}>{2}</{0}>".format(
        token, ' mathvariant="normal"' if scope == "token" else "", character
    )
    if scope == "mstyle":
        body = '<mstyle mathvariant="normal">' + body + "</mstyle>"
    root = equation(body, 'mathvariant="normal"' if scope == "math" else "")
    runs = [
        run
        for run in root.findall(".//m:r", NS)
        if character in "".join(run.xpath("./m:t/text()", namespaces=NS))
    ]
    assert len(runs) == 1
    assert runs[0].xpath("./m:rPr/m:scr/@m:val", namespaces=NS) == [script]
    assert runs[0].xpath("./m:rPr/m:sty/@m:val", namespaces=NS) == [style]
    assert not runs[0].findall("m:rPr/m:nor", NS)
    if token in {"mtext", "ms"}:
        assert runs[0].xpath("./m:rPr/m:lit/@m:val", namespaces=NS) == ["1"]


@pytest.mark.parametrize("token", ["mtext", "ms"])
def test_styled_literal_text_keeps_literal_spacing(token):
    root = equation(f'<{token} mathvariant="bold">a + b</{token}>')
    expected = "𝐚 + 𝐛" if token == "mtext" else '"𝐚 + 𝐛"'
    assert "".join(root.xpath(".//m:t/text()", namespaces=NS)) == expected
    for run in root.findall(".//m:r", NS):
        assert run.xpath("./m:rPr/m:sty/@m:val", namespaces=NS) == ["b"]
        assert run.xpath("./m:rPr/m:lit/@m:val", namespaces=NS) == ["1"]


def test_local_variant_changes_plain_characters_but_not_encoded_symbols():
    root = equation('<mi mathvariant="normal">ℝ𝐱x</mi>', 'mathvariant="bold"')
    assert root.xpath(".//m:t/text()", namespaces=NS) == ["ℝ", "𝐱", "x"]
    assert root.xpath(".//m:scr/@m:val", namespaces=NS) == [
        "double-struck",
        "roman",
        "roman",
    ]
    assert root.xpath(".//m:sty/@m:val", namespaces=NS) == ["p", "b", "p"]


@pytest.mark.parametrize(
    "source", [r"\notarealcommand{x}", r"\frac{1}{\notarealcommand}"]
)
@pytest.mark.parametrize("frontend", ["mathml", "omml", "document"])
def test_unresolved_latex_commands_are_not_published_as_formula_text(source, frontend):
    from mathml2docx.math import latex_to_mathml, latex_to_omml

    convert = {
        "mathml": latex_to_mathml,
        "omml": latex_to_omml,
        "document": MathmlToDocx().parse_latex,
    }[frontend]
    with pytest.raises(UnsupportedMathMLError, match="Unresolved LaTeX command"):
        convert(source)


@pytest.mark.parametrize("literal", [r"\notarealcommand", r"\middle"])
def test_unresolved_latex_guard_preserves_explicit_text(literal):
    document = MathmlToDocx().parse_latex(r"\text{" + literal + "}")
    assert document._element.xpath("//m:t/text()") == [literal]


def test_unresolved_latex_guard_preserves_a_real_backslash_symbol():
    document = MathmlToDocx().parse_latex(r"\backslash x")
    assert document._element.xpath("//m:t/text()") == ["\\", "x"]


def test_unresolved_latex_guard_does_not_change_literal_mathml_tokens():
    root = equation(r"<mi>\notarealcommand</mi>")
    assert root.xpath(".//m:t/text()", namespaces=NS) == [r"\notarealcommand"]


def test_unresolved_latex_cli_fails_without_writing_a_docx(tmp_path, monkeypatch):
    import sys

    from mathml2docx.__main__ import main

    source = tmp_path / "unknown.tex"
    output = tmp_path / "unknown.docx"
    source.write_text(r"\notarealcommand{x}", encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv", ["mathml2docx", str(source), str(output), "--format", "latex"]
    )
    with pytest.raises(UnsupportedMathMLError, match="Unresolved LaTeX command"):
        main()
    assert not output.exists()


def equation(body, attributes=""):
    return mathml_to_omml("<math " + attributes + ">" + body + "</math>")


def test_root_fraction_default_preserves_binomial_notation():
    result = equation(
        "<mfenced><mfrac><mi>n</mi><mi>k</mi></mfrac></mfenced>",
        'linethickness="0"',
    )
    assert result.xpath(".//m:fPr/m:type/@m:val", namespaces=NS) == ["noBar"]


def test_nested_style_defaults_and_local_overrides_are_scoped():
    result = equation(
        '<mstyle linethickness="0"><mfrac linethickness="medium">'
        "<mfrac><mi>a</mi><mi>b</mi></mfrac><mi>c</mi></mfrac></mstyle>"
        "<mfrac><mi>d</mi><mi>e</mi></mfrac>"
    )
    assert result.xpath(".//m:fPr/m:type/@m:val", namespaces=NS) == [
        "bar",
        "noBar",
        "bar",
    ]


@pytest.mark.parametrize("container", ["math", "mstyle"])
def test_fence_defaults_keep_interval_endpoints_and_separator_intent(container):
    source = f'<{container} open="[" close="]" separators=""><mfenced><mi>a</mi><mi>b</mi></mfenced></{container}>'
    if container != "math":
        source = "<math>" + source + "</math>"
    result = mathml_to_omml(source)
    assert result.xpath(".//m:begChr/@m:val", namespaces=NS) == ["["]
    assert result.xpath(".//m:endChr/@m:val", namespaces=NS) == ["]"]
    assert result.xpath(".//m:t/text()", namespaces=NS) == ["a", "b"]


def test_fence_local_overrides_and_xml_whitespace_in_attributes():
    result = equation(
        '<mstyle open="[" close="]" separators=";">'
        '<mfenced open=" ( " close=" ) " separators=","><mi>a</mi><mi>b</mi></mfenced>'
        "</mstyle>"
    )
    assert result.xpath(".//m:begChr/@m:val", namespaces=NS) == ["("]
    assert result.xpath(".//m:endChr/@m:val", namespaces=NS) == [")"]
    assert result.xpath(".//m:t/text()", namespaces=NS) == ["a", ",", "b"]


@pytest.mark.parametrize(
    "script",
    [
        "<msqrt><mi>y</mi></msqrt>",
        "<mphantom><mo>¯</mo></mphantom>",
        '<mpadded width="0"><mo>^</mo></mpadded>',
        '<mo xmlns="urn:foreign">^</mo>',
        "<unknown>^</unknown>",
    ],
)
def test_structured_accents_require_explicit_recovery(script):
    with pytest.raises(UnsupportedMathMLError):
        equation('<mover accent="true"><mi>x</mi>' + script + "</mover>")


def test_hidden_underaccent_is_not_changed_to_a_visible_bar():
    with pytest.raises(UnsupportedMathMLError):
        equation(
            '<munder accentunder="true"><mi>x</mi><mphantom><mo>¯</mo></mphantom></munder>'
        )


def test_nonaccent_overscript_retains_its_radical_without_flattening():
    result = equation("<mover><mi>x</mi><msqrt><mo>→</mo></msqrt></mover>")
    assert result.xpath("./m:limUpp/m:lim/m:rad/m:e/m:r/m:t/text()", namespaces=NS) == [
        "→"
    ]
    assert not result.xpath(".//m:acc", namespaces=NS)


def test_style_default_can_override_operator_dictionary_accent():
    result = equation(
        '<mstyle accent="false"><mover><mi>x</mi><mo>→</mo></mover></mstyle>'
    )
    assert result.xpath("./m:limUpp/m:lim/m:r/m:t/text()", namespaces=NS) == ["→"]


@pytest.mark.parametrize("accent", ["⟶", "↼", "¨", "˙", "⏞"])
def test_default_accents_use_the_operator_dictionary(accent):
    result = equation("<mover><mi>x</mi><mo>" + accent + "</mo></mover>")
    assert result.xpath("./m:acc/m:accPr/m:chr/@m:val", namespaces=NS) == [accent]


def test_munderover_supports_both_bars_without_turning_them_into_limits():
    result = equation(
        '<munderover accentunder="true" accent="true">'
        "<mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow><mo>_</mo><mo>¯</mo>"
        "</munderover>"
    )
    assert result.xpath(".//m:barPr/m:pos/@m:val", namespaces=NS) == ["top", "bot"]
    assert not result.xpath(".//m:limLow | .//m:limUpp", namespaces=NS)
    assert result.xpath(".//m:t/text()", namespaces=NS) == ["a", "+", "b"]


def test_embellished_operator_retains_explicit_nonaccent_intent():
    result = equation('<mover><mi>x</mi><mrow><mo accent="false">→</mo></mrow></mover>')
    assert result.xpath("./m:limUpp/m:lim/m:r/m:t/text()", namespaces=NS) == ["→"]
    assert not result.xpath(".//m:acc", namespaces=NS)


@pytest.mark.parametrize(
    "body",
    [
        '<mtable><mtr><mtd columnspan="2"><mi>a</mi></mtd><mtd><mi>b</mi></mtd></mtr></mtable>',
        '<mtable><mtr><mtd rowspan="2"><mi>a</mi></mtd><mtd><mi>b</mi></mtd></mtr><mtr><mtd><mi>c</mi></mtd></mtr></mtable>',
        "<mtable><mtr><mtd><mi>a</mi></mtd></mtr><mtr><mtd><mi>b</mi></mtd><mtd><mi>c</mi></mtd></mtr></mtable>",
        "<mtable/>",
        "<mtable><mtr/></mtable>",
    ],
)
def test_valid_unrepresentable_tables_reach_the_recovery_callback(body):
    calls = []
    parser = MathmlToDocx(
        mathml_fallback=lambda source, error: (
            calls.append(error) or "table image needed"
        )
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        document = parser.parse_mathml("<math>" + body + "</math>")
    assert len(calls) == 1
    assert isinstance(calls[0], UnsupportedMathMLError)
    assert "table image needed" in document.paragraphs[0].text
    assert not document._element.xpath("//m:oMath")


@pytest.mark.parametrize(
    "body",
    [
        '<mi>a</mi><mo linebreak="newline">=</mo><mi>b</mi>',
        '<mstyle linebreak="newline"><mi>a</mi><mo>=</mo><mi>b</mi></mstyle>',
        '<mo linebreak="newline">(</mo><mi>x</mi><mo>)</mo>',
    ],
)
def test_operator_linebreak_is_not_silently_dropped(body):
    with pytest.raises(UnsupportedMathMLError, match="line break"):
        equation(body)


@pytest.mark.parametrize("encoding", ["ISO-8859-1", "UTF-16", "UTF-8"])
def test_unicode_input_ignores_byte_encoding_declaration(encoding):
    source = (
        '<?xml version="1.0" encoding="'
        + encoding
        + '"?><math><mtext>café α 한글</mtext></math>'
    )
    result = mathml_to_omml(source)
    assert result.xpath(".//m:t/text()", namespaces=NS) == ["café α 한글"]


def test_token_whitespace_is_xml_whitespace_only_including_mtext():
    result = equation(
        "<mi>&#xA0;x&#xA0;</mi><mn>1&#x202F;234</mn>"
        "<mtext> \n  Theorem\t 1: \r </mtext><ms>&#xA0;</ms>"
    )
    assert result.xpath(".//m:t/text()", namespaces=NS) == [
        "\u00a0x\u00a0",
        "1\u202f234",
        "Theorem 1:",
        '"\u00a0"',
    ]


@pytest.mark.parametrize(
    "attributes,content,expected",
    [
        ("", 'double quote is "', '"double quote is \\""'),
        ('lquote="[" rquote="]"', "[a]", "[\\[a\\]]"),
        ('lquote="&lt;&lt;" rquote="&gt;&gt;"', "a&lt;&lt;b&gt;&gt;", "<<a\\<<b\\>>>>"),
        ("", "a\\b", '"a\\\\b"'),
    ],
)
def test_string_content_visibly_escapes_its_delimiters(attributes, content, expected):
    result = equation("<ms " + attributes + ">" + content + "</ms>")
    assert result.xpath(".//m:t/text()", namespaces=NS) == [expected]


@pytest.mark.parametrize(
    "invalid",
    [
        "<mfrac><mi>x</mi></mfrac>",
        "<mroot><mi>x</mi></mroot>",
        "<msubsup><mi>x</mi><mi>i</mi></msubsup>",
        "<munderover><mo>∑</mo><mi>i</mi></munderover>",
        "<mmultiscripts><mi>x</mi><mi>i</mi></mmultiscripts>",
        "<mmultiscripts><none/></mmultiscripts>",
        "<semantics/>",
        "<maction/>",
        "<mlongdiv><mn>1</mn><mn>2</mn></mlongdiv>",
    ],
)
@pytest.mark.parametrize("unknown_first", [True, False])
def test_wrong_known_arity_precedes_fallback_regardless_of_sibling_order(
    invalid, unknown_first
):
    body = "<unknown/>" + invalid if unknown_first else invalid + "<unknown/>"
    with pytest.raises(ValueError) as caught:
        equation(body)
    assert type(caught.value) is ValueError


def test_prevalidation_ignores_annotation_content():
    result = equation(
        '<semantics><mi>x</mi><annotation-xml encoding="application/xml"><mfrac><mi>unused</mi></mfrac></annotation-xml></semantics>'
    )
    assert result.xpath(".//m:t/text()", namespaces=NS) == ["x"]


def test_nonxml_space_outside_a_token_is_invalid_content():
    with pytest.raises(ValueError) as caught:
        equation("<mrow>&#xA0;<mi>x</mi></mrow>")
    assert type(caught.value) is ValueError


@pytest.mark.parametrize(
    "attributes,operator_attributes,expected",
    [
        ("", "", "sSubSup"),
        ('display="block"', "", "limUpp"),
        ('display="block" displaystyle="false"', "", "sSubSup"),
        ('displaystyle="true"', "", "limUpp"),
        ("", 'movablelimits="false"', "limUpp"),
    ],
)
def test_movable_limits_respect_displaystyle(attributes, operator_attributes, expected):
    result = equation(
        "<munderover><mo "
        + operator_attributes
        + ">∑</mo><mi>i</mi><mi>n</mi></munderover>",
        attributes,
    )
    assert result[0].tag == "{" + NS["m"] + "}" + expected


def test_displaystyle_changes_inside_fraction_and_nested_style():
    result = equation(
        "<mfrac><munder><mo>∑</mo><mi>i</mi></munder><mi>n</mi></mfrac>"
        '<mstyle displaystyle="false"><munder><mo>∑</mo><mi>j</mi></munder></mstyle>',
        'display="block"',
    )
    assert result.xpath("./m:f/m:num/m:sSub/m:sub/m:r/m:t/text()", namespaces=NS) == [
        "i"
    ]
    assert result.xpath("./m:sSub/m:sub/m:r/m:t/text()", namespaces=NS) == ["j"]


def test_embellished_sum_retains_movablelimits_and_local_override():
    result = equation(
        '<mstyle movablelimits="false"><munder><mrow><mo movablelimits="true">∑</mo></mrow><mi>i</mi></munder></mstyle>'
    )
    assert result.xpath("./m:sSub/m:sub/m:r/m:t/text()", namespaces=NS) == ["i"]


def test_integral_does_not_implicitly_move_limits():
    result = equation("<munderover><mo>∫</mo><mn>0</mn><mn>1</mn></munderover>")
    assert result.xpath("./m:limUpp/m:e/m:limLow", namespaces=NS)


def test_libreoffice_recovery_sees_inherited_bevelled_fraction_default():
    source = '<math bevelled="true"><mfrac><mi>x</mi><mi>y</mi></mfrac></math>'
    with pytest.raises(UnsupportedMathMLError, match="LibreOffice"):
        mathml_to_omml(source, target="libreoffice")


def test_rtl_layout_requires_explicit_recovery_instead_of_ltr_output():
    with pytest.raises(UnsupportedMathMLError, match="Right-to-left"):
        equation("<msup><mi>x</mi><mn>2</mn></msup>", 'dir="rtl"')


@pytest.mark.parametrize(
    "character,script,style",
    [
        ("𝐱", "roman", "b"),
        ("𝑥", "roman", "i"),
        ("𝒙", "roman", "bi"),
        ("ℝ", "double-struck", "p"),
        ("ℜ", "fraktur", "p"),
        ("𝖝", "fraktur", "b"),
        ("ℱ", "script", "p"),
        ("𝔁", "script", "b"),
        ("𝗑", "sans-serif", "p"),
        ("𝘅", "sans-serif", "b"),
        ("𝘹", "sans-serif", "i"),
        ("𝙭", "sans-serif", "bi"),
        ("𝚡", "monospace", "p"),
    ],
)
def test_unicode_mathematical_alphabets_keep_their_native_variant(
    character, script, style
):
    result = equation("<mi>" + character + "</mi>")
    assert result.xpath("./m:r/m:rPr/m:scr/@m:val", namespaces=NS) == [script]
    assert result.xpath("./m:r/m:rPr/m:sty/@m:val", namespaces=NS) == [style]
    assert result.xpath("./m:r/m:t/text()", namespaces=NS) == [character]


def test_implicit_mixed_unicode_alphabets_do_not_share_one_incorrect_style():
    result = equation("<mi>ℝx𝐱</mi>")
    assert result.xpath("./m:r/m:t/text()", namespaces=NS) == ["ℝ", "x", "𝐱"]
    assert result.xpath("./m:r/m:rPr/m:scr/@m:val", namespaces=NS) == [
        "double-struck",
        "roman",
        "roman",
    ]
    assert result.xpath("./m:r/m:rPr/m:sty/@m:val", namespaces=NS) == ["p", "p", "b"]


def test_latex_unicode_variants_are_not_overwritten_by_identifier_italic_default():
    from mathml2docx.math import latex_to_omml

    result = latex_to_omml(r"\mathbb{R}+\mathbf{x}")
    assert result.xpath("./m:r[m:t='ℝ']/m:rPr/m:scr/@m:val", namespaces=NS) == [
        "double-struck"
    ]
    assert result.xpath("./m:r[m:t='ℝ']/m:rPr/m:sty/@m:val", namespaces=NS) == ["p"]
    assert result.xpath("./m:r[m:t='𝐱']/m:rPr/m:sty/@m:val", namespaces=NS) == ["b"]


@pytest.mark.parametrize("tag", ["mtext", "ms"])
@pytest.mark.parametrize(
    "character,script,style",
    [
        ("𝑥", "roman", "i"),
        ("𝐱", "roman", "b"),
        ("ℝ", "double-struck", "p"),
        ("𝒙", "roman", "bi"),
        ("ℜ", "fraktur", "p"),
        ("𝖝", "fraktur", "b"),
        ("ℱ", "script", "p"),
        ("𝔁", "script", "b"),
        ("𝗑", "sans-serif", "p"),
        ("𝘅", "sans-serif", "b"),
        ("𝘹", "sans-serif", "i"),
        ("𝙭", "sans-serif", "bi"),
        ("𝚡", "monospace", "p"),
    ],
)
def test_encoded_text_glyph_is_literal_with_native_variant_and_without_nor(
    tag, character, script, style
):
    result = equation("<" + tag + ">" + character + "</" + tag + ">")
    runs = result.xpath("./m:r[m:t=$character]", character=character, namespaces=NS)
    assert len(runs) == 1
    assert runs[0].xpath("m:rPr/m:lit/@m:val", namespaces=NS) == ["1"]
    assert not runs[0].xpath("m:rPr/m:nor", namespaces=NS)
    assert runs[0].xpath("m:rPr/m:scr/@m:val", namespaces=NS) == [script]
    assert runs[0].xpath("m:rPr/m:sty/@m:val", namespaces=NS) == [style]


@pytest.mark.parametrize("tag", ["mtext", "ms"])
def test_mixed_encoded_literal_keeps_spaces_operators_and_escaped_quotes(tag):
    result = equation(
        "<" + tag + ">value&#xA0;𝑥 + 𝐱 = ℝ; 0x*literal &quot;q&quot;</" + tag + ">"
    )
    expected = 'value\u00a0𝑥 + 𝐱 = ℝ; 0x*literal "q"'
    if tag == "ms":
        expected = '"value\u00a0𝑥 + 𝐱 = ℝ; 0x*literal \\"q\\""'
    assert "".join(result.xpath("./m:r/m:t/text()", namespaces=NS)) == expected
    assert result.xpath("./m:r[m:rPr/m:lit]/m:t/text()", namespaces=NS) == [
        "𝑥",
        "𝐱",
        "ℝ",
    ]
    ordinary = result.xpath("./m:r[not(m:rPr/m:lit)]", namespaces=NS)
    assert len(ordinary) == 4
    assert all(
        run.xpath("m:rPr/m:nor/@m:val", namespaces=NS) == ["1"] for run in ordinary
    )


def test_libreoffice_rejects_the_exact_escaped_string_that_can_drop_content():
    source = "<math><ms>say &quot;yes&quot;</ms></math>"
    result = mathml_to_omml(source)
    assert result.xpath("./m:r/m:t/text()", namespaces=NS) == ['"say \\"yes\\""']
    with pytest.raises(UnsupportedMathMLError, match="LibreOffice"):
        mathml_to_omml(source, target="libreoffice")


def test_libreoffice_escaped_string_text_recovery_preserves_the_complete_source():
    source = "<math><ms>say &quot;yes&quot;</ms></math>"
    with pytest.warns(MathMLFallbackWarning):
        document = MathmlToDocx(
            math_target="libreoffice", unsupported_math="text"
        ).parse_mathml(source)
    assert source in document.paragraphs[0].text
    assert "[Unconverted MathML]" in document.paragraphs[0].text
    assert not document._element.xpath("//m:oMath")


def test_libreoffice_escaped_string_image_recovery_receives_all_literal_content():
    from io import BytesIO

    from lxml import etree
    from PIL import Image

    source = "<math><ms>say &quot;yes&quot;</ms></math>"
    calls = []

    def render(normalized_source, error):
        calls.append(
            (etree.fromstring(normalized_source.encode()).find("ms").text, error)
        )
        stream = BytesIO()
        Image.new("RGB", (12, 6), "white").save(stream, format="PNG")
        return stream.getvalue()

    with pytest.warns(MathMLFallbackWarning):
        document = MathmlToDocx(
            math_target="libreoffice", mathml_fallback=render
        ).parse_mathml(source)
    assert len(calls) == 1
    assert calls[0][0] == 'say "yes"'
    assert isinstance(calls[0][1], UnsupportedMathMLError)
    assert len(document.inline_shapes) == 1
    assert "yes" in document.inline_shapes[0]._inline.docPr.get("descr")
    assert not document._element.xpath("//m:oMath")
