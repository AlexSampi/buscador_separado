from __future__ import annotations

import html
import re
from pathlib import Path

from PySide6 import QtCore, QtWidgets

from cv_sorter.services.notes_utils import cv_desde_nota, resumen_desde_nota
from cv_sorter.ui.result_item_widget import ItemResultado


def highlight_words(self, text: str, words: list[str]) -> str:
    safe = html.escape(text)
    if not words:
        return safe

    uniq = sorted({w.strip().lower() for w in words if w.strip()}, key=len, reverse=True)
    if not uniq:
        return safe

    pattern = re.compile(r"(" + "|".join(re.escape(w) for w in uniq) + r")", re.IGNORECASE)

    def repl(m):
        return (
            "<span style='background:#e9d5ff;"
            "border:1px solid rgba(139,92,246,0.25);"
            "padding:1px 4px;border-radius:6px;"
            "font-weight:900;'>"
            f"{html.escape(m.group(0))}</span>"
        )

    return pattern.sub(repl, safe)


def ordenar_resultados(self, encontrados: list[Path]) -> list[Path]:
    if not hasattr(self, "combo_orden"):
        return encontrados

    modo_orden = self.combo_orden.currentText()

    def mtime_safe(p: Path):
        try:
            return p.stat().st_mtime
        except Exception:
            return 0

    def nombre_safe(p: Path):
        try:
            return p.name.lower()
        except Exception:
            return str(p).lower()

    if modo_orden == "Más recientes primero":
        return sorted(encontrados, key=mtime_safe, reverse=True)

    if modo_orden == "Más antiguos primero":
        return sorted(encontrados, key=mtime_safe)

    if modo_orden == "Nombre Z-A":
        return sorted(encontrados, key=nombre_safe, reverse=True)

    return sorted(encontrados, key=nombre_safe)


def recalcular_alturas_resultados(self):
    if not hasattr(self, "buscar_lista"):
        return

    es_modo_notas = hasattr(self, "scope_notas") and self.scope_notas.isChecked()

    for row in range(self.buscar_lista.count()):
        item = self.buscar_lista.item(row)
        w = self.buscar_lista.itemWidget(item)
        if w is None:
            continue

        w.adjustSize()
        alto_min = 126 if es_modo_notas else 108
        alto = max(w.sizeHint().height(), alto_min)
        item.setSizeHint(QtCore.QSize(0, alto))

    self.buscar_lista.doItemsLayout()
    self.buscar_lista.updateGeometries()
    self.buscar_lista.viewport().update()


