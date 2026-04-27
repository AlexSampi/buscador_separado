from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
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
            self.refresh_display()

    def _ensure_host_window(self):
        host_window = self.window()
        if host_window is not None and host_window is not self._host_window:
            if self._host_window is not None:
                self._host_window.removeEventFilter(self)
            self._host_window = host_window
            self._host_window.installEventFilter(self)

    def showEvent(self, event):
        self._ensure_host_window()
        self.refresh_display()
        return super().showEvent(event)

    def resizeEvent(self, event):
        self.refresh_display()
        return super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if obj is self._host_window and event.type() == QtCore.QEvent.Resize:
            self.refresh_display()
        return super().eventFilter(obj, event)

    def refresh_display(self):
        self._ensure_host_window()
        QtCore.QTimer.singleShot(0, self._apply_mode)

    def _apply_mode(self):
        if self._source_pixmap.isNull():
            self.image_label.clear()
            return

        window_width = self._host_window.width() if self._host_window is not None else self.width()
        window_height = self._host_window.height() if self._host_window is not None else self.height()

        if window_width < 1080 or window_height < 680:
            self.hide()
            return

        self.show()
        medium_mode = window_width < 1320 or window_height < 820
        self.caption_label.setVisible(not medium_mode)

        if medium_mode:
            self.setMinimumWidth(220)
            self.setMaximumWidth(280)
            self.setMinimumHeight(148)
            self.setMaximumHeight(188)
            target = QtCore.QSize(170, 122)
        else:
            self.setMinimumWidth(280)
            self.setMaximumWidth(360)
            self.setMinimumHeight(220)
            self.setMaximumHeight(300)
            target = QtCore.QSize(260, 188)

        scaled = self._source_pixmap.scaled(
            target,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)
        self.image_label.setFixedSize(scaled.size())
        self.updateGeometry()


def _refresh_widget_style(widget: QtWidgets.QWidget | None):
    if widget is None:
        return
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _crear_metric_card(titulo: str, tone: str) -> tuple[QtWidgets.QWidget, QtWidgets.QLabel]:
    card = QtWidgets.QWidget()
    card.setObjectName("ClasificarMetricCard")
    card.setProperty("metricTone", tone)
    card.setMinimumHeight(58)
    card.setMaximumHeight(64)

    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(12, 10, 12, 10)
    layout.setSpacing(1)

    value = QtWidgets.QLabel("0")
    value.setObjectName("ClasificarMetricValue")

    label = QtWidgets.QLabel(titulo)
    label.setObjectName("ClasificarMetricLabel")

    layout.addWidget(value)
    layout.addWidget(label)
    return card, value


def _categoria_corta_clasificacion(categoria: str) -> str:
    categoria = (categoria or "Otros").strip()
    mapping = {
        "IT_Programacion": "IT / Prog",
        "Ingenieria": "Ingenieria",
        "Diseno": "Diseno",
        "Marketing": "Marketing",
        "Administracion": "Admin",
        "Otros": "Otros",
    }
    return mapping.get(categoria, categoria.replace("_", " "))


def _aplicar_estilo_chip(label: QtWidgets.QLabel, texto: str, color: QtGui.QColor, subtle: bool = False):
    c = QtGui.QColor(color)
    alpha_bg = 28 if subtle else 46
    alpha_border = 96 if subtle else 132
    label.setText(texto)
    label.setStyleSheet(
        f"""
        QLabel {{
            background: rgba({c.red()}, {c.green()}, {c.blue()}, {alpha_bg});
            border: 1px solid rgba({c.red()}, {c.green()}, {c.blue()}, {alpha_border});
            border-radius: 999px;
            padding: 6px 12px;
            color: #111827;
            font-size: 11px;
            font-weight: 900;
        }}
        """
    )


def _extraer_ratio_progreso(texto: str) -> tuple[int, int] | None:
    match = re.search(r"(\d+)\s*/\s*(\d+)", texto or "")
    if not match:
        return None
    current = int(match.group(1))
    total = int(match.group(2))
    if total <= 0:
        return None
    return current, total


def _conteo_categorias_clasificacion(self) -> Counter:
    conteo: Counter = Counter()
    for resultado in getattr(self, "_clasificar_resultados", []) or []:
        categoria = self._normalizar_categoria_clasificacion(resultado.get("categoria", "Otros"))
        conteo[categoria] += 1
    return conteo


