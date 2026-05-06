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
    remove_strikethrough=True,      # Remove texto tachado (padrão: True)
)
processor.save("output_pdf.md")

# Exemplo PDF — mantendo texto tachado
processor_with_strikethrough = PDFProcessor(
    pdf_path="seu_documento.pdf",
    remove_strikethrough=False,     # Mantém texto tachado na saída
)
processor_with_strikethrough.save("output_pdf_com_tachado.md")

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
# PDF normal (texto tachado é removido automaticamente):
#   python pipeline.py documento.pdf
#
# PDF mantendo texto tachado:
#   python pipeline.py documento.pdf --keep-strikethrough
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

