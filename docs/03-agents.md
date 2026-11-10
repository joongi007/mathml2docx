# Agents and skills

## Installable skill

Download and extract the [mathml2docx skill ZIP](downloads/mathml2docx-skill.zip).
It contains `mathml2docx/SKILL.md` and a conversion script. Put the folder in a skill
directory supported by your agent. Install the library separately.

The source is `skills/mathml2docx/`. An example request is:

> Use the mathml2docx skill to convert input.html to output.docx, preserving equations.

You can also run the helper directly. It refuses to overwrite existing output and
only enables image processing when `--images` is supplied.

```sh
python skills/mathml2docx/scripts/convert.py input.html output.docx
```

## Machine-readable documentation

- [llms.txt](llms.txt): documentation index and entry points
- [llms-full.txt](llms-full.txt): documentation text from the current build

Both files and the skill ZIP are regenerated from source during each documentation
build. They can be provided to an AI tool or collected by a documentation reader.

## Relationship to MCP

This distribution does not include an MCP server. Static GitHub Pages serves
files and downloads; it does not handle MCP initialization, tool calls, or resource
requests. To expose these documents through MCP, use a separate server that
publishes them as resources. Conversion itself runs through the Python library or
skill helper in a Python environment.
