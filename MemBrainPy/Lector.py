# Lector.py

"""
Lector.py

Módulo profesional para leer archivos .pli siguiendo la sintaxis de P-Lingua
y construir un objeto SistemaP con membranas, recursos y reglas.
"""

import re
from typing import Dict, List, Tuple, Optional
from .SistemaP import SistemaP, Membrana, Regla

__all__ =["leer_sistema"]

def parse_multiset(s: str) -> Dict[str, int]:
    """
    Parsea una cadena de multiconjunto de P-Lingua, por ejemplo:
        "a*2, b c, d*3"
    Retorna un diccionario {'a': 2, 'b': 1, 'c': 1, 'd': 3}.
    Acepta separadores por comas o espacios.
    """
    conteo: Dict[str, int] = {}
    for part in re.split(r'[,\s]+', s.strip()):
        if not part:
            continue
        m = re.fullmatch(r"(\w+)\s*(?:\*\s*(\d+))?", part)
        if not m:
            raise ValueError(f"Elemento de multiconjunto inválido: '{part}'")
        simbolo = m.group(1)
        cantidad = int(m.group(2)) if m.group(2) else 1
        conteo[simbolo] = conteo.get(simbolo, 0) + cantidad
    return conteo


def parse_structure(s: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parsea la sección @mu de P-Lingua, que define la jerarquía de membranas
    en notación de corchetes anidados con apóstrofes para IDs.
    Ejemplo: "[[[]'4]'2[[]'5]'3]'1"
    Retorna lista de tuplas (mem_id, parent_id), donde parent_id = None para la piel.
    Lanza ValueError si la sintaxis es incorrecta o hay corchetes desbalanceados.
    """
    result: List[Tuple[str, Optional[str]]] = []

    def helper(idx: int, parent: Optional[str]) -> int:
        if idx >= len(s) or s[idx] != '[':
            raise ValueError(f"Se esperaba '[', pero se encontró '{s[idx]}' en posición {idx}")
        depth = 0
        for j in range(idx, len(s)):
            if s[j] == '[':
                depth += 1
            elif s[j] == ']':
                depth -= 1
                if depth == 0:
                    close_idx = j
                    break
        else:
            raise ValueError("Corchetes '[' y ']' desbalanceados en parse_structure")

        # Tras ']', debe venir apóstrofe seguido del ID alfanumérico
        k = close_idx + 1
        while k < len(s) and s[k].isspace():
            k += 1
        if k >= len(s) or s[k] != "'":
            raise ValueError(f"Se esperaba apóstrofe tras ']' en posición {close_idx}")
        k += 1
        start_id = k
        while k < len(s) and s[k].isalnum():
            k += 1
        if start_id == k:
            raise ValueError(f"ID de membrana vacío en parse_structure cerca de índice {start_id}")
        mem_id = s[start_id:k]
        result.append((mem_id, parent))

        # Procesar contenido interno [idx+1:close_idx] en busca de hijos
        i = idx + 1
        while i < close_idx:
            if s[i] == '[':
                i = helper(i, mem_id)
            else:
                i += 1
        return k  # posición posterior al ID

    pos0 = s.find('[')
    if pos0 == -1:
        raise ValueError("No se encontró '[' inicial en la definición @mu")
    helper(pos0, None)
    return result


def parse_rules(s: str) -> List[Tuple[str, Dict[str, int], Dict[str, int], int]]:
    """
    Parsea todas las reglas en el texto dado, con la sintaxis:
        [L --> R (: prioridad)? ]'<mem_id>';
    donde L y R son multiconjuntos (R puede incluir sufijos (out) o (in <dest>)).
    Retorna lista de tuplas:
        (mem_id, izquierda_dict, derecha_dict, prioridad)
    Lanza ValueError si alguna regla no coincide con el patrón esperado.
    """
    rules: List[Tuple[str, Dict[str, int], Dict[str, int], int]] = []

    # Patrón para capturar: [ L --> R (opcional :n) ] 'id';
    regla_pat = re.compile(
        r'\[\s*(.+?)\s*-->\s*(.+?)(?:\s*:\s*(\d+))?\s*\]\s*\'\s*(\w+)\s*\'\s*;'
    )

    for m in regla_pat.finditer(s):
        left_str = m.group(1).strip()
        right_str = m.group(2).strip()
        prio_str = m.group(3)
        mem_id = m.group(4).strip()

        izquierda = parse_multiset(left_str)

        # Procesar lado derecho con sufijos (out) o (in <dest>)
        derecha: Dict[str, int] = {}
        # Usar finditer para capturar cada símbolo + sufijo + multiplicador
        pattern_r = re.compile(
            r'(\w+)'                                  # símbolo base
            r'(?:\s*\(\s*(out)\s*\)|\s*\(\s*in\s+(\w+)\s*\))?'  # opcional "(out)" o "(in X)"
            r'(?:\*\s*(\d+))?'                        # opcional "*n"
        )
        for mm in pattern_r.finditer(right_str):
            simb = mm.group(1)
            suf_out = mm.group(2)
            suf_in = mm.group(3)
            mult = int(mm.group(4)) if mm.group(4) else 1

            if suf_out:
                simb_full = f"{simb}_out"
            elif suf_in:
                simb_full = f"{simb}_in_{suf_in}"
            else:
                simb_full = simb

            derecha[simb_full] = derecha.get(simb_full, 0) + mult

        prioridad = int(prio_str) if prio_str else 1
        rules.append((mem_id, izquierda, derecha, prioridad))

    return rules


def leer_sistema(path: str) -> SistemaP:
    """
    Lee un archivo .pli siguiendo la sintaxis de P-Lingua y construye un SistemaP.
    Se esperan tres secciones (en cualquier orden):
      1) @mu = <estructura>;          // define membranas y anidamiento
      2) @ms(<id>) = <multiconjunto>;  // recursos iniciales
      3) [L --> R(: prioridad)?]'id';   // reglas asociadas a membrana <id>

    También ignora encabezados como "@model<…>" y bloque "def main() { … }".

    Args:
        path: ruta al archivo .pli.

    Retorna:
        SistemaP con membranas, recursos y reglas cargados.

    Lanza:
        ValueError si falta alguna sección o hay sintaxis incorrecta.
    """
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()

    # 1) Eliminar comentarios /* ... */
    raw = re.sub(r'/\*[\s\S]*?\*/', '', raw)

    # 2) Si existe "def main() { ... }", extraer contenido interior
    main_block = re.search(r'def\s+main\s*\(\)\s*\{([\s\S]*)\}', raw)
    text = main_block.group(1) if main_block else raw

    # ===== Parsear sección @mu =====
    mu_match = re.search(r'@mu\s*=\s*(.+?);', text)
    if not mu_match:
        raise ValueError("No se encontró la definición @mu en el archivo .pli")
    mu_str = mu_match.group(1).strip()
    structure = parse_structure(mu_str)

    sistema = SistemaP(output_membrane=None)
    # Crear membranas con recursos vacíos inicialmente
    for mem_id, parent_id in structure:
        membrana = Membrana(id_mem=mem_id, resources={})
        sistema.add_membrane(membrana, parent_id)

    # ===== Parsear recursos @ms(id) =====
    ms_pat = re.compile(r'@ms\s*\(\s*(\w+)\s*\)\s*=\s*(.+?);')
    for m in ms_pat.finditer(text):
        mem_id = m.group(1).strip()
        ms_str = m.group(2).strip()
        recursos = parse_multiset(ms_str)
        if mem_id not in sistema.skin:
            raise ValueError(f"Membrana '{mem_id}' en @ms no definida en @mu")
        sistema.skin[mem_id].resources = recursos

    # ===== Parsear reglas =====
    reglas_parsed = parse_rules(text)
    for mem_id, izquierda, derecha, prioridad in reglas_parsed:
        if mem_id not in sistema.skin:
            raise ValueError(f"Regla asignada a membrana desconocida '{mem_id}'")
        regla = Regla(left=izquierda, right=derecha, priority=prioridad)
        sistema.skin[mem_id].add_regla(regla)

    return sistema
