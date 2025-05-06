from visualizadorBasico import visualizar_sistema
from visualizadorAvanzado import simular_y_visualizar_grafico
import tests_sistemas as tests
import Lector


#sistema = Lector.leerSistema("tests/Test1.pli")
sistema = tests.sistema_basico()


simular_y_visualizar_grafico(sistema, pasos = 30, delay = 1)
#visualizar_sistema(sistema, pasos=999, delay=2)