#!/usr/bin/env python3
"""Generate the ErrorKey literal in _annotations.py from ERROR_TEMPLATES."""

import re
import textwrap
from pathlib import Path

from smufolib.utils.error import ERROR_TEMPLATES


def main():
    """Main function of the script."""

    filePath = Path(__file__).parents[1] / "smufolib" / "utils" / "_annotations.py"

    content = filePath.read_text(encoding="utf-8")

    # Remove existing ErrorKey literal block if present
    pattern = r"ErrorKey\s*=\s*Literal\[[\s\S]*?\]"
    content = re.sub(pattern, "", content)

    keys = sorted(ERROR_TEMPLATES.keys())  # Sort for stability
    literal_lines = ["    " + repr(k) + "," for k in keys]

    generated = textwrap.dedent(f"""

    ErrorKey = Literal[
    {chr(10).join(literal_lines)}
    ]
    """)

    content = content.rstrip()
    content += generated

    filePath.write_text(content, encoding="utf-8")

    print(f"Appended ErrorKey literal to {filePath}.")


if __name__ == "__main__":
    main()
