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

def generar_sistema_por_estructura(
    expr: ExpresionBooleana,
    output_membrane: str = "M_root"
) -> SistemaP:
    sistema = SistemaP()

    # 1) Raíz con token de arranque
    raiz = Membrana(
        id_mem=output_membrane,
        resources={f"go_{output_membrane}": 1}
    )
    sistema.add_membrane(raiz, None)
    sistema.output_membrane = output_membrane

    cont = {"VAR":0, "AND":0, "OR":0}
    protos: Dict[str, Membrana] = {}

    def build(nodo) -> str:
        # nombres legibles para cada tipo de nodo
        if isinstance(nodo, Variable):
            key = f"VAR_{nodo.nombre}"
        elif isinstance(nodo, Conjuncion):
            cont["AND"] += 1
            key = f"AND_{cont['AND']}"
        else:  # Disyuncion
            cont["OR"] += 1
            key = f"OR_{cont['OR']}"

        if key in protos:
            return key

        proto = Membrana(id_mem=key, resources={})
        go = f"go_{key}"

        if isinstance(nodo, Variable):
            # división variable → T/F
            proto.reglas.append(Regla(
                left={go:1}, right={}, priority=1,
                division=(
                    {f"{key}_T":1},
                    {f"{key}_F":1}
                )
            ))
        else:
            # construir hijos
            L = build(nodo.left)
            R = build(nodo.right)
            proto.reglas.append(Regla(
                left={go:1}, right={}, priority=1,
                create_membranes=[
                    (L, {f"go_{L}":1}),
                    (R, {f"go_{R}":1})
                ]
            ))
            # poda/evaluación local
            if isinstance(nodo, Conjuncion):
                proto.reglas.append(Regla(
                    left={f"{L}_F":1}, right={f"{key}_F":1}, priority=0
                ))
                proto.reglas.append(Regla(
                    left={f"{R}_F":1}, right={f"{key}_F":1}, priority=0
                ))
                proto.reglas.append(Regla(
                    left={f"{L}_T":1, f"{R}_T":1},
                    right={f"{key}_T":1}, priority=-1
                ))
            else:
                proto.reglas.append(Regla(
                    left={f"{L}_T":1}, right={f"{key}_T":1}, priority=0
                ))
                proto.reglas.append(Regla(
                    left={f"{R}_T":1}, right={f"{key}_T":1}, priority=0
                ))
                proto.reglas.append(Regla(
                    left={f"{L}_F":1, f"{R}_F":1},
                    right={f"{key}_F":1}, priority=-1
                ))

        sistema.register_prototype(proto)
        protos[key] = proto
        return key

    # 2) Montar toda la jerarquía
    root_key = build(expr)
    raiz.reglas.append(Regla(
        left={f"go_{output_membrane}":1}, right={}, priority=1,
        create_membranes=[(root_key, {f"go_{root_key}":1})]
    ))

    # 3) Reglas en la raíz que reconocen el resultado movido desde el hijo
    raiz.reglas.append(Regla(
        left={f"{root_key}_T":1}, right={"sat":1}, priority=0
    ))
    raiz.reglas.append(Regla(
        left={f"{root_key}_F":1}, right={"unsat":1}, priority=0
    ))

    return sistema


def resolver_satisfaccion(
    expr: ExpresionBooleana,
    max_pasos: int = 20
) -> bool:
    sistema = generar_sistema_por_estructura(expr)
    copia   = deepcopy(sistema)
    root_id = copia.output_membrane

    for _ in range(max_pasos):
        simular_lapso(copia)
        res = copia.skin[root_id].resources
        if res.get("sat", 0) > 0:
            return True
        if res.get("unsat", 0) > 0:
            return False

    return False

# ----------------------------------------------------------------------
# Ejecución directa
# ----------------------------------------------------------------------

if __name__ == "__main__":
    expr = configurar_expresion_booleana()
    if expr:
        print("Expresión parseada:", expr)
        print("¿Satisfacible?", resolver_satisfaccion(expr))
