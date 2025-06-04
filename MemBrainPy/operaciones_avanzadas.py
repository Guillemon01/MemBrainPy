"""Operaciones matemáticas compuestas basadas en :mod:`funciones`.

Este módulo define utilidades como `multiplicar` o `potencia` que emplean
las funciones elementales de ``funciones.py`` para realizar cálculos más
complejos. Cada operación ejecuta internamente sistemas P creados por las
funciones básicas y devuelve el resultado numérico correspondiente.
"""

from SistemaP import simular_lapso
import funciones


def _run_suma(n: int, m: int) -> int:
    """Ejecuta el sistema de :func:`funciones.suma` y devuelve ``n+m``.

    La simulación se realiza en modo ``max_paralelo`` con una semilla fija
    para que el comportamiento sea determinista durante las pruebas.
    """
    sistema = funciones.suma(n, m)
    # Bucle acotado por n+m pasos para garantizar finalización
    for _ in range(max(n + m, 1)):
        simular_lapso(sistema, rng_seed=0)
        mem = sistema.skin["m1"]
        if mem.resources.get("a", 0) == 0 and mem.resources.get("b", 0) == 0:
            break
    return sistema.skin["m_out"].resources.get("c", 0)


def multiplicar(a: int, b: int) -> int:
    """Devuelve ``a*b`` empleando sumas sucesivas."""
    resultado = 0
    for _ in range(b):
        resultado = _run_suma(resultado, a)
    return resultado


def potencia(base: int, exponente: int) -> int:
    """Calcula ``base**exponente`` usando multiplicaciones repetidas."""
    resultado = 1
    for _ in range(exponente):
        resultado = multiplicar(resultado, base)
    return resultado
