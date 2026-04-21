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
        botones_layout.setSpacing(8)
        botones_layout.setContentsMargins(0, 0, 0, 0)

        self.boton_abrir = QtWidgets.QPushButton()
        self.boton_abrir.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_abrir.setFixedWidth(118)
        self.boton_abrir.setFixedHeight(36)
        self.boton_abrir.setObjectName("BotonAbrir")

        self.boton_notas = QtWidgets.QPushButton()
        self.boton_notas.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_notas.setFixedWidth(140)
        self.boton_notas.setFixedHeight(36)
        self.boton_notas.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        self.boton_cliente = QtWidgets.QPushButton()
        self.boton_cliente.setCursor(QtCore.Qt.PointingHandCursor)
        self.boton_cliente.setFixedWidth(126)
        self.boton_cliente.setFixedHeight(36)
        self.boton_cliente.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        if self.modo_resultado == "note":
            self.boton_abrir.hide()
            self.boton_cliente.hide()

            self.boton_notas.setText("🗒 Notas ▾")
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

            self.boton_notas.setText("🗒 Notas ▾")

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
        botones_layout.addWidget(self.boton_notas)

        layout.addLayout(botones_layout)

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