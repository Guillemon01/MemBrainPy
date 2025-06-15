"""
visualizadorAvanzado.py

Módulo para visualizar la simulación de Sistemas P, usando matplotlib.
"""

from __future__ import annotations
from copy import deepcopy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import List, Dict, Optional, Tuple
import math

from .SistemaP import (
    SistemaP,
    Membrana,
    Regla,
    simular_lapso,
    generar_maximales,
    max_applications,
    LapsoResult,
)


def dibujar_membrana(
    ax: plt.Axes,
    membrana: Membrana,
    sistema: SistemaP,
    x: float,
    y: float,
    width: float,
    height: float
) -> None:
    """
    Dibuja recursivamente una membrana (y sus hijas) en el eje dado.

    Args:
        ax: objeto Axes de matplotlib donde dibujar.
        membrana: instancia de Membrana a representar.
        sistema: SistemaP que contiene todas las membranas.
        x: coordenada x de la esquina inferior izquierda de la membrana.
        y: coordenada y de la esquina inferior izquierda de la membrana.
        width: ancho de la representación de la membrana.
        height: alto de la representación de la membrana.
    """
    borde_color = "blue" if sistema.output_membrane == membrana.id_mem else "black"
    rect = Rectangle(
        (x, y),
        width,
        height,
        fill=False,
        edgecolor=borde_color,
        linewidth=2
    )
    ax.add_patch(rect)

    recursos_text = "".join(symbol * count + " " for symbol, count in membrana.resources.items())
    ax.text(
        x + 0.02 * width,
        y + 0.9 * height,
        f"{membrana.id_mem}\n{recursos_text}",
        fontsize=10,
        verticalalignment="top",
        bbox=dict(facecolor="white", alpha=0.3, boxstyle="round")
    )

    if membrana.children:
        n_hijas = len(membrana.children)
        margen_superior = 0.3 * height
        area_interior_h = height - margen_superior - 0.05 * height
        alto_hija = area_interior_h / n_hijas
        ancho_hija = 0.9 * width
        x_hija = x + 0.05 * width

        for idx, hija_id in enumerate(membrana.children):
            hija = sistema.skin[hija_id]
            y_hija = y + idx * alto_hija
            dibujar_membrana(
                ax,
                hija,
                sistema,
                x_hija,
                y_hija,
                ancho_hija,
                alto_hija
            )


def obtener_membranas_top(sistema: SistemaP) -> List[Membrana]:
    """
    Devuelve la lista de membranas de nivel superior (aquellas que no son hijas de ninguna).

    Args:
        sistema: SistemaP que contiene todas las membranas.

    Returns:
        Lista de instancias Membrana que no aparecen como hija en ningún otro.
    """
    todos_ids = set(sistema.skin.keys())
    ids_hijas = {h for m in sistema.skin.values() for h in m.children}
    top_ids = todos_ids - ids_hijas
    return [sistema.skin[mid] for mid in top_ids]


def dibujar_reglas(fig: plt.Figure, sistema: SistemaP) -> None:
    """
    Dibuja, en una columna a la derecha de la figura, todas las reglas asociadas
    a cada membrana del sistema.

    Args:
        fig: objeto Figure de matplotlib donde agregar el texto.
        sistema: SistemaP cuyas reglas se van a mostrar.
    """
    lineas: List[str] = []
    for m in sistema.skin.values():
        for r in m.reglas:
            consumo = ",".join(f"{k}:{v}" for k, v in r.left.items())
            produccion = ",".join(f"{k}:{v}" for k, v in r.right.items())
            crea = f" crea={r.create_membranes}" if r.create_membranes else ""
            dis = f" disuelve={r.dissolve_membranes}" if r.dissolve_membranes else ""
            lineas.append(
                f"{m.id_mem}: {consumo}->{produccion} (Pri={r.priority}){crea}{dis}"
            )

    fig.text(
        0.78,
        0.1,
        "Reglas:\n" + "\n".join(lineas),
        fontsize=8,
        verticalalignment="bottom",
        bbox=dict(facecolor="wheat", alpha=0.7)
    )

def format_maximal(
    seleccion: Dict[str, List[Tuple[Regla, int]]]
) -> str:
    """
    Toma un diccionario {'m2': [(r,2), (s,1)], 'm3': [(t,1)]}
    y devuelve una cadena legible, por ejemplo:
        m2: 2×(a,c→e); 1×(d→f)
        m3: 1×(g→h)

    Args:
        seleccion: mapeo de ID de membrana a lista de tuplas (Regla, veces).

    Returns:
        Texto formateado con cada membrana y sus reglas aplicadas.
    """
    lineas: List[str] = []
    for mid, combo in seleccion.items():
        partes: List[str] = []
        for regla, cnt in combo:
            cons = ",".join(
                k if v == 1 else f"{k}:{v}" for k, v in regla.left.items()
            )
            prod = ",".join(
                k if v == 1 else f"{k}:{v}" for k, v in regla.right.items()
            )
            partes.append(f"{cnt}×({cons}→{prod})")
        lineas.append(f"{mid}: " + "; ".join(partes))
    return "\n".join(lineas)

