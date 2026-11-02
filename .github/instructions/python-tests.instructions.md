---
applyTo: "tests/**/*.py,**/tests/**/*.py,**/test_*.py,**/*_test.py"
---

# Instrucciones para pruebas de Python con pytest

## Principios generales
- Usa `pytest` como framework de pruebas y sigue la estructura y configuración que ya tenga el repositorio.
- Comprueba comportamientos y contratos observables, no detalles internos de implementación que puedan cambiar sin alterar el resultado.
- Organiza cada prueba con el patrón Arrange–Act–Assert (preparar, ejecutar, comprobar) y verifica un comportamiento principal por prueba.
- Utiliza nombres descriptivos, por ejemplo `test_calculate_total_returns_zero_for_empty_input`.
- Mantén las pruebas deterministas, independientes entre sí y ejecutables en cualquier orden. No dependas de servicios externos, red, rutas locales del desarrollador ni del estado residual de otras pruebas.

## pytest
- Usa `pytest.mark.parametrize` para probar de manera concisa múltiples entradas, límites y resultados esperados.
- Utiliza fixtures para preparar datos compartidos o recursos y limita su alcance al mínimo necesario.
- Usa `tmp_path` para archivos temporales; `monkeypatch` o `unittest.mock` para aislar efectos externos; `caplog` para comprobar logs cuando formen parte del comportamiento esperado.
- Comprueba excepciones mediante `pytest.raises`, incluyendo el tipo correcto y el mensaje solo cuando el mensaje sea parte relevante del contrato.
- No simules indiscriminadamente las funciones bajo prueba ni las operaciones internas de pandas o NumPy. Simula dependencias externas en sus límites.

## Pruebas de pandas
- Para comparar DataFrames o Series completos, prefiere `pandas.testing.assert_frame_equal` y `pandas.testing.assert_series_equal`; comprueba explícitamente índice, orden, nombres y tipos cuando sean relevantes.
- Incluye casos para DataFrames vacíos, columnas ausentes, valores nulos, duplicados, tipos mixtos, índices no consecutivos y claves de unión repetidas cuando sean aplicables.
- Verifica la cardinalidad de joins/merges, el número de filas, el orden esperado y el tratamiento de registros rechazados o descartados.
- No conviertas los resultados a listas o diccionarios para compararlos si eso oculta diferencias importantes de índice o dtype.

## Pruebas de NumPy y cálculos numéricos
- Comprueba forma (`shape`), dimensiones, dtype y valores de los arrays cuando formen parte del contrato.
- Usa `numpy.testing.assert_array_equal` para igualdad exacta y `numpy.testing.assert_allclose` o `pytest.approx` para resultados numéricos con tolerancias justificadas.
- Prueba, cuando sea pertinente, arrays vacíos, dimensiones inesperadas, `NaN`, infinitos, valores extremos y divisiones por cero.
- Si el código usa aleatoriedad, fija una semilla o inyecta un generador para que la prueba sea reproducible. No dependas de que una muestra aleatoria produzca casualmente un resultado concreto.

## Cobertura de escenarios
- Cubre el caso nominal, los límites, entradas inválidas y los errores que el contrato indique que deben producirse.
- Comprueba explícitamente que las funciones no modifican entradas cuando el contrato exige conservarlas.
- Para transformaciones de datos, valida tanto el resultado como invariantes importantes (por ejemplo, columnas requeridas, unicidad de claves o conservación del número de registros).
- Evita pruebas duplicadas que repitan la misma garantía sin aportar cobertura adicional. No persigas un porcentaje de cobertura arbitrario a costa de pruebas poco útiles.

## Ejecución y entrega
- Ejecuta las pruebas relevantes con `pytest -q` o con el comando estándar del proyecto. Ejecuta la suite completa cuando el alcance del cambio lo permita.
- No alteres la configuración global, los datos reales ni el entorno compartido para hacer pasar una prueba.
- Si una prueba falla, identifica si el problema está en el código, en la expectativa o en los datos de prueba; no debilites la aserción sin una justificación basada en el requisito.
- Resume qué escenarios se han probado, el comando ejecutado y cualquier prueba que no haya podido ejecutarse.

## Ejemplos: pruebas recomendadas y pruebas que evitar

### Casos múltiples: usar parametrización

