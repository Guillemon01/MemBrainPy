from SistemaP import simular_lapso, SistemaP, Membrana
from time import sleep

def visualizar_sistema(sistema: SistemaP, pasos: int = 5, delay: float = 1.0):
    """
    Simula y muestra la evolución de un sistema P durante 'pasos' lapsos,
    indicando qué membranas se crean o disuelven en cada paso.
    """
    print("===== INICIO DE SIMULACIÓN =====")
    for paso in range(1, pasos + 1):
        print(f"\n--- Lapso {paso} ---")

        # Capturar IDs antes de evolucionar
        before_ids = set(sistema.piel.keys())

        # Ejecutar un lapso
        simular_lapso(sistema)

        # Capturar IDs tras el lapso
        after_ids = set(sistema.piel.keys())

        # Calcular qué membranas han aparecido o desaparecido
        creadas   = after_ids - before_ids
        disueltas = before_ids  - after_ids

        if creadas:
            print("Membranas creadas:", ", ".join(sorted(creadas)))
        if disueltas:
            print("Membranas disueltas:", ", ".join(sorted(disueltas)))

        # Mostrar estado y jerarquía
        mostrar_estado(sistema)

        sleep(delay)
    print("===== FIN DE SIMULACIÓN =====")


def mostrar_estado(sistema: SistemaP):
    """
    Imprime en consola el estado actual de cada membrana,
    mostrando su jerarquía y recursos.
    """
    print("\nEstado actual de las membranas:")
    # Encontrar membranas top-level
    todas_ids = set(sistema.piel.keys())
    hijos_ids = {hijo for mem in sistema.piel.values() for hijo in mem.hijos}
    top_ids = sorted(todas_ids - hijos_ids)

    def _print_subtree(id_mem: str, indent: int = 0):
        mem = sistema.piel[id_mem]
        pref = "  " * indent
        # Línea con id, padre (si lo tiene) y lista de hijos
        padre = mem.padre or "—"
        hijos = ", ".join(mem.hijos) if mem.hijos else "—"
        print(f"{pref}- Membrana {mem.id} (padre: {padre}; hijos: {hijos})")
        # Recursos
        recursos_str = ", ".join(f"{s}:{c}" for s, c in mem.recursos.items()) or "vacía"
        print(f"{pref}  Recursos: {recursos_str}")
        # Recursión sobre hijas
        for hijo_id in sorted(mem.hijos):
            _print_subtree(hijo_id, indent + 1)

    for top_id in top_ids:
        _print_subtree(top_id)

    print("-" * 40)
