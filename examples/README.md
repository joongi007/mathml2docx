# Runnable examples

[English](README.md) · [한국어](README.ko.md) · [Example gallery](https://joongi007.github.io/mathml2docx/examples/00-index/)

Download the example ZIP from the gallery and extract it. It contains this
`examples/` package, its helper modules and the required assets. Run the commands
below from the folder containing `examples/`:

```sh
python -m pip install "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
python -m examples.01_quickstart
# Generate all 30 examples:
python -m examples.run_all
```

The installation uses the published PyPI package. All examples require Python
3.6.2+ because some use LaTeX; the core library supports Python 3.6.0+.
docxtpl is used by example 17. See [installation](https://joongi007.github.io/mathml2docx/01-getting-started/)
for individual extras and Python 3.6 pip setup.

For an existing uv or Poetry project, extract the bundle into the project and
use the matching commands instead:

```sh
uv add "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
uv run python -m examples.run_all
```

```sh
poetry add "mathml2docx[latex,markdown]" "docxtpl>=0.16,<1"
poetry run python -m examples.run_all
```

For a new project, follow the [project setup instructions](https://joongi007.github.io/mathml2docx/01-getting-started/)
first. To run one example, replace `examples.run_all` with `examples.01_quickstart`.

Outputs go to `examples/output/`. Run examples as modules with `python -m` so
their package-relative imports work. To use a snippet in your own application,
replace `.support` helpers with your own paths and `document.save(...)` calls.

Sources and assets are shared by the English and Korean documentation. Native
Word equations and LibreOffice can render differently; see
[compatibility and validation](https://joongi007.github.io/mathml2docx/11-validation/).
