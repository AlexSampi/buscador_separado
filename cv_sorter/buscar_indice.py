from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, List, Dict, Any

from cv_sorter.extraer_texto import extraer_texto
from cv_sorter.utils import normalizar_texto, asegurar_carpeta

# Abre (crea si no existe) la base de datos SQLite
def _connect(db_path: Path) -> sqlite3.Connection:
    asegurar_carpeta(db_path.parent)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con

# Construye o actualiza el indice con todos los CVs
# Actualiza los cambios en la DB
def recrear_indice(db_path: Path, files: Iterable[Path], cfg: dict) -> None:
    """
    REGLAS:
    - DEDUPE POR NOMBRE EXACTO (case-insensitive) DURANTE INDEXADO
    - Esto reduce brutalmente el índice si tienes CV copiados en 10 carpetas.
    """
    con = _connect(db_path)
    cur = con.cursor()

    # Crea la tabla si no existe todavía. Tres columnas
    # 1 - Ruta del archivo {PK}
    # 2 - Fecha de modificación
    # 3 - Texto normalizado del CV
    cur.execute("""
    CREATE TABLE IF NOT EXISTS docs (
      path TEXT PRIMARY KEY,
      mtime REAL NOT NULL,
      text_norm TEXT NOT NULL
    )
    """)
    con.commit()

    # Deduplicación: Tecnica de almacenamiento que elimina copias redundantes de información, guardado una instancia unica
    seen_names = set()  # dedupe por nombre durante indexado
    files_list = list(files)

    for f in files_list:
        try:
            # Si el mismo nombre aparece en varias carpetas, solo se indeza la primera vez que se encuentra, así el indice no crece innecesariamente
            name_key = f.name.casefold()
            if name_key in seen_names:
                continue
            seen_names.add(name_key)

            # OPTIMIZACIÓN: Antes de procesar un archivo, comprueba si ya está en el indice y si su fecha de modificación NO ha cambiado
            # Si ambas son verdad, el archivo no ha cambiado desde su ultima indexación, por lo que se salta.
            # Evita hacer OCR innecesariamente en ejecuciones posteriores
            mtime = f.stat().st_mtime
            row = cur.execute("SELECT mtime FROM docs WHERE path=?", (str(f),)).fetchone()
            if row and float(row[0]) == float(mtime):
                continue
            

            txt = extraer_texto(f, config=cfg) or "" # Extrae texto
            txt_norm = normalizar_texto(txt) # Normaliza texto

            # Si ya existe -> Reemplaza
            # Si no existe -> Inserta
            cur.execute(
                "INSERT OR REPLACE INTO docs(path, mtime, text_norm) VALUES(?,?,?)",
                (str(f), mtime, txt_norm)
            )
        except Exception:
            continue

    con.commit()
    con.close()

# Busca en el indice los CVs con los términos dados
def buscar_terminos(
    db_path: Path,
    terms: List[str],
    mode: str = "AND",
    max_results: int = 200,
) -> List[Dict[str, Any]]:
    """
    mode:
      - "AND": debe contener TODAS las palabras (como palabra completa)
      - "OR" : debe contener ALGUNA palabra (y devuelve cuáles matchean)
      - "NOT": POR IMPLEMENTAR. No contenca la(s) palabra(s)
    Devuelve: [{"path": str, "matched": [str, ...]}, ...]
    """
    con = _connect(db_path)
    cur = con.cursor()

    cleaned: List[str] = []
    norm_terms: List[str] = []
    # Prepara dos listas
    for t in terms:
        t0 = (t or "").strip()
        if not t0:
            continue
        nt = normalizar_texto(t0).strip()  # ojo: normalize añade espacios, strip aquí para construir patrón
        if not nt:
            continue
        cleaned.append(t0) # Lista con terminos originales para mostrar en la UI
        norm_terms.append(nt) # Lista con terminos normalizados para buscar

    if not norm_terms:
        con.close()
        return []

    # Genera la consulta de forma interna en forma de QUERY
    mode_up = (mode or "AND").upper().strip()
    joiner = " AND " if mode_up == "AND" else " OR "

    # buscamos palabra completa: "% react %", NO derivados tipo react-ivar, hipe-react-ivo
    where = joiner.join(["text_norm LIKE ?"] * len(norm_terms))
    params = [f"% {t} %" for t in norm_terms]

    rows = cur.execute(
        f"SELECT path, text_norm FROM docs WHERE {where} LIMIT ?",
        (*params, int(max_results))
    ).fetchall()

    con.close()

    # Diccionario de salida
    out: List[Dict[str, Any]] = []
    for path, text_norm in rows:
        matched: List[str] = []
        if mode_up == "OR":
            tn = text_norm or " "
            for orig, nt in zip(cleaned, norm_terms):
                if f" {nt} " in tn:
                    matched.append(orig)
        out.append({"path": path, "matched": matched})

    return out
