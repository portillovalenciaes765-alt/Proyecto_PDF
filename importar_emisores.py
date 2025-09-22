# Script: importar_emisores.py
# Propósito: Leer el catálogo de emisores desde un archivo Excel
# y cargarlo en la base de datos SQLite.

import pandas as pd
import sqlite3
from config import DB_FILE

# --- CONFIGURACIÓN DE LA IMPORTACIÓN ---
EXCEL_FILE = r"C:\Users\carlo\OneDrive\Proyecto_PDF\FORMULARIO CERTIFICADO CALEFACCION UNIFICADO_FORMULARIO EXCEL (1).xlsm"
SHEET_NAME = "BASEDATOSEMISORES_DB_BROWSER"
TABLE_NAME = "Emisores"
# -----------------------------------------

def importar_emisores_a_db():
    """Lee el archivo de Excel y vuelca los datos en la tabla SQLite."""
    conn = None
    try:
        print(f"Leyendo la hoja '{SHEET_NAME}' del archivo de Excel...")
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        print("Lectura de Excel completada con éxito.")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Vaciamos la tabla antes de insertar para evitar duplicados
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        conn.commit()
        print(f"Vaciando datos antiguos de la tabla '{TABLE_NAME}'.")

        # Usamos 'append' para no perder la estructura con la columna 'id'
        df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
        
        print(f"\n¡Éxito! El catálogo de emisores ha sido importado a la tabla '{TABLE_NAME}'.")
        return True # Devuelve True si todo fue bien

    except Exception as e:
        print(f"\nHa ocurrido un error durante la importación de emisores: {e}")
        return False # Devuelve False si hubo un error
    finally:
        if conn:
            conn.close()