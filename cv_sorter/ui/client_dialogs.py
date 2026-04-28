from __future__ import annotations

from PySide6 import QtCore, QtWidgets
import re

from cv_sorter.ui.client_widgets import ClienteCardWidget
from cv_sorter.ui.dialogs import DialogoTextoPremium


class DialogoClientesPremium(QtWidgets.QDialog):
    ESTADOS_VALIDOS = {
        "Pendiente",
        "Enviado",
        "Entrevista",
        "Rechazado",
        "Contratado",
    }

    def __init__(self, parent=None, nombre_cv: str = "", clientes_iniciales: list[dict] | None = None):
        super().__init__(parent)

        self.setModal(True)
        self.setWindowTitle("Clientes asociados")
        self.setObjectName("DialogoPremium")
        self.resize(670, 520)

        self._filtro_estado_actual = "Todas"
        self._tenia_clientes_iniciales = bool(clientes_iniciales)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        self.header_wrap = QtWidgets.QWidget()
        self.header_wrap.setObjectName("DialogHeaderWrap")
        header_layout = QtWidgets.QHBoxLayout(self.header_wrap)
        header_layout.setContentsMargins(12, 10, 12, 10)
        header_layout.setSpacing(10)

        self.lbl_header_icon = QtWidgets.QLabel("🏢")
        self.lbl_header_icon.setObjectName("DialogHeaderIcon")
        self.lbl_header_icon.setAlignment(QtCore.Qt.AlignCenter)

        header_text_col = QtWidgets.QVBoxLayout()
        header_text_col.setContentsMargins(0, 0, 0, 0)
        header_text_col.setSpacing(2)

        self.lbl_titulo = QtWidgets.QLabel("Clientes asociados")
        self.lbl_titulo.setObjectName("DialogTitulo")

        self.lbl_subtitulo = QtWidgets.QLabel(
            "Añade las empresas una a una y guarda notas si lo necesitas."
        )
        self.lbl_subtitulo.setObjectName("DialogSubtitulo")
        self.lbl_subtitulo.setWordWrap(True)

        header_text_col.addWidget(self.lbl_titulo)
        header_text_col.addWidget(self.lbl_subtitulo)

        self.lbl_contador = QtWidgets.QLabel("0 empresas")
        self.lbl_contador.setObjectName("DialogContador")

        header_layout.addWidget(self.lbl_header_icon, 0, QtCore.Qt.AlignTop)
        header_layout.addLayout(header_text_col, 1)
        header_layout.addWidget(self.lbl_contador, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.lbl_cv = QtWidgets.QLabel(nombre_cv)
        self.lbl_cv.setObjectName("DialogCV")
        self.lbl_cv.setWordWrap(True)
        self.lbl_cv.setVisible(bool(nombre_cv.strip()))

        top_row = QtWidgets.QHBoxLayout()
        top_row.setContentsMargins(0, 2, 0, 0)
        top_row.setSpacing(8)

        self.input_empresa = QtWidgets.QLineEdit()
        self.input_empresa.setObjectName("ClientesInput")
        self.input_empresa.setPlaceholderText("Añadir empresa...")

        self.btn_anadir = QtWidgets.QPushButton("＋ Añadir")
        self.btn_anadir.setObjectName("DialogBtnOk")
        self.btn_anadir.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_anadir.setFixedHeight(40)
        self.btn_anadir.setMinimumWidth(118)
        self.btn_anadir.setAutoDefault(False)
        self.btn_anadir.setDefault(False)

        top_row.addWidget(self.input_empresa, 1)
        top_row.addWidget(self.btn_anadir, 0)

        self.lbl_hint = QtWidgets.QLabel("Pulsa Enter o el botón para añadir una empresa.")
        self.lbl_hint.setObjectName("DialogHint")

        self.filtros_wrap = QtWidgets.QWidget()
        self.filtros_wrap.setObjectName("DialogFiltrosWrap")
        filtros_layout = QtWidgets.QHBoxLayout(self.filtros_wrap)
        filtros_layout.setContentsMargins(0, 0, 0, 0)
        filtros_layout.setSpacing(6)

        self.filtro_todos = QtWidgets.QPushButton("Todas")
        self.filtro_pendiente = QtWidgets.QPushButton("Pendiente")
        self.filtro_enviado = QtWidgets.QPushButton("Enviado")
        self.filtro_entrevista = QtWidgets.QPushButton("Entrevista")
        self.filtro_rechazado = QtWidgets.QPushButton("Rechazado")
        self.filtro_contratado = QtWidgets.QPushButton("Contratado")

        self._filtros_estado = [
            self.filtro_todos,
            self.filtro_pendiente,
            self.filtro_enviado,
            self.filtro_entrevista,
            self.filtro_rechazado,
            self.filtro_contratado,
        ]

        for b in self._filtros_estado:
            b.setObjectName("DialogFiltroChip")
            b.setCheckable(True)
            b.setCursor(QtCore.Qt.PointingHandCursor)
            b.setAutoDefault(False)
            b.setDefault(False)
            filtros_layout.addWidget(b)

        filtros_layout.addStretch(1)
        self.filtro_todos.setChecked(True)

        self.empty_wrap = QtWidgets.QWidget()
        self.empty_wrap.setObjectName("DialogEmptyWrap")

        empty_layout = QtWidgets.QVBoxLayout(self.empty_wrap)
        empty_layout.setContentsMargins(18, 14, 18, 14)
        empty_layout.setSpacing(6)
        empty_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.lbl_empty_icon = QtWidgets.QLabel("🏢")
        self.lbl_empty_icon.setObjectName("DialogEmptyIcon")
        self.lbl_empty_icon.setAlignment(QtCore.Qt.AlignCenter)

        self.lbl_empty = QtWidgets.QLabel("Todavía no has añadido ninguna empresa")
        self.lbl_empty.setObjectName("DialogEmpty")
        self.lbl_empty.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_empty.setWordWrap(True)

        self.lbl_empty_sub = QtWidgets.QLabel("Escribe una arriba y pulsa Añadir")
        self.lbl_empty_sub.setObjectName("DialogEmptySub")
        self.lbl_empty_sub.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_empty_sub.setWordWrap(True)

        empty_layout.addWidget(self.lbl_empty_icon)
        empty_layout.addWidget(self.lbl_empty)
        empty_layout.addWidget(self.lbl_empty_sub)

        self.lista_empresas = QtWidgets.QListWidget()
        self.lista_empresas.setObjectName("ListaClientesDialogo")
        self.lista_empresas.setSpacing(8)
        self.lista_empresas.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lista_empresas.setFocusPolicy(QtCore.Qt.NoFocus)
        self.lista_empresas.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)

        self.contenido_stack = QtWidgets.QStackedWidget()
        self.contenido_stack.setObjectName("DialogContenidoStack")
        self.contenido_stack.addWidget(self.empty_wrap)
        self.contenido_stack.addWidget(self.lista_empresas)

        self.lbl_info = QtWidgets.QLabel("")
        self.lbl_info.setObjectName("DialogInfo")
        self.lbl_info.setVisible(False)

        botones = QtWidgets.QHBoxLayout()
        botones.setContentsMargins(0, 2, 0, 0)
        botones.setSpacing(8)
        botones.addStretch(1)

        self.btn_cancelar = QtWidgets.QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("DialogBtnSec")
        self.btn_cancelar.setAutoDefault(False)
        self.btn_cancelar.setDefault(False)

        self.btn_guardar = QtWidgets.QPushButton("Guardar clientes")
        self.btn_guardar.setObjectName("DialogBtnOk")
        self.btn_guardar.setAutoDefault(False)
        self.btn_guardar.setDefault(False)

        botones.addWidget(self.btn_cancelar)
        botones.addWidget(self.btn_guardar)

        layout.addWidget(self.header_wrap)
        layout.addWidget(self.lbl_cv)
        layout.addLayout(top_row)
        layout.addWidget(self.lbl_hint)
        layout.addWidget(self.filtros_wrap)
        layout.addWidget(self.contenido_stack, 1)
        layout.addWidget(self.lbl_info)
        layout.addLayout(botones)

        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_guardar.clicked.connect(self._on_guardar_clientes)
        self.btn_anadir.clicked.connect(self._anadir_empresa_desde_input)
        self.input_empresa.returnPressed.connect(self._on_return_input_empresa)

        self.filtro_todos.clicked.connect(lambda: self._aplicar_filtro_estado("Todas"))
        self.filtro_pendiente.clicked.connect(lambda: self._aplicar_filtro_estado("Pendiente"))
        self.filtro_enviado.clicked.connect(lambda: self._aplicar_filtro_estado("Enviado"))
        self.filtro_entrevista.clicked.connect(lambda: self._aplicar_filtro_estado("Entrevista"))
        self.filtro_rechazado.clicked.connect(lambda: self._aplicar_filtro_estado("Rechazado"))
        self.filtro_contratado.clicked.connect(lambda: self._aplicar_filtro_estado("Contratado"))

        for item in (clientes_iniciales or []):
            empresa = self._normalizar_empresa(str((item or {}).get("empresa", "")).strip())
            nota = str((item or {}).get("nota", "")).strip()
            nota_fecha = str((item or {}).get("nota_fecha", "")).strip()
            asignado_fecha = str((item or {}).get("asignado_fecha", "")).strip()
            estado = str((item or {}).get("estado", "Pendiente")).strip() or "Pendiente"
            if estado not in self.ESTADOS_VALIDOS:
                estado = "Pendiente"

            self._anadir_empresa_a_lista(
                empresa,
                nota,
                estado,
                nota_fecha=nota_fecha,
                asignado_fecha=asignado_fecha,
                comprobar_duplicado=False
            )
        self._actualizar_estado_ui()
        self._refrescar_visibilidad_lista()
        self.input_empresa.setFocus()

    def _normalizar_empresa(self, texto: str) -> str:
        return " ".join((texto or "").strip().split())

    def _empresas_actuales(self) -> list[str]:
        empresas = []
        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}
            empresa = str(data.get("empresa", "")).strip()
            if empresa:
                empresas.append(empresa)
        return empresas

    def _ya_existe_empresa(self, empresa: str) -> bool:
        empresa_cf = empresa.casefold()
        return any(x.casefold() == empresa_cf for x in self._empresas_actuales())

    def _on_return_input_empresa(self):
        self._anadir_empresa_desde_input()

    def _on_guardar_clientes(self):
        total = self.lista_empresas.count()

        if total <= 0 and not self._tenia_clientes_iniciales:
            self.lbl_info.setText("Añade al menos una empresa antes de guardar.")
            self.lbl_info.setVisible(True)
            self.input_empresa.setFocus()
            return

        self.lbl_info.setVisible(False)
        self.accept()

    def _anadir_empresa_desde_input(self):
        empresa = self._normalizar_empresa(self.input_empresa.text())

        if not empresa:
            self.lbl_info.setText("Escribe una empresa antes de añadirla.")
            self.lbl_info.setVisible(True)
            self.input_empresa.setFocus()
            return

        if self._ya_existe_empresa(empresa):
            self.lbl_info.setText("Esa empresa ya está en la lista.")
            self.lbl_info.setVisible(True)
            self.input_empresa.selectAll()
            self.input_empresa.setFocus()
            return

        self._anadir_empresa_a_lista(empresa, "", "Pendiente")
        self.input_empresa.clear()
        self.lbl_info.setVisible(False)
        self.input_empresa.setFocus(QtCore.Qt.OtherFocusReason)

    def _anadir_empresa_a_lista(
        self,
        empresa: str,
        nota: str = "",
        estado: str = "Pendiente",
        nota_fecha: str = "",
        asignado_fecha: str = "",
        comprobar_duplicado: bool = True
    ):
        empresa = self._normalizar_empresa(empresa)
        nota = (nota or "").strip()
        estado = (estado or "Pendiente").strip()

        if estado not in self.ESTADOS_VALIDOS:
            estado = "Pendiente"

        if not empresa:
            return

        if comprobar_duplicado and self._ya_existe_empresa(empresa):
            return
        
        if not asignado_fecha:
            asignado_fecha = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm")
            widget = ClienteCardWidget(empresa, nota, estado, nota_fecha)
            widget.eliminar_clicked.connect(self._eliminar_empresa)
            widget.notas_clicked.connect(self._editar_nota_empresa)
            widget.estado_changed.connect(self._actualizar_estado_empresa)

        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, {
            "empresa": empresa,
            "nota": nota,
            "nota_fecha": (nota_fecha or "").strip(),
            "asignado_fecha": asignado_fecha,
            "estado": estado,
        })
        item.setSizeHint(widget.sizeHint())

        self.lista_empresas.addItem(item)
        self.lista_empresas.setItemWidget(item, widget)

        self._actualizar_estado_ui()
        self._refrescar_visibilidad_lista()

    def _eliminar_empresa(self, empresa: str):
        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}
            if str(data.get("empresa", "")).strip() == empresa:
                self.lista_empresas.takeItem(i)
                break

        self._actualizar_estado_ui()
        self._refrescar_visibilidad_lista()

    def _actualizar_estado_empresa(self, empresa: str, estado: str):
        estado = (estado or "Pendiente").strip()
        if estado not in self.ESTADOS_VALIDOS:
            estado = "Pendiente"

        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}

            if str(data.get("empresa", "")).strip() != empresa:
                continue

            data["estado"] = estado
            item.setData(QtCore.Qt.UserRole, data)

            widget = self.lista_empresas.itemWidget(item)
            if widget is not None and hasattr(widget, "set_estado"):
                widget.set_estado(estado)

            self._actualizar_estado_ui()
            self._refrescar_visibilidad_lista()
            return

    def _editar_nota_empresa(self, empresa: str):
        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}

            if str(data.get("empresa", "")).strip() != empresa:
                continue

            nota_actual = str(data.get("nota", "")).strip()

            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Notas de empresa")
            msg.setText(f"¿Qué quieres hacer con las notas de '{empresa}'?")
            btn_anadir = msg.addButton("Añadir nota", QtWidgets.QMessageBox.AcceptRole)

            btn_borrar_ultima = None
            btn_borrar_todo = None

            if nota_actual:
                btn_borrar_ultima = msg.addButton("Borrar última", QtWidgets.QMessageBox.ActionRole)
                btn_borrar_todo = msg.addButton("Borrar todo", QtWidgets.QMessageBox.DestructiveRole)

            btn_cancelar = msg.addButton("Cancelar", QtWidgets.QMessageBox.RejectRole)
            msg.exec()

            clicked = msg.clickedButton()

            if clicked == btn_cancelar or clicked is None:
                return

            if btn_borrar_todo is not None and clicked == btn_borrar_todo:
                respuesta = QtWidgets.QMessageBox.question(
                    self,
                    "Borrar historial",
                    f"¿Seguro que quieres borrar todas las notas de '{empresa}'?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No,
                )
                if respuesta != QtWidgets.QMessageBox.Yes:
                    return

                data["nota"] = ""
                data["nota_fecha"] = ""

            elif btn_borrar_ultima is not None and clicked == btn_borrar_ultima:
                partes = re.split(r"\n\s*\n(?=\[)", nota_actual)

                if not partes:
                    QtWidgets.QMessageBox.information(
                        self,
                        "Sin notas",
                        "No hay notas para borrar."
                    )
                    return

                if len(partes) == 1:
                    respuesta = QtWidgets.QMessageBox.question(
                        self,
                        "Borrar última nota",
                        f"Solo queda una nota en '{empresa}'.\n\n¿Quieres borrarla?",
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.No,
                    )
                    if respuesta != QtWidgets.QMessageBox.Yes:
                        return

                    data["nota"] = ""
                    data["nota_fecha"] = ""
                else:
                    nueva = "\n\n".join(partes[1:]).strip()
                    data["nota"] = nueva

                    m = re.match(r"^\[(.*?)\]", nueva)
                    data["nota_fecha"] = m.group(1).strip() if m else ""

            elif clicked == btn_anadir:
                dialogo = DialogoTextoPremium(
                    parent=self,
                    titulo="Nueva nota de empresa",
                    subtitulo="Escribe una nueva anotación. Se añadirá al historial con fecha y hora.",
                    nombre_cv=empresa,
                    texto_inicial="",
                    placeholder="Ejemplo: enviado, pendiente de respuesta, perfil que encaja mejor con backend...",
                    texto_boton_ok="Añadir nota",
                    texto_boton_cancelar="Cancelar",
                    permitir_vacio=False,
                )

                if dialogo.exec() != QtWidgets.QDialog.Accepted:
                    return

                nueva_nota = dialogo.obtener_texto().strip()
                if not nueva_nota:
                    return

                fecha = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm")
                nueva_entrada = f"[{fecha}]\n{nueva_nota}"

                if nota_actual:
                    data["nota"] = nueva_entrada + "\n\n" + nota_actual
                else:
                    data["nota"] = nueva_entrada

                data["nota_fecha"] = fecha

            else:
                return

            if "estado" not in data or not str(data.get("estado", "")).strip():
                data["estado"] = "Pendiente"

            item.setData(QtCore.Qt.UserRole, data)

            widget = self.lista_empresas.itemWidget(item)
            if widget is not None:
                if hasattr(widget, "set_nota"):
                    widget.set_nota(
                        str(data.get("nota", "")).strip(),
                        str(data.get("nota_fecha", "")).strip()
                    )
                if hasattr(widget, "set_estado"):
                    widget.set_estado(str(data.get("estado", "Pendiente")).strip() or "Pendiente")

            self._actualizar_estado_ui()
            self._refrescar_visibilidad_lista()
            return

    def _actualizar_estado_ui(self):
        total = self.lista_empresas.count()

        conteo_estados = {
            "Pendiente": 0,
            "Enviado": 0,
            "Entrevista": 0,
            "Rechazado": 0,
            "Contratado": 0,
        }

        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}
            estado = str(data.get("estado", "Pendiente")).strip() or "Pendiente"
            if estado in conteo_estados:
                conteo_estados[estado] += 1

        if total == 0:
            self.lbl_contador.setText("0 empresas")
        else:
            partes = [f"{total} empresa" if total == 1 else f"{total} empresas"]

            if conteo_estados["Pendiente"]:
                partes.append(
                    f"{conteo_estados['Pendiente']} pendiente"
                    if conteo_estados["Pendiente"] == 1
                    else f"{conteo_estados['Pendiente']} pendientes"
                )

            if conteo_estados["Enviado"]:
                partes.append(
                    f"{conteo_estados['Enviado']} enviada"
                    if conteo_estados["Enviado"] == 1
                    else f"{conteo_estados['Enviado']} enviadas"
                )

            if conteo_estados["Entrevista"]:
                partes.append(
                    f"{conteo_estados['Entrevista']} entrevista"
                    if conteo_estados["Entrevista"] == 1
                    else f"{conteo_estados['Entrevista']} entrevistas"
                )

            if conteo_estados["Rechazado"]:
                partes.append(
                    f"{conteo_estados['Rechazado']} rechazada"
                    if conteo_estados["Rechazado"] == 1
                    else f"{conteo_estados['Rechazado']} rechazadas"
                )

            if conteo_estados["Contratado"]:
                partes.append(
                    f"{conteo_estados['Contratado']} contratada"
                    if conteo_estados["Contratado"] == 1
                    else f"{conteo_estados['Contratado']} contratadas"
                )

            self.lbl_contador.setText(" • ".join(partes))

        self.btn_guardar.setText("Guardar")
        self.btn_guardar.setEnabled(total > 0 or self._tenia_clientes_iniciales)

    def _aplicar_filtro_estado(self, estado: str):
        self._filtro_estado_actual = estado or "Todas"

        mapa = {
            "Todas": self.filtro_todos,
            "Pendiente": self.filtro_pendiente,
            "Enviado": self.filtro_enviado,
            "Entrevista": self.filtro_entrevista,
            "Rechazado": self.filtro_rechazado,
            "Contratado": self.filtro_contratado,
        }

        for b in self._filtros_estado:
            b.blockSignals(True)
            b.setChecked(False)
            b.blockSignals(False)

        btn = mapa.get(self._filtro_estado_actual, self.filtro_todos)
        btn.blockSignals(True)
        btn.setChecked(True)
        btn.blockSignals(False)

        self._refrescar_visibilidad_lista()

    def _refrescar_visibilidad_lista(self):
        visibles = 0

        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}
            estado = str(data.get("estado", "Pendiente")).strip() or "Pendiente"

            mostrar = (
                self._filtro_estado_actual == "Todas"
                or estado == self._filtro_estado_actual
            )

            item.setHidden(not mostrar)

            if mostrar:
                visibles += 1

        hay_datos = self.lista_empresas.count() > 0

        if not hay_datos:
            self.lbl_empty.setText("Todavía no has añadido ninguna empresa")
            self.lbl_empty_sub.setText("Escribe una arriba y pulsa Añadir")
            self.contenido_stack.setCurrentWidget(self.empty_wrap)
            self.input_empresa.setFocus()

        elif visibles == 0:
            self.lbl_empty.setText("No hay empresas en este estado")
            self.lbl_empty_sub.setText("Cambia el filtro o añade una empresa arriba")
            self.contenido_stack.setCurrentWidget(self.empty_wrap)

        else:
            self.contenido_stack.setCurrentWidget(self.lista_empresas)

    def obtener_clientes(self) -> list[dict]:
        datos = []

        for i in range(self.lista_empresas.count()):
            item = self.lista_empresas.item(i)
            data = item.data(QtCore.Qt.UserRole) or {}

            empresa = str(data.get("empresa", "")).strip()
            nota = str(data.get("nota", "")).strip()
            nota_fecha = str(data.get("nota_fecha", "")).strip()
            asignado_fecha = str(data.get("asignado_fecha", "")).strip()
            estado = str(data.get("estado", "Pendiente")).strip() or "Pendiente"

            if estado not in self.ESTADOS_VALIDOS:
                estado = "Pendiente"

            if empresa:
                datos.append({
                    "empresa": empresa,
                    "nota": nota,
                    "nota_fecha": nota_fecha,
                    "asignado_fecha": asignado_fecha,
                    "estado": estado,
                })

        return datos