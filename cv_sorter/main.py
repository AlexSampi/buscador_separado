import sys
import traceback

from PySide6 import QtWidgets

from cv_sorter.ui_main import VentanaPrincipal
from cv_sorter.utils import ruta_recurso


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)

        ventana = VentanaPrincipal(
            titulo_app="OVEUN | Organización de CV",
            ruta_logo=str(ruta_recurso("assets/logo.png"))
        )
        ventana.show()

        return app.exec()

    except Exception:
        traceback.print_exc()
        input("\nPulsa Enter para cerrar...")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())