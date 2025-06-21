'''funciones.py

Colección de funciones que generan Sistemas P específicos (división, suma, resta, etc.).
Utilizan el módulo 'SistemaP' para construir la estructura de membranas y reglas.
'''
from typing import Dict, Optional

from .SistemaP import SistemaP, Membrana, Regla, Production, Direction


def division(n: int, divisor: int) -> SistemaP:
    """
    División entera de n 'a' entre divisor:
      - prioridad 2: consume divisor 'a' → produce 'b' en membrana de salida.
      - prioridad 1: consume 1 'a'      → produce 'r' en membrana de salida.
    En modo max_paralelo genera b^(n//divisor) y r^(n%divisor).
    """
    sistema = SistemaP(output_membrane="m_out")
    # Membrana de salida (piel)
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    # Membrana de trabajo con el contador 'a'
    m1 = Membrana(id_mem="m1", resources={"a": n})
    # Regla de prioridad 2: agrupa bloques de tamaño `divisor`
    regla_div = Regla(
        left={"a": divisor},
        productions=[Production(symbol="b", count=1, direction=Direction.OUT)],
        priority=2
    )
    # Regla de prioridad 1: consume 'a' restante → produce 'r'
    regla_res = Regla(
        left={"a": 1},
        productions=[Production(symbol="r", count=1, direction=Direction.OUT)],
        priority=1
    )
    m1.add_regla(regla_div)
    m1.add_regla(regla_res)
    sistema.add_membrane(m1, parent_id="m_out")

    return sistema


def suma(n: int, m: int) -> SistemaP:
    """
    Suma n 'a' + m 'b':
      - prioridad 1: consume 1 'a' → produce 1 'c' en salida.
      - prioridad 1: consume 1 'b' → produce 1 'c' en salida.
    En modo max_paralelo produce c^(n+m).
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n, "b": m})
    regla_a = Regla(
        left={"a": 1},
        productions=[Production(symbol="c", count=1, direction=Direction.OUT)],
        priority=1
    )
    regla_b = Regla(
        left={"b": 1},
        productions=[Production(symbol="c", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_a)
    mem.add_regla(regla_b)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def resta(n: int, m: int) -> SistemaP:
    """
    Resta n - m:
      - prioridad 3: consume 1 'a' + 1 'b' → empareja (no produce).
      - prioridad 2: consume 1 'a' → produce 'd' en salida si n > m.
      - prioridad 1: consume 1 'b' → produce 'e' en salida si m > n.
    En modo max_paralelo empareja, luego produce d^(n-m) o e^(m-n).
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n, "b": m})
    regla_emp = Regla(
        left={"a": 1, "b": 1},
        productions=[],  # empareja sin producir
        priority=3
    )
    regla_a = Regla(
        left={"a": 1},
        productions=[Production(symbol="d", count=1, direction=Direction.OUT)],
        priority=2
    )
    regla_b = Regla(
        left={"b": 1},
        productions=[Production(symbol="e", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_emp)
    mem.add_regla(regla_a)
    mem.add_regla(regla_b)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def paridad(n: int) -> SistemaP:
    """
    Paridad de n 'a':
      - prioridad 2: consume 2 'a' → empareja (no produce).
      - prioridad 1: consume 1 'a' → produce 'i' en salida.
    En modo max_paralelo genera emparejamientos p^(n//2) y un 'i' si n es impar.
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n})
    regla_emp = Regla(
        left={"a": 2},
        productions=[],  # empareja pares de 'a'
        priority=2
    )
    regla_i = Regla(
        left={"a": 1},
        productions=[Production(symbol="i", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_emp)
    mem.add_regla(regla_i)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def duplicar(n: int) -> SistemaP:
    """
    Duplica contador n:
      - prioridad 1: consume 1 'a' → produce 2 'b' en salida.
    En modo max_paralelo produce 2n 'b'.
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n})
    regla_dup = Regla(
        left={"a": 1},
        productions=[Production(symbol="b", count=2, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_dup)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def comparacion(n: int, m: int) -> SistemaP:
    """
    Compara n y m:
      - prioridad 3: consume 1 'a' + 1 'b' → empareja.
      - prioridad 2: consume 1 'a' → produce 'g' en salida;
                   consume 1 'b' → produce 'l' en salida.
      - prioridad 1: consume 0     → produce 'e' en salida.
    En modo max_paralelo empareja, luego produce g/l o e.
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n, "b": m})
    regla_emp = Regla(
        left={"a": 1, "b": 1},
        productions=[],  # empareja sin producir
        priority=3
    )
    regla_a = Regla(
        left={"a": 1},
        productions=[Production(symbol="g", count=1, direction=Direction.OUT)],
        priority=2
    )
    regla_b = Regla(
        left={"b": 1},
        productions=[Production(symbol="l", count=1, direction=Direction.OUT)],
        priority=2
    )
    regla_e = Regla(
        left={},
        productions=[Production(symbol="e", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_emp)
    mem.add_regla(regla_a)
    mem.add_regla(regla_b)
    mem.add_regla(regla_e)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def modulo(n: int, m: int) -> SistemaP:
    """
    Resto de n mod m:
      - prioridad 2: consume m 'a' → empareja (descarta bloques completos).
      - prioridad 1: consume 1 'a' → produce 'r' en salida.
    En modo max_paralelo genera r^(n % m).
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n})
    regla_emp = Regla(
        left={"a": m},
        productions=[],  # descarta bloques completos de tamaño m
        priority=2
    )
    regla_r = Regla(
        left={"a": 1},
        productions=[Production(symbol="r", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_emp)
    mem.add_regla(regla_r)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema


def umbral(n: int, k: int) -> SistemaP:
    """
    Test de umbral k en n:
      - prioridad 2: consume k 'a' → produce 't' en salida.
      - prioridad 1: consume 0     → produce 'f' en salida.
    En modo max_paralelo, si n >= k produce 't'; si n < k produce 'f'.
    """
    sistema = SistemaP(output_membrane="m_out")
    m_out = Membrana(id_mem="m_out", resources={})
    sistema.add_membrane(m_out)

    mem = Membrana(id_mem="m1", resources={"a": n})
    regla_t = Regla(
        left={"a": k},
        productions=[Production(symbol="t", count=1, direction=Direction.OUT)],
        priority=2
    )
    regla_f = Regla(
        left={},
        productions=[Production(symbol="f", count=1, direction=Direction.OUT)],
        priority=1
    )
    mem.add_regla(regla_t)
    mem.add_regla(regla_f)
    sistema.add_membrane(mem, parent_id="m_out")

    return sistema
