from __future__ import annotations
import uuid
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
    result: DefaultDict[str, int] = collections.defaultdict(int)
    for sym, count in ms1.items():
        result[sym] += count
    for sym, count in ms2.items():
        result[sym] += count
    return dict(result)


def sub_multiset(ms: Multiset, rest: Multiset) -> Multiset:
    result: DefaultDict[str, int] = collections.defaultdict(int)
    for sym, count in ms.items():
        result[sym] = count
    for sym, count in rest.items():
        result[sym] -= count
    return {sym: cnt for sym, cnt in result.items() if cnt > 0}


def multiset_times(ms: Multiset, times: int) -> Multiset:
    return {sym: cnt * times for sym, cnt in ms.items()}


def max_applications(resources: Multiset, rule: Regla) -> int:
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
    Una regla de evolución o estructural de un Sistema P.
    - left: multiconjunto de entrada
    - right: multiconjunto de salida (objetos)
    - priority: para seleccionar
    - create_membranes: lista de (etiqueta, recursos_iniciales) para crear
    - dissolve_membranes: etiquetas a disolver
    - division: opcional (v, w) para regla de división
    """
    left: Multiset
    right: Multiset
    priority: int
    create_membranes: List[Tuple[str, Multiset]] = field(default_factory=list)
    dissolve_membranes: List[str] = field(default_factory=list)
    division: Optional[Tuple[Multiset, Multiset]] = None

    def total_consumption(self) -> int:
        return sum(self.left.values())

    def __repr__(self) -> str:
        return (
            f"Regla(left={self.left}, right={self.right}, "
            f"priority={self.priority}, create={self.create_membranes}, "
            f"dissolve={self.dissolve_membranes}, division={self.division})"
        )


@dataclass
class Membrana:
    """
    Representa una membrana de un Sistema P.
    - id_mem: identificador único de la membrana.
    - resources: multiconjunto de objetos.
    - reglas: lista de reglas asociadas.
    - children: lista de IDs de membranas hijas.
    - parent: ID de la membrana padre.
    """
    id_mem: str
    resources: Multiset
    reglas: List[Regla] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None

    def add_regla(self, regla: Regla) -> None:
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
    - skin: todas las membranas activas.
    - prototypes: definición de membranas para creación.
    - output_membrane: ID de salida.
    """
    skin: Dict[str, Membrana] = field(default_factory=dict)
    prototypes: Dict[str, Membrana] = field(default_factory=dict)
    output_membrane: Optional[str] = None

    def register_prototype(self, membrana: Membrana) -> None:
        """
        Registra una membrana como prototipo para futuras creaciones.
        """
        self.prototypes[membrana.id_mem] = membrana

    def add_membrane(self, membrana: Membrana, parent_id: Optional[str] = None) -> None:
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
            maximales.append(list(seleccionado))

    backtrack(0, recursos, [])
    return maximales


# --------------------------- SIMULACIÓN DE UN LAPSO ---------------------------

