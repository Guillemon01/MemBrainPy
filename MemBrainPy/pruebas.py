import os
import copy
import SistemaP 
import visualizadorAvanzado  
import tests_sistemas
import funciones
import operaciones_avanzadas

sistemas_list = [tests_sistemas.sistema_basico(),
                 tests_sistemas.sistema_con_conflictos(),
]

# Si tu función visualizadora sólo necesita la lista de instancias, sin nombre:
# sistemas_list = [constructor() for constructor in sistemas_dict.values()]
# Llamada final
visualizadorAvanzado.simular_varios_y_visualizar(sistemas=sistemas_list)