def set_clasificar_progress_state(
    self,
    stage: str,
    headline: str,
    detail: str = "",
    current: int | None = None,
    total: int | None = None,
):
    if not hasattr(self, "clasificar_progress_shell"):
        return

    stage = (stage or "idle").strip().lower() or "idle"
    shell = self.clasificar_progress_shell
    bar = self.clasificar_progress_bar

    shell.setProperty("classifyStage", stage)
    bar.setProperty("classifyStage", stage)
    _refresh_widget_style(shell)
    _refresh_widget_style(bar)

    self.clasificar_progress_label.setText(headline or "Lote listo")
    self.clasificar_progress_meta.setText(detail or "")

    defaults = {
        "idle": (0, "Inicial"),
        "prepared": (12, "Lista"),
        "scanning": (8, "En curso"),
        "ready": (100, "Lista"),
        "applying": (12, "Aplicando"),
        "done": (100, "Hecho"),
        "error": (0, "Aviso"),
    }

    if current is not None and total and total > 0:
        percent = max(0, min(100, round((current / total) * 100)))
        value_txt = f"{current}/{total}"
    else:
        percent, value_txt = defaults.get(stage, (0, "0%"))

    bar.setValue(percent)
    self.clasificar_progress_value.setText(value_txt)


def actualizar_metricas_clasificacion(
    self,
    total: int | None = None,
    categorias: int | None = None,
    preparados: int | None = None,
    top: str | None = None,
):
    if not hasattr(self, "clasificar_metric_total_value"):
        return

    conteo = _conteo_categorias_clasificacion(self)

    if total is None:
        total = sum(conteo.values())
    if categorias is None:
        categorias = len(conteo)
    if preparados is None:
        preparados = total
    if top is None:
        if conteo:
            top_categoria, _top_total = max(conteo.items(), key=lambda item: (item[1], item[0]))
            top = _categoria_corta_clasificacion(top_categoria)
        else:
            top = "--"

    self.clasificar_metric_total_value.setText(str(total))
    self.clasificar_metric_categorias_value.setText(str(categorias))
    self.clasificar_metric_listos_value.setText(str(preparados))
    self.clasificar_metric_top_value.setText(top)


def _actualizar_chips_distribucion(self):
    chips = getattr(self, "clasificar_distribution_chips", []) or []
    if not chips:
        return

    conteo = _conteo_categorias_clasificacion(self)
    ordered = sorted(conteo.items(), key=lambda item: (-item[1], item[0]))[:3]

    for idx, chip in enumerate(chips):
        if idx >= len(ordered):
            chip.hide()
            continue
        categoria, cantidad = ordered[idx]
        _aplicar_estilo_chip(
            chip,
            f"{_categoria_corta_clasificacion(categoria)} · {cantidad}",
            self._color_categoria_clasificacion(categoria),
            subtle=True,
        )
        chip.show()


def actualizar_detalle_preview_clasificacion(self, item: QtWidgets.QListWidgetItem | None = None):
    if not hasattr(self, "clasificar_preview_title"):
        return

    total = len(getattr(self, "_clasificar_resultados", []) or [])
    if item is None and hasattr(self, "clasificar_lista"):
        item = self.clasificar_lista.currentItem()

    if item is None or total <= 0:
        self.clasificar_preview_stage.setText("Borrador")
        self.clasificar_preview_counter.setText("Borrador")
        self.clasificar_preview_title.setText("Selecciona un CV del lote")
        self.clasificar_preview_meta.setText("Aqui veras la categoria sugerida y el destino antes de aplicar.")
        self.clasificar_preview_destination.setText("Destino previsto: aparecera al generar resultados.")
        self.clasificar_preview_hint.setText("Doble clic para ajustar la categoria antes de aplicar.")
        _aplicar_estilo_chip(self.clasificar_preview_badge, "Pendiente", QtGui.QColor(139, 92, 246), subtle=True)
        _actualizar_chips_distribucion(self)
        return

    idx = item.data(QtCore.Qt.UserRole)
    try:
        idx = int(idx)
    except Exception:
        idx = -1

    if idx < 0 or idx >= total:
        return

    dato = self._clasificar_resultados[idx]
    nombre = dato.get("nombre", "Sin nombre")
    categoria = self._normalizar_categoria_clasificacion(dato.get("categoria", "Otros"))
    destino = self._texto_destino_previsto(categoria, nombre) or "Destino pendiente de generar."
    color = self._color_categoria_clasificacion(categoria)

    self.clasificar_preview_stage.setText("CV seleccionado")
    self.clasificar_preview_counter.setText(f"{idx + 1}/{total}")
    self.clasificar_preview_title.setText(nombre)
    self.clasificar_preview_meta.setText(f"Sugerencia OVEUN · {_categoria_corta_clasificacion(categoria)}")
    self.clasificar_preview_destination.setText(destino)
    self.clasificar_preview_hint.setText("Doble clic en la tarjeta para corregir la categoria.")
    _aplicar_estilo_chip(self.clasificar_preview_badge, categoria.replace("_", " "), color)
    _actualizar_chips_distribucion(self)