def simular_y_visualizar(
    sistema: SistemaP,
    pasos: int = 5,
    #modo: str = "max_paralelo",
    rng_seed: Optional[int] = None
) -> None:
    """
    Permite navegar (←, →) entre varios estados de simulación hasta 'pasos':
      →: avanza un paso (genera un nuevo lapso y visualiza el maximal elegido).
      ←: retrocede al estado anterior.

    Args:
        sistema: instancia de SistemaP inicial.
        pasos: número máximo de pasos que se pueden generar.
        modo: modo de simulación ("max_paralelo" o "secuencial").
    """
    modo = "max_paralelo"  # Modo por defecto Y UNICO AHORA MISMO
    historial: List[SistemaP] = [deepcopy(sistema)]
    max_aplicados: List[Optional[Dict[str, List[Tuple[Regla, int]]]]] = [None]
    idx = 0

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.subplots_adjust(top=0.85)  # espacio para texto superior


    def dibujar_estado(i: int) -> None:
        """
        Dibuja el estado 'i' del historial en la figura:
        - Membranas (estructuras).
        - Recursos dentro de cada membrana.
        - Maximal aplicado en ese paso.
        - Conjuntos máximos candidatos.

        Args:
            i: índice del paso a mostrar (0 = estado inicial).
        """
        # 1) Limpiar textos previos de la figura
        for text in list(fig.texts):
            text.remove()

        # 2) Limpiar y preparar ejes
        ax.clear()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # 3) Título con número de paso
        ax.set_title(f"Paso {i}")

        # 4) Mostrar maximal realmente aplicado (si i > 0)
        if i > 0 and max_aplicados[i]:
            texto_max = format_maximal(max_aplicados[i])  # type: ignore
            fig.text(
                0.5,
                0.92,
                texto_max,
                ha="center",
                va="center",
                fontsize=10,
                bbox=dict(facecolor="white", alpha=0.8, boxstyle="round")
            )

        # 5) Mostrar listados de maximales candidatos por membrana
        texto_candidatos = "Maximales generados:"
        estado_actual = historial[i]
        for m in estado_actual.skin.values():
            rec_disp = deepcopy(m.resources)
            aplicables = [r for r in m.reglas if max_applications(rec_disp, r) > 0]
            if aplicables:
                prio_max = max(r.priority for r in aplicables)
                reglas_top = [r for r in aplicables if r.priority == prio_max]
                conjuntos = generar_maximales(reglas_top, rec_disp)
                representaciones: List[str] = []
                for combo in conjuntos:
                    elementos: List[str] = []
                    for regla, veces in combo:
                        ridx = m.reglas.index(regla) + 1
                        elementos += [f"r{ridx}"] * veces
                    representaciones.append("{" + ",".join(elementos) + "}")
                texto_candidatos += f" {m.id_mem}: " + ",".join(representaciones)

        ax.text(
            0.02,
            0.02,
            texto_candidatos,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment="bottom",
            bbox=dict(facecolor="white", alpha=0.5)
        )

        # 6) Dibujar las membranas de nivel superior repartiendo horizontalmente
        tops = obtener_membranas_top(estado_actual)
        num_tops = len(tops)
        if num_tops > 0:
            for j, m in enumerate(tops):
                x_base = j * (0.7 / num_tops)
                y_base = 0.2
                ancho = (0.7 / num_tops) - 0.02
                alto = 0.7
                dibujar_membrana(ax, m, estado_actual, x_base, y_base, ancho, alto)

        # 7) Dibujar reglas en la zona derecha
        dibujar_reglas(fig, estado_actual)

        fig.canvas.draw_idle()

    def on_key(event) -> None:
        """
        Controla las pulsaciones de flecha izquierda/derecha para navegar por el historial.
        """
        nonlocal idx

        if event.key == "right" and idx < pasos:
            if idx == len(historial) - 1:
                copia = deepcopy(historial[idx])
                lapso_res: LapsoResult = simular_lapso(copia, rng_seed=rng_seed)
                historial.append(copia)
                max_aplicados.append(lapso_res.seleccionados)
            idx += 1
            dibujar_estado(idx)

        elif event.key == "left" and idx > 0:
            idx -= 1
            dibujar_estado(idx)

    fig.canvas.mpl_connect("key_press_event", on_key)
    dibujar_estado(0)
    plt.show(block=True)