def simular_lapso(
    sistema: SistemaP,
    rng_seed: Optional[int] = None
) -> LapsoResult:
    modo = "max_paralelo"
    rng = random.Random(rng_seed)

    producciones: Dict[str, Multiset] = {mid: {} for mid in sistema.skin}
    consumos: Dict[str, Multiset] = {}
    to_create: List = []  # tuplas (parent_id, new_id, resources[, reglas])
    to_dissolve: List[str] = []
    seleccionados: Dict[str, List[Tuple[Regla, int]]] = {}

    # Fase 1: selección y consumo
    for mem in list(sistema.skin.values()):
        recursos_disp = deepcopy(mem.resources)
        aplicables = [r for r in mem.reglas if max_applications(recursos_disp, r) > 0]

        if modo == "max_paralelo" and aplicables:
            max_prio = max(r.priority for r in aplicables)
            top_rules = [r for r in aplicables if r.priority == max_prio]
            maxsets = generar_maximales(top_rules, recursos_disp)

            if maxsets:
                rng.shuffle(maxsets)
                elegido = maxsets[0]
                seleccionados[mem.id_mem] = elegido

                for regla, cnt in elegido:
                    # División structural
                    if regla.division:
                        v, w = regla.division
                        base = sub_multiset(mem.resources, multiset_times(regla.left, cnt))
                        # disolver original
                        to_dissolve.append(mem.id_mem)
                        for _ in range(cnt):
                            # IDs únicos
                            id1 = f"{mem.id_mem}_{uuid.uuid4().hex[:8]}"
                            id2 = f"{mem.id_mem}_{uuid.uuid4().hex[:8]}"
                            r1 = add_multiset(base, v)
                            r2 = add_multiset(base, w)
                            # heredar reglas
                            child_rules = [deepcopy(r) for r in mem.reglas]
                            to_create.append((mem.parent, id1, r1, child_rules))
                            to_create.append((mem.parent, id2, r2, child_rules))
                        continue

                    # Consumo de objetos
                    consumo_total = multiset_times(regla.left, cnt)
                    recursos_disp = sub_multiset(recursos_disp, consumo_total)

                    # Producciones de objetos
                    for simb, num in regla.right.items():
                        if simb.endswith("_out"):
                            base_sym = simb[:-4]
                            padre_id = mem.parent
                            if padre_id:
                                producciones[padre_id][base_sym] = (
                                    producciones[padre_id].get(base_sym, 0) + num * cnt
                                )
                        elif "_in_" in simb:
                            base_sym, target = simb.split("_in_")
                            if target in sistema.skin:
                                producciones[target][base_sym] = (
                                    producciones[target].get(base_sym, 0) + num * cnt
                                )
                        else:
                            producciones[mem.id_mem][simb] = (
                                producciones[mem.id_mem].get(simb, 0) + num * cnt
                            )

                    # Creación y disolución etiquetadas
                    for _ in range(cnt):
                        for new_id, init_res in regla.create_membranes:
                            to_create.append((mem.id_mem, new_id, deepcopy(init_res)))
                        for dis_id in regla.dissolve_membranes:
                            to_dissolve.append(dis_id)

        consumos[mem.id_mem] = recursos_disp

    # Fase 2: aplicar producciones
    for mem_id, prod in producciones.items():
        base = consumos.get(mem_id, sistema.skin[mem_id].resources)
        sistema.skin[mem_id].resources = add_multiset(base, prod)

    # Fase 3: disoluciones
    root_id = sistema.output_membrane
    dissolved_list: List[str] = []
    for dis_id in to_dissolve:
        if dis_id == root_id or dis_id not in sistema.skin:
            continue
        padre_id = sistema.skin[dis_id].parent
        if padre_id:
            padre = sistema.skin[padre_id]
            heredados = sistema.skin[dis_id].resources
            padre.resources = add_multiset(padre.resources, heredados)
            for hijo_id in sistema.skin[dis_id].children:
                sistema.skin[hijo_id].parent = padre_id
                padre.children.append(hijo_id)
            padre.children.remove(dis_id)
        del sistema.skin[dis_id]
        dissolved_list.append(dis_id)

    # Fase 4: creaciones
    created_list: List[Tuple[str, str]] = []
    for entry in to_create:
        if len(entry) == 3:
            parent_id, new_id, res = entry
            # reglas de prototipo si existe
            rules = []
            if new_id in sistema.prototypes:
                rules = [deepcopy(r) for r in sistema.prototypes[new_id].reglas]
            nueva = Membrana(id_mem=new_id, resources=res, reglas=rules)
            sistema.add_membrane(nueva, parent_id)
            created_list.append((parent_id, new_id))
        else:
            parent_id, new_id, res, rules_list = entry
            nueva = Membrana(id_mem=new_id, resources=res, reglas=[deepcopy(r) for r in rules_list])
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
    rng_seed: Optional[int] = None,
    csv_path: Optional[str] = None
) -> pd.DataFrame:
    modo = "max_paralelo"
    all_results: List[LapsoResult] = []
    for i in range(lapsos):
        seed = None
        if rng_seed is not None:
            seed = rng_seed + i
        lapso_res = simular_lapso(sistema, rng_seed=seed)
        all_results.append(lapso_res)

    rows = []
    for idx_l, lapso in enumerate(all_results, start=1):
        cre_str = ";".join(f"{p}->{c}" for p, c in lapso.created) if lapso.created else ""
        dis_str = ";".join(lapso.dissolved) if lapso.dissolved else ""
        for mem_id in lapso.consumos:
            rec_rest = lapso.consumos.get(mem_id, {})
            prod = lapso.producciones.get(mem_id, {})
            apps = lapso.seleccionados.get(mem_id, [])
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
        print(df.to_csv(index=False))
    return df


def merge_systems(*systems: SistemaP, global_id: str = "global", output_membrane: Optional[str] = None) -> SistemaP:
    merged = SistemaP()
    global_mem = Membrana(id_mem=global_id, resources={}, reglas=[], children=[], parent=None)
    merged.add_membrane(global_mem)
    for idx, sys in enumerate(systems):
        mapping: Dict[str, str] = {}
        for old_id in sys.skin:
            mapping[old_id] = f"{global_id}_{idx}_{old_id}"
        for old_id, membrana in sys.skin.items():
            new_id = mapping[old_id]
            new_mem = Membrana(
                id_mem=new_id,
                resources=deepcopy(membrana.resources),
                reglas=[deepcopy(r) for r in membrana.reglas],
                children=[],
                parent=None
            )
            merged.skin[new_id] = new_mem
        for old_id, membrana in sys.skin.items():
            new_id = mapping[old_id]
            old_parent = membrana.parent
            if old_parent is None:
                parent_id = global_id
            else:
                parent_id = mapping.get(old_parent, global_id)
            merged.add_membrane(merged.skin[new_id], parent_id)
    if output_membrane:
        merged.output_membrane = output_membrane
    return merged