def build_classify_page(self):
    pantalla_clasificar = QtWidgets.QWidget()
    pantalla_clasificar.setObjectName("Pantalla")
    layout_clasificar = QtWidgets.QVBoxLayout(pantalla_clasificar)
    self._poner_fondo_lineas(pantalla_clasificar, "clasificar")
    layout_clasificar.setContentsMargins(18, 18, 18, 18)
    layout_clasificar.setSpacing(8)

    card_clasificar = QtWidgets.QWidget()
    card_clasificar.setObjectName("Card")
    layout_card = QtWidgets.QVBoxLayout(card_clasificar)
    layout_card.setContentsMargins(20, 20, 20, 20)
    layout_card.setSpacing(10)

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
        "Revisa el lote, ajusta la propuesta si hace falta y aplica la clasificacion desde una pantalla mas clara."
    )
    self.clasificar_subtitulo.setObjectName("SubtituloSistema")
    self.clasificar_subtitulo.setWordWrap(True)

    self.clasificar_estado = QtWidgets.QLabel(
        "Selecciona la carpeta origen para generar una propuesta automatica."
    )
    self.clasificar_estado.setObjectName("ClasificarEstado")
    self.clasificar_estado.setProperty("classifyTone", "soft")
    self.clasificar_estado.setWordWrap(True)
    self.clasificar_estado.setMinimumHeight(42)

    self.clasificar_progress_shell = QtWidgets.QWidget()
    self.clasificar_progress_shell.setObjectName("ClasificarProgressShell")
    self.clasificar_progress_shell.setProperty("classifyStage", "idle")
    self.clasificar_progress_shell.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    progress_layout = QtWidgets.QVBoxLayout(self.clasificar_progress_shell)
    progress_layout.setContentsMargins(14, 10, 14, 10)
    progress_layout.setSpacing(5)

    progress_top = QtWidgets.QHBoxLayout()
    progress_top.setContentsMargins(0, 0, 0, 0)
    progress_top.setSpacing(10)

    self.clasificar_progress_label = QtWidgets.QLabel("Lote en espera")
    self.clasificar_progress_label.setObjectName("ClasificarProgressLabel")

    self.clasificar_progress_value = QtWidgets.QLabel("Inicial")
    self.clasificar_progress_value.setObjectName("ClasificarProgressValue")
    self.clasificar_progress_value.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    progress_top.addWidget(self.clasificar_progress_label, 1)
    progress_top.addWidget(self.clasificar_progress_value, 0)

    self.clasificar_progress_bar = QtWidgets.QProgressBar()
    self.clasificar_progress_bar.setObjectName("ClasificarProgressBar")
    self.clasificar_progress_bar.setProperty("classifyStage", "idle")
    self.clasificar_progress_bar.setRange(0, 100)
    self.clasificar_progress_bar.setValue(0)
    self.clasificar_progress_bar.setTextVisible(False)
    self.clasificar_progress_bar.setFixedHeight(8)

    self.clasificar_progress_meta = QtWidgets.QLabel("Selecciona una carpeta para empezar.")
    self.clasificar_progress_meta.setObjectName("ClasificarProgressMeta")
    self.clasificar_progress_meta.setWordWrap(False)

    progress_layout.addLayout(progress_top)
    progress_layout.addWidget(self.clasificar_progress_bar)
    progress_layout.addWidget(self.clasificar_progress_meta)

    body = QtWidgets.QWidget()
    body.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
    body_layout = QtWidgets.QGridLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setHorizontalSpacing(14)
    body_layout.setVerticalSpacing(10)
    body_layout.setColumnStretch(0, 4)
    body_layout.setColumnStretch(1, 14)

    self.clasificar_box = QtWidgets.QWidget()
    self.clasificar_box.setObjectName("ClasificarPanel")
    self.clasificar_box.setProperty("classifyPanel", "control")
    self.clasificar_box.setMinimumWidth(408)
    self.clasificar_box.setMaximumWidth(428)
    self.clasificar_box.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
    clas_box_layout = QtWidgets.QVBoxLayout(self.clasificar_box)
    clas_box_layout.setContentsMargins(0, 0, 0, 0)
    clas_box_layout.setSpacing(0)

    clas_content = QtWidgets.QWidget()
    clas_content.setObjectName("ClasificarControlContent")
    clas_content_layout = QtWidgets.QVBoxLayout(clas_content)
    clas_content_layout.setContentsMargins(16, 16, 16, 16)
    clas_content_layout.setSpacing(8)

    clas_scroll = QtWidgets.QScrollArea()
    clas_scroll.setObjectName("ClasificarControlScroll")
    clas_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    clas_scroll.setWidgetResizable(True)
    clas_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    clas_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    clas_scroll.setWidget(clas_content)
    clas_scroll.setStyleSheet("background: transparent; border: none;")

    clas_box_layout.addWidget(clas_scroll)

    preview_box = QtWidgets.QWidget()
    preview_box.setObjectName("ClasificarPanel")
    preview_box.setProperty("classifyPanel", "preview")
    preview_box.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    preview_layout = QtWidgets.QVBoxLayout(preview_box)
    preview_layout.setContentsMargins(18, 18, 18, 18)
    preview_layout.setSpacing(10)

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
    self.clasificar_input_origen.setPlaceholderText("Selecciona la carpeta del lote...")
    self.clasificar_input_origen.setReadOnly(True)

    self.clasificar_btn_origen = QtWidgets.QPushButton("Elegir origen")
    self.clasificar_btn_origen.setObjectName("SideBtn")
    self.clasificar_btn_origen.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_origen.setMinimumWidth(116)

    fila_origen.addWidget(self.clasificar_input_origen, 1)
    fila_origen.addWidget(self.clasificar_btn_origen, 0)

    self.clasificar_lab_destino_auto = QtWidgets.QLabel("Destino automatico")
    self.clasificar_lab_destino_auto.setObjectName("SideSubTitle")
    self.clasificar_lab_destino_auto.setProperty("classifyLabel", "section")

    self.clasificar_destino_auto = QtWidgets.QLabel("Se calculara automaticamente al elegir la carpeta de origen.")
    self.clasificar_destino_auto.setObjectName("SideInfo")
    self.clasificar_destino_auto.setProperty("classifyHint", "soft")
    self.clasificar_destino_auto.setWordWrap(True)

    acciones_title = QtWidgets.QLabel("Acciones")
    acciones_title.setObjectName("SideSubTitle")
    acciones_title.setProperty("classifyLabel", "section")

    acciones_grid = QtWidgets.QGridLayout()
    acciones_grid.setContentsMargins(0, 0, 0, 0)
    acciones_grid.setHorizontalSpacing(8)
    acciones_grid.setVerticalSpacing(8)
    acciones_grid.setColumnStretch(0, 1)
    acciones_grid.setColumnStretch(1, 1)

    self.clasificar_btn_escaneo = QtWidgets.QPushButton("Escanear")
    self.clasificar_btn_escaneo.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_escaneo.setProperty("classifyRole", "primary")
    self.clasificar_btn_escaneo.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_escaneo.setMinimumHeight(34)
    self.clasificar_btn_escaneo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_escaneo.setToolTip("Analiza la carpeta de origen y genera una propuesta automatica.")
    self.clasificar_btn_escaneo.setStyleSheet("font-size: 11px; padding: 7px 10px;")

    self.clasificar_btn_aplicar = QtWidgets.QPushButton("Aplicar lote")
    self.clasificar_btn_aplicar.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_aplicar.setProperty("classifyRole", "accent")
    self.clasificar_btn_aplicar.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_aplicar.setEnabled(False)
    self.clasificar_btn_aplicar.setMinimumHeight(34)
    self.clasificar_btn_aplicar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_aplicar.setToolTip("Aplica la propuesta de clasificacion y mueve los CVs al destino previsto.")
    self.clasificar_btn_aplicar.setStyleSheet("font-size: 11px; padding: 7px 10px;")

    self.clasificar_btn_deshacer = QtWidgets.QPushButton("Deshacer")
    self.clasificar_btn_deshacer.setObjectName("BotonSecundario")
    self.clasificar_btn_deshacer.setProperty("classifyRole", "secondary")
    self.clasificar_btn_deshacer.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_deshacer.setEnabled(False)
    self.clasificar_btn_deshacer.setMinimumHeight(34)
    self.clasificar_btn_deshacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_deshacer.setToolTip("Revierte la ultima clasificacion aplicada.")
    self.clasificar_btn_deshacer.setStyleSheet("font-size: 11px; padding: 7px 10px;")

    self.clasificar_btn_limpiar = QtWidgets.QPushButton("Limpiar")
    self.clasificar_btn_limpiar.setObjectName("SideBtn")
    self.clasificar_btn_limpiar.setProperty("classifyRole", "ghost")
    self.clasificar_btn_limpiar.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_limpiar.setMinimumHeight(34)
    self.clasificar_btn_limpiar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    self.clasificar_btn_limpiar.setToolTip("Limpia la propuesta actual y reinicia la pantalla.")
    self.clasificar_btn_limpiar.setStyleSheet("font-size: 11px; padding: 7px 10px;")

    acciones_grid.addWidget(self.clasificar_btn_escaneo, 0, 0)
    acciones_grid.addWidget(self.clasificar_btn_aplicar, 0, 1)
    acciones_grid.addWidget(self.clasificar_btn_deshacer, 1, 0)
    acciones_grid.addWidget(self.clasificar_btn_limpiar, 1, 1)

    resumen_title = QtWidgets.QLabel("Estado del lote")
    resumen_title.setObjectName("SideSubTitle")
    resumen_title.setProperty("classifyLabel", "section")

    metrics_grid = QtWidgets.QGridLayout()
    metrics_grid.setContentsMargins(0, 0, 0, 0)
    metrics_grid.setHorizontalSpacing(6)
    metrics_grid.setVerticalSpacing(6)

    metric_total_card, self.clasificar_metric_total_value = _crear_metric_card("CVs", "violet")
    metric_categorias_card, self.clasificar_metric_categorias_value = _crear_metric_card("Areas", "soft")
    metric_listos_card, self.clasificar_metric_listos_value = _crear_metric_card("Listos", "mint")
    metric_top_card, self.clasificar_metric_top_value = _crear_metric_card("Foco", "amber")

    metrics_grid.addWidget(metric_total_card, 0, 0)
    metrics_grid.addWidget(metric_categorias_card, 0, 1)
    metrics_grid.addWidget(metric_listos_card, 1, 0)
    metrics_grid.addWidget(metric_top_card, 1, 1)

    self.clasificar_resumen = QtWidgets.QLabel(
        "Escanea un lote para ver volumen, categorias y destino sugerido antes de mover los CVs."
    )
    self.clasificar_resumen.setObjectName("ClasificarResumen")
    self.clasificar_resumen.setProperty("classifyTone", "summary")
    self.clasificar_resumen.setWordWrap(True)
    self.clasificar_resumen.setMinimumHeight(72)
    self.clasificar_resumen.setMaximumHeight(86)
    self.clasificar_resumen.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

    clas_content_layout.addWidget(self.clasificar_lab_origen)
    clas_content_layout.addLayout(fila_origen)
    clas_content_layout.addWidget(self.clasificar_lab_destino_auto)
    clas_content_layout.addWidget(self.clasificar_destino_auto)
    clas_content_layout.addWidget(acciones_title)
    clas_content_layout.addLayout(acciones_grid)
    clas_content_layout.addWidget(resumen_title)
    clas_content_layout.addLayout(metrics_grid)
    clas_content_layout.addWidget(self.clasificar_resumen)
    clas_content_layout.addStretch(1)

    preview_title = QtWidgets.QLabel("Vista previa")
    preview_title.setObjectName("SideTitle")
    preview_title.setProperty("classifyLabel", "preview")

    preview_hint = QtWidgets.QLabel(
        "Selecciona un CV para revisar la propuesta y corrige la categoria con doble clic."
    )
    preview_hint.setObjectName("SideInfo")
    preview_hint.setProperty("classifyHint", "preview")
    preview_hint.setWordWrap(True)

    self.clasificar_result_stack = QtWidgets.QStackedWidget()

    empty = QtWidgets.QWidget()
    empty.setObjectName("EmptyState")
    empty.setProperty("classifyTone", "empty")
    empty_layout = QtWidgets.QVBoxLayout(empty)
    empty_layout.setContentsMargins(16, 16, 16, 16)
    empty_layout.setSpacing(8)
    empty_layout.setAlignment(QtCore.Qt.AlignCenter)

    empty_title = QtWidgets.QLabel("Propuesta pendiente")
    empty_title.setObjectName("EmptyTitle")
    empty_title.setAlignment(QtCore.Qt.AlignCenter)
    empty_title.setProperty("classifyTone", "empty")

    empty_text = QtWidgets.QLabel(
        "Escanea el lote para ver aqui la sugerencia y el destino previsto."
    )
    empty_text.setObjectName("EmptyText")
    empty_text.setAlignment(QtCore.Qt.AlignCenter)
    empty_text.setWordWrap(True)
    empty_text.setMaximumWidth(360)
    empty_text.setProperty("classifyTone", "empty")

    hero_media = _ResponsiveHeroCard("OVEUN listo para clasificar")
    hero_media.setObjectName("ClasificarHeroMedia")
    hero_media.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    hero_media.setMinimumWidth(260)
    hero_media.setMaximumWidth(360)
    hero_media.setMinimumHeight(220)
    hero_media.setMaximumHeight(300)

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
    self.clasificar_lista.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    self.clasificar_lista.setSpacing(12)
    self.clasificar_lista.setWordWrap(True)
    self.clasificar_lista.setUniformItemSizes(False)
    self.clasificar_lista.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    self.clasificar_lista.setViewportMargins(0, 10, 0, 10)
    self.clasificar_lista.setProperty("classifySurface", "results")
    self.clasificar_lista.currentItemChanged.connect(
        lambda current, _previous: actualizar_detalle_preview_clasificacion(self, current)
    )

    results_page = QtWidgets.QWidget()
    results_page.setObjectName("ClasificarResultsPage")
    results_layout = QtWidgets.QVBoxLayout(results_page)
    results_layout.setContentsMargins(0, 0, 0, 0)
    results_layout.setSpacing(12)

    preview_meta_row = QtWidgets.QHBoxLayout()
    preview_meta_row.setContentsMargins(0, 0, 0, 0)
    preview_meta_row.setSpacing(10)

    self.clasificar_preview_stage = QtWidgets.QLabel("Propuesta activa")
    self.clasificar_preview_stage.setObjectName("ClasificarPreviewEyebrow")

    self.clasificar_preview_counter = QtWidgets.QLabel("Sin seleccion")
    self.clasificar_preview_counter.setObjectName("ClasificarPreviewCounter")
    self.clasificar_preview_counter.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    preview_meta_row.addWidget(self.clasificar_preview_stage, 1)
    preview_meta_row.addWidget(self.clasificar_preview_counter, 0)

    distribution_wrap = QtWidgets.QWidget()
    distribution_wrap.setObjectName("ClasificarDistributionRow")
    distribution_layout = QtWidgets.QHBoxLayout(distribution_wrap)
    distribution_layout.setContentsMargins(0, 0, 0, 0)
    distribution_layout.setSpacing(8)
    self.clasificar_distribution_chips = []
    for _ in range(3):
        chip = QtWidgets.QLabel("")
        chip.setObjectName("ClasificarDistributionChip")
        chip.hide()
        self.clasificar_distribution_chips.append(chip)
        distribution_layout.addWidget(chip, 0)
    distribution_layout.addStretch(1)

    self.clasificar_preview_card = QtWidgets.QWidget()
    self.clasificar_preview_card.setObjectName("ClasificarPreviewCard")
    detail_layout = QtWidgets.QVBoxLayout(self.clasificar_preview_card)
    detail_layout.setContentsMargins(18, 16, 18, 16)
    detail_layout.setSpacing(10)

    detail_head = QtWidgets.QHBoxLayout()
    detail_head.setContentsMargins(0, 0, 0, 0)
    detail_head.setSpacing(10)

    detail_text_wrap = QtWidgets.QWidget()
    detail_text_layout = QtWidgets.QVBoxLayout(detail_text_wrap)
    detail_text_layout.setContentsMargins(0, 0, 0, 0)
    detail_text_layout.setSpacing(4)

    self.clasificar_preview_title = QtWidgets.QLabel("Selecciona un CV del lote")
    self.clasificar_preview_title.setObjectName("ClasificarPreviewTitle")
    self.clasificar_preview_title.setWordWrap(True)

    self.clasificar_preview_meta = QtWidgets.QLabel("La propuesta mostrara categoria y destino antes de aplicar.")
    self.clasificar_preview_meta.setObjectName("ClasificarPreviewMeta")
    self.clasificar_preview_meta.setWordWrap(True)

    detail_text_layout.addWidget(self.clasificar_preview_title)
    detail_text_layout.addWidget(self.clasificar_preview_meta)

    self.clasificar_preview_badge = QtWidgets.QLabel("Pendiente")
    self.clasificar_preview_badge.setObjectName("ClasificarPreviewBadge")
    self.clasificar_preview_badge.setAlignment(QtCore.Qt.AlignCenter)

    detail_head.addWidget(detail_text_wrap, 1)
    detail_head.addWidget(self.clasificar_preview_badge, 0, QtCore.Qt.AlignTop)

    self.clasificar_preview_destination = QtWidgets.QLabel("Destino previsto: se actualizara al generar resultados.")
    self.clasificar_preview_destination.setObjectName("ClasificarPreviewDestination")
    self.clasificar_preview_destination.setWordWrap(True)

    self.clasificar_preview_hint = QtWidgets.QLabel("Doble clic para corregir una categoria antes de aplicar la propuesta.")
    self.clasificar_preview_hint.setObjectName("ClasificarPreviewHint")
    self.clasificar_preview_hint.setWordWrap(True)

    detail_layout.addLayout(detail_head)
    detail_layout.addWidget(self.clasificar_preview_destination)
    detail_layout.addWidget(self.clasificar_preview_hint)

    self.clasificar_result_stack.addWidget(empty)
    results_layout.addLayout(preview_meta_row)
    results_layout.addWidget(distribution_wrap)
    results_layout.addWidget(self.clasificar_preview_card)
    results_layout.addWidget(self.clasificar_lista, 1)
    self.clasificar_result_stack.addWidget(results_page)
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
    layout_card.addWidget(self.clasificar_progress_shell)
    layout_card.addWidget(body, 1)

    actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
    set_clasificar_progress_state(
        self,
        "idle",
        "Lote en espera",
        "Selecciona una carpeta para empezar.",
    )
    actualizar_detalle_preview_clasificacion(self, None)

    layout_clasificar.addWidget(card_clasificar, 1)
    return pantalla_clasificar


