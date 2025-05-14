from copy import deepcopy
from typing import Dict, List, Optional, Tuple
from itertools import product
import random


# Funciones de apoyo para multisets

def union_multiconjuntos(ms1: Dict[str, int], ms2: Dict[str, int]) -> Dict[str, int]:
    resultado = ms1.copy()
    for simbolo, cantidad in ms2.items():
        resultado[simbolo] = resultado.get(simbolo, 0) + cantidad
    return resultado

def resta_multiconjuntos(ms: Dict[str, int], ms_resta: Dict[str, int]) -> Dict[str, int]:
    resultado = ms.copy()
    for simbolo, cantidad in ms_resta.items():
        resultado[simbolo] = resultado.get(simbolo, 0) - cantidad
    # Eliminar símbolos con cantidad <= 0 para reflejar correctamente el consumo
    return {s: c for s, c in resultado.items() if c > 0}

# Calcula cuántas veces se puede aplicar completamente una regla a unos recursos dados
def veces_aplicable(recursos: Dict[str, int], regla: 'Regla') -> int:
    max_veces = float('inf')
    for simbolo, cantidad in regla.izquierda.items():
        disponibles = recursos.get(simbolo, 0)
        max_veces = min(max_veces, disponibles // cantidad)
    return max_veces if max_veces != float('inf') else 0

from typing import List, Tuple, Dict

def multiplicar_multiconjunto(ms: Dict[str, int], veces: int) -> Dict[str, int]:
    """Devuelve el multiconjunto ms multiplicado por un escalar ‘veces’."""
    return {s: c * veces for s, c in ms.items()}

def generar_maximales(reglas: List[Regla],
                      recursos: Dict[str, int]
                      ) -> List[List[Tuple[Regla, int]]]:
    """
    Genera todas las combinaciones (listas de pares (regla, veces)) tales que:
      - Consumen <= recursos.
      - Son maximal: no se puede aumentar ninguna ejecución de ninguna regla.
    """

    maximales: List[List[Tuple[Regla, int]]] = []
    
    def backtrack(start: int,
                  recursos_disp: Dict[str, int],
                  seleccion: List[Tuple[Regla, int]]):
        # Buscamos si aún hay alguna regla aplicable
        any_aplicable = False
        for i in range(start, len(reglas)):
            regla = reglas[i]
            max_v = veces_aplicable(recursos_disp, regla)
            if max_v > 0:
                any_aplicable = True
                # Intentamos todas las posibilidades de 1..max_v aplicaciones de esta regla
                for v in range(1, max_v + 1):
                    # Restamos los recursos
                    consumido = multiplicar_multiconjunto(regla.izquierda, v)
                    nuevos_rec = resta_multiconjuntos(recursos_disp, consumido)
                    seleccion.append((regla, v))
                    backtrack(i + 1, nuevos_rec, seleccion)
                    seleccion.pop()
        # Si no hay ninguna regla aplicable en todo el rango [start..], es maximal
        if not any_aplicable:
            maximales.append(seleccion.copy())

    backtrack(0, recursos, [])
    return maximales



# Clase que representa una regla del sistema P
class Regla:
    def __init__(
        self,
        izquierda: Dict[str, int],
        derecha: Dict[str, int],
        prioridad: int,
        crea_membranas: Optional[List[str]] = None,
        disuelve_membranas: Optional[List[str]] = None
    ):
        self.izquierda = izquierda
        self.derecha = derecha
        self.prioridad = prioridad
        self.crea_membranas = crea_membranas or []
        self.disuelve_membranas = disuelve_membranas or []

    def total_consumo(self) -> int:
        return sum(self.izquierda.values())

    def total_produccion(self) -> int:
        return sum(self.derecha.values())

    def __repr__(self):
        return (
            f"Regla(izq={self.izquierda}, der={self.derecha}, pri={self.prioridad}, "
            f"crea={self.crea_membranas}, disuelve={self.disuelve_membranas})"
        )

# Clase que representa una membrana
class Membrana:
    def __init__(self, id_mem: str, recursos: Dict[str, int]):
        self.id = id_mem
        self.recursos = recursos
        self.reglas: List[Regla] = []
        self.hijos: List[str] = []
        self.padre: Optional[str] = None

    def agregar_regla(self, regla: Regla):
        self.reglas.append(regla)

    def __repr__(self):
        return (
            f"Membrana(id={self.id}, padre={self.padre}, recursos={self.recursos}, "
            f"hijos={self.hijos})"
        )

# Clase que agrupa todas las membranas
class SistemaP:
    def __init__(self):
        self.piel: Dict[str, Membrana] = {}

    def agregar_membrana(self, membrana: Membrana, parent_id: Optional[str] = None):
        membrana.padre = parent_id
        self.piel[membrana.id] = membrana
        if parent_id:
            padre = self.piel[parent_id]
            padre.hijos.append(membrana.id)

    def obtener_membrana(self, id_mem: str) -> Optional[Membrana]:
        return self.piel.get(id_mem)

    def __repr__(self):
        return f"SistemaP({self.piel})"


def regla_aplicable(recursos: Dict[str, int], regla: Regla) -> bool:
    for simbolo, cantidad in regla.izquierda.items():
        if recursos.get(simbolo, 0) < cantidad:
            return False
    return True


def resolver_conflicto(membrana: Membrana, reglas: List[Regla]) -> List[Regla]:
    reglas_ordenadas = sorted(reglas, key=lambda r: r.total_consumo(), reverse=True)
    return reglas_ordenadas[:1]


def simular_lapso(sistema: SistemaP, modo: str = "paralelo") -> None:
    """
    Simula un lapso del sistema P.

    modo: 'paralelo' (default) o 'secuencial'.
      - paralelo: evalúa todas las reglas simultáneamente (priorizando por consumo).
      - secuencial: para cada membrana, elige la regla de mayor prioridad y la ejecuta tantas veces como sea posible de golpe.
    """
    producciones: Dict[str, Dict[str, int]] = {mid: {} for mid in sistema.piel}
    consumos: Dict[str, Dict[str, int]] = {}
    to_create: List[Tuple[str, str]] = []
    to_dissolve: List[str] = []

    for membrana in list(sistema.piel.values()):
        recursos_disp = deepcopy(membrana.recursos)

        if modo == "secuencial":
            # Seleccionar la regla de mayor prioridad
            aplicables = [r for r in membrana.reglas if regla_aplicable(recursos_disp, r)]
            if aplicables:
                max_prio = max(r.prioridad for r in aplicables)
                candidatos = [r for r in aplicables if r.prioridad == max_prio]
                regla = resolver_conflicto(membrana, candidatos)[0]
                # Calcular cuántas veces se puede aplicar
                veces = veces_aplicable(recursos_disp, regla)
                if veces > 0:
                    # Consumir y producir de golpe
                    for simbolo, cantidad in regla.izquierda.items():
                        recursos_disp[simbolo] = recursos_disp.get(simbolo, 0) - cantidad * veces
                    for simbolo, cantidad in regla.derecha.items():
                        producciones[membrana.id][simbolo] = producciones[membrana.id].get(simbolo, 0) + cantidad * veces
                    # Operaciones de membrana repetidas veces
                    for _ in range(veces):
                        for new_id in regla.crea_membranas:
                            to_create.append((membrana.id, new_id))
                        for dis_id in regla.disuelve_membranas:
                            to_dissolve.append(dis_id)
            consumos[membrana.id] = {s: c for s, c in recursos_disp.items() if c > 0}
            continue

        if modo == "max_paralelo":
            aplicables = [r for r in membrana.reglas if veces_aplicable(recursos_disp, r) > 0]
            if aplicables:
                maximales = generar_maximales(aplicables, recursos_disp)
                if maximales:
                    elegido = random.choice(maximales)
                    # Aplicar el maximal
                    for regla, veces in elegido:
                        # Consumir usando tus funciones auxiliares
                        consumido = multiplicar_multiconjunto(regla.izquierda, veces)
                        recursos_disp = resta_multiconjuntos(recursos_disp, consumido)
                        # Producir
                        for s, c in regla.derecha.items():
                            producciones[membrana.id][s] = producciones[membrana.id].get(s, 0) + c * veces
                        # Membranas a crear o disolver
                        for _ in range(veces):
                            for new_id in regla.crea_membranas:
                                to_create.append((membrana.id, new_id))
                            for dis_id in regla.disuelve_membranas:
                                to_dissolve.append(dis_id)
            # Guardar el estado de recursos restante
            consumos[membrana.id] = recursos_disp.copy()
            continue



        # Modo paralelo (comportamiento original)
        reglas_por_prio: Dict[int, List[Regla]] = {}
        for regla in membrana.reglas:
            if regla_aplicable(recursos_disp, regla):
                reglas_por_prio.setdefault(regla.prioridad, []).append(regla)

        for prio in sorted(reglas_por_prio.keys(), reverse=True):
            seleccionadas = resolver_conflicto(membrana, reglas_por_prio[prio])
            for regla in seleccionadas:
                if regla_aplicable(recursos_disp, regla):
                    recursos_disp = resta_multiconjuntos(recursos_disp, regla.izquierda)
                    for s, c in regla.derecha.items():
                        producciones[membrana.id][s] = producciones[membrana.id].get(s, 0) + c
                    for new_id in regla.crea_membranas:
                        to_create.append((membrana.id, new_id))
                    for dis_id in regla.disuelve_membranas:
                        to_dissolve.append(dis_id)
        consumos[membrana.id] = recursos_disp

    # 2) Actualizar recursos en cada membrana
    for mid, prod in producciones.items():
        mem = sistema.piel[mid]
        base = consumos.get(mid, mem.recursos)
        mem.recursos = union_multiconjuntos(base, prod)

    # 3) Procesar disoluciones
    for dis_id in to_dissolve:
        if dis_id not in sistema.piel:
            continue
        mem = sistema.piel[dis_id]
        parent_id = mem.padre
        if parent_id is None:
            continue
        padre = sistema.piel[parent_id]
        padre.recursos = union_multiconjuntos(padre.recursos, mem.recursos)
        for child_id in mem.hijos:
            child = sistema.piel[child_id]
            child.padre = parent_id
            padre.hijos.append(child_id)
        padre.hijos.remove(dis_id)
        del sistema.piel[dis_id]

    # 4) Procesar creaciones
    for parent_id, new_id in to_create:
        if new_id in sistema.piel:
            continue
        nueva = Membrana(new_id, {})
        sistema.agregar_membrana(nueva, parent_id)
