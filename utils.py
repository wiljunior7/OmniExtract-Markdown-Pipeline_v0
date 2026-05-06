"""
utils.py — Funções auxiliares do pipeline PDF → Markdown
=========================================================
"""

import io
import re
import unicodedata

import fitz  # PyMuPDF
import pandas as pd
from PIL import Image


# ---------------------------------------------------------------------------
# Detecção de texto tachado (strikethrough)
# ---------------------------------------------------------------------------
def get_strikethrough_rects(page: fitz.Page) -> list[fitz.Rect]:
    """
    Detecta todas as regiões de texto tachado (strikethrough) em uma página,
    coletando informações tanto de anotações quanto de desenhos vetoriais (line art).

    Método 1 — Anotações: busca anotações do tipo PDF_ANNOT_STRIKE_OUT.
    Método 2 — Line art: busca linhas horizontais finas que cruzam o meio
               vertical de blocos de texto (traçado vetorial desenhado
               diretamente no content stream).

    Returns:
        Lista de fitz.Rect representando as áreas tachadas.
    """
    rects: list[fitz.Rect] = []

    # ── 1. Anotações de Strikethrough ──────────────────────────────────
    annots = page.annots()
    if annots:
        for annot in annots:
            if annot.type[0] == fitz.PDF_ANNOT_STRIKE_OUT:
                rects.append(annot.rect)

    # ── 2. Line art (linhas vetoriais horizontais finas) ───────────────
    try:
        drawings = page.get_drawings()
    except Exception:
        drawings = []

    for drawing in drawings:
        for item in drawing.get("items", []):
            # item é uma tupla: ("l", ponto_inicio, ponto_fim) para linhas
            if item[0] != "l":
                continue

            p1, p2 = fitz.Point(item[1]), fitz.Point(item[2])

            # Deve ser horizontal (variação vertical < 2pt)
            if abs(p1.y - p2.y) > 2:
                continue

            # Comprimento mínimo para ser considerada um traço de tachado
            line_length = abs(p2.x - p1.x)
            if line_length < 20:
                continue

            # Cria um retângulo fino ao redor da linha para interseção
            y_center = (p1.y + p2.y) / 2
            x0 = min(p1.x, p2.x)
            x1 = max(p1.x, p2.x)
            line_rect = fitz.Rect(x0, y_center - 4, x1, y_center + 4)
            rects.append(line_rect)

    return rects


def is_span_strikethrough(span_rect: fitz.Rect, strikethrough_rects: list[fitz.Rect]) -> bool:
    """
    Verifica se um span de texto está dentro de uma região tachada.

    A interseção é considerada positiva quando a linha de tachado cruza
    significativamente (≥ 50% da largura do span) a área do span.

    Args:
        span_rect:            Retângulo (bbox) do span de texto.
        strikethrough_rects:  Lista de retângulos de regiões tachadas.

    Returns:
        True se o span estiver coberto por tachado.
    """
    if not strikethrough_rects:
        return False

    for st_rect in strikethrough_rects:
        intersection = span_rect & st_rect  # interseção de retângulos
        if intersection.is_empty:
            continue

        # Verifica se a linha de tachado cobre pelo menos 50% da largura do span
        span_width = span_rect.width
        if span_width <= 0:
            continue
        coverage = intersection.width / span_width
        if coverage >= 0.50:
            return True

    return False

# ---------------------------------------------------------------------------
# Parâmetros de detecção de título
# ---------------------------------------------------------------------------
# Ajuste esses limiares conforme o documento-alvo
TITLE_SIZES = {
    1: 22,   # H1: fonte ≥ 22pt
    2: 17,   # H2: fonte ≥ 17pt
    3: 14,   # H3: fonte ≥ 14pt
    4: 12,   # H4: fonte ≥ 12pt (bold)
}


# ---------------------------------------------------------------------------
# Detecção de nível de título
# ---------------------------------------------------------------------------
def detect_title_level(font_size: float, is_bold: bool) -> int | None:
    """
    Retorna o nível de título Markdown (1-4) ou None se for texto normal.

    Critérios:
      - Fonte grande → H1, H2, H3
      - Fonte média + bold → H4
      - Caso contrário → None (parágrafo comum)
    """
    for level in (1, 2, 3):
        if font_size >= TITLE_SIZES[level]:
            return level
    if font_size >= TITLE_SIZES[4] and is_bold:
        return 4
    return None


