"""
PDF → Markdown Pipeline
========================
Pipeline profissional para extração de PDFs, otimizado para RAG,
bases de conhecimento e ingestão de documentos corporativos.

Funcionalidades:
  ✔ Remove header e footer automaticamente
  ✔ Detecta títulos e subtítulos por análise de fonte
  ✔ Preserva tabelas (GitHub-Flavored Markdown)
  ✔ Extrai imagens e gera referências no Markdown
  ✔ Suporta OCR para PDF escaneado (via pytesseract)
  ✔ Remove automaticamente texto tachado (strikethrough)
  ✔ Gera Markdown estruturado e limpo

Uso:
  python pipeline.py input.pdf [output.md] [--ocr] [--images-dir ./imgs]
"""

import argparse
import logging
import re
import sys
from collections import Counter
from pathlib import Path

import fitz  # PyMuPDF
import pandas as pd
import pdfplumber
from tqdm import tqdm

from utils import (
    ocr_page,
    save_image_from_fitz,
    clean_text,
    dataframe_to_markdown_table,
    detect_title_level,
    ocr_image_file,
    get_strikethrough_rects,
    is_span_strikethrough,
)

# ---------------------------------------------------------------------------
# Configuração de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Silencia bibliotecas terceiras que são extremamente verbosas
for _noisy in ("pdfminer", "pdfplumber", "PIL", "PIL.Image"):
    logging.getLogger(_noisy).setLevel(logging.ERROR)


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
HEADER_FOOTER_THRESHOLD = 0.10  # 10% superior/inferior da página
MIN_REPEATED_RATIO = 0.40       # texto aparece em >40% das páginas → header/footer
MIN_TABLE_ROWS = 1
IMAGE_MIN_WIDTH = 50
IMAGE_MIN_HEIGHT = 50


