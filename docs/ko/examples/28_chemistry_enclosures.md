# 화학 표기와 수식 테두리

정체 원소 기호·동위원소 앞 첨자·전하·반응 화살표와 기본 수식 테두리.

## 입력과 출력 비교

실제 HTML/MathML 입력을 브라우저에서 보고, 생성된 DOCX를 LibreOffice로 내보낸 PDF와 비교하세요. 수식 편집은 DOCX를 Word에서 열어 확인할 수 있습니다.

<div class="example-comparison"><section class="example-preview"><div class="preview-heading"><h3>브라우저 · HTML / MathML</h3><a href="../assets/inputs/28_chemistry_enclosures.html">HTML 미리보기 열기</a></div><iframe src="../assets/inputs/28_chemistry_enclosures.html" title="브라우저 · HTML / MathML" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section>
<section class="example-preview"><div class="preview-heading"><h3>LibreOffice · PDF</h3><a href="../assets/previews/28_chemistry_enclosures.pdf">PDF 열기</a></div><iframe src="../assets/pdf-pages/28_chemistry_enclosures.html" title="LibreOffice · PDF" loading="lazy" sandbox="" referrerpolicy="no-referrer"></iframe></section></div>

Markdown·LaTeX 예제는 변환 과정에서 만든 HTML·MathML을 표시합니다. 브라우저의 MathML 지원, Word 스타일, 글꼴, 페이지 배치에 따라 표시가 달라질 수 있습니다.

PDF 패널은 페이지 이미지를 표시합니다. 확대·검색·텍스트 선택은 원본 PDF 열기를, 편집은 DOCX 다운로드를 이용하세요.

## 실행

[예제 ZIP](../downloads/mathml2docx-examples.zip)의 압축을 풀고 [예제 의존성](00-index.md)을 설치한 뒤, `examples/` 폴더가 들어 있는 위치에서 실행하세요.

```sh
python -m examples.28_chemistry_enclosures
```

[생성된 DOCX](../downloads/examples/28_chemistry_enclosures.docx)

[참조 PDF](../assets/previews/28_chemistry_enclosures.pdf)

## 전체 코드

```python
"""Chemical equations, isotope scripts, and native mathematical enclosures."""

from mathml2docx import TableStyle, convert

from .support import save

html = """<html><body>
<style>body {font-family:'Malgun Gothic';font-size:11pt} h1,h2 {color:#17365d}</style>
<h1>Chemical notation / 화학 표기</h1>
<p>Atom counts and ionic charges use separate scripts. Element symbols remain upright.</p>
<p>Water / 물: <math><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mi mathvariant="normal">O</mi></math>.</p>
<p>Sulfate ion / 황산 이온: <math><msubsup><mrow><mi mathvariant="normal">S</mi><mi mathvariant="normal">O</mi></mrow><mn>4</mn><mrow><mn>2</mn><mo>−</mo></mrow></msubsup></math>.</p>
<h2>Isotopes / 동위원소</h2>
<math display="block"><mmultiscripts><mi mathvariant="normal">C</mi><none/><none/><mprescripts/><mn>6</mn><mn>14</mn></mmultiscripts><mo>→</mo><mmultiscripts><mi mathvariant="normal">N</mi><none/><none/><mprescripts/><mn>7</mn><mn>14</mn></mmultiscripts><mo>+</mo><mmultiscripts><mi mathvariant="normal">e</mi><none/><none/><mprescripts/><mrow><mo>−</mo><mn>1</mn></mrow><mn>0</mn></mmultiscripts></math>
<h2>Reaction conditions / 반응 조건</h2>
<math display="block"><mn>2</mn><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mo>+</mo><msub><mi mathvariant="normal">O</mi><mn>2</mn></msub><mover accent="false"><mo>→</mo><mtext>heat</mtext></mover><mn>2</mn><msub><mi mathvariant="normal">H</mi><mn>2</mn></msub><mi mathvariant="normal">O</mi></math>
<h2>Enclosures / 수식 테두리</h2>
<table><tr><th>Notation</th><th>Editable expression</th></tr>
<tr><td>Box</td><td><math><menclose notation="box"><mfrac><mi>a</mi><mi>b</mi></mfrac></menclose></math></td></tr>
<tr><td>Cancellation</td><td><math><menclose notation="updiagonalstrike"><mi>x</mi></menclose><mo>+</mo><mn>1</mn></math></td></tr>
<tr><td>Top and right (actuarial)</td><td><math><menclose notation="actuarial"><mi>n</mi></menclose></math></td></tr>
<tr><td>Radical</td><td><math><menclose notation="radical"><mi>x</mi><mo>+</mo><mn>1</mn></menclose></math></td></tr></table>
<p>These formulas use native Word equations. Chemical structure diagrams require a separate renderer. For LibreOffice, choose math_target=libreoffice with image recovery for enclosures; Writer can omit native Word borders.</p>
</body></html>"""
save(convert(html, table_style=TableStyle.GRID), "28_chemistry_enclosures.docx")
```