**Preferido:**

```python
import pytest


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (" Ana ", "ana"),
        ("BOB", "bob"),
        ("", ""),
    ],
)
def test_normalize_name(value, expected):
    assert normalize_name(value) == expected
```

**Evitar:** copiar y pegar muchas pruebas casi idénticas si `pytest.mark.parametrize` expresa mejor los casos. Mantén pruebas separadas cuando sus preparaciones, causas de fallo o contratos sean materialmente distintos.

### DataFrames: comparar el resultado completo

**Preferido:**

```python
import pandas as pd
from pandas.testing import assert_frame_equal


def test_add_total_column():
    source = pd.DataFrame({"quantity": [2, 3], "unit_price": [5.0, 4.0]})

    actual = add_total_column(source)
    expected = pd.DataFrame(
        {
            "quantity": [2, 3],
            "unit_price": [5.0, 4.0],
            "total": [10.0, 12.0],
        }
    )

    assert_frame_equal(actual, expected)
```

**Evitar:** convertir ambos DataFrames a listas o diccionarios si al hacerlo se pierden diferencias importantes de índice, orden o tipos.

```python
# Evitar cuando se necesita verificar también índice y dtype:
# assert actual.to_dict("records") == expected.to_dict("records")
```

### Excepciones: comprobar el contrato esperado

**Preferido:**

```python
import pandas as pd
import pytest


def test_missing_required_column_raises_value_error():
    frame = pd.DataFrame({"quantity": [1]})

    with pytest.raises(ValueError, match="unit_price"):
        calculate_line_total(frame)
```

**Evitar:** capturar cualquier excepción y dar la prueba por superada. La prueba debe fallar si no se produce la excepción esperada o si se produce otra por un defecto distinto.

### Ficheros temporales: usar `tmp_path`

**Preferido:**

```python
import pandas as pd


def test_read_input_csv(tmp_path):
    source = tmp_path / "input.csv"
    source.write_text("id,value\n1,10\n", encoding="utf-8")

    actual = read_input(source)

    assert actual.to_dict("records") == [{"id": 1, "value": 10}]
```

Para comprobar un DataFrame completo, prefiere `pandas.testing.assert_frame_equal`; aquí la comparación en forma de registros solo se muestra como ejemplo sencillo de lectura.

**Evitar:** depender de una ruta absoluta del ordenador del desarrollador, leer datos sensibles reales o escribir en carpetas compartidas durante una prueba unitaria.

### NumPy: usar tolerancias justificadas

**Preferido:**

```python
import numpy as np


def test_calculate_ratios():
    actual = calculate_ratios(np.array([1.0, 2.0]), denominator=3.0)
    expected = np.array([1 / 3, 2 / 3])

    np.testing.assert_allclose(actual, expected, rtol=1e-7, atol=1e-9)
```

**Evitar:** usar igualdad exacta para resultados de coma flotante cuando pequeñas diferencias de redondeo son admisibles. No elijas tolerancias arbitrariamente grandes para hacer pasar la prueba: justifícalas según el requisito.

### Aislamiento: simular dependencias externas, no la función probada

**Preferido:** sustituir una llamada a un servicio externo, un cliente de base de datos o una API en el límite del sistema usando `monkeypatch` o `unittest.mock`.

**Evitar:** simular la propia función que se quiere verificar o reemplazar las operaciones de pandas/NumPy que constituyen el comportamiento bajo prueba; eso puede hacer que la prueba solo compruebe el mock.

### Determinismo: no depender de red ni de aleatoriedad accidental

**Preferido:** preparar los datos localmente y proporcionar una semilla o un generador controlado a las funciones que usan aleatoriedad.

**Evitar:** pruebas que necesiten Internet, un servicio de desarrollo activo, el orden de ejecución de otras pruebas o que una muestra aleatoria produzca casualmente un resultado concreto.

### No debilitar la prueba para ocultar un defecto

**Preferido:** investigar si el fallo está en el código, en el dato de prueba o en la expectativa y ajustar la prueba solo cuando contradiga el requisito real.

**Evitar:** eliminar aserciones, ampliar tolerancias sin justificación, convertir fallos en `xfail` de forma indiscriminada o modificar el comportamiento esperado únicamente para que la suite pase.
