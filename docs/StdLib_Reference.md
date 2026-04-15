# CI-LANG STANDARD LIBRARY REFERENCE (v1.0)

This document lists all built-in modules and their functions provided in the `stdlib/` directory.

---

## 1. `math.ci` (Numerical Foundation)
**Constants:**
- `pi`: 3.14159...
- `e`: 2.71828...
- `tau`: 6.28318...

**Trigonometry:**
- `sin(x)`, `cos(x)`, `tan(x)`

**Logarithmics & Powers:**
- `sqrt(x)`: Square root.
- `exp(x)`: Exponential ($e^x$).
- `log(x)`: Natural log.
- `log10(x)`: Base-10 log.
- `pow(base, exponent)`: Power function.

**Rounding & Utility:**
- `ceil(x)`, `floor(x)`, `round(x)`
- `abs(x)`: Absolute value.
- `clamp(val, low, high)`: Restricts value to range.
- `lerp(a, b, t)`: Linear interpolation between a and b.

---

## 2. `chaos.ci` (Homeostatic Foundation)
**Core Functions:**
- `measure_homeostasis(val, target)`: Returns absolute divergence.
- `adaptive_gain(lambda, memory)`: Calculates control gain based on entropy $\lambda$ and memory $M$.
- `stabilize(current, target, lambda, memory)`: Applies high-level homeostatic pull logic.

---

## 3. `bridge.ci` (Linguistic Foundation)
**Core Functions:**
- `consult_teacher()`: Checks the mailbox for LLM-generated stabilization advice.
- `report_state(id, val, entropy)`: Formats and prints agent telemetry for monitor ingestion.
- `clear_channel()`: Resets the linguistic communication buffer.

---

## 4. `agent.ci` (Swarm Foundation)
**Core Blueprints:**
- `apply_macs(current, target)`: A high-level helper that automates the measurement and stabilization process using standard system metrics.

---
**Technical Note**: All functions marked as "Intrinsic" compile directly to FluxVM opcodes for near-native performance.
