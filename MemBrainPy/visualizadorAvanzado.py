import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from copy import deepcopy
import random

from SistemaP import SistemaP, Membrana, Regla, simular_lapso, generar_maximales, veces_aplicable

def dibujar_membrana(ax, membrana: Membrana, sistema: SistemaP, x: float, y: float, width: float, height: float):
    """Dibuja la membrana con sus recursos y, recursivamente, a sus hijas."""
    rect = Rectangle((x, y), width, height, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(rect)

    recursos_text = ''.join(simbolo * cantidad + ' ' 
                           for simbolo, cantidad in membrana.recursos.items())
    ax.text(x + 0.02*width, y + 0.9*height, f"{membrana.id}\n{recursos_text}",
            fontsize=10, verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.3, boxstyle='round'))

    if membrana.hijos:
        n = len(membrana.hijos)
        top_margin = 0.3 * height
        area_h = height - top_margin - 0.05*height
        child_h = area_h / n
        child_w = 0.9 * width
        child_x = x + 0.05 * width
        for i, hid in enumerate(membrana.hijos):
            h = sistema.piel[hid]
            dibujar_membrana(ax, h, sistema,
                             child_x,
                             y + i*child_h,
                             child_w,
                             child_h)

def dibujar_reglas(ax, sistema: SistemaP):
    """Lista en la esquina superior derecha todas las reglas con su prioridad."""
    lines = ["Reglas:"]
    for m in sistema.piel.values():
        for r in m.reglas:
            cons = ",".join(f"{k}:{v}" for k,v in r.izquierda.items())
            prod = ",".join(f"{k}:{v}" for k,v in r.derecha.items())
            crea = f" crea={r.crea_membranas}" if r.crea_membranas else ""
            dis = f" disuelve={r.disuelve_membranas}" if r.disuelve_membranas else ""
            lines.append(f"{m.id}: {cons}->{prod} (Pri={r.prioridad}){crea}{dis}")
    ax.text(0.65, 0.95, "\n".join(lines),
            transform=ax.transAxes, fontsize=8,
            verticalalignment='top',
            bbox=dict(facecolor='wheat', alpha=0.5))

def obtener_membranas_top(sistema: SistemaP):
    """Devuelve las membranas de nivel superior (las que no son hijas)."""
    all_ids   = set(sistema.piel.keys())
    child_ids = {h for m in sistema.piel.values() for h in m.hijos}
    top_ids   = all_ids - child_ids
    return [sistema.piel[i] for i in top_ids]

def simular_y_visualizar(sistema: SistemaP, pasos: int = 5, modo: str = 'max_paralelo'):
    """
    Navega con ← y → entre hasta 'pasos' estados:
      →: si no existe aún, genera un nuevo lapso (aleatorio).
      ←: retrocede en el historial.
    """
    historial = [deepcopy(sistema)]
    idx = 0

    fig, ax = plt.subplots(figsize=(10, 8))

    def dibujar_estado(i):
        ax.clear()
        ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
        ax.set_title(f"Paso {i}")

        est = historial[i]

        # 1) Mostrar los maximales candidatos
        texto = "Maximales generados:"
        for m in est.piel.values():
            rec_disp = deepcopy(m.recursos)
            aplic = [r for r in m.reglas if veces_aplicable(rec_disp, r) > 0]
            if aplic:
                prio = max(r.prioridad for r in aplic)
                top_regs = [r for r in aplic if r.prioridad == prio]
                maxs = generar_maximales(top_regs, rec_disp)
                sets = []
                for combo in maxs:
                    elems = []
                    for regla, v in combo:
                        ridx = m.reglas.index(regla) + 1
                        elems += [f"r{ridx}"] * v
                    sets.append("{" + ",".join(elems) + "}")
                texto += f" {m.id}: " + ",".join(sets)
        ax.text(0.02, 0.05, texto, transform=ax.transAxes,
                fontsize=8, verticalalignment='bottom',
                bbox=dict(facecolor='white', alpha=0.5))

        # 2) Dibujar membranas y reglas
        tops = obtener_membranas_top(est)
        n = len(tops)
        for j, m in enumerate(tops):
            x = j * (100/n) + 5
            dibujar_membrana(ax, m, est, x, 50, 100/n - 10, 40)
        dibujar_reglas(ax, est)
        fig.canvas.draw_idle()

    def on_key(event):
        nonlocal idx
        if event.key == 'right' and idx < pasos:
            # Si es un paso nuevo, lo generamos de manera aleatoria
            if idx == len(historial) - 1:
                nuevo = deepcopy(historial[idx])
                simular_lapso(nuevo, modo=modo)
                historial.append(nuevo)
            idx += 1
            dibujar_estado(idx)

        elif event.key == 'left' and idx > 0:
            idx -= 1
            dibujar_estado(idx)

    fig.canvas.mpl_connect('key_press_event', on_key)

    # Primer dibujo
    dibujar_estado(0)
    plt.show(block=True)
