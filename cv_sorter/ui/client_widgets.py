from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets


class ClienteCardWidget(QtWidgets.QWidget):
    eliminar_clicked = QtCore.Signal(str)
    notas_clicked = QtCore.Signal(str)
    estado_changed = QtCore.Signal(str, str)

    ESTADOS_VALIDOS = (
        "Pendiente",
        "Enviado",
        "Entrevista",
        "Rechazado",
        "Contratado",
    )

    def __init__(self, empresa: str, nota: str = "", estado: str = "Pendiente", nota_fecha: str = "", parent=None):
        super().__init__(parent)

        self.empresa = (empresa or "").strip()
        self.nota = (nota or "").strip()
        self.estado = (estado or "Pendiente").strip()
        self.nota_fecha = (nota_fecha or "").strip()
        if self.estado not in self.ESTADOS_VALIDOS:
            self.estado = "Pendiente"

        self.setObjectName("ClienteCard")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)

        self._shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 3)
        self._shadow.setColor(QtGui.QColor(0, 0, 0, 34))
        self.setGraphicsEffect(self._shadow)

        self.lbl_empresa = QtWidgets.QLabel(self.empresa)
        self.lbl_empresa.setObjectName("ClienteCardNombre")
        self.lbl_empresa.setWordWrap(True)

        self.lbl_nota = QtWidgets.QLabel()
        self.lbl_nota.setObjectName("ClienteCardNota")
        self.lbl_nota.setWordWrap(True)

        self.combo_estado = QtWidgets.QComboBox()
        self.combo_estado.setObjectName("ClienteCardEstado")
        self.combo_estado.setCursor(QtCore.Qt.PointingHandCursor)
        self.combo_estado.setFixedHeight(32)
        self.combo_estado.setMinimumWidth(130)
        self.combo_estado.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.combo_estado.addItems(list(self.ESTADOS_VALIDOS))

        self.btn_notas = QtWidgets.QPushButton()
        self.btn_notas.setObjectName("ClienteCardNotas")
        self.btn_notas.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_notas.setFixedHeight(32)
        self.btn_notas.setAutoDefault(False)
        self.btn_notas.setDefault(False)
        self.btn_notas.setFocusPolicy(QtCore.Qt.NoFocus)

        self.btn_eliminar = QtWidgets.QPushButton("✕")
        self.btn_eliminar.setObjectName("ClienteCardEliminar")
        self.btn_eliminar.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_eliminar.setFixedSize(32, 32)
        self.btn_eliminar.setAutoDefault(False)
        self.btn_eliminar.setDefault(False)
        self.btn_eliminar.setFocusPolicy(QtCore.Qt.NoFocus)

        col_texto = QtWidgets.QVBoxLayout()
        col_texto.setContentsMargins(0, 0, 0, 0)
        col_texto.setSpacing(3)
        col_texto.addWidget(self.lbl_empresa)
        col_texto.addWidget(self.lbl_nota)

        col_acciones = QtWidgets.QVBoxLayout()
        col_acciones.setContentsMargins(0, 0, 0, 0)
        col_acciones.setSpacing(6)
        col_acciones.addWidget(self.combo_estado, 0, QtCore.Qt.AlignRight)
        col_acciones.addWidget(self.btn_notas, 0, QtCore.Qt.AlignRight)
        col_acciones.addStretch(1)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(10)
        layout.addLayout(col_texto, 1)
        layout.addLayout(col_acciones, 0)
        layout.addWidget(self.btn_eliminar, 0, QtCore.Qt.AlignTop)

        self._actualizar_estilo_estado()
        self._actualizar_estilo_notas()

        self.btn_notas.clicked.connect(lambda: self.notas_clicked.emit(self.empresa))
        self.btn_eliminar.clicked.connect(lambda: self.eliminar_clicked.emit(self.empresa))
        self.combo_estado.currentTextChanged.connect(self._on_estado_changed)

    def _actualizar_estilo_notas(self):
        if self.nota.strip():
            self.btn_notas.setText("📝 Notas ✓")
            self.btn_notas.setProperty("hasNote", True)
            preview = self.nota.strip().replace("\n", " ")
            if len(preview) > 58:
                preview = preview[:58].rstrip() + "..."
        else:
            self.btn_notas.setText("📝 Notas")
            self.btn_notas.setProperty("hasNote", False)
            preview = ""

        estado_txt = f"Estado: {self.estado or 'Pendiente'}"

        if self.nota_fecha.strip():
            fecha_txt = f" · Nota: {self.nota_fecha.strip()}"
        else:
            fecha_txt = ""

        if preview:
            self.lbl_nota.setText(f"{estado_txt}{fecha_txt} · {preview}")
        else:
            self.lbl_nota.setText(f"{estado_txt}{fecha_txt}")

        self.btn_notas.style().unpolish(self.btn_notas)
        self.btn_notas.style().polish(self.btn_notas)

    def _actualizar_estilo_estado(self):
        estado = (self.estado or "Pendiente").strip()
        if estado not in self.ESTADOS_VALIDOS:
            estado = "Pendiente"
            self.estado = estado

        idx = self.combo_estado.findText(estado)
        if idx >= 0 and self.combo_estado.currentIndex() != idx:
            self.combo_estado.blockSignals(True)
            self.combo_estado.setCurrentIndex(idx)
            self.combo_estado.blockSignals(False)

        self.combo_estado.setProperty("estado", estado)
        self.combo_estado.style().unpolish(self.combo_estado)
        self.combo_estado.style().polish(self.combo_estado)

    def _on_estado_changed(self, estado: str):
        estado = (estado or "Pendiente").strip()
        if estado not in self.ESTADOS_VALIDOS:
            estado = "Pendiente"

        self.estado = estado
        self._actualizar_estilo_estado()
        self._actualizar_estilo_notas()
        self.estado_changed.emit(self.empresa, self.estado)

    def set_nota(self, nota: str, nota_fecha: str = ""):
        self.nota = (nota or "").strip()
        self.nota_fecha = (nota_fecha or "").strip()
        self._actualizar_estilo_notas()

    def set_estado(self, estado: str):
        estado = (estado or "Pendiente").strip()
        if estado not in self.ESTADOS_VALIDOS:
            estado = "Pendiente"
        self.estado = estado
        self._actualizar_estilo_estado()
        self._actualizar_estilo_notas()