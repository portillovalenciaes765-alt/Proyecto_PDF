# Script: importar_catalogo.py
import pandas as pd
import sqlite3
from config import DB_FILE

EXCEL_FILE = r"C:\Users\carlo\OneDrive\Proyecto_PDF\FORMULARIO CERTIFICADO CALEFACCION UNIFICADO_FORMULARIO EXCEL (1).xlsm"
SHEET_NAME = "BASEDATOSEQUIPOS"
TABLE_NAME = "Equipos"

def importar_excel_a_db():
    """Lee el archivo de Excel y vuelca los datos en la tabla SQLite."""
    conn = None
    try:
        print(f"Leyendo la hoja '{SHEET_NAME}' del archivo '{EXCEL_FILE}'...")
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df.columns = df.columns.str.replace(r'[\s/().,]', '_', regex=True).str.replace(r'%', 'porc', regex=True)
        print("Lectura de Excel completada con éxito.")

        conn = sqlite3.connect(DB_FILE)
        
        print(f"Cargando datos en la tabla '{TABLE_NAME}' de la base de datos...")
        df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
        
        print("\n¡Éxito! El catálogo de equipos ha sido importado a la base de datos.")
        print(f"Puedes verificar la tabla '{TABLE_NAME}' en tu archivo '{DB_FILE}'.")
        return True

    except Exception as e:
        print(f"\nHa ocurrido un error durante la importación: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    importar_excel_a_db()