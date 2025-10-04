## Merge CSV files for exercises and solutions into one CSV

import csv

exercises = 'enunturi.csv'
solutions = 'solutii.csv'
result = 'informatica.csv'

with open(exercises, newline='', encoding='utf-8') as f1, \
     open(solutions, newline='', encoding='utf-8') as f2, \
     open(result, 'w', newline='', encoding='utf-8') as g:
    
    reader1 = csv.reader(f1)
    reader2 = csv.reader(f2)
    writer = csv.writer(g)

    # Read and merge headers correctly
    header1 = next(reader1)
    header2 = next(reader2)
    header = header1 + header2[2:]
    
    # Write CSV
    writer.writerow(header)
    for row1, row2 in zip(reader1, reader2):
        row = row1 + row2[2:]
        writer.writerow(row)

# Report
print(f"Merged {exercises} and {solutions} into {result}.")
