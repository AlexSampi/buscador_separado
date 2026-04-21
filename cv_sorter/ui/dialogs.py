from __future__ import annotations

from PySide6 import QtCore, QtWidgets


class DialogoTextoPremium(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        titulo: str = "Editar texto",
        subtitulo: str = "",
        nombre_cv: str = "",
        texto_inicial: str = "",
        placeholder: str = "",
        texto_boton_ok: str = "Guardar",
        texto_boton_cancelar: str = "Cancelar",
        permitir_vacio: bool = True,
    ):
        super().__init__(parent)

        self.setModal(True)
        self.setWindowTitle(titulo)
        self.setObjectName("DialogoPremium")
        self.resize(560, 420)

        self._permitir_vacio = permitir_vacio

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 18)
        layout.setSpacing(12)

        self.lbl_titulo = QtWidgets.QLabel(titulo)
        self.lbl_titulo.setObjectName("DialogTitulo")

        self.lbl_subtitulo = QtWidgets.QLabel(subtitulo)
        self.lbl_subtitulo.setObjectName("DialogSubtitulo")
        self.lbl_subtitulo.setWordWrap(True)
        self.lbl_subtitulo.setVisible(bool(subtitulo.strip()))

        self.lbl_cv = QtWidgets.QLabel(nombre_cv)
        self.lbl_cv.setObjectName("DialogCV")
        self.lbl_cv.setWordWrap(True)
        self.lbl_cv.setVisible(bool(nombre_cv.strip()))

        self.editor = QtWidgets.QTextEdit()
        self.editor.setObjectName("DialogTextEdit")
        self.editor.setPlaceholderText(placeholder)
        self.editor.setPlainText(texto_inicial)
        self.editor.setAcceptRichText(False)

        self.lbl_info = QtWidgets.QLabel("")
        self.lbl_info.setObjectName("DialogInfo")
        self.lbl_info.setVisible(False)

        botones = QtWidgets.QHBoxLayout()
        botones.setContentsMargins(0, 4, 0, 0)
        botones.setSpacing(10)
        botones.addStretch(1)

        self.btn_cancelar = QtWidgets.QPushButton(texto_boton_cancelar)
        self.btn_cancelar.setObjectName("DialogBtnSec")

        self.btn_guardar = QtWidgets.QPushButton(texto_boton_ok)
        self.btn_guardar.setObjectName("DialogBtnOk")
        self.btn_guardar.setDefault(True)

        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)

        layout.addWidget(self.lbl_titulo)
        layout.addWidget(self.lbl_subtitulo)
        layout.addWidget(self.lbl_cv)
        layout.addWidget(self.editor, 1)
        layout.addWidget(self.lbl_info)
        layout.addLayout(botones)

        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self._on_accept)

        self.editor.setFocus()

    def _on_accept(self):
        texto = self.obtener_texto()

        if not self._permitir_vacio and not texto.strip():
            self.lbl_info.setText("Escribe algo antes de guardar.")
            self.lbl_info.setVisible(True)
            self.editor.setFocus()
            return

        self.accept()

    def obtener_texto(self) -> str:
        return self.editor.toPlainText().strip()