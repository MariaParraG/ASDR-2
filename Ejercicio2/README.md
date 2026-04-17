# Análisis Sintáctico Descendente - ASD
## Ejercicio 2 — Gramática y Análisis LL(1)

---

## Gramática Original

```
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
```

---

## a) Conjuntos de PRIMEROS

La gramática tiene **recursividad mutua indirecta**: S → B → A → S.
Por eso los PRIMEROS se calculan por punto fijo (iteración hasta estabilización).

| No Terminal | PRIMERO |
|-------------|---------|
| C | { siete, ε } |
| A | { uno, dos, tres, cuatro, cinco, siete, ε } |
| B | { uno, dos, tres, cuatro, cinco, siete, ε } |
| S | { uno, dos, tres, cuatro, cinco, siete, ε } |

**Razonamiento:**
- `C → siete B | ε` → PRIMERO(C) = { siete, ε }
- `B → A cinco C seis | ε`: si A→ε el primer símbolo visible es **cinco**, más PRIMERO(A)
- `A → S tres B C | cuatro | ε`: si S→ε el primer símbolo visible es **tres**, más PRIMERO(S)
- `S → B uno | dos C | ε`: si B→ε el primer símbolo visible es **uno**, más PRIMERO(B)

Por la recursividad mutua, S, A y B terminan compartiendo todos los terminales.

---

## b) Conjuntos de SIGUIENTES

| No Terminal | SIGUIENTES |
|-------------|------------|
| S | { tres, $ } |
| A | { cinco } |
| B | { uno, cinco, siete } |
| C | { tres, cinco, seis, $ } |

**Detalles:**
- `SIGUIENTES(S)`: símbolo inicial → {$}; en `A → S tres B C` → {**tres**}
- `SIGUIENTES(A)`: en `B → A cinco C seis` → {**cinco**}
- `SIGUIENTES(B)`: en `S → B uno` → {**uno**}; en `A → S tres B C` → PRIMERO(C)\{ε}={siete} ∪ SIGUIENTES(A)={cinco}
- `SIGUIENTES(C)`: en `S → dos C` → SIGUIENTES(S)={tres,$}; en `A → S tres B C` → SIGUIENTES(A)={cinco}; en `B → A cinco C seis` → {**seis**}

---

## c) Conjuntos de Predicción

| Regla | Conjunto de Predicción |
|-------|------------------------|
| S → B uno | { uno, dos, tres, cuatro, cinco, siete } |
| S → dos C | { dos } |
| S → ε | { tres, $ } |
| A → S tres B C | { uno, dos, tres, cuatro, cinco, siete } |
| A → cuatro | { cuatro } |
| A → ε | { cinco } |
| B → A cinco C seis | { uno, dos, tres, cuatro, cinco, siete } |
| B → ε | { uno, cinco, siete } |
| C → siete B | { siete } |
| C → ε | { tres, cinco, seis, $ } |

---

## d) ¿Es LL(1)?

| No Terminal | Conflicto | ¿Disjuntos? |
|-------------|-----------|-------------|
| S | "dos" en S→B uno y S→dos C; "tres" en S→B uno y S→ε | ❌ |
| A | "cuatro" en A→S tres B C y A→cuatro; "cinco" en A→S tres B C y A→ε | ❌ |
| B | "uno", "cinco", "siete" en B→A cinco C seis y B→ε | ❌ |
| C | { siete } ∩ { tres, cinco, seis, $ } = ∅ | ✅ |

### Conclusión

> ❌ **La gramática NO es LL(1).**
>
> La causa raíz es la **recursividad mutua indirecta** S → B → A → S, que hace que los
> conjuntos de PRIMEROS de S, A y B sean casi idénticos, generando conflictos masivos
> en los conjuntos de predicción de esos tres no terminales.

---

## e) Implementación del ASDR

Ver archivo `asdr.py` para la implementación completa.

### Uso

```bash
python asdr_ej2.py
```

### Notas de implementación

- Se implementa una función por cada no terminal: `S`, `A`, `B`, `C`.
- Todos los conflictos LL(1) están marcados con comentarios `[CONFLICTO]`.
- Para los conflictos se aplica una heurística: se prioriza la producción más específica
  (ej. `S → dos C` sobre `S → B uno` cuando el token es "dos").
- El analizador incluye un límite de profundidad para evitar recursión infinita
  causada por la recursividad mutua.

---

## Referencias

- Lenguajes de Programación — Procesadores de Lenguaje
- Universidad Sergio Arboleda
