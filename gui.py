from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel,
    QHBoxLayout, QLineEdit, QSpinBox, QPushButton, QMessageBox, QGroupBox,
    QComboBox, QDateEdit, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox
)
from PyQt6.QtCore import QDate, Qt  # <-- ¡ESTA ES LA LÍNEA CRUCIAL!

from database import (
    realizar_copia_seguridad, 
    insertar_proveedor, 
    obtener_proveedores_combo, 
    insertar_albaran,
    obtener_10_ultimos_albaranes,
    buscar_albaranes,
    eliminar_albaran,
    actualizar_albaran
)

class DialogoEditarAlbaran(QDialog):
    def __init__(self, parent, id_alb, fecha, nombre_prov, palb, pfinal):
        super().__init__(parent)
        self.id_alb = id_alb
        self.setWindowTitle(f"📝 Editar Albarán Nº {id_alb}")
        self.resize(400, 300)
        
        # Estilo oscuro a juego con la app principal
        self.setStyleSheet("""
            QDialog { background-color: #282a36; }
            QLabel { color: #f8f8f2; font-size: 13px; font-weight: bold; }
            QComboBox, QDateEdit, QDoubleSpinBox { 
                background-color: #44475a; color: #ffffff; 
                border: 1px solid #6272a4; border-radius: 4px; padding: 5px; 
            }
            QPushButton { background-color: #ffb86c; color: #282a36; font-weight: bold; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #ffc987; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Campo de Proveedor (informativo, o desplegable si se quiere cambiar)
        layout.addWidget(QLabel("Proveedor:"))
        self.combo_prov = QComboBox()
        layout.addWidget(self.combo_prov)
        
        # Rellenar el combo de proveedores en la ventana emergente
        from database import obtener_proveedores_combo
        proveedores = obtener_proveedores_combo()
        index_a_seleccionar = 0
        for idx, (id_p, nom) in enumerate(proveedores):
            self.combo_prov.addItem(nom, id_p)
            if nom == nombre_prov:
                index_a_seleccionar = idx
        self.combo_prov.setCurrentIndex(index_a_seleccionar)
        
        # Campo: Fecha
        layout.addWidget(QLabel("Fecha del Albarán:"))
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.fromString(fecha, "yyyy-MM-dd"))
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
        layout.addWidget(self.input_fecha)
        
        # Campo: palb
        layout.addWidget(QLabel("Precio Albarán (palb €):"))
        self.input_palb = QDoubleSpinBox()
        self.input_palb.setRange(0.00, 99999.99)
        self.input_palb.setDecimals(2)
        self.input_palb.setValue(float(palb))
        layout.addWidget(self.input_palb)
        
        # Campo: pfinal
        layout.addWidget(QLabel("Precio Final (pfinal €):"))
        self.input_pfinal = QDoubleSpinBox()
        self.input_pfinal.setRange(0.00, 99999.99)
        self.input_pfinal.setDecimals(2)
        self.input_pfinal.setValue(float(pfinal))
        layout.addWidget(self.input_pfinal)
        
        # Botones de Aceptar y Cancelar de PyQt
        layout.addStretch()
        self.botones = QDialogButtonBox(QDialogButtonBox.ButtonRole.ActionRole)
        self.btn_guardar = QPushButton("💾 Guardar Cambios")
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_cancelar.setStyleSheet("background-color: #ff5555; color: white;")
        
        self.botones.addButton(self.btn_guardar, QDialogButtonBox.ButtonRole.AcceptRole)
        self.botones.addButton(self.btn_cancelar, QDialogButtonBox.ButtonRole.RejectRole)
        
        self.botones.accepted.connect(self.accept)
        self.botones.rejected.connect(self.reject)
        layout.addWidget(self.botones)

    def obtener_valores(self):
        """Devuelve los datos modificados del formulario."""
        return (
            self.input_fecha.date().toString("yyyy-MM-dd"),
            self.combo_prov.currentData(),
            self.input_palb.value(),
            self.input_pfinal.value()
        )
class DialogoNuevoProveedor(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("🏢 Registro de Proveedores")
        self.resize(350, 250)
        self.setStyleSheet("""
            QDialog { background-color: #282a36; }
            QLabel { color: #f8f8f2; font-size: 13px; font-weight: bold; }
            QLineEdit, QSpinBox { background-color: #44475a; color: #ffffff; border: 1px solid #6272a4; border-radius: 4px; padding: 5px; }
            QPushButton { background-color: #50fa7b; color: #282a36; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #40c963; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("Nombre Comercial del Proveedor:"))
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Ej: Distribuciones Pérez")
        layout.addWidget(self.input_nombre)
        
        layout.addWidget(QLabel("Margen Comercial (Porcentaje %):"))
        self.input_margen = QSpinBox()
        self.input_margen.setRange(0, 100)
        self.input_margen.setValue(10)
        layout.addWidget(self.input_margen)
        
        layout.addStretch()
        
        self.btn_guardar = QPushButton("💾 Guardar Proveedor")
        self.btn_guardar.clicked.connect(self.guardar_logica)
        layout.addWidget(self.btn_guardar)

    def guardar_logica(self):
        nombre = self.input_nombre.text().strip()
        margen = self.input_margen.value()
        
        if not nombre:
            QMessageBox.warning(self, "Campos vacíos", "Introduce el nombre del proveedor.")
            return
            
        try:
            insertar_proveedor(nombre, margen)
            QMessageBox.information(self, "Éxito", f"Proveedor '{nombre}' registrado.")
            self.accept() # Cierra el diálogo indicando que todo fue bien
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                QMessageBox.critical(self, "Error", "Ese proveedor ya existe.")
            else:
                QMessageBox.critical(self, "Error", f"Error: {e}")


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("albaranesGUI - Control de Márgenes")
        self.resize(950, 650)
        
        # Estilo visual moderno y oscuro (Paleta tipo Dracula/Material)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QTabWidget::pane { border: 1px solid #44475a; background-color: #282a36; }
            QTabBar::tab { 
                background: #44475a; color: #f8f8f2; 
                padding: 10px 18px; font-weight: bold; 
                border-top-left-radius: 4px; border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { background: #6272a4; color: #ffffff; }
            QLabel { color: #f8f8f2; font-size: 13px; }
        """)

        # Configuración del componente central obligatorio de PyQt6
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        diseno_principal = QVBoxLayout(widget_central)

        # Contenedor de pestañas principal
        self.pestanas = QTabWidget()
        diseno_principal.addWidget(self.pestanas)

        # Inicialización de las 3 áreas de trabajo solicitadas
        self.tab_entradas = QWidget()
        self.tab_historial = QWidget()
        self.tab_reportes = QWidget()

        self.pestanas.addTab(self.tab_entradas, "📥 Introducir Datos")
        self.pestanas.addTab(self.tab_historial, "🔍 Buscar / Editar / Borrar")
        self.pestanas.addTab(self.tab_reportes, "📊 Consultas y Márgenes")

        # Construir y rellenar las interfaces correspondientes
        self.configurar_tab_entradas()
        self.configurar_tab_historial()
        self.configurar_tab_reportes_temp() # Temporal para la pestaña 3

    def configurar_tab_entradas(self):
        """Diseña la entrada de albaranes a pantalla completa con acceso secundario a proveedores."""
        layout_principal = QVBoxLayout(self.tab_entradas)
        layout_principal.setSpacing(15)
        
        # CONTENEDOR PRINCIPAL DEL ALBARÁN
        grupo_albaran = QGroupBox("📄 Registro Diario de Albaranes")
        grupo_albaran.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #8be9fd; border: 1px solid #44475a; border-radius: 6px; margin-top: 12px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; font-size: 14px; }
            QComboBox, QDateEdit, QDoubleSpinBox { background-color: #44475a; color: #ffffff; border: 1px solid #6272a4; border-radius: 4px; padding: 6px; font-size: 14px; }
        """)
        layout_alb = QVBoxLayout(grupo_albaran)
        layout_alb.setSpacing(12)
        
        # Fila para el Selector de Proveedor + Botón de añadir proveedor al lado
        layout_alb.addWidget(QLabel("Seleccionar Proveedor:"))
        layout_linea_prov = QHBoxLayout()
        
        self.combo_proveedores = QComboBox()
        layout_linea_prov.addWidget(self.combo_proveedores, stretch=4) # Ocupa el 80% del ancho
        
        self.btn_abrir_prov = QPushButton("⚙️ Gestionar Proveedores")
        self.btn_abrir_prov.setStyleSheet("""
            QPushButton { background-color: #6272a4; color: white; font-weight: bold; padding: 6px; border-radius: 4px; border: none; }
            QPushButton:hover { background-color: #44475a; }
        """)
        self.btn_abrir_prov.clicked.connect(self.abrir_ventana_proveedores)
        layout_linea_prov.addWidget(self.btn_abrir_prov, stretch=1) # Ocupa el 20%
        
        layout_alb.addLayout(layout_linea_prov)
        
        # Campo: Fecha
        layout_alb.addWidget(QLabel("Fecha del Albarán:"))
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDate.currentDate())
        self.input_fecha.setDisplayFormat("yyyy-MM-dd")
        layout_alb.addWidget(self.input_fecha)
        
        # Campo: palb
        layout_alb.addWidget(QLabel("Precio Albarán (palb €):"))
        self.input_palb = QDoubleSpinBox()
        self.input_palb.setRange(0.00, 99999.99)
        self.input_palb.setDecimals(2)
        layout_alb.addWidget(self.input_palb)
        
        # Campo: pfinal
        layout_alb.addWidget(QLabel("Precio Final (pfinal €):"))
        self.input_pfinal = QDoubleSpinBox()
        self.input_pfinal.setRange(0.00, 99999.99)
        self.input_pfinal.setDecimals(2)
        layout_alb.addWidget(self.input_pfinal)
        
        layout_alb.addStretch()
        
        # Botón guardar Albarán
        self.btn_guardar_alb = QPushButton("💾 Guardar Albarán")
        self.btn_guardar_alb.setStyleSheet("""
            QPushButton { background-color: #8be9fd; color: #282a36; font-weight: bold; padding: 10px; border-radius: 4px; border: none; font-size: 14px; }
            QPushButton:hover { background-color: #78d1e1; }
        """)
        self.btn_guardar_alb.clicked.connect(self.guardar_albaran_logica)
        layout_alb.addWidget(self.btn_guardar_alb)
        
        layout_principal.addWidget(grupo_albaran)
        
        # Cargar los datos iniciales
        self.actualizar_combo_proveedores()
    

    def actualizar_combo_proveedores(self):
        """Sincroniza el menú desplegable con los proveedores reales de la BD."""
        self.combo_proveedores.clear()
        proveedores = obtener_proveedores_combo()
        
        if not proveedores:
            self.combo_proveedores.addItem("-- Registra un proveedor primero --", None)
            return
            
        for id_prov, nombre in proveedores:
            self.combo_proveedores.addItem(nombre, id_prov)

    def abrir_ventana_proveedores(self):
        """Abre la ventana flotante de proveedores y actualiza los desplegables al cerrar."""
        dialogo = DialogoNuevoProveedor(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            # Si guardó un proveedor con éxito, refrescamos los desplegables inmediatamente
            self.actualizar_combo_proveedores()
            self.actualizar_combo_busqueda()
    
    def guardar_albaran_logica(self):
        """Valida y guarda el albarán en la base de datos."""
        id_prov = self.combo_proveedores.currentData()
        
        if id_prov is None:
            QMessageBox.warning(self, "Error", "Debes seleccionar un proveedor válido.")
            return
            
        fecha = self.input_fecha.date().toString("yyyy-MM-dd")
        palb = self.input_palb.value()
        pfinal = self.input_pfinal.value()
        
        if palb <= 0 or pfinal <= 0:
            QMessageBox.warning(self, "Valores incorrectos", "Los precios decimales deben ser superiores a 0.00 €.")
            return
            
        try:
            insertar_albaran(fecha, id_prov, palb, pfinal)
            QMessageBox.information(self, "Éxito", "Albarán guardado correctamente.")
            
            # Restablecer precios a cero manteniendo la fecha de hoy
            self.input_palb.setValue(0.00)
            self.input_pfinal.setValue(0.00)
            self.cargar_datos_reportes()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo registrar el albarán: {e}")

    def configurar_tabs_pendientes(self):
        """Estructura marcadores de posición visuales para el siguiente paso del desarrollo."""
        # Pestaña 2
        lay_h = QVBoxLayout(self.tab_historial)
        lbl_h = QLabel("Próximo objetivo:\nAquí crearemos la tabla para mostrar y buscar los últimos 10 albaranes.")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_h.addWidget(lbl_h)

        # Pestaña 3
        lay_r = QVBoxLayout(self.tab_reportes)

    def configurar_tab_historial(self):
        """Diseña la pestaña de historial con filtros de búsqueda, tabla y acciones de edición/borrado."""
        layout_principal = QVBoxLayout(self.tab_historial)
        layout_principal.setSpacing(10)
        
        # ----------------------------------------------------
        # BLOQUE SUPERIOR: FILTROS DE BÚSQUEDA
        # ----------------------------------------------------
        grupo_filtros = QGroupBox("🔍 Filtrar y Buscar Albaranes")
        grupo_filtros.setStyleSheet("""
            QGroupBox { font-weight: bold; color: #f1fa8c; border: 1px solid #44475a; border-radius: 6px; margin-top: 5px; }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 3px; }
            QComboBox, QDateEdit { background-color: #44475a; color: #ffffff; border: 1px solid #6272a4; border-radius: 4px; padding: 3px; }
        """)
        layout_filtros = QHBoxLayout(grupo_filtros)
        
        # Filtro Proveedor
        layout_filtros.addWidget(QLabel("Proveedor:"))
        self.combo_buscar_prov = QComboBox()
        layout_filtros.addWidget(self.combo_buscar_prov)
        
        # Filtro Fecha Inicio
        layout_filtros.addWidget(QLabel("Desde:"))
        self.buscar_fecha_inicio = QDateEdit()
        self.buscar_fecha_inicio.setCalendarPopup(True)
        self.buscar_fecha_inicio.setDate(QDate.currentDate().addMonths(-1)) # Hace un mes por defecto
        self.buscar_fecha_inicio.setDisplayFormat("yyyy-MM-dd")
        layout_filtros.addWidget(self.buscar_fecha_inicio)
        
        # Filtro Fecha Fin
        layout_filtros.addWidget(QLabel("Hasta:"))
        self.buscar_fecha_fin = QDateEdit()
        self.buscar_fecha_fin.setCalendarPopup(True)
        self.buscar_fecha_fin.setDate(QDate.currentDate())
        self.buscar_fecha_fin.setDisplayFormat("yyyy-MM-dd")
        layout_filtros.addWidget(self.buscar_fecha_fin)
        
        # Botón Buscar
        self.btn_buscar = QPushButton("🔍 Buscar")
        self.btn_buscar.setStyleSheet("background-color: #f1fa8c; color: #282a36; font-weight: bold; padding: 5px 15px; border-radius: 4px;")
        self.btn_buscar.clicked.connect(self.ejecutar_busqueda_logica)
        layout_filtros.addWidget(self.btn_buscar)
        
        # Botón Mostrar Últimos 10 (Restablecer)
        self.btn_ver_ultimos = QPushButton("🔄 Ver Últimos 10")
        self.btn_ver_ultimos.setStyleSheet("background-color: #6272a4; color: #ffffff; padding: 5px 10px; border-radius: 4px;")
        self.btn_ver_ultimos.clicked.connect(self.cargar_10_ultimos_albaranes)
        layout_filtros.addWidget(self.btn_ver_ultimos)
        
        layout_principal.addWidget(grupo_filtros)
        
        # ----------------------------------------------------
        # BLOQUE CENTRAL: TABLA DE DATOS
        # ----------------------------------------------------
        self.tabla_albaranes = QTableWidget()
        self.tabla_albaranes.setColumnCount(5)
        self.tabla_albaranes.setHorizontalHeaderLabels(["ID", "Fecha", "Proveedor", "palb (€)", "pfinal (€)"])
        self.tabla_albaranes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ocultar la columna ID para que no sature visualmente, pero la usaremos internamente
        self.tabla_albaranes.setColumnHidden(0, False) # Ponlo en True si prefieres ocultarla
        
        self.tabla_albaranes.setStyleSheet("""
            QTableWidget { background-color: #21222c; color: #f8f8f2; gridline-color: #44475a; border: 1px solid #44475a; }
            QHeaderView::section { background-color: #44475a; color: #ffffff; padding: 5px; font-weight: bold; border: 1px solid #282a36; }
        """)
        layout_principal.addWidget(self.tabla_albaranes)
        
        # ----------------------------------------------------
        # BLOQUE INFERIOR: ACCIONES (EDITAR / BORRAR)
        # ----------------------------------------------------
        layout_acciones = QHBoxLayout()
        
        self.btn_editar_alb = QPushButton("📝 Editar Seleccionado")
        self.btn_editar_alb.setStyleSheet("background-color: #ffb86c; color: #282a36; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.btn_editar_alb.clicked.connect(self.editar_albaran_logica)
        
        self.btn_borrar_alb = QPushButton("🗑️ Borrar Seleccionado")
        self.btn_borrar_alb.setStyleSheet("background-color: #ff5555; color: #ffffff; font-weight: bold; padding: 8px; border-radius: 4px;")
        self.btn_borrar_alb.clicked.connect(self.borrar_albaran_logica)
        
        layout_acciones.addWidget(self.btn_editar_alb)
        layout_acciones.addWidget(self.btn_borrar_alb)
        layout_principal.addLayout(layout_acciones)
        
        # Cargar los buscadores y los datos iniciales
        self.actualizar_combo_busqueda()
        self.cargar_10_ultimos_albaranes()

    def actualizar_combo_busqueda(self):
        """Llena el combo de búsqueda de proveedores."""
        self.combo_buscar_prov.clear()
        proveedores = obtener_proveedores_combo()
        for id_prov, nombre in proveedores:
            self.combo_buscar_prov.addItem(nombre, id_prov)

    def rellenar_tabla(self, lista_albaranes):
        """Función interna reutilizable para pintar filas en la tabla."""
        self.tabla_albaranes.setRowCount(0)
        for fila_idx, albaran in enumerate(lista_albaranes):
            self.tabla_albaranes.insertRow(fila_idx)
            for col_idx, valor in enumerate(albaran):
                celda = QTableWidgetItem(str(valor))
                celda.setFlags(celda.flags() ^ Qt.ItemFlag.ItemIsEditable) # Celdas de solo lectura
                self.tabla_albaranes.setItem(fila_idx, col_idx, celda)

    def cargar_10_ultimos_albaranes(self):
        """Muestra de forma automática los 10 últimos registros."""
        albaranes = obtener_10_ultimos_albaranes()
        self.rellenar_tabla(albaranes)

    def ejecutar_busqueda_logica(self):
        """Busca albaranes aplicando los filtros seleccionados."""
        id_prov = self.combo_buscar_prov.currentData()
        f_inicio = self.buscar_fecha_inicio.date().toString("yyyy-MM-dd")
        f_fin = self.buscar_fecha_fin.date().toString("yyyy-MM-dd")
        
        if id_prov is None:
            QMessageBox.warning(self, "Atención", "Selecciona un proveedor válido para buscar.")
            return
            
        resultados = buscar_albaranes(id_prov, f_inicio, f_fin)
        self.rellenar_tabla(resultados)
        if not resultados:
            QMessageBox.information(self, "Búsqueda", "No se encontraron albaranes en ese rango de fechas.")

    def borrar_albaran_logica(self):
        """Borra la fila seleccionada de la tabla tras confirmación."""
        fila_seleccionada = self.tabla_albaranes.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección vacía", "Por favor, haz clic en una fila de la tabla para borrar.")
            return
            
        id_alb = int(self.tabla_albaranes.item(fila_seleccionada, 0).text())
        confirmacion = QMessageBox.question(
            self, "Confirmar borrado", 
            "¿Estás completamente seguro de eliminar este albaran? Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            eliminar_albaran(id_alb)
            QMessageBox.information(self, "Eliminado", "El albarán ha sido borrado.")
            self.cargar_10_ultimos_albaranes() # Refrescar

    def editar_albaran_logica(self):
        """Abre el diálogo emergente para modificar el albarán seleccionado."""
        fila_seleccionada = self.tabla_albaranes.currentRow()
        if fila_seleccionada == -1:
            QMessageBox.warning(self, "Selección vacía", "Selecciona un albarán de la tabla para editar.")
            return
            
            # Extraemos los datos actuales directamente de la fila seleccionada de la tabla
            id_alb = int(self.tabla_albaranes.item(fila_seleccionada, 0).text())
            fecha = self.tabla_albaranes.item(fila_seleccionada, 1).text()
            nombre_prov = self.tabla_albaranes.item(fila_seleccionada, 2).text()
            palb = self.tabla_albaranes.item(fila_seleccionada, 3).text()
            pfinal = self.tabla_albaranes.item(fila_seleccionada, 4).text()
        
            # Inicializamos nuestra nueva ventana emergente pasándole estos datos
            dialogo = DialogoEditarAlbaran(self, id_alb, fecha, nombre_prov, palb, pfinal)
        
            # Si el usuario pulsa "Guardar Cambios" (.exec() devuelve 1 si se acepta)
            if dialogo.exec() == QDialog.DialogCode.Accepted:
                nueva_fecha, nuevo_id_prov, nuevo_palb, nuevo_pfinal = dialogo.obtener_valores()
            
                if nuevo_palb <= 0 or nuevo_pfinal <= 0:
                    QMessageBox.warning(self, "Valores incorrectos", "Los precios deben ser mayores a 0.00 €.")
                    return
                
                try:
                    # Guardamos los cambios en la base de datos usando SQL directo
                    from database import actualizar_albaran
                    actualizar_albaran(id_alb, nueva_fecha, nuevo_id_prov, nuevo_palb, nuevo_pfinal)
                
                    QMessageBox.information(self, "Éxito", "Albarán actualizado correctamente.")
                
                    # Refrescamos la tabla para ver los cambios reflejados al instante
                    self.cargar_10_ultimos_albaranes()
                    self.cargar_datos_reportes()
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudieron salvar los cambios: {e}")


    def configurar_tab_reportes_temp(self):
        """Diseña la interfaz de análisis financiero con los totales y márgenes agrupados."""
        # Nota: Mantenemos el nombre original del método para no romper la llamada del __init__
        layout_principal = QVBoxLayout(self.tab_reportes)
        layout_principal.setSpacing(15)

        # Botón superior para refrescar los informes
        self.btn_actualizar_reportes = QPushButton("📊 Actualizar Balances Financieros")
        self.btn_actualizar_reportes.setStyleSheet("""
            QPushButton { background-color: #6272a4; color: white; font-weight: bold; padding: 10px; border-radius: 4px; border: none; font-size: 13px; }
            QPushButton:hover { background-color: #44475a; }
        """)
        self.btn_actualizar_reportes.clicked.connect(self.cargar_datos_reportes)
        layout_principal.addWidget(self.btn_actualizar_reportes)

        # Contenedor horizontal para dividir Meses y Años lado a lado
        layout_bloque_fechas = QHBoxLayout()
        layout_bloque_fechas.setSpacing(15)

        # TABLA 1: TOTALES POR MES
        grupo_mes = QGroupBox("📅 Totales Mensuales")
        grupo_mes.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; color: #ff79c6; 
                border: 1px solid #44475a; border-radius: 6px; 
                padding-top: 25px;  /* Emplaza la tabla hacia abajo para no tapar el título */
            } 
            QGroupBox::title { subcontrol-origin: margin; left: 10px; top: 5px; }
        """)
        lay_mes = QVBoxLayout(grupo_mes)
        self.tabla_meses = QTableWidget()
        self.tabla_meses.setColumnCount(3)
        self.tabla_meses.setHorizontalHeaderLabels(["Mes", "Suma PAlb (€)", "Suma PFinal (€)"])
        self.tabla_meses.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_meses.setStyleSheet("QTableWidget { background-color: #21222c; color: #f8f8f2; gridline-color: #44475a; }")
        lay_mes.addWidget(self.tabla_meses)
        layout_bloque_fechas.addWidget(grupo_mes)

        # TABLA 2: TOTALES POR AÑO
        grupo_ano = QGroupBox("📆 Totales Anuales")
        grupo_ano.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; color: #ffb86c; 
                border: 1px solid #44475a; border-radius: 6px; 
                padding-top: 25px;  /* Emplaza la tabla hacia abajo para no tapar el título */
            } 
            QGroupBox::title { subcontrol-origin: margin; left: 10px; top: 5px; }
        """)
        lay_ano = QVBoxLayout(grupo_ano)
        self.tabla_anos = QTableWidget()
        self.tabla_anos.setColumnCount(3)
        self.tabla_anos.setHorizontalHeaderLabels(["Año", "Suma PAlb (€)", "Suma PFinal (€)"])
        self.tabla_anos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_anos.setStyleSheet("QTableWidget { background-color: #21222c; color: #f8f8f2; gridline-color: #44475a; }")
        lay_ano.addWidget(self.tabla_anos)
        layout_bloque_fechas.addWidget(grupo_ano)

        layout_principal.addLayout(layout_bloque_fechas)

        # TABLA 3: RESUMEN DE MÁRGENES POR PROVEEDOR
        grupo_margen = QGroupBox("🏢 Rendimiento y Porcentajes de Margen por Proveedor")
        grupo_margen.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; color: #50fa7b; 
                border: 1px solid #44475a; border-radius: 6px; 
                padding-top: 25px; 
            } 
            QGroupBox::title { subcontrol-origin: margin; left: 10px; top: 5px; }
        """)
        lay_margen = QVBoxLayout(grupo_margen)
        self.tabla_margenes = QTableWidget()
        self.tabla_margenes.setColumnCount(5)
        self.tabla_margenes.setHorizontalHeaderLabels(["Proveedor", "Margen Fijo (%)", "Total PAlb (€)", "Total PFinal (€)", "Margen Real (%)"])
        self.tabla_margenes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla_margenes.setStyleSheet("QTableWidget { background-color: #21222c; color: #f8f8f2; gridline-color: #44475a; }")
        lay_margen.addWidget(self.tabla_margenes)
        
        layout_principal.addWidget(grupo_margen, stretch=2)

        # Cargar los datos automáticamente al abrir la pestaña
        self.cargar_datos_reportes()

    def cargar_datos_reportes(self):
        """Ejecuta las consultas analíticas en la BD y rellena las tres tablas de reporte."""
        from database import obtener_totales_por_mes, obtener_totales_por_ano, obtener_resumen_margen_proveedores

        # 1. Rellenar Tabla Mensual
        self.tabla_meses.setRowCount(0)
        for f_idx, fila in enumerate(obtener_totales_por_mes()):
            self.tabla_meses.insertRow(f_idx)
            for c_idx, val in enumerate(fila):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tabla_meses.setItem(f_idx, c_idx, item)

        # 2. Rellenar Tabla Anual
        self.tabla_anos.setRowCount(0)
        for f_idx, fila in enumerate(obtener_totales_por_ano()):
            self.tabla_anos.insertRow(f_idx)
            for c_idx, val in enumerate(fila):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.tabla_anos.setItem(f_idx, c_idx, item)

        # 3. Rellenar Tabla de Márgenes por Proveedor
        self.tabla_margenes.setRowCount(0)
        for f_idx, fila in enumerate(obtener_resumen_margen_proveedores()):
            self.tabla_margenes.insertRow(f_idx)
            for c_idx, val in enumerate(fila):
                # Si es el margen teórico o real, le añadimos el símbolo '%' para mejorar la lectura
                texto_celda = f"{val} %" if c_idx in [1, 4] else str(val)
                item = QTableWidgetItem(texto_celda)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                
                # Resaltado visual: Si el margen real es menor que el fijado, pintamos el texto en rojo suave
                if c_idx == 4 and len(fila) >= 2:
                    try:
                        if float(fila[4]) < float(fila[1]):
                            item.setForeground(Qt.GlobalColor.red)
                        elif float(fila[4]) > float(fila[1]):
                            item.setForeground(Qt.GlobalColor.green)
                        else: 
                            item.setForeground(Qt.GlobalColor.white)
                    except ValueError:
                        pass
                        
                self.tabla_margenes.setItem(f_idx, c_idx, item)

    
