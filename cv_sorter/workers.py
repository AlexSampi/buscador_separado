from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets


class _ClassifyWorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(list, object)   # resultados, base(Path)
    error = QtCore.Signal(str)
    progress = QtCore.Signal(str)


class _ApplyClassificationWorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(dict)
    error = QtCore.Signal(str)
    progress = QtCore.Signal(str)


class _UndoClassificationWorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(dict)
    error = QtCore.Signal(str)
    progress = QtCore.Signal(str)

class _SearchWorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(list, object)  # encontrados, base(Path)
    error = QtCore.Signal(str)


class _ClassifyWorker(QtCore.QRunnable):
    def __init__(self, base: Path, max_resultados: int = 300):
        super().__init__()
        self.base = Path(base)
        self.max_resultados = max_resultados
        self.signals = _ClassifyWorkerSignals()

    def _es_cv_clasificable(self, p: Path) -> bool:
        if not p.is_file():
            return False

        nombre = p.name.lower()
        if nombre.endswith(".notas.txt"):
            return False
        if nombre.endswith(".clientes.txt"):
            return False

        return p.suffix.lower() in {".pdf", ".doc", ".docx", ".odt", ".rtf"}

    def _clasificar_cv_simple(self, texto: str) -> str:
        t = (texto or "").lower()

        if any(x in t for x in ["python", "java", "c++", "javascript", "react", "sql", "programador", "desarrollador", "software", "backend", "frontend", "full stack"]):
            return "IT_Programacion"

        if any(x in t for x in ["ingeniero", "ingeniería", "industrial", "mecánico", "mecanico", "eléctrico", "electrico", "civil", "telecom", "automatizacion", "automoción", "automocion"]):
            return "Ingenieria"

        if any(x in t for x in ["diseño", "diseno", "photoshop", "illustrator", "ux", "ui", "figma", "diseñador", "disenador", "grafico", "gráfico"]):
            return "Diseno"

        if any(x in t for x in ["marketing", "seo", "sem", "redes sociales", "publicidad", "community manager", "comunicación", "comunicacion"]):
            return "Marketing"

        if any(x in t for x in ["administrativo", "administración", "administracion", "excel", "contabilidad", "facturación", "facturacion", "office", "rrhh", "recursos humanos"]):
            return "Administracion"

        return "Otros"

    def _extraer_texto_seguro(self, p: Path) -> str:
        suf = p.suffix.lower()

        if suf == ".pdf":
            try:
                import fitz
                doc = fitz.open(str(p))
                partes = []
                for i, page in enumerate(doc):
                    if i >= 2:
                        break
                    partes.append(page.get_text())
                texto = "\n".join(partes).strip()
                return texto or p.name
            except Exception:
                return p.name

        return p.name

    def run(self):
        try:
            archivos = []
            for p in self.base.rglob("*"):
                try:
                    if self._es_cv_clasificable(p):
                        archivos.append(p)
                except Exception:
                    continue

            archivos = sorted(archivos, key=lambda x: x.name.lower())

            if not archivos:
                self.signals.finished.emit([], self.base)
                return

            resultados = []
            total = len(archivos)
            limite = min(total, self.max_resultados)

            for i, p in enumerate(archivos[:limite], start=1):
                try:
                    if i == 1 or i % 25 == 0:
                        self.signals.progress.emit(f"Analizando {i}/{limite}...")

                    texto = self._extraer_texto_seguro(p)
                    categoria = self._clasificar_cv_simple(texto)

                    resultados.append({
                        "path": str(p),
                        "nombre": p.name,
                        "categoria": categoria,
                    })

                except Exception:
                    continue

            self.signals.finished.emit(resultados, self.base)

        except Exception as e:
            self.signals.error.emit(str(e))

