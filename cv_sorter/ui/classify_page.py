from __future__ import annotations

from pathlib import Path
import yaml

from PySide6 import QtCore, QtGui, QtWidgets

from cv_sorter.workers import _ApplyClassificationWorker

from cv_sorter.workers import _ClassifyWorker


def build_classify_page(self):
    # ------------------------------------------------------------------ #
    # PANTALLA CLASIFICAR                                                 #
    # ------------------------------------------------------------------ #
    pantalla_clasificar = QtWidgets.QWidget()
    pantalla_clasificar.setObjectName("Pantalla")
    layout_clasificar = QtWidgets.QVBoxLayout(pantalla_clasificar)
    self._poner_fondo_lineas(pantalla_clasificar, "clasificar")
    layout_clasificar.setContentsMargins(18, 18, 18, 18)
    layout_clasificar.setSpacing(10)

    card_clasificar = QtWidgets.QWidget()
    card_clasificar.setObjectName("Card")
    layout_card_clasificar = QtWidgets.QVBoxLayout(card_clasificar)
    layout_card_clasificar.setContentsMargins(24, 24, 24, 24)
    layout_card_clasificar.setSpacing(14)

    fila_top_clas = QtWidgets.QHBoxLayout()
    fila_top_clas.setContentsMargins(0, 0, 0, 0)
    fila_top_clas.setSpacing(10)

    self.clasificar_volver = QtWidgets.QPushButton("Volver")
    self.clasificar_volver.setObjectName("BotonSecundario")
    self.clasificar_volver.setCursor(QtCore.Qt.PointingHandCursor)

    fila_top_clas.addWidget(self.clasificar_volver, 0)
    fila_top_clas.addStretch(1)

    self.clasificar_titulo = QtWidgets.QLabel("CLASIFICAR CVS DESDE CARPETA")
    self.clasificar_titulo.setObjectName("TituloSistema")

    self.clasificar_subtitulo = QtWidgets.QLabel(
        "Nuevo modo para revisar y mover CVs automáticamente a carpetas de destino."
    )
    self.clasificar_subtitulo.setObjectName("SubtituloSistema")
    self.clasificar_subtitulo.setWordWrap(True)

    self.clasificar_estado = QtWidgets.QLabel("Selecciona la carpeta origen para generar una propuesta automática.")
    self.clasificar_estado.setObjectName("ClasificarEstado")
    self.clasificar_estado.setWordWrap(True)
    self.clasificar_estado.setMinimumHeight(54)

    self.clasificar_box = QtWidgets.QWidget()
    self.clasificar_box.setObjectName("ClasificarPanel")
    clas_box_layout = QtWidgets.QVBoxLayout(self.clasificar_box)
    clas_box_layout.setContentsMargins(20, 20, 20, 20)
    clas_box_layout.setSpacing(14)

    # -----------------------------
    # Carpeta origen
    # -----------------------------
    self.clasificar_lab_origen = QtWidgets.QLabel("Carpeta origen")
    self.clasificar_lab_origen.setObjectName("SideSubTitle")

    fila_origen = QtWidgets.QHBoxLayout()
    fila_origen.setContentsMargins(0, 0, 0, 0)
    fila_origen.setSpacing(8)

    self.clasificar_input_origen = QtWidgets.QLineEdit()
    self.clasificar_input_origen.setPlaceholderText("Selecciona la carpeta donde están los CVs a revisar...")
    self.clasificar_input_origen.setReadOnly(True)

    self.clasificar_btn_origen = QtWidgets.QPushButton("📂 Elegir origen")
    self.clasificar_btn_origen.setObjectName("SideBtn")
    self.clasificar_btn_origen.setCursor(QtCore.Qt.PointingHandCursor)

    fila_origen.addWidget(self.clasificar_input_origen, 1)
    fila_origen.addWidget(self.clasificar_btn_origen, 0)

    # -----------------------------
    # Destino automático
    # -----------------------------
    self.clasificar_lab_destino_auto = QtWidgets.QLabel("Destino automático")
    self.clasificar_lab_destino_auto.setObjectName("SideSubTitle")

    self.clasificar_destino_auto = QtWidgets.QLabel("Se calculará automáticamente al elegir carpeta origen.")
    self.clasificar_destino_auto.setObjectName("SideInfo")
    self.clasificar_destino_auto.setWordWrap(True)

    # -----------------------------
    # Acciones
    # -----------------------------
    fila_acciones_clas = QtWidgets.QHBoxLayout()
    fila_acciones_clas.setContentsMargins(0, 0, 0, 0)
    fila_acciones_clas.setSpacing(8)

    self.clasificar_btn_escaneo = QtWidgets.QPushButton("🔎 Escanear CVs")
    self.clasificar_btn_escaneo.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_escaneo.setCursor(QtCore.Qt.PointingHandCursor)

    self.clasificar_btn_aplicar = QtWidgets.QPushButton("📂 Aplicar clasificación")
    self.clasificar_btn_aplicar.setObjectName("BotonPrimarioPequeno")
    self.clasificar_btn_aplicar.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_aplicar.setEnabled(False)

    self.clasificar_btn_deshacer = QtWidgets.QPushButton("↩ Deshacer última clasificación")
    self.clasificar_btn_deshacer.setObjectName("BotonSecundario")
    self.clasificar_btn_deshacer.setCursor(QtCore.Qt.PointingHandCursor)
    self.clasificar_btn_deshacer.setEnabled(False)

    self.clasificar_btn_limpiar = QtWidgets.QPushButton("🧹 Limpiar")
    self.clasificar_btn_limpiar.setObjectName("SideBtn")
    self.clasificar_btn_limpiar.setCursor(QtCore.Qt.PointingHandCursor)

    fila_acciones_clas.addWidget(self.clasificar_btn_escaneo, 0)
    fila_acciones_clas.addWidget(self.clasificar_btn_aplicar, 0)
    fila_acciones_clas.addWidget(self.clasificar_btn_deshacer, 0)
    fila_acciones_clas.addWidget(self.clasificar_btn_limpiar, 0)
    fila_acciones_clas.addStretch(1)

    # -----------------------------
    # Resumen
    # -----------------------------
    self.clasificar_resumen = QtWidgets.QLabel("Pendiente de escaneo.")
    self.clasificar_resumen.setObjectName("ClasificarResumen")
    self.clasificar_resumen.setWordWrap(True)
    self.clasificar_resumen.setMinimumHeight(58)

    # -----------------------------
    # Lista preview
    # -----------------------------
    self.clasificar_lista = QtWidgets.QListWidget()
    self.clasificar_lista.setObjectName("ClasificarLista")
    self.clasificar_lista.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
    self.clasificar_lista.setSpacing(12)
    self.clasificar_lista.setWordWrap(True)
    self.clasificar_lista.setUniformItemSizes(False)
    self.clasificar_lista.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
    self.clasificar_lista.setViewportMargins(0, 10, 0, 10)

    clas_box_layout.addWidget(self.clasificar_lab_origen)
    clas_box_layout.addLayout(fila_origen)
    clas_box_layout.addWidget(self.clasificar_lab_destino_auto)
    clas_box_layout.addWidget(self.clasificar_destino_auto)
    clas_box_layout.addLayout(fila_acciones_clas)
    clas_box_layout.addWidget(self.clasificar_resumen)
    clas_box_layout.addWidget(self.clasificar_lista, 1)

    layout_card_clasificar.addLayout(fila_top_clas)
    layout_card_clasificar.addWidget(self.clasificar_titulo)
    layout_card_clasificar.addWidget(self.clasificar_subtitulo)
    layout_card_clasificar.addSpacing(6)
    layout_card_clasificar.addWidget(self.clasificar_estado)
    layout_card_clasificar.addWidget(self.clasificar_box, 1)

    layout_clasificar.addWidget(card_clasificar, 1)# PEGA AQUÍ EL BLOQUE VISUAL DE CLASIFICAR
    return pantalla_clasificar

