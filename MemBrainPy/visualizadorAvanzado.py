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
    # Dibujar el rectángulo principal para la membrana
    rect = Rectangle((x, y), width, height, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    
    # Construir el texto con el id y los recursos.
    # Por cada símbolo, se repite la letra tantas veces como indique su cantidad.
    recursos_text = ""
    for simbolo, cantidad in membrana.recursos.items():
        recursos_text += simbolo * cantidad + " "
    
    # Colocar el texto cerca de la esquina superior izquierda del rectángulo.
    ax.text(x + 0.02 * width, y + height - 0.1 * height, f"{membrana.id}\n{recursos_text}", 
            fontsize=10, verticalalignment='top', bbox=dict(facecolor='w', alpha=0.3, boxstyle="round"))
    
    # Si la membrana tiene hijas, las dibujamos de forma anidada.
    if membrana.hijos:
        n_hijos = len(membrana.hijos)
        # Se reserva un margen superior para el contenido propio de la membrana.
        margen_superior = 0.3 * height
        area_hijas_y = y  # Usaremos la parte inferior del rectángulo para las hijas.
        area_hijas_height = height - margen_superior - 0.05 * height  # Se deja también un pequeño margen inferior.
        # Distribuir las membranas hijas verticalmente (puedes ajustar el layout si lo deseas).
        child_height = area_hijas_height / n_hijos
        child_width = width * 0.9  # Dejar un margen lateral para que se vea la anidación.
        child_x = x + 0.05 * width
        for i, hijo_id in enumerate(membrana.hijos):
            hijo = sistema.piel.get(hijo_id)
            if hijo:
                child_y = area_hijas_y + i * child_height
                dibujar_membrana(ax, hijo, sistema, child_x, child_y, child_width, child_height)

def dibujar_reglas(ax, sistema: SistemaP):
    """
    Dibuja todas las reglas de todas las membranas en la esquina superior derecha de la figura.
    
    Se agrupan las reglas en un bloque de texto que se coloca en coordenadas relativas al eje.
    """
    reglas_text = "Reglas:\n"
    for id_mem, membrana in sistema.piel.items():
        for regla in membrana.reglas:
            # Representación textual de la regla: consume -> produce (prioridad)
            consume = ", ".join([f"{k}:{v}" for k, v in regla.izquierda.items()])
            produce = ", ".join([f"{k}:{v}" for k, v in regla.derecha.items()])
            reglas_text += f"{membrana.id}: {consume} -> {produce} (Pri={regla.prioridad})\n"
    
    # Ubicar el bloque de reglas en la esquina superior derecha usando coordenadas normalizadas.
    ax.text(0.70, 0.95, reglas_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='top', bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

def obtener_membranas_top(sistema: SistemaP):
    """
    Devuelve una lista de membranas top-level, es decir, aquellas que no son hijas de ninguna otra.
    
    Se extraen las claves de 'sistema.piel' y se elimina aquellas que aparecen en el atributo 'hijos' de cualquier membrana.
    """
    todas_ids = set(sistema.piel.keys())
    ids_hijos = set()
    for membrana in sistema.piel.values():
        for hijo in membrana.hijos:
            ids_hijos.add(hijo)
    top_ids = todas_ids - ids_hijos
    return [sistema.piel[id_mem] for id_mem in top_ids]

def visualizar_sistema_grafico(sistema: SistemaP):
    """
    Dibuja el sistema P de forma gráfica en una ventana de matplotlib.
    
    Las membranas top-level se distribuyen horizontalmente en el espacio disponible.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect('equal')
    ax.axis('off')
    
    top_membranas = obtener_membranas_top(sistema)
    n_top = len(top_membranas)
    if n_top == 0:
        return
    
    # Dividir el espacio horizontalmente para cada membrana top-level.
    area_width = 100 / n_top
    for i, membrana in enumerate(top_membranas):
        # Asignar a cada top-level membrana un rectángulo con márgenes.
        x = i * area_width + 5
        y = 50  # Posición vertical fija (puedes ajustar según tus necesidades)
        width = area_width - 10
        height = 40
        dibujar_membrana(ax, membrana, sistema, x, y, width, height)
    
    # Dibujar el bloque de reglas en la esquina superior derecha.
    dibujar_reglas(ax, sistema)
    plt.show()

def simular_y_visualizar_grafico(sistema: SistemaP, pasos: int = 5, delay: float = 1.0):
    """
    Simula la evolución del sistema P y actualiza la visualización gráfica en cada lapso.
    
    Para cada paso se:
      1. Realiza un lapso de simulación.
      2. Redibuja la escena completa (membranas anidadas y reglas).
      3. Pausa durante 'delay' segundos.
    """
    plt.ion()  # Activar modo interactivo
    fig, ax = plt.subplots(figsize=(10, 8))
    
    for paso in range(1, pasos + 1):
        ax.clear()
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(f"Paso {paso}")
        
        # Ejecutar un lapso de evolución
        simular_lapso(sistema)
        
        # Dibujar las membranas top-level (y recursivamente, sus hijas)
        top_membranas = obtener_membranas_top(sistema)
        n_top = len(top_membranas)
        if n_top > 0:
            area_width = 100 / n_top
            for i, membrana in enumerate(top_membranas):
                x = i * area_width + 5
                y = 50
                width = area_width - 10
                height = 40
                dibujar_membrana(ax, membrana, sistema, x, y, width, height)
        
        # Dibujar las reglas en la esquina superior derecha
        dibujar_reglas(ax, sistema)
        plt.pause(delay)
    
    plt.ioff()
    plt.show()
