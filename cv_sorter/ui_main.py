from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

import getpass


import re
import yaml

import html



from cv_sorter.utils import ruta_recurso
from cv_sorter.ui.home_page import (
    build_home_page,
    actualizar_layout_home_responsive,
    event_filter_home,
    home_ir_a_todos_cvs,
    home_elegir_carpeta,
    actualizar_stats_home,
)

from cv_sorter.ui.home_quick_actions import (
    buscar_cvs_con_notas_desde_home,
    buscar_cvs_con_cliente_desde_home,
    obtener_cvs_con_notas,
    obtener_cvs_con_cliente,
    cargar_resultados_home_directos,
)

from cv_sorter.ui.search_page import (
    build_search_page,
    event_filter_search,
    actualizar_robot_peek_buscar,
)
from cv_sorter.ui.classify_page import (
    build_classify_page,
    actualizar_resumen_clasificacion_manual,
    actualizar_estado_boton_deshacer,
    clasificar_limpiar,
    clasificar_editar_item,
    clasificar_elegir_origen,
    clasificar_aplicar,
    clasificar_aplicar_on_progress,
    clasificar_aplicar_on_finished,
    clasificar_aplicar_on_error,
    clasificar_on_error,
    clasificar_escanear,
    clasificar_on_finished,
    clasificar_on_progress,
)

from cv_sorter.workers import (
    _ClassifyWorker,
    _ApplyClassificationWorker,
    _UndoClassificationWorker,
    _SearchWorker,
)

from cv_sorter.services.classification_service import (
    calcular_score_cv,
    guardar_clasificacion_cv,
    leer_clasificacion_cv,
    categorias,
    color_categoria,
    normalizar_categoria,
)

from cv_sorter.ui.classify_widgets import ItemClasificacionWidget

from cv_sorter.ui.result_item_widget import ItemResultado

from cv_sorter.services.notes_utils import (
    cv_desde_nota,
    resumen_desde_nota,
)

from cv_sorter.ui.search_results_logic import (
    highlight_words,
    ordenar_resultados,
    recalcular_alturas_resultados,
    pintar_resultados,
)

from cv_sorter.ui.cv_result_actions import (
    crear_o_abrir_notas,
    anadir_anotacion_con_fecha,
    gestionar_clientes_cv,
)

