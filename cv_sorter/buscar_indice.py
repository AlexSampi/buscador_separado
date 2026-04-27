from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List

from cv_sorter.extraer_texto import extraer_texto
from cv_sorter.utils import asegurar_carpeta, normalizar_texto


def _connect(db_path: Path) -> sqlite3.Connection:
    asegurar_carpeta(db_path.parent)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA synchronous=NORMAL;")
    return con


def _path_key(path: Path) -> str:
    try:
        return str(path.resolve())
    except Exception:
        return str(path)


def recrear_indice(db_path: Path, files: Iterable[Path], cfg: dict) -> None:
    con = _connect(db_path)
    cur = con.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
          path TEXT PRIMARY KEY,
          mtime REAL NOT NULL,
          text_norm TEXT NOT NULL
        )
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_docs_mtime ON docs(mtime)")
    con.commit()

    files_list = [Path(f) for f in files]
    files_map = {_path_key(f): f for f in files_list}
    rutas_actuales = set(files_map.keys())

    filas_existentes = {
        path: float(mtime)
        for path, mtime in cur.execute("SELECT path, mtime FROM docs").fetchall()
    }

    rutas_eliminar = [path for path in filas_existentes if path not in rutas_actuales]
    if rutas_eliminar:
        cur.executemany("DELETE FROM docs WHERE path=?", [(path,) for path in rutas_eliminar])

    for path_key, archivo in files_map.items():
        try:
            mtime = archivo.stat().st_mtime
        except Exception:
            continue

        mtime_existente = filas_existentes.get(path_key)
        if mtime_existente is not None and float(mtime_existente) == float(mtime):
            continue

        try:
            txt = extraer_texto(archivo, config=cfg) or ""
            txt_norm = normalizar_texto(txt)
            cur.execute(
                "INSERT OR REPLACE INTO docs(path, mtime, text_norm) VALUES(?,?,?)",
                (path_key, mtime, txt_norm),
            )
        except Exception:
            continue

    con.commit()
    con.close()


def buscar_terminos(
    db_path: Path,
    terms: List[str],
    mode: str = "AND",
    max_results: int = 200,
) -> List[Dict[str, Any]]:
    con = _connect(db_path)
    cur = con.cursor()

    cleaned: List[str] = []
    norm_terms: List[str] = []

    for t in terms:
        t0 = (t or "").strip()
        if not t0:
            continue
        nt = normalizar_texto(t0).strip()
        if not nt:
            continue
        cleaned.append(t0)
        norm_terms.append(nt)

    if not norm_terms:
        con.close()
        return []

    mode_up = (mode or "AND").upper().strip()
    joiner = " AND " if mode_up == "AND" else " OR "

    where = joiner.join(["text_norm LIKE ?"] * len(norm_terms))
    params = [f"% {t} %" for t in norm_terms]

    rows = cur.execute(
        f"SELECT path, text_norm FROM docs WHERE {where} LIMIT ?",
        (*params, int(max_results)),
    ).fetchall()

    con.close()

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
