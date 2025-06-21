# MemBrainPy/__init__.py

import pkgutil
import importlib

__all__ = []

# Itera sobre cada submódulo/subpaquete de este paquete
for finder, module_name, is_pkg in pkgutil.iter_modules(__path__):
    
    # importa el módulo o subpaquete
    module = importlib.import_module(f"{__name__}.{module_name}")
    # añade el nombre del módulo al namespace del paquete
    globals()[module_name] = module
    __all__.append(module_name)

    # re-exporta todos sus símbolos públicos
    # si el módulo define __all__, úsalo; si no, exporta todo lo que no empiece por "_"
    public_symbols = getattr(module, "__all__", [n for n in dir(module) if not n.startswith("_")])
    for sym in public_symbols:
        if sym == module_name:
            # evitamos sobrescribir el propio paquete con un símbolo del mismo nombre
            continue
        attr = getattr(module, sym, None)
        if attr is None:
            continue
        globals()[sym] = attr
        __all__.append(sym)
