## Extracts exercises into a csv (input and output file names are command line arguments)
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
import csv

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <input.tex> <output.csv>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, encoding="utf-8") as f:
    data = f.read()

rows = []
current_section = None

# Regex for \section*{...}
section_pattern = re.compile(r'\\section\*\{([^}]*)\}')

# Regex for exercises
exercise_pattern = re.compile(r'(\d+\.\d+\.)\s+(.*?)(?=\n\d+\.\d+\.|\Z)', re.DOTALL)

# Regex for options
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)

for line in data.splitlines():
    sec_match = section_pattern.match(line.strip())
    if sec_match:
        current_section = sec_match.group(1).strip()

for match in exercise_pattern.finditer(data):
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Split at first "\\" into exercise_text and options part
    parts = block.split('\\\\', 1)
    exercise_text = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""

    # Check if dual mode (C + Pascal)
    is_dual = rest.lstrip().startswith("Limbajul C")

    if is_dual:
        # Split into two blocks at "Limbajul Pascal"
        parts_dual = re.split(r'Limbajul Pascal', rest, maxsplit=1)
        c_block = parts_dual[0]
        pascal_block = parts_dual[1] if len(parts_dual) > 1 else ""

        opts_c = {k: "" for k in "abcdef"}
        opts_p = {k: "" for k in "abcdef"}

        for opt_match in option_pattern.finditer(c_block):
            letter, content = opt_match.groups()
            opts_c[letter] = content.strip()

        for opt_match in option_pattern.finditer(pascal_block):
            letter, content = opt_match.groups()
            opts_p[letter] = content.strip()

        rows.append([
            current_section,
            exercise_number,
            exercise_text,
            opts_c["a"], opts_c["b"], opts_c["c"], opts_c["d"], opts_c["e"], opts_c["f"],
            opts_p["a"], opts_p["b"], opts_p["c"], opts_p["d"], opts_p["e"], opts_p["f"],
        ])

    else:
        opts = {k: "" for k in "abcdef"}
        for opt_match in option_pattern.finditer(rest):
            letter, content = opt_match.groups()
            opts[letter] = content.strip()

        rows.append([
            current_section,
            exercise_number,
            exercise_text,
            opts["a"], opts["b"], opts["c"], opts["d"], opts["e"], opts["f"],
            "N/A", "N/A", "N/A", "N/A", "N/A", "N/A",
        ])

# Write to CSV
header = [
    "section", "exercise_number", "exercise_text",
    "a-C", "b-C", "c-C", "d-C", "e-C", "f-C",
    "a-Pascal", "b-Pascal", "c-Pascal", "d-Pascal", "e-Pascal", "f-Pascal"
]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Extracted {len(rows)} exercises to {output_file}")
