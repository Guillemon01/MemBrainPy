# config_and_run.py
from MemBrainPy import configurador
from MemBrainPy import visualizadorAvanzado

# Lanza la UI para que el usuario cree/configure un SistemaP
sistema = configurador.configurar_sistema_p()


if sistema is None:
    print("Configuración cancelada. Saliendo.")
else:
    # Una vez tengas el SistemaP configurado, simula y visualízalo:
    visualizadorAvanzado.simular_y_visualizar(
        sistema,
        pasos=30,              # número de lapsos que quieres simular
        rng_seed=123           # semilla para reproducibilidad (o None)
    )