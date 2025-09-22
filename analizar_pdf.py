import sqlite3
import os
from datetime import datetime

from pypdf import PdfReader, PdfWriter

# --- CONFIGURACIÓN ---
DB_FILE = "proyectos.db"
PDF_TEMPLATE_PATH = "formulario_campos_unicos.pdf" # Apuntamos a tu PDF con campos únicos
OUTPUT_FOLDER = "PDFs_Rellenados"

# --- FUNCIONES DE BASE DE DATOS ---

def obtener_datos_constantes(cursor):
    """Obtiene los datos fijos de la empresa, instalador y persona autorizada."""
    datos_const = {}
    try:
        cursor.execute("SELECT * FROM EmpresaInstaladora WHERE id = 1")
        datos_const['empresa'] = cursor.fetchone()
        cursor.execute("SELECT * FROM InstaladorHabilitado WHERE id = 1")
        datos_const['instalador'] = cursor.fetchone()
        cursor.execute("SELECT * FROM PersonaAutorizadaTramitacion WHERE id = 1")
        datos_const['persona_autorizada'] = cursor.fetchone()
    except sqlite3.OperationalError as e:
        print(f"Error al leer tablas constantes: {e}. ¿Ejecutaste el script para crear/actualizar las tablas?")
        return None
    return datos_const

def obtener_datos_equipo(cursor, marca, modelo):
    """Obtiene la fila completa de datos para un equipo específico."""
    cursor.execute("SELECT * FROM Equipos WHERE Marca = ? AND Modelo = ?", (marca, modelo))
    return cursor.fetchone()

def guardar_proyecto_en_db(cursor, datos_proyecto):
    """Guarda un nuevo proyecto en la tabla 'proyectos' y devuelve su ID."""
    # Filtrar claves que no existen como columnas en la tabla 'proyectos'
    cursor.execute("PRAGMA table_info(proyectos)")
    columnas_validas = {row[1] for row in cursor.fetchall()}
    
    datos_a_insertar = {key: value for key, value in datos_proyecto.items() if key in columnas_validas}
    
    columnas = ', '.join(datos_a_insertar.keys())
    placeholders = ', '.join(['?'] * len(datos_a_insertar))
    sql = f"INSERT INTO proyectos ({columnas}) VALUES ({placeholders})"
    valores = tuple(datos_a_insertar.values())
    
    cursor.execute(sql, valores)
    return cursor.lastrowid

# --- FUNCIÓN PRINCIPAL DE RELLENADO ---

