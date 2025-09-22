# Módulo: main.py
# Responsabilidad: Orquestar todo el flujo de trabajo del programa.

import sqlite3
import os
from config import DB_FILE, PDF_TEMPLATE_PATH, OUTPUT_FOLDER 

# Importamos las funciones principales de nuestros otros módulos
# NUEVO: añadimos 'guardar_locales_proyecto'
from database_manager import preparar_base_de_datos, cargar_datos_constantes, guardar_proyecto_en_db, guardar_locales_proyecto
from asistente_io import asistente_principal
from pdf_generator import rellenar_pdf_final

# NUEVO: importamos la función para cargar emisores
from importar_catalogo import importar_excel_a_db as importar_equipos
from importar_emisores import importar_emisores_a_db as importar_emisores

def ejecutar_flujo_completo():
    """
    Función que ejecuta todo el proceso en el orden correcto.
    """
    # --- 1. INICIALIZACIÓN Y VERIFICACIÓN DE LA BASE DE DATOS ---
    conn = None
    try:
        # Si la base de datos no existe, la crearemos
        if not os.path.exists(DB_FILE):
            print(f"Base de datos no encontrada. Creando '{DB_FILE}'...")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        preparar_base_de_datos(cursor)
        cargar_datos_constantes(cursor)
        conn.commit()

        # Verificamos si el catálogo de EQUIPOS está cargado
        cursor.execute("SELECT COUNT(*) FROM Equipos")
        if cursor.fetchone()[0] == 0:
            print("\nAVISO: Catálogo de 'Equipos' vacío. Importando desde Excel...")
            conn.close()
            if not importar_equipos():
                print("\nERROR CRÍTICO: No se pudo importar el catálogo de equipos. El programa se detendrá.")
                return
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            print("Catálogo de 'Equipos' cargado.")

        # NUEVO: Verificamos si el catálogo de EMISORES está cargado
        cursor.execute("SELECT COUNT(*) FROM Emisores")
        if cursor.fetchone()[0] == 0:
            print("\nAVISO: Catálogo de 'Emisores' vacío. Importando desde Excel...")
            conn.close()
            if not importar_emisores():
                print("\nERROR CRÍTICO: No se pudo importar el catálogo de emisores. El programa se detendrá.")
                return
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            print("Catálogo de 'Emisores' cargado.")
            
        print("-" * 50)
    except Exception as e:
        print(f"Ocurrió un error inicializando la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()
    
    # --- 2. ASISTENTE INTERACTIVO ---
    datos_del_nuevo_proyecto = asistente_principal()
    
    if not datos_del_nuevo_proyecto:
        print("\nAsistente cancelado o finalizado sin datos. No se generará ningún certificado.")
        return

    # --- 3. GUARDADO DEL NUEVO PROYECTO ---
    conn = None
    nuevo_id = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Guardamos el proyecto principal
        nuevo_id = guardar_proyecto_en_db(cursor, datos_del_nuevo_proyecto)
        
        # NUEVO: Si el asistente recogió datos de locales, los guardamos
        if 'locales' in datos_del_nuevo_proyecto and datos_del_nuevo_proyecto['locales']:
            guardar_locales_proyecto(cursor, nuevo_id, datos_del_nuevo_proyecto['locales'])
        
        conn.commit()
        print(f"\nProyecto guardado en la base de datos con el ID: {nuevo_id}")
    except Exception as e:
        print(f"\nHa ocurrido un error guardando el proyecto en la base de datos: {e}")
        return
    finally:
        if conn:
            conn.close()
            
    # --- 4. GENERACIÓN DEL PDF FINAL ---
    if nuevo_id:
        print("Iniciando la generación del PDF final...")
        rellenar_pdf_final(nuevo_id, DB_FILE, PDF_TEMPLATE_PATH, OUTPUT_FOLDER)
    else:
        print("No se pudo obtener un ID para el nuevo proyecto. No se generará el PDF.")


# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == '__main__':
    ejecutar_flujo_completo()