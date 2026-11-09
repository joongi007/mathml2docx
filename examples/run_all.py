"""Generate all examples: python -m examples.run_all."""

import importlib

from .support import ROOT


def main():
    for source in sorted(ROOT.glob("[0-9][0-9]_*.py")):
        print("Running", source.stem)
        importlib.import_module("examples." + source.stem)


if __name__ == "__main__":
    main()
