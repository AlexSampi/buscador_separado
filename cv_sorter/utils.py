from __future__ import annotations

import os
import re
import json
import shutil
import sys
import hashlib
import unicodedata
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple


def carpeta_datos_usuario(nombre_app: str = "Buscador de CVs") -> Path:
    # Carpeta escribible para logs, índice, etc.
    # En Windows: %LOCALAPPDATA%\Buscador de CVs
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA")
        if base:
            return Path(base) / nombre_app

    # Fallback multiplataforma
    return Path.home() / f".{nombre_app}"


def raiz_proyecto() -> Path:
    # En modo .exe, no debo usar Program Files para escritura.
    # Devuelvo una carpeta de datos del usuario.
    if getattr(sys, "frozen", False):
        return carpeta_datos_usuario()

    # En modo dev, mantengo el comportamiento anterior.
    sentinelas = ["01_Universidad", "02_FP", "03_Otras certificaciones"]
    inicio = Path(os.getcwd()).resolve()

    p = inicio
    for _ in range(7):
        if all((p / s).exists() for s in sentinelas):
            return p
        if p.parent == p:
            break
        p = p.parent

    return inicio


def asegurar_carpeta(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def sello_fecha() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def nombre_archivo_seguro(nombre: str) -> str:
    nombre = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", nombre)
    return nombre.strip()


def escribir_json(ruta: Path, data: dict) -> None:
    asegurar_carpeta(ruta.parent)
    ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalizar_texto(s: str) -> str:
    if not s:
        return " "

    s = s.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))

    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()

    return f" {s} "


def ruta_recurso(ruta_relativa: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return (base / ruta_relativa).resolve()


def ruta_logo_app() -> Path:
    candidatos = (
        "assets/logo.png",
        "assets/logo.jpg",
        "logo.png",
        "logo.jpg",
    )

    for candidato in candidatos:
        ruta = ruta_recurso(candidato)
        if ruta.exists():
            return ruta

    return ruta_recurso("logo.jpg")


def ocultar_carpeta_windows(p: Path) -> None:
    try:
        if os.name != "nt":
            return
        if not p.exists():
            return
        subprocess.run(["attrib", "+h", str(p)], capture_output=True, text=True, check=False)
    except Exception:
        pass


def sha256_archivo(p: Path, tam_bloque: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(tam_bloque)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def buscar_identico_en_carpeta(origen: Path, carpeta_destino: Path) -> Optional[Path]:
    if not carpeta_destino.exists():
        return None

    tam_origen = origen.stat().st_size
    hash_origen: Optional[str] = None

    for candidato in carpeta_destino.glob(f"*{origen.suffix}"):
        try:
            if not candidato.is_file():
                continue
            if candidato.stat().st_size != tam_origen:
                continue
            if hash_origen is None:
                hash_origen = sha256_archivo(origen)
            if sha256_archivo(candidato) == hash_origen:
                return candidato
        except Exception:
            continue

    return None


def copiar_con_colision(origen: Path, carpeta_destino: Path) -> Path:
    asegurar_carpeta(carpeta_destino)

    destino = carpeta_destino / nombre_archivo_seguro(origen.name)
    if not destino.exists():
        shutil.copy2(origen, destino)
        return destino

    base = destino.stem
    ext = destino.suffix
    i = 1
    while True:
        candidato = carpeta_destino / f"{base} ({i}){ext}"
        if not candidato.exists():
            shutil.copy2(origen, candidato)
            return candidato
        i += 1


def mover_con_colision(origen: Path, carpeta_destino: Path) -> Path:
    asegurar_carpeta(carpeta_destino)

    destino = carpeta_destino / nombre_archivo_seguro(origen.name)
    if not destino.exists():
        shutil.move(str(origen), str(destino))
        return destino

    base = destino.stem
    ext = destino.suffix
    i = 1
    while True:
        candidato = carpeta_destino / f"{base} ({i}){ext}"
        if not candidato.exists():
            shutil.move(str(origen), str(candidato))
            return candidato
        i += 1


def copiar_unico(origen: Path, carpeta_destino: Path) -> Tuple[Path, bool]:
    asegurar_carpeta(carpeta_destino)

    identico = buscar_identico_en_carpeta(origen, carpeta_destino)
    if identico is not None:
        return identico, True

    destino = carpeta_destino / nombre_archivo_seguro(origen.name)
    if not destino.exists():
        shutil.copy2(origen, destino)
        return destino, False

    nuevo = copiar_con_colision(origen, carpeta_destino)
    return nuevo, False


def borrar_identicos_en_carpeta(origen: Path, carpeta_destino: Path) -> int:
    if not carpeta_destino.exists():
        return 0

    tam_origen = origen.stat().st_size
    hash_origen = sha256_archivo(origen)
    borrados = 0

    for candidato in carpeta_destino.glob(f"*{origen.suffix}"):
        try:
            if not candidato.is_file():
                continue
            if candidato.stat().st_size != tam_origen:
                continue
            if sha256_archivo(candidato) == hash_origen:
                candidato.unlink(missing_ok=True)
                borrados += 1
        except Exception:
            continue

    return borrados
