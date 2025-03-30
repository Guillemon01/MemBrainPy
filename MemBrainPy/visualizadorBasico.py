from SistemaP import simular_lapso, SistemaP
from time import sleep

def visualizar_sistema(sistema: SistemaP, pasos: int = 5, delay: float = 1.0):
    """
    Simula y muestra la evolución de un sistema P durante 'pasos' lapsos.
    
    :param sistema: SistemaP ya inicializado con membranas y reglas.
    :param pasos: Número de lapsos a simular.
    :param delay: Tiempo de espera entre pasos, para visualización (en segundos).
    """
    print("===== INICIO DE SIMULACIÓN =====")
    for paso in range(1, pasos + 1):
        print(f"\n--- Lapso {paso} ---")
        simular_lapso(sistema)
        mostrar_estado(sistema)
        sleep(delay)
    print("===== FIN DE SIMULACIÓN =====")

def mostrar_estado(sistema: SistemaP):
    """
    Imprime en consola el estado actual de cada membrana.
    """
    for id_mem, membrana in sistema.piel.items():
        print(f"Membrana {id_mem}:")
        for simbolo, cantidad in membrana.recursos.items():
            print(f"  {simbolo} → {cantidad}")
        print("-" * 20)
