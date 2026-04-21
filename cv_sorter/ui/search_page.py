from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


def build_search_page(self):
    # ------------------------------------------------------------------ #
    # PANTALLA BUSCAR                                                     #
    # ------------------------------------------------------------------ #
    pantalla_buscar = QtWidgets.QWidget()
    pantalla_buscar.setObjectName("Pantalla")
    layout_buscar = QtWidgets.QVBoxLayout(pantalla_buscar)
    self._poner_fondo_lineas(pantalla_buscar, "buscar")
    layout_buscar.setContentsMargins(18, 18, 18, 18)
    layout_buscar.setSpacing(10)
    # Card principal en BUSCAR (para que se vea moderno)
    card_buscar = QtWidgets.QWidget()
    card_buscar.setObjectName("Card")
    self._buscar_root = card_buscar
    layout_card_buscar = QtWidgets.QVBoxLayout(card_buscar)
    layout_card_buscar.setContentsMargins(16, 16, 16, 16)
    layout_card_buscar.setSpacing(12)

    # Ahora metemos todo dentro de la card
    layout_buscar.addWidget(card_buscar, 1)

    # ==========================
    # CUERPO (GRID): arriba a 2 columnas + abajo (izq | der)
    # ==========================
    body = QtWidgets.QWidget()
    grid = QtWidgets.QGridLayout(body)
    layout_card_buscar.addWidget(body, 1)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(16)
    grid.setVerticalSpacing(10)

    # Columna izquierda se estira, derecha fija
    grid.setColumnStretch(0, 1)
    grid.setColumnStretch(1, 0)

    # ---- TOP (ocupa 2 columnas) ----
    top = QtWidgets.QWidget()
    top_layout = QtWidgets.QVBoxLayout(top)
    top_layout.setContentsMargins(2, 2, 2, 2)
    top_layout.setSpacing(10)

    # Header
    header_container = QtWidgets.QWidget()
    header_layout = QtWidgets.QVBoxLayout(header_container)
    header_layout.setContentsMargins(0, 0, 0, 4)
    header_layout.setSpacing(2)

    titulo_buscar = QtWidgets.QLabel("SISTEMA DE BÚSQUEDA")
    titulo_buscar.setObjectName("TituloSistema")

    subtitulo_buscar = QtWidgets.QLabel("Análisis inteligente por palabras clave")
    subtitulo_buscar.setObjectName("SubtituloSistema")

    header_layout.addWidget(titulo_buscar)
    header_layout.addWidget(subtitulo_buscar)

    # Fila top (volver + input + buscar)
    fila_top_w = QtWidgets.QWidget()
    fila_top = QtWidgets.QHBoxLayout(fila_top_w)
    fila_top.setContentsMargins(0, 2, 0, 2)
    fila_top.setSpacing(12)

    self.buscar_volver = QtWidgets.QPushButton("Volver")
    self.buscar_volver.setObjectName("BotonSecundario")
    self.buscar_volver.setCursor(QtCore.Qt.PointingHandCursor)

    self.scope_cvs = QtWidgets.QPushButton("CVs")
    self.scope_cvs.setObjectName("ScopeChip")
    self.scope_cvs.setCursor(QtCore.Qt.PointingHandCursor)
    self.scope_cvs.setCheckable(True)
    self.scope_cvs.setChecked(True)

    self.scope_notas = QtWidgets.QPushButton("Notas")
    self.scope_notas.setObjectName("ScopeChip")
    self.scope_notas.setCursor(QtCore.Qt.PointingHandCursor)
    self.scope_notas.setCheckable(True)
    self.scope_notas.setChecked(False)

    scope_wrap = QtWidgets.QWidget()
    scope_layout = QtWidgets.QHBoxLayout(scope_wrap)
    scope_layout.setContentsMargins(0, 0, 0, 0)
    scope_layout.setSpacing(8)
    scope_layout.addWidget(self.scope_cvs)
    scope_layout.addWidget(self.scope_notas)

    self.buscar_input = QtWidgets.QLineEdit()
    self.buscar_input.setPlaceholderText("Buscar CVs (vacío = mostrar todos)")

    self.buscar_boton = QtWidgets.QPushButton("🔎 Buscar")
    self.buscar_boton.setObjectName("BotonPrimarioPequeno")
    self.buscar_boton.setCursor(QtCore.Qt.PointingHandCursor)
    self.buscar_boton.setMinimumWidth(140)
    self.buscar_boton.setFixedHeight(44)

    fila_top.addWidget(self.buscar_volver)
    fila_top.addWidget(scope_wrap, 0)
    fila_top.addWidget(self.buscar_input, 1)
    fila_top.addWidget(self.buscar_boton)

    top_layout.addWidget(header_container)
    top_layout.addWidget(fila_top_w)

    # Añadimos TOP ocupando 2 columnas
    grid.addWidget(top, 0, 0, 1, 2)

    # ---- IZQUIERDA (debajo del top) ----
    left = QtWidgets.QWidget()
    left_layout = QtWidgets.QVBoxLayout(left)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(8)

    grid.addWidget(left, 1, 0)

    # ---- DERECHA (panel acciones rápidas) ----
    right = QtWidgets.QWidget()
    right.setObjectName("SidePanel")
    right.setFixedWidth(300)

    right_layout = QtWidgets.QVBoxLayout(right)
    right_layout.setContentsMargins(14, 12, 14, 12)
    right_layout.setSpacing(8)

    # Añadimos la columna derecha al grid
    grid.addWidget(right, 1, 1)

    
    
    

    # --- Robot "peek" en BUSCAR (overlay flotante) ---
    self.robot_peek_label = QtWidgets.QLabel(card_buscar)
    self.robot_peek_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
    self.robot_peek_label.setStyleSheet("background: transparent;")
    self.robot_peek_label.hide()

    pix_peek = QtGui.QPixmap(self._asset_path("robot_peek.png"))
    if not pix_peek.isNull():
        pix_peek = pix_peek.scaled(
            120, 120,  # más pequeño para que NO tape el botón
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        self.robot_peek_label.setPixmap(pix_peek)
        self.robot_peek_label.hide()   # IMPORTANTE: no enseñarlo todavía

        # --- Ancla de manos dentro del PNG (proporciones) ---
        # Ajusta estos dos valores si no coincide perfecto
        self._peek_hand_rx = 0.50   # 0.0 izquierda — 1.0 derecha
        self._peek_hand_ry = 0.70   # 0.0 arriba — 1.0 abajo

    # Guardamos referencia para reposicionarlo bien
    
    card_buscar.installEventFilter(self)

    

    # Fila 2: Switch OR (se queda)
    fila_modo = QtWidgets.QHBoxLayout()

    # --- Selector de modo AND / OR / NOT ---
    modo_row = QtWidgets.QWidget()
    modo_layout = QtWidgets.QHBoxLayout(modo_row)
    modo_layout.setContentsMargins(0, 0, 0, 0)
    modo_layout.setSpacing(12)

    lab_modo = QtWidgets.QLabel("Modo de búsqueda:")
    lab_modo.setObjectName("ModoLabel")

    self.rb_and = QtWidgets.QRadioButton("Todas las palabras")
    self.rb_or  = QtWidgets.QRadioButton("Al menos una")
    self.rb_not = QtWidgets.QRadioButton("Excluir palabras")

    self.rb_and.setObjectName("ModoChip")
    self.rb_or.setObjectName("ModoChip")
    self.rb_not.setObjectName("ModoChip")
    for rb in (self.rb_and, self.rb_or, self.rb_not):
        rb.setAutoExclusive(True)

    # Por defecto: AND (lo más común)
    self.rb_and.setChecked(True)
    for rb in (self.rb_and, self.rb_or, self.rb_not):
        rb.setProperty("chip", True)
        rb.toggled.connect(lambda _=False, r=rb: r.style().polish(r))

    modo_layout.addWidget(lab_modo)
    modo_layout.addWidget(self.rb_and)
    modo_layout.addWidget(self.rb_or)
    modo_layout.addWidget(self.rb_not)
    modo_layout.addStretch(1)

    left_layout.addWidget(modo_row)

    # Texto explicativo (para que cualquiera entienda)
    self.modo_help = QtWidgets.QLabel("AND: debe contener todas las palabras.")
    self.modo_help.setObjectName("ModoHelp")
    self.modo_help.setWordWrap(True)
    left_layout.addWidget(self.modo_help)

    # Actualizar texto al cambiar de modo
    self.rb_and.toggled.connect(self._actualizar_modo_help)
    self.rb_or.toggled.connect(self._actualizar_modo_help)
    self.rb_not.toggled.connect(self._actualizar_modo_help)

    self.rb_and.toggled.connect(self._actualizar_resumen_modo)
    self.rb_or.toggled.connect(self._actualizar_resumen_modo)
    self.rb_not.toggled.connect(self._actualizar_resumen_modo)

    # Estado / resultado
    self.buscar_estado = QtWidgets.QLabel("")
    self.buscar_estado.setWordWrap(True)
    left_layout.addWidget(self.buscar_estado)

    # --- Barra resumen (empresa: claridad) ---
    self.buscar_resumen = QtWidgets.QWidget()
    self.buscar_resumen.setObjectName("BarraResumen")
    res_layout = QtWidgets.QHBoxLayout(self.buscar_resumen)
    res_layout.setContentsMargins(12, 10, 12, 10)
    res_layout.setSpacing(10)

    self.resumen_count = QtWidgets.QLabel("0 resultados")
    self.resumen_count.setObjectName("ResumenCount")

    self.resumen_query = QtWidgets.QLabel("Búsqueda: —")
    self.resumen_query.setObjectName("Pill")

    self.resumen_modo = QtWidgets.QLabel("Modo: Todas")
    self.resumen_modo.setObjectName("Pill")

    self.resumen_scope = QtWidgets.QLabel("Buscar en: CVs")
    self.resumen_scope.setObjectName("Pill")

    self.resumen_carpeta = QtWidgets.QLabel("Carpeta: Todas")
    self.resumen_carpeta.setObjectName("Pill")

    res_layout.addWidget(self.resumen_count)
    res_layout.addStretch(1)
    res_layout.addWidget(self.resumen_query)
    res_layout.addWidget(self.resumen_modo)
    res_layout.addWidget(self.resumen_scope)
    res_layout.addWidget(self.resumen_carpeta)
    res_layout.addStretch(1)

    left_layout.addWidget(self.buscar_resumen)

    # --- Filtro por categoría ---
    self.filtro_categoria_wrap = QtWidgets.QWidget()
    self.filtro_categoria_wrap.setObjectName("HeaderLista")

    filtro_cat_layout = QtWidgets.QHBoxLayout(self.filtro_categoria_wrap)
    filtro_cat_layout.setContentsMargins(10, 6, 10, 6)
    filtro_cat_layout.setSpacing(10)

    self.lbl_filtro_categoria = QtWidgets.QLabel("Categoría")
    self.lbl_filtro_categoria.setObjectName("HeaderCol")

    self.combo_categoria = QtWidgets.QComboBox()
    self.combo_categoria.setObjectName("ComboOrden")
    self.combo_categoria.setCursor(QtCore.Qt.PointingHandCursor)
    self.combo_categoria.setFixedHeight(30)
    self.combo_categoria.setMinimumWidth(190)
    self.combo_categoria.addItems([
        "Todas",
        "IT_Programacion",
        "Ingenieria",
        "Diseno",
        "Marketing",
        "Administracion",
        "Otros",
    ])

    filtro_cat_layout.addWidget(self.lbl_filtro_categoria, 0)
    filtro_cat_layout.addWidget(self.combo_categoria, 0)
    filtro_cat_layout.addStretch(1)

    left_layout.addWidget(self.filtro_categoria_wrap)

    # --- Stack resultados: Empty (bonito) / Lista ---
    self.result_stack = QtWidgets.QStackedWidget()

    # Página 0: Empty state
    empty = QtWidgets.QWidget()
    empty.setObjectName("EmptyState")
    el = QtWidgets.QVBoxLayout(empty)
    el.setContentsMargins(18, 6, 18, 18)
    el.setSpacing(10)
    el.setAlignment(QtCore.Qt.AlignHCenter)  # quitamos AlignTop

    icon = QtWidgets.QLabel("🔍")
    icon.setAlignment(QtCore.Qt.AlignCenter)
    icon.setObjectName("EmptyIcon")

    self.empty_title = QtWidgets.QLabel("Empieza escribiendo una búsqueda")
    self.empty_title.setObjectName("EmptyTitle")
    self.empty_title.setAlignment(QtCore.Qt.AlignCenter)

    self.empty_text = QtWidgets.QLabel("Ejemplos: “python sql”, “java spring”, “react docker”.")
    self.empty_text.setObjectName("EmptyText")
    self.empty_text.setWordWrap(True)
    self.empty_text.setAlignment(QtCore.Qt.AlignCenter)

    # Contenedor del bloque (lupa + textos) para centrarlo verticalmente
    empty_block = QtWidgets.QWidget()
    empty_block_layout = QtWidgets.QVBoxLayout(empty_block)
    empty_block_layout.setContentsMargins(0, 0, 0, 0)
    empty_block_layout.setSpacing(10)
    empty_block_layout.setAlignment(QtCore.Qt.AlignHCenter)

    empty_block_layout.addWidget(icon, 0, QtCore.Qt.AlignHCenter)
    empty_block_layout.addWidget(self.empty_title, 0, QtCore.Qt.AlignHCenter)
    empty_block_layout.addWidget(self.empty_text, 0, QtCore.Qt.AlignHCenter)

    # Centrado vertical real
    el.addStretch(1)
    el.addWidget(empty_block, 0, QtCore.Qt.AlignHCenter)
    el.addStretch(1)

    self.result_stack.addWidget(empty)  # index 0

    # Lista de resultados con widgets personalizados
    self.buscar_lista = QtWidgets.QListWidget()
    self.buscar_lista.setObjectName("ListaResultados")
    self.buscar_lista.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
    self.buscar_lista.setSpacing(12)
    self.buscar_lista.setViewportMargins(0, 10, 0, 10)  # margen arriba/abajo para que no recorte
    self.buscar_lista.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

    # --- Cabecera de sección "Resultados" (como en la foto) ---
    self.resultados_header = QtWidgets.QWidget()
    self.resultados_header.setObjectName("ResultadosHeader")
    rh = QtWidgets.QHBoxLayout(self.resultados_header)
    rh.setContentsMargins(0, 6, 0, 2)
    rh.setSpacing(10)

    pill = QtWidgets.QFrame()
    pill.setObjectName("ResPill")
    pill.setFixedSize(46, 20)

    lab_res = QtWidgets.QLabel("Resultados")
    lab_res.setObjectName("ResTitle")

    rh.addWidget(pill)
    rh.addWidget(lab_res)
    rh.addStretch(1)

    left_layout.addWidget(self.resultados_header)

    # --- Header de lista (más corporativo) ---
    self.header_lista = QtWidgets.QWidget()
    self.header_lista.setObjectName("HeaderLista")

    hl = QtWidgets.QHBoxLayout(self.header_lista)
    hl.setContentsMargins(10, 6, 10, 6)
    hl.setSpacing(10)

    lab_archivo = QtWidgets.QLabel("Archivo")
    lab_archivo.setObjectName("HeaderCol")

    self.combo_orden = QtWidgets.QComboBox()
    self.combo_orden.setObjectName("ComboOrden")
    self.combo_orden.addItems([
        "Más recientes primero",
        "Más antiguos primero",
        "Nombre A-Z",
        "Nombre Z-A",
    ])
    self.combo_orden.setCursor(QtCore.Qt.PointingHandCursor)
    self.combo_orden.setFixedHeight(30)
    self.combo_orden.setMinimumWidth(180)

    lab_acciones = QtWidgets.QLabel("Acciones")
    lab_acciones.setObjectName("HeaderCol")
    lab_acciones.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    hl.addWidget(lab_archivo, 1)
    hl.addWidget(self.combo_orden, 0)
    hl.addWidget(lab_acciones, 0)

    left_layout.addWidget(self.header_lista)

    self.result_stack.addWidget(self.buscar_lista)  # index 1
    left_layout.addWidget(self.result_stack, 1)

    self.result_stack.setCurrentIndex(0)  # estado inicial bonito

    # ==========================
    # PANEL LATERAL (DERECHA)
    # ==========================

    side_title = QtWidgets.QLabel("Acciones rápidas")
    side_title.setObjectName("SideTitle")
    right_layout.addWidget(side_title)

    self.sp_btn_carpeta = QtWidgets.QPushButton("📂 Elegir carpeta")
    self.sp_btn_carpeta.setObjectName("SideBtn")

    self.sp_btn_limpiar_filtro = QtWidgets.QPushButton("✕ Quitar filtro")
    self.sp_btn_limpiar_filtro.setObjectName("SideBtnDanger")

    self.sp_btn_limpiar_resultados = QtWidgets.QPushButton("🧹 Limpiar resultados")
    self.sp_btn_limpiar_resultados.setObjectName("SideBtn")

    right_layout.addWidget(self.sp_btn_carpeta)
    right_layout.addWidget(self.sp_btn_limpiar_filtro)
    right_layout.addWidget(self.sp_btn_limpiar_resultados)

    # --- PASO 2B.2: glow premium en botones pequeños ---
    self._aplicar_glow_boton(self.buscar_boton, QtGui.QColor(167, 139, 250, 170), blur=30, y=12)
    self._aplicar_glow_boton(self.buscar_volver, QtGui.QColor(196, 181, 253, 120), blur=22, y=10)

    self._aplicar_glow_boton(self.sp_btn_carpeta, QtGui.QColor(196, 181, 253, 110), blur=18, y=8)
    self._aplicar_glow_boton(self.sp_btn_limpiar_resultados, QtGui.QColor(196, 181, 253, 110), blur=18, y=8)
    self._aplicar_glow_boton(self.sp_btn_limpiar_filtro, QtGui.QColor(239, 68, 68, 110), blur=18, y=8)

    sep = QtWidgets.QFrame()
    sep.setFrameShape(QtWidgets.QFrame.HLine)
    sep.setObjectName("SideSep")
    right_layout.addWidget(sep)

    ex_title = QtWidgets.QLabel("Ejemplos")
    ex_title.setObjectName("SideSubTitle")
    right_layout.addWidget(ex_title)

    chips = QtWidgets.QWidget()
    chips_layout = QtWidgets.QGridLayout(chips)
    chips_layout.setContentsMargins(0, 0, 0, 0)
    chips_layout.setHorizontalSpacing(8)
    chips_layout.setVerticalSpacing(8)
    chips_layout.setColumnStretch(0, 0)
    chips_layout.setColumnStretch(1, 0)
    # Hacer que el contenedor sea compacto
    chips.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    ejemplos = ["python", "java", "sql", "react", "docker", "aws"]

    for i, txt in enumerate(ejemplos):
        b = QtWidgets.QToolButton()
        b.setText(txt)
        b.setObjectName("Chip")
        b.setCursor(QtCore.Qt.PointingHandCursor)
        b.clicked.connect(lambda _, t=txt: self._aplicar_filtro_busqueda(t))
        chips_layout.addWidget(b, i // 2, i % 2)

    right_layout.addWidget(chips)

    sep2 = QtWidgets.QFrame()
    sep2.setFrameShape(QtWidgets.QFrame.HLine)
    sep2.setObjectName("SideSep")
    right_layout.addWidget(sep2)

    st_title = QtWidgets.QLabel("Estado")
    st_title.setObjectName("SideSubTitle")
    right_layout.addWidget(st_title)

    self.sp_estado = QtWidgets.QLabel("Listo para buscar")
    self.sp_estado.setObjectName("SideInfo")
    self.sp_estado.setWordWrap(True)
    right_layout.addWidget(self.sp_estado)

    # Espacio flexible para “hueco blanco”
    right_layout.addStretch(1)

    # --- Robot corriendo (decorativo en el hueco de abajo) ---
    # --- Contenedor para que el robot “ocupe” más del hueco ---
    robot_wrap = QtWidgets.QWidget()
    robot_wrap.setObjectName("SideRobotWrap")
    robot_wrap.setFixedHeight(260)  # prueba 240–320 según te guste
    rw = QtWidgets.QVBoxLayout(robot_wrap)
    rw.setContentsMargins(0, 0, 0, 0)
    rw.setSpacing(0)
    rw.addStretch(1)

    self.sp_robot_run = QtWidgets.QLabel()
    self.sp_robot_run.setObjectName("SideRobotRun")
    self.sp_robot_run.setAlignment(QtCore.Qt.AlignCenter)
    self.sp_robot_run.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)

    pm_run = QtGui.QPixmap(self._asset_path("robot_run.png"))
    if not pm_run.isNull():
        pm_run = pm_run.scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.sp_robot_run.setPixmap(pm_run)

    rw.addWidget(self.sp_robot_run, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)

    right_layout.addWidget(robot_wrap, 0)

    

    # --- Consejo OVEUN (debajo del robot) ---
    self.sp_tip_title = QtWidgets.QLabel("🤖 Consejo OVEUN")
    self.sp_tip_title.setObjectName("SideTipTitle")
    self.sp_tip_title.setAlignment(QtCore.Qt.AlignCenter)

    self.sp_tip_text = QtWidgets.QLabel('Prueba "python sql" o activa OR para ampliar resultados.')
    self.sp_tip_text.setObjectName("SideTipText")
    self.sp_tip_text.setWordWrap(True)
    self.sp_tip_text.setAlignment(QtCore.Qt.AlignCenter)

    right_layout.addWidget(self.sp_tip_title)
    right_layout.addWidget(self.sp_tip_text)# PEGA AQUÍ EL BLOQUE VISUAL DE BUSCAR
    return pantalla_buscar

def event_filter_search(self, obj, event):
    if hasattr(self, "_buscar_root") and obj is self._buscar_root:
        if event.type() == QtCore.QEvent.Resize:
            self._actualizar_robot_peek_buscar()
            return False

    return False

def actualizar_robot_peek_buscar(self):
        if not hasattr(self, "robot_peek_label"):
            return
        if not hasattr(self, "buscar_boton"):
            return
        if not hasattr(self, "_buscar_root"):
            return

        pm = self.robot_peek_label.pixmap()
        if pm is None:
            return

        root = self._buscar_root  # card_buscar

        # Centro del botón en coordenadas del root (card_buscar)
        btn_center = self.buscar_boton.mapTo(root, self.buscar_boton.rect().center())

        # Y del TOP del botón en coordenadas del root
        boton_top = self.buscar_boton.mapTo(root, QtCore.QPoint(0, 0)).y()

        robot_w = pm.width()
        robot_h = pm.height()

        # --- Ajustes finos ---
        hands_overlap = 4   # cuanto "tocan" las manos el botón (2-8 suele ir bien)
        shift_x = 0         # mueve el robot izquierda/derecha
        shift_y = 0         # mueve el robot arriba/abajo

        # --- Ancla (manos) dentro del PNG ---
        rx = getattr(self, "_peek_hand_rx", 0.50)
        ry = getattr(self, "_peek_hand_ry", 0.78)
        hand_x = int(robot_w * rx)
        hand_y = int(robot_h * ry)

        # Queremos que (hand_x, hand_y) del robot caiga sobre el TOP del botón
        x = btn_center.x() - hand_x + shift_x
        y = (boton_top + hands_overlap) - hand_y + shift_y

        # Clamp horizontal (que no se salga)
        x = max(0, min(x, root.width() - robot_w))

        # Permitimos que asome por arriba un poco
        y = max(-robot_h // 2, min(y, root.height() - robot_h))

        self.robot_peek_label.setGeometry(x, y, robot_w, robot_h)
        self.robot_peek_label.show()
        self.robot_peek_label.raise_()