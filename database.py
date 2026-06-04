import sqlite3
from contextlib import contextmanager
import os
import shutil
from datetime import datetime

DB_NAME = "gestion.db"
RUTA_NUBE = r"./copias_seguridad_nube" # Carpeta local que simula la nube

@contextmanager
def obtener_conexion():
    """Conexión segura con soporte para claves foráneas."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def inicializar_base_datos():
    """Crea las tablas con la estructura exacta solicitada."""
    sql_proveedor = """
    CREATE TABLE IF NOT EXISTS proveedor (
        IdProv INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        margen INTEGER NOT NULL DEFAULT 0
    );
    """
    
    sql_albaran = """
    CREATE TABLE IF NOT EXISTS albaran (
        IdAlb INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        IdProv INTEGER NOT NULL,
        palb REAL NOT NULL,
        pfinal REAL NOT NULL,
        FOREIGN KEY (IdProv) REFERENCES proveedor(IdProv) ON DELETE CASCADE
    );
    """
    
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql_proveedor)
        cursor.execute(sql_albaran)
        print("Base de datos reiniciada con la nueva estructura.")

def realizar_copia_seguridad():
    """Respaldo automático al cerrar la aplicación."""
    if not os.path.exists(DB_NAME):
        return
    if not os.path.exists(RUTA_NUBE):
        os.makedirs(RUTA_NUBE)
        
    fecha_hoy = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_backup = f"gestion_{fecha_hoy}.db"
    ruta_destino = os.path.join(RUTA_NUBE, nombre_backup)
    
    try:
        shutil.copy2(DB_NAME, ruta_destino)
        print(f"✅ Copia de seguridad guardada en: {ruta_destino}")
    except Exception as e:
        print(f"❌ Error en copia de seguridad: {e}")

def obtener_10_ultimos_albaranes():
    """Trae los 10 últimos albaranes ordenados por fecha descendente, incluyendo el nombre del proveedor."""
    sql = """
    SELECT a.IdAlb, a.fecha, p.nombre, a.palb, a.pfinal 
    FROM albaran a
    JOIN proveedor p ON a.IdProv = p.IdProv
    ORDER BY a.fecha DESC
    LIMIT 10
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

def buscar_albaranes(id_prov, fecha_inicio, fecha_fin):
    """Busca albaranes de un proveedor específico entre un rango de fechas."""
    sql = """
    SELECT a.IdAlb, a.fecha, p.nombre, a.palb, a.pfinal 
    FROM albaran a
    JOIN proveedor p ON a.IdProv = p.IdProv
    WHERE a.IdProv = ? AND a.fecha BETWEEN ? AND ?
    ORDER BY a.fecha DESC
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (id_prov, fecha_inicio, fecha_fin))
        return cursor.fetchall()

def obtener_proveedores_combo():
    """Trae ID y Nombre de los proveedores para rellenar los desplegables (ComboBox)."""
    sql = "SELECT IdProv, nombre FROM proveedor ORDER BY nombre ASC"
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    
def insertar_proveedor(nombre, margen):
    """Inserta un nuevo proveedor en la base de datos usando consultas parametrizadas."""
    sql = "INSERT INTO proveedor (nombre, margen) VALUES (?, ?)"
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (nombre, margen))

def insertar_albaran(fecha, id_prov, palb, pfinal):
    """Inserta un albarán en la base de datos vinculándolo a un proveedor."""
    sql = "INSERT INTO albaran (fecha, IdProv, palb, pfinal) VALUES (?, ?, ?, ?)"
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (fecha, id_prov, palb, pfinal))

def eliminar_albaran(id_alb):
    """Elimina un albarán por su ID único."""
    sql = "DELETE FROM albaran WHERE IdAlb = ?"
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (id_alb,))

def actualizar_albaran(id_alb, fecha, id_prov, palb, pfinal):
    """Actualiza todos los datos de un albarán existente."""
    sql = """
    UPDATE albaran 
    SET fecha = ?, IdProv = ?, palb = ?, pfinal = ? 
    WHERE IdAlb = ?
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (fecha, id_prov, palb, pfinal, id_alb))

def obtener_totales_por_mes():
    """Calcula las sumas de palb y pfinal agrupadas por Año y Mes."""
    sql = """
    SELECT strftime('%Y-%m', fecha) as mes,
           ROUND(SUM(palb), 2),
           ROUND(SUM(pfinal), 2)
    FROM albaran
    GROUP BY mes
    ORDER BY mes DESC
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

def obtener_totales_por_ano():
    """Calcula las sumas de palb y pfinal agrupadas por Año."""
    sql = """
    SELECT strftime('%Y', fecha) as ano,
           ROUND(SUM(palb), 2),
           ROUND(SUM(pfinal), 2)
    FROM albaran
    GROUP BY ano
    ORDER BY ano DESC
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

def obtener_resumen_margen_proveedores():
    """
    Calcula el margen real obtenido por proveedor basado en los albaranes introducidos.
    Fórmula: ((Suma PFinal - Suma PAlb) / Suma PFinal) * 100
    """
    sql = """
    SELECT p.nombre,
           p.margen as margen_teorico,
           ROUND(SUM(a.palb), 2) as total_palb,
           ROUND(SUM(a.pfinal), 2) as total_pfinal,
           ROUND(((SUM(a.pfinal) - (SUM(a.palb) * 1.07)) / SUM(a.pfinal)) * 100, 2) as margen_real
    FROM albaran a
    JOIN proveedor p ON a.IdProv = p.IdProv
    GROUP BY p.IdProv
    ORDER BY margen_real DESC
    """
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()


