# CI-Lang v1.0 User Guide
## Mastering Chaos Intelligence

CI-Lang is a bimodal, stack-based language designed for high-concurrency swarm orchestration. It treats entropy as a first-class citizen using thermodynamic control operators.

---

### 1. Variables & Data Types
CI-Lang supports `number`, `string`, and `array` types.
```ci
let x = 10.5        # Decimal literals
let msg = "Stability" # String literals
let data = [1, 2, 3] # Native arrays
```

### 2. Syntax Modes (Bimodal)
You can choose between **Indent-based** blocks (like Python) or **Brace-based** blocks (like C).
#### Indent Mode:
```ci
if x > 5:
    print("Large")
```
#### Brace Mode:
```ci
if x > 5: {
    print("Large")
}
```

### 3. Homeostatic Operators (Deep Math)
These are the core of CI-Intelligence:
- **Flow Operator (→)**: Pulls a value toward a target based on system entropy.
  ```ci
  val = val → 100.0  # val moves toward 100.0
  ```
- **Chaos Equality (≈)**: Checks if two values are "close enough" based on current system noise.
  ```ci
  if val ≈ target:
      print("Homeostasis Achieved")
  ```

### 4. Continuous Control (Agents)
Agents are the units of execution in a swarm. They have a persistent `state` and a ticking `update` loop.
```ci
agent Drone:
    state:
        alt = 0.0
    
    update(dt):
        alt = alt → 500.0  # Takeoff to 500m
        push alt             # Report state
```

### 5. Swarm Orchestration
Launch thousands of agents with a single command:
```ci
spawn Drone size = 1000;
```

### 6. Math Built-ins & Constants
CI-Lang provides native access to high-precision constants and functions:
- **Constants**: `PI`, `E`, `INF`, `NAN`
- **Functions**: `sin(x)`, `cos(x)`, `sqrt(x)`, `exp(x)`, `log(x)`, `round(x)`

---
### 7. Running a Program
Compile your source code into bytecode, then execute it through the Swarm Manager:
1. `python src/cic.py your_script.ci -o output.bc`
2. `python src/run_swarm.py --bytecode output.bc --steps 1000`
