"""
Analizador Sintáctico Descendente Recursivo (ASDR) — Ejercicio 2
=================================================================
Gramática:

    S → B uno
    S → dos C
    S → ε
    A → S tres B C
    A → cuatro
    A → ε
    B → A cinco C seis
    B → ε
    C → siete B
    C → ε

⚠️  La gramática NO es LL(1).
    Hay recursividad mutua indirecta: S → B → A → S
    Los conflictos están marcados con [CONFLICTO] en el código.
    Se usa un límite de profundidad para evitar recursión infinita.
"""

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

MAX_DEPTH = 20   # límite de profundidad para evitar recursión infinita
TERMINALES = {"uno", "dos", "tres", "cuatro", "cinco", "seis", "siete"}
EOF = "$"


# ---------------------------------------------------------------------------
# Tokenizador
# ---------------------------------------------------------------------------

def tokenizar(cadena: str) -> list:
    """Convierte una cadena de texto en lista de tokens + '$'."""
    tokens = cadena.strip().split()
    tokens.append(EOF)
    return tokens


# ---------------------------------------------------------------------------
# Estado global del analizador
# ---------------------------------------------------------------------------

tokens: list = []
pos: int = 0
depth: int = 0


def token_actual() -> str:
    return tokens[pos]


def avanzar():
    global pos
    pos += 1


def match(esperado: str):
    if token_actual() == esperado:
        print(f"{'  ' * depth}match('{esperado}')")
        avanzar()
    else:
        raise SyntaxError(
            f"Error sintáctico: se esperaba '{esperado}' "
            f"pero se encontró '{token_actual()}'"
        )


# ---------------------------------------------------------------------------
# Conjuntos de predicción (referencia)
# ---------------------------------------------------------------------------

# Todos los terminales de la gramática
TODOS = {"uno", "dos", "tres", "cuatro", "cinco", "siete"}

PRED = {
    # S
    "S_B_uno":  {"uno", "dos", "tres", "cuatro", "cinco", "siete"},  # CONFLICTO con S_dos_C y S_eps
    "S_dos_C":  {"dos"},
    "S_eps":    {"tres", EOF},

    # A
    "A_S_tres": {"uno", "dos", "tres", "cuatro", "cinco", "siete"},  # CONFLICTO con A_cuatro y A_eps
    "A_cuatro": {"cuatro"},
    "A_eps":    {"cinco"},

    # B
    "B_A_cinco": {"uno", "dos", "tres", "cuatro", "cinco", "siete"}, # CONFLICTO con B_eps
    "B_eps":     {"uno", "cinco", "siete"},

    # C — sin conflicto ✅
    "C_siete":  {"siete"},
    "C_eps":    {"tres", "cinco", "seis", EOF},
}


# ---------------------------------------------------------------------------
# Funciones del ASDR
# ---------------------------------------------------------------------------

def S():
    """
    S → B uno    [PRED: {uno, dos, tres, cuatro, cinco, siete}]
    S → dos C    [PRED: {dos}]
    S → ε        [PRED: {tres, $}]

    [CONFLICTO] "dos"  aparece en S→B uno y S→dos C
    [CONFLICTO] "tres" aparece en S→B uno y S→ε
    Heurística: priorizar producciones específicas antes que la general S→B uno.
    """
    global depth
    depth += 1
    if depth > MAX_DEPTH:
        depth -= 1
        raise RecursionError("Profundidad máxima alcanzada (recursividad mutua S↔B↔A)")

    t = token_actual()
    print(f"{'  ' * depth}S()  token='{t}'")

    if t == "dos":
        # [CONFLICTO] "dos" también en S→B uno, pero priorizamos S→dos C
        print(f"{'  ' * depth}  → S → dos C  [heurística: específica]")
        match("dos"); C()
    elif t in {"tres", EOF}:
        # Solo compatible con S→ε
        print(f"{'  ' * depth}  → S → ε")
    elif t in {"uno", "cuatro", "cinco", "siete"}:
        # Solo compatible con S→B uno (no hay otra opción)
        print(f"{'  ' * depth}  → S → B uno")
        B(); match("uno")
    else:
        raise SyntaxError(f"Error sintáctico en S: token inesperado '{t}'")

    depth -= 1


def A():
    """
    A → S tres B C  [PRED: {uno, dos, tres, cuatro, cinco, siete}]
    A → cuatro      [PRED: {cuatro}]
    A → ε           [PRED: {cinco}]

    [CONFLICTO] "cuatro" aparece en A→S tres B C y A→cuatro
    [CONFLICTO] "cinco"  aparece en A→S tres B C y A→ε
    Heurística: priorizar A→cuatro y A→ε cuando el token sea exactamente esos.
    """
    global depth
    depth += 1
    if depth > MAX_DEPTH:
        depth -= 1
        raise RecursionError("Profundidad máxima alcanzada (recursividad mutua S↔B↔A)")

    t = token_actual()
    print(f"{'  ' * depth}A()  token='{t}'")

    if t == "cuatro":
        # [CONFLICTO] "cuatro" también en A→S tres B C, priorizamos A→cuatro
        print(f"{'  ' * depth}  → A → cuatro  [heurística: específica]")
        match("cuatro")
    elif t == "cinco":
        # [CONFLICTO] "cinco" también en A→S tres B C, priorizamos A→ε
        print(f"{'  ' * depth}  → A → ε  [heurística: SIGUIENTES]")
    elif t in {"uno", "dos", "tres", "siete"}:
        print(f"{'  ' * depth}  → A → S tres B C")
        S(); match("tres"); B(); C()
    else:
        raise SyntaxError(f"Error sintáctico en A: token inesperado '{t}'")

    depth -= 1


