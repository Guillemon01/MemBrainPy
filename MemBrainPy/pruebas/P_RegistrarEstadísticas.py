from MemBrainPy import registrar_estadisticas, simular_lapso
from MemBrainPy import tests_sistemas

sistema = tests_sistemas.sistema_basico()
save_csv = True
filename = 'output.csv'

df = registrar_estadisticas(sistema, lapsos=30, rng_seed=None)
print(df)

if save_csv:
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\nDataFrame guardado en '{filename}'")
