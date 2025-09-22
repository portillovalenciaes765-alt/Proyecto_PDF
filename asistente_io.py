# Módulo: asistente_io.py
import sqlite3
from config import DB_FILE
from database_manager import obtener_marcas_unicas, obtener_modelos_por_marca
from database_manager import obtener_emisores
from helpers import mostrar_tabla_locales

# --- FUNCIONES DE AYUDA (Tus funciones se quedan igual) ---

def obtener_opcion_numerada(pregunta, opciones, default_key):
    """Muestra un menú de opciones numeradas y devuelve el texto de la opción elegida."""
    print(f"\n{pregunta}")
    opciones_validas = {}
    for key, value in opciones.items():
        print(f"  {key}: {value}")
        opciones_validas[str(key)] = value
    
    respuesta_str = input(f"Tu elección [{default_key}]: ") or str(default_key)
    return opciones_validas.get(respuesta_str, opciones_validas[str(default_key)])
    
def solicitar_direccion(titulo_seccion):
    """Pide al usuario una dirección completa y la devuelve como un diccionario."""
    print(f"\n--- {titulo_seccion} ---")
    direccion = {}
    opciones_via = {"1": "CALLE", "2": "AVENIDA", "3": "PASEO", "4": "PLAZA"}
    direccion['tipo_via'] = obtener_opcion_numerada("Tipo de Vía:", opciones_via, "1")
    direccion['nombre_via'] = input("  Nombre de la Vía: ")
    direccion['numero'] = input("  Número: ")
    # --- CAMPOS AÑADIDOS ---
    direccion['bloque'] = input("  Bloque (opcional): ")
    direccion['portal'] = input("  Portal (opcional): ")
    direccion['escalera'] = input("  Escalera (opcional): ")
    # -----------------------
    direccion['piso'] = input("  Piso (opcional): ")
    direccion['puerta'] = input("  Puerta (opcional): ")
    direccion['localidad'] = input("  Localidad: ")
    direccion['provincia'] = input("  Provincia: ")
    direccion['cp'] = input("  Código Postal: ")
    return direccion

# --- FUNCIÓN PRINCIPAL (VERSIÓN REESTRUCTURADA) ---