def pintar_resultados(self, encontrados, base: Path):
    self._last_resultados = list(encontrados)
    self._last_base = Path(base)

    encontrados = list(encontrados)

    filtro_categoria = getattr(self, "_filtro_categoria_buscar", "Todas")
    es_modo_notas = hasattr(self, "scope_notas") and self.scope_notas.isChecked()

    if filtro_categoria != "Todas" and not es_modo_notas:
        filtrados = []
        for p in encontrados:
            try:
                categoria_cv = self._categoria_visible_cv(p)
            except Exception:
                categoria_cv = ""

            if categoria_cv == filtro_categoria:
                filtrados.append(p)

        encontrados = filtrados

    encontrados = ordenar_resultados(self, encontrados)
    self.buscar_lista.clear()

    q = self.buscar_input.text().strip() or "—"
    modo = "Todas"
    if hasattr(self, "rb_or") and self.rb_or.isChecked():
        modo = "Al menos una"
    elif hasattr(self, "rb_not") and self.rb_not.isChecked():
        modo = "Excluir"
    carp = str(self._carpeta_filtro) if self._carpeta_filtro else "Todas"

    self.resumen_query.setText(f"Búsqueda: {q}")
    self.resumen_modo.setText(f"Modo: {modo}")

    scope_txt = "CVs"
    if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
        scope_txt = "Notas"
    self.resumen_scope.setText(f"Buscar en: {scope_txt}")

    self.resumen_carpeta.setText(f"Carpeta: {carp}")

    if not encontrados:
        self.buscar_estado.setText("No se encontró nada.")
        self.resumen_count.setText("0 resultados")

        if hasattr(self, "result_stack"):
            self.result_stack.setCurrentIndex(0)

        es_modo_notas = hasattr(self, "scope_notas") and self.scope_notas.isChecked()

        if es_modo_notas:
            if hasattr(self, "empty_title"):
                self.empty_title.setText("No hay notas que coincidan")
            if hasattr(self, "empty_text"):
                self.empty_text.setText("No se encontraron archivos .notas.txt con esas palabras.")
        else:
            if hasattr(self, "empty_title"):
                self.empty_title.setText("No hay resultados")
            if hasattr(self, "empty_text"):
                self.empty_text.setText("Prueba con menos palabras, activa el modo OR o cambia la carpeta.")

        if hasattr(self, "sp_estado"):
            self.sp_estado.setText("Sin resultados")
        self._actualizar_consejo_oveun("no_results")
        return

    self.buscar_estado.setText("")
    self.resumen_count.setText(f"{len(encontrados)} resultados")

    modo_actual = "AND"
    if hasattr(self, "rb_or") and self.rb_or.isChecked():
        modo_actual = "OR"
    elif hasattr(self, "rb_not") and self.rb_not.isChecked():
        modo_actual = "NOT"

    if modo_actual == "NOT" and len(encontrados) >= 150:
        self.buscar_estado.setText("Mostrando los primeros 150 resultados para evitar bloquear la app.")
    elif len(encontrados) >= 300:
        self.buscar_estado.setText("Mostrando los primeros 300 resultados.")
    else:
        self.buscar_estado.setText("")

    if hasattr(self, "result_stack"):
        self.result_stack.setCurrentIndex(1)

    if hasattr(self, "empty_title"):
        self.empty_title.setText("Empieza escribiendo una búsqueda")
    if hasattr(self, "empty_text"):
        self.empty_text.setText('Ejemplos: “python sql”, “java spring”, “react docker”.')

    if hasattr(self, "sp_estado"):
        self.sp_estado.setText(f"{len(encontrados)} resultados encontrados")
        self._actualizar_consejo_oveun("has_results")

    for p in encontrados:
        try:
            rel = p.relative_to(base)
        except Exception:
            rel = p

        palabras = getattr(self, "_last_palabras", [])

        modo_actual = "AND"
        if hasattr(self, "rb_or") and self.rb_or.isChecked():
            modo_actual = "OR"
        elif hasattr(self, "rb_not") and self.rb_not.isChecked():
            modo_actual = "NOT"

        palabras_para_resaltar = [] if modo_actual == "NOT" else palabras

        nombre_html = highlight_words(self, p.name, palabras_para_resaltar)
        rel_html = highlight_words(self, str(rel), palabras_para_resaltar)

        etiqueta = (
            "<div style='line-height:1.15;'>"
            f"<span style='font-weight:900; color:#111827;'>{nombre_html}</span><br>"
            f"<span style='color:#6b7280; font-size:12px;'>{rel_html}</span>"
            "</div>"
        )

        es_modo_notas = hasattr(self, "scope_notas") and self.scope_notas.isChecked()

        if es_modo_notas:
            ruta_nota = p
            ruta_cv = cv_desde_nota(p)

            ultima_fecha, preview = resumen_desde_nota(ruta_nota)

            try:
                ruta_nota_rel = ruta_nota.relative_to(base)
            except Exception:
                ruta_nota_rel = ruta_nota

            nombre_mostrar = highlight_words(self, ruta_cv.name, palabras_para_resaltar)
            rel_mostrar = highlight_words(self, str(ruta_nota_rel), palabras_para_resaltar)
            fecha_html = highlight_words(self, ultima_fecha, palabras_para_resaltar) if ultima_fecha else "Sin fecha"
            preview_html = highlight_words(self, preview, palabras_para_resaltar) if preview else "Sin contenido visible"

            etiqueta = (
                "<div style='line-height:1.20;'>"
                f"<span style='font-weight:900; color:#111827;'>{nombre_mostrar}</span><br>"
                f"<span style='color:#6b7280; font-size:12px;'>Nota: {rel_mostrar}</span><br>"
                f"<span style='color:#7c3aed; font-size:12px; font-weight:800;'>Última anotación: {fecha_html}</span><br>"
                f"<span style='color:#4b5563; font-size:12px;'>{preview_html}</span>"
                "</div>"
            )

            item_widget = ItemResultado(
                etiqueta=etiqueta,
                ruta_cv=str(ruta_cv),
                tiene_notas=True,
                modo_resultado="note",
                ruta_nota=str(ruta_nota),
            )

        else:
            ruta_cv = p
            ruta_nota = ruta_cv.with_suffix(ruta_cv.suffix + ".notas.txt")
            tiene_notas = ruta_nota.exists()
            categoria_guardada = self._categoria_visible_cv(ruta_cv)

            score_cv = self._score_visible_cv(ruta_cv)

            if categoria_guardada or score_cv:
                etiqueta = (
                    "<div style='line-height:1.15;'>"
                    f"<span style='font-weight:900; color:#111827;'>{nombre_html}</span><br>"
                    f"<span style='color:#6b7280; font-size:12px;'>{rel_html}</span><br>"
                    f"<span style='color:#7c3aed; font-size:12px; font-weight:800;'>"
                    f"Categoría: {html.escape(categoria_guardada or '—')} · Score: {score_cv}"
                    "</span>"
                    "</div>"
                )

            item_widget = ItemResultado(
                etiqueta=etiqueta,
                ruta_cv=str(ruta_cv),
                tiene_notas=tiene_notas,
                modo_resultado="cv",
            )
            item_widget.notas_clicked.connect(self._crear_o_abrir_notas)
            item_widget.anadir_nota_clicked.connect(self._anadir_anotacion_con_fecha)
            item_widget.cliente_clicked.connect(self._gestionar_clientes_cv)

        item = QtWidgets.QListWidgetItem()
        self.buscar_lista.addItem(item)
        self.buscar_lista.setItemWidget(item, item_widget)

        item_widget.adjustSize()
        alto_item = max(item_widget.sizeHint().height(), 108 if not es_modo_notas else 126)
        item.setSizeHint(QtCore.QSize(0, alto_item))

        QtCore.QTimer.singleShot(0, self._recalcular_alturas_resultados)

    self.buscar_lista.update()