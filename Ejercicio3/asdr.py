"""
Analizador Sintáctico Descendente Recursivo (ASDR) — Ejercicio 3
=================================================================
Gramática original:

    S → A B C
    S → S uno          ← recursividad izquierda directa

Gramática transformada (sin recursividad izquierda):

    S  → A B C S'
    S' → uno S' | ε
    A  → dos B C
    A  → ε
    B  → C tres
    B  → ε
    C  → cuatro B
    C  → ε

⚠️  La gramática NO es LL(1).
    Conflictos en B y C, documentados abajo.
    Se resuelven con heurísticas y backtracking local.
"""

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

TERMINALES = {"uno", "dos", "tres", "cuatro"}
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

PRED = {
    # S — única producción, sin conflicto
    "S_main":   {"dos", "cuatro", "tres", "uno", EOF},

    # S'
    "Sp_uno":   {"uno"},
    "Sp_eps":   {EOF},

    # A
    "A_dos":    {"dos"},
    "A_eps":    {"cuatro", "tres", "uno", EOF},

    # B — CONFLICTO: {cuatro, tres} en ambas
    "B_C_tres": {"cuatro", "tres"},
    "B_eps":    {"cuatro", "tres", "uno", EOF},

    # C — CONFLICTO: {cuatro} en ambas
    "C_cuatro": {"cuatro"},
    "C_eps":    {"cuatro", "tres", "uno", EOF},
}

# ---------------------------------------------------------------------------
# Funciones del ASDR
# ---------------------------------------------------------------------------

def S():
    """
    S → A B C S'   [PRED: {dos, cuatro, tres, uno, $}]

    Una sola producción (después de eliminar recursividad izquierda).
    Sin conflicto LL(1) en S. ✅
    """
    global depth
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}S()  token='{t}'")

    if t in PRED["S_main"]:
        print(f"{'  ' * depth}  → S → A B C S'")
        A(); B(); C(); Sp()
    else:
        raise SyntaxError(f"Error sintáctico en S: token inesperado '{t}'")

    depth -= 1


def Sp():
    """
    S' → uno S'   [PRED: {uno}]
    S' → ε        [PRED: {$}]

    Sin conflicto LL(1). ✅
    """
    global depth
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}S'()  token='{t}'")

    if t in PRED["Sp_uno"]:
        print(f"{'  ' * depth}  → S' → uno S'")
        match("uno"); Sp()
    elif t in PRED["Sp_eps"]:
        print(f"{'  ' * depth}  → S' → ε")
    else:
        raise SyntaxError(f"Error sintáctico en S': token inesperado '{t}'")

    depth -= 1


def A():
    """
    A → dos B C   [PRED: {dos}]
    A → ε         [PRED: {cuatro, tres, uno, $}]

    Sin conflicto LL(1). ✅
    """
    global depth
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}A()  token='{t}'")

    if t in PRED["A_dos"]:
        print(f"{'  ' * depth}  → A → dos B C")
        match("dos"); B(); C()
    elif t in PRED["A_eps"]:
        print(f"{'  ' * depth}  → A → ε")
    else:
        raise SyntaxError(f"Error sintáctico en A: token inesperado '{t}'")

    depth -= 1


def B():
    """
    B → C tres   [PRED: {cuatro, tres}]
    B → ε        [PRED: {cuatro, tres, uno, $}]

    *** CONFLICTO LL(1): {cuatro, tres} aparecen en ambas producciones ***

    Estrategia con backtracking local:
    - Si el token es 'cuatro' o 'tres', intentamos B → C tres.
      Si C consume algo y luego falla al buscar 'tres', retrocedemos a B → ε.
    - Si el token es 'uno' o '$', solo aplica B → ε.
    """
    global depth, pos
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}B()  token='{t}'")

    if t in {"cuatro", "tres"}:
        # Intentamos B → C tres con backtracking
        saved_pos = pos
        try:
            print(f"{'  ' * depth}  → B → C tres  [intento, token='{t}']")
            C(); match("tres")
            print(f"{'  ' * depth}  B → C tres exitoso")
        except SyntaxError:
            # Retrocedemos y aplicamos B → ε
            pos = saved_pos
            print(f"{'  ' * depth}  → B → ε  [backtrack desde B→C tres, [CONFLICTO]]")
    else:
        # 'uno' o '$': solo B → ε
        print(f"{'  ' * depth}  → B → ε")

    depth -= 1


def C():
    """
    C → cuatro B   [PRED: {cuatro}]
    C → ε          [PRED: {cuatro, tres, uno, $}]

    *** CONFLICTO LL(1): 'cuatro' aparece en ambas producciones ***

    Heurística: preferir C → cuatro B cuando el token es 'cuatro',
    ya que la producción C → ε con 'cuatro' significaría ignorar
    un token válido que sí puede ser consumido.
    """
    global depth
    depth += 1
    t = token_actual()
    print(f"{'  ' * depth}C()  token='{t}'")

    if t == "cuatro":
        # [CONFLICTO] 'cuatro' en ambas; priorizamos C → cuatro B
        print(f"{'  ' * depth}  → C → cuatro B  [heurística: consumir 'cuatro']")
        match("cuatro"); B()
    elif t in {"tres", "uno", EOF}:
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


# ---------------------------------------------------------------------------
# Casos de prueba
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    casos = [
        # (descripción,                                          cadena)
        ("S → ε  (A→ε, B→ε, C→ε, S'→ε)",                      ""),
        ("S → A B C S', A→ε, B→ε, C→ε, S'→uno S'→ε",          "uno"),
        ("S → A B C S', A→dos B C",                             "dos"),
        ("C → cuatro B, B → ε",                                 "cuatro"),
        ("B → C tres, C → ε",                                   "tres"),
        ("C → cuatro B, B → C tres, C → ε",                    "cuatro tres"),
        ("dos cuatro tres uno (A→dos B C, B→C tres, C→cuatro B, S'→uno)", "dos cuatro tres uno"),
        ("Recursividad: S' → uno uno",                          "uno uno"),
        ("Cadena inválida",                                      "tres dos"),
    ]

    print("ANALIZADOR SINTÁCTICO DESCENDENTE RECURSIVO — EJERCICIO 3")
    print("Gramática sin recursividad izquierda (S' introducido)")

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
