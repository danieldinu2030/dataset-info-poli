## Extracts solutions into a csv (input and output file names are command line arguments)
# Format example:
# <test_number>.<exercise_number>. Răspuns corect: <a-f>)
# <multiple lines of solution text (if necessary)>

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

# Regex for sections
section_pattern = re.compile(r'\\section\*\{([^}]*)\}')

# Regex for answers
answer_pattern = re.compile(
    r'(\d+\.\d+\.)\s+R[ăa]spuns corect:\s*([a-f])\)\s*(.*?)(?=\n\s*\n|\Z)',
    re.DOTALL
)

# Get section positions
section_positions = [(m.start(), m.group(1).strip()) for m in section_pattern.finditer(data)]

rows = []

all_matches = list(answer_pattern.finditer(data))
print(f"Found {len(all_matches)} answers by regex")

for match in all_matches:
    ex_start = match.start()
    exercise_number = match.group(1)
    answer_letter = match.group(2)

    # Solution should include "Răspuns corect: ..." exactly as in source
    solution_text = f"Răspuns corect: {answer_letter}) {match.group(3).strip()}"

    # Clean trailing whitespace
    solution_text = solution_text.strip()

    # Determine section name
    section_name = "Unknown"
    for sec_pos, sec_name in section_positions:
        if sec_pos <= ex_start:
            section_name = sec_name
        else:
            break

    rows.append([section_name, exercise_number, answer_letter, solution_text])

# Write CSV
header = ["section", "exercise_number", "answer", "solution"]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    writer.writerows(rows)

print(f"Extracted {len(rows)} answers to {output_file}")
