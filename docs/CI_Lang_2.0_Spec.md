# CI-Lang 2.0 Specification (Codename: Xaos)
Version: 0.2-alpha
Status: Draft / Under Development

## 1. Philosophy: The Disorder Paradigm
CI-Lang 2.0 reflects the physics of disorder. Unlike classical languages that fight entropy to maintain static state, CI-Lang assumes:
- **Order is a temporary state** requiring energy (computational cycles).
- **Chaos is the natural baseline**, used as the primary engine of computation.
- **Emergence** is the goal, achieved through autonomous agent interactions.

## 2. The Entropy Kernel
The core of the FluxVM 2.0 is the **Entropy Kernel**. It maintains a global scalar `E` (0.0 - 1.0) and regulates the "boiling point" of the system.

### 2.1. Alive Memory (Thermodynamic Memory)
Memory is no longer static. Every variable ($v$) is a `MemoryCell` with:
- `value`: The current state.
- `volatility` ($\omega$): The measure of how fast the value drifts.
- `last_tick`: Timestamp of the last stable update.

**Drift Formula**:
$$v_{t+1} = v_t + \mathcal{N}(0, \omega \cdot E)$$
Where $\mathcal{N}$ is the Normal distribution.

## 3. Native Syntax

### 3.1. Agent Declaration
Agents are autonomous entities that evolve in a swarm.
```c
agent Neuron {
    state {
        potential: 0.0,
        threshold: 0.5
    }
    volatility = 0.1;
    update(dt) {
        potential = potential + coupling_sum(neighbors.potential) * 0.01;
        if (potential > threshold) {
            emit("spike", potential);
            potential = 0.0;
        }
    }
}
```

### 3.2. System and Environment
The `system` block defines the global physics.
```c
system Universe {
    entropy_target = 0.3;
    spawn Neuron size=1000 topology=random(k=5);
    
    // Low entropy blocks for deterministic logic
    execute_low_entropy {
        // High energy cost logic goes here
    }
}
```

## 4. BNF Grammar (Xaos 2.0)
```bnf
<program>      ::= "system" IDENT "{" { <system_stmt> } "}"
<system_stmt>  ::= <agent_decl> | <swarm_cmd> | <entropy_cmd> | <execute_block>
<agent_decl>   ::= "agent" IDENT "{" <state_block> <volatility_stmt>? <update_block> "}"
<state_block>  ::= "state" "{" { IDENT ":" <expr> [ "," ] } "}"
<update_block> ::= "update" "(" IDENT ")" "{" { <stmt> } "}"
<execute_block>::= "execute_low_entropy" "{" { <stmt> } "}"
<expr>         ::= <binary_op> | <chaos_op> | <literal> | IDENT
<chaos_op>     ::= "⟨" <expr> "⟩" | <expr> "≈" <expr>
```

## 5. Execution Semantics
1. **Tick Phase**: All `agent` update functions are called in parallel (emulated or true parallel).
2. **Drift Phase**: The VM applies `volatility` drift to all memory cells not explicitly `locked`.
3. **Entropy Phase**: The `Entropy Controller` measures aggregate variance and adjusts $E$ to reach `entropy_target`.
4. **Readout Phase**: External listeners sample the swarm state.