def actualizar_preview_clasificacion(self):
    if not hasattr(self, "clasificar_result_stack"):
        return

    if hasattr(self, "clasificar_lista") and self.clasificar_lista.count() > 0:
        self.clasificar_result_stack.setCurrentIndex(1)
        if self.clasificar_lista.currentItem() is None:
            self.clasificar_lista.setCurrentRow(0)
        actualizar_detalle_preview_clasificacion(self, self.clasificar_lista.currentItem())
    else:
        self.clasificar_result_stack.setCurrentIndex(0)
        actualizar_detalle_preview_clasificacion(self, None)
        if hasattr(self, "clasificar_hero_media") and self.clasificar_hero_media:
            self.clasificar_hero_media.refresh_display()


def actualizar_resumen_clasificacion_manual(self):
    total = len(self._clasificar_resultados)

    if total <= 0:
        self.clasificar_resumen.setText(
            "Escanea un lote para ver volumen, categorias y destino sugerido antes de mover los CVs."
        )
        actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
        _actualizar_chips_distribucion(self)
        return

    conteo = _conteo_categorias_clasificacion(self)
    destino_txt = str(self._clasificar_destino) if self._clasificar_destino else "Sin destino automatico"
    top_categoria, top_total = max(conteo.items(), key=lambda item: (item[1], item[0]))
    top_txt = _categoria_corta_clasificacion(top_categoria)

    self.clasificar_resumen.setText(
        f"{total} CVs listos. Predomina {top_txt} con {top_total}. "
        f"Destino: {destino_txt}. Revisa la propuesta antes de aplicar."
    )
    actualizar_metricas_clasificacion(
        self,
        total=total,
        categorias=len(conteo),
        preparados=total,
        top=top_txt,
    )
    _actualizar_chips_distribucion(self)


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
        self.clasificar_resumen.setText(
            "Escanea un lote para ver volumen, categorias y destino sugerido antes de mover los CVs."
        )
    if hasattr(self, "clasificar_destino_auto"):
        self.clasificar_destino_auto.setText("Se calculara automaticamente al elegir carpeta origen.")
    if hasattr(self, "clasificar_estado"):
        self.clasificar_estado.setText("Selecciona carpeta origen para generar una propuesta automatica.")
    if hasattr(self, "clasificar_btn_aplicar"):
        self.clasificar_btn_aplicar.setEnabled(False)
        self.clasificar_btn_aplicar.setText("Aplicar lote")
    if hasattr(self, "clasificar_btn_escaneo"):
        self.clasificar_btn_escaneo.setEnabled(True)
        self.clasificar_btn_escaneo.setText("Escanear")
    if hasattr(self, "clasificar_btn_origen"):
        self.clasificar_btn_origen.setEnabled(True)
    if hasattr(self, "clasificar_btn_limpiar"):
        self.clasificar_btn_limpiar.setEnabled(True)

    self._clasificar_ultimo_historial = []
    self._actualizar_estado_boton_deshacer()
    actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
    set_clasificar_progress_state(
        self,
        "idle",
        "Lote en espera",
        "Selecciona una carpeta para empezar.",
    )
    actualizar_preview_clasificacion(self)

    self._carpeta_filtro = None
    self._actualizar_resumen_carpeta()
    self.footer_contexto.setText("Carpeta: -")


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
    if hasattr(self, "clasificar_lista") and idx < self.clasificar_lista.count():
        self.clasificar_lista.setCurrentRow(idx)
    self._actualizar_resumen_clasificacion_manual()
    self.clasificar_estado.setText("Categoria actualizada manualmente.")
    set_clasificar_progress_state(
        self,
        "ready",
        "Propuesta afinada",
        "Has corregido una categoria manualmente. La propuesta esta lista para aplicar.",
    )


