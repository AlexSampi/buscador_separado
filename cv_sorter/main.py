import sys
import traceback

from PySide6 import QtWidgets

from cv_sorter.ui.theme import apply_app_styles
from cv_sorter.ui_main import VentanaPrincipal
from cv_sorter.utils import ruta_logo_app


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        apply_app_styles(app)

        ventana = VentanaPrincipal(
            titulo_app="OVEUN | CV Console",
            ruta_logo=str(ruta_logo_app()),
        )
        ventana.show()

        return app.exec()

    except Exception:
        traceback.print_exc()
        input("\nPulsa Enter para cerrar...")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
