import re
from typing import Dict, List, Tuple, Optional

from SistemaP import SistemaP, Membrana, Regla


def parse_multiset(s: str) -> Dict[str, int]:
    """
    Parsea una cadena de la forma 'a*2, b, c*3' en un diccionario {'a':2, 'b':1, 'c':3}.
    """
    result: Dict[str, int] = {}
    for part in re.split(r',\s*', s.strip()):
        if not part:
            continue
        m = re.match(r"(\w+)\s*(?:\*\s*(\d+))?", part)
        if not m:
            raise ValueError(f"Elemento de multiconjunto inválido: '{part}'")
        sym = m.group(1)
        cnt = int(m.group(2)) if m.group(2) else 1
        result[sym] = result.get(sym, 0) + cnt
    return result


def parse_mu(s: str) -> List[Tuple[str, Optional[str]]]:
    """
    Parsea la definición de estructura de membranas en notación de paréntesis anidados.
    Ejemplo: "[[[]'4]'2[[]'5]'3]'1"
    Devuelve lista de tuplas (mem_id, parent_id).
    """
    results: List[Tuple[str, Optional[str]]] = []

    def helper(start: int, parent: Optional[str]) -> int:
        # start apunta a '['
        assert s[start] == '[', "Se esperaba '[' en parse_mu"
        depth = 0
        # buscar ']' correspondiente
        for j in range(start, len(s)):
            if s[j] == '[':
                depth += 1
            elif s[j] == ']':
                depth -= 1
                if depth == 0:
                    end = j
                    break
        else:
            raise ValueError("No se encontró ']' de cierre para '[' en parse_mu")

        # leerID tras ']'
        k = end + 1
        while k < len(s) and s[k].isspace():
            k += 1
        if k >= len(s) or s[k] != "'":
            raise ValueError("Se esperaba apóstrofe y ID tras ']' en parse_mu")
        k += 1
        m = k
        while m < len(s) and s[m].isalnum():
            m += 1
        mem_id = s[k:m]
        results.append((mem_id, parent))

        # recorrer hijos dentro de [start+1:end]
        i = start + 1
        while i < end:
            if s[i] == '[':
                # parse hijo recursivamente
                i = helper(i, mem_id)
            else:
                i += 1
        return m  # devolver índice posterior al ID

    # arrancar desde el primer '['
    helper(0, None)
    return results


def leerSistema(path: str) -> SistemaP:
    """
    Lee un archivo .pli y devuelve un SistemaP inicializado.
    Se esperan secciones:
      - @mu = ...;
      - @ms(i) = ...;
      - [L --> R] 'm;
    """
    text = ''
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()

    # eliminar comentarios /* ... */
    text = re.sub(r'/\*[\s\S]*?\*/', '', text)

    # parsear estructura
    mu_match = re.search(r'@mu\s*=\s*(.+?);', text)
    if not mu_match:
        raise ValueError("No se encontró la definición @mu en el archivo .pli")
    mu_str = mu_match.group(1).strip()
    mem_list = parse_mu(mu_str)

    sistema = SistemaP()
    # crear membranas (recursos vacíos)
    for mem_id, parent in mem_list:
        mem = Membrana(mem_id, {})
        sistema.agregar_membrana(mem, parent)

    # parsear multisets
    for match in re.finditer(r'@ms\(\s*(\d+)\s*\)\s*=\s*(.+?);', text):
        mem_id = match.group(1)
        ms_str = match.group(2)
        recursos = parse_multiset(ms_str)
        mem = sistema.obtener_membrana(mem_id)
        if not mem:
            raise ValueError(f"Membrana {mem_id} no definida en estructura @mu")
        mem.recursos = recursos

    # parsear reglas
    rule_pat = r'\[(.+?)-->\s*(.+?)\]\s*\'(\d+);'
    for rm in re.finditer(rule_pat, text):
        left_str = rm.group(1).strip()
        right_str = rm.group(2).strip()
        mem_id = rm.group(3)

        izquierda = parse_multiset(left_str)
        # procesar derecha ignorando paréntesis (out/in)
        symbols = re.findall(r"(\w+)(?:\s*\([^)]*\))?", right_str)
        derecha: Dict[str, int] = {}
        for sym in symbols:
            derecha[sym] = derecha.get(sym, 0) + 1

        regla = Regla(izquierda, derecha, prioridad=0)
        mem = sistema.obtener_membrana(mem_id)
        if not mem:
            raise ValueError(f"Regla asignada a membrana desconocida {mem_id}")
        mem.agregar_regla(regla)

    return sistema
