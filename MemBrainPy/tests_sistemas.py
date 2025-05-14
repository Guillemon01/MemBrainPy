import random
from SistemaP import SistemaP, Membrana, Regla


def sistema_basico(recursos: dict = None, num_reglas: int = None) -> SistemaP:
    """
    Crea un sistema P muy simple con una única membrana y reglas sencillas.
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"a": random.randint(5, 8), "b": random.randint(3, 5)}
    m1 = Membrana("m1", recursos)
    # Regla 1: consume {"a": 2, "b": 1} y produce {"c": 1}, prioridad 2
    m1.agregar_regla(Regla({"a": 2, "b": 1}, {"c": 1}, prioridad=2))
    # Regla 2: consume {"a": 1} y produce {"b": 2}, prioridad 1
    if num_reglas is None or num_reglas > 1:
        m1.agregar_regla(Regla({"a": 1}, {"b": 2}, prioridad=1))
    # Opcional: regla de creación de membrana nueva
    if random.random() < 0.5:
        new_id = f"m_new_{random.randint(2, 10)}"
        m1.agregar_regla(Regla({"a": 1}, {}, prioridad=1, crea_membranas=[new_id]))
    sistema.agregar_membrana(m1)
    return sistema


def sistema_aniado(recursos: dict = None, num_membranas: int = None, anidacion_max: int = None) -> SistemaP:
    """
    Crea un sistema P con membranas anidadas.
    Ahora también puede generar reglas que disuelven membranas hijas.
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"a": random.randint(5, 8), "b": random.randint(3, 5)}
    if num_membranas is None:
        num_membranas = random.randint(2, 4)
    if anidacion_max is None:
        anidacion_max = random.randint(2, 3)

    # Crear la membrana top-level
    top_mem = Membrana("m1", recursos)
    top_mem.agregar_regla(Regla({"a": 2}, {"c": 1}, prioridad=2))
    sistema.agregar_membrana(top_mem)

    # Lista de tuplas (membrana, nivel)
    membranas_info = [(top_mem, 1)]

    # Crear membranas adicionales
    for i in range(2, num_membranas + 1):
        candidatos = [(m, lvl) for (m, lvl) in membranas_info if lvl < anidacion_max]
        if not candidatos:
            break
        parent, parent_level = random.choice(candidatos)
        new_id = f"m{i}"
        nuevos_recursos = {"a": random.randint(3, 7), "b": random.randint(2, 5)}
        nueva_mem = Membrana(new_id, nuevos_recursos)
        nueva_mem.agregar_regla(Regla({"a": 1}, {"b": 1}, prioridad=1))
        sistema.agregar_membrana(nueva_mem, parent.id)
        membranas_info.append((nueva_mem, parent_level + 1))

    # Opcional: regla de disolución de una de las hijas del top-level
    if top_mem.hijos:
        dis_id = random.choice(top_mem.hijos)
        top_mem.agregar_regla(Regla({"b": 1}, {}, prioridad=1, disuelve_membranas=[dis_id]))

    return sistema