class _ApplyClassificationWorker(QtCore.QRunnable):
    def __init__(self, resultados: list[dict], destino_base: Path):
        super().__init__()
        self.resultados = list(resultados or [])
        self.destino_base = Path(destino_base)
        self.signals = _ApplyClassificationWorkerSignals()

    def _nombre_seguro(self, categoria: str) -> str:
        cat = (categoria or "Otros").strip()
        validas = {
            "IT_Programacion",
            "Ingenieria",
            "Diseno",
            "Marketing",
            "Administracion",
            "Otros",
        }
        return cat if cat in validas else "Otros"

    def _ruta_destino_unica(self, carpeta: Path, nombre_archivo: str) -> Path:
        destino = carpeta / nombre_archivo
        if not destino.exists():
            return destino

        stem = destino.stem
        suffix = destino.suffix
        n = 2
        while True:
            candidato = carpeta / f"{stem}_{n}{suffix}"
            if not candidato.exists():
                return candidato
            n += 1

    def run(self):
        try:
            total = len(self.resultados)
            if total <= 0:
                self.signals.finished.emit({
                    "movidos": 0,
                    "errores": 0,
                    "destino_base": str(self.destino_base),
                })
                return

            self.destino_base.mkdir(parents=True, exist_ok=True)

            movidos = 0
            errores = 0
            historial = []

            import shutil

            for i, item in enumerate(self.resultados, start=1):
                try:
                    if i == 1 or i % 10 == 0:
                        self.signals.progress.emit(f"Aplicando clasificación {i}/{total}...")

                    ruta_origen = Path(item.get("path", ""))
                    nombre = item.get("nombre", ruta_origen.name if ruta_origen else "")
                    categoria = self._nombre_seguro(item.get("categoria", "Otros"))

                    if not ruta_origen.exists() or not ruta_origen.is_file():
                        errores += 1
                        continue

                    carpeta_cat = self.destino_base / categoria
                    carpeta_cat.mkdir(parents=True, exist_ok=True)

                    ruta_destino = self._ruta_destino_unica(carpeta_cat, nombre)

                    shutil.move(str(ruta_origen), str(ruta_destino))

                    historial.append({
                        "nombre": nombre,
                        "categoria": categoria,
                        "origen": str(ruta_origen),
                        "destino": str(ruta_destino),
                    })

                    movidos += 1

                except Exception:
                    errores += 1
                    continue

            self.signals.finished.emit({
                "movidos": movidos,
                "errores": errores,
                "destino_base": str(self.destino_base),
                "historial": historial,
            })

        except Exception as e:
            self.signals.error.emit(str(e))


class _UndoClassificationWorker(QtCore.QRunnable):
    def __init__(self, movimientos: list[dict], carpeta_raiz: Path | None = None):
        super().__init__()
        self.movimientos = list(movimientos or [])
        self.carpeta_raiz = Path(carpeta_raiz) if carpeta_raiz else None
        self.signals = _UndoClassificationWorkerSignals()

    def _ruta_destino_unica(self, carpeta: Path, nombre_archivo: str) -> Path:
        destino = carpeta / nombre_archivo
        if not destino.exists():
            return destino

        stem = destino.stem
        suffix = destino.suffix
        n = 2
        while True:
            candidato = carpeta / f"{stem}_{n}{suffix}"
            if not candidato.exists():
                return candidato
            n += 1

    def _borrar_arbol_vacio(self, raiz: Path | None) -> list[str]:
        borradas = []

        if raiz is None:
            return borradas

        try:
            raiz = Path(raiz)
        except Exception:
            return borradas

        if not raiz.exists() or not raiz.is_dir():
            return borradas

        todos = [raiz]
        try:
            todos.extend([p for p in raiz.rglob("*") if p.is_dir()])
        except Exception:
            return borradas

        todos.sort(key=lambda p: len(p.parts), reverse=True)

        for carpeta in todos:
            try:
                if carpeta.exists() and carpeta.is_dir() and not any(carpeta.iterdir()):
                    carpeta.rmdir()
                    borradas.append(str(carpeta))
                    print("[UNDO] carpeta vacía eliminada:", carpeta)
            except Exception as e:
                print("[UNDO] no se pudo borrar carpeta:", carpeta, "->", e)

        return borradas

    def run(self):
        try:
            total = len(self.movimientos)
            if total <= 0:
                self.signals.finished.emit({
                    "restaurados": 0,
                    "errores": 0,
                })
                return

            restaurados = 0
            errores = 0

            import shutil

            for i, mov in enumerate(self.movimientos, start=1):
                try:
                    if i == 1 or i % 10 == 0:
                        self.signals.progress.emit(f"Deshaciendo clasificación {i}/{total}...")

                    origen_actual = Path(mov.get("destino", ""))
                    destino_original = Path(mov.get("origen", ""))

                    if not origen_actual.exists() or not origen_actual.is_file():
                        errores += 1
                        continue

                    meta_clasificacion = origen_actual.with_name(origen_actual.name + ".clasificacion.yml")
                    if meta_clasificacion.exists():
                        try:
                            meta_clasificacion.unlink()
                        except Exception:
                            pass

                    destino_original.parent.mkdir(parents=True, exist_ok=True)

                    ruta_final = self._ruta_destino_unica(
                        destino_original.parent,
                        destino_original.name
                    )

                    shutil.move(str(origen_actual), str(ruta_final))
                    restaurados += 1

                except Exception as e:
                    print("[UNDO][ERROR]", mov, "->", e)
                    errores += 1
                    continue

            print("[UNDO] carpeta_raiz recibida:", self.carpeta_raiz)

            carpetas_borradas = self._borrar_arbol_vacio(self.carpeta_raiz)

            print("[UNDO] carpetas borradas:", carpetas_borradas)

            self.signals.finished.emit({
                "restaurados": restaurados,
                "errores": errores,
                "carpetas_borradas": carpetas_borradas,
                "carpeta_raiz": str(self.carpeta_raiz) if self.carpeta_raiz else "",
            })

        except Exception as e:
            self.signals.error.emit(str(e))

