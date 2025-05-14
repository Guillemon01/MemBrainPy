from copy import deepcopy
from typing import Dict, List, Optional, Tuple
import random

# -- Clases básicas --
class Regla:
    def __init__(
        self,
        izquierda: Dict[str, int],
        derecha: Dict[str, int],  # claves: símbolo, símbolo_out, símbolo_in_<id>
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

    def __repr__(self):
        return (
            f"Regla(izq={self.izquierda}, der={self.derecha}, pri={self.prioridad}, "
            f"crea={self.crea_membranas}, dis={self.disuelve_membranas})"
        )

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
        return f"Membrana(id={self.id}, rec={self.recursos}, hijos={self.hijos})"

class SistemaP:
    def __init__(self):
        self.piel: Dict[str, Membrana] = {}

    def agregar_membrana(self, membrana: Membrana, parent_id: Optional[str] = None):
        membrana.padre = parent_id
        self.piel[membrana.id] = membrana
        if parent_id:
            self.piel[parent_id].hijos.append(membrana.id)

    def __repr__(self):
        return f"SistemaP({list(self.piel.keys())})"

# -- Funciones de multiconjuntos y aplicabilidad --

def union_multiconjuntos(ms1: Dict[str,int], ms2: Dict[str,int]) -> Dict[str,int]:
    out = ms1.copy()
    for k,v in ms2.items(): out[k] = out.get(k,0) + v
    return out


def resta_multiconjuntos(ms: Dict[str,int], rest: Dict[str,int]) -> Dict[str,int]:
    out = ms.copy()
    for k,v in rest.items(): out[k] = out.get(k,0) - v
    return {k:v for k,v in out.items() if v>0}


def veces_aplicable(rec: Dict[str,int], reg: Regla) -> int:
    m = float('inf')
    for k,v in reg.izquierda.items(): m = min(m, rec.get(k,0)//v)
    return 0 if m==float('inf') else m


def multiplicar_multiconjunto(ms: Dict[str,int], veces: int) -> Dict[str,int]:
    return {k: v*veces for k,v in ms.items()}

# -- Generación de maximales --

def generar_maximales(reglas: List[Regla], recursos: Dict[str,int]) -> List[List[Tuple[Regla,int]]]:
    maximales: List[List[Tuple[Regla,int]]] = []
    def backtrack(start:int, rec:Dict[str,int], sel:List[Tuple[Regla,int]]):
        for i in range(start, len(reglas)):
            r = reglas[i]
            maxv = veces_aplicable(rec, r)
            for cnt in range(1, maxv+1):
                cons = multiplicar_multiconjunto(r.izquierda, cnt)
                new_rec = resta_multiconjuntos(rec, cons)
                sel.append((r, cnt))
                backtrack(i+1, new_rec, sel)
                sel.pop()
        # comprobación de maximalidad global
        if all(veces_aplicable(rec, r)==0 for r in reglas):
            maximales.append(sel.copy())
    backtrack(0, recursos, [])
    return maximales

# -- Simulación de un lapso con direccionamiento in/out --

def simular_lapso(sistema: SistemaP, modo: str = "max_paralelo") -> None:
    producciones: Dict[str, Dict[str,int]] = {mid:{} for mid in sistema.piel}
    consumos: Dict[str, Dict[str,int]]    = {}
    to_create: List[Tuple[str,str]]      = []
    to_dissolve: List[str]               = []

    for mem in list(sistema.piel.values()):
        rec_disp = deepcopy(mem.recursos)
        # calcular aplicables y priorizar
        aplic = [r for r in mem.reglas if veces_aplicable(rec_disp,r)>0]
        if modo=="secuencial":
            # ... (igual que antes) omitido aquí ...
            pass
        # modo max_paralelo
        if modo=="max_paralelo" and aplic:
            mp = max(r.prioridad for r in aplic)
            top = [r for r in aplic if r.prioridad==mp]
            maxs = generar_maximales(top, rec_disp)
            if maxs:
                random.shuffle(maxs)
                elegido = maxs[0]
                for r,cnt in elegido:
                    # consumo
                    cons = multiplicar_multiconjunto(r.izquierda, cnt)
                    rec_disp = resta_multiconjuntos(rec_disp, cons)
                    # producción con direccionamiento
                    for simb, num in r.derecha.items():
                        # out
                        if simb.endswith("_out"):
                            base = simb[:-4]
                            padre = mem.padre
                            if padre:
                                producciones[padre][base] = producciones[padre].get(base,0) + num*cnt
                        # in_j
                        elif "_in_" in simb:
                            base, target = simb.split("_in_")
                            producciones[target][base] = producciones[target].get(base,0) + num*cnt
                        # default (sin sufijo): queda aquí
                        else:
                            producciones[mem.id][simb] = producciones[mem.id].get(simb,0) + num*cnt
                    # crea / disuelve
                    for _ in range(cnt):
                        for nid in r.crea_membranas:   to_create.append((mem.id,nid))
                        for did in r.disuelve_membranas: to_dissolve.append(did)
        # recursos restantes
        consumos[mem.id] = rec_disp.copy()

    # sincronizar recursos y producciones
    for mid, prod in producciones.items():
        base = consumos.get(mid, sistema.piel[mid].recursos)
        sistema.piel[mid].recursos = union_multiconjuntos(base, prod)
    # disoluciones
    for did in to_dissolve:
        if did in sistema.piel:
            p = sistema.piel[did].padre
            if p:
                padre = sistema.piel[p]
                padre.recursos = union_multiconjuntos(padre.recursos, sistema.piel[did].recursos)
                # reubicar hijas
                for c in sistema.piel[did].hijos:
                    sistema.piel[c].padre = p; padre.hijos.append(c)
                padre.hijos.remove(did)
            del sistema.piel[did]
    # creaciones
    for par, nid in to_create:
        if nid not in sistema.piel:
            sistema.agregar_membrana(Membrana(nid,{}), par)
