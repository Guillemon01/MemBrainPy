from copy import deepcopy
from typing import Dict, List

# Funciones de apoyo para multisets (representados como diccionarios {símbolo: cantidad})

def union_multiconjuntos(ms1: Dict[str, int], ms2: Dict[str, int]) -> Dict[str, int]:
    """
    Devuelve la unión (suma) de dos multisets.
    """
    resultado = ms1.copy()
    for simbolo, cantidad in ms2.items():
        resultado[simbolo] = resultado.get(simbolo, 0) + cantidad
    return resultado

def resta_multiconjuntos(ms: Dict[str, int], ms_resta: Dict[str, int]) -> Dict[str, int]:
    """
    Resta las cantidades del multiset ms_resta del multiset ms.
    Se asume que ms tiene suficientes recursos.
    """
    resultado = ms.copy()
    for simbolo, cantidad in ms_resta.items():
        resultado[simbolo] = resultado.get(simbolo, 0) - cantidad
    return resultado

# Clase que representa una regla del sistema P
class Regla:
    def __init__(self, izquierda: Dict[str, int], derecha: Dict[str, int], prioridad: int):
        """
        izquierda: diccionario que representa los símbolos a consumir.
        derecha: diccionario que representa los símbolos a producir.
        prioridad: entero que determina el orden de aplicación en caso de conflicto.
        """
        self.izquierda = izquierda  # Consumo
        self.derecha = derecha      # Producción
        self.prioridad = prioridad

    def total_consumo(self) -> int:
        """Suma total de los recursos que consume la regla."""
        return sum(self.izquierda.values())

    def total_produccion(self) -> int:
        """Suma total de los recursos que produce la regla."""
        return sum(self.derecha.values())

    def __repr__(self):
        return f"Regla(izq={self.izquierda}, der={self.derecha}, pri={self.prioridad})"


# Clase que representa una membrana
class Membrana:
    def __init__(self, id_mem: str, recursos: Dict[str, int]):
        """
        id_mem: identificador único de la membrana.
        recursos: diccionario que representa la cantidad de cada símbolo.
        reglas: lista de reglas asociadas a la membrana.
        hijos: lista de id's de membranas hijas.
        """
        self.id = id_mem
        self.recursos = recursos
        self.reglas: List[Regla] = []
        self.hijos: List[str] = []  # Se pueden usar para construir la estructura anidada

    def agregar_regla(self, regla: Regla):
        self.reglas.append(regla)

    def __repr__(self):
        return f"Membrana(id={self.id}, recursos={self.recursos})"


# Clase que agrupa todas las membranas (la "piel" del sistema P)
class SistemaP:
    def __init__(self):
        # Diccionario: id_membrana -> instancia de Membrana
        self.piel: Dict[str, Membrana] = {}

    def agregar_membrana(self, membrana: Membrana):
        self.piel[membrana.id] = membrana

    def obtener_membrana(self, id_mem: str) -> Membrana:
        return self.piel.get(id_mem)

    def __repr__(self):
        return f"SistemaP({self.piel})"


# Función que verifica si se puede aplicar una regla dado un conjunto de recursos
def regla_aplicable(recursos: Dict[str, int], regla: Regla) -> bool:
    """
    Devuelve True si en 'recursos' se tienen suficientes símbolos para aplicar la regla.
    """
    for simbolo, cantidad in regla.izquierda.items():
        if recursos.get(simbolo, 0) < cantidad:
            return False
    return True


# Función de resolución de conflictos
def resolver_conflicto(membrana: Membrana, reglas: List[Regla]) -> List[Regla]:
    """
    Dada una lista de reglas aplicables con la misma prioridad para una membrana,
    reordena (o filtra) la lista según una estrategia de resolución de conflictos.
    
    Aquí se aplica una estrategia simple: se ordenan las reglas por el total de recursos consumidos (mayor a menor)
    y se devuelve la lista reordenada. Esto es un punto de partida, y se pueden incorporar otras estrategias,
    como comparar el número de símbolos en la parte derecha o izquierda.
    """
    reglas_ordenadas = sorted(reglas, key=lambda r: r.total_consumo(), reverse=True)
    # Para simplificar, se opta por aplicar una sola regla por grupo de prioridad.
    return reglas_ordenadas[:1]


