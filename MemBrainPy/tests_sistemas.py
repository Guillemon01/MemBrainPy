# tests_sistemas.py
import random
from SistemaP import SistemaP, Membrana, Regla

def sistema_basico(recursos: dict = None, num_reglas: int = None) -> SistemaP:
    """
    Crea un sistema P muy simple con una única membrana y reglas sencillas.
    
    Parámetros:
      - recursos: diccionario con los recursos iniciales de la membrana.
                  Si es None, se generan valores aleatorios.
      - num_reglas: número de reglas a agregar a la membrana.
                    Si es None, se usarán 2 reglas por defecto.
    
    Ejemplo de recursos generados por defecto: {"a": 5 a 8, "b": 3 a 5}
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"a": random.randint(5, 8), "b": random.randint(3, 5)}
    m1 = Membrana("m1", recursos)
    # Regla 1: consume {"a": 2, "b": 1} y produce {"c": 1}, prioridad 2
    m1.agregar_regla(Regla({"a": 2, "b": 1}, {"c": 1}, prioridad=2))
    # Regla 2: consume {"a": 1} y produce {"b": 2}, prioridad 1 (si se desea agregar)
    if num_reglas is None or num_reglas > 1:
        m1.agregar_regla(Regla({"a": 1}, {"b": 2}, prioridad=1))
    sistema.agregar_membrana(m1)
    return sistema

def sistema_aniado(recursos: dict = None, num_membranas: int = None, anidacion_max: int = None) -> SistemaP:
    """
    Crea un sistema P con membranas anidadas.
    
    Parámetros:
      - recursos: diccionario para la membrana top-level. Si es None, se generan valores aleatorios.
      - num_membranas: número total de membranas a crear. Si es None, se elige un valor aleatorio entre 2 y 4.
      - anidacion_max: nivel máximo de anidación permitido. Si es None, se elige un valor aleatorio entre 2 y 3.
    
    La función crea una membrana top-level y, de forma aleatoria, asigna membranas hijas a aquellas
    que todavía pueden anidar (nivel actual menor que anidacion_max).
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"a": random.randint(5, 8), "b": random.randint(3, 5)}
    if num_membranas is None:
        num_membranas = random.randint(2, 4)  # se requiere al menos 2 para poder anidar
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
        # Seleccionar candidatos que puedan anidar (nivel < anidacion_max)
        candidatos = [ (m, lvl) for (m, lvl) in membranas_info if lvl < anidacion_max ]
        if not candidatos:
            break  # no quedan membranas que puedan tener hijos
        parent, parent_level = random.choice(candidatos)
        new_id = f"m{i}"
        nuevos_recursos = {"a": random.randint(3, 7), "b": random.randint(2, 5)}
        nueva_mem = Membrana(new_id, nuevos_recursos)
        # Agregar una regla simple a la membrana hija
        nueva_mem.agregar_regla(Regla({"a": 1}, {"b": 1}, prioridad=1))
        sistema.agregar_membrana(nueva_mem)
        # Registrar la relación de anidación
        parent.hijos.append(new_id)
        membranas_info.append((nueva_mem, parent_level + 1))
        
    return sistema

def sistema_con_conflictos(recursos: dict = None) -> SistemaP:
    """
    Crea un sistema P en el que existen conflictos de recursos entre las reglas.
    
    Parámetros:
      - recursos: diccionario con los recursos iniciales para la membrana.
                  Si es None, se generan valores aleatorios (por ejemplo, {"x": 5 a 8}).
    
    Se definen al menos dos reglas que compiten por los mismos recursos.
    """
    sistema = SistemaP()
    if recursos is None:
        recursos = {"x": random.randint(5, 8)}
    m1 = Membrana("m1", recursos)
    # Regla 1: consume {"x": 3} y produce {"y": 1}, prioridad 1
    m1.agregar_regla(Regla({"x": 3}, {"y": 1}, prioridad=1))
    # Regla 2: consume {"x": 2} y produce {"z": 1}, prioridad 1
    m1.agregar_regla(Regla({"x": 2}, {"z": 1}, prioridad=1))
    # Opcionalmente, agregar otra regla conflictiva
    m1.agregar_regla(Regla({"x": 1}, {"w": 2}, prioridad=1))
    sistema.agregar_membrana(m1)
    return sistema
