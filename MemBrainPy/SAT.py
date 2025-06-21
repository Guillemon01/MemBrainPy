"""
Módulo SAT.py

Provee herramientas para:
  1. Definir y parsear expresiones booleanas.
  2. Configurar interactivamente una expresión vía GUI.
  3. Traducir una fórmula booleana a un P-sistema SAT jerárquico.
  4. Resolver satisfacibilidad simulando el P-sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from copy import deepcopy
from typing import List, Dict, Optional

from .SistemaP import SistemaP, Membrana, Regla, simular_lapso
from .SistemaP import (
    SistemaP,
    Membrana,
    Regla,
    Production,
    Direction
)
# ----------------------------------------------------------------------
# 1. AST para expresiones booleanas
# ----------------------------------------------------------------------

class ExpresionBooleana:
    def __str__(self) -> str: ...
    def to_cnf(self) -> 'ExpresionBooleana': ...
    def obtener_clausulas(self) -> List[List[str]]: ...

class Variable(ExpresionBooleana):
    def __init__(self, nombre: str):
        self.nombre = nombre
    def __str__(self) -> str:
        return self.nombre
    def to_cnf(self) -> 'ExpresionBooleana':
        return self
    def obtener_clausulas(self) -> List[List[str]]:
        return [[self.nombre]]

class Negacion(ExpresionBooleana):
    def __init__(self, operando: ExpresionBooleana):
        self.operando = operando
    def __str__(self) -> str:
        if isinstance(self.operando, Variable):
            return f"~{self.operando}"
        return f"~({self.operando})"
    def to_cnf(self) -> 'ExpresionBooleana':
        op = self.operando
        if isinstance(op, Negacion):
            return op.operando.to_cnf()
        if isinstance(op, Conjuncion):
            return Disyuncion(Negacion(op.left), Negacion(op.right)).to_cnf()
        if isinstance(op, Disyuncion):
            return Conjuncion(Negacion(op.left), Negacion(op.right)).to_cnf()
        return self
    def obtener_clausulas(self) -> List[List[str]]:
        return [[f"~{self.operando.nombre}"]]

class Conjuncion(ExpresionBooleana):
    def __init__(self, left: ExpresionBooleana, right: ExpresionBooleana):
        self.left, self.right = left, right
    def __str__(self) -> str:
        return f"({self.left} & {self.right})"
    def to_cnf(self) -> 'ExpresionBooleana':
        return Conjuncion(self.left.to_cnf(), self.right.to_cnf())
    def obtener_clausulas(self) -> List[List[str]]:
        return self.left.obtener_clausulas() + self.right.obtener_clausulas()

class Disyuncion(ExpresionBooleana):
    def __init__(self, left: ExpresionBooleana, right: ExpresionBooleana):
        self.left, self.right = left, right
    def __str__(self) -> str:
        return f"({self.left} | {self.right})"
    def to_cnf(self) -> 'ExpresionBooleana':
        L = self.left.to_cnf()
        R = self.right.to_cnf()
        if isinstance(L, Conjuncion):
            return Conjuncion(
                Disyuncion(L.left, R).to_cnf(),
                Disyuncion(L.right, R).to_cnf()
            )
        if isinstance(R, Conjuncion):
            return Conjuncion(
                Disyuncion(L, R.left).to_cnf(),
                Disyuncion(L, R.right).to_cnf()
            )
        return Disyuncion(L, R)
    def obtener_clausulas(self) -> List[List[str]]:
        lits: List[str] = []
        def recoger(e: ExpresionBooleana):
            if isinstance(e, Disyuncion):
                recoger(e.left); recoger(e.right)
            elif isinstance(e, Variable):
                lits.append(e.nombre)
            elif isinstance(e, Negacion) and isinstance(e.operando, Variable):
                lits.append(f"~{e.operando.nombre}")
            else:
                raise ValueError("Literal no válido en cláusula")
        recoger(self)
        return [lits]

# ----------------------------------------------------------------------
# 2. Parser recursivo con sintaxis (~, &, |, not, and, or)
# ----------------------------------------------------------------------

class AnalizadorExpresion:
    TOKEN_SPEC = [
        ('NOT',    r'(~|!|not\b)'),
        ('AND',    r'(\&\&?|\band\b)'),
        ('OR',     r'(\|\|?|\bor\b)'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('VAR',    r'[A-Za-z][A-Za-z0-9_]*'),
        ('SPACE',  r'\s+'),
    ]
    def __init__(self, texto: str):
        pattern = '|'.join(f'(?P<{n}>{r})' for n,r in self.TOKEN_SPEC)
        self.tokens = [
            m for m in re.finditer(pattern, texto, flags=re.IGNORECASE)
            if m.lastgroup != 'SPACE'
        ]
        self.pos = 0

    def _peek(self):
        return (self.tokens[self.pos].lastgroup,
                self.tokens[self.pos].group()) \
            if self.pos < len(self.tokens) else None

    def _next(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def parse(self) -> ExpresionBooleana:
        expr = self._parse_or()
        if self.pos != len(self.tokens):
            raise ValueError("Texto restante tras parsear")
        return expr

    def _parse_or(self):
        node = self._parse_and()
        while True:
            tk = self._peek()
            if tk and tk[0]=='OR':
                self._next()
                node = Disyuncion(node, self._parse_and())
            else:
                break
        return node

    def _parse_and(self):
        node = self._parse_not()
        while True:
            tk = self._peek()
            if tk and tk[0]=='AND':
                self._next()
                node = Conjuncion(node, self._parse_not())
            else:
                break
        return node

    def _parse_not(self):
        tk = self._peek()
        if tk and tk[0]=='NOT':
            self._next()
            return Negacion(self._parse_not())
        return self._parse_atom()

    def _parse_atom(self):
        tk = self._peek()
        if not tk:
            raise ValueError("Se esperaba variable o '('")
        if tk[0]=='VAR':
            _, v = self._next()
            return Variable(v)
        if tk[0]=='LPAREN':
            self._next()
            node = self._parse_or()
            if not (self._peek() and self._peek()[0]=='RPAREN'):
                raise ValueError("Falta ')'")
            self._next()
            return node
        raise ValueError(f"Token inesperado: {tk}")

# ----------------------------------------------------------------------
# 3. GUI para introducir la expresión, con guía de sintaxis
# ----------------------------------------------------------------------

class ConfiguradorExpresionBooleana(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configurar Expresión Booleana")
        self.resizable(False, False)

        texto_guia = (
            "Sintaxis aceptada:\n"
            " - Variables: letras, dígitos y '_', e.g. A, x1, var_name\n"
            " - Negación: '~' o 'not'    (ej. ~A o not A)\n"
            " - Conjunción: '&' o 'and'   (ej. A&B o A and B)\n"
            " - Disyunción: '|' o 'or'    (ej. A|B o A or B)\n"
            " - Paréntesis: '(' y ')'\n"
            "Ejemplo:\n  ~(A & B) | (C and not D) & (x1 or ~y2)\n"
        )
        ttk.Label(self, text=texto_guia, justify='left')\
           .grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(self, text="Fórmula:").grid(row=1, column=0, sticky='e', padx=5)
        self.entry = ttk.Entry(self, width=50)
        self.entry.grid(row=1, column=1, sticky='w', padx=5)

        ttk.Button(self, text="Aceptar", command=self._on_accept)\
           .grid(row=2, column=0, columnspan=2, pady=10)

        self.result: Optional[ExpresionBooleana] = None

    def _on_accept(self):
        texto = self.entry.get().strip()
        try:
            self.result = AnalizadorExpresion(texto).parse()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error de parseo", str(e))

def configurar_expresion_booleana() -> Optional[ExpresionBooleana]:
    app = ConfiguradorExpresionBooleana()
    app.mainloop()
    return app.result

# ----------------------------------------------------------------------
# 4. Generación de P-sistema SAT jerárquico
# ----------------------------------------------------------------------

import itertools
from typing import List, Dict, Tuple
from .SistemaP import SistemaP, Membrana, Regla, Production, Direction
from .SAT import ExpresionBooleana, Variable, Negacion, Conjuncion, Disyuncion

def generar_sistema_por_estructura(
    expr: ExpresionBooleana,
    output_membrane: str = "M_root"
) -> SistemaP:
    """
    Genera un P-sistema en el que cada membrana de asignación contiene
    la codificación completa de la expresión booleana expr en forma de reglas
    y simula su evaluación bajo esa asignación.
    """
    # 1. Recorrer el árbol de la expresión para asignar IDs a nodos
    node_children: Dict[str, Tuple[str, ...]] = {}
    node_type: Dict[str, str] = {}
    node_var: Dict[str, str] = {}
    counter = {"i": 0}

    def build(node: ExpresionBooleana) -> str:
        i = counter["i"]
        nid = f"n{i}"
        counter["i"] += 1
        if isinstance(node, Variable):
            node_type[nid] = 'var'
            node_var[nid] = node.nombre
            node_children[nid] = ()
        elif isinstance(node, Negacion):
            child = build(node.operando)
            node_type[nid] = 'not'
            node_children[nid] = (child,)
        elif isinstance(node, Conjuncion):
            left = build(node.left)
            right = build(node.right)
            node_type[nid] = 'and'
            node_children[nid] = (left, right)
        elif isinstance(node, Disyuncion):
            left = build(node.left)
            right = build(node.right)
            node_type[nid] = 'or'
            node_children[nid] = (left, right)
        else:
            raise ValueError(f"Nodo desconocido: {node}")
        return nid

    # Construir nodos y determinar root_id
    root_id = build(expr)

    # 2. Crear sistema y membrana raíz
    sistema = SistemaP()
    root_mem = Membrana(id_mem=output_membrane, resources={})
    sistema.add_membrane(root_mem, parent_id=None)
    sistema.output_membrane = output_membrane

    # 3. Extraer variables únicas y ordenadas
    variables = sorted({v for v in node_var.values()})
    n = len(variables)

    # 4. Por cada asignación booleana, crear membrana y reglas de evaluación
    for bits in itertools.product([False, True], repeat=n):
        assign_id = f"assign_{''.join('1' if b else '0' for b in bits)}"
        # recursos iniciales de la asignación
        res = {f"{var}_{'T' if val else 'F'}": 1 for var, val in zip(variables, bits)}
        mem = Membrana(id_mem=assign_id, resources=res)
        sistema.add_membrane(mem, parent_id=output_membrane)

        # 4.1. Reglas de variables -> generan nodo_T o nodo_F
        for nid, typ in node_type.items():
            if typ == 'var':
                var = node_var[nid]
                # true
                mem.add_regla(Regla(
                    left={f"{var}_T": 1},
                    productions=[Production(symbol=f"{nid}_T", count=1)],
                    priority=1
                ))
                # false
                mem.add_regla(Regla(
                    left={f"{var}_F": 1},
                    productions=[Production(symbol=f"{nid}_F", count=1)]
                ))

        # 4.2. Reglas de operadores
        for nid, typ in node_type.items():
            children = node_children[nid]
            if typ == 'not':
                c = children[0]
                # si child es true -> result false
                mem.add_regla(Regla(
                    left={f"{c}_T": 1},
                    productions=[Production(symbol=f"{nid}_F", count=1)]
                ))
                # si child es false -> result true
                mem.add_regla(Regla(
                    left={f"{c}_F": 1},
                    productions=[Production(symbol=f"{nid}_T", count=1)],
                    priority=1
                ))
            elif typ == 'and':
                c1, c2 = children
                # ambos true -> true
                mem.add_regla(Regla(
                    left={f"{c1}_T": 1, f"{c2}_T": 1},
                    productions=[Production(symbol=f"{nid}_T", count=1)],
                    priority=1
                ))
                # cualquiera false -> false
                mem.add_regla(Regla(
                    left={f"{c1}_F": 1},
                    productions=[Production(symbol=f"{nid}_F", count=1)]
                ))
                mem.add_regla(Regla(
                    left={f"{c2}_F": 1},
                    productions=[Production(symbol=f"{nid}_F", count=1)]
                ))
            elif typ == 'or':
                c1, c2 = children
                # cualquiera true -> true
                mem.add_regla(Regla(
                    left={f"{c1}_T": 1},
                    productions=[Production(symbol=f"{nid}_T", count=1)],
                    priority=1
                ))
                mem.add_regla(Regla(
                    left={f"{c2}_T": 1},
                    productions=[Production(symbol=f"{nid}_T", count=1)],
                    priority=1
                ))
                # ambos false -> false
                mem.add_regla(Regla(
                    left={f"{c1}_F": 1, f"{c2}_F": 1},
                    productions=[Production(symbol=f"{nid}_F", count=1)]
                ))

        # 4.3. Regla final: si root es true, emite sat
        mem.add_regla(Regla(
            left={f"{root_id}_T": 1},
            productions=[Production(symbol="sat", count=1, direction=Direction.OUT)],
            priority=2
        ))
        # opcional: si root es false, emite unsat
        mem.add_regla(Regla(
            left={f"{root_id}_F": 1},
            productions=[Production(symbol="unsat", count=1, direction=Direction.OUT)]
        ))

    return sistema





def resolver_satisfaccion(
    expr: ExpresionBooleana,
    max_pasos: int = 20
) -> bool:
    """
    Simula el sistema generado por generar_sistema_por_estructura,
    y devuelve True si la membrana de salida contiene 'sat'.
    """
    sistema = generar_sistema_por_estructura(expr)
    copia   = deepcopy(sistema)
    for _ in range(max_pasos):
        simular_lapso(copia)
        if "sat" in copia.skin[copia.output_membrane].resources:
            return True
    # Si no se decide tras max_pasos, lo damos por insat.
    return False

# ----------------------------------------------------------------------
# Ejecución directa
# ----------------------------------------------------------------------

if __name__ == "__main__":
    expr = configurar_expresion_booleana()
    if expr:
        print("Expresión parseada:", expr)
        print("¿Satisfacible?", resolver_satisfaccion(expr))
