## Extracts exercises into a csv (input and output file names are command line arguments)
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
import csv

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input.tex> <output.csv>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, encoding="utf-8") as f:
    data = f.read()

# Regex for sections (optional grouping)
section_pattern = re.compile(r'\\section\*\{([^}]*)\}')

# Regex for exercises
exercise_pattern = re.compile(r'(\d+\.\d+\.)\s+(.*?)(?=\n\d+\.\d+\.|\Z)', re.DOTALL)

# Regex for options
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)


def extract_opts(block):
    """Extract a-f options from a block into a dict."""
    opts = {k: "" for k in "abcdef"}
    for m in option_pattern.finditer(block):
        letter, text = m.groups()
        opts[letter] = text.strip()
    return opts


# Get section positions
section_positions = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(data)]

rows = []

for match in exercise_pattern.finditer(data):
    ex_start = match.start()
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Determine section name
    section_name = "Unknown"
    for sec_pos, sec_name in section_positions:
        if sec_pos <= ex_start:
            section_name = sec_name
        else:
            break

    # Split at first "\\" into exercise text and remainder
    parts = block.split('\\\\', 1)
    exercise_text = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""

    # Dual mode
    if rest.lstrip().startswith("Limbajul C++/ Limbajul C"):
        parts_dual = re.split(r'Limbajul Pascal', rest, maxsplit=1)
        cpp_c_block = parts_dual[0]
        pascal_block = parts_dual[1] if len(parts_dual) > 1 else ""

        opts_cpp = extract_opts(cpp_c_block)
        opts_c   = {k: "N/A" for k in "abcdef"}
        opts_p   = extract_opts(pascal_block)

    # Trio mode
    elif rest.lstrip().startswith("Limbajul C++"):
        lang_split = re.split(r'(?=Limbajul (?:C\+\+|C|Pascal))', rest)
        cpp_block    = next((s for s in lang_split if s.startswith("Limbajul C++")), "")
        c_block      = next((s for s in lang_split if s.startswith("Limbajul C\n")), "")
        pascal_block = next((s for s in lang_split if s.startswith("Limbajul Pascal")), "")

        opts_cpp = extract_opts(cpp_block)
        opts_c   = extract_opts(c_block)
        opts_p   = extract_opts(pascal_block)

    # Single mode
    else:
        opts_cpp = extract_opts(rest)
        opts_c   = {k: "N/A" for k in "abcdef"}
        opts_p   = {k: "N/A" for k in "abcdef"}

    rows.append([
        section_name,
        exercise_number,
        exercise_text,
        opts_cpp["a"], opts_cpp["b"], opts_cpp["c"], opts_cpp["d"], opts_cpp["e"], opts_cpp["f"],
        opts_c["a"],   opts_c["b"],   opts_c["c"],   opts_c["d"],   opts_c["e"],   opts_c["f"],
        opts_p["a"],   opts_p["b"],   opts_p["c"],   opts_p["d"],   opts_p["e"],   opts_p["f"],
    ])

# Write CSV
header = [
    "section", "exercise_number", "exercise_text",
    "a-C++", "b-C++", "c-C++", "d-C++", "e-C++", "f-C++",
    "a-C", "b-C", "c-C", "d-C", "e-C", "f-C",
    "a-Pascal", "b-Pascal", "c-Pascal", "d-Pascal", "e-Pascal", "f-Pascal",
    ]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Extracted {len(rows)} exercises to {output_file}")
