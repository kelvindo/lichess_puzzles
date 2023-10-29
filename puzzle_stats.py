import csv
from collections import defaultdict
from process_puzzles import Puzzle

puzzles = []
with open("puzzles/opening_tag.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        puzzle = Puzzle.from_dict(row)
        puzzles.append(puzzle)


opening_counts = defaultdict(int)

for puzzle in puzzles:
    opening_tags = puzzle.opening_tags.split(" ")
    for tag in opening_tags:
        opening_counts[tag] += 1

# print the counts in sorted order
for opening, count in sorted(opening_counts.items(), key=lambda x: x[1], reverse=False):
    print(f"{opening}: {count}")

print(len(opening_counts))
