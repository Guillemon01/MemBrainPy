from visualizadorAvanzado import simular_y_visualizar
import tests_sistemas as tests
import funciones
import Lector


#sistema = Lector.leerSistema("tests/Test1.pli")
sistema =funciones.division(10, 3)


simular_y_visualizar(sistema, pasos = 30, modo="max_paralelo")
#visualizar_sistema(sistema, pasos=999, delay=2)