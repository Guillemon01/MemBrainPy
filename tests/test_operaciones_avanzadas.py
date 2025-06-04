import sys
sys.path.append('MemBrainPy')
from operaciones_avanzadas import multiplicar, potencia


def test_multiplicar():
    assert multiplicar(3, 4) == 12
    assert multiplicar(0, 5) == 0
    assert multiplicar(5, 0) == 0
    assert multiplicar(7, 1) == 7


def test_potencia():
    assert potencia(2, 5) == 32
    assert potencia(3, 3) == 27
    assert potencia(5, 0) == 1