class _SearchWorker(QtCore.QRunnable):
    def __init__(self, base: Path, palabras: list[str], modo: str, search_scope: str = "cvs", max_resultados: int = 300):
        super().__init__()
        self.base = Path(base)
        self.palabras = [w.strip().lower() for w in palabras if w and w.strip()]
        self.modo = (modo or "AND").upper()
        self.search_scope = (search_scope or "cvs").lower()
        self.max_resultados = max_resultados
        self.signals = _SearchWorkerSignals()

    def _cargar_config(self) -> dict:
        from cv_sorter.utils import ruta_recurso
        import yaml

        ruta_cfg = ruta_recurso("cv_sorter/config.yaml")
        return yaml.safe_load(ruta_cfg.read_text(encoding="utf-8")) or {}

    def _listar_archivos_indizables(self, cfg: dict) -> list[Path]:
        extensiones_cvs = {
            ".pdf", ".doc", ".docx", ".odt", ".rtf"
        }

        cfg_exts = {e.lower() for e in (cfg.get("files", {}) or {}).get("include_ext", [])}
        if cfg_exts:
            extensiones_cvs = {e for e in cfg_exts if e != ".txt"}

        archivos: list[Path] = []

        for p in self.base.rglob("*"):
            try:
                if not p.is_file():
                    continue

                nombre = p.name.lower()

                if self.search_scope == "notes":
                    if nombre.endswith(".notas.txt"):
                        archivos.append(p)
                    continue

                if nombre.endswith(".notas.txt"):
                    continue

                if p.suffix.lower() not in extensiones_cvs:
                    continue

                archivos.append(p)

            except Exception:
                continue

        return archivos

    def run(self):
        try:
            from cv_sorter.buscar_indice import recrear_indice, buscar_terminos
            from cv_sorter.utils import carpeta_datos_usuario

            cfg = self._cargar_config()
            archivos = self._listar_archivos_indizables(cfg)

            print(f"[WORKER] scope={self.search_scope} modo={self.modo} base={self.base}")
            print(f"[WORKER] archivos encontrados: {len(archivos)}")

            if not archivos:
                self.signals.finished.emit([], self.base)
                return

            archivos_validos = set()
            for p in archivos:
                try:
                    archivos_validos.add(str(p.resolve()))
                except Exception:
                    archivos_validos.add(str(p))

            index_dir_name = ((cfg.get("paths", {}) or {}).get("index_dir", ".cv_index") or ".cv_index").strip()

            base_index_dir = carpeta_datos_usuario() / index_dir_name
            base_index_dir.mkdir(parents=True, exist_ok=True)

            db_name = "search_notes.sqlite3" if self.search_scope == "notes" else "search_cvs.sqlite3"
            db_path = base_index_dir / db_name

            print(f"[WORKER] recreando índice en: {db_path}")
            recrear_indice(db_path, archivos, cfg)
            print("[WORKER] índice recreado")

            if not self.palabras:
                encontrados = archivos[:self.max_resultados]
                self.signals.finished.emit(encontrados, self.base)
                return

            elif self.modo == "NOT":
                coincidencias = buscar_terminos(
                    db_path=db_path,
                    terms=self.palabras,
                    mode="OR",
                    max_results=max(100000, len(archivos) + 50),
                )

                excluidos = set()
                for r in coincidencias:
                    try:
                        excluidos.add(str(Path(r["path"]).resolve()))
                    except Exception:
                        excluidos.add(str(Path(r["path"])))

                encontrados = []
                for p in archivos:
                    try:
                        clave = str(p.resolve())
                    except Exception:
                        clave = str(p)

                    if clave in excluidos:
                        continue

                    encontrados.append(p)

                    if len(encontrados) >= self.max_resultados:
                        break

            else:
                filas = buscar_terminos(
                    db_path=db_path,
                    terms=self.palabras,
                    mode=self.modo,
                    max_results=self.max_resultados,
                )

                encontrados = []
                for r in filas:
                    try:
                        p = Path(r["path"])
                        clave = str(p.resolve())
                    except Exception:
                        p = Path(r["path"])
                        clave = str(p)

                    if clave in archivos_validos:
                        encontrados.append(p)

            print(f"[WORKER] resultados finales: {len(encontrados)}")
            self.signals.finished.emit(encontrados, self.base)

        except Exception as e:
            self.signals.error.emit(str(e))