import os

file_path = r'h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md'
target_text = '(Redação dada pela Emenda Constitucional nº 65, de 16 de setembro de 2009).'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content.replace(target_text, '')
    
    # Optional: also remove double newlines if they were created, but let's stick to the request first.
    # Actually, the request says "apague todos os textos", so I'll just remove the text.
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully removed occurrences of the target text.")
else:
    print(f"File not found: {file_path}")
