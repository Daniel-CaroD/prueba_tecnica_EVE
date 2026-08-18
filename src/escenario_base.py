"""
Módulo encargado de crear el escenario base para cada flujo,
realizando lo siguiente:
1. Calcular el tiempo al vencimiento en años (punto medio).
2. Obtener la tasa correspondiente a partir de la curva CEC.
3. Aplicar interpolación lineal o exponencial cuando el plazo exacto no exista en la curva.
4. Calcular el valor presente del flujo.
5. Calcular el Valor Económico del Portafolio (VEP) Base.
"""

# Importaciones necesarias
import pandas as pd
import numpy as np

# Caluclar el tiempo de vencimiento en años (punto medio) para cada flujo
def calcular_tiempo_vencimiento(df_flujos: pd.DataFrame) -> pd.DataFrame:
    datos = df_flujos.copy()

    # Validar que las columnas requeridas existan
    columnas_requeridas = ["tipo_indice",
                            "fecha_corte",
                            "fecha_pago_flujo",
                            "fecha_siguiente_reprecio"]

    columnas_faltantes = [columna
                          for columna in columnas_requeridas
                          if columna not in datos.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan las siguientes columnas requeridas en el DataFrame: {', '.join(columnas_faltantes)}")

    # Validar que tipo_indice y fecha_corte no contenga valores nulos
    if datos["tipo_indice"].isnull().any():
        raise ValueError("La columna 'tipo_indice' contiene valores nulos. No se puede calcular el tiempo al vencimiento")

    if datos["fecha_corte"].isnull().any():
        raise ValueError("La columna 'fecha_corte' contiene valores nulos. No se puede calcular el tiempo al vencimiento")

    # Si tipo_indice = FLOATING validar que fecha_siguiente_reprecio no contenga valores nulos
    mascara_floating =  datos["tipo_indice"].str.upper() == "FLOATING"

    if datos.loc[mascara_floating, "fecha_siguiente_reprecio"].isnull().any():
        raise ValueError("La columna 'fecha_siguiente_reprecio' contiene valores nulos para flujos variables/flotantes. No se puede calcular el tiempo al vencimiento")

    # Si tipo_indice <> FLOATING validar que fecha_pago_flujo no contenga valores nulos
    if datos.loc[~mascara_floating, "fecha_pago_flujo"].isnull().any():
        raise ValueError("La columna 'fecha_pago_flujo' contiene valores nulos para flujos fijos. No se puede calcular el tiempo al vencimiento")

    # Crear columna fecha_relevante
    datos["fecha_relevante"] = datos["fecha_pago_flujo"]
    datos.loc[mascara_floating, "fecha_relevante"] = datos.loc[mascara_floating, "fecha_siguiente_reprecio"]

    # Calcular plazo hasta fecha relevante
    datos["plazo_dias"] = (datos["fecha_relevante"] - datos["fecha_corte"]).dt.days

    # Convertir plazo a años
    datos["plazo_anios"] = datos["plazo_dias"] / 365

    # Asignación de punto medio de vencimiento
    bandas_tiempo = {
    (0, 1 / 365): 0.0028,
    (1 / 365, 1 / 12): 0.0417,
    (1 / 12, 3 / 12): 0.1667,
    (3 / 12, 6 / 12): 0.375,
    (6 / 12, 9 / 12): 0.625,
    (9 / 12, 1): 0.8075,
    (1, 1.5): 1.25,
    (1.5, 2): 1.75,
    (2, 3): 2.5,
    (3, 4): 3.5,
    (4, 5): 4.5,
    (5, 6): 5.5,
    (6, 7): 6.5,
    (7, 8): 7.5,
    (8, 9): 8.5,
    (9, 10): 9.5,
    (10, 15): 12.5,
    (15, 20): 17.5,
    (20, float("inf")): 25}

    for (limite_inferior, limite_superior), punto_medio in bandas_tiempo.items():
        mascara = (datos["plazo_anios"] > limite_inferior) & (datos["plazo_anios"] <= limite_superior)
        datos.loc[mascara, "tiempo_vencimiento"] = punto_medio
    
    # Validar que no hayan 'tiempo_vencimiento' nulos
    if datos["tiempo_vencimiento"].isnull().any():
        raise ValueError("No fue posible asignar una banda de tiempo a uno o más flujos.")
    
    df_flujos["tiempo_vencimiento_anios"] = datos["tiempo_vencimiento"]
    return df_flujos

# Obtener la tasa correspondiente a partir de la curva CEC
def obtener_tasa_cec(df_flujos: pd.DataFrame, df_curvasCEC: pd.DataFrame, interpolacion: str = "lineal") -> pd.DataFrame:

    datos = df_flujos.copy()
    curvas = df_curvasCEC.copy()
    interpolacion = interpolacion.lower()

    # Validar método de interpolación seleccionado
    if interpolacion not in ("lineal", "exponencial"):
        raise ValueError(f"El método de interpolación {interpolacion} no está definido. Debe ser 'lineal' o 'exponencial'")

    # Validar que las columnas requeridas existan
    columnas_flujos = {"moneda_pago_inicial", "fecha_corte", "tiempo_vencimiento_anios"}
    columnas_curvas = {"curve_name", "fecha_corte", "tenor", "zero_coupon_rate"}

    faltantes_flujos = columnas_flujos - set(datos.columns)
    faltantes_curvas = columnas_curvas - set(curvas.columns)

    if faltantes_flujos:
        raise ValueError(f"Faltan columnas requeridas en los flujos: {faltantes_flujos}")

    if faltantes_curvas:
        raise ValueError(f"Faltan columnas requeridas en las curvas CEC: {faltantes_curvas}")

     # Validar que las columnas necesarias no contengan valores nulos
    for columna in ("fecha_corte", "moneda_pago_inicial", "tiempo_vencimiento_anios"):
        if datos[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' de los flujos contiene valores nulos")

    for columna in ("fecha_corte", "curve_name"):
        if curvas[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' de las curvas CEC contiene valores nulos")

    # Relacionar cada moneda con su curva CEC correspondiente
    curvas_por_moneda = {"COP": "COP COP CEC",
                        "UVR": "UVR COP CEC",
                        "USD": "USD USD: BONOS TREASURIES"}

    # Convertir los tenores de la curva CEC a días
    curvas["tenor_dias"] = (curvas["tenor"].str.extract(r"(\d+)")[0].astype(float))

    if curvas["tenor_dias"].isnull().any():
        raise ValueError("Existen valores de 'tenor' en las curvas CEC que no tienen el formato esperado (#D)")

    # Obtener la tasa correspondiente para cada flujo
    datos["tasa_cec"] = pd.NA

    for idx, flujo in datos.iterrows():
        fecha_corte = flujo["fecha_corte"]
        moneda = flujo["moneda_pago_inicial"].upper()
        plazo_anios = flujo["tiempo_vencimiento_anios"]

        # Validar que la moneda tenga una curva definida
        if moneda not in curvas_por_moneda:
            raise ValueError(f"No existe una curva CEC definida para la moneda '{moneda}'")

        nombre_curva = curvas_por_moneda[moneda]

        # Seleccionar la curva correspondiente a la moneda y fecha de corte
        curva = curvas[(curvas["curve_name"] == nombre_curva) & (curvas["fecha_corte"] == fecha_corte)].copy()

        if curva.empty:
            raise ValueError(f"No existe una curva CEC para la moneda '{moneda}' y la fecha de corte {fecha_corte}")

        # Convertir el punto medio de años a días
        plazo_dias = plazo_anios * 365

        # Buscar coincidencia exacta en el tenor
        coincidencia = curva[(curva["tenor_dias"] - plazo_dias).abs() < 1e-6]

        if not coincidencia.empty:
            datos.loc[idx, "tasa_cec"] = (coincidencia.iloc[0]["zero_coupon_rate"])
            continue

        # Si no hay conicidencia exacta en el tenor:
        # Buscar nodo anterior
        curva_anterior = curva[curva["tenor_dias"] < plazo_dias].sort_values("tenor_dias")

        # Buscar nodo siguiente
        curva_siguiente = curva[curva["tenor_dias"] > plazo_dias].sort_values("tenor_dias")

        # Validar que existan ambos nodos
        if curva_anterior.empty or curva_siguiente.empty:
            raise ValueError(f"No es posible interpolar la tasa CEC para el plazo {plazo_anios} años ({plazo_dias:.4f} días), la moneda '{moneda}' y la fecha {fecha_corte}. El plazo está fuera del rango de la curva.")

        # Obtener nodos inmediatamente anterior y siguiente
        nodo_anterior = curva_anterior.iloc[-1]
        nodo_siguiente = curva_siguiente.iloc[0]

        # Plazos de los nodos
        t1 = nodo_anterior["tenor_dias"]
        t2 = nodo_siguiente["tenor_dias"]

        # Tasas de los nodos
        r1 = nodo_anterior["zero_coupon_rate"]
        r2 = nodo_siguiente["zero_coupon_rate"]

        # Interpolación lineal
        if interpolacion == "lineal":
            tasa = (r1 + ((plazo_dias - t1) / (t2 - t1)) * (r2 - r1))

        # Interpolación exponencial mediante factores de descuento
        else:
            # Calcular factores de descuento de los nodos
            factor_1 = np.exp(-r1 * t1)
            factor_2 = np.exp(-r2 * t2)

            # Interpolar exponencialmente los factores de descuento
            factor = factor_1 * ((factor_2 / factor_1) ** ((plazo_dias - t1) / (t2 - t1)))

            # Convertir el factor interpolado nuevamente a tasa
            tasa = -np.log(factor) / plazo_dias

        datos.loc[idx, "tasa_cec"] = tasa

    # Convertir la tasa a numéro
    datos["tasa_cec"] = pd.to_numeric(datos["tasa_cec"])

    df_flujos["tasa_cec"] = datos["tasa_cec"]
    return df_flujos

# Calcular el valor presente de cada flujo
def calcular_valor_presente(df_flujos: pd.DataFrame) -> pd.DataFrame:
    datos = df_flujos.copy()

     # Validar que las columnas requeridas existan
    columnas_requeridas = ["importe_flujo_caja", "tasa_cec", "tiempo_vencimiento_anios"]

    columnas_faltantes = [columna
                          for columna in columnas_requeridas
                          if columna not in datos.columns]

    if columnas_faltantes:
        raise ValueError(f"Faltan las siguientes columnas requeridas en el DataFrame: {', '.join(columnas_faltantes)}")

    # Validar que las columnas necesarias no contengan valores nulos
    for columna in columnas_requeridas:
        if datos[columna].isnull().any():
            raise ValueError(f"La columna '{columna}' contiene valores nulos. No se puede calcular el valor presente")

    # Calcular el factor de descuento
    datos["factor_descuento"] = np.exp(-datos["tasa_cec"] * datos["tiempo_vencimiento_anios"])

    # Calcular el valor presente
    datos["vp_base"] = (datos["importe_flujo_caja"] * datos["factor_descuento"])

    df_flujos["vp_base"] = datos["vp_base"]

    return df_flujos

# Calcular el VEP Base
def calcular_vep_base(df_flujos: pd.DataFrame) -> float:
    datos = df_flujos.copy()

     # Validar que la columna requerida exista
    if "vp_base" not in datos.columns:
        raise ValueError("La columna 'vp_base' no existe. Debe calcularse antes de obtener el VEP Base")

    # Validar que no contenga valores nulos
    if datos["vp_base"].isnull().any():
        raise ValueError("La columna 'vp_base' contiene valores nulos. No se puede calcular el VEP Base")

    # Validar que la columna sea numérica
    if not pd.api.types.is_numeric_dtype(datos["vp_base"]):
        raise ValueError("La columna 'vp_base' debe ser numérica para calcular el VEP Base")

    # Calcular el VEP Base como la suma de los valores presentes
    vep_base = datos["vp_base"].sum()

    return float(vep_base)