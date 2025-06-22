#!/usr/bin/env python3
# prueba_sat.py

from MemBrainPy import configurar_expresion_booleana, generar_sistema_por_estructura, resolver_satisfaccion
from MemBrainPy import visualizadorAvanzado

def main():
    expr = configurar_expresion_booleana()
    if expr is None:
        print("No se proporcionó ninguna expresión. Saliendo.")
        return

    print("Has introducido:", expr)
    Res = resolver_satisfaccion(expr)
    print(Res)
    sistema = generar_sistema_por_estructura(expr)
    visualizadorAvanzado.simular_y_visualizar(sistema, pasos=10)

if __name__ == "__main__":
    main()
