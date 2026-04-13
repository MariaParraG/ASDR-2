"""
Analizador Sintáctico Descendente Recursivo (ASDR)
===================================================
Gramática (sin recursividad izquierda):

    S  → A B C
    S  → D E
    A  → dos B tres
    A  → ε
    B  → B'
    B' → cuatro C cinco B' | ε
    C  → seis A B
    C  → ε
    D  → uno A E
    D  → B
    E  → tres

NOTA: La gramática NO es LL(1).
Los conjuntos de predicción de S→ABC y S→DE comparten el terminal "cuatro".
El conflicto está marcado en la función S() con un comentario.
"""

# ---------------------------------------------------------------------------
# Léxico / tokenizador simple
# ---------------------------------------------------------------------------

TERMINALES = {"uno", "dos", "tres", "cuatro", "cinco", "seis"}
EOF = "$"


def tokenizar(cadena: str) -> list:
    """Convierte una cadena de texto en una lista de tokens + '$'."""
    tokens = cadena.strip().split()
    tokens.append(EOF)
    return tokens


# ---------------------------------------------------------------------------
# Estado global del analizador
# ---------------------------------------------------------------------------

tokens: list = []
pos: int = 0


def token_actual() -> str:
    return tokens[pos]


def avanzar():
    global pos
    pos += 1


def match(esperado: str):
    """Consume el token actual si coincide con el esperado; si no, lanza error."""
    if token_actual() == esperado:
        print(f"  match('{esperado}')")
        avanzar()
    else:
        raise SyntaxError(
            f"Error sintáctico: se esperaba '{esperado}' pero se encontró '{token_actual()}'"
        )


# ---------------------------------------------------------------------------
# Conjuntos de predicción (para referencia y decisión)
# ---------------------------------------------------------------------------

PRED = {
    "S_ABC": {"dos", "cuatro", "seis", EOF},
    "S_DE":  {"uno", "cuatro", "tres"},   # "cuatro" también aparece en S_ABC → CONFLICTO LL(1)
    "A_dos": {"dos"},
    "A_eps": {"cuatro", "seis", "tres", "cinco", EOF},
    "Bp_cuatro": {"cuatro"},
    "Bp_eps":    {"seis", "cinco", "tres", EOF},
    "C_seis": {"seis"},
    "C_eps":  {"cinco", EOF},
    "D_uno": {"uno"},
    "D_B":   {"cuatro", "tres"},
}


# ---------------------------------------------------------------------------
# Funciones del ASDR (una por no terminal)
# ---------------------------------------------------------------------------

def S():
    """
    S → A B C  [PRED: {dos, cuatro, seis, $}]
    S → D E    [PRED: {uno, cuatro, tres}]

    *** CONFLICTO LL(1): 'cuatro' pertenece a ambos conjuntos ***
    Se resuelve aquí priorizando S→DE cuando el token sea 'uno' o 'tres',
    y S→ABC en los demás casos admisibles. Para 'cuatro' la decisión es
    arbitraria y evidencia que la gramática NO es LL(1).
    """
    print("S()")
    t = token_actual()

    if t in {"uno", "tres"}:
        # Solo compatible con S → D E
        D(); E()
    elif t in {"dos", "seis", EOF}:
        # Solo compatible con S → A B C
        A(); B(); C()
    elif t == "cuatro":
        # *** CONFLICTO *** : elegimos S → A B C (decisión arbitraria)
        print("  [ADVERTENCIA] Conflicto LL(1) en 'cuatro': eligiendo S → A B C")
        A(); B(); C()
    else:
        raise SyntaxError(
            f"Error sintáctico en S: token inesperado '{t}'"
        )


def A():
    """
    A → dos B tres  [PRED: {dos}]
    A → ε           [PRED: {cuatro, seis, tres, cinco, $}]
    """
    print("A()")
    t = token_actual()

    if t in PRED["A_dos"]:
        match("dos"); B(); match("tres")
    elif t in PRED["A_eps"]:
        print("  A → ε")
    else:
        raise SyntaxError(f"Error sintáctico en A: token inesperado '{t}'")


def B():
    """B → B'"""
    print("B()")
    Bp()


def Bp():
    """
    B' → cuatro C cinco B'  [PRED: {cuatro}]
    B' → ε                   [PRED: {seis, cinco, tres, $}]
    """
    print("B'()")
    t = token_actual()

    if t in PRED["Bp_cuatro"]:
        match("cuatro"); C(); match("cinco"); Bp()
    elif t in PRED["Bp_eps"]:
        print("  B' → ε")
    else:
        raise SyntaxError(f"Error sintáctico en B': token inesperado '{t}'")


def C():
    """
    C → seis A B  [PRED: {seis}]
    C → ε         [PRED: {cinco, $}]
    """
    print("C()")
    t = token_actual()

    if t in PRED["C_seis"]:
        match("seis"); A(); B()
    elif t in PRED["C_eps"]:
        print("  C → ε")
    else:
        raise SyntaxError(f"Error sintáctico en C: token inesperado '{t}'")


def D():
    """
    D → uno A E  [PRED: {uno}]
    D → B        [PRED: {cuatro, tres}]
    """
    print("D()")
    t = token_actual()

    if t in PRED["D_uno"]:
        match("uno"); A(); E()
    elif t in PRED["D_B"]:
        B()
    else:
        raise SyntaxError(f"Error sintáctico en D: token inesperado '{t}'")


def E():
    """E → tres"""
    print("E()")
    match("tres")


# ---------------------------------------------------------------------------
# Función principal del analizador
# ---------------------------------------------------------------------------

def analizar(cadena: str) -> bool:
    """
    Intenta analizar la cadena dada.
    Retorna True si es aceptada, False si contiene errores sintácticos.
    """
    global tokens, pos
    tokens = tokenizar(cadena)
    pos = 0

    print(f"\n{'='*60}")
    print(f"Analizando: {cadena!r}")
    print(f"Tokens: {tokens}")
    print(f"{'='*60}")

    try:
        S()
        if token_actual() == EOF:
            print("\n✅ CADENA ACEPTADA")
            return True
        else:
            print(f"\n❌ CADENA RECHAZADA: tokens sobrantes a partir de '{token_actual()}'")
            return False
    except SyntaxError as e:
        print(f"\n❌ CADENA RECHAZADA: {e}")
        return False


# ---------------------------------------------------------------------------
# Casos de prueba
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    casos = [
        # Descripción,                    Cadena de entrada
        ("S → ε (todo vacío)",            ""),
        ("S → A B C con A=dos B tres",    "dos tres"),
        ("S → D E con D=uno A E",         "uno tres"),
        ("S → D E con D=B=B'=cuatro...",  "cuatro cinco tres"),
        ("S → A B C con B=cuatro C cinco","cuatro cinco"),
        ("Cadena con seis (C→seis A B)",  "seis"),
        ("Cadena inválida",               "cinco dos"),
    ]

    print("ANALIZADOR SINTÁCTICO DESCENDENTE RECURSIVO")
    print("Gramática del Ejercicio 1 (sin recursividad izquierda)")

    resultados = []
    for desc, cadena in casos:
        ok = analizar(cadena)
        resultados.append((desc, cadena, ok))

    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    for desc, cadena, ok in resultados:
        estado = "✅ ACEPTADA" if ok else "❌ RECHAZADA"
        print(f"  {estado}  [{desc}]  → tokens: {cadena!r}")

    # Modo interactivo
    print("\n" + "="*60)
    print("MODO INTERACTIVO")
    print("Ingresa tokens separados por espacios (ej: uno dos tres)")
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
