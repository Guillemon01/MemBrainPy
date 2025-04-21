from copy import deepcopy
from typing import Dict, List, Optional, Tuple

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
    return resultado

# Clase que representa una regla del sistema P
class Regla:
    def __init__(
        self,
        izquierda: Dict[str, int],
        derecha: Dict[str, int],
        prioridad: int,
        crea_membranas: Optional[List[str]] = None,       # añadido
        disuelve_membranas: Optional[List[str]] = None    # añadido
    ):
        self.izquierda = izquierda
        self.derecha = derecha
        self.prioridad = prioridad
        self.crea_membranas = crea_membranas or []         # añadido
        self.disuelve_membranas = disuelve_membranas or [] # añadido

    def total_consumo(self) -> int:
        return sum(self.izquierda.values())

    def total_produccion(self) -> int:
        return sum(self.derecha.values())

    def __repr__(self):
        return (f"Regla(izq={self.izquierda}, der={self.derecha}, pri={self.prioridad}, "
                f"crea={self.crea_membranas}, disuelve={self.disuelve_membranas})")

# Clase que representa una membrana
class Membrana:
    def __init__(self, id_mem: str, recursos: Dict[str, int]):
        self.id = id_mem
        self.recursos = recursos
        self.reglas: List[Regla] = []
        self.hijos: List[str] = []
        self.padre: Optional[str] = None                   # añadido

    def agregar_regla(self, regla: Regla):
        self.reglas.append(regla)

    def __repr__(self):
        return (f"Membrana(id={self.id}, padre={self.padre}, recursos={self.recursos}, "
                f"hijos={self.hijos})")

# Clase que agrupa todas las membranas
class SistemaP:
    def __init__(self):
        self.piel: Dict[str, Membrana] = {}

    def agregar_membrana(self, membrana: Membrana, parent_id: Optional[str] = None):
        membrana.padre = parent_id                          # añadido
        self.piel[membrana.id] = membrana
        if parent_id:
            padre = self.piel[parent_id]
            padre.hijos.append(membrana.id)                # añadido

    def obtener_membrana(self, id_mem: str) -> Membrana:
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

def simular_lapso(sistema: SistemaP) -> None:
    # Acumuladores
    producciones: Dict[str, Dict[str, int]] = {mid: {} for mid in sistema.piel}
    to_create: List[Tuple[str, str]] = []      # (parent_id, new_id)
    to_dissolve: List[str] = []                # IDs de membranas a disolver

    # 1) Aplicación de reglas
    for membrana in list(sistema.piel.values()):
        recursos_disp = deepcopy(membrana.recursos)
        reglas_por_prio: Dict[int, List[Regla]] = {}
        for regla in membrana.reglas:
            if regla_aplicable(recursos_disp, regla):
                reglas_por_prio.setdefault(regla.prioridad, []).append(regla)

        for prio in sorted(reglas_por_prio.keys(), reverse=True):
            seleccionadas = resolver_conflicto(membrana, reglas_por_prio[prio])
            for regla in seleccionadas:
                if regla_aplicable(recursos_disp, regla):
                    recursos_disp = resta_multiconjuntos(recursos_disp, regla.izquierda)
                    # Recursos producidos
                    for s, c in regla.derecha.items():
                        producciones[membrana.id][s] = producciones[membrana.id].get(s, 0) + c
                    # Operaciones de membrana
                    for new_id in regla.crea_membranas:
                        to_create.append((membrana.id, new_id))
                    for dis_id in regla.disuelve_membranas:
                        to_dissolve.append(dis_id)

    # 2) Actualizar recursos en cada membrana
    for mid, prod in producciones.items():
        mem = sistema.piel[mid]
        mem.recursos = union_multiconjuntos(mem.recursos, prod)

    # 3) Procesar disoluciones
    for dis_id in to_dissolve:
        if dis_id not in sistema.piel:
            continue
        mem = sistema.piel[dis_id]
        parent_id = mem.padre
        if parent_id is None:
            continue  # no disolver la piel
        padre = sistema.piel[parent_id]
        # Transferir recursos
        padre.recursos = union_multiconjuntos(padre.recursos, mem.recursos)
        # Reparentar hijos
        for child_id in mem.hijos:
            child = sistema.piel[child_id]
            child.padre = parent_id
            padre.hijos.append(child_id)
        # Eliminar la membrana
        padre.hijos.remove(dis_id)
        del sistema.piel[dis_id]

    # 4) Procesar creaciones
    for parent_id, new_id in to_create:
        if new_id in sistema.piel:
            continue  # ya existe
        nueva = Membrana(new_id, {})                 # vacía al crearse
        sistema.agregar_membrana(nueva, parent_id)
