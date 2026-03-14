[🇧🇷 Português](#português) | [🇺🇸 English](#english) | [🇪🇸 Español](#español) | [🇨🇳 中文](#中文)

---

<a id="português"></a>
# 🇧🇷 OmniExtract Markdown Pipeline 📄🖼️📊

Um pipeline profissional em Python para extração de dados e conversão de **PDFs, Imagens e Planilhas Excel** para o formato Markdown limpo e estruturado.

Este projeto foi projetado para ser ideal para a preparação de documentos, criação de bases de conhecimento, pipelines de Ingestão de Dados (RAG - *Retrieval-Augmented Generation*) e uso por Large Language Models (LLMs).

## 🚀 Funcionalidades

- **Extração de PDFs**:
  - Remove automaticamente cabeçalhos e rodapés repetitivos.
  - Detecta títulos e subtítulos analisando o tamanho e formatação da fonte.
  - Preserva e converte tabelas para o formato GitHub-Flavored Markdown.
  - Extrai imagens embutidas, salvando-as localmente e referenciando-as no arquivo Markdown gerado.
  - Suporte a fallback de OCR para PDFs digitalizados (escaneados).
- **Extração de Imagens**:
  - Processa imagens avulsas (`.png`, `.jpg`, `.jpeg`, etc.) utilizando OCR para converter o texto detectado em Markdown.
- **Extração de Excel**:
  - Processa múltiplas planilhas (`.xlsx`) de um único arquivo.
  - Converte as guias e suas tabelas inteiras nativamente para tabelas em formato Markdown de forma segura.

## 🛠️ Tecnologias Utilizadas

- **PDF**: `PyMuPDF` (layout e imagens), `pdfplumber` (tabelas precisas)
- **OCR**: `pytesseract` (invólucro para o Tesseract-OCR), `Pillow` (PIL)
- **Dados/Tabelas**: `pandas`, `openpyxl`, `tabulate`

## ⚙️ Instalação e Requisitos

### 1. Requisitos do Sistema
Para utilizar a funcionalidade de OCR (necessária para Imagens e PDFs digitalizados), você precisa ter o **Tesseract OCR** instalado na sua máquina e adicionado ao `PATH` do sistema.

- **Windows**: Você pode baixar e instalar o Tesseract [aqui](https://github.com/UB-Mannheim/tesseract/wiki).

### 2. Dependências Python
Clone este repositório e instale as dependências contidas no `requirements.txt`:

```bash
git clone https://github.com/seu-usuario/omniextract-markdown.git
cd omniextract-markdown
pip install -r requirements.txt
```

## 💻 Como Usar

O pipeline reconhece automaticamente a extensão do arquivo passado como input (`.pdf`, `.png`, `.xlsx`, etc.).

### Modo 1: Linha de Comando (CLI)

```bash
# PDF normal (texto digital nativo)
python pipeline.py documento.pdf

# PDF escaneado (forçando OCR via Tesseract)
python pipeline.py documento.pdf --ocr

# Planilha Excel (transforma todas as abas em tabelas Markdown)
python pipeline.py relatorios.xlsx

# Arquivo de Imagem (aciona o OCR automaticamente)
python pipeline.py foto_documento.png
```

### Modo 2: Programaticamente via código (Python)
Veja exemplos completos em `example_usage.py`.

```python
from pipeline import PDFProcessor, ExcelProcessor, ImageProcessor

# Processando Excel
excel = ExcelProcessor(excel_path="dados.xlsx")
excel.save("dados.md")
```

---

<br>

<a id="english"></a>
# 🇺🇸 OmniExtract Markdown Pipeline 📄🖼️📊

A professional Python pipeline for data extraction and conversion from **PDFs, Images, and Excel Spreadsheets** to a clean and structured Markdown format.

This project is designed to be ideal for document preparation, knowledge base creation, Data Ingestion pipelines (RAG - *Retrieval-Augmented Generation*), and usage by Large Language Models (LLMs).

## 🚀 Features

- **PDF Extraction**:
  - Automatically removes repetitive headers and footers.
  - Detects titles and subtitles by analyzing font size and formatting.
  - Preserves and converts tables to GitHub-Flavored Markdown format.
  - Extracts embedded images, saving them locally and referencing them in the generated Markdown.
  - OCR fallback support for scanned PDFs.
- **Image Extraction**:
  - Processes single images (`.png`, `.jpg`, `.jpeg`, etc.) using OCR to convert the detected text into Markdown.
- **Excel Extraction**:
  - Processes multiple sheets (`.xlsx`) from a single file.
  - Safely converts tabs and entire tables natively to Markdown format.

## 🛠️ Technologies Used

- **PDF**: `PyMuPDF` (layout and images), `pdfplumber` (precise tables)
- **OCR**: `pytesseract` (Tesseract-OCR wrapper), `Pillow` (PIL)
- **Data/Tables**: `pandas`, `openpyxl`, `tabulate`

## ⚙️ Installation and Requirements

### 1. System Requirements
To use the OCR functionality (required for Images and scanned PDFs), you must have **Tesseract OCR** installed on your machine and added to your system's `PATH`.

- **Windows**: Download and install Tesseract [here](https://github.com/UB-Mannheim/tesseract/wiki).

### 2. Python Dependencies
Clone this repository and install the dependencies from `requirements.txt`:

```bash
git clone https://github.com/your-username/omniextract-markdown.git
cd omniextract-markdown
pip install -r requirements.txt
```

## 💻 How to Use

The pipeline automatically detects the input file extension (`.pdf`, `.png`, `.xlsx`, etc.).

### Mode 1: Command Line (CLI)

```bash
# Standard PDF (native text)
python pipeline.py document.pdf

# Scanned PDF (forcing OCR)
python pipeline.py document.pdf --ocr

# Excel Spreadsheet (all sheets to Markdown)
python pipeline.py reports.xlsx

# Image file (auto OCR triggers)
python pipeline.py document_photo.png
```

### Mode 2: Programmatically (Python Code)
Check out complete examples in `example_usage.py`.

```python
from pipeline import PDFProcessor, ExcelProcessor, ImageProcessor

# Processing Excel
excel = ExcelProcessor(excel_path="data.xlsx")
excel.save("data.md")
```

---

<br>

<a id="español"></a>
# 🇪🇸 OmniExtract Markdown Pipeline 📄🖼️📊

Un pipeline profesional en Python para la extracción de datos y la conversión de **PDFs, Imágenes y Hojas de cálculo en Excel** a un formato Markdown limpio y estructurado.

Este proyecto ha sido diseñado para ser ideal en la preparación de documentos, la creación de bases de conocimiento, los pipelines de Ingestión de Datos (RAG - *Retrieval-Augmented Generation*) y su uso por Modelos de Gran Lenguaje (LLMs).

## 🚀 Características

- **Extracción de PDF**:
  - Elimina automáticamente encabezados y pies de página repetitivos.
  - Detecta títulos y subtítulos analizando el tamaño y el formato de la fuente.
  - Preserva y convierte tablas al formato GitHub-Flavored Markdown.
  - Extrae opciones de imágenes integradas, guardándolas localmente y referenciándolas en el código Markdown generado.
  - Soporte de respaldo OCR para PDFs escaneados.
- **Extracción de Imágenes**:
  - Procesa imágenes independientes (`.png`, `.jpg`, `.jpeg`, etc.) usando OCR para convertir el texto detectado en Markdown.
- **Extracción de Excel**:
  - Procesa múltiples pestañas (`.xlsx`) de un solo archivo.
  - Convierte las pestañas y tablas enteras de forma nativa a tablas en formato Markdown de manera segura.

## 🛠️ Tecnologías Utilizadas

- **PDF**: `PyMuPDF` (diseño y gráficos), `pdfplumber` (tablas precisas)
- **OCR**: `pytesseract` (envoltorio para Tesseract-OCR), `Pillow` (PIL)
- **Datos/Tablas**: `pandas`, `openpyxl`, `tabulate`

## ⚙️ Instalación y Requisitos

### 1. Requisitos del Sistema
Para la funcionalidad OCR (necesaria para Imágenes y PDFs escaneados), debes tener **Tesseract OCR** instalado en tu máquina y añadido al `PATH` de tu sistema.

- **Windows**: Descargue e instale Tesseract [aquí](https://github.com/UB-Mannheim/tesseract/wiki).

### 2. Dependencias de Python
Clona este repositorio e instala las dependencias de `requirements.txt`:

```bash
git clone https://github.com/tu-usuario/omniextract-markdown.git
cd omniextract-markdown
pip install -r requirements.txt
```

## 💻 Uso

El pipeline detecta automáticamente la extensión de salida del archivo (`.pdf`, `.png`, `.xlsx`, etc.).

### Modo 1: Línea de Comandos (CLI)

```bash
# PDF estándar (texto nativo)
python pipeline.py documento.pdf

# PDF escaneado (OCR forzado)
python pipeline.py documento.pdf --ocr

# Excel (todas las hojas unidas al Markdown)
python pipeline.py informes.xlsx

# Archivo de imagen (activadores OCR automáticos)
python pipeline.py documento_foto.png
```

### Modo 2: Código Programáticamente
Vea los ejemplos completos que están en `example_usage.py`.

```python
from pipeline import PDFProcessor, ExcelProcessor, ImageProcessor

# Procesando datos en Excel
excel = ExcelProcessor(excel_path="datos.xlsx")
excel.save("datos.md")
```

---

<br>

<a id="中文"></a>
# 🇨🇳 OmniExtract Markdown Pipeline 📄🖼️📊

一个用于从 **PDF，图像和Excel电子表格** 中提取和转换为干净、结构化的Markdown格式的专业Python数据处理管道。

该项目旨在成为大语言模型（LLMs）、准备分析数据文档、知识库创建和构建RAG架构数据检索和增强管线的最理想解。

## 🚀 特点

- **PDF 提取**:
  - 自动删除重复使用的页眉和页脚。
  - 通过对字体格式和大小智能分析检测出标题级别。
  - 保留并将表格转换为 GitHub-Flavored Markdown 表格格式。
  - 提取文件内容直接内置的图像、将它们保存在本地文件夹中及于生成的Markdown文件中调用本地图像呈现。
  - OCR用于扫描PDF文件的识别检测。
- **图片提取**:
  - 充分利用 OCR 从单独独立图片（`.png`, `.jpg`, `.jpeg` 等等 ) 能够获取并处理所检测和被翻译为 Markdown 的文字。
- **Excel数据提取**:
  - 处理和解析来自工作表里的多个数据。
  - 以原生，十分可靠且简单的方式，将所有的表格内容格式安全地转并转换为 Markdown 里的表格对象。

## 🛠️ 所需使用的科技及工具

- **PDF文件分析解析**: `PyMuPDF` (布局和绘图分析), `pdfplumber` (数据内容及高精准的转换表格数据)
- **OCR图形处理提取**: `pytesseract` (封装 Tesseract-OCR), `Pillow` (PIL图形图像库)
- **数据处理和分析**: `pandas`, `openpyxl`, `tabulate`

## ⚙️ 安装与要求

### 1. 软件操作系统运行依赖环境
如果你需要使用OCR图形识别相关的配置功能（处理包含扫面原文本内容的扫描版图书类型PDF或提取普通图片）, 必须预先于操作本地设备部署安装 **Tesseract OCR** 并设置系统变量 `PATH`.

- **Windows 操作系统平台**: 在[此页面下载及进行环境部署安装教程](https://github.com/UB-Mannheim/tesseract/wiki)。

### 2. Python项目依赖和资源
克隆或拉取仓库的代码后于终端指令集用 requirements.txt：

```bash
git clone https://github.com/seu-usuario/omniextract-markdown.git
cd omniextract-markdown
pip install -r requirements.txt
```

## 💻 快速入门与使用指引

项目识别及自动确认当前载入或所导入及所需读取文本材料的各类可处理后缀 ( 如： `.pdf`, `.png`, `.xlsx` 等).

### 第一种方法: CLI 命令控制窗口操作模式

```bash
# 全数字内容PDF格式材料 (原生纯纯文档)
python pipeline.py document.pdf

# 受限且封锁式文本不可达之材料扫描类型版PDF (支持开启OCR模块模式运作)
python pipeline.py document.pdf --ocr

# 试算数据表格 Excel (.xlsx) (默认会提取里头存放的所有的 Sheet的内容到最终Markdown中)
python pipeline.py document.xlsx

# 处理分析单点独立的图片资源类型材料并执行图片里内容的解密处理(全自启动OCR提取模型处理机制)
python pipeline.py document_photo.png
```

### 第二种方法: 使用代码嵌入 (Python导入用法)
更多其他范例，您尽可以请看： `example_usage.py`。

```python
from pipeline import PDFProcessor, ExcelProcessor, ImageProcessor

# 处理Excel内容数据处理表对象：
excel = ExcelProcessor(excel_path="data.xlsx")
excel.save("data.md")
```
