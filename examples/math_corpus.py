"""Original mathematical examples and deterministic composition corpus.

The small expression model describes mathematical roles, independently of OMML.
Its encoder emits only MathML. Tests interpret the resulting OMML separately.
No third-party equation datasets or Office stylesheets are copied here.
"""

import random
from html import escape

# Hand-authored expressions for visual inspection. Names describe mathematical use.
SHOWCASE = [
    (
        "Quadratic roots",
        "<mi>x</mi><mo>=</mo><mfrac><mrow><mo>−</mo><mi>b</mi><mo>±</mo><msqrt><msup><mi>b</mi><mn>2</mn></msup><mo>−</mo><mn>4</mn><mi>a</mi><mi>c</mi></msqrt></mrow><mrow><mn>2</mn><mi>a</mi></mrow></mfrac>",
    ),
    (
        "Continued fraction",
        "<mfrac><mn>1</mn><mrow><mn>1</mn><mo>+</mo><mfrac><mn>1</mn><mrow><mn>2</mn><mo>+</mo><mfrac><mn>1</mn><mn>3</mn></mfrac></mrow></mfrac></mrow></mfrac>",
    ),
    (
        "Binomial coefficient",
        '<mfenced><mfrac linethickness="0"><mi>n</mi><mi>k</mi></mfrac></mfenced>',
    ),
    (
        "Nested roots",
        "<mroot><mrow><mi>x</mi><mo>+</mo><msqrt><mi>y</mi><mo>+</mo><msqrt><mi>z</mi></msqrt></msqrt></mrow><mn>3</mn></mroot>",
    ),
    (
        "Indexed tensor",
        "<msubsup><mi>T</mi><mrow><mi>i</mi><mi>j</mi></mrow><mrow><mi>k</mi><mi>l</mi></mrow></msubsup><mo>=</mo><msub><mi>a</mi><mi>i</mi></msub><msup><mi>b</mi><mi>k</mi></msup>",
    ),
    (
        "Series with limits",
        "<munderover><mo>∑</mo><mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi></munderover><mfrac><mn>1</mn><msup><mi>k</mi><mn>2</mn></msup></mfrac>",
    ),
    (
        "Improper integral",
        '<msubsup><mo>∫</mo><mn>0</mn><mo>∞</mo></msubsup><msup><mi>e</mi><mrow><mo>−</mo><msup><mi>x</mi><mn>2</mn></msup></mrow></msup><mspace width="0.167em"/><mi mathvariant="normal">d</mi><mi>x</mi>',
    ),
    (
        "Partial derivatives",
        "<mfrac><mrow><msup><mo>∂</mo><mn>2</mn></msup><mi>u</mi></mrow><mrow><mo>∂</mo><msup><mi>x</mi><mn>2</mn></msup></mrow></mfrac><mo>+</mo><mfrac><mrow><msup><mo>∂</mo><mn>2</mn></msup><mi>u</mi></mrow><mrow><mo>∂</mo><msup><mi>y</mi><mn>2</mn></msup></mrow></mfrac><mo>=</mo><mn>0</mn>",
    ),
    (
        "Matrix with expressions",
        '<mfenced open="[" close="]"><mtable><mtr><mtd><mfrac><mn>1</mn><mn>2</mn></mfrac></mtd><mtd><msqrt><mn>2</mn></msqrt></mtd></mtr><mtr><mtd><msub><mi>a</mi><mi>i</mi></msub></mtd><mtd><msup><mi>b</mi><mn>2</mn></msup></mtd></mtr></mtable></mfenced>',
    ),
    (
        "Piecewise values",
        '<mfenced open="{" close="" separators=""><mtable><mtr><mtd><msup><mi>x</mi><mn>2</mn></msup></mtd><mtd><mrow><mi>x</mi><mo>≥</mo><mn>0</mn></mrow></mtd></mtr><mtr><mtd><mrow><mo>−</mo><mi>x</mi></mrow></mtd><mtd><mrow><mi>x</mi><mo>&lt;</mo><mn>0</mn></mrow></mtd></mtr></mtable></mfenced>',
    ),
    (
        "Vector and hat accents",
        '<mover accent="true"><mi>v</mi><mo>→</mo></mover><mo>+</mo><mover accent="true"><mi>x</mi><mo>^</mo></mover>',
    ),
    (
        "Overline and underline",
        '<mover><mrow><mi>A</mi><mi>B</mi></mrow><mo accent="true">―</mo></mover><mo>+</mo><munder><mi>x</mi><mo accent="true">―</mo></munder>',
    ),
    (
        "Limits of a ratio",
        "<munder><mi>lim</mi><mrow><mi>x</mi><mo>→</mo><mn>0</mn></mrow></munder><mfrac><mrow><mi>sin</mi><mi>x</mi></mrow><mi>x</mi></mfrac><mo>=</mo><mn>1</mn>",
    ),
    (
        "Probability",
        '<mi>P</mi><mfenced open="(" close=")" separators=""><mrow><mi>A</mi><mo>∣</mo><mi>B</mi></mrow></mfenced><mo>=</mo><mfrac><mrow><mi>P</mi><mfenced><mrow><mi>A</mi><mo>∩</mo><mi>B</mi></mrow></mfenced></mrow><mrow><mi>P</mi><mfenced><mi>B</mi></mfenced></mrow></mfrac>',
    ),
    (
        "Mathematical alphabets",
        '<mi mathvariant="double-struck">R</mi><mo>⊃</mo><mi mathvariant="bold">v</mi><mo>∈</mo><mi mathvariant="script">F</mi><mo>+</mo><mi>𝛼</mi>',
    ),
    (
        "Semantic annotation",
        '<semantics><mfrac><mi>α</mi><mi>β</mi></mfrac><annotation encoding="application/x-tex">not rendered: alpha / beta</annotation></semantics>',
    ),
    (
        "Phantom alignment space",
        "<mi>x</mi><mphantom><mn>123</mn></mphantom><mo>+</mo><mi>y</mi>",
    ),
    (
        "Custom separators",
        '<mfenced open="⟨" close="⟩" separators=";|"><mi>x</mi><mi>y</mi><mi>z</mi><mi>w</mi></mfenced>',
    ),
    (
        "Bevelled fraction",
        '<mfrac bevelled="true"><mrow><mi>a</mi><mo>+</mo><mi>b</mi></mrow><mi>c</mi></mfrac>',
    ),
    (
        "Text and quoted string",
        "<mi>f</mi><mfenced><ms>input</ms></mfenced><mo>=</mo><mtext>output value</mtext>",
    ),
]

