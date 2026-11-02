---
applyTo: "**/*.py"
---

# Instrucciones para desarrollo en Python

## Antes de modificar código
- Inspecciona la estructura del repositorio, los módulos relacionados y la configuración existente (`pyproject.toml`, `requirements*.txt`, `setup.cfg`, `tox.ini` o equivalente).
- Sigue la versión de Python, las dependencias, las convenciones y las herramientas ya adoptadas por el proyecto. No añadas dependencias ni introduzcas una nueva arquitectura sin justificarlo.
- Comprueba los contratos y requisitos existentes antes de cambiar el comportamiento público.

## Diseño y calidad
- Escribe código claro, modular y mantenible, con funciones de responsabilidad única y entradas y salidas explícitas.
- Usa nombres descriptivos y sigue PEP 8. Añade anotaciones de tipo a las funciones y métodos públicos y docstrings cuando aclaren propósito, parámetros, retorno o excepciones.
- Prefiere transformaciones deterministas y funciones sin efectos secundarios cuando resulte práctico. Separa el cálculo de la lectura/escritura de archivos, la red, la base de datos y otros efectos externos.
- Valida las entradas en los límites apropiados. Maneja explícitamente valores ausentes, datos vacíos, tipos inesperados y errores de dominio. No ocultes excepciones con `except Exception` ni devuelvas valores ficticios para disimular errores.
- No uses `print` para diagnóstico en código de aplicación; utiliza el sistema de logging del proyecto cuando corresponda.
- No uses `assert` como mecanismo de validación de entradas en tiempo de ejecución.
- Evita abstracciones, clases, capas o configuraciones innecesarias. No refactorices código ajeno a la tarea sin motivo.

## Uso de pandas
- Prefiere operaciones vectorizadas de `Series` y `DataFrame` frente a bucles por fila (`iterrows` o `apply` fila a fila) cuando exista una alternativa clara y correcta. No sacrifiques legibilidad por una optimización prematura.
- Define explícitamente el tratamiento de `NaN`, `None`, `NaT`, duplicados, índices, orden de filas, zonas horarias y tipos de columna cuando afecten al resultado.
- Evita la asignación encadenada. Selecciona y modifica datos de forma explícita; crea copias solo cuando sean necesarias para evitar aliasing o modificaciones no deseadas.
- En `merge`/`join`, verifica las claves y la cardinalidad esperada. Usa `validate=` cuando sea posible y evita multiplicar filas accidentalmente por claves duplicadas.
- No conviertas valores inválidos en ausentes ni descartes filas silenciosamente. Si empleas opciones como `errors="coerce"`, asegúrate de que el requisito lo permite y documenta o controla los valores resultantes.
- No asumas que un `DataFrame` tiene datos: contempla entradas vacías y comprueba columnas requeridas antes de operar.

## Uso de NumPy
- Explicita las dimensiones, formas (`shape`) y tipos (`dtype`) que espera cada operación cuando sean relevantes.
- Prefiere operaciones vectorizadas y broadcasting claro a bucles Python, siempre que mantenga la semántica correcta.
- Trata de forma deliberada los `NaN`, infinitos, divisiones por cero, arrays vacíos y conversiones de tipo.
- Para comparaciones de resultados en coma flotante, utiliza tolerancias apropiadas en vez de igualdad exacta, salvo cuando la igualdad exacta sea parte del contrato.
- Para aleatoriedad reproducible, utiliza `numpy.random.default_rng(seed)` con una semilla explícita cuando proceda; evita depender del generador global.

## Validación de cambios
- Añade o actualiza pruebas para el comportamiento modificado y para los casos límite relevantes.
- Ejecuta las pruebas y las comprobaciones ya configuradas en el proyecto. No afirmes que una validación ha pasado si no la has ejecutado.
- Al terminar, resume los archivos modificados, las decisiones relevantes, los comandos ejecutados y cualquier limitación o prueba pendiente.

## Ejemplos: prácticas recomendadas y prácticas que evitar

### pandas: preferir operaciones vectorizadas y validar los datos

**Preferido:** operación vectorizada, con el tratamiento de nulos definido.

```python
import pandas as pd


def calculate_line_total(items: pd.DataFrame) -> pd.Series:
    required = {"quantity", "unit_price"}
    missing = required.difference(items.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {sorted(missing)}")

    return items["quantity"] * items["unit_price"]
```

**Evitar:** recorrer cada fila sin necesidad, asumir que las columnas existen y ocultar los problemas con un valor inventado.

```python
# Evitar este patrón salvo que exista una razón concreta para hacerlo.
# totals = []
# for _, row in items.iterrows():
#     totals.append(row["quantity"] * row["unit_price"])
```

La vectorización no justifica cambiar la semántica: si los nulos, los tipos o el orden afectan al resultado, deben especificarse expresamente.

### pandas: validar la cardinalidad de un merge

**Preferido:** comprobar que la relación entre claves es la esperada.

```python
result = orders.merge(
    customers,
    on="customer_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)
```

**Evitar:** hacer un `merge` sin comprobar claves duplicadas cuando se espera una única fila de cliente por pedido. Una duplicación inesperada puede multiplicar silenciosamente las filas.

### NumPy: comparar resultados numéricos con tolerancia

**Preferido:**

```python
import numpy as np

actual = np.array([0.1 + 0.2])
expected = np.array([0.3])
np.testing.assert_allclose(actual, expected, rtol=1e-7, atol=1e-9)
```

**Evitar:** comparar con igualdad exacta los resultados de operaciones en coma flotante cuando el contrato no exige igualdad exacta.

```python
# Evitar para resultados de coma flotante sujetos a redondeo:
# assert actual == expected
```

### Errores: no ocultar fallos

**Preferido:** capturar únicamente el error que se sabe tratar y añadir contexto útil.

```python
from pathlib import Path
import pandas as pd


def read_input(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"No existe el fichero de entrada: {path}") from exc
```

**Evitar:**

```python
# Evitar: oculta la causa del fallo y devuelve un resultado aparentemente válido.
# try:
#     data = pd.read_csv(path)
# except Exception:
#     data = pd.DataFrame()
```

No sustituyas datos erróneos por ceros, DataFrames vacíos u otros valores por defecto a menos que ese comportamiento esté definido explícitamente en los requisitos.

### Efectos secundarios: separar cálculo e I/O

**Preferido:** mantener la transformación como función y delegar la lectura/escritura a otra capa.

```python
import pandas as pd


def normalize_names(names: pd.Series) -> pd.Series:
    return names.astype("string").str.strip().str.casefold()
```

**Evitar:** que una función de transformación lea ficheros, modifique variables globales, imprima mensajes y escriba resultados como efectos secundarios implícitos.

### Validación: no usar `assert` para validar entradas

**Preferido:**

```python
import numpy as np


def mean_value(values: np.ndarray) -> float:
    if values.size == 0:
        raise ValueError("values no puede estar vacío")
    return float(np.mean(values))
```

**Evitar:** usar `assert values.size > 0` como validación de entradas de producción: las aserciones pueden desactivarse y no son un mecanismo apropiado para validar contratos.
