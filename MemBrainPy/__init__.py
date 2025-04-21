from visualizadorBasico import visualizar_sistema
from visualizadorAvanzado import simular_y_visualizar_grafico
import tests_sistemas as tests

# Elegir uno de los sistemas de prueba
sistema = tests.Sistema_complejo()

# Simular visualmente durante 5 pasos
#visualizar_sistema(sistema, pasos=5, delay=1.5)
simular_y_visualizar_grafico(sistema, pasos = 999, delay = 2)