"""
Módulo encargado de construir los escenarios de choque
y recalcular los valores presentes de los flujos bajo
cada escenario.
Realizando lo siguiente:
1. Calcular los seis escenarios de choque para cada flujo:
    - Choque Paralelo Arriba
    - Choque Paralelo Abajo
    - Choque de Empinamiento
    - Choque de Aplanamiento
    - Choque Corto Arriba
    - Choque Corto Abajo
2. Calcular la tasa de interés correspondiente a cada
   escenario de choque.
3. Calcular el factor de descuento y el valor presente
   de cada flujo bajo cada escenario.
4. Agregar los valores presentes de los flujos para
   obtener el VEP de cada escenario.
"""

# Importaciones necesarias
import pandas as pd
import numpy as np

def construir_escenarios_choque(df_flujos: pd.DataFrame, x: float = 4) -> pd.DataFrame:
    datos = df_flujos.copy()

    # Validar que las columnas requeridas existan
    columnas_requeridas = ["moneda_pago_inicial", "tiempo_vencimiento_anios", "tasa_cec"]
    columnas_faltantes = [columna for columna in columnas_requeridas if columna not in datos.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan las siguientes columnas requeridas en el DataFrame: {', '.join(columnas_faltantes)}")

    # Validar que las columnas necesarias no contengan valores nulos
    for columna in columnas_requeridas:
        if datos[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' contiene valores nulos. No se pueden construir los escenarios de choque")

    # Validar parámetro x de las funciones
    if x <= 0:
        raise ValueError("El parámetro 'x' debe ser mayor que cero")


    # Tamaño en pb de las perturbaciones de las tasas de interés por moneda
    choques_por_moneda = {
        "COP": {
            "S0": 400,
            "S1": 500,
            "S2": 300
        },
        "UVR": {
            "S0": 200,
            "S1": 300,
            "S2": 100
        },
        "USD": {
            "S0": 200,
            "S1": 300,
            "S2": 150
        }
    }

    # Nombres de los choques
    nombres_choques = ["paralelo_arriba",
                        "paralelo_abajo",
                        "corto_arriba",
                        "corto_abajo",
                        "empinamiento",
                        "aplanamiento"]

    # Estandarizar la moneda
    datos["moneda_pago_inicial"] = (datos["moneda_pago_inicial"].astype(str).str.upper().str.strip())

    # Validar que todas las monedas tengan choques definidos
    monedas_no_definidas = (set(datos["moneda_pago_inicial"]) - set(choques_por_moneda.keys()))

    if monedas_no_definidas:
        raise ValueError(f"No existen choques definidos para las siguientes monedas: {sorted(monedas_no_definidas)}")

    # Calcular los escenarios para cada flujo
    for idx, flujo in datos.iterrows():

        moneda = flujo["moneda_pago_inicial"]
        tk = flujo["tiempo_vencimiento_anios"]

        # Obtener S0, S1 y S2 correspondientes a la moneda
        s0 = choques_por_moneda[moneda]["S0"] / 10_000
        s1 = choques_por_moneda[moneda]["S1"] / 10_000
        s2 = choques_por_moneda[moneda]["S2"] / 10_000

        # Factores de corto y largo plazo:
        s_corto = np.exp(-tk / x)
        s_largo = 1 - s_corto

        # Choque paralelo
        choque_paralelo_arriba = s0
        choque_paralelo_abajo = -s0

        # Choque corto
        choque_corto_arriba = s1 * s_corto
        choque_corto_abajo = -s1 * s_corto

        # Choque largo
        choque_largo_arriba = s1 * s_largo
        choque_largo_abajo = -s1 * s_largo

        # Choque de empinamiento
        choque_empinamiento = ( (-0.65 * abs(choque_corto_arriba)) + (0.9 * abs(choque_largo_arriba)))

        # Choque de aplanamiento
        choque_aplanamiento = (0.8 * abs(choque_corto_arriba) - 0.6 * abs(choque_largo_arriba))

        # agrupar y guardar choques
        choques = {"paralelo_arriba": choque_paralelo_arriba,
                    "paralelo_abajo": choque_paralelo_abajo,
                    "corto_arriba": choque_corto_arriba,
                    "corto_abajo": choque_corto_abajo,
                    "empinamiento": choque_empinamiento,
                    "aplanamiento": choque_aplanamiento}

        for nombre, valor in choques.items():
            datos.loc[idx, f"choque_{nombre}"] = valor

        # Guardar factores
        factores = {"s_corto": s_corto, "s_largo": s_largo}

        for nombre, valor in factores.items():
            datos.loc[idx, nombre] = valor

        # Calcular tasas bajo cada escenario
        tasa_base = flujo["tasa_cec"]

        for nombre, choque in choques.items():
            datos.loc[idx, f"tasa_{nombre}"] = (tasa_base + choque)

    # Convertir las columnas calculadas a tipo numérico
    columnas_calculadas = ["s_corto", "s_largo"]

    columnas_calculadas += [f"choque_{nombre}" for nombre in nombres_choques]

    columnas_calculadas += [f"tasa_{nombre}" for nombre in nombres_choques]

    datos[columnas_calculadas] = (datos[columnas_calculadas].apply(pd.to_numeric))

    return datos

# Calcular el valor presente (VP) de los flujos bajo cada escenario de choque
def calcular_vp_escenarios(df_flujos: pd.DataFrame) -> pd.DataFrame:

    datos = df_flujos.copy()

    # Validar que las columnas requeridas existan
    columnas_requeridas = ["importe_flujo_caja",
                            "tiempo_vencimiento_anios",
                            "tasa_paralelo_arriba",
                            "tasa_paralelo_abajo",
                            "tasa_empinamiento",
                            "tasa_aplanamiento",
                            "tasa_corto_arriba",
                            "tasa_corto_abajo"]

    columnas_faltantes = [columna for columna in columnas_requeridas if columna not in datos.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan las siguientes columnas requeridas en el DataFrame: {', '.join(columnas_faltantes)}")

    # Validar que las columnas necesarias no contengan valores nulos
    for columna in columnas_requeridas:
        if datos[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' contiene valores nulos. No se puede calcular el valor presente bajo los escenarios")

    # Relacionar cada escenario con su tasa correspondiente
    escenarios = {"paralelo_arriba": "tasa_paralelo_arriba",
                    "paralelo_abajo": "tasa_paralelo_abajo",
                    "empinamiento": "tasa_empinamiento",
                    "aplanamiento": "tasa_aplanamiento",
                    "corto_arriba": "tasa_corto_arriba",
                    "corto_abajo": "tasa_corto_abajo"}

    # Calcular el VP para cada escenario
    for nombre_escenario, columna_tasa in escenarios.items():

        # Calcular el factor de descuento
        factor_descuento = np.exp(-datos[columna_tasa] * datos["tiempo_vencimiento_anios"])

        # Calcular el valor presente
        datos[f"vp_{nombre_escenario}"] = (datos["importe_flujo_caja"] * factor_descuento)

    return datos

# Calcular el Valor Económico del Portafolio (VEP) para cada escenario de choque
def calcular_vep_escenarios(df_flujos: pd.DataFrame) -> dict:

    datos = df_flujos.copy()

    # Validar que las columnas requeridas existan
    columnas_requeridas = ["vp_paralelo_arriba",
                            "vp_paralelo_abajo",
                            "vp_empinamiento",
                            "vp_aplanamiento",
                            "vp_corto_arriba",
                            "vp_corto_abajo"]

    columnas_faltantes = [columna for columna in columnas_requeridas if columna not in datos.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan las siguientes columnas requeridas en el DataFrame: {', '.join(columnas_faltantes)}")

    # Validar que las columnas necesarias no contengan valores nulos
    for columna in columnas_requeridas:
        if datos[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' contiene valores nulos. No se puede calcular el VEP de choque")

    # Relacionar cada escenario con su columna de VP
    escenarios = {"VEP Paralelo Arriba": "vp_paralelo_arriba",
                    "VEP Paralelo Abajo": "vp_paralelo_abajo",
                    "VEP Empinamiento": "vp_empinamiento",
                    "VEP Aplanamiento": "vp_aplanamiento",
                    "VEP Corto Arriba": "vp_corto_arriba",
                    "VEP Corto Abajo": "vp_corto_abajo"}

    # Calcular el VEP de cada escenario
    resultados_choque = {}

    for nombre_vep, columna_vp in escenarios.items():
        resultados_choque[nombre_vep] = datos[columna_vp].sum()

    return resultados_choque

# Calcular el impacto de cada escenario de choque sobre el Valor Económico del Portafolio (VEP)
def calcular_impacto(resultados: dict) -> dict:

    # Validar que exista el VEP Base
    if "VEP Base" not in resultados:
        raise ValueError("No se encontró 'VEP Base' en los resultados")

    escenarios = ["VEP Paralelo Arriba",
                    "VEP Paralelo Abajo",
                    "VEP Empinamiento",
                    "VEP Aplanamiento",
                    "VEP Corto Arriba",
                    "VEP Corto Abajo"]

    # Validar que existan todos los VEP de choque
    escenarios_faltantes = [escenario for escenario in escenarios if escenario not in resultados]

    if escenarios_faltantes:
        raise ValueError(f"Faltan los siguientes VEP de choque: {', '.join(escenarios_faltantes)}")

    # Obtener VEP Base
    vep_base = resultados["VEP Base"]

    # Calcular el impacto de cada escenario
    impacto = {}

    for escenario in escenarios:
        impacto[escenario.replace("VEP ", "Delta VEP ")] = (vep_base - resultados[escenario])

    return impacto