class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, titulo_app: str, ruta_logo: str):
        super().__init__()
   
        self.setWindowTitle(titulo_app)
        self._threadpool = QtCore.QThreadPool.globalInstance()
        self._last_palabras = []
        self._last_resultados = []
        self._last_base = None

       
        self.setMinimumSize(980, 640)

        central = QtWidgets.QWidget()
        central.setObjectName("Central")
        self.setCentralWidget(central)

       

        # --- Stack de pantallas ---
        self.stack = QtWidgets.QStackedWidget()
        self._bg_layers = {}  # fondos decorativos por pantalla

        

        # HOME
        home = build_home_page(self, ruta_logo)

        # CLASIFICAR
        pantalla_clasificar = build_classify_page(self)

        # BUSCAR
        pantalla_buscar = build_search_page(self)

       

        # Stack de pantallas
        self.stack.addWidget(home)
        self.stack.addWidget(pantalla_buscar)
        self.stack.addWidget(pantalla_clasificar)
        

        layout_main = QtWidgets.QVBoxLayout(central)
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.addWidget(self.stack)
     
        
        self.stack.setCurrentIndex(0)

        QtCore.QTimer.singleShot(0, self._ir_home)
        QtCore.QTimer.singleShot(0, self._actualizar_layout_home_responsive)
        QtCore.QTimer.singleShot(0, self._actualizar_stats_home)

        self.boton_buscar.clicked.connect(self._ir_buscar)
        self.boton_clasificar.clicked.connect(self._ir_clasificar)
        self.buscar_volver.clicked.connect(self._ir_home)
        self.clasificar_volver.clicked.connect(self._ir_home)
        self.boton_salir.clicked.connect(QtWidgets.QApplication.instance().quit)

        self.clasificar_btn_origen.clicked.connect(self._clasificar_elegir_origen)
        self.clasificar_btn_escaneo.clicked.connect(self._clasificar_escanear)
        self.clasificar_btn_aplicar.clicked.connect(self._clasificar_aplicar)
        self.clasificar_btn_deshacer.clicked.connect(self.clasificar_deshacer)
        self.clasificar_btn_limpiar.clicked.connect(self._clasificar_limpiar)
        self.clasificar_lista.itemDoubleClicked.connect(self._clasificar_editar_item)

        # HOME -> accesos rápidos funcionales
        self.chip_todos_cvs.clicked.connect(self._home_ir_a_todos_cvs)
        self.chip_con_notas.clicked.connect(self._buscar_cvs_con_notas_desde_home)
        self.chip_con_cliente.clicked.connect(self._buscar_cvs_con_cliente_desde_home)
        self.chip_elegir_carpeta.clicked.connect(self._home_elegir_carpeta)

        QtCore.QTimer.singleShot(0, self._ir_home)
        QtCore.QTimer.singleShot(0, lambda: self._mostrar_feedback_home("Panel listo", "Selecciona una carpeta para empezar"))
        
        
        self._aplicar_estilo()
        self._crear_footer()
        # ---------------------------
        # Conexiones funcionales (BUSCAR)
        # ---------------------------
        self.buscar_boton.clicked.connect(self._accion_buscar)
        self.buscar_boton.clicked.connect(self._actualizar_robot_peek_buscar)
        self.buscar_input.returnPressed.connect(self._accion_buscar)
        self.combo_orden.currentIndexChanged.connect(self._reordenar_resultados_actuales)
        self.buscar_input.textChanged.connect(self._actualizar_resumen_busqueda)
        self.scope_cvs.clicked.connect(lambda: self._set_scope_busqueda("cvs"))
        self.scope_notas.clicked.connect(lambda: self._set_scope_busqueda("notas"))
        self.combo_categoria.currentTextChanged.connect(self._on_categoria_buscar_changed)


        
        self.sp_btn_carpeta.clicked.connect(self._elegir_carpeta_buscar)
        self.sp_btn_limpiar_filtro.clicked.connect(self._limpiar_filtro_carpeta)
        self.sp_btn_limpiar_resultados.clicked.connect(self._limpiar_resultados_ui)

       
        # Estado inicial
        self._carpeta_filtro = None
        self._robot_anim = None
        self._robot_bounce_blocked = False

        self._actualizar_resumen_busqueda()
        self._actualizar_resumen_carpeta()
        self._actualizar_resumen_modo()
        self._set_scope_busqueda("cvs")
        self._clasificar_origen = None
        self._clasificar_destino = None
        self._clasificar_resultados = []
        self._clasificar_ultimo_historial = []
        self._actualizar_estado_boton_deshacer()
        self._filtro_categoria_buscar = "Todas"

        # --- FIX 3: animación lift del HomeCard ---
        self._home_card_base_pos = None
        self._home_card_anim = None
        self._home_card_hovered = False

        QtCore.QTimer.singleShot(0, self._actualizar_layout_home_responsive)

        usuario = getpass.getuser()
        self.footer_version.setText(f"{usuario} · v0.1.0")    
        

        # =========================================================
        # FONDOS (líneas lila) PARA CUALQUIER PANTALLA
        # =========================================================
    

    def _actualizar_layout_home_responsive(self):
        return actualizar_layout_home_responsive(self)

    def _poner_fondo_lineas(self, root_widget: QtWidgets.QWidget, key: str):
            """Pone el fondo de líneas en cualquier pantalla (HOME/BUSCAR/ORDENAR)."""
            if not hasattr(self, "_bg_layers"):
                self._bg_layers = {}

            lbl = QtWidgets.QLabel(root_widget)
            lbl.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
            lbl.setScaledContents(True)
            lbl.lower()  # detrás de todo

            self._bg_layers[key] = (root_widget, lbl)

            root_widget.installEventFilter(self)
            self._actualizar_fondo_lineas(key)

    def _actualizar_fondo_lineas(self, key: str):
            if not hasattr(self, "_bg_layers"):
                return
            if key not in self._bg_layers:
                return

            root_widget, lbl = self._bg_layers[key]
            if not root_widget or not lbl:
                return

            lbl.setGeometry(root_widget.rect())
            lbl.setPixmap(self._render_lineas_esquinas(root_widget.size()))
            lbl.lower()  # <-- CLAVE: asegura que el fondo queda detrás SIEMPRE
        # =========================================================
        # EVENT FILTER (ÚNICO) - resize fondos + robot
        # =========================================================

    def eventFilter(self, obj, event):
        # 1) Fondos dinámicos
        if hasattr(self, "_bg_layers"):
            for key, (root, _lbl) in self._bg_layers.items():
                if obj is root and event.type() == QtCore.QEvent.Resize:
                    self._actualizar_fondo_lineas(key)

        # 2) BUSCAR
        event_filter_search(self, obj, event)

        # 3, 4 y 5) HOME
        event_filter_home(self, obj, event)

        return super().eventFilter(obj, event)
    
    def _render_lineas_esquinas(self, size: QtCore.QSize) -> QtGui.QPixmap:
        w = max(1, size.width())
        h = max(1, size.height())

        pm = QtGui.QPixmap(w, h)
        pm.fill(QtGui.QColor("#eef2ff"))

        return pm
    
    def _set_robot_mood(self, mood: str, look_left: bool = False):
        faces = {
            "idle": "🙂",
            "buscar": "🤓",
            "salir": "🥺",
        }

        emoji = faces.get(mood, "🙂")

        # Emoji en el pecho (si existe)
        if hasattr(self, "robot_chest"):
            self.robot_chest.setText(emoji)

        # Guardamos hacia dónde mira para espejar la posición del pecho
        self._robot_look_left = look_left

        # Flip SIN acumular: siempre desde el original precomputado
        if hasattr(self, "_robot_pix_original"):
            if look_left and hasattr(self, "_robot_pix_flipped"):
                self.robot_home_label.setPixmap(self._robot_pix_flipped)
            else:
                self.robot_home_label.setPixmap(self._robot_pix_original)

        # Recolocar el pecho después de cambiar pixmap
        QtCore.QTimer.singleShot(0, self._posicionar_robot_chest)

            

                    

        

    def _robot_bounce(self):
        """Bounce suave, con cooldown y sin acumular animaciones."""
        if not hasattr(self, "robot_home_label"):
            return

        # Cooldown: evita spam al pasar rápido por botones
        if getattr(self, "_robot_bounce_blocked", False):
            return
        self._robot_bounce_blocked = True
        QtCore.QTimer.singleShot(160, lambda: setattr(self, "_robot_bounce_blocked", False))

        w = self.robot_home_label
        start = w.pos()
        up = QtCore.QPoint(start.x(), start.y() - 3)  # menos movimiento (antes -6)

        # Si ya hay una animación, la paramos para que no se "buguee"
        anim_prev = getattr(self, "_robot_anim", None)
        if anim_prev is not None:
            anim_prev.stop()

        anim = QtCore.QPropertyAnimation(w, b"pos", self)
        anim.setDuration(260)  # más lento (antes 180)
        anim.setStartValue(start)
        anim.setKeyValueAt(0.5, up)
        anim.setEndValue(start)
        anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self._robot_anim = anim
        anim.start()

    def _posicionar_robot_chest(self):
        if not hasattr(self, "robot_home_label") or not hasattr(self, "robot_chest"):
            return

        w = self.robot_home_label.width()
        h = self.robot_home_label.height()
        if w <= 0 or h <= 0:
            return

        # Usamos las variables configurables
        base_rx = getattr(self, "_chest_rx", 0.52)
        base_ry = getattr(self, "_chest_ry", 0.56)

        look_left = getattr(self, "_robot_look_left", False)
        rx = (1.0 - base_rx) if look_left else base_rx

        cx = int(w * rx)
        cy = int(h * base_ry)

       # Posición dentro del label
        x_in_label = cx - self.robot_chest.width() // 2
        y_in_label = cy - self.robot_chest.height() // 2

        # Convertir a coordenadas del parent actual (RobotLayer)
        parent = self.robot_chest.parentWidget()
        pt = self.robot_home_label.mapTo(parent, QtCore.QPoint(x_in_label, y_in_label))

        self.robot_chest.move(pt)
        self.robot_chest.raise_()

        # Colocar reactor detrás del chest (mismo centro)
        if hasattr(self, "robot_reactor"):
            cx = pt.x() + (self.robot_chest.width() // 2)
            cy = pt.y() + (self.robot_chest.height() // 2)

            rw = self.robot_reactor.width()
            rh = self.robot_reactor.height()
            self.robot_reactor.move(cx - rw // 2, cy - rh // 2)

            # MUY IMPORTANTE:
            self.robot_reactor.stackUnder(self.robot_chest)

           # NO pises el color/alpha: eso lo anima el pulso
            s = self.robot_reactor.width()
            ss = self.robot_reactor.styleSheet()
            # si no tiene border-radius actualizado, lo actualizamos sin tocar el rgba
            if "border-radius" not in ss:
                self.robot_reactor.setStyleSheet(ss + f"; border-radius: {s//2}px;")

    

    def _debug_reactor(self):
        return

    def _asset_path(self, filename: str) -> str:
        return str(ruta_recurso(f"assets/{filename}"))
    
    def _reset_opacity_stack(self):
        if not hasattr(self, "stack"):
            return
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            eff = w.graphicsEffect()
            if isinstance(eff, QtWidgets.QGraphicsOpacityEffect):
                eff.setOpacity(1.0)
    
    def _transition_to(self, index: int):
        """Cambio de pantalla estable (sin QGraphicsOpacityEffect)."""
        if not hasattr(self, "stack"):
            return

        # Limpia cualquier opacity effect que se haya quedado enganchado
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            eff = w.graphicsEffect()
            if isinstance(eff, QtWidgets.QGraphicsOpacityEffect):
                w.setGraphicsEffect(None)

        self.stack.setCurrentIndex(index)
    
        
    def _ir_home(self):
        self._reset_opacity_stack()
        self._transition_to(0)

        home_w = self.stack.widget(0)
        home_w.setGraphicsEffect(None)
        home_w.show()
        home_w.raise_()

        if hasattr(self, "home_wrapper") and self.home_wrapper:
            self.home_wrapper.raise_()

        if hasattr(self, "home_shell") and self.home_shell:
            self.home_shell.raise_()

        if hasattr(self, "home_card") and self.home_card:
            self.home_card.raise_()

        if hasattr(self, "robot_layer_home") and self.robot_layer_home:
            self.robot_layer_home.raise_()

        if hasattr(self, "robot_home_label") and self.robot_home_label:
            self.robot_home_label.raise_()

        if hasattr(self, "robot_reactor") and self.robot_reactor:
            self.robot_reactor.raise_()

        if hasattr(self, "robot_chest") and self.robot_chest:
            self.robot_chest.raise_()

        QtCore.QTimer.singleShot(0, self._actualizar_layout_home_responsive)

        self.footer_estado.setText("Listo")
        self.footer_contexto.setText("Carpeta: —")
        QtCore.QTimer.singleShot(0, self._actualizar_stats_home)
    
    def _categoria_visible_cv(self, ruta_cv: str | Path) -> str:
        data = self._leer_clasificacion_cv(ruta_cv)
        categoria = str(data.get("categoria", "")).strip()

        if not categoria:
            return ""

        return self._normalizar_categoria_clasificacion(categoria)
    
    def _score_visible_cv(self, ruta_cv: str | Path) -> int:
        data = self._leer_clasificacion_cv(ruta_cv)
        try:
            return int(data.get("score", 0))
        except Exception:
            return 0
    
    def _texto_destino_previsto(self, categoria: str, nombre: str) -> str:
        if not self._clasificar_destino:
            return ""

        txt = str(Path(self._clasificar_destino) / categoria / nombre)

        if len(txt) > 120:
            txt = txt[:117] + "..."

        return txt
    
    def _repintar_lista_clasificacion(self):
        if not hasattr(self, "clasificar_lista"):
            return

        self.clasificar_lista.clear()

        for idx, r in enumerate(self._clasificar_resultados):
            nombre = r.get("nombre", "Sin nombre")
            categoria = self._normalizar_categoria_clasificacion(r.get("categoria", "Otros"))
            destino_previsto = self._texto_destino_previsto(categoria, nombre)
            color = self._color_categoria_clasificacion(categoria)

            widget = ItemClasificacionWidget(
                nombre=nombre,
                categoria=categoria,
                destino=destino_previsto or "—",
                color_categoria=color,
            )

            item = QtWidgets.QListWidgetItem()
            item.setData(QtCore.Qt.UserRole, idx)
            item.setToolTip(
                f"Archivo: {nombre}\n"
                f"Categoría: {categoria}\n"
                f"Destino: {destino_previsto or '—'}"
            )

            self.clasificar_lista.addItem(item)
            self.clasificar_lista.setItemWidget(item, widget)

            widget.editar_clicked.connect(lambda _=False, it=item: self._clasificar_editar_item(it))

            widget.adjustSize()
            item.setSizeHint(widget.sizeHint())
            QtCore.QTimer.singleShot(0, self._recalcular_alturas_clasificacion)

    def _recalcular_alturas_clasificacion(self):
        if not hasattr(self, "clasificar_lista"):
            return

        for row in range(self.clasificar_lista.count()):
            item = self.clasificar_lista.item(row)
            w = self.clasificar_lista.itemWidget(item)
            if w is None:
                continue

            w.adjustSize()
            item.setSizeHint(w.sizeHint())

        self.clasificar_lista.doItemsLayout()
        self.clasificar_lista.updateGeometries()
        self.clasificar_lista.viewport().update()

    def clasificar_deshacer(self):
        self.clasificar_estado.setText("Click en deshacer detectado...")

        total_historial = len(self._clasificar_ultimo_historial or [])
        if total_historial <= 0:
            QtWidgets.QMessageBox.warning(
                self,
                "Sin historial disponible",
                "No hay ninguna clasificación reciente que se pueda revertir."
            )
            self.clasificar_estado.setText("No hay historial para deshacer.")
            return

        respuesta = QtWidgets.QMessageBox.question(
            self,
            "Confirmar reversión",
            (
                f"Se va a intentar restaurar {total_historial} CVs a su ubicación original.\n\n"
                "También se eliminarán los metadatos de clasificación asociados y, si quedan carpetas vacías, se limpiarán automáticamente.\n\n"
                "¿Quieres continuar?"
            ),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if respuesta != QtWidgets.QMessageBox.Yes:
            self.clasificar_estado.setText("Deshacer cancelado por el usuario.")
            return

        self.clasificar_btn_deshacer.setEnabled(False)
        self.clasificar_btn_aplicar.setEnabled(False)
        self.clasificar_btn_escaneo.setEnabled(False)
        self.clasificar_estado.setText("Preparando reversión de la clasificación...")

        worker = _UndoClassificationWorker(
            self._clasificar_ultimo_historial,
            carpeta_raiz=self._clasificar_destino
        )
        worker.signals.progress.connect(self._clasificar_deshacer_on_progress)
        worker.signals.finished.connect(self._clasificar_deshacer_on_finished)
        worker.signals.error.connect(self._clasificar_deshacer_on_error)

        self._threadpool.start(worker)
    

    def _clasificar_deshacer_on_progress(self, texto: str):
        self.clasificar_estado.setText(texto)

    def _clasificar_deshacer_on_finished(self, info: dict):
        restaurados = int(info.get("restaurados", 0))
        errores = int(info.get("errores", 0))
        carpetas_borradas = list(info.get("carpetas_borradas", []) or [])
        carpeta_raiz = str(info.get("carpeta_raiz", "") or "").strip()

        self.clasificar_btn_escaneo.setEnabled(True)
        self.clasificar_btn_aplicar.setEnabled(False)

        texto_estado = f"Reversión completada · Restaurados: {restaurados} · Errores: {errores}"
        if carpetas_borradas:
            texto_estado += f" · Carpetas limpiadas: {len(carpetas_borradas)}"

        self.clasificar_estado.setText(texto_estado)

        texto_resumen = f"Restaurados: {restaurados} · Errores: {errores}"
        if carpetas_borradas:
            texto_resumen += f" · Carpetas vacías eliminadas: {len(carpetas_borradas)}"

        self.clasificar_resumen.setText(texto_resumen)

        mensaje = (
            "La última clasificación se ha revertido correctamente.\n\n"
            f"CVs restaurados: {restaurados}\n"
            f"Errores: {errores}"
        )

        if carpetas_borradas:
            mensaje += f"\nCarpetas vacías eliminadas: {len(carpetas_borradas)}"

        if carpeta_raiz and carpeta_raiz in carpetas_borradas:
            mensaje += "\nLa carpeta raíz de clasificación también se eliminó porque quedó vacía."

        QtWidgets.QMessageBox.information(
            self,
            "Reversión completada",
            mensaje
        )

        self._clasificar_ultimo_historial = []
        self._actualizar_estado_boton_deshacer()
        self.clasificar_lista.clear()
        self._clasificar_resultados = []

    def _clasificar_deshacer_on_error(self, msg: str):
        self.clasificar_btn_escaneo.setEnabled(True)
        self._actualizar_estado_boton_deshacer()
        self.clasificar_estado.setText(f"Error al deshacer: {msg}")

        QtWidgets.QMessageBox.critical(
            self,
            "Error al revertir la clasificación",
            f"No se pudo completar la reversión.\n\nDetalle:\n{msg}"
        )

    def _ir_clasificar(self):
        self._reset_opacity_stack()
        self._transition_to(2)

        clas_w = self.stack.widget(2)
        clas_w.setGraphicsEffect(None)
        clas_w.show()
        clas_w.raise_()

        if hasattr(self, "clasificar_hero_media") and self.clasificar_hero_media:
            QtCore.QTimer.singleShot(0, self.clasificar_hero_media.refresh_display)
            QtCore.QTimer.singleShot(120, self.clasificar_hero_media.refresh_display)

        self.footer_estado.setText("Modo clasificar")
        carpeta = str(self._clasificar_origen) if self._clasificar_origen else "—"
        self.footer_contexto.setText(f"Carpeta: {carpeta}")

    

    def _ir_buscar(self):
        self._reset_opacity_stack()
        self._transition_to(1)

        buscar_w = self.stack.widget(1)
        buscar_w.setGraphicsEffect(None)
        buscar_w.show()
        buscar_w.raise_()

        # Asegura que el contenido está por encima del fondo
        if hasattr(self, "_buscar_root") and self._buscar_root:
            self._buscar_root.raise_()
            self.footer_estado.setText("En búsqueda")
            carpeta = str(self._carpeta_filtro) if self._carpeta_filtro else "—"
            self.footer_contexto.setText(f"Carpeta: {carpeta}")

        # Recolocar el robot cuando la pantalla ya tenga geometría real
        QtCore.QTimer.singleShot(0, self._actualizar_robot_peek_buscar)
        QtCore.QTimer.singleShot(80, self._actualizar_robot_peek_buscar)
        QtCore.QTimer.singleShot(180, self._actualizar_robot_peek_buscar)

    def _set_modo_busqueda(self, modo: str):
        modo = (modo or "AND").upper()
        if modo == "OR":
            self.rb_or.setChecked(True)
        elif modo == "NOT":
            self.rb_not.setChecked(True)
        else:
            self.rb_and.setChecked(True)

        self._actualizar_modo_help()

    def _contar_cvs_base(self, base: Path | None) -> int:
        if base is None or not Path(base).exists():
            return 0

        total = 0
        for p in Path(base).rglob("*"):
            try:
                if not p.is_file():
                    continue
                if p.name.lower().endswith(".notas.txt"):
                    continue
                if p.name.lower().endswith(".clientes.txt"):
                    continue
                if p.suffix.lower() in {".pdf", ".doc", ".docx", ".odt", ".rtf"}:
                    total += 1
            except Exception:
                continue
        return total
    
    # --- WRAPPERS HOME / SEARCH / CLASIFICAR ---

    def _actualizar_resumen_clasificacion_manual(self):
        return actualizar_resumen_clasificacion_manual(self)

    def _actualizar_estado_boton_deshacer(self):
        return actualizar_estado_boton_deshacer(self)
    
    def _clasificar_limpiar(self):
        return clasificar_limpiar(self)

    def _clasificar_editar_item(self, item):
        return clasificar_editar_item(self, item)

    def _clasificar_elegir_origen(self):
        return clasificar_elegir_origen(self)
    
    def _clasificar_escanear(self):
        return clasificar_escanear(self)

    def _clasificar_on_progress(self, texto: str):
        return clasificar_on_progress(self, texto)

    def _clasificar_on_finished(self, resultados, base):
        return clasificar_on_finished(self, resultados, base)

    def _clasificar_on_error(self, msg: str):
        return clasificar_on_error(self, msg)
    
    def _clasificar_aplicar(self):
        return clasificar_aplicar(self)

    def _clasificar_aplicar_on_progress(self, texto: str):
        return clasificar_aplicar_on_progress(self, texto)

    def _clasificar_aplicar_on_finished(self, info: dict):
        return clasificar_aplicar_on_finished(self, info)

    def _clasificar_aplicar_on_error(self, msg: str):
        return clasificar_aplicar_on_error(self, msg)

    def _normalizar_categoria_clasificacion(self, categoria: str) -> str:
        return normalizar_categoria(categoria)


    def _categorias_clasificacion(self) -> list[str]:
        return categorias()


    def _color_categoria_clasificacion(self, categoria: str) -> QtGui.QColor:
        return color_categoria(categoria)


    def _calcular_score_cv(self, ruta_cv: str | Path) -> int:
        return calcular_score_cv(ruta_cv)


    def _guardar_clasificacion_cv(self, ruta_cv: str | Path, categoria: str, origen: str = "auto") -> bool:
        return guardar_clasificacion_cv(ruta_cv, categoria, origen)


    def _leer_clasificacion_cv(self, ruta_cv: str | Path) -> dict:
        return leer_clasificacion_cv(ruta_cv)


    def _ruta_clasificacion_cv(self, ruta_cv: str | Path) -> Path:
        from cv_sorter.services.classification_service import ruta_clasificacion_cv
        return ruta_clasificacion_cv(ruta_cv)
    
    def _highlight_words(self, text: str, words: list[str]) -> str:
        return highlight_words(self, text, words)


    def _ordenar_resultados(self, encontrados: list[Path]) -> list[Path]:
        return ordenar_resultados(self, encontrados)


    def _recalcular_alturas_resultados(self):
        return recalcular_alturas_resultados(self)


    def _pintar_resultados(self, encontrados, base: Path):
        return pintar_resultados(self, encontrados, base)
    
    def _crear_o_abrir_notas(self, ruta_cv: str):
        return crear_o_abrir_notas(self, ruta_cv)


    def _anadir_anotacion_con_fecha(self, ruta_cv: str):
        return anadir_anotacion_con_fecha(self, ruta_cv)


    def _gestionar_clientes_cv(self, ruta_cv: str):
        return gestionar_clientes_cv(self, ruta_cv)
    
    def _buscar_cvs_con_notas_desde_home(self):
        return buscar_cvs_con_notas_desde_home(self)


    def _buscar_cvs_con_cliente_desde_home(self):
        return buscar_cvs_con_cliente_desde_home(self)


    def _obtener_cvs_con_notas(self) -> list[Path]:
        return obtener_cvs_con_notas(self)


    def _obtener_cvs_con_cliente(self) -> list[Path]:
        return obtener_cvs_con_cliente(self)


    def _cargar_resultados_home_directos(self, resultados: list[Path], scope: str = "cvs"):
        return cargar_resultados_home_directos(self, resultados, scope)
    


    def _buscar_desde_home(self, texto: str, modo: str = "AND"):
        """Abre la pantalla Buscar, rellena el input y lanza la búsqueda."""
        self._ir_buscar()
        self.buscar_input.setText(texto)
        self.buscar_input.setFocus()
        self._set_modo_busqueda(modo)

        # esperamos un ciclo para que la pantalla ya esté visible
        QtCore.QTimer.singleShot(0, self._accion_buscar)    

        # Reposicionar peek después del cambio (un pelín más fiable)
        QtCore.QTimer.singleShot(120, self._actualizar_robot_peek_buscar)
        QtCore.QTimer.singleShot(220, self._actualizar_robot_peek_buscar)

        self._actualizar_consejo_oveun("no_query")

    def _home_base_actual(self) -> Path | None:
        base_raw = getattr(self, "_carpeta_filtro", None) or getattr(self, "_last_base", None)
        if not base_raw:
            return None

        try:
            base = Path(base_raw)
        except Exception:
            return None

        if not base.exists() or not base.is_dir():
            return None

        return base

    def _mostrar_feedback_home(self, titulo: str, detalle: str = ""):
        if not hasattr(self, "home_hint"):
            return

        texto = (titulo or "").strip()
        detalle = (detalle or "").strip()

        if detalle:
            texto = f"{texto} · {detalle}"

        self.home_hint.setText(texto)
        self.home_hint.setVisible(bool(texto))

    def _actualizar_contexto_home(self):
        if not hasattr(self, "home_context_text"):
            return

        base = self._home_base_actual()

        if base is None:
            self.home_context_text.setText("Sin carpeta activa")
            self.home_context_meta.setText("Selecciona una carpeta para activar accesos y estadísticas.")
            return

        self.home_context_text.setText(f"Carpeta activa: {base.name}")
        self.home_context_meta.setText(str(base))

    def _actualizar_estado_accesos_home(self):
        base = self._home_base_actual()
        hay_base = base is not None

        chips_dependientes = []
        for nombre in ("chip_todos_cvs", "chip_con_notas", "chip_con_cliente"):
            chip = getattr(self, nombre, None)
            if chip is not None:
                chips_dependientes.append(chip)

        for chip in chips_dependientes:
            chip.setEnabled(hay_base)
            chip.setProperty("disabledSoft", not hay_base)
            chip.style().unpolish(chip)
            chip.style().polish(chip)

        if hasattr(self, "chip_elegir_carpeta"):
            self.chip_elegir_carpeta.setEnabled(True)

    def _actualizar_stats_home(self):
        base = self._home_base_actual()

        total = 0
        con_notas = 0
        con_cliente = 0

        if base is not None:
            for p in base.rglob("*"):
                try:
                    if not p.is_file():
                        continue

                    nombre = p.name.lower()
                    if nombre.endswith(".notas.txt") or nombre.endswith(".clientes.txt"):
                        continue

                    if p.suffix.lower() not in {".pdf", ".doc", ".docx", ".odt", ".rtf"}:
                        continue

                    total += 1

                    ruta_notas = p.with_suffix(p.suffix + ".notas.txt")
                    if ruta_notas.exists():
                        try:
                            if ruta_notas.read_text(encoding="utf-8").strip():
                                con_notas += 1
                        except Exception:
                            pass

                    ruta_clientes = p.with_suffix(p.suffix + ".clientes.txt")
                    if ruta_clientes.exists():
                        try:
                            if ruta_clientes.read_text(encoding="utf-8").strip():
                                con_cliente += 1
                        except Exception:
                            pass

                except Exception:
                    continue

        if hasattr(self, "stat_total_num"):
            self.stat_total_num.setText(str(total))
        if hasattr(self, "stat_notas_num"):
            self.stat_notas_num.setText(str(con_notas))
        if hasattr(self, "stat_cliente_num"):
            self.stat_cliente_num.setText(str(con_cliente))

        self._actualizar_contexto_home()
        self._actualizar_estado_accesos_home()

    def _home_ir_a_todos_cvs(self):
        return home_ir_a_todos_cvs(self)

    def _home_elegir_carpeta(self):
        return home_elegir_carpeta(self)
    
    def _actualizar_robot_peek_buscar(self):
        return actualizar_robot_peek_buscar(self)
    
    def _crear_footer(self):
            sb = self.statusBar()
            sb.setSizeGripEnabled(False)

            # 3 textos del footer (izq, centro, derecha)
            self.footer_estado = QtWidgets.QLabel("Listo")
            self.footer_contexto = QtWidgets.QLabel("Carpeta: —")
            self.footer_version = QtWidgets.QLabel("v0.1.0")

            # Colocación en la barra
            sb.addWidget(self.footer_estado, 1)          # izquierda
            sb.addWidget(self.footer_contexto, 3)        # centro
            sb.addPermanentWidget(self.footer_version)   # derecha

            # Estilo (sutil)
            sb.setStyleSheet("""
            QStatusBar {
                background: rgba(255,255,255,0.55);
                border-top: 1px solid rgba(139, 92, 246, 0.18);
            }
            QStatusBar QLabel {
                color: rgba(17, 24, 39, 0.68);   /* texto más legible */
                font-size: 11px;
                font-weight: 800;
                padding: 2px 12px;
            }
        """)


    def _aplicar_glow_boton(self, w: QtWidgets.QWidget,
                        color: QtGui.QColor,
                        blur: int = 26,
                        y: int = 10):
        eff = QtWidgets.QGraphicsDropShadowEffect(w)
        eff.setBlurRadius(blur)
        eff.setOffset(0, y)
        eff.setColor(color)
        w.setGraphicsEffect(eff)  

    
    def _animar_home_card_lift(self, entrar: bool):
        # Desactivado: estaba rompiendo el layout de HOME
        return

    def _animar_boton_buscar_hover(self, entrar: bool):
        if not hasattr(self, "boton_buscar") or self.boton_buscar is None:
            return
        if not hasattr(self, "_buscar_btn_shadow") or self._buscar_btn_shadow is None:
            return

        boton = self.boton_buscar
        shadow = self._buscar_btn_shadow

        if self._buscar_btn_base_pos is None:
            self._buscar_btn_base_pos = boton.pos()

        if self._buscar_btn_anim is not None:
            self._buscar_btn_anim.stop()

        start = 0.0 if entrar else 1.0
        end = 1.0 if entrar else 0.0

        y_lift = 3
        blur_from, blur_to = 30, 40
        off_from, off_to = 10, 14
        alpha_from, alpha_to = 145, 190

        anim = QtCore.QVariantAnimation(self)
        anim.setDuration(140)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        def on_value(v):
            t = float(v)
            base = self._buscar_btn_base_pos

            boton.move(base.x(), base.y() - int(y_lift * t))

            blur = blur_from + (blur_to - blur_from) * t
            offy = off_from + (off_to - off_from) * t
            alpha = int(alpha_from + (alpha_to - alpha_from) * t)

            shadow.setBlurRadius(blur)
            shadow.setOffset(0, offy)
            shadow.setColor(QtGui.QColor(167, 139, 250, alpha))

        def on_finished():
            base = self._buscar_btn_base_pos
            if entrar:
                boton.move(base.x(), base.y() - y_lift)
                shadow.setBlurRadius(blur_to)
                shadow.setOffset(0, off_to)
                shadow.setColor(QtGui.QColor(167, 139, 250, alpha_to))
            else:
                boton.move(base.x(), base.y())
                shadow.setBlurRadius(blur_from)
                shadow.setOffset(0, off_from)
                shadow.setColor(QtGui.QColor(167, 139, 250, alpha_from))

        anim.valueChanged.connect(on_value)
        anim.finished.connect(on_finished)

        self._buscar_btn_anim = anim
        anim.start()
        
    def _aplicar_estilo(self):
        try:
            ruta_qss = ruta_recurso("cv_sorter/ui/styles.qss")
            self.setStyleSheet(Path(ruta_qss).read_text(encoding="utf-8"))
            print("ESTILO APLICADO")
        except Exception as e:
            print("[QSS ERROR]", e)
    
        # ---------------------------
        # FUNCIONES BUSCAR
        # ---------------------------
    def _accion_buscar(self):
        texto = self.buscar_input.text().strip()
        self._last_palabras = [p.lower() for p in texto.split() if p.strip()]

        if not texto:
            self.buscar_estado.setText("")

            if hasattr(self, "sp_estado"):
                self.sp_estado.setText("Mostrando todos...")

            self._actualizar_consejo_oveun("searching")

        self.buscar_estado.setText("")

        if hasattr(self, "sp_estado"):
            self.sp_estado.setText("Buscando...")

        self._actualizar_consejo_oveun("searching")

        import sys

        if self._carpeta_filtro:
            base = Path(self._carpeta_filtro)
        else:
            base = self._home_base_actual()

            if base is None:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Sin carpeta base",
                    "Selecciona una carpeta primero o entra desde HOME."
                )
                return

        if not base.exists():
            self.buscar_estado.setText(f"No existe la carpeta: {base}")
            if hasattr(self, "sp_estado"):
                self.sp_estado.setText("Carpeta no válida")
            return

        palabras = [p.lower() for p in texto.split() if p.strip()]

        modo = "AND"
        if hasattr(self, "rb_or") and self.rb_or.isChecked():
            modo = "OR"
        elif hasattr(self, "rb_not") and self.rb_not.isChecked():
            modo = "NOT"

        max_resultados = 150 if modo == "NOT" else 300

        scope = "cvs"
        if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
            scope = "notes"

        worker = _SearchWorker(
            base=base,
            palabras=palabras,
            modo=modo,
            search_scope=scope,
            max_resultados=max_resultados
        )
        worker.signals.finished.connect(self._on_search_finished)
        worker.signals.error.connect(self._on_search_error)

        self.buscar_boton.setEnabled(False)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self._threadpool.start(worker)

    def _actualizar_consejo_oveun(self, estado: str = "idle"):
        """Actualiza el texto del tip según contexto."""

        # Mood del robot
        if hasattr(self, "robot_chest"):
            if estado == "searching":
                self.robot_chest.setText("🤓")
            elif estado == "no_results":
                self.robot_chest.setText("🥺")
            elif estado == "has_results":
                self.robot_chest.setText("😎")
            elif estado == "cleared":
                self.robot_chest.setText("🙂")
            elif estado == "no_query":
                self.robot_chest.setText("🙂")
            else:
                self.robot_chest.setText("🙂")

        if not hasattr(self, "sp_tip_text"):
            return

        if estado == "no_query":
            self.sp_tip_text.setText('Empieza con algo como "react docker" o "java spring".')
        elif estado == "searching":
            self.sp_tip_text.setText("Analizando archivos… (tip: usa AND para ser más estricto)")
        elif estado == "no_results":
            self.sp_tip_text.setText("Sin resultados: prueba OR, usa menos palabras o cambia carpeta.")
        elif estado == "has_results":
            self.sp_tip_text.setText("Tip: abre un CV y usa Notas para guardar observaciones.")
        elif estado == "cleared":
            self.sp_tip_text.setText('Resultados limpiados. Prueba "python sql" para empezar.')
        else:
            self.sp_tip_text.setText('Prueba "python sql" o activa OR para ampliar resultados.')

    def _actualizar_modo_help(self):
        if not hasattr(self, "modo_help"):
            return

        if self.rb_and.isChecked():
            self.modo_help.setText("Busca CVs que contengan todas las palabras escritas.")
        elif self.rb_or.isChecked():
            self.modo_help.setText("Busca CVs que contengan al menos una de las palabras escritas.")
        elif self.rb_not.isChecked():
            self.modo_help.setText("Excluye CVs que contengan cualquiera de esas palabras.")

    def _actualizar_resumen_scope(self):
        if not hasattr(self, "resumen_scope"):
            return

        if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
            self.resumen_scope.setText("Buscar en: Notas")
        else:
            self.resumen_scope.setText("Buscar en: CVs")  
            

    def _actualizar_placeholder_busqueda(self):
        if not hasattr(self, "buscar_input"):
            return

        if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
            self.buscar_input.setPlaceholderText("Buscar notas (vacío = mostrar todas)")
        else:
            self.buscar_input.setPlaceholderText("Buscar CVs (vacío = mostrar todos)")

    def _actualizar_resumen_busqueda(self):
        if not hasattr(self, "resumen_query"):
            return

        texto = self.buscar_input.text().strip() if hasattr(self, "buscar_input") else ""
        if texto:
            self.resumen_query.setText(f"Búsqueda: {texto}")
        else:
            self.resumen_query.setText("Búsqueda: —")

    def _set_scope_busqueda(self, scope: str):
        scope = (scope or "cvs").lower()

        if scope == "notas":
            self.scope_notas.setChecked(True)
            self.scope_cvs.setChecked(False)
        else:
            self.scope_cvs.setChecked(True)
            self.scope_notas.setChecked(False)

        self._actualizar_resumen_scope()
        self._actualizar_placeholder_busqueda()      

    def _actualizar_resumen_carpeta(self):
        if not hasattr(self, "resumen_carpeta"):
            return

        if getattr(self, "_carpeta_filtro", None):
            self.resumen_carpeta.setText(f"Carpeta: {self._carpeta_filtro}")
        else:
            self.resumen_carpeta.setText("Carpeta: Todas")

    def _aplicar_filtro_busqueda(self, texto: str):
        self.buscar_input.setText(texto)
        self.buscar_input.setFocus()
        self._accion_buscar() 

    def _actualizar_resumen_modo(self):
        if not hasattr(self, "resumen_modo"):
            return

        if self.rb_and.isChecked():
            self.resumen_modo.setText("Modo: Todas")
        elif self.rb_or.isChecked():
            self.resumen_modo.setText("Modo: Al menos una")
        elif self.rb_not.isChecked():
            self.resumen_modo.setText("Modo: Excluir") 

            


    def _on_search_finished(self, encontrados, base):
        try:
            self._pintar_resultados(encontrados, Path(base))
        finally:
            self.buscar_boton.setEnabled(True)
            QtWidgets.QApplication.restoreOverrideCursor()

    def _on_search_error(self, msg: str):
        self.buscar_boton.setEnabled(True)
        QtWidgets.QApplication.restoreOverrideCursor()

        self.buscar_estado.setText(f"Error buscando: {msg}")

        if hasattr(self, "result_stack"):
            self.result_stack.setCurrentIndex(0)

        if hasattr(self, "sp_estado"):
            self.sp_estado.setText("Error en búsqueda")

        self._actualizar_consejo_oveun("no_results")       

    def _reordenar_resultados_actuales(self):
        if not getattr(self, "_last_resultados", None):
            return
        if not getattr(self, "_last_base", None):
            return

        self._pintar_resultados(list(self._last_resultados), Path(self._last_base))

    def _on_categoria_buscar_changed(self, texto: str):
        self._filtro_categoria_buscar = (texto or "Todas").strip() or "Todas"
        self._reordenar_resultados_actuales()

    def _elegir_carpeta_buscar(self):
        carpeta = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecciona una carpeta")
        if not carpeta:
            return
        self._carpeta_filtro = Path(carpeta)
        self.footer_contexto.setText(f"Carpeta: {self._carpeta_filtro}")
        self._actualizar_resumen_carpeta()

    def _limpiar_filtro_carpeta(self):
        self._carpeta_filtro = None
        self.footer_contexto.setText("Carpeta: —")
        self._actualizar_resumen_carpeta()

        if hasattr(self, "buscar_input"):
            self.buscar_input.clear()

        self._last_palabras = []

        if hasattr(self, "buscar_estado"):
            self.buscar_estado.setText("")

        if hasattr(self, "resumen_count"):
            self.resumen_count.setText("0 resultados")

        self._actualizar_resumen_busqueda()
        self._actualizar_resumen_modo()

        if hasattr(self, "result_stack"):
            self.result_stack.setCurrentIndex(0)

        if hasattr(self, "empty_title"):
            self.empty_title.setText("Empieza escribiendo una búsqueda")
        if hasattr(self, "empty_text"):
            self.empty_text.setText('Ejemplos: “python sql”, “java spring”, “react docker”.')

        if hasattr(self, "sp_estado"):
            self.sp_estado.setText("Filtro quitado")

        self._actualizar_consejo_oveun("cleared")

    def _limpiar_resultados_ui(self):
            self.buscar_lista.clear()
            self._last_palabras = []
            self.buscar_estado.setText("")
            self.resumen_count.setText("0 resultados")
            self._filtro_categoria_buscar = "Todas"
            if hasattr(self, "combo_categoria"):
                self.combo_categoria.blockSignals(True)
                self.combo_categoria.setCurrentText("Todas")
                self.combo_categoria.blockSignals(False)

            if hasattr(self, "result_stack"):
                self.result_stack.setCurrentIndex(0)

            if hasattr(self, "sp_estado"):
                self.sp_estado.setText("Resultados limpiados")
            
            self._actualizar_consejo_oveun("cleared")

    def _refrescar_estado_cliente_en_lista(self, ruta_cv: str):
        if not hasattr(self, "buscar_lista"):
            return

        ruta_cv = str(Path(ruta_cv))

        for row in range(self.buscar_lista.count()):
            item = self.buscar_lista.item(row)
            widget = self.buscar_lista.itemWidget(item)

            if widget is None:
                continue

            if not hasattr(widget, "ruta_cv"):
                continue

            if str(Path(widget.ruta_cv)) != ruta_cv:
                continue

            if hasattr(widget, "_tiene_clientes_registrados") and hasattr(widget, "marcar_con_clientes"):
                widget.marcar_con_clientes(widget._tiene_clientes_registrados())

    def _refrescar_estado_notas_en_lista(self, ruta_cv: str):
        if not hasattr(self, "buscar_lista"):
            return

        ruta_cv = str(Path(ruta_cv))

        for row in range(self.buscar_lista.count()):
            item = self.buscar_lista.item(row)
            widget = self.buscar_lista.itemWidget(item)

            if widget is None:
                continue

            if not hasattr(widget, "ruta_cv"):
                continue

            if str(Path(widget.ruta_cv)) != ruta_cv:
                continue

            ruta_nota = Path(ruta_cv).with_suffix(Path(ruta_cv).suffix + ".notas.txt")
            tiene_notas = ruta_nota.exists()

            if hasattr(widget, "marcar_con_notas"):
                widget.marcar_con_notas(tiene_notas)
