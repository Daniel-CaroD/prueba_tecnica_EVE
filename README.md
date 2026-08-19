# Prueba Técnica --- Cálculo del Valor Económico del Patrimonio (VEP)
### Gerencia de Riesgo de Liquidez y Tasa de Interés

**Autor:** Daniel Steven Caro Durango
**Fecha:** 19 de Agosto de 2026

---

## Tabla de contenido

1. [Descripción general](#descripción-general)
2. [Estructura del proyecto](#estructura-del-proyecto)
3. [Archivos de entrada](#archivos-de-entrada)
4. [Requisitos](#requisitos)
5. [Configuración del entorno virtual](#configuración-del-entorno-virtual)
6. [Ejecución](#ejecución)
7. [Flujo general de cálculo](#flujo-general-de-cálculo)
8. [Paso 1 --- Lectura y control de datos](#paso-1--lectura-y-control-de-datos)
9. [Paso 2 --- Construcción del escenario base](#paso-2--construcción-del-escenario-base)
10. [Valor presente del escenario base](#valor-presente-del-escenario-base)
11. [Paso 3 --- VEP Base](#paso-3--vep-base)
12. [Paso 4 --- Construcción de escenarios de choque](#paso-4--construcción-de-escenarios-de-choque)
13. [Tasas bajo cada escenario](#tasas-bajo-cada-escenario)
14. [Valor presente bajo los escenarios de choque](#valor-presente-bajo-los-escenarios-de-choque)
15. [VEP bajo cada escenario](#vep-bajo-cada-escenario)
16. [Impacto sobre el VEP](#impacto-sobre-el-vep)
17. [Paso 5 --- Cálculo del impacto](#paso-5--cálculo-del-impacto)
18. [Controles de calidad y manejo de errores](#controles-de-calidad-y-manejo-de-errores)
19. [Resultados de salida](#resultados-de-salida)
20. [Decisiones de diseño](#decisiones-de-diseño)

---

## Descripción general

Este proyecto implementa en Python una versión del cálculo del **Valor Económico del Patrimonio (VEP)** para un portafolio de inversiones, utilizando los flujos proyectados suministrados y una curva de descuento CEC.

La solución sigue los cinco pasos definidos en la prueba técnica:

1. Lectura y control inicial de los datos.
2. Construcción del escenario base.
3. Cálculo del VEP base.
4. Construcción de los seis escenarios de choque.
5. Cálculo del impacto mediante `Delta_VEP = VEP_Base - VEP_Choque`.

El proyecto se desarrolló siguiendo las indicaciones establecidas en la guía de la prueba, incorporando controles de calidad y validaciones orientadas a reducir posibles incidencias tanto en los insumos proporcionados como durante la ejecución y modificación del código. Asimismo, se buscó desarrollar una solución reproducible y versátil, de manera que pueda ser aplicada a diferentes conjuntos de datos y escenarios bajo las condiciones definidas por la metodología.

Como principal referencia metodológica para el desarrollo de los cálculos se utilizó el Anexo 15 del Capítulo XXXI del SIAR, complementado con las indicaciones y condiciones específicas establecidas en la guía de la prueba técnica.

---

## Estructura del proyecto

```
prueba_tecnica/
│
├── dashboard/
│   └── Dashboard_VEP.pbix
│
├── data/
│   ├── input/
│   │   ├── Curvas_CEC.xlsx
│   │   └── Flujos.xlsx
│   │
│   └── output/
│       └── resultados.xlsx
│
├── docs/
│   ├── caps31-anexo-15.docx
│   └── Prueba Analista.pdf
│
├── src/
│   ├── __init__.py
│   ├── escenario_base.py
│   ├── escenario_choque.py
│   ├── exportar_resultados.py
│   ├── lectura_datos.py
│   └── main.py
│
├── .gitignore
├── README.md
├── README.pdf
└── requirements.txt
```

### Responsabilidad de cada módulo

| Módulo | Responsabilidad |
|---|---|
| `main.py` | Orquesta el proceso completo y define la secuencia metodológica. |
| `lectura_datos.py` | Lee los archivos Excel, muestra información inicial y realiza conversiones de tipos. |
| `escenario_base.py` | Calcula la fecha relevante, el plazo, la banda/punto medio, la tasa CEC, el factor de descuento, el VP y el VEP base. |
| `escenario_choque.py` | Construye los seis escenarios de choque, calcula las tasas estresadas, los VP, los VEP y el impacto de cada escenario. |
| `exportar_resultados.py` | Genera el archivo Excel final con las hojas `Flujos` y `Resumen` y aplica formato básico. |

La separación permite mantener una correspondencia directa entre las etapas de la prueba y los módulos del código.

---

## Archivos de entrada

### `Flujos.xlsx`

Contiene los flujos futuros asociados al portafolio de inversiones. La hoja `Diccionario` suministrada en el archivo describe el significado de los campos.

La hoja utilizada por el programa es `Sheet`.

En el archivo suministrado se encuentran **22 flujos** y las principales variables utilizadas por el cálculo son:

- `tipo_indice`
- `moneda_pago_inicial`
- `importe_flujo_caja`
- `fecha_corte`
- `fecha_pago_flujo`
- `fecha_siguiente_reprecio`

### `Curvas_CEC.xlsx`

Contiene la estructura temporal de las tasas CEC utilizada para descontar los flujos. La hoja `Diccionario` describe la estructura de sus campos.

La hoja utilizada por el programa es `Sheet`.

Las variables utilizadas directamente son:

- `curve_name`
- `fecha_corte`
- `tenor`
- `zero_coupon_rate`

El archivo suministrado contiene curvas para COP, UVR y USD; los flujos suministrados para esta prueba están denominados en **COP**.

---

## Requisitos

Se requiere:

- Python 3.9 o superior.
- pip, para la instalación y gestión de las dependencias.
- Las siguientes librerías de Python:
  - `pandas`
  - `numpy`
  - `openpyxl`

Las dependencias se encuentran en `requirements.txt`.

---

## Configuración del entorno virtual

Se recomienda utilizar un entorno virtual para aislar las dependencias del proyecto.

### Linux

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows --- PowerShell

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea temporalmente la ejecución del script de activación, puede utilizarse una política de ejecución apropiada para el usuario o ejecutar el proyecto desde CMD.

### Windows --- CMD

```
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Desactivar el entorno

En cualquier sistema:

```bash
deactivate
```

---

## Ejecución

El proyecto debe ejecutarse desde la **raíz del proyecto**, es decir, desde la carpeta que contiene `src/` y `data/`.

### Linux / macOS

```bash
python3 -m src.main
```

### Windows (PowerShell o CMD)

```
python -m src.main
```

Se recomienda ejecutar `src.main` como módulo y no ejecutar `src/main.py` directamente, ya que el proyecto utiliza imports del paquete `src`.

Al finalizar, el archivo se genera en:

```
data/output/resultados.xlsx
```

---

## Flujo general de cálculo

```
Flujos.xlsx + Curvas_CEC.xlsx
        |
        v
Lectura de datos
        |
        v
Controles de calidad y tipificación
        |
        v
Determinar fecha relevante
        |
        v
Calcular plazo en años
        |
        v
Asignar banda y punto medio
        |
        v
Obtener tasa CEC
        |
        v
Interpolación si es necesaria
        |
        v
Factor de descuento base
        |
        v
VP base
        |
        v
VEP Base
        |
        v
Construir 6 escenarios de choque
        |
        v
Calcular tasas bajo cada escenario
        |
        v
Factor de descuento por escenario
        |
        v
VP por escenario
        |
        v
VEP por escenario
        |
        v
Delta VEP
        |
        v
Exportar resultados.xlsx
```

*Figura: Flujo general de cálculo del VEP*

---

## Paso 1 --- Lectura y control de datos

La función `leer_datos()` utiliza `pandas.read_excel()` para cargar las hojas requeridas.

Se manejan explícitamente:

- archivo inexistente.
- hoja inexistente.
- otros errores de lectura.
- archivos/hojas sin registros.

Adicionalmente, `mostrar_informacion()` presenta:

- primeros registros.
- número de filas.
- número de columnas.
- tipos de datos.

Esto permite detectar inconsistencias antes de iniciar el cálculo financiero.

### Conversión de tipos

`validar_tipos()` clasifica las variables de acuerdo con su naturaleza:

- numéricas.
- categóricas.
- fechas.

Las variables numéricas se convierten mediante `pd.to_numeric()` y las fechas mediante `pd.to_datetime()`. Cuando un valor no nulo no puede convertirse correctamente, el proceso genera un error.

Esta separación es deliberada: una cosa es comprobar que un dato puede interpretarse como el tipo requerido y otra determinar si una columna puede admitir valores nulos.

---

## Paso 2 --- Construcción del escenario base

El escenario base se construye en cuatro etapas:

1. Determinación del plazo.
2. Obtención de la tasa CEC.
3. Descuento del flujo.
4. Agregación para obtener el VEP.

### Determinación de la fecha relevante

El Anexo 15 establece que los flujos deben ubicarse según el vencimiento contractual cuando corresponda a instrumentos con cupones fijos, y según la próxima fecha de reprecio cuando los cupones son variables o flotantes.

Por esta razón, la implementación utiliza:

- **flujo fijo:** `fecha_pago_flujo`;
- **flujo flotante:** `fecha_siguiente_reprecio`.

La fecha de referencia se denomina `fecha_relevante`.

### Cálculo del plazo

Primero se calcula el número de días:

```
plazo_dias = fecha_relevante - fecha_corte
```

y posteriormente:

```
plazo_anios = plazo_dias / 365
```

La conversión a años utiliza 365 días para llevar los plazos de las fechas a la unidad utilizada por las curvas y las fórmulas de descuento.

### Asignación a bandas y puntos medios

El Anexo 15 establece 19 bandas de tiempo y sus respectivos puntos medios en la Tabla 4 del numeral 2.2.

La implementación asigna cada flujo a la banda correspondiente y utiliza el **punto medio de la banda** como `tiempo_vencimiento_anios`.

| Banda | Punto medio (años) |
|---|---|
| Overnight (< 1 día) | 0.0028 |
| > Overnight -- 1 mes | 0.0417 |
| > 1 -- 3 meses | 0.1667 |
| > 3 -- 6 meses | 0.375 |
| > 6 -- 9 meses | 0.625 |
| > 9 meses -- 1 año | 0.8075 |
| > 1 -- 1.5 años | 1.25 |
| > 1.5 -- 2 años | 1.75 |
| > 2 -- 3 años | 2.5 |
| > 3 -- 4 años | 3.5 |
| > 4 -- 5 años | 4.5 |
| > 5 -- 6 años | 5.5 |
| > 6 -- 7 años | 6.5 |
| > 7 -- 8 años | 7.5 |
| > 8 -- 9 años | 8.5 |
| > 9 -- 10 años | 9.5 |
| > 10 -- 15 años | 12.5 |
| > 15 -- 20 años | 17.5 |
| > 20 años | 25 |

### Obtención de la tasa CEC

Para cada flujo se selecciona la curva correspondiente a la moneda y fecha de corte.

| Moneda | Curva |
|---|---|
| COP | `COP COP CEC` |
| UVR | `UVR COP CEC` |
| USD | `USD USD: BONOS TREASURIES` |

El tenor de la curva se transforma de formatos como `31D` a días numéricos.

#### Coincidencia exacta

Si el plazo del flujo coincide exactamente con un nodo de la curva, se utiliza directamente `zero_coupon_rate`.

#### Interpolación

Cuando el plazo del flujo no coincide con un nodo de la curva, se permite utilizar interpolación lineal o exponencial. La implementación incorpora ambos métodos.

**Interpolación lineal**

Se calcula mediante:

$$R(t) = R_1 + \frac{t - t_1}{t_2 - t_1}\,(R_2 - R_1)$$

donde:

- $R(t)$ = tasa CEC correspondiente al plazo del flujo.
- $t$ = plazo objetivo.
- $t_1$, $t_2$ = nodos anterior y siguiente.
- $R_1$, $R_2$ = tasas CEC correspondientes a dichos nodos.

**Interpolación exponencial**

En la interpolación exponencial se interpolan primero los factores de descuento de los nodos anterior y siguiente. Para ello, se calcula:

$$FD_1 = e^{-R_1 t_1} \qquad FD_2 = e^{-R_2 t_2}$$

donde:

- $FD_1$ = factor de descuento del nodo anterior.
- $FD_2$ = factor de descuento del nodo siguiente.
- $R_1$, $R_2$ = tasas CEC de los nodos anterior y siguiente.
- $t_1$, $t_2$ = plazos de los nodos anterior y siguiente, expresados en años.

Luego se calcula la proporción del plazo objetivo entre ambos nodos:

$$p = \frac{t - t_1}{t_2 - t_1}$$

donde $t$ es el plazo objetivo, expresado en años.

Con esta proporción se interpola el factor de descuento:

$$FD(t) = FD_1 \left(\frac{FD_2}{FD_1}\right)^{p}$$

Finalmente, el factor de descuento interpolado se convierte nuevamente en una tasa:

$$R(t) = \frac{-\ln(FD(t))}{t}$$

donde $R(t)$ es la tasa CEC interpolada correspondiente al plazo objetivo.

Este procedimiento permite realizar la interpolación mediante factores de descuento y trabajar tanto con tasas positivas como negativas. Para los datos de la prueba y pruebas realizadas con diferentes datos, los resultados obtenidos mediante interpolación lineal y exponencial son muy similares.

---

## Valor presente del escenario base

De acuerdo con la metodología establecida en el Anexo 15, el valor presente de cada flujo se obtiene aplicando un factor de descuento con composición continua:

$$FD(t) = e^{-R(t)\,t}$$

donde:

- $FD(t)$ = factor de descuento correspondiente al flujo.
- $R(t)$ = tasa de descuento correspondiente al plazo del flujo.
- $t$ = plazo del flujo en años.

### Implementación

Para cada flujo, el código utiliza la tasa CEC obtenida previamente y el **punto medio de la banda temporal asignada** como plazo de descuento.

El factor de descuento se calcula como:

$$FD = e^{-\,\text{tasa\_cec} \times \text{tiempo\_vencimiento\_anios}}$$

Posteriormente, el valor presente del flujo se obtiene multiplicando su importe por el factor de descuento:

$$VP = \text{importe\_flujo\_caja} \times FD$$

De esta manera, el valor presente de cada flujo se calcula de forma consistente con la metodología de descuento continuo indicada en el Anexo 15.

---

## Paso 3 --- VEP Base

El VEP base se obtiene como la suma de los valores presentes:

$$VEP_{\text{Base}} = \sum_{k} VP_k$$

Esto corresponde al requerimiento de la prueba de calcular el valor económico del portafolio como la suma de los valores presentes de los flujos proyectados.

---

## Paso 4 --- Construcción de escenarios de choque

A partir de la curva CEC del escenario base se construyen los seis escenarios de choque definidos en la prueba:

1. Paralelo Arriba.
2. Paralelo Abajo.
3. Empinamiento.
4. Aplanamiento.
5. Corto Arriba.
6. Corto Abajo.

Los choques se aplican sobre la tasa CEC base de cada flujo, teniendo en cuenta su moneda y su plazo de vencimiento.

### Tamaño de los choques

De acuerdo con la Tabla 1 del literal 1.3 del Anexo 15, se definen tres parámetros para cada moneda:

- $S_{0,c}$ = tamaño del choque paralelo.
- $S_{1,c}$ = tamaño del choque de corto plazo.
- $S_{2,c}$ = tamaño del choque de largo plazo.
- $c$ = moneda del flujo.

| Moneda | $S_{0,c}$ --- Paralelo | $S_{1,c}$ --- Corto | $S_{2,c}$ --- Largo |
|---|---|---|---|
| COP | 400 pb | 500 pb | 300 pb |
| UVR | 200 pb | 300 pb | 100 pb |
| USD | 200 pb | 300 pb | 150 pb |

Los valores se convierten de puntos básicos a unidades decimales dividiendo entre `10.000` antes de aplicarlos a las tasas.

### Choques paralelos

El choque paralelo desplaza toda la curva en una magnitud constante dependiente de la moneda.

**Paralelo Arriba**

$$\Delta R_{PA,c}(t_k) = +S_{0,c}$$

**Paralelo Abajo**

$$\Delta R_{PB,c}(t_k) = -S_{0,c}$$

Por lo tanto, el choque tiene la misma magnitud para todos los plazos de una misma moneda.

### Choques de corto plazo

El Anexo 15 define el choque de corto plazo como un desplazamiento cuyo efecto es mayor en los vencimientos cortos y disminuye a medida que aumenta el plazo. Para ello se utiliza una función escalar que depende del vencimiento.

En la implementación se utiliza:

$$S_{\text{corto}}(t_k) = e^{-t_k / x}$$

donde:

- $t_k$ = plazo del flujo en años.
- $x$ = parámetro que controla la velocidad con la que disminuye el efecto del choque a medida que aumenta el plazo.

El parámetro `x` se implementa como una variable configurable de la función, con un valor predeterminado de `4`. Este valor corresponde al utilizado como referencia en el ejemplo presentado en el Anexo 15.

El choque de corto plazo para la moneda $c$ se obtiene multiplicando este factor por el tamaño del choque de corto plazo correspondiente a dicha moneda:

$$\Delta R_{\text{corto},c}(t_k) = S_{1,c} \times S_{\text{corto}}(t_k)$$

donde:

- $c$ = moneda del flujo.
- $S_{1,c}$ = tamaño del choque de corto plazo para la moneda $c$.
- $\Delta R_{\text{corto},c}(t_k)$ = desplazamiento de la tasa en el plazo $t_k$.

El valor de $S_{\text{corto}}(t_k)$ disminuye a medida que aumenta $t_k$, por lo que el choque se concentra principalmente en los vencimientos cortos.

A partir de este choque se construyen los dos escenarios:

**Corto Arriba**

$$\Delta R_{CA,c}(t_k) = +\Delta R_{\text{corto},c}(t_k)$$

**Corto Abajo**

$$\Delta R_{CB,c}(t_k) = -\Delta R_{\text{corto},c}(t_k)$$

### Choques de largo plazo

El componente de largo plazo se obtiene como complemento del componente de corto plazo:

$$S_{\text{largo}}(t_k) = 1 - S_{\text{corto}}(t_k)$$

El choque de largo plazo para la moneda $c$ es:

$$\Delta R_{\text{largo},c}(t_k) = S_{2,c}\, S_{\text{largo}}(t_k)$$

A diferencia del componente de corto plazo, este factor aumenta con el plazo.

Estos componentes se utilizan para construir los escenarios de **Empinamiento** y **Aplanamiento**.

### Empinamiento

El escenario de empinamiento combina los componentes de corto y largo plazo mediante:

$$\Delta R_{\text{Emp},c}(t_k) = -0.65\,\lvert \Delta R_{\text{corto},c}(t_k) \rvert + 0.9\,\lvert \Delta R_{\text{largo},c}(t_k) \rvert$$

El resultado genera un desplazamiento que reduce el componente de corto plazo y aumenta el componente de largo plazo, modificando la pendiente de la curva.

### Aplanamiento

El escenario de aplanamiento se construye como:

$$\Delta R_{\text{Apl},c}(t_k) = 0.8\,\lvert \Delta R_{\text{corto},c}(t_k) \rvert - 0.6\,\lvert \Delta R_{\text{largo},c}(t_k) \rvert$$

De esta manera, el choque modifica los extremos de la curva en sentidos opuestos al escenario de empinamiento.

---

## Tasas bajo cada escenario

Una vez determinado el choque correspondiente a cada escenario, la tasa estresada se obtiene sumando el desplazamiento a la tasa CEC del escenario base:

$$R_i(t_k) = R_0(t_k) + \Delta R_i(t_k)$$

donde:

- $R_0(t_k)$ = tasa CEC del escenario base.
- $\Delta R_i(t_k)$ = choque aplicado bajo el escenario $i$.
- $R_i(t_k)$ = tasa CEC resultante bajo el escenario $i$.

Este cálculo se realiza para cada flujo y para cada uno de los seis escenarios.

---

## Valor presente bajo los escenarios de choque

Una vez obtenida la tasa estresada, se recalcula el factor de descuento para cada flujo:

$$FD_i(t_k) = e^{-R_i(t_k)\,t_k}$$

donde $t_k$ corresponde al punto medio de la banda temporal asignada al flujo.

Posteriormente, el valor presente bajo el escenario $i$ se calcula como:

$$VP_{i,k} = FC_k \times FD_i(t_k)$$

donde:

- $FC_k$ = importe del flujo de caja.
- $FD_i(t_k)$ = factor de descuento bajo el escenario $i$.
- $VP_{i,k}$ = valor presente del flujo $k$ bajo el escenario $i$.

De esta forma, cada escenario vuelve a calcular el factor de descuento y el valor presente a partir de la tasa estresada. No se reutiliza el factor de descuento calculado para el escenario base.

---

## VEP bajo cada escenario

El VEP de cada escenario se obtiene sumando los valores presentes de todos los flujos:

$$VEP_i = \sum_{k} VP_{i,k}$$

donde $VEP_i$ representa el Valor Económico del Patrimonio bajo el escenario de choque $i$.

El cálculo se realiza de forma independiente para cada uno de los seis escenarios:

- `VEP Paralelo Arriba`
- `VEP Paralelo Abajo`
- `VEP Empinamiento`
- `VEP Aplanamiento`
- `VEP Corto Arriba`
- `VEP Corto Abajo`

Los cálculos intermedios se conservan en la hoja `Flujos`, permitiendo trazar el resultado desde el flujo individual hasta el VEP de cada escenario.

---

## Impacto sobre el VEP

Finalmente, el impacto de cada escenario se calcula respecto al escenario base mediante:

$$\Delta VEP_i = VEP_{\text{Base}} - VEP_i$$

La variación porcentual se obtiene como:

$$\Delta VEP_i\% = \frac{\Delta VEP_i}{VEP_{\text{Base}}}$$

Estos resultados se consolidan en la hoja `Resumen`, junto con el VEP base y los VEP correspondientes a cada escenario.

---

## Paso 5 --- Cálculo del impacto

La prueba define el impacto de cada escenario como la diferencia entre el VEP del escenario base y el VEP obtenido bajo el escenario de choque:

$$\Delta VEP_i = VEP_{\text{Base}} - VEP_i$$

Por tanto:

- $\Delta VEP > 0$: el escenario reduce el VEP respecto al escenario base.
- $\Delta VEP < 0$: el VEP bajo el escenario es superior al VEP base.
- $\Delta VEP = 0$: el VEP no presenta variación respecto al escenario base.

La variación porcentual permite expresar este impacto en términos relativos al VEP del escenario base:

$$\Delta VEP\% = \frac{\Delta VEP_i}{VEP_{\text{Base}}} \times 100$$

Equivalentemente:

$$\Delta VEP\% = \frac{VEP_{\text{Base}} - VEP_i}{VEP_{\text{Base}}} \times 100$$

Esta medida permite comparar la magnitud del impacto de los diferentes escenarios independientemente del valor absoluto del VEP.

---

## Controles de calidad y manejo de errores

La solución incorpora controles en distintas etapas.

### Lectura

- archivo inexistente.
- hoja inexistente.
- errores generales de lectura.
- archivos vacíos.

### Tipos

- conversión de columnas numéricas.
- conversión de fechas.
- detección de valores no convertibles.

### Escenario base

- columnas requeridas.
- valores nulos en variables críticas.
- fechas relevantes según el tipo de índice.
- plazos positivos.
- asignación de banda.
- existencia de curva.
- existencia de nodos para interpolación.
- método de interpolación permitido.

### Escenarios de choque

- columnas requeridas.
- valores nulos.
- $x > 0$.
- monedas con parámetros definidos.

El objetivo es evitar que una inconsistencia de datos produzca resultados financieros aparentemente válidos pero incorrectos.

---

## Resultados de salida

El programa genera:

```
data/output/resultados.xlsx
```

### `Flujos`

Incluye las variables originales y las calculadas durante el proceso:

```
estrategia
posicion
codigo_posicion
frecuencia_pago_principal_pata_1
indice_principal_mostrado_pata_1
tipo_tasa
tipo_indice
moneda_pago_inicial
rn_operacion
saldo
tipo_importe_flujo_caja
importe_flujo_caja
fecha_corte
fecha_pago_flujo
fecha_siguiente_reprecio
tiempo_vencimiento_anios
tasa_cec
vp_base
choque_paralelo_arriba
choque_paralelo_abajo
choque_corto_arriba
choque_corto_abajo
choque_empinamiento
choque_aplanamiento
s_corto
s_largo
tasa_paralelo_arriba
tasa_paralelo_abajo
tasa_corto_arriba
tasa_corto_abajo
tasa_empinamiento
tasa_aplanamiento
vp_paralelo_arriba
vp_paralelo_abajo
vp_empinamiento
vp_aplanamiento
vp_corto_arriba
vp_corto_abajo
```

### `Resumen`

Contiene:

| Columna | Descripción |
|---|---|
| `Escenario` | Base o escenario de choque |
| `VEP` | VEP calculado bajo el escenario |
| `Delta VEP` | Diferencia respecto al escenario base |
| `Delta VEP %` | Variación porcentual respecto al VEP base |

Se incluye explícitamente el **caso base**, con `Delta VEP = 0`.

---

## Decisiones de diseño

### Separación por etapas

Se mantiene la secuencia de la guía:

```
Lectura
-> Escenario base
-> VEP base
-> Escenarios de choque
-> Impacto
-> Exportacion
```

Esto facilita la trazabilidad y la revisión matemática.

### Responsabilidad por función

Las funciones se dividen por operación: plazo, tasa, VP, VEP, escenarios e impacto. Esto evita concentrar toda la lógica en una única función.

### Transformaciones por etapa

Las funciones mantienen las transformaciones separadas y utilizan copias de los datos cuando necesitan trabajar sobre una versión intermedia. Esto facilita la trazabilidad y evita concentrar toda la lógica en una única función.

### Cálculo por flujo

Los escenarios se calculan a nivel de flujo porque el choque depende del punto medio de vencimiento de cada flujo.
