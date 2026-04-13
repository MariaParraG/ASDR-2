# Análisis Sintáctico Descendente - ASD
## Ejercicio 1 — Gramática y Análisis LL(1)

---

## Gramática Original

```
S → A B C
S → D E
A → dos B tres
A → ε
B → B cuatro C cinco
B → ε
C → seis A B
C → ε
D → uno A E
D → B
E → tres
```

---

## a) Eliminar Recursividad por la Izquierda

La única producción con **recursividad izquierda directa** es:

```
B → B cuatro C cinco | ε
```

Aplicando la transformación estándar:
- Parte recursiva (α): `cuatro C cinco`
- Parte no recursiva (β): `ε`

**Resultado de la transformación:**

```
B  → B'
B' → cuatro C cinco B' | ε
```

### Gramática Resultante (sin recursividad izquierda)

```
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
```

---

## b) Conjuntos de PRIMEROS

| No Terminal | PRIMERO |
|-------------|---------|
| E           | { tres } |
| A           | { dos, ε } |
| B'          | { cuatro, ε } |
| B           | { cuatro, ε } |
| C           | { seis, ε } |
| D           | { uno, cuatro, ε } |
| S           | { dos, cuatro, seis, uno, tres, ε } |

**Cálculo de PRIMERO(S):**
- De `A B C`: PRIMERO(A)={dos,ε} → A puede ser ε → PRIMERO(B)={cuatro,ε} → B puede ser ε → PRIMERO(C)={seis,ε} → C puede ser ε → ε ∈ PRIMERO(S)
- De `D E`: PRIMERO(D)={uno,cuatro,ε} → D puede ser ε → PRIMERO(E)={tres}

---

## c) Conjuntos de SIGUIENTES

| No Terminal | SIGUIENTES |
|-------------|------------|
| S           | { $ } |
| E           | { $ } |
| A           | { cuatro, seis, tres, cinco, $ } |
| B           | { seis, cinco, tres, $ } |
| B'          | { seis, cinco, tres, $ } |
| C           | { cinco, $ } |
| D           | { tres } |

**Detalles:**
- `SIGUIENTES(S) = { $ }` (símbolo inicial)
- `SIGUIENTES(E)`: en `S → D E`, SIGUIENTES(S) = { $ }
- `SIGUIENTES(C)`: en `S → A B C` → SIGUIENTES(S)={$}; en `B' → cuatro C cinco B'` → {cinco}
- `SIGUIENTES(B)`: en `S → A B C` → PRIMERO(C)\{ε} ∪ SIGUIENTES(S); en `C → seis A B` → SIGUIENTES(C); en `D → B` → SIGUIENTES(D)={tres}
- `SIGUIENTES(A)`: en `S → A B C` → {cuatro,seis,$}; en `D → uno A E` → {tres}; en `C → seis A B` → SIGUIENTES(B)
- `SIGUIENTES(D)`: en `S → D E` → PRIMERO(E) = { tres }

---

## d) Conjuntos de Predicción

| Regla | Conjunto de Predicción |
|-------|------------------------|
| S → A B C | { dos, cuatro, seis, $ } |
| S → D E   | { uno, cuatro, tres } |
| A → dos B tres | { dos } |
| A → ε | { cuatro, seis, tres, cinco, $ } |
| B → B' | { cuatro, seis, cinco, tres, $ } |
| B' → cuatro C cinco B' | { cuatro } |
| B' → ε | { seis, cinco, tres, $ } |
| C → seis A B | { seis } |
| C → ε | { cinco, $ } |
| D → uno A E | { uno } |
| D → B | { cuatro, tres } |
| E → tres | { tres } |

---

## e) ¿Es LL(1)?

Para que una gramática sea LL(1), los conjuntos de predicción de las reglas de un mismo no terminal deben ser **disjuntos**.

| No Terminal | Reglas | Intersección | ¿Disjuntos? |
|-------------|--------|--------------|-------------|
| S | S → A B C / S → D E | {cuatro} | ❌ |
| A | A → dos B tres / A → ε | ∅ | ✅ |
| B' | B'→ cuatro C cinco B' / B'→ ε | ∅ | ✅ |
| C | C → seis A B / C → ε | ∅ | ✅ |
| D | D → uno A E / D → B | ∅ | ✅ |

### Conclusión

> ❌ **La gramática NO es LL(1).**
>
> Los conjuntos de predicción de `S → A B C` y `S → D E` comparten el terminal **"cuatro"**.
> Esto ocurre porque `D → B → B' → ε`, lo que hace que "cuatro" pueda iniciar ambas alternativas
> de S, impidiendo la decisión determinista con un solo símbolo de lookahead.

---

## f) Implementación del ASDR

Ver archivo `asdr.py` para la implementación completa del Analizador Sintáctico Descendente Recursivo.

### Uso

```bash
python asdr.py
```

El programa incluye casos de prueba y permite ingresar cadenas de tokens manualmente.

---

## Referencias

- Lenguajes de Programación — Procesadores de Lenguaje
- Universidad Sergio Arboleda — Diapositiva 22
