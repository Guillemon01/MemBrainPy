"""
SistemaP.py

Implementación “profesional” de un simulador de Sistemas P (modo máximo paralelo),
con registro de estadísticas por lapso de simulación y exportación en CSV.
"""

from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, DefaultDict
import random
import collections
import pandas as pd


# ----------------------------- TIPOS AUXILIARES ------------------------------

Multiset = Dict[str, int]


@dataclass
class LapsoResult:
    """
    Contiene los datos de un lapso de simulación:
      - seleccionados: parejas (Regla, veces) aplicados en cada membrana.
      - consumos: multiconjuntos consumidos por cada membrana (lo que queda después de la fase de selección).
      - producciones: multiconjuntos producidos para cada membrana este lapso.
      - created: lista de tuplas (id_padre, id_nueva) de membranas creadas.
      - dissolved: lista de IDs de membranas disueltas.
    """
    seleccionados: Dict[str, List[Tuple[Regla, int]]]
    consumos: Dict[str, Multiset]
    producciones: Dict[str, Multiset]
    created: List[Tuple[str, str]]
    dissolved: List[str]


# ------------------------ UTILIDADES PARA MULTICONJUNTOS ----------------------

def add_multiset(ms1: Multiset, ms2: Multiset) -> Multiset:
    """
    Devuelve la unión de dos multiconjuntos (sumando multiplicidades).
    """
    result: DefaultDict[str, int] = collections.defaultdict(int)
    for sym, count in ms1.items():
        result[sym] += count
    for sym, count in ms2.items():
        result[sym] += count
    return dict(result)


def sub_multiset(ms: Multiset, rest: Multiset) -> Multiset:
    """
    Resta el multiconjunto 'rest' de 'ms'. Elimina claves con multiplicidad <= 0.
    """
    result: DefaultDict[str, int] = collections.defaultdict(int)
    for sym, count in ms.items():
        result[sym] = count
    for sym, count in rest.items():
        result[sym] -= count
    return {sym: cnt for sym, cnt in result.items() if cnt > 0}


def multiset_times(ms: Multiset, times: int) -> Multiset:
    """
    Multiplica todas las multiplicidades del multiconjunto 'ms' por 'times'.
    """
    return {sym: cnt * times for sym, cnt in ms.items()}


