"""
Exemplo de uso programático do pipeline PDF → Markdown
"""

from pipeline import PDFProcessor, ExcelProcessor, ImageProcessor

# ─────────────────────────────────────────────────────────────
# Modo 1: Uso via código Python
# ─────────────────────────────────────────────────────────────

# Exemplo PDF
processor = PDFProcessor(
    pdf_path="seu_documento.pdf",  # ← altere aqui
    images_dir="output_images",    # pasta para salvar imagens extraídas
    use_ocr=False,                  # True para PDFs escaneados
)
processor.save("output_pdf.md")

# Exemplo Excel
excel_processor = ExcelProcessor(
    excel_path="sua_planilha.xlsx", # ← altere aqui
)
excel_processor.save("output_excel.md")

# Exemplo Imagem (OCR)
image_processor = ImageProcessor(
    image_path="sua_imagem.png",    # ← altere aqui
    lang="por+eng"
)
image_processor.save("output_image.md")


# ─────────────────────────────────────────────────────────────
# Modo 2: Linha de comando (CLI)
# ─────────────────────────────────────────────────────────────
#
# O tipo é detectado automaticamente pela extensão:
#
# PDF normal:
#   python pipeline.py documento.pdf
#
# Excel:
#   python pipeline.py planilha.xlsx
#
# Imagem (OCR):
#   python pipeline.py imagem.png
#
# PDF escaneado (OCR explícito via pytesseract para fallback):
#   python pipeline.py documento.pdf --ocr
#
# Especificar saída manual:
#   python pipeline.py imagem.jpg saida.md
