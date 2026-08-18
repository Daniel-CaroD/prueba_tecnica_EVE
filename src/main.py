"""
Archivo principal del proyecto.
Encargado de orquestar las diferentes funcionalidades del proyecto
y ejecutar el flujo del mismo.
"""

# Imports y definición de rutas
from src.lectura_datos import leer_datos, mostrar_informacion, validar_tipos
from src.escenario_base import calcular_tiempo_vencimiento, obtener_tasa_cec, calcular_valor_presente, calcular_vep_base
from src.escenario_choque import construir_escenarios_choque, calcular_vp_escenarios, calcular_vep_escenarios, calcular_impacto
from src.exportar_resultados import exportar_resultados

ruta_flujos = "data/input/Flujos.xlsx"
ruta_curvasCEC = "data/input/Curvas_CEC.xlsx"
ruta_salida = "data/output/resultados.xlsx"

def main():

    # ==========================================================================
    # Paso 1: Lectura y gestión de los datos almacenados en los archivos .xlsx
    # ==========================================================================

    # Almacenar datos en dataframes
    flujos = leer_datos(ruta_flujos, "Sheet")
    curvasCEC = leer_datos(ruta_curvasCEC, "Sheet")

    # Mostrar información general de los dataframes
    mostrar_informacion(flujos, "Flujos")
    mostrar_informacion(curvasCEC, "CurvasCEC")

    # Definir tipado de columnas
    columnas_flujos = {
        "numericas": ("saldo", "importe_flujo_caja"),
        "categoricas": ("estrategia", "posicion", "codigo_posicion", "frecuencia_pago_principal_pata_1", "indice_principal_mostrado_pata_1", 
                        "tipo_tasa", "tipo_indice", "moneda_pago_inicial", "rn_operacion", "tipo_importe_flujo_caja"),
        "fecha": ("fecha_corte", "fecha_pago_flujo", "fecha_siguiente_reprecio")
    }

    columnas_curvasCEC = {
        "numericas": ("zero_coupon_rate",),
        "categoricas": ("curve_name", "tenor"),
        "fecha": ("fecha_corte",)
    }

    # Validar y convertir tipado de columnas
    validar_tipos(flujos, columnas_flujos, "Flujos")
    validar_tipos(curvasCEC, columnas_curvasCEC, "CurvasCEC")
    
    # ==========================================================================
    # Paso 2: Construcción del escenario base
    # ==========================================================================

    # Calcular el tiempo de vencimiento en años (punto medio) para cada flujo
    flujos = calcular_tiempo_vencimiento(flujos)

    # Obtener la tasa correspondiente a partir de la curva CEC
    flujos = obtener_tasa_cec(flujos, curvasCEC, interpolacion="lineal") # <- Interpolación puede ser lineal o exponencial

    # Calcular el valor presente del flujo
    flujos = calcular_valor_presente(flujos)

    # ==========================================================================
    # Paso 3: Cálculo del Valor Económico del Portafolio (VEP) Base
    # ==========================================================================

    vep_base = calcular_vep_base(flujos)

    # ==========================================================================
    # Paso 4:  Construcción de escenarios de choque
    # ==========================================================================

    flujos = construir_escenarios_choque(flujos, x=4)
    flujos = calcular_vp_escenarios(flujos)
    vep_choques = calcular_vep_escenarios(flujos)

    resultados = {"VEP Base": vep_base,
                  **vep_choques}  

    # ==========================================================================
    # Paso 5:  Cálculo del impacto
    # ==========================================================================

    impacto_choques = calcular_impacto(resultados)

    # ==========================================================================
    # Exportar resultados
    # ==========================================================================

    resultados = {**resultados,
                  **impacto_choques}
    exportar_resultados(flujos, resultados, ruta_salida)  

if __name__ == "__main__":
    main()