def max_applications(resources: Multiset, rule: Regla) -> int:
    """
    Dado un multiconjunto 'resources' y una regla 'rule',
    devuelve el número máximo de veces que la regla puede aplicarse.
    """
    min_times = float('inf')
    for sym, needed in rule.left.items():
        available = resources.get(sym, 0)
        min_times = min(min_times, available // needed)
    if min_times == float('inf'):
        return 0
    return int(min_times)


# --------------------------------- CLASES BÁSICAS -----------------------------

@dataclass
class Regla:
    """
    Una regla de evolución de un Sistema P de transición.
    """
    left: Multiset
    right: Multiset
    priority: int
    create_membranes: List[str] = field(default_factory=list)
    dissolve_membranes: List[str] = field(default_factory=list)

    def total_consumption(self) -> int:
        """
        Suma total de objetos en el multiconjunto 'left'.
        """
        return sum(self.left.values())

    def __repr__(self) -> str:
        return (
            f"Regla(left={self.left}, right={self.right}, "
            f"priority={self.priority}, create={self.create_membranes}, "
            f"dissolve={self.dissolve_membranes})"
        )


@dataclass
class Membrana:
    """
    Representa una membrana de un Sistema P.
    - id_mem: identificador único de la membrana.
    - resources: multiconjunto (diccionario) de objetos presentes en la membrana.
    - reglas: lista de reglas asociadas a esta membrana.
    - children: lista de IDs de membranas hijas.
    - parent: ID de la membrana padre (None si es la piel).
    """
    id_mem: str
    resources: Multiset
    reglas: List[Regla] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None

    def add_regla(self, regla: Regla) -> None:
        """
        Agrega una Regla a la membrana.
        """
        self.reglas.append(regla)

    def __repr__(self) -> str:
        return (
            f"Membrana(id={self.id_mem!r}, resources={self.resources}, "
            f"children={self.children}, parent={self.parent!r})"
        )


@dataclass
class SistemaP:
    """
    Representa un Sistema P completo.
    - skin: diccionario de todas las membranas indexado por su ID.
    - output_membrane: ID de la membrana de salida (si hay).
    """
    skin: Dict[str, Membrana] = field(default_factory=dict)
    output_membrane: Optional[str] = None

    def add_membrane(self, membrana: Membrana, parent_id: Optional[str] = None) -> None:
        """
        Inserta una membrana en el sistema.
        Si 'parent_id' no es None, ajusta la relación padre-hijo.
        """
        membrana.parent = parent_id
        self.skin[membrana.id_mem] = membrana
        if parent_id:
            self.skin[parent_id].children.append(membrana.id_mem)

    def __repr__(self) -> str:
        return f"SistemaP(mem={list(self.skin.keys())}, output={self.output_membrane!r})"


# --------------------------- GENERACIÓN DE MAXIMALES --------------------------

def generar_maximales(
    reglas: List[Regla],
    recursos: Multiset
) -> List[List[Tuple[Regla, int]]]:
    """
    Dadas una lista de reglas 'reglas' y un multiconjunto 'recursos',
    genera recursivamente todas las selecciones máximas de pares (Regla, veces)
    aplicables al multiconjunto 'recursos'.
    """
    maximales: List[List[Tuple[Regla, int]]] = []

    def backtrack(start_idx: int, current_resources: Multiset, seleccionado: List[Tuple[Regla, int]]):
        added = False
        for idx in range(start_idx, len(reglas)):
            regla = reglas[idx]
            max_v = max_applications(current_resources, regla)
            if max_v <= 0:
                continue
            added = True
            for count in range(1, max_v + 1):
                consume = multiset_times(regla.left, count)
                new_resources = sub_multiset(current_resources, consume)
                seleccionado.append((regla, count))
                backtrack(idx + 1, new_resources, seleccionado)
                seleccionado.pop()
        if not added:
            # Si no podemos aplicar más reglas, guardamos la selección actual
            maximales.append(list(seleccionado))

    backtrack(0, recursos, [])
    return maximales


# --------------------------- SIMULACIÓN DE UN LAPSO ---------------------------

def simular_lapso(
    sistema: SistemaP,
    modo: str = "max_paralelo",
    rng_seed: Optional[int] = None
) -> LapsoResult:
    """
    Simula un lapso de un Sistema P en 'modo', usando rng_seed para crear
    un RNG local. Con ello, dado el mismo rng_seed, la selección aleatoria
    de máximales es reproducible.

    Args:
        sistema: SistemaP a simular.
        modo: "max_paralelo" (por defecto) o "secuencial" (pendiente).
        rng_seed: semilla opcional para reproducibilidad de rng.shuffle.

    Returns:
        LapsoResult con:
          - seleccionados: qué (Regla, veces) se aplicaron en cada membrana.
          - consumos: recursos remanentes de cada membrana tras consumo.
          - producciones: recursos producidos hacia cada membrana.
          - created: lista de (id_padre, id_nueva) creadas.
          - dissolved: lista de IDs disueltas.
    """
    # Crear un RNG local; si rng_seed es None, se inicializa de forma no determinista
    rng = random.Random(rng_seed)

    producciones: Dict[str, Multiset] = {mid: {} for mid in sistema.skin}
    consumos: Dict[str, Multiset] = {}
    to_create: List[Tuple[str, str]] = []
    to_dissolve: List[str] = []
    seleccionados: Dict[str, List[Tuple[Regla, int]]] = {}

    # Fase 1: selección y consumo en cada membrana
    for mem in list(sistema.skin.values()):
        recursos_disp = deepcopy(mem.resources)
        aplicables = [r for r in mem.reglas if max_applications(recursos_disp, r) > 0]

        if modo == "secuencial":
            # Lógica secuencial no implementada
            pass

        elif modo == "max_paralelo" and aplicables:
            # Filtrar reglas de máxima prioridad
            max_prio = max(r.priority for r in aplicables)
            top_rules = [r for r in aplicables if r.priority == max_prio]
            maxsets = generar_maximales(top_rules, recursos_disp)

            if maxsets:
                # Reordenamiento reproducible según la semilla
                rng.shuffle(maxsets)
                elegido = maxsets[0]
                seleccionados[mem.id_mem] = elegido

                # Aplicar cada regla seleccionada
                for regla, cnt in elegido:
                    consumo_total = multiset_times(regla.left, cnt)
                    recursos_disp = sub_multiset(recursos_disp, consumo_total)

                    # Registrar producciones (_out e _in_)
                    for simb, num in regla.right.items():
                        if simb.endswith("_out"):
                            base = simb[:-4]
                            padre_id = mem.parent
                            if padre_id:
                                producciones[padre_id][base] = (
                                    producciones[padre_id].get(base, 0) + num * cnt
                                )
                        elif "_in_" in simb:
                            base, target = simb.split("_in_")
                            if target in sistema.skin:
                                producciones[target][base] = (
                                    producciones[target].get(base, 0) + num * cnt
                                )
                        else:
                            producciones[mem.id_mem][simb] = (
                                producciones[mem.id_mem].get(simb, 0) + num * cnt
                            )

                    # Anotar creaciones y disoluciones
                    for _ in range(cnt):
                        for new_id in regla.create_membranes:
                            to_create.append((mem.id_mem, new_id))
                        for dis_id in regla.dissolve_membranes:
                            to_dissolve.append(dis_id)

        # Guardar recursos restantes tras consumo
        consumos[mem.id_mem] = recursos_disp

    # Fase 2: aplicar producciones y actualizar recursos
    for mem_id, prod in producciones.items():
        base = consumos.get(mem_id, sistema.skin[mem_id].resources)
        sistema.skin[mem_id].resources = add_multiset(base, prod)

    # Fase 3: procesar disoluciones
    root_id = sistema.output_membrane
    dissolved_list: List[str] = []
    for dis_id in to_dissolve:
        if dis_id == root_id:
            continue
        if dis_id in sistema.skin:
            padre_id = sistema.skin[dis_id].parent
            if padre_id:
                padre = sistema.skin[padre_id]
                # Heredar recursos y reasignar hijos
                heredados = sistema.skin[dis_id].resources
                padre.resources = add_multiset(padre.resources, heredados)
                for hijo_id in sistema.skin[dis_id].children:
                    sistema.skin[hijo_id].parent = padre_id
                    padre.children.append(hijo_id)
                padre.children.remove(dis_id)
            del sistema.skin[dis_id]
            dissolved_list.append(dis_id)

    # Fase 4: procesar creaciones de nuevas membranas
    created_list: List[Tuple[str, str]] = []
    for parent_id, new_id in to_create:
        if new_id not in sistema.skin:
            nueva = Membrana(id_mem=new_id, resources={})
            sistema.add_membrane(nueva, parent_id)
            created_list.append((parent_id, new_id))

    return LapsoResult(
        seleccionados=seleccionados,
        consumos=consumos,
        producciones=producciones,
        created=created_list,
        dissolved=dissolved_list
    )



# ---------------------- REGISTRAR ESTADÍSTICAS MÚLTIPLES -----------------------

def registrar_estadisticas(
    sistema: SistemaP,
    lapsos: int,
    modo: str = "max_paralelo",
    rng_seed: Optional[int] = None,
    csv_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Ejecuta 'lapsos' iteraciones de simular_lapso sobre el mismo sistema (que evoluciona
    en cada lapso) y acumula los resultados de cada uno. Luego, construye y
    retorna un DataFrame con los detalles de cada membrana en cada lapso.

    Cada fila del DataFrame corresponde a:
      - lapso: índice (empezando en 1) del paso de simulación.
      - membrana: ID de la membrana.
      - recursos_restantes: multiconjunto de recursos después de consumir.
      - producciones: multiconjunto producido hacia esa membrana en el lapso.
      - aplicaciones: lista de cadenas describiendo (regla, veces) aplicadas.
      - creadas_global: lista de tuplas (id_padre, id_nueva) creadas en el lapso.
      - disueltas_global: lista de IDs de membranas disueltas en el lapso.

    Args:
        sistema: SistemaP que se va a simular (se modifica en cada lapso).
        lapsos: número de lapsos a simular.
        modo: modo de simulación ("max_paralelo" o "secuencial").
        rng_seed: semilla opcional para reproducibilidad; cada lapso usa seed=rng_seed+i.
        csv_path: ruta opcional donde guardar el CSV resultante; si es None, solo retorna el DataFrame.

    Returns:
        pd.DataFrame con las estadísticas detalladas por lapso y membrana.
    """
    all_results: List[LapsoResult] = []
    for i in range(lapsos):
        seed = None
        if rng_seed is not None:
            seed = rng_seed + i
        lapso_res = simular_lapso(sistema, modo=modo, rng_seed=seed)
        all_results.append(lapso_res)

    # Construir lista de filas
    rows = []
    for idx_l, lapso in enumerate(all_results, start=1):
        # Representar created y dissolved como cadenas
        cre_str = ";".join(f"{p}->{c}" for p, c in lapso.created) if lapso.created else ""
        dis_str = ";".join(lapso.dissolved) if lapso.dissolved else ""
        for mem_id, _ in lapso.consumos.items():
            rec_rest = lapso.consumos.get(mem_id, {})
            prod = lapso.producciones.get(mem_id, {})
            apps = lapso.seleccionados.get(mem_id, [])
            # Formatear aplicaciones como "r_left->r_right(x veces)"
            apps_str = ";".join(
                f"{list(r.left.items())}->{list(r.right.items())}×{cnt}"
                for r, cnt in apps
            ) if apps else ""
            rows.append({
                "lapso": idx_l,
                "membrana": mem_id,
                "recursos_restantes": str(rec_rest),
                "producciones": str(prod),
                "aplicaciones": apps_str,
                "creadas_global": cre_str,
                "disueltas_global": dis_str
            })

    df = pd.DataFrame(rows)
    if csv_path:
        df.to_csv(csv_path, index=False)
    else:
        # Imprimir CSV por consola
        print(df.to_csv(index=False))
    return df

def merge_systems(*systems: SistemaP, global_id: str = "global", output_membrane: Optional[str] = None) -> SistemaP:
    """
    Fusiona varios SistemasP en un único SistemaP con una membrana global.
    - systems: uno o varios SistemasP a fusionar (pasados como argumentos separados).
    - global_id: identificador de la nueva membrana piel.
    - output_membrane: opcional, ID de membrana de salida en el sistema resultante.

    La membrana global contendrá como hijas las antiguas membranas piel de cada sistema,
    preservando sus contenidos, reglas y subestructuras.
    """
    # Instanciar sistema resultante
    merged = SistemaP()
    # Crear y añadir membrana piel global
    global_mem = Membrana(id_mem=global_id, resources={}, reglas=[], children=[], parent=None)
    merged.add_membrane(global_mem)

    # Recorrer cada sistema a fusionar
    for idx, sys in enumerate(systems):
        # Mapeo de IDs antiguos a nuevos para evitar colisiones
        mapping: Dict[str, str] = {}
        for old_id in sys.skin:
            mapping[old_id] = f"{global_id}_{idx}_{old_id}"
        # Copiar membranas al sistema fusionado
        for old_id, membrana in sys.skin.items():
            new_id = mapping[old_id]
            new_mem = Membrana(
                id_mem=new_id,
                resources=deepcopy(membrana.resources),
                reglas=[deepcopy(r) for r in membrana.reglas],
                children=[],
                parent=None
            )
            # Añadir sin asignar padre todavía
            merged.skin[new_id] = new_mem
        # Reconstruir jerarquía padre-hijo
        for old_id, membrana in sys.skin.items():
            new_id = mapping[old_id]
            old_parent = membrana.parent
            if old_parent is None:
                parent_id = global_id
            else:
                parent_id = mapping.get(old_parent, global_id)
            merged.add_membrane(merged.skin[new_id], parent_id)

    # Definir membrana de salida si se especifica
    if output_membrane:
        merged.output_membrane = output_membrane

    return merged