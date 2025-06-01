"""
__init__.py

Punto de entrada para registrar estadísticas de una simulación de SistemaP
y luego visualizarla. Usa los módulos:
  - SistemaP: simulación y registro de estadísticas.
  - funciones: constructores de sistemas concretos.
  - visualizadorAvanzado: visualización interactiva de la simulación.
  - Lector: (opcional) para leer sistemas desde fichero.
"""

from SistemaP import registrar_estadisticas
from visualizadorAvanzado import simular_y_visualizar
import funciones
# import Lector  # Descomentar si se quiere leer desde fichero .pli

def main():
    # 1) Construir (o leer) el sistema P a simular.
    # Ejemplo usando división: 10 'a' dividido por 3.
    sistema = funciones.division(10, 3)

    # Si se prefiere leer desde un fichero .pli, descomentar:
    # sistema = Lector.leerSistema("tests/Test1.pli")

    # 2) Registrar estadísticas de la simulación (por ejemplo, 30 lapsos)
    lapsos = 30
    # El método devuelve un DataFrame; además, guardará el CSV en ./Estadisticas/
    df_estadisticas = registrar_estadisticas(
        sistema,
        lapsos=lapsos,
        modo="max_paralelo",
        rng_seed=None,                            # Sin semilla fija (aleatorio en desempates)
        csv_path="MemBrainPy/Estadisticas/estadisticas.csv"  # Cambiado para guardar dentro de la carpeta Estadisticas
    )
    print(f"Estadísticas guardadas en 'Estadisticas/estadisticas.csv' (columnas: {list(df_estadisticas.columns)})")

    # 3) Visualizar la simulación de forma interactiva
    simular_y_visualizar(sistema, pasos=lapsos, modo="max_paralelo")


if __name__ == "__main__":
    main()
