import re
import os

filepath = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md"

def get_level_and_id(line):
    l = line.strip()
    if not l: return None, None
    
    # Headers
    if l.startswith('#### TÍTULO'): return 1, l
    if l.startswith('#### CAPÍTULO'): return 2, l
    if l.startswith('#### Seção'): return 3, l
    if l.startswith('#### Subseção'): return 4, l
    
    # Articles
    match = re.match(r'^Art\.\s*(\d+[A-Z-]*)\.?', l)
    if match: return 5, f"Art. {match.group(1)}"
    
    # Paragraphs
    if l.startswith('Parágrafo único'): return 6, "Parágrafo único"
    match = re.match(r'^§\s*(\d+)\.?', l)
    if match: return 6, f"§ {match.group(1)}"
    
    # Items
    match = re.match(r'^([IVXLCDM]+)\s*[–-]', l)
    if match: return 7, match.group(1)
    
    # Sub-items
    match = re.match(r'^([a-z])\)', l)
    if match: return 8, match.group(1)
    
    return None, None

def clean_document():
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Initial line count: {len(lines)}")

    # Step 1: Group into blocks
    blocks = []
    current_block = []
    current_level = 0
    current_id = None
    
    for line in lines:
        level, id_ = get_level_and_id(line)
        if level is not None:
            if current_block:
                blocks.append({
                    'level': current_level,
                    'id': current_id,
                    'lines': current_block
                })
            current_block = [line]
            current_level = level
            current_id = id_
        else:
            current_block.append(line)
    
    if current_block:
        blocks.append({
            'level': current_level,
            'id': current_id,
            'lines': current_block
        })

    print(f"Found {len(blocks)} blocks.")

    # Step 2: Remove obsolete versions
    final_blocks = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b['id'] is None:
            final_blocks.append(b)
            i += 1
            continue
            
        # Check if next block is a "duplicate" version of this one
        j = i + 1
        is_obsolete = False
        while j < len(blocks):
            next_b = blocks[j]
            
            # If same ID and Level, then i is obsolete
            if next_b['id'] == b['id'] and next_b['level'] == b['level']:
                is_obsolete = True
                break
                
            # If we hit a HIGHER level (e.g. Art. -> CHAPTER), stop
            if next_b['level'] is not None and next_b['level'] < b['level']:
                break
                
            # If we hit a different ID at SAME level, stop
            if next_b['level'] == b['level'] and next_b['id'] != b['id']:
                # Special case: check for footnotes/rules between duplicates
                is_trivial = True
                for l in next_b['lines']:
                    ls = l.strip()
                    if ls and ls != '---' and not re.match(r'^\d+$', ls):
                        is_trivial = False
                        break
                if not is_trivial:
                    break
            j += 1
            
        if not is_obsolete:
            final_blocks.append(b)
        i += 1

    # Step 3: Final filter for markers and "Revogado" blocks
    output_lines = []
    for b in final_blocks:
        # Check if block is marked as Revogado
        is_revogado = False
        for line in b['lines']:
            if re.search(r'\(revogad[oa]\)', line, re.I):
                is_revogado = True
                break
        
        if is_revogado:
            continue
            
        for line in b['lines']:
            l = line.strip()
            # Remove metadata notes
            if l.startswith('(Redação dada') or \
               l.startswith('(Inserido') or \
               l.startswith('(Substituída') or \
               l.startswith('(Suprimida') or \
               l.startswith('(Declarado inconstitucional') or \
               l.startswith('(Decisão proferida') or \
               l.startswith('(Trecho declarado inconstitucional') or \
               l.startswith('(Suspenso por medida cautelar'):
                continue
            
            # Skip horizontal rules and footnote numbers on their own
            if l == '---' or re.match(r'^\d+$', l):
                continue
                
            output_lines.append(line)

    # Step 4: Clean up extra whitespace
    final_content = "".join(output_lines)
    final_content = re.sub(r'\n{3,}', '\n\n', final_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + '\n')

    print(f"Final line count: {len(output_lines)}")
    print("Cleanup complete.")

if __name__ == "__main__":
    clean_document()