def rellenar_pdf_final(project_id):
    """Lee toda la información de la DB para un ID de proyecto y rellena el PDF."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        datos_fijos = obtener_datos_constantes(cursor)
        if not datos_fijos or not datos_fijos.get('empresa'):
            print("Error fatal: No se pudieron cargar los datos constantes. Ejecuta 'cargar_datos_empresa.py'")
            return
            
        cursor.execute("SELECT * FROM proyectos WHERE id = ?", (project_id,))
        proyecto = cursor.fetchone()
        if not proyecto:
            print(f"Error: No se encontró el proyecto con ID {project_id}.")
            return

        mapa_de_datos = {}
        
        # --- MAPEO DE DATOS CONSTANTES (SECCIONES 4, 5, 14) ---
        # Persona Autorizada (Sección 4)
        pa = datos_fijos['persona_autorizada']
        mapa_de_datos.update({
            'S4_AUTORIZADO_NIF': pa['nif'], 'S4_AUTORIZADO_NOMBRE': pa['nombre'],
            'S4_AUTORIZADO_APELLIDO1': pa['apellido1'], 'S4_AUTORIZADO_APELLIDO2': pa['apellido2'],
            'S4_AUTORIZADO_CORREO': pa['email'], 'S4_AUTORIZADO_TIPOVIA': pa['direccion_tipo_via'],
            'S4_AUTORIZADO_NOMBREVIA': pa['direccion_nombre_via'], 'S4_AUTORIZADO_Nº': pa['direccion_numero'],
            'S4_AUTORIZADO_PISO': pa['direccion_piso'], 'S4_AUTORIZADO_PUERTA': pa['direccion_puerta'],
            'S4_AUTORIZADO_LOCALIDAD': pa['direccion_localidad'], 'S4_AUTORIZADO_PROVINCIA': pa['direccion_provincia'],
            'S4_AUTORIZADO_CP': pa['direccion_cp'], 'S4_AUTORIZADO_MOVIL': pa['telefono_movil']
        })
        
        # Empresa Instaladora (Sección 5)
        ei = datos_fijos['empresa']
        mapa_de_datos.update({
            'S5_EMPRESA_NIF': ei['nif'], 'S5_EMPRESA_NOMBRE': ei['razon_social'],
            'S5_EMPRESA_CORREO': ei['email'], 'S5_EMPRESA_TIPOVIA': ei['direccion_tipo_via'],
            'S5_EMPRESA_NOMBREVIA': ei['direccion_nombre_via'], 'S5_EMPRESA_Nº': ei['direccion_numero'],
            'S5_EMPRESA_PUERTA': ei['direccion_puerta'], 'S5_EMPRESA_LOCALIDAD': ei['direccion_localidad'],
            'S5_EMPRESA_PROVINCIA': ei['direccion_provincia'], 'S5_EMPRESA_CP': ei['direccion_cp'],
            'S5_EMPRESA_TELEFONO': ei['telefono_fijo'], 'S5_EMPRESA_MOVIL': ei['telefono_movil']
        })
        
        # Instalador Habilitado (Sección 5 y 14)
        ih = datos_fijos['instalador']
        mapa_de_datos.update({
            'S5_INSTALADOR_NIF': ih['nif'], 'S5_INSTALADOR_NOMBRE': ih['nombre'],
            'S5_INSTALADOR_APELLIDO1': ih['apellido1'], 'S5_INSTALADOR_APELLIDO2': ih['apellido2'],
            'S5_INSTALADOR_CORREO': ih['email'], 'S5_INSTALADOR_NºCARNE': ih['num_carne'],
            'S5_INSTALADOR_CCAAEXPIDECARNE': ih['ccaa_expide_carne'],
            'S14MEMORIA_ProfeInstalador_NOMBRE': f"{ih['nombre']} {ih['apellido1']} {ih['apellido2']}",
            'S14MEMORIA_ProfeInstalador_NIF': ih['nif'],
            'S14MEMORIA_TecTitulCompet_NOMBRE': f"{ih['nombre']} {ih['apellido1']} {ih['apellido2']}",
            'S14MEMORIA_TecTitulCompet_NIF': ih['nif']
        })
        
        # --- MAPEO DE DATOS DEL PROYECTO (SECCIONES 1, 2, 3) ---
        mapa_de_datos.update({
            'S1_TITULAR_NIF': proyecto['titular_nif_cif'], 'S1_TITULAR_NOMBRE': proyecto['titular_nombre'] or '',
            'S1_TITULAR_APELLIDO1': proyecto['titular_apellido1'] or '', 'S1_TITULAR_APELLIDO2': proyecto['titular_apellido2'] or '',
            'S1_TITULAR_RAZONSOCIAL': proyecto['titular_razon_social'] or '', 'S1_TITULAR_CORREO': proyecto['titular_email'],
            'S1_TITULAR_TIPOVIA': proyecto['titular_dir_tipo_via'], 'S1_TITULAR_NOMBREVIA': proyecto['titular_dir_nombre_via'],
            'S1_TITULAR_Nº': proyecto['titular_dir_numero'], 'S1_TITULAR_PISO': proyecto['titular_dir_piso'],
            'S1_TITULAR_PUERTA': proyecto['titular_dir_puerta'], 'S1_TITULAR_LOCALIDAD': proyecto['titular_dir_localidad'],
            'S1_TITULAR_PROVINCIA': proyecto['titular_dir_provincia'], 'S1_TITULAR_CP': proyecto['titular_dir_cp'],
            'S1_TITULAR_MOVIL': proyecto['titular_tel_movil'], 'S1_TITULAR_TELEFONO': proyecto['titular_tel_fijo'],
            
            'S2_REP_NIF': proyecto['representante_nif'] or '', 'S2_REP_NOMBRE': proyecto['representante_nombre'] or '',
            # ... resto de campos del representante ...
            
            'S3_UBICACIONINSTALACION_TIPOVIA': proyecto['ubicacion_dir_tipo_via'],
            'S3_UBICACIONINSTALACION_NOMBRE': proyecto['ubicacion_dir_nombre_via'],
            'S3_UBICACIONINSTALACION_Nº': proyecto['ubicacion_dir_numero'],
            # ... resto de campos de ubicación ...
            'S3_UBICACIONINSTALACION_LOCALIDAD': proyecto['ubicacion_dir_localidad'],
            'S3_UBICACIONINSTALACION_PROVINCIA': proyecto['ubicacion_dir_provincia'],
            'S3_UBICACIONINSTALACION_CP': proyecto['ubicacion_dir_cp'],
        })

        # --- SECCIÓN 8: Documentación Aportada (Lógica Fija) ---
        mapa_de_datos.update({
            'S8_Tasa': '/On', 'S8_Tarifa': '/On', 'S8_MEMORIA': '/On', 'S8_ManUsoyMant': '/On'
        })

        # --- SECCIÓN FIRMA (Página 4) ---
        fecha_obj = datetime.strptime(proyecto['fecha_firma'], "%d/%m/%Y")
        mapa_de_datos.update({
            'S8_FIRMA_LOCALIDAD': ei['direccion_localidad'],
            'S8_FIRMA_DIA': fecha_obj.strftime("%d"),
            'S8_FIRMA_MES': fecha_obj.strftime("%B").upper(),
            'S8_FIRMA_AÑO': fecha_obj.strftime("%Y"),
            'S14MEMORIA_ProfeInstalador_Fecha': proyecto['fecha_firma'],
            'S14MEMORIA_TecTituCompet_Fecha': proyecto['fecha_firma']
        })

        # --- SECCIÓN MEMORIA TÉCNICA (PÁGINA 5 EN ADELANTE) ---
        # ¡Aquí viene toda la lógica que definimos!
        # ... (Toda la lógica de mapeo condicional iría aquí) ...
        # Por ejemplo:
        # if proyecto['tipo_instalacion'] == 'NUEVA':
        #     mapa_de_datos['S1MEMORIA_INSTALACION_NUEVA'] = '/On'
        #     mapa_de_datos['S1MEMORIA_INSTALACION_REFORMA/AMPLIACION'] = '/Off'
        # elif proyecto['tipo_instalacion'] == 'REFORMA':
        #     mapa_de_datos['S1MEMORIA_INSTALACION_NUEVA'] = '/Off'
        #     mapa_de_datos['S1MEMORIA_INSTALACION_REFORMA/AMPLIACION'] = '/On'
        #     mapa_de_datos['S1MEMORIA_DETALLES DE LA REFORMA'] = proyecto['observaciones_reforma']
            
        # ... Esto es solo un ejemplo, hay que añadir TODA la lógica que discutimos
        # para Ventilación, Aislamiento, ACS, etc.
        
        print(f"\nGenerando PDF para el proyecto ID {project_id}...")

        # ESCRITURA DEL PDF
        writer = PdfWriter(clone_from=PdfReader(PDF_TEMPLATE_PATH))
        for page in writer.pages:
            writer.update_page_form_field_values(page, mapa_de_datos)
        
        if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
        nombre_salida = f"{proyecto['nombre_proyecto'].replace(' ', '_')}_ID_{project_id}_rellenado.pdf"
        ruta_salida = os.path.join(OUTPUT_FOLDER, nombre_salida)
        with open(ruta_salida, "wb") as output_stream:
            writer.write(output_stream)

        print("-" * 50)
        print("¡CERTIFICADO GENERADO CON ÉXITO!")
        print(f"Se ha guardado el archivo en '{ruta_salida}'")
        print("-" * 50)

    except Exception as e:
        print(f"\nHa ocurrido un error en rellenar_pdf_final: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn: conn.close()

# --- BLOQUE PRINCIPAL INTERACTIVO (EL ASISTENTE) ---
def asistente_principal():
    print("--- Asistente para la Creación de Certificados IT.3.1.5 ---")
    datos_proyecto_nuevo = {}
    
    # Este es un ASISTENTE SIMPLIFICADO para hacer una prueba.
    # No contiene todas las preguntas que definimos.
    # El objetivo es insertar un proyecto en la DB para probar rellenar_pdf_final
    
    print("\nPASO 1: DATOS DEL PROYECTO")
    datos_proyecto_nuevo['nombre_proyecto'] = input("Nombre para identificar este proyecto (ej: Reforma Calle Sol): ")
    datos_proyecto_nuevo['fecha_firma'] = input("Fecha de firma del documento (dd/mm/aaaa): ")

    print("\nPASO 2: DATOS DEL TITULAR (Sección 1)")
    datos_proyecto_nuevo['titular_tipo'] = 'Jurídica' # Asumimos Jurídica para la prueba
    datos_proyecto_nuevo['titular_nif_cif'] = "B98765432"
    datos_proyecto_nuevo['titular_razon_social'] = "Comunidad de Vecinos Test"
    datos_proyecto_nuevo['titular_nombre'] = None
    datos_proyecto_nuevo['titular_apellido1'] = None
    datos_proyecto_nuevo['titular_apellido2'] = None
    datos_proyecto_nuevo['titular_email'] = "comunidad@vecinos.test"
    datos_proyecto_nuevo['titular_tel_fijo'] = "919999999"
    datos_proyecto_nuevo['titular_tel_movil'] = "699999999"
    datos_proyecto_nuevo['titular_dir_tipo_via'] = "PASEO"
    datos_proyecto_nuevo['titular_dir_nombre_via'] = "DE LA CASTELLANA"
    datos_proyecto_nuevo['titular_dir_numero'] = "100"
    datos_proyecto_nuevo['titular_dir_piso'] = "5"
    datos_proyecto_nuevo['titular_dir_puerta'] = "D"
    datos_proyecto_nuevo['titular_dir_localidad'] = "MADRID"
    datos_proyecto_nuevo['titular_dir_provincia'] = "MADRID"
    datos_proyecto_nuevo['titular_dir_cp'] = "28046"

    # Dejamos vacíos el resto de campos que se pedirían al usuario
    campos_no_preguntados = [
        'titular_dir_bloque', 'titular_dir_portal', 'titular_dir_escalera',
        'representante_nif', 'representante_nombre', 'representante_apellido1', 'representante_apellido2',
        'representante_email', 'representante_tel_fijo', 'representante_tel_movil', 
        'representante_dir_tipo_via', 'representante_dir_nombre_via', 'representante_dir_numero',
        'representante_dir_bloque', 'representante_dir_portal', 'representante_dir_escalera',
        'representante_dir_piso', 'representante_dir_puerta', 'representante_dir_localidad',
        'representante_dir_provincia', 'representante_dir_cp',
        'ubicacion_dir_tipo_via', 'ubicacion_dir_nombre_via', 'ubicacion_dir_numero',
        'ubicacion_dir_bloque', 'ubicacion_dir_portal', 'ubicacion_dir_escalera',
        'ubicacion_dir_piso', 'ubicacion_dir_puerta', 'ubicacion_dir_localidad',
        'ubicacion_dir_provincia', 'ubicacion_dir_cp',
        'num_otros_emisores', 'equipo_marca', 'equipo_modelo'
    ]
    for campo in campos_no_preguntados:
        datos_proyecto_nuevo[campo] = None

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        nuevo_id = guardar_proyecto_en_db(cursor, datos_proyecto_nuevo)
        conn.commit()
        print(f"\nProyecto de prueba guardado en la base de datos con el ID: {nuevo_id}")
        
        rellenar_pdf_final(nuevo_id)
    except Exception as e:
        print(f"\nHa ocurrido un error en el asistente principal: {e}")
    finally:
        if conn: conn.close()

if __name__ == '__main__':
    asistente_principal()