def asistente_principal():
    """
    Función principal que guía al usuario a través de todas las preguntas.
    """
    print("--- Asistente para la Creación de Certificados IT.3.1.5 ---")
    datos_proyecto_nuevo = {}
    conn_equipos = None  # Definimos la conexión aquí

    try:
        # --- 1. ABRIMOS LA CONEXIÓN A LA DB AL PRINCIPIO ---
        conn_equipos = sqlite3.connect(DB_FILE)
        conn_equipos.row_factory = sqlite3.Row # ¡IMPORTANTE! Activamos el modo "diccionario"
        cursor_equipos = conn_equipos.cursor()

        # --- INICIO DE LAS PREGUNTAS ---

        # PASO 1: DATOS GENERALES DEL PROYECTO
        print("\n--- PASO 1: DATOS GENERALES DEL PROYECTO ---")
        datos_proyecto_nuevo['nombre_proyecto'] = input("Nombre para identificar este proyecto: ")
        datos_proyecto_nuevo['fecha_firma'] = input("Fecha de firma del documento (dd/mm/aaaa): ")

        # PASO 2: DATOS DEL TITULAR Y REPRESENTANTE
        print("\n--- PASO 2: DATOS DEL TITULAR (Sección 1 y 2) ---")
        tipo_titular = obtener_opcion_numerada("¿El titular es Persona Física (1) o Jurídica (2)?", {"1": "Física", "2": "Jurídica"}, "1")
        datos_proyecto_nuevo['titular_tipo'] = tipo_titular
        
        if tipo_titular == 'Física':
            print("\n  -- Datos de la Persona Física Titular (Sección 1) --")
            datos_proyecto_nuevo['titular_nif_cif'] = input("    NIF del titular: ")
            datos_proyecto_nuevo['titular_nombre'] = input("    Nombre: ")
            datos_proyecto_nuevo['titular_apellido1'] = input("    Primer Apellido: ")
            datos_proyecto_nuevo['titular_apellido2'] = input("    Segundo Apellido: ")
            datos_proyecto_nuevo['titular_email'] = input("    Correo Electrónico: ")
            datos_proyecto_nuevo['titular_tel_fijo'] = input("    Teléfono Fijo (opcional): ")
            datos_proyecto_nuevo['titular_tel_movil'] = input("    Teléfono Móvil: ")

            # Pedimos la dirección DESPUÉS de los datos personales
            dir_titular = solicitar_direccion("Dirección del Titular (Persona Física)")
            for key, value in dir_titular.items():
                datos_proyecto_nuevo[f"titular_dir_{key}"] = value

        else: # Jurídica
            print("\n  -- Datos de la Empresa Titular (Sección 1) --")
            datos_proyecto_nuevo['titular_nif_cif'] = input("    CIF de la empresa titular: ")
            datos_proyecto_nuevo['titular_razon_social'] = input("    Razón Social: ")
            datos_proyecto_nuevo['titular_email'] = input("    Correo Electrónico de la empresa: ")
            datos_proyecto_nuevo['titular_tel_fijo'] = input("    Teléfono Fijo de la empresa (opcional): ")
            datos_proyecto_nuevo['titular_tel_movil'] = input("    Teléfono Móvil de la empresa: ")

            # Pedimos la dirección de la empresa
            dir_empresa_titular = solicitar_direccion("Dirección de la Empresa Titular")
            for key, value in dir_empresa_titular.items():
                datos_proyecto_nuevo[f"titular_dir_{key}"] = value

            print("\n  -- Ahora, datos del Representante Legal (Sección 2) --")
            datos_proyecto_nuevo['representante_nif'] = input("    NIF del representante: ")
            datos_proyecto_nuevo['representante_nombre'] = input("    Nombre del representante: ")
            datos_proyecto_nuevo['representante_apellido1'] = input("    Primer Apellido: ")
            datos_proyecto_nuevo['representante_apellido2'] = input("    Segundo Apellido: ")
            datos_proyecto_nuevo['representante_email'] = input("    Correo Electrónico del representante: ")
            datos_proyecto_nuevo['representante_tel_fijo'] = input("    Teléfono Fijo del representante (opcional): ")
            datos_proyecto_nuevo['representante_tel_movil'] = input("    Teléfono Móvil del representante: ")

            # Pedimos la dirección del representante
            dir_representante = solicitar_direccion("Dirección del Representante Legal")
            for key, value in dir_representante.items():
            # Asegúrate de que las columnas en tu DB se llamen así
                datos_proyecto_nuevo[f"representante_dir_{key}"] = value

        # PASO 3: DATOS DE UBICACIÓN
        dir_ubicacion = solicitar_direccion("PASO 3: DATOS DE UBICACIÓN DE LA INSTALACIÓN (Sección 3)")
        for key, value in dir_ubicacion.items():
            datos_proyecto_nuevo[f"ubicacion_dir_{key}"] = value

        # PASO 4: SELECCIÓN DE EQUIPO Y DATOS TÉCNICOS
        print("\n--- PASO 4: SELECCIÓN DE EQUIPO Y DATOS TÉCNICOS ---")
        marcas = obtener_marcas_unicas(cursor_equipos)
        opciones_marcas = {str(i+1): marca for i, marca in enumerate(marcas)}
        marca_seleccionada = obtener_opcion_numerada("Selecciona la Marca del equipo:", opciones_marcas, "1")
        modelos = obtener_modelos_por_marca(cursor_equipos, marca_seleccionada)
        opciones_modelos = {str(i+1): modelo for i, modelo in enumerate(modelos)}
        modelo_seleccionado = obtener_opcion_numerada(f"Selecciona el Modelo para la marca {marca_seleccionada}:", opciones_modelos, "1")
        
        datos_proyecto_nuevo['equipo_marca'] = marca_seleccionada
        datos_proyecto_nuevo['equipo_modelo'] = modelo_seleccionado

        print(f"\n> Equipo seleccionado: {marca_seleccionada} - {modelo_seleccionado}")

        # 2. Lógica de "Confirmación con Anulación" para el Combustible (TU IDEA)
        cursor_equipos.execute("SELECT Combustible FROM Equipos WHERE Marca = ? AND Modelo = ?", (marca_seleccionada, modelo_seleccionado))
        combustible_sugerido_tupla = cursor_equipos.fetchone()
        
        # Comprobamos que la consulta devolvió algo y que no está vacío
        if combustible_sugerido_tupla and combustible_sugerido_tupla[0]:
            combustible_sugerido = combustible_sugerido_tupla[0]
            
            # Pregunta de confirmación
            opciones_confirmacion = {"1": "Sí", "2": "No"}
            confirmacion = obtener_opcion_numerada(f"El combustible habitual de este equipo es '{combustible_sugerido}'. ¿Es correcto para esta instalación?", opciones_confirmacion, "1")
            
            if confirmacion == "Sí":
                datos_proyecto_nuevo['fuente_energia'] = combustible_sugerido
            else: # El usuario ha dicho "No", mostramos la lista completa
                print("  > Por favor, selecciona el combustible correcto de la lista completa:")
                opciones_fuente_completa = {
                    "1": "Gas Natural", "2": "GLP", "3": "Gasóleo", "4": "Electricidad",
                    "5": "Biomasa (pellets)", "6": "Biomasa (astillas)", "7": "Biomasa (hueso aceituna)",
                    "8": "Solar Térmica", "9": "Solar FV"
                }
                datos_proyecto_nuevo['fuente_energia'] = obtener_opcion_numerada("Fuente de Energía principal:", opciones_fuente_completa, "1")
        else:
            # Plan B: si el equipo no tiene combustible definido, mostramos la lista completa
            print("> No se encontró un combustible predefinido para este equipo.")
            opciones_fuente_completa = {
                "1": "Gas Natural", "2": "GLP", "3": "Gasóleo", "4": "Electricidad",
                "5": "Biomasa (pellets)", "6": "Biomasa (astillas)", "7": "Biomasa (hueso aceituna)",
                "8": "Solar Térmica", "9": "Solar FV"
            }
            datos_proyecto_nuevo['fuente_energia'] = obtener_opcion_numerada("Fuente de Energía principal:", opciones_fuente_completa, "1")

        opciones_tipo_inst = {"1": "NUEVA", "2": "REFORMA / AMPLIACIÓN DE EXISTENTE"}
        tipo_instalacion_seleccion = obtener_opcion_numerada("Tipo de Instalación:", opciones_tipo_inst, "2")
        datos_proyecto_nuevo['tipo_instalacion'] = tipo_instalacion_seleccion
        if tipo_instalacion_seleccion == "REFORMA / AMPLIACIÓN DE EXISTENTE":
            datos_proyecto_nuevo['observaciones_reforma'] = input("  > Alcance de la reforma: ")
        # Pregunta por Generación Individualizada
        opciones_individualizada = {"1": "Sí", "2": "No"}
        # El nombre de la columna en la DB será 'generacion_individualizada'
        datos_proyecto_nuevo['generacion_individualizada'] = obtener_opcion_numerada("¿Conjunto de instalaciones con generación de calor o frío individualizadas?", opciones_individualizada, "1") 

       # --- REEMPLAZA ESTAS LÍNEAS EN asistente_io.py ---
        opciones_uso = {"1": "Administrativo", "2": "Comercial", "3": "Docente", "4": "Residencial Privado Unifamiliar", "5": "Residencial Privado Colectivo", "6": "Residencial Público", "7": "OTROS"}
        uso_edificio_seleccion = obtener_opcion_numerada("Tipo de Uso del Edificio:", opciones_uso, "5")
        datos_proyecto_nuevo['uso_edificio'] = uso_edificio_seleccion
        if uso_edificio_seleccion == "OTROS":
            datos_proyecto_nuevo['uso_edificio_otros'] = input("  > Por favor, especifique el tipo de uso: ")

        num_viviendas_str = input("Número de Viviendas [1]: ") or "1"
        datos_proyecto_nuevo['numero_viviendas'] = int(num_viviendas_str)

        #  DATOS DE ACS (Página 7 IT315) ---  
        print("\n--- PASO 5: DATOS DE ACS (Página 9) ---")
        demanda_acs_str = input("Demanda diaria de ACS a 60°C (litros/día) [84]: ") or "84"
        datos_proyecto_nuevo['demanda_acs_litros_dia'] = float(demanda_acs_str)
        datos_proyecto_nuevo['volumen_acumulacion_acs'] = input("Volumen máximo de acumulación de ACS (litros) [Microacumulación]: ") or "Microacumulación"
        #-------------------------------------------------------------------------------

        opciones_riesgo = {"1": "Sí", "2": "No"}
        datos_proyecto_nuevo['sala_maquinas_alto_riesgo'] = obtener_opcion_numerada("En referencia a la sala de máquinas: ¿Es de ALTO RIESGO?", opciones_riesgo, "2")
        
        opciones_terminal = {"1": "Radiadores", "2": "Suelo radiante", "3": "rejillas(Equipo por conductos)"}
        equipo_terminal_seleccionado = obtener_opcion_numerada("Equipo Terminal principal:", opciones_terminal, "1")
        datos_proyecto_nuevo['equipo_terminal'] = equipo_terminal_seleccionado
        
        if equipo_terminal_seleccionado == "Radiadores":
            num_rad_str = input("  > N° de Radiadores por circuito: ")
            datos_proyecto_nuevo['num_radiadores'] = int(num_rad_str)
        else:
            num_otros_str = input(f"  > Número de emisores ({equipo_terminal_seleccionado}): ")
            datos_proyecto_nuevo['num_otros_emisores'] = int(num_otros_str)
        # Añadimos la pregunta por el número de generadores
        num_generadores_str = input("¿Cuántos generadores de calor tiene la instalación? [1]: ") or "1"
        datos_proyecto_nuevo['num_generadores'] = int(num_generadores_str)
            
            # --- PASO 5: SISTEMA DE DISTRIBUCIÓN (Página 10) --- # <= ESTE ES EL BLOQUE QUE AÑADES
        print("\n--- PASO 5: DATOS DE SISTEMA DE DISTRIBUCIÓN ---")
        
        opciones_distribucion = {"1": "Monotubo", "2": "Bitubo"}
        datos_proyecto_nuevo['tipo_distribucion'] = obtener_opcion_numerada("Clase/Tipo de Distribución:", opciones_distribucion, "2")
        
        opciones_tuberia = {"1": "Cobre", "2": "Hierro", "3": "Multicapa", "4": "OTRO"}
        tipo_tuberia_seleccion = obtener_opcion_numerada("Tipo de tubería utilizada:", opciones_tuberia, "1")
        if tipo_tuberia_seleccion == "OTRO":
            datos_proyecto_nuevo['tipo_tuberia'] = input("  > Por favor, especifica el tipo de tubería: ")
        else:
            datos_proyecto_nuevo['tipo_tuberia'] = tipo_tuberia_seleccion
            
        datos_proyecto_nuevo['seccion_max_tuberia'] = input("Sección máxima de la tubería utilizada (ej: 1/2, 25): ")
        datos_proyecto_nuevo['seccion_min_tuberia'] = input("Sección mínima de la tubería utilizada (ej: 1/4, 18): ")

        if equipo_terminal_seleccionado == "rejillas(Equipo por conductos)":
            datos_proyecto_nuevo['tipo_conducto'] = input("  > Tipo de conducto utilizado (ej: CLIMAVER): ")
        # --- PASO 6: DATOS DE AISLAMIENTO TÉRMICO ---
        print("\n--- PASO 6: DATOS DE AISLAMIENTO TÉRMICO (Página 10) ---")
        
        print("\n-- Aislamiento para Tuberías y Accesorios --")
        datos_proyecto_nuevo['aislamiento_tuberias_mat'] = input("  Material de aislamiento [COQUILLA ARMAFLEX]: ") or "COQUILLA ARMAFLEX"
        datos_proyecto_nuevo['aislamiento_tuberias_esp'] = input("  Espesor del aislamiento [25mm]: ") or "25mm"

        if equipo_terminal_seleccionado == "rejillas(Equipo por conductos)":
            print("\n-- Aislamiento para Conductos --")
            datos_proyecto_nuevo['aislamiento_conductos_mat'] = input("  Material de aislamiento [COQUILLA ARMAFLEX]: ") or "COQUILLA ARMAFLEX"
            datos_proyecto_nuevo['aislamiento_conductos_esp'] = input("  Espesor del aislamiento [25mm]: ") or "25mm"

        # --- PASO 7: VENTILACIÓN DE LOCALES ---
        print("\n--- PASO 7: VENTILACIÓN DE LOCALES (Página 9) ---")
        opciones_ventilacion = {"1": "DIRECTA", "2": "NATURAL", "3": "FORZADA"}
        tipo_ventilacion_seleccion = obtener_opcion_numerada("Tipo de ventilación:", opciones_ventilacion, "2")
        datos_proyecto_nuevo['ventilacion_tipo'] = tipo_ventilacion_seleccion

        if tipo_ventilacion_seleccion == "DIRECTA":
            num_aberturas_str = input("  > ¿Cuántas aperturas directas al exterior tiene el sitio? [1]: ") or "1"
            num_aberturas = int(num_aberturas_str)
            datos_proyecto_nuevo['vent_directa_n_aberturas'] = num_aberturas
            total_area = 0
            for i in range(num_aberturas):
                area_str = input(f"    Área de la apertura {i+1} en cm²: ")
                total_area += float(area_str)
            datos_proyecto_nuevo['vent_directa_area_total'] = total_area
        
        elif tipo_ventilacion_seleccion == "NATURAL":
            num_conductos_str = input("  > ¿Cuántos conductos al exterior tiene el sitio? [1]: ") or "1"
            num_conductos = int(num_conductos_str)
            datos_proyecto_nuevo['vent_natural_n_conductos'] = num_conductos
            total_area = 0
            for i in range(num_conductos):
                area_str = input(f"    Área del conducto {i+1} en cm²: ")
                total_area += float(area_str)
            datos_proyecto_nuevo['vent_natural_area_total'] = total_area
        
        elif tipo_ventilacion_seleccion == "FORZADA":
            datos_proyecto_nuevo['vent_forzada_caudal'] = float(input("  > Desplazamiento de aire en m³/h: "))
            datos_proyecto_nuevo['vent_forzada_relacion'] = float(input("  > Medida de ventilación forzada en Cm²/kW: "))
            datos_proyecto_nuevo['vent_forzada_enclavamiento'] = input("  > Ventilador enclavado con: ")
            
        #Pagina 9 seccion 11 IT 3.1.5
        # --- PASO X: DATOS DE EMPLAZAMIENTO DEL GENERADOR ---
        print("\n--- DATOS DE EMPLAZAMIENTO DEL GENERADOR (Página 9) ---")
        
        opciones_emplazamiento = {"1": "INTERIOR", "2": "EXTERIOR"}
        datos_proyecto_nuevo['emplazamiento_generador'] = obtener_opcion_numerada("Ubicación del Generador:", opciones_emplazamiento, "1")
        
        datos_proyecto_nuevo['lugar_ubicacion_generador'] = input("  > Lugar de ubicación específico (ej: Fachada, Cubierta, Cocina): ")

    except Exception as e:
        print(f"\nHa ocurrido un error en el asistente principal: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # --- 2. CERRAMOS LA CONEXIÓN AL FINAL DE TODO ---
        if conn_equipos:
            conn_equipos.close()

# --- PASO 8: RESUMEN DE CARGAS CALORÍFICAS (Bucle de Locales) ---
        print("\n--- PASO 8: RESUMEN DE CARGAS CALORÍFICAS POR LOCAL ---")
        
        locales_proyecto = []
        emisores_disponibles = obtener_emisores(cursor_equipos)
        opciones_emisores = {str(i+1): f"{emisor['Marca']} - {emisor['Modelo']}" for i, emisor in enumerate(emisores_disponibles)}

        for i in range(9): # Bucle limitado a un máximo de 9 locales
            mostrar_tabla_locales(locales_proyecto)
            
            continuar = input(f"\n¿Añadir local {i+1} de 9? (S/N) [S]: ").strip().lower() or "s"
            if continuar != 's':
                break
            
            print(f"\n--- Datos para el Local {i+1} ---")
            local_actual = {}
            local_actual['nombre_local'] = input(" > Nombre del local (ej: Salón, Dormitorio 1): ")
            local_actual['superficie_m2'] = float(input(" > Superficie en m²: "))
            
            # Selección de emisor
            emisor_elegido_idx_str = obtener_opcion_numerada(" > Selecciona el emisor para este local:", opciones_emisores, "1")
            emisor_seleccionado = emisores_disponibles[int(emisor_elegido_idx_str) - 1]
            
            unidad = emisor_seleccionado['Unidad_Medida']
            local_actual['cantidad_elementos'] = float(input(f" > Cantidad de '{unidad}': "))
            
            # Guardamos la info necesaria
            local_actual['emisor_id'] = emisor_seleccionado['id']
            local_actual['emisor_texto'] = f"{emisor_seleccionado['Marca']} {emisor_seleccionado['Modelo']}"
            local_actual['unidad_medida'] = unidad
            
            locales_proyecto.append(local_actual)

        # Guardamos la lista de locales en el diccionario principal
        datos_proyecto_nuevo['locales'] = locales_proyecto            
    return datos_proyecto_nuevo