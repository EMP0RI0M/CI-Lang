# CI-LANG VM & COMPILER INTERNALS (v1.0)

This document specifies the lower-level architecture of CI-Lang, intended for engine developers.

---

## 1. FluxVM Architecture
FluxVM is a **Three-Plane Stack Machine**:

### 1.1 Data Stack (Primary)
Standard FILO stack for floating-point and matrix operations.

### 1.2 Entropy Register ($\lambda$)
A hardware-level register that tracks global system disorder. Values range from `[0.0, 1.0]`. Instructions like `ARROW` (→) and `CH_EQ` (≈) are electrically coupled to this register.

### 1.3 Memory Register ($M$)
Accumulates the historical integral of entropy spikes to prevent "system amnesia" during prolonged volatility.

---

## 2. Bytecode Specification (Selected Opcodes)
| Opcode | Description |
| :--- | :--- |
| `LOAD <name>` | Push variable value to stack. |
| `STORE <name>` | Pop value from stack and store in variable. |
| `PUSH` | Report top-of-stack as an Agent Output. |
| `HALT` | Terminate thread execution. |
| `ARROW` | Flow Operator (→). Modulated by $\lambda$. |
| `CH_EQ` | Chaos Equality (≈). Modulated by $\lambda$. |
| `SIN/COS/SQRT` | Math Intrinsics (Direct CPU pass-through). |

---

## 3. Compilation Pipeline
1. **Lexer**: Indentation-aware tokenization.
2. **Parser**: Bimodal (Brace/Indent) recursive descent.
3. **Compiler**: Single-pass AST-to-Bytecode generation.
4. **Linker**: Import resolution from `stdlib/`.

---

## 4. Swarm Execution
The `SwarmManager` initializes $N$ instances of `FluxVM`. In each tick:
1. Every VM executes its code until `HALT`.
2. VM `outputs` are collected via the `PUSH` opcode.
3. Global entropy is recalculated.
4. `drift()` is applied to all volatile variables.
