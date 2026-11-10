# Upstream issue review

Reviewed on 2026-11-09, with implementation and verification on 2026-11-10 and
additional DOCX answer checks on 2026-11-11. The public GitHub API supplied all
49 open/closed issues from `pqzx/html2docx`, excluding pull requests. No upstream
issue was modified or closed.

The count includes duplicates, questions, withdrawn reports, and administrative
or publishing requests. Addressable code defects/features were implemented with
the limitations below. XML, execution, and LibreOffice checks do not establish
pixel-identical Word output or complete CSS/MathML support. Upstream publishing
and repository security settings are separate administrative tasks.

## Verifying existing fixes

The original package at `89205f4` was restored in a temporary directory. All six
`tests/test_existing_fixes.py` cases passed there: base64/inline images, missing
src, leading br, UTF-8/paragraph styles, nonempty rowspan, and basic text styles.
The same cases also run against the replacement engine.

## Regressions and issue-specific evidence

Of the nine `tests/test_regressions.py` cases, the original code produced four
errors and one failure. They pass with the new engine. Public API, equations,
security, merging, lists, and templates are covered by `tests/test_v1.py`.
Those are XML/relationship checks rather than direct Word screen comparisons.

| Issue | Status | Evidence and limits |
| --- | --- | --- |
| [#1 failed to convert html table to docx](https://github.com/pqzx/html2docx/issues/1) | Verified | Existing datasets cover tbody and nested tables. |
| [#2 Conversion of <ol><li>: No style with name 'List Number'](https://github.com/pqzx/html2docx/issues/2) | Fixed | Explicit numbering XML avoids dependence on a List Number style being present. |
| [#3 Errno 36] File name too long: 'data:image/png;base64,iVBOR](https://github.com/pqzx/html2docx/issues/3) | Existing fix verified | Base64 image handling. |
| [#4 Does it support css styles?](https://github.com/pqzx/html2docx/issues/4) | Implemented subset | Static style tags/selectors, specificity, inheritance, important, and explicit external CSS loading; applied Word properties are listed in the recipes. |
| [#6 IndexError: list index out of range](https://github.com/pqzx/html2docx/issues/6) | Original input tested | Converted and saved the original FILE.txt input and rendered it with LibreOffice. Merging is also covered by regression tests. |
| [#10 Issue with float margins and named (vs RGB) colors](https://github.com/pqzx/html2docx/issues/10) | Fixed and verified | Fractional lengths and named colors. |
| [#12 <img src="data:image/png;base64,xxxx==>](https://github.com/pqzx/html2docx/issues/12) | Existing fix verified | Base64 PNG images. |
| [#13 ValueError: invalid literal for int() with base 10: 'r'](https://github.com/pqzx/html2docx/issues/13) | Verified | hr and heading tags follow separate paths; existing hr tests pass. |
| [#14 Renders as more or less plain text](https://github.com/pqzx/html2docx/issues/14) | Original input tested | Converted/rendered the 5,660-character Qt HTML from the issue. Preserves fonts, size, color, and emphasis; font size alone does not imply a Heading style. |
| [#15 HTML Tag <a href=...](https://github.com/pqzx/html2docx/issues/15) | Verified | Saved/reopened link text and relationships. Older python-docx paragraph.text behavior is a separate concern. |
| [#21 Color conversion not done when a text is in bold or italic](https://github.com/pqzx/html2docx/issues/21) | Fixed | CSS colors also inherit into bold/italic elements. |
| [#22 Tweak to handle links without href](https://github.com/pqzx/html2docx/issues/22) | Fixed | Text in links without href is retained. |
| [#25 Create document from Word template](https://github.com/pqzx/html2docx/issues/25) | Implemented and verified | Existing Word templates, markers across runs, and bookmarks spanning paragraphs; surrounding formatting and bookmarks are tested. |
| [#27 UnicodeDecodeError:   how to convert html documents with accented characters?](https://github.com/pqzx/html2docx/issues/27) | Existing fix verified | UTF-8 file input with non-ASCII text. |
| [#28 Code breaks for base64 image source, saying OSError: [Errno 36] File name too long](https://github.com/pqzx/html2docx/issues/28) | Existing fix verified | Base64 image handling. |
| [#30 <title> attribute should be rendered with the MS Word "Title" style](https://github.com/pqzx/html2docx/issues/30) | Implemented | title creates a Word Title paragraph. |
| [#31 Addin page breaks?](https://github.com/pqzx/html2docx/issues/31) | Implemented | page-break-before/after and break-before/after. |
| [#32 parse_dict_string raising excemptions in edge cases](https://github.com/pqzx/html2docx/issues/32) | Fixed | tinycss2 preserves URL colons, quotes, and whitespace. |
| [#33 Tab_stops](https://github.com/pqzx/html2docx/issues/33) | Supported with example | pre tabs are preserved; recipes show Word tab stops and dotted leaders. |
| [#35 Suggestion for HTML class to Word style mapping](https://github.com/pqzx/html2docx/issues/35) | Implemented | Paragraph classes can map to Quote; inline classes use character style names. |
| [#36 Add support for DocxTemplate fom docxtpl package](https://github.com/pqzx/html2docx/issues/36) | Implemented and verified | Real docxtpl Jinja rendering followed by HTML insertion, save, and reopen. Also fixed reinitializing get_docx and losing rendered content. |
| [#37 'HtmlToDocx' object has no attribute 'run'](https://github.com/pqzx/html2docx/issues/37) | Structural fix; input unavailable | Removed shared run-state dependence. Tests cover leading br, pictures, links, empty input, and cells. The original private input cannot be reproduced. |
| [#38 Getting IndexError: list index out of range when parsing wikipedia page](https://github.com/pqzx/html2docx/issues/38) | Current real input tested | The same Wikipedia URL supplied 2,481,297 bytes, 28 tables, and 626 paragraphs and was PDF-rendered. The original 2022 snapshot was unavailable. |
| [#40 Nested Ordered list not working correctly](https://github.com/pqzx/html2docx/issues/40) | Original input tested | Rendered the attached HTML. Examples cover starts, restarts, depth, li values, and spacing after numbers. |
| [#41 Add the ability to make bold, italics and Underline. Also, can you look into adding superscripts and subscripts?](https://github.com/pqzx/html2docx/issues/41) | Existing fix verified | b/i/sup/sub formatting. |
| [#42 Background Color is Not working](https://github.com/pqzx/html2docx/issues/42) | Fixed | Background colors are stored as real RGB w:shd fills. |
| [#43 table_style = 'TableGrid'](https://github.com/pqzx/html2docx/issues/43) | Fixed | TableGrid alias and public TableStyle.GRID constant. |
| [#44 Converting block level elements like <div> into paragraphs](https://github.com/pqzx/html2docx/issues/44) | Fixed | div, section, and other blocks create paragraphs. |
| [#46 Add classes with specific styles](https://github.com/pqzx/html2docx/issues/46) | Implemented | Tag/class Word style mappings. |
| [#47 Release Latest Version, so we can use paragraph_style support](https://github.com/pqzx/html2docx/issues/47) | Package prepared; publication separate | Built and installed 1.0.0 wheel/sdist with paragraph styles. This repository does not confer upstream PyPI publishing rights. |
| [#48 Unable to convert html with rowspan to docx correctly](https://github.com/pqzx/html2docx/issues/48) | Existing fix verified and extended | The original Phone rowspan case already passed; empty merged cells are now covered too. |
| [#49 margin handler cannot handle percentages](https://github.com/pqzx/html2docx/issues/49) | Fixed | Percent and fractional lengths; percent is relative to available document body width. |
| [#50 Including tables](https://github.com/pqzx/html2docx/issues/50) | Reviewed | Withdrawn by the reporter as malformed HTML; no additional reproduction was requested. |
| [#51 "IndexError: list index out of range" when using colspan attribute](https://github.com/pqzx/html2docx/issues/51) | Fixed | Column counts account for colspan, including empty merged cells. |
| [#52 How can I render HTML-file content to specific tag/word into a template.docx file (word replacement)?](https://github.com/pqzx/html2docx/issues/52) | Implemented and verified | Inline/multi-run/cell markers and single-/multi-paragraph bookmarks. Tests retain surrounding content and inserted image/link/math relationships. |
| [#54 "IndexError: list index out of range" when using rowspan attribute](https://github.com/pqzx/html2docx/issues/54) | Fixed | The Country/Dhaka/Sylhet example checks merge positions and text. |
| [#55 'gbk' codec can't decode byte 0xac in position 1024: illegal multibyte sequence](https://github.com/pqzx/html2docx/issues/55) | Existing fix verified | Explicit UTF-8 reads and an encoding argument. |
| [#57 Poor Performance for Large Tables](https://github.com/pqzx/html2docx/issues/57) | Fixed and measured | Cache the table cell grid rather than repeatedly reconstructing it with Table.cell; see measurements below. |
| [#60 img without src will crash](https://github.com/pqzx/html2docx/issues/60) | Existing fix verified | img without src does not crash. |
| [#61 ImportError: cannot import name 'OxmlElement' from 'docx.oxml'](https://github.com/pqzx/html2docx/issues/61) | Verified in supported environments | Import and document creation are tested with supported dependency ranges; not every historical version combination is guaranteed. |
| [#62 parser crash with a tag  without href](https://github.com/pqzx/html2docx/issues/62) | Fixed | Text in a without href is retained. |
| [#66 [bug] tables containing a <td> whose first child is <br> results in a crash](https://github.com/pqzx/html2docx/issues/66) | Existing fix verified | A leading br inside a cell retains following text. |
| [#67 handling base64 image](https://github.com/pqzx/html2docx/issues/67) | Existing fix verified | Data URL PNGs become real DOCX images. |
| [#68 Underline not converting into docx](https://github.com/pqzx/html2docx/issues/68) | Fixed | CSS text-decoration:underline. |
| [#70 ValueError: invalid literal for int() with base 10: '0.88'](https://github.com/pqzx/html2docx/issues/70) | Fixed and verified | Fractional RGBA alpha works and is composited against the inherited background; 50% red over blue is tested as purple. |
| [#71 Images are not positioned correctly in the resulting DOCX file](https://github.com/pqzx/html2docx/issues/71) | Original images included | Loaded all six public images through an explicit loader, saved DOCX, and rendered PDF. Separate regressions check inline position, CSS dimensions, and surrounding text. |
| [#74 Issue with Ordered List Numbering and Strikethrough Rendering in DOCX](https://github.com/pqzx/html2docx/issues/74) | Fixed; optional frontend added | Numbering restarts per list; parse_markdown handles tables/code/strike, keeps literal code tildes, and checks real Word strike properties. |
| [#75 I continued this project on other repo](https://github.com/pqzx/html2docx/issues/75) | Informational | Announcement of a successor repository, not a product defect. |
| [#78 Security: please enable private vulnerability reporting](https://github.com/pqzx/html2docx/issues/78) | Code and administrative actions separated | Implicit HTTP/CSS fetching was removed and local base paths restricted. Upstream Private Vulnerability Reporting requires its owner to change repository settings. |

## Table performance

A single 300-row × 3-column text table was converted once before and once after
replacement in the same Python 3.14 environment: 10.128 seconds before and 0.057
seconds after. After additional CSS support, a repeat measured 0.089 seconds.
These are individual measurements, not a performance guarantee or a benchmark
of every merge pattern.

## Additional checks and examples

- `tests/test_extended.py`: selectors/cascade/inheritance, relative font sizes,
  alpha compositing, markers/bookmarks, image preservation, DOCTYPE, and nested p.
- `tests/test_examples.py`: execute all 24 examples separately and reopen their
  output to inspect tables, math, links, markers, and templates.
- `tests/test_docx_oracles.py`: compare saved equation/gallery/report content with
  independently authored text answers; see [validation](11-validation.md).
- [Runnable examples](examples/00-index.md): full source, input, generated DOCX
  downloads in the deployed site, and LibreOffice reference PDFs.
- LibreOffice 7.3.7.2 rendered the 24 examples and available original issue inputs.
  Selected report/list/equation screens were inspected. Known visual differences
  and outstanding Word checks are documented in [the limitations](11-validation.md).
- Qt font size alone is not inferred as heading semantics. Explicit headings and
  CSS formatting are preserved; Markdown is available as an optional frontend.
