import os
import re

try:
    import fitz  # PyMuPDF
except ImportError:
    print("Error: PyMuPDF is not installed. Please run 'pip install PyMuPDF' first.")
    exit(1)

pdf_path = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.pdf"
md_path = r"h:\Vini - Vibe Conding\Workspace\ocr.pdf\OmniExtract Markdown Pipeline\Constituição do Estado do Ceará.md"

def get_strikeout_texts(pdf_path):
    doc = fitz.open(pdf_path)
    strike_texts = set()
    
    for page in doc:
        # 1. Check Text Flags (Bit 4 = 16 for StrikeOut)
        try:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:
                if b.get('type') == 0:
                    for l in b.get("lines", []):
                        current_strike = []
                        for s in l.get("spans", []):
                            if s.get("flags", 0) & 16:
                                current_strike.append(s["text"])
                            else:
                                if current_strike:
                                    text = "".join(current_strike).strip()
                                    if len(text) > 3:
                                        strike_texts.add(text)
                                    current_strike = []
                        if current_strike:
                            text = "".join(current_strike).strip()
                            if len(text) > 3:
                                strike_texts.add(text)
        except Exception as e:
            pass
            
        # 2. Check StrikeOut Annotations
        try:
            for annot in page.annots():
                if annot.type[0] == 8: # StrikeOut
                    text = page.get_textbox(annot.rect).strip()
                    if text and len(text) > 3:
                        strike_texts.add(text)
        except Exception:
            pass
            
        # 3. Check for graphic lines drawn over text (heuristics)
        try:
            drawings = page.get_drawings()
            for d in drawings:
                rect = d["rect"]
                # Look for horizontal thin lines (height < 4, width > 10)
                if rect.width > 10 and rect.height < 4:
                    text = page.get_textbox(rect).strip()
                    # It's possible the text box is slightly taller than the line
                    # Let's expand the rect height a bit just to be sure we catch the text
                    expanded_rect = fitz.Rect(rect.x0, rect.y0 - 6, rect.x1, rect.y1 + 6)
                    text = page.get_textbox(expanded_rect).strip()
                    
                    # Ensure it's not just a separator line
                    if text and len(text) > 3 and not re.match(r'^[-_.]+$', text):
                        # Filter out common false positives like "___"
                        strike_texts.add(text)
        except Exception:
            pass

    return strike_texts

def clean_markdown(md_path, strike_texts):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_len = len(content)
    
    # Sort strike_texts by length descending, so we remove longer matches first
    sorted_strikes = sorted(list(strike_texts), key=len, reverse=True)
    
    removed_count = 0
    for st in sorted_strikes:
        words = st.split()
        if len(words) == 0:
            continue
            
        # Build regex to match the text flexibly, ignoring line breaks or extra spaces
        pattern = r'\s*'.join(re.escape(word) for word in words)
        
        # Make the pattern matching case-insensitive
        regex = re.compile(pattern, re.IGNORECASE)
        
        new_content, count = regex.subn('', content)
        if count > 0:
            removed_count += count
            content = new_content
            
    # Clean up empty lines and orphaned punctuation
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        l = line.strip()
        if l in [',', '.', ';', ':', '-', '–']:
            continue
        new_lines.append(line)
        
    # Remove excessive blank lines
    final_content = re.sub(r'\n{3,}', '\n\n', "\n".join(new_lines))
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + '\n')
        
    print(f"Removed {removed_count} instances of struck-through text.")
    print(f"File size changed from {original_len} to {len(final_content)} characters.")

if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        exit(1)
        
    if not os.path.exists(md_path):
        print(f"MD file not found: {md_path}")
        exit(1)
        
    print("Extracting struck-through texts from PDF...")
    strike_texts = get_strikeout_texts(pdf_path)
    
    # Filter out very common short noise
    filtered_strikes = [t for t in strike_texts if len(t.strip()) > 3 and not re.match(r'^[\W\d_]+$', t)]
    
    print(f"Found {len(filtered_strikes)} unique struck-through phrases in PDF.")
    
    if filtered_strikes:
        # print first few for debugging
        print("Samples of text to remove:")
        for t in filtered_strikes[:5]:
            print(f" - {t[:50]}...")
            
        print("Cleaning markdown...")
        clean_markdown(md_path, filtered_strikes)
        print("Done!")
    else:
        print("No struck-through text found in PDF.")