def simular_varios_y_visualizar(
    sistemas: List[SistemaP],
    pasos: int = 5,
    #modo: str = 'max_paralelo',
    rng_seed: Optional[int] = None
) -> None:
    '''
    Simula y visualiza simultáneamente varios Sistemas P.
    Parámetros idénticos a simular_y_visualizar, pero recibe una lista de sistemas.
    Navegación con flechas izquierda/derecha para retroceder y avanzar pasos.
    '''
    modo = "max_paralelo"  # Modo por defecto Y UNICO AHORA MISMO

    import textwrap  # para ajustar texto largo
    # Validar que todos los elementos sean instancias de SistemaP
    for idx_s, sis in enumerate(sistemas):
        if not isinstance(sis, SistemaP):
            raise TypeError(f"Elemento {idx_s} de 'sistemas' no es un SistemaP, es {type(sis).__name__}")

    # Inicialización de historiales y seleccionados por sistema
    historiales: List[List[SistemaP]] = [[deepcopy(s) for s in sistemas]]
    max_aplicados: List[List[Optional[Dict[str, List[Tuple[Regla, int]]]]]] = [[None] * len(sistemas)]
    idx = 0

    # Configuración de subplots según número de sistemas
    n = len(sistemas)
    cols = min(3, n)
    rows = math.ceil(n/cols)
    fig, axes = plt.subplots(rows, cols, figsize=(cols*6, rows*4))
    axes_list = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    def dibujar_estado_varios(i: int) -> None:
        fig.suptitle(f'Paso {i}', fontsize=16)
        for j, ax in enumerate(axes_list):
            ax.clear()
            if j < len(historiales[i]):
                est = historiales[i][j]
                sel = max_aplicados[i][j]
                # Mostrar maximal aplicado
                if sel:
                    txt = format_maximal(sel)
                    ax.text(
                        0.5, 0.92,
                        txt,
                        ha='center', va='center',
                        transform=ax.transAxes,
                        fontsize=10,
                        bbox=dict(facecolor='white', alpha=0.8, boxstyle='round')
                    )
                # Mostrar candidatos generados (texto ajustado en varias líneas)
                texto_cand = 'Maximales generados:'
                for m in est.skin.values():
                    rec = deepcopy(m.resources)
                    aplic = [r for r in m.reglas if max_applications(rec, r) > 0]
                    if aplic:
                        prio = max(r.priority for r in aplic)
                        top = [r for r in aplic if r.priority == prio]
                        combos = generar_maximales(top, rec)
                        rep: List[str] = []
                        for combo in combos:
                            elems: List[str] = []
                            for regla, cnt in combo:
                                idx_r = m.reglas.index(regla) + 1
                                elems += [f'r{idx_r}'] * cnt
                            rep.append('{' + ','.join(elems) + '}')
                        texto_cand += f' {m.id_mem}: ' + ','.join(rep)
                # Ajustar líneas para no salirse de la figura
                wrapped = textwrap.fill(texto_cand, width=40)
                ax.text(
                    0.02, 0.05,
                    wrapped,
                    transform=ax.transAxes,
                    fontsize=8,
                    verticalalignment='bottom',
                    bbox=dict(facecolor='white', alpha=0.5)
                )
                # Dibujar membranas de nivel superior
                tops = obtener_membranas_top(est)
                numt = len(tops)
                if numt:
                    for k, m in enumerate(tops):
                        xb = k*(0.7/numt)
                        yb = 0.2
                        w = (0.7/numt)-0.02
                        h = 0.7
                        dibujar_membrana(ax, m, est, xb, yb, w, h)
                # Dibujar reglas dentro del subplot, subido en Y para no interferir
                lineas: List[str] = []
                for m in est.skin.values():
                    for r in m.reglas:
                        c = ','.join(f"{k}:{v}" for k,v in r.left.items())
                        p = ','.join(f"{k}:{v}" for k,v in r.right.items())
                        cr = f" crea={r.create_membranes}" if r.create_membranes else ''
                        ds = f" disuelve={r.dissolve_membranes}" if r.dissolve_membranes else ''
                        lineas.append(f"{m.id_mem}: {c}->{p} (Pri={r.priority}){cr}{ds}")
                reglas_text = 'Reglas:\n' + '\n'.join(lineas)
                ax.text(
                    0.78, 0.3,
                    reglas_text,
                    transform=ax.transAxes,
                    fontsize=6,
                    verticalalignment='top',
                    bbox=dict(facecolor='wheat', alpha=0.7)
                )
                ax.set_title(f'Sistema {j+1}')
            else:
                ax.axis('off')
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.canvas.draw_idle()

    def on_key_varios(event) -> None:
        nonlocal idx
        if event.key == 'right' and idx < pasos:
            if idx == len(historiales) - 1:
                nuevos = [deepcopy(historiales[-1][k]) for k in range(len(sistemas))]
                sel_line: List[Optional[Dict[str,List[Tuple[Regla,int]]]]]=[]
                for k, sis in enumerate(nuevos):
                    seed = None if rng_seed is None else rng_seed + k + len(historiales)
                    lap = simular_lapso(sis, rng_seed=seed)
                    sel_line.append(lap.seleccionados)
                historiales.append(nuevos)
                max_aplicados.append(sel_line)
            idx += 1
            dibujar_estado_varios(idx)
        elif event.key == 'left' and idx > 0:
            idx -= 1
            dibujar_estado_varios(idx)

    fig.canvas.mpl_connect('key_press_event', on_key_varios)
    dibujar_estado_varios(0)
    plt.show(block=True)
