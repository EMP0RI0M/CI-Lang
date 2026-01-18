# PART IV: CI-LANG: THE CHAOS PROGRAMMING LANGUAGE

## Chapter 11: Syntax and BNF Grammar

### 11.1 Fundamental Constructs
CI-Lang is a domain-specific language designed to describe the evolution of chaotic populations. Its syntax mirrors the hierarchical nature of physical systems: **Global System > Emergent Swarms > Autonomous Agents**.

The code is declarative at the top level (defining what things exist) and imperative within the update blocks (defining how things evolve).

### 11.2 Program Structure
A CI-Lang program is contained within a `system` block. This block represents the entire "Universe" of the simulation, containing the global environment variables and the definitions of all entities within it.

```c
system MyUniverse {
    // Global parameters
    entropy_target = 0.4;
    
    // Entity declarations
    agent MyAgent { ... }
    swarm MySwarm { ... }
}
```

### 11.3 Agents: The Genotype
The `agent` block is the blueprint for a single autonomous unit. 
- **state**: Defines the internal variables of the agent. These are implicitly "Alive Memory" cells.
- **volatility**: Defines the default sensitivity of the agent's memory to noise.
- **update(dt)**: The code executed at every tick of the system.

```c
agent Neuron {
    state { potential: 0.0 }
    volatility = 0.05;
    update(dt) {
        potential = potential * 0.95 + noise(volatility);
    }
}
```

### 11.4 Swarms: The Population
The `swarm` keyword instantiates a population of agents. It defines the size of the population and the interconnection **Topology**.
- **size**: Number of agents.
- **topology**: The connection graph (e.g., `random`, `grid`, `ring`).

```c
swarm SensoryGrid size=100 topology=grid(width=10) {
    agent_template { ... }
}
```

### 11.5 Controllers and Readouts
- **controller**: A high-level block that runs at fixed intervals to adjust global system parameters.
- **readout**: A specialized observer that samples the swarm state and maps it to external outputs.

```c
controller StabilityGovernor {
    every 10 ticks {
        if (entropy::measure() > 0.6) { volatility = volatility - 0.01; }
    }
}
```

### 11.6 The Chaos Operators
CI-Lang introduces unique operators for handling uncertainty:
- `⟨ x ⟩` (**The Entropy Bracket**): Wraps an expression in a stochastic interval.
- `x ≈ y` (**The Similarity Match**): Returns a probability that two values are "close enough" in phase space.
- `drift(x, speed)`: Explicitly nudges a value toward its neighbors or an attractor.

### 11.7 BNF Definition (Xaos 2.0)
The formal grammar of CI-Lang 2.0 is defined as follows:

```bnf
<program>       ::= "system" IDENT "{" { <top_stmt> } "}"
<top_stmt>      ::= <agent_decl> | <swarm_decl> | <controller_decl> | <readout_decl> | <global_assign>
<agent_decl>    ::= "agent" IDENT "{" <state_block> <vol_stmt>? <update_block> "}"
<state_block>   ::= "state" "{" { IDENT ":" <expr> [ "," ] } "}"
<update_block>  ::= "update" "(" IDENT ")" "{" { <stmt> } "}"
<swarm_decl>    ::= "swarm" IDENT "size" "=" <NUMBER> [ "topology" "=" <TOPOLOGY> ] "{" [ <agent_templ> ] "}"
<TOPOLOGY>      ::= "random" "(" "k" "=" <NUMBER> ")" | "grid" | "ring" | "full"
<stmt>          ::= <assign_stmt> | <if_stmt> | <for_stmt> | <chaos_stmt> | <emit_stmt>
<expr>          ::= <binary_op> | <call_expr> | <chaos_op> | <literal> | IDENT
<chaos_op>      ::= "⟨" <expr> "⟩" | <expr> "≈" <expr> | "noise" "(" <expr> ")"
```

### 11.8 Examples: The Stabilizer
To illustrate the syntax, here is a complete CI-Lang snippet for a consensus-seeking swarm:

```c
system Consensus {
    entropy_target = 0.2;
    swarm S size=50 topology=random(k=4) {
        agent_template {
            state { val: 0.5 }
            volatility = 0.1;
            update(dt) {
                // Pull toward neighbors
                val = val + coupling_sum(neighbors.val) * 0.05;
                // Periodic chaos to prevent freezing
                if (tick() % 100 == 0) { val = val + noise(0.2); }
            }
        }
    }
}
```

---
> "Grammar is the skeleton of thought. In CI-Lang, the skeleton is made of springs." — The Founder
---
