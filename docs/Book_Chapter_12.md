# PART IV: CI-LANG: THE CHAOS PROGRAMMING LANGUAGE

## Chapter 12: Semantics

### 12.1 Execution Model: The Living Pulse
Unlike the sequential, deterministic execution of classical languages, CI-Lang semantics are built on the **Living Pulse**. A program is not a linear path of instructions; it is a parallel evolution of state. 

The runtime does not "execute" an agent to find a result; it "steps" the agent through time. Each step is a transition in high-dimensional phase space.

### 12.2 The Tick-Cycle: Synchronicity and Causality
The fundamental unit of time in CI-Lang is the **Tick**.
1. **The Sampling Phase**: Every agent reads its internal state and the states of its neighbors. This is a read-only snapshot.
2. **The Update Phase**: The agent's `update(dt)` block executes using the snapshot data. Results are stored in a **Write Buffer**.
3. **The Commit Phase**: All write buffers are applied to the `MemoryCells` simultaneously.
4. **The Drift Phase**: The Entropy Kernel applies thermodynamic noise and natural decay (volatility) to all unprotected states.

This synchronous update ensures that the swarm's emergence is not dependent on execution order, preventing race conditions from affecting the system's "physics."

### 12.3 State Update Semantics: Values as Distributions
In CI-Lang, an assignment like `val = 0.5` does not mean "store the bit pattern for 0.5 at this address." It means "Set the peak of the probability density for this MemoryCell to 0.5."

If the system entropy is high, the actual value retrieved in the next tick might be `0.51` or `0.49`. The semantic meaning of an assignment is the **Injection of Intention** into a field of noise. The machine respects your intention, but the universe (entropy) adds its own data.

### 12.4 Stochasticity Rules: The Entropy Bracket
The `⟨ x ⟩` operator introduces explicit **Stochastic Semantics**. 
- Wrapping an expression in brackets tells the compiler that the result is an **Interval**, not a point.
- Any operation performed on an Interval (e.g., `⟨ x ⟩ + ⟨ y ⟩`) follows the rules of **Stochastic Arithmetic**, where the variance of the result is the sum of the variances.

This allows CI-Lang to perform "Fuzzy Math" at the hardware level, enabling agents to reason with uncertainty without complex library calls.

### 12.5 Global Variables vs. Global Fields
CI-Lang distinguishes between **Constants** (static values) and **Fields** (dynamic averages).
- `const PI = 3.14159`: A deterministic bit-pattern.
- `field AvgState = swarm::mean(S.val)`: A real-time, chaotic readout of the swarm's collective center of aggregate.

Fields are semantically "Heavy." Reading a field might trigger a GPU reduction or a high-energy computation. They are the "Collective Memories" of the system.

### 12.6 Entropy-Access Semantics: Programming the Boiling Point
The `entropy::target` and `entropy::measure()` keywords allow the program to interact with its own "temperature." 
- Setting `entropy::target = 0.1` has the semantic effect of **Increasing Energy Consumption**. The VM must work harder to synchronize agents and suppress noise.
- Setting `entropy::target = 0.8` is **Energy Efficient**. The VM allows the agents to drift freely, consuming near-zero power to maintain order.

Semantics in CI-Lang is therefore a **Thermodynamic Negotiation** between the programmer and the machine.

---
> "In a deterministic world, meaning is a line. In a chaotic world, meaning is a vibration." — The Founder
---