def actualizar_resumen_clasificacion_manual(self):
    total = len(self._clasificar_resultados)

    if total <= 0:
        self.clasificar_resumen.setText("No hay resultados para clasificar.")
        return

    conteo = {}
    for r in self._clasificar_resultados:
        cat = self._normalizar_categoria_clasificacion(r.get("categoria", "Otros"))
        conteo[cat] = conteo.get(cat, 0) + 1

    destino_txt = str(self._clasificar_destino) if self._clasificar_destino else "Sin destino automático"
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
        self.clasificar_destino_auto.setText("Se calculará automáticamente al elegir carpeta origen.")

    if hasattr(self, "clasificar_estado"):
        self.clasificar_estado.setText("Selecciona carpeta origen para generar una propuesta automática.")

    if hasattr(self, "clasificar_btn_aplicar"):
        self.clasificar_btn_aplicar.setEnabled(False)

    self._clasificar_ultimo_historial = []
    self._actualizar_estado_boton_deshacer()

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
        "Editar categoría",
        f"Selecciona la categoría para:\n{nombre}",
        categorias,
        categorias.index(categoria_actual) if categoria_actual in categorias else 0,
        False
    )

    if not ok:
        return

    nueva_categoria = self._normalizar_categoria_clasificacion(nueva_categoria)
    self._clasificar_resultados[idx]["categoria"] = nueva_categoria

    self._repintar_lista_clasificacion()
    self._actualizar_resumen_clasificacion_manual()

    self.clasificar_estado.setText("Categoría actualizada manualmente.")

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

    self.clasificar_estado.setText("Carpeta origen seleccionada. Destino automático preparado.")
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

    self.clasificar_estado.setText("Iniciando escaneo...")
    self.clasificar_resumen.setText("Analizando CVs, espera un momento...")
    self.clasificar_btn_escaneo.setEnabled(False)

    worker = _ClassifyWorker(
        base=self._clasificar_origen,
        max_resultados=300
    )
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
        self.clasificar_resumen.setText("No se detectaron CVs válidos.")
        return

    self.clasificar_btn_aplicar.setEnabled(True)

    self._actualizar_resumen_clasificacion_manual()
    self.clasificar_estado.setText("Propuesta de clasificación generada. Revisa el destino previsto antes de aplicar.")

    self._repintar_lista_clasificacion() 

