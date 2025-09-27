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

# Regex for options (a) ... f)), each option ends with "\\" or end-of-block
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)

def extract_opts(block):
    """Extract a-f options from a block into a dict of strings (empty if missing)."""
    opts = {k: "" for k in "abcdef"}
    for m in option_pattern.finditer(block):
        letter, text = m.groups()
        opts[letter] = text.strip()
    return opts

def check_all_opts(block):
    """Return True if block contains all option letters a-f (presence, not content length)."""
    found = set()
    for m in option_pattern.finditer(block):
        found.add(m.group(1))
    return set("abcdef").issubset(found)

# Get section positions (start index, name)
section_positions = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(data)]

rows = []
skipped = 0

for match in exercise_pattern.finditer(data):
    ex_start = match.start()
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Determine section name (last section whose position <= exercise start)
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

    # Dual mode: "Limbajul C++/ Limbajul C"
    if rest.lstrip().startswith("Limbajul C++/ Limbajul C") or re.match(r'^\s*Limbajul C\+\+\s*/\s*Limbajul C', rest):
        # Capture the combined C++/C block (up to Limbajul Pascal or end) and optional Pascal block
        m_cppc = re.search(r'(?s)Limbajul C\+\+\s*/\s*Limbajul C\s*(.*?)(?=(?:Limbajul Pascal\b|\Z))', rest)
        m_pas  = re.search(r'(?s)Limbajul Pascal\s*(.*)', rest)

        cppc_block = m_cppc.group(1) if m_cppc else ""
        pascal_block = m_pas.group(1) if m_pas else ""

        ok_cppc = check_all_opts(cppc_block)
        ok_pas  = check_all_opts(pascal_block)

        if not (ok_cppc and ok_pas):
            print(f"{exercise_number} does not match (dual mode) — missing options; skipping")
            skipped += 1
            continue

        opts_cpp = extract_opts(cppc_block)
        # In dual mode, the same options apply to both C++ and C
        opts_c = opts_cpp.copy()
        opts_p = extract_opts(pascal_block)
        mode = "Dual"

    # Trio mode: separate Limbajul C++, Limbajul C, Limbajul Pascal (all required)
    elif rest.lstrip().startswith("Limbajul C++"):
        m_cpp = re.search(r'(?s)Limbajul C\+\+\s*(.*?)(?=(?:Limbajul C\b|Limbajul Pascal\b|\Z))', rest)
        m_c   = re.search(r'(?s)Limbajul C\s*(.*?)(?=(?:Limbajul Pascal\b|\Z))', rest)
        m_pas = re.search(r'(?s)Limbajul Pascal\s*(.*)', rest)

        cpp_block = m_cpp.group(1) if m_cpp else ""
        c_block   = m_c.group(1)   if m_c   else ""
        pascal_block = m_pas.group(1) if m_pas else ""

        ok_cpp = check_all_opts(cpp_block)
        ok_c   = check_all_opts(c_block)
        ok_pas = check_all_opts(pascal_block)

        if not (ok_cpp and ok_c and ok_pas):
            print(f"{exercise_number} does not match (trio mode) — missing options; skipping")
            skipped += 1
            continue

        opts_cpp = extract_opts(cpp_block)
        opts_c   = extract_opts(c_block)
        opts_p   = extract_opts(pascal_block)
        mode = "Trio"

    # Single mode: only one language block in 'rest' (treated as C++ block)
    else:
        if not check_all_opts(rest):
            print(f"{exercise_number} does not match (single mode) — missing options; skipping")
            skipped += 1
            continue

        opts_cpp = extract_opts(rest)
        opts_c   = {k: "N/A" for k in "abcdef"}
        opts_p   = {k: "N/A" for k in "abcdef"}
        mode = "Single"

    # Append CSV row (only for exercises that passed validation)
    rows.append([
        section_name,
        exercise_number,
        mode,
        exercise_text,
        opts_cpp["a"], opts_cpp["b"], opts_cpp["c"], opts_cpp["d"], opts_cpp["e"], opts_cpp["f"],
        opts_c["a"],   opts_c["b"],   opts_c["c"],   opts_c["d"],   opts_c["e"],   opts_c["f"],
        opts_p["a"],   opts_p["b"],   opts_p["c"],   opts_p["d"],   opts_p["e"],   opts_p["f"],
    ])

# Write CSV
header = [
    "section", "exercise_number", "mode", "exercise_text",
    "a-C++", "b-C++", "c-C++", "d-C++", "e-C++", "f-C++",
    "a-C", "b-C", "c-C", "d-C", "e-C", "f-C",
    "a-Pascal", "b-Pascal", "c-Pascal", "d-Pascal", "e-Pascal", "f-Pascal",
]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Extracted {len(rows)} exercises to {output_file}")
if skipped:
    print(f"Skipped {skipped} exercises due to format mismatches.")
