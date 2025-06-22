from MemBrainPy import visualizadorAvanzado, Lector
from pathlib import Path


# 1. Obtener la ruta del archivo .pli en el mismo directorio que este script
carpeta_actual = Path(__file__).resolve().parent


ruta_pli1 = carpeta_actual / "Test1.pli"
ruta_pli2 = carpeta_actual / "Test2.pli"
ruta_pli3 = carpeta_actual / "Test3.pli"
ruta_pli4 = carpeta_actual / "Test4.pli"

# 2. Leer el sistema
sistema1 = Lector.leer_sistema(str(ruta_pli1))
sistema2 = Lector.leer_sistema(str(ruta_pli2))
sistema3 = Lector.leer_sistema(str(ruta_pli3))
sistema4 = Lector.leer_sistema(str(ruta_pli4))

sistemas = [sistema1, sistema2, sistema3, sistema4]

visualizadorAvanzado.simular_varios_y_visualizar(sistemas, pasos=30)