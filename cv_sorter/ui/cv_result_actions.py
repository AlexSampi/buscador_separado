from __future__ import annotations

from pathlib import Path

import yaml
from PySide6 import QtCore, QtGui, QtWidgets

from cv_sorter.services.notes_utils import actualizar_notas_unificadas
from cv_sorter.ui.client_dialogs import DialogoClientesPremium
from cv_sorter.ui.dialogs import DialogoTextoPremium


def crear_o_abrir_notas(self, ruta_cv: str):
    p = Path(ruta_cv)

    try:
        notas = actualizar_notas_unificadas(p)
    except Exception:
        notas = p.with_suffix(p.suffix + ".notas.txt")
        if not notas.exists():
            notas.write_text(f"Notas para: {p.name}\n\n", encoding="utf-8")

    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(p)))
    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(notas)))


def anadir_anotacion_con_fecha(self, ruta_cv: str):
    p = Path(ruta_cv)
    notas = p.with_suffix(p.suffix + ".notas.txt")

    dialogo = DialogoTextoPremium(
        parent=self,
        titulo="Nueva anotación",
        subtitulo="Escribe una observación para este candidato. Se guardará con fecha y hora.",
        nombre_cv=p.name,
        texto_inicial="",
        placeholder="Ejemplo: buen nivel de inglés, experiencia en soporte, disponibilidad inmediata...",
        texto_boton_ok="Guardar anotación",
        texto_boton_cancelar="Cancelar",
        permitir_vacio=False,
    )

    if dialogo.exec() != QtWidgets.QDialog.Accepted:
        return

    texto = dialogo.obtener_texto()
    if not texto:
        return

    if not notas.exists():
        notas.write_text(f"Notas para: {p.name}\n\n", encoding="utf-8")

    marca_tiempo = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm")
    bloque = f"[{marca_tiempo}]\n{texto}\n\n"

    try:
        with notas.open("a", encoding="utf-8") as f:
            f.write(bloque)
    except Exception as e:
        QtWidgets.QMessageBox.warning(
            self,
            "Error al guardar la anotación",
            f"No se pudo guardar la anotación.\n\n{e}"
        )
        return

    self._refrescar_estado_notas_en_lista(str(p))

    if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
        QtCore.QTimer.singleShot(0, self._accion_buscar)


def gestionar_clientes_cv(self, ruta_cv: str):
    p = Path(ruta_cv)
    ruta_clientes = p.with_suffix(p.suffix + ".clientes.txt")

    clientes_iniciales = []

    if ruta_clientes.exists():
        try:
            contenido = ruta_clientes.read_text(encoding="utf-8").strip()

            if contenido:
                try:
                    cargado = yaml.safe_load(contenido)

                    if isinstance(cargado, list):
                        for item in cargado:
                            if isinstance(item, dict):
                                empresa = str(item.get("empresa", "")).strip()
                                nota = str(item.get("nota", "")).strip()
                                nota_fecha = str(item.get("nota_fecha", "")).strip()
                                estado = str(item.get("estado", "Pendiente")).strip() or "Pendiente"
                                if empresa:
                                    clientes_iniciales.append({
                                        "empresa": empresa,
                                        "nota": nota,
                                        "nota_fecha": nota_fecha,
                                        "estado": estado,
                                    })
                            elif isinstance(item, str):
                                empresa = item.strip()
                                if empresa:
                                    clientes_iniciales.append({
                                        "empresa": empresa,
                                        "nota": "",
                                        "estado": "Pendiente",
                                    })
                    elif isinstance(cargado, str):
                        for linea in cargado.splitlines():
                            empresa = linea.strip().lstrip("-").strip()
                            if empresa:
                                clientes_iniciales.append({
                                    "empresa": empresa,
                                    "nota": "",
                                    "estado": "Pendiente",
                                })
                    else:
                        for linea in contenido.splitlines():
                            empresa = linea.strip().lstrip("-").strip()
                            if empresa:
                                clientes_iniciales.append({
                                    "empresa": empresa,
                                    "nota": "",
                                    "estado": "Pendiente",
                                })

                except Exception:
                    for linea in contenido.splitlines():
                        empresa = linea.strip().lstrip("-").strip()
                        if empresa:
                            clientes_iniciales.append({
                                "empresa": empresa,
                                "nota": "",
                                "estado": "Pendiente",
                            })

        except Exception:
            clientes_iniciales = []

    dialogo = DialogoClientesPremium(
        parent=self,
        nombre_cv=p.name,
        clientes_iniciales=clientes_iniciales,
    )

    if dialogo.exec() != QtWidgets.QDialog.Accepted:
        return

    clientes = dialogo.obtener_clientes()

    if clientes:
        texto_yaml = yaml.safe_dump(clientes, allow_unicode=True, sort_keys=False)
        print("[CLIENTES] guardando en:", ruta_clientes)
        print("[CLIENTES] contenido:\n", texto_yaml)

        ruta_clientes.write_text(
            texto_yaml,
            encoding="utf-8"
        )
    else:
        if ruta_clientes.exists():
            ruta_clientes.unlink()

    # 👇 MOVER FUERA DEL IF
    self._refrescar_estado_cliente_en_lista(str(p))

    if hasattr(self, "scope_notas") and self.scope_notas.isChecked():
        QtCore.QTimer.singleShot(0, self._accion_buscar)