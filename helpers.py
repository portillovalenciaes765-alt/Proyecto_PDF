# Módulo: helpers.py
# Responsabilidad: Contiene pequeñas funciones de ayuda.

def mostrar_tabla_locales(locales):
    """Muestra una tabla con los locales añadidos."""
    if not locales:
        print("Aún no se han añadido locales.")
        return
    
    print("\n--- Resumen de Locales Añadidos ---")
    print(f"{'Local':<20} | {'Emisor':<30} | {'Cantidad':<15}")
    print("-" * 70)
    for local in locales:
        cantidad_str = f"{local['cantidad_elementos']} {local['unidad_medida']}"
        print(f"{local['nombre_local']:<20} | {local['emisor_texto']:<30} | {cantidad_str:<15}")
    print("-" * 70)