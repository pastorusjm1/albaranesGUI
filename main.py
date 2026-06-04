import sys
from PyQt6.QtWidgets import QApplication
from database import inicializar_base_datos
from gui import VentanaPrincipal

if __name__ == "__main__":
    inicializar_base_datos()
    
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
