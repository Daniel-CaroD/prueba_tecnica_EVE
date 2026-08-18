"""
Módulo encargado de exportar los resultados obtenidos
en un archivo .xlsx con dos hojas:
1. Flujos: DataFrame con las columnas originales y las columnas calculadas.
2. Resultados: resultados agregados de los cálculos realizados.
"""

# Importaciones necesarias
import pandas as pd

from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def exportar_resultados(df_flujos: pd.DataFrame, resultados: dict, ruta_salida: str) -> None:
    
    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:

        # Exportar DataFrame de flujos
        df_flujos.to_excel(writer, sheet_name="Flujos", index=False)

        # Crear DataFrame de resultados
        df_resultados = pd.DataFrame(list(resultados.items()), columns=["Resultado", "Valor"])

        # Exportar resultados
        df_resultados.to_excel(writer, sheet_name="Resultados", index=False)

        # Obtener hojas de Excel
        hoja_flujos = writer.sheets["Flujos"]
        hoja_resultados = writer.sheets["Resultados"]

        # Estilo de encabezados
        relleno_gris = PatternFill(fill_type="solid", fgColor="808080")

        fuente_encabezado = Font(bold=True, color="FFFFFF")

        # Aplicar formato a ambas hojas
        for hoja in (hoja_flujos, hoja_resultados):

            # Formato de encabezados
            for celda in hoja[1]:
                celda.fill = relleno_gris
                celda.font = fuente_encabezado
                celda.alignment = Alignment(horizontal="center", vertical="center")

            # Ajustar ancho de columnas
            for columna in hoja.columns:
                longitud_maxima = 0
                letra_columna = get_column_letter(columna[0].column)

                for celda in columna:
                    if celda.value is not None:
                        longitud_maxima = max(longitud_maxima, len(str(celda.value)))

                hoja.column_dimensions[letra_columna].width = (longitud_maxima + 2)

        # Agregar filtros a la tabla de flujos
        hoja_flujos.auto_filter.ref = hoja_flujos.dimensions