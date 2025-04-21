import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from SistemaP import SistemaP, Membrana, Regla, simular_lapso


def dibujar_membrana(ax, membrana: Membrana, sistema: SistemaP, x: float, y: float, width: float, height: float):
    """
    Dibuja una membrana como un rectángulo en el eje 'ax' usando la posición (x, y) con el ancho y alto dados.

    Dentro del rectángulo se muestra:
      - El identificador (id) de la membrana.
      - Los recursos: se repite cada símbolo tantas veces como indique su cantidad.
      - Si la membrana tiene hijas, se dibujan de forma anidada dentro del rectángulo (disposición vertical).
    """
    rect = Rectangle((x, y), width, height, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    recursos_text = ""
    for simbolo, cantidad in membrana.recursos.items():
        recursos_text += simbolo * cantidad + " "
    ax.text(
        x + 0.02 * width,
        y + height - 0.1 * height,
        f"{membrana.id}\n{recursos_text}",
        fontsize=10,
        verticalalignment='top',
        bbox=dict(facecolor='w', alpha=0.3, boxstyle="round")
    )
    if membrana.hijos:
        n_hijos = len(membrana.hijos)
        margen_superior = 0.3 * height
        area_hijas_y = y
        area_hijas_height = height - margen_superior - 0.05 * height
        child_height = area_hijas_height / n_hijos
        child_width = width * 0.9
        child_x = x + 0.05 * width
        for i, hijo_id in enumerate(membrana.hijos):
            hijo = sistema.piel.get(hijo_id)
            if hijo:
                child_y = area_hijas_y + i * child_height
                dibujar_membrana(ax, hijo, sistema, child_x, child_y, child_width, child_height)


def dibujar_reglas(ax, sistema: SistemaP):
    """
    Dibuja todas las reglas de todas las membranas en la esquina superior derecha de la figura.
    Incluye información de creación y disolución de membranas.
    """
    reglas_text = "Reglas:\n"
    for id_mem, membrana in sistema.piel.items():
        for regla in membrana.reglas:
            consume = ", ".join([f"{k}:{v}" for k, v in regla.izquierda.items()]) or ""
            produce = ", ".join([f"{k}:{v}" for k, v in regla.derecha.items()]) or ""
            crea = f" crea={regla.crea_membranas}" if regla.crea_membranas else ""
            disuelve = f" disuelve={regla.disuelve_membranas}" if regla.disuelve_membranas else ""
            reglas_text += (
                f"{membrana.id}: {consume} -> {produce}"
                f" (Pri={regla.prioridad}){crea}{disuelve}\n"
            )
    ax.text(
        0.70,
        0.95,
        reglas_text,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='top',
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    )


def obtener_membranas_top(sistema: SistemaP):
    todas_ids = set(sistema.piel.keys())
    ids_hijos = set(hijo for mem in sistema.piel.values() for hijo in mem.hijos)
    top_ids = todas_ids - ids_hijos
    return [sistema.piel[id_mem] for id_mem in top_ids]


def visualizar_sistema_grafico(sistema: SistemaP):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    top_membranas = obtener_membranas_top(sistema)
    n_top = len(top_membranas)
    if n_top == 0:
        return
    area_width = 100 / n_top
    for i, membrana in enumerate(top_membranas):
        x = i * area_width + 5
        y = 50
        width = area_width - 10
        height = 40
        dibujar_membrana(ax, membrana, sistema, x, y, width, height)
    dibujar_reglas(ax, sistema)
    plt.show()


def simular_y_visualizar_grafico(sistema: SistemaP, pasos: int = 5, delay: float = 1.0):
    """
    Simula la evolución del sistema P y actualiza la visualización gráfica en cada lapso,
    incluyendo un retardo inicial antes del primer paso.
    """
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 8))

    # Dibujo inicial (Paso 0) y retardo
    ax.clear()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title("Estado Inicial")
    top_membranas = obtener_membranas_top(sistema)
    if top_membranas:
        area_width = 100 / len(top_membranas)
        for i, membrana in enumerate(top_membranas):
            x = i * area_width + 5
            y = 50
            width = area_width - 10
            height = 40
            dibujar_membrana(ax, membrana, sistema, x, y, width, height)
    dibujar_reglas(ax, sistema)
    plt.pause(delay)

    for paso in range(1, pasos + 1):
        ax.clear()
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"Paso {paso}")

        # Ejecutar un lapso de evolución
        simular_lapso(sistema)

        # Dibujar estado tras el lapso
        top_membranas = obtener_membranas_top(sistema)
        if top_membranas:
            area_width = 100 / len(top_membranas)
            for i, membrana in enumerate(top_membranas):
                x = i * area_width + 5
                y = 50
                width = area_width - 10
                height = 40
                dibujar_membrana(ax, membrana, sistema, x, y, width, height)
        dibujar_reglas(ax, sistema)
        plt.pause(delay)

    plt.ioff()
    plt.show()