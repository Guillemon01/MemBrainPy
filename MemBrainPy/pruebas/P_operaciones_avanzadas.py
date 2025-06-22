from MemBrainPy import multiplicar, potencia

def test_multiplicar():
    assert multiplicar(3, 4) == 12
    assert multiplicar(0, 5) == 0
    assert multiplicar(5, 0) == 0
    assert multiplicar(7, 1) == 7
    print("Todas las pruebas de multiplicar pasaron correctamente.")


def test_potencia():
    assert potencia(2, 5) == 32
    assert potencia(3, 3) == 27
    assert potencia(5, 0) == 1
    print("Todas las pruebas de potencia pasaron correctamente.")


test_multiplicar()
test_potencia()
