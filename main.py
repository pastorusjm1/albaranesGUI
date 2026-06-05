import sys
from PyQt6.QtWidgets import QApplication
from database import inicializar_base_datos
from gui import VentanaPrincipal

import atexit
from servicio_backup import ejecutar_respaldo_completo

# Registramos el respaldo automático al salir
# Reemplaza 'gestion.db' por la ruta real de tu archivo
atexit.register(ejecutar_respaldo_completo, 'gestion.db')

# Aquí continúa tu código normal para arrancar la interfaz gráfica (GUI)
# if __name__ == "__main__":
#     ...


if __name__ == "__main__":
    inicializar_base_datos()
    
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
