import re

filepath = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md"

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("\nLines containing 'evogad' (case-insensitive):")
for i, line in enumerate(lines, 1):
    if 'evogad' in line.lower():
        print(f"  Line {i}: {line.rstrip()}")

print(f"\nTotal matches: {sum(1 for line in lines if 'evogad' in line.lower())}")
