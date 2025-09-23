## Check for regex exercise format before running extract_enunturi.py
# Format example:
# <test_number>.<exercise_number>. <beginning of exercise text>
# <multiple lines of exercise text (if necessary)>
# \\
# Limbajul C++
# a) option a-C++
# \\
# b) option b-C++
# \\
# c) option c-C++
# \\
# d) option d-C++
# \\
# e) option e-C++
# \\
# f) option f-C++
# \\
# Limbajul C (optional)
# \\
# a) option a-C (optional)
# \\
# b) option b-C (optional)
# \\
# c) option c-C (optional)
# \\
# d) option d-C (optional)
# \\
# e) option e-C (optional)
# \\
# f) option f-C (optional)
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

# Regex for options
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)


def check_all_opts(block):
    """Return True if block has all a-f options."""
    opts = {k: "" for k in "abcdef"}
    for opt_match in option_pattern.finditer(block):
        letter, _ = opt_match.groups()
        opts[letter] = "X"
    return all(opts.values())


for match in exercise_pattern.finditer(data):
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Split at first "\\" into exercise_text and options
    parts = block.split('\\\\', 1)
    rest = parts[1].strip() if len(parts) > 1 else ""

    # Dual mode
    if rest.lstrip().startswith("Limbajul C++/ Limbajul C"):
        parts_dual = re.split(r'Limbajul Pascal', rest, maxsplit=1)
        cpp_c_block = parts_dual[0]
        pascal_block = parts_dual[1] if len(parts_dual) > 1 else ""

        ok = check_all_opts(cpp_c_block) and check_all_opts(pascal_block)
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (dual mode)"
        print(msg)
        continue # skip to next exercise

    # Trio mode
    if rest.lstrip().startswith("Limbajul C++"):
        # Use safer regex groups
        m_cpp = re.search(r'(?s)Limbajul C\+\+\s*(.*?)(?=(?:Limbajul C\b|Limbajul Pascal\b|\Z))', rest)
        m_c   = re.search(r'(?s)Limbajul C\s*(.*?)(?=(?:Limbajul Pascal\b|\Z))', rest)
        m_pas = re.search(r'(?s)Limbajul Pascal\s*(.*)', rest)

        cpp_block = m_cpp.group(1) if m_cpp else ""
        c_block   = m_c.group(1)   if m_c   else ""
        pascal_block = m_pas.group(1) if m_pas else ""

        ok = check_all_opts(cpp_block) and check_all_opts(c_block) and check_all_opts(pascal_block)
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (trio mode)"
        print(msg)
        continue # skip to the next exercise

    # Single mode
    ok = check_all_opts(rest)
    msg = f"{exercise_number} {'matches' if ok else 'does not match'} (single mode)"
    print(msg)
