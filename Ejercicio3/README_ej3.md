# Análisis Sintáctico Descendente - ASD
## Ejercicio 3 — Gramática y Análisis LL(1)

---

## Gramática Original

```
S → A B C
S → S uno
A → dos B C
A → ε
B → C tres
B → ε
C → cuatro B
C → ε
```

---

## a) Eliminar Recursividad por la Izquierda

La única producción con **recursividad izquierda directa** es:

```
S → S uno | A B C
```

- Parte recursiva (α): `uno`
- Parte no recursiva (β): `A B C`

Aplicando la transformación estándar:

```
S  → A B C S'
S' → uno S' | ε
```

### Gramática Resultante (sin recursividad izquierda)

```
S  → A B C S'
S' → uno S' | ε
A  → dos B C
A  → ε
B  → C tres
B  → ε
C  → cuatro B
C  → ε
```

---

## b) Conjuntos de PRIMEROS

| No Terminal | PRIMERO |
|-------------|---------|
| C  | { cuatro, ε } |
| B  | { cuatro, tres, ε } |
| A  | { dos, ε } |
| S' | { uno, ε } |
| S  | { dos, cuatro, tres, uno, ε } |

**Detalles:**
- `PRIMERO(C)`: C→cuatro B → {cuatro}; C→ε → {ε}
- `PRIMERO(B)`: B→C tres → PRIMERO(C)\{ε}={cuatro}, si C→ε → {tres}; B→ε → {ε}
- `PRIMERO(A)`: A→dos B C → {dos}; A→ε → {ε}
- `PRIMERO(S')`: S'→uno S' → {uno}; S'→ε → {ε}
- `PRIMERO(S)`: S→A B C S' → encadena PRIMEROS de A,B,C,S' con propagación de ε

---

## c) Conjuntos de SIGUIENTES

| No Terminal | SIGUIENTES |
|-------------|------------|
| S  | { $ } |
| S' | { $ } |
| A  | { cuatro, tres, uno, $ } |
| B  | { cuatro, tres, uno, $ } |
| C  | { cuatro, tres, uno, $ } |

**Detalles:**
- `SIGUIENTES(S)` = { $ } (símbolo inicial)
- `SIGUIENTES(S')`: en S→A B C **S'** → SIGUIENTES(S)={$}
- `SIGUIENTES(A)`: en S→**A** B C S' → PRIMERO(B C S')\{ε} con propagación hasta SIGUIENTES(S)
- `SIGUIENTES(B)`: en A→dos **B** C → PRIMERO(C)\{ε} ∪ SIGUIENTES(A); en C→cuatro **B** → SIGUIENTES(C)
- `SIGUIENTES(C)`: en A→dos B **C** → SIGUIENTES(A); en S→A B **C** S' → PRIMERO(S')\{ε} ∪ SIGUIENTES(S); en B→**C** tres → {tres}

---

## d) Conjuntos de Predicción

| Regla | Conjunto de Predicción |
|-------|------------------------|
| S → A B C S'   | { dos, cuatro, tres, uno, $ } |
| S' → uno S'    | { uno } |
| S' → ε         | { $ } |
| A → dos B C    | { dos } |
| A → ε          | { cuatro, tres, uno, $ } |
| B → C tres     | { cuatro, tres } |
| B → ε          | { cuatro, tres, uno, $ } |
| C → cuatro B   | { cuatro } |
| C → ε          | { cuatro, tres, uno, $ } |

---

## e) ¿Es LL(1)?

| No Terminal | Intersección entre predicciones | ¿Disjuntos? |
|-------------|----------------------------------|-------------|
| S  | única producción | ✅ |
| S' | {uno} ∩ {$} = ∅ | ✅ |
| A  | {dos} ∩ {cuatro, tres, uno, $} = ∅ | ✅ |
| B  | {cuatro, tres} ∩ {cuatro, tres, uno, $} = **{cuatro, tres}** | ❌ |
| C  | {cuatro} ∩ {cuatro, tres, uno, $} = **{cuatro}** | ❌ |

### Conclusión

> ❌ **La gramática NO es LL(1).**
>
> Existen conflictos en **B** y **C**:
>
> - **B**: `cuatro` y `tres` pertenecen a PRED(B→C tres) y también a PRED(B→ε),
>   porque C puede derivar ε haciendo que `tres` sea visible como primer símbolo de B→C tres,
>   y a la vez `cuatro` y `tres` son SIGUIENTES de B.
>
> - **C**: `cuatro` pertenece a PRED(C→cuatro B) y también a PRED(C→ε),
>   porque `cuatro` aparece en SIGUIENTES(C) al poder ir seguido de otro C.

---

## f) Implementación del ASDR

Ver archivo `asdr_ej3.py` para la implementación completa.

### Uso

```bash
python asdr_ej3.py
```

### Notas de implementación

- Se implementa una función por cada no terminal: `S`, `Sp` (S'), `A`, `B`, `C`.
- Los conflictos en B y C están marcados con `[CONFLICTO]` y se resuelven con heurísticas:
  - **B**: se intenta B→C tres cuando el lookahead es `cuatro` o `tres`, priorizando
    la producción no vacía; si falla se retrocede a B→ε.
  - **C**: se intenta C→cuatro B solo cuando el token es exactamente `cuatro`.
- Se usa backtracking local (try/except) para manejar los conflictos de forma más robusta.

---

## Referencias

- Lenguajes de Programación — Procesadores de Lenguaje
- Universidad Sergio Arboleda
