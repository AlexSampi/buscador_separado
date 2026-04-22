from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path


def build_home_page(self, ruta_logo: str):
    # ------------------------------------------------------------------ #
    # HOME                                                                #
    # ------------------------------------------------------------------ #
    home = QtWidgets.QWidget()
    home.setObjectName("Pantalla")
    self.home_page_widget = home
    self.home_page_widget.installEventFilter(self)
    layout_home = QtWidgets.QVBoxLayout(home)

    self._poner_fondo_lineas(home, "home")
                                            
    # ---- Barra superior ----
    topbar = QtWidgets.QWidget()
    topbar.setObjectName("TopBar")
    top_layout = QtWidgets.QHBoxLayout(topbar)
    top_layout.setContentsMargins(10, 6, 10, 6)

    logo_small = QtWidgets.QLabel()
    logo_small.setFixedSize(32, 32)
    logo_small.setScaledContents(True)

    pix = QtGui.QPixmap(ruta_logo)
    if not pix.isNull():
        logo_small.setPixmap(pix)

    titulo_barra = QtWidgets.QLabel("OVEUN  |  Organización de CV")
    titulo_barra.setObjectName("TopBarTitle")

    top_layout.addWidget(logo_small)
    top_layout.addSpacing(10)
    top_layout.addWidget(titulo_barra)
    top_layout.addStretch()

    layout_home.addWidget(topbar)
    layout_home.addSpacing(20)
    layout_home.setSpacing(14)
    layout_home.setContentsMargins(34, 26, 34, 26)
    
    

    self.titulo = QtWidgets.QLabel("Organización de CV")
    self.titulo.setObjectName("LabelTitulo")
    self.titulo.setAlignment(QtCore.Qt.AlignCenter)

    self.subtitulo = QtWidgets.QLabel("Organiza, busca y analiza candidatos rápidamente")
    self.subtitulo.setObjectName("LabelSubtituloMain")
    self.subtitulo.setAlignment(QtCore.Qt.AlignCenter)

    self.micro = QtWidgets.QLabel("Oveun • Software & tech")
    self.micro.setObjectName("LabelSubtitulo")
    self.micro.setAlignment(QtCore.Qt.AlignCenter)

    
    layout_home.addSpacing(6)   # <-- aquí va el número
    
    layout_home.addSpacing(0)
    

    
    self.boton_buscar = QtWidgets.QPushButton("Buscar CVs")
    self.boton_clasificar = QtWidgets.QPushButton("Clasificar CVs")
    self.boton_salir = QtWidgets.QPushButton("Cerrar app")
    self.boton_salir.setProperty("variant", "small")

    

    self.boton_buscar.setObjectName("BotonPrimario")
    self.boton_clasificar.setObjectName("BotonSecundario")
    self.boton_salir.setObjectName("BotonPeligro")

    home_wrapper = QtWidgets.QWidget()
    home_wrapper.setObjectName("HomeWrapper")
    self.home_wrapper = home_wrapper
    wrapper_layout = QtWidgets.QVBoxLayout(home_wrapper)
    wrapper_layout.setContentsMargins(0, 0, 0, 0)
    wrapper_layout.setSpacing(0)
    wrapper_layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

    self.home_hero_host = QtWidgets.QWidget()
    self.home_hero_host.setSizePolicy(
        QtWidgets.QSizePolicy.Maximum,
        QtWidgets.QSizePolicy.Maximum
    )
    self.home_hero_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
    self.home_hero_layout.setContentsMargins(0, 0, 0, 0)
    self.home_hero_layout.setSpacing(0)
    self.home_hero_host.setLayout(self.home_hero_layout)

    self.home_shell = QtWidgets.QWidget()
    self.home_shell.setObjectName("HomeShell")
    self.home_shell.setMinimumWidth(0)
    self.home_shell.setSizePolicy(
        QtWidgets.QSizePolicy.Preferred,
        QtWidgets.QSizePolicy.Maximum
    )

    self.home_robot_shell = QtWidgets.QWidget()
    self.home_robot_shell.setObjectName("HomeCard")
    self.home_robot_shell.setSizePolicy(
        QtWidgets.QSizePolicy.Maximum,
        QtWidgets.QSizePolicy.Maximum
    )
    self.home_robot_shell_layout = QtWidgets.QVBoxLayout(self.home_robot_shell)
    self.home_robot_shell_layout.setContentsMargins(22, 22, 22, 22)
    self.home_robot_shell_layout.setSpacing(0)

    self.home_shell_layout = QtWidgets.QGridLayout(self.home_shell)
    self.home_shell_layout.setContentsMargins(0, 0, 0, 0)
    self.home_shell_layout.setHorizontalSpacing(0)
    self.home_shell_layout.setVerticalSpacing(0)

    self.robot_layer_home = QtWidgets.QWidget(self.home_robot_shell)
    self.robot_layer_home.setObjectName("RobotLayerHome")
    self.robot_layer_home.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
    self.robot_layer_home.setSizePolicy(
        QtWidgets.QSizePolicy.Maximum,
        QtWidgets.QSizePolicy.Maximum
    )
    self.home_robot_shell_layout.addStretch(1)
    self.home_robot_shell_layout.addWidget(
        self.robot_layer_home,
        0,
        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
    )
    self.home_robot_shell_layout.addStretch(1)

    contenedor_botones = QtWidgets.QWidget()
    contenedor_botones.setObjectName("HomeCard")
    self.home_card = contenedor_botones
    self.home_card.setMouseTracking(True)
    contenedor_botones.setMinimumWidth(0)
    contenedor_botones.setMinimumHeight(0)
    contenedor_botones.setMaximumHeight(16777215)
    contenedor_botones.setMaximumWidth(920)
    contenedor_botones.setSizePolicy(
        QtWidgets.QSizePolicy.Preferred,
        QtWidgets.QSizePolicy.Maximum
    )

    layout_botones = QtWidgets.QVBoxLayout(contenedor_botones)
    layout_botones.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

    self.home_card_shadow = QtWidgets.QGraphicsDropShadowEffect(contenedor_botones)
    self.home_card_shadow.setBlurRadius(24)
    self.home_card_shadow.setOffset(0, 0)
    self.home_card_shadow.setColor(QtGui.QColor(17, 24, 39, 52))
    contenedor_botones.setGraphicsEffect(self.home_card_shadow)

    #contenedor_botones.installEventFilter(self)

    self.home_wrapper.installEventFilter(self)
    self.boton_buscar.installEventFilter(self)
    self.boton_clasificar.installEventFilter(self)
    self.boton_salir.installEventFilter(self)

    layout_botones.setSpacing(14)
    layout_botones.setContentsMargins(34, 34, 34, 8)
    self._home_responsive_breakpoint = 980
    self._home_responsive_mode = None


    for boton in (self.boton_buscar, self.boton_clasificar):
        boton.setMinimumHeight(72)
        boton.setCursor(QtCore.Qt.PointingHandCursor)
        boton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        boton.setFixedWidth(260)

        eff = QtWidgets.QGraphicsDropShadowEffect(boton)
        eff.setBlurRadius(30)
        eff.setOffset(0, 10)
        eff.setColor(QtGui.QColor(167, 139, 250, 145))
        boton.setGraphicsEffect(eff)

    self._buscar_btn_shadow = self.boton_buscar.graphicsEffect()
    self._buscar_btn_base_pos = None
    self._buscar_btn_hovered = False
    self._buscar_btn_anim = None

    # Wrapper para centrar botones principales
    buscar_wrap = QtWidgets.QWidget()
    bw = QtWidgets.QVBoxLayout(buscar_wrap)
    bw.setContentsMargins(18, 4, 18, 2)
    bw.setSpacing(12)

    fila_botones = QtWidgets.QGridLayout()
    fila_botones.setContentsMargins(0, 0, 0, 0)
    fila_botones.setHorizontalSpacing(18)
    fila_botones.setVerticalSpacing(12)
    fila_botones.setColumnStretch(0, 1)
    fila_botones.setColumnStretch(3, 1)
    fila_botones.addWidget(self.boton_buscar, 0, 1)
    fila_botones.addWidget(self.boton_clasificar, 0, 2)
    self.home_primary_buttons_layout = fila_botones
    self._home_primary_buttons = (self.boton_buscar, self.boton_clasificar)

    bw.addLayout(fila_botones)

    layout_botones.addWidget(buscar_wrap)
    

    # La HomeCard se añade dentro de home_shell; no la metemos también en wrapper_layout

    # ===========================
    # ACCESOS RÁPIDOS HOME
    # ===========================

    self.chip_todos_cvs = QtWidgets.QPushButton("📂 Todos los CVs")
    self.chip_con_notas = QtWidgets.QPushButton("📝 Con notas")
    self.chip_con_cliente = QtWidgets.QPushButton("🏢 Con cliente")
    self.chip_elegir_carpeta = QtWidgets.QPushButton("📁 Elegir carpeta")

    for chip in (
        self.chip_todos_cvs,
        self.chip_con_notas,
        self.chip_con_cliente,
        self.chip_elegir_carpeta,
    ):
        chip.setObjectName("ChipSub")
        chip.setCursor(QtCore.Qt.PointingHandCursor)
        chip.setFixedHeight(42)
        chip.setMinimumWidth(170)
        chip.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        chip.setStyleSheet("""
            QPushButton {
                background: #ffffff;
                color: #111827;
                border: 1px solid rgba(17, 24, 39, 0.10);
                border-radius: 14px;
                padding: 0 14px;
                font-size: 12px;
                font-weight: 800;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(124, 58, 237, 0.08);
                border: 1px solid rgba(124, 58, 237, 0.35);
            }
            QPushButton:disabled {
                background: rgba(255,255,255,0.65);
                color: #9ca3af;
                border: 1px solid rgba(156,163,175,0.22);
            }
        """)

    sec_quick = QtWidgets.QWidget()
    sec_quick.setObjectName("HomeSection")
    sec_quick_l = QtWidgets.QVBoxLayout(sec_quick)
    sec_quick_l.setContentsMargins(0, 6, 0, 0)
    sec_quick_l.setSpacing(10)

    lab_quick = QtWidgets.QLabel("Accesos rápidos")
    lab_quick.setObjectName("HomeSectionTitle")
    lab_quick.setStyleSheet("""
        color: #374151;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.4px;
    """)

    self.home_contexto = QtWidgets.QFrame()
    self.home_contexto.setObjectName("HomeContextCard")
    self.home_contexto.setMinimumHeight(82)
    self.home_contexto.setStyleSheet("""
        QFrame {
            background: rgba(124, 58, 237, 0.10);
            border: 1px solid rgba(124, 58, 237, 0.28);
            border-radius: 16px;
        }
        QLabel {
            background: transparent;
            border: none;
        }
    """)

    home_context_l = QtWidgets.QHBoxLayout(self.home_contexto)
    home_context_l.setContentsMargins(14, 10, 14, 10)
    home_context_l.setSpacing(10)

    self.home_context_icon = QtWidgets.QLabel("📁")
    self.home_context_icon.setObjectName("HomeContextIcon")
    self.home_context_icon.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
    self.home_context_icon.setStyleSheet("""
        color: #7c3aed;
        font-size: 18px;
        font-weight: 900;
        background: transparent;
        border: none;
    """)

    self.home_context_text = QtWidgets.QLabel("Sin carpeta activa")
    self.home_context_text.setObjectName("HomeContextText")
    self.home_context_text.setWordWrap(True)
    self.home_context_text.setStyleSheet("""
        color: #111827;
        font-size: 14px;
        font-weight: 900;
        background: transparent;
        border: none;
    """)

    self.home_context_meta = QtWidgets.QLabel("Selecciona una carpeta para activar accesos y estadísticas.")
    self.home_context_meta.setObjectName("HomeContextMeta")
    self.home_context_meta.setWordWrap(True)
    self.home_context_meta.setStyleSheet("""
        color: #6b7280;
        font-size: 12px;
        font-weight: 600;
        background: transparent;
        border: none;
    """)

    context_col = QtWidgets.QVBoxLayout()
    context_col.setContentsMargins(0, 0, 0, 0)
    context_col.setSpacing(2)
    context_col.addWidget(self.home_context_text)
    context_col.addWidget(self.home_context_meta)

    home_context_l.addWidget(self.home_context_icon, 0, QtCore.Qt.AlignTop)
    home_context_l.addLayout(context_col, 1)

    quick_grid = QtWidgets.QGridLayout()
    quick_grid.setContentsMargins(0, 0, 0, 0)
    quick_grid.setHorizontalSpacing(10)
    quick_grid.setVerticalSpacing(10)

    quick_grid.addWidget(self.chip_todos_cvs, 0, 0)
    quick_grid.addWidget(self.chip_con_notas, 0, 1)
    quick_grid.addWidget(self.chip_con_cliente, 1, 0)
    quick_grid.addWidget(self.chip_elegir_carpeta, 1, 1)

    sec_quick_l.addWidget(lab_quick)
    sec_quick_l.addWidget(self.home_contexto)
    sec_quick_l.addLayout(quick_grid)

    layout_botones.addSpacing(10)
    layout_botones.addWidget(sec_quick)
    layout_botones.addSpacing(18)

    # ===========================
    # RESUMEN RÁPIDO HOME
    # ===========================

    resumen_wrap = QtWidgets.QWidget()
    resumen_wrap.setObjectName("HomeStatsWrap")
    resumen_layout = QtWidgets.QHBoxLayout(resumen_wrap)
    resumen_layout.setContentsMargins(0, 4, 0, 0)
    resumen_layout.setSpacing(10)

    self.stat_total = QtWidgets.QFrame()
    self.stat_total.setObjectName("HomeStatCard")
    st_total_l = QtWidgets.QVBoxLayout(self.stat_total)
    st_total_l.setContentsMargins(14, 12, 14, 12)
    st_total_l.setSpacing(2)

    self.stat_total_num = QtWidgets.QLabel("0")
    self.stat_total_num.setObjectName("HomeStatNumber")
    self.stat_total_txt = QtWidgets.QLabel("CVs detectados")
    self.stat_total_txt.setObjectName("HomeStatLabel")

    st_total_l.addWidget(self.stat_total_num)
    st_total_l.addWidget(self.stat_total_txt)

    self.stat_notas = QtWidgets.QFrame()
    self.stat_notas.setObjectName("HomeStatCard")
    st_notas_l = QtWidgets.QVBoxLayout(self.stat_notas)
    st_notas_l.setContentsMargins(14, 12, 14, 12)
    st_notas_l.setSpacing(2)

    self.stat_notas_num = QtWidgets.QLabel("0")
    self.stat_notas_num.setObjectName("HomeStatNumber")
    self.stat_notas_txt = QtWidgets.QLabel("CVs con notas")
    self.stat_notas_txt.setObjectName("HomeStatLabel")

    st_notas_l.addWidget(self.stat_notas_num)
    st_notas_l.addWidget(self.stat_notas_txt)

    self.stat_cliente = QtWidgets.QFrame()
    self.stat_cliente.setObjectName("HomeStatCard")
    st_cliente_l = QtWidgets.QVBoxLayout(self.stat_cliente)
    st_cliente_l.setContentsMargins(14, 12, 14, 12)
    st_cliente_l.setSpacing(2)

    self.stat_cliente_num = QtWidgets.QLabel("0")
    self.stat_cliente_num.setObjectName("HomeStatNumber")
    self.stat_cliente_txt = QtWidgets.QLabel("CVs con cliente")
    self.stat_cliente_txt.setObjectName("HomeStatLabel")

    st_cliente_l.addWidget(self.stat_cliente_num)
    st_cliente_l.addWidget(self.stat_cliente_txt)

    resumen_layout.addWidget(self.stat_total)
    resumen_layout.addWidget(self.stat_notas)
    resumen_layout.addWidget(self.stat_cliente)
    resumen_layout.addStretch(1)

    layout_botones.addWidget(resumen_wrap)
    layout_botones.addSpacing(6)


    sep_home = QtWidgets.QFrame()
    sep_home.setFrameShape(QtWidgets.QFrame.HLine)
    sep_home.setObjectName("HomeSep")
    layout_botones.addWidget(sep_home)

    row_bottom = QtWidgets.QHBoxLayout()
    row_bottom.setContentsMargins(0, 8, 0, 0)
    row_bottom.setSpacing(0)

    row_bottom.addStretch(1)

    self.boton_salir.setFixedHeight(44)
    self.boton_salir.setFixedWidth(150)

    row_bottom.addWidget(self.boton_salir, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

    layout_botones.addLayout(row_bottom)

    

    # --- NUEVO HERO CENTRAL (vertical + robot superpuesto) ---
    self.home_scroll = QtWidgets.QScrollArea()
    self.home_scroll.setObjectName("HomeScroll")
    self.home_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
    self.home_scroll.setWidgetResizable(True)
    self.home_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    self.home_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
    self.home_scroll.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
    self.home_scroll.viewport().setAutoFillBackground(False)
    self.home_scroll.viewport().installEventFilter(self)

    contenedor_central = QtWidgets.QWidget()
    self.home_scroll_content = contenedor_central
    layout_central = QtWidgets.QVBoxLayout(contenedor_central)
    layout_central.setContentsMargins(0, 0, 0, 0)
    layout_central.setSpacing(14)
    layout_central.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

    # Para detectar hover en los botones
    self.boton_buscar.installEventFilter(self)
    self.boton_clasificar.installEventFilter(self)
    self.boton_salir.installEventFilter(self)

    # Textos arriba
    self.titulo.setAlignment(QtCore.Qt.AlignCenter)
    self.subtitulo.setAlignment(QtCore.Qt.AlignCenter)
    self.micro.setAlignment(QtCore.Qt.AlignCenter)

    layout_central.addWidget(self.titulo, 0, QtCore.Qt.AlignCenter)
    layout_central.addWidget(self.subtitulo, 0, QtCore.Qt.AlignCenter)
    layout_central.addWidget(self.micro, 0, QtCore.Qt.AlignCenter)
    layout_central.addSpacing(8)

    # Hint final
    self.home_hint = QtWidgets.QLabel("")
    self.home_hint.setObjectName("HomeHint")
    self.home_hint.setAlignment(QtCore.Qt.AlignCenter)
    self.home_hint.setVisible(False)

    # --- ROBOT HOME en la capa del shell ---
    self.robot_home_label = QtWidgets.QLabel(self.robot_layer_home)
    self.robot_home_label.setAlignment(QtCore.Qt.AlignCenter)

    ruta_robot = self._asset_path("robot_home_welcome.png")
    pix_robot = QtGui.QPixmap(ruta_robot)

    if not pix_robot.isNull():
        self._robot_pix_original = pix_robot.scaled(
            300, 300,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )
        self._robot_pix_flipped = self._robot_pix_original.transformed(
            QtGui.QTransform().scale(-1, 1)
        )
        self.robot_home_label.setPixmap(self._robot_pix_original)

        robot_shadow = QtWidgets.QGraphicsDropShadowEffect(self.robot_home_label)
        robot_shadow.setBlurRadius(30)
        robot_shadow.setOffset(0, 10)
        robot_shadow.setColor(QtGui.QColor(17, 24, 39, 60))
        self.robot_home_label.setGraphicsEffect(robot_shadow)

    self.robot_home_label.adjustSize()
    self.robot_home_label.installEventFilter(self)

    # --- Emoji/luz del pecho (restaurado del robot antiguo) ---
    self._chest_rx = 0.66
    self._chest_ry = 0.545
    self._robot_look_left = False

    self.robot_chest = QtWidgets.QLabel()
    self.robot_chest.setObjectName("RobotChest")
    self.robot_chest.setText("🙂")
    self.robot_chest.setAlignment(QtCore.Qt.AlignCenter)
    self.robot_chest.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
    self.robot_chest.setFixedSize(80, 80)
    self.robot_chest.setStyleSheet("""
        QLabel#RobotChest {
            font-size: 36px;
            background: transparent;
            border: none;
        }
    """)
    self.robot_chest.show()

    self._reactor_base = 46
    self.robot_reactor = QtWidgets.QLabel()
    self.robot_reactor.setObjectName("RobotReactor")
    self.robot_reactor.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
    self.robot_reactor.setFixedSize(self._reactor_base, self._reactor_base)
    self.robot_reactor.setStyleSheet("background: transparent;")
    self.robot_reactor.hide()

    self._chest_pulse = QtCore.QVariantAnimation(self)
    self._chest_pulse.setDuration(1400)
    self._chest_pulse.setStartValue(0.0)
    self._chest_pulse.setEndValue(1.0)
    self._chest_pulse.setLoopCount(-1)
    self._chest_pulse.setEasingCurve(QtCore.QEasingCurve.InOutSine)

    def _pulse_value(v: float):
        t = float(v)
        alpha = 60 + int(120 * t)
        s = int(self._reactor_base + 14 * t)

        if hasattr(self, "robot_reactor"):
            self.robot_reactor.setFixedSize(s, s)
            self.robot_reactor.setStyleSheet(
                f"background-color: rgba(139, 92, 246, {alpha});"
                f"border-radius: {s//2}px;"
            )

            if hasattr(self, "robot_chest"):
                cx = self.robot_chest.x() + self.robot_chest.width() // 2
                cy = self.robot_chest.y() + self.robot_chest.height() // 2
                self.robot_reactor.move(cx - s // 2, cy - s // 2)
                self.robot_reactor.stackUnder(self.robot_chest)

    self._chest_pulse.valueChanged.connect(_pulse_value)

    self.robot_chest.setParent(self.robot_layer_home)
    self.robot_chest.show()
    self.robot_chest.raise_()

    self.robot_reactor.setParent(self.robot_layer_home)
    self.robot_reactor.show()
    self.robot_reactor.stackUnder(self.robot_chest)

    QtCore.QTimer.singleShot(0, self._posicionar_robot_chest)
    QtCore.QTimer.singleShot(0, self._chest_pulse.start)

    self.home_shell_layout.addWidget(contenedor_botones, 0, 0, QtCore.Qt.AlignCenter)
    self.robot_layer_home.raise_()

    self.home_hero_layout.addWidget(self.home_shell, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
    self.home_hero_layout.addWidget(self.home_robot_shell, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

    wrapper_layout.addWidget(self.home_hero_host, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

    layout_central.addWidget(home_wrapper, 0, QtCore.Qt.AlignHCenter)
    layout_central.addWidget(self.home_hint, 0, QtCore.Qt.AlignHCenter)

    self.home_scroll.setWidget(contenedor_central)
    layout_home.addWidget(self.home_scroll, 1)
    return home

def _aplicar_modo_home_responsive(self, compacto: bool):
        if not hasattr(self, "home_primary_buttons_layout"):
            return

        nuevo_modo = "compacto" if compacto else "grande"
        if getattr(self, "_home_responsive_mode", None) == nuevo_modo:
            return

        layout = self.home_primary_buttons_layout
        for boton in getattr(self, "_home_primary_buttons", ()):
            layout.removeWidget(boton)

        if compacto:
            for boton in getattr(self, "_home_primary_buttons", ()):
                boton.setMinimumWidth(0)
                boton.setMaximumWidth(260)
                boton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            layout.setHorizontalSpacing(0)
            layout.setVerticalSpacing(12)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 0)
            layout.setColumnStretch(2, 1)
            layout.setColumnStretch(3, 0)
            layout.addWidget(self.boton_buscar, 0, 1)
            layout.addWidget(self.boton_clasificar, 1, 1)
        else:
            for boton in getattr(self, "_home_primary_buttons", ()):
                boton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
                boton.setFixedWidth(260)
            layout.setHorizontalSpacing(18)
            layout.setVerticalSpacing(12)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 0)
            layout.setColumnStretch(2, 0)
            layout.setColumnStretch(3, 1)
            layout.addWidget(self.boton_buscar, 0, 1)
            layout.addWidget(self.boton_clasificar, 0, 2)

        self._home_responsive_mode = nuevo_modo
        layout.invalidate()
        layout.activate()

def actualizar_layout_home_responsive(self):
        if not hasattr(self, "home_shell"):
            return
        if not hasattr(self, "home_card"):
            return
        if not hasattr(self, "home_robot_shell"):
            return
        if not hasattr(self, "home_hero_layout"):
            return
        if not hasattr(self, "robot_layer_home"):
            return
        if not hasattr(self, "robot_home_label"):
            return

        if hasattr(self, "home_scroll") and self.home_scroll is not None:
            home_w = self.home_scroll.viewport().width()
        elif hasattr(self, "home_page_widget") and self.home_page_widget is not None:
            home_w = self.home_page_widget.width()
        elif self.centralWidget():
            home_w = self.centralWidget().width()
        else:
            home_w = self.width()

        hero_available_w = max(0, home_w - 68)
        breakpoint = getattr(self, "_home_responsive_breakpoint", 980)
        compacto = hero_available_w < breakpoint
        _aplicar_modo_home_responsive(self, compacto)

        direccion = (
            QtWidgets.QBoxLayout.TopToBottom
            if compacto else
            QtWidgets.QBoxLayout.LeftToRight
        )
        self.home_hero_layout.setDirection(direccion)
        self.home_hero_layout.setSpacing(12 if compacto else 18)
        self.home_hero_layout.setStretch(0, 0)
        self.home_hero_layout.setStretch(1, 0)
        self.home_hero_layout.invalidate()
        self.home_hero_layout.activate()

        if hero_available_w >= 1320:
            card_target_w = 920
        elif hero_available_w >= 1180:
            card_target_w = 860
        else:
            card_target_w = 800

        if compacto:
            card_w = min(740, max(380, hero_available_w - 18))
        else:
            if hero_available_w >= 1240:
                robot_shell_w = 340
            elif hero_available_w >= 1080:
                robot_shell_w = 320
            else:
                robot_shell_w = 300
            card_w = min(
                card_target_w,
                max(620, hero_available_w - robot_shell_w - 18)
            )

        self.home_card.setFixedWidth(card_w)

        lay = self.home_card.layout()
        if lay is not None:
            lay.invalidate()
            lay.activate()

        self.home_card.adjustSize()

        contenido_h = self.home_card.sizeHint().height()
        card_h = contenido_h + 20

        self.home_card.setMinimumHeight(card_h)
        self.home_card.setMaximumHeight(16777215)

        shell_w = card_w
        shell_h = card_h
        self.home_shell.setFixedSize(shell_w, shell_h)
        self.home_shell_layout.setContentsMargins(0, 0, 0, 0)
        self.home_shell_layout.invalidate()
        self.home_shell_layout.activate()

        self.robot_home_label.adjustSize()
        rw = self.robot_home_label.width()
        rh = self.robot_home_label.height()

        if compacto:
            robot_shell_w = card_w
            robot_shell_h = max(300, min(340, rh + 32))
        else:
            if hero_available_w >= 1240:
                robot_shell_w = 340
            elif hero_available_w >= 1080:
                robot_shell_w = 320
            else:
                robot_shell_w = 300
            robot_shell_h = card_h

        self.home_robot_shell.setFixedSize(robot_shell_w, robot_shell_h)
        robot_stage_w = rw + 24
        robot_stage_h = rh + 24
        self.robot_layer_home.setFixedSize(robot_stage_w, robot_stage_h)
        self.robot_layer_home.raise_()

        robot_x = max(0, (robot_stage_w - rw) // 2)
        robot_y = max(0, (robot_stage_h - rh) // 2)
        self.robot_home_label.move(robot_x, robot_y)
        self.robot_home_label.raise_()

        if hasattr(self, "robot_reactor"):
            self.robot_reactor.raise_()

        if hasattr(self, "robot_chest"):
            QtCore.QTimer.singleShot(0, self._posicionar_robot_chest)

        if hasattr(self, "boton_buscar"):
            btn_pos = self.boton_buscar.pos()
            if getattr(self, "_buscar_btn_hovered", False):
                btn_pos = QtCore.QPoint(btn_pos.x(), btn_pos.y() + 3)
            self._buscar_btn_base_pos = btn_pos

        QtCore.QTimer.singleShot(0, self.robot_layer_home.raise_)
        QtCore.QTimer.singleShot(0, self.robot_home_label.raise_)

def event_filter_home(self, obj, event):
    # 3) HOME responsive + orden de capas
    if obj in (
        getattr(self, "home_page_widget", None),
        getattr(self, "home_wrapper", None),
        getattr(getattr(self, "home_scroll", None), "viewport", lambda: None)(),
    ):
        if event.type() == QtCore.QEvent.Resize:
            QtCore.QTimer.singleShot(0, self._actualizar_layout_home_responsive)
            return False

    if hasattr(self, "robot_home_label") and obj is self.robot_home_label:
        if event.type() == QtCore.QEvent.Resize:
            QtCore.QTimer.singleShot(0, self._posicionar_robot_chest)
            QtCore.QTimer.singleShot(0, self.robot_home_label.raise_)
            return False

    # 4) Hover botones HOME → robot reacciona
    boton_buscar = getattr(self, "boton_buscar", None)
    boton_clasificar = getattr(self, "boton_clasificar", None)
    boton_salir = getattr(self, "boton_salir", None)

    if boton_buscar is None or boton_clasificar is None or boton_salir is None:
        return False

    if event.type() == QtCore.QEvent.Enter:
        if obj is boton_buscar:
            self._set_robot_mood("buscar", look_left=True)
            self._robot_bounce()
            if not self._buscar_btn_hovered:
                self._buscar_btn_hovered = True
                self._animar_boton_buscar_hover(True)
            return False

        elif obj is boton_clasificar:
            self._set_robot_mood("buscar", look_left=True)
            self._robot_bounce()
            return False

        elif obj is boton_salir:
            self._set_robot_mood("salir", look_left=True)
            self._robot_bounce()
            return False

    elif event.type() == QtCore.QEvent.Leave:
        if obj in (boton_buscar, boton_clasificar, boton_salir):
            self._set_robot_mood("idle", look_left=False)

        if obj is boton_buscar and self._buscar_btn_hovered:
            self._buscar_btn_hovered = False
            self._animar_boton_buscar_hover(False)

        if obj in (boton_buscar, boton_clasificar, boton_salir):
            return False

    # 5) Hover de la HomeCard
    if hasattr(self, "home_card") and obj is self.home_card:
        return False

    return False

def home_ir_a_todos_cvs(self):
        base = self._home_base_actual()
        self._actualizar_stats_home()

        if base is None:
            self._mostrar_feedback_home("Primero selecciona una carpeta", "Pulsa «Elegir carpeta» o ve a Buscar")
            return

        self._mostrar_feedback_home("Mostrando todos los CVs", base.name)

        self._ir_buscar()
        self.buscar_input.clear()
        self.buscar_input.setFocus()
        self._set_modo_busqueda("AND")
        self._set_scope_busqueda("cvs")

        resultados = []
        for p in base.rglob("*"):
            try:
                if not p.is_file():
                    continue
                nombre = p.name.lower()
                if nombre.endswith(".notas.txt") or nombre.endswith(".clientes.txt"):
                    continue
                if p.suffix.lower() not in {".pdf", ".doc", ".docx", ".odt", ".rtf"}:
                    continue
                resultados.append(p)
            except Exception:
                continue

        resultados = sorted(resultados, key=lambda x: x.name.lower())
        self._cargar_resultados_home_directos(resultados[:300], scope="cvs")

def home_elegir_carpeta(self):
    self._ir_buscar()
    self._elegir_carpeta_buscar()
    QtCore.QTimer.singleShot(0, self._actualizar_stats_home)

def actualizar_stats_home(self):
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

    total_cvs = self._contar_cvs_base(base)
    total_notas = len(self._obtener_cvs_con_notas()) if hasattr(self, "_obtener_cvs_con_notas") else 0
    total_cliente = len(self._obtener_cvs_con_cliente()) if hasattr(self, "_obtener_cvs_con_cliente") else 0

    if hasattr(self, "stat_total_num"):
        self.stat_total_num.setText(str(total_cvs))
    if hasattr(self, "stat_notas_num"):
        self.stat_notas_num.setText(str(total_notas))
    if hasattr(self, "stat_cliente_num"):
        self.stat_cliente_num.setText(str(total_cliente))