def clasificar_elegir_origen(self):
    carpeta = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecciona carpeta origen")
    if not carpeta:
        return

    self._clasificar_origen = Path(carpeta)
    self.clasificar_input_origen.setText(str(self._clasificar_origen))

    nombre_base = self._clasificar_origen.name.strip() or "CVs"
    self._clasificar_destino = self._clasificar_origen.parent / f"{nombre_base}_clasificados"

    if hasattr(self, "clasificar_destino_auto"):
        self.clasificar_destino_auto.setText(str(self._clasificar_destino))

    self._clasificar_resultados = []
    self._clasificar_ultimo_historial = []
    self._actualizar_estado_boton_deshacer()

    if hasattr(self, "clasificar_lista"):
        self.clasificar_lista.clear()
    if hasattr(self, "clasificar_btn_aplicar"):
        self.clasificar_btn_aplicar.setEnabled(False)

    actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
    set_clasificar_progress_state(
        self,
        "prepared",
        "Origen preparado",
        "Destino listo. Lanza el escaneo para generar la propuesta.",
    )
    actualizar_preview_clasificacion(self)
    self.clasificar_estado.setText("Carpeta origen lista. Destino automatico preparado.")
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
    actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
    actualizar_preview_clasificacion(self)

    self.clasificar_estado.setText("Iniciando escaneo...")
    self.clasificar_resumen.setText("Analizando CVs del lote...")
    self.clasificar_btn_escaneo.setEnabled(False)
    self.clasificar_btn_escaneo.setText("Escaneando...")
    self.clasificar_btn_origen.setEnabled(False)
    self.clasificar_btn_limpiar.setEnabled(False)
    set_clasificar_progress_state(
        self,
        "scanning",
        "Escaneando lote",
        "Preparando lectura del lote...",
    )

    worker = _ClassifyWorker(base=self._clasificar_origen, max_resultados=300)
    worker.signals.progress.connect(self._clasificar_on_progress)
    worker.signals.finished.connect(self._clasificar_on_finished)
    worker.signals.error.connect(self._clasificar_on_error)
    self._threadpool.start(worker)


