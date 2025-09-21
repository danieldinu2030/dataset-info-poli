## Check for regex exercise format before running extract_enunturi.py
# Format example:
# <test_number>.<exercise_number>. <beginning of exercise text>
# <multiple lines of exercise text (if necessary)>
# \\
# Limbajul C++/ Limbajul C (optional, if it exists, then all optional lines below exist)
# a) option a
# \\
# b) option b
# \\
# c) option c
# \\
# d) option d
# \\
# e) option e
# \\
# f) option f
# \\
# Limbajul Pascal (optional)
# \\
# a) option a-Pascal (optional)
# \\
# b) option b-Pascal (optional)
# \\
# c) option c-Pascal (optional)
# \\
# d) option d-Pascal (optional)
# \\
# e) option e-Pascal (optional)
# \\
# f) option f-Pascal (optional)
# \\

import re
import sys

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <input.tex>")
    sys.exit(1)

input_file = sys.argv[1]

with open(input_file, encoding="utf-8") as f:
    data = f.read()

# Regex for exercises
exercise_pattern = re.compile(r'(\d+\.\d+\.)\s+(.*?)(?=\n\d+\.\d+\.|\Z)', re.DOTALL)

# Regex for verbatim blocks
verbatim_pattern = re.compile(r'\\begin{verbatim}(.*?)\\end{verbatim}', re.DOTALL)

# Regex for options
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)

for match in exercise_pattern.finditer(data):
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Check for \\ inside verbatim in this block
    verbatim_blocks = verbatim_pattern.findall(block)
    verbatim_has_backslash = any(r"\\" in vb for vb in verbatim_blocks)

    # Mask verbatim blocks so we can safely split on \\ outside them
    def mask_verbatim(text):
        def replacer(match):
            return "__VERBATIM__"
        return verbatim_pattern.sub(replacer, text)

    masked_block = mask_verbatim(block)

    # Split at first \\ (outside of verbatim)
    parts = masked_block.split('\\\\', 1)
    rest = parts[1].strip() if len(parts) > 1 else ""

    is_dual = rest.lstrip().startswith("Limbajul C")

    if is_dual:
        parts_dual = re.split(r'Limbajul Pascal', rest, maxsplit=1)
        c_block = parts_dual[0]
        pascal_block = parts_dual[1] if len(parts_dual) > 1 else ""

        opts_c = {k: "" for k in "abcdef"}
        opts_p = {k: "" for k in "abcdef"}

        for opt_match in option_pattern.finditer(c_block):
            letter, _ = opt_match.groups()
            opts_c[letter] = "X"

        for opt_match in option_pattern.finditer(pascal_block):
            letter, _ = opt_match.groups()
            opts_p[letter] = "X"

        match_status = "matches" if all(opts_c.values()) and all(opts_p.values()) else "does not match"
        msg = f"{exercise_number} {match_status} (dual mode)"
    else:
        opts = {k: "" for k in "abcdef"}
        for opt_match in option_pattern.finditer(rest):
            letter, _ = opt_match.groups()
            opts[letter] = "X"

        match_status = "matches" if all(opts.values()) else "does not match"
        msg = f"{exercise_number} {match_status} (single mode)"

    # Add warning inline if needed
    if verbatim_has_backslash:
        msg += ", but contains '\\\\' inside a verbatim block; this will break extraction regex"

    print(msg)