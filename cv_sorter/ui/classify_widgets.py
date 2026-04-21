from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class ItemClasificacionWidget(QtWidgets.QWidget):
    editar_clicked = QtCore.Signal()

    def __init__(self, nombre: str, categoria: str, destino: str, color_categoria: QtGui.QColor, parent=None):
        super().__init__(parent)

        self.setObjectName("ResultadoItem")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self._shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(18)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QtGui.QColor(0, 0, 0, 40))
        self.setGraphicsEffect(self._shadow)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        texto_wrap = QtWidgets.QWidget()
        texto_layout = QtWidgets.QVBoxLayout(texto_wrap)
        texto_layout.setContentsMargins(0, 0, 0, 0)
        texto_layout.setSpacing(4)

        self.lbl_nombre = QtWidgets.QLabel(nombre or "Sin nombre")
        self.lbl_nombre.setObjectName("ClasItemNombre")
        self.lbl_nombre.setWordWrap(True)
        self.lbl_nombre.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.lbl_categoria = QtWidgets.QLabel(f"Categoría: {categoria or 'Otros'}")
        self.lbl_categoria.setObjectName("ClasItemMeta")
        self.lbl_categoria.setWordWrap(True)
        self.lbl_categoria.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.lbl_destino = QtWidgets.QLabel(f"Destino: {destino or '—'}")
        self.lbl_destino.setObjectName("ClasItemMeta")
        self.lbl_destino.setWordWrap(True)
        self.lbl_destino.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        texto_layout.addWidget(self.lbl_nombre)
        texto_layout.addWidget(self.lbl_categoria)
        texto_layout.addWidget(self.lbl_destino)

        acciones_layout = QtWidgets.QVBoxLayout()
        acciones_layout.setContentsMargins(0, 0, 0, 0)
        acciones_layout.setSpacing(8)

        self.badge_categoria = QtWidgets.QLabel(categoria or "Otros")
        self.badge_categoria.setObjectName("ClasItemBadge")
        self.badge_categoria.setAlignment(QtCore.Qt.AlignCenter)
        self.badge_categoria.setProperty("categoria", categoria or "Otros")

        self.btn_editar = QtWidgets.QPushButton("✏ Editar")
        self.btn_editar.setObjectName("BotonAbrir")
        self.btn_editar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_editar.setFixedHeight(34)
        self.btn_editar.setMinimumWidth(96)

        acciones_layout.addWidget(self.badge_categoria, 0, QtCore.Qt.AlignRight)
        acciones_layout.addWidget(self.btn_editar, 0, QtCore.Qt.AlignRight)
        acciones_layout.addStretch(1)

        layout.addWidget(texto_wrap, 1)
        layout.addLayout(acciones_layout, 0)

        self._color_categoria = QtGui.QColor(color_categoria)
        self._aplicar_color_badge()

        self.btn_editar.clicked.connect(self.editar_clicked.emit)

    def _aplicar_color_badge(self):
        c = QtGui.QColor(self._color_categoria)
        alpha_bg = 38
        alpha_border = 120
        self.badge_categoria.setStyleSheet(
            f"""
            QLabel#ClasItemBadge {{
                background: rgba({c.red()}, {c.green()}, {c.blue()}, {alpha_bg});
                border: 1px solid rgba({c.red()}, {c.green()}, {c.blue()}, {alpha_border});
                border-radius: 999px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 900;
                color: #111827;
                min-width: 118px;
            }}
            """
        )

    def sizeHint(self):
        base = super().sizeHint()
        return QtCore.QSize(base.width(), max(base.height(), 104))

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