# ---------------------------------------------------------------------------
# PDFProcessor
# ---------------------------------------------------------------------------
class PDFProcessor:
    """Processa um PDF e gera Markdown estruturado."""

    def __init__(self, pdf_path: str, images_dir: str = "output_images", use_ocr: bool = False,
                 remove_strikethrough: bool = True):
        self.pdf_path = Path(pdf_path)
        self.images_dir = Path(images_dir)
        self.use_ocr = use_ocr
        self.remove_strikethrough = remove_strikethrough
        self.images_dir.mkdir(parents=True, exist_ok=True)

        # Abre com PyMuPDF (visual) e pdfplumber (dados)
        self.fitz_doc = fitz.open(str(self.pdf_path))
        self.plumber_doc = pdfplumber.open(str(self.pdf_path))

        self.total_pages = len(self.fitz_doc)
        self.header_footer_texts: set[str] = set()

        log.info(f"PDF carregado: {self.pdf_path.name} ({self.total_pages} páginas)")
        if self.remove_strikethrough:
            log.info("  → Remoção de texto tachado (strikethrough) ATIVADA")

    # ------------------------------------------------------------------
    # Detecção de Header / Footer
    # ------------------------------------------------------------------
    def _detect_header_footer(self):
        """
        Coleta blocos de texto nas zonas superior e inferior de cada página.
        Textos que se repetem em ≥ MIN_REPEATED_RATIO das páginas são marcados
        como header/footer e serão ignorados na extração.
        """
        log.info("Detectando headers e footers repetidos...")
        candidates: list[str] = []

        for page in self.fitz_doc:
            h = page.rect.height
            w = page.rect.width
            margin = h * HEADER_FOOTER_THRESHOLD

            # Zona do header (topo)
            header_rect = fitz.Rect(0, 0, w, margin)
            # Zona do footer (rodapé)
            footer_rect = fitz.Rect(0, h - margin, w, h)

            for rect in (header_rect, footer_rect):
                text = page.get_text("text", clip=rect).strip()
                if text:
                    candidates.append(text)

        if not candidates:
            return

        counts = Counter(candidates)
        threshold = self.total_pages * MIN_REPEATED_RATIO

        for text, count in counts.items():
            if count >= threshold:
                self.header_footer_texts.add(text)

        log.info(f"  → {len(self.header_footer_texts)} padrões de header/footer encontrados")

    # ------------------------------------------------------------------
    # Verificação se bloco é header/footer
    # ------------------------------------------------------------------
    def _is_header_footer(self, text: str) -> bool:
        if not text:
            return False
        text_stripped = text.strip()
        for hf in self.header_footer_texts:
            if hf in text_stripped or text_stripped in hf:
                return True
        return False

    # ------------------------------------------------------------------
    # Extração de tabelas (pdfplumber)
    # ------------------------------------------------------------------
    def _extract_tables(self, page_index: int) -> list[tuple[tuple, str]]:
        """
        Retorna lista de (bbox, markdown_table) para cada tabela da página.
        bbox = (x0, y0, x1, y1) em coordenadas pdfplumber.
        """
        page = self.plumber_doc.pages[page_index]
        tables_md = []

        try:
            tables = page.find_tables()
        except Exception as e:
            log.warning(f"  Falha ao buscar tabelas na página {page_index + 1}: {e}")
            return []

        for table in tables:
            try:
                data = table.extract()
                if not data or len(data) < MIN_TABLE_ROWS + 1:
                    continue

                # Primeira linha como cabeçalho
                headers = [str(c) if c else "" for c in data[0]]
                rows = [[str(c) if c else "" for c in row] for row in data[1:]]

                df = pd.DataFrame(rows, columns=headers)
                md_table = dataframe_to_markdown_table(df)

                bbox = table.bbox  # (x0, top, x1, bottom)
                tables_md.append((bbox, md_table))
            except Exception as e:
                log.warning(f"  Erro ao extrair tabela: {e}")

        return tables_md

    # ------------------------------------------------------------------
    # Extração de imagens (PyMuPDF)
    # ------------------------------------------------------------------
    def _extract_images(self, page_index: int) -> list[tuple[tuple, str]]:
        """
        Extrai imagens da página e salva em self.images_dir.
        Retorna lista de (bbox, markdown_reference).
        """
        page = self.fitz_doc[page_index]
        images_md = []
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                pix = fitz.Pixmap(self.fitz_doc, xref)

                # Ignora imagens muito pequenas (artefatos de layout)
                if pix.width < IMAGE_MIN_WIDTH or pix.height < IMAGE_MIN_HEIGHT:
                    pix = None
                    continue

                img_name = f"page{page_index + 1}_img{img_index + 1}.png"
                img_path = self.images_dir / img_name
                save_image_from_fitz(pix, str(img_path))

                # Tenta obter a posição da imagem na página
                img_rects = page.get_image_rects(xref)
                bbox = img_rects[0] if img_rects else None

                rel_path = img_path.as_posix()
                md_ref = f"\n![Imagem {img_index + 1} (pág. {page_index + 1})]({rel_path})\n"
                images_md.append((bbox, md_ref))
                pix = None
            except Exception as e:
                log.warning(f"  Erro ao extrair imagem xref={xref}: {e}")

        return images_md

    # ------------------------------------------------------------------
    # Extração de texto com detecção de títulos
    # ------------------------------------------------------------------
    def _extract_text_blocks(self, page_index: int, table_bboxes: list) -> list[str]:
        """
        Extrai blocos de texto, detecta títulos e filtra header/footer.
        Blocos sobrepostos com tabelas são ignorados.
        Spans com texto tachado (strikethrough) são removidos quando habilitado.
        """
        page = self.fitz_doc[page_index]
        h = page.rect.height
        margin = h * HEADER_FOOTER_THRESHOLD

        # Detecta regiões de texto tachado na página
        st_rects: list[fitz.Rect] = []
        if self.remove_strikethrough:
            st_rects = get_strikethrough_rects(page)
            if st_rects:
                log.debug(f"  Página {page_index + 1}: {len(st_rects)} regiões de tachado detectadas")

        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
        text_parts = []

        for block in blocks:
            if block.get("type") != 0:  # 0 = texto
                continue

            bbox = block.get("bbox", (0, 0, 0, 0))
            bx0, by0, bx1, by1 = bbox

            # Filtra zona de header/footer
            if by1 <= margin or by0 >= (h - margin):
                continue

            # Verifica sobreposição com tabelas
            overlaps_table = False
            for (tx0, ty0, tx1, ty1) in table_bboxes:
                if bx0 < tx1 and bx1 > tx0 and by0 < ty1 and by1 > ty0:
                    overlaps_table = True
                    break
            if overlaps_table:
                continue

            # Processa linhas do bloco
            block_text_parts = []
            for line in block.get("lines", []):
                line_text = ""
                max_size = 0
                is_bold = False
                all_strikethrough = True  # assume tachado até provar contrário
                has_any_span = False

                for span in line.get("spans", []):
                    span_text = span.get("text", "").strip()
                    if not span_text:
                        continue

                    has_any_span = True

                    # Verifica se o span está tachado
                    if self.remove_strikethrough and st_rects:
                        span_rect = fitz.Rect(span.get("bbox", (0, 0, 0, 0)))
                        if is_span_strikethrough(span_rect, st_rects):
                            continue  # pula span tachado
                        else:
                            all_strikethrough = False
                    else:
                        all_strikethrough = False

                    size = span.get("size", 12)
                    flags = span.get("flags", 0)
                    bold = bool(flags & 2**4)  # bit 4 = bold

                    if size > max_size:
                        max_size = size
                    if bold:
                        is_bold = True
                    line_text += span_text + " "

                # Se todos os spans da linha eram tachados, pula a linha inteira
                if has_any_span and all_strikethrough and self.remove_strikethrough:
                    continue

                line_text = clean_text(line_text)
                if not line_text:
                    continue
                if self._is_header_footer(line_text):
                    continue

                # Detecta nível de título
                title_level = detect_title_level(max_size, is_bold)
                if title_level:
                    block_text_parts.append(f"\n{'#' * title_level} {line_text}\n")
                else:
                    block_text_parts.append(line_text)

            if block_text_parts:
                text_parts.append("\n".join(block_text_parts))

        return text_parts

    # ------------------------------------------------------------------
    # OCR Fallback
    # ------------------------------------------------------------------
    def _needs_ocr(self, text_parts: list[str]) -> bool:
        """Retorna True se o conteúdo de texto extraído for muito escasso."""
        combined = " ".join(text_parts)
        return len(combined.strip()) < 50

    # ------------------------------------------------------------------
    # Processamento principal
    # ------------------------------------------------------------------
    def process(self) -> str:
        """
        Executa o pipeline completo e retorna o Markdown gerado.
        """
        self._detect_header_footer()

        markdown_pages = []

        log.info("Processando páginas...")
        for page_index in tqdm(range(self.total_pages), desc="Páginas", unit="pág"):

            page_parts = []

            # 1. Extrai tabelas
            tables = self._extract_tables(page_index)
            table_bboxes_plumber = [bbox for bbox, _ in tables]

            # Converte bbox do pdfplumber para coordenadas fitz (y invertido não necessário aqui,
            # pdfplumber usa coordenadas de topo)
            table_bboxes_fitz = table_bboxes_plumber  # mesmo sistema neste contexto

            # 2. Extrai imagens
            images = self._extract_images(page_index)

            # 3. Extrai texto com detecção de títulos
            text_parts = self._extract_text_blocks(page_index, table_bboxes_fitz)

            # 4. OCR fallback
            if self.use_ocr and self._needs_ocr(text_parts):
                log.info(f"  [OCR] Página {page_index + 1} — ativando OCR...")
                ocr_text = ocr_page(self.fitz_doc[page_index])
                if ocr_text:
                    text_parts = [ocr_text]

            # 5. Monta o conteúdo da página
            # Texto
            page_parts.extend(text_parts)

            # Tabelas
            for _, md_table in tables:
                page_parts.append("\n" + md_table + "\n")

            # Imagens
            for _, md_img in images:
                page_parts.append(md_img)

            if page_parts:
                page_md = "\n".join(page_parts).strip()
                if page_md:
                    markdown_pages.append(page_md)

        self.plumber_doc.close()
        self.fitz_doc.close()

        final_md = "\n\n---\n\n".join(markdown_pages)
        return final_md

    # ------------------------------------------------------------------
    # Exportação
    # ------------------------------------------------------------------
    def save(self, output_path: str) -> None:
        """Processa o PDF e salva o Markdown no caminho especificado."""
        md = self.process()
        out = Path(output_path)
        out.write_text(md, encoding="utf-8")
        log.info(f"✅ Markdown salvo em: {out}")
        log.info(f"   Tamanho: {len(md):,} caracteres")


