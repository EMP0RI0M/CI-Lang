# PART III: THE CHAOS ENGINE

## Chapter 7: The CI Agent Model

### 7.1 Agents with Internal States
In CI-Lang, the **Agent** is not just an object; it is a **Vibrating State Space**. 

Each agent possesses an internal memory managed by the **Chaos VM**. Unlike traditional variables that hold static bits, an agent's state is composed of `MemoryCells`. Each cell encapsulates a value and its associated **Volatility ($\omega$)**. 

The state is not a fixed point; it is a probability density. When an agent is initialized, it is "born" into a specific region of the phase space, but its future trajectory is never set in stone.

### 7.2 Local Updates: The Thermodynamic Pulse
Every tick of the system triggers the **Update Block**. This is where the agent's internal logic—expressed in FluxVM bytecode—is executed. 

The update is **local**. An agent has no global knowledge of the entire swarm; it only knows its own state and the aggregate signals it receives from its immediate environment. This locality is mandatory for scalability and mirrors the decentralized nature of biological intelligence. The update block is the agent's "breath," its rhythmic attempts to impose its own rules on the incoming data.

### 7.3 Neighbor Influence: Coupling and Adjacency
Agents do not exist in a vacuum. They are **Coupled**. 

Through a **Topology Map**, agents are connected to neighbors. During the update phase, an agent can "sample" the states of its neighbors. This influence is usually modeled as a **Coupling Strength ($g$)**. 
$$S_{i}(t+1) = f(S_{i}(t)) + g \cdot \sum_{j \in neighbors} (S_{j}(t) - S_{i}(t))$$
This creates a "Synchrony Pressure." If coupling is high, agents will tend to align their states. if it is low, they will drift apart. Intelligence emerges in the tension between these two forces.

### 7.4 Noise Injection: The Entropy Kernel
To prevent the agent from becoming a static slave to its neighbor's signals or its own deterministic rules, we inject **Thermodynamic Noise**.

The **Entropy Kernel** monitors the global heat of the system and injects Gaussian fluctuations directly into the memory cells. This is not "error." It is the **Fuel of Divergence**. It allows the agent to "jitter" out of shallow attractors and explore the deeper, more complex regions of its potential state space.

### 7.5 Drift and Persistence: The Physics of Memory
Memory in CI is a balance between **Persistence** (the ability to hold a state) and **Drift** (the ability to forget). 

Every memory cell has a natural decay. If an agent does not explicitly "energize" a state by computing it, the state will naturally drift toward the global mean. This ensures that the system is always "fresh." Information that is not useful—information that is not regularly reinforced by the agent's logic or its environment—is naturally recycled back into the chaos.

---
> "An agent is a localized flame, burning through the entropy of its neighbors to create a flicker of meaning." — The Founder
---
