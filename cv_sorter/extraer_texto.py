from __future__ import annotations

import os
import io
import re
from pathlib import Path
from typing import Optional

from cv_sorter.utils import ruta_recurso


# Recibe archivo y decide siguiente acción en base a su extensión
def extraer_texto(ruta_archivo: Path, config: Optional[dict] = None) -> str:
    extension = ruta_archivo.suffix.lower()

    if extension == ".txt":
        return _leer_txt(ruta_archivo)

    if extension == ".docx":
        return _extraer_docx(ruta_archivo)

    # PDF tiene dos partes
    # 1- Intenta extraer texto sin IA
    if extension == ".pdf":
        texto = _extraer_texto_pdf_embebido(ruta_archivo, config)
        if texto.strip():
            return texto

        # Si en el anterior paso sale vacío, indica que pdf fue escaneado y no tine texto real -> Recurre a OCR
        if config and (config.get("ocr", {}) or {}).get("enabled", False):
            return _ocr_pdf_con_pymupdf(ruta_archivo, config)

        return ""

    # Imagenes -> OCR
    if extension in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
        if config and (config.get("ocr", {}) or {}).get("enabled", False):
            return _ocr_imagen(ruta_archivo, config)
        return ""

    return ""

# Formato para leer el archivo
def _leer_txt(ruta_archivo: Path) -> str:
    try:
        return ruta_archivo.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return ruta_archivo.read_text(encoding="latin-1", errors="ignore")
        except Exception:
            return ""


def _extraer_docx(ruta_archivo: Path) -> str:
    """ Claude:
    Usa la librería python-docx para leer el Word. Un .docx internamente es un ZIP con XMLs, 
    y python-docx lo parsea y expone los párrafos como objetos. 
    Este código recorre todos los párrafos, descarta los vacíos y los une con saltos de línea. 
    Una limitación a tener en cuenta es que no extrae texto de tablas, solo de párrafos normales. 
    """
    try:
        from docx import Document

        documento = Document(str(ruta_archivo))
        partes = []

        for parrafo in documento.paragraphs:
            if parrafo.text:
                partes.append(parrafo.text)

        return "\n".join(partes)
    except Exception:
        return ""


def _parece_pdf(ruta_archivo: Path) -> bool:
    # Hay PDFs que en realidad son "pdfs" rotos o cosas raras. Esto me ahorra errores tontos.
    try:
        with ruta_archivo.open("rb") as f:
            return f.read(5) == b"%PDF-"
    except Exception:
        return False


def _extraer_texto_pdf_embebido(ruta_archivo: Path, config: Optional[dict]) -> str:
    if not _parece_pdf(ruta_archivo):
        return ""

    max_paginas = 999
    if config:
        max_paginas = int((config.get("ocr", {}) or {}).get("max_pdf_pages", 6))

    # 1) PyMuPDF: suele ser el más robusto y no mete warnings raros por stderr
    try:
        import fitz

        doc = fitz.open(str(ruta_archivo))
        partes = []

        for i in range(min(doc.page_count, max_paginas)):
            pagina = doc.load_page(i)
            texto = pagina.get_text("text") or ""
            if texto.strip():
                partes.append(texto)

        doc.close()
        return "\n".join(partes)
    except Exception:
        pass

    # 2) Fallback pypdf: útil si PyMuPDF falla por cualquier motivo
    try:
        import contextlib
        import io as _io
        from pypdf import PdfReader

        partes = []
        with contextlib.redirect_stderr(_io.StringIO()):
            lector = PdfReader(str(ruta_archivo), strict=False)
            for i, pagina in enumerate(lector.pages):
                if i >= max_paginas:
                    break
                texto = pagina.extract_text() or ""
                if texto.strip():
                    partes.append(texto)

        return "\n".join(partes)
    except Exception:
        return ""


def _resolver_tesseract_y_tessdata(config: dict) -> tuple[Optional[str], Optional[str]]:
    # Prioridad:
    # 1) tesseract embebido dentro del exe (ocr_bin)
    # 2) si no existe, lo que venga en config (por si alguien lo tiene instalado fuera)
    ocr_config = config.get("ocr", {}) or {}

    tesseract_embebido = ruta_recurso("ocr_bin/tesseract.exe")
    tessdata_embebido = ruta_recurso("ocr_bin/tessdata")

    comando_tesseract = None
    carpeta_tessdata = None

    if tesseract_embebido.exists():
        comando_tesseract = str(tesseract_embebido)

        # Importante: tesseract necesita sus DLLs, así que meto su carpeta en PATH
        os.environ["PATH"] = str(tesseract_embebido.parent) + os.pathsep + os.environ.get("PATH", "")

        # Y si está tessdata, lo apunto con TESSDATA_PREFIX
        if tessdata_embebido.exists():
            carpeta_tessdata = str(tessdata_embebido)
            os.environ["TESSDATA_PREFIX"] = carpeta_tessdata

    if not comando_tesseract:
        comando_config = (ocr_config.get("tesseract_cmd", "") or "").strip()
        if comando_config:
            comando_tesseract = comando_config

    if not carpeta_tessdata and tessdata_embebido.exists():
        carpeta_tessdata = str(tessdata_embebido)
        os.environ["TESSDATA_PREFIX"] = carpeta_tessdata

    return comando_tesseract, carpeta_tessdata


def _ocr_imagen(ruta_imagen: Path, config: dict) -> str:
    try:
        import pytesseract
        from PIL import Image

        comando_tesseract, carpeta_tessdata = _resolver_tesseract_y_tessdata(config)
        if comando_tesseract:
            pytesseract.pytesseract.tesseract_cmd = comando_tesseract

        idiomas = ((config.get("ocr", {}) or {}).get("languages", "spa+eng") or "spa+eng").strip()

        # Para evitar que tesseract no encuentre los traineddata cuando va embebido
        parametros_extra = ""
        if carpeta_tessdata:
            parametros_extra = f'--tessdata-dir "{carpeta_tessdata}"'

        imagen = Image.open(str(ruta_imagen))
        return pytesseract.image_to_string(imagen, lang=idiomas, config=parametros_extra) or ""
    except Exception:
        return ""


def _ocr_pdf_con_pymupdf(ruta_pdf: Path, config: dict) -> str:
    if not _parece_pdf(ruta_pdf):
        return ""

    try:
        import fitz
        import pytesseract
        from PIL import Image

        ocr_config = config.get("ocr", {}) or {}

        comando_tesseract, carpeta_tessdata = _resolver_tesseract_y_tessdata(config)
        if comando_tesseract:
            pytesseract.pytesseract.tesseract_cmd = comando_tesseract

        idiomas = (ocr_config.get("languages", "spa+eng") or "spa+eng").strip()
        dpi = int(ocr_config.get("pdf_dpi", 250))
        max_paginas = int(ocr_config.get("max_pdf_pages", 6))

        parametros_extra = ""
        if carpeta_tessdata:
            parametros_extra = f'--tessdata-dir "{carpeta_tessdata}"'

        doc = fitz.open(str(ruta_pdf))
        partes = []

        for i in range(min(doc.page_count, max_paginas)):
            pagina = doc.load_page(i)

            # Renderizo página a imagen, y de ahí OCR.
            # Esto evita dependencias externas tipo Poppler.
            pix = pagina.get_pixmap(dpi=dpi)
            imagen = Image.open(io.BytesIO(pix.tobytes("png")))

            partes.append(pytesseract.image_to_string(imagen, lang=idiomas, config=parametros_extra) or "")

        doc.close()

        texto = "\n".join(partes)
        texto = re.sub(r"[ \t]+\n", "\n", texto)
        return texto
    except Exception:
        return ""
