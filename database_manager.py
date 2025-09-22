# Módulo: database_manager.py
import sqlite3

def preparar_base_de_datos(cursor):
    """Asegura que todas las tablas necesarias existen en la base de datos."""
    # Tabla Proyectos (Tu versión completa y funcional)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_proyecto TEXT, titular_tipo TEXT,
            titular_nif_cif TEXT, titular_razon_social TEXT, titular_nombre TEXT, titular_apellido1 TEXT,
            titular_apellido2 TEXT, titular_email TEXT, titular_tel_fijo TEXT, titular_tel_movil TEXT,
            titular_dir_tipo_via TEXT, titular_dir_nombre_via TEXT, titular_dir_numero TEXT,
            titular_dir_bloque TEXT, titular_dir_portal TEXT, titular_dir_escalera TEXT,
            titular_dir_piso TEXT, titular_dir_puerta TEXT, titular_dir_localidad TEXT,
            titular_dir_provincia TEXT, titular_dir_cp TEXT, 
            representante_nif TEXT, representante_nombre TEXT, representante_apellido1 TEXT, 
            representante_apellido2 TEXT, representante_email TEXT, representante_tel_fijo TEXT,
            representante_tel_movil TEXT, representante_dir_tipo_via TEXT, representante_dir_nombre_via TEXT,
            representante_dir_numero TEXT, representante_dir_bloque TEXT, representante_dir_portal TEXT,
            representante_dir_escalera TEXT, representante_dir_piso TEXT, representante_dir_puerta TEXT,
            representante_dir_localidad TEXT, representante_dir_provincia TEXT, representante_dir_cp TEXT,
            ubicacion_dir_tipo_via TEXT, ubicacion_dir_nombre_via TEXT, ubicacion_dir_numero TEXT,
            ubicacion_dir_bloque TEXT, ubicacion_dir_portal TEXT, ubicacion_dir_escalera TEXT,
            ubicacion_dir_piso TEXT, ubicacion_dir_puerta TEXT, ubicacion_dir_localidad TEXT,
            ubicacion_dir_provincia TEXT, ubicacion_dir_cp TEXT, 
            fecha_firma TEXT, tipo_instalacion TEXT, observaciones_reforma TEXT, 
            equipo_servicio TEXT, fuente_energia TEXT, uso_edificio TEXT, uso_edificio_otros TEXT, 
            sala_maquinas_alto_riesgo TEXT, equipo_terminal TEXT, num_radiadores INTEGER, 
            num_otros_emisores INTEGER, tipo_distribucion TEXT, tipo_tuberia TEXT,
            seccion_max_tuberia TEXT, seccion_min_tuberia TEXT, tipo_conducto TEXT, equipo_marca TEXT, equipo_modelo TEXT,
            aislamiento_tuberias_mat TEXT, aislamiento_tuberias_esp TEXT,
            aislamiento_conductos_mat TEXT, aislamiento_conductos_esp TEXT,
            ventilacion_tipo TEXT, vent_directa_n_aberturas INTEGER,
            vent_directa_area_total REAL, vent_natural_n_conductos INTEGER,
            vent_natural_area_total REAL, vent_forzada_caudal REAL,
            vent_forzada_relacion REAL, vent_forzada_enclavamiento TEXT,
            num_generadores INTEGER, generacion_individualizada TEXT, emplazamiento_generador TEXT,
            lugar_ubicacion_generador TEXT,demanda_acs_litros_dia REAL,volumen_acumulacion_acs TEXT
        )''')
    
    # Tablas Constantes (Tus versiones funcionales)
    cursor.execute('''CREATE TABLE IF NOT EXISTS EmpresaInstaladora (id INTEGER PRIMARY KEY DEFAULT 1, nif TEXT, razon_social TEXT, email TEXT, direccion_tipo_via TEXT, direccion_nombre_via TEXT, direccion_numero TEXT, direccion_puerta TEXT, direccion_localidad TEXT, direccion_provincia TEXT, direccion_cp TEXT, telefono_fijo TEXT, telefono_movil TEXT, num_registro TEXT, tipo_empresa TEXT, CHECK (id = 1))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS InstaladorHabilitado (id INTEGER PRIMARY KEY DEFAULT 1, nif TEXT, nombre TEXT, apellido1 TEXT, apellido2 TEXT, num_carne TEXT, email TEXT, ccaa_expide_carne TEXT, tipo_carnet TEXT, telefono_movil TEXT, CHECK (id = 1))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS PersonaAutorizadaTramitacion (id INTEGER PRIMARY KEY DEFAULT 1, nif TEXT, nombre TEXT, apellido1 TEXT, apellido2 TEXT, email TEXT, direccion_tipo_via TEXT, direccion_nombre_via TEXT, direccion_numero TEXT, direccion_bloque TEXT, direccion_portal TEXT, direccion_escalera TEXT, direccion_piso TEXT, direccion_puerta TEXT, direccion_localidad TEXT, direccion_provincia TEXT, direccion_cp TEXT, telefono_fijo TEXT, telefono_movil TEXT, CHECK (id = 1))''')
    
    # Tabla para el catálogo de equipos (creada vacía, el importador la define)
    cursor.execute('CREATE TABLE IF NOT EXISTS Equipos (id INTEGER PRIMARY KEY)')

    # NUEVO: Tabla para el catálogo de emisores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Emisores (
        id INTEGER PRIMARY KEY AUTOINCREMENT, Marca TEXT, Modelo TEXT, Tipo_Emisor TEXT,
        Potencia_W_por_Unidad REAL, Unidad_Medida TEXT, Altura_mm REAL, Anchura_mm REAL,
        Profundidad_mm REAL, Peso_kg REAL, Presion_Max_Trabajo_Bar REAL,
        Sistema_Tipico TEXT, Orientacion TEXT
    )''')
    
    # NUEVO: Tabla para los locales de cada proyecto
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Locales_Proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT, proyecto_id INTEGER, nombre_local TEXT, planta TEXT, tipo_local TEXT,
        numero INTEGER, superficie_m2 REAL, orientacion TEXT, calculo_cargas_W REAL,
        emisor_id INTEGER, cantidad_elementos REAL, carga_real_W REAL,
        FOREIGN KEY (proyecto_id) REFERENCES proyectos (id),
        FOREIGN KEY (emisor_id) REFERENCES Emisores (id)
    )''')

    print("-> Estructura de tablas verificada/creada.")

# ... (Tu función cargar_datos_constantes se queda igual)
def cargar_datos_constantes(cursor):
    """Inserta los datos fijos si las tablas están vacías."""
    cursor.execute("SELECT COUNT(*) FROM EmpresaInstaladora")
    if cursor.fetchone()[0] == 0:
        print("-> Tablas de datos constantes vacías. Cargando datos...")
        datos_pa = {'nif': '47459611P', 'nombre': 'ROGER', 'apellido1': 'ALVA', 'apellido2': 'LEON', 'email': 'cportillo.atg@gmail.com', 'direccion_tipo_via': 'Avenida', 'direccion_nombre_via': 'LOS CASTILLOS', 'direccion_numero': '16', 'direccion_bloque': '', 'direccion_portal': '', 'direccion_escalera': '', 'direccion_piso': '6', 'direccion_puerta': 'C', 'direccion_localidad': 'ALCORCON', 'direccion_provincia': 'MADRID', 'direccion_cp': '28925', 'telefono_fijo': '', 'telefono_movil': '663250275'}
        datos_ei = {'nif': 'B86844487', 'razon_social': 'ASISTENCIA TECNICA DEL GAS SL', 'email': 'cportillo.atg@gmail.com', 'direccion_tipo_via': 'Calle', 'direccion_nombre_via': 'DEL RAYO', 'direccion_numero': '6', 'direccion_puerta': 'NAVE 18', 'direccion_localidad': 'ALCORCON', 'direccion_provincia': 'LEGANES', 'direccion_cp': '28918', 'telefono_fijo': '911124625', 'telefono_movil': '66325075', 'num_registro': '201413', 'tipo_empresa': 'EITE'}
        datos_ih = {'nif': '47459611P', 'nombre': 'ROGER', 'apellido1': 'ALVA', 'apellido2': 'LEON', 'num_carne': 'IGA 585 / ITE 3141', 'email': 'cportillo.atg@gmail.com', 'ccaa_expide_carne': 'MADRID', 'tipo_carnet': 'AB', 'telefono_movil': '663250275'}
        cursor.execute('''INSERT INTO PersonaAutorizadaTramitacion (id, nif, nombre, apellido1, apellido2, email, direccion_tipo_via, direccion_nombre_via, direccion_numero, direccion_bloque, direccion_portal, direccion_escalera, direccion_piso, direccion_puerta, direccion_localidad, direccion_provincia, direccion_cp, telefono_fijo, telefono_movil) VALUES (1, :nif, :nombre, :apellido1, :apellido2, :email, :direccion_tipo_via, :direccion_nombre_via, :direccion_numero, :direccion_bloque, :direccion_portal, :direccion_escalera, :direccion_piso, :direccion_puerta, :direccion_localidad, :direccion_provincia, :direccion_cp, :telefono_fijo, :telefono_movil)''', datos_pa)
        cursor.execute('''INSERT INTO EmpresaInstaladora (id, nif, razon_social, email, direccion_tipo_via, direccion_nombre_via, direccion_numero, direccion_puerta, direccion_localidad, direccion_provincia, direccion_cp, telefono_fijo, telefono_movil, num_registro, tipo_empresa) VALUES (1, :nif, :razon_social, :email, :direccion_tipo_via, :direccion_nombre_via, :direccion_numero, :direccion_puerta, :direccion_localidad, :direccion_provincia, :direccion_cp, :telefono_fijo, :telefono_movil, :num_registro, :tipo_empresa)''', datos_ei)
        cursor.execute('''INSERT INTO InstaladorHabilitado (id, nif, nombre, apellido1, apellido2, num_carne, email, ccaa_expide_carne, tipo_carnet, telefono_movil) VALUES (1, :nif, :nombre, :apellido1, :apellido2, :num_carne, :email, :ccaa_expide_carne, :tipo_carnet, :telefono_movil)''', datos_ih)
        print("-> Datos constantes cargados.")
    else:
        print("-> Datos constantes ya existen. No se necesita carga.")

def guardar_proyecto_en_db(cursor, datos_proyecto):
    """Guarda un nuevo proyecto en la tabla 'proyectos' y devuelve su ID."""
    cursor.execute("PRAGMA table_info(proyectos)")
    columnas_validas = {row[1] for row in cursor.fetchall()}
    
    # Filtra el diccionario para incluir solo las claves que son columnas válidas
    datos_a_insertar = {key: value for key, value in datos_proyecto.items() if key in columnas_validas}
    
    if not datos_a_insertar:
        print("Advertencia: No hay datos para guardar en la tabla 'proyectos'.")
        return None

    columnas = ', '.join(datos_a_insertar.keys())
    placeholders = ', '.join(['?'] * len(datos_a_insertar))
    sql = f"INSERT INTO proyectos ({columnas}) VALUES ({placeholders})"
    valores = tuple(datos_a_insertar.values())
    
    cursor.execute(sql, valores)
    return cursor.lastrowid

# --- FUNCIONES DE AYUDA (ASEGÚRATE DE QUE ESTÉN TODAS) ---

def obtener_marcas_unicas(cursor):
    """Devuelve una lista de todas las marcas únicas que no estén vacías."""
    cursor.execute("SELECT DISTINCT Marca FROM Equipos WHERE Marca IS NOT NULL AND Marca != '' ORDER BY Marca")
    marcas = [row[0] for row in cursor.fetchall()]
    return marcas

def obtener_modelos_por_marca(cursor, marca):
    """Devuelve una lista de modelos para una marca específica, excluyendo vacíos."""
    cursor.execute("SELECT Modelo FROM Equipos WHERE Marca = ? AND Modelo IS NOT NULL AND Modelo != '' ORDER BY Modelo", (marca,))
    modelos = [row[0] for row in cursor.fetchall()]
    return modelos

def obtener_emisores(cursor):
    """Devuelve una lista de todos los emisores disponibles."""
    cursor.execute("SELECT id, Marca, Modelo, Unidad_Medida FROM Emisores ORDER BY Marca, Modelo")
    return cursor.fetchall()

def guardar_locales_proyecto(cursor, proyecto_id, locales):
    """Guarda la lista de locales asociados a un proyecto."""
    for local in locales:
        cursor.execute('''
        INSERT INTO Locales_Proyecto (proyecto_id, nombre_local, superficie_m2, emisor_id, cantidad_elementos)
        VALUES (?, ?, ?, ?, ?)
        ''', (proyecto_id, local['nombre_local'], local['superficie_m2'], local['emisor_id'], local['cantidad_elementos']))
        