def sistema_con_conflictos(recursos: dict = None) -> SistemaP:
    """
    Crea un sistema P en el que existen conflictos de recursos entre las reglas.
    Ahora también puede generar reglas que crean membranas.
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"x": random.randint(5, 8)}
    m1 = Membrana("m1", recursos)
    # Regla 1: consume {"x": 3} y produce {"y": 1}, prioridad 1
    m1.agregar_regla(Regla({"x": 3}, {"y": 1}, prioridad=1))
    # Regla 2: consume {"x": 2} y produce {"z": 1}, prioridad 1
    m1.agregar_regla(Regla({"x": 2}, {"z": 1}, prioridad=1))
    # Regla conflictiva adicional
    m1.agregar_regla(Regla({"x": 1}, {"w": 2}, prioridad=1))
    # Opcional: regla de creación de membrana nueva
    if random.random() < 0.5:
        new_id = f"m_new_{random.randint(2, 10)}"
        m1.agregar_regla(Regla({"x": 1}, {}, prioridad=1, crea_membranas=[new_id]))
    sistema.agregar_membrana(m1)
    return sistema

def sistema_demo_max_paralelo() -> SistemaP:
    sistema = SistemaP()
    # Configuración determinística para asegurar múltiples maximales
    recursos = {'a': 3, 'b': 1}
    m1 = Membrana('m1', recursos)
    # Maximales posibles:
    #  - Ejecutar R1 una vez (consume 2a+1b)
    #  - Ejecutar R2 tres veces (consume 3a)
    #  - Ejecutar R2 una vez y luego R1 una vez (consume 3a+1b)
    m1.agregar_regla(Regla({'a': 2, 'b': 1}, {'c': 1}, prioridad=2))
    m1.agregar_regla(Regla({'a': 1}, {'d': 2}, prioridad=2))
    sistema.agregar_membrana(m1)
    return sistema


def Sistema_complejo(recursos: dict = None, tipo: str = None, complejidad: int = None) -> SistemaP:
    """
    Crea un sistema P en el que se asegura la ejecución de al menos una regla de creación o disolución.

    Parámetros:
      - recursos: diccionario inicial para 'm1'. Si es None, genera {'a':2 a 5, 'r':1}.
      - tipo: 'crea' o 'disuelve'. Si es None, se elige aleatoriamente.
      - complejidad: número de reglas adicionales a generar (aleatorio si None).
    """
    sistema = SistemaP()
    # Recursos base: asegurar 'a'>=1 y 'r'>=1 para disolución
    if recursos is None:
        recursos = {"a": random.randint(2, 5), "r": 1}
    m1 = Membrana("m1", recursos.copy())
    sistema.agregar_membrana(m1)

    # Crear una membrana hija m2
    m2 = Membrana("m2", {"dummy": 0})
    sistema.agregar_membrana(m2, parent_id="m1")

    # Añadir reglas adicionales para complejidad
    num_extra = complejidad if isinstance(complejidad, int) and complejidad > 0 else random.randint(1, 5)
    for i in range(num_extra):
        consume = {"a": random.randint(1, 2)}
        produce = {"x": random.randint(1, 3)}
        prio = random.randint(1, 3)
        m1.agregar_regla(Regla(consume, produce, prioridad=prio))

    # Elegir tipo de regla forzada y asignar prioridad superior
    tipo_sel = tipo if tipo in ("crea", "disuelve") else random.choice(["crea", "disuelve"])
    existing_prios = [reg.prioridad for reg in m1.reglas]
    forced_prio = max(existing_prios, default=0) + 1
    if tipo_sel == "crea":
        new_id = "m_forzada"
        m1.agregar_regla(Regla({"a": 1}, {}, prioridad=forced_prio, crea_membranas=[new_id]))
    else:
        m1.agregar_regla(Regla({"r": 1}, {}, prioridad=forced_prio, disuelve_membranas=["m2"]))

    return sistema

def sistema_test_comparativo() -> SistemaP:
    """
    Genera un sistema P que muestra una clara diferencia de comportamiento
    entre los modos 'paralelo' y 'secuencial'.

    Configuración del sistema:
      - Recursos iniciales: {'a': 3, 'b': 1}
      - Regla pri=2: consume {'a':2, 'b':1} y produce {'c':1}
      - Regla pri=1: consume {'a':1} y produce {'b':2}

    Uso:
      sistema = sistema_test_comparativo()
      simular_lapso(sistema, modo='paralelo')
      # se espera recursos finales {'c':1, 'b':2}

      sistema = sistema_test_comparativo()
      simular_lapso(sistema, modo='secuencial')
      # se espera recursos finales {'c':1, 'b':4}
    """
    sistema = SistemaP()
    # Membrana única con recursos determinísticos
    m1 = Membrana('m1', {'a': 3, 'b': 1})
    # Regla de mayor prioridad: consume a y b -> genera c
    m1.agregar_regla(Regla({'a': 2, 'b': 1}, {'c': 1}, prioridad=2))
    # Regla de prioridad menor: consume a -> genera b
    m1.agregar_regla(Regla({'a': 1}, {'b': 2}, prioridad=1))
    sistema.agregar_membrana(m1)
    return sistema

def direccionamiento() -> SistemaP:
    """
    Demuestra reglas con direccionamiento:
      - Membrana m1 con 3 'x'.
      - Regla Pri=2: consume 2 'x' -> produce 1 'y_out' (envía y al padre).
      - Regla Pri=2: consume 1 'x' -> produce 1 'z_in_m2' (envía z a m2).
      - Membrana m2 (hija de m1) vacía.
    En max_paralelo:
      * m1 consumirá 2x+1x y enviará 1 y al padre (si existe) y 1 z a m2.
    """
    sistema = SistemaP()
    # Membrana raíz
    m1 = Membrana('m1', {'x': 3})
    m1.agregar_regla(Regla({'x': 2}, {'y_out': 1}, prioridad=2))
    m1.agregar_regla(Regla({'x': 1}, {'z_in_m2': 1}, prioridad=2))
    sistema.agregar_membrana(m1)
    # Membrana hija m2
    m2 = Membrana('m2', {})
    sistema.agregar_membrana(m2, parent_id='m1')
    return sistema


def actividad1() -> SistemaP:
    """
    Actividad 1:
      Estructura:
        m1 (id="m1") ──> m2 (id="m2")
      w1 = a^2, w2 = {}
      i0 = "m2"
      Reglas en m1:
        r1 (Pri=2): a -> a + b_in_m2 + 2·c_in_m2
        r2 (Pri=1): a^2 -> 2·a_out
    """
    sistema = SistemaP()
    sistema.membrana_salida = "m2"
    m1 = Membrana("m1", {"a": 2})
    m2 = Membrana("m2", {})
    sistema.agregar_membrana(m1)
    sistema.agregar_membrana(m2, parent_id="m1")
    m1.agregar_regla(Regla({"a": 1}, {"a": 1, "b_in_m2": 1, "c_in_m2": 2}, prioridad=1))
    m1.agregar_regla(Regla( {"a": 2},{"a_out": 2}, prioridad=1))
    return sistema


def actividad2(n: int, k: int) -> SistemaP:
    """
    Actividad 2:
      Estructura:
        m1 (id="m1") ──> m2 (id="m2")
                       └─> m3 (id="m3")
      w1 = {}, w2 = a^n c^k d^1, w3 = {}
      i0 = "m3"
      Reglas en m1:
        r4 (Pri=2): d c e -> n_in_m3
        r5 (Pri=1): d     -> s_in_m3
      Reglas en m2:
        r1 (Pri=2): a c   -> e
        r2 (Pri=2): a e   -> c
        r3 (Pri=1): d     -> d + δ (disuelve m2)
    """
    sistema = SistemaP()
    sistema.membrana_salida = "m3"
    m1 = Membrana("m1", {})
    m2 = Membrana("m2", {"a": n, "c": k, "d": 1})
    m3 = Membrana("m3", {})
    sistema.agregar_membrana(m1)
    sistema.agregar_membrana(m2, parent_id="m1")
    sistema.agregar_membrana(m3, parent_id="m1")
    m1.agregar_regla(Regla({"d": 1, "c": 1, "e": 1},{"n_in_m3": 1},prioridad=2))
    m1.agregar_regla(Regla({"d": 1},{"s_in_m3": 1},prioridad=1))

    # Reglas en m2
    m2.agregar_regla(Regla({"a": 1, "c": 1},{"e": 1},prioridad=2))
    m2.agregar_regla(Regla({"a": 1, "e": 1},{"c": 1},prioridad=2))
    m2.agregar_regla(Regla({"d": 1},{"d": 1},prioridad=1,disuelve_membranas=["m2"]))
    return sistema
