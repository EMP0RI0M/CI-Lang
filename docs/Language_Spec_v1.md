# CI-LANG LANGUAGE SPECIFICATION v1.0 (STRICT)

## 1. Introduction
CI-Lang (Chaos Intelligence Language) is a domain-specific language designed for the runtime stabilization of distributed multi-agent systems via entropy-regulated feedback control.

---

## 2. Core Execution Model
The CI-Lang execution model differs from traditional imperative models:
- **Stateful Persistence**: All local variables are treated as persistent state within the VM registers.
- **Continuous Flow**: Value updates are ideally continuous (flow-based) rather than discrete point assignments.
- **Entropy Regulation**: The global `entropy_register` ($\lambda$) influences all adaptive operations ($≈, \rightarrow$) in real-time.
- **Homeostatic Memory**: The system accumulates a "Memory of Instability" ($M$) that modulates the aggressiveness of control signals.

---

## 3. Lexical Structure
### 3.1 Primary Syntax: Indentation
Indentation (4 spaces) is the primary method of block definition.
### 3.2 Secondary Syntax: Braces
Braces `{}` are maintained as a legacy block structure for compatibility with C-style code.
### 3.3 Semantic Aliasing
- `func` (Canonical) | `def` (Sugar)
- `let` (Canonical)  | `var` (Sugar)
- `class` (Canonical) | `struct` (Sugar)

### 3.4 Reserved Keywords
Users may NOT use the following as identifiers:
`agent`, `state`, `chaos`, `entropy`, `flux`, `spawn`, `volatility`, `push`, `reflect`, `system`, `adapt`, `to`, `if`, `while`, `else`, `return`, `func`, `def`, `let`, `var`, `class`, `struct`.

---

## 4. Operator Semantics
### 4.1 Comparison Operators
- `==` (**Exact Equality**): Returns `True` if and only if $A \equiv B$. Deterministic.
- `≈` (**Chaos-Aware Equality**): Evaluates equality within a tolerance window $\epsilon$ modulated by system entropy $\lambda$:
  $$A ≈ B \equiv |A - B| < (k_{toler} \cdot \lambda)$$

### 4.2 The Flow Operator (`→`)
- `x = A → B`: Directs the state of $x$ from value $A$ toward target $B$ with a damping factor modulated by system entropy. It is not an assignment, but a **Directional Pull**.
  $$x_{t+1} = x_t + (1 - \lambda)(target - x_t)$$

---

## 5. First-Class Citizens
### 5.1 Agents
The `agent` is the primary unit of execution.
```ci
agent A:
    state:
        val = 1.0
    update(dt):
        val = val → target
```

### 5.2 The Chaos Block
A `chaos` block signifies a region where the VM operates in **Non-Deterministic Mode**, allowing entropy to influence branching.

---

## 6. Target Hardware (FluxVM)
All CI-Lang code compiles to FluxVM Bytecode, which operates on three stack planes:
1. **Data Stack**: Numeric manipulation.
2. **Entropy Plane**: Regulatory control.
3. **Memory Plane**: Historical state retention.

---
**Status**: LOCKED (v1.0)