# ---------------------------------------------------------------------------
# Limpeza de texto
# ---------------------------------------------------------------------------
def clean_text(text: str) -> str:
    """
    Remove artefatos comuns de extração de PDF:
      - Caracteres de controle
      - Espaços múltiplos
      - Hifenização no fim de linha (word wrap)
      - Normaliza unicode (NFC)
    """
    if not text:
        return ""

    # Normaliza unicode
    text = unicodedata.normalize("NFC", text)

    # Remove caracteres de controle (exceto \n e \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    # Junta palavras hifenizadas no fim de linha
    text = re.sub(r"-\s*\n\s*", "", text)

    # Remove quebras de linha dentro de parágrafos
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Colapsa espaços múltiplos
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


# ---------------------------------------------------------------------------
# OCR de página
# ---------------------------------------------------------------------------
def ocr_page(page: fitz.Page, dpi: int = 300, lang: str = "por+eng") -> str:
    """
    Realiza OCR em uma página PyMuPDF e retorna o texto extraído.

    Args:
        page:  Página fitz.Page a ser processada.
        dpi:   Resolução para rasterização (300 DPI recomendado).
        lang:  Idiomas do Tesseract (padrão: português + inglês).

    Returns:
        Texto extraído via OCR, limpo e normalizado.
    """
    try:
        import pytesseract
    except ImportError:
        raise ImportError("pytesseract não está instalado. Execute: pip install pytesseract")

    # Rasteriza a página como imagem
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat)

    img_data = pix.tobytes("png")
    pix = None  # libera memória

    img = Image.open(io.BytesIO(img_data))

    # OCR com Tesseract
    ocr_text = pytesseract.image_to_string(img, lang=lang, config="--psm 6")

    return clean_text(ocr_text)


# ---------------------------------------------------------------------------
# Salvar imagem extraída do PyMuPDF
# ---------------------------------------------------------------------------
def save_image_from_fitz(pix: fitz.Pixmap, output_path: str) -> None:
    """
    Salva um Pixmap PyMuPDF em disco, convertendo CMYK → RGB se necessário.

    Args:
        pix:         Pixmap PyMuPDF.
        output_path: Caminho de destino (.png).
    """
    if pix.n - pix.alpha > 3:  # CMYK ou outro espaço não-RGB
        pix = fitz.Pixmap(fitz.csRGB, pix)

    pix.save(output_path)


# ---------------------------------------------------------------------------
# DataFrame → Tabela GitHub-Flavored Markdown
# ---------------------------------------------------------------------------
def dataframe_to_markdown_table(df: pd.DataFrame) -> str:
    """
    Converte um pandas DataFrame em tabela Markdown (GitHub-Flavored).

    Trata células multilinhas substituindo \\n por <br> para compatibilidade.

    Args:
        df: DataFrame com os dados da tabela.

    Returns:
        String com a tabela formatada em Markdown.
    """
    if df.empty:
        return ""

    def _escape_cell(val: str) -> str:
        """Escapa pipes e converte quebras de linha em <br>."""
        val = str(val).replace("|", "\\|")
        val = val.replace("\n", "<br>")
        return val.strip()

    # Cabeçalho
    headers = [_escape_cell(col) for col in df.columns]
    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    # Linhas de dados
    data_rows = []
    for _, row in df.iterrows():
        cells = [_escape_cell(str(v)) for v in row]
        data_rows.append("| " + " | ".join(cells) + " |")

    return "\n".join([header_row, separator] + data_rows)

# ---------------------------------------------------------------------------
# OCR de arquivo de imagem
# ---------------------------------------------------------------------------
def ocr_image_file(image_path: str, lang: str = "por+eng") -> str:
    """
    Realiza OCR em um arquivo de imagem e retorna o texto extraído.

    Args:
        image_path: Caminho para a imagem (.png, .jpg, etc).
        lang:  Idiomas do Tesseract (padrão: português + inglês).

    Returns:
        Texto extraído via OCR, limpo e normalizado.
    """
    try:
        import pytesseract
    except ImportError:
        raise ImportError("pytesseract não está instalado. Execute: pip install pytesseract")

    img = Image.open(image_path)
    
    # OCR com Tesseract
    ocr_text = pytesseract.image_to_string(img, lang=lang, config="--psm 6")

    return clean_text(ocr_text)

