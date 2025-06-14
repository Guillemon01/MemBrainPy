import os
import copy
import SistemaP 
import visualizadorAvanzado  
import tests_sistemas
import funciones
import operaciones_avanzadas
import configurador
"""
sistemas_list = [tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_con_conflictos(),
]
"""

sistema = configurador.configurar_sistema_p()


# Si tu función visualizadora sólo necesita la lista de instancias, sin nombre:
# sistemas_list = [constructor() for constructor in sistemas_dict.values()]
# Llamada final
visualizadorAvanzado.simular_y_visualizar(sistema)
