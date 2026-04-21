from pathlib import Path
from PySide6 import QtCore, QtGui
import yaml


CATEGORIAS = [
    "IT_Programacion",
    "Ingenieria",
    "Diseno",
    "Marketing",
    "Administracion",
    "Otros",
]


def normalizar_categoria(categoria: str) -> str:
    cat = (categoria or "").strip()
    return cat if cat in CATEGORIAS else "Otros"


def categorias():
    return list(CATEGORIAS)


def color_categoria(categoria: str) -> QtGui.QColor:
    cat = normalizar_categoria(categoria)

    mapa = {
        "IT_Programacion": QtGui.QColor("#4FC3F7"),
        "Ingenieria": QtGui.QColor("#81C784"),
        "Diseno": QtGui.QColor("#BA68C8"),
        "Marketing": QtGui.QColor("#FFB74D"),
        "Administracion": QtGui.QColor("#90A4AE"),
        "Otros": QtGui.QColor("#E0E0E0"),
    }

    return mapa.get(cat, QtGui.QColor("#E0E0E0"))


def ruta_clasificacion_cv(ruta_cv: str | Path) -> Path:
    p = Path(ruta_cv)
    return p.with_name(p.name + ".clasificacion.yml")


def guardar_clasificacion_cv(ruta_cv: str | Path, categoria: str, origen: str = "auto") -> bool:
    ruta_meta = ruta_clasificacion_cv(ruta_cv)

    data = {
        "categoria": normalizar_categoria(categoria),
        "fecha": QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm"),
        "origen": (origen or "auto").strip() or "auto",
    }

    try:
        ruta_meta.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
            encoding="utf-8"
        )
        return True
    except Exception:
        return False


def leer_clasificacion_cv(ruta_cv: str | Path) -> dict:
    ruta_meta = ruta_clasificacion_cv(ruta_cv)

    if not ruta_meta.exists():
        return {}

    try:
        data = yaml.safe_load(ruta_meta.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return {}


def calcular_score_cv(ruta_cv: str | Path) -> int:
    ruta_cv = Path(ruta_cv)

    texto = ""

    try:
        import fitz
        doc = fitz.open(str(ruta_cv))
        for page in doc[:3]:
            texto += page.get_text()
        doc.close()
    except Exception:
        try:
            texto = ruta_cv.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return 0

    texto = texto.lower()

    score = 0

    reglas = {
        "python": 15,
        "java": 12,
        "sql": 10,
        "docker": 8,
        "aws": 8,
        "react": 7,
        "javascript": 7,
        "git": 6,
        "linux": 6,
        "api": 6,
        "spring": 8,
        "django": 8,
    }

    for palabra, puntos in reglas.items():
        if palabra in texto:
            score += puntos

    return min(score, 100)