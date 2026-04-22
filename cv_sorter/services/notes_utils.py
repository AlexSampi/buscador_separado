from pathlib import Path
import re
import yaml


INICIO_BLOQUE_CLIENTES = "\n--- NOTAS_CLIENTE_AUTOGENERADAS_INICIO ---\n"
FIN_BLOQUE_CLIENTES = "\n--- NOTAS_CLIENTE_AUTOGENERADAS_FIN ---\n"


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


def ruta_notas_desde_cv(path: str | Path) -> Path:
    p = Path(path)
    return p.with_suffix(p.suffix + ".notas.txt")


def ruta_clientes_desde_cv(path: str | Path) -> Path:
    p = Path(path)
    return p.with_suffix(p.suffix + ".clientes.txt")


def cargar_clientes_desde_cv(path: str | Path) -> list[dict]:
    ruta = ruta_clientes_desde_cv(path)

    if not ruta.exists():
        return []

    try:
        contenido = ruta.read_text(encoding="utf-8").strip()
    except Exception:
        return []

    if not contenido:
        return []

    try:
        cargado = yaml.safe_load(contenido)
    except Exception:
        return []

    clientes = []

    if isinstance(cargado, list):
        for item in cargado:
            if isinstance(item, dict):
                empresa = str(item.get("empresa", "")).strip()
                nota = str(item.get("nota", "")).strip()
                nota_fecha = str(item.get("nota_fecha", "")).strip()
                estado = str(item.get("estado", "Pendiente")).strip() or "Pendiente"

                if empresa:
                    clientes.append({
                        "empresa": empresa,
                        "nota": nota,
                        "nota_fecha": nota_fecha,
                        "estado": estado,
                    })

    return clientes


def construir_bloque_notas_clientes(path_cv: str | Path) -> str:
    clientes = cargar_clientes_desde_cv(path_cv)

    if not clientes:
        return ""

    lineas = ["NOTAS DE CLIENTE", ""]

    for cliente in clientes:
        empresa = cliente.get("empresa", "").strip() or "Sin empresa"
        estado = cliente.get("estado", "").strip() or "Pendiente"
        nota = cliente.get("nota", "").strip()
        nota_fecha = cliente.get("nota_fecha", "").strip()

        lineas.append(f"- Cliente: {empresa}")
        lineas.append(f"  Estado: {estado}")

        if nota_fecha:
            lineas.append(f"  Fecha: {nota_fecha}")

        if nota:
            lineas.append(nota)
        else:
            lineas.append("  Nota: —")

        lineas.append("")

    return "\n".join(lineas).rstrip() + "\n"


def actualizar_notas_unificadas(path_cv: str | Path) -> Path:
    ruta_cv = Path(path_cv)
    ruta_notas = ruta_notas_desde_cv(ruta_cv)

    if ruta_notas.exists():
        try:
            texto_actual = ruta_notas.read_text(encoding="utf-8")
        except Exception:
            texto_actual = f"Notas para: {ruta_cv.name}\n\n"
    else:
        texto_actual = f"Notas para: {ruta_cv.name}\n\n"

    patron = re.compile(
        re.escape(INICIO_BLOQUE_CLIENTES) + r".*?" + re.escape(FIN_BLOQUE_CLIENTES),
        re.DOTALL,
    )
    texto_base = patron.sub("", texto_actual).rstrip() + "\n"

    bloque_clientes = construir_bloque_notas_clientes(ruta_cv)

    if bloque_clientes:
        texto_final = (
            texto_base.rstrip()
            + "\n"
            + INICIO_BLOQUE_CLIENTES
            + "\n"
            + bloque_clientes
            + FIN_BLOQUE_CLIENTES
            + "\n"
        )
    else:
        texto_final = texto_base.rstrip() + "\n"

    ruta_notas.write_text(texto_final, encoding="utf-8")
    return ruta_notas