def clasificar_on_error(self, msg: str):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_estado.setText(f"Error en clasificación: {msg}")
    self.clasificar_resumen.setText("No se pudo completar el escaneo.")

def clasificar_aplicar(self):
    if not self._clasificar_resultados:
        self.clasificar_estado.setText("Primero genera una propuesta de clasificación.")
        return

    if not self._clasificar_destino:
        self.clasificar_estado.setText("No hay destino automático preparado.")
        return

    respuesta = QtWidgets.QMessageBox.question(
        self,
        "Confirmar clasificación",
        (
            f"Se van a mover {len(self._clasificar_resultados)} CVs a la carpeta de clasificación.\n\n"
            f"Destino:\n{self._clasificar_destino}\n\n"
            "Esta acción reorganizará los archivos y generará sus metadatos.\n\n"
            "¿Quieres continuar?"
        ),
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No
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
                            encoding="utf-8"
                        )
                    except Exception:
                        pass

                    clasificaciones_guardadas += 1
        except Exception:
            continue

    self.clasificar_estado.setText(
        f"Clasificación aplicada correctamente · Historial: {len(historial)} · Metadatos: {clasificaciones_guardadas}"
    )
    self.clasificar_resumen.setText(
        f"Movidos: {movidos} · Errores: {errores} · Metadatos: {clasificaciones_guardadas} · Buscar usará: {destino}"
    )

    QtWidgets.QMessageBox.information(
        self,
        "Clasificación completada",
        (
            "La clasificación se ha aplicado correctamente.\n\n"
            f"CVs movidos: {movidos}\n"
            f"Errores: {errores}\n"
            f"Elementos en historial: {len(historial)}\n"
            f"Metadatos guardados: {clasificaciones_guardadas}\n\n"
            f"Carpeta activa para Buscar:\n{destino}\n\n"
            "A continuación se abrirá la pantalla de búsqueda con esa carpeta ya seleccionada."
        )
    )

    self.clasificar_lista.clear()
    self._clasificar_resultados = []

    QtCore.QTimer.singleShot(0, self._ir_buscar)

def clasificar_aplicar_on_error(self, msg: str):
    self.clasificar_btn_escaneo.setEnabled(True)
    self.clasificar_btn_aplicar.setEnabled(bool(self._clasificar_resultados))
    self.clasificar_estado.setText(f"Error aplicando clasificación: {msg}")