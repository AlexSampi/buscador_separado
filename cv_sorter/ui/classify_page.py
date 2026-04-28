from __future__ import annotations

from pathlib import Path
import yaml

from PySide6 import QtCore, QtGui, QtWidgets

from cv_sorter.utils import ruta_recurso
from cv_sorter.workers import _ApplyClassificationWorker, _ClassifyWorker


class _ResponsiveHeroCard(QtWidgets.QWidget):
    def __init__(self, caption: str, parent=None):
        super().__init__(parent)
        self._source_pixmap = QtGui.QPixmap()
        self._host_window = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(8)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setObjectName("ClasificarHeroImage")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setMinimumSize(0, 0)
        self.image_label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self.caption_label = QtWidgets.QLabel(caption)
        self.caption_label.setObjectName("ClasificarHeroCaption")
        self.caption_label.setAlignment(QtCore.Qt.AlignCenter)
        self.caption_label.setWordWrap(True)

        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.caption_label, 0, QtCore.Qt.AlignCenter)

    def set_source_pixmap(self, pixmap: QtGui.QPixmap):
        self._source_pixmap = QtGui.QPixmap(pixmap)
        if self.isVisible():
            self._schedule_refresh()

    def _ensure_host_window(self):
        host_window = self.window()
        if host_window is not None and host_window is not self._host_window:
            if self._host_window is not None:
                self._host_window.removeEventFilter(self)
            self._host_window = host_window
            self._host_window.installEventFilter(self)

    def showEvent(self, event):
        self._ensure_host_window()
        self._schedule_refresh()
        return super().showEvent(event)

    def resizeEvent(self, event):
        self._schedule_refresh()
        return super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if obj is self._host_window and event.type() == QtCore.QEvent.Resize:
            self._schedule_refresh()
        return super().eventFilter(obj, event)

    def _schedule_refresh(self):
        QtCore.QTimer.singleShot(0, self._apply_mode)

    def refresh_display(self):
        self._ensure_host_window()
        self._schedule_refresh()

    def _apply_mode(self):
        if self._source_pixmap.isNull():
            self.image_label.clear()
            return

        self._ensure_host_window()

        if self._host_window is not None and self._host_window.isVisible():
            window_height = self._host_window.height()
            window_width = self._host_window.width()
        else:
            window_height = self.height()
            window_width = self.width()

        if window_height <= 0 or window_width <= 0:
            return

        if window_height < 660 or window_width < 1040:
            self.setVisible(False)
            return
        self.setVisible(True)

        medium_mode = window_height < 820 or window_width < 1280
        self.caption_label.setVisible(not medium_mode)

        if medium_mode:
            self.setMinimumWidth(250)
            self.setMaximumWidth(320)
            self.setMinimumHeight(168)
            self.setMaximumHeight(220)
            target_width = 190
            target_height = 138
        else:
            self.setMinimumWidth(320)
            self.setMaximumWidth(440)
            self.setMinimumHeight(286)
            self.setMaximumHeight(362)
            target_width = 360
            target_height = 260

        scaled = self._source_pixmap.scaled(
            target_width,
            target_height,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setFixedSize(scaled.size())
        self.updateGeometry()


def build_classify_page(self):
    pantalla_clasificar = QtWidgets.QWidget()
    pantalla_clasificar.setObjectName("Pantalla")
    layout_clasificar = QtWidgets.QVBoxLayout(pantalla_clasificar)
    self._poner_fondo_lineas(pantalla_clasificar, "clasificar")
    layout_clasificar.setContentsMargins(18, 18, 18, 18)
    layout_clasificar.setSpacing(10)

    card_clasificar = QtWidgets.QWidget()
    card_clasificar.setObjectName("Card")
    layout_card = QtWidgets.QVBoxLayout(card_clasificar)
    layout_card.setContentsMargins(24, 24, 24, 24)
    layout_card.setSpacing(14)

    fila_top = QtWidgets.QHBoxLayout()
    fila_top.setContentsMargins(0, 0, 0, 0)
    fila_top.setSpacing(10)

    self.clasificar_volver = QtWidgets.QPushButton("Volver")
    self.clasificar_volver.setObjectName("BotonSecundario")
    self.clasificar_volver.setCursor(QtCore.Qt.PointingHandCursor)

    fila_top.addWidget(self.clasificar_volver, 0)
    fila_top.addStretch(1)

    self.clasificar_titulo = QtWidgets.QLabel("CLASIFICAR CVS DESDE CARPETA")
    self.clasificar_titulo.setObjectName("TituloSistema")

    self.clasificar_subtitulo = QtWidgets.QLabel(
        "Revisa el lote, valida la propuesta y aplica la clasificacion con control visual antes de mover los CVs."
    )
    self.clasificar_subtitulo.setObjectName("SubtituloSistema")
    self.clasificar_subtitulo.setWordWrap(True)

    self.clasificar_estado = QtWidgets.QLabel(
        "Selecciona una carpeta de origen para generar una propuesta automatica lista para revisar."
    )
    self.clasificar_estado.setObjectName("ClasificarEstado")
    self.clasificar_estado.setProperty("classifyTone", "soft")
    self.clasificar_estado.setWordWrap(True)
    self.clasificar_estado.setMinimumHeight(54)

    body = QtWidgets.QWidget()
    body.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    body_layout = QtWidgets.QGridLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setHorizontalSpacing(16)
    body_layout.setVerticalSpacing(12)
    body_layout.setColumnStretch(0, 4)
    body_layout.setColumnStretch(1, 14)

    self.clasificar_box = QtWidgets.QWidget()
    self.clasificar_box.setObjectName("ClasificarPanel")
    self.clasificar_box.setProperty("classifyPanel", "control")
    self.clasificar_box.setMinimumWidth(420)
    self.clasificar_box.setMaximumWidth(440)
    self.clasificar_box.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
    clas_box_layout = QtWidgets.QVBoxLayout(self.clasificar_box)
    clas_box_layout.setContentsMargins(20, 20, 20, 20)
    clas_box_layout.setSpacing(12)

    preview_box = QtWidgets.QWidget()
    preview_box.setObjectName("ClasificarPanel")
    preview_box.setProperty("classifyPanel", "preview")
    preview_box.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    preview_layout = QtWidgets.QVBoxLayout(preview_box)
    preview_layout.setContentsMargins(20, 20, 20, 20)
    preview_layout.setSpacing(12)

    body_layout.addWidget(self.clasificar_box, 0, 0)
    body_layout.addWidget(preview_box, 0, 1)

    self.clasificar_lab_origen = QtWidgets.QLabel("Carpeta de origen")
    self.clasificar_lab_origen.setObjectName("SideSubTitle")
    self.clasificar_lab_origen.setProperty("classifyLabel", "section")

    fila_origen = QtWidgets.QHBoxLayout()
    fila_origen.setContentsMargins(0, 0, 0, 0)
    fila_origen.setSpacing(8)

    self.clasificar_input_origen = QtWidgets.QLineEdit()
    self.clasificar_input_origen.setProperty("classifyInput", "origin")
    self.clasificar_input_origen.setPlaceholderText("Selecciona la carpeta que contiene los CVs del lote...")
    self.clasificar_input_origen.setReadOnly(True)

    self.clasificar_btn_origen = QtWidgets.QPushButton("Elegir origen")
    self.clasificar_btn_origen.setObjectName("SideBtn")
    self.clasificar_btn_origen.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_origen.setMinimumWidth(116)

    fila_origen.addWidget(self.clasificar_input_origen, 1)
    fila_origen.addWidget(self.clasificar_btn_origen, 0)

    self.clasificar_lab_destino_auto = QtWidgets.QLabel("Destino previsto")
    self.clasificar_lab_destino_auto.setObjectName("SideSubTitle")
    self.clasificar_lab_destino_auto.setProperty("classifyLabel", "section")

    self.clasificar_destino_auto = QtWidgets.QLabel("Se calculara automaticamente al elegir la carpeta de origen.")
    self.clasificar_destino_auto.setObjectName("SideInfo")
    self.clasificar_destino_auto.setProperty("classifyHint", "soft")
    self.clasificar_destino_auto.setWordWrap(True)

    acciones_title = QtWidgets.QLabel("Acciones rapidas")
    acciones_title.setObjectName("SideSubTitle")
    acciones_title.setProperty("classifyLabel", "section")

    acciones_grid = QtWidgets.QGridLayout()
    acciones_grid.setContentsMargins(0, 0, 0, 0)
    acciones_grid.setHorizontalSpacing(8)
    acciones_grid.setVerticalSpacing(8)
    acciones_grid.setColumnStretch(0, 1)
    acciones_grid.setColumnStretch(1, 1)

    self.clasificar_btn_escaneo = QtWidgets.QPushButton("Escanear lote")
    self.clasificar_btn_escaneo.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_escaneo.setProperty("classifyRole", "primary")
    self.clasificar_btn_escaneo.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_escaneo.setMinimumHeight(38)
    self.clasificar_btn_escaneo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_escaneo.setToolTip("Analiza la carpeta de origen y genera una propuesta automatica.")
    self.clasificar_btn_escaneo.setStyleSheet("font-size: 12px; padding: 8px 10px;")

    self.clasificar_btn_aplicar = QtWidgets.QPushButton("Aplicar propuesta")
    self.clasificar_btn_aplicar.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_aplicar.setProperty("classifyRole", "accent")
    self.clasificar_btn_aplicar.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_aplicar.setEnabled(False)
    self.clasificar_btn_aplicar.setMinimumHeight(38)
    self.clasificar_btn_aplicar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_aplicar.setToolTip("Aplica la propuesta de clasificacion y mueve los CVs al destino previsto.")
    self.clasificar_btn_aplicar.setStyleSheet("font-size: 12px; padding: 8px 10px;")

    self.clasificar_btn_deshacer = QtWidgets.QPushButton("Revertir ultimo")
    self.clasificar_btn_deshacer.setObjectName("BotonSecundario")
    self.clasificar_btn_deshacer.setProperty("classifyRole", "secondary")
    self.clasificar_btn_deshacer.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_deshacer.setEnabled(False)
    self.clasificar_btn_deshacer.setMinimumHeight(38)
    self.clasificar_btn_deshacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_deshacer.setToolTip("Revierte la ultima clasificacion aplicada.")
    self.clasificar_btn_deshacer.setStyleSheet("font-size: 12px; padding: 8px 10px;")

    self.clasificar_btn_limpiar = QtWidgets.QPushButton("Limpiar")
    self.clasificar_btn_limpiar.setObjectName("SideBtn")
    self.clasificar_btn_limpiar.setProperty("classifyRole", "ghost")
    self.clasificar_btn_limpiar.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_limpiar.setMinimumHeight(38)
    self.clasificar_btn_limpiar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_limpiar.setToolTip("Limpia la propuesta actual y reinicia la pantalla.")
    self.clasificar_btn_limpiar.setStyleSheet("font-size: 12px; padding: 8px 10px;")

    acciones_grid.addWidget(self.clasificar_btn_escaneo, 0, 0)
    acciones_grid.addWidget(self.clasificar_btn_aplicar, 0, 1)
    acciones_grid.addWidget(self.clasificar_btn_deshacer, 1, 0)
    acciones_grid.addWidget(self.clasificar_btn_limpiar, 1, 1)

    resumen_title = QtWidgets.QLabel("Resumen del lote")
    resumen_title.setObjectName("SideSubTitle")
    resumen_title.setProperty("classifyLabel", "section")

    self.clasificar_resumen = QtWidgets.QLabel("Pendiente de escaneo.")
    self.clasificar_resumen.setObjectName("ClasificarResumen")
    self.clasificar_resumen.setProperty("classifyTone", "summary")
    self.clasificar_resumen.setWordWrap(True)
    self.clasificar_resumen.setMinimumHeight(78)
    self.clasificar_resumen.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    clas_box_layout.addWidget(self.clasificar_lab_origen)
    clas_box_layout.addLayout(fila_origen)
    clas_box_layout.addWidget(self.clasificar_lab_destino_auto)
    clas_box_layout.addWidget(self.clasificar_destino_auto)
    clas_box_layout.addWidget(acciones_title)
    clas_box_layout.addLayout(acciones_grid)
    clas_box_layout.addWidget(resumen_title)
    clas_box_layout.addWidget(self.clasificar_resumen)
    clas_box_layout.addStretch(1)

    preview_title = QtWidgets.QLabel("Vista previa")
    preview_title.setObjectName("SideTitle")
    preview_title.setProperty("classifyLabel", "preview")

    preview_hint = QtWidgets.QLabel("Doble clic en un CV para ajustar su categoria antes de aplicar.")
    preview_hint.setObjectName("SideInfo")
    preview_hint.setProperty("classifyHint", "preview")
    preview_hint.setWordWrap(True)

    self.clasificar_result_stack = QtWidgets.QStackedWidget()

    empty = QtWidgets.QWidget()
    empty.setObjectName("EmptyState")
    empty.setProperty("classifyTone", "empty")
    empty_layout = QtWidgets.QVBoxLayout(empty)
    empty_layout.setContentsMargins(18, 18, 18, 18)
    empty_layout.setSpacing(10)
    empty_layout.setAlignment(QtCore.Qt.AlignCenter)

    empty_title = QtWidgets.QLabel("Aun no hay propuesta")
    empty_title.setObjectName("EmptyTitle")
    empty_title.setAlignment(QtCore.Qt.AlignCenter)
    empty_title.setProperty("classifyTone", "empty")

    empty_text = QtWidgets.QLabel(
        "Selecciona una carpeta de origen y ejecuta el escaneo para ver la clasificacion sugerida."
    )
    empty_text.setObjectName("EmptyText")
    empty_text.setAlignment(QtCore.Qt.AlignCenter)
    empty_text.setWordWrap(True)
    empty_text.setMaximumWidth(360)
    empty_text.setProperty("classifyTone", "empty")

    hero_media = _ResponsiveHeroCard("OVEUN listo para revisar el lote")
    hero_media.setObjectName("ClasificarHeroMedia")
    hero_media.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    hero_media.setMinimumWidth(320)
    hero_media.setMaximumWidth(440)
    hero_media.setMinimumHeight(286)
    hero_media.setMaximumHeight(362)

    hero_pixmap = QtGui.QPixmap(str(ruta_recurso("assets/robot_clasificador.png")))
    if hero_pixmap.isNull():
        hero_pixmap = QtGui.QPixmap(str(ruta_recurso("assets/robot_home_welcome.png")))
    if not hero_pixmap.isNull():
        hero_media.set_source_pixmap(hero_pixmap)
    self.clasificar_hero_media = hero_media

    empty_layout.addWidget(empty_title, 0, QtCore.Qt.AlignCenter)
    empty_layout.addWidget(empty_text, 0, QtCore.Qt.AlignCenter)
    empty_layout.addWidget(hero_media, 0, QtCore.Qt.AlignCenter)

    self.clasificar_lista = QtWidgets.QListWidget()
    self.clasificar_lista.setObjectName("ClasificarLista")
    self.clasificar_lista.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    self.clasificar_lista.setSpacing(12)
    self.clasificar_lista.setWordWrap(True)
    self.clasificar_lista.setUniformItemSizes(False)
    self.clasificar_lista.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    self.clasificar_lista.setViewportMargins(0, 10, 0, 10)
    self.clasificar_lista.setProperty("classifySurface", "results")

    self.clasificar_result_stack.addWidget(empty)
    self.clasificar_result_stack.addWidget(self.clasificar_lista)
    self.clasificar_result_stack.setCurrentIndex(0)

    preview_layout.addWidget(preview_title)
    preview_layout.addWidget(preview_hint)
    preview_layout.addWidget(self.clasificar_result_stack, 1)

    shadow_control = QtWidgets.QGraphicsDropShadowEffect(self.clasificar_box)
    shadow_control.setBlurRadius(28)
    shadow_control.setOffset(0, 8)
    shadow_control.setColor(QtGui.QColor(109, 40, 217, 18))
    self.clasificar_box.setGraphicsEffect(shadow_control)

    shadow_preview = QtWidgets.QGraphicsDropShadowEffect(preview_box)
    shadow_preview.setBlurRadius(34)
    shadow_preview.setOffset(0, 10)
    shadow_preview.setColor(QtGui.QColor(109, 40, 217, 24))
    preview_box.setGraphicsEffect(shadow_preview)

    layout_card.addLayout(fila_top)
    layout_card.addWidget(self.clasificar_titulo)
    layout_card.addWidget(self.clasificar_subtitulo)
    layout_card.addSpacing(6)
    layout_card.addWidget(self.clasificar_estado)
    layout_card.addWidget(body, 1)

    layout_clasificar.addWidget(card_clasificar, 1)
    return pantalla_clasificar


def actualizar_preview_clasificacion(self):
    if not hasattr(self, "clasificar_result_stack"):
        return

    if hasattr(self, "clasificar_lista") and self.clasificar_lista.count() > 0:
        self.clasificar_result_stack.setCurrentIndex(1)
    else:
        self.clasificar_result_stack.setCurrentIndex(0)
        if hasattr(self, "clasificar_hero_media") and self.clasificar_hero_media:
            self.clasificar_hero_media.refresh_display()


def actualizar_resumen_clasificacion_manual(self):
    total = len(self._clasificar_resultados)

    if total <= 0:
        self.clasificar_resumen.setText("No hay resultados para clasificar.")
        return

    conteo = {}
    for r in self._clasificar_resultados:
        cat = self._normalizar_categoria_clasificacion(r.get("categoria", "Otros"))
        conteo[cat] = conteo.get(cat, 0) + 1

    destino_txt = str(self._clasificar_destino) if self._clasificar_destino else "Sin destino automatico"
    resumen_partes = [f"{total} CVs analizados", f"Destino: {destino_txt}"]

    for cat in sorted(conteo.keys()):
        resumen_partes.append(f"{cat}: {conteo[cat]}")

    self.clasificar_resumen.setText(" · ".join(resumen_partes))


def actualizar_estado_boton_deshacer(self):
    if not hasattr(self, "clasificar_btn_deshacer"):
        return

    historial = getattr(self, "_clasificar_ultimo_historial", []) or []
    self.clasificar_btn_deshacer.setEnabled(len(historial) > 0)


def clasificar_limpiar(self):
    self._clasificar_origen = None
    self._clasificar_destino = None
    self._clasificar_resultados = []

    if hasattr(self, "clasificar_input_origen"):
        self.clasificar_input_origen.clear()

    if hasattr(self, "clasificar_lista"):
        self.clasificar_lista.clear()

    if hasattr(self, "clasificar_resumen"):
        self.clasificar_resumen.setText("Pendiente de escaneo.")

    if hasattr(self, "clasificar_destino_auto"):
        self.clasificar_destino_auto.setText("Se calculara automaticamente al elegir carpeta origen.")

    if hasattr(self, "clasificar_estado"):
        self.clasificar_estado.setText("Selecciona carpeta origen para generar una propuesta automatica.")

    if hasattr(self, "clasificar_btn_aplicar"):
        self.clasificar_btn_aplicar.setEnabled(False)

    self._clasificar_ultimo_historial = []
    self._actualizar_estado_boton_deshacer()
    actualizar_preview_clasificacion(self)

    self._carpeta_filtro = None
    self._actualizar_resumen_carpeta()
    self.footer_contexto.setText("Carpeta: —")


def clasificar_editar_item(self, item: QtWidgets.QListWidgetItem):
    if item is None:
        return

    idx = item.data(QtCore.Qt.UserRole)
    if idx is None:
        return

    try:
        idx = int(idx)
    except Exception:
        return

    if idx < 0 or idx >= len(self._clasificar_resultados):
        return

    dato = self._clasificar_resultados[idx]
    nombre = dato.get("nombre", "Sin nombre")
    categoria_actual = self._normalizar_categoria_clasificacion(dato.get("categoria", "Otros"))

    categorias = self._categorias_clasificacion()

    nueva_categoria, ok = QtWidgets.QInputDialog.getItem(
        self,
        "Editar categoria",
        f"Selecciona la categoria para:\n{nombre}",
        categorias,
        categorias.index(categoria_actual) if categoria_actual in categorias else 0,
        False,
    )

    if not ok:
        return

    nueva_categoria = self._normalizar_categoria_clasificacion(nueva_categoria)
    self._clasificar_resultados[idx]["categoria"] = nueva_categoria

    self._repintar_lista_clasificacion()
    self._actualizar_resumen_clasificacion_manual()
    self.clasificar_estado.setText("Categoria actualizada manualmente.")


def clasificar_elegir_origen(self):
    carpeta = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecciona carpeta origen")
    if not carpeta:
        return

    self._clasificar_origen = Path(carpeta)
    self.clasificar_input_origen.setText(str(self._clasificar_origen))

    nombre_base = self._clasificar_origen.name.strip() or "CVs"
    destino_auto = self._clasificar_origen.parent / f"{nombre_base}_clasificados"
    self._clasificar_destino = destino_auto

    if hasattr(self, "clasificar_destino_auto"):
        self.clasificar_destino_auto.setText(str(self._clasificar_destino))

    self._clasificar_resultados = []
    self._clasificar_ultimo_historial = []
    self._actualizar_estado_boton_deshacer()

    if hasattr(self, "clasificar_lista"):
        self.clasificar_lista.clear()

    if hasattr(self, "clasificar_btn_aplicar"):
        self.clasificar_btn_aplicar.setEnabled(False)

    actualizar_preview_clasificacion(self)
    self.clasificar_estado.setText("Carpeta origen seleccionada. Destino automatico preparado.")
    self.footer_contexto.setText(f"Carpeta: {self._clasificar_origen}")


def clasificar_escanear(self):
    if not self._clasificar_origen:
        self.clasificar_estado.setText("Selecciona primero la carpeta origen.")
        return

    if not self._clasificar_origen.exists():
        self.clasificar_estado.setText("La carpeta origen no existe.")
        return

    self.clasificar_lista.clear()
    self._clasificar_resultados = []
    actualizar_preview_clasificacion(self)

    self.clasificar_estado.setText("Iniciando escaneo...")
    self.clasificar_resumen.setText("Analizando CVs, espera un momento...")
    self.clasificar_btn_escaneo.setEnabled(False)

    worker = _ClassifyWorker(base=self._clasificar_origen, max_resultados=300)
    worker.signals.progress.connect(self._clasificar_on_progress)
    worker.signals.finished.connect(self._clasificar_on_finished)
    worker.signals.error.connect(self._clasificar_on_error)

    self._threadpool.start(worker)


def clasificar_on_progress(self, texto: str):
    if hasattr(self, "clasificar_estado"):
        self.clasificar_estado.setText(texto)


def clasificar_on_finished(self, resultados, base):
    self.clasificar_btn_escaneo.setEnabled(True)
    self._clasificar_resultados = list(resultados)

    self.clasificar_lista.clear()

    total = len(resultados)
    if total <= 0:
        self.clasificar_btn_aplicar.setEnabled(False)
        self.clasificar_estado.setText("Escaneo completado sin resultados.")
        self.clasificar_resumen.setText("No se detectaron CVs validos.")
        actualizar_preview_clasificacion(self)
        return

    self.clasificar_btn_aplicar.setEnabled(True)

    self._actualizar_resumen_clasificacion_manual()
    self.clasificar_estado.setText("Propuesta de clasificacion generada. Revisa el destino previsto antes de aplicar.")

    self._repintar_lista_clasificacion()
    actualizar_preview_clasificacion(self)


def clasificar_on_error(self, msg: str):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_estado.setText(f"Error en clasificacion: {msg}")
    self.clasificar_resumen.setText("No se pudo completar el escaneo.")
    actualizar_preview_clasificacion(self)


def clasificar_aplicar(self):
    if not self._clasificar_resultados:
        self.clasificar_estado.setText("Primero genera una propuesta de clasificacion.")
        return

    if not self._clasificar_destino:
        self.clasificar_estado.setText("No hay destino automatico preparado.")
        return

    respuesta = QtWidgets.QMessageBox.question(
        self,
        "Confirmar clasificacion",
        (
            f"Se van a mover {len(self._clasificar_resultados)} CVs a la carpeta de clasificacion.\n\n"
            f"Destino:\n{self._clasificar_destino}\n\n"
            "Esta accion reorganizara los archivos y generara sus metadatos.\n\n"
            "Quieres continuar?"
        ),
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )

    if respuesta != QtWidgets.QMessageBox.Yes:
        return

    self.clasificar_btn_aplicar.setEnabled(False)
    self.clasificar_btn_escaneo.setEnabled(False)
    self.clasificar_estado.setText("Preparando movimiento de CVs...")

    worker = _ApplyClassificationWorker(
        resultados=self._clasificar_resultados,
        destino_base=self._clasificar_destino,
    )
    worker.signals.progress.connect(self._clasificar_aplicar_on_progress)
    worker.signals.finished.connect(self._clasificar_aplicar_on_finished)
    worker.signals.error.connect(self._clasificar_aplicar_on_error)

    self._threadpool.start(worker)


def clasificar_aplicar_on_progress(self, texto: str):
    self.clasificar_estado.setText(texto)


def clasificar_aplicar_on_finished(self, info: dict):
    movidos = int(info.get("movidos", 0))
    errores = int(info.get("errores", 0))
    destino = str(info.get("destino_base", ""))
    historial = list(info.get("historial", []))

    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_aplicar.setEnabled(False)

    self._clasificar_ultimo_historial = historial
    self._actualizar_estado_boton_deshacer()
    if destino:
        self._carpeta_filtro = Path(destino)
        self._actualizar_resumen_carpeta()
        self.footer_contexto.setText(f"Carpeta: {self._carpeta_filtro}")

    clasificaciones_guardadas = 0

    for mov in historial:
        try:
            ruta_final = mov.get("destino", "")
            categoria = mov.get("categoria", "Otros")

            if ruta_final:
                score = self._calcular_score_cv(ruta_final)

                if self._guardar_clasificacion_cv(ruta_final, categoria, origen="auto"):
                    ruta_meta = self._ruta_clasificacion_cv(ruta_final)

                    try:
                        data = yaml.safe_load(ruta_meta.read_text(encoding="utf-8")) or {}
                    except Exception:
                        data = {}

                    data["score"] = score

                    try:
                        ruta_meta.write_text(
                            yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                            encoding="utf-8",
                        )
                    except Exception:
                        pass

                    clasificaciones_guardadas += 1
        except Exception:
            continue

    self.clasificar_estado.setText(
        f"Clasificacion aplicada correctamente · Historial: {len(historial)} · Metadatos: {clasificaciones_guardadas}"
    )
    self.clasificar_resumen.setText(
        f"Movidos: {movidos} · Errores: {errores} · Metadatos: {clasificaciones_guardadas} · Buscar usara: {destino}"
    )

    QtWidgets.QMessageBox.information(
        self,
        "Clasificacion completada",
        (
            "La clasificacion se ha aplicado correctamente.\n\n"
            f"CVs movidos: {movidos}\n"
            f"Errores: {errores}\n"
            f"Elementos en historial: {len(historial)}\n"
            f"Metadatos guardados: {clasificaciones_guardadas}\n\n"
            f"Carpeta activa para Buscar:\n{destino}\n\n"
            "A continuacion se abrira la pantalla de busqueda con esa carpeta ya seleccionada."
        ),
    )

    self.clasificar_lista.clear()
    self._clasificar_resultados = []
    actualizar_preview_clasificacion(self)

    QtCore.QTimer.singleShot(0, self._ir_buscar)


def clasificar_aplicar_on_error(self, msg: str):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_aplicar.setEnabled(bool(self._clasificar_resultados))
    self.clasificar_estado.setText(f"Error aplicando clasificacion: {msg}")