# Función para simular un lapso (un paso de evolución) en el sistema P.
def simular_lapso(sistema: SistemaP) -> None:
    """
    Simula un lapso en el que se:
      1. Recopilan las reglas aplicables de cada membrana.
      2. Se agrupan por prioridad y se reordena cada grupo en base a una estrategia de resolución de conflictos.
      3. Se ejecutan las reglas (consumiendo recursos y acumulando producciones).
      4. Se actualizan los recursos de cada membrana con las producciones acumuladas, sin utilizar
         los recursos producidos durante el mismo lapso.
    """
    # Diccionario para almacenar la producción acumulada por cada membrana en este lapso.
    producciones: Dict[str, Dict[str, int]] = {id_mem: {} for id_mem in sistema.piel.keys()}

    # Procesamos cada membrana por separado.
    for membrana in sistema.piel.values():
        # Se trabaja con una copia de los recursos actuales para evitar usar recursos producidos en el mismo lapso.
        recursos_disponibles = deepcopy(membrana.recursos)

        # Agrupar reglas aplicables por prioridad.
        reglas_por_prioridad: Dict[int, List[Regla]] = {}
        for regla in membrana.reglas:
            if regla_aplicable(recursos_disponibles, regla):
                reglas_por_prioridad.setdefault(regla.prioridad, []).append(regla)

        # Procesar grupos de reglas ordenados por prioridad (suponemos que mayor valor de prioridad es mayor)
        for prioridad in sorted(reglas_por_prioridad.keys(), reverse=True):
            reglas = reglas_por_prioridad[prioridad]
            # Resolver conflicto (se puede ampliar la estrategia aquí)
            reglas_seleccionadas = resolver_conflicto(membrana, reglas)
            for regla in reglas_seleccionadas:
                if regla_aplicable(recursos_disponibles, regla):
                    # Consumir recursos (se resta la parte izquierda)
                    recursos_disponibles = resta_multiconjuntos(recursos_disponibles, regla.izquierda)
                    # Acumular producción: se suma la parte derecha en el diccionario de producciones
                    for simbolo, cantidad in regla.derecha.items():
                        producciones[membrana.id][simbolo] = producciones[membrana.id].get(simbolo, 0) + cantidad

        # Nota: En este punto, la ejecución de reglas de la membrana se hace "paralelamente" en el sentido
        # de que los recursos consumidos se basan en el estado inicial y las producciones se acumulan por separado.

    # Actualizar el estado de cada membrana: sumar la producción acumulada a los recursos originales.
    for id_mem, prod in producciones.items():
        membrana = sistema.piel[id_mem]
        membrana.recursos = union_multiconjuntos(membrana.recursos, prod)


# ------------------------------
# Ejemplo de uso / test básico
# ------------------------------
if __name__ == "__main__":
    # Creación de un sistema P
    sistema = SistemaP()

    # Crear una membrana con algunos recursos iniciales
    m1 = Membrana("m1", {"a": 5, "b": 3})
    
    # Definir algunas reglas para la membrana
    # Ejemplo: consumir 2 a's y 1 b para producir 1 c
    regla1 = Regla(izquierda={"a": 2, "b": 1}, derecha={"c": 1}, prioridad=2)
    # Otra regla: consumir 1 a para producir 2 b's
    regla2 = Regla(izquierda={"a": 1}, derecha={"b": 2}, prioridad=1)
    
    m1.agregar_regla(regla1)
    m1.agregar_regla(regla2)

    # Agregar la membrana al sistema
    sistema.agregar_membrana(m1)

    # Mostrar estado inicial
    print("Estado inicial del sistema:")
    for membrana in sistema.piel.values():
        print(membrana)

    # Simular un lapso
    simular_lapso(sistema)

    # Mostrar estado después del lapso
    print("\nEstado del sistema tras un lapso de simulación:")
    for membrana in sistema.piel.values():
        print(membrana)
