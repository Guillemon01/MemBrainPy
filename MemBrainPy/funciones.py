from SistemaP import SistemaP, Membrana, Regla


def division(n: int, divisor: int) -> SistemaP:
    """
    División entera de n 'a' entre divisor:
      - Pri 2: consume divisor 'a' -> produce 'b' (cociente).
      - Pri 1: consume 1 'a'    -> produce 'r' (resto).
    En max_paralelo genera b^(n//divisor) y r^(n%divisor).
    """
    sistema = SistemaP()
    m = Membrana('m1', {'a': n})
    m.agregar_regla(Regla({'a': divisor}, {'b': 1}, prioridad=2))
    m.agregar_regla(Regla({'a': 1}, {'r': 1}, prioridad=1))
    sistema.agregar_membrana(m)
    return sistema


def suma(n: int, m: int) -> SistemaP:
    """
    Suma n 'a' + m 'b':
      - Pri 1: consume 1 'a' -> produce 1 'c'.
      - Pri 1: consume 1 'b' -> produce 1 'c'.
    En max_paralelo produce c^(n+m).
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1}, {'c': 1}, prioridad=1))
    mem.agregar_regla(Regla({'b': 1}, {'c': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def resta(n: int, m: int) -> SistemaP:
    """
    Resta n - m:
      - Pri 3: consume 1 'a'+1 'b' -> elimina pares.
      - Pri 2: consume 1 'a'      -> produce 'd' si n>m.
      - Pri 1: consume 1 'b'      -> produce 'e' si m>n.
    En max_paralelo empareja, luego produce d^(n-m) o e^(m-n).
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1, 'b': 1}, {}, prioridad=3))
    mem.agregar_regla(Regla({'a': 1}, {'d': 1}, prioridad=2))
    mem.agregar_regla(Regla({'b': 1}, {'e': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def paridad(n: int) -> SistemaP:
    """
    Paridad de n 'a':
      - Pri 2: consume 2 'a' -> produce 'p'.
      - Pri 1: consume 1 'a' -> produce 'i'.
    En max_paralelo genera p^(n//2) y, si n es impar, un 'i' adicional.
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n})
    # Par: cada par de 'a' las elimina
    mem.agregar_regla(Regla({'a': 2}, {}, prioridad=2))
    # Impar: el sobra 1 'a' produce un 'i'
    mem.agregar_regla(Regla({'a': 1}, {'i': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def duplicar(n: int) -> SistemaP:
    """
    Duplica contador n:
      - Pri 1: consume 1 'a' -> produce 2 'b'.
    En max_paralelo produce 2n 'b'.
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': 1}, {'b': 2}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def comparacion(n: int, m: int) -> SistemaP:
    """
    Compara n y m:
      - Pri 3: consume 1 'a'+1 'b' -> elimina pares.
      - Pri 2: consume 1 'a' -> produce 'g' (greater);
                consume 1 'b' -> produce 'l' (less).
      - Pri 1: consume 0     -> produce 'e' (equal).
    En max_paralelo empareja, luego g/l o e.
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1, 'b': 1}, {}, prioridad=3))
    mem.agregar_regla(Regla({'a': 1}, {'g': 1}, prioridad=2))
    mem.agregar_regla(Regla({'b': 1}, {'l': 1}, prioridad=2))
    mem.agregar_regla(Regla({}, {'e': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def modulo(n: int, m: int) -> SistemaP:
    """
    Resto de n mod m:
      - Pri 2: consume m 'a' -> descarta bloques completos.
      - Pri 1: consume 1 'a' -> produce 'r'.
    En max_paralelo genera r^(n%m).
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': m}, {}, prioridad=2))
    mem.agregar_regla(Regla({'a': 1}, {'r': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema


def umbral(n: int, k: int) -> SistemaP:
    """
    Test de umbral k en n:
      - Pri 2: consume k 'a' -> produce 't' (true).
      - Pri 1: consume 0     -> produce 'f' (false).
    En max_paralelo, si n>=k produce t; si n<k produce f.
    """
    sistema = SistemaP()
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': k}, {'t': 1}, prioridad=2))
    mem.agregar_regla(Regla({}, {'f': 1}, prioridad=1))
    sistema.agregar_membrana(mem)
    return sistema
