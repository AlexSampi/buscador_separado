from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets


class ItemResultado(QtWidgets.QWidget):
    """
    Widget personalizado para cada fila de la lista de resultados.
    Muestra el nombre del CV + ruta relativa y un botón de Notas.
    La señal notas_clicked emite el path absoluto del CV.
    """
    notas_clicked = QtCore.Signal(str)
    anadir_nota_clicked = QtCore.Signal(str)
    cliente_clicked = QtCore.Signal(str)

    def __init__(
        self,
        etiqueta: str,
        ruta_cv: str,
        tiene_notas: bool = False,
        parent=None,
        modo_resultado: str = "cv",
        ruta_nota: str | None = None,
    ):
        super().__init__(parent)

        self.ruta_cv = ruta_cv
        self.modo_resultado = (modo_resultado or "cv").lower()
        self.ruta_nota = ruta_nota

        self.setObjectName("ResultadoItem")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self._alto_minimo = 108 if (modo_resultado or "cv").lower() == "cv" else 126

        self._shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self._shadow)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        self.label = QtWidgets.QLabel(etiqueta)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.label.setMinimumWidth(0)

        layout.addWidget(self.label, 1)

        botones_layout = QtWidgets.QHBoxLayout()
        botones_layout.setSpacing(12)
        botones_layout.setContentsMargins(0, 0, 0, 0)

        self.boton_abrir = QtWidgets.QPushButton()
        self.boton_abrir.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_abrir.setFixedWidth(118)
        self.boton_abrir.setFixedHeight(36)
        self.boton_abrir.setObjectName("BotonAbrir")

        self.boton_notas = QtWidgets.QPushButton("📝 Notas")
        self.boton_notas.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_notas.setFixedWidth(90)
        self.boton_notas.setFixedHeight(36)
        self.boton_notas.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.boton_notas_menu = QtWidgets.QPushButton("▾")
        self.boton_notas_menu.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_notas_menu.setFixedWidth(32)
        self.boton_notas_menu.setFixedHeight(36)
        self.boton_notas_menu.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.boton_notas_menu.setObjectName("BotonNotasMenu")

        self.boton_cliente = QtWidgets.QPushButton()
        # --- SEMÁFORO ---
        self.boton_estado = QtWidgets.QPushButton("Neutro")
        self.boton_estado.setFixedWidth(132)
        self.boton_estado.setFixedHeight(36)
        self.boton_estado.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_estado.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.boton_estado.setIconSize(QtCore.QSize(12, 12))

        menu_estado = QtWidgets.QMenu(self.boton_estado)
        menu_estado.setMinimumWidth(135)

        icono_neutro = self._crear_icono_estado("#d1d5db")
        icono_verde = self._crear_icono_estado("#22c55e")
        icono_naranja = self._crear_icono_estado("#f59e0b")
        icono_rojo = self._crear_icono_estado("#ef4444")

        accion_neutro = menu_estado.addAction(icono_neutro, "Neutro")
        accion_verde = menu_estado.addAction(icono_verde, "Bueno")
        accion_naranja = menu_estado.addAction(icono_naranja, "Dudas")
        accion_rojo = menu_estado.addAction(icono_rojo, "Descartar")

        accion_neutro.triggered.connect(lambda: self._cambiar_estado(""))
        accion_verde.triggered.connect(lambda: self._cambiar_estado("verde"))
        accion_naranja.triggered.connect(lambda: self._cambiar_estado("naranja"))
        accion_rojo.triggered.connect(lambda: self._cambiar_estado("rojo"))

        self.boton_estado.setMenu(menu_estado)
        self.boton_cliente.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_cliente.setFixedWidth(126)
        self.boton_cliente.setFixedHeight(36)
        self.boton_cliente.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        if self.modo_resultado == "note":
            self.boton_abrir.hide()
            self.boton_cliente.hide()

            self.boton_notas.setText("📝 Notas")
            self.boton_notas.setObjectName("BotonNotasActivo")

            menu_notas = QtWidgets.QMenu(self.boton_notas)

            accion_abrir_nota = menu_notas.addAction("Abrir nota")
            accion_abrir_nota.triggered.connect(
                lambda: QtGui.QDesktopServices.openUrl(
                    QtCore.QUrl.fromLocalFile(self.ruta_nota or self.ruta_cv)
                )
            )

            menu_notas.addSeparator()

            accion_abrir_cv = menu_notas.addAction("Abrir CV")
            accion_abrir_cv.triggered.connect(
                lambda: QtGui.QDesktopServices.openUrl(
                    QtCore.QUrl.fromLocalFile(self.ruta_cv)
                )
            )
            self.boton_notas.setMenu(menu_notas)

            self.boton_notas.style().unpolish(self.boton_notas)
            self.boton_notas.style().polish(self.boton_notas)

        else:
            self.boton_abrir.setText("📄 Abrir")
            self.boton_abrir.clicked.connect(
                lambda: QtGui.QDesktopServices.openUrl(
                    QtCore.QUrl.fromLocalFile(self.ruta_cv)
                )
            )

            tiene_clientes = self._tiene_clientes_registrados()
            self._actualizar_estilo_cliente(tiene_clientes)
            self.boton_cliente.clicked.connect(
                lambda: self.cliente_clicked.emit(self.ruta_cv)
            )

            menu_notas = QtWidgets.QMenu(self.boton_notas)

            accion_abrir_notas = menu_notas.addAction("Abrir notas")
            accion_abrir_notas.triggered.connect(
                lambda: self.notas_clicked.emit(self.ruta_cv)
            )

            menu_notas.addSeparator()

            accion_anadir_nota = menu_notas.addAction("Añadir anotación")
            accion_anadir_nota.triggered.connect(
                lambda: self.anadir_nota_clicked.emit(self.ruta_cv)
            )

            self.boton_notas.setMenu(menu_notas)

            self._actualizar_estilo_notas(tiene_notas)

        botones_layout.addWidget(self.boton_abrir)
        botones_layout.addWidget(self.boton_cliente)
        botones_layout.addWidget(self.boton_estado)
        botones_layout.addWidget(self.boton_notas)

        layout.addLayout(botones_layout)

        estado = self._leer_estado()
        self._actualizar_visual_estado(estado)

    def _crear_icono_estado(self, color_hex: str) -> QtGui.QIcon:
        pix = QtGui.QPixmap(14, 14)
        pix.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(color_hex))
        painter.drawEllipse(1, 1, 12, 12)
        painter.end()

        return QtGui.QIcon(pix)

    def _actualizar_estilo_notas(self, tiene_notas: bool):
        nombre = "BotonNotasActivo" if tiene_notas else "BotonNotas"
        self.boton_notas.setObjectName(nombre)

        self.boton_notas.style().unpolish(self.boton_notas)
        self.boton_notas.style().polish(self.boton_notas)

        tooltip = (
            "Este CV ya tiene notas — abrir o añadir anotación"
            if tiene_notas
            else "Crear notas o añadir una anotación"
        )
        self.boton_notas.setToolTip(tooltip)

    def _ruta_clientes(self) -> Path:
        p = Path(self.ruta_cv)
        return p.with_suffix(p.suffix + ".clientes.txt")

    def _tiene_clientes_registrados(self) -> bool:
        ruta = self._ruta_clientes()
        if not ruta.exists():
            return False

        try:
            contenido = ruta.read_text(encoding="utf-8").strip()
            return bool(contenido)
        except Exception:
            return False

    def _actualizar_estilo_cliente(self, tiene_clientes: bool):
        if tiene_clientes:
            self.boton_cliente.setText("🏢 Cliente: Sí")
            self.boton_cliente.setObjectName("BotonClienteActivo")
            self.boton_cliente.setToolTip("Este CV ya tiene clientes registrados")
        else:
            self.boton_cliente.setText("🏢 Cliente: No")
            self.boton_cliente.setObjectName("BotonCliente")
            self.boton_cliente.setToolTip("Registrar a qué cliente se ofreció este CV")

        self.boton_cliente.style().unpolish(self.boton_cliente)
        self.boton_cliente.style().polish(self.boton_cliente)

    def marcar_con_clientes(self, tiene_clientes: bool):
        self._actualizar_estilo_cliente(tiene_clientes)

    def marcar_con_notas(self, tiene_notas: bool):
        self._actualizar_estilo_notas(tiene_notas)

    def sizeHint(self):
        base = super().sizeHint()
        alto = max(base.height(), getattr(self, "_alto_minimo", 108))
        return QtCore.QSize(base.width(), alto)

    def enterEvent(self, event):
        if hasattr(self, "_shadow"):
            self._shadow.setBlurRadius(26)
            self._shadow.setOffset(0, 6)
            self._shadow.setColor(QtGui.QColor(0, 0, 0, 60))
        return super().enterEvent(event)

    def leaveEvent(self, event):
        if hasattr(self, "_shadow"):
            self._shadow.setBlurRadius(18)
            self._shadow.setOffset(0, 4)
            self._shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        return super().leaveEvent(event)
    
    def _ruta_estado(self) -> Path:
        p = Path(self.ruta_cv)
        return p.with_suffix(p.suffix + ".estado.txt")


    def _cambiar_estado(self, estado: str):
        ruta = self._ruta_estado()

        try:
            if estado:
                ruta.write_text(estado, encoding="utf-8")
            else:
                if ruta.exists():
                    ruta.unlink()
        except Exception:
            return

        self._actualizar_visual_estado(estado)


    def _leer_estado(self) -> str:
        ruta = self._ruta_estado()

        if not ruta.exists():
            return ""

        try:
            return ruta.read_text(encoding="utf-8").strip()
        except Exception:
            return ""


    def _actualizar_visual_estado(self, estado: str):
        if estado == "verde":
            self.boton_estado.setText("Bueno")
            self.boton_estado.setIcon(self._crear_icono_estado("#22c55e"))
            self.boton_estado.setStyleSheet("""
                QPushButton {
                    background-color: #dcfce7;
                    color: #166534;
                    border: 1px solid #86efac;
                    border-radius: 8px;
                    font-weight: 700;
                    padding: 0 6px;
                    text-align: center;
                }
            """)
            self.setStyleSheet("""
                QWidget#ResultadoItem {
                    background-color: rgba(34, 197, 94, 0.06);
                    border: 1px solid rgba(34, 197, 94, 0.18);
                    border-radius: 14px;
                }
            """)
        elif estado == "naranja":
            self.boton_estado.setText("Dudas")
            self.boton_estado.setIcon(self._crear_icono_estado("#f59e0b"))
            self.boton_estado.setStyleSheet("""
                QPushButton {
                    background-color: #fef3c7;
                    color: #92400e;
                    border: 1px solid #fcd34d;
                    border-radius: 8px;
                    font-weight: 700;
                    padding: 0 10px;
                    text-align: center;
                }
            """)
            self.setStyleSheet("""
                QWidget#ResultadoItem {
                    background-color: rgba(245, 158, 11, 0.06);
                    border: 1px solid rgba(245, 158, 11, 0.18);
                    border-radius: 14px;
                }
            """)
        elif estado == "rojo":
            self.boton_estado.setText("Desc.")
            self.boton_estado.setIcon(self._crear_icono_estado("#ef4444"))
            self.boton_estado.setStyleSheet("""
                QPushButton {
                    background-color: #fee2e2;
                    color: #991b1b;
                    border: 1px solid #fca5a5;
                    border-radius: 8px;
                    font-weight: 700;
                    padding: 0 10px;
                    text-align: center;
                }
            """)
            self.setStyleSheet("""
                QWidget#ResultadoItem {
                    background-color: rgba(239, 68, 68, 0.06);
                    border: 1px solid rgba(239, 68, 68, 0.18);
                    border-radius: 14px;
                }
            """)
        else:
            self.boton_estado.setText("Neutro")
            self.boton_estado.setIcon(self._crear_icono_estado("#d1d5db"))
            self.boton_estado.setStyleSheet("""
                QPushButton {
                    background-color: #f3f4f6;
                    color: #6b7280;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    font-weight: 700;
                    padding: 0 10px;
                    text-align: center;
                }
            """)
            self.setStyleSheet("""
                QWidget#ResultadoItem {
                    background-color: rgba(255, 255, 255, 0.92);
                    border: 1px solid rgba(139, 92, 246, 0.10);
                    border-radius: 14px;
                }
            """)