# ---------------------------------------------------------------------------
# ImageProcessor
# ---------------------------------------------------------------------------
class ImageProcessor:
    """Processa uma imagem e extrai seu texto para Markdown."""

    def __init__(self, image_path: str, lang: str = "por+eng"):
        self.image_path = Path(image_path)
        self.lang = lang
        log.info(f"Imagem carregada: {self.image_path.name}")

    def process(self) -> str:
        log.info("Processando OCR da imagem...")
        try:
            text = ocr_image_file(str(self.image_path), lang=self.lang)
            return text
        except Exception as e:
            log.error(f"Erro ao processar imagem via OCR: {e}")
            return ""

    def save(self, output_path: str) -> None:
        md = self.process()
        out = Path(output_path)
        out.write_text(md, encoding="utf-8")
        log.info(f"✅ Markdown (via OCR de Imagem) salvo em: {out}")
        log.info(f"   Tamanho: {len(md):,} caracteres")


# ---------------------------------------------------------------------------
# ExcelProcessor
# ---------------------------------------------------------------------------
class ExcelProcessor:
    """Processa um Excel (múltiplas abas) e gera tabelas Markdown."""

    def __init__(self, excel_path: str):
        self.excel_path = Path(excel_path)
        log.info(f"Excel carregado: {self.excel_path.name}")

    def process(self) -> str:
        log.info("Processando planilhas do Excel...")
        try:
            # Lê todas as abas, preenchendo as colunas vazias de forma segura
            sheet_dict = pd.read_excel(self.excel_path, sheet_name=None)
        except Exception as e:
            log.error(f"Falha ao ler Excel: {e}")
            return ""

        markdown_pages = []
        for sheet_name, df in sheet_dict.items():
            if df.empty:
                continue
            
            # Formata as colunas caso existam colunas omitidas ou unnamed
            df.columns = [str(c) if not str(c).startswith("Unnamed") else "" for c in df.columns]
            
            md_table = dataframe_to_markdown_table(df)
            markdown_pages.append(f"## Planilha: {sheet_name}\n\n{md_table}")
        
        return "\n\n---\n\n".join(markdown_pages)

    def save(self, output_path: str) -> None:
        md = self.process()
        out = Path(output_path)
        out.write_text(md, encoding="utf-8")
        log.info(f"✅ Markdown (Tabelas do Excel) salvo em: {out}")
        log.info(f"   Tamanho: {len(md):,} caracteres")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pipeline profissional PDF / Imagem / Excel → Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="Caminho para o arquivo PDF, Imagem ou Excel (.pdf, .png, .jpg, .xlsx)")
    parser.add_argument("output", nargs="?", help="Caminho de saída (.md). Padrão: mesmo nome do arquivo")
    parser.add_argument("--ocr", action="store_true", help="Ativa OCR como fallback para páginas escaneadas")
    parser.add_argument("--images-dir", default="output_images", help="Diretório para salvar imagens extraídas")
    parser.add_argument("--keep-strikethrough", action="store_true",
                        help="Mantém texto tachado (por padrão, texto tachado é removido)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Logging detalhado")

    args = parser.parse_args()

    if args.verbose:
        # Só aumenta o nível do nosso próprio logger, não de libs externas
        log.setLevel(logging.DEBUG)

    input_path = Path(args.input)
    if not input_path.exists():
        log.error(f"Arquivo não encontrado: {input_path}")
        sys.exit(1)

    output_path = args.output or input_path.with_suffix(".md")

    ext = input_path.suffix.lower()

    if ext == ".pdf":
        processor = PDFProcessor(
            pdf_path=str(input_path),
            images_dir=args.images_dir,
            use_ocr=args.ocr,
            remove_strikethrough=not args.keep_strikethrough,
        )
    elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
        processor = ImageProcessor(image_path=str(input_path))
    elif ext in [".xls", ".xlsx"]:
        processor = ExcelProcessor(excel_path=str(input_path))
    else:
        log.error(f"Formato não suportado para extração: {ext}")
        sys.exit(1)

    processor.save(str(output_path))


if __name__ == "__main__":
    main()
