# Módulo: pdf_generator.py
# Responsabilidad: Contiene la lógica para rellenar el PDF con datos de la base de datos.

import sqlite3
import os
from datetime import datetime
from pypdf import PdfReader, PdfWriter
import traceback

# --- FUNCIONES DE BASE DE DATOS ---
def obtener_datos_constantes(cursor):
    """Obtiene los datos fijos de la empresa, instalador y persona autorizada."""
    datos_const = {}
    cursor.execute("SELECT * FROM EmpresaInstaladora WHERE id = 1")
    datos_const['empresa'] = cursor.fetchone()
    cursor.execute("SELECT * FROM InstaladorHabilitado WHERE id = 1")
    datos_const['instalador'] = cursor.fetchone()
    cursor.execute("SELECT * FROM PersonaAutorizadaTramitacion WHERE id = 1")
    datos_const['persona_autorizada'] = cursor.fetchone()
    return datos_const

# --- FUNCIÓN PRINCIPAL DE RELLENADO ---
def rellenar_pdf_final(project_id, db_file, template_path, output_folder):
    """Rellena el PDF final con todos los datos del proyecto."""
    mapa_de_datos = {}
    conn = None
    proyecto = None

    # --- TAREA 1: LEER TODOS LOS DATOS DE LA BASE DE DATOS ---
    try:
        conn = sqlite3.connect(f'file:{db_file}?mode=ro', uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 1. OBTENER DATOS BÁSICOS
        datos_fijos = obtener_datos_constantes(cursor)
        cursor.execute("SELECT * FROM proyectos WHERE id = ?", (project_id,))
        proyecto = cursor.fetchone()
        cursor.execute("SELECT * FROM Equipos WHERE Marca = ? AND Modelo = ?", (proyecto['equipo_marca'], proyecto['equipo_modelo']))
        datos_equipo = cursor.fetchone()
        
        if not (datos_fijos and datos_fijos.get('empresa') and proyecto and datos_equipo):
            print("Error: No se pudieron cargar datos constantes, del proyecto o del equipo.")
            return

        # --- SECCIÓN DE MAPEO DE DATOS ---
        
        pa = datos_fijos.get('persona_autorizada')
        ei = datos_fijos.get('empresa')
        ih = datos_fijos.get('instalador')
        
        # MAPEO DATOS CONSTANTES (Secciones 4, 5, 14)
        if pa: mapa_de_datos.update({'S4_AUTORIZADO_NIF': pa['nif'], 'S4_AUTORIZADO_NOMBRE': pa['nombre'], 'S4_AUTORIZADO_APELLIDO1': pa['apellido1'], 'S4_AUTORIZADO_APELLIDO2': pa['apellido2'], 'S4_AUTORIZADO_CORREO': pa['email'], 'S4_AUTORIZADO_TIPOVIA': pa['direccion_tipo_via'], 'S4_AUTORIZADO_NOMBREVIA': pa['direccion_nombre_via'], 'S4_AUTORIZADO_Nº': pa['direccion_numero'], 'S4_AUTORIZADO_PISO': pa['direccion_piso'], 'S4_AUTORIZADO_PUERTA': pa['direccion_puerta'], 'S4_AUTORIZADO_LOCALIDAD': pa['direccion_localidad'], 'S4_AUTORIZADO_PROVINCIA': pa['direccion_provincia'], 'S4_AUTORIZADO_CP': pa['direccion_cp'], 'S4_AUTORIZADO_MOVIL': pa['telefono_movil'], 'S4_AUTORIZADO_TELEFONO': pa['telefono_fijo']})
        if ei: mapa_de_datos.update({'S5_EMPRESA_NIF': ei['nif'], 'S5_EMPRESA_NOMBRE': ei['razon_social'], 'S5_EMPRESA_CORREO': ei['email'], 'S5_EMPRESA_TIPOVIA': ei['direccion_tipo_via'], 'S5_EMPRESA_NOMBREVIA': ei['direccion_nombre_via'], 'S5_EMPRESA_Nº': ei['direccion_numero'], 'S5_EMPRESA_PUERTA': ei['direccion_puerta'], 'S5_EMPRESA_LOCALIDAD': ei['direccion_localidad'], 'S5_EMPRESA_PROVINCIA': ei['direccion_provincia'], 'S5_EMPRESA_CP': ei['direccion_cp'], 'S5_EMPRESA_TELEFONO': ei['telefono_fijo'], 'S5_EMPRESA_MOVIL': ei['telefono_movil']})
        if ih: mapa_de_datos.update({'S5_INSTALADOR_NIF': ih['nif'], 'S5_INSTALADOR_NOMBRE': ih['nombre'], 'S5_INSTALADOR_APELLIDO1': ih['apellido1'], 'S5_INSTALADOR_APELLIDO2': ih['apellido2'], 'S5_INSTALADOR_CORREO': ih['email'], 'S5_INSTALADOR_NºCARNE': ih['num_carne'], 'S5_INSTALADOR_CCAAEXPIDECARNE': ih['ccaa_expide_carne'], 'S14MEMORIA_ProfeInstalador_NOMBRE': f"{ih['nombre']} {ih['apellido1']} {ih['apellido2']}", 'S14MEMORIA_ProfeInstalador_NIF': ih['nif'], 'S14MEMORIA_TecTitulCompet_NOMBRE': f"{ih['nombre']} {ih['apellido1']} {ih['apellido2']}", 'S14MEMORIA_TecTitulCompet_NIF': ih['nif']})

        # MAPEO DATOS DEL PROYECTO (Secciones 1, 2, 3 y Fecha)
        if proyecto['titular_tipo'] == 'Jurídica':
            mapa_de_datos.update({
                'S1_TITULAR_NOMBRE': proyecto['titular_razon_social'], 'S1_TITULAR_APELLIDO1': '', 'S1_TITULAR_APELLIDO2': '',
                'S1_TITULAR_NIF': proyecto['titular_nif_cif'], 'S1_TITULAR_CORREO': proyecto['titular_email'],
                'S1_TITULAR_TELEFONO': proyecto['titular_tel_fijo'], 'S1_TITULAR_MOVIL': proyecto['titular_tel_movil'],
                'S1_TITULAR_TIPOVIA': proyecto['titular_dir_tipo_via'], 'S1_TITULAR_NOMBREVIA': proyecto['titular_dir_nombre_via'],
                'S1_TITULAR_Nº': proyecto['titular_dir_numero'], 'S1_TITULAR_BLOQUE': proyecto['titular_dir_bloque'],
                'S1_TITULAR_PORTAL': proyecto['titular_dir_portal'], 'S1_TITULAR_ESCALERA': proyecto['titular_dir_escalera'],
                'S1_TITULAR_PISO': proyecto['titular_dir_piso'], 'S1_TITULAR_PUERTA': proyecto['titular_dir_puerta'],
                'S1_TITULAR_LOCALIDAD': proyecto['titular_dir_localidad'], 'S1_TITULAR_PROVINCIA': proyecto['titular_dir_provincia'],
                'S1_TITULAR_CP': proyecto['titular_dir_cp']
            })
            mapa_de_datos.update({
                'S2_REP_NIF': proyecto['representante_nif'], 'S2_REP_NOMBRE': proyecto['representante_nombre'],
                'S2_REP_APELLIDO1': proyecto['representante_apellido1'], 'S2_REP_APELLIDO2': proyecto['representante_apellido2'],
                'S2_REP_CORREO': proyecto['representante_email'], 'S2_REP_TELEFONO': proyecto['representante_tel_fijo'],
                'S2_REP_MOVIL': proyecto['representante_tel_movil'], 'S2_REP_TIPOVIA': proyecto['representante_dir_tipo_via'],
                'S2_REP_NOMBREVIA': proyecto['representante_dir_nombre_via'], 'S2_REP_Nº': proyecto['representante_dir_numero'],
                'S2_REP_BLOQUE': proyecto['representante_dir_bloque'], 'S2_REP_PORTAL': proyecto['representante_dir_portal'],
                'S2_REP_ESCALERA': proyecto['representante_dir_escalera'], 'S2_REP_PISO': proyecto['representante_dir_piso'],
                'S2_REP_PUERTA': proyecto['representante_dir_puerta'], 'S2_REP_LOCALIDAD': proyecto['representante_dir_localidad'],
                'S2_REP_PROVINCIA': proyecto['representante_dir_provincia'], 'S2_REP_CP': proyecto['representante_dir_cp']
            })
        else: # Física
            mapa_de_datos.update({
                'S1_TITULAR_NOMBRE': proyecto['titular_nombre'], 'S1_TITULAR_APELLIDO1': proyecto['titular_apellido1'],
                'S1_TITULAR_APELLIDO2': proyecto['titular_apellido2'], 'S1_TITULAR_NIF': proyecto['titular_nif_cif'],
                'S1_TITULAR_CORREO': proyecto['titular_email'], 'S1_TITULAR_TELEFONO': proyecto['titular_tel_fijo'],
                'S1_TITULAR_MOVIL': proyecto['titular_tel_movil'], 'S1_TITULAR_TIPOVIA': proyecto['titular_dir_tipo_via'],
                'S1_TITULAR_NOMBREVIA': proyecto['titular_dir_nombre_via'], 'S1_TITULAR_Nº': proyecto['titular_dir_numero'],
                'S1_TITULAR_BLOQUE': proyecto['titular_dir_bloque'], 'S1_TITULAR_PORTAL': proyecto['titular_dir_portal'],
                'S1_TITULAR_ESCALERA': proyecto['titular_dir_escalera'], 'S1_TITULAR_PISO': proyecto['titular_dir_piso'],
                'S1_TITULAR_PUERTA': proyecto['titular_dir_puerta'], 'S1_TITULAR_LOCALIDAD': proyecto['titular_dir_localidad'],
                'S1_TITULAR_PROVINCIA': proyecto['titular_dir_provincia'], 'S1_TITULAR_CP': proyecto['titular_dir_cp']
            })

        mapa_de_datos.update({
            'S3_UBICACIONINSTALACION_TIPOVIA': proyecto['ubicacion_dir_tipo_via'], 'S3_UBICACIONINSTALACION_NOMBRE': proyecto['ubicacion_dir_nombre_via'],
            'S3_UBICACIONINSTALACION_Nº': proyecto['ubicacion_dir_numero'], 'S3_UBICACIONINSTALACION_BLOQUE': proyecto['ubicacion_dir_bloque'],
            'S3_UBICACIONINSTALACION_PORTAL': proyecto['ubicacion_dir_portal'], 'S3_UBICACIONINSTALACION_ESCALERA': proyecto['ubicacion_dir_escalera'],
            'S3_UBICACIONINSTALACION_PISO': proyecto['ubicacion_dir_piso'], 'S3_UBICACIONINSTALACION_PUERTA': proyecto['ubicacion_dir_puerta'],
            'S3_UBICACIONINSTALACION_LOCALIDAD': proyecto['ubicacion_dir_localidad'], 'S3_UBICACIONINSTALACION_PROVINCIA': proyecto['ubicacion_dir_provincia'],
            'S3_UBICACIONINSTALACION_CP': proyecto['ubicacion_dir_cp']
        })
        
        if proyecto['fecha_firma'] and ei:
            fecha_obj = datetime.strptime(proyecto['fecha_firma'], "%d/%m/%Y")
            mapa_de_datos.update({
                'S8_FIRMA_LOCALIDAD': ei['direccion_localidad'], 'S8_FIRMA_DIA': fecha_obj.strftime("%d"),
                'S8_FIRMA_MES': fecha_obj.strftime("%B").upper(), 'S8_FIRMA_AÑO': fecha_obj.strftime("%Y"),
                'S14MEMORIA_ProfeInstalador_Fecha': proyecto['fecha_firma'], 'S14MEMORIA_TecTituCompet_Fecha': proyecto['fecha_firma']
            })

        # --- MAPEO DE LÓGICA TÉCNICA Y DATOS DE EQUIPO ---
        # Documentación Aportada (Sección 8)
        mapa_de_datos.update({'S8_Tasa': '/On', 'S8_Tarifa': '/On', 'S8_MEMORIA': '/On', 'S8_ManUsoyMant': '/On'})
        
        # Memoria Técnica (Página 5)
        servicio_db = datos_equipo['Servicio']
        if "Calefacción" in servicio_db: mapa_de_datos['S1MEMORIA_TIPO_Calefacción'] = '/On'
        if "ACS" in servicio_db: mapa_de_datos['S1MEMORIA_TIPO_ACS'] = '/On'
        if "Aire Acondicionado" in servicio_db: mapa_de_datos['S1MEMORIA_TIPO_Aire Acondicionado'] = '/On'
        
        if proyecto['tipo_instalacion'] == "REFORMA / AMPLIACIÓN DE EXISTENTE":
            mapa_de_datos['S1MEMORIA_INSTALACION_REFORMA/AMPLIACION'] = '/On'
            mapa_de_datos['S1MEMORIA_DETALLES DE LA REFORMA'] = proyecto['observaciones_reforma']
        else: # NUEVA
            mapa_de_datos['S1MEMORIA_INSTALACION_NUEVA'] = '/On'
            # --- AÑADE ESTE BLOQUE DESPUÉS DE LA LÓGICA DE "TIPO DE INSTALACIÓN" ---

        # Fuente de Energía
        if 'fuente_energia' in proyecto.keys():
            fuente_map = {
                "Gas Natural": "S1MEMORIA_FUENTE_Gas Natural", 
                "Electricidad": "S1MEMORIA_FUENTE_Electricidad",
                "Biomasa (pellets)": "S1MEMORIA_FUENTE_Biomasa pellets", 
                "GLP": "S1MEMORIA_FUENTE_GLP",
                "Solar Térmica": "S1MEMORIA_FUENTE_Solar Térmica", 
                "Biomasa astillas": "S1MEMORIA_FUENTE_Biomasa astillas",
                "Gasóleo": "S1MEMORIA_FUENTE_Gasóleo", 
                "Solar FV": "S1MEMORIA_FUENTE_Solar FV",
                "Biomasa hueso de aceitunas": "S1MEMORIA_FUENTE_Biomasa hueso de aceitunas", 
                "Otros": "S1MEMORIA_FUENTE_Otros"
            }
            fuente_seleccionada = proyecto['fuente_energia']
            for fuente, campo_pdf in fuente_map.items():
                mapa_de_datos[campo_pdf] = '/On' if fuente_seleccionada == fuente else '/Off'

# --- AÑADE ESTE BLOQUE en la función rellenar_pdf_final ---

        # Generación Individualizada (con el valor /Sí descubierto)
        if 'generacion_individualizada' in proyecto.keys():
            # Los nombres de los campos que tú creaste
            campo_si = 'S1MEMORIA_GeneracionIndividualizada_Si'
            campo_no = 'S1MEMORIA_GeneracionIndividualizada_No'
            
            # El valor que descubrimos que funciona para MARCAR
            valor_on = '/Sí' 
            # El valor que sabemos que funciona para DESMARCAR
            valor_off = '/Off' 

            if proyecto['generacion_individualizada'] == "Sí":
                mapa_de_datos[campo_si] = valor_on
                mapa_de_datos[campo_no] = valor_off
            else: # "No"
                mapa_de_datos[campo_si] = valor_off
                # Asumiendo que el checkbox "No" también se activa con '/Sí'
                # basado en el comportamiento del de "Sala de Máquinas"
                mapa_de_datos[campo_no] = valor_on
      
        # Tipo de Uso del Edificio
        if 'uso_edificio' in proyecto.keys():
            uso_map = {
                "Administrativo": "S1MEMORIA_TIPO USO EDIF_Administrativo", 
                "Comercial": "S1MEMORIA_TIPO USO EDIF_Comercial",
                "Docente": "S1MEMORIA_TIPO USO EDIF_Docente", 
                "Residencial Privado Unifamiliar": "S1MEMORIA_TIPO USO EDIF_ResidPrivadoUnif",
                "Residencial Privado Colectivo": "S1MEMORIA_TIPO USO EDIF_ResidPrivadColectivo", 
                "Residencial Público": "S1MEMORIA_TIPO USO EDF_Residencial Público"
            }
            uso_seleccionado = proyecto['uso_edificio']
            for uso, campo_pdf in uso_map.items():
                mapa_de_datos[campo_pdf] = '/On' if uso_seleccionado == uso else '/Off'
            
            if uso_seleccionado == "OTROS":
                mapa_de_datos['S1MEMORIA_TIPO USO EDIF_OTROS'] = '/On'
                mapa_de_datos['S1MEMORIA_TIPO USO EDIF_OTROS_DESCRIPCION'] = proyecto['uso_edificio_otros'] or ''
            else:
                mapa_de_datos['S1MEMORIA_TIPO USO EDIF_OTROS'] = '/Off'
                mapa_de_datos['S1MEMORIA_TIPO USO EDIF_OTROS_DESCRIPCION'] = ''
        
        if 'numero_viviendas' in proyecto.keys():
            mapa_de_datos['S1MEMORIA_Número de Viviendas'] = str(proyecto['numero_viviendas'])
        
# --- REEMPLAZA EL BLOQUE "Sala de Máquinas" CON ESTE CÓDIGO FINAL ---

        # Sala de Máquinas (con los valores de checkbox correctos descubiertos)
        if 'sala_maquinas_alto_riesgo' in proyecto.keys():
            # Los nombres de los campos que tú creaste
            campo_si = 'S1MEMORIA_SalaMaquinAltoRiesgo_Si'
            campo_no = 'S1MEMORIA_SalaMaquinAltoRiesgo_No'
            
            # El valor que descubrimos que funciona para MARCAR CUALQUIER OPCIÓN
            valor_on = '/Sí' 
            # El valor que sabemos que funciona para DESMARCAR
            valor_off = '/Off' 

            if proyecto['sala_maquinas_alto_riesgo'] == "Sí":
                mapa_de_datos[campo_si] = valor_on  # Activa la casilla "Sí"
                mapa_de_datos[campo_no] = valor_off # Desactiva la casilla "No"
            else: # "No"
                mapa_de_datos[campo_si] = valor_off # Desactiva la casilla "Sí"
                mapa_de_datos[campo_no] = valor_on  # Activa la casilla "No"
        
        # Tipo de Emisores
        if 'equipo_terminal' in proyecto.keys():
            emisores_map = {
                "Radiadores": "S1MEMORIA_EMISORES_Radiadores",
                "Suelo radiante": "S1MEMORIA_EMISORES_Suelo Radiante",
                "rejillas(Equipo por conductos)": "S1MEMORIA_EMISORES_Conductos",
                "Fan Coil": "S1MEMORIA_EMISORES_Fan Coil",
                "Expansión Directa": "S1MEMORIA_EMISORES_Expansión Directa"
            }
            terminal_seleccionado = proyecto['equipo_terminal']
            for emisor, campo_pdf in emisores_map.items():
                mapa_de_datos[campo_pdf] = '/On' if terminal_seleccionado == emisor else '/Off'

        # --- AÑADE ESTE BLOQUE a la sección de mapeo en rellenar_pdf_final ---

        # Mapeo para Emplazamiento del Generador (Sección 11) pagina 9
        if 'emplazamiento_generador' in proyecto.keys():
            if proyecto['emplazamiento_generador'] == 'INTERIOR':
                mapa_de_datos['S11MEMORIA_EMPLAZAMIENTO_INTERIOR'] = '/On'
                mapa_de_datos['S11MEMORIA_EMPLAZAMIENTO_EXTERIOR'] = '/Off'
            else: # EXTERIOR
                mapa_de_datos['S11MEMORIA_EMPLAZAMIENTO_INTERIOR'] = '/Off'
                mapa_de_datos['S11MEMORIA_EMPLAZAMIENTO_EXTERIOR'] = '/On'
        
        if 'lugar_ubicacion_generador' in proyecto.keys():
            mapa_de_datos['S11MEMORIA_UBICACIONDELGENERADOR'] = proyecto['lugar_ubicacion_generador']

        
    # --- LÓGICA DE MAPEO PARA SISTEMA DE DISTRIBUCIÓN ---
        mapa_de_datos.update({
            'S11MEMORIA_SistDist_TipoTuberia': proyecto['tipo_tuberia'],
            'S11MEMORIA_SistDist_DiamMax': proyecto['seccion_max_tuberia'],
            'S11MEMORIA_SistDist_DiamMin': proyecto['seccion_min_tuberia'],
            'S11MEMORIA_SistDist_EquipTerminales': proyecto['equipo_terminal']
        })
        
        # Lógica condicional para Monotubo/Bitubo
        seleccion_distribucion = proyecto['tipo_distribucion']
        equipo_terminal = proyecto['equipo_terminal']

        # Inicializamos todos los checkboxes a Off
        mapa_de_datos['S11MEMORIA_SistDist_ClaseMonotubo'] = '/Off'
        mapa_de_datos['S11MEMORIA_SistDist_ClaseBitubo'] = '/Off'
        mapa_de_datos['S11MEMORIA_SistDist_TipoMonotubular'] = '/Off'
        mapa_de_datos['S11MEMORIA_SistDist_TipoBitubular'] = '/Off'
        mapa_de_datos['S11MEMORIA_SistDist_NºRadiadoresxCircuit'] = ''

        # LÓGICA CORREGIDA
        if 'equipo_terminal' in proyecto.keys() and proyecto['equipo_terminal'] == "rejillas(Equipo por conductos)":
            mapa_de_datos['S11MEMORIA_SistDist_TipoConducto'] = proyecto['tipo_conducto']
            if seleccion_distribucion == "Monotubo":
                mapa_de_datos['S11MEMORIA_SistDist_ClaseMonotubo'] = '/On'
            else: # Bitubo
                mapa_de_datos['S11MEMORIA_SistDist_ClaseBitubo'] = '/On'
        else:
            if seleccion_distribucion == "Monotubo":
                mapa_de_datos['S11MEMORIA_SistDist_TipoMonotubular'] = '/On'
                if 'equipo_terminal' in proyecto.keys() and proyecto['equipo_terminal'] == "Radiadores":
                    mapa_de_datos['S11MEMORIA_SistDist_NºRadiadoresxCircuit'] = str(proyecto['num_radiadores'])
            else: # Bitubo
                mapa_de_datos['S11MEMORIA_SistDist_TipoBitubular'] = '/On'
                if 'equipo_terminal' in proyecto.keys() and proyecto['equipo_terminal'] == "Radiadores":
                    mapa_de_datos['S11MEMORIA_SistDist_NºRadiadoresxCircuit'] = str(proyecto['num_radiadores'])
       
# LÓGICA PARA SISTEMA DE DISTRIBUCIÓN (CORREGIDA)
        if 'aislamiento_tuberias_mat' in proyecto.keys() and proyecto['aislamiento_tuberias_mat']:
            mapa_de_datos['S11MEMORIA_TUB.ACCESOR_MAT.AISLAM'] = proyecto['aislamiento_tuberias_mat']
        if 'aislamiento_tuberias_esp' in proyecto.keys() and proyecto['aislamiento_tuberias_esp']:
            mapa_de_datos['S11MEMORIA_TUB.ACCESOR_ESPES.AISLAM'] = proyecto['aislamiento_tuberias_esp']
        
        if 'equipo_terminal' in proyecto.keys() and proyecto['equipo_terminal'] == "rejillas(Equipo por conductos)":
            if 'aislamiento_conductos_mat' in proyecto.keys() and proyecto['aislamiento_conductos_mat']:
                mapa_de_datos['S11MEMORIA_CONDUCTOS_MAT.AISLAM'] = proyecto['aislamiento_conductos_mat']
            if 'aislamiento_conductos_esp' in proyecto.keys() and proyecto['aislamiento_conductos_esp']:
                mapa_de_datos['S11MEMORIA_CONDUCTOS_ESPES.AISLAM'] = proyecto['aislamiento_conductos_esp']

# --- REEMPLAZA ESTE BLOQUE EN LA FUNCIÓN rellenar_pdf_final ---

        # Mapeo para Ventilación de Locales (Sección 11 - Pág 9)
        if 'ventilacion_tipo' in proyecto.keys():
            tipo_ventilacion = proyecto['ventilacion_tipo']
            
            # Inicializamos todos los campos de esta sección para que queden limpios
            mapa_de_datos.update({
                'S11MEMORIA_VentDirecta_N°Aberturas': '',
                'S11MEMORIA_VentDirecta_AreaTotalAbertura': '',
                'S11MEMORIA_VentNatural_N°Conductos': '',
                'S11MEMORIA_VentNatural_AreaTotalConductos': '',
                'S11MEMORIA_Forzada_Caudal': '',
                'S11MEMORIA_Forzada_RelacionCm²/kW': '',
                'S11MEMORIA_Forzada_Enclavamiento': ''
            })

            if tipo_ventilacion == "DIRECTA":
                if 'vent_directa_n_aberturas' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_VentDirecta_N°Aberturas'] = str(proyecto['vent_directa_n_aberturas'])
                if 'vent_directa_area_total' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_VentDirecta_AreaTotalAbertura'] = str(proyecto['vent_directa_area_total'])
            
            elif tipo_ventilacion == "NATURAL":
                if 'vent_natural_n_conductos' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_VentNatural_N°Conductos'] = str(proyecto['vent_natural_n_conductos'])
                if 'vent_natural_area_total' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_VentNatural_AreaTotalConductos'] = str(proyecto['vent_natural_area_total'])
            
            elif tipo_ventilacion == "FORZADA":
                if 'vent_forzada_caudal' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_Forzada_Caudal'] = str(proyecto['vent_forzada_caudal'])
                if 'vent_forzada_relacion' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_Forzada_RelacionCm²/kW'] = str(proyecto['vent_forzada_relacion'])
                if 'vent_forzada_enclavamiento' in proyecto.keys():
                    mapa_de_datos['S11MEMORIA_Forzada_Enclavamiento'] = proyecto['vent_forzada_enclavamiento']

                    # --- AÑADE ESTE BLOQUE COMPLETO en rellenar_pdf_final ---

        # Mapeo para N° de Generadores (Página 6)
        if 'num_generadores' in proyecto.keys():
            mapa_de_datos['S2MEMORIA_N° GENERADORES'] = str(proyecto['num_generadores'])

        # Mapeo para la tabla "Condiciones Interiores de Diseño" (Página 10)
        # Valores fijos que siempre aparecen
        mapa_de_datos.update({
            'S11MEMORIA_DiseñoInt_TempIntLocal_Invierno': '21',
            'S11MEMORIA_DiseñoInt_TempIntLocal_Verano': '25',
            'S11MEMORIA_DiseñoInt_TempExt_Invierno': '3',
            'S11MEMORIA_DiseñoInt_TempExt_Verano': '37',
            'S11MEMORIA_SistAporteAirePrimario': 'La instalación no incorpora sistema de aporte de aire primario. La ventilación de los locales se garantiza mediante el sistema de ventilación de la vivienda conforme a CTE DB HS 3.'
        })

        # Mapeo condicional para ACS
        servicio_db = datos_equipo['Servicio']
             
        if "ACS" in servicio_db:
            mapa_de_datos['S11MEMORIA_DiseñoInt_TempMinACS'] = '35'
            mapa_de_datos['S11MEMORIA_DiseñoInt_TempMaxACS'] = '31'
        
        # Mapeo condicional para Velocidad del Agua
        # Por ahora, asumimos que no es AIRE-AIRE. Cuando integremos equipos, esta lógica será más compleja.
        if "Calefacción" in servicio_db:
             mapa_de_datos['S11MEMORIA_VmaxAguaCalefaccion'] = '1,2'

        # Mapeo condicional para Velocidad del Aire
        if 'equipo_terminal' in proyecto.keys() and proyecto['equipo_terminal'] == "rejillas(Equipo por conductos)":
            mapa_de_datos['S11MEMoria_VmaxAireConductos'] = '2,5'

            # --- AÑADE ESTE BLOQUE al final de la sección de mapeo ---

        # --- MAPEO DE DATOS DEL EQUIPO SELECCIONADO DESDE LA DB ---
# --- REEMPLAZA ESTE BLOQUE en rellenar_pdf_final ---

        # --- MAPEO DE DATOS DEL EQUIPO SELECCIONADO DESDE LA DB ---
        if datos_equipo:
            print("DEBUG: Mapeando datos del equipo encontrado...")
        # Mapeo directo con los nombres de campo del PDF que me has pasado
            mapa_de_datos.update({
            'S1MEMORIA_Potencia Nominal instalacion': str(datos_equipo['Potencia_Nominal__kW_']),
            'S2MEMORIA_Potencia total calefaccion': str(datos_equipo['Potencia_Útil_Nom__Calefacción__kW_']),
            'S5MEMORIA_POTENCIA PRODUC ACS': str(datos_equipo['Potencia_Útil_Nom__ACS__kW_']),
            'S2MEMORIA_SCOP': str(datos_equipo['Rendimiento_medio_estacional_porc']),
            'S2MEMORIA_COP': str(datos_equipo['Rendimiento_instantáneo_máximo']),
            'S2MEMORIA_Potencia del generador mas potente': str(datos_equipo['Potencia_Nominal__kW_']),
            'S2MEMORIA_N°CHIMENEAS': str(datos_equipo['Número_de_chimeneas']),
            'S2MEMORIA_DIAMETRO': str(datos_equipo['Conexión_Salida_Humos__mm_']),
            'S2MEMORIA_MATERIAL': str(datos_equipo['Material']),
            'S6MEMORIA_PotTotal Calderas': str(datos_equipo['Potencia_Nominal__kW_']),
            'S6MEMORIA_Rendimiento inst  max_COP': str(datos_equipo['Rendimiento_instantáneo_máximo']),
            'S6MEMORIA_Rendimiento medio estacional_SCOP': str(datos_equipo['Rendimiento_medio_estacional_porc']),
            'S6MEMORIA_N° de calderas': str(proyecto['num_generadores'])
        })
        
            # Lógica para el Tipo de Equipo (checkboxes)
            if 'Tipo_de_Equipo' in datos_equipo.keys() and datos_equipo['Tipo_de_Equipo']:
                tipo_equipo = datos_equipo['Tipo_de_Equipo'].strip()
                if tipo_equipo == 'Caldera':
                    mapa_de_datos['S2MEMORIA_TIPOGEN_Caldera'] = '/On'
                    mapa_de_datos['S2MEMORIA_TIPOGEN_BdC'] = '/Off'
                elif tipo_equipo == 'Bomba de calor':
                    mapa_de_datos['S2MEMORIA_TIPOGEN_Caldera'] = '/Off'
                    mapa_de_datos['S2MEMORIA_TIPOGEN_BdC'] = '/On'
                # Puedes añadir lógica para OTRO si es necesario
                
            # Lógica para el Combustible (checkboxes) - VERSIÓN COMPLETA
            if 'fuente_energia' in proyecto.keys() and proyecto['fuente_energia']:
                # Leemos la elección final del usuario desde la tabla 'proyectos'
                combustible = proyecto['fuente_energia'].strip().lower()
                
                # Desmarcamos todos primero para asegurar que solo uno quede marcado
                mapa_de_datos.update({
                    'S1MEMORIA_FUENTE_Gas Natural': '/Off',
                    'S1MEMORIA_FUENTE_GLP': '/Off',
                    'S1MEMORIA_FUENTE_Gasóleo': '/Off',
                    'S1MEMORIA_FUENTE_Electricidad': '/Off',
                    'S1MEMORIA_FUENTE_Biomasa pellets': '/Off',
                    'S1MEMORIA_FUENTE_Biomasa astillas': '/Off',
                    'S1MEMORIA_FUENTE_Biomasa hueso de aceitunas': '/Off',
                    'S1MEMORIA_FUENTE_Solar Térmica': '/Off',
                    'S1MEMORIA_FUENTE_Solar FV': '/Off',
                    'S1MEMORIA_FUENTE_Otros': '/Off'
                })

                # Marcamos el correcto basándonos en el texto de la base de datos
                if 'gas natural' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Gas Natural'] = '/On'
                elif 'glp' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_GLP'] = '/On'
                elif 'gasóleo' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Gasóleo'] = '/On'
                elif 'electricidad' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Electricidad'] = '/On'
                elif 'pellets' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Biomasa pellets'] = '/On'
                elif 'astillas' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Biomasa astillas'] = '/On'
                elif 'hueso' in combustible: # Usamos una palabra clave única
                    mapa_de_datos['S1MEMORIA_FUENTE_Biomasa hueso de aceitunas'] = '/On'
                elif 'solar térmica' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Solar Térmica'] = '/On'
                elif 'solar fv' in combustible:
                    mapa_de_datos['S1MEMORIA_FUENTE_Solar FV'] = '/On'
                else:
                    mapa_de_datos['S1MEMORIA_FUENTE_Otros'] = '/On'


            # Lógica para el Sistema Típico (checkboxes)
            if 'Sistema_Tipico' in datos_equipo.keys() and datos_equipo['Sistema_Tipico']:
                sistema = datos_equipo['Sistema_Tipico'].strip()
                mapa_de_datos['S2MEMORIA_Agua  Agua'] = '/On' if sistema == 'Agua - Agua' else '/Off'
                mapa_de_datos['S2MEMORIA_Agua  Aire'] = '/On' if sistema == 'Agua - Aire' else '/Off'
                mapa_de_datos['S2MEMORIA_Aire  Agua'] = '/On' if sistema == 'Aire - Agua' else '/Off'
                mapa_de_datos['S2MEMORIA_Aire  Aire'] = '/On' if sistema == 'Aire - Aire' else '/Off'

            # Lógica para Tipo de Sistema ACS (Automático)
            # Basado en tu razonamiento, si el equipo da ACS, es un sistema Descentralizado.
            if 'Servicio' in datos_equipo.keys() and 'ACS' in datos_equipo['Servicio']:
                mapa_de_datos['S5MEMORIA_TIPOACS_Descentralizado'] = '/On'
                mapa_de_datos['S5MEMORIA_TIPOACS_Centralizado'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPOACS_Produc renov apoyo/acum descentralizado'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPOACS_Produc renov apoyo desc, acum centralizada'] = '/Off'
            else:
                # Si el equipo no da ACS, nos aseguramos de que todo esté desmarcado
                mapa_de_datos['S5MEMORIA_TIPOACS_Descentralizado'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPOACS_Centralizado'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPOACS_Produc renov apoyo/acum descentralizado'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPOACS_Produc renov apoyo desc, acum centralizada'] = '/Off'

            #ALGUNOS DATOS DE ACS Pagina 7 IT315-----------------------------------------------------------
            # Lógica para "Sistema de aprovechamiento de renovables"
            # Si el equipo es una Caldera, asumimos que "No aplica".
            if 'Tipo_de_Equipo' in datos_equipo.keys() and datos_equipo['Tipo_de_Equipo'] == 'Caldera':
                mapa_de_datos['S5MEMORIA_SIST APROVE ENER RENOV_No aplica'] = '/On'
            else:
                # Para otros equipos, de momento lo dejamos sin marcar.
                mapa_de_datos['S5MEMORIA_SIST APROVE ENER RENOV_No aplica'] = '/Off'

            # Lógica para Tipo de Acumulación de ACS (Automático)
            # Si el equipo da ACS, asumimos que la acumulación es Descentralizada.
            if 'Servicio' in datos_equipo.keys() and 'ACS' in datos_equipo['Servicio']:
                mapa_de_datos['S5MEMORIA_TIPO ACUM_DESCENTRALIZADA'] = '/On'
                mapa_de_datos['S5MEMORIA_TIPO ACUM_CENTRALIZADA'] = '/Off'
            else:
                # Si no da ACS, nos aseguramos de que ambos estén desmarcados
                mapa_de_datos['S5MEMORIA_TIPO ACUM_DESCENTRALIZADA'] = '/Off'
                mapa_de_datos['S5MEMORIA_TIPO ACUM_CENTRALIZADA'] = '/Off'

            if 'volumen_acumulacion_acs' in proyecto.keys():
                mapa_de_datos['S5MEMORIA_VOLUMEN ACUM ACS'] = proyecto['volumen_acumulacion_acs']

            if 'demanda_acs_litros_dia' in proyecto.keys():
                mapa_de_datos['S5MEMORIA_DEMANDA DIARIA  ACS A 60°C'] = str(proyecto['demanda_acs_litros_dia'])

                    # Lógica para Tipo de Generador de Calor en ACS
            if 'Tipo_de_Equipo' in datos_equipo.keys() and datos_equipo['Tipo_de_Equipo']:
                tipo_equipo = datos_equipo['Tipo_de_Equipo'].strip()
                if tipo_equipo == 'Caldera':
                    mapa_de_datos['S5MEMORIA_TIPO GEN_CALDERA'] = '/On'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_BdC'] = '/Off'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_OTRO'] = '/Off'
                elif tipo_equipo == 'Bomba de calor':
                    mapa_de_datos['S5MEMORIA_TIPO GEN_CALDERA'] = '/Off'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_BdC'] = '/On'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_OTRO'] = '/Off'
                else:
                    mapa_de_datos['S5MEMORIA_TIPO GEN_CALDERA'] = '/Off'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_BdC'] = '/Off'
                    mapa_de_datos['S5MEMORIA_TIPO GEN_OTRO'] = '/On'
            #------------------------------------------------------------------------------------------------

                    # Lógica para Combustible en la sección 6 (Datos Caldera)
            if 'Combustible' in datos_equipo.keys() and datos_equipo['Combustible']:
                combustible = datos_equipo['Combustible'].strip().lower()
                
                # Marcamos el checkbox correcto basándonos en el combustible del equipo
                if 'gas natural' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_Gas Natural'] = '/On'
                elif 'glp' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_GLP'] = '/On'
                elif 'gasóleo' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_Gasóleo'] = '/On'
                elif 'electricidad' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_Electricidad'] = '/On'
                elif 'pellets' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_Biomasa pellets'] = '/On'
                elif 'astillas' in combustible:
                    mapa_de_datos['S6MS6MEMORIA_COMBUSTIBLE_Biomasa astillas'] = '/On'
                elif 'hueso' in combustible:
                    mapa_de_datos['S6MEMORIA_COMBUSTIBLE_Biomasa hueso aceituna'] = '/On'

            # Lógica para Servicios en la sección 6 (Datos Caldera)
            if 'Servicio' in datos_equipo.keys() and datos_equipo['Servicio']:
                servicio_db = datos_equipo['Servicio']
                
                # Marcamos cada checkbox si el servicio correspondiente está en el texto
                if "Calefacción" in servicio_db:
                    mapa_de_datos['S6MEMORIA_SERVICIOS_Calefacción'] = '/On'
                if "ACS" in servicio_db:
                    mapa_de_datos['S6MEMORIA_SERVICIOS_ACS'] = '/On'
                if "piscinas" in servicio_db: # Usamos una palabra clave
                    mapa_de_datos['S6MEMORIA_SERVICIOS_Climatización de piscinas'] = '/On'
            #------------------------------------------------------------------------------------------------------------------

            # Lógica para la tabla de Regulación y Control (Página 11)
            if 'Servicio' in datos_equipo.keys() and datos_equipo['Servicio']:
                servicios_activos = datos_equipo['Servicio']
            else:
                servicios_activos = ""
            
            mapa_control = {
                'Control_Termostato': ["S11MEMORIA_ReguYCtrl_11", "S11MEMORIA_ReguYCtrl_12", "S11MEMORIA_ReguYCtrl_13"],
                'Control_VTs': ["S11MEMORIA_ReguYCtrl_21", "S11MEMORIA_ReguYCtrl_22", "S11MEMORIA_ReguYCtrl_23"],
                'Control_SondaFluido': ["S11MEMORIA_ReguYCtrl_31", "S11MEMORIA_ReguYCtrl_32", "S11MEMORIA_ReguYCtrl_33"],
                'Control_SondaExterior': ["S11MEMORIA_ReguYCtrl_41", "S11MEMORIA_ReguYCtrl_42", "S11MEMORIA_ReguYCtrl_43"],
                'Control_Centralita': ["S11MEMORIA_ReguYCtrl_51", "S11MEMORIA_ReguYCtrl_52", "S11MEMORIA_ReguYCtrl_53"],
                'Control_Impulsion': ["S11MEMORIA_ReguYCtrl_61", "S11MEMORIA_ReguYCtrl_62", "S11MEMORIA_ReguYCtrl_63"],
            }

            # --- Lógica Celda por Celda (CORREGIDA SIN .get()) ---
            # Fila 1: Termostato
            if 'Control_Termostato' in datos_equipo.keys() and datos_equipo['Control_Termostato'] and datos_equipo['Control_Termostato'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_Termostato'][0]] = '/On'
                if 'Climatización' in servicios_activos: mapa_de_datos[mapa_control['Control_Termostato'][2]] = '/On'

            # Fila 2: Válvulas Termostáticas
            if 'Control_VTs' in datos_equipo.keys() and datos_equipo['Control_VTs'] and datos_equipo['Control_VTs'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_VTs'][0]] = '/On'
                if 'Climatización' in servicios_activos: mapa_de_datos[mapa_control['Control_VTs'][2]] = '/On'
            
            # Fila 3: Sonda de Fluido
            if 'Control_SondaFluido' in datos_equipo.keys() and datos_equipo['Control_SondaFluido'] and datos_equipo['Control_SondaFluido'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_SondaFluido'][0]] = '/On'
                if 'ACS' in servicios_activos: mapa_de_datos[mapa_control['Control_SondaFluido'][1]] = '/On'

            # Fila 4: Sonda Exterior
            if 'Control_SondaExterior' in datos_equipo.keys() and datos_equipo['Control_SondaExterior'] and datos_equipo['Control_SondaExterior'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_SondaExterior'][0]] = '/On'
                if 'Climatización' in servicios_activos: mapa_de_datos[mapa_control['Control_SondaExterior'][2]] = '/On'

            # Fila 5: Centralita
            if 'Control_Centralita' in datos_equipo.keys() and datos_equipo['Control_Centralita'] and datos_equipo['Control_Centralita'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_Centralita'][0]] = '/On'
                if 'ACS' in servicios_activos: mapa_de_datos[mapa_control['Control_Centralita'][1]] = '/On'
                if 'Climatización' in servicios_activos: mapa_de_datos[mapa_control['Control_Centralita'][2]] = '/On'

            # Fila 6: Termostato Impulsión
            if 'Control_Impulsion' in datos_equipo.keys() and datos_equipo['Control_Impulsion'] and datos_equipo['Control_Impulsion'] != 'No':
                if 'Calefacción' in servicios_activos: mapa_de_datos[mapa_control['Control_Impulsion'][0]] = '/On'
                if 'Climatización' in servicios_activos: mapa_de_datos[mapa_control['Control_Impulsion'][2]] = '/On'
    #----------------------------------------------------------------------------------------------------------------------------------

        # --- MAPEO FINAL: TABLA DE CARGAS CALORÍFICAS ---
        cursor.execute("""
            SELECT lp.nombre_local, lp.superficie_m2, lp.cantidad_elementos,
                   e.Modelo, e.Unidad_Medida, e.Potencia_W_por_Unidad
            FROM Locales_Proyecto lp
            JOIN Emisores e ON lp.emisor_id = e.id
            WHERE lp.proyecto_id = ?
        """, (project_id,))
        
        locales = cursor.fetchall()

        for i, local in enumerate(locales):
            if i >= 9: break

            fila = i + 1
            calculo_cargas = local['superficie_m2'] * 95 
            carga_real = local['cantidad_elementos'] * local['Potencia_W_por_Unidad']

            mapa_de_datos[f'S11_TablaCargas_TipoLocal_{fila}'] = local['nombre_local']
            mapa_de_datos[f'S11_TablaCargas_Superficie_{fila}'] = str(local['superficie_m2'])
            mapa_de_datos[f'S11_TablaCargas_Calculo_{fila}'] = str(round(calculo_cargas, 2))
            mapa_de_datos[f'S11_TablaCargas_Equipo_{fila}'] = local['Modelo']
            mapa_de_datos[f'S11_TablaCargas_Elementos_{fila}'] = f"{local['cantidad_elementos']} {local['Unidad_Medida']}"
            mapa_de_datos[f'S11_TablaCargas_CargaReal_{fila}'] = str(round(carga_real, 2))

    except Exception as e:
        print(f"\nHa ocurrido un error leyendo los datos de la base de datos: {e}")
        traceback.print_exc()
        if conn: conn.close()
        return
    finally:
        if conn:
            conn.close()

    # --- TAREA 2: ESCRIBIR LOS DATOS EN EL PDF ---
    if not proyecto:
        print("No se pudieron cargar los datos del proyecto, no se puede generar el PDF.")
        return
        
    try:
        reader = PdfReader(template_path)
        writer = PdfWriter()
        writer.append(reader)

        for page in writer.pages:
            writer.update_page_form_field_values(page, mapa_de_datos)
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        nombre_salida = f"{proyecto['nombre_proyecto'].replace(' ', '_')}_ID_{project_id}_rellenado.pdf"
        ruta_salida = os.path.join(output_folder, nombre_salida)

        with open(ruta_salida, "wb") as output_stream:
            writer.write(output_stream)
        
        print("\n" + "*" * 50)
        print("¡CERTIFICADO GENERADO CON ÉXITO!")
        print(f"Se ha guardado el archivo en '{ruta_salida}'")
        print("*" * 50)

    except Exception as e:
        print(f"\nHa ocurrido un error al escribir en el archivo PDF: {e}")
        traceback.print_exc()