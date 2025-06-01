"""
__init__.py

Punto de entrada para simular Sistemas P sin usar línea de comandos:
los parámetros están hardcodeados para elegir entre lector (.pli) o función división,
y decidir si se registran estadísticas o no.
"""

from SistemaP import registrar_estadisticas
from visualizadorAvanzado import simular_y_visualizar
import funciones
from Lector import leer_sistema

def main():
    # ---------------- Parámetros hardcodeados ----------------
    # Elegir "lector" para leer un .pli, o "division" para usar la función de ejemplo:
    modo_sistema = "division"     # Cambiar a "division" para usar funciones.division

    # Si modo_sistema == "lector", indicar la ruta al .pli:
    ruta_pli = "tests/Test2.pli"

    # Número de lapsos a simular:
    lapsos = 30

    # Si registrar_estadisticas = True, guardará CSV en Estadisticas/estadisticas.csv:
    registrar = True
    # ---------------------------------------------------------

    # 1) Construir el sistema según el modo seleccionado
    if modo_sistema == "lector":
        sistema = leer_sistema(ruta_pli)
    else:  # modo_sistema == "division"
        sistema = funciones.division(10, 3)

    # 2) Si se pidió registrar estadísticas, ejecutarlo y guardar en ./Estadisticas/
    if registrar:
        csv_path = "MemBrainPy/Estadisticas/estadisticas.csv"
        df_estadisticas = registrar_estadisticas(
            sistema,
            lapsos=lapsos,
            modo="max_paralelo",
            rng_seed=None,
            csv_path=csv_path
        )
        print(f"Estadísticas guardadas en '{csv_path}' (columnas: {list(df_estadisticas.columns)})")

    # 3) Visualizar la simulación de forma interactiva
    simular_y_visualizar(sistema, pasos=lapsos, modo="max_paralelo")


if __name__ == "__main__":
    main()
