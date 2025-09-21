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

# Regex for verbatim blocks
verbatim_pattern = re.compile(r'\\begin{verbatim}(.*?)\\end{verbatim}', re.DOTALL)

# Regex for options
option_pattern = re.compile(r'([a-f])\)\s*(.*?)(?=\\\\|\Z)', re.DOTALL)

# --- helper: split into language blocks ---
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
        # Dual mode: only C++ block checked, C ignored
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > first_idx), None)
        start = first_idx + 1
        end = pascal_idx if pascal_idx is not None else len(lines)
        cpp_block = "\n".join(lines[start:end]).strip()
        pascal_block = "\n".join(lines[pascal_idx+1:]).strip() if pascal_idx is not None else ""
        return {"mode": "dual", "cpp_block": cpp_block, "c_block": "", "pascal_block": pascal_block}

    elif first_marker == "C++":
        c_idx = next((i for i, m in markers if m == "C" and i > first_idx), None)
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > (c_idx if c_idx is not None else first_idx)), None)

        cpp_start = first_idx + 1
        cpp_end = c_idx if c_idx is not None else (pascal_idx if pascal_idx is not None else len(lines))
        cpp_block = "\n".join(lines[cpp_start:cpp_end]).strip()

        c_block = ""
        if c_idx is not None:
            c_start = c_idx + 1
            c_end = pascal_idx if pascal_idx is not None else len(lines)
            c_block = "\n".join(lines[c_start:c_end]).strip()

        pascal_block = ""
        if pascal_idx is not None:
            p_start = pascal_idx + 1
            pascal_block = "\n".join(lines[p_start:]).strip()

        return {"mode": "trio", "cpp_block": cpp_block, "c_block": c_block, "pascal_block": pascal_block}

    elif first_marker == "C":
        c_start = first_idx + 1
        pascal_idx = next((i for i, m in markers if m == "Pascal" and i > first_idx), None)
        c_end = pascal_idx if pascal_idx is not None else len(lines)
        c_block = "\n".join(lines[c_start:c_end]).strip()
        pascal_block = "\n".join(lines[pascal_idx+1:]).strip() if pascal_idx is not None else ""
        return {"mode": "single-C", "cpp_block": "", "c_block": c_block, "pascal_block": pascal_block}

    else:
        return {"mode": "single", "cpp_block": rest_text, "c_block": "", "pascal_block": ""}

# Helper to check if all six options are present
def has_all_opts(text_block):
    opts = {k: "" for k in "abcdef"}
    for opt_match in option_pattern.finditer(text_block):
        letter, _ = opt_match.groups()
        opts[letter] = "X"
    return all(opts.values())

# Main check
for match in exercise_pattern.finditer(data):
    exercise_number = match.group(1)
    block = match.group(2).strip()

    # Detect \\ inside verbatim
    verbatim_blocks = verbatim_pattern.findall(block)
    verbatim_has_backslash = any('\\\\' in vb for vb in verbatim_blocks)

    # Mask verbatim blocks to avoid splitting inside them
    masked_block = verbatim_pattern.sub("__VERBATIM__", block)
    parts = masked_block.split('\\\\', 1)
    rest = parts[1].strip() if len(parts) > 1 else ""

    info = split_language_blocks(rest)

    if info["mode"] == "trio":
        ok = has_all_opts(info["cpp_block"]) and has_all_opts(info["c_block"]) and has_all_opts(info["pascal_block"])
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (trio mode)"

    elif info["mode"] == "dual":
        # Only C++ options checked in dual mode
        ok = has_all_opts(info["cpp_block"]) and (not info["pascal_block"] or has_all_opts(info["pascal_block"]))
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (dual mode)"

    elif info["mode"] == "single-C":
        ok = has_all_opts(info["c_block"]) and (not info["pascal_block"] or has_all_opts(info["pascal_block"]))
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (single-C mode)"

    else:  # single
        ok = has_all_opts(info["cpp_block"])
        msg = f"{exercise_number} {'matches' if ok else 'does not match'} (single mode)"

    if verbatim_has_backslash:
        msg += ", contains '\\\\' inside a verbatim block (may break extraction)"

    print(msg)