def clasificar_on_progress(self, texto: str):
    if hasattr(self, "clasificar_estado"):
        self.clasificar_estado.setText(texto)

    ratio = _extraer_ratio_progreso(texto)
    if ratio is None:
        set_clasificar_progress_state(self, "scanning", "Escaneando lote", texto)
    else:
        current, total = ratio
        set_clasificar_progress_state(self, "scanning", "Escaneando lote", texto, current, total)


def clasificar_on_finished(self, resultados, base):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_escaneo.setText("Escanear")
    self.clasificar_btn_origen.setEnabled(True)
    self.clasificar_btn_limpiar.setEnabled(True)
    self._clasificar_resultados = list(resultados)

    self.clasificar_lista.clear()

    total = len(resultados)
    if total <= 0:
        self.clasificar_btn_aplicar.setEnabled(False)
        self.clasificar_estado.setText("Escaneo completado sin resultados.")
        self.clasificar_resumen.setText("No se detectaron CVs validos.")
        actualizar_metricas_clasificacion(self, total=0, categorias=0, preparados=0, top="--")
        set_clasificar_progress_state(
            self,
            "ready",
            "Escaneo completado",
            "No se detectaron CVs validos en la carpeta seleccionada.",
            1,
            1,
        )
        actualizar_preview_clasificacion(self)
        return

    self.clasificar_btn_aplicar.setEnabled(True)
    self._actualizar_resumen_clasificacion_manual()
    self.clasificar_estado.setText("Propuesta generada. Revisa el destino antes de aplicar.")
    set_clasificar_progress_state(
        self,
        "ready",
        "Propuesta lista",
        f"{total} CVs listos para revisar antes de aplicar.",
        total,
        total,
    )

    self._repintar_lista_clasificacion()
    if self.clasificar_lista.count() > 0:
        self.clasificar_lista.setCurrentRow(0)
    actualizar_preview_clasificacion(self)


