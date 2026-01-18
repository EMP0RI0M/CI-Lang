# PART IV: CI-LANG: THE CHAOS PROGRAMMING LANGUAGE

## Chapter 13: Standard Library

### 13.1 Noise: The Primary Catalyst
The `noise(volatility)` function is the most used builtin in CI-Lang. It draws a value from a Gaussian distribution centered at zero with a standard deviation controlled by the agent's volatility or an explicit parameter. It is the "Jitter" that prevents state stagnation.

### 13.2 Logistic Kernels: Generating Chaos
While the Logistic Map is a mathematical concept, CI-Lang provides it as a optimized kernel:
- `logistic_step(x, r)`: Computes one iteration.
- `logistic_swarm(r_range)`: Initializes an entire swarm with a distribution of $r$ parameters, creating a multi-modal chaotic reservoir.

### 13.3 Random Kernels and Distributions
CI-Lang supports non-standard distributions aligned with physical noise:
- `perlin_noise(dt)`: Smooth, temporal noise for gradual state drift.
- `cauchy_pull()`: Heavy-tailed noise for "black swan" events that force drastic state shifts.

### 13.4 Coupling Functions: The Social Builtins
- `coupling_sum(neighbor_attr)`: Calculates the aggregate influence of neighbors.
- `diffusion(attr, rate)`: Simulates a heat-like spread of a value across the swarm topology.
- `synchrony()`: Measures the local phase-alignment between an agent and its neighbors.

### 13.5 Activation and Activation-like Functions
We provide standard non-linearities but with "Chaos-Aware" signatures:
- `stochastic_relu(x)`: A ReLU with a noise-leak in the negative regime.
- `soft_collapse(x, threshold)`: Gradually pulls a chaotic distribution toward a stable value once it nears a threshold.

### 13.6 Observables: The Swarm's Feedback
- `entropy::measure()`: Returns the global Shannon entropy.
- `swarm::mean(attr)`: The first-moment average of the population.
- `swarm::variance(attr)`: The measure of spread, often used as a proxy for "Internal Temperature."

---
> "The library is not a collection of tools, but a list of ways the universe likes to move." — The Founder
---
