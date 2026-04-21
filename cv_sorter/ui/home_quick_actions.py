from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore

from cv_sorter.services.notes_utils import cv_desde_nota


def buscar_cvs_con_notas_desde_home(self):
    base = self._home_base_actual()
    self._actualizar_stats_home()

    if base is None:
        self._mostrar_feedback_home("Primero selecciona una carpeta", "Pulsa «Elegir carpeta» o ve a Buscar")
        return

    self._ir_buscar()
    self.buscar_input.clear()
    self.buscar_input.setFocus()
    self._set_modo_busqueda("AND")
    self._set_scope_busqueda("cvs")

    resultados = obtener_cvs_con_notas(self)
    cargar_resultados_home_directos(self, resultados, scope="cvs")

    QtCore.QTimer.singleShot(120, self._actualizar_robot_peek_buscar)
    QtCore.QTimer.singleShot(220, self._actualizar_robot_peek_buscar)


def buscar_cvs_con_cliente_desde_home(self):
    base = self._home_base_actual()
    self._actualizar_stats_home()

    if base is None:
        self._mostrar_feedback_home("Primero selecciona una carpeta", "Pulsa «Elegir carpeta» o ve a Buscar")
        return

    self._ir_buscar()
    self.buscar_input.clear()
    self.buscar_input.setFocus()
    self._set_modo_busqueda("AND")
    self._set_scope_busqueda("cvs")

    resultados = obtener_cvs_con_cliente(self)
    cargar_resultados_home_directos(self, resultados, scope="cvs")

    QtCore.QTimer.singleShot(120, self._actualizar_robot_peek_buscar)
    QtCore.QTimer.singleShot(220, self._actualizar_robot_peek_buscar)


def obtener_cvs_con_notas(self) -> list[Path]:
    base = Path(getattr(self, "_carpeta_filtro", "") or getattr(self, "_last_base", "") or "")
    if not base or not base.exists():
        return []

    resultados = []
    for p in base.rglob("*"):
        try:
            if not p.is_file():
                continue
            nombre = p.name.lower()
            if nombre.endswith(".notas.txt"):
                cv = cv_desde_nota(p)
                if cv.exists() and cv.is_file():
                    resultados.append(cv)
        except Exception:
            continue

    vistos = set()
    unicos = []
    for p in resultados:
        clave = str(p).lower()
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(p)

    return sorted(unicos, key=lambda x: x.name.lower())


def obtener_cvs_con_cliente(self) -> list[Path]:
    base = Path(getattr(self, "_carpeta_filtro", "") or getattr(self, "_last_base", "") or "")
    if not base or not base.exists():
        return []

    resultados = []
    for p in base.rglob("*"):
        try:
            if not p.is_file():
                continue

            suf = p.suffix.lower()
            if suf not in {".pdf", ".doc", ".docx", ".odt", ".rtf"}:
                continue

            ruta_clientes = p.with_suffix(p.suffix + ".clientes.txt")
            if not ruta_clientes.exists():
                continue

            contenido = ruta_clientes.read_text(encoding="utf-8").strip()
            if contenido:
                resultados.append(p)

        except Exception:
            continue

    return sorted(resultados, key=lambda x: x.name.lower())


def cargar_resultados_home_directos(self, resultados: list[Path], scope: str = "cvs"):
    self._last_resultados = list(resultados or [])
    self._last_palabras = []

    base = None
    if getattr(self, "_carpeta_filtro", None):
        try:
            base = Path(self._carpeta_filtro)
        except Exception:
            base = None
    elif getattr(self, "_last_base", None):
        try:
            base = Path(self._last_base)
        except Exception:
            base = None

    if base is None or not base.exists():
        if hasattr(self, "buscar_lista"):
            self.buscar_lista.clear()

        if hasattr(self, "result_stack"):
            self.result_stack.setCurrentIndex(0)

        if hasattr(self, "empty_title"):
            self.empty_title.setText("Selecciona una carpeta primero")
        if hasattr(self, "empty_text"):
            self.empty_text.setText(
                "Para usar los accesos rápidos del HOME, primero elige una carpeta en la pantalla Buscar."
            )

        if hasattr(self, "buscar_estado"):
            self.buscar_estado.setText("No hay carpeta base seleccionada.")
        if hasattr(self, "resumen_count"):
            self.resumen_count.setText("0 resultados")
        if hasattr(self, "resumen_query"):
            self.resumen_query.setText("Búsqueda: —")
        if hasattr(self, "resumen_scope"):
            self.resumen_scope.setText("Buscar en: CVs")
        if hasattr(self, "resumen_carpeta"):
            self.resumen_carpeta.setText("Carpeta: —")
        if hasattr(self, "footer_estado"):
            self.footer_estado.setText("Selecciona una carpeta")
        if hasattr(self, "footer_contexto"):
            self.footer_contexto.setText("Carpeta: —")
        return

    self._last_base = base

    if hasattr(self, "combo_orden"):
        self.combo_orden.setCurrentIndex(0)

    if hasattr(self, "scope_cvs") and hasattr(self, "scope_notas"):
        if (scope or "cvs").lower() == "notes":
            self.scope_notas.setChecked(True)
        else:
            self.scope_cvs.setChecked(True)

    self._pintar_resultados(self._last_resultados, base)

    total = len(self._last_resultados)
    if hasattr(self, "footer_estado"):
        self.footer_estado.setText(f"{total} resultado(s)")
    if hasattr(self, "footer_contexto"):
        self.footer_contexto.setText(f"Carpeta: {base}")