def clasificar_on_error(self, msg: str):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_escaneo.setText("Escanear")
    self.clasificar_btn_origen.setEnabled(True)
    self.clasificar_btn_limpiar.setEnabled(True)
    self.clasificar_estado.setText(f"Error en clasificacion: {msg}")
    self.clasificar_resumen.setText("No se pudo completar el escaneo.")
    set_clasificar_progress_state(
        self,
        "error",
        "Escaneo interrumpido",
        msg,
    )
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
    self.clasificar_btn_aplicar.setText("Aplicando...")
    self.clasificar_btn_escaneo.setEnabled(False)
    self.clasificar_btn_origen.setEnabled(False)
    self.clasificar_btn_limpiar.setEnabled(False)
    self.clasificar_estado.setText("Preparando movimiento de CVs...")
    set_clasificar_progress_state(
        self,
        "applying",
        "Aplicando propuesta",
        "OVEUN esta preparando el movimiento del lote.",
    )

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
    ratio = _extraer_ratio_progreso(texto)
    if ratio is None:
        set_clasificar_progress_state(self, "applying", "Aplicando propuesta", texto)
    else:
        current, total = ratio
        set_clasificar_progress_state(self, "applying", "Aplicando propuesta", texto, current, total)


def clasificar_aplicar_on_finished(self, info: dict):
    movidos = int(info.get("movidos", 0))
    errores = int(info.get("errores", 0))
    destino = str(info.get("destino_base", ""))
    historial = list(info.get("historial", []))

    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_escaneo.setText("Escanear")
    self.clasificar_btn_aplicar.setEnabled(False)
    self.clasificar_btn_aplicar.setText("Aplicar lote")
    self.clasificar_btn_origen.setEnabled(True)
    self.clasificar_btn_limpiar.setEnabled(True)

    self._clasificar_ultimo_historial = historial
    self._actualizar_estado_boton_deshacer()
    if destino:
        self._carpeta_filtro = Path(destino)
        self._actualizar_resumen_carpeta()
        self.footer_contexto.setText(f"Carpeta: {self._carpeta_filtro}")

    clasificaciones_guardadas = 0
    for movimiento in historial:
        try:
            ruta_final = movimiento.get("destino", "")
            categoria = movimiento.get("categoria", "Otros")
            if not ruta_final:
                continue

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
    actualizar_metricas_clasificacion(
        self,
        total=movidos + errores,
        categorias=0,
        preparados=movidos,
        top="Movido",
    )
    set_clasificar_progress_state(
        self,
        "done",
        "Clasificacion aplicada",
        f"Movidos {movidos} CVs. Errores: {errores}.",
        max(movidos, 1),
        max(movidos + errores, 1),
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
    self.clasificar_btn_escaneo.setText("Escanear")
    self.clasificar_btn_aplicar.setEnabled(bool(self._clasificar_resultados))
    self.clasificar_btn_aplicar.setText("Aplicar lote")
    self.clasificar_btn_origen.setEnabled(True)
    self.clasificar_btn_limpiar.setEnabled(True)
    self.clasificar_estado.setText(f"Error aplicando clasificacion: {msg}")
    self.clasificar_resumen.setText("La propuesta sigue disponible. Revisa el mensaje y vuelve a intentarlo.")
    set_clasificar_progress_state(
        self,
        "error",
        "No se pudo aplicar la propuesta",
        msg,
    )
