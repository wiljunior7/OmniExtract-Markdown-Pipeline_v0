
import os

file_path = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md"

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"File size: {len(content)} characters")
print(f"Occurrences of '~~': {content.count('~~')}")
print(f"Occurrences of '<strike>': {content.count('<strike>')}")
print(f"Occurrences of '<s>': {content.count('<s>')}")
print(f"Occurrences of '<del>': {content.count('<del>')}")
print(f"Occurrences of 'Emenda': {content.count('Emenda')}")

# Print the first few occurrences of ~~ if any
if '~~' in content:
    idx = content.find('~~')
    print(f"Snippet near first ~~: {content[idx-50:idx+100]}")
else:
    print("No '~~' found.")