LATEX = [
    r"x_1^2+y_2^3=z^4",
    r"\frac{-b\pm\sqrt{b^2-4ac}}{2a}",
    r"\frac{1}{1+\frac{1}{2+\frac{1}{3}}}",
    r"\binom{n}{k}",
    r"\sqrt[3]{x+\sqrt{y}}",
    r"\sum_{k=1}^{n}\frac{1}{k^2}",
    r"\prod_{j=1}^{m}(1+x_j)",
    r"\int_0^\infty e^{-x^2}\,dx",
    r"\frac{\partial^2 u}{\partial x^2}+\frac{\partial^2 u}{\partial y^2}=0",
    r"\begin{pmatrix}a&b\\c&d\end{pmatrix}",
    r"\begin{bmatrix}1&0&0\\0&1&0\\0&0&1\end{bmatrix}",
    r"\begin{cases}x^2&x\ge0\\-x&x<0\end{cases}",
    r"\hat{x}+\vec{v}",
    r"\overline{AB}+\underline{x}",
    r"\mathbb{R}+\mathbf{x}+\mathrm{sin}(x)",
    r"\lim_{x\to0}\frac{\sin x}{x}=1",
    r"\log(x)+\exp(y)",
    r"\alpha+\beta\le\gamma",
    r"a\quad b\qquad c",
    r"\left\langle\frac{x}{y}\right\rangle",
    r"\left|\frac{a}{b}\right|",
    r"\sum\nolimits_{i=1}^{n}i",
    r"\text{result}=\frac{a+b}{c}",
    r"\forall x\in\mathbb{R}:x^2\ge0",
]


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
