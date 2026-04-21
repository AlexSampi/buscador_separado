from pathlib import Path
import re


def cv_desde_nota(path: str | Path) -> Path:
    p = Path(path)
    nombre = p.name
    sufijo = ".notas.txt"

    if nombre.lower().endswith(sufijo):
        return p.with_name(nombre[:-len(sufijo)])

    return p


def resumen_desde_nota(path: str | Path) -> tuple[str, str]:
    p = Path(path)

    try:
        texto = p.read_text(encoding="utf-8").strip()
    except Exception:
        return ("", "")

    if not texto:
        return ("", "")

    lineas = [ln.rstrip() for ln in texto.splitlines()]

    patron_fecha = re.compile(r"^\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]$")

    indices_fecha = []
    for i, linea in enumerate(lineas):
        if patron_fecha.match(linea.strip()):
            indices_fecha.append(i)

    if not indices_fecha:
        no_vacias = [ln.strip() for ln in lineas if ln.strip()]
        preview = " ".join(no_vacias[-2:])[:180] if no_vacias else ""
        return ("", preview)

    ultimo_idx = indices_fecha[-1]
    m = patron_fecha.match(lineas[ultimo_idx].strip())
    ultima_fecha = m.group(1) if m else ""

    bloque = []
    for linea in lineas[ultimo_idx + 1:]:
        if patron_fecha.match(linea.strip()):
            break
        if linea.strip():
            bloque.append(linea.strip())

    preview = " ".join(bloque).strip()
    if len(preview) > 180:
        preview = preview[:177] + "..."

    return (ultima_fecha, preview)