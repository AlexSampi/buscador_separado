
import sys

from PySide6.QtWidgets import QApplication

from cv_sorter.ui.theme import apply_app_styles
from cv_sorter.ui_main import VentanaPrincipal


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_app_styles(app)

    ventana = VentanaPrincipal("Organización de CV", "logo.jpg")
    ventana.show()

    sys.exit(app.exec())
