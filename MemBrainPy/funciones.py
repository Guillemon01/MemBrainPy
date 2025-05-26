from SistemaP import SistemaP, Membrana, Regla


def division(n: int, divisor: int) -> SistemaP:
    """
    División entera de n 'a' entre divisor:
      - Pri 2: consume divisor 'a' -> produce 'b' en membrana de salida.
      - Pri 1: consume 1 'a'      -> produce 'r' en membrana de salida.
    En max_paralelo genera b^(n//divisor) y r^(n%divisor).
    """
    sistema = SistemaP(membrana_salida='m_out')
    # membrana de salida
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    # membrana de trabajo con el contador 'a'
    m1 = Membrana('m1', {'a': n})
    m1.agregar_regla(Regla({'a': divisor}, {'b_out': 1}, prioridad=2))
    m1.agregar_regla(Regla({'a': 1}, {'r_out': 1}, prioridad=1))
    sistema.agregar_membrana(m1, parent_id='m_out')
    return sistema


def suma(n: int, m: int) -> SistemaP:
    """
    Suma n 'a' + m 'b':
      - Pri 1: consume 1 'a' -> produce 1 'c' en salida.
      - Pri 1: consume 1 'b' -> produce 1 'c' en salida.
    En max_paralelo produce c^(n+m).
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1}, {'c_out': 1}, prioridad=1))
    mem.agregar_regla(Regla({'b': 1}, {'c_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def resta(n: int, m: int) -> SistemaP:
    """
    Resta n - m:
      - Pri 3: consume 1 'a'+1 'b' -> empareja (no produce).
      - Pri 2: consume 1 'a'      -> produce 'd' en salida si n>m.
      - Pri 1: consume 1 'b'      -> produce 'e' en salida si m>n.
    En max_paralelo empareja, luego produce d^(n-m) o e^(m-n).
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1, 'b': 1}, {}, prioridad=3))
    mem.agregar_regla(Regla({'a': 1}, {'d_out': 1}, prioridad=2))
    mem.agregar_regla(Regla({'b': 1}, {'e_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def paridad(n: int) -> SistemaP:
    """
    Paridad de n 'a':
      - Pri 2: consume 2 'a' -> produce nada (empareja).
      - Pri 1: consume 1 'a' -> produce 'i' en salida.
    En max_paralelo genera p^(n//2) (emparejamientos) y un 'i' si n es impar.
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': 2}, {}, prioridad=2))
    mem.agregar_regla(Regla({'a': 1}, {'i_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def duplicar(n: int) -> SistemaP:
    """
    Duplica contador n:
      - Pri 1: consume 1 'a' -> produce 2 'b' en salida.
    En max_paralelo produce 2n 'b'.
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': 1}, {'b_out': 2}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def comparacion(n: int, m: int) -> SistemaP:
    """
    Compara n y m:
      - Pri 3: consume 1 'a'+1 'b' -> empareja.
      - Pri 2: consume 1 'a' -> produce 'g' en salida;
                consume 1 'b' -> produce 'l' en salida.
      - Pri 1: consume 0     -> produce 'e' en salida.
    En max_paralelo empareja, luego produce g/l o e.
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n, 'b': m})
    mem.agregar_regla(Regla({'a': 1, 'b': 1}, {}, prioridad=3))
    mem.agregar_regla(Regla({'a': 1}, {'g_out': 1}, prioridad=2))
    mem.agregar_regla(Regla({'b': 1}, {'l_out': 1}, prioridad=2))
    mem.agregar_regla(Regla({}, {'e_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def modulo(n: int, m: int) -> SistemaP:
    """
    Resto de n mod m:
      - Pri 2: consume m 'a' -> empareja (descarta bloques completos).
      - Pri 1: consume 1 'a' -> produce 'r' en salida.
    En max_paralelo genera r^(n%m).
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': m}, {}, prioridad=2))
    mem.agregar_regla(Regla({'a': 1}, {'r_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema


def umbral(n: int, k: int) -> SistemaP:
    """
    Test de umbral k en n:
      - Pri 2: consume k 'a' -> produce 't' en salida.
      - Pri 1: consume 0     -> produce 'f' en salida.
    En max_paralelo, si n>=k produce t; si n<k produce f.
    """
    sistema = SistemaP(membrana_salida='m_out')
    m_out = Membrana('m_out', {})
    sistema.agregar_membrana(m_out)
    mem = Membrana('m1', {'a': n})
    mem.agregar_regla(Regla({'a': k}, {'t_out': 1}, prioridad=2))
    mem.agregar_regla(Regla({}, {'f_out': 1}, prioridad=1))
    sistema.agregar_membrana(mem, parent_id='m_out')
    return sistema