def B():
    """
    B → A cinco C seis  [PRED: {uno, dos, tres, cuatro, cinco, siete}]
    B → ε               [PRED: {uno, cinco, siete}]

    [CONFLICTO] "uno", "cinco", "siete" aparecen en ambas producciones
    Heurística: B→ε cuando el token sea uno de los SIGUIENTES(B) y no haya
    otra señal; B→A cinco C seis solo si hay tokens "productivos" disponibles.
    Como B→ε es más seguro ante la recursividad mutua, se prioriza B→ε
    para "uno" y "siete"; se intenta B→A cinco C seis para los demás.
    """
    global depth
    depth += 1
    if depth > MAX_DEPTH:
        depth -= 1
        raise RecursionError("Profundidad máxima alcanzada (recursividad mutua S↔B↔A)")

    t = token_actual()
    print(f"{'  ' * depth}B()  token='{t}'")

    if t in {"uno", "siete", EOF}:
        # Priorizamos B→ε (son SIGUIENTES(B) claros)
        print(f"{'  ' * depth}  → B → ε  [heurística: SIGUIENTES]")
    elif t == "cinco":
        # [CONFLICTO] "cinco" en ambas; como A→ε ante "cinco", B→A cinco... derivaría
        # A→ε y luego match("cinco"), lo que es válido. Lo intentamos.
        print(f"{'  ' * depth}  → B → A cinco C seis")
        A(); match("cinco"); C(); match("seis")
    elif t in {"dos", "tres", "cuatro"}:
        print(f"{'  ' * depth}  → B → A cinco C seis")
        A(); match("cinco"); C(); match("seis")
    else:
        raise SyntaxError(f"Error sintáctico en B: token inesperado '{t}'")

    depth -= 1


def C():
    """
    C → siete B  [PRED: {siete}]
    C → ε        [PRED: {tres, cinco, seis, $}]

    ✅ Sin conflicto LL(1)
    """
    global depth
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}C()  token='{t}'")

    if t == "siete":
        print(f"{'  ' * depth}  → C → siete B")
        match("siete"); B()
    elif t in PRED["C_eps"]:
        print(f"{'  ' * depth}  → C → ε")
    else:
        raise SyntaxError(f"Error sintáctico en C: token inesperado '{t}'")

    depth -= 1


# ---------------------------------------------------------------------------
# Función principal del analizador
# ---------------------------------------------------------------------------

def analizar(cadena: str) -> bool:
    global tokens, pos, depth
    tokens = tokenizar(cadena)
    pos = 0
    depth = 0

    print(f"\n{'='*60}")
    print(f"Analizando: {cadena!r}")
    print(f"Tokens:     {tokens}")
    print(f"{'='*60}")

    try:
        S()
        if token_actual() == EOF:
            print("\n✅ CADENA ACEPTADA")
            return True
        else:
            print(f"\n❌ CADENA RECHAZADA: tokens sobrantes desde '{token_actual()}'")
            return False
    except SyntaxError as e:
        print(f"\n❌ CADENA RECHAZADA: {e}")
        return False
    except RecursionError as e:
        print(f"\n❌ CADENA RECHAZADA: {e}")
        return False


# ---------------------------------------------------------------------------
# Casos de prueba
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    casos = [
        # (descripción,                              cadena)
        ("S → ε",                                   ""),
        ("S → dos C, C → ε",                        "dos"),
        ("S → dos C, C → siete B, B → ε",           "dos siete"),
        ("S → B uno, B → ε",                        "uno"),
        ("S → B uno, B → A cinco C seis, A → ε, C → ε", "cinco seis uno"),
        ("S → B uno, B → A cinco C seis, A → cuatro, C → ε", "cuatro cinco seis uno"),
        ("A → S tres B C completo",                 "tres"),
        ("Cadena inválida",                          "seis dos"),
    ]

    print("ANALIZADOR SINTÁCTICO DESCENDENTE RECURSIVO — EJERCICIO 2")
    print("Gramática con recursividad mutua S ↔ B ↔ A (no LL(1))")

    resultados = []
    for desc, cadena in casos:
        ok = analizar(cadena)
        resultados.append((desc, cadena, ok))

    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    for desc, cadena, ok in resultados:
        estado = "✅ ACEPTADA " if ok else "❌ RECHAZADA"
        etiqueta = f"'{cadena}'" if cadena else "'ε'"
        print(f"  {estado}  [{desc}]  → {etiqueta}")

    # Modo interactivo
    print("\n" + "="*60)
    print("MODO INTERACTIVO")
    print("Tokens válidos:", ", ".join(sorted(TERMINALES)))
    print("Escribe 'salir' para terminar.")
    print("="*60)

    while True:
        try:
            entrada = input("\nCadena: ").strip()
            if entrada.lower() == "salir":
                break
            analizar(entrada)
        except KeyboardInterrupt:
            break

    print("\nFin del analizador.")
