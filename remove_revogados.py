#!/usr/bin/env python3
"""
Script to remove all REVOGADO (revoked) texts from the 
Constituição do Estado do Ceará markdown file.

Patterns to remove:
1. Lines that are themselves "(Revogado)." or "(revogado)." or similar
2. Lines that explain the revocation: "(Revogado pela Emenda...)" or "(Revogada pela Emenda...)"
3. The original text of revoked articles/paragraphs/items that appears BEFORE the revoked marker

The document structure has this pattern for revoked items:
  - Original text (old version)
  - § X (Revogado).
  - (Revogado pela Emenda Constitucional nº XX, de ...)

We need to:
  A) Remove the "(Revogado)" line itself
  B) Remove the "(Revogado pela Emenda...)" explanation line  
  C) Remove the original text that was revoked (the text before the Revogado marker)
"""

import re
import os

filepath = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print(f"Total lines before processing: {len(lines)}")

# First, let's find all lines that contain revogado patterns
revogado_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    # Check for various revogado patterns (case insensitive)
    lower = stripped.lower()
    if 'revogad' in lower:
        revogado_lines.append((i, stripped))
        
print(f"\nFound {len(revogado_lines)} lines containing 'revogad':")
for idx, (line_num, text) in enumerate(revogado_lines):
    print(f"  [{line_num+1}] {text[:120]}")
    if idx > 80:
        print(f"  ... and {len(revogado_lines) - idx - 1} more")
        break

# Strategy:
# We identify "revogado blocks" - groups of lines that should be removed.
# A revogado block consists of:
# 1. The original text line(s) that were revoked
# 2. The "§ X (Revogado)." or "Art. X (Revogado)." or "X – (revogado)." line
# 3. The "(Revogado pela Emenda...)" explanation line

# We'll mark lines for removal
lines_to_remove = set()

for i, line in enumerate(lines):
    stripped = line.strip()
    lower = stripped.lower()
    
    # Pattern 1: Lines that are revogado markers like:
    # "§ 4º (Revogado)."
    # "Art. 8º (Revogado)."
    # "I – (revogado)."
    # "a) (revogado)."
    # "§ 1º F. (Revogado)."
    if re.search(r'\((?:R|r)evogad[oa]\)', stripped):
        lines_to_remove.add(i)
        
        # Look backwards to find the original text that was revoked
        # The original text typically starts with the same article/paragraph/item identifier
        # Extract the identifier from the revogado line
        # e.g., "§ 4º (Revogado)." -> identifier is "§ 4º"
        # e.g., "Art. 8º (Revogado)." -> identifier is "Art. 8º"
        # e.g., "I – (revogado)." -> identifier is "I"
        # e.g., "a) (revogado)." -> identifier is "a)"
        
        # Get the prefix before (Revogado)
        match = re.match(r'^(.+?)\s*\((?:R|r)evogad[oa]\)', stripped)
        if match:
            prefix = match.group(1).strip()
            # Clean the prefix for matching (remove trailing punctuation)
            prefix_clean = prefix.rstrip('.').strip()
            
            # Search backwards for the original text with the same prefix
            j = i - 1
            while j >= 0:
                prev_stripped = lines[j].strip()
                prev_lower = prev_stripped.lower()
                
                # Skip empty lines
                if not prev_stripped:
                    j -= 1
                    continue
                
                # Skip horizontal rules
                if prev_stripped == '---':
                    j -= 1
                    continue
                    
                # Check if this line starts with the same identifier
                if prev_stripped.startswith(prefix_clean):
                    # Found the original text - mark it for removal
                    # It may span multiple lines, so we need to find where it starts
                    lines_to_remove.add(j)
                    
                    # Check if previous lines are continuation of this text
                    # (lines that don't start with an identifier pattern)
                    k = j + 1
                    while k < i:
                        next_stripped = lines[k].strip()
                        if next_stripped and not re.match(r'^(§|Art\.|[IVXLCDM]+\s*[–-]|[a-z]\)|\()', next_stripped) and next_stripped != '---':
                            lines_to_remove.add(k)
                        elif not next_stripped:
                            pass  # keep empty lines for now
                        k += 1
                    
                    # Also check if original text spans backwards (multi-line article text)
                    m = j - 1
                    while m >= 0:
                        prev_prev = lines[m].strip()
                        if not prev_prev:
                            break
                        if prev_prev == '---':
                            break
                        # If it's a continuation line (doesn't start with identifier pattern)
                        if not re.match(r'^(§|Art\.|[IVXLCDM]+\s*[–-]|[a-z]\)|Parágrafo|[\d]+$)', prev_prev):
                            lines_to_remove.add(m)
                        else:
                            break
                        m -= 1
                    
                    break
                    
                # If we hit another article/paragraph/section, stop looking
                if re.match(r'^(####|Art\.\s|§\s|Seção|CAPÍTULO|TÍTULO|Subseção)', prev_stripped):
                    break
                    
                j -= 1
    
    # Pattern 2: Lines that explain the revocation
    # "(Revogado pela Emenda Constitucional nº ...)"
    # "(Revogada pela Emenda Constitucional nº ...)"
    if re.match(r'^\((?:R|r)evogad[oa] pela\s', stripped):
        lines_to_remove.add(i)


# Now remove the marked lines
new_lines = []
for i, line in enumerate(lines):
    if i not in lines_to_remove:
        new_lines.append(line)

# Clean up multiple consecutive empty lines (more than 2)
cleaned_lines = []
empty_count = 0
for line in new_lines:
    if line.strip() == '' or line.strip() == '\r':
        empty_count += 1
        if empty_count <= 2:
            cleaned_lines.append(line)
    else:
        empty_count = 0
        cleaned_lines.append(line)

print(f"\nLines marked for removal: {len(lines_to_remove)}")
print(f"Total lines after processing: {len(cleaned_lines)}")

# Write back
output_content = '\n'.join(cleaned_lines)

# Backup original
backup_path = filepath + '.backup'
if not os.path.exists(backup_path):
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nBackup saved to: {backup_path}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(output_content)
    
print(f"\nProcessed file saved to: {filepath}")

# Verify - check if any revogado remains
remaining = []
for i, line in enumerate(cleaned_lines):
    if 'revogad' in line.lower() or 'Revogad' in line:
        remaining.append((i+1, line.strip()))

if remaining:
    print(f"\nWARNING: {len(remaining)} lines still contain 'revogad':")
    for line_num, text in remaining[:20]:
        print(f"  [{line_num}] {text[:120]}")
else:
    print("\nAll revogado references successfully removed!")
