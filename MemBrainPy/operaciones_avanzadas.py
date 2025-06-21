'''Operaciones matemáticas compuestas basadas en :mod:`funciones`.

Este módulo define utilidades como `multiplicar` o `potencia` que emplean
las funciones elementales de ``funciones.py`` para realizar cálculos más
complejos. Cada operación ejecuta internamente sistemas P creados por las
funciones básicas y devuelve el resultado numérico correspondiente.
'''
from __future__ import annotations
from typing import Optional

from .SistemaP import simular_lapso, SistemaP, Membrana
from . import funciones


def _run_suma(n: int, m: int, rng_seed: Optional[int] = 0) -> int:
    """Ejecuta el sistema de :func:`funciones.suma` y devuelve ``n + m``.

    La simulación se realiza paso a paso en modo max_paralelo hasta vaciar
    las membranas "a" y "b", o alcanzar un límite de pasos determinista.
    """
    sistema: SistemaP = funciones.suma(n, m)
    max_steps = max(n + m, 1)
    for step in range(max_steps):
        simular_lapso(sistema, rng_seed=(rng_seed or 0) + step)
        m1 = sistema.skin.get("m1")
        if not m1:
            break
        if m1.resources.get("a", 0) == 0 and m1.resources.get("b", 0) == 0:
            break
    m_out = sistema.skin.get("m_out")
    return m_out.resources.get("c", 0) if m_out else 0


def multiplicar(a: int, b: int, rng_seed: Optional[int] = 0) -> int:
    """Devuelve ``a * b`` empleando sumas sucesivas."""
    resultado = 0
    for i in range(max(b, 0)):
        resultado = _run_suma(resultado, a, rng_seed=(rng_seed or 0) + i)
    return resultado


def potencia(base: int, exponente: int, rng_seed: Optional[int] = 0) -> int:
    """Calcula ``base ** exponente`` usando multiplicaciones repetidas."""
    resultado = 1
    for i in range(max(exponente, 0)):
        resultado = multiplicar(resultado, base, rng_seed=(rng_seed or 0) + i)
    return resultado


__all__ = ["multiplicar", "potencia"]
