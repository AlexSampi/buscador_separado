import sys

from PySide6.QtWidgets import QApplication

from cv_sorter.ui.theme import apply_app_styles
from cv_sorter.ui_main import VentanaPrincipal
from cv_sorter.utils import ruta_logo_app


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_app_styles(app)

    ventana = VentanaPrincipal("OVEUN | CV Console", str(ruta_logo_app()))
    ventana.show()

    sys.exit(app.exec())
