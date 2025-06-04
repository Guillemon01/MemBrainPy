# Libreria_membranas

Libreria_membranas es un pequeño proyecto educativo que implementa un simulador
para **Sistemas P**, un modelo de computación inspirado en el funcionamiento de
las membranas celulares. El código está escrito en Python e incluye varios
módulos que permiten crear sistemas de membranas de manera programática, leer
archivos en formato P‑Lingua y ejecutar simulaciones paso a paso.

## Características principales

- **Simulación en modo máximo paralelo** mediante el módulo `SistemaP`, que se
  encarga de aplicar reglas, crear y disolver membranas y registrar el estado
de cada lapso de tiempo.
- **Lectura de sistemas** a partir de ficheros `.pli` con el módulo `Lector`.
- **Colección de funciones básicas** (`funciones.py`) para operaciones como
  división, suma, resta o paridad, construidas con reglas de membranas.
- **Operaciones compuestas** (`operaciones_avanzadas.py`) que reutilizan las
  funciones básicas para multiplicar o calcular potencias.
- **Visualización** interactiva de las simulaciones (en `visualizadorAvanzado`).
- **Pruebas automatizadas** en `tests/` para asegurar el correcto
  funcionamiento de las operaciones avanzadas.

## Instalación

El proyecto puede instalarse a partir del repositorio clonándolo de GitHub y
asegurándose de tener las dependencias necesarias. Únicamente se requiere
`pandas` para registrar estadísticas:

```bash
pip install pandas
```

A continuación se puede ejecutar `pytest` para lanzar las pruebas incluidas:

```bash
python -m pytest -q
```

## Uso básico

El punto de entrada se encuentra en `MemBrainPy/__init__.py`. Al ejecutar ese
script se crea un sistema de ejemplo (por defecto, una división) y se simula
durante varios lapsos registrando estadísticas en `./MemBrainPy/Estadisticas`.
Para probar otros sistemas basta con modificar las variables definidas en
`main()`.

También pueden construirse sistemas manualmente utilizando las funciones de
`funciones.py` o leyendo archivos `.pli` mediante `Lector.leer_sistema`.
Una vez obtenido un objeto `SistemaP`, la función `simular_lapso` permite
avanzar la simulación.

```python
from SistemaP import simular_lapso
import funciones

sistema = funciones.suma(2, 3)
for _ in range(5):
    simular_lapso(sistema, modo="max_paralelo")
print(sistema.skin["m_out"].resources)
```

## Organización del repositorio

```
MemBrainPy/
├── MemBrainPy/              # Código fuente de la librería
│   ├── SistemaP.py          # Núcleo del simulador de Sistemas P
│   ├── Lector.py            # Parser de archivos P-Lingua (.pli)
│   ├── funciones.py         # Funciones básicas de aritmética con membranas
│   ├── operaciones_avanzadas.py  # Operaciones compuestas (multiplicar, potencia)
│   └── visualizadorAvanzado.py   # Herramientas de visualización
├── tests/                   # Conjunto de pruebas con pytest
└── setup.py                 # Metadatos y configuración de instalación
```

El archivo `Estadisticas/estadisticas.csv` se genera automáticamente cuando se
registran simulaciones; no es necesario modificarlo manualmente.

## Estado del proyecto

Este repositorio se creó con fines académicos y de experimentación, por lo que
puede ampliarse o modificarse según las necesidades. Las contribuciones y
sugerencias son bienvenidas.
