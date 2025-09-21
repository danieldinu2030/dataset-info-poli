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

rows = []

# Regex patterns
section_pattern = re.compile(r'\\section\*\{([^}]*)\}')
exercise_pattern = re.compile(r'(\d+\.\d+\.)\s+(.*?)(?=\n\d+\.\d+\.|\Z)', re.DOTALL)
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)

def split_language_blocks(rest_text):
    """
    Returns dict with keys:
        mode: 'trio' | 'dual' | 'single' | 'single-C'
        cpp_block, c_block, pascal_block
    """
    lines = rest_text.splitlines()
    markers = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == "Limbajul C++/ Limbajul C":
            markers.append((i, "C++/C"))
        elif s == "Limbajul C++":
            markers.append((i, "C++"))
        elif s == "Limbajul C":
            markers.append((i, "C"))
        elif s == "Limbajul Pascal":
            markers.append((i, "Pascal"))

    if not markers:
        return {"mode": "single", "cpp_block": rest_text, "c_block": "", "pascal_block": ""}

    first_idx, first_marker = markers[0]

    if first_marker == "C++/C":
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > first_idx), None)
        cpp_c_block = "\n".join(lines[first_idx+1:pascal_idx if pascal_idx is not None else len(lines)]).strip()
        pascal_block = "\n".join(lines[pascal_idx+1:] if pascal_idx is not None else []).strip()
        return {"mode": "dual", "cpp_block": cpp_c_block, "c_block": "", "pascal_block": pascal_block}

    elif first_marker == "C++":
        c_idx = next((i for i, m in markers if m == "C" and i > first_idx), None)
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > (c_idx if c_idx is not None else first_idx)), None)

        cpp_block = "\n".join(lines[first_idx+1:c_idx if c_idx is not None else (pascal_idx if pascal_idx is not None else len(lines))]).strip()
        c_block = "\n".join(lines[c_idx+1:pascal_idx if pascal_idx is not None else len(lines)]).strip() if c_idx is not None else ""
        pascal_block = "\n".join(lines[pascal_idx+1:] if pascal_idx is not None else []).strip()
        return {"mode": "trio", "cpp_block": cpp_block, "c_block": c_block, "pascal_block": pascal_block}

    elif first_marker == "C":
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > first_idx), None)
        c_block = "\n".join(lines[first_idx+1:pascal_idx if pascal_idx is not None else len(lines)]).strip()
        pascal_block = "\n".join(lines[pascal_idx+1:] if pascal_idx is not None else []).strip()
        return {"mode": "single-C", "cpp_block": "", "c_block": c_block, "pascal_block": pascal_block}

    else:
        return {"mode": "single", "cpp_block": rest_text, "c_block": "", "pascal_block": ""}

# Get section positions for dynamic assignment
section_positions = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(data)]

# Main extraction
for ex in exercise_pattern.finditer(data):
    ex_start = ex.start()
    exercise_number = ex.group(1)
    block = ex.group(2).strip()

    # Determine current section
    section_name = "Unknown"
    for sec_pos, sec_name in section_positions:
        if sec_pos <= ex_start:
            section_name = sec_name
        else:
            break

    # Split at first \\ for exercise text
    parts = block.split('\\\\', 1)
    exercise_text = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""

    info = split_language_blocks(rest)

    # Initialise all options as "N/A"
    opts_cpp = {k: "N/A" for k in "abcdef"}
    opts_c   = {k: "N/A" for k in "abcdef"}
    opts_p   = {k: "N/A" for k in "abcdef"}

    if info["mode"] == "trio":
        for opt_match in option_pattern.finditer(info["cpp_block"]):
            letter, content = opt_match.groups()
            opts_cpp[letter] = content.strip()
        for opt_match in option_pattern.finditer(info["c_block"]):
            letter, content = opt_match.groups()
            opts_c[letter] = content.strip()
        for opt_match in option_pattern.finditer(info["pascal_block"]):
            letter, content = opt_match.groups()
            opts_p[letter] = content.strip()

    elif info["mode"] == "dual":
        for opt_match in option_pattern.finditer(info["cpp_block"]):
            letter, content = opt_match.groups()
            opts_cpp[letter] = content.strip()
        for opt_match in option_pattern.finditer(info["pascal_block"]):
            letter, content = opt_match.groups()
            opts_p[letter] = content.strip()
        # C set remains N/A for dual mode
        # opts_c is intentionally left as N/A

    elif info["mode"] == "single-C":
        for opt_match in option_pattern.finditer(info["c_block"]):
            letter, content = opt_match.groups()
            opts_c[letter] = content.strip()
        for opt_match in option_pattern.finditer(info["pascal_block"]):
            letter, content = opt_match.groups()
            opts_p[letter] = content.strip()

    else:  # single
        for opt_match in option_pattern.finditer(info["cpp_block"]):
            letter, content = opt_match.groups()
            opts_cpp[letter] = content.strip()

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
    "a-Pascal", "b-Pascal", "c-Pascal", "d-Pascal", "e-Pascal", "f-Pascal"
]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Extracted {len(rows)} exercises to {output_file}")
