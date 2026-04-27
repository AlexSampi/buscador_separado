from __future__ import annotations

from pathlib import Path

from PySide6 import QtWidgets

from cv_sorter.utils import ruta_recurso


def load_app_stylesheet() -> str:
    ruta_qss = ruta_recurso("cv_sorter/ui/styles.qss")
    return Path(ruta_qss).read_text(encoding="utf-8")


def apply_app_styles(app: QtWidgets.QApplication) -> None:
    app.setStyleSheet(load_app_stylesheet())
