from __future__ import annotations

import io
import os
import re
from pathlib import Path
from typing import Optional

from cv_sorter.utils import ruta_recurso


def extraer_texto(ruta_archivo: Path, config: Optional[dict] = None) -> str:
    extension = ruta_archivo.suffix.lower()
    texto = ""

    if extension == ".txt":
        texto = _leer_txt(ruta_archivo)

    elif extension == ".docx":
        texto = _extraer_docx(ruta_archivo)

    elif extension == ".pdf":
        texto = _extraer_texto_pdf_embebido(ruta_archivo, config)
        if not texto.strip() and config and (config.get("ocr", {}) or {}).get("enabled", False):
            texto = _ocr_pdf_con_pymupdf(ruta_archivo, config)

    elif extension in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"):
        if config and (config.get("ocr", {}) or {}).get("enabled", False):
            texto = _ocr_imagen(ruta_archivo, config)

    # Si no pudimos leer contenido real, al menos indexamos el nombre.
    return texto.strip() or ruta_archivo.name


def _leer_txt(ruta_archivo: Path) -> str:
    try:
        return ruta_archivo.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return ruta_archivo.read_text(encoding="latin-1", errors="ignore")
        except Exception:
            return ""


def _extraer_docx(ruta_archivo: Path) -> str:
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

    try:
        import contextlib
        import io as io_stderr
        from pypdf import PdfReader

        partes = []
        with contextlib.redirect_stderr(io_stderr.StringIO()):
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
    ocr_config = config.get("ocr", {}) or {}

    tesseract_embebido = ruta_recurso("ocr_bin/tesseract.exe")
    tessdata_embebido = ruta_recurso("ocr_bin/tessdata")

    comando_tesseract = None
    carpeta_tessdata = None

    if tesseract_embebido.exists():
        comando_tesseract = str(tesseract_embebido)
        os.environ["PATH"] = str(tesseract_embebido.parent) + os.pathsep + os.environ.get("PATH", "")

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
            pix = pagina.get_pixmap(dpi=dpi)
            imagen = Image.open(io.BytesIO(pix.tobytes("png")))
            partes.append(pytesseract.image_to_string(imagen, lang=idiomas, config=parametros_extra) or "")

        doc.close()

        texto = "\n".join(partes)
        return re.sub(r"[ \t]+\n", "\n", texto)
    except Exception:
        return ""
