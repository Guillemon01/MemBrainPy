# MemBrainPy/MemBrainPy/__init__.py

from .SistemaP import SistemaP, Membrana, Regla
from .visualizadorAvanzado import simular_y_visualizar
# … añade aquí todo lo que quieras importar “directo” desde el paquete

__all__ = [
    "SistemaP", "Membrana", "Regla",
    "simular_y_visualizar",
    # …
]
