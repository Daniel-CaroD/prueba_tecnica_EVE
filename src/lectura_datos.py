"""
Módulo encargado de leer y gestionar los datos almacenados en archivos .xlsx
"""

# Importaciones necesarias
import pandas as pd

# Lee los datos y aplica validaciones generales
def leer_datos(ruta: str, nombre_hoja: str) -> pd.DataFrame:
    try:
        datos =  pd.read_excel(ruta, sheet_name=nombre_hoja)

        # Validar que el archivo contenga datos
        if datos.empty:
            raise ValueError(f"[Error] El archivo {ruta} - {nombre_hoja}  está vacío")
        
        # Si no presenta ningún error, retornar el DataFrame
        print(f"Los datos del archivo {ruta} - {nombre_hoja} se han leído correctamente")
        print("")

        return datos

    except Exception as e:
        raise ValueError(f"[Error] Error al leer el archivo {ruta}: {e}")

# Imprime la información general del Dataframe, para verificar posibles inconsistencias
def mostrar_informacion(datos: pd.DataFrame, nombre: str) -> None:
    print(f"========= Información de {nombre} =========")

    print("Primeros registros:")
    print(datos.head(3))

    print("")
    print(f"Número de registros: {datos.shape[0]}")
    print(f"Número de columnas: {datos.shape[1]}")

    print("")
    print("Tipos de datos:")
    print(datos.dtypes)

    print("==============================================")
    print("")

# Valida y convierte los tipos de datos según los parámetros establecidos
def validar_tipos(datos: pd.DataFrame, columnas: dict, nombre: str) -> None:

    # Validar y convertir columnas numéricas
    for columna in columnas["numericas"]:

        if not pd.api.types.is_numeric_dtype(datos[columna]):
            valores_originales = datos[columna].copy()
            datos[columna] = pd.to_numeric(datos[columna], errors="coerce")

            valores_invalidos = (valores_originales.notna() & datos[columna].isna())

            if valores_invalidos.any():
                raise ValueError(f"[Error] La columna {columna} de {nombre} contiene valores que no pueden convertirse a números")

    # Convertir columnas categóricas a texto
    for columna in columnas["categoricas"]:
        datos[columna] = datos[columna].astype("string")

    # Validar y convertir columnas de fecha
    for columna in columnas["fecha"]:

        if not pd.api.types.is_datetime64_any_dtype(datos[columna]):
            valores_originales = datos[columna].copy()
            datos[columna] = pd.to_datetime(datos[columna], errors="coerce")

            valores_invalidos = (valores_originales.notna()& datos[columna].isna())

            if valores_invalidos.any():
                raise ValueError(f"[Error] La columna {columna} de {nombre} contiene valores que no pueden convertirse a fechas.")