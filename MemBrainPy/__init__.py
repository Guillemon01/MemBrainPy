"""
Punto de entrada para simular Sistemas P sin usar línea de comandos:
Los parámetros ahora son opcionales y configurables al llamar a main().
"""

import os
import copy
from SistemaP import registrar_estadisticas
from visualizadorAvanzado import simular_y_visualizar
import tests_sistemas
import funciones
import operaciones_avanzadas


def main(
    registrar: bool = True,
    visualizar: bool = True,
    tipo_sistema: str = "division",
    rng_seed: int = None
):  
    """
    registrar: indica si se deben registrar estadísticas.
    visualizar: indica si se debe realizar la visualización.
    tipo_sistema: el sistema a probar; valores posibles:
        - "basico", "conflicto", "complejo" (de tests_sistemas)
        - "division", "suma", "duplicar" (de funciones)
        - "multiplicar", "potencia" (de operaciones_avanzadas)
    rng_seed: semilla para generador de números aleatorios; si es None, las funciones internas generan aleatoriamente.
    """
    # Número de lapsos a simular
    lapsos = 30

    # Selección del sistema según el tipo solicitado
    if tipo_sistema == "basico":
        sistema = tests_sistemas.sistema_basico()
    elif tipo_sistema == "conflicto":
        sistema = tests_sistemas.sistema_con_conflictos()
    elif tipo_sistema == "complejo":
        sistema = tests_sistemas.Sistema_complejo()
    elif tipo_sistema == "division":
        sistema = funciones.division(10, 3)
    elif tipo_sistema == "suma":
        sistema = funciones.suma(4, 3)
    elif tipo_sistema == "duplicar":
        sistema = funciones.duplicar(4)
    elif tipo_sistema == "multiplicar":
        sistema = operaciones_avanzadas.multiplicar(4, 3)
    else:
        raise ValueError(
            f"Tipo de sistema desconocido: '{tipo_sistema}'.\nOpciones: basico, conflicto, complejo, division, suma, duplicar, multiplicar."
        )

    # Directorio de estadísticas al mismo nivel que este archivo
    dir_base = os.path.dirname(os.path.abspath(__file__))
    estadisticas_dir = os.path.join(dir_base, "Estadisticas")
    os.makedirs(estadisticas_dir, exist_ok=True)
    csv_path = os.path.join(estadisticas_dir, "estadisticas.csv")

    # Registrar estadísticas si se solicitó
    if registrar:
        sistema_a_registrar = copy.deepcopy(sistema)
        df_estadisticas = registrar_estadisticas(
            sistema_a_registrar,
            lapsos=lapsos,
            modo="max_paralelo",
            rng_seed=rng_seed,
            csv_path=csv_path
        )
        print(
            f"Estadísticas guardadas en '{csv_path}' (columnas: {list(df_estadisticas.columns)})"
        )

    # Realizar visualización si se solicitó
    if visualizar:
        simular_y_visualizar(
            sistema,
            pasos=lapsos,
            modo="max_paralelo",
            rng_seed=rng_seed
        )


if __name__ == "